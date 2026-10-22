import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from import_open_issues import Source, preview

ROOT = Path(__file__).resolve().parents[3]
BASELINE_SHA256 = "314b9ddd758d25923105d85c23225293d0a1398b506d1b28925d783a5c3e1c7a"
SOURCE = Source("github.com", "elsonidoq/skills", "docs/open_issues.md", "952e39b813a443caeb7417e63c170e219a433dbd")


class PreviewTests(unittest.TestCase):
    def test_actual_baseline_is_faithfully_previewed_by_production_helper(self):
        original = (ROOT / "docs/open_issues.md").read_text()
        self.assertEqual(hashlib.sha256(original.encode()).hexdigest(), BASELINE_SHA256)
        result = preview(original, SOURCE, "elsonidoq/skills")
        self.assertEqual(result.diagnostics, ())
        self.assertEqual([r.title.split(":", 1)[0] for r in result.records], ["OI-18", "OI-19", *[f"OI-{n}" for n in range(1, 18)]])
        self.assertEqual(result.counts, {"records": 19, "open": 16, "closed": 3, "unmappable": 0})
        by_id = {r.title.split(":", 1)[0]: r for r in result.records}
        self.assertEqual({key for key, value in by_id.items() if value.state == "closed"}, {"OI-6", "OI-7", "OI-12"})
        for record in result.records:
            self.assertIn(record.original_excerpt, original)
            self.assertEqual(dict(record.fields)["Status"].lower(), record.state)
            for field in ("Problem", "Primary evidence", "Resumption condition"):
                self.assertIn(field, dict(record.fields))
                self.assertIn(dict(record.fields)[field], record.body)
            self.assertIn("Original Markdown excerpt", record.body)
            self.assertIn("952e39b813a443caeb7417e63c170e219a433dbd", record.body)
        self.assertIn("Latest verification (owner-controlled assignments)", dict(by_id["OI-15"].fields))
        self.assertIn("Temporary logs may expire", by_id["OI-8"].body)
        self.assertIn("not a confirmed", by_id["OI-5"].body)
        self.assertIn("[GitHub issue #2](https://github.com/elsonidoq/skills/issues/2)", by_id["OI-4"].body)
        self.assertIn("[OI-5](https://github.com/elsonidoq/skills/blob/952e39b813a443caeb7417e63c170e219a433dbd/docs/open_issues.md)", by_id["OI-6"].body)
        self.assertTrue(by_id["OI-18"].original_entry_url.endswith("#oi-18-resumed-runs-cannot-append-to-their-existing-jsonl-metrics-artifact"))

    def test_multiline_extra_fields_links_and_identity(self):
        text = """## OI-1: Renamed title\n\n- **Status:** open\n- **Problem:** First line\n  second line with [relative](../runtime/a.py#part), [absolute #2](https://github.com/x/y/issues/2), OI-9 and `../code.py`.\n- **Primary evidence:** evidence\n- **Resumption condition:** resume\n- **History:** retained\n"""
        result = preview(text, SOURCE, "dest/repo")
        record = result.records[0]
        self.assertEqual(record.identity, "github.com/elsonidoq/skills:docs/open_issues.md:OI-1")
        self.assertIn("https://github.com/elsonidoq/skills/blob/952e39b813a443caeb7417e63c170e219a433dbd/runtime/a.py#part", record.body)
        self.assertIn("[absolute #2](https://github.com/x/y/issues/2)", record.body)
        self.assertIn("[OI-9](https://github.com/elsonidoq/skills/blob/952e39b813a443caeb7417e63c170e219a433dbd/docs/open_issues.md)", record.body)
        self.assertIn("`../code.py`", record.body)
        self.assertIn(("History", "retained"), record.fields)
        renamed = preview(text.replace("Renamed title", "Revised title"), SOURCE, "dest/repo").records[0]
        self.assertEqual(renamed.identity, record.identity)
        other = preview(text, Source("github.com", "other/repo", "docs/open_issues.md", "different-revision"), "dest/repo").records[0]
        self.assertNotEqual(other.identity, record.identity)

    def test_unmappable_duplicate_unsafe_and_sensitive_inputs_are_diagnostic(self):
        valid = """## OI-1: Valid\n- **Status:** open\n- **Problem:** safe\n- **Primary evidence:** safe\n- **Resumption condition:** safe\n"""
        bad_status = valid.replace("OI-1: Valid", "OI-2: Unknown").replace("Status:** open", "Status:** pending")
        duplicate = valid.replace("Valid", "Duplicate")
        unsafe = valid.replace("OI-1: Valid", "OI-3: Unsafe").replace("safe", "<script>alert(1)</script>", 1)
        sensitive = valid.replace("OI-1: Valid", "OI-4: Sensitive").replace("safe", "token=DO_NOT_EXPORT", 1)
        result = preview(valid + bad_status + duplicate + unsafe + sensitive, SOURCE, "dest/repo")
        self.assertEqual([r.title for r in result.records], ["OI-1: Valid"])
        reasons = "\n".join(d.reason for d in result.diagnostics)
        self.assertIn("unmappable status", reasons)
        self.assertIn("duplicate OI identity", reasons)
        self.assertIn("unsafe Markdown", reasons)
        self.assertIn("sensitive candidate data rejected", reasons)
        self.assertNotIn("DO_NOT_EXPORT", "\n".join(r.body for r in result.records))
        self.assertEqual(result.counts["unmappable"], 4)

    def test_missing_structure_does_not_drop_valid_records_or_claim_completeness(self):
        valid = """## OI-1: Good\n- **Status:** closed\n- **Problem:** p\n- **Primary evidence:** e\n- **Resumption condition:** r\n"""
        malformed = "## OI-2: Missing\n- **Status:** open\n- **Problem:** p\n"
        result = preview(valid + malformed, SOURCE, "dest/repo")
        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.records[0].state, "closed")
        self.assertEqual(result.diagnostics[0].oi_id, "OI-2")
        self.assertIn("missing required", result.diagnostics[0].reason)


if __name__ == "__main__":
    unittest.main()
