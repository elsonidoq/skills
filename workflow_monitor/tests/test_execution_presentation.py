"""Offline recording fixtures exercise closed HTTP execution presentation, not a provider."""
import json
import unittest
from unittest.mock import patch

from workflow_monitor.tests import test_http
from workflow_monitor.tests.test_mapping import snapshot


class ExecutionPresentationTests(unittest.TestCase):
    setUp = test_http.HttpTests.setUp

    def view(self, rows, tasks=None):
        raw = snapshot()
        if tasks is not None:
            description = json.loads(raw["runs"][0]["description"])
            description["tasks"] = tasks
            raw["runs"][0]["description"] = json.dumps(description)
        raw["observations"] = [dict(seq=index, run_id=run, occurrence_id=occ, phase=phase,
                                    task_id=task, kind=kind, recorded_at=index, facts=json.dumps(facts))
                               for index, (run, occ, phase, task, kind, facts) in enumerate(rows, 1)]
        self.reader.value = raw
        runs = self.client.get('/api/monitor/v1/runs', headers=self.api_headers).json()['runs']
        return [self.client.get(f"/api/monitor/v1/runs/{run['ref']}/snapshot", headers=self.api_headers).json() for run in runs]

    def test_stopping_check_is_specific_scoped_and_attached_to_preceding_task_agent(self):
        rows = [
            ('run-a', 'terminal', 'terminal', None, 'started', {}),
            ('run-a', 'prepare', 'prepare', 'one', 'started', {}),
            ('run-a', 'worker', 'worker', 'one', 'started', {'role': 'worker'}),
            ('run-b', 'other-worker', 'worker', 'one', 'started', {'role': 'worker'}),
            ('run-a', 'worker', 'worker', 'one', 'returned', {'role': 'worker'}),
            ('run-a', 'check', 'check', 'one', 'started', {'ordinal': 1}),
            ('run-a', 'check', 'check', 'one', 'failed', {'ordinal': 1, 'exit_code': 1}),
            ('run-a', 'prepare', 'prepare', 'one', 'failed', {'error_category': 'check'}),
            ('run-a', 'terminal', 'terminal', None, 'failed', {}),
        ]
        first, second = self.view(rows)
        stopping = [item for item in first['occurrences'] if item['stopping']]
        self.assertEqual([item['phase'] for item in stopping], ['check'])
        worker = next(item for item in first['occurrences'] if item['role'] == 'worker')
        self.assertEqual(stopping[0]['support_ref'], worker['ref'])
        self.assertNotEqual(stopping[0]['support_ref'], second['occurrences'][0]['ref'])
        self.assertIsNone(worker['outcome'])  # legacy outcome remains acceptance-neutral
        self.assertEqual(worker['execution_summary']['state'], 'success')
        self.assertNotIn('parent_occurrence_id', json.dumps(first))

    def test_pre_agent_stop_has_no_invented_parent(self):
        first, _ = self.view([
            ('run-a', 'terminal', 'terminal', None, 'started', {}),
            ('run-a', 'prepare', 'prepare', 'one', 'started', {}),
            ('run-a', 'prepare', 'prepare', 'one', 'failed', {}),
            ('run-a', 'terminal', 'terminal', None, 'failed', {}),
        ])
        stopping = [item for item in first['occurrences'] if item['stopping']]
        self.assertEqual(len(stopping), 1)
        self.assertEqual(stopping[0]['phase'], 'prepare')
        self.assertIsNone(stopping[0]['support_ref'])

    def test_recovered_failure_stays_in_details_not_as_a_stopping_node(self):
        first, _ = self.view([
            ('run-a', 'terminal', 'terminal', None, 'started', {}),
            ('run-a', 'worker', 'worker', 'one', 'started', {'role': 'worker'}),
            ('run-a', 'worker', 'worker', 'one', 'returned', {'role': 'worker'}),
            ('run-a', 'bad-check', 'check', 'one', 'failed', {'exit_code': 1}),
            ('run-a', 'good-check', 'check', 'one', 'passed', {'exit_code': 0}),
            ('run-a', 'terminal', 'terminal', None, 'passed', {}),
        ])
        self.assertFalse(any(item['stopping'] for item in first['occurrences']))
        failed = next(item for item in first['occurrences'] if item['outcome'] == 'failed')
        worker = next(item for item in first['occurrences'] if item['role'] == 'worker')
        self.assertEqual(failed['support_ref'], worker['ref'])
        self.assertTrue(any(item['kind'] == 'failed' for item in first['records']))

    def test_question_parent_is_opaque_and_scoped(self):
        first, _ = self.view([
            ('run-a', 'PRIVATE-SENTINEL', 'worker', 'one', 'started', {'role': 'worker'}),
            ('run-a', 'question', 'worker', 'one', 'question_requested', {'parent_occurrence_id': 'PRIVATE-SENTINEL'}),
        ])
        worker, question = first['occurrences']
        self.assertEqual(question['parent_ref'], worker['ref'])
        self.assertNotIn('PRIVATE-SENTINEL', json.dumps(first))

    def test_execution_and_acceptance_are_separate_full_snapshot_facts(self):
        base = 'a' * 40
        first, _ = self.view([
            ('run-a', 'worker-ok', 'worker', 'one', 'started', {'role': 'worker'}),
            ('run-a', 'worker-ok', 'worker', 'one', 'returned', {'role': 'worker'}),
            ('run-a', 'check', 'check', 'one', 'failed', {'ordinal': 1, 'exit_code': 1}),
            ('run-a', 'worker-bad', 'worker', 'two', 'started', {'role': 'worker'}),
            ('run-a', 'worker-bad', 'worker', 'two', 'failed', {'role': 'worker'}),
            ('run-a', 'review', 'review', None, 'started', {'role': 'reviewer', 'review_base': base, 'review_head': base}),
            ('run-a', 'review', 'review', None, 'failed', {'role': 'reviewer', 'review_base': base, 'review_head': base,
                                                            'approved': False, 'finding_count': 2}),
        ])
        agents = [item for item in first['occurrences'] if item['role'] == 'worker']
        self.assertEqual(sorted(item['execution_summary']['state'] for item in agents), ['failure', 'success'])
        reviewer = next(item for item in first['occurrences'] if item['role'] == 'reviewer')
        self.assertEqual(reviewer['execution_summary']['state'], 'success')
        malformed, _ = self.view([
            ('run-a', 'review', 'review', None, 'started', {'role': 'reviewer', 'review_base': base, 'review_head': base}),
            ('run-a', 'review', 'review', None, 'failed', {'role': 'reviewer', 'review_base': base, 'review_head': base}),
        ])
        self.assertEqual(next(item for item in malformed['occurrences'] if item['role'] == 'reviewer')['execution_summary']['state'], 'failure')
        acceptance = first['runs'][0]['acceptance_summary']
        self.assertEqual(acceptance['checks'][0]['state'], 'failed')
        self.assertEqual((acceptance['reviews'][0]['approved'], acceptance['reviews'][0]['finding_count']), (False, 2))
        self.assertNotIn('PRIVATE-SENTINEL', json.dumps(first))

    def test_waiting_terminal_and_runner_qualification_are_distinct(self):
        rows = [
            ('run-a', 'live', 'worker', 'one', 'started', {'role': 'worker'}),
            ('run-a', 'waiting', 'worker', 'two', 'started', {'role': 'worker'}),
            ('run-a', 'question', 'worker', 'two', 'question_requested', {'parent_occurrence_id': 'waiting'}),
            ('run-a', 'done', 'worker', 'one', 'started', {'role': 'worker'}),
            ('run-a', 'done', 'worker', 'one', 'returned', {'role': 'worker'}),
            ('run-a', 'late-question', 'worker', 'one', 'question_requested', {'parent_occurrence_id': 'done'}),
        ]
        for runner_state, expected in (('live', 'running'), ('stopped', 'unknown'), ('unknown', 'unknown')):
            with self.subTest(runner_state=runner_state), patch('workflow_monitor.app.qualify', return_value={'state': runner_state, 'reason': None}):
                first, _ = self.view(rows)
            states = [item['execution_summary']['state'] for item in first['occurrences'] if item['role'] == 'worker']
            self.assertEqual(states.count(expected), 1)
            self.assertIn('success', states)  # terminal return beats its stale question
            self.assertIn('waiting', states)

    def test_task_progress_is_pre_page_checkpoint_based_and_dependency_scoped(self):
        tasks = [{"id": "one", "depends": []}, {"id": "two", "depends": ["one"]}, {"id": "three", "depends": []}]
        rows = [("run-a", f"noise-{number}", "check", "one", "started", {"ordinal": number}) for number in range(50)]
        rows.extend([
            ("run-a", "one", "worker", "one", "started", {"role": "worker"}),
            ("run-a", "one", "worker", "one", "returned", {"role": "worker"}),
            ("run-a", "checkpoint", "checkpoint", "one", "started", {}),
            ("run-a", "checkpoint", "checkpoint", "one", "passed", {}),
            ("run-a", "two", "worker", "two", "started", {"role": "worker"}),
            ("run-a", "two", "worker", "two", "failed", {"role": "worker"}),
            ("run-a", "review", "review", None, "failed", {"role": "reviewer", "approved": False, "finding_count": 1}),
            ("run-a", "terminal", "terminal", None, "failed", {}),
        ])
        first, _ = self.view(rows, tasks)
        run = first["runs"][0]["ref"]
        page = self.client.get(f"/api/monitor/v1/runs/{run}/snapshot", headers=self.api_headers).json()
        full = self.client.get(f"/api/monitor/v1/runs/{run}/history?snapshot={page['snapshot_ref']}&cursor={page['next_cursor']}", headers=self.api_headers).json()
        one, two, three = first["tasks"]
        self.assertEqual(one["progress"], {"state": "completed", "qualification": None})
        self.assertEqual(two["progress"], {"state": "failed", "qualification": None})
        self.assertEqual(next(item for item in first["occurrences"] if item["ref"] == one["reason"]["occurrence_ref"])["phase"], "checkpoint")
        self.assertEqual(three["annotation"], {"code": "not_started_run_stopped", "label": "Not started; run stopped"})
        self.assertEqual([(item["ref"], item["progress"], item["reason"]) for item in first["tasks"]],
                         [(item["ref"], item["progress"], item["reason"]) for item in full["tasks"]])
        self.assertNotIn("skipped", json.dumps(first)); self.assertNotIn("cancelled", json.dumps(first))

    def test_failed_prerequisite_blocks_only_its_declared_dependent(self):
        tasks = [{"id": "one", "depends": []}, {"id": "two", "depends": ["one"]}, {"id": "three", "depends": []}]
        first, _ = self.view([
            ("run-a", "one", "worker", "one", "started", {"role": "worker"}),
            ("run-a", "one", "worker", "one", "failed", {"role": "worker"}),
            ("run-a", "terminal", "terminal", None, "failed", {}),
        ], tasks)
        one, two, three = first["tasks"]
        self.assertEqual(one["progress"]["state"], "failed")
        self.assertEqual(two["progress"], {"state": "blocked", "qualification": None})
        self.assertEqual(two["reason"], {"code": "prerequisite_failed", "task_ref": one["ref"]})
        self.assertEqual(three["progress"], {"state": "pending", "qualification": None})
        self.assertEqual(three["annotation"], {"code": "not_started_run_stopped", "label": "Not started; run stopped"})

    def test_return_without_checkpoint_is_not_completed_and_waiting_is_an_annotation(self):
        tasks = [{"id": "one", "depends": []}, {"id": "two", "depends": ["one"]}, {"id": "three", "depends": []}]
        first, _ = self.view([
            ("run-a", "one", "worker", "one", "started", {"role": "worker"}),
            ("run-a", "one", "worker", "one", "returned", {"role": "worker"}),
            ("run-a", "three", "worker", "three", "started", {"role": "worker"}),
            ("run-a", "question", "worker", "three", "question_requested", {"parent_occurrence_id": "three"}),
        ], tasks)
        one, dependent, waiting = first["tasks"]
        self.assertEqual(one["progress"], {"state": "unknown", "qualification": "completion_unrecorded"})
        self.assertEqual(dependent["progress"]["state"], "blocked")
        self.assertEqual(waiting["annotation"]["code"], "waiting_for_input")

    def test_incomplete_history_is_qualified_and_unavailable_plan_has_no_progress(self):
        with patch('workflow_monitor.app.qualify', return_value={'state': 'stopped', 'reason': None}):
            first, _ = self.view([('run-a', 'one', 'worker', 'one', 'started', {'role': 'worker'})])
        self.assertEqual(first['tasks'][0]['progress'], {'state': 'unknown', 'qualification': 'incomplete_history'})
        raw = snapshot()
        raw['runs'] = [raw['runs'][0]]
        raw['runs'][0]['description'] = 'malformed'
        raw['observations'] = [dict(seq=1, run_id='run-a', occurrence_id='checkpoint', phase='checkpoint', task_id='one',
                                    kind='passed', recorded_at=1, facts=json.dumps({}))]
        self.reader.value = raw
        run = self.client.get('/api/monitor/v1/runs', headers=self.api_headers).json()['runs'][0]
        view = self.client.get(f"/api/monitor/v1/runs/{run['ref']}/snapshot", headers=self.api_headers).json()
        self.assertEqual(run['plan_availability'], 'unavailable')
        self.assertEqual(view['tasks'], [])

    def test_stop_does_not_borrow_another_tasks_agent(self):
        first, _ = self.view([
            ('run-a', 'terminal', 'terminal', None, 'started', {}),
            ('run-a', 'worker', 'worker', 'one', 'started', {'role': 'worker'}),
            ('run-a', 'worker', 'worker', 'one', 'returned', {'role': 'worker'}),
            ('run-a', 'prepare', 'prepare', 'two', 'started', {}),
            ('run-a', 'prepare', 'prepare', 'two', 'failed', {}),
            ('run-a', 'terminal', 'terminal', None, 'failed', {}),
        ])
        stopping = next(item for item in first['occurrences'] if item['stopping'])
        self.assertEqual(stopping['phase'], 'prepare')
        self.assertIsNone(stopping['support_ref'])
