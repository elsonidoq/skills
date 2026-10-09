#!/usr/bin/env python3
"""Static checks for context-continuity batching instructions."""

from copy import deepcopy
from pathlib import Path
import unittest


TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")


RUBRIC_PATH = Path(__file__).parents[1] / "references" / "batch-routing.md"


class SeedRubricTests(unittest.TestCase):
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
            "Family rationale", "Effort rationale", "Luna/medium", "Luna/max",
            "Sol/low", "Sol/medium", "Astra", "Terra", "no universal ladder",
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


def approval_errors(text):
    """Section-bound instruction check, not a runtime authorization engine."""
    graph = " ".join(text.split("## Build the Execution Graph", 1)[-1].split(
        "## Select Execution Capability", 1)[0].split())
    capability = " ".join(text.split("## Select Execution Capability", 1)[-1].split(
        "## Execute and Integrate", 1)[0].split())
    errors = []
    for label, phrase in {
        "table": "present the entire execution plan as a Markdown table",
        "description": "one or two sentences describing the batch",
        "profile": "proposed exact binding and effort",
        "approval": "Implementation authorization is not execution-routing approval",
        "gate": "before any implementation write or dispatch",
        "question": "use `ask_user` to obtain explicit approval",
        "resume": "Reuse verified unchanged approval on resume",
        "change": "Changes to batch boundaries or exact profiles require approval of the affected rows",
    }.items():
        if phrase not in graph:
            errors.append(label)
    if "Do not ask for routine batching approval" in graph:
        errors.append("approval-bypass")
    for label, phrase in {
        "assessment-order": "Assess every batch before presenting the complete table",
        "no-default": "Never inherit Sol/medium or another universal default",
        "uniform-valid": "Identical profiles across batches are valid when individually justified",
    }.items():
        if phrase not in capability:
            errors.append(label)
    return errors


class ApprovalGateTests(unittest.TestCase):
    def test_complete_table_and_assessment_gate(self):
        self.assertEqual(approval_errors(TEXT), [])

    def test_missing_table_description_profile_approval_and_default_guards(self):
        for phrase, diagnostic in (
            ("present the entire execution plan as a Markdown table", "table"),
            ("one or two sentences describing the batch", "description"),
            ("proposed exact binding and effort", "profile"),
            ("Implementation authorization is not execution-routing approval", "approval"),
            ("before any implementation write or dispatch", "gate"),
            ("use `ask_user` to obtain explicit approval", "question"),
            ("Assess every batch before presenting the complete table", "assessment-order"),
            ("Never inherit Sol/medium or another universal default", "no-default"),
        ):
            with self.subTest(diagnostic=diagnostic):
                normalized = " ".join(TEXT.split())
                self.assertIn(diagnostic, approval_errors(normalized.replace(phrase, "REMOVED", 1)))
        mutated = TEXT.replace("## Select Execution Capability", "Do not ask for routine batching approval\n\n## Select Execution Capability", 1)
        self.assertIn("approval-bypass", approval_errors(mutated))

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
        for phrase, label in (("Reuse verified unchanged approval on resume", "resume"),
                              ("Changes to batch boundaries or exact profiles require approval of the affected rows", "change")):
            self.assertIn(label, approval_errors(" ".join(TEXT.split()).replace(phrase, "REMOVED", 1)))


def dispatch_seam_errors(text):
    """Check actual launch carrier; footer repetitions cannot supply missing rules."""
    carrier = " ".join(text.split("## Select Execution Capability", 1)[-1].split(
        "## Execute and Integrate", 1)[0].split())
    errors = [phrase for phrase in (
        "once its required conditions are satisfied, dispatch",
        "no state-specific dispatch-intent checkpoint is required",
        "reopen only for concrete invalidating evidence",
        "condition, concrete gap, affected action and smallest resolution",
        "reopen only affected preparation",
        "healthy worker progress is not invalidation",
        "Normally use direct `subagent({agent,task,...})`",
        "even multiple internal sequential tasks",
        "A batch alone does not justify a workflow wrapper",
        "named continuation/recovery, branching/aggregation or reusable orchestration",
        "terse reason in the existing dispatch brief/tracker",
        "Justified one-child workflows remain allowed; do not migrate existing runs",
        "Direct delegated launch is not local execution",
        "Both shapes retain the same approval",
    ) if phrase not in carrier]
    for unsafe in ("Use workflowScript merely because it is a batch", "Ban all one-child workflows",
                   "Migrate existing runs to direct launch", "Direct delegation counts as local execution",
                   "Skip profile validation for direct launch", "Skip approval gates for workflow launch"):
        if unsafe in carrier:
            errors.append(unsafe)
    return errors


