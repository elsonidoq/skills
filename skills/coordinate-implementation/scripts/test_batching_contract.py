#!/usr/bin/env python3
"""Static checks for context-continuity batching instructions."""

from copy import deepcopy
from pathlib import Path
import unittest


TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")


RUBRIC_PATH = Path(__file__).parents[1] / "references" / "batch-routing.md"




def carrier(text, heading):
    marker = "## " + heading
    start = text.find(marker)
    if start < 0:
        return ""
    import re
    match = re.search(r"(?:\n| )## ", text[start + len(marker):])
    end = start + len(marker) + match.start() if match else len(text)
    return " ".join(text[start:end].split())


class CarrierTests(unittest.TestCase):
    def assert_carrier_guards(self, heading, clauses):
        body = carrier(TEXT, heading)
        for clause in clauses:
            with self.subTest(heading=heading, clause=clause):
                self.assertIn(clause, body)
                altered = " ".join(TEXT.split()).replace(body, body.replace(clause, "REMOVED"), 1)
                self.assertNotIn(clause, carrier(altered + " ## Footer " + clause, heading))

class SeedRubricTests(CarrierTests):
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
            "Family rationale", "Effort rationale", "| Luna |", "| Sol |", "| Astra |", "| Terra |",
            "Luna/max", "no universal ladder",
        ):
            with self.subTest(term=term):
                self.assertIn(term, rubric)

    def test_qualified_prior_authority_and_repair_limits(self):
        self.assertTrue(RUBRIC_PATH.is_file(), "shared batch routing seed is missing")
        rubric = RUBRIC_PATH.read_text(encoding="utf-8")
        for term in (
            "different harnesses", "Do not average", "benchmark-only eligibility",
            "empty guidelines", "override the seed", "owner/source authority",
            "unresolved architecture", "weak oracles", "Deep tool use",
            "high failure cost", "repeated negative guidance", "supported effort",
            "callable binding", "unknown", "diagnose", "invalidated",
        ):
            with self.subTest(term=term):
                self.assertIn(term, rubric)
        self.assertIn("../../../specs/002-batch-routing-contracts/research.md", rubric)

    def test_family_examples_have_one_independent_row_per_family(self):
        rubric = RUBRIC_PATH.read_text(encoding="utf-8")
        start = rubric.index("## Provisional family and effort choices")
        end = rubric.index("## Evidence limits", start)
        body = rubric[start:end]
        rows = [line for line in body.splitlines() if line.startswith("| ")]
        self.assertEqual([row.split("|")[1].strip() for row in rows[2:6]], ["Luna", "Sol", "Astra", "Terra"])
        self.assertNotIn("Astra or Terra", body)
        for clause in ("family does not imply an effort", "no fixed family-to-effort step follows",
                       "no family ranking follows", "neither require equal proposal rows nor enumerate variants"):
            with self.subTest(clause=clause):
                self.assertIn(clause, body)
                altered = body.replace(clause, "REMOVED", 1)
                self.assertNotIn(clause, carrier(altered + " ## Footer " + clause,
                                                  "Provisional family and effort choices"))


def approval_errors(text):
    graph = carrier(text, "Prepare Approved Execution")
    guards = {
        "table": "entire proposed execution table", "description": "outcome",
        "profile": "exact binding/effort", "approval": "Implementation approval is not routing approval",
        "gate": "before writes or dispatch", "question": "use `ask_user`",
        "resume": "Reuse verified unchanged approval", "change": "profiles renew affected rows",
        "assessment-order": "Assess each batch", "no-default": "not a universal default",
        "uniform-valid": "one exact profile per invocation",
    }
    errors = [label for label, phrase in guards.items() if phrase not in graph]
    if "Do not ask for routine batching approval" in graph:
        errors.append("approval-bypass")
    return errors


class ApprovalGateTests(CarrierTests):
    def test_complete_table_and_assessment_gate(self):
        self.assert_carrier_guards('Prepare Approved Execution', ('explicit batch/profile approval', 'entire proposed execution table', 'not a universal default'))

    def test_missing_table_description_profile_approval_and_default_guards(self):
        self.assert_carrier_guards('Prepare Approved Execution', ('entire proposed execution table', 'outcome', 'exact binding/effort', 'Implementation approval is not routing approval', 'before writes or dispatch', 'use `ask_user`', 'Assess each batch', 'not a universal default'))

    def test_symbolic_resumed_and_changed_plan_approval(self):
        self.assertEqual(approval_errors(TEXT), [])
        approved = (("B1", ("T001", "T002"), "symbolic/sol:medium"),)
        for current, answer, expected in (
            (approved, "approve", True), (approved, "cancel", False),
            (approved, "ambiguous", False), (approved, None, False),
            ((("B1", ("T001", "T002"), "symbolic/sol:low"),), "approve", False),
            ((("B1", ("T001",), "symbolic/sol:medium"),), "approve", False),
        ):
            # Simulated comparison only: unchanged durable content + explicit approval.
            self.assertEqual(answer == "approve" and current == approved, expected)
        for phrase, label in (("Reuse verified unchanged approval", "resume"),
                              ("profiles renew affected rows", "change")):
            self.assertIn(label, approval_errors(" ".join(TEXT.split()).replace(phrase, "REMOVED", 1)))


def dispatch_seam_errors(text):
    body = carrier(text, "Delegate")
    guards = (
        "Once required preparation is satisfied, dispatch", "Reopen only affected decisions/checks",
        "routine progress is not invalidation", "one direct asynchronous worker",
        "including internal sequential tasks", "does not justify a workflow wrapper",
        "earned orchestration need", "Both shapes retain all gates",
        "whole unchanged REQUIRED union before coding",
    )
    errors = [phrase for phrase in guards if phrase not in body]
    for unsafe in ("Use workflowScript merely because it is a batch", "Ban all one-child workflows",
                   "Migrate existing runs to direct launch", "Direct delegation counts as local execution",
                   "Skip profile validation for direct launch", "Skip approval gates for workflow launch"):
        if unsafe in body:
            errors.append(unsafe)
    return errors


class DispatchSeamTests(CarrierTests):
    def test_actual_carrier_terminates_preparation(self):
        self.assertEqual(dispatch_seam_errors(TEXT), [])

    def test_removal_is_not_rescued_by_footer(self):
        for phrase in dispatch_seam_errors(""):
            with self.subTest(phrase=phrase):
                normalized = " ".join(TEXT.split())
                self.assertIn(phrase, normalized)
                altered = normalized.replace(phrase, "REMOVED", 1)
                self.assertIn(phrase, dispatch_seam_errors(altered + " ## Execute and Integrate Footer: " + phrase))

    def test_launch_shortcuts_and_categorical_bans_are_rejected(self):
        for unsafe in ("Use workflowScript merely because it is a batch", "Ban all one-child workflows",
                       "Migrate existing runs to direct launch", "Direct delegation counts as local execution",
                       "Skip profile validation for direct launch", "Skip approval gates for workflow launch"):
            with self.subTest(unsafe=unsafe):
                altered = TEXT.replace("## Execute and Integrate", unsafe + "\n\n## Execute and Integrate", 1)
                self.assertIn(unsafe, dispatch_seam_errors(altered))

    def test_symbolic_direct_multitask_and_justified_workflow_arguments(self):
        self.assertEqual(dispatch_seam_errors(TEXT), [])
        selected = "symbolic/sol:medium"
        for shape, reason in (("direct", None), ("workflow", "named continuation: inspect retained child on recovery")):
            with self.subTest(shape=shape):
                args = {"agent": "worker", "task": "T001→T002→T003 sequentially", "model": selected, "async": True}
                brief = {"strategy": "delegated", "orchestration_reason": reason}
                invocation = args if shape == "direct" else {"workflowScript": {"child": args}}
                child = invocation if shape == "direct" else invocation["workflowScript"]["child"]
                self.assertEqual(child["model"], selected)
                self.assertTrue(child["async"])
                self.assertEqual(brief["strategy"], "delegated")
                if shape == "workflow":
                    self.assertTrue(brief["orchestration_reason"].startswith("named continuation:"))
                self.assertEqual(approval_errors(TEXT), [])
                for gate in ("permission", "binding", "effort", "tools", "owner", "manual"):
                    self.assertIsNone(SimulatedProfileTraceTests.simulated_dispatch(selected, **{gate: False})["args"])


def preparation_trace_errors(text, trace):
    """Validate bounded offline action sequences against the real carrier, not execute routing."""
    errors = dispatch_seam_errors(text) + approval_errors(text)
    recovery = " ".join(text.split("## Recover Context", 1)[-1].split(
        "## Prepare Approved Execution", 1)[0].split())
    for phrase in ("running child means inspect/wait, not duplicate dispatch",
                   "unknown child status"):
        if phrase not in recovery:
            errors.append(phrase)
    for event in trace:
        action, reason = event["action"], event["reason"]
        if event.get("child") in ("running", "unknown"):
            required = "inspect/wait" if event["child"] == "running" else "reconcile"
            if action != required or reason != "existing child":
                errors.append("child reconciliation")
        elif event.get("gap"):
            if action != "blocked" or reason != event["gap"] or not event.get("resolution"):
                errors.append("precise missing condition")
        elif event.get("changed"):
            if action != "reopen" or reason != event["changed"] or event.get("affected") != event["changed"]:
                errors.append("affected-only reopen")
        elif event.get("ready"):
            if action != "dispatch" or reason != "mandatory preparation complete; state commit not required":
                errors.append("redundant post-ready preparation")
    return errors


