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

    def test_context_coherence_preserves_dependency_order(self):
        self.assertIn("coherent sequential work", TEXT)
        self.assertIn("do not reorder dependencies or pad a segment", TEXT)
        self.assertIn("Internal producer/consumer dependencies, shared files, and phase/story headings may", TEXT)
        self.assertIn("shared\ncontext and integration checkpoints", TEXT)


if __name__ == "__main__":
    unittest.main()
