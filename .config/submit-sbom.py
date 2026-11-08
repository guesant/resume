import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


def collect_components(components):
    for component in components:
        if component.get("purl") and component.get("version"):
            yield component
        yield from collect_components(component.get("components", []))


def build_snapshot(report, manifest):
    repository = os.environ["GITHUB_REPOSITORY"]
    revision = os.environ["GITHUB_SHA"]
    ref = os.environ["GITHUB_REF"]
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
        raise ValueError("Invalid GitHub repository")
    branch = "profile" if repository == "guesant/guesant" else "main"
    if ref != f"refs/heads/{branch}" or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Snapshots require a branch commit")

    bom = json.loads(Path(report).read_text())
    if bom["bomFormat"] != "CycloneDX":
        raise ValueError("Expected a CycloneDX SBOM")
    components = list(collect_components(bom["components"]))
    refs = {component["bom-ref"]: component["purl"] for component in components}
    dependencies = {
        entry["ref"]: entry.get("dependsOn", []) for entry in bom.get("dependencies", [])
    }
    resolved = {}
    for component in components:
        purl = component["purl"]
        item = resolved.setdefault(purl, {"package_url": purl, "dependencies": []})
        children = item["dependencies"] + [
            refs[child] for child in dependencies.get(component["bom-ref"], []) if child in refs
        ]
        item["dependencies"] = sorted(set(children) - {purl})
    if not resolved:
        raise ValueError("The SBOM contains no resolved packages")

    detector = {"name": "Trivy", "version": "0.74.0", "url": "https://github.com/aquasecurity/trivy"}
    if Path(manifest).parent.parent == Path(".config/tooling"):
        package = json.loads(Path(manifest).with_name("package.json").read_text())
        version = package["packageManager"].split("@", 1)[1].split("+", 1)[0]
        detector = {"name": "pnpm", "version": version, "url": "https://github.com/pnpm/pnpm"}

    return {
        "version": 0,
        "sha": revision,
        "ref": ref,
        "job": {"id": os.environ["GITHUB_RUN_ID"], "correlator": f"quality/{manifest}"},
        "detector": detector,
        "scanned": datetime.now(timezone.utc).isoformat(),
        "manifests": {
            manifest: {
                "name": manifest,
                "file": {"source_location": manifest},
                "resolved": resolved,
            }
        },
    }


def submit(report, manifest):
    snapshot = build_snapshot(report, manifest)
    payload = json.dumps(snapshot, indent=2)
    output = Path(".local/reports/snapshots") / Path(manifest).with_suffix(".json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload + "\n")
    request = Request(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/dependency-graph/snapshots",
        data=payload.encode(),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        if response.status != 201:
            raise RuntimeError(f"Dependency submission returned HTTP {response.status}")
        print("Dependency snapshot submitted")


if __name__ == "__main__":
    submit(*sys.argv[1:])
    for lockfile in sorted(Path(".config/tooling").glob("*/pnpm-lock.yaml")):
        report = Path(".local/reports/sbom") / lockfile.parent / "dependencies.cdx.json"
        submit(report, str(lockfile))