class PreparationTraceTests(CarrierTests):
    """Explicit events/actions are symbolic observations, never child/runtime evidence."""
    def test_ready_dispatch_and_redundant_preparation_rejected(self):
        ready = {"ready": True, "action": "dispatch", "reason": "mandatory preparation complete; state commit not required"}
        for ordinary in ("initial readiness", "unchanged passing check", "prose polish"):
            with self.subTest(event=ordinary):
                trace = [dict(ready, event=ordinary)]
                self.assertEqual(preparation_trace_errors(TEXT, trace), [])
                trace[0]["action"] = "prepare again"
                self.assertIn("redundant post-ready preparation", preparation_trace_errors(TEXT, trace))

    def test_concrete_invalidation_reopens_only_affected_preparation(self):
        trace = []
        for changed in ("contradiction", "failed prerequisite", "scope change", "profile", "permission", "runtime", "workspace ownership"):
            trace.append({"changed": changed, "action": "reopen", "reason": changed, "affected": changed})
        self.assertEqual(preparation_trace_errors(TEXT, trace), [])
        for event in trace:
            with self.subTest(changed=event["changed"]):
                self.assertIn("affected-only reopen", preparation_trace_errors(TEXT, [dict(event, affected="all preparation")]))

    def test_missing_gates_have_precise_stop_and_smallest_resolution(self):
        for gap, resolution in (("approval", "obtain current routing approval"),
                                ("profile support", "verify selected effort support"),
                                ("ownership", "reconcile affected dirty path"),
                                ("REQUIRED manual proof", "supply original required manual evidence")):
            with self.subTest(gap=gap):
                event = {"gap": gap, "action": "blocked", "reason": gap, "resolution": resolution}
                self.assertEqual(preparation_trace_errors(TEXT, [event]), [])
                self.assertIn("precise missing condition", preparation_trace_errors(TEXT, [dict(event, action="dispatch")]))

    def test_running_inspect_wait_and_unknown_reconcile_never_replace(self):
        for child, action in (("running", "inspect/wait"), ("unknown", "reconcile")):
            with self.subTest(child=child):
                event = {"child": child, "action": action, "reason": "existing child", "event": "healthy worker progress"}
                self.assertEqual(preparation_trace_errors(TEXT, [event]), [])
                self.assertIn("child reconciliation", preparation_trace_errors(TEXT, [dict(event, action="replacement dispatch")]))

    def test_ready_trace_cannot_pass_missing_actual_carrier(self):
        trace = [{"ready": True, "action": "dispatch", "reason": "mandatory preparation complete; state commit not required"}]
        phrase = "Reopen only affected decisions/checks"
        altered = TEXT.replace(phrase, "REMOVED", 1) + "\n## Footer\n" + phrase
        self.assertIn(phrase, preparation_trace_errors(altered, trace))


class BatchingContractTests(CarrierTests):
    def test_coherent_sequential_work_is_not_split_by_incidental_boundaries(self):
        self.assert_carrier_guards('Prepare Approved Execution', ('shared files, phase headings and internal dependencies alone do not require splits', 'One writer verifies and commits each producer before its consumer'))

    def test_only_evidenced_boundaries_split_and_order_stays_fixed(self):
        self.assert_carrier_guards('Prepare Approved Execution', ('Normally 4–7 related tasks, not a quota', 'material profile, context, permission, owner-gate', 'never silently reorder', 'sequentially, never in parallel'))

    def test_batch_size_guideline_and_small_batch_exceptions(self):
        # Static instruction checks, not a runtime batching algorithm or obedience test.
        self.assert_carrier_guards('Prepare Approved Execution', (
            'Size by implementation complexity, shared context, verification cost and observed context capacity',
            'Avoid 1–2-task batches unless a concrete split constraint requires them; briefly justify each exception',
            'Merge small remainder batches into an adjacent batch when practical',
            'never exceed workable context merely to meet the range',
            'Do not default an entire large specification to one batch',
        ))

    def test_checkpoints_and_review_do_not_add_task_handoffs(self):
        self.assert_carrier_guards('Delegate', (
            'healthy internal continuation without routine coordinator approval',
        ))
        self.assert_carrier_guards('Review and Acceptance', (
            'No per-task reviews', 'one fresh independent final review',
        ))

    def test_selection_to_dispatch_contract(self):
        self.assert_carrier_guards('Prepare Approved Execution', ('six-factor', 'Family and Effort rationales', 'callable binding', 'supported effort', 'at assignment and dispatch', 'no silent settings/agent override', 'unobservable actual binding/effort is unknown'))

    def test_rotation_uses_observed_context_and_durable_handoff(self):
        self.assert_carrier_guards('Delegate', ('selected profile, supported resume', 'adequate relevant retained context', 'narrow a fresh brief', 'Rotation is not retry authority'))


class SimulatedProfileTraceTests(CarrierTests):
    """Offline decision/argument fixtures tied to instruction carriers, not a runtime router."""

    @staticmethod
    def simulated_dispatch(selected, *, permission=True, binding=True, effort=True,
                           tools=True, owner=True, manual=True):
        # Symbolic gate fixture only; no installed runtime/provider invocation.
        if not all((permission, binding, effort, tools, owner, manual)):
            return {"disposition": "blocked", "args": None}
        return {"disposition": "ready", "args": {"model": selected}, "observed_effort": "unknown"}

    def test_empty_guidelines_luna_medium(self):
        rubric = RUBRIC_PATH.read_text()
        self.assertIn("With empty guidelines", rubric)
        self.assertIn("Shallow, closed-design work with strong contracts", rubric)
        decision = {"tasks": ["T001", "T002"], "evidence": "none", "proposal": "symbolic/luna:medium",
                    "family": "closed design, shallow tools, cheap recovery", "effort": "bounded inference"}
        self.assertEqual(decision["proposal"], "symbolic/luna:medium")
        self.assertEqual(decision["evidence"], "none")
        self.assertIn("owner-selected exact profile", TEXT)
        actual = self.simulated_dispatch(decision["proposal"])
        self.assertEqual(actual["disposition"], "ready")
        self.assertEqual(actual["args"]["model"], "symbolic/luna:medium")

    def test_luna_max_exact_effort_to_dispatch(self):
        self.assertIn("Luna/max remains a symbolic supported effort only when it has an explicit extra-reasoning", RUBRIC_PATH.read_text())
        selected = "symbolic/luna:max"
        brief = {"selected": selected, "family": "bounded multi-file, strong oracles",
                 "effort": "moderate residual reasoning needs extra budget"}
        args = self.simulated_dispatch(brief["selected"])["args"]
        self.assertEqual(args["model"], "symbolic/luna:max")
        self.assertIn("Copy the owner-selected exact profile", TEXT)

    def test_deep_tools_and_weak_oracle_stop_optimistic_luna(self):
        rubric = RUBRIC_PATH.read_text()
        self.assertIn("Deep tool use, weak oracles", rubric)
        self.assertIn("defeat optimistic Luna routing", rubric)
        self.assertIn("six-factor", TEXT)
        for case in ("deep tools", "weak oracle"):
            with self.subTest(case=case):
                # Owner/design gate prevents launch while assessment lacks an authorized stronger option.
                actual = self.simulated_dispatch("symbolic/luna:medium", owner=False)
                self.assertEqual(actual["disposition"], "blocked")
                self.assertIsNone(actual["args"])
                self.assertIn("stronger option only with adequate contracts", rubric)

    def test_unsupported_binding_effort_and_permission_block(self):
        self.assertIn("missing permission/binding/effort/tool support blocks dispatch", TEXT)
        for missing in ("permission", "binding", "effort", "tools", "owner", "manual"):
            gates = dict.fromkeys(("permission", "binding", "effort", "tools", "owner", "manual"), True)
            gates[missing] = False
            actual = self.simulated_dispatch("symbolic/luna:medium", **gates)
            args = actual["args"]
            with self.subTest(missing=missing):
                self.assertIsNone(args)
        self.assertIn("names/suffixes alone are not proof", TEXT)
        self.assertIn("unmet manual/permission gates block reliance", TEXT)

    def test_unobservable_actual_effort_is_unknown(self):
        self.assertIn("binding/effort is unknown", TEXT)
        selected = "symbolic/luna:max"
        returned = {"selected": selected, "observed_model": "symbolic/luna", "observed_effort": "unknown"}
        self.assertEqual(returned["observed_effort"], "unknown")
        self.assertNotEqual(returned["observed_effort"], selected.split(":")[1])


# Offline sample artifacts only: these helpers do not implement a runtime router.
def sample_batch_contract(selected="symbolic/luna:medium"):
    tasks = [
        {"id": "T005", "baseline": "fixture-base", "owned_paths": ["fixture/producer.md"],
         "required": [{"ref": "T005/V1", "criterion": "producer exports stable item IDs",
                       "observable_key": "producer_ids", "expected": ["V1", "V2"],
                       "check": "fixture shared-check", "expected_evidence": "shared-output",
                       "manual_gate": "scope inspection", "permission_gate": "local only"}]},
        {"id": "T006", "baseline": "fixture-task-005", "owned_paths": ["fixture/consumer.md"],
         "required": [{"ref": "T006/V1", "criterion": "consumer preserves every producer ID",
                       "observable_key": "consumer_ids", "expected": ["V1", "V2"],
                       "check": "fixture shared-check", "expected_evidence": "shared-output",
                       "manual_gate": "scope inspection", "permission_gate": "local only"}]},
    ]
    brief = {"selected": selected, "tasks": tasks,
             "required_union": [item for task in tasks for item in task["required"]],
             "producer_checks": ["T005/V1 before T006"],
             "checkpoint_convention": "per-task verified commit with runtime return"}
    returned = {
        "observed_profile": "unknown",
        "items": {item["ref"]: {"status": "pass", "evidence": "shared-output", "reason": None}
                  for item in brief["required_union"]},
        "revision": "fixture-task-006", "environment": "offline-python",
        "item_revisions": {"T005/V1": "fixture-task-006", "T006/V1": "fixture-task-006"},
        "outputs": {"shared-output": {"command": "fixture shared-check", "exit": 0,
                                      "revision": "fixture-task-006", "environment": "offline-python",
                                      "observations": {"producer_ids": ["V1", "V2"],
                                                       "consumer_ids": ["V1", "V2"]}}},
        "files": ["fixture/producer.md", "fixture/consumer.md"],
        "checkpoints": [
            {"task": "T005", "baseline": "fixture-base", "result": "fixture-task-005"},
            {"task": "T006", "baseline": "fixture-task-005", "result": "fixture-task-006"},
        ],
    }
    return brief, returned


