"""Offline recording fixtures exercise closed HTTP execution presentation, not a provider."""
import json
import unittest

from workflow_monitor.tests import test_http
from workflow_monitor.tests.test_mapping import snapshot


class ExecutionPresentationTests(unittest.TestCase):
    setUp = test_http.HttpTests.setUp

    def view(self, rows):
        raw = snapshot()
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
        self.assertIsNone(worker['outcome'])  # return is not acceptance
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
