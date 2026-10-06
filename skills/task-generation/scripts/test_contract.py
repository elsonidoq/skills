#!/usr/bin/env python3
"""Static checks for shared task-generation requirements."""

from pathlib import Path
import unittest


TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")


class TaskGenerationContractTests(unittest.TestCase):
    def test_direct_and_speckit_adapters(self):
        self.assertIn("SpecKit adapter", TEXT)
        self.assertIn("direct adapter", TEXT)
        self.assertIn("does not\n  require a plan or SpecKit", TEXT)
        self.assertIn("authorization to\n**prepare** tasks", TEXT)
        self.assertIn("Do not require final task/implementation approval", TEXT)

    def test_objective_items_replace_task_profile_allocation(self):
        for obsolete in ("sonnet-class", "opus-class", "30%", "same-class", "class share"):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, TEXT)
        for required in (
            "stable task-local references", "T001/V1", "pass criterion",
            "smallest sufficient check", "expected evidence", "manual/permission gates",
            "REQUIRED", "optional checks separately", "files or interfaces",
            "required capabilities", "shared context", "not an execution assignment",
            "producing review/approval gate", "Do not fabricate historical contracts",
            "../coordinate-implementation/references/batch-routing.md",
        ):
            with self.subTest(required=required):
                self.assertIn(required, TEXT)

    def test_adapter_legacy_and_checkpoint_boundaries_remain(self):
        self.assertIn("Existing task-embedded requirements remain valid for legacy", TEXT)
        self.assertIn("Keep the stage create-only", TEXT)
        self.assertIn("separate source and tasks file", TEXT)
        self.assertIn("task-commit contract", TEXT)
        self.assertIn("checkpointing it separately", TEXT)

    def test_context_coherence_preserves_dependency_order(self):
        self.assertIn("coherent sequential work", TEXT)
        self.assertIn("do not reorder dependencies or pad a segment", TEXT)
        self.assertIn("Internal producer/consumer dependencies, shared files, and phase/story headings may", TEXT)
        self.assertIn("shared\ncontext and integration checkpoints", TEXT)


if __name__ == "__main__":
    unittest.main()
