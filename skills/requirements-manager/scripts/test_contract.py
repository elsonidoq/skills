#!/usr/bin/env python3
"""Static contract checks for the plan-free Requirements Manager."""
from pathlib import Path
import unittest

TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")


class RequirementsManagerContractTests(unittest.TestCase):
    def test_direct_requirement_is_durable_and_plan_free(self):
        self.assertIn("detailed prompt or explicitly selected source", TEXT)
        self.assertIn("Record its scope, acceptance", TEXT)
        self.assertIn("exclusions, constraints, source evidence", TEXT)
        self.assertIn("specification or plan is created", TEXT)
        self.assertIn("does not require a plan or SpecKit", TEXT)

    def test_shared_producers_and_direct_tasking_are_used(self):
        self.assertIn("`epic-brainstorming`", TEXT)
        self.assertIn("`task-generation`", TEXT)
        self.assertIn("direct adapter", TEXT)
        self.assertIn("context-coherent", TEXT)

    def test_route_approval_and_handoff_are_explicit(self):
        self.assertIn("best_practices_spec_driven_development.md", TEXT)
        self.assertIn("missing-install report", TEXT)
        self.assertIn("owner's route", TEXT)
        self.assertIn("explicit current owner approval", TEXT)
        self.assertIn("`coordinate-implementation`", TEXT)
        self.assertIn("coordinator alone selects execution", TEXT)
        self.assertIn("authorization to **prepare** tasks", TEXT)
        self.assertIn("approval order is:", TEXT)

    def test_capability_stops_and_stale_evidence_are_not_bypassed(self):
        self.assertIn("capability and stop", TEXT)
        self.assertIn("stale or unverifiable", TEXT)
        self.assertIn("to this manager's review gate", TEXT)


if __name__ == "__main__":
    unittest.main()
