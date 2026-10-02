#!/usr/bin/env python3
"""Static coordinator intake/strategy checks; not proof of runtime obedience."""

from pathlib import Path
import unittest

TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")


class IntakeContractTests(unittest.TestCase):
    def test_origin_specific_authorization(self):
        for phrase in (
            "specification, plan, tasks, both current approvals",
            "Standard depth", "TinySpec depth",
            "separate TinySpec/source and tasks", "embedded in tasks",
            "Missing/conflicting depth", "approval/recovery mapping",
            "required SpecKit stage evidence",
            "legacy `requirements-manager` origin",
            "requirement/source, tasks, review evidence",
            "No specification, plan, or SpecKit prerequisite is required",
            "For other documented origins",
            "Ambiguous origin is a blocker",
            "missing, stale, or unverifiable",
        ):
            self.assertIn(phrase, TEXT)
        self.assertNotIn("This skill still requires a spec, plan, and tasks", TEXT)
        self.assertIn("Installation alone does not make SpecKit applicable", TEXT)

    def test_complete_count_and_resume(self):
        for phrase in (
            "complete approved implementation task list",
            "exclude standalone review tasks",
            "not origin, plan presence, or remaining task count",
            "Up to three bounded implementation tasks",
            "More than three implementation tasks require delegation",
            "Retain the recorded strategy on resume",
            "Completing tasks alone never changes delegated execution to local",
        ):
            self.assertIn(phrase, TEXT)

    def test_local_suitability_and_common_graph(self):
        for phrase in (
            "current owner-selected model/class matches",
            "observed context capacity is adequate",
            "delegate the affected task or segment",
            "Both routes use this single execution graph",
            "never silently switch models or downgrade task classes",
            "No unauthorized local fallback",
            "producing workflow's review gate",
        ):
            self.assertIn(phrase, TEXT)
        self.assertEqual(TEXT.count("## Build the Execution Graph"), 1)
        self.assertNotIn("Delegation is mandatory for implementation", TEXT)

    def test_capabilities_context_and_inspected_failures(self):
        for phrase in (
            "fresh independent reviewer",
            "no forced one-session-per-class limit",
            "Inspect the failed run and tool invocation before retry or relaunch",
            "If context metrics are unavailable",
            "Agent/model selection: UNAVAILABLE",
            "Delegation: UNAVAILABLE",
        ):
            self.assertIn(phrase, TEXT)

    def test_task_commits_and_one_final_review(self):
        self.assertIn("Commit each task's verified changes as one focused commit", TEXT)
        self.assertIn("No per-task reviews", TEXT)
        self.assertIn("full committed revision range", TEXT)
        self.assertIn("not merely a clean working-tree diff", TEXT)
        self.assertNotIn("per-batch commit", TEXT)

    def test_origin_neutral_downstream_references(self):
        self.assertIn("applicable source/supporting artifacts", TEXT)
        self.assertNotIn("Review accumulated changes against the spec, plan, tasks", TEXT)


if __name__ == "__main__":
    unittest.main()
