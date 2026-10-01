#!/usr/bin/env python3
"""Static contract checks for the shared brainstorming skill."""

from pathlib import Path
import unittest


SKILL = Path(__file__).parents[1] / "SKILL.md"


class EpicBrainstormingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_frontmatter_and_gate_outcomes(self):
        self.assertIn("name: epic-brainstorming", self.text)
        self.assertIn("description: Use when", self.text)
        self.assertIn("`NO_BRAINSTORM_NEEDED`", self.text)
        self.assertIn("`BRAINSTORM_NEEDED`", self.text)
        self.assertIn("Bias toward `NO_BRAINSTORM_NEEDED`", self.text)

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

    def test_capability_stop_and_portable_binding(self):
        self.assertIn("owner-selected `sonnet-class` binding", self.text)
        self.assertIn("missing capability and stop before downstream production", self.text)
        self.assertNotIn("openai-", self.text)
        self.assertNotIn("anthropic/", self.text)


if __name__ == "__main__":
    unittest.main()