class DispatchSeamTests(unittest.TestCase):
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
    recovery = " ".join(text.split("### Recovery before continuation", 1)[-1].split(
        "### Writes and checkpoint ordering", 1)[0].split())
    for phrase in ("running child means inspect/wait, not duplicate dispatch",
                   "unknown status or a missing child ID requires runtime reconciliation"):
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


class PreparationTraceTests(unittest.TestCase):
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
        for changed in ("profile", "content", "workspace ownership"):
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
        phrase = "reopen only for concrete invalidating evidence"
        altered = TEXT.replace(phrase, "REMOVED", 1) + "\n## Footer\n" + phrase
        self.assertIn(phrase, preparation_trace_errors(altered, trace))


class BatchingContractTests(unittest.TestCase):
    def test_coherent_sequential_work_is_not_split_by_incidental_boundaries(self):
        self.assertIn("amortize startup and retain\n   useful context", TEXT)
        self.assertIn("Internal dependencies, shared files, and phase/story headings do not require", TEXT)
        self.assertIn("verifies each producer before its\n   consumer", TEXT)
        self.assertIn("commits each task separately", TEXT)

    def test_only_evidenced_boundaries_split_and_order_stays_fixed(self):
        self.assertIn("Normally 2–5 related tasks when scope and observed context permit", TEXT)
        self.assertIn("material profile differences, permissions, owner gates, context limits, incompatible scope", TEXT)
        self.assertIn("Never pull\n   a distant producer forward or reorder a prerequisite", TEXT)
        self.assertIn("delegate only asynchronously in the background", TEXT)
        self.assertIn("never\n   run implementation batches in parallel", TEXT)

    def test_selection_to_dispatch_contract(self):
        for phrase in (
            "[qualified seed rubric](references/batch-routing.md)",
            "one exact profile per invocation", "ordered task IDs", "weakest material blind spot",
            "applicable approved evidence or explicit none", "proposed versus owner-selected",
            "Family rationale", "Effort rationale", "conditional repair option",
            "at assignment and again at dispatch", "supported effort", "callable binding",
            "Registry entries and suffix syntax alone", "actual model or effort remains unknown",
            "model: \"provider/id:effort\"", "no silent settings/agent override",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, " ".join(TEXT.split()))
        self.assertNotIn("one required\n   model class", TEXT)

    def test_rotation_uses_observed_context_and_durable_handoff(self):
        self.assertIn("observed context\n  headroom is adequate", TEXT)
        self.assertIn("smaller fresh brief with durable handoff context", TEXT)


class SimulatedProfileTraceTests(unittest.TestCase):
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
        self.assertIn("proposed versus owner-selected", TEXT)
        actual = self.simulated_dispatch(decision["proposal"])
        self.assertEqual(actual["disposition"], "ready")
        self.assertEqual(actual["args"]["model"], "symbolic/luna:medium")

    def test_luna_max_exact_effort_to_dispatch(self):
        self.assertIn("Max must have an explicit extra-reasoning rationale", RUBRIC_PATH.read_text())
        selected = "symbolic/luna:max"
        brief = {"selected": selected, "family": "bounded multi-file, strong oracles",
                 "effort": "moderate residual reasoning needs extra budget"}
        args = self.simulated_dispatch(brief["selected"])["args"]
        self.assertEqual(args["model"], "symbolic/luna:max")
        self.assertIn("Copy the owner-selected binding and effort unchanged", TEXT)

    def test_deep_tools_and_weak_oracle_stop_optimistic_luna(self):
        rubric = RUBRIC_PATH.read_text()
        self.assertIn("Deep tool use, weak oracles", rubric)
        self.assertIn("defeat optimistic Luna routing", rubric)
        self.assertIn("weakest material blind spot", TEXT)
        for case in ("deep tools", "weak oracle"):
            with self.subTest(case=case):
                # Owner/design gate prevents launch while assessment lacks an authorized stronger option.
                actual = self.simulated_dispatch("symbolic/luna:medium", owner=False)
                self.assertEqual(actual["disposition"], "blocked")
                self.assertIsNone(actual["args"])
                self.assertIn("stronger option or stop at the owner/design gate", rubric)

    def test_unsupported_binding_effort_and_permission_block(self):
        self.assertIn("Any missing permission, binding, supported effort or tool access blocks dispatch", TEXT)
        for missing in ("permission", "binding", "effort", "tools", "owner", "manual"):
            gates = dict.fromkeys(("permission", "binding", "effort", "tools", "owner", "manual"), True)
            gates[missing] = False
            actual = self.simulated_dispatch("symbolic/luna:medium", **gates)
            args = actual["args"]
            with self.subTest(missing=missing):
                self.assertIsNone(args)
        self.assertIn("Registry entries and suffix syntax alone", TEXT)
        self.assertIn("Required manual gates remain blocking", TEXT)

    def test_unobservable_actual_effort_is_unknown(self):
        self.assertIn("actual model or effort remains unknown", TEXT)
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
             "checkpoint_convention": "per-task commit then separate evidence commit"}
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
            {"task": "T005", "baseline": "fixture-base", "result": "fixture-task-005",
             "evidence_checkpoint": "fixture-evidence-005"},
            {"task": "T006", "baseline": "fixture-evidence-005", "result": "fixture-task-006",
             "evidence_checkpoint": "fixture-evidence-006"},
        ],
    }
    # The next task starts after the prior separate evidence checkpoint.
    tasks[1]["baseline"] = "fixture-evidence-005"
    return brief, returned


