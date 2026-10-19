#!/usr/bin/env python3
"""Feedback-only owner sensitivity and symbolic filesystem decisions, not model obedience."""
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
TEXT = (ROOT / "skills/memory-handling/references/project-coordination.md").read_text()

GUARDS = {
    "Read existing guidance": (
        "standalone planning/task entry", "not an execution-feedback/routing intake obligation", "Missing store or STATE is nonblocking",
        "do not auto-initialize", "source criteria → task dependencies/REQUIRED checks → worker brief",
        "Empty guidance means no applicable guidance", "explicit relevant need",
        "read it first and open only matching records", "Do not recursively load history",
        "Missing relevant evidence retains uncertainty",
    ),
    "Explicit feedback only": (
        "explicit user corrective/future-round direction", "without a routine second exact-content approval",
        "user provenance", "trigger/action", "Ordinary implementation approval, agent observations",
        "explanation-only questions authorize no feedback write", "No feedback means no write",
        "Materially ambiguous meaning/scope requires asking", "An explicit no-write boundary prevails",
        "local owner/allowed paths", "outside-project paths", "symlink escapes",
        "unreadable/non-file collisions", "dirty and concurrent content", "re-read/compare",
        "Concurrent drift or same-file ambiguity stops", "secrets/sensitive payloads",
        "Create only the bounded guidelines owner", "never history/index/run scaffolding",
        "Recheck relevant guidance after writes", "one focused owned-path commit",
    ),
    "No routine bookkeeping": (
        "do not authorize STATE creation/edit/removal", "coordination summaries/run records",
        "history/index updates", "reflection, candidate synthesis or evidence-only commits",
        "No renamed durable snapshot", "Leave historical records and existing STATE/custom content unchanged",
        "baseline/result SHAs and verification proof without duplicated persistence",
    ),
}


def contract_errors(text):
    errors = []
    for heading, clauses in GUARDS.items():
        marker = "## " + heading
        start = text.find(marker)
        end = text.find("\n## ", start + len(marker))
        body = " ".join((text[start:] if end < 0 else text[start:end]).split()) if start >= 0 else ""
        errors.extend(f"{heading}: missing {c}" for c in clauses if c not in body)
    for unsafe in ("Automatically initialize coordination memory", "Write a run SUMMARY on completion",
                   "Refresh the coordination index after every task", "Reflect at blocked pause",
                   "Commit evidence separately before the next task", "Infer lessons from failed runs"):
        if unsafe.lower() in text.lower():
            errors.append("bookkeeping: " + unsafe)
    return errors


def feedback_decision(kind, *, no_write=False, safe=True):
    """Authored symbolic feedback oracle; no skill execution or approval engine."""
    if no_write or kind in ("none", "explanation", "implementation-approval", "agent-observation"):
        return "no-write"
    if kind == "ambiguous":
        return "ask/no-write"
    return "write-guideline" if safe else "stop/no-write"


class CoordinationContractTests(unittest.TestCase):
    def test_shared_owner_contract(self):
        self.assertEqual(contract_errors(TEXT), [])

    def test_each_guidance_feedback_safety_and_nonpersistence_guard(self):
        for heading, clauses in GUARDS.items():
            for clause in clauses:
                with self.subTest(heading=heading, clause=clause):
                    normalized = " ".join(TEXT.split()).replace(" ## ", "\n## ")
                    altered = normalized.replace(clause, "REMOVED", 1) + "\n## Footer\n" + clause
                    self.assertTrue(any(e.startswith(heading + ":") for e in contract_errors(altered)))

    def test_routine_bookkeeping_resurrection_mutations(self):
        for unsafe in ("Automatically initialize coordination memory", "Write a run SUMMARY on completion",
                       "Refresh the coordination index after every task", "Reflect at blocked pause",
                       "Commit evidence separately before the next task", "Infer lessons from failed runs"):
            self.assertIn("bookkeeping: " + unsafe, contract_errors(TEXT + "\n" + unsafe))

    def test_clear_future_feedback_needs_no_second_approval(self):
        self.assertEqual(feedback_decision("clear-future-direction"), "write-guideline")

    def test_explanation_no_feedback_approval_observation_and_no_write(self):
        for kind in ("none", "explanation", "implementation-approval", "agent-observation"):
            self.assertEqual(feedback_decision(kind), "no-write")
        self.assertEqual(feedback_decision("clear-future-direction", no_write=True), "no-write")
        self.assertEqual(feedback_decision("ambiguous"), "ask/no-write")

    def test_dirty_concurrent_path_symlink_sensitive_and_owner_safety_stops(self):
        for gap in ("dirty ownership", "concurrent drift", "outside root", "symlink", "sensitive payload", "unknown owner"):
            with self.subTest(gap=gap):
                self.assertEqual(feedback_decision("clear-future-direction", safe=False), "stop/no-write")

    def test_absent_store_no_feedback_no_initialization(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for event in ("planning", "dispatch", "recovery", "review", "closeout", "blocked pause"):
                self.assertEqual(feedback_decision("none"), "no-write", event)
                self.assertEqual(list(root.iterdir()), [])

    def test_authorized_creation_is_guidelines_only_and_preserves_custom_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            custom = root / "custom.txt"
            custom.write_bytes(b"user content\n")
            self.assertEqual(feedback_decision("clear-future-direction"), "write-guideline")
            owner = root / "memory/coordination/GUIDELINES.md"
            owner.parent.mkdir(parents=True)
            owner.write_text("Trigger: future dispatch. Action: use direct async. User provenance: explicit feedback.\n")
            self.assertEqual(custom.read_bytes(), b"user content\n")
            self.assertEqual([p.name for p in owner.parent.iterdir()], ["GUIDELINES.md"])
            baseline = owner.read_bytes()
            for kind in ("none", "explanation", "ambiguous"):
                self.assertNotEqual(feedback_decision(kind), "write-guideline")
                self.assertEqual(owner.read_bytes(), baseline)

    def test_history_is_selective_no_match_retains_uncertainty(self):
        index = {"routing": "prior-routing", "unrelated": "prior-other"}
        self.assertEqual([v for k, v in index.items() if k == "routing"], ["prior-routing"])
        self.assertEqual([v for k, v in index.items() if k == "no-match"], [])
        self.assertEqual(contract_errors(TEXT), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