class SimulatedUnionReturnTests(CarrierTests):
    """Sample brief/return trace, not a live invocation or model performance test."""

    def test_whole_required_union_and_return_carriers(self):
        self.assert_carrier_guards('Delegate', ('whole unchanged REQUIRED union before coding', "each ID's criterion", 'smallest check', 'expected proof and pass condition', 'Missing contracts return to the producer'))

    def test_two_task_shared_check_union_and_ordered_checkpoints(self):
        brief, returned = sample_batch_contract()
        refs = [item["ref"] for item in brief["required_union"]]
        self.assertEqual(refs, ["T005/V1", "T006/V1"])
        self.assertEqual(set(returned["items"]), set(refs))
        for ref in refs:
            self.assertEqual(returned["items"][ref]["evidence"], "shared-output")
        self.assertEqual(len(returned["outputs"]), 1)  # no duplicate execution
        self.assertEqual([cp["task"] for cp in returned["checkpoints"]], ["T005", "T006"])
        for task, cp in zip(brief["tasks"], returned["checkpoints"]):
            self.assertEqual(cp["baseline"], task["baseline"])
            self.assertTrue(cp["result"])
            self.assertNotIn("evidence_checkpoint", cp)
        self.assertEqual(returned["observed_profile"], "unknown")

    def test_not_verified_return_keeps_reference_and_explicit_reason(self):
        brief, returned = sample_batch_contract()
        returned["items"]["T006/V1"] = {
            "status": "not_verified", "evidence": None,
            "reason": "required local tool unavailable; check not run",
        }
        self.assertEqual(set(returned["items"]), {i["ref"] for i in brief["required_union"]})
        self.assertEqual(returned["items"]["T006/V1"]["status"], "not_verified")
        self.assertTrue(returned["items"]["T006/V1"]["reason"])


def item_dispositions(brief, returned):
    """Illustrative task-specific proof oracle, not a runtime schema or policy engine."""
    dispositions = {}
    for item in brief["required_union"]:
        ref = item["ref"]
        result = returned["items"].get(ref, {})
        pointer = result.get("evidence")
        output = returned["outputs"].get(pointer, {})
        limitations = []
        if not result:
            limitations.append("missing item mapping")
        if result.get("status") not in ("pass", "fail"):
            limitations.append(result.get("reason") or "unrun or confidence-only report")
        if not output:
            limitations.append("missing output")
        if output.get("command") != item["check"]:
            limitations.append("irrelevant command")
        if output.get("revision") != returned["item_revisions"][ref]:
            limitations.append("stale revision")
        if output.get("environment") != returned["environment"]:
            limitations.append("wrong environment")
        observations = output.get("observations", {})
        if item["observable_key"] not in observations:
            limitations.append("irrelevant observable")
        valid_observation = not any(l in limitations for l in (
            "missing output", "irrelevant command", "stale revision", "wrong environment", "irrelevant observable"))
        violates = valid_observation and observations[item["observable_key"]] != item["expected"]
        if output.get("exit") != 0 or (result.get("status") == "fail" and not violates):
            limitations.append("conflicting proof/report")
        if not all(returned["gates"].get(ref, {}).get(g) for g in ("manual", "permission")):
            limitations.append("unmet original gate")
        disposition = "failed" if violates else "insufficient-evidence" if limitations else "satisfied"
        dispositions[ref] = {"disposition": disposition, "proof": pointer,
                             "reason": "criterion violated" if violates else "; ".join(limitations) or "relevant IDs match",
                             "limitations": limitations}
    return dispositions


def simulated_audit(brief, returned):
    """Bounded acceptance oracle for sample artifacts, not production enforcement."""
    expected = {item["ref"] for item in brief["required_union"]}
    if set(returned["items"]) != expected:
        return "blocked"
    if any(i["disposition"] != "satisfied" for i in item_dispositions(brief, returned).values()):
        return "blocked"
    allowed = {path for task in brief["tasks"] for path in task["owned_paths"]}
    if not set(returned["files"]).issubset(allowed):
        return "blocked"
    checkpoints = returned["checkpoints"]
    if [cp["task"] for cp in checkpoints] != [task["id"] for task in brief["tasks"]]:
        return "blocked"
    for task, cp in zip(brief["tasks"], checkpoints):
        if (cp["baseline"] != task["baseline"] or not cp.get("result")
                or not cp.get("diff_inspected")
                or not cp.get("focused_scope")):
            return "blocked"
    return "accepted"


def audited_sample(selected="symbolic/luna:medium"):
    brief, returned = sample_batch_contract(selected)
    returned["observed_profile"] = selected  # simulated reported observation, not request inference
    returned["gates"] = {item["ref"]: {"manual": True, "permission": True}
                         for item in brief["required_union"]}
    for cp in returned["checkpoints"]:
        cp.update(diff_inspected=True, focused_scope=True)
    return brief, returned


class SimulatedAcceptanceTests(CarrierTests):
    """Offline Luna success and negative evidence cases; no live performance claim."""

    def test_cheap_acceptance_instruction_carriers(self):
        self.assert_carrier_guards('Execute and Integrate', ('actual diff', 'focused commit/SHA', 'REQUIRED outputs', 'residual owned changes', 'Only satisfied REQUIRED items', 'fulfilled original gates', 'generic green is not proof'))

    def assert_complete_accepted(self, selected):
        brief, returned = audited_sample(selected)
        self.assertEqual(simulated_audit(brief, returned), "accepted")
        required = {item["ref"] for item in brief["required_union"]}
        passed = {ref for ref, result in returned["items"].items() if result["status"] == "pass"}
        self.assertEqual(passed, required)  # 100% REQUIRED evidence
        self.assertEqual(brief["selected"], selected)
        self.assertEqual(returned["observed_profile"], selected)
        self.assertTrue(all(cp["diff_inspected"] for cp in returned["checkpoints"]))
        self.assertEqual(len(returned["checkpoints"]), 2)
        self.assertNotIn("reviewer", returned)  # accepted without a strong per-batch reviewer

    def test_simulated_luna_medium_accepted_without_strong_reviewer(self):
        self.assert_complete_accepted("symbolic/luna:medium")

    def test_simulated_luna_max_accepted_preserves_max(self):
        self.assert_complete_accepted("symbolic/luna:max")

    def test_invalid_required_evidence_blocks_dependent_release(self):
        for case in ("removed item", "removed output", "failed", "contradictory", "unrun",
                     "unauthorized scope", "manual gate", "permission gate",
                     "missing checkpoint", "uninspected diff", "unfocused checkpoint"):
            with self.subTest(case=case):
                brief, returned = audited_sample()
                if case == "removed item":
                    del returned["items"]["T006/V1"]
                elif case == "removed output":
                    returned["outputs"].clear()
                elif case == "failed":
                    returned["items"]["T006/V1"]["status"] = "fail"
                elif case == "contradictory":
                    returned["outputs"]["shared-output"]["exit"] = 1  # pass report contradicted
                elif case == "unrun":
                    returned["items"]["T006/V1"].update(status="not_verified", evidence=None,
                                                        reason="check not run")
                elif case == "unauthorized scope":
                    returned["files"].append("outside/owned-scope.md")
                elif case in ("manual gate", "permission gate"):
                    returned["gates"]["T006/V1"][case.split()[0]] = False
                elif case == "missing checkpoint":
                    returned["checkpoints"].pop()
                elif case == "uninspected diff":
                    returned["checkpoints"][1]["diff_inspected"] = False
                else:
                    returned["checkpoints"][1]["focused_scope"] = False
                disposition = simulated_audit(brief, returned)
                self.assertEqual(disposition, "blocked")
                release_dependents = disposition == "accepted"
                self.assertFalse(release_dependents)



def failed_capability_sample():
    brief, returned = audited_sample("symbolic/luna:max")
    brief["assessment"] = {"reasoning": "bounded compatibility inference", "tools": "local",
                           "oracle": "explicit invariant", "scope": "two coupled tasks",
                           "recovery": "cheap", "guidance": "none"}
    returned["items"]["T006/V1"].update(status="fail", evidence="consumer-failed")
    returned["outputs"]["consumer-failed"] = {
        "command": "fixture shared-check", "exit": 1, "revision": "fixture-task-006",
        "environment": "offline-python", "observations": {"consumer_ids": ["V1"]}}
    return brief, returned


def simulated_repair_brief(brief, failed, diagnosis, *, inspected=True,
                           binding=True, effort=True, owner=True, permission=True, tools=True):
    """Offline diagnosed repair artifact; never launches an agent or restores Git state."""
    if diagnosis != "model_capability" or not all((inspected, binding, effort, owner, permission, tools)):
        return None
    return {"original_assessment": deepcopy(brief["assessment"]),
            "original_selected": brief["selected"], "original_observed": failed["observed_profile"],
            "selected": "symbolic/sol:medium", "diagnosis": diagnosis,
            "diagnostic_evidence": "consumer-failed: explicit compatibility invariant",
            "passed": ["T005/V1"], "failed": ["T006/V1"],
            "affected_dependencies": ["T006 consumer and external dependents"],
            "invalidated": ["T006/V1"], "reusable": ["T005/V1"],
            "current_sha": failed["revision"], "exact_gaps": {"T006/V1": "consumer drops V2"},
            "inspected_run": "fixture-run", "inspected_invocation": "fixture-invocation",
            "operation": "implementation continuation under same original contracts",
            "prior_proof": deepcopy(failed["outputs"]),
            "current_state": deepcopy(failed), "complete_contract": deepcopy(brief)}


