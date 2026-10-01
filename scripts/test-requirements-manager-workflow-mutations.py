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
        spec, plan = checker.section(text, "spec_create"), checker.section(text, "plan_create")
        changed = self.texts.copy(); changed["epic"] = text.replace(spec, "TEMP", 1).replace(plan, spec, 1).replace("TEMP", plan, 1)
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

    def test_required_operational_omissions(self):
        self.mutate("remove fix application", "epic", "apply exactly those decisions", "apply decisions", "brainstorm-fix-application:")
        self.mutate("remove specification approval", "epic", "obtain and durably record explicit approval of the current", "obtain approval", "spec-approval:")
        self.mutate("remove approval renewal", "epic", "renew specification approval", "renew approval", "plan-transition:")
        self.mutate("remove constitution verification", "epic", "verify the resulting detected constitution is usable", "verify constitution", "constitution:")
        self.mutate("remove capability stop", "epic", "If a required capability is unavailable, stop at the affected stage", "capability check", "epic-capability-stop:")
        self.mutate("remove per-task commits", "coordinator", "Commit each task's verified changes as one focused commit", "Commit changes", "commit-review:")
        self.mutate("remove independent final review", "coordinator", "fresh independent\nfinal review", "final review", "commit-review:")
        self.mutate("remove async-only", "coordinator", "only asynchronously in the background", "asynchronously", "async-delegation:")
        self.mutate("remove local eligibility", "coordinator", "scope is clear", "scope", "eligibility:")
        self.mutate("remove delegation threshold", "coordinator", "More than three implementation tasks require delegation", "Many tasks delegate", "delegation-count:")
        self.mutate("remove upstream coherence", "epic", "do not reorder dependencies or pad distant work", "preserve dependencies", "upstream-epic-coherence:")
        self.mutate("remove selected class eligibility", "coordinator", "current owner-selected model/class matches each task", "selected class", "eligibility:")
        self.mutate("remove context eligibility", "coordinator", "observed context capacity is adequate", "context", "eligibility:")
        self.mutate("remove completed full count", "coordinator", "including completed tasks", "including tasks", "threshold:")
        self.mutate("remove review exclusion", "coordinator", "exclude standalone review tasks", "exclude reviews", "threshold:")

    def test_shared_invocation_and_conditional_transition_mutations(self):
        text = self.texts["requirements"]
        start = text.index("## 2. Resolve only material uncertainty")
        end = text.index("\n## 3.", start)
        changed = self.texts.copy(); changed["requirements"] = text[:start] + text[end + 1:]
        errors = checker.check_contracts(changed)
        self.assertTrue(any(e.startswith("requirements-operational-brainstorm:") for e in errors), errors)
        self.mutate("bypass brainstorm fix", "epic", "`epic_brainstorm_fix`.", "`spec_create`.", "brainstorm-output-transition:")
        self.mutate("bypass fix to specification", "epic", "context for `spec_create`", "context for `tasks_create`", "brainstorm-fix-output-transition:")

    def test_actual_contradictory_policy_insertions(self):
        self.mutate("mandatory direct plan", "requirements", "## 3. Produce direct tasks", "Direct requirements must have a plan.\n\n## 3. Produce direct tasks", "mandatory-direct-plan:")
        self.mutate("mandatory direct plan in shared tasks", "tasks", "# Task Generation", "# Task Generation\n\nDirect requirements must have a plan.", "mandatory-direct-plan:")
        self.mutate("mandatory direct plan in coordinator", "coordinator", "# Coordinate Implementation", "# Coordinate Implementation\n\nDirect requirements must have a plan.", "mandatory-direct-plan:")
        self.mutate("automatic split upstream", "tasks", "# Task Generation", "# Task Generation\n\nAutomatically split at stage headings.", "automatic-batch-split:")
        self.mutate("automatic split EPIC", "epic", "# EPIC Manager", "# EPIC Manager\n\nAutomatically split shared files.", "automatic-batch-split:")
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
