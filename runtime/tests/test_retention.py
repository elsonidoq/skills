"""Private run inputs and append-only operation history through real disposable engine work."""
import json
import sqlite3

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
                    return '{"approved":true,"findings":[]}'
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
        self.assertEqual(observed['input'], {'task_ids': ['first', 'second'], 'review_base': self.base})
        self.assertIn(1, [row['details'].get('exit_code') for row in observed['history']])
        self.assertNotIn('PRIVATE original task text', json.dumps(observed))
        self.assertNotIn('PRIVATE worker answer', json.dumps(observed))
