#!/usr/bin/env python3
"""Unified-memory instruction sensitivity and symbolic write-safety decisions.

These fixtures do not execute a skill or prove model obedience.
"""
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
TEXT = (ROOT / "skills/memory-handling/SKILL.md").read_text()

GUARDS = {
    "Discovering the association": (
        "exactly once per session", "one index", "custom index path", "Read-time discovery never creates storage",
        "Missing optional storage or STATE is nonblocking", "memory adoption: missing — run initialize-coherence",
        "never guess a path", "global agent memory as a fallback",
        "separate guidance store",
    ),
    "Retrieval protocol": (
        "Read the whole associated index first", "Open only relevant entries in full",
        "Do not recursively or", "wholesale load history", "Recheck after a memory write",
    ),
    "Authorized writes": (
        "trigger, consequence, and evidence pointer", "actual user provenance", "future trigger/action",
        "Clear bounded feedback needs no routine", "Explanation-only questions",
        "ordinary implementation approval", "agent", "failed runs", "inferred lessons",
        "Ambiguous", "explicit no-write boundary prevails",
        "outside-project paths", "symlink escapes", "unreadable or non-file collisions",
        "uncertain local", "dirty or concurrent content", "secrets or sensitive payloads",
        "Preserve custom", "Re-read and compare", "concurrent drift",
        "separate guidance, history, run, or STATE scaffolding", "task-commit contract",
    ),
    "No routine bookkeeping": (
        "do not authorize memory writes", "STATE, progress ledgers", "routine summaries",
        "index refreshes", "run/evidence records", "reflection", "candidate synthesis",
        "evidence-only commits", "Recovery remains owned by its existing coordinator",
    ),
}


def contract_errors(text):
    errors = []
    for heading, clauses in GUARDS.items():
        marker = "## " + heading
        start = text.find(marker)
        end = text.find("\n## ", start + len(marker))
        body = " ".join((text[start:] if end < 0 else text[start:end]).split()) if start >= 0 else ""
        errors.extend(f"{heading}: missing {clause}" for clause in clauses if clause not in body)
    for unsafe in (
        "Create a separate GUIDELINES.md store", "Automatically initialize memory on read",
        "Write a run SUMMARY on completion", "Refresh the memory index after every task",
        "Reflect at blocked pause", "Commit evidence separately before the next task",
        "Infer lessons from failed runs",
    ):
        if unsafe.lower() in text.lower():
            errors.append("bookkeeping: " + unsafe)
    return errors


def write_decision(kind, *, no_write=False, safe=True):
    """Authored symbolic authority oracle; it is not a filesystem write engine."""
    if no_write or kind in (
        "none", "explanation", "implementation-approval", "agent-observation", "failed-run", "inferred-lesson",
    ):
        return "no-write"
    if kind == "ambiguous":
        return "ask/no-write"
    return "write-unified-entry" if safe else "stop/no-write"


class UnifiedMemoryContractTests(unittest.TestCase):
    def test_actual_unified_owner_contract(self):
        self.assertEqual(contract_errors(TEXT), [])

    def test_each_guard_mutation_has_named_diagnostic(self):
        for heading, clauses in GUARDS.items():
            for clause in clauses:
                with self.subTest(heading=heading, clause=clause):
                    altered = TEXT.replace(clause, "REMOVED")
                    self.assertIn(f"{heading}: missing {clause}", contract_errors(altered))

    def test_separate_store_and_bookkeeping_resurrection_mutations_are_rejected(self):
        for unsafe in (
            "Create a separate GUIDELINES.md store", "Automatically initialize memory on read",
            "Write a run SUMMARY on completion", "Refresh the memory index after every task",
            "Reflect at blocked pause", "Commit evidence separately before the next task",
            "Infer lessons from failed runs",
        ):
            with self.subTest(unsafe=unsafe):
                self.assertIn("bookkeeping: " + unsafe, contract_errors(TEXT + "\n" + unsafe))

    def test_authority_matrix(self):
        self.assertEqual(write_decision("clear-future-direction"), "write-unified-entry")
        for kind in ("none", "explanation", "implementation-approval", "agent-observation", "failed-run", "inferred-lesson"):
            self.assertEqual(write_decision(kind), "no-write")
        self.assertEqual(write_decision("clear-future-direction", no_write=True), "no-write")
        self.assertEqual(write_decision("ambiguous"), "ask/no-write")

    def test_path_symlink_sensitive_owner_dirty_and_concurrent_safety_stops(self):
        for gap in ("dirty ownership", "concurrent drift", "outside root", "symlink", "sensitive payload", "unknown owner"):
            with self.subTest(gap=gap):
                self.assertEqual(write_decision("clear-future-direction", safe=False), "stop/no-write")

    def test_absent_optional_store_does_not_initialize(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for event in ("planning", "dispatch", "recovery", "review", "closeout", "blocked pause"):
                self.assertEqual(write_decision("none"), "no-write", event)
                self.assertEqual(list(root.iterdir()), [])

    def test_authorized_custom_association_creates_one_index_and_entry_preserving_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            custom = root / "custom.txt"
            custom.write_bytes(b"user content\n")
            self.assertEqual(write_decision("clear-future-direction"), "write-unified-entry")
            index = root / "owner-selected" / "MEMORY.md"
            entry = index.parent / "entries" / "parent-turns.md"
            entry.parent.mkdir(parents=True)
            index.write_text("# Memory index\n\n- Owner guidance: parent turns → entries/parent-turns.md\n")
            entry.write_text("User provenance: explicit future feedback.\nTrigger: parent turn.\nAction: notify only for questions or terminal completion.\n")
            self.assertEqual(custom.read_bytes(), b"user content\n")
            self.assertTrue(index.is_file())
            self.assertTrue(entry.is_file())
            self.assertEqual(sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()),
                             ["custom.txt", "owner-selected/MEMORY.md", "owner-selected/entries/parent-turns.md"])
            baseline = (index.read_bytes(), entry.read_bytes())
            for kind in ("none", "explanation", "ambiguous", "failed-run"):
                self.assertNotEqual(write_decision(kind), "write-unified-entry")
                self.assertEqual((index.read_bytes(), entry.read_bytes()), baseline)

    def test_selective_entries_and_recheck_contract_remain(self):
        index = {"parent-turn": "entries/parent-turns.md", "unrelated": "entries/other.md"}
        self.assertEqual([value for key, value in index.items() if key == "parent-turn"], ["entries/parent-turns.md"])
        self.assertEqual([value for key, value in index.items() if key == "no-match"], [])
        self.assertEqual(contract_errors(TEXT), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
