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


class ProportionateValidationTests(unittest.TestCase):
    """Instruction-removal regressions, not behavioral/model evaluations."""

    def assert_clause_required(self, key, clause, diagnostic):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        self.assertIn(clause, texts[key])
        texts[key] = texts[key].replace(clause, "", 1)
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

    def test_schema_security_durability_retain_necessary_checks(self):
        self.assert_clause_required("planner", "migration, authorization or persistence", "validation-risk")

    def test_optional_checks_cannot_silently_block(self):
        for key, clause, diagnostic in (
            ("planner", "Optional checks are not acceptance blockers", "validation-authority"),
            ("tasks", "Optional checks do not become blockers", "validation-tasks"),
            ("coordinator", "optional hardening/broader regression is not a blocker", "validation-execution"),
        ):
            with self.subTest(key=key):
                self.assert_clause_required(key, clause, diagnostic)

    def test_owner_required_checks_need_authority_to_change(self):
        self.assert_clause_required("planner",
            "Never drop an owner-required check or approved\nsafety criterion without explicit authority",
            "validation-authority")
        self.assert_clause_required("coordinator", "leave acceptance blocked", "validation-execution")
        self.assert_clause_required("tasks", "owner-required criteria", "validation-tasks")

    def test_timeout_narrows_remaining_work_without_blind_retry(self):
        for clause in (
            "checkpoint early", "retain valid completed\n  evidence",
            "narrow the remaining step instead of restarting the entire batch",
            "timeout alone is not retry authority",
        ):
            with self.subTest(clause=clause):
                self.assert_clause_required("coordinator", clause, "validation-timeout")

    def test_reuse_and_causal_repairs_avoid_repeated_intake(self):
        for clause in ("Reuse valid unchanged evidence", "Avoid repeated historical intake", "actually blocks"):
            with self.subTest(clause=clause):
                self.assert_clause_required("planner", clause, "validation-reuse")


