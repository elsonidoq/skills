"""Public minimization must expose identities, never private row content."""
import json
import unittest

from workflow_monitor.mapping import normalize
from workflow_monitor.public import minimize
from workflow_monitor.tests.test_mapping import snapshot


class PublicTests(unittest.TestCase):
    def test_refs_are_run_scoped_and_facts_remain_typed(self):
        source = snapshot()
        source["observations"][0]["facts"] = '{"role":"worker","private":"PRIVATE-SENTINEL"}'
        result = minimize(normalize(source))
        self.assertEqual(result["inventory"]["observation_count"], 5)
        self.assertEqual(result["records"][0]["exit_code"], None)
        self.assertFalse(result["records"][0]["no_change"])
        self.assertNotEqual(result["occurrences"][0]["ref"], result["occurrences"][-1]["ref"])
        self.assertEqual([run["display_id"] for run in result["runs"]], ["run-a", "run-b"])
        self.assertNotIn("PRIVATE-SENTINEL", repr(result))
        self.assertEqual(result["unknown_records"][0]["code"], "unsupported_observation")

    def test_planned_topology_is_run_scoped_and_review_is_not_an_execution(self):
        source = snapshot()
        for row in source["runs"]:
            description = json.loads(row["description"])
            description["tasks"] = [{"id": "T001", "depends": [], "label": "One", "summary": "First"},
                                    {"id": "T002", "depends": ["T001"], "label": "Two", "summary": "Second"},
                                    {"id": "T003", "depends": [], "label": "Three", "summary": "Pending"}]
            row["description"] = json.dumps(description)
        result = minimize(normalize(source))
        by_run = {}
        for task in result["tasks"]:
            by_run.setdefault(task["run_ref"], []).append(task)
        self.assertEqual({len(tasks) for tasks in by_run.values()}, {3})
        self.assertNotEqual(by_run[result["runs"][0]["ref"]][0]["ref"], by_run[result["runs"][1]["ref"]][0]["ref"])
        dependent = next(task for task in result["tasks"] if task["run_ref"] == result["runs"][0]["ref"] and task["label"] == "Two")
        prerequisite = next(task for task in result["tasks"] if task["run_ref"] == dependent["run_ref"] and task["label"] == "One")
        self.assertEqual(dependent["prerequisite_refs"], [prerequisite["ref"]])
        self.assertEqual({run["plan_availability"] for run in result["runs"]}, {"complete"})
        self.assertEqual(len(result["review_definitions"]), 2)
        self.assertTrue(all(item["label"] == "Planned independent review — not an agent call." for item in result["review_definitions"]))
        self.assertNotIn(result["review_definitions"][0]["ref"], {item["ref"] for item in result["occurrences"]})

    def test_zero_null_no_change_and_questions_stay_distinct(self):
        source = snapshot()
        source["observations"].append({"seq": 8, "run_id": "run-b", "occurrence_id": "check", "phase": "check", "task_id": None,
                                       "kind": "passed", "recorded_at": 9, "facts": '{"ordinal":0,"exit_code":0}'})
        source["observations"].append({"seq": 9, "run_id": "run-b", "occurrence_id": "checkpoint", "phase": "checkpoint", "task_id": None,
                                       "kind": "passed", "recorded_at": 10, "facts": '{"no_change":false}'})
        result = minimize(normalize(source))
        check = next(row for row in result["records"] if row["ordinal"] == 0)
        checkpoint = next(row for row in result["records"] if row["no_change"] is False)
        self.assertEqual((check["exit_code"], check["no_change"]), (0, None))
        self.assertEqual((checkpoint["exit_code"], checkpoint["no_change"]), (None, False))
        self.assertEqual([row["kind"] for row in result["records"] if row["kind"].startswith("question") or row["kind"] == "answer_sent"], ["question_requested", "answer_sent"])


if __name__ == "__main__":
    unittest.main()
