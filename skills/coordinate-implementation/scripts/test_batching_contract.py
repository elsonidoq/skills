#!/usr/bin/env python3
"""Static checks for context-continuity batching instructions."""

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


if __name__ == "__main__":
    unittest.main()
