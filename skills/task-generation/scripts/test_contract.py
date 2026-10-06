#!/usr/bin/env python3
"""Static checks for shared task-generation requirements."""

from pathlib import Path
import unittest


ROOT = Path(__file__).parents[3]
TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")
TINY_FIXTURE = (ROOT / "scripts/fixtures/planner/tiny-tasks.md").read_text(encoding="utf-8")
STANDARD_FIXTURE = (ROOT / "scripts/fixtures/planner/standard-tasks.md").read_text(encoding="utf-8")


class TaskGenerationContractTests(unittest.TestCase):
    def test_direct_and_speckit_adapters(self):
        self.assertIn("SpecKit adapter", TEXT)
        self.assertIn("direct adapter", TEXT)
        self.assertIn("does not\n  require a plan or SpecKit", TEXT)
        self.assertIn("authorization to\n**prepare** tasks", TEXT)
        self.assertIn("Do not require final task/implementation approval", TEXT)

    def test_context_coherence_preserves_dependency_order(self):
        self.assertIn("compatible selected family, binding, effort", TEXT)
        self.assertIn("do not reorder dependencies or pad a segment", TEXT)
        self.assertIn("Internal producer/consumer dependencies, shared files, and", TEXT)
        self.assertIn("phase/story headings may remain together", TEXT)
        self.assertIn("shared context and integration checkpoints", TEXT)

    def test_rejects_old_class_and_share_policy(self):
        self.assertNotIn("sonnet-class", TEXT)
        self.assertNotIn("opus-class", TEXT)
        self.assertNotIn("No more than 30%", TEXT)
        self.assertIn("no provider IDs, fixed family mappings, effort defaults, or family share cap", TEXT)

    def test_requires_independent_pending_routing_preview(self):
        self.assertIn("complete task-and-reviewer routing preview", TEXT)
        self.assertIn("least-adequate-effort rationale after decomposition", TEXT)
        self.assertIn("supported pairing without a qualifying benchmark row", TEXT)
        self.assertIn("Validate both adapters without imposing a Standard plan prerequisite", TEXT)

    def test_direct_fixture_has_safe_pending_selection(self):
        self.assertIn("direct adapter: no Standard\nplan is required", TINY_FIXTURE)
        self.assertIn("| Reviewer |", TINY_FIXTURE)
        self.assertIn("Pending owner selection", TINY_FIXTURE)
        self.assertIn("No matching benchmark row", TINY_FIXTURE)
        self.assertNotIn("Model class", TINY_FIXTURE)

    def test_standard_fixture_has_safe_pending_selection(self):
        self.assertIn("complete **pending** task/reviewer routing preview", STANDARD_FIXTURE)
        self.assertIn("| Reviewer |", STANDARD_FIXTURE)
        self.assertIn("Pending owner selection", STANDARD_FIXTURE)
        self.assertIn("Matching benchmark applicability is unknown", STANDARD_FIXTURE)
        self.assertNotIn("Model class", STANDARD_FIXTURE)


if __name__ == "__main__":
    unittest.main()
