"""Actual disposable Store tests for closed optional monitoring storage."""
import json
from unittest.mock import patch

from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.monitoring import Recorder, descriptor
from coherence_workflow.store import Authority
from fixtures.support import ProjectTest


class MonitoringStorageTests(ProjectTest):
    def test_closed_append_survives_reopen_and_ordinary_progress(self):
        contract = {'tasks': [{'id': 'one', 'depends': []}], 'monitor': {'tasks': {'one': {'label': 'Public'}}}}
        with Authority(self.project) as owner:
            owner.store.start('run', self.base)
            rec = Recorder(owner.store, 'run')
            self.assertTrue(rec.register(descriptor(contract, {'provider': 'offline', 'model': 'fixture', 'effort': 'medium'})))
            occurrence = rec.occurrence()
            facts = {'role': 'worker', 'invocation_id': 'call-one', 'invocation_kind': 'task_worker',
                     'selected_input_checkpoints': [], 'correction_chain': ['call-one']}
            rec.emit(occurrence, 'worker', 'started', task_id='one', facts=facts)
            rec.emit(occurrence, 'worker', 'returned', task_id='one', facts=facts)
            owner.store.task('run', 'one', 'complete', self.base)
            before = dict(owner.store.db.execute('SELECT * FROM execution_tasks').fetchone())
        with Authority(self.project) as owner:
            record = owner.store.monitor('run')
            self.assertEqual([row['kind'] for row in record['observations']], ['started', 'returned'])
            self.assertEqual(record['observations'][0]['occurrence_id'], occurrence)
            retained = json.loads(record['run']['description'])
            self.assertEqual(retained['tasks'][0]['label'], 'Public')
            self.assertEqual(retained['description_version'], 2)
            self.assertTrue(any(phase['pre_recording'] for phase in retained['phases']))
            self.assertTrue(any(phase['possible_branches'] for phase in retained['phases']))
            self.assertEqual(dict(owner.store.db.execute('SELECT * FROM execution_tasks').fetchone()), before)

    def test_fixer_calls_use_closed_distinct_invocation_facts(self):
        with Authority(self.project) as owner:
            owner.store.start('fixer-calls', self.base)
            rec = Recorder(owner.store, 'fixer-calls')
            self.assertTrue(rec.register(descriptor({'tasks': []}, {})))
            first = {
                'role': 'fixing_worker', 'execution_id': 'fix-1', 'invocation_id': 'call-1',
                'invocation_kind': 'task_worker', 'selected_input_checkpoints': [],
                'correction_chain': ['call-1'], 'fixing_round': 1,
                'trigger_execution_id': 'review-1', 'predecessor_execution_id': 'review-1',
            }
            second = {**first, 'invocation_id': 'call-2', 'invocation_kind': 'corrective_worker',
                      'correction_chain': ['call-1', 'call-2'], 'predecessor_invocation_id': 'call-1'}
            rec.emit('call-1', 'worker', 'started', task_id='fix-fix-1', facts=first)
            rec.emit('call-2', 'worker', 'started', task_id='fix-fix-1', facts=second)
            rows = [(row['kind'], json.loads(row['facts']))
                    for row in owner.store.monitor('fixer-calls')['observations']]

        self.assertEqual(rows, [('started', first), ('started', second)])

    def test_invalid_optional_metadata_and_append_failure_do_not_veto_progress(self):
        contract = {'tasks': [{'id': 'one'}], 'monitor': {'tasks': {'one': {'label': ['private']}}}}
        self.assertEqual(descriptor(contract, {})['tasks'][0]['label'], 'Task')
        with Authority(self.project) as owner:
            owner.store.start('run', self.base)
            rec = Recorder(owner.store, 'run')
            self.assertTrue(rec.register(descriptor(contract, {})))
            self.assertIsNone(rec.emit(rec.occurrence(), 'worker', 'started', facts={'role': 'PRIVATE-SENTINEL'}))
            self.assertIsNone(rec.emit(rec.occurrence(), 'checkpoint', 'passed', facts={'baseline': self.base, 'head': self.base, 'no_change': 'false'}))
            facts = {'role': 'worker', 'invocation_id': 'call-one', 'invocation_kind': 'task_worker',
                     'selected_input_checkpoints': [], 'correction_chain': ['call-one']}
            rec.emit(rec.occurrence(), 'worker', 'started', facts=facts)
            self.assertNotIn('gap', [row[0] for row in owner.store.db.execute('SELECT kind FROM execution_observations')])
            with patch.object(owner.store, 'append_monitor_observation', side_effect=RuntimeError('private sentinel')):
                self.assertIsNone(rec.emit(rec.occurrence(), 'worker', 'started', facts=facts))
            rec.emit(rec.occurrence(), 'worker', 'started', facts=facts)
            self.assertIn('gap', [row[0] for row in owner.store.db.execute('SELECT kind FROM execution_observations')])
            owner.store.task('run', 'one', 'complete', self.base)
            self.assertEqual(owner.store.db.execute('SELECT state FROM execution_tasks').fetchone()[0], 'complete')

    def test_invoke_records_exact_selected_join_and_correction_chain(self):
        class Worker:
            def __init__(self, *args, **kwargs): self.calls = 0
            def prompt(self, prompt, *, read_only=False, **kwargs):
                if read_only:
                    return '{"approved":true,"findings":[]}'
                self.calls += 1
                return 'returned'

        tasks = [
            {'id': 'left', 'description': 'left'},
            {'id': 'right', 'description': 'right'},
            {'id': 'join', 'description': 'join', 'depends': ['left', 'right']},
        ]
        with Authority(self.project) as owner:
            Engine(owner, 'relations', admit(tasks),
                   {'provider': 'fixture', 'model': 'offline', 'effort': 'medium'}, adapter=Worker).invoke()
            rows = [(row['task_id'], row['kind'], json.loads(row['facts'])) for row in
                    owner.store.monitor('relations')['observations'] if row['phase'] == 'worker']
            checkpoints = [{**json.loads(row['facts']), 'checkpoint_occurrence_id': row['occurrence_id']}
                           for row in owner.store.monitor('relations')['observations']
                           if row['phase'] == 'checkpoint' and row['kind'] == 'passed']

        started = {task_id: facts for task_id, kind, facts in rows if kind == 'started'}
        self.assertEqual(set(started), {'left', 'right', 'join'})
        self.assertEqual(started['left']['invocation_kind'], 'task_worker')
        self.assertEqual(started['join']['selected_input_checkpoints'], [
            {'checkpoint_occurrence_id': checkpoints[0]['checkpoint_occurrence_id'], 'task_id': 'left',
             'producer_invocation_id': checkpoints[0]['producer_invocation_id'],
             'correction_chain': checkpoints[0]['correction_chain']},
            {'checkpoint_occurrence_id': checkpoints[1]['checkpoint_occurrence_id'], 'task_id': 'right',
             'producer_invocation_id': checkpoints[1]['producer_invocation_id'],
             'correction_chain': checkpoints[1]['correction_chain']},
        ])
        self.assertTrue(all(facts['correction_chain'][-1] == facts['invocation_id']
                            for facts in started.values()))

    def test_resumed_interrupted_correction_retains_recorded_invocation_lineage(self):
        project = self.project
        task = {
            'id': 'resume', 'description': 'resume one interrupted correction',
            'owned_paths': ['effect.txt', 'ready.txt'],
            'required': [{'id': 'ready', 'check': [
                'python3', '-B', '-c',
                "from pathlib import Path; assert Path('effect.txt').read_text() == 'complete\\n'; assert Path('ready.txt').read_text() == 'ready\\n'",
            ]}],
        }
        calls = []

        class InterruptedWorker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, *, read_only=False, claim=None, **kwargs):
                if read_only:
                    return '{"approved":true,"findings":[]}'
                calls.append('initial' if len(calls) == 0 else 'interrupted-correction')
                if len(calls) == 1:
                    claim('effect.txt')
                    (project / 'effect.txt').write_text('complete\n')
                    return 'completed effect once'
                raise KeyboardInterrupt

        with Authority(project) as owner:
            with self.assertRaises(KeyboardInterrupt):
                Engine(owner, 'resume-lineage', admit([task]),
                       {'provider': 'fixture', 'model': 'offline', 'effort': 'medium'},
                       adapter=InterruptedWorker).invoke()
            owner.store.resume('resume-lineage')

            class ResumedWorker:
                def __init__(self, *args, **kwargs): pass
                def prompt(self, prompt, *, read_only=False, claim=None, **kwargs):
                    if read_only:
                        return '{"approved":true,"findings":[]}'
                    self_case.assertIn('Continue only the unfinished same-task work.', prompt)
                    calls.append('resumed-correction')
                    claim('ready.txt')
                    (project / 'ready.txt').write_text('ready\n')
                    return 'continued without replaying completed effect'

            self_case = self
            result = Engine(owner, 'resume-lineage', admit([task]),
                            {'provider': 'fixture', 'model': 'offline', 'effort': 'medium'},
                            adapter=ResumedWorker, resume=True).invoke()
            observations = owner.store.monitor('resume-lineage')['observations']

        self.assertEqual(result['status'], 'complete')
        self.assertEqual(calls, ['initial', 'interrupted-correction', 'resumed-correction'])
        workers = [json.loads(row['facts']) for row in observations
                   if row['phase'] == 'worker' and row['kind'] == 'started']
        self.assertEqual([facts['invocation_kind'] for facts in workers],
                         ['task_worker', 'corrective_worker', 'corrective_worker'])
        self.assertEqual(workers[2]['predecessor_invocation_id'], workers[1]['invocation_id'])
        self.assertEqual(workers[2]['correction_chain'], [facts['invocation_id'] for facts in workers])
        checkpoint = next(json.loads(row['facts']) for row in observations
                          if row['phase'] == 'checkpoint' and row['kind'] == 'passed')
        self.assertEqual(checkpoint['producer_invocation_id'], workers[2]['invocation_id'])
        self.assertEqual(checkpoint['correction_chain'], workers[2]['correction_chain'])

    def test_failed_invocation_records_exact_terminal_stop(self):
        class FailingWorker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, *, read_only=False, **kwargs):
                if read_only:
                    return '{"approved":true,"findings":[]}'
                raise RuntimeError('offline failure')

        with Authority(self.project) as owner:
            with self.assertRaisesRegex(RuntimeError, 'offline failure'):
                Engine(owner, 'terminal-stop', admit([{'id': 'broken', 'description': 'broken'}]),
                       {'provider': 'fixture', 'model': 'offline', 'effort': 'medium'}, adapter=FailingWorker).invoke()
            rows = owner.store.monitor('terminal-stop')['observations']

        worker = next(json.loads(row['facts']) for row in rows
                      if row['phase'] == 'worker' and row['kind'] == 'failed')
        terminal = next(json.loads(row['facts']) for row in rows
                        if row['phase'] == 'terminal' and row['kind'] == 'failed')
        self.assertEqual(worker['stopped_by_invocation_id'], worker['invocation_id'])
        self.assertEqual(terminal['stopped_by_invocation_id'], worker['invocation_id'])
