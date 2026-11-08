import json
import math
import sys
from pathlib import Path


def blocks(package, group):
    score = group["max_severity"]
    if score != "":
        rating = float(score)
        if not math.isfinite(rating) or not 0 <= rating <= 10:
            raise ValueError("Invalid OSV severity")
        return rating >= 7

    ratings = [
        advisory["database_specific"]["severity"]
        for advisory in package["vulnerabilities"]
        if advisory["id"] in group["ids"]
    ]
    if not ratings or any(rating not in {"LOW", "MODERATE", "HIGH", "CRITICAL"} for rating in ratings):
        raise ValueError(f"Missing OSV severity for {group['ids']}")
    return any(rating in {"HIGH", "CRITICAL"} for rating in ratings)


report = json.loads(Path(sys.argv[1]).read_text())
sources = {Path(result["source"]["path"]).resolve() for result in report["results"]}
missing = {Path(path).resolve() for path in sys.argv[2:]} - sources
if missing:
    sys.exit(f"OSV omitted CycloneDX sources: {sorted(map(str, missing))}")

findings = [
    group["ids"]
    for result in report["results"]
    for package in result["packages"]
    for group in package.get("groups", [])
    if blocks(package, group)
]
if findings:
    sys.exit(f"OSV HIGH or CRITICAL findings: {findings}")
