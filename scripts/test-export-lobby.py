import importlib.util
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location("export_lobby", Path(__file__).with_name("export-lobby.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ExportTests(unittest.TestCase):
    def test_public_allowlist_and_stable_identifiers(self):
        document = {"cv": {"email": "secret@example.test", "sections": {"projects": [{"name": "[A project](https://example.test/project)", "summary": "Public description", "secret": "hidden", "technologies": ["Not inferred"]}]}}}
        item = module.export_document(document, "en")[0]
        self.assertEqual(item["title"], "A project")
        self.assertEqual(item["tags"], [])
        self.assertEqual(item["metadata"], {})
        self.assertNotIn("secret", str(item))
        self.assertNotIn("email", str(item))
        document["cv"]["sections"]["projects"][0]["summary"] = "Edited summary"
        self.assertEqual(item["id"], module.export_document(document, "en")[0]["id"])

    def test_private_disabled_and_draft_are_not_exported(self):
        entries = [{"name": "Hidden", **flag} for flag in ({"private": True}, {"public": False}, {"enabled": False}, {"draft": True})]
        self.assertEqual(module.export_document({"cv": {"sections": {"projects": entries}}}, "en"), [])

    def test_projects_export_the_declared_public_platform_url(self):
        name = "[ava-pro](https://github.com/guesant/ava-pro)"
        document = {"cv": {"sections": {"projects": [{"name": name, "summary": "Public summary"}]}}}
        item = module.export_document(document, "en")[0]
        self.assertEqual(item["metadata"]["content_url"], "https://github.com/guesant/ava-pro")
        self.assertTrue(item["url"].startswith("https://curriculum.guesant.net/en/#project-"))
        self.assertEqual(item["title"], "ava-pro")

    def test_content_urls_are_not_inferred_or_exported_from_other_fields(self):
        for name in ("ava-pro", "[Project](https://github.com.evil.test/repo)", "[Project](https://user:secret@github.com/guesant/repo)", "[Project](javascript:alert(1))"):
            self.assertIsNone(module.public_content_url(name))
        document = {"cv": {"sections": {"cases": [{"name": "[Case](https://github.com/guesant/repo)", "summary": "Public summary"}]}}}
        self.assertNotIn("content_url", module.export_document(document, "en")[0]["metadata"])

    def test_canonical_anchor_exists_and_is_idempotent(self):
        item = module.export_document({"cv": {"sections": {"skills": [{"label": "Tools", "details": "A, B"}]}}}, "en")[0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.html"
            path.write_text("<html><body><h1>Skills</h1><p><strong>Tools</strong>: A, B</p></body></html>")
            module.add_anchors(path, [item])
            module.add_anchors(path, [item])
            self.assertEqual(path.read_text().count(f'id="{item["id"]}"'), 1)
            self.assertTrue(item["url"].endswith("#" + item["id"]))

    def test_empty_document_is_a_valid_empty_export(self):
        self.assertEqual(module.export_document({"cv": {"sections": {}}}, "en"), [])

    def test_anchor_targets_the_correct_section_not_an_earlier_mention(self):
        item = module.export_document({"cv": {"sections": {"cases": [{"name": "Repeated Name", "summary": "Case details"}]}}}, "en")[0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.html"
            path.write_text("<html><body><h1>Experience</h1><p>Repeated Name</p><h1>Cases</h1><h2>Repeated Name</h2><p>Case details</p></body></html>")
            module.add_anchors(path, [item])
            content = path.read_text()
            self.assertGreater(content.index(f'id="{item["id"]}"'), content.index("<h1>Cases</h1>"))


if __name__ == "__main__":
    unittest.main()
