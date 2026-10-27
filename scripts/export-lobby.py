import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from ruamel.yaml import YAML


ROOT = Path(__file__).resolve().parents[1]
SECTIONS = {
    "pt-BR": {"experiência": "experience", "formação": "education", "educação": "education", "competências": "skill", "projetos": "project", "cases": "case"},
    "en": {"experience": "experience", "education": "education", "skills": "skill", "projects": "project", "cases": "case"},
}


def plain(value):
    text = str(value or "")
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[*`]+", "", text).strip()


def public_content_url(value):
    match = re.fullmatch(r"\[[^\]]+\]\((https://[^\s)]+)\)", str(value or "").strip())
    if not match:
        return None
    url = match.group(1)
    parsed = urlsplit(url)
    if parsed.hostname not in {"github.com", "gitlab.com", "www.youtube.com", "youtube.com", "youtu.be"} or parsed.username or parsed.password or parsed.port not in {None, 443}:
        return None
    return url


def export_document(document, locale):
    items = []
    for section, kind in SECTIONS[locale].items():
        for entry in document.get("cv", {}).get("sections", {}).get(section, []):
            if entry.get("public") is False or entry.get("enabled") is False or entry.get("private") or entry.get("draft"):
                continue
            primary = entry.get("name") or entry.get("company") or entry.get("institution") or entry.get("label")
            if not primary:
                raise ValueError(f"Missing public title in {section}")
            title = plain(primary)
            identifier = kind + "-" + hashlib.sha256(str(primary).encode()).hexdigest()[:16]
            summary = plain(entry.get("summary") or entry.get("details") or entry.get("area"))
            metadata = {key: plain(entry[key]) for key in ("position", "degree", "area", "start_date", "end_date", "date") if entry.get(key) is not None}
            if kind == "project":
                content_url = public_content_url(primary)
                if content_url:
                    metadata["content_url"] = content_url
            items.append({"id": identifier, "language": locale.lower(), "type": kind, "title": title, "summary": summary, "url": f"https://curriculum.guesant.net/{locale}/#{identifier}", "tags": [], "metadata": metadata})
    return items


def add_anchors(path, items):
    content = path.read_text()
    for item in items:
        identifier = item["id"]
        if f'id="{identifier}"' in content:
            continue
        title = item["title"]
        locale = "pt-BR" if item["language"] == "pt-br" else "en"
        section_names = {
            name.casefold() for name, kind in SECTIONS[locale].items()
            if kind == item["type"]
        }
        headings = list(re.finditer(r"<h1\b[^>]*>(.*?)</h1>", content, re.DOTALL))
        section_start = None
        section_end = len(content)
        for index, heading in enumerate(headings):
            heading_text = html.unescape(re.sub(r"<[^>]+>", "", heading.group(1))).strip()
            if heading_text.casefold() in section_names:
                section_start = heading.end()
                if index + 1 < len(headings):
                    section_end = headings[index + 1].start()
                break
        if section_start is None:
            raise ValueError(f"Cannot find public section: {item['type']}")
        candidates = [html.escape(title), html.escape(title, quote=False), title]
        matched = False
        for candidate in dict.fromkeys(candidates):
            position = content.find(candidate, section_start, section_end)
            if position < 0:
                continue
            container = content.rfind("<h2", section_start, position)
            if container < 0:
                container = max(content.rfind("<p", section_start, position), content.rfind("<li", section_start, position))
            if container >= section_start:
                content = content[:container] + f'<span id="{identifier}"></span>' + content[container:]
                matched = True
                break
        if not matched:
            raise ValueError(f"Cannot anchor public entry: {identifier}")
    path.write_text(content)


def main():
    items = []
    for locale in SECTIONS:
        document = YAML(typ="safe").load((ROOT / "cv" / f"{locale}.yaml").read_text())
        localized = export_document(document, locale)
        add_anchors(ROOT / "site" / locale / "index.html", localized)
        items.extend(localized)
    (ROOT / "site" / "lobby.json").write_text(json.dumps({"version": 1, "source": "resume", "items": items}, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
