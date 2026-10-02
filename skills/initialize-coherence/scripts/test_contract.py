#!/usr/bin/env python3
"""Source-first static Coherence checks. Fixtures are not model-obedience evidence."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASELINE = json.loads((HERE / "fixtures/source-contract.json").read_text())
SKILL = HERE.parent / "SKILL.md"
SCENARIOS = json.loads((HERE / "fixtures/scenarios.json").read_text())
ROWS = {row["id"]: row for row in BASELINE["ledger"]}
SOURCE_HASHES = {
    "skills/install-memory/SKILL.md": "7894452bb308c5292c13f5cfb3d19ed945842d88e1a31e1d5dbb8861dddc715f",
    "skills/initialize-documentation/SKILL.md": "978b51d11867496a6237d233987886e9dcb718a6ac3beedf7fc52a1f16c24b32",
}


def normalized(text):
    return " ".join(text.split()).casefold()


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

    def test_frontmatter_single_entry_and_probe_inventory(self):
        text = SKILL.read_text()
        self.assertTrue(text.startswith("---\nname: initialize-coherence\ndescription: Use when"))
        self.assertIn("# Initialize Coherence", text)
        names = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertIn("initialize-coherence", names)
        self.assertTrue({"install-memory", "initialize-documentation"}.isdisjoint(names))
        probe = (ROOT / "scripts/probe-pi-load.sh").read_text().split("REQUIRED=(", 1)[1].split(")", 1)[0]
        self.assertEqual(probe.count("initialize-coherence"), 1)
        for retired in ("install-memory", "initialize-documentation"):
            self.assertNotIn(retired, probe)

    def test_stage_sequence_and_dirty_first_gate(self):
        text = SKILL.read_text()
        self.assertEqual(re.findall(r"^## (.+)$", text, re.M),
                         ["Preflight", "Discovery", "Investigation", "Approval", "Adoption", "Documentation", "Validation"])
        pre = stage(text, "Preflight")
        self.assertLess(pre.index("git status --short"), pre.index("FIRST verify"))
        self.assertIn("no adoption write may precede this dirty capability gate", normalized(pre))
        investigation = stage(text, "Investigation")
        self.assertEqual(re.findall(r"^(\d)\. ", investigation, re.M), ["1", "2", "3", "4"])
        self.assertIn("skip this stage only for an initially clean project", normalized(investigation))

    def test_consumer_routes_preserve_noninitializing_closeout_and_memory_rules(self):
        for path in BASELINE["active_consumers"]:
            text = (ROOT / path).read_text()
            for retired in ("install-memory", "initialize-documentation"):
                self.assertNotIn(retired, text, path)
            self.assertIn("initialize-coherence", text, path)
        memory = normalized((ROOT / "skills/memory-handling/SKILL.md").read_text())
        for phrase in ("memory adoption: missing — run initialize-coherence", "do not create, guess, or modify a global store", "read the whole index first", "index → matching entries"):
            self.assertIn(phrase, memory)
        compact = normalized((ROOT / "skills/compact-memory/SKILL.md").read_text())
        for phrase in ("no verified project memory store", "do not create a memory store or modify global memory", "stop on a concurrent change", "fresh, independent backup"):
            self.assertIn(phrase, compact)
        finish = normalized((ROOT / "skills/finish-session/SKILL.md").read_text())
        gate = normalized(stage((ROOT / "skills/finish-session/SKILL.md").read_text(), "Step 0: Documentation Initialization Gate"))
        for phrase in ("existence check only", "do not audit documentation accuracy, create missing files", "database-schema owner", "documentation-routing guide", "initialize-coherence", "and stop"):
            self.assertIn(phrase, gate)
        self.assertIn("do not create or modify one implicitly", finish)

    def test_setup_matches_branch_and_readiness_bounds(self):
        readme = normalized((ROOT / "README.md").read_text())
        requirements = normalized((ROOT / "REQUIREMENTS.md").read_text())
        for phrase in ("proposal-first", "compatible adoption", "bounded refresh", "fresh read-only investigation", "empty/template shells", "structural readiness", "outstanding work", "/reload", "authorize separately"):
            self.assertIn(phrase, readme)
        for phrase in ("0.87.x", "0.87.1", "pi-subagents@0.73.1", "pi-ask-user@0.15.1", "tinyspec/direct tasking does not require it", "manual routing", "schema owner", "missing required structure blocks readiness"):
            self.assertIn(phrase, requirements)

    def test_introduced_references_and_repo_nonassociation(self):
        for path in ("README.md", "docs/index.md", "skills/initialize-coherence/SKILL.md"):
            for target in re.findall(r"\]\(([^)]+)\)", (ROOT / path).read_text()):
                if not target.startswith(("http", "#")):
                    self.assertTrue((ROOT / path).parent.joinpath(target.split("#", 1)[0]).exists(), (path, target))
        index = (ROOT / "docs/index.md").read_text()
        self.assertIn("no declared project-memory adoption contract", index)
        self.assertIn("suite-level database/schema owner", index)


class PreservationTests(unittest.TestCase):
    """Each original ledger row has a separately named carrying-stage check."""


def positive_check(row):
    def test(self):
        body = normalized(stage(SKILL.read_text(), row["stage"]))
        for phrase in row["requires"]:
            self.assertIn(normalized(phrase), body, row["id"])
    return test


for row in BASELINE["ledger"]:
    setattr(PreservationTests, row["positive"], positive_check(row))


class ScenarioTests(unittest.TestCase):
    """Pressure contexts select source clauses; no agent transcript or write simulator."""
    def test_fixture_rows_and_source_groups_are_accounted(self):
        seen = set()
        for scenario in SCENARIOS:
            self.assertTrue(scenario["context"])
            self.assertTrue(scenario["bound"])
            self.assertIn(scenario["branch"], ("all", "clean", "non-clean"))
            for row in scenario["rows"]:
                self.assertIn(row, ROWS); seen.add(row)
        self.assertEqual(seen, set(ROWS))


def scenario_check(scenario):
    def test(self):
        text = SKILL.read_text()
        for name in scenario["rows"]:
            row = ROWS[name]
            body = normalized(stage(text, row["stage"]))
            for phrase in row["requires"]:
                self.assertIn(normalized(phrase), body, f"{scenario['name']}: {scenario['bound']}")
        if scenario["branch"] == "non-clean":
            self.assertIn("on a non-clean project first verify", normalized(stage(text, "Preflight")))
        elif scenario["branch"] == "clean":
            self.assertIn("on the clean branch", normalized(stage(text, "Documentation")))
    return test


for scenario in SCENARIOS:
    setattr(ScenarioTests, f"test_{scenario['name']}", scenario_check(scenario))


class StatusFixtureTests(unittest.TestCase):
    def status(self, kind):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(["git", "-C", directory, *args], text=True)
            git("init", "-q")
            if kind == "tracked":
                (root / "tracked.txt").write_text("baseline\n")
                git("add", "tracked.txt")
                git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                    "-c", "core.hooksPath=/dev/null", "commit", "-qm", "isolated fixture")
                (root / "tracked.txt").write_text("changed\n")
            elif kind == "untracked":
                (root / "untracked.txt").write_text("fixture\n")
            return git("status", "--short")

    def test_clean_has_no_status_output(self):
        self.assertEqual(self.status("clean"), "")
        self.assertIn("clean means no output", normalized(stage(SKILL.read_text(), "Preflight")))

    def test_tracked_dirty_is_nonclean(self):
        self.assertIn(" M tracked.txt", self.status("tracked"))
        self.assertIn("on a non-clean project first verify", normalized(stage(SKILL.read_text(), "Preflight")))

    def test_untracked_only_is_nonclean(self):
        self.assertEqual(self.status("untracked"), "?? untracked.txt\n")
        self.assertIn("untracked files make the project non-clean", normalized(stage(SKILL.read_text(), "Preflight")))


if __name__ == "__main__":
    baseline_only = "--baseline" in sys.argv
    if baseline_only:
        sys.argv.remove("--baseline")
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(BaselineTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(not result.wasSuccessful())
    unittest.main()
