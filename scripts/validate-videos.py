from collections import Counter
from pathlib import Path
import re
import sys

from ruamel.yaml import YAML


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "cv" / "videos.yaml"
LOCALE_PATHS = [ROOT / "cv" / "en.yaml", ROOT / "cv" / "pt-BR.yaml"]
URL_PATTERN = re.compile(r"https://www\.youtube\.com/watch\?[^)\s]+")
LINK_PATTERN = re.compile(
    r"\[([^\]]+)\]\((https://www\.youtube\.com/watch\?[^)\s]+)\)"
)
SECTIONS = {
    "projects",
    "projetos",
    "Technical Productions",
    "Produções Técnicas",
}
PARENT_CATEGORIES = {
    "infrastructure-and-networking",
    "automation-and-tooling",
    "graphics-and-rendering",
    "browser-and-application-tooling",
    "algorithms-and-debugging",
}
YAML_READER = YAML(typ="safe")


def fail(message: str) -> None:
    print(f"video validation failed: {message}", file=sys.stderr)
    sys.exit(1)


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        document = YAML_READER.load(stream)
    if not isinstance(document, dict):
        fail(f"{path} does not contain a mapping")
    return document


def collect_links(value, section=None, entry=None):
    links = []
    if isinstance(value, dict):
        current_entry = value.get("name", entry)
        for key, child in value.items():
            current_section = key if key in SECTIONS else section
            links.extend(collect_links(child, current_section, current_entry))
    elif isinstance(value, list):
        for child in value:
            links.extend(collect_links(child, section, entry))
    elif isinstance(value, str):
        links.extend(
            (title, url, section, entry) for title, url in LINK_PATTERN.findall(value)
        )
    return links


catalog_document = load_yaml(CATALOG_PATH)
catalog_entries = catalog_document.get("videos")
if not isinstance(catalog_entries, list) or len(catalog_entries) != 12:
    fail("the catalog must contain exactly 12 videos")

required_fields = {"id", "title", "url", "owner_type", "owner_id", "category", "evidence_type"}
catalog_by_url = {}
catalog_by_id = {}

for entry in catalog_entries:
    if not isinstance(entry, dict):
        fail("every catalog entry must be a mapping")
    missing_fields = required_fields - entry.keys()
    if missing_fields:
        fail(f"catalog entry is missing {sorted(missing_fields)}")
    if entry["id"] in catalog_by_id:
        fail(f"duplicate catalog id: {entry['id']}")
    if entry["url"] in catalog_by_url:
        fail(f"duplicate catalog URL: {entry['url']}")
    if entry["category"] not in PARENT_CATEGORIES:
        fail(f"unknown category: {entry['category']}")
    if entry["owner_type"] == "project" and not entry["owner_id"]:
        fail(f"project video has no owner: {entry['id']}")
    if entry["owner_type"] == "technical-production" and entry["owner_id"] != "JipaCoding":
        fail(f"unexpected technical production owner: {entry['id']}")
    catalog_by_id[entry["id"]] = entry
    catalog_by_url[entry["url"]] = entry

for locale_path in LOCALE_PATHS:
    document = load_yaml(locale_path)
    links = collect_links(document)
    urls = [url for _, url, _, _ in links]
    counts = Counter(urls)
    if set(urls) != set(catalog_by_url):
        missing = sorted(set(catalog_by_url) - set(urls))
        extra = sorted(set(urls) - set(catalog_by_url))
        fail(f"{locale_path} differs from the catalog, missing={missing}, extra={extra}")
    duplicated = sorted(url for url, count in counts.items() if count != 1)
    if duplicated:
        fail(f"{locale_path} repeats video URLs: {duplicated}")
    for title, url, section, entry_name in links:
        catalog_entry = catalog_by_url[url]
        if title != catalog_entry["title"]:
            fail(f"title mismatch for {url} in {locale_path}")
        if catalog_entry["owner_type"] == "project":
            expected_sections = {"projects", "projetos"}
            if section not in expected_sections or catalog_entry["owner_id"] not in str(entry_name):
                fail(f"wrong project placement for {url} in {locale_path}")
        else:
            expected_sections = {"Technical Productions", "Produções Técnicas"}
            if section not in expected_sections or entry_name != "JipaCoding":
                fail(f"wrong technical production placement for {url} in {locale_path}")

print("video catalog validation passed")
