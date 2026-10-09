#!/usr/bin/env python3
"""Static checks for shared task-generation requirements."""

from pathlib import Path
import unittest


TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")


class TaskGenerationContractTests(unittest.TestCase):
    def test_practical_ordinary_contract_and_named_removals(self):
        contract = TEXT.split("## Task contract", 1)[1].split("## Review and handoff", 1)[0]
        review = TEXT.split("## Review and handoff", 1)[1].split("## Mandatory", 1)[0]
        for carrier, clause in ((contract, "Use practical observables"), (contract, "item mappings"),
                                (review, "inadequate approved/legacy contracts"),
                                (review, "producing review/renewal")):
            self.assertIn(clause, carrier)
            self.assertNotIn(clause, carrier.replace(clause, "REMOVED"))
        # Concrete ordinary wiring oracle: optional green cannot conceal changed IDs.
        ordinary = {"ref": "T001/V1", "criterion": "ID reaches consumer unchanged",
                    "expected": "chosen-7", "check": "existing argument fixture",
                    "evidence": "captured consumer ID", "manual": None, "permission": "local"}
        self.assertEqual(ordinary["expected"], "chosen-7")
        self.assertNotEqual(ordinary["expected"], "default-1")
        self.assertIsNone(ordinary["manual"])
        self.assertIn("Both adapters", contract)

    def test_guidance_changes_dependency_check_and_brief_in_both_adapters(self):
        preflight = TEXT.split("## Preconditions and adapters", 1)[1].split("## Task contract", 1)[0]
        for clause in ("including direct entry without planner", "relevant decision",
                       "dependency/check and coordinator brief", "not merely a link"):
            self.assertIn(clause, preflight)
            self.assertNotIn(clause, preflight.replace(clause, "REMOVED", 1))

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
