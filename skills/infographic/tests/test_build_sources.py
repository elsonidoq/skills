import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build.py"
SPEC = importlib.util.spec_from_file_location("infographic_build", SCRIPT)
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


def content_with_source(source: str) -> dict:
    return {
        "title": "Source boundary test",
        "lede": "Every source stays inside the knowledge base.",
        "blocks": [
            {"type": "section", "heading": "Claim", "body": "A supported claim."},
            {"type": "sources", "items": [source, "documents/local.md"]},
        ],
    }


class TempKnowledgeBase:
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "kb"
        documents = self.root / "documents"
        documents.mkdir(parents=True)
        (documents / "local.md").write_text(
            "---\nsource: https://example.com/local\n---\nlocal\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()


class SourceBoundaryTests(TempKnowledgeBase, unittest.TestCase):

    def assert_source_rejected(self, source: str):
        problems = build.validate(content_with_source(source), self.root)
        self.assertTrue(
            any("sources" in problem and source in problem for problem in problems),
            problems,
        )

    def test_accepts_relative_regular_source_below_root(self):
        problems = build.validate(content_with_source("documents/local.md"), self.root)
        self.assertEqual(problems, [])

    def test_rejects_absolute_source_path(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        self.assert_source_rejected(str(outside))

    def test_rejects_parent_traversal_source_path(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        self.assert_source_rejected("../outside.md")

    def test_rejects_directory_source(self):
        (self.root / "documents" / "directory").mkdir()
        self.assert_source_rejected("documents/directory")

    def test_rejects_symlink_resolving_outside_root(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        link = self.root / "documents" / "outside-link.md"
        link.symlink_to(outside)
        self.assert_source_rejected("documents/outside-link.md")


class InlineLinkBoundaryTests(TempKnowledgeBase, unittest.TestCase):
    def assert_link_rejected(self, target: str):
        problem = build.link_target_problem(target, self.root)
        self.assertIsNotNone(problem)

    def test_accepts_relative_regular_link_target_below_root(self):
        self.assertIsNone(build.link_target_problem("documents/local.md", self.root))

    def test_rejects_absolute_link_target(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text(
            "---\nsource: https://example.com/outside\n---\noutside\n",
            encoding="utf-8",
        )
        self.assert_link_rejected(str(outside))

    def test_rejects_parent_traversal_link_target(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text(
            "---\nsource: https://example.com/outside\n---\noutside\n",
            encoding="utf-8",
        )
        self.assert_link_rejected("../outside.md")

    def test_rejects_symlink_link_target_resolving_outside_root(self):
        outside = Path(self.temp.name) / "outside.md"
        outside.write_text(
            "---\nsource: https://example.com/outside\n---\noutside\n",
            encoding="utf-8",
        )
        link = self.root / "documents" / "outside-link.md"
        link.symlink_to(outside)
        self.assert_link_rejected("documents/outside-link.md")


if __name__ == "__main__":
    unittest.main()
