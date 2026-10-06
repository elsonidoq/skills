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
         "required": [{"ref": "T005/V1", "criterion": "shared check passes",
                       "check": "fixture shared-check", "expected_evidence": "shared-output",
                       "manual_gate": "scope inspection", "permission_gate": "local only"}]},
        {"id": "T006", "baseline": "fixture-task-005", "owned_paths": ["fixture/consumer.md"],
         "required": [{"ref": "T006/V1", "criterion": "shared check passes",
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
        "outputs": {"shared-output": {"command": "fixture shared-check", "exit": 0,
                                      "observable": "both invariants satisfied"}},
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


def simulated_audit(brief, returned):
    """Bounded acceptance oracle for sample artifacts, not production enforcement."""
    expected = {item["ref"] for item in brief["required_union"]}
    if set(returned["items"]) != expected:
        return "blocked"
    for item in brief["required_union"]:
        result = returned["items"][item["ref"]]
        output = returned["outputs"].get(result.get("evidence"))
        if (result.get("status") != "pass" or not output
                or output.get("command") != item["check"]
                or output.get("exit") != 0
                or output.get("observable") != "both invariants satisfied"
                or not all(returned["gates"].get(item["ref"], {}).get(gate)
                           for gate in ("manual", "permission"))):
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
        "command": "fixture shared-check", "exit": 1, "observable": "compatibility invariant failed"}
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
            "command": "fixture shared-check", "exit": 0, "observable": "both invariants satisfied"}
        repaired["items"]["T006/V1"]["evidence"] = "repair-output"
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


if __name__ == "__main__":
    unittest.main()
