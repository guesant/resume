import re
from pathlib import Path
from urllib.parse import urlsplit

from ruamel.yaml import YAML


ROOT = Path(__file__).resolve().parents[1]


def public_catalog(value):
    if not isinstance(value, dict) or value.get("version") != 1:
        raise ValueError("Invalid technologies catalog")
    groups = []
    identifiers = set()
    group_identifiers = set()
    for group in value["groups"]:
        if any(group.get(flag) for flag in ("private", "draft")) or group.get("public") is False or group.get("enabled") is False:
            continue
        labels = {locale: str(group["labels"][locale]) for locale in ("en", "pt-br")}
        if not all(labels.values()):
            raise ValueError("Missing technology group translation")
        group_id = identifier(group["id"], group_identifiers)
        items = []
        for item in group["items"]:
            if any(item.get(flag) for flag in ("private", "draft")) or item.get("public") is False or item.get("enabled") is False:
                continue
            item_id = identifier(item["id"], identifiers)
            url = urlsplit(item["url"])
            if url.scheme != "https" or not url.hostname or url.username or url.password or url.port:
                raise ValueError("Invalid technology URL")
            if not isinstance(item["name"], str) or not item["name"].strip():
                raise ValueError("Missing technology name")
            items.append({"id": item_id, "name": item["name"], "url": item["url"]})
        if items:
            groups.append({"id": group_id, "labels": labels, "items": items})
    return groups


def identifier(value, identifiers):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", value) or value in identifiers:
        raise ValueError("Invalid or duplicate technology identifier")
    identifiers.add(value)
    return value


def load_catalog():
    document = YAML(typ="safe").load((ROOT / "cv" / "technologies.yaml").read_text())
    return public_catalog(document)


def curriculum_document(locale, catalog):
    document = YAML(typ="safe").load((ROOT / "cv" / f"{locale}.yaml").read_text())
    section = "skills" if locale == "en" else "competências"
    document["cv"]["sections"][section] = [
        {"label": group["labels"][locale.lower()], "details": ", ".join(item["name"] for item in group["items"])}
        for group in catalog
    ]
    return document


def main():
    catalog = load_catalog()
    output = ROOT / "build" / "inputs"
    output.mkdir(parents=True, exist_ok=True)
    for locale in ("en", "pt-BR"):
        document = curriculum_document(locale, catalog)
        document["settings"]["render_command"]["output_folder"] = f"../{locale}"
        with (output / f"{locale}.yaml").open("w") as stream:
            YAML().dump(document, stream)


if __name__ == "__main__":
    main()