class SimulatedRepairTests(CarrierTests):
    """Offline failure/repair scenarios, not comparative model performance evidence."""

    def test_diagnosis_first_repair_instruction_carriers(self):
        self.assert_carrier_guards('Execute and Integrate', ('inspect run/invocation, partial commits and check evidence', 'affected dependencies/invalidated items', 'same original contracts', 'reruns invalidated items only', 'Unknown cause blocks blind restart', 'never automatic rollback or discard'))

    def test_luna_max_capability_failure_authorized_sol_medium_repair(self):
        brief, failed = failed_capability_sample()
        original = deepcopy(failed)
        self.assertEqual(simulated_audit(brief, failed), "blocked")
        repair = simulated_repair_brief(brief, failed, "model_capability")
        self.assertEqual(repair["original_selected"], "symbolic/luna:max")
        self.assertEqual(repair["original_observed"], "symbolic/luna:max")
        self.assertEqual(repair["original_assessment"], brief["assessment"])
        self.assertEqual(repair["complete_contract"], brief)
        self.assertTrue(repair["diagnostic_evidence"])
        self.assertTrue(repair["affected_dependencies"])
        self.assertEqual(repair["selected"], "symbolic/sol:medium")
        repaired = deepcopy(failed)
        repaired["observed_profile"] = repair["selected"]  # simulated observation
        # Invalidated item cannot pass by reusing failed evidence.
        repaired["items"]["T006/V1"]["status"] = "pass"
        self.assertEqual(simulated_audit(brief, repaired), "blocked")
        repaired["outputs"]["repair-output"] = {
            "command": "fixture shared-check", "exit": 0, "revision": "fixture-repair-006",
            "environment": "offline-python", "observations": {"consumer_ids": ["V1", "V2"]}}
        repaired["revision"] = "fixture-repair-006"
        repaired["item_revisions"]["T006/V1"] = "fixture-repair-006"
        repaired["items"]["T006/V1"]["evidence"] = "repair-output"
        repaired["outputs"]["repair-output"]["revision"] = "fixture-task-006"
        self.assertEqual(simulated_audit(brief, repaired), "blocked")  # unchanged stale proof cannot release
        repaired["outputs"]["repair-output"]["revision"] = repaired["revision"]
        repaired["checkpoints"][1].update(result="fixture-repair-006",
                                            evidence_checkpoint="fixture-repair-evidence-006")
        self.assertEqual(repair["invalidated"], ["T006/V1"])
        self.assertEqual(simulated_audit(brief, repaired), "accepted")
        self.assertEqual(repaired["items"]["T005/V1"], original["items"]["T005/V1"])
        self.assertEqual(repaired["checkpoints"][0], original["checkpoints"][0])
        self.assertEqual(failed, original)  # original attempt and valid work retained

    def test_unknown_unavailable_or_unauthorized_repair_stops(self):
        brief, failed = failed_capability_sample()
        self.assertIsNone(simulated_repair_brief(brief, failed, "unknown"))
        for gate in ("inspected", "binding", "effort", "owner", "permission", "tools"):
            with self.subTest(gate=gate):
                self.assertIsNone(simulated_repair_brief(brief, failed, "model_capability", **{gate: False}))
        self.assertIn("Unknown cause blocks blind restart", " ".join(TEXT.split()))



COORDINATION_PATH = Path(__file__).parents[2] / "memory-handling" / "references" / "project-coordination.md"


def simulated_feedback(selected, observed, outcome, diagnosis, *, strong=True, invalidated=False):
    """Qualified offline attempt record, not a learner or guideline writer."""
    return {"selected": selected, "observed": observed, "first_outcome": outcome,
            "final_outcome": outcome, "diagnosis": diagnosis,
            "contract_strength": "strong" if strong else "weak",
            "batch": "B01", "task_items": {"T006/V1": {"disposition": "satisfied" if outcome == "accepted" else "insufficient-evidence",
                                                          "proof": "fixture-output"}},
            "escalation_reason": "consumer drops V2" if diagnosis == "model_capability" else "no capability escalation; " + diagnosis,
            "next_selected": "symbolic/sol:medium" if diagnosis == "model_capability" else "pending selection",
            "capability_penalty": outcome == "blocked" and diagnosis == "model_capability",
            "qualified_positive": outcome == "accepted" and strong and not invalidated}


class SimulatedFeedbackTests(CarrierTests):
    def test_factual_first_final_attempts_and_unknown_preserved(self):
        first = simulated_feedback("symbolic/luna:max", "unknown", "blocked", "model_capability")
        first["task_items"]["T006/V1"] = {"disposition": "failed", "proof": "consumer-failed"}
        original = deepcopy(first)
        final = simulated_feedback("symbolic/sol:medium", "unknown", "accepted", "model_capability")
        record = {"task_return": "runtime return", "attempts": [first, final],
                  "reused": ["T005/V1"], "invalidated_rerun": ["T006/V1"]}
        self.assertNotIn("summary", record)
        self.assertEqual(first, original)
        self.assertEqual([a["observed"] for a in record["attempts"]], ["unknown", "unknown"])
        self.assertEqual(first["task_items"]["T006/V1"]["proof"], "consumer-failed")
        self.assertEqual(final["task_items"]["T006/V1"]["disposition"], "satisfied")
        self.assertEqual(first["escalation_reason"], "consumer drops V2")
        self.assertEqual(first["next_selected"], final["selected"])

    def test_feedback_instruction_carriers(self):
        self.assert_carrier_guards('Review and Acceptance', ('selected versus observed profile', 'unknown stays unknown', 'Explicit future-directed user feedback alone'))

    def test_environment_blocked_luna_medium_without_capability_penalty(self):
        brief, returned = audited_sample()
        returned["observed_profile"] = "unknown"
        returned["items"]["T006/V1"].update(status="not_verified", evidence=None,
                                              reason="required local tool unavailable; not run")
        outcome = simulated_audit(brief, returned)
        self.assertEqual(outcome, "blocked")
        feedback = simulated_feedback(brief["selected"], returned["observed_profile"],
                                      outcome, "environment_or_tooling")
        self.assertEqual(feedback["selected"], "symbolic/luna:medium")
        self.assertEqual(feedback["observed"], "unknown")
        self.assertEqual(feedback["diagnosis"], "environment_or_tooling")
        self.assertFalse(feedback["capability_penalty"])
        self.assertFalse(feedback["qualified_positive"])
        self.assertTrue(returned["items"]["T006/V1"]["reason"])
        for cause in ("planning_or_spec_gap", "verification_contract_gap", "batching_error",
                      "environment_or_tooling", "external_dependency", "unknown"):
            self.assertFalse(simulated_feedback(brief["selected"], "unknown", "blocked", cause)["capability_penalty"])
        for strong, invalidated in ((False, False), (True, True)):
            self.assertFalse(simulated_feedback(brief["selected"], "unknown", "accepted", "unknown",
                                               strong=strong, invalidated=invalidated)["qualified_positive"])

    def test_approved_applicable_guideline_sol_medium_overrides_seed_luna_max(self):
        seed = "symbolic/luna:max"
        guideline = {"ref": "fixture/GUIDELINES.md#compatibility", "approved": True,
                     "applicable": True, "evidence": "fixture/repeated-compatibility-failures",
                     "profile": "symbolic/sol:medium"}
        def select(guidance, *, owner=True, source=True):
            proposal = guidance["profile"] if guidance["approved"] and guidance["applicable"] else seed
            dispatch = SimulatedProfileTraceTests.simulated_dispatch(proposal, owner=owner and source)
            return proposal, dispatch
        proposal, dispatch = select(guideline)
        self.assertEqual(proposal, "symbolic/sol:medium")
        self.assertEqual(dispatch["args"]["model"], proposal)
        self.assertTrue(guideline["ref"] and guideline["evidence"])
        for gate in ("owner", "source"):
            self.assertEqual(select(guideline, **{gate: False})[1]["disposition"], "blocked")
        for field in ("approved", "applicable"):
            unqualified = dict(guideline, **{field: False})
            self.assertEqual(select(unqualified)[0], seed)
        self.assertEqual(guideline["profile"], "symbolic/sol:medium")  # no mutation

    def test_memory_lifecycle_approval_and_drift_preserved(self):
        memory = " ".join(COORDINATION_PATH.read_text().split())
        for clause in ("Missing store or STATE is nonblocking", "do not auto-initialize",
                       "explicit user corrective/future-round direction", "Concurrent drift",
                       "never history/index/run scaffolding", "An explicit no-write boundary prevails"):
            self.assertIn(clause, memory)


