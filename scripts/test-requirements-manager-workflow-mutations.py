#!/usr/bin/env python3
"""Named in-memory negative mutations for workflow-contract enforcement."""
import importlib.util
from pathlib import Path
import unittest

CHECKER_PATH = Path(__file__).with_name("check-requirements-manager-workflow.py")
spec = importlib.util.spec_from_file_location("workflow_checker", CHECKER_PATH)
checker = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(checker)


class WorkflowMutationTests(unittest.TestCase):
    def setUp(self):
        self.texts = checker.load_texts()

    def assert_mutation_fails(self, name, key, old, expected):
        self.assertIn(old, self.texts[key], f"fixture for {name} is stale")
        mutated = self.texts.copy()
        mutated[key] = mutated[key].replace(old, "REMOVED", 1)
        failures = checker.check_contracts(mutated)
        self.assertTrue(any(item.startswith(expected) for item in failures),
                        f"{name} did not produce {expected}: {failures}")

    def test_named_operational_stage_and_order_mutations(self):
        self.assert_mutation_fails("remove operational body with diagram intact", "epic",
                                   "### `plan_create` — `opus-class`", "epic-order:")
        mutated = self.texts.copy()
        text = mutated["epic"]
        first, second = "### `spec_create`", "### `plan_create`"
        self.assertLess(text.index(first), text.index(second))
        mutated["epic"] = text.replace(first, "TEMP", 1).replace(second, first, 1).replace("TEMP", second, 1)
        self.assertTrue(any(item.startswith("epic-order:") for item in checker.check_contracts(mutated)))

    def test_named_shared_gate_review_and_capability_mutations(self):
        self.assert_mutation_fails("remove shared invocation", "epic", "shared `epic-brainstorming`", "shared-gate:")
        self.assert_mutation_fails("remove create-only", "epic", "This stage is create-only", "shared-gate:")
        self.assert_mutation_fails("remove approval renewal", "epic", "renew specification approval", "shared-gate:")
        self.assert_mutation_fails("remove capability stop", "brainstorm", "If a required capability is unavailable, report", "brainstorm:")

    def test_named_direct_route_and_strategy_mutations(self):
        self.assert_mutation_fails("reinstate mandatory direct plan", "requirements",
                                   "It does not require a plan or SpecKit.", "direct-route:")
        self.assert_mutation_fails("change threshold", "coordinator",
                                   "Up to three bounded implementation tasks may run locally", "threshold:")
        self.assert_mutation_fails("remove class-context suitability", "coordinator",
                                   "current owner-selected model/class matches each task", "threshold:")

    def test_named_batching_and_upstream_mutations(self):
        self.assert_mutation_fails("automatic heading/file/dependency split", "coordinator",
                                   "Internal dependencies, shared files, and phase/story headings do not require", "context-batching:")
        self.assert_mutation_fails("remove upstream coherence", "tasks", "coherent sequential work", "upstream-coherence:")
        self.assert_mutation_fails("permit dependency regrouping", "tasks", "do not reorder dependencies or pad", "upstream-coherence:")
        self.assert_mutation_fails("permit parallel delegation", "coordinator",
                                   "never\n   run implementation batches in parallel", "context-batching:")
        self.assert_mutation_fails("permit foreground delegation", "coordinator",
                                   "only asynchronously in the background", "context-batching:")

    def test_named_commit_review_and_legacy_mutations(self):
        self.assert_mutation_fails("remove per-task commits", "coordinator",
                                   "Commit each task's verified changes as one focused commit", "commit-review:")
        self.assert_mutation_fails("remove independent review", "coordinator",
                                   "full committed revision range", "commit-review:")
        mutated = self.texts.copy()
        mutated["epic"] += "\nOpenCode\n"
        self.assertTrue(any(item.startswith("legacy:") for item in checker.check_contracts(mutated)))


if __name__ == "__main__":
    unittest.main()
