"""Synthetic same-run resume fixtures; no real workflow run is replayed."""
import contextlib
import io
import json
from unittest.mock import patch

from coherence_workflow import cli
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority
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
