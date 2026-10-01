#!/usr/bin/env python3
"""Static checks for context-continuity batching instructions."""

from pathlib import Path
import unittest


TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")


class BatchingContractTests(unittest.TestCase):
    def test_coherent_sequential_work_is_not_split_by_incidental_boundaries(self):
        self.assertIn("amortize startup and retain\n   useful context", TEXT)
        self.assertIn("Internal dependencies, shared files, and phase/story headings do not require", TEXT)
        self.assertIn("verifies each producer before its\n   consumer", TEXT)
        self.assertIn("commits each task separately", TEXT)

    def test_only_evidenced_boundaries_split_and_order_stays_fixed(self):
        self.assertIn("Aim for 5–7 tasks only when scope and observed context permit", TEXT)
        self.assertIn("model-class changes, owner gates, context limits, genuinely incompatible scope", TEXT)
        self.assertIn("Never pull\n   a distant producer forward or reorder a prerequisite", TEXT)
        self.assertIn("delegate only asynchronously in the background", TEXT)
        self.assertIn("never\n   run implementation batches in parallel", TEXT)

    def test_rotation_uses_observed_context_and_durable_handoff(self):
        self.assertIn("observed context\n  headroom is adequate", TEXT)
        self.assertIn("smaller fresh brief with durable handoff context", TEXT)


if __name__ == "__main__":
    unittest.main()
