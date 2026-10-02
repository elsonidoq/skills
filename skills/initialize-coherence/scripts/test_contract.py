#!/usr/bin/env python3
"""Source-first static Coherence checks. Fixtures are not model-obedience evidence."""
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASELINE = json.loads((HERE / "fixtures/source-contract.json").read_text())
SKILL = HERE.parent / "SKILL.md"
SOURCE_HASHES = {
    "skills/install-memory/SKILL.md": "7894452bb308c5292c13f5cfb3d19ed945842d88e1a31e1d5dbb8861dddc715f",
    "skills/initialize-documentation/SKILL.md": "978b51d11867496a6237d233987886e9dcb718a6ac3beedf7fc52a1f16c24b32",
}


def normalized(text):
    return " ".join(text.split())


def stage(text, name):
    marker = f"## {name}"
    start = text.find(marker)
    if start < 0:
        return ""
    end = text.find("\n## ", start + len(marker))
    return text[start:] if end < 0 else text[start:end]


def check_contract(text):
    errors = []
    for row in BASELINE["ledger"]:
        body = normalized(stage(text, row["stage"]))
        for phrase in row["requires"]:
            if normalized(phrase) not in body:
                errors.append(f"{row['id']}: missing {phrase!r} in {row['stage']}")
    return errors


class BaselineTests(unittest.TestCase):
    def test_original_sources_are_attributed_and_immutable(self):
        self.assertEqual(BASELINE["revision"], "7f6c0cb0cbdd15967d91c84b2295a45f3c64a2d3")
        for path, digest in SOURCE_HASHES.items():
            self.assertEqual(hashlib.sha256(BASELINE["sources"][path].encode()).hexdigest(), digest)

    def test_every_original_operational_line_has_a_ledger_carrier(self):
        for path, text in BASELINE["sources"].items():
            covered = set()
            for row in BASELINE["ledger"]:
                for citation in row["citations"]:
                    if citation["path"] == path:
                        covered.update(range(citation["start"], citation["end"] + 1))
            for number, line in enumerate(text.splitlines(), 1):
                if number >= 8 and line.strip():
                    self.assertIn(number, covered, f"unaccounted source clause {path}:{number}")

    def test_rows_have_behavior_stages_checks_and_ownership_decisions(self):
        ids = set()
        for row in BASELINE["ledger"]:
            self.assertNotIn(row["id"], ids); ids.add(row["id"])
            for key in ("behavior", "stage", "ownership_change", "task", "positive", "negative", "evidence", "requires"):
                self.assertTrue(row[key], (row["id"], key))
            for citation in row["citations"]:
                path = citation["path"]
                text = BASELINE.get("sources", {}).get(path, BASELINE["supporting"].get(path, ""))
                self.assertTrue(text, path)
                self.assertLessEqual(citation["end"], len(text.splitlines()))
        self.assertEqual(set(BASELINE["acceptance"]), {"A1", "A2", "A3", "A4", "A5"})
        self.assertEqual({r["behavior_group"] for r in BASELINE["ledger"]}, {f"B{i}" for i in range(1, 9)})


class CandidateTests(unittest.TestCase):
    def test_candidate_carrying_stages(self):
        self.assertTrue(SKILL.exists(), "initialize-coherence candidate missing")
        self.assertEqual(check_contract(SKILL.read_text()), [])


if __name__ == "__main__":
    baseline_only = "--baseline" in sys.argv
    if baseline_only:
        sys.argv.remove("--baseline")
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(BaselineTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(not result.wasSuccessful())
    unittest.main()
