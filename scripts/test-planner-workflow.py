#!/usr/bin/env python3
"""Offline contract/mutation/trace/installer/RPC-driver tests. No model calls."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import re
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = load("checker", "check-planner-workflow.py")
trace = load("trace", "planner-trace.py")
links = load("links", "install-links.py")
rpc = load("rpc", "planner-rpc-smoke.py")


class PlanningCommitAuthorityTests(unittest.TestCase):
    """Static regression guard, not proof of runtime model compliance."""

    def test_planning_commit_authority_is_explicit_and_required(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        clauses = (
            "writing and committing the selected path's bounded planning artifacts",
            "Do not ask for separate\nplanning-commit authorization",
            "or defer these checkpoints until artifact approval",
            "Artifact approvals govern content and downstream progression",
            "Pass this commit authority unchanged to\nplanning delegates",
            "Genuine Git, policy, verification or ownership conflicts stop",
        )
        for clause in clauses:
            with self.subTest(removed=clause):
                changed = dict(texts)
                changed["planner"] = changed["planner"].replace(clause, "REMOVED", 1)
                self.assertTrue(any(
                    error.startswith("planning-commit-authority:")
                    for error in checker.check_contracts(changed)
                ))


class EarlyRiskReductionTests(unittest.TestCase):
    """Offline instruction sensitivity; no real library or model-obedience proof."""

    def test_shared_risk_owner_is_required(self):
        self.assertIn("risk", checker.PATHS)
        texts = checker.load_texts()
        del texts["risk"]
        self.assertTrue(any(e.startswith("risk-reference:") for e in checker.check_contracts(texts)))

    def test_risk_clause_removals_have_named_diagnostics(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        for label, key, heading, clauses in checker.RISK_CARRIERS:
            for clause in clauses:
                with self.subTest(diagnostic=label, removed=clause):
                    changed = dict(texts)
                    body = checker.section(changed[key], heading)
                    self.assertIn(" ".join(clause.split()), " ".join(body.split()))
                    pattern = r"\s+".join(re.escape(word) for word in clause.split())
                    changed[key] = changed[key].replace(body, re.sub(pattern, "REMOVED", body), 1)
                    errors = checker.check_contracts(changed)
                    self.assertTrue(any(e.startswith(label + ":") for e in errors), errors)

    def test_risk_carrier_removal_and_summary_only_replacement(self):
        texts = checker.load_texts()
        for label, key, heading, _ in checker.RISK_CARRIERS:
            for replacement in ("", heading + "\n"):
                with self.subTest(carrier=label, replacement=replacement):
                    changed = dict(texts)
                    body = checker.section(changed[key], heading)
                    changed[key] = changed[key].replace(body, replacement, 1) + "\n## Summary only\n" + body.replace(heading, "Summary of removed carrier", 1)
                    self.assertTrue(any(e.startswith(label + ":") for e in checker.check_contracts(changed)))

    def test_risk_missing_wrong_reference_and_distributed_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in set(checker.PATHS.values()):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((ROOT / path).read_text())
            for key in ("planner", "tiny", "helper", "tasks"):
                target = root / checker.PATHS[key]
                original = target.read_text()
                for wrong in ("absent.md", "dependency-research.md"):
                    target.write_text(original.replace("early-risk-reduction.md", wrong))
                    with self.assertRaisesRegex(ValueError, "risk-reference: " + key):
                        checker.load_texts(root)
                target.write_text(original)
            (root / checker.PATHS["risk"]).unlink()
            with self.assertRaisesRegex(ValueError, "risk-reference:"):
                checker.load_texts(root)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("planner", "tiny-spec", "delegating-architectural-planning", "task-generation"):
                (root / name).symlink_to(ROOT / "skills" / name, target_is_directory=True)
                relative = ("references/early-risk-reduction.md" if name == "planner"
                            else "../planner/references/early-risk-reduction.md")
                self.assertEqual((root / name / relative).resolve(), (ROOT / checker.PATHS["risk"]).resolve())
                self.assertIn("# Early technical risk reduction", (root / name / relative).read_text())

    def assert_risk_adapter_semantics(self, source):
        # Bounded expected-fixture assertions, not a generic semantic task validator.
        blocks = re.split(r"(?m)^- \[ \] T\d+", source)[1:]
        self.assertEqual(len(blocks), 3)
        producer, consumer, cleanup = blocks
        for block in blocks:
            for field in ("Outcome", "Files/interfaces", "Acceptance", "Capabilities", "Depends"):
                self.assertIn(f"**{field}**", block)
            for field in ("REQUIRED", "Pass:", "Smallest check:", "Evidence:", "Gate:"):
                self.assertIn(field, block)
        for phrase in ("real dependency/runtime", "representative and adversarial", "failure rejects the technique",
                       "Commands:", "commands actually run", "observed findings", "version/runtime/revision applicability",
                       "NOT VERIFIED, not PASS", "blocks dependent reliance", "retain executable artifact, commands and findings"):
            self.assertIn(phrase, producer)
        for phrase in ("**Depends**: T001", "inspect and run applicable", "use it as implementation reference",
                       "behavior with production tests", "a report-only link is insufficient", "remaining integration risks",
                       "T001 passed and still-applicable", "failed/unrun producer cannot release"):
            self.assertIn(phrase, consumer)
        for phrase in ("**Depends**: T001, T002", "cleanup only after all applicable consumers and production validation pass",
                       "preserve reproducible evidence, commands, findings and limits", "otherwise retain proof"):
            self.assertIn(phrase, cleanup)

    def test_B_C_both_adapter_producer_consumer_lifetime(self):
        validator = load("risk_order", "../skills/task-generation/scripts/check-task-order.py")
        for name in ("risk-tiny-tasks.md", "risk-standard-tasks.md"):
            source = (HERE / "fixtures/planner" / name).read_text()
            self.assertEqual(validator.check(source), [], name)
            self.assert_risk_adapter_semantics(source)
        self.assertIn("before production lifecycle plumbing", (HERE / "fixtures/planner/risk-tiny-tasks.md").read_text())
        self.assertIn("before integration plumbing", (HERE / "fixtures/planner/risk-standard-tasks.md").read_text())

    def test_early_deletion_report_only_missing_dependency_failed_as_proven_rejected(self):
        for name in ("risk-tiny-tasks.md", "risk-standard-tasks.md"):
            source = (HERE / "fixtures/planner" / name).read_text()
            for old, new in (
                ("cleanup only after all applicable consumers and production validation pass", "delete immediately after producer"),
                ("inspect and run applicable", "link a report about"),
                ("**Depends**: T001\n", "**Depends**: none\n"),
                ("failure rejects the technique", "failed technique is proven"),
            ):
                with self.subTest(adapter=name, negative=new):
                    self.assertIn(old, source)
                    with self.assertRaises(AssertionError):
                        self.assert_risk_adapter_semantics(source.replace(old, new, 1))

    def test_A_D_E_labelled_walkthroughs_and_operational_mapping(self):
        source = (HERE / "fixtures/planner/risk-walkthroughs.md").read_text()
        for heading, phrases in (
            ("## A", ("source/documentation", "No executable spike", "name/type", "Evidence:", "Gate:")),
            ("## D", ("real-system validation", "not a forced", "Prerequisites:", "Criterion:", "Check:",
                      "Evidence:", "Gate:", "NOT VERIFIED", "cannot release dependent")),
            ("## E", ("Retain observed disproof", "not proven", "Block the assumed T002", "correct/replan",
                      "Renew affected existing", "retains the first failure", "Gate:")),
        ):
            for phrase in phrases:
                self.assertIn(phrase, checker.section(source, heading))
        texts = checker.load_texts()
        for label in ("risk-selection", "risk-producer", "risk-disproof", "risk-boundary"):
            _, key, heading, clauses = next(c for c in checker.RISK_CARRIERS if c[0] == label)
            for clause in clauses:
                self.assertIn(clause, checker.section(texts[key], heading))


class ProportionateValidationTests(unittest.TestCase):
    """Instruction-removal regressions, not behavioral/model evaluations."""

    def assert_clause_required(self, key, clause, diagnostic):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        self.assertIn(clause, texts[key])
        texts[key] = texts[key].replace(clause, "")
        self.assertTrue(any(e.startswith(diagnostic + ":")
                            for e in checker.check_contracts(texts)))

    def test_selection_wiring_gets_focused_check_not_automatic_matrix(self):
        for clause in (
            "lowest validation layer", "smallest sufficient check",
            "selected result or argument reaches the intended consumer",
            "Do not automatically add\nexhaustive matrices, fault injection, new test infrastructure or broad suites",
            "necessary integration layer",
        ):
            with self.subTest(clause=clause):
                self.assert_clause_required("planner", clause, "validation-focused")

    def test_batch_profile_feedback_and_diagnosed_repair_carriers(self):
        for key, clause, diagnostic in (
            ("coordination", "explicit user corrective/future-round direction", "coordination-feedback"),
            ("coordination", "No feedback means no write", "coordination-feedback"),
            ("coordinator", "inspect run/invocation, partial commits and check evidence", "coordination-routing"),
            ("coordinator", "reruns invalidated", "coordination-routing"),
            ("coordinator", "Unknown cause blocks blind restart", "coordination-routing"),
        ):
            self.assert_clause_required(key, clause, diagnostic)

    def test_schema_security_durability_retain_necessary_checks(self):
        self.assert_clause_required("planner", "migration, authorization or persistence", "validation-risk")

    def test_optional_checks_cannot_silently_block(self):
        for key, clause, diagnostic in (
            ("planner", "Optional checks are not acceptance blockers", "validation-authority"),
            ("tasks", "Optional checks do not become blockers", "validation-tasks"),
            ("coordinator", "optional checks cannot compensate", "validation-execution"),
        ):
            with self.subTest(key=key):
                self.assert_clause_required(key, clause, diagnostic)

    def test_owner_required_checks_need_authority_to_change(self):
        self.assert_clause_required("planner",
            "Never drop an owner-required check or approved\nsafety criterion without explicit authority",
            "validation-authority")
        self.assert_clause_required("coordinator", "manual/permission gates block reliance", "validation-execution")
        self.assert_clause_required("tasks", "owner-required criteria", "validation-tasks")

    def test_timeout_narrows_remaining_work_without_blind_retry(self):
        for clause in ("On timeout inspect the checkpoint and failed", "preserve completed proof",
                       "narrow only the diagnosed remaining work", "Rotation is not retry authority"):
            self.assert_clause_required("coordinator", clause, "validation-timeout")

    def test_reuse_and_causal_repairs_avoid_repeated_intake(self):
        for clause in ("Reuse valid unchanged evidence", "Avoid repeated historical intake", "actually blocks"):
            with self.subTest(clause=clause):
                self.assert_clause_required("planner", clause, "validation-reuse")


class VerificationCarrierTests(unittest.TestCase):
    def test_unconditional_escalation_restoration_rejected_with_summaries_intact(self):
        texts = checker.load_texts()
        conditional = "Targeted repair retains"
        carrier = checker.section(texts["coordinator"], "## Execute and Integrate")
        self.assertIn(conditional, carrier)
        texts["coordinator"] = texts["coordinator"].replace(
            carrier, carrier.replace(conditional, "Always use stronger repair", 1), 1)
        texts["coordinator"] += "\n## Footer\n" + conditional
        self.assertTrue(any(e.startswith("verification-repair:") for e in checker.check_contracts(texts)))

    def test_named_section_removals_fail_even_with_summary_intact(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        for label, key, heading, clauses in checker.VERIFICATION_CARRIERS:
            for clause in clauses:
                with self.subTest(case=label, removed=clause):
                    changed = dict(texts)
                    body = checker.section(changed[key], heading)
                    self.assertIn(" ".join(clause.split()), " ".join(body.split()))
                    pattern = r"\s+".join(re.escape(word) for word in clause.split())
                    changed[key] = changed[key].replace(body, re.sub(pattern, "REMOVED", body), 1)
                    changed[key] += "\n## Summary mention only\n" + clause
                    self.assertTrue(any(e.startswith(label + ":") for e in checker.check_contracts(changed)))


class InstructionTests(unittest.TestCase):
    def setUp(self):
        self.texts = checker.load_texts()

    def test_candidate_contract(self):
        self.assertEqual(checker.check_contracts(self.texts), [])

    def test_route_sections_do_not_overlap(self):
        tiny = checker.section(self.texts["planner"], "### TinySpec path")
        standard = checker.section(self.texts["planner"], "### Standard path")
        self.assertNotIn("### Standard path", tiny)
        self.assertNotIn("## Approval, resume", standard)
        self.assertIn("immediately proceed to handoff", tiny)

    def test_preservation_ledger_maps_retired_carriers(self):
        ledger = (ROOT / "docs/plans/planner-refactor.md").read_text()
        for number in range(1, 25):
            self.assertIn(f"P{number:02d}", ledger)
        # This ledger covers the historical planner refactor, not later onboarding.
        for old in ("create-epic", "epics-manager", "requirements-manager", "epic-brainstorming"):
            self.assertFalse((ROOT / "skills" / old / "SKILL.md").exists())

    def test_negative_mutations(self):
        mutations = [
            ("planner", "BOTH options", "one option", "choice:"),
            ("planner", "call `ask_user` and STOP", "continue directly", "choice:"),
            ("planner", "no source edits", "source edits permitted", "choice:"),
            ("planner", "Session history", "state file", "choice:"),
            ("planner", "Either choice is valid", "Follow the recommendation", "choice:"),
            ("planner", "positive and negative claims", "positive claims", "discovery:"),
            ("planner", "explicit owner deferral", "default deferral", "discovery:"),
            ("planner", "constraints **verbatim**", "constraints summarized", "handoff:"),
            ("planner", "Create separate tasks", "Use source checklist", "tiny-flow:"),
            ("planner", "No independent planning", "Mandatory independent planning", "tiny-flow:"),
            ("planner", "template-only", "generic", "standard-preflight:"),
            ("planner", "verify repaired output", "assume valid output", "standard-preflight:"),
            ("planner", "**`spec_create` — shared routing selection", "**`spec_create` — `sonnet-class`", "spec:"),
            ("planner", "specification approval before `plan_create`", "approval later", "spec:"),
            ("planner", "Only when no adapter is invoked", "After the adapter returns", "plan:"),
            ("planner", "do not create the plan again", "create the plan again", "plan:"),
            ("planner", "renewed specification approval", "existing specification approval", "plan:"),
            ("planner", "no producer self-review/correction", "self-review permitted", "task-stage:"),
            ("planner", "independent owner-selected reviewer", "implementer reviewer", "review:"),
            ("approval", "before calling `ask_user`", "after calling `ask_user`", "approval:"),
            ("approval", "Every actual task ID separately", "unstructured paragraphs", "approval:"),
            ("planner", "brief bullet-list executive summary", "summary in tool context", "tiny-flow:"),
            ("planner", "immediately continue to `plan_create`", "wait for another prompt", "spec:"),
            ("planner", "immediately proceed to handoff", "report readiness and stop", "tiny-flow:"),
            ("planner", "Do not end the turn merely to report approval", "End the turn after approval", "continuation:"),
            ("planner", "automatically invoke `coordinate-implementation`", "wait for a separate execution request", "final-continuation:"),
            ("approval", "inside tasks", "separate new source", "legacy:"),
            ("tasks", "stable task-local references", "unstable references", "task-contract:"),
            ("brainstorm", "no more than three items", "unbounded agenda", "brainstorm:"),
            ("brainstorm", "Only in selected-production", "In any mode", "brainstorm:"),
            ("coordinator", "Commit each task's verified changes as one focused owned-path commit", "Commit each batch", "execution-checkpoints:"),
            ("coordinator", "sequentially, never in parallel", "foreground is fine", "execution-sequential:"),
            ("coordinator", "TinySpec needs separate source/tasks", "source checklist only", "intake:"),
            ("coordinator", "Copy the owner-selected exact profile", "Use an agent default", "execution-selection:"),
            ("coordinator", "at assignment and dispatch", "at assignment only", "execution-selection:"),
            ("coordinator", "Completing tasks does not change that strategy", "Recount incomplete tasks", "execution-strategy:"),
            ("adoption", "every unrelated byte", "custom content", "adoption:"),
            ("docs", "not substantive implementation authorization", "implementation authorization", "docs:"),
        ]
        for key, old, new, diagnostic in mutations:
            with self.subTest(mutation=old):
                self.assertIn(" ".join(old.split()), " ".join(self.texts[key].split()))
                changed = dict(self.texts)
                changed[key] = re.sub(r"\s+".join(re.escape(w) for w in old.split()), new, changed[key])
                errors = checker.check_contracts(changed)
                self.assertTrue(any(e.startswith(diagnostic) for e in errors), errors)

    def test_job_first_contract_and_targeted_mutations(self):
        body = checker.section(self.texts["planner"], "## Job first; bookkeeping is subordinate")
        self.assertTrue(body)
        self.assertLess(self.texts["planner"].index(body),
                        self.texts["planner"].index("## Discovery and capability boundary"))
        obligations = (
            "Bookkeeping must always remain a small fraction of total effort",
            "Once required prerequisites are satisfied, advance the next authorized stage",
            "Reuse applicable settled evidence and decisions",
            "Keep required records terse",
            "Do not substitute repeated record polishing, duplicate evidence",
            "concrete invalidating evidence",
            "Carry this rule into every stage brief",
            "never waive required approvals, safety checks, permissions, reviews or commits",
            "exact blocker and smallest required resolution",
        )
        for removed in (*obligations, body):
            with self.subTest(removed=removed):
                self.assertIn(removed, body)
                changed = dict(self.texts)
                changed["planner"] = changed["planner"].replace(removed, "", 1)
                self.assertTrue(any(e.startswith("job-first:")
                                    for e in checker.check_contracts(changed)))

    def test_bulleted_brief_and_automatic_continuation_contract(self):
        self.assertIn("Every actual task ID separately", self.texts["approval"])
        self.assertIn("Do not end the turn merely to report approval", self.texts["planner"])
        self.assertIn("automatically invoke `coordinate-implementation`", self.texts["planner"])
        self.assertIn("explicitly requested planning-only", self.texts["planner"])
        self.assertIn("immediately continue to `plan_create`", checker.stage(self.texts["planner"], "spec_create"))
        self.assertIn("immediately proceed to handoff", checker.section(self.texts["planner"], "### TinySpec path"))

    def test_shared_invocation_cannot_be_satisfied_by_prerequisite_mentions(self):
        mutations = [
            ("Invoke `planning-brainstorming` in preselection mode", "Inspect the request directly", "shared-invocation:"),
            ("readiness target “informed scope assessment.”", "readiness target task generation", "shared-invocation:"),
            ("Apply recorded decisions through the shared mechanism inside selected bounds only.", "Apply recommendations directly.", "shared-application:"),
            ("invoke `tiny-spec`", "write a source directly", "tiny-flow:"),
            ("invoke `task-generation` direct adapter", "write a task checklist directly", "tiny-flow:"),
        ]
        for old, new, diagnostic in mutations:
            with self.subTest(mutation=old):
                changed = dict(self.texts)
                self.assertIn(old, changed["planner"])
                changed["planner"] = changed["planner"].replace(old, new, 1)
                self.assertTrue(any(e.startswith(diagnostic) for e in checker.check_contracts(changed)))

    def test_whole_stage_deletion_and_swap(self):
        for name in ("spec_create", "plan_create", "tasks_create", "overall_review"):
            body = checker.stage(self.texts["planner"], name)
            changed = dict(self.texts)
            changed["planner"] = changed["planner"].replace(body, f"**`{name}`**\n", 1)
            self.assertTrue(checker.check_contracts(changed), name)
        spec = checker.stage(self.texts["planner"], "spec_create")
        plan = checker.stage(self.texts["planner"], "plan_create")
        changed = dict(self.texts)
        changed["planner"] = changed["planner"].replace(spec, "TEMP_STAGE", 1).replace(plan, spec, 1).replace("TEMP_STAGE", plan, 1)
        self.assertTrue(any(e.startswith("standard-order:") for e in checker.check_contracts(changed)))

    def test_contradictions(self):
        policies = ("Automatically choose TinySpec", "Automatically choose Standard",
                    "Apply an unresolved material default", "Direct requirements must have a plan",
                    "Parallel implementation batches are permitted", "Foreground delegation is permitted",
                    "Batch commits replace task commits", "Automatically split shared files",
                    "Automatically split internal dependencies", "Automatically split at stage headings",
                    "Regroup dependencies to fill batches")
        for policy in policies:
            changed = dict(self.texts); changed["planner"] += "\n" + policy
            self.assertTrue(checker.check_contracts(changed), policy)

    def test_both_adapter_fixtures_use_existing_parser(self):
        validator = load("task_order", "../skills/task-generation/scripts/check-task-order.py")
        for name in ("tiny-tasks.md", "standard-tasks.md"):
            source = (HERE / "fixtures/planner" / name).read_text()
            self.assertEqual(validator.check(source), [], name)
            for field in ("Outcome", "Files/interfaces", "Acceptance", "Capabilities"):
                self.assertIn(f"**{field}**", source)

    def test_batch_handoff_mutations_and_adapter_items(self):
        for key, clause, diagnostic in (
            ("planner", "stable task-local REQUIRED", "batch-handoff:"),
            ("approval", "inadequate REQUIRED contracts", "batch-legacy:"),
            ("tiny", "stable task-local REQUIRED", "batch-source:"),
            ("helper", "not model-class labeling", "batch-helper:"),
            ("brainstorm", "not implementation-task assignments", "batch-brainstorm:"),
        ):
            with self.subTest(carrier=key):
                self.assertIn(clause, self.texts[key])
                changed = dict(self.texts)
                changed[key] = changed[key].replace(clause, "removed", 1)
                self.assertTrue(any(e.startswith(diagnostic) for e in checker.check_contracts(changed)))
        for name in ("tiny-tasks.md", "standard-tasks.md"):
            source = (HERE / "fixtures/planner" / name).read_text()
            self.assertNotIn("Model class", source)
            for ident in re.findall(r"^- \[ \] (T\d+)", source, re.M):
                self.assertIn(f"REQUIRED {ident}/V1", source)
                self.assertIn("Evidence:", source)

    def test_custom_lint_is_not_coupled_to_suite(self):
        with tempfile.TemporaryDirectory() as directory:
            run = subprocess.run(["bash", str(HERE / "check-skills-lint.sh"), directory], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("SKIP planner workflow checks", run.stdout)


class ActivePlanningRoutingTests(unittest.TestCase):
    """Consumer-scoped policy mutations; no provider or model-obedience claims."""

    def setUp(self):
        self.texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(self.texts), [])

    def mutate(self, key, heading, old, new, diagnostic):
        changed = dict(self.texts)
        carrier = (checker.stage(changed[key], heading) if heading == "plan_create"
                   else checker.section(changed[key], heading))
        self.assertEqual(carrier.count(old), 1, old)
        changed[key] = changed[key].replace(carrier, carrier.replace(old, new, 1), 1)
        errors = checker.check_contracts(changed)
        self.assertTrue(any(e.startswith(diagnostic + ":") for e in errors), errors)

    def test_standard_exact_family_and_effort_entire_direct_helper_pass(self):
        for key, heading, label in (("planner", "plan_create", "plan-profile"),
                                    ("helper", "## Planner Standard adapter contract", "adapter-profile")):
            for old, new in (("Sol family", "Luna family"),
                             ("**medium** supported effort", "**low** supported effort"),
                             ("for the ENTIRE", "for creation-only"),
                             ("Unavailable Sol/medium stops", "Unavailable Sol/medium falls back"),
                             ("no substitution, settings/default override or standalone", "allow substitution or standalone"),
                             ("unchanged", "using an agent default")):
                with self.subTest(consumer=key, mutant=new):
                    self.mutate(key, heading, old, new, label)

    def test_restored_class_authority_in_actual_consumers(self):
        for key, heading, old in (("planner", "### TinySpec path", "**Source creation — shared routing selection"),
                                  ("brainstorm", "## 1. Gate assessment", "shared routing selection"),
                                  ("helper", "## Planner Standard adapter contract", "Sol family")):
            for label in ("sonnet-class", "opus-class"):
                with self.subTest(consumer=key, label=label):
                    self.mutate(key, heading, old, label, "obsolete-planning-class")

    def test_selection_and_observed_gates_reach_each_consumer(self):
        cases = (("planner", "## Shared routing selection", "planning-selection",
                  ("Family rationale", "Effort rationale", "weakest verification blind spot",
                   "one exact selected profile unchanged", "Missing owner selection or support stops",
                   "settings or agent defaults overriding selection stop dispatch",
                   "unknown actual model or effort stays unknown")),
                 ("brainstorm", "## Capability preflight", "routing-brainstorm",
                  ("all six", "effort independently", "missing selection/support", "unknown actual")),
                 ("helper", "## Preflight", "routing-helper",
                  ("all six", "effort independently", "missing selection/support", "unknown actual",
                   "standalone selection cannot override a manager-governed\nStandard invocation's Sol/medium exception")))
        for key, heading, label, clauses in cases:
            for clause in clauses:
                with self.subTest(consumer=key, clause=clause):
                    self.mutate(key, heading, clause, "removed", label)

    def test_brainstorm_application_and_assessment_wiring(self):
        for heading, clause, label in (("## 1. Gate assessment", "using the preflight's shared routing selection", "routing-brainstorm-assessment"),
                                       ("## 3. Apply decisions", "with the preflight's\nshared routing selection", "routing-brainstorm-application")):
            self.mutate("brainstorm", heading, clause, "using a default", label)

    def test_manager_adapter_bypass_and_duplicate_pass_are_rejected(self):
        for old, new in (("policies below do not apply to this adapter invocation", "standalone selection supersedes the manager"),
                         ("once to create the plan", "twice to create the plan"),
                         ("do not direct it to create the plan again", "direct it to create the plan again")):
            self.mutate("helper", "## Planner Standard adapter contract", old, new, "adapter-profile")
        self.mutate("planner", "plan_create", "may bypass this rule", "fallback is permitted", "plan-profile")

    def test_summary_cannot_replace_operational_selection(self):
        for key, heading, label in (("planner", "## Shared routing selection", "planning-selection"),
                                    ("helper", "## Planner Standard adapter contract", "adapter-profile")):
            changed = dict(self.texts)
            carrier = checker.section(changed[key], heading)
            changed[key] = changed[key].replace(carrier, heading + "\n", 1) + "\n## Summary only\n" + carrier
            self.assertTrue(any(e.startswith(label + ":") for e in checker.check_contracts(changed)))

    def test_shared_router_link_and_applicability_are_required(self):
        self.mutate("routing", "## Applicability to planning/advisory invocations",
                    "rules do not become planning prerequisites", "rules become planning prerequisites", "routing-applicability")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in set(checker.PATHS.values()):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((ROOT / path).read_text())
            for key in ("planner", "brainstorm", "helper"):
                target = root / checker.PATHS[key]
                original = target.read_text()
                target.write_text(original.replace("../coordinate-implementation/references/batch-routing.md", "../absent.md"))
                with self.assertRaisesRegex(ValueError, "routing-reference: " + key):
                    checker.load_texts(root)
                target.write_text(original)


class DependencyResearchTests(unittest.TestCase):
    """Contract sensitivity and labelled simulated walkthroughs, not agent runs."""

    def setUp(self):
        self.texts = checker.load_texts()
        self.texts.setdefault("research", (ROOT / "skills/planner/references/dependency-research.md").read_text())

    def assert_diagnostic(self, texts, label):
        errors = checker.check_contracts(texts)
        self.assertTrue(any(e.startswith(label + ":") for e in errors), errors)

    def test_shared_reference_is_required_carrier(self):
        self.assertIn("research", checker.PATHS)
        changed = dict(self.texts)
        del changed["research"]
        self.assert_diagnostic(changed, "research-reference")

    def test_research_clause_removals_have_named_diagnostics(self):
        # Remove the actual obligation inside its carrier, not a summary keyword.
        cases = [
            ("planner", "## Discovery and capability boundary", "[dependency research contract](references/dependency-research.md)", "research-planner-link"),
            ("tiny", "## Dependency evidence before approach decisions", "[dependency research contract](../planner/references/dependency-research.md)", "research-tiny"),
            ("helper", "## Preflight", "[dependency research contract](../planner/references/dependency-research.md)", "research-helper"),
            ("planner", "## Before selection:", "no dependency docs,\nsource, plan or decisions may be persisted", "research-preselection"),
            ("planner", "### TinySpec path", "before consequential approach decisions", "research-tiny-handoff"),
            ("planner", "spec_create", "apply the shared research contract before consequential dependency constraints\n   are chosen", "research-spec"),
            ("planner", "plan_create", "For helper invocation or the direct Standard pass", "research-plan"),
            ("planner", "plan_create", "with explicit bounded permission\n   in addition to detected SpecKit artifacts", "research-plan"),
            ("tiny", "## Dependency evidence before approach decisions", "Direct/standalone entry verifies equivalent TinySpec selection/preparation authority", "research-tiny"),
            ("helper", "## Preflight", "Standalone entry verifies equivalent Standard planning/preparation authority", "research-helper"),
            ("helper", "## Planner Boundary", "only explicit bounded\npermission permits canonical research-document and necessary discovery-link writes", "research-boundary"),
            ("helper", "## Planner Boundary", "No arbitrary documentation edits or product code writes", "research-boundary"),
            ("research", "## Discover, trigger and reuse", "Read repository instructions, dependency declarations/lockfiles", "research-discovery"),
            ("research", "## Discover, trigger and reuse", "Trivial use can skip new internet\nresearch with a brief reason", "research-discovery"),
            ("research", "## Discover, trigger and reuse", "refresh only\nthose portions", "research-discovery"),
            ("research", "## Obtain sufficient evidence", "Adequate local guidance can satisfy evidence\nwithout a new search call", "research-evidence"),
            ("research", "## Obtain sufficient evidence", "official documentation, official guides/\nexamples/repositories and maintainers first", "research-evidence"),
            ("research", "## Classify and translate", "URL and applicable version", "research-traceability"),
            ("research", "## Classify and translate", "**Repository-derived decision:** local evidence, resulting decision and rationale", "research-traceability"),
            ("research", "## Classify and translate", "**Assumption:** uncertainty and a defined validation check", "research-traceability"),
            ("research", "## Classify and translate", "Unsupported snippets, uninspected URLs, uncertain statements and generic model\nrecollection cannot satisfy required source evidence", "research-traceability"),
            ("research", "## Classify and translate", "recommendation/local evidence → derived decision/implementation constraint → observable\nvalidation", "research-traceability"),
            ("research", "## Persist within verified authority", "primary URLs tied to supporting\nclaims, research date for evolving guidance", "research-persistence"),
            ("research", "## Safe failure and return", "stop affected consequential design and return the exact gap", "research-failure"),
            ("research", "## Safe failure and return", "No generic-knowledge fallback, fabricated\nsources, automatic deferral, installation or premature readiness", "research-failure"),
            ("research", "## Safe failure and return", "Record impact, allowed bounds and outstanding validation", "research-failure"),
            ("research", "## Discover, trigger and reuse", "installed/targeted dependency and version/range", "research-discovery"),
            ("research", "## Obtain sufficient evidence", "verify actually usable, permitted", "research-evidence"),
            ("research", "## Persist within verified authority", "repository technical owner and its discoverability index", "research-persistence"),
            ("research", "## Persist within verified authority", "Re-read each target immediately before", "research-persistence"),
            ("tiny", "## Compact source contract", "Trace source recommendation/local evidence → compact implementation\n  constraint → observable acceptance/check", "research-tiny-traceability"),
            ("helper", "## Planner Boundary", "supporting source spans → implementation constraints → observable checks", "research-boundary"),
            ("helper", "## Preflight", "standalone local fallback cannot bypass required research", "research-helper"),
            ("helper", "## Planner Standard adapter contract", "absence is not implied authority", "research-helper-adapter"),
            ("planner", "## Selected production and stage handoffs", "supporting spans → constraints → observable checks", "research-review"),
            ("planner", "overall_review", "direct Standard\n   pass and helper-managed/standalone contract coverage", "research-standard-review"),
        ]
        for key, heading, clause, label in cases:
            with self.subTest(diagnostic=label, removed=clause):
                changed = dict(self.texts)
                carrier = checker.stage(changed[key], heading) if heading in ("spec_create", "plan_create", "overall_review") else checker.section(changed[key], heading)
                self.assertEqual(carrier.count(clause), 1)
                changed[key] = changed[key].replace(carrier, carrier.replace(clause, "", 1), 1)
                self.assert_diagnostic(changed, label)

    def test_whole_research_carriers_cannot_be_replaced_by_summary(self):
        for key, heading, label in (
            ("tiny", "## Dependency evidence before approach decisions", "research-tiny"),
            ("helper", "## Preflight", "research-helper"),
            ("research", "## Classify and translate", "research-traceability"),
            ("research", "## Safe failure and return", "research-failure"),
        ):
            with self.subTest(carrier=heading):
                changed = dict(self.texts)
                body = checker.section(changed[key], heading)
                changed[key] = changed[key].replace(body, heading + "\n", 1) + "\n## Summary only\n" + body
                self.assert_diagnostic(changed, label)

    def test_planner_stage_deletions_preserve_summary_but_fail_research(self):
        for name, label in (("spec_create", "research-spec"), ("plan_create", "research-plan"),
                            ("overall_review", "research-standard-review")):
            with self.subTest(stage=name):
                changed = dict(self.texts)
                body = checker.stage(changed["planner"], name)
                changed["planner"] = changed["planner"].replace(body, f"**`{name}`**\n", 1)
                self.assertIn("Carry dependency research triggers", changed["planner"])
                self.assert_diagnostic(changed, label)

    def test_standard_and_helper_after_design_wording_is_rejected(self):
        for key, before, after, label in (
            ("planner", "Before consequential plan decisions", "After consequential plan decisions", "research-plan"),
            ("planner", "before consequential dependency constraints", "after consequential dependency constraints", "research-spec"),
            ("helper", "before consequential architecture/plan decisions", "after consequential architecture/plan decisions", "research-helper"),
        ):
            with self.subTest(route=label):
                changed = dict(self.texts)
                self.assertIn(before, changed[key])
                changed[key] = changed[key].replace(before, after, 1)
                self.assert_diagnostic(changed, label)

    def test_distributed_whole_directory_links_resolve_shared_owner(self):
        # Packaging shape used by install-links.py; no installation is performed.
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ("planner", "tiny-spec", "delegating-architectural-planning"):
                (target / name).symlink_to(ROOT / "skills" / name, target_is_directory=True)
            for name, relative in (("planner", "references/dependency-research.md"),
                                   ("tiny-spec", "../planner/references/dependency-research.md"),
                                   ("delegating-architectural-planning", "../planner/references/dependency-research.md")):
                self.assertEqual((target / name / relative).resolve(),
                                 (ROOT / "skills/planner/references/dependency-research.md").resolve())
                self.assertIn("# Dependency research contract", (target / name / relative).read_text())

    def test_tiny_research_moved_after_approach_is_rejected(self):
        changed = dict(self.texts)
        body = checker.section(changed["tiny"], "## Dependency evidence before approach decisions")
        changed["tiny"] = changed["tiny"].replace(body, "", 1) + "\n" + body
        self.assert_diagnostic(changed, "research-order")

    def test_missing_or_unresolvable_packaged_links(self):
        # Isolated file copies only; no installer or user's installation is changed.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in set(checker.PATHS.values()):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((ROOT / path).read_text())
            checker.load_texts(root)
            tiny = root / checker.PATHS["tiny"]
            tiny.write_text(tiny.read_text().replace("../planner/references/dependency-research.md", "../planner/references/absent.md"))
            with self.assertRaisesRegex(ValueError, "research-reference:.*tiny"):
                checker.load_texts(root)
            tiny.write_text((ROOT / checker.PATHS["tiny"]).read_text())
            (root / "skills/planner/references/dependency-research.md").unlink()
            with self.assertRaisesRegex(ValueError, "research-reference:"):
                checker.load_texts(root)

    def test_unsafe_research_permissions_are_rejected(self):
        for key, heading, policy, label in (
            ("planner", "## Before selection:", "Persist dependency docs before selection.", "research-preselection"),
            ("helper", "## Planner Boundary", "Arbitrary documentation edits are permitted.", "research-boundary"),
            ("research", "## Safe failure and return", "Use model recollection when required research is unavailable.", "research-failure"),
        ):
            with self.subTest(policy=policy):
                changed = dict(self.texts)
                changed[key] = changed[key].replace(heading, heading + "\n" + policy, 1)
                self.assert_diagnostic(changed, label)

    def test_simulated_indexing_trace_in_both_routes_and_entries(self):
        # Fictional v2 guide, local call sites and outputs: not real source research.
        evidence = {"kind": "documented recommendation", "version": "simulated v2",
                    "span": "Lifecycle: complete queued batches before close",
                    "url": "https://example.invalid/simulated/v2/lifecycle"}
        decision = {"kind": "repository-derived decision", "local": "simulated shutdown races pending flush",
                    "constraint": "await queued batches before close", "source": evidence["span"]}
        assumption = {"kind": "assumption", "claim": "bounded shutdown wait", "check": "measure wait under simulated load"}
        check = {"constraint": decision["constraint"], "observable": "pending batch completion precedes close event"}
        self.assertIn("queued batches", evidence["span"])
        self.assertEqual(decision["source"], evidence["span"])
        self.assertEqual(check["constraint"], decision["constraint"])
        self.assertIn("precedes close", check["observable"])
        self.assertTrue(assumption["check"])
        for key, heading, expected in (
            ("planner", "### TinySpec path", "before consequential approach decisions"),
            ("planner", "plan_create", "For helper invocation or the direct Standard pass"),
            ("tiny", "## Dependency evidence before approach decisions", "Direct/standalone entry verifies equivalent"),
            ("helper", "## Preflight", "Standalone entry verifies equivalent"),
        ):
            with self.subTest(simulated_route=key, entry=heading):
                carrier = checker.stage(self.texts[key], heading) if heading == "plan_create" else checker.section(self.texts[key], heading)
                self.assertIn(expected, carrier)
        classification = checker.section(self.texts["research"], "## Classify and translate")
        for obligation in ("**Documented recommendation:**", "**Repository-derived decision:**", "**Assumption:**", "observable\nvalidation"):
            self.assertIn(obligation, classification)

    def test_simulated_reuse_skip_and_version_refresh(self):
        # Expected offline walkthrough facts, not an automated research policy engine.
        discovery = checker.section(self.texts["research"], "## Discover, trigger and reuse")
        evidence = checker.section(self.texts["research"], "## Obtain sufficient evidence")
        persistence = checker.section(self.texts["research"], "## Persist within verified authority")
        for case, carrier, obligations in (
            ("recent applicable simulated v2 guidance: reuse, zero new searches/date bump", evidence,
             ("Adequate local guidance can satisfy evidence\nwithout a new search call",)),
            ("trivial simulated import: skip with reason", discovery,
             ("Trivial use can skip new internet\nresearch with a brief reason",)),
            ("simulated v1 lifecycle outdated for v2: refresh lifecycle only", discovery,
             ("version applicability", "refresh only\nthose portions", "no universal freshness deadline or decorative date bump")),
            ("targeted simulated refresh preserves other guidance", persistence,
             ("Re-read each target immediately before", "preserve unrelated content")),
        ):
            with self.subTest(simulated_case=case):
                for obligation in obligations:
                    self.assertIn(obligation, carrier)

    def test_simulated_insufficient_evidence_and_bounded_deferral(self):
        failure = checker.section(self.texts["research"], "## Safe failure and return")
        classification = checker.section(self.texts["research"], "## Classify and translate")
        for case, carrier, obligations in (
            ("simulated unavailable search plus inadequate local guide: return missing v2 lifecycle evidence, affected shutdown decision", failure,
             ("required tools, usable sources, version evidence or write authority", "stop affected consequential design and return the exact gap", "affected\ndecisions and evidence/authority needed")),
            ("simulated uninspected URL/snippet: cannot satisfy evidence", classification,
             ("Unsupported snippets, uninspected URLs", "recollection cannot satisfy required source evidence")),
            ("simulated explicit owner deferral: defer only shutdown timing; impact risk, bounded use, pending-load check remain", failure,
             ("explicit bounded owner deferral through existing gates", "Record impact, allowed bounds and outstanding validation", "not fabricate evidence or waive unrelated gates")),
        ):
            with self.subTest(simulated_case=case):
                for obligation in obligations:
                    self.assertIn(obligation, carrier)
        pre = checker.section(self.texts["planner"], "## Before selection:")
        self.assertIn("no dependency docs,\nsource, plan or decisions may be persisted", pre)
        self.assertIn("Carry findings in session until selection", pre)


class ProjectCoordinationWiringTests(unittest.TestCase):
    """Wiring checks for mandatory project-local memory; no live agent/SpecKit calls."""

    def test_shared_reference_is_required_not_summary_only(self):
        texts = checker.load_texts()
        del texts["coordination"]
        self.assertTrue(any(e.startswith("coordination-reference:") for e in checker.check_contracts(texts)))

    def test_routine_consumer_bookkeeping_resurrection_fails(self):
        texts = checker.load_texts()
        for key in ("planner", "tiny", "tasks", "helper", "memory", "coordinator", "adoption"):
            for clause in ("Automatically initialize coordination memory", "Write a run SUMMARY on completion",
                           "Refresh the coordination index after every task", "Reflect at blocked pause",
                           "Commit evidence separately before the next task", "Infer lessons from failed runs",
                           "Automatically create STATE.md", "Update STATE after child-ID return", "Remove finished STATE items"):
                with self.subTest(consumer=key, clause=clause):
                    changed = dict(texts)
                    changed[key] += "\n" + clause
                    self.assertTrue(any(e.startswith("coordination-unsafe-" + key + ":") for e in checker.check_contracts(changed)))

    def test_all_distributed_consumers_resolve_coordination_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for name in ("memory-handling", "planner", "tiny-spec", "task-generation", "coordinate-implementation"):
                (target / name).symlink_to(ROOT / "skills" / name, target_is_directory=True)
            owner = ROOT / checker.PATHS["coordination"]
            for name in ("memory-handling", "planner", "tiny-spec", "task-generation", "coordinate-implementation"):
                relative = "references/project-coordination.md" if name == "memory-handling" else "../memory-handling/references/project-coordination.md"
                self.assertEqual((target / name / relative).resolve(), owner.resolve())
                self.assertIn("# Project coordination memory", (target / name / relative).read_text())

    def test_no_reflection_or_extra_checkpoint_and_feedback_guards(self):
        texts = checker.load_texts()
        text = texts["coordinator"]
        self.assertNotIn("### Coordination evidence checkpoint", text)
        self.assertNotIn("## Coordination reflection and guideline approval", text)
        self.assertIn("No extra\nevidence-only checkpoint", text)
        for clause in ("No feedback means no write", "without a routine second exact-content approval", "never history/index/run scaffolding"):
            changed = dict(texts)
            changed["coordination"] = re.sub(r"\s+".join(re.escape(w) for w in clause.split()), "REMOVED", changed["coordination"])
            self.assertTrue(any(e.startswith("coordination-feedback:") for e in checker.check_contracts(changed)))


class StageDispatchTests(unittest.TestCase):
    """Authored symbolic direct/earned-workflow cases, not a provider/tool invocation."""
    def test_stage_dispatch_guards_are_scoped_and_not_footer_rescuable(self):
        texts = checker.load_texts()
        clauses = ("direct asynchronous single-stage dispatch", "selected profile unchanged",
                   "Inspect the returned artifact/checkpoint", "before the next authorized stage",
                   "Never prewire dependent source→tasks", "direct delegation cannot adequately serve",
                   "stage sequence alone is insufficient", "do not authorize parallel implementation batches")
        for clause in clauses:
            changed = dict(texts)
            body = checker.section(changed["planner"], "## Selected production and stage handoffs")
            pattern = r"\s+".join(re.escape(w) for w in clause.split())
            self.assertRegex(body, pattern)
            changed["planner"] = changed["planner"].replace(body, re.sub(pattern, "REMOVED", body))
            changed["planner"] += "\n## Footer\n" + clause
            self.assertTrue(any(e.startswith("stage-dispatch:") for e in checker.check_contracts(changed)))

    def test_direct_async_parent_inspection_then_next_authorized_stage(self):
        trace = ["direct-async-source", "parent-artifact-checkpoint-inspection", "direct-async-tasks"]
        self.assertLess(trace.index("parent-artifact-checkpoint-inspection"), trace.index("direct-async-tasks"))
        for inspected, authorized, unchanged_profile, allowed in (
            (True, True, True, True), (False, True, True, False),
            (True, False, True, False), (True, True, False, False),
        ):
            self.assertEqual(inspected and authorized and unchanged_profile, allowed)

    def test_earned_workflow_not_convenience_or_sequential_wrapper(self):
        for reason, direct_insufficient, inspected, authorized, expected in (
            ("branching", True, True, True, True),
            ("parallel-independent", True, True, True, True),
            ("earned-orchestration", True, True, True, True),
            ("single-child", True, True, True, False),
            ("convenience", True, True, True, False),
            ("sequential-only", True, True, True, False),
            ("branching", False, True, True, False),
            ("branching", True, False, True, False),
            ("branching", True, True, False, False),
        ):
            self.assertEqual(reason in ("branching", "parallel-independent", "earned-orchestration")
                             and direct_insufficient and inspected and authorized, expected)
        texts = checker.load_texts()
        for unsafe in ("Default to a single-child workflow wrapper", "Prewire source→tasks without parent inspection",
                       "Sequential convenience justifies workflows"):
            changed = dict(texts)
            changed["planner"] = changed["planner"].replace("## Selected production and stage handoffs",
                                                          "## Selected production and stage handoffs\n" + unsafe)
            self.assertTrue(any(e.startswith("stage-dispatch:") for e in checker.check_contracts(changed)))


BRIEF = "\n".join((
    "- Outcome: fix search ranking.",
    "- Scope: ranking only; exclude API migration.",
    "- Decisions: stable API.",
    "- Risk: tie behavior.",
    "- Review: task checks inspected, live checks NOT RUN.",
    "- Authorization: current source/tasks implementation; coordinator starts next.",
))


def message(*blocks):
    return {"type": "message_end", "message": {"role": "assistant", "content": list(blocks)}}


def text(value):
    return {"type": "text", "text": value}


def call(ident):
    return {"type": "toolCall", "name": "ask_user", "id": ident}


def start(ident, name="ask_user"):
    return {"type": "tool_execution_start", "toolName": name, "toolCallId": ident,
            "args": {"options": [{"title": "TinySpec"}, {"title": "Standard"}]}}


def end(ident, answer="TinySpec", cancelled=False):
    return {"type": "tool_execution_end", "toolCallId": ident,
            "result": {"details": {"response": {"kind": "selection", "selections": [answer]},
                                    "cancelled": cancelled}}}


def scenario():
    return [message(text("Scope assessment and both paths"), call("choose")), start("choose"), end("choose"),
            {"type": "artifact_snapshot", "path": "tiny.md", "digest": "reviewed-content"},
            message(text(BRIEF), call("approve")), start("approve"), end("approve", "Approve")]


class TraceTests(unittest.TestCase):
    contract = {"choice_call": "choose", "expected_depth": "TinySpec", "approvals": ["approve"]}

    def test_valid_order(self):
        self.assertEqual(trace.check(scenario(), self.contract), [])

    def test_prose_only_brief_is_rejected(self):
        events = scenario()
        events[4] = message(text("Outcome, scope, decisions, risk and review are described. Approve implementation?"), call("approve"))
        self.assertTrue(any("bullet" in error for error in trace.check(events, self.contract)))

    def test_empty_final_bullets_do_not_inherit_progress_list(self):
        events = scenario()
        events[4] = message(text("- Progress one\n- Progress two\n- Progress three\n- Progress four\nApproval summary:\n- \n- \n- \n- "), call("approve"))
        self.assertTrue(any("bullet" in error for error in trace.check(events, self.contract)))

    def test_empty_bullets_are_not_a_formatted_brief(self):
        events = scenario(); events[4] = message(text("- \n- \n- \n- "), call("approve"))
        self.assertTrue(trace.check(events, self.contract))

    def continuation_contract(self):
        return {**self.contract, "continuations": [{
            "after": "approve", "approved_response": {"kind": "selection", "selections": ["Approve"]},
            "next_tool": "read", "next_args": {"path": "skills/coordinate-implementation/SKILL.md"},
        }]}

    def next_phase(self):
        event = start("load-coordinator", "read")
        event["args"] = {"path": "skills/coordinate-implementation/SKILL.md"}
        return event

    def test_approved_phase_starts_before_returning_control(self):
        events = scenario() + [self.next_phase(), {"type": "agent_settled"}]
        self.assertEqual(trace.check(events, self.continuation_contract()), [])

    def test_readiness_summary_without_next_phase_fails(self):
        events = scenario() + [message(text("Approved. Run the coordinator in your next prompt.")), {"type": "agent_settled"}]
        self.assertTrue(any("did not start" in e for e in trace.check(events, self.continuation_contract())))

    def test_starting_next_phase_after_returning_control_is_not_automatic(self):
        events = scenario() + [{"type": "agent_settled"}, self.next_phase()]
        self.assertTrue(trace.check(events, self.continuation_contract()))

    def test_denied_approval_blocks_automatic_continuation(self):
        events = scenario(); events[-1] = end("approve", "Request changes")
        self.assertEqual(trace.check(events, self.continuation_contract()), [])
        events.append(self.next_phase())
        self.assertTrue(any("without affirmative" in e for e in trace.check(events, self.continuation_contract())))

    def test_denial_then_settled_does_not_allow_later_phase_start(self):
        events = scenario(); events[-1] = end("approve", "Request changes")
        events.extend([{"type": "agent_settled"}, self.next_phase()])
        self.assertTrue(any("without affirmative" in e for e in trace.check(events, self.continuation_contract())))

    def test_action_while_approval_pending_is_never_retroactively_authorized(self):
        for answer in ("Approve", "Request changes"):
            events = scenario(); events[-1] = end("approve", answer)
            events.insert(6, self.next_phase())
            self.assertTrue(any("pending" in e for e in trace.check(events, self.continuation_contract())), answer)

    def test_denial_can_be_superseded_by_actual_renewed_approval(self):
        events = scenario(); events[-1] = end("approve", "Request changes")
        events.extend([{"type": "agent_settled"}, message(text(BRIEF), call("renew")),
                       start("renew"), end("renew", "Approve"), self.next_phase(), {"type": "agent_settled"}])
        contract = self.continuation_contract()
        contract["approvals"] = ["approve", "renew"]
        contract["continuations"].append({**contract["continuations"][0], "after": "renew"})
        self.assertEqual(trace.check(events, contract), [])

    def test_explicit_planning_only_requires_no_execution_transition(self):
        # Supervisor omits final implementation expectation for an explicit bounded request.
        self.assertEqual(trace.check(scenario() + [{"type": "agent_settled"}], self.contract), [])

    def test_continuation_cannot_use_untracked_result(self):
        contract = self.continuation_contract(); contract["continuations"][0]["after"] = "untracked"
        self.assertTrue(trace.check(scenario(), contract))

    def test_preselection_mutation_attempt_even_if_blocked(self):
        events = scenario(); events.insert(1, start("bad-write", "write"))
        self.assertTrue(any("mutation attempted" in e for e in trace.check(events, self.contract)))

    def test_shell_requires_audit(self):
        events = scenario(); events.insert(1, start("shell", "bash"))
        self.assertTrue(trace.check(events, self.contract))

    def test_brief_after_tool_block_does_not_count(self):
        events = scenario(); events[4] = message(call("approve"), text(BRIEF))
        self.assertTrue(any("BEFORE" in e for e in trace.check(events, self.contract)))

    def test_tool_context_alone_is_not_prior_brief(self):
        events = scenario(); events[4] = message(call("approve")); events[5]["args"]["context"] = BRIEF
        self.assertTrue(trace.check(events, self.contract))

    def test_hidden_reasoning_is_not_a_brief(self):
        events = scenario(); events[4] = message({"type": "thinking", "thinking": BRIEF}, call("approve"))
        self.assertTrue(trace.check(events, self.contract))

    def test_changed_artifact_while_approval_pending(self):
        events = scenario(); events.insert(6, {"type": "artifact_snapshot", "path": "tiny.md", "digest": "new"})
        self.assertTrue(any("changed" in e for e in trace.check(events, self.contract)))

    def test_cancelled_or_failed_choice_not_authorization(self):
        for kind in ("cancelled", "isError"):
            events = scenario()
            if kind == "cancelled": events[2]["result"]["details"]["cancelled"] = True
            else: events[2]["isError"] = True
            self.assertTrue(trace.check(events, self.contract))

    def test_no_forged_choice_from_assistant_prose(self):
        events = scenario(); events[2]["result"]["details"]["response"] = None
        events.insert(3, message(text("Owner chose TinySpec")))
        self.assertTrue(trace.check(events, self.contract))

    def test_omitted_option_and_missing_call(self):
        events = scenario(); events[1]["args"]["options"] = [{"title": "TinySpec"}]
        self.assertTrue(any("omits Standard" in e for e in trace.check(events, self.contract)))
        self.assertTrue(trace.check([], self.contract))

    def test_denial_does_not_allow_execution(self):
        events = scenario(); events[-1] = end("approve", "Request changes")
        self.assertEqual(trace.check(events, self.contract), [])
        events.append({"type": "execution_attempt"})
        self.assertTrue(trace.check(events, self.contract))

    def test_orphan_wrong_tool_reversed_and_duplicate_choice_events(self):
        orphan = end("choose")
        orphan["result"]["details"]["response"] = {"kind": "freeform", "text": "TinySpec"}
        choice_only = {"choice_call": "choose", "expected_depth": "TinySpec"}
        cases = [
            [orphan],
            [start("choose", "read"), end("choose")],
            [end("choose"), start("choose")],
            [start("choose"), start("choose"), end("choose")],
            [start("choose"), end("choose"), end("choose")],
        ]
        for events in cases:
            with self.subTest(events=events):
                self.assertTrue(trace.check(events, choice_only))

    def test_supervisor_maps_punctuated_or_prefixed_title_to_depth(self):
        for title in ("TinySpec: compact source and tasks", "Option A — TinySpec"):
            with self.subTest(title=title):
                events = scenario()
                events[1]["args"]["options"] = [{"title": title}, {"title": "Standard: separate stages"}]
                events[2] = end("choose", title)
                contract = {**self.contract, "expected_title": title}
                self.assertEqual(trace.check(events, contract), [])
                # No fuzzy inference when the supervisor's expected title differs.
                self.assertTrue(trace.check(events, self.contract))

    def test_duplicate_or_orphan_approval_events_rejected(self):
        events = scenario(); events.insert(6, start("approve"))
        self.assertTrue(trace.check(events, self.contract))
        events = scenario(); events.pop(5)
        self.assertTrue(trace.check(events, self.contract))

    def test_standard_override(self):
        events = scenario(); events[2] = end("choose", "Standard")
        self.assertEqual(trace.check(events, {**self.contract, "expected_depth": "Standard"}), [])


class DelegationAuthorityTests(unittest.TestCase):
    """Named operational-carrier mutations; not live model obedience."""

    def test_creation_correction_stop_carrier_clause_removals(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        for label, key, selector, clauses in checker.DELEGATION_CARRIERS:
            for clause in clauses:
                with self.subTest(carrier=label, removed=clause):
                    body = checker.operational_carrier(texts[key], selector)
                    self.assertIn(clause, body)
                    changed = dict(texts)
                    changed[key] = changed[key].replace(body, re.sub(r"\s+".join(re.escape(w) for w in clause.split()), "REMOVED", body), 1)
                    self.assertTrue(any(e.startswith(label + ":") for e in checker.check_contracts(changed)))

    def test_actual_stage_removal_leaving_summary_cannot_pass(self):
        texts = checker.load_texts()
        for label, key, selector, _ in checker.DELEGATION_CARRIERS + checker.AUTHORITY_CARRIERS:
            with self.subTest(carrier=label):
                body = checker.operational_carrier(texts[key], selector)
                self.assertTrue(body)
                changed = dict(texts)
                changed[key] = changed[key].replace(body, "", 1) + "\n## Summary only\n" + body.replace(selector.removeprefix("item:"), "Summary", 1)
                self.assertTrue(any(e.startswith(label + ":") for e in checker.check_contracts(changed)))

    def test_parent_mechanical_upstream_task_and_managed_fallback_mutations(self):
        texts = checker.load_texts()
        for label, key, selector, _ in checker.DELEGATION_CARRIERS:
            for forbidden in ("parent may create artifacts", "parent may fix mechanical issues",
                              "parent may fix upstream artifacts", "parent may fix tasks",
                              "managed direct fallback is permitted", "inline fallback is permitted"):
                with self.subTest(carrier=label, forbidden=forbidden):
                    body = checker.operational_carrier(texts[key], selector)
                    changed = dict(texts)
                    changed[key] = changed[key].replace(body, body + "\n" + forbidden + "\n", 1)
                    self.assertTrue(any(e.startswith(label + ": contradictory") for e in checker.check_contracts(changed)))

    def test_source_quality_and_downstream_truth_actual_inputs(self):
        texts = checker.load_texts()
        for label, key, selector, clauses in checker.AUTHORITY_CARRIERS:
            for clause in clauses:
                with self.subTest(carrier=label, removed=clause):
                    body = checker.operational_carrier(texts[key], selector)
                    self.assertIn(clause, body)
                    changed = dict(texts)
                    changed[key] = changed[key].replace(body, re.sub(r"\s+".join(re.escape(w) for w in clause.split()), "REMOVED", body), 1)
                    self.assertTrue(any(e.startswith(label + ":") for e in checker.check_contracts(changed)))

    def test_downstream_sdd_forward_reread_and_competing_plan_authority(self):
        texts = checker.load_texts()
        for label, key, selector, _ in checker.AUTHORITY_CARRIERS:
            if not label.startswith("truth-"):
                continue
            for forbidden in ("forward SDD guidance as requirements input",
                              "reread SDD guidance for requirements", "approved plan is requirements truth"):
                with self.subTest(carrier=label, forbidden=forbidden):
                    body = checker.operational_carrier(texts[key], selector)
                    changed = dict(texts)
                    changed[key] = changed[key].replace(body, body + "\n" + forbidden + "\n", 1)
                    self.assertTrue(any(e.startswith(label + ": contradictory") for e in checker.check_contracts(changed)))

    def test_source_quality_distributed_links_and_actor_governance(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        for key, title in (("planner", "SDD reference"), ("tiny", "SDD quality guidance")):
            destination = re.search(r"\[" + title + r"\]\(([^)]+)\)", texts[key]).group(1)
            owner = (ROOT / checker.PATHS[key]).parent / destination
            self.assertEqual(owner.resolve(), (ROOT / checker.PATHS["guidance"]).resolve())
            self.assertTrue(owner.is_file())
        for selector in ("item:- A SpecKit adapter", "item:- A direct adapter"):
            body = checker.operational_carrier(texts["tasks"], selector)
            self.assertIn("Trace source", body)
            self.assertIn("permission/safety", body)
        self.assertIn("separate source and tasks file", texts["tasks"])


class CompleteBriefTests(unittest.TestCase):
    """Trusted exact fixture outcomes, not a generic semantic/NLP oracle."""

    def setUp(self):
        self.inventory = json.loads((HERE / "fixtures/planner/approval-inventory.json").read_text())

    def brief(self, inventory):
        return "\n".join("- " + item for item in inventory["scope"] +
                         [f"{i['id']}: {i['outcome']}" for kind in ("stages", "tasks") for i in inventory[kind]])

    def run_brief(self, brief, inventory=None):
        inventory = self.inventory if inventory is None else inventory
        events = scenario()
        events[3] = {"type": "artifact_snapshot", "path": "approval-artifacts.md", "digest": "fixture-v1"}
        events[4] = message(text(brief), call("approve"))
        contract = {**TraceTests.contract, "brief_inventories": {"approve": inventory}}
        return trace.check(events, contract)

    def test_trusted_artifacts_match_eight_stage_and_eight_task_inventory(self):
        artifact = (HERE / "fixtures/planner/approval-artifacts.md").read_text()
        for bullet in self.brief(self.inventory).splitlines():
            self.assertIn(bullet, artifact)
        self.assertGreater(len(self.inventory["stages"]), 6)
        self.assertGreater(len(self.inventory["tasks"]), 6)
        self.assertEqual(self.run_brief(self.brief(self.inventory)), [])

    def test_missing_reordered_duplicate_collapsed_empty_truncated_and_wrong_outcomes(self):
        original = self.brief(self.inventory).splitlines()
        for kind, first, last in (("stages", 1, 8), ("tasks", 9, 16)):
            variants = {}
            variants["omitted"] = original[:last] + original[last + 1:]
            swapped = original.copy(); swapped[first], swapped[first + 1] = swapped[first + 1], swapped[first]
            variants["reordered"] = swapped
            variants["duplicate"] = original + [original[first]]
            collapsed = original.copy(); collapsed[first:first + 2] = [original[first] + " and " + original[first + 1]]
            variants["collapsed catch-all"] = collapsed
            empty = original.copy(); empty[first] = "- " + self.inventory[kind][0]["id"] + ":"
            variants["empty outcome"] = empty
            wrong = original.copy(); wrong[first] = "- " + self.inventory[kind][0]["id"] + ": do the rest."
            variants["wrong outcome"] = wrong
            variants["six total truncation"] = original[:6]
            for name, lines in variants.items():
                with self.subTest(kind=kind, case=name):
                    self.assertTrue(any(kind + " coverage" in e for e in self.run_brief("\n".join(lines))))
        self.assertTrue(any("scope coverage" in e for e in self.run_brief("\n".join(original[1:]))))

    def test_tiny_combined_spec_only_and_standard_overall_applicability(self):
        for route in ("tiny-combined", "standard-spec-only", "standard-overall"):
            inventory = copy.deepcopy(self.inventory)
            if route != "standard-overall": inventory["stages"] = []
            if route == "standard-spec-only": inventory["tasks"] = []
            with self.subTest(route=route):
                self.assertEqual(self.run_brief(self.brief(inventory), inventory), [])
                if not inventory["stages"]:
                    self.assertTrue(self.run_brief(self.brief(inventory) + "\n- Stage invented: no plan.", inventory))
                if not inventory["tasks"]:
                    self.assertTrue(self.run_brief(self.brief(inventory) + "\n- T001: nonexistent task.", inventory))

    def test_current_renewal_accepts_fresh_rejects_stale_inventory_and_brief(self):
        events = scenario()
        events[3] = {"type": "artifact_snapshot", "path": "approval-artifacts.md", "digest": "fixture-v1"}
        events[4] = message(text(self.brief(self.inventory)), call("approve"))
        renewed = copy.deepcopy(self.inventory)
        renewed["tasks"][-1]["outcome"] = "document revised recovery limits."
        renewed["artifacts"]["approval-artifacts.md"] = "fixture-v2"
        events += [{"type": "artifact_snapshot", "path": "approval-artifacts.md", "digest": "fixture-v2"},
                   message(text(self.brief(renewed)), call("renew")), start("renew"), end("renew", "Approve")]
        contract = {**TraceTests.contract, "approvals": ["approve", "renew"],
                    "brief_inventories": {"approve": self.inventory, "renew": renewed}}
        self.assertEqual(trace.check(events, contract), [])
        stale = copy.deepcopy(events); stale[-3] = message(text(self.brief(self.inventory)), call("renew"))
        self.assertTrue(any("renew: tasks coverage" in e for e in trace.check(stale, contract)))
        stale_contract = copy.deepcopy(contract); stale_contract["brief_inventories"]["renew"] = self.inventory
        self.assertTrue(any("current artifact content" in e for e in trace.check(events, stale_contract)))

    def test_full_inventory_context_hidden_and_late_briefs_rejected(self):
        for placement in ("context", "hidden", "late"):
            events = scenario(); brief = self.brief(self.inventory)
            events[3] = {"type": "artifact_snapshot", "path": "approval-artifacts.md", "digest": "fixture-v1"}
            if placement == "context":
                events[4] = message(call("approve")); events[5]["args"]["context"] = brief
            elif placement == "hidden":
                events[4] = message({"type": "thinking", "thinking": brief}, call("approve"))
            else:
                events[4] = message(call("approve"), text(brief))
            contract = {**TraceTests.contract, "brief_inventories": {"approve": self.inventory}}
            with self.subTest(placement=placement):
                self.assertTrue(any("BEFORE" in e for e in trace.check(events, contract)))

    def test_actual_trace_cli_with_trusted_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            events = scenario()
            events[3] = {"type": "artifact_snapshot", "path": "approval-artifacts.md", "digest": "fixture-v1"}
            events[4] = message(text(self.brief(self.inventory)), call("approve"))
            contract = {**TraceTests.contract, "brief_inventories": {"approve": self.inventory}}
            (path / "contract.json").write_text(json.dumps(contract))
            for expected, body in ((0, events), (1, [*events[:4], message(text("- Scope only."), call("approve")), *events[5:]])):
                (path / "trace.jsonl").write_text("\n".join(map(json.dumps, body)))
                result = subprocess.run([sys.executable, str(HERE / "planner-trace.py"), str(path / "trace.jsonl"), str(path / "contract.json")], capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stdout)


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skills = self.root / "suite" / "skills"; self.skills.mkdir(parents=True)
        for name in ("planner", "tiny-spec", "initialize-coherence"):
            (self.skills / name).mkdir(); (self.skills / name / "SKILL.md").write_text("fixture")
        self.guidance = self.root / "guide.md"; self.guidance.write_text("reference")
        self.dest = self.root / "home" / "skills"; self.dest.mkdir(parents=True)
        self.docs = self.root / "home" / "docs"
        self.backups = self.root / "home" / "backups"
        self.settings = self.root / "settings.json"

    def install(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return links.install(self.skills, self.guidance, self.dest, self.docs, self.backups, self.settings)

    def test_coherence_retirement_inventory_is_explicit(self):
        self.assertTrue({"install-memory", "initialize-documentation"}.issubset(links.RETIRED))
        for name in ("install-memory", "initialize-documentation"):
            (self.dest / name).symlink_to(self.skills / name)
        self.install()
        for name in ("install-memory", "initialize-documentation"):
            self.assertFalse(os.path.lexists(self.dest / name))
        self.assertTrue((self.dest / "initialize-coherence").is_symlink())

    def test_fresh_and_idempotent(self):
        self.assertEqual(self.install(), 3)
        before = {p.name: os.readlink(p) for p in self.dest.iterdir()}
        self.assertEqual(self.install(), 3)
        self.assertEqual(before, {p.name: os.readlink(p) for p in self.dest.iterdir()})

    def test_retired_owned_broken_and_valid_links(self):
        (self.skills / "create-epic").mkdir()
        (self.skills / "install-memory").mkdir()  # surviving directory, no operational entry
        for name in links.RETIRED:
            (self.dest / name).symlink_to(self.skills / name)
        self.install()
        self.assertEqual(len(list(self.backups.iterdir())), len(links.RETIRED))
        for name in links.RETIRED:
            self.assertFalse(os.path.lexists(self.dest / name))
        self.install(); self.assertEqual(len(list(self.backups.iterdir())), len(links.RETIRED))

    def test_retired_foreign_entries_preserved(self):
        (self.dest / "create-epic").write_text("foreign file")
        (self.dest / "epics-manager").mkdir()
        (self.dest / "requirements-manager").symlink_to(self.root / "previous-checkout" / "skills" / "requirements-manager")
        self.install()
        self.assertEqual((self.dest / "create-epic").read_text(), "foreign file")
        self.assertTrue((self.dest / "epics-manager").is_dir())
        self.assertTrue((self.dest / "requirements-manager").is_symlink())
        self.assertFalse(self.backups.exists())

    def test_coherence_retired_foreign_and_uncertain_entries_preserved(self):
        for kind in ("file", "directory", "foreign-link", "old-checkout", "uncertain-link"):
            with self.subTest(kind=kind):
                for name in ("install-memory", "initialize-documentation"):
                    path = self.dest / name
                    if kind == "file": path.write_text("custom")
                    elif kind == "directory": path.mkdir()
                    elif kind == "foreign-link": path.symlink_to(self.root / "foreign" / name)
                    elif kind == "old-checkout": path.symlink_to(self.root / "old" / "skills" / name)
                    else: path.symlink_to(self.skills / (name + "-custom"))
                self.install()
                self.assertFalse(self.backups.exists())
                for name in ("install-memory", "initialize-documentation"):
                    path = self.dest / name
                    self.assertTrue(os.path.lexists(path))
                    if path.is_dir() and not path.is_symlink(): path.rmdir()
                    else: path.unlink()

    def test_new_name_conflict_stops_before_retirement(self):
        (self.dest / "install-memory").symlink_to(self.skills / "install-memory")
        for name in ("planner", "initialize-coherence"):
            with self.subTest(name=name):
                conflict = self.dest / name
                conflict.write_text("owner data")
                with self.assertRaises(ValueError): self.install()
                self.assertTrue((self.dest / "install-memory").is_symlink())
                self.assertEqual(conflict.read_text(), "owner data")
                conflict.unlink()

    def test_documentation_conflict_preserved(self):
        self.docs.mkdir(); (self.docs / self.guidance.name).write_text("foreign docs")
        with self.assertRaises(ValueError): self.install()
        self.assertFalse((self.dest / "planner").exists())

    def test_settings_preserve_unrelated_values(self):
        self.settings.write_text(json.dumps({"skills": [str(self.skills), "/foreign/skills"], "custom": {"keep": True}}))
        self.settings.chmod(0o600)
        self.install()
        self.assertEqual(json.loads(self.settings.read_text()), {"skills": ["/foreign/skills"], "custom": {"keep": True}})
        self.assertEqual(self.settings.stat().st_mode & 0o777, 0o600)

    def test_bad_settings_stop_before_writes(self):
        for contents in ("not-json", "[]", '{"skills": "not-a-list"}', '{"skills": [1]}'):
            with self.subTest(contents=contents):
                self.settings.write_text(contents)
                (self.dest / "install-memory").symlink_to(self.skills / "install-memory")
                with self.assertRaises(ValueError): self.install()
                self.assertFalse((self.dest / "planner").exists())
                self.assertEqual(self.settings.read_text(), contents)
                self.assertTrue((self.dest / "install-memory").is_symlink())
                self.assertFalse(self.backups.exists())
                (self.dest / "install-memory").unlink()

    def test_retirement_race_preserves_replaced_foreign_link(self):
        old = self.dest / "install-memory"
        old.symlink_to(self.skills / "install-memory")
        foreign = self.root / "foreign"
        original = links.backup
        def replace_before_backup(path, *args, **kwargs):
            path.unlink(); path.symlink_to(foreign)
            return original(path, *args, **kwargs)
        with mock.patch.object(links, "backup", side_effect=replace_before_backup):
            with self.assertRaisesRegex(ValueError, "retired destination changed concurrently"):
                self.install()
        self.assertEqual(links.target(old), foreign)
        self.assertFalse(self.backups.exists())

    def test_settings_byte_race_preserves_equivalent_json(self):
        original = json.dumps({"skills": [str(self.skills)], "custom": True})
        changed = original + "\n\n"
        self.settings.write_text(original)
        symlink = Path.symlink_to
        def replace_settings(path, *args, **kwargs):
            self.settings.write_text(changed)
            return symlink(path, *args, **kwargs)
        with mock.patch.object(Path, "symlink_to", new=replace_settings):
            with self.assertRaisesRegex(ValueError, "settings changed concurrently"):
                self.install()
        self.assertEqual(self.settings.read_text(), changed)

    def test_retirement_race_during_backup_directory_creation(self):
        old = self.dest / "initialize-documentation"
        old.symlink_to(self.skills / "initialize-documentation")
        mkdir = Path.mkdir
        def replace(path, *args, **kwargs):
            if path == self.backups:
                old.unlink(); old.symlink_to(self.root / "foreign")
            return mkdir(path, *args, **kwargs)
        with mock.patch.object(Path, "mkdir", new=replace):
            with self.assertRaisesRegex(ValueError, "retired destination changed concurrently"):
                self.install()
        self.assertEqual(links.target(old), self.root / "foreign")
        self.assertEqual(list(self.backups.iterdir()), [])

    def test_settings_race_after_temp_write_preserves_foreign_bytes(self):
        self.settings.write_text(json.dumps({"skills": [str(self.skills)]}))
        chmod = os.chmod
        changed = '{"custom": "concurrent owner change"}'
        def replace(path, *args, **kwargs):
            self.settings.write_text(changed)
            return chmod(path, *args, **kwargs)
        with mock.patch.object(links.os, "chmod", side_effect=replace):
            with self.assertRaisesRegex(ValueError, "settings changed concurrently"):
                self.install()
        self.assertEqual(self.settings.read_text(), changed)
        self.assertEqual(list(self.root.glob("settings.json.*.tmp")), [])

    def test_new_link_race_never_overwrites_foreign_file(self):
        mkdir = Path.mkdir
        conflict = self.dest / "initialize-coherence"
        def replace(path, *args, **kwargs):
            if path == self.docs:
                conflict.write_text("concurrent owner work")
            return mkdir(path, *args, **kwargs)
        with mock.patch.object(Path, "mkdir", new=replace):
            with self.assertRaises(FileExistsError): self.install()
        self.assertEqual(conflict.read_text(), "concurrent owner work")

    def test_current_link_race_preserves_foreign_work(self):
        self.install()
        original = Path.mkdir
        def replace_link(path, *args, **kwargs):
            if path == self.docs:
                link = self.dest / "planner"
                link.unlink(); link.symlink_to(self.root / "foreign")
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, "mkdir", new=replace_link):
            with self.assertRaisesRegex(ValueError, "destination changed concurrently"):
                self.install()
        self.assertEqual(links.target(self.dest / "planner"), self.root / "foreign")


class RpcDriverTests(unittest.TestCase):
    def test_actual_offline_fake_rpc_process(self):
        # No pi/model process: exercises LF framing and UI correlation through real pipes.
        program = '''import json,sys
request=json.loads(sys.stdin.buffer.readline())
print(json.dumps({"type":"response","success":True,"id":request["id"]}),flush=True)
print(json.dumps({"type":"extension_ui_request","id":"ui-1","method":"select","title":"Choose workflow","options":["TinySpec","Standard"]}),flush=True)
answer=json.loads(sys.stdin.buffer.readline())
assert answer["id"]=="ui-1" and answer["value"]=="TinySpec"
print(json.dumps({"type":"message_end","message":{"role":"assistant","content":[{"type":"text","text":"unicode \\u2028 remains in one frame"}]}}),flush=True)
print(json.dumps({"type":"agent_settled"}),flush=True)
sys.stdin.buffer.read()
'''
        with tempfile.TemporaryDirectory() as directory:
            result = rpc.record([sys.executable, "-c", program], "prompt", [{"method": "select", "title_contains": "workflow", "response": {"value": "TinySpec"}}], Path(directory) / "out", directory, timeout=5)
            self.assertEqual(result["driver"], "COMPLETED", result)
            self.assertIn("NOT EVALUATED", result["acceptance"])

    def test_runtime_failures_never_report_completion(self):
        cases = [
            ({"type": "response", "success": False, "error": "provider blocked"}, "RPC command failed"),
            ({"type": "tool_execution_end", "isError": True}, "tool failed"),
            ({"type": "tool_execution_start", "toolName": "bash"}, "read-only"),
            ({"type": "extension_ui_request", "id": "q", "method": "confirm"}, "unscripted"),
            ({"type": "extension_error", "error": "load failed"}, "extension failed"),
        ]
        for event, diagnostic in cases:
            with self.subTest(event=event), tempfile.TemporaryDirectory() as directory:
                program = "import json,sys; sys.stdin.buffer.readline(); print(" + repr(json.dumps(event)) + ",flush=True); sys.stdin.buffer.read()"
                result = rpc.record([sys.executable, "-c", program], "prompt", [], Path(directory) / "out", directory, timeout=2)
                self.assertEqual(result["driver"], "FAIL", result)
                self.assertIn(diagnostic, result["error"])

    def test_deadline_is_failure_not_empty_error_success(self):
        with tempfile.TemporaryDirectory() as directory:
            result = rpc.record([sys.executable, "-c", "import sys; sys.stdin.buffer.read()"], "prompt", [], Path(directory) / "out", directory, timeout=0.1)
            self.assertEqual(result["driver"], "FAIL", result)
            self.assertTrue(result["error"])

    def test_unoffered_option_and_unexpected_dialog(self):
        request = {"id": "x", "method": "select", "title": "Choose", "options": ["Standard"]}
        with self.assertRaises(ValueError):
            rpc.answer_dialog(request, {"method": "select", "response": {"value": "TinySpec"}})
        with self.assertRaises(ValueError):
            rpc.answer_dialog(request, {"method": "input", "response": {"value": "TinySpec"}})


class ComparativeCarrierTests(unittest.TestCase):
    def test_owner_comparison_and_graph_tradeoff_mutations(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        for key, clause, label in (
            ("routing", "actual shortfall or select the smaller option", "routing-comparison:"),
            ("routing", "none is verified/permitted", "routing-comparison:"),
            ("routing", "strict requirement versus a default preference", "routing-comparison:"),
            ("coordinator", "separate comparative Family and Effort rationales", "routing-tradeoff:"),
        ):
            with self.subTest(clause=clause):
                changed = dict(texts)
                changed[key] = changed[key].replace(clause, "REMOVED", 1)
                self.assertTrue(any(e.startswith(label) for e in checker.check_contracts(changed)))


if __name__ == "__main__":
    unittest.main()