class SimulatedUnionReturnTests(unittest.TestCase):
    """Sample brief/return trace, not a live invocation or model performance test."""

    def test_whole_required_union_and_return_carriers(self):
        normalized = " ".join(TEXT.split())
        for phrase in (
            "whole union of REQUIRED task-local references", "expected evidence and pass criterion",
            "manual/permission gates", "shared output retains every item mapping",
            "pass/fail/not_verified", "explicit not_verified reason",
            "ordered baseline/result and separate evidence checkpoint references",
            "Missing or ambiguous REQUIRED contracts return to the producing review/approval gate",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

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
            self.assertTrue(cp["evidence_checkpoint"])
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
                or not cp.get("evidence_checkpoint") or not cp.get("diff_inspected")
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


class SimulatedAcceptanceTests(unittest.TestCase):
    """Offline Luna success and negative evidence cases; no live performance claim."""

    def test_cheap_acceptance_instruction_carriers(self):
        for phrase in (
            "validate every REQUIRED item against consistent concrete outputs",
            "Missing, failed, contradictory, unauthorized or unrun REQUIRED evidence blocks acceptance",
            "unmet manual/permission gates block acceptance and dependent release",
            "Optional checks cannot compensate", "no mandatory strong-model per-batch reviewer",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, " ".join(TEXT.split()))

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


class SimulatedRepairTests(unittest.TestCase):
    """Offline failure/repair scenarios, not comparative model performance evidence."""

    def test_diagnosis_first_repair_instruction_carriers(self):
        for phrase in (
            "Inspect the failed child run, invocation, partial commits and check evidence",
            "identify affected dependencies and invalidated REQUIRED items",
            "raise effort, change model or both", "no fixed profile ladder",
            "original assessment and selected/observed profile", "complete batch contract",
            "rerun every invalidated item", "reuse only confirmed-valid evidence",
            "Repair success alone does not prove model-only attribution",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, " ".join(TEXT.split()))

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
        self.assertIn("unknown cause stops blind restart", " ".join(TEXT.split()))



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


class SimulatedFeedbackTests(unittest.TestCase):
    def test_factual_first_final_attempts_and_unknown_preserved(self):
        first = simulated_feedback("symbolic/luna:max", "unknown", "blocked", "model_capability")
        first["task_items"]["T006/V1"] = {"disposition": "failed", "proof": "consumer-failed"}
        original = deepcopy(first)
        final = simulated_feedback("symbolic/sol:medium", "unknown", "accepted", "model_capability")
        record = {"summary": "fixture/SUMMARY.md", "index_rows": 1, "attempts": [first, final],
                  "reused": ["T005/V1"], "invalidated_rerun": ["T006/V1"]}
        self.assertEqual(record["index_rows"], 1)
        self.assertEqual(first, original)
        self.assertEqual([a["observed"] for a in record["attempts"]], ["unknown", "unknown"])
        self.assertEqual(first["task_items"]["T006/V1"]["proof"], "consumer-failed")
        self.assertEqual(final["task_items"]["T006/V1"]["disposition"], "satisfied")
        self.assertEqual(first["escalation_reason"], "consumer drops V2")
        self.assertEqual(first["next_selected"], final["selected"])

    def test_feedback_instruction_carriers(self):
        memory = " ".join(COORDINATION_PATH.read_text().split())
        coordinator = " ".join(TEXT.split())
        for text in (memory, coordinator):
            for phrase in (
                "exact selected and observed profile", "contract strength", "first/final outcome",
                "accepted, partial, escalated and blocked", "model_capability",
                "planning_or_spec_gap", "verification_contract_gap", "batching_error",
                "environment_or_tooling", "external_dependency", "unknown",
                "Non-model causes never count as capability failure",
                "weak or invalidated successes", "unknown observation is never overwritten",
            ):
                with self.subTest(phrase=phrase, carrier="memory" if text == memory else "coordinator"):
                    self.assertIn(phrase, text)
        self.assertNotIn("class-share gates remain authoritative", memory)
        self.assertIn("Relevant approved guidance may override the seed", memory)

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
        for phrase in (
            "Resolve the current project root", "create only missing directories",
            "commit only those new files", "no opt-out or handoff-only persistence path",
            "read the compact evidence index first", "open only those selected records",
            "before its index entry", "never overwrite another run",
            "allow accept, edit, reject, or add", "Implementation approval grants no guideline",
            "compare with the approved baseline", "drift stops application",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, memory)


class PracticalVerificationTests(unittest.TestCase):
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


class VerificationGapTests(unittest.TestCase):
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


class ComparativeRoutingTests(unittest.TestCase):
    """Named manual recommendations and counterexamples, not a family-ranking engine."""
    def test_comparison_carrier_and_mutations(self):
        rubric = " ".join(RUBRIC_PATH.read_text().split())
        for clause in ("suitable smaller verified, permitted alternative",
                       "actual shortfall or select the smaller option", "none is verified/permitted",
                       "orchestration overhead", "stateful tooling/recovery",
                       "strict requirement versus a default preference"):
            self.assertIn(clause, rubric)
            self.assertNotIn(clause, rubric.replace(clause, "REMOVED", 1))
        graph = " ".join(TEXT.split("## Build the Execution Graph", 1)[1].split("## Select Execution Capability", 1)[0].split())
        self.assertIn("startup/context savings against losing a smaller-profile opportunity", graph)

    def test_named_comparative_recommendations_and_suitability_only_rejected(self):
        # Inputs and reasoned outputs are explicitly authored, not computed from a score.
        cases = (
            ("closed_design_strong_cheap_oracle", "bounded tools; cheap rollback; both verified/permitted",
             "symbolic/luna:low", "Luna meets the closed contract; no Sol shortfall claim", "low: tightly bounded inference"),
            ("hidden_coupling_costly_recovery", "adequate contract; weak oracle; stateful recovery; both verified/permitted",
             "symbolic/sol:medium", "Luna shortfall: hidden coupling and long recovery escape cheap checks", "medium: recovery reasoning"),
            ("alternative_unavailable", "only Sol verified/permitted; registry Luna is not callability",
             "symbolic/sol:low", "none is verified/permitted; no invented Luna inadequacy", "low: closed inference"),
            ("strict_medium", "owner policy requires medium; closed contract",
             "symbolic/luna:medium", "Luna meets closed contract", "medium: strict requirement, low not permitted"),
            ("default_medium_allows_low", "medium preference permits low; closed contract",
             "symbolic/luna:low", "Luna meets closed contract", "low: bounded inference beats default preference"),
            ("unsupported_effort", "selected Luna/low unsupported", None,
             "stop: effort support gate, not family inadequacy", "unsupported low blocks"),
            ("inadequate_contract", "missing consumer invariant despite available Sol", None,
             "stop: producing review/renewal, no model repairs criteria", "no effort can fix missing criteria"),
        )
        for name, inputs, proposal, family, effort in cases:
            with self.subTest(case=name):
                self.assertTrue(inputs and family and effort)
                self.assertNotEqual(family, effort)
                self.assertEqual(proposal is None, name in ("unsupported_effort", "inadequate_contract"))
        # Small artifact oracle: suitability alone is insufficient when an alternative exists.
        rationale = {"proposal": "symbolic/sol:medium", "alternative": "symbolic/luna:low",
                     "family": "hidden coupling defeats the cheap oracle", "effort": "medium for recovery",
                     "comparison": "Luna shortfall: stateful recovery outside checks"}
        def complete(record):
            return bool(record["family"] and record["effort"] and
                        (not record["alternative"] or record["comparison"]))
        self.assertTrue(complete(rationale))
        self.assertFalse(complete(dict(rationale, family="Sol is suitable", comparison="")))
        override = dict(rationale, selected="symbolic/luna:medium", observed="unknown")
        self.assertEqual(override["proposal"], "symbolic/sol:medium")
        self.assertEqual(SimulatedProfileTraceTests.simulated_dispatch(override["selected"])["args"]["model"], override["selected"])
        self.assertEqual(override["observed"], "unknown")
        stage = {"Standard plan_create": "symbolic/sol:medium", "implementation": cases[0][2]}
        self.assertNotEqual(stage["Standard plan_create"], stage["implementation"])
        self.assertIn("This exception does not assign implementation-task profiles", (Path(__file__).parents[2] / "planner/SKILL.md").read_text())

    def test_batch_tradeoff_examples(self):
        for name, saving, opportunity, decision in (
            ("docs_plus_final_recovery", "one intake saved", "docs can use verified smaller profile; recovery needs deeper tooling", "split consecutive tasks"),
            ("coherent_same_profile", "shared interface context and startup saved", "none: both need same recovery capability", "combine sequentially"),
        ):
            with self.subTest(case=name):
                self.assertTrue(saving and opportunity)
                self.assertIn(decision, ("split consecutive tasks", "combine sequentially"))
        self.assertIn("not force diversity or a split", TEXT)
        self.assertIn("commits each task separately", TEXT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