class PracticalVerificationTests(CarrierTests):
    """Named offline examples; no runtime obedience, paid operation or real user gate."""

    def test_oracle_sensitive_routing_cases(self):
        rubric = RUBRIC_PATH.read_text()
        for case, adequate, coupling, oracle, expected in (
            ("moderate_complexity_strong_cheap_oracle", True, "bounded", "strong cheap", "symbolic/luna:max"),
            ("weak_oracle_hidden_coupling", True, "hidden", "weak", "symbolic/sol:medium"),
            ("inadequate_contract_producing_gate", False, "hidden", "missing", None),
        ):
            with self.subTest(case=case):
                # Explicit contrasting proposals, not a production selection algorithm.
                proposal = None if not adequate else "symbolic/sol:medium" if coupling == "hidden" else "symbolic/luna:max"
                family = "closed design, moderate difficulty, strong cheap oracle" if oracle == "strong cheap" else "hidden coupling and weakest oracle"
                effort = "bounded extra inference" if adequate else "producing review/renewal required"
                self.assertEqual(proposal, expected)
                self.assertTrue(family and effort)
                self.assertNotEqual(family, effort)
                self.assertIn("strong cheap reliable oracles", rubric)
                self.assertIn("inadequate contracts", rubric)

    def test_shared_check_two_distinct_items(self):
        brief, returned = audited_sample()
        actual = item_dispositions(brief, returned)
        self.assertEqual([i["disposition"] for i in actual.values()], ["satisfied", "satisfied"])
        self.assertEqual(len(returned["outputs"]), 1)
        self.assertNotEqual(brief["required_union"][0]["observable_key"], brief["required_union"][1]["observable_key"])
        self.assertEqual(returned["outputs"]["shared-output"]["observations"]["consumer_ids"], ["V1", "V2"])
        self.assertEqual(simulated_audit(brief, returned), "accepted")

    def test_task_specific_evidence_dispositions(self):
        cases = ("removed_mapping", "green_but_irrelevant", "stale_revision", "wrong_environment",
                 "missing_output", "conflicting_proof", "unrun_required", "confidence_only",
                 "demonstrated_criterion_violation", "defect_with_evidence_limitation")
        for case in cases:
            with self.subTest(case=case):
                brief, returned = audited_sample()
                result = returned["items"]["T006/V1"]
                output = returned["outputs"]["shared-output"]
                if case == "removed_mapping":
                    del returned["items"]["T006/V1"]
                elif case == "green_but_irrelevant":
                    output["observations"] = {"broad_suite": "green"}
                elif case == "stale_revision":
                    output["revision"] = "old-sha"
                elif case == "wrong_environment":
                    output["environment"] = "other-platform"
                elif case == "missing_output":
                    returned["outputs"].clear()
                elif case == "conflicting_proof":
                    output["exit"] = 1  # no demonstrated criterion violation
                elif case == "unrun_required":
                    result.update(status="not_verified", reason="tool unavailable; not run", evidence=None)
                elif case == "confidence_only":
                    result.clear()
                    result["confidence"] = "high"
                else:
                    output["observations"]["consumer_ids"] = ["V1"]  # concrete dropped ID
                    if case == "defect_with_evidence_limitation":
                        result.update(status="not_verified", reason="separate report incomplete")
                returned["optional"] = {"broad-suite": "green"}
                actual = item_dispositions(brief, returned)["T006/V1"]
                expected = "failed" if case.startswith("demonstrated") or case.startswith("defect_") else "insufficient-evidence"
                self.assertEqual(actual["disposition"], expected)
                self.assertTrue(actual["reason"])
                self.assertEqual(simulated_audit(brief, returned), "blocked")
                if expected == "failed":
                    self.assertEqual(output["observations"]["consumer_ids"], ["V1"])
                if case == "defect_with_evidence_limitation":
                    self.assertIn("separate report incomplete", actual["limitations"])

    def test_producer_pending_blocks_consumer_release(self):
        brief, returned = audited_sample()
        returned["items"]["T005/V1"].update(status="not_verified", reason="producer pending")
        self.assertEqual(simulated_audit(brief, returned), "blocked")
        returned["items"]["T005/V1"].update(status="pass", reason=None)
        self.assertEqual(simulated_audit(brief, returned), "accepted")

    def test_representative_sample_stop_and_ordinary_path(self):
        for case, sample, decision, scope, allowed in (
            ("pending", "sample-1", "pending", "approved-scope", False),
            ("rejected", "sample-1", "reject", "approved-scope", False),
            ("absent_sample", None, "approve", "approved-scope", False),
            ("llm_self_review", "sample-1", "LLM-pass", "approved-scope", False),
            ("approved_sample", "sample-1", "approve", "approved-scope", True),
            ("outside_sample_scope", "sample-1", "approve", "full-unapproved", False),
        ):
            with self.subTest(case=case):
                brief, returned = audited_sample()
                gate = {"sample": sample, "user_decision": decision, "operation": scope,
                        "blocked_operation": "downstream/full expensive operation"}
                returned["gates"]["T006/V1"]["manual"] = bool(sample) and decision == "approve" and scope == "approved-scope"
                self.assertEqual(simulated_audit(brief, returned) == "accepted", allowed)
                self.assertEqual(gate["sample"], sample)
        # Original ordinary contract has no representative-sample gate.
        brief, returned = audited_sample()
        self.assertEqual(simulated_audit(brief, returned), "accepted")
        self.assertNotIn("sample", returned)

    def test_unjustified_clean_retry_and_exceptional_safe_clean_retry(self):
        def permitted(reason, ownership, mechanics, owner, project_gate):
            return bool(reason) and all((ownership, mechanics, owner, project_gate))
        for case, reason, ownership, mechanics, owner, project_gate, expected in (
            ("unjustified_clean_retry", None, True, True, True, True, False),
            ("exceptional_safe_clean_retry", "documented contaminated task output", True, True, True, True, True),
            ("unsafe_mechanics", "fundamental unsoundness", True, False, True, True, False),
            ("unknown_ownership", "contamination", False, True, True, True, False),
            ("missing_owner_gate", "project rule", True, True, False, True, False),
            ("missing_project_gate", "project rule", True, True, True, False, False),
        ):
            with self.subTest(case=case):
                self.assertEqual(permitted(reason, ownership, mechanics, owner, project_gate), expected)
        # Symbolic only: no reset/discard or repository operation is executed.
        brief, failed = failed_capability_sample()
        for diagnosis in ("unknown", "environment_or_tooling", "manual", "permission", "verification_contract_gap", "planning_or_spec_gap"):
            self.assertIsNone(simulated_repair_brief(brief, failed, diagnosis))
        repair = simulated_repair_brief(brief, failed, "model_capability")
        self.assertEqual(repair["current_sha"], failed["revision"])
        self.assertEqual(repair["exact_gaps"], {"T006/V1": "consumer drops V2"})
        self.assertEqual(repair["complete_contract"], brief)
        self.assertEqual(repair["prior_proof"], failed["outputs"])
        self.assertIn("implementation continuation", repair["operation"])


class VerificationGapTests(CarrierTests):
    def test_practical_distinct_criteria_before_generic_green(self):
        brief, _ = sample_batch_contract()
        criteria = [i["criterion"] for i in brief["required_union"]]
        self.assertEqual(criteria, ["producer exports stable item IDs", "consumer preserves every producer ID"])

    def test_explicit_item_dispositions_and_revision_proof(self):
        brief, returned = audited_sample()
        self.assertIn("revision", returned["outputs"]["shared-output"])
        self.assertIn("insufficient-evidence", TEXT)

    def test_exceptional_retry_is_not_automatic_discard(self):
        self.assertIn("Clean retry is exceptional", TEXT)


