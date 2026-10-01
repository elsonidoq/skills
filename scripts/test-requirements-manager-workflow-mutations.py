#!/usr/bin/env python3
"""Named in-memory negative mutations for operational workflow checks."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

CHECKER_PATH = Path(__file__).with_name("check-requirements-manager-workflow.py")
spec = importlib.util.spec_from_file_location("workflow_checker", CHECKER_PATH)
checker = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(checker)


class WorkflowMutationTests(unittest.TestCase):
    def setUp(self): self.texts = checker.load_texts()

    def mutate(self, name, key, old, new, diagnostic):
        self.assertIn(old, self.texts[key], f"fixture for {name} is stale")
        changed = self.texts.copy(); changed[key] = changed[key].replace(old, new, 1)
        errors = checker.check_contracts(changed)
        self.assertTrue(any(item.startswith(diagnostic) for item in errors), f"{name}: {errors}")

    def test_stage_body_block_class_and_order(self):
        text = self.texts["epic"]
        body = checker.section(text, "brainstorm_gate")
        self.assertTrue(body)
        changed = self.texts.copy(); changed["epic"] = text.replace(body, "### `brainstorm_gate` — `sonnet-class`\n", 1)
        self.assertTrue(any(e.startswith("stage-brainstorm_gate:") for e in checker.check_contracts(changed)))
        self.mutate("change specification class", "epic", "### `spec_create` — `sonnet-class`", "### `spec_create` — `opus-class`", "stage-class-spec_create:")
        first, second = "### `spec_create`", "### `plan_create`"
        changed = self.texts.copy(); changed["epic"] = text.replace(first, "TEMP", 1).replace(second, first, 1).replace("TEMP", second, 1)
        self.assertTrue(any(e.startswith("epic-order:") for e in checker.check_contracts(changed)))

    def test_transitions_ownership_and_recovery(self):
        self.mutate("bypass gate transition", "epic", "skip goes to `spec_create`; needed goes to `epic_brainstorm`", "skip continues", "gate-transition:")
        self.mutate("remove plan review fix", "epic", "review the created plan", "review the artifact", "plan-transition:")
        self.mutate("remove create-only ownership", "epic", "task defects belong to `overall_review`", "task defects are fixed here", "task-ownership:")
        self.mutate("remove owner approval", "epic", "explicit overall-review approval", "review approval", "review-approval:")
        self.mutate("remove stale recovery", "epic", "return\nto the earliest affected stage", "continue from any stage", "stale-recovery:")
        self.mutate("remove reading handoff", "epic", "prior-stage handoff", "previous notes", "reading-handoff:")

    def test_capability_briefing_and_producer_mutations(self):
        self.mutate("remove constitution", "epic", "template-only content", "generic content", "constitution:")
        self.mutate("remove required reference", "epic", "Read [`../../docs/best_practices_spec_driven_development.md`](../../docs/best_practices_spec_driven_development.md)", "Read the reference", "reference-sizing:")
        self.mutate("remove stage briefing", "epic", "specification and\nclarification summary", "summary", "briefings:")
        self.mutate("remove prepare authorization", "requirements", "authorization to **prepare** tasks", "authorization", "direct-route:")

    def test_actual_contradictory_policy_insertions(self):
        self.mutate("mandatory direct plan", "requirements", "## 3. Produce direct tasks", "Direct requirements must have a plan.\n\n## 3. Produce direct tasks", "mandatory-direct-plan:")
        self.mutate("automatic stage split", "coordinator", "## Build the Execution Graph", "Automatically split at stage headings.\n\n## Build the Execution Graph", "automatic-batch-split:")
        self.mutate("automatic file split", "coordinator", "## Build the Execution Graph", "Automatically split shared files.\n\n## Build the Execution Graph", "automatic-batch-split:")
        self.mutate("automatic dependency split", "coordinator", "## Build the Execution Graph", "Automatically split internal dependencies.\n\n## Build the Execution Graph", "automatic-batch-split:")
        self.mutate("permit parallel", "coordinator", "## Build the Execution Graph", "Parallel implementation batches are permitted.\n\n## Build the Execution Graph", "unsafe-execution:")
        self.mutate("permit foreground", "coordinator", "## Build the Execution Graph", "Foreground delegation is permitted.\n\n## Build the Execution Graph", "unsafe-execution:")
        self.mutate("permit regrouping", "coordinator", "## Build the Execution Graph", "Regroup dependencies to fill batches.\n\n## Build the Execution Graph", "unsafe-execution:")
        self.mutate("permit batch commits", "coordinator", "## Build the Execution Graph", "Batch commits replace task commits.\n\n## Build the Execution Graph", "unsafe-execution:")

    def test_custom_directory_lint_reports_suite_check_skip(self):
        script = CHECKER_PATH.with_name("check-skills-lint.sh")
        with tempfile.TemporaryDirectory() as candidate:
            run = subprocess.run(["bash", str(script), candidate], text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("SKIP requirements-manager workflow checks (custom skills directory", run.stdout)

    def test_material_default_and_legacy(self):
        self.mutate("allow material default", "epic", "## Decision and handoff discipline", "Apply an unresolved material default.\n\n## Decision and handoff discipline", "material-default:")
        changed = self.texts.copy(); changed["epic"] += "\nOpenCode\n"
        self.assertTrue(any(e.startswith("legacy:") for e in checker.check_contracts(changed)))


if __name__ == "__main__": unittest.main()
