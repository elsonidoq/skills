"""Mapper tests use local T006-compatible Store records; no provider is invoked."""
import json
import sys
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))

from coherence_workflow.monitoring import Recorder, descriptor
from coherence_workflow.store import Authority, git
from workflow_monitor.mapping import normalize
from workflow_monitor.public import minimize
from workflow_monitor.reader import Reader

BASE = "a" * 40


def snapshot():
    description = descriptor({"tasks": [{"id": "one", "depends": [], "outcome": "Complete the full retained work text. " * 12},
                                         {"id": "two", "depends": ["one"], "description": "Second work"}],
                              "monitor": {"tasks": {"one": {"label": "One"}}}},
                             {"provider": "offline", "model": "fixture", "effort": "medium"}, BASE)
    import json
    return {"state": "ok", "runs": [{"run_id": "run-a", "description": json.dumps(description), "started_at": 1},
                                         {"run_id": "run-b", "description": json.dumps(description), "started_at": 2}],
            "observations": [
                {"seq": 1, "run_id": "run-a", "occurrence_id": "worker-1", "phase": "worker", "task_id": "one", "kind": "started", "recorded_at": 2, "facts": '{"role":"worker"}'},
                {"seq": 2, "run_id": "run-a", "occurrence_id": "worker-1", "phase": "worker", "task_id": "one", "kind": "failed", "recorded_at": 3, "facts": '{"role":"worker"}'},
                {"seq": 3, "run_id": "run-a", "occurrence_id": "worker-2", "phase": "worker", "task_id": "one", "kind": "passed", "recorded_at": 4, "facts": '{"role":"worker"}'},
                {"seq": 4, "run_id": "run-a", "occurrence_id": "review", "phase": "review", "task_id": None, "kind": "passed", "recorded_at": 5, "facts": '{"role":"reviewer","review_base":"' + BASE + '","review_head":"' + BASE + '","approved":true,"finding_count":0}'},
                {"seq": 5, "run_id": "run-a", "occurrence_id": "unknown", "phase": "worker", "task_id": None, "kind": "future", "recorded_at": 6, "facts": '{}'},
                {"seq": 6, "run_id": "run-b", "occurrence_id": "question", "phase": "worker", "task_id": None, "kind": "question_requested", "recorded_at": 7, "facts": '{"parent_occurrence_id":"parent","role":"worker"}'},
                {"seq": 7, "run_id": "run-b", "occurrence_id": "question", "phase": "worker", "task_id": None, "kind": "answer_sent", "recorded_at": 8, "facts": '{"parent_occurrence_id":"parent","role":"worker"}'},
            ]}


class MappingTests(unittest.TestCase):
    def test_complete_anchors_occurrences_observations_and_typed_edges(self):
        graph = normalize(snapshot())
        self.assertEqual(len(graph["phases"]), 16)
        self.assertEqual(len(graph["occurrences"]), 4)
        self.assertEqual([row["seq"] for row in graph["observations"]], [1, 2, 3, 4, 6, 7])
        self.assertEqual(graph["tasks"][0]["work_description"], "Complete the full retained work text. " * 12)
        self.assertEqual(graph["tasks"][1]["work_description"], "Second work")
        self.assertEqual(graph["unknown_records"], [{"run_id": "run-a", "seq": 5, "code": "unsupported_observation"}])
        kinds = {edge["type"] for edge in graph["edges"]}
        self.assertTrue({"possible_flow", "task_prerequisite", "recorded_next", "phase_occurrence", "execution_milestone", "reviewed_range"} <= kinds)
        failures = [row for row in graph["occurrences"] if row["occurrence_id"] == "worker-1"]
        self.assertEqual(failures[0]["observations"][-1]["kind"], "failed")

    def test_actual_emitted_store_rows_flow_through_reader_and_mapper(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            git(project, "init", "-q")
            git(project, "config", "user.name", "Fixture")
            git(project, "config", "user.email", "fixture@example.invalid")
            (project / "tracked").write_text("fixture\n")
            git(project, "add", "tracked")
            git(project, "commit", "-qm", "fixture")
            base = git(project, "rev-parse", "HEAD").decode().strip()
            work = "Complete this full work description without truncation. " * 12
            with Authority(project) as owner:
                owner.store.start("emitted", base)
                recorder = Recorder(owner.store, "emitted")
                recorder.register(descriptor({"tasks": [{"id": "one", "depends": [], "outcome": work},
                                                        {"id": "two", "depends": ["one"], "description": "Second task"}]}, {}))
                occurrence = recorder.occurrence()
                facts = {"role": "worker", "invocation_id": "invocation", "invocation_kind": "task_worker",
                         "selected_input_checkpoints": [], "correction_chain": ["invocation"]}
                recorder.emit(occurrence, "worker", "started", task_id="one", facts=facts)
                recorder.emit(occurrence, "worker", "failed", task_id="one", facts={**facts, "stopped_by_invocation_id": "invocation"})
            graph = normalize(Reader(project).open_snapshot("emitted"))
        self.assertEqual([(item["occurrence_id"], item["incomplete"]) for item in graph["occurrences"]], [(occurrence, False)])
        self.assertEqual([item["kind"] for item in graph["observations"]], ["started", "failed"])
        public = minimize(graph)
        self.assertEqual([task["work_description"] for task in public["tasks"]], [work, "Second task"])
        self.assertEqual(public["tasks"][1]["prerequisite_refs"], [public["tasks"][0]["ref"]])
        self.assertEqual(len(public["review_definitions"]), 1)

    def test_unavailable_is_not_decoded_as_an_empty_graph(self):
        self.assertEqual(normalize({"state": "unsupported"})["state"], "unsupported")
        self.assertEqual(normalize({"state": "ok", "runs": [], "observations": []})["occurrences"], [])

    def test_missing_work_or_review_intent_remains_unknown_without_reconstruction(self):
        source = snapshot()
        description = json.loads(source["runs"][0]["description"])
        description["tasks"][0]["work_description"] = None
        description.pop("initial_review")
        source["runs"][0]["description"] = json.dumps(description)
        graph = normalize(source)
        self.assertTrue(graph["runs"][0]["plan_available"])
        self.assertIsNone(graph["tasks"][0]["work_description"])

    def test_invalid_or_empty_descriptor_retains_supported_history_without_topology(self):
        valid = json.loads(snapshot()["runs"][0]["description"])
        invalids = [None, "{"]
        for change in ({"tasks": valid["tasks"] + [{"id": None, "depends": []}]}, {"tasks": []}, {"tasks": [{"id": "one", "depends": ["missing"]}]}):
            description = dict(valid)
            description.update(change)
            invalids.append(json.dumps(description))
        source = {"state": "ok", "runs": [{"run_id": f"run-{index}", "description": description}
                                                   for index, description in enumerate(invalids)],
                  "observations": [{"seq": index, "run_id": f"run-{index}", "occurrence_id": "worker",
                                    "phase": "worker", "task_id": "one", "kind": "returned", "facts": '{"role":"worker"}'}
                                   for index in range(len(invalids))]}
        graph = normalize(source)
        self.assertEqual(graph["tasks"], [])
        self.assertNotIn("task_prerequisite", {edge["type"] for edge in graph["edges"]})
        self.assertEqual([row["plan_available"] for row in graph["runs"]], [False] * len(invalids))
        self.assertEqual(len(graph["observations"]), len(invalids))
        self.assertEqual(len(graph["occurrences"]), len(invalids))


if __name__ == "__main__":
    unittest.main()