class ComparativeRoutingTests(CarrierTests):
    """Named manual recommendations and counterexamples, not a family-ranking engine."""
    def test_comparison_carrier_and_mutations(self):
        rubric = " ".join(RUBRIC_PATH.read_text().split())
        for heading, clauses in (
            ("Provisional family and effort choices", (
                "rubric first, capability verification second",
                "suitable options even with zero previous launches",
                "actual shortfall or select the adequate candidate without an unsupported premium",
                "pending readiness is not inadequacy", "orchestration overhead",
                "stateful tooling/recovery", "strict requirement versus a default preference")),
            ("Readiness before dispatch", (
                "authenticated availability for the exact provider/id",
                "authoritative runtime-supported choices include the exact selected effort",
                "current exact launch contract", "model scope/thinking ceiling",
                "tool/extension access", "mutation permissions", "execution environment",
                "exact owner selection", "missing/stale/opaque evidence",
                "detached-child environment", "clamping or omitted/different effort",
                "Reuse still-applicable proof", "final preflight before provider invocation",
                "no previous launch is required", "not a universal fresh audit",
                "bounded authorization or an explicit fallback choice",
                "retain the recommendation", "never silently substitute Sol")),
        ):
            body = carrier(RUBRIC_PATH.read_text(), heading)
            for clause in clauses:
                with self.subTest(carrier=heading, guard=clause):
                    self.assertIn(clause, body, heading + ': missing ' + clause)
                    mutant = body.replace(clause, 'REMOVED')
                    self.assertNotIn(clause, carrier(mutant + ' ## Footer ' + clause, heading))
        self.assertNotIn('suitable smaller verified, permitted alternative', rubric)
        self.assertNotIn('none is verified/permitted', rubric)
        for old in ('suitable smaller verified, permitted alternative',
                    'only previously launched alternatives are eligible'):
            mutant = rubric.replace('suitable options even with zero previous launches', old)
            self.assertNotIn('suitable options even with zero previous launches', mutant)
        self.assert_carrier_guards("Prepare Approved Execution", ("separate comparative Family and Effort rationales",))

    def test_named_comparative_recommendations_and_suitability_only_rejected(self):
        # Inputs and reasoned outputs are explicitly authored, not computed from a score.
        cases = (
            ("closed_design_strong_cheap_oracle", "closed design; bounded tools; strong cheap oracle; bounded coupling; cheap rollback; no approved guidance (uncertain); zero previous launches; pending readiness",
             "symbolic/luna:low", "Luna meets the closed contract; no Sol shortfall claim", "low: tightly bounded inference"),
            ("hidden_coupling_costly_recovery", "recovery inference; stateful tools; weakest adequate weak oracle; hidden coupling; costly rollback; no approved guidance (uncertain)",
             "symbolic/sol:medium", "Luna shortfall: hidden coupling and long recovery escape cheap checks", "medium: recovery reasoning"),
            ("alternative_unavailable", "closed design; catalog-only Luna; readiness pending, no launch history",
             "symbolic/luna:low", "Luna meets the closed contract; readiness does not change sufficiency", "low: closed inference"),
            ("strict_medium", "owner policy requires medium; closed contract",
             "symbolic/luna:medium", "Luna meets closed contract", "medium: strict requirement, low not permitted"),
            ("default_medium_allows_low", "medium preference permits low; closed contract",
             "symbolic/luna:low", "Luna meets closed contract", "low: bounded inference beats default preference"),
            ("unsupported_effort", "selected Luna/low unsupported", None,
             "stop: effort support gate, not family inadequacy", "unsupported low blocks"),
            ("inadequate_contract", "missing consumer invariant despite available Sol", None,
             "stop: producing review/renewal, no model repairs criteria", "no effort can fix missing criteria"),
            ("unresolved_design", "owner architecture decision remains open", None,
             "stop: producing review/owner clarification", "no effort can settle owner direction"),
        )
        # Independent expectations for these finite authored inputs, not routing rules.
        expected = {
            "closed_design_strong_cheap_oracle": ("symbolic/luna:low", "closed contract", "low:"),
            "hidden_coupling_costly_recovery": ("symbolic/sol:medium", "Luna shortfall: hidden coupling", "medium:"),
            "alternative_unavailable": ("symbolic/luna:low", "readiness does not change sufficiency", "low:"),
            "strict_medium": ("symbolic/luna:medium", "closed contract", "medium:"),
            "default_medium_allows_low": ("symbolic/luna:low", "closed contract", "low:"),
            "unsupported_effort": (None, "stop: effort support gate", "unsupported low blocks"),
            "inadequate_contract": (None, "stop: producing review/renewal", "no effort can fix missing criteria"),
            "unresolved_design": (None, "stop: producing review/owner clarification", "no effort can settle owner direction"),
        }
        for name, inputs, proposal, family, effort in cases:
            with self.subTest(case=name):
                expected_profile, family_reason, effort_reason = expected[name]
                self.assertTrue(inputs and family and effort)
                if name == 'closed_design_strong_cheap_oracle':
                    for factor in ('closed design', 'bounded tools', 'strong cheap oracle',
                                   'bounded coupling', 'cheap rollback', 'no approved guidance (uncertain)',
                                   'zero previous launches', 'pending readiness'):
                        self.assertIn(factor, inputs, name + ': missing factor/state ' + factor)
                if name == 'hidden_coupling_costly_recovery':
                    for factor in ('recovery inference', 'stateful tools', 'weakest adequate weak oracle',
                                   'hidden coupling', 'costly rollback', 'no approved guidance (uncertain)'):
                        self.assertIn(factor, inputs, name + ': missing factor ' + factor)
                self.assertNotEqual(family, effort)
                self.assertEqual(proposal, expected_profile, name + ": recommendation violates case constraints")
                self.assertIn(family_reason, family, name + ": missing case-specific family reasoning")
                self.assertTrue(effort.startswith(effort_reason), name + ": effort reasoning violates case constraints")
        old_fallback = dict(case='alternative_unavailable', proposal='symbolic/sol:low')
        self.assertNotEqual(old_fallback['proposal'], expected[old_fallback['case']][0],
                            'automatic unavailable-to-Sol fallback must fail')
        invalid_medium = {"case": "strict_medium", "proposal": "symbolic/luna:low",
                          "effort": "medium: strict requirement, low not permitted"}
        self.assertFalse(invalid_medium["proposal"] == expected[invalid_medium["case"]][0],
                         "mandatory medium cannot permit low despite a medium rationale")
        # Small artifact oracle: suitability alone is insufficient when an alternative exists.
        rationale = {"proposal": "symbolic/sol:medium", "alternative": "symbolic/luna:low",
                     "family": "hidden coupling defeats the cheap oracle", "effort": "medium for recovery",
                     "comparison": "Luna shortfall: stateful recovery outside checks"}
        def complete(record):
            # This recovery sample must explain its named alternative's concrete shortfall.
            return bool(record["family"] and record["effort"] and
                        (not record["alternative"] or
                         record["comparison"] == "Luna shortfall: stateful recovery outside checks"))
        self.assertTrue(complete(rationale), "recovery comparison must explain the named alternative's shortfall")
        self.assertFalse(complete(dict(rationale, family="Sol is suitable", comparison="")))
        self.assertFalse(complete(dict(rationale, comparison="Sol is suitable")),
                         "suitability alone does not explain the suitable alternative")
        override = dict(rationale, selected="symbolic/luna:medium", observed="unknown")
        self.assertEqual(override["proposal"], "symbolic/sol:medium")
        self.assertEqual(SimulatedProfileTraceTests.simulated_dispatch(override["selected"])["args"]["model"], override["selected"])
        self.assertEqual(override["observed"], "unknown")
        stage = {"Standard plan_create": "symbolic/sol:medium", "implementation": cases[0][2]}
        self.assertNotEqual(stage["Standard plan_create"], stage["implementation"])
        self.assertIn("This exception does not assign implementation-task profiles", (Path(__file__).parents[2] / "planner/SKILL.md").read_text())

    def test_pending_gap_and_ready_without_history(self):
        # Finite symbolic preparations; these booleans do not discover runtime evidence.
        proof = dict(binding=True, authenticated=True, effort=True, contract=True,
                     scope_ceiling=True, tools=True, permissions=True, environment=True,
                     owner=True)
        ready = dict(proposal='symbolic/luna:low', readiness=proof, selected='symbolic/luna:low',
                     historical_launch=None, observed='unknown', outcome='dispatch preparation')
        self.assertTrue(all(ready['readiness'].values()))
        self.assertIsNone(ready['historical_launch'])
        captured = SimulatedProfileTraceTests.simulated_dispatch(ready['selected'])
        self.assertEqual(captured['args']['model'], ready['selected'])
        self.assertEqual(ready['observed'], 'unknown')
        for gap in proof:
            with self.subTest(case='missing_' + gap):
                pending = dict(ready, readiness=dict(proof, **{gap: False}), outcome='blocked')
                self.assertFalse(all(pending['readiness'].values()), 'missing_' + gap + ': dispatch blocked')
                self.assertEqual(pending['proposal'], 'symbolic/luna:low')
        catalog = dict(ready, readiness=dict.fromkeys(proof, False), selected=None,
                       outcome='blocked: bounded authorization or explicit fallback choice')
        self.assertEqual([k for k, v in catalog['readiness'].items() if not v], list(proof))
        self.assertEqual(catalog['proposal'], 'symbolic/luna:low')
        self.assertIsNone(catalog['selected'])
        for name, gap in (
            ('credential_presence_only', 'authenticated'), ('thinking_flag_only', 'effort'),
            ('suffix_only', 'effort'), ('permissive_missing_metadata', 'effort'),
            ('stale_availability', 'authenticated'), ('opaque_availability', 'authenticated'),
            ('detached_environment_mismatch', 'environment'), ('unsupported_effort', 'effort'),
            ('clamped_effort', 'effort'), ('omitted_effort', 'effort'), ('different_effort', 'effort'),
            ('tool_denied', 'tools'), ('permission_denied', 'permissions'),
            ('missing_owner_selection', 'owner'), ('settings_default_mismatch', 'contract'),
        ):
            with self.subTest(case=name):
                negative = dict(proof, **{gap: False})
                self.assertFalse(all(negative.values()), name + ': exact dispatch must stop')

    def test_batch_tradeoff_examples(self):
        expected = {"docs_plus_final_recovery": "split consecutive tasks",
                    "coherent_same_profile": "combine sequentially"}
        for name, saving, opportunity, decision in (
            ("docs_plus_final_recovery", "one intake saved", "docs can use verified smaller profile; recovery needs deeper tooling", "split consecutive tasks"),
            ("coherent_same_profile", "shared interface context and startup saved", "none: both need same recovery capability", "combine sequentially"),
        ):
            with self.subTest(case=name):
                self.assertTrue(saving and opportunity)
                self.assertEqual(decision, expected[name], name + ": decision contradicts this trade-off")
        swapped = {"docs_plus_final_recovery": "combine sequentially",
                   "coherent_same_profile": "split consecutive tasks"}
        for name, decision in swapped.items():
            self.assertNotEqual(decision, expected[name], name + ": swapped decision must be rejected")
        self.assertIn("shared files, phase headings and internal dependencies alone do not require splits", " ".join(TEXT.split()))
        self.assertIn("Commit each task's verified changes as one focused owned-path commit", TEXT)


