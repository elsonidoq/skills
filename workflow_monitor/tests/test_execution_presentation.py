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
            description["tasks"] = [{"id": task["id"], "depends": task["depends"],
                                     "label": task.get("label", task["id"]),
                                     "work_description": task.get("work_description")}
                                    for task in tasks]
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
        # Adjacency and nested prepare rows are not support evidence, but the
        # recorded terminal failure remains visible as a cause-unknown stop.
        self.assertTrue(next(item for item in first['occurrences'] if item['phase'] == 'terminal')['stopping'])
        worker = next(item for item in first['occurrences'] if item['role'] == 'worker')
        self.assertIsNone(next(item for item in first['occurrences'] if item['phase'] == 'check')['support_ref'])
        self.assertNotEqual(worker['ref'], second['occurrences'][0]['ref'])
        self.assertIsNone(worker['outcome'])  # legacy outcome remains acceptance-neutral
        self.assertEqual(worker['execution_summary']['state'], 'success')
        self.assertEqual(next(item for item in first['occurrences'] if item['role'] == 'worker')['occurrence_id'], 'worker')

    def test_pre_agent_stop_has_no_invented_parent(self):
        first, _ = self.view([
            ('run-a', 'terminal', 'terminal', None, 'started', {}),
            ('run-a', 'prepare', 'prepare', 'one', 'started', {}),
            ('run-a', 'prepare', 'prepare', 'one', 'failed', {}),
            ('run-a', 'terminal', 'terminal', None, 'failed', {}),
        ])
        self.assertTrue(next(item for item in first['occurrences'] if item['phase'] == 'terminal')['stopping'])
        self.assertTrue(any(item['phase'] == 'prepare' and item['outcome'] == 'failed' for item in first['occurrences']))

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
        self.assertIsNone(failed['support_ref'])
        self.assertTrue(any(item['kind'] == 'failed' for item in first['records']))

    def test_explicit_invocation_stop_selects_only_the_recorded_failure(self):
        worker = {'role': 'worker', 'invocation_id': 'worker-invocation', 'invocation_kind': 'task_worker',
                  'selected_input_checkpoints': [], 'correction_chain': ['worker-invocation']}
        first, _ = self.view([
            ('run-a', 'worker', 'worker', 'one', 'started', worker),
            ('run-a', 'worker', 'worker', 'one', 'failed', {**worker, 'stopped_by_invocation_id': 'worker-invocation', 'error_category': 'check'}),
            ('run-a', 'terminal', 'terminal', None, 'failed', {'stopped_by_invocation_id': 'worker-invocation', 'error_category': 'check'}),
        ])
        failed = next(item for item in first['occurrences'] if item['occurrence_id'] == 'worker')
        self.assertTrue(failed['stopping'])
        self.assertEqual(next(item for item in first['activities'] if item['invocation_id'] == 'worker-invocation')['error_category'], 'check')

    def test_question_parent_keeps_routing_scoped_and_displays_recorded_identity(self):
        first, _ = self.view([
            ('run-a', 'PRIVATE-SENTINEL', 'worker', 'one', 'started', {'role': 'worker'}),
            ('run-a', 'question', 'worker', 'one', 'question_requested', {'parent_occurrence_id': 'PRIVATE-SENTINEL'}),
        ])
        worker, question = first['occurrences']
        self.assertEqual(question['parent_ref'], worker['ref'])
        self.assertEqual(worker['occurrence_id'], 'PRIVATE-SENTINEL')
        self.assertEqual(first['records'][1]['parent_occurrence_id'], 'PRIVATE-SENTINEL')

    def test_acceptance_uses_the_same_typed_ranges_as_records(self):
        credential = 'Bearer synthetic-credential-not-a-commit'
        first, _ = self.view([
            ('run-a', 'checkpoint', 'checkpoint', 'one', 'passed',
             {'baseline': credential, 'head': {'token': credential}, 'no_change': True}),
            ('run-a', 'review', 'review', None, 'failed',
             {'role': 'reviewer', 'review_base': [credential], 'review_head': credential,
              'approved': False, 'finding_count': -1}),
        ])
        summary = first['runs'][0]['acceptance_summary']
        self.assertIsNone(summary['checkpoints'][0]['baseline'])
        self.assertIsNone(summary['checkpoints'][0]['head'])
        self.assertIsNone(summary['reviews'][0]['base'])
        self.assertIsNone(summary['reviews'][0]['head'])
        self.assertIsNone(summary['reviews'][0]['finding_count'])
        self.assertNotIn(credential, json.dumps(first))

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

    def test_manual_gate_waiting_uses_full_task_questions_and_matching_resolution(self):
        noise = [('run-a', f'noise-{i}', 'check', None, 'started', {}) for i in range(50)]
        gate = [
            ('run-a', 'gate', 'gate', 'one', 'started', {'ordinal': 1}),
            ('run-a', 'question', 'gate', 'one', 'question_requested', {'parent_occurrence_id': 'gate'}),
            # A different question's answer cannot clear the outstanding request.
            ('run-a', 'other-question', 'gate', 'two', 'answer_returned', {'parent_occurrence_id': 'other-gate'}),
        ]
        for resolution in (None, 'answer_returned', 'answer_sent', 'delivery_failed'):
            with self.subTest(resolution=resolution):
                rows = noise + gate
                if resolution:
                    rows += [('run-a', 'question', 'gate', 'one', resolution, {'parent_occurrence_id': 'gate'})]
                first, _ = self.view(rows)
                task = first['tasks'][0]
                if resolution is None:
                    self.assertEqual(task['progress'], {'state': 'running', 'qualification': 'waiting_for_input'})
                    self.assertEqual(task['annotation']['code'], 'waiting_for_input')
                    question = next(item for item in first['occurrences'] if item['occurrence_id'] == 'question')
                    self.assertEqual(task['annotation']['occurrence_ref'], question['ref'])
                else:
                    self.assertIsNone(task['annotation'])
                    self.assertNotEqual(task['progress'].get('qualification'), 'waiting_for_input')
                self.assertFalse(any(item['role'] == 'worker' for item in first['occurrences']))
                self.assertEqual(len(first['records']), 50)
                reference = first['runs'][0]['ref']
                later = self.client.get(f"/api/monitor/v1/runs/{reference}/history?snapshot={first['snapshot_ref']}&cursor={first['next_cursor']}", headers=self.api_headers).json()
                self.assertEqual(first['tasks'], later['tasks'])

        # Resolving one of two same-task questions does not clear the other.
        first, _ = self.view(noise + gate + [
            ('run-a', 'second', 'gate', 'one', 'question_requested', {'parent_occurrence_id': 'gate'}),
            ('run-a', 'second', 'gate', 'one', 'answer_returned', {'parent_occurrence_id': 'gate'}),
        ])
        self.assertEqual(first['tasks'][0]['annotation']['code'], 'waiting_for_input')

        for phase, kind, expected in [('gate', 'failed', 'failed'), ('gate', 'passed', 'unknown'),
                                       ('terminal', 'failed', 'unknown'), ('checkpoint', 'passed', 'completed')]:
            with self.subTest(terminal=(phase, kind)):
                first, _ = self.view(noise + gate + [
                    ('run-a', 'gate' if phase == 'gate' else phase, phase, None if phase == 'terminal' else 'one', kind, {})])
                self.assertEqual(first['tasks'][0]['progress']['state'], expected)
                self.assertIsNone(first['tasks'][0]['annotation'])

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
        self.assertTrue(next(item for item in first['occurrences'] if item['phase'] == 'terminal')['stopping'])
