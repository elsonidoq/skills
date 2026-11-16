#!/usr/bin/env python3
"""Static obligations and removal sensitivity, not live dialogue proof."""

from pathlib import Path
import unittest
import re


SKILL = Path(__file__).parents[1] / "SKILL.md"


class PlanningBrainstormingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def require(self, heading, clauses):
        carrier = re.sub(r"```.*?```", "", self.text, flags=re.S)
        carrier = carrier.split(heading, 1)[1].split("\n## ", 1)[0]
        carrier = " ".join(carrier.split())
        for clause in clauses:
            with self.subTest(clause=clause):
                self.assertIn(clause, carrier)
                self.assertNotIn(clause, carrier.replace(clause, "REMOVED", 1))

    def test_frontmatter_and_gate_outcomes(self):
        self.assertIn("name: planning-brainstorming", self.text)
        self.assertIn("description: Use when", self.text)
        self.require("## Judge readiness", (
            "`NO_BRAINSTORM_NEEDED`", "`BRAINSTORM_NEEDED`", "Bias toward this result",
            "direction is settled", "blocks readiness", "read-only", "retain answers in session history",
            "Create no source, decision or state files, including for resume",
        ))

    def test_parent_gate_needs_no_child_or_saved_assignment(self):
        self.require("# Planning Brainstorming", (
            "parent conducts assessment and dialogue", "owner-launched model and effort",
            "neither requires a child call or a saved assignment",
            "does not choose TinySpec/Standard",
        ))
        self.require("## Resolve the material questions with the owner", (
            "missing delegation alone does not block parent dialogue",
        ))

    def test_bounded_agenda_and_owner_dialogue(self):
        self.require("## Judge readiness", (
            "no more than three items", "two to four concrete alternatives",
            "`open-design`, `product-decision` or `technical-tradeoff`", "blocking reason",
        ))
        self.require("## Resolve the material questions with the owner", (
            "parent, not a delegated worker", "one agenda item at a time", "owner's rationale",
            "Record deferrals and their rationale", "ask in prose and end the turn",
            "Missing answers, cancellation or unavailable dialogue never authorize inferred decisions",
            "A caller's mandatory preflight can stop earlier",
        ))

    def test_exact_bounded_application_and_recovery(self):
        self.require("## Apply and return the decisions", (
            "exactly the recorded decisions", "do not expand scope or rewrite unrelated sections",
            "Re-present the saved agenda", "repeat the applicability consultation above",
            "If source or decisions changed materially, run the readiness judgment again",
            "task-commit contract", "Read-only preselection creates no empty commit",
        ))
        self.require("## Judge readiness", (
            "Memory Handling", "[save-adr](../save-adr/SKILL.md#consult-and-propagate)", "fresh or resumed standalone entry",
            "even if the caller did not supply them", "An absent decision store alone is nonblocking",
        ))

    def test_shared_saved_assignment_dispatch_and_capability_stop(self):
        self.require("## Apply and return the decisions", (
            "Only with selected-production or legacy-repair write authority",
            "Resolve `brainstorm-application`",
            "[saved-assignment contract](../planner/SKILL.md#saved-planner-assignments)",
            "shared `brainstorming` assignment", "exact binding unchanged in the brief and dispatch",
            "permitted and callable at dispatch", "stops only application",
            "focused correction question", "no recommendation, inferred substitute or fallback binding",
            "Do not resolve `brainstorm-assessment` for the parent",
        ))
        for retired in ("qualified seed rubric", "six applicable factors", "family/effort",
                        "Family and Effort rationales", "shared readiness conjunction",
                        "owner-selected profile"):
            self.assertNotIn(retired, self.text)


if __name__ == "__main__":
    unittest.main()