class FirstProposalRoutingTests(CarrierTests):
    """Authored static sensitivity cases, never evidence of model reasoning."""

    RECIPE_GUARDS = (
        "actual invocation demands and verification boundaries",
        "Before comparing candidates, inspect only the retained evidence materially needed",
        "or state explicit non-reliance/absence",
        "remaining work/weakest adequate oracle",
        "one plausible adequate alternative",
        "specific selection difference, or `no established difference`",
        "provisional choice or exact owner preference",
        "sufficient capability without an unsupported premium",
        "there is **no established difference** between them for this invocation",
        "not a model deficit",
        "no additional remaining inference over low is established",
        "This example does not rely on retained benchmark evidence",
    )

    def test_preproposal_completeness_check(self):
        body = carrier(RUBRIC_PATH.read_text(), "First proposal recipe")
        for clause in (
            "Before presenting the proposal, check completeness",
            "all six factors and the weakest adequate oracle",
            "each family in this rubric is considered or briefly accounted for",
            "family and effort have separate comparative rationales",
            "prior launch success is used only as readiness evidence",
            "ties remain explicit rather than becoming superiority claims",
            "Repair missing items before asking for profile approval",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, body)

    def test_recipe_carrier_and_evidence_sequence_mutations(self):
        rubric = RUBRIC_PATH.read_text()
        body = carrier(rubric, "First proposal recipe")
        for clause in self.RECIPE_GUARDS:
            with self.subTest(clause=clause):
                self.assertIn(clause, body)
                altered = " ".join(rubric.split()).replace(clause, "REMOVED", 1)
                self.assertNotIn(clause, carrier(altered + " ## Footer " + clause, "First proposal recipe"))
        evidence = carrier(rubric, "Evidence limits")
        for clause in ("*after* demands/oracles and *before* the comparison/proposal",
                       "exact family/version/effort", "harness and task relevance",
                       "retained provenance, and limits", "causal effort gains"):
            self.assertIn(clause, evidence)

    @staticmethod
    def settled_input():
        """Reported seven-task illustration, kept as finite static test input only."""
        tasks = {
            "T000": "constitution cleanup and propagation",
            "T001": "capture/tolerant reader with permanent filesystem/read-count tests",
            "T002": "both journal modes, containment, accounting and publication",
            "T003": "metadata-only status and evidence-preserving cleanup",
            "T004": "maintained progress and endpoint-wrapper paths",
            "T005": "canonical documentation against verified behavior",
            "T006": "composed checks and fresh independent review",
        }
        # The source reports only counts; these are deliberately not historical criterion/item IDs.
        return {"tasks": tasks, "criteria": tuple(f"symbolic source criterion {i}" for i in range(1, 10)),
                "required": tuple(f"symbolic REQUIRED item {i}" for i in range(1, 15)),
                "risks": ("reader-opening scans", "async native-task settlement",
                          "cross-mode publication", "failure-preserving cleanup")}

    @staticmethod
    def assert_complete_proposal(test, proposal, expected_rows, settled, producing_gate=None):
        """Finite authored-fixture assertions, not a routing engine or model-quality oracle."""
        rows = proposal["rows"]
        test.assertEqual([row["task"] for row in rows], list(settled["tasks"]))
        # Profile spelling is carried for an invocation record, never used as reasoning proof.
        without_profile = lambda items: [{key: value for key, value in row.items() if key != "proposed"} for row in items]
        test.assertEqual(without_profile(rows), without_profile(expected_rows))
        for row in rows:
            test.assertTrue(all(row[key] for key in ("demand", "oracle", "alternative", "comparison",
                                                      "family", "effort", "evidence", "proposed")))
            test.assertEqual(row["observed"], "unknown")
        test.assertFalse(proposal["dispatch"])
        test.assertIsNone(proposal.get("fallback"))
        if producing_gate is not None:
            test.assertEqual(proposal.get("producing_gate"), producing_gate)
            test.assertIsNone(proposal.get("escalation"))

    def test_seven_reason_sensitive_first_proposal_cases(self):
        settled = self.settled_input()
        self.assertEqual((len(settled["tasks"]), len(settled["criteria"]), len(settled["required"])), (7, 9, 14))
        self.assertTrue(all("symbolic" in item for item in settled["criteria"] + settled["required"]))
        tie_rows = [
            {"task": task, "demand": demand, "oracle": oracle, "alternative": "Sol/low",
             "comparison": "no established difference", "family": "honest tie; no family superiority claim",
             "effort": "no extra remaining inference over low; empirical benefit unestablished",
             "evidence": "explicit non-reliance", "proposed": "Luna/medium", "observed": "unknown"}
            for task, demand, oracle in (
                ("T000", "constitution cleanup", "propagation check"),
                ("T001", "capture/tolerant reader", "filesystem/read-count test"),
                ("T002", "journal containment/accounting/publication", "both-mode focused check"),
                ("T003", "metadata-only cleanup", "failure-custody check"),
                ("T004", "progress/endpoint wrapper", "existing wrapper check"),
                ("T005", "canonical documentation", "verified-behavior check"),
                ("T006", "composed verification/review", "composed final oracle"))]
        coupling_rows = [dict(row) for row in tie_rows]
        for task, risk in (("T001", "reader-opening scans"), ("T002", "async native-task settlement and cross-mode publication"),
                           ("T003", "failure-preserving cleanup")):
            row = next(item for item in coupling_rows if item["task"] == task)
            row.update(alternative="Luna/medium", proposed="Sol/medium",
                       comparison="provisional uncalibrated judgment: Sol may help inspect " + risk + "; not Luna incapacity",
                       family="tentative coupling judgment with no task-specific probability",
                       effort="remaining inference over low: reconcile " + risk + "; empirical benefit unestablished",
                       evidence="synthetic fixture; retained evidence non-reliance")
        tie = {"rows": tie_rows, "dispatch": False, "readiness": "pending", "selected": None}
        coupling = {"rows": coupling_rows, "dispatch": False, "readiness": "pending", "selected": None}
        self.assert_complete_proposal(self, tie, tie_rows, settled)
        self.assert_complete_proposal(self, coupling, coupling_rows, settled)
        self.assertNotEqual(tie_rows, coupling_rows)  # multiple justified proposals, not one gold table

        # S1/S4 heading-preserving negatives: all fields remain but exact concrete mapping is lost.
        generic = {**tie, "rows": [dict(row) for row in tie_rows]}
        generic["rows"][2]["family"] = "more margin"
        leaderboard = {**tie, "rows": [dict(row) for row in tie_rows]}
        leaderboard["rows"][2]["comparison"] = "leaderboard result"
        invented_effort = {**coupling, "rows": [dict(row) for row in coupling_rows]}
        invented_effort["rows"][1]["effort"] = "medium is better because Sol is stronger"
        for name, proposal, expected in (("S1_generic", generic, tie_rows), ("S1_leaderboard", leaderboard, tie_rows),
                                         ("S4_invented_effort", invented_effort, coupling_rows)):
            with self.subTest(case=name):
                with self.assertRaises(AssertionError):
                    self.assert_complete_proposal(self, proposal, expected, settled)
        for bad_rows in ([], tie_rows[:2] + tie_rows[3:], [dict(row, task="T006") for row in tie_rows]):
            with self.subTest(case="coverage_or_mapping"):
                with self.assertRaises(AssertionError):
                    self.assert_complete_proposal(self, {**tie, "rows": bad_rows}, tie_rows, settled)

        # S2 preserves no-launch adequacy; S3 exposes all actual risks as tentative, uncalibrated judgment.
        self.assertEqual(tie["readiness"], "pending")
        for risk in settled["risks"]:
            self.assertIn(risk, " ".join(row["comparison"] + row["effort"] for row in coupling_rows))
        self.assertIn("not Luna incapacity", " ".join(row["comparison"] for row in coupling_rows))
        # S5: pending readiness retains a proposal and blocks launch/fallback.
        pending = {**tie, "dispatch": False, "selected": None, "fallback": None}
        self.assert_complete_proposal(self, pending, tie_rows, settled)
        for bad in ({**pending, "dispatch": True}, {**pending, "fallback": "Sol/medium"}):
            with self.subTest(case="S5_launch_or_fallback"):
                with self.assertRaises(AssertionError):
                    self.assert_complete_proposal(self, bad, tie_rows, settled)
        # S6 is the honest owner-preference tie; S7 missing criteria returns to producing review, not escalation.
        self.assertEqual(tie_rows[0]["comparison"], "no established difference")
        producing_gate = "missing publication criterion"
        deficient = {**tie, "dispatch": False, "producing_gate": producing_gate, "escalation": None}
        self.assert_complete_proposal(self, deficient, tie_rows, settled, producing_gate)
        missing_gate = dict(deficient)
        del missing_gate["producing_gate"]
        for bad in ({**deficient, "dispatch": True}, {**deficient, "escalation": "Sol/medium"}, missing_gate):
            with self.subTest(case="S7_launch_escalation_or_deleted_gate"):
                with self.assertRaises(AssertionError):
                    self.assert_complete_proposal(self, bad, tie_rows, settled, producing_gate)