class InstructionTests(unittest.TestCase):
    def setUp(self):
        self.texts = checker.load_texts()

    def test_candidate_contract(self):
        self.assertEqual(checker.check_contracts(self.texts), [])

    def test_stage_routing_is_independent_not_fixed_class(self):
        self.assertIn("## Stage family and effort selection", self.texts["planner"])
        self.assertNotIn("— `opus-class`", self.texts["planner"])

    def test_stage_rubric_capability_and_combined_preview_guard_deletions(self):
        cases = (
            ("planner", "## Stage family and effort selection", "independent family suitability and least-adequate supported effort after decomposition", "stage-routing"),
            ("planner", "## Stage family and effort selection", "permitted usable exact binding/effort", "stage-routing"),
            ("planner", "## Stage family and effort selection", "Unsupported runtime\neffort or missing hard capability stops", "stage-routing"),
            ("planner", "## Stage family and effort selection", "Risk strengthens safeguards, not high effort or strongest-family selection", "stage-routing"),
            ("planner", "## Stage family and effort selection", "fresh reviewer role\ndoes not justify high", "stage-routing"),
            ("planner", "## Stage family and effort selection", "Weak oracles return for decomposition", "stage-routing"),
            ("planner", "## Stage family and effort selection", "targeted research or explicit bounded owner", "stage-routing"),
            ("planner", "## Stage family and effort selection", "gap, rationale, allowed scope, remaining validation", "stage-routing"),
            ("planner", "## Stage family and effort selection", "never silently switch models", "stage-routing"),
            ("planner", "## Assignment preview and combined final approval", "complete task-by-task assignment preview plus independent final implementation reviewer", "assignment-preview"),
            ("planner", "## Assignment preview and combined final approval", "exact concrete binding/version", "assignment-preview"),
            ("planner", "## Assignment preview and combined final approval", "independent\neffort", "assignment-preview"),
            ("planner", "## Assignment preview and combined final approval", "benchmark citations/coverage gaps", "assignment-preview"),
            ("planner", "## Assignment preview and combined final approval", "in the same final approval", "assignment-preview"),
            ("planner", "## Assignment preview and combined final approval", "current artifact/preview revision evidence", "assignment-preview"),
            ("planner", "## Assignment preview and combined final approval", "No routine second assignment-approval question", "assignment-preview"),
            ("brainstorm", "## Capability preflight", "provider-documented permitted usable exact binding/effort", "helper-routing"),
            ("helper", "## Preflight", "Supported no-row pairings", "helper-routing"),
        )
        for key, heading, guard, label in cases:
            with self.subTest(guard=guard):
                changed = dict(self.texts)
                body = checker.section(changed[key], heading)
                self.assertEqual(body.count(guard), 1)
                changed[key] = changed[key].replace(body, body.replace(guard, "", 1), 1)
                self.assertTrue(any(e.startswith(label + ":") for e in checker.check_contracts(changed)))

    def test_risk_role_unsupported_effort_no_row_and_second_gate_negative_policies(self):
        for policy in (
            "Risk always selects high effort", "Reviewer role always selects high effort",
            "Weak oracles select maximum effort", "Always default to medium effort",
            "No benchmark row forbids a supported pairing", "Unsupported runtime effort may proceed",
            "Catalog presence authorizes execution", "Ask a second routine assignment question",
            "Silently switch the selected model",
        ):
            with self.subTest(policy=policy):
                changed = dict(self.texts); changed["planner"] += "\n" + policy
                self.assertTrue(any(e.startswith("family-effort-unsafe:") for e in checker.check_contracts(changed)))

    def test_preview_moved_after_routes_is_rejected(self):
        changed = dict(self.texts)
        p = changed["planner"]
        start = p.index("## Assignment preview and combined final approval")
        end = p.index("### TinySpec path", start)
        preview = p[start:end]
        changed["planner"] = p[:start] + p[end:] + "\n" + preview
        self.assertTrue(any(e.startswith("assignment-preview:") for e in checker.check_contracts(changed)))

    def test_supported_no_row_uncertainty_and_non_escalation_examples(self):
        # Labelled instruction walkthrough, not a model allocation or provider run.
        routing = checker.section(self.texts["planner"], "## Stage family and effort selection")
        for profile, obligations in (
            ("simulated high-risk strong-oracle lower effort", ("Risk strengthens safeguards, not high effort", "least-adequate supported effort after decomposition")),
            ("simulated fresh reviewer lower effort", ("fresh reviewer role\ndoes not justify high",)),
            ("simulated weak-oracle work returned to decomposition", ("Weak oracles return for decomposition", "not reflexive max")),
            ("simulated supported no-row pairing with bounded owner disposition", ("Supported no-row pairings", "gap, rationale, allowed scope, remaining validation", "absence alone never bars support")),
        ):
            with self.subTest(profile=profile):
                for obligation in obligations:
                    self.assertIn(obligation, routing)

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
            ("planner", "**`spec_create` — owner-selected family/effort", "**`spec_create` — unsupported runtime effort", "spec:"),
            ("planner", "specification approval before `plan_create`", "approval later", "spec:"),
            ("planner", "Only when no adapter is invoked", "After the adapter returns", "plan:"),
            ("planner", "do not create the plan again", "create the plan again", "plan:"),
            ("planner", "renewed specification approval", "existing specification approval", "plan:"),
            ("planner", "no producer self-review/correction", "self-review permitted", "task-stage:"),
            ("planner", "independent owner-selected reviewer", "implementer reviewer", "review:"),
            ("approval", "before calling `ask_user`", "after calling `ask_user`", "approval:"),
            ("approval", "4–6 short bullets", "unstructured paragraphs", "approval:"),
            ("planner", "brief bullet-list executive summary", "summary in tool context", "tiny-flow:"),
            ("planner", "immediately continue to `plan_create`", "wait for another prompt", "spec:"),
            ("planner", "immediately proceed to handoff", "report readiness and stop", "tiny-flow:"),
            ("planner", "Do not end the turn merely to report approval", "End the turn after approval", "continuation:"),
            ("planner", "automatically invoke `coordinate-implementation`", "wait for a separate execution request", "final-continuation:"),
            ("approval", "inside tasks", "separate new source", "legacy:"),
            ("tasks", "30%", "100%", "task-contract:"),
            ("brainstorm", "no more than three items", "unbounded agenda", "brainstorm:"),
            ("brainstorm", "Only in selected-production", "In any mode", "brainstorm:"),
            ("coordinator", "Commit each task's verified changes as one focused commit", "Commit each batch", "execution-freeze:"),
            ("coordinator", "only asynchronously in the background", "foreground is fine", "execution-freeze:"),
            ("coordinator", "separate TinySpec/source and tasks", "source checklist only", "intake:"),
            ("adoption", "every unrelated byte", "custom content", "adoption:"),
            ("docs", "not substantive implementation authorization", "implementation authorization", "docs:"),
        ]
        for key, old, new, diagnostic in mutations:
            with self.subTest(mutation=old):
                self.assertIn(old, self.texts[key])
                changed = dict(self.texts)
                changed[key] = changed[key].replace(old, new, 1)
                errors = checker.check_contracts(changed)
                self.assertTrue(any(e.startswith(diagnostic) for e in errors), errors)

    def test_bulleted_brief_and_automatic_continuation_contract(self):
        self.assertIn("4–6 short bullets", self.texts["approval"])
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
            for field in ("Outcome", "Files/interfaces", "Acceptance", "Capabilities", "Model class"):
                self.assertIn(f"**{field}**", source)

    def test_custom_lint_is_not_coupled_to_suite(self):
        with tempfile.TemporaryDirectory() as directory:
            run = subprocess.run(["bash", str(HERE / "check-skills-lint.sh"), directory], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("SKIP planner workflow checks", run.stdout)


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

    def test_lost_coordinator_reflection_fails_with_shared_summary_intact(self):
        texts = checker.load_texts()
        body = checker.section(texts["coordinator"], "## Coordination reflection and guideline approval")
        texts["coordinator"] = texts["coordinator"].replace(body, "", 1) + "\n## Summary only\n" + body
        self.assertIn("Exact guideline approval", texts["coordination"])
        self.assertTrue(any(e.startswith("coordination-approval:") for e in checker.check_contracts(texts)))

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

    def test_reflection_phase_after_review_and_checkpoint_inside_execution(self):
        text = checker.load_texts()["coordinator"]
        self.assertLess(text.index("## Execute and Integrate"), text.index("### Coordination evidence checkpoint"))
        self.assertLess(text.index("### Coordination evidence checkpoint"), text.index("## Review and Acceptance"))
        self.assertLess(text.index("## Review and Acceptance"), text.index("## Coordination reflection and guideline approval"))


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

    def test_combined_assignment_preview_is_content_bound_in_both_routes(self):
        # Generic artifact-drift oracle also binds the reviewed assignment preview.
        # No new production approval engine; events are simulated offline.
        for depth in ("TinySpec", "Standard"):
            with self.subTest(depth=depth):
                events = scenario()
                events[2] = end("choose", depth)
                events.insert(4, {"type": "artifact_snapshot", "path": "assignments.md", "digest": "reviewed-pairs-and-uncertainty"})
                contract = {**self.contract, "expected_depth": depth}
                self.assertEqual(trace.check(events, contract), [])
                events.insert(-1, {"type": "artifact_snapshot", "path": "assignments.md", "digest": "changed-pair"})
                self.assertTrue(any("changed" in e for e in trace.check(events, contract)))

    def test_standard_override(self):
        events = scenario(); events[2] = end("choose", "Standard")
        self.assertEqual(trace.check(events, {**self.contract, "expected_depth": "Standard"}), [])


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


if __name__ == "__main__":
    unittest.main()
