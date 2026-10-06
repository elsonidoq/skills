#!/usr/bin/env python3
"""Static checks for context-continuity batching instructions."""

from pathlib import Path
import unittest


TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")


RUBRIC_PATH = Path(__file__).parents[1] / "references" / "batch-routing.md"


class SeedRubricTests(unittest.TestCase):
    def test_six_factors_and_independent_profile_dimensions(self):
        self.assertTrue(RUBRIC_PATH.is_file(), "shared batch routing seed is missing")
        rubric = RUBRIC_PATH.read_text(encoding="utf-8")
        for factor in (
            "Residual reasoning", "Agentic/tool depth", "Verification blind spots",
            "Scope/coupling", "Failure cost/reversibility", "Applicable approved guidance",
        ):
            with self.subTest(factor=factor):
                self.assertIn(factor, rubric)
        for term in (
            "Family rationale", "Effort rationale", "Luna/medium", "Luna/max",
            "Sol/low", "Sol/medium", "Astra", "Terra", "no universal ladder",
        ):
            with self.subTest(term=term):
                self.assertIn(term, rubric)

    def test_qualified_prior_authority_and_repair_limits(self):
        self.assertTrue(RUBRIC_PATH.is_file(), "shared batch routing seed is missing")
        rubric = RUBRIC_PATH.read_text(encoding="utf-8")
        for term in (
            "different harnesses", "Do not average", "benchmark-only eligibility",
            "empty guidelines", "override the seed", "owner/source authority",
            "unresolved architecture", "weak oracles", "deep tool use",
            "high failure cost", "repeated negative guidance", "supported effort",
            "callable binding", "unknown", "diagnose", "invalidated",
        ):
            with self.subTest(term=term):
                self.assertIn(term, rubric)
        self.assertIn("../../../specs/002-batch-routing-contracts/research.md", rubric)


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