class ExecutionReadinessTests(CarrierTests):
    """Instruction mutations and finite offline cases, not an environment detector."""

    def test_first_check_proof_and_setup_distinctions(self):
        self.assert_carrier_guards('Prepare Approved Execution', (
            'Before tooling-dependent dispatch, establish the smallest applicable executable proof',
            'in the assigned workspace',
            'An authorized bounded setup/readiness assignment may establish it',
            'dependent product implementation waits for sufficient proof',
            'only capabilities exercised or otherwise established',
            'new dependencies need bounded readiness checks',
            'Authorization is not availability; an existing dependency directory is not a usable installation',
            'client binaries do not prove a required server can run',
            'Reusable packages do not establish writable-cache isolation',
            'inspect where the actual loader/tool writes',
            'Read the current guard branch, not historical adjacent restrictions',
            'Reuse readiness proof only while its workspace, tool/dependency versions and write conditions still apply',
            'Already-authorized bounded local setup may proceed without another approval request',
            'Separate unresolved setup from a large implementation assignment when it materially threatens delivery',
        ))

    def test_authorized_but_unusable_and_reusable_but_not_isolated(self):
        # A bounded assignment executes a harmless first check in its own workspace.
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            permission = False
            self.assertFalse(permission)  # no setup invocation before authority
            self.assertFalse((workspace / 'first-check.out').exists())
            permission = True
            result = subprocess.run([sys.executable, '-c',
                "from pathlib import Path; Path('first-check.out').write_text('usable')"],
                cwd=workspace, capture_output=True, text=True)
            proof = dict(check='first-required', exit=result.returncode,
                         workspace=workspace, version=sys.version_info[:3],
                         loader_write=workspace / 'first-check.out', guard='current',
                         exercised={'local-python-write'})
            def gaps(record, assigned=workspace, capability='local-python-write'):
                missing = []
                if not permission:
                    missing.append('permission')
                if record['workspace'] != assigned:
                    missing.append('workspace')
                if record['check'] != 'first-required' or record['exit'] != 0:
                    missing.append('check/outcome')
                if record['version'] != sys.version_info[:3] or record['guard'] != 'current':
                    missing.append('context')
                if record['loader_write'].parent != assigned or not record['loader_write'].is_file():
                    missing.append('actual write location')
                if capability not in record['exercised']:
                    missing.append('capability')
                return missing
            self.assertEqual(gaps(proof), [])
            for task in ('producer', 'consumer'):
                self.assertEqual(gaps(proof), [], task)  # same applicable result, not two runs
            for label, weak, capability in (
                ('authorization/directory-only', dict(proof, check='directory-exists'), 'local-python-write'),
                ('failed first check', dict(proof, exit=1), 'local-python-write'),
                ('client-only', proof, 'server-start'),
                ('cache mismatch', dict(proof, loader_write=workspace.parent / 'cache'), 'local-python-write'),
                ('parent workspace', dict(proof, workspace=workspace.parent), 'local-python-write'),
                ('historical adjacent guard', dict(proof, guard='retired'), 'local-python-write'),
                ('new dependency', proof, 'different-loader'),
            ):
                with self.subTest(distinction=label):
                    self.assertTrue(gaps(weak, capability=capability))
            permission = False
            self.assertIn('permission', gaps(proof))
            print('V1: authorized assigned-workspace check -> shared product release; '
                  'unusable/directory/client/cache/parent/retired/new-dependency controls blocked')

    def test_compact_whole_contract_and_deterministic_batching(self):
        self.assert_carrier_guards('Delegate', (
            'Keep briefs compact and source-bound, not transcript-bound',
            'Source pointers do not replace the whole applicable REQUIRED contract',
            'Batch independent deterministic inspections/checks when safe',
            'preserve dependency order, attributable failures and permission boundaries',
            'Return concise item-mapped results with accessible proof',
            'one canonical contract reference',
            'every REQUIRED disposition and ordered baseline/result SHAs',
        ))

    def test_compact_brief_return_and_safe_check_batch(self):
        brief, returned = audited_sample()
        brief.update(contract='canonical-contract', scope='producer -> consumer',
                     constraints=['local only', 'sequential writers'])
        self.assertEqual(simulated_audit(brief, returned), 'accepted')
        self.assertEqual(len(returned['outputs']), 1)
        # Contract fields must be present before work, not reconstructed from pointers.
        for field in ('criterion', 'check', 'expected', 'expected_evidence',
                      'manual_gate', 'permission_gate'):
            broken = deepcopy(brief)
            del broken['required_union'][0][field]
            self.assertFalse(all(field in item for item in broken['required_union']))
        for mutation in ('missing-item', 'missing-gate', 'missing-access'):
            broken = deepcopy(returned)
            if mutation == 'missing-item':
                del broken['items']['T006/V1']
            elif mutation == 'missing-gate':
                broken['gates']['T006/V1']['permission'] = False
            else:
                broken['outputs'].clear()
            self.assertEqual(simulated_audit(brief, broken), 'blocked')
        # Bounded check scheduling controls, not a general workflow simulator.
        checks = [('read-producer', (), 'read', True),
                  ('read-consumer', (), 'read', True)]
        safe = lambda group: all(not deps and mode == 'read' and allowed
                                 for _, deps, mode, allowed in group)
        self.assertTrue(safe(checks))
        self.assertFalse(safe([('consumer', ('producer',), 'read', True)]))
        self.assertFalse(safe([('writer', (), 'write', True)]))
        self.assertFalse(safe([('external', (), 'read', False)]))
        observed = {'read-producer': 0, 'read-consumer': 1}
        self.assertEqual([name for name, code in observed.items() if code], ['read-consumer'])
        print('V2: compact inline union/shared output/ordered checkpoints; '
              'missing criterion/gate/access and dependent/write/permission batching rejected')

    def test_affected_selection_final_bytes_and_baseline_applicability(self):
        self.assert_carrier_guards('Execute and Integrate', (
            'Choose affected checks from the changed contract and current test collection',
            'verify selectors reach current guards rather than retired adjacent contracts',
            'Attribute inherited failures only with an applicable baseline',
            'identify both revisions and relevant differences',
            'equivalent selector, tool/environment and failure oracle',
            'byte identity is not an automatic comparison prerequisite',
            'Retain inherited failures alongside new regressions or increased severity',
            'Run checks on final bytes; later edits invalidate only affected proof',
            'A skipped test or old green report is not new proof',
            'Reuse prior evidence only after confirming scope, relevant bytes and environment remain applicable',
        ))
        # Reuse must not turn a skipped final check into a fresh pass.
        brief, returned = audited_sample()
        returned['items']['T006/V1'].update(status='skipped', reason='old report was green')
        self.assertEqual(simulated_audit(brief, returned), 'blocked')
        brief, returned = audited_sample()
        returned['item_revisions']['T006/V1'] = 'edited-after-check'
        self.assertEqual(simulated_audit(brief, returned), 'blocked')

    def test_current_proof_reuse_and_changed_baseline_comparison(self):
        proof = dict(revision='before', bytes='guard-v1', selector='current-guard',
                     collected=1, status='fail', environment='offline-python',
                     oracle='preserve-both-IDs', behavior=['dropped-V2'])
        def reusable(old, current):
            return (old['bytes'] == current['bytes'] and old['environment'] == current['environment']
                    and old['selector'] == current['selector'] == 'current-guard'
                    and current['collected'] > 0 and current['status'] != 'skipped')
        def compare(old, current):
            if (not old['revision'] or not current['revision'] or
                any(old[key] != current[key] for key in ('selector', 'environment', 'oracle')) or
                current['selector'] != 'current-guard' or not current['collected']):
                return None  # insufficient evidence, not demonstrated violation
            return (set(old['behavior']) & set(current['behavior']),
                    set(current['behavior']) - set(old['behavior']))
        current = dict(proof, revision='after', bytes='guard-v2',
                       behavior=['dropped-V2', 'dropped-V1'])
        self.assertFalse(reusable(proof, current))
        self.assertEqual(compare(proof, current), ({'dropped-V2'}, {'dropped-V1'}))
        self.assertTrue(reusable(proof, dict(proof, revision='unrelated-edit')))
        for changes in (dict(selector='retired'), dict(collected=0), dict(status='skipped'),
                        dict(bytes='edited-after-check'), dict(environment='different')):
            self.assertFalse(reusable(proof, dict(proof, **changes)))
        for changes in (dict(oracle='different-oracle'), dict(selector='retired'),
                        dict(revision=''), dict(environment='different')):
            self.assertIsNone(compare(proof, dict(current, **changes)))
        # Same failure text is deliberately not an input to the comparison oracle.
        print('V3: changed-byte comparison retains inherited drop plus new drop; '
              'unaffected proof reusable; stale/empty/skip/mismatched oracle blocked')

    def test_stall_is_diagnosed_before_deadline_without_polling(self):
        self.assert_carrier_guards('Delegate', (
            'On an observed stall or failure, inspect the actual invocation and available checkpoint/proof now',
            'do not wait for a full timeout just because budget remains',
            'Narrow the diagnosed missing work while preserving verified checkpoints and applicable partial evidence',
            'This is event-driven recovery, not routine polling or an arbitrary stop threshold',
            'Silence alone is not an observable stall',
            'Without supported signals, early detection is not promised',
        ))

    def test_event_inspection_retains_checkpoint_and_silence_waits(self):
        signals = ('worker setup blocker', 'failed first check',
                   'runtime attention/failure', 'available progress showing blocked work')
        brief, failed = failed_capability_sample()
        def trace_valid(signal, actions):
            return actions == (['inspect invocation/checkpoint/proof', 'narrow diagnosed gap']
                               if signal in signals else ['inspect/wait'])
        for signal in signals:
            trace = ['inspect invocation/checkpoint/proof', 'narrow diagnosed gap']
            self.assertTrue(trace_valid(signal, trace))
            self.assertFalse(trace_valid(signal, ['wait for timeout'] + trace))
            # Diagnosis is bounded setup, not an inferred model-capability failure.
            narrowed = dict(current_sha=failed['revision'], passed=['T005/V1'],
                            prior_proof=deepcopy(failed['outputs']),
                            missing='assigned-workspace first-check proof')
            self.assertEqual(narrowed['current_sha'], failed['revision'])
            self.assertEqual(narrowed['prior_proof'], failed['outputs'])
            self.assertEqual(narrowed['passed'], ['T005/V1'])
        self.assertTrue(trace_valid(None, ['inspect/wait']))
        self.assertFalse(trace_valid(None, ['relaunch']))
        for child, action in (('running', 'inspect/wait'), ('unknown', 'reconcile')):
            event = dict(child=child, action=action, reason='existing child')
            self.assertEqual(preparation_trace_errors(TEXT, [event]), [])
            self.assertIn('child reconciliation', preparation_trace_errors(
                TEXT, [dict(event, action='replacement dispatch')]))
        self.assertIsNone(simulated_repair_brief(brief, failed, 'unknown'))
        self.assertIsNone(simulated_repair_brief(brief, failed, 'model_capability', inspected=False))
        print('V4: blocker event -> inspect invocation/checkpoint/proof -> narrow retaining SHA/items; '
              'silence/running/unknown prevent replacement; no early-detection promise')


if __name__ == "__main__":
    unittest.main(verbosity=2)
