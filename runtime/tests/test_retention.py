"""Private run inputs and append-only operation history through real disposable engine work."""
import json
import sqlite3
from unittest.mock import patch

from coherence_workflow.cli import status
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-review', 'effort': 'medium'}}


class RunInputHistoryTests(ProjectTest):
    def test_original_inputs_and_failed_check_history_survive_same_task_correction_and_safe_projection(self):
        project, prompts = self.project, []
        contract = admit({'review_base': self.base, 'tasks': [
            {'id': 'first', 'description': 'PRIVATE original task text', 'owned_paths': ['owned.txt'], 'checks': [
                ['python3', '-B', '-c', "from pathlib import Path; assert Path('ready').exists(), 'not ready'"]]},
            {'id': 'second', 'description': 'Ordered after first', 'depends': ['first']},
        ]})

        class CorrectingWorker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                prompts.append(prompt)
                if 'PRIVATE original task text' in prompt:
                    kwargs['claim']('owned.txt')
                    project.joinpath('owned.txt').write_text('owned\n')
                if 'Actual failed attempt:' in prompt:
                    project.joinpath('ready').write_text('ready\n')
                return 'PRIVATE worker answer'

        with Authority(project) as owner:
            Engine(owner, 'retained', contract, EXECUTOR, adapter=CorrectingWorker,
                   paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            saved = owner.store.input('retained')

        self.assertEqual(saved['contract'], contract)
        self.assertEqual(saved['executor'], EXECUTOR)
        self.assertEqual(saved['authority']['paid_scope'], {'agent_providers': ['fixture'], 'apis': []})
        self.assertEqual(saved['review_base'], self.base)
        self.assertEqual(len(prompts), 3)

        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        db.row_factory = sqlite3.Row
        history = [(row['kind'], row['state'], json.loads(row['details'])) for row in db.execute(
            "SELECT kind,state,details FROM execution_history WHERE run_id='retained' ORDER BY seq")]
        db.close()
        failed = [details for kind, state, details in history if kind == 'check' and state == 'failed']
        passed = [details for kind, state, details in history if kind == 'check' and state == 'passed']
        checkpoints = [details for kind, state, details in history if kind == 'checkpoint' and state == 'passed']
        self.assertEqual(failed[0]['exit_code'], 1)
        self.assertIn('not ready', failed[0]['output'])
        self.assertEqual(passed[0]['exit_code'], 0)
        self.assertEqual(checkpoints[0]['paths'], ['owned.txt'])
        self.assertEqual(checkpoints[0]['artifacts'], [])
        self.assertEqual(checkpoints[0]['parent'], self.base)

        observed = status(project, 'retained')
        self.assertEqual(observed['input'], {'task_ids': ['first', 'second'], 'review_base': self.base,
                                             'review_policy': 'owner-pair-v1'})
        self.assertIn(1, [row['details'].get('exit_code') for row in observed['history']])
        self.assertNotIn('PRIVATE original task text', json.dumps(observed))
        self.assertNotIn('PRIVATE worker answer', json.dumps(observed))


class RequiredStorageRecoveryTests(ProjectTest):
    def test_transient_required_history_write_recovers_before_dependent_correction_without_replaying_worker(self):
        contract = admit({'tasks': [{'id': 'one', 'description': 'synthetic', 'owned_paths': ['owned.txt'], 'checks': [
            ['python3', '-B', '-c', "from pathlib import Path; assert Path('ready').exists(), 'not ready'"]]}]})
        effects, failed_write = [], [False]

        class Worker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                if 'Actual failed attempt:' in prompt:
                    effects.append('correction')
                    project.joinpath('ready').write_text('ready\n')
                else:
                    effects.append('worker')
                    kwargs['claim']('owned.txt')
                    project.joinpath('owned.txt').write_text('changed\n')
                return 'done'

        project = self.project
        with Authority(project) as owner:
            original = owner.store._history_insert
            def transient(db, run, task, kind, state, details, recorded_at):
                if kind == 'check' and state == 'failed' and not failed_write[0]:
                    failed_write[0] = True
                    effects.append('history-write-failed')
                    raise sqlite3.OperationalError('temporary storage failure')
                return original(db, run, task, kind, state, details, recorded_at)
            with patch.object(owner.store, '_history_insert', side_effect=transient):
                result = Engine(owner, 'storage-recovery', contract, EXECUTOR, adapter=Worker,
                                paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            rows = list(owner.store.db.execute("SELECT kind,state FROM execution_history WHERE run_id='storage-recovery' ORDER BY seq"))

        self.assertEqual(result['status'], 'complete')
        self.assertEqual(effects, ['worker', 'history-write-failed', 'correction'])
        self.assertEqual(sum(1 for kind, state in rows if (kind, state) == ('check', 'failed')), 1)
        self.assertEqual(project.joinpath('owned.txt').read_text(), 'changed\n')

    def test_unrecoverable_required_original_input_stops_before_worker_launch(self):
        contract = admit({'tasks': [{'id': 'one', 'description': 'synthetic'}]})
        prompts = []

        class Worker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                prompts.append(prompt)
                return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}' if kwargs.get('read_only') else 'done'

        with Authority(self.project) as owner:
            with patch.object(owner.store, '_history_insert', side_effect=sqlite3.OperationalError('storage unavailable')):
                with self.assertRaisesRegex(Exception, 'required run input persistence failed after safe correction'):
                    Engine(owner, 'storage-limit', contract, EXECUTOR, adapter=Worker,
                           paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
        self.assertEqual(prompts, [])

    def test_reconciled_completed_write_is_not_replayed(self):
        with Authority(self.project) as owner:
            effects = []
            def completed_write():
                effects.append('effect')
                raise sqlite3.OperationalError('connection dropped after completion')
            owner.store._required_write('synthetic progress', completed_write, lambda: True)
        self.assertEqual(effects, ['effect'])
