"""Synthetic same-run resume fixtures; no real workflow run is replayed."""
import contextlib
import io
import json
from unittest.mock import patch

from coherence_workflow import cli
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium'}


class SameRunResumeTests(ProjectTest):
    def test_cli_resume_skips_recovered_checkpoint_and_retains_original_range(self):
        project, initial_calls, resumed_calls = self.project, [], []
        contract = admit({'paid_scope': {'approved': True, 'agent_providers': ['fixture'], 'apis': []}, 'tasks': [
            {'id': 'first', 'description': 'synthetic first', 'owned_paths': ['one.txt']},
            {'id': 'second', 'description': 'synthetic second', 'owned_paths': ['two.txt']},
        ]})

        class Interrupted:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
                initial_calls.append('worker')
                if len(initial_calls) == 2:
                    raise KeyboardInterrupt
                kwargs['claim']('one.txt')
                project.joinpath('one.txt').write_text('one\n')
                return 'first'

        with Authority(project) as owner:
            with self.assertRaises(KeyboardInterrupt):
                Engine(owner, 'resume-run', contract, EXECUTOR, adapter=Interrupted,
                       paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
        original_head = self.base
        tasks = self.root / 'ignored-tasks.json'
        executor = self.root / 'ignored-executor.json'
        tasks.write_text('[]')
        executor.write_text(json.dumps(EXECUTOR))

        class Resumed:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    resumed_calls.append('review')
                    return '{"approved":true,"findings":[]}'
                resumed_calls.append('worker')
                kwargs['claim']('two.txt')
                project.joinpath('two.txt').write_text('two\n')
                return 'second'

        output = io.StringIO()
        with patch.object(cli, 'PiAdapter', Resumed), contextlib.redirect_stdout(output):
            self.assertEqual(cli.main(['resume', '--project', str(project), '--run', 'resume-run']), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(initial_calls, ['worker', 'worker'])
        self.assertEqual(resumed_calls, ['worker', 'review'])
        self.assertEqual(len(result['checkpoints']), 2)
        self.assertEqual(project.joinpath('one.txt').read_text(), 'one\n')
        self.assertEqual(project.joinpath('two.txt').read_text(), 'two\n')
        self.assertEqual(result['baseline'], original_head)
        with Authority(project) as owner:
            history = [dict(row) for row in owner.store.db.execute(
                "SELECT kind,state,details FROM execution_history WHERE run_id='resume-run' ORDER BY seq")]
        self.assertTrue(any(row['kind'] == 'invocation' and row['state'] == 'resumed' for row in history))

    def test_resume_continues_only_eligible_second_review(self):
        contract = {'tasks': [{'id': 'done', 'description': 'synthetic'}]}
        with Authority(self.project) as owner:
            store = owner.store
            store.start('review-resume', self.base, contract=contract, executor=EXECUTOR,
                        authority={'paid_scope': {'agent_providers': ['fixture'], 'apis': []}}, review_base=self.base)
            store.task('review-resume', 'done', 'complete', self.base, self.base)
            store.history('review-resume', 'done', 'checkpoint', 'passed',
                          {'sha': self.base, 'paths': [], 'artifacts': [], 'no_change': True})
            store.review_dispatch('review-resume', 'review-1', review_base=self.base, review_head=self.base)
            store.review_outcome('review-resume', 'review-1', 'rejected', findings=['x:1 - synthetic'],
                                 references={'base': self.base, 'head': self.base})
            store.review_dispatch('review-resume', 'fix-1', role='fixer', review_ordinal=1, fixing_round=1,
                                  trigger_execution_id='review-1', predecessor_execution_id='review-1',
                                  review_base=self.base, review_head=self.base)
            store.review_outcome('review-resume', 'fix-1', 'approved', findings=[],
                                 references={'base': self.base, 'head': self.base})
            store.finish('review-resume', 'failed', self.base, 'interrupted after fixer')

        class Reviewer:
            calls = 0
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                assert kwargs['read_only']
                Reviewer.calls += 1
                return '{"approved":true,"findings":[]}'

        with Authority(self.project) as owner:
            saved = owner.store.resume('review-resume')['input']
            result = Engine(owner, 'review-resume', saved['contract'], saved['executor'], adapter=Reviewer,
                            paid_scope=saved['authority']['paid_scope'], resume=True).invoke()
            chain = owner.store.review_chain('review-resume', private=True)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(Reviewer.calls, 1)
        self.assertEqual((chain['review_count'], chain['fixing_round_count']), (2, 1))
        self.assertEqual(chain['executions'][0]['findings'], [['x:1 - synthetic']])


class UnfinishedTaskResumeTests(ProjectTest):
    def test_resume_continues_saved_partial_task_without_adopting_unrelated_work(self):
        project = self.project
        contract = admit({'paid_scope': {'approved': True, 'agent_providers': ['fixture'], 'apis': []}, 'tasks': [
            {'id': 'completed', 'description': 'first synthetic task', 'owned_paths': ['one.txt']},
            {'id': 'partial', 'description': 'partial synthetic task', 'owned_paths': ['two.txt'],
             'generated_outputs': ['web/dist/'], 'checks': [[
                 'python3', '-B', '-c', "from pathlib import Path; assert Path('ready').exists(), 'synthetic setup missing'"]]}
        ]})

        class Interrupted:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
                if 'Actual failed attempt:' in prompt:
                    raise KeyboardInterrupt
                if 'first synthetic task' in prompt:
                    kwargs['claim']('one.txt')
                    project.joinpath('one.txt').write_text('complete\n')
                    return 'first complete'
                kwargs['claim']('two.txt')
                project.joinpath('two.txt').write_text('partial\n')
                (project/'web/dist').mkdir(parents=True)
                kwargs['claim']('web/dist/known.js')
                project.joinpath('web/dist/known.js').write_text('generated\n')
                return 'partial work'

        with Authority(project) as owner:
            with self.assertRaises(KeyboardInterrupt):
                Engine(owner, 'partial-resume', contract, EXECUTOR, adapter=Interrupted,
                       paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            first_sha = owner.store.db.execute(
                "SELECT result FROM execution_tasks WHERE run_id='partial-resume' AND task_id='completed'").fetchone()['result']

        project.joinpath('other.txt').write_text('unrelated staged\n')
        git(project, 'add', '--', 'other.txt')
        staged = git(project, 'show', ':other.txt')
        project.joinpath('sentinel.txt').write_text('unrelated dirty bytes\n')
        tasks, executor = self.root / 'ignored-tasks.json', self.root / 'ignored-executor.json'
        tasks.write_text('[]')
        executor.write_text(json.dumps(EXECUTOR))

        class Resumed:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
                if 'Actual failed attempt:' in prompt:
                    project.joinpath('ready').write_text('ready\n')
                    return 'corrected setup'
                assert 'cleanup' in kwargs
                kwargs['claim']('two.txt')
                project.joinpath('two.txt').write_text('continued\n')
                kwargs['cleanup']('web/dist/known.js')
                return 'continued partial task'

        output = io.StringIO()
        with patch.object(cli, 'PiAdapter', Resumed), contextlib.redirect_stdout(output):
            self.assertEqual(cli.main(['resume', '--project', str(project), '--run', 'partial-resume']), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(project.joinpath('two.txt').read_text(), 'continued\n')
        self.assertFalse((project/'web/dist/known.js').exists())
        self.assertEqual(git(project, 'show', ':other.txt'), staged)
        self.assertEqual(project.joinpath('sentinel.txt').read_text(), 'unrelated dirty bytes\n')
        self.assertEqual(git(project, 'show', '--name-only', '--format=', 'HEAD').decode().splitlines(), ['two.txt'])
        with Authority(project) as owner:
            history = [(row['kind'], row['state'], json.loads(row['details'])) for row in owner.store.db.execute(
                "SELECT kind,state,details FROM execution_history WHERE run_id='partial-resume' ORDER BY seq")]
            first = owner.store.db.execute(
                "SELECT result FROM execution_tasks WHERE run_id='partial-resume' AND task_id='completed'").fetchone()['result']
            memberships = owner.store.db.execute(
                "SELECT COUNT(*) FROM execution_usage_memberships WHERE run_id='partial-resume' AND task_id='partial'").fetchone()[0]
        self.assertEqual(first, first_sha)
        self.assertEqual(memberships, 1)
        self.assertTrue(any(kind == 'check' and state == 'failed' and details['exit_code'] == 1
                            for kind, state, details in history))
        self.assertTrue(any(kind == 'mutation' and state == 'claimed' and details['artifacts'] == ['web/dist/known.js']
                            for kind, state, details in history))
