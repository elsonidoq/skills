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

    def test_delivery_boundary_clause_removals_have_named_diagnostics(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        for label, key, heading, clauses in checker.BOUNDARY_CARRIERS:
            for clause in clauses:
                with self.subTest(diagnostic=label, removed=clause):
                    changed = dict(texts)
                    body = checker.section(changed[key], heading)
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
        tasks = re.findall(r"(?m)^- \[ \] (T\d+) (.+)$", source)
        self.assertEqual([task_id for task_id, _ in tasks], ["T001", "T002"])
        self.assertTrue(tasks[0][1].startswith("[PROTOTYPE] "))
        self.assertFalse(any("cleanup" in title.lower() for _, title in tasks))
        blocks = re.split(r"(?m)^- \[ \] T\d+", source)[1:]
        prototype, delivery = blocks
        for block in blocks:
            for field in ("Outcome", "Files/interfaces", "Acceptance", "Capabilities", "Depends"):
                self.assertIn(f"**{field}**", block)
            for field in ("REQUIRED", "Pass:", "Smallest check:", "Evidence:", "Gate:"):
                self.assertIn(field, block)
        for phrase in ("ONE consequential question", "actual dependency/abstraction", "informational conclusion",
                       "script code and actual observed execution", "commands actually run", "tested limits",
                       "NOT VERIFIED, not PASS", "blocks assumed reliance", "No accompanying proof suite or separate harness",
                       "not a production feature or abstraction scaffold", "typically tens of lines"):
            self.assertIn(" ".join(phrase.split()), " ".join(prototype.split()))
        for phrase in ("**Depends**: T001", "inspect and use the applicable proof", "as informational evidence for implementation",
                       "permanent production acceptance tests", "A report-only link is insufficient",
                       "all applicable consumers", "production validation pass", "retain concise command/result/limits",
                       "failed/unrun producer cannot release"):
            self.assertIn(" ".join(phrase.split()), " ".join(delivery.split()))

    def test_B_C_both_adapter_informational_prototype_and_coherent_delivery(self):
        validator = load("risk_order", "../skills/task-generation/scripts/check-task-order.py")
        for name in ("risk-tiny-tasks.md", "risk-standard-tasks.md"):
            source = (HERE / "fixtures/planner" / name).read_text()
            self.assertEqual(validator.check(source), [], name)
            self.assert_risk_adapter_semantics(source)

    def test_prototype_marker_scope_execution_and_lifetime_negatives(self):
        mutations = (
            ("[PROTOTYPE] ", ""),
            ("ONE consequential question", "unbounded questions"),
            ("script code and actual observed execution", "script code only"),
            ("No accompanying proof suite or separate harness", "a separate proof suite and harness"),
            ("not a production feature or abstraction scaffold", "production scaffolding is required"),
            ("inspect and use the applicable proof", "link a report about the proof"),
            ("A report-only link is insufficient", "a report-only link is sufficient"),
            ("**Depends**: T001\n", "**Depends**: none\n"),
            ("production validation pass", "producer pass"),
        )
        for name in ("risk-tiny-tasks.md", "risk-standard-tasks.md"):
            source = (HERE / "fixtures/planner" / name).read_text()
            for old, new in mutations:
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
                body = checker.section(texts[key], heading)
                self.assertIn(" ".join(clause.split()), " ".join(body.split()))

    def test_outcome_boundaries_and_shared_proof_scenarios(self):
        # Concrete sensitivity records, not a planner, live operation, or semantic scoring layer.
        acceptance = [
            {"item": "A1", "criterion": "later independent records continue after an error",
             "pass": "later record is published", "check": "local sequential reader test",
             "evidence": "processed IDs and published values"},
            {"item": "A2", "criterion": "metadata opening reads no content before consumption",
             "pass": "zero reads before first frame", "check": "cumulative local read counter",
             "evidence": "counter and call order"},
            {"item": "wiring", "criterion": "selected identifier reaches the consumer unchanged",
             "pass": "captured argument is chosen-7", "check": "existing captured consumer argument fixture",
             "evidence": "captured argument equals selected ID", "expected": "chosen-7", "observed": "chosen-7"},
        ]
        gates = [{"permission": "local-only; no service or production operation",
                  "manual": "no additional approval gate"}]
        delivery = {
            "files": ["capture.py", "reader.py", "contract.md"],
            "required_items": ["T001/V1"],
            "tasks": [{"id": "T001", "outcome": "capture and publish validated records",
                       "acceptance": copy.deepcopy(acceptance), "gates": copy.deepcopy(gates),
                       "support_work": ["focused tests", "evidence", "operative docs", "routine teardown"]}],
            "separate_support_tasks": [],
        }

        def assert_settled_delivery(record):
            self.assertEqual(record["files"], ["capture.py", "reader.py", "contract.md"])
            self.assertEqual(record["required_items"], ["T001/V1"])
            self.assertEqual(len(record["tasks"]), 1)
            task = record["tasks"][0]
            self.assertEqual(task["outcome"], "capture and publish validated records")
            self.assertEqual(task["acceptance"], acceptance)
            wiring_check = task["acceptance"][-1]
            self.assertEqual(wiring_check["observed"], wiring_check["expected"])
            self.assertEqual(wiring_check["check"], "existing captured consumer argument fixture")
            self.assertEqual(task["gates"], gates)
            self.assertEqual(task["support_work"],
                             ["focused tests", "evidence", "operative docs", "routine teardown"])
            self.assertEqual(record["separate_support_tasks"], [])

        assert_settled_delivery(delivery)
        for label, mutate in (
            ("drop acceptance", lambda record: record["tasks"][0]["acceptance"].pop()),
            ("wrong captured value", lambda record: record["tasks"][0]["acceptance"][-1].update(observed="default-1")),
            ("drop gate", lambda record: record["tasks"][0]["gates"].clear()),
            ("split support task", lambda record: record["separate_support_tasks"].append("T002: report")),
        ):
            changed = copy.deepcopy(delivery)
            mutate(changed)
            with self.subTest(mutation=label), self.assertRaises(AssertionError):
                assert_settled_delivery(changed)

        risk_cases = [
            {"ref": "T001/V2", "kind": "migration", "prerequisite": {"id": "P-migration",
             "criterion": "existing records survive migration", "pass": "all sampled records remain",
             "check": "isolated migration dry run", "evidence": "dry-run output"},
             "delivery": {"id": "D-migration", "depends_on": [{"task": "P-migration", "relationship": "blocks"}],
                          "permission": "owner permission for migration", "manual": "approval before execution",
                          "executed": False}},
            {"ref": "T001/V2", "kind": "paid", "prerequisite": {"id": "P-paid", "criterion": "cost stays within approved bound",
             "pass": "cost estimate is within bound", "check": "offline cost review", "evidence": "bounded estimate"},
             "delivery": {"id": "D-paid", "depends_on": [{"task": "P-paid", "relationship": "blocks"}],
                          "permission": "owner permission for paid use", "manual": "approval before provider call",
                          "executed": False}},
            {"ref": "T001/V2", "kind": "live", "prerequisite": {"id": "P-live", "criterion": "staging behavior is acceptable",
             "pass": "staging check passes", "check": "isolated staging validation", "evidence": "staging result"},
             "delivery": {"id": "D-live", "depends_on": [{"task": "P-live", "relationship": "blocks"}],
                          "permission": "owner permission for live action", "manual": "approval before live execution",
                          "executed": False}},
        ]

        def assert_risky_prerequisites(records):
            self.assertEqual([record["kind"] for record in records], ["migration", "paid", "live"])
            self.assertEqual([record["ref"] for record in records], ["T001/V2"] * 3)
            for record in records:
                prerequisite = record["prerequisite"]
                delivery_task = record["delivery"]
                self.assertTrue(all(prerequisite[field] for field in
                                    ("criterion", "pass", "check", "evidence")))
                self.assertEqual(delivery_task["depends_on"],
                                 [{"task": prerequisite["id"], "relationship": "blocks"}])
                self.assertTrue(delivery_task["permission"])
                self.assertTrue(delivery_task["manual"])
                self.assertFalse(delivery_task["executed"])

        assert_risky_prerequisites(risk_cases)
        for label, mutate in (
            ("drop prerequisite edge", lambda record: record["delivery"].update(depends_on=[])),
            ("drop permission", lambda record: record["delivery"].update(permission="")),
            ("drop manual gate", lambda record: record["delivery"].update(manual="")),
        ):
            changed_risks = copy.deepcopy(risk_cases)
            mutate(changed_risks[0])
            with self.subTest(mutation=label), self.assertRaises(AssertionError):
                assert_risky_prerequisites(changed_risks)

        applicability = {"revision": "rev-1", "environment": "python-3.12-local",
                         "scope": "bounded-reader"}
        required = {"ref": "T001/V3", "criterion": "reuse unchanged proof and rerun only affected consumers",
                    "pass": "one shared result; changed applicability reruns only its consumer",
                    "check": "two-consumer revision/environment/scope scenario",
                    "evidence": "named reuse and invalidation outcomes",
                    "gates": {"permission": "local symbolic test only; no external operation",
                              "manual": "inspect applicability and limits"}}
        shared = {
            "required": required,
            "proof": {"id": "proof-1", "status": "pass", "applicability": applicability,
                      "evidence": {"code": "test_outcome_boundaries_and_shared_proof_scenarios",
                                   "execution": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-planner-workflow.py",
                                   "result": "PASS", "limits": "symbolic only; no model or service proof"}},
            "consumers": [
                {"id": "consumer-A", "mapping": "T001/V3", "applicability": copy.deepcopy(applicability),
                 "proof_used": "proof-1", "consumed": True, "production_validation": "pass"},
                {"id": "consumer-B", "mapping": "T001/V3", "applicability": copy.deepcopy(applicability),
                 "proof_used": "proof-1", "consumed": True, "production_validation": "pass"},
            ],
            "reuse": {"runs": 1, "result": "proof-1", "consumers": ["consumer-A", "consumer-B"]},
            "disposal": {"allowed": True, "after_consumed": ["consumer-A", "consumer-B"],
                         "after_validation": ["consumer-A", "consumer-B"],
                         "retained": {"command": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-planner-workflow.py",
                                      "result": "PASS", "limits": "symbolic only"}},
        }

        def assert_shared_proof(record):
            item = record["required"]
            self.assertEqual(set(item), {"ref", "criterion", "pass", "check", "evidence", "gates"})
            self.assertEqual(set(item["gates"]), {"permission", "manual"})
            self.assertTrue(all(item[field] for field in ("ref", "criterion", "pass", "check", "evidence")))
            self.assertTrue(all(item["gates"].values()))
            proof = record["proof"]
            self.assertEqual(proof["status"], "pass")
            self.assertTrue(all(proof["evidence"][field] for field in ("code", "execution", "result", "limits")))
            self.assertEqual(proof["evidence"]["result"], proof["status"].upper())
            consumers = record["consumers"]
            ids = [consumer["id"] for consumer in consumers]
            self.assertEqual(ids, ["consumer-A", "consumer-B"])
            self.assertEqual([consumer["mapping"] for consumer in consumers], [item["ref"], item["ref"]])
            self.assertEqual([consumer["applicability"] for consumer in consumers],
                             [proof["applicability"], proof["applicability"]])
            self.assertTrue(all(consumer["consumed"] and consumer["production_validation"] == "pass"
                                for consumer in consumers))
            self.assertEqual([consumer["proof_used"] for consumer in consumers], [proof["id"], proof["id"]])
            self.assertEqual(record["reuse"], {"runs": 1, "result": proof["id"], "consumers": ids})
            self.assertTrue(record["disposal"]["allowed"])
            self.assertEqual(record["disposal"]["after_consumed"], ids)
            self.assertEqual(record["disposal"]["after_validation"], ids)
            self.assertEqual(record["disposal"]["retained"],
                             {"command": proof["evidence"]["execution"], "result": "PASS",
                              "limits": "symbolic only"})

        assert_shared_proof(shared)
        for dimension, replacement in (("revision", "rev-2"), ("environment", "python-3.13-local"),
                                       ("scope", "narrower-reader")):
            changed = copy.deepcopy(shared)
            changed["consumers"][0]["applicability"][dimension] = replacement
            changed["consumers"][0]["proof_used"] = "proof-2"
            changed["resolution"] = {
                "rerun": ["consumer-A"], "reuse": {"consumer-B": "proof-1"},
                "rerun_result": {"id": "proof-2", "status": "pass",
                                 "applicability": copy.deepcopy(changed["consumers"][0]["applicability"]),
                                 "evidence": copy.deepcopy(changed["proof"]["evidence"]),
                                 "production_validation": "pass"}
            }
            with self.subTest(invalidation=dimension):
                self.assertNotEqual(changed["consumers"][0]["applicability"][dimension],
                                    changed["proof"]["applicability"][dimension])
                self.assertEqual({key: value for key, value in changed["consumers"][0]["applicability"].items()
                                  if key != dimension},
                                 {key: value for key, value in changed["proof"]["applicability"].items()
                                  if key != dimension})
                self.assertEqual(changed["consumers"][1]["applicability"], changed["proof"]["applicability"])
                self.assertEqual(changed["resolution"]["rerun"], ["consumer-A"])
                self.assertEqual(changed["resolution"]["reuse"], {"consumer-B": "proof-1"})
                rerun = changed["resolution"]["rerun_result"]
                self.assertEqual(rerun["status"], "pass")
                self.assertEqual(rerun["evidence"]["result"], "PASS")
                self.assertTrue(all(rerun["evidence"][field] for field in ("code", "execution", "limits")))
                self.assertEqual(rerun["production_validation"], "pass")
                self.assertEqual(rerun["applicability"], changed["consumers"][0]["applicability"])
                self.assertEqual(changed["consumers"][0]["production_validation"], "pass")
                self.assertEqual(changed["consumers"][0]["proof_used"], "proof-2")
                self.assertEqual(changed["consumers"][1]["proof_used"], "proof-1")
                self.assertEqual(changed["disposal"]["after_consumed"], ["consumer-A", "consumer-B"])
                self.assertEqual(changed["disposal"]["after_validation"], ["consumer-A", "consumer-B"])
                self.assertTrue(changed["disposal"]["allowed"])

        for label, mutate in (
            ("missing mapping", lambda record: record["consumers"][0].update(mapping=None)),
            ("stale proof", lambda record: record["consumers"][0]["applicability"].update(revision="stale")),
            ("premature consumption disposal", lambda record: record["disposal"].update(after_consumed=["consumer-A"])),
            ("premature validation disposal", lambda record: record["disposal"].update(after_validation=["consumer-A"])),
            ("failed proof", lambda record: record["proof"].update(status="failed")),
            ("unrun proof", lambda record: record["proof"].update(status="not-run")),
            ("report-only proof", lambda record: record["proof"].update(evidence={"code": None, "execution": None,
                                                                                    "result": "PASS", "limits": "link only"})),
        ):
            changed = copy.deepcopy(shared)
            mutate(changed)
            with self.subTest(mutation=label), self.assertRaises(AssertionError):
                assert_shared_proof(changed)

        print("Outcome records: settled multi-file acceptance/gates and focused wiring reject artificial splits; "
              "migration/paid/live prerequisites retain blocking edges and manual permission; "
              "two-consumer proof maps all fields, reuses unchanged output, scopes reruns and rejects unsafe disposal/release")


class SymbolicReaderStageOracle:
    """Tiny counter-observed local scenario; no real files, dependency or indexing product."""
    records = (
        {"id": "first", "state": "success", "value": "one"},
        {"id": "bad", "state": "error", "detail": "full private diagnostic"},
        {"id": "skip", "state": "skipped", "value": "not published"},
        {"id": "later", "state": "success", "value": "two"},
    )

    def __init__(self):
        self.capture_calls = self.dump_calls = self.rebuild_calls = 0
        self.reader_open_calls = self.reset_verify_calls = self.frame_scan_calls = 0
        self.status_calls = self.completion_calls = self.cleanup_calls = 0
        self.operator_record_calls = 0
        self.reader_content_reads = 0
        self.content_read_call_order = []
        self.captured = []
        self.descriptors = ()
        self.processed = []
        self.successful = []
        self.skipped = []
        self.published = []
        self.private_diagnostics = []
        self.public_progress = []
        self.invoked_modes = []

    def sequential_capture(self):
        self.capture_calls += 1
        self.captured = list(self.records)
        return self.captured

    def dump_descriptors(self):
        self.dump_calls += 1
        self.descriptors = tuple(record["id"] for record in self.captured)

    def rebuild_and_inline_validate_once(self):
        self.rebuild_calls += 1
        for record in self.captured:
            self.operator_record_calls += 1
            self.processed.append(record["id"])
            if record["state"] == "error":
                self.private_diagnostics.append(record["detail"])
            elif record["state"] == "skipped":
                self.skipped.append(record["id"])
            else:
                self.successful.append(record["id"])
                self.published.append(record["value"])
        self.public_progress.append(f"Processed {len(self.processed)} records")
        return tuple(self.successful)

    def maintained_reader_invocation(self, mode):
        self.invoked_modes.append(mode)
        return self.open_metadata_only_reader(mode)

    def open_metadata_only_reader(self, mode):
        self.reader_open_calls += 1
        return {"mode": mode, "descriptors": self.descriptors}

    def reset_and_verify(self, _reader):
        self.reset_verify_calls += 1

    def status(self, _reader):
        self.status_calls += 1
        return {"successes": len(self.successful), "skipped": len(self.skipped)}

    def completion(self, _reader):
        self.completion_calls += 1

    def cleanup(self, _reader):
        self.cleanup_calls += 1

    def read_dataset_content(self, _record):
        self.reader_content_reads += 1
        self.content_read_call_order.append("read_dataset_content")

    def consume_first_frame(self, reader):
        self.frame_scan_calls += 1
        self.content_read_call_order.append("consume_first_frame")
        self.read_dataset_content(reader["descriptors"][0])


class A4AcceptancePreservationTests(unittest.TestCase):
    def assert_local_lifecycle(self, oracle_type):
        for mode in ("mode-a", "mode-b"):
            oracle = oracle_type()
            oracle.sequential_capture()
            oracle.dump_descriptors()
            oracle.rebuild_and_inline_validate_once()
            reader = oracle.maintained_reader_invocation(mode)
            oracle.reset_and_verify(reader)
            status = oracle.status(reader)
            oracle.completion(reader)
            oracle.cleanup(reader)

            # These counters are incremented by the actual local operator methods/record loop.
            self.assertEqual(oracle.capture_calls, 1)
            self.assertEqual(oracle.dump_calls, 1)
            self.assertEqual(oracle.rebuild_calls, 1)
            self.assertEqual(oracle.captured, list(oracle.records))
            self.assertEqual(oracle.descriptors, tuple(record["id"] for record in oracle.records))
            self.assertEqual(oracle.operator_record_calls, len(oracle.records))
            self.assertEqual(oracle.processed, ["first", "bad", "skip", "later"])
            self.assertEqual(oracle.successful, ["first", "later"])
            self.assertEqual(oracle.skipped, ["skip"])
            self.assertEqual(oracle.published, ["one", "two"])
            self.assertEqual(status, {"successes": 2, "skipped": 1})
            self.assertNotIn("full private diagnostic", status.values())
            self.assertEqual(oracle.private_diagnostics, ["full private diagnostic"])
            self.assertLessEqual(len(oracle.public_progress), 1)
            self.assertEqual(oracle.reader_open_calls, 1)
            self.assertEqual(oracle.reset_verify_calls, 1)
            self.assertEqual(oracle.invoked_modes, [mode])
            self.assertEqual(oracle.reader_content_reads, 0)
            self.assertEqual(oracle.content_read_call_order, [])
            self.assertEqual(oracle.frame_scan_calls, 0)

            oracle.consume_first_frame(reader)
            self.assertEqual(oracle.reader_content_reads, 1)
            self.assertEqual(oracle.content_read_call_order,
                             ["consume_first_frame", "read_dataset_content"])
            self.assertEqual(oracle.frame_scan_calls, 1)
            after_consumption = oracle.reader_content_reads
            oracle.completion(reader)
            oracle.status(reader)
            oracle.cleanup(reader)
            self.assertEqual(oracle.reader_content_reads, after_consumption)
            self.assertEqual(oracle.content_read_call_order,
                             ["consume_first_frame", "read_dataset_content"])
            self.assertEqual(oracle.frame_scan_calls, 1)

    def test_metadata_open_counters_and_local_stage_advancement(self):
        self.assert_local_lifecycle(SymbolicReaderStageOracle)

        class PreOpenReread(SymbolicReaderStageOracle):
            def open_metadata_only_reader(self, mode):
                self.read_dataset_content(self.descriptors[0])
                return super().open_metadata_only_reader(mode)

        class RebuildReread(SymbolicReaderStageOracle):
            def rebuild_and_inline_validate_once(self):
                result = super().rebuild_and_inline_validate_once()
                self.read_dataset_content(self.descriptors[0])
                return result

        class SilentReread(SymbolicReaderStageOracle):
            def open_metadata_only_reader(self, mode):
                reader = super().open_metadata_only_reader(mode)
                self.read_dataset_content(reader["descriptors"][0])
                return reader

        class NonAdvancingRebuild(SymbolicReaderStageOracle):
            def rebuild_and_inline_validate_once(self):
                self.rebuild_calls += 1
                return ()

        for mutation in (PreOpenReread, RebuildReread, SilentReread, NonAdvancingRebuild):
            with self.subTest(mutation=mutation.__name__):
                with self.assertRaises(AssertionError):
                    self.assert_local_lifecycle(mutation)
        print("A4 local oracle: sequential capture, one rebuild/operator pass, error continuation, "
              "success/skip accounting, private diagnostics, both maintained modes; "
              "cumulative counter/call order rejects pre-open, rebuild and post-open rereads "
              "plus non-advancement")


class ComposedAcceptanceTests(unittest.TestCase):
    """Actual carriers plus one shared local composition fixture, not live obedience."""
    def test_changed_carriers_and_bounded_mutations(self):
        texts = checker.load_texts()
        errors = checker.check_contracts(texts)
        self.assertFalse([e for e in errors if e.startswith('composed-')], errors)
        for label, key, heading, clauses in checker.COMPOSED_CARRIERS:
            for clause in clauses:
                with self.subTest(diagnostic=label, removed=clause):
                    changed = dict(texts)
                    body = checker.section(texts[key], heading)
                    pattern = r'\s+'.join(re.escape(word) for word in clause.split())
                    changed[key] = changed[key].replace(body, re.sub(pattern, 'REMOVED', body), 1)
                    changed[key] += '\n## Footer only\n' + clause
                    self.assertTrue(any(e.startswith(label + ':') for e in checker.check_contracts(changed)))

    def test_consumes_shared_composed_reference_and_adapter_records(self):
        fixture = load('composed_task_reference', '../skills/task-generation/scripts/test_contract.py')
        suite = unittest.TestSuite(fixture.ComposedAcceptanceTests(name) for name in (
            'test_isolated_green_broken_and_corrected_first_write',
            'test_direct_and_speckit_inline_acceptance_records'))
        result = unittest.TestResult()
        suite.run(result)
        self.assertEqual(result.errors, [])
        self.assertEqual(result.failures, [])
        self.assertEqual(result.testsRun, 2)


class ParsimonyTests(unittest.TestCase):
    """Bounded authored decisions + actual carrier inspection, not agent behavior."""

    def test_canonical_policy_and_consumer_boundaries(self):
        policy = ROOT / "skills/planner/references/parsimony.md"
        self.assertTrue(policy.is_file(), "canonical parsimony owner missing")
        text = policy.read_text()
        for clause in ("smallest working solution", "legitimate behavior", "serious exposed",
                       "paginated read", "target drift", "existing gates", "not application startup"):
            self.assertIn(clause, text)
        for path, heading in (
            ("planner", "## Before selection"),
            ("brainstorming", "## Decision Rules"),
            ("planning-brainstorming", "## 1. Gate assessment"),
            ("tiny-spec", "## Compact source contract"),
            ("delegating-architectural-planning", "## Preflight"),
            ("delegating-architectural-planning", "## Planner Standard adapter contract"),
            ("task-generation", "## Preconditions and adapters"),
            ("requesting-code-review", "## Prepare The Review"),
            ("receiving-code-review", "## Evaluate Feedback"),
        ):
            with self.subTest(consumer=path, boundary=heading):
                body = checker.section((ROOT / "skills" / path / "SKILL.md").read_text(), heading)
                self.assertIn("parsimony.md", body)

    def test_policy_removal_is_detected(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        texts["parsimony"] = ""
        self.assertTrue(any(e.startswith("parsimony-policy:") for e in checker.check_contracts(texts)))

    def test_authored_simple_feature_and_justified_protection_review(self):
        # Expected findings for two authored review inputs, not generated reviews.
        cases = (
            ("rename saved view", "delete views after 30 days", "reject optional addition",
             ("absent source basis", "legitimate behavior", "false blocking")),
            ("public cross-tenant export", "authorize tenant before export", "retain protection",
             ("serious exposed", "security", "necessary protection")),
            ("upload to platform", "enforce actual platform limit", "retain protection",
             ("platform constraint", "invent no thresholds")),
        )
        policy = (ROOT / "skills/planner/references/parsimony.md").read_text()
        review = (ROOT / "skills/requesting-code-review/code-reviewer.md").read_text()
        for request, addition, expected, basis in cases:
            with self.subTest(request=request, addition=addition, expected=expected):
                for clause in basis:
                    self.assertIn(clause, policy + review)
        self.assertIn("additions as well as omissions", review)
        self.assertIn("REQUIRED", review)

    def test_safe_read_correction_versus_unsafe_target_drift(self):
        text = (ROOT / "skills/planner/references/parsimony.md").read_text()
        for clause in ("SDK/tool/compiler/platform", "invalidates evidence",
                       "smaller/paginated read", "target drift stops", "actionable correction"):
            self.assertIn(clause, text)

    def test_generated_defaults_do_not_invent_requirements(self):
        paths = [".specify/templates/" + n + "-template.md" for n in ("spec", "plan", "tasks")]
        paths += [".pi/prompts/speckit." + n + ".md" for n in ("specify", "plan", "tasks", "analyze", "checklist")]
        forbidden = ("Data retention: Industry-standard", "Include both quantitative metrics",
                     "For each dependency → best practices task", "Security hardening",
                     "No user story work can begin until this phase is complete",
                     "Include specific metrics (time, percentage, count, rate)")
        for path in paths:
            with self.subTest(path=path):
                text = (ROOT / path).read_text()
                self.assertIn("parsimony.md", text)
                for old in forbidden:
                    self.assertNotIn(old, text)


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
            ("coordinator", "Do not autonomously loop expensive failed runs", "coordination-routing"),
            ("coordinator", "No arbitrary workflow", "coordination-routing"),
        ):
            self.assert_clause_required(key, clause, diagnostic)

    def test_schema_security_durability_retain_necessary_checks(self):
        self.assert_clause_required("planner", "migration, authorization or persistence", "validation-risk")

    def test_optional_checks_cannot_silently_block(self):
        for key, clause, diagnostic in (
            ("planner", "Optional checks are not acceptance blockers", "validation-authority"),
            ("tasks", "optional task context", "validation-tasks"),
            ("coordinator", "Project check commands are optional", "validation-execution"),
        ):
            with self.subTest(key=key):
                self.assert_clause_required(key, clause, diagnostic)

    def test_owner_required_checks_need_authority_to_change(self):
        self.assert_clause_required("planner",
            "Never drop an owner-required check or approved\nsafety criterion without explicit authority",
            "validation-authority")
        self.assert_clause_required("coordinator", "Never adopt existing dirty files", "validation-execution")
        self.assert_clause_required("tasks", "real outcome", "validation-tasks")

    def test_timeout_narrows_remaining_work_without_blind_retry(self):
        for clause in ("Inspect a failed run and its invocation", "unknown cause stops blind retries",
                       "Preserve partial and unrelated work"):
            self.assert_clause_required("coordinator", clause, "validation-timeout")

    def test_reuse_and_causal_repairs_avoid_repeated_intake(self):
        for clause in ("Reuse valid unchanged evidence", "Avoid repeated historical intake", "actually blocks"):
            with self.subTest(clause=clause):
                self.assert_clause_required("planner", clause, "validation-reuse")


class VerificationCarrierTests(unittest.TestCase):
    def test_unconditional_escalation_restoration_rejected_with_summaries_intact(self):
        texts = checker.load_texts()
        conditional = "Do not autonomously loop expensive failed runs"
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
            ("planner", "independent review and final approval remain required", "producer approval suffices", "task-stage:"),
            ("planner", "independent owner-selected reviewer", "implementer reviewer", "review:"),
            ("approval", "before calling `ask_user`", "after calling `ask_user`", "approval:"),
            ("approval", "Every actual task ID separately", "unstructured paragraphs", "approval:"),
            ("planner", "brief bullet-list executive summary", "summary in tool context", "tiny-flow:"),
            ("planner", "immediately continue to `plan_create`", "wait for another prompt", "spec:"),
            ("planner", "immediately proceed to handoff", "report readiness and stop", "tiny-flow:"),
            ("planner", "Do not end the turn merely to report approval", "End the turn after approval", "continuation:"),
            ("planner", "automatically invoke `coordinate-implementation`", "wait for a separate execution request", "final-continuation:"),
            ("approval", "inside tasks", "separate new source", "legacy:"),
            ("tasks", "nonempty string `id`", "missing ID", "task-contract:"),
            ("brainstorm", "no more than three items", "unbounded agenda", "brainstorm:"),
            ("brainstorm", "Only in selected-production", "In any mode", "brainstorm:"),
            ("coordinator", "checkpoint per implementation/repair task", "checkpoint per batch", "execution-checkpoints:"),
            ("coordinator", "real focused checkpoint", "Any report releases", "execution-sequential:"),
            ("coordinator", "exactly six linter checks", "required source checklist", "intake:"),
            ("coordinator", "owner-selected executor/effort", "agent default bindings", "execution-selection:"),
            ("coordinator", "without silent substitutions", "substitute defaults", "execution-selection:"),
            ("coordinator", "never invent an answer", "invent an answer", "execution-strategy:"),
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
        body = checker.section(self.texts["planner"], "## Job first; no coordinator bookkeeping")
        self.assertTrue(body)
        self.assertLess(self.texts["planner"].index(body),
                        self.texts["planner"].index("## Discovery and capability boundary"))
        obligations = (
            "no coordinator bookkeeping",
            "Do not maintain administrative ledgers, progress records, evidence manifests",
            "Runtime-owned operational state stays runtime-owned",
            "Once required prerequisites are satisfied, advance the next authorized stage",
            "Reuse applicable settled evidence and decisions",
            "State each required fact once",
            "No repeated record polishing, duplicate evidence",
            "concrete invalidating evidence",
            "Carry this rule into every stage brief",
            "Never waive required approvals, safety checks, permissions, reviews or commits",
            "exact blocker and smallest required resolution",
        )
        for removed in (*obligations, body):
            with self.subTest(removed=removed):
                self.assertIn(" ".join(removed.split()), " ".join(body.split()))
                changed = dict(self.texts)
                changed["planner"] = re.sub(r"\s+".join(re.escape(w) for w in removed.split()), "", changed["planner"], count=1)
                self.assertTrue(any(e.startswith("job-first:")
                                    for e in checker.check_contracts(changed)))

    def test_scoped_constraints_concision_and_unsubmitted_editing(self):
        # Regression: a 37 KB task contract must not inherit a worker read-tool bound;
        # shortening an unsubmitted draft is ordinary production, not independent review.
        cases = (
            ("planner", "actual enforced limit at the consuming interface", "constraint-scope:"),
            ("planner", "An agent inference is not an owner requirement", "constraint-scope:"),
            ("planner", "interpret owner agreement within the explanation and scope actually presented", "constraint-scope:"),
            ("tasks", "A worker file-tool bound is not a task-contract loader bound", "task-concision:"),
            ("tasks", "State shared constraints once", "task-concision:"),
            ("tasks", "Keep task-specific work and useful checks clear", "task-concision:"),
            ("approval", "Ordinary drafting is not submitted-artifact correction", "draft-editing:"),
            ("approval", "without a supervisor decision", "draft-editing:"),
            ("planner", "producers may draft, revise, shorten and mechanically", "task-stage:"),
            ("planner", "independent review and final approval remain required", "task-stage:"),
        )
        for key, phrase, diagnostic in cases:
            with self.subTest(phrase=phrase):
                self.assertIn(" ".join(phrase.split()), " ".join(self.texts[key].split()))
                changed = dict(self.texts)
                changed[key] = re.sub(r"\s+".join(re.escape(w) for w in phrase.split()), "REMOVED", changed[key], count=1)
                self.assertTrue(any(e.startswith(diagnostic)
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
                target.write_text(original.replace("references/profile-selection.md", "references/absent.md"))
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
        self.assertIn("No extra evidence-only checkpoint", " ".join(text.split()))
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


class AcceptedDecisionBriefContinuityTests(unittest.TestCase):
    """Supplied authority fixture: planner brief/handoff wiring, not consumer obedience."""
    def test_accepted_constraints_reach_all_stage_briefs_and_handoffs(self):
        records = (
            {"status": "accepted", "constraint": "preserve the export capability",
             "source": "decisions/export.md#accepted", "operation": "capability removal",
             "gate": "existing approved supersession"},
            {"status": "accepted", "constraint": "retain the stable wire format",
             "source": "decisions/wire.md#accepted", "operation": "compatible helper deletion",
             "gate": None},
            {"status": "proposed", "constraint": "use a replacement exporter",
             "source": "decisions/replacement.md#proposed"},
            {"status": "superseded", "constraint": "use the retired wire format",
             "source": "decisions/old-wire.md#superseded"},
        )
        accepted = tuple(record for record in records if record["status"] == "accepted")
        self.assertEqual(accepted[0]["gate"], "existing approved supersession")
        self.assertIsNone(accepted[1]["gate"])

        stages = {
            "TinySpec": ("source", "tasks", "review"),
            "Standard": ("spec", "plan", "tasks", "review"),
        }
        emitted = {}
        for context in ("fresh", "resumed"):
            for dispatch in ("direct", "delegated"):
                for depth, names in stages.items():
                    for name in names:
                        key = (context, dispatch, depth, name)
                        emitted[key] = {
                            "accepted_constraints": tuple((record["constraint"], record["source"])
                                                          for record in accepted),
                            "handoff": tuple((record["constraint"], record["source"])
                                             for record in accepted),
                        }

        expected = tuple((record["constraint"], record["source"]) for record in accepted)

        def assert_continuity(output):
            self.assertEqual(len(output), 28)
            for brief in output.values():
                self.assertIn("accepted_constraints", brief)
                self.assertEqual(brief["accepted_constraints"], expected)
                self.assertEqual(brief["handoff"], expected)

        assert_continuity(emitted)
        missing_carrier = copy.deepcopy(emitted)
        del missing_carrier[("resumed", "delegated", "Standard", "review")]["accepted_constraints"]
        with self.assertRaises(AssertionError):
            assert_continuity(missing_carrier)

    def test_read_through_carriers_reject_omission(self):
        texts = checker.load_texts()
        cases = (
            ("## Discovery and capability boundary", "[save-adr](../save-adr/SKILL.md)",
             "accepted-decision-consultation:"),
            ("## Discovery and capability boundary", "whole discovered decision index",
             "accepted-decision-consultation:"),
            ("## Selected production and stage handoffs", "each applicable accepted outcome constraint\nand source link",
             "accepted-decision-stage-brief:"),
            ("## Handoff, not execution", "applicable accepted outcome constraints and source links",
             "accepted-decision-handoff:"),
        )
        for heading, clause, diagnostic in cases:
            with self.subTest(carrier=heading):
                changed = dict(texts)
                body = checker.section(changed["planner"], heading)
                changed["planner"] = changed["planner"].replace(
                    body, body.replace(clause, "OMITTED", 1), 1)
                self.assertTrue(any(error.startswith(diagnostic)
                                    for error in checker.check_contracts(changed)))


class ArchitecturalAcceptedDecisionContinuityTests(unittest.TestCase):
    """Supplied accepted-authority preflight/brief fixture; no SpecKit invocation."""

    def test_standalone_manager_and_resumed_briefs_preserve_exact_constraints(self):
        records = (
            {"status": "accepted", "constraint": "preserve the export capability",
             "source": "decisions/export.md#accepted", "outcome": "export remains available"},
            {"status": "accepted", "constraint": "retain the stable wire format",
             "source": "decisions/wire.md#accepted", "outcome": "wire payload remains stable"},
            {"status": "proposed", "constraint": "replace the exporter"},
            {"status": "superseded", "constraint": "use the retired wire format"},
        )
        accepted = tuple((record["constraint"], record["source"])
                         for record in records if record["status"] == "accepted")

        def preflight(entry, context, change=None):
            brief = {"entry": entry, "accepted_constraints": accepted, "source_links": accepted,
                     "reestablished": context == "resumed"}
            if change == "remove export":
                return {"stop": "existing owner and approval-renewal gates", "brief": brief}
            return {"stop": None, "brief": brief}

        runs = [preflight(entry, context)
                for entry in ("standalone", "manager")
                for context in ("fresh", "resumed")]
        self.assertEqual(len(runs), 4)
        self.assertEqual([run["brief"]["entry"] for run in runs],
                         ["standalone", "standalone", "manager", "manager"])
        for run in runs:
            self.assertIsNone(run["stop"])
            self.assertEqual(run["brief"]["accepted_constraints"], accepted)
            self.assertEqual(run["brief"]["source_links"], accepted)
        self.assertFalse(runs[0]["brief"]["reestablished"])
        self.assertTrue(runs[-1]["brief"]["reestablished"])
        self.assertEqual(preflight("standalone", "fresh", "remove export")["stop"],
                         "existing owner and approval-renewal gates")

        text = (ROOT / "skills/delegating-architectural-planning/SKILL.md").read_text()
        preflight_text = checker.section(text, "## Preflight")
        for clause in (
            "standalone or manager-governed entry, and in fresh or resumed contexts",
            "each exact applicable accepted outcome constraint and source link into the planning brief and any resume/handoff",
            "existing owner and approval-renewal gates",
            "Compatible helper/mechanism cleanup that preserves the outcome needs no new gate",
            "including the exact applicable accepted outcome constraints and source links",
        ):
            with self.subTest(clause=clause):
                normalized = " ".join(clause.split())
                self.assertIn(normalized, " ".join(preflight_text.split()))
                removed = re.sub(r"\s+".join(re.escape(word) for word in clause.split()),
                                 "OMITTED", preflight_text, count=1)
                self.assertNotIn(normalized, " ".join(removed.split()))


class BrainstormAcceptedDecisionContinuityTests(unittest.TestCase):
    """Static contract plus synthetic read-only walkthrough; not model-obedience proof."""

    def test_discovered_preselection_selected_and_resumed_constraints_without_writes(self):
        # Only dummy project data. This models the intended read/gate order, not a
        # production planner implementation or an actual agent following the skill.
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "choices").mkdir()
            (project / "AGENTS.md").write_text("Decision index: choices/index.json\n")
            (project / "choices/index.json").write_text(json.dumps([
                "export.json", "replacement.json", "retired.json"]))
            for name, status in (("export", "accepted"), ("replacement", "proposed"),
                                 ("retired", "superseded")):
                (project / f"choices/{name}.json").write_text(json.dumps({
                    "status": status, "outcome": "preserve the export capability",
                    "mechanism": "incidental helper", "source": f"choices/{name}.json"}))

            def snapshot():
                return {str(path.relative_to(project)): path.read_bytes()
                        for path in project.rglob("*") if path.is_file()}

            def assess(mode, change, supplied=()):
                reads = ["AGENTS.md"]
                routing = (project / reads[0]).read_text().strip()
                index = project / routing.split(": ", 1)[1]
                accepted = list(supplied)
                if index.is_file():
                    reads.append(str(index.relative_to(project)))
                    for name in json.loads(index.read_text()):  # whole index, not first match
                        record_path = index.parent / name
                        reads.append(str(record_path.relative_to(project)))
                        record = json.loads(record_path.read_text())
                        if record["status"] == "accepted":
                            accepted.append((record["outcome"], record["source"]))
                reads.append("affected gate assessment")
                return {"mode": mode, "reads": reads, "gate_constraints": tuple(accepted),
                        "handoff_constraints": tuple(accepted),
                        "stop": "existing owner supersession gate" if accepted and
                        change == "remove export" else None}

            before = snapshot()
            expected = (("preserve the export capability", "choices/export.json"),)
            for mode in ("standalone fresh preselection", "resumed preselection",
                         "selected-production", "resumed selected-production"):
                with self.subTest(mode=mode):
                    run = assess(mode, "remove export")  # no caller-supplied ADR
                    self.assertEqual(run["gate_constraints"], expected)
                    self.assertEqual(run["handoff_constraints"], expected)
                    self.assertLess(run["reads"].index("choices/export.json"),
                                    run["reads"].index("affected gate assessment"))
                    self.assertIn("choices/retired.json", run["reads"])
                    self.assertEqual(run["stop"], "existing owner supersession gate")
                    self.assertIsNone(assess(mode, "delete compatible helper")["stop"])
                    self.assertEqual(snapshot(), before)
            # Fixture setup removes storage; assessment itself must not recreate it.
            for path in (project / "choices").iterdir():
                path.unlink()
            (project / "choices").rmdir()
            before = snapshot()
            for mode in ("standalone fresh preselection", "resumed preselection"):
                run = assess(mode, "unrelated legacy work")
                self.assertEqual(run["gate_constraints"], ())
                self.assertIsNone(run["stop"])
                self.assertEqual(snapshot(), before)

    def test_read_through_requires_consult_timing_and_existing_boundaries(self):
        text = (ROOT / "skills/planning-brainstorming/SKILL.md").read_text()
        preflight = checker.section(text, "## Capability preflight")
        gate = checker.section(text, "## 1. Gate assessment")
        handoff = checker.section(text, "## Durable handoff and resume")
        for forbidden in ("do not discover", "session history only",
                          "from the supplied constraints/session history in preselection"):
            self.assertNotIn(forbidden, " ".join(text.split()))
        self.assertIn("no source edits or", checker.section(text, "## Modes"))
        self.assertIn("Only in selected-production or legacy-repair mode",
                      checker.section(text, "## 3. Apply decisions"))
        for body, clause in (
            (preflight, "Before gate assessment, consult [save-adr](../save-adr/SKILL.md)'s **Consult and\npropagate** contract."),
            (preflight, "In all modes, including standalone fresh preselection, allow\nread-only discovery of existing project decision ownership, the whole decision index and\nrelevant accepted records in full before affected gate assessment, even when not supplied\nby the caller."),
            (preflight, "Use supplied constraints and session history as additional context, not a\ndiscovery limit."),
            (preflight, "Preselection forbids writes or artifact production, not reading existing\ndecision artifacts."),
            (preflight, "An absent decision store alone is nonblocking; material authority or\nconflicts follow the canonical contract."),
            (gate, "Applicable accepted outcome constraints and source links inform readiness and whether an owner question is material; they do not replace current bounded-source content or existing material-question authority."),
            (handoff, "Handoff context includes settled decisions, applicable accepted outcome\nconstraints and source links, trade-offs, intentional deferrals, uncertainties, and the\nnext-stage readiness target."),
            (handoff, "On resume in every mode, including preselection, re-establish\napplicability through read-only discovery and consultation of current project decision\nownership, the whole index and relevant accepted records under save-adr, not solely supplied\nconstraints/session history or an earlier-read claim."),
            (handoff, "Keep preselection read-only and absent\nstore alone nonblocking."),
        ):
            with self.subTest(clause=clause):
                self.assertIn(" ".join(clause.split()), " ".join(body.split()))
                self.assertNotIn(" ".join(clause.split()),
                                 " ".join(body.replace(clause, "OMITTED", 1).split()))


class AcceptedDecisionTaskAdapterTests(unittest.TestCase):
    """Bounded accepted-authority fixtures for source-to-task adapters, not live tasking."""

    def test_source_acceptance_reaches_task_gate_check_and_brief(self):
        records = (
            {"status": "accepted", "constraint": "preserve the export capability",
             "source": "decisions/export.md#accepted", "observable": "export remains available",
             "gate": "existing approved supersession"},
            {"status": "accepted", "constraint": "retain the stable wire format",
             "source": "decisions/wire.md#accepted", "observable": "wire payload remains stable",
             "gate": None},
            {"status": "proposed", "constraint": "replace the exporter",
             "source": "decisions/replacement.md#proposed"},
            {"status": "superseded", "constraint": "use the retired wire format",
             "source": "decisions/old-wire.md#superseded"},
        )
        accepted = tuple(record for record in records if record["status"] == "accepted")

        def adapt(adapter, context, source_record):
            # The fixture represents the required source observable → task mapping.
            source_acceptance = {key: source_record[key]
                                 for key in ("constraint", "source", "observable", "gate")}
            return {
                "adapter": adapter,
                "context": context,
                "requirements_truth": "TinySpec" if adapter == "direct" else "specification",
                "source_acceptance": source_acceptance,
                "dependency_or_gate": source_acceptance["gate"],
                "required_check": {"observable": source_acceptance["observable"],
                                   "constraint": source_acceptance["constraint"],
                                   "source": source_acceptance["source"]},
                "brief": (source_acceptance["constraint"], source_acceptance["source"]),
            }

        mappings = [adapt(adapter, context, record)
                    for adapter in ("direct", "SpecKit")
                    for context in ("fresh", "resumed")
                    for record in accepted]

        def assert_mapping(output):
            self.assertEqual(len(output), 8)
            for mapping in output:
                source = mapping["source_acceptance"]
                self.assertIn(mapping["adapter"], ("direct", "SpecKit"))
                self.assertIn(mapping["context"], ("fresh", "resumed"))
                self.assertEqual(mapping["requirements_truth"],
                                 "TinySpec" if mapping["adapter"] == "direct" else "specification")
                self.assertEqual(mapping["dependency_or_gate"], source["gate"])
                self.assertEqual(mapping["required_check"], {
                    "observable": source["observable"], "constraint": source["constraint"],
                    "source": source["source"],
                })
                self.assertEqual(mapping["brief"], (source["constraint"], source["source"]))

        assert_mapping(mappings)
        missing_check = copy.deepcopy(mappings)
        missing_check[0]["required_check"] = {}
        with self.assertRaises(AssertionError):
            assert_mapping(missing_check)

        # Current accepted authority wins: a task source that removes it must stop pending
        # its existing supersession gate; proposed/superseded records never become truth.
        conflict = adapt("direct", "resumed", accepted[0])
        conflict["required_check"]["observable"] = "export removed"

        def assert_source_truth(mapping):
            self.assertEqual(mapping["required_check"]["observable"],
                             mapping["source_acceptance"]["observable"])

        with self.assertRaises(AssertionError):
            assert_source_truth(conflict)
        self.assertEqual(conflict["dependency_or_gate"], "existing approved supersession")
        self.assertNotIn("replace the exporter", [m["brief"][0] for m in mappings])
        self.assertNotIn("use the retired wire format", [m["brief"][0] for m in mappings])

    def test_adapter_carriers_detect_removal(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        for label, key, selector, clauses in checker.ACCEPTED_ADAPTER_CARRIERS:
            for clause in clauses:
                with self.subTest(carrier=label, removed=clause):
                    changed = dict(texts)
                    body = checker.operational_carrier(changed[key], selector)
                    pattern = r"\s+".join(re.escape(word) for word in clause.split())
                    changed[key] = changed[key].replace(body, re.sub(pattern, "REMOVED", body), 1)
                    self.assertTrue(any(error.startswith(label + ":")
                                        for error in checker.check_contracts(changed)))


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


class MechanicalOwnershipTests(unittest.TestCase):
    """Trusted comparison examples plus carrier mutations; not model obedience."""
    def test_each_boundary_rejects_former_blanket_ban(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_workflow_ownership(texts), [])
        for key, selector in checker.MECHANICAL_CARRIERS:
            with self.subTest(carrier=key, boundary=selector):
                changed = dict(texts)
                body = checker.operational_carrier(texts[key], selector)
                changed[key] = changed[key].replace(body, body + "\nNo parent artifact edits\n", 1)
                self.assertTrue(any("former blanket ban" in e for e in checker.check_workflow_ownership(changed)))
                changed[key] = texts[key].replace(body, body.replace("bounded mechanical correction contract", "REMOVED"), 1)
                self.assertTrue(any("missing owner reference" in e for e in checker.check_workflow_ownership(changed)))

    def test_equivalence_guards_cannot_be_footer_rescued(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_workflow_ownership(texts), [])
        body = checker.section(texts["approval"], "## Bounded mechanical corrections")
        for guard in checker.MECHANICAL_GUARDS:
            with self.subTest(guard=guard):
                changed = dict(texts)
                changed["approval"] = texts["approval"].replace(body, re.sub(r"\s+".join(re.escape(w) for w in guard.split()), "REMOVED", body), 1)
                changed["approval"] += "\n## Footer\n" + guard
                self.assertTrue(any(e.startswith("mechanical-owner:") for e in checker.check_workflow_ownership(changed)))

    def test_named_equivalence_examples(self):
        # Authored comparison records: no NLP inference or live model simulation.
        import hashlib
        cases = json.loads((HERE / "fixtures/planner/mechanical-corrections.json").read_text())
        owner = checker.section(checker.load_texts()["approval"], "## Bounded mechanical corrections")
        aspects = ("requirements", "decisions", "scope", "dependencies", "acceptance", "approval validity")
        self.assertEqual(len(cases), 10)
        for case in cases:
            with self.subTest(case=case["name"]):
                self.assertNotEqual(case["before"], case["after"])
                comparison = case["comparison"]
                self.assertEqual(set(comparison["before"]), set(aspects))
                if case["route"] == "mechanical":
                    self.assertTrue(comparison["record"])
                    self.assertEqual(comparison["before"], comparison["after"])
                    self.assertEqual(case["currentDigest"], hashlib.sha256(case["after"].encode()).hexdigest())
                    self.assertIn("Record the equivalence comparison", owner)
                    self.assertIn("typos, formatting or broken links only", owner)
                else:
                    self.assertEqual(case["route"], "delegate-review-renew")
                    self.assertIn("Uncertain or substantive changes", owner)
                    self.assertIn("affected review and renewed approval", owner)
                    if case["name"] == "unproven-approval":
                        self.assertFalse(comparison["record"])
                        self.assertNotEqual(case["currentDigest"], hashlib.sha256(case["after"].encode()).hexdigest())
                        self.assertIn("If equivalence or approval validity cannot be established, direct repair is not permitted", owner)
                    else:
                        aspect = case["name"].removeprefix("disguised-")
                        self.assertNotEqual(comparison["before"][aspect], comparison["after"][aspect])
                        self.assertIn(aspect, owner)
        self.assertIn("A cosmetic label alone is insufficient", owner)
        self.assertIn("never silently reuse a stale digest", owner)


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
    def test_assessment_before_readiness_actual_consumer_inventory(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        for label, key, heading in checker.ROUTING_CARRIERS:
            body = checker.section(texts[key], heading)
            for clause in checker.ROUTING_SEQUENCE:
                with self.subTest(carrier=label, removed=clause):
                    changed = dict(texts)
                    pattern = r'\s+'.join(re.escape(w) for w in clause.split())
                    changed[key] = changed[key].replace(body, re.sub(pattern, 'REMOVED', body), 1)
                    # An owner/footer-only copy cannot rescue the actual operational consumer.
                    changed[key] += '\n## Footer\n' + clause
                    self.assertTrue(any(e.startswith(label + ': missing') for e in checker.check_contracts(changed)))
            for reversal in ('compare only verified alternatives', 'verify readiness before proposing',
                             'silently substitute Sol', 'always audit provider source before comparison'):
                with self.subTest(carrier=label, reversed=reversal):
                    changed = dict(texts)
                    changed[key] = changed[key].replace(body, body + '\n' + reversal + '\n', 1)
                    self.assertTrue(any(e.startswith(label + ': contradictory') for e in checker.check_contracts(changed)))

    def test_owner_comparison_and_graph_tradeoff_mutations(self):
        texts = checker.load_texts()
        self.assertEqual(checker.check_contracts(texts), [])
        for key, clause, label in (
            ("routing", "Family explains sufficient capability versus the named adequate alternative", "routing-comparison:"),
            ("routing", "pending readiness is not inadequacy", "routing-comparison:"),
            ("routing", "strict requirement versus a default preference", "routing-comparison:"),
            ("coordinator", "not effect proof or execution eligibility", "runtime-authority:"),
        ):
            with self.subTest(clause=clause):
                changed = dict(texts)
                changed[key] = changed[key].replace(clause, "REMOVED", 1)
                self.assertTrue(any(e.startswith(label) for e in checker.check_contracts(changed)))


class PlanningSeedPreservationTests(unittest.TestCase):
    """Planning-only safety from retired execution seed; no callable ranking oracle."""
    def test_preproposal_completeness_stays_in_planning_owner(self):
        text = (ROOT / checker.PATHS['routing']).read_text()
        body = ' '.join(checker.section(text, '## First proposal recipe').split())
        for clause in (
            'Before presenting the proposal, check completeness',
            'all six factors and the weakest adequate oracle',
            'each family in this rubric is considered or briefly accounted for',
            'family and effort have separate comparative rationales',
            'prior launch success is used only as readiness evidence',
            'ties remain explicit rather than becoming superiority claims',
            'Repair missing items before asking for profile approval',
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, body)


    def test_six_factors_family_effort_and_evidence_boundaries_survive_owner_move(self):
        text=(ROOT/checker.PATHS['routing']).read_text()
        for factor in ('Residual reasoning','Agentic/tool depth','Verification blind spots',
                       'Scope/coupling','Failure cost/reversibility','Applicable approved guidance'):
            self.assertIn(factor,checker.section(text,'## Assess all six factors'))
        body=checker.section(text,'## Provisional family and effort choices')
        rows=[line.split('|')[1].strip() for line in body.splitlines() if line.startswith('| ')]
        self.assertEqual(rows[2:6],['Luna','Sol','Astra','Terra'])
        for clause in ('Family rationale','Effort rationale','Luna/max','no universal ladder',
                       'family does not imply an effort','no fixed family-to-effort step follows',
                       'no family ranking follows','neither require equal proposal rows nor enumerate variants'):
            self.assertIn(clause,body)
            self.assertNotIn(clause,body.replace(clause,'REMOVED'))
        evidence=checker.section(text,'## Evidence limits')
        for clause in ('Unlike harnesses','no row supplies Pi probabilities','causal effort gains',
                       'Evidence absence/non-reliance is explicit'):
            self.assertIn(clause,evidence)
        self.assertIn('cannot bypass a manager-governed Standard rule',text)


class RuntimeHandoffTests(unittest.TestCase):
    def test_current_runtime_policy_replaces_historical_eligibility_not_historical_records(self):
        import hashlib
        source=(ROOT/'specs/003-coordinate-workflow/tasks.md').read_text()
        approved=source.split('## T008 exact operative amendment proposals',1)[1].split('Remaining constitution/task-commit safeguards',1)[0]
        self.assertEqual(hashlib.sha256(approved.encode()).hexdigest(),'a318e50bf8914fce910f62d9aedf8700e3b9a1bb0b804a08281e46b0423bdcea')
        constitution=(ROOT/'.specify/memory/constitution.md').read_text()
        checkpoint=(ROOT/'skills/memory-handling/references/task-commit-contract.md').read_text()
        for text in (constitution, checkpoint):
            for phrase in ('Six task-linter checks', 'focused verified owned-path',
                           'failed hooks/checks/signing', 'historical rows',
                           'no graph, cgroup, manifest, original-session, intent-settlement or evidence-receipt eligibility'):
                self.assertIn(phrase, text)
            self.assertNotIn('durable effect identity', text)
            self.assertNotIn('current Git state and durable receipt', text)

    def test_installed_adapter_template_is_sequential_and_hashes_honest(self):
        import hashlib,json
        for path,manifest in [('.pi/prompts/speckit.tasks.md','.specify/integrations/pi.manifest.json'),
                              ('.specify/templates/tasks-template.md','.specify/integrations/speckit.manifest.json')]:
            text=(ROOT/path).read_text()
            self.assertNotIn('parallelizable',text)
            self.assertNotIn('Tests are OPTIONAL',text)
            self.assertIn('task', text)
            metadata=json.loads((ROOT/manifest).read_text())
            actual=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
            self.assertEqual(metadata['files'][path],actual)
            self.assertEqual(metadata['local_overrides'][path]['current_sha256'],actual)
            self.assertNotEqual(metadata['local_overrides'][path]['upstream_sha256'],actual)

    def test_compact_task_adapter_has_no_phase_or_batch_execution_protocol(self):
        for path in ('.pi/prompts/speckit.tasks.md', '.specify/templates/tasks-template.md'):
            text = (ROOT / path).read_text()
            for retired in ('Sequential number', 'all phases, task IDs',
                            'Each user story (P1, P2, P3...) gets its own phase',
                            'Description with file path', 'Normally 4–7',
                            'contract test task [P] before implementation'):
                self.assertNotIn(retired, text, path)
            for required in ('authorized suite installation', 'independently necessary prerequisite',
                             'required', 'optional', 'JSON/YAML', 'required[].check'):
                self.assertIn(required, text, path)

    def test_task_producers_do_not_recreate_executor_eligibility_metadata(self):
        for path in ('skills/planner/SKILL.md', 'skills/tiny-spec/SKILL.md',
                     'skills/task-generation/SKILL.md', 'skills/delegating-architectural-planning/SKILL.md'):
            text=(ROOT/path).read_text()
            self.assertNotIn('Root `execution_intent`', text, path)
            self.assertNotIn('unresolved/incompatible intent blocks execution', text, path)
        self.assertEqual(checker.check_contracts(checker.load_texts()), [])


class CoordinateAcceptedDecisionBriefTests(unittest.TestCase):
    """Skill-local brief walkthroughs, not emitted engine-prompt proof."""

    def test_direct_fresh_and_resumed_worker_review_briefs_preserve_constraints(self):
        accepted = (
            ("preserve the export capability", "outcome", "decisions/export.md#accepted"),
            ("retain the stable wire format", "explicit mechanism", "decisions/wire.md#accepted"),
        )

        def brief(entry, context, role, packaging=True, storage=True):
            # Known caller-supplied constraints remain available when discovery packaging is not.
            return {
                "entry": entry,
                "context": context,
                "role": role,
                "constraints": accepted,
                "packaging": packaging,
                "storage": storage,
            }

        walkthroughs = [brief("direct", context, role, packaging, storage)
                        for context in ("fresh", "resumed")
                        for role in ("worker", "review")
                        for packaging, storage in ((True, True), (False, False))]
        self.assertEqual(len(walkthroughs), 8)
        for item in walkthroughs:
            with self.subTest(item=item):
                self.assertEqual(item["entry"], "direct")
                self.assertIn(item["context"], ("fresh", "resumed"))
                self.assertIn(item["role"], ("worker", "review"))
                self.assertEqual(item["constraints"], accepted)
        self.assertFalse(walkthroughs[-1]["packaging"])
        self.assertFalse(walkthroughs[-1]["storage"])

    def test_skill_requires_consultation_and_worker_review_propagation(self):
        source = (ROOT / "skills/coordinate-implementation/SKILL.md").read_text()
        carriers = (
            ("## Load and Verify", "consult\n[save-adr](../save-adr/SKILL.md)'s **Consult and propagate** contract",
             "Known supplied constraints survive unavailable\ncontract packaging; absent decision storage alone does not block unrelated work."),
            ("## Recover Context", "re-establish applicable accepted-decision authority",
             "outcomes, explicit mechanism\nconstraints and source links in the resumed worker and review briefs"),
            ("## Execute and Integrate", "task brief carries applicable accepted outcomes, explicit mechanism constraints and source links",),
            ("## Review and Acceptance", "review scope carries applicable accepted outcomes, explicit mechanism\nconstraints and source links",),
        )

        def assert_carriers(text):
            for heading, *clauses in carriers:
                body = checker.section(text, heading)
                for clause in clauses:
                    self.assertIn(" ".join(clause.split()), " ".join(body.split()))

        assert_carriers(source)
        for heading, *clauses in carriers:
            for clause in clauses:
                with self.subTest(heading=heading, clause=clause):
                    changed = source.replace(clause, "OMITTED", 1)
                    with self.assertRaises(AssertionError):
                        assert_carriers(changed)


class ReviewAcceptedDecisionScopeTests(unittest.TestCase):
    """Paired request/reviewer scope walkthroughs, not a live review."""

    def test_direct_fresh_and_resumed_review_scope_compares_actual_changes(self):
        records = (
            {"status": "accepted", "constraint": "preserve the export capability",
             "source": "decisions/export.md#accepted", "outcome": "export capability"},
            {"status": "accepted", "constraint": "retain the stable wire format",
             "source": "decisions/wire.md#accepted", "mechanism": "stable wire helper"},
            {"status": "proposed", "constraint": "replace the exporter",
             "source": "decisions/replacement.md#proposed"},
            {"status": "superseded", "constraint": "use the retired wire format",
             "source": "decisions/old-wire.md#superseded"},
        )
        accepted = tuple(record for record in records if record["status"] == "accepted")

        def request(context, authority=accepted):
            return {
                "entry": "direct",
                "context": context,
                "requirements": tuple((record["constraint"], record["source"])
                                      for record in authority),
            }

        def reviewer_verdict(scope, actual_diff, authority=accepted):
            self.assertEqual(scope["requirements"], tuple(
                (record["constraint"], record["source"]) for record in authority))
            if authority != accepted:
                return "owner decision for conflicting accepted authority"
            active = tuple(record for record in records if record["status"] == "accepted")
            if any(record.get("outcome") and record["outcome"] in actual_diff for record in active):
                return "stop for existing approved supersession"
            if any(record.get("mechanism") and record["mechanism"] in actual_diff for record in active):
                return "stop for existing approved supersession"
            return "ready"

        scopes = [request(context) for context in ("fresh", "resumed")]
        for scope in scopes:
            with self.subTest(context=scope["context"], change="capability removal"):
                self.assertEqual(reviewer_verdict(scope, "- export capability"),
                                 "stop for existing approved supersession")
            with self.subTest(context=scope["context"], change="helper deletion"):
                self.assertEqual(reviewer_verdict(scope, "- unused internal helper"), "ready")
            with self.subTest(context=scope["context"], change="explicit mechanism removal"):
                self.assertEqual(reviewer_verdict(scope, "- stable wire helper"),
                                 "stop for existing approved supersession")
            with self.subTest(context=scope["context"], change="proposed/superseded records"):
                self.assertEqual(reviewer_verdict(scope, "- replacement exporter - retired wire format"),
                                 "ready")

        conflicting = accepted + ({"status": "accepted", "constraint": "remove the export capability",
                                   "source": "decisions/conflict.md#accepted"},)
        self.assertEqual(reviewer_verdict(request("resumed", conflicting), "- export capability", conflicting),
                         "owner decision for conflicting accepted authority")

    def test_request_and_reviewer_carriers_each_detect_removal(self):
        request = (ROOT / "skills/requesting-code-review/SKILL.md").read_text()
        reviewer = (ROOT / "skills/requesting-code-review/code-reviewer.md").read_text()
        carriers = (
            (request, "## Prepare The Review", (
                "consult [save-adr](../save-adr/SKILL.md)'s **Consult and propagate** contract",
                "fresh or resumed contexts",
                "rather than parent context or a prior-read claim",
                "accepted outcome, explicit mechanism constraint, and source link",
                "proposed and superseded records are not current policy",
            )),
            (reviewer, "## Review Focus", (
                "consult [save-adr](../save-adr/SKILL.md)'s **Consult and propagate** contract",
                "fresh or resumed contexts",
                "do not rely on parent context or a prior-read claim",
                "Compare the actual diff, including deletion or simplification",
                "explicitly accepted mechanism",
                "compatible helper deletion that preserves the outcome needs no new gate",
                "Contradictory accepted authority or uncertain current supersession stops only the affected verdict",
            )),
        )

        def assert_carriers(texts):
            for text, heading, clauses in texts:
                body = checker.section(text, heading)
                for clause in clauses:
                    self.assertIn(" ".join(clause.split()), " ".join(body.split()))

        assert_carriers(carriers)
        for index, (text, heading, clauses) in enumerate(carriers):
            for clause in clauses:
                with self.subTest(half=heading, clause=clause):
                    changed = list(carriers)
                    body = checker.section(text, heading)
                    pattern = r"\s+".join(re.escape(word) for word in clause.split())
                    changed[index] = (text.replace(body, re.sub(pattern, "OMITTED", body, count=1), 1),
                                      heading, clauses)
                    with self.assertRaises(AssertionError):
                        assert_carriers(changed)


if __name__ == "__main__":
    unittest.main()
