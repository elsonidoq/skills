"""Typed DTOs expose recorded workflow content, not arbitrary payloads."""
import json
import unittest

from workflow_monitor.mapping import normalize
from workflow_monitor.public import _display_text, minimize
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

    def test_run_labels_use_safe_original_identifiers(self):
        generated = "1234567890abcdef1234567890abcdef"
        graph = {"state": "ok", "runs": [{"run_id": value} for value in
                 ("review-convergence-20261024", generated, "/private/path", "", "bad\nname")]}
        runs = minimize(graph)["runs"]
        self.assertEqual([run["label"] for run in runs],
                         ["review-convergence-20261024", generated, None, None, None])
        self.assertEqual([run["display_id"] for run in runs], [row["run_id"] for row in graph["runs"]])
        self.assertTrue(all(run["worktree_name"] is None for run in runs))
        self.assertIsNone(_display_text(None))
        self.assertIsNone(_display_text("  "))
        self.assertIsNone(_display_text("bad\\name"))
        self.assertEqual(_display_text("folder with spaces"), "folder with spaces")

    def test_recorded_prose_and_identities_are_not_hidden_by_presentation_limits(self):
        source = snapshot()
        description = json.loads(source['runs'][0]['description'])
        prose = '<img src=x onerror=alert(1)> Workflow explanation ' * 30
        description['tasks'][0].update(label=prose, work_description=prose)
        source['runs'][0]['description'] = json.dumps(description)
        result = minimize(normalize(source))
        self.assertEqual(result['tasks'][0]['label'], prose)
        self.assertEqual(result['tasks'][0]['work_description'], prose)
        self.assertEqual(result['tasks'][0]['task_id'], 'one')
        self.assertEqual(result['occurrences'][0]['occurrence_id'], 'worker-1')
        self.assertEqual(result['phases'][0]['phase_id'], 'intake')
        # Unknown payload/credential fields remain outside the recording DTO contract.
        source['observations'][0]['facts'] = json.dumps({'role': 'worker', 'api_key': 'synthetic-credential'})
        protected = minimize(normalize(source))
        self.assertNotIn('synthetic-credential', json.dumps(protected))
        self.assertEqual(protected['unknown_records'][0]['code'], 'unsupported_observation')

    def test_planned_topology_is_run_scoped_and_review_is_not_an_execution(self):
        source = snapshot()
        for row in source["runs"]:
            description = json.loads(row["description"])
            description["tasks"] = [{"id": "T001", "depends": [], "label": "One", "work_description": "First"},
                                    {"id": "T002", "depends": ["T001"], "label": "Two", "work_description": "Second"},
                                    {"id": "T003", "depends": [], "label": "Three", "work_description": None}]
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
        self.assertEqual(result["review_definitions"][0]["prerequisite_refs"], [item["ref"] for item in by_run[result["runs"][0]["ref"]]])
        self.assertNotIn(result["review_definitions"][0]["ref"], {item["ref"] for item in result["occurrences"]})
        # Generic review phase vocabulary is not explicit review-plan intent.
        description = json.loads(source["runs"][0]["description"])
        description.pop("initial_review")
        source["runs"][0]["description"] = json.dumps(description)
        unknown_intent = minimize(normalize(source))
        self.assertEqual(len(unknown_intent["review_definitions"]), 1)
        self.assertIsNone(next(task for task in unknown_intent["tasks"] if task["run_ref"] == unknown_intent["runs"][0]["ref"] and task["task_id"] == "T003")["work_description"])

    def test_metric_expansion_is_typed_and_drops_private_nested_payloads(self):
        private = '/private/SESSION-CREDENTIAL-SENTINEL'
        metric = {'invocation_id': 'call-one', 'interval': {
            'session_id': private, 'branch': private, 'epoch': 'epoch-one',
            'tokens': {'input': {'value': 0}, 'output': {'value': True},
                       'cache_read': {'value': float('inf')}, 'cache_write': {'value': -1}},
            'compactions': {'count': True, 'entry_ids': ['entry-one', private]},
            'summary_overhead': {'included_in_sdk_deltas': True, 'entries': [
                {'entry_id': 'entry-one', 'usage': {'reasoning': 0, 'cacheWrite1h': False,
                 'prompt': private, 'cost': {'total': float('nan'), 'api_key': private}}}]}},
            'before': {'counters': {'input': True, 'total': 0}, 'context': {'occupancy': -1},
                       'compaction_entry_ids': [private], 'private': private},
            'after': None, 'actual_session_id': private, 'session_selection_reason': private,
            'private': private}
        graph = {'state': 'ok', 'activities': [{'run_id': 'run-one', 'invocation_id': 'call-one',
                 'occurrence_id': 'occ-one', 'role': 'worker', 'metric': metric,
                 'metric_coverage': 'partial', 'metric_reasons': ['missing_expected_invocations']}]}
        result = minimize(graph)
        projected = result['activities'][0]['metrics']
        self.assertEqual(projected['tokens']['input']['value'], 0)
        for key in ('output', 'cache_read', 'cache_write'):
            self.assertIsNone(projected['tokens'][key]['value'])
            self.assertEqual(projected['tokens'][key]['availability'], 'unknown')
        self.assertIsNone(projected['before']['counters']['input']['value'])
        self.assertEqual(projected['before']['counters']['total']['value'], 0)
        self.assertIsNone(projected['before']['context']['effective_headroom']['value'])
        self.assertEqual(projected['after']['availability'], 'unknown')
        self.assertIsNone(projected['after']['context']['compaction_applicable']['value'])
        self.assertIsNone(projected['compactions']['count']['value'])
        self.assertEqual(projected['compactions']['entry_ids'], ['entry-one'])
        usage = projected['summary_overhead']['entries'][0]['usage']
        self.assertEqual(usage['reasoning']['value'], 0)
        self.assertIsNone(usage['cacheWrite1h']['value'])
        self.assertIsNone(usage['cost']['total']['value'])
        self.assertNotIn(private, json.dumps(result, allow_nan=False))

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
