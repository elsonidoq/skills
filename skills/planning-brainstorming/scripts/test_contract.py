#!/usr/bin/env python3
"""Static contract checks for the shared brainstorming skill."""

from pathlib import Path
import unittest


SKILL = Path(__file__).parents[1] / "SKILL.md"


class PlanningBrainstormingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_frontmatter_and_gate_outcomes(self):
        self.assertIn("name: planning-brainstorming", self.text)
        self.assertIn("description: Use when", self.text)
        self.assertIn("`NO_BRAINSTORM_NEEDED`", self.text)
        self.assertIn("`BRAINSTORM_NEEDED`", self.text)
        self.assertIn("Bias toward `NO_BRAINSTORM_NEEDED`", self.text)

    def test_parent_gate_needs_no_child_or_saved_assignment(self):
        self.assertIn("Gate assessment runs directly in the parent session", self.text)
        self.assertIn("owner-launched model and effort", self.text)
        self.assertIn("Do not delegate the gate or resolve a saved `brainstorm-assessment` binding", self.text)
        self.assertIn("A settled request\nneeds no child call", self.text)
        self.assertIn("missing delegation capability or a saved brainstorming assignment does not\nblock parent assessment or owner dialogue", self.text)
        self.assertIn("The parent assesses readiness without a subagent call", self.text)

    def test_bounded_agenda_and_owner_dialogue(self):
        self.assertIn("no more than three items", self.text)
        self.assertIn("two to four concrete alternatives", self.text)
        self.assertIn("The orchestrator, not a delegated worker", self.text)
        self.assertIn("at a time through the available question capability", self.text)

    def test_exact_bounded_application_and_recovery(self):
        self.assertIn("apply exactly the recorded owner decisions", self.text)
        self.assertIn("Do not invent scope", self.text)
        self.assertIn("re-present the saved agenda", self.text)
        self.assertIn("Record owner deferrals", self.text)

    def test_shared_saved_assignment_dispatch_and_capability_stop(self):
        self.assertIn("Only for authorized delegated decision application, resolve `brainstorm-application`", self.text)
        self.assertIn("[shared saved-assignment contract](../planner/SKILL.md#saved-planner-assignments)", self.text)
        self.assertIn("shared saved `brainstorming` assignment", self.text)
        self.assertIn("exact binding\nunchanged in the bounded brief and dispatch", self.text)
        self.assertIn("permitted and callable only\nat dispatch", self.text)
        self.assertIn("focused owner-correction question and no\ncandidate recommendation, inference, substitution, or fallback", self.text)
        self.assertIn("The parent still\nconducts owner dialogue", self.text)
        self.assertIn("Only in selected-production or legacy-repair mode", self.text)
        self.assertIn("missing capability and stop before downstream production", self.text)
        self.assertIn("ask in prose and end the turn", self.text)
        self.assertIn("do not continue downstream or infer an", self.text)
        for retired in ("qualified seed rubric", "six applicable factors", "family/effort",
                        "Family and Effort rationales", "shared readiness conjunction",
                        "owner-selected profile"):
            self.assertNotIn(retired, self.text)


if __name__ == "__main__":
    unittest.main()
