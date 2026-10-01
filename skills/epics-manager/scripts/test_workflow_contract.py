#!/usr/bin/env python3
"""Static operational-contract checks for the EPIC manager skill."""

from pathlib import Path
import unittest


TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")


class EpicWorkflowContractTests(unittest.TestCase):
    def test_operational_stage_order_and_classes(self):
        chain = "epic_brainstorm_fix]\n  → spec_create → plan_create → tasks_create → overall_review → done"
        self.assertIn("brainstorm_gate", TEXT)
        self.assertIn(chain, TEXT)
        self.assertIn("### `brainstorm_gate` — `sonnet-class`", TEXT)
        self.assertIn("### `epic_brainstorm_fix` — `sonnet-class`", TEXT)
        self.assertIn("### `spec_create` — `sonnet-class`", TEXT)
        self.assertIn("### `plan_create` — `opus-class`", TEXT)
        self.assertIn("### `tasks_create` — `sonnet-class`", TEXT)

    def test_shared_gate_and_create_review_ownership(self):
        self.assertIn("shared `epic-brainstorming`", TEXT)
        self.assertIn("shared `task-generation`", TEXT)
        self.assertIn("This stage is create-only", TEXT)
        self.assertIn("task defects belong to `overall_review`", TEXT)
        self.assertIn("one same-session pass", TEXT)

    def test_upstream_prepares_coherent_work_without_reordering(self):
        self.assertIn("coherent consecutive\nsame-class work", TEXT)
        self.assertIn("do not reorder dependencies or pad distant work", TEXT)
        self.assertIn("producer checks and shared-context\nnotes", TEXT)

    def test_approvals_resume_and_capability_stops(self):
        self.assertIn("renew specification approval", TEXT)
        self.assertIn("explicit overall-review approval", TEXT)
        self.assertIn("Resume from the earliest missing, stale, or inconsistent", TEXT)
        self.assertIn("If a required capability is unavailable, stop", TEXT)
        self.assertIn("observed permitted independent reviewer", TEXT)

    def test_restored_source_constitution_and_approval_contracts(self):
        self.assertIn("best_practices_spec_driven_development.md", TEXT)
        self.assertIn("missing-install report", TEXT)
        self.assertIn("template-only content", TEXT)
        self.assertIn("owner-derived principles", TEXT)
        self.assertIn("substantive scope change", TEXT)
        self.assertIn("documentation-initialization exception", TEXT)
        self.assertIn("settled and non-obvious constraints **verbatim**", TEXT)
        self.assertIn("prior-stage handoff", TEXT)
        self.assertIn("never apply an unresolved\nmaterial default", TEXT)
        self.assertIn("specification and\nclarification summary", TEXT)
        self.assertIn("outcome and plan-phase briefing", TEXT)
        self.assertIn("review the created plan", TEXT)
        self.assertIn("authorization to\nprepare tasks", TEXT)


if __name__ == "__main__":
    unittest.main()
