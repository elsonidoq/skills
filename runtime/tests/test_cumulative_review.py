"""Offline review dispatch/retention checks, not evidence of live reviewer judgment."""
import json

from coherence_workflow.cli import status
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-review', 'effort': 'medium'}}


class CumulativeReviewTests(ProjectTest):
    def test_initial_coverage_repair_delta_and_resumed_cumulative_result(self):
        project, prompts, reviewers = self.project, [], []
        initial_coverage = 'stable.txt: examined unchanged rendering; expected output is correct'
        fix_coverage = 'owned.txt: defect resolved; adjacent missing-input interaction checked'
        finding = 'owned.txt:1 - missing input crashes the requested operation'

        class Adapter:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    prompts.append(prompt)
                    reviewers.append(self)
                    first = len(prompts) == 1
                    return json.dumps({'approved': not first,
                        'coverage': [initial_coverage] if first else [initial_coverage, fix_coverage],
                        'coverage_gaps': [], 'findings': [finding] if first else []})
                if 'Continue the rejecting review' in prompt:
                    kwargs['claim']('owned.txt')
                    (project/'owned.txt').write_text('fixed missing input\n')
                else:
                    kwargs['claim']('stable.txt')
                    (project/'stable.txt').write_text('original stable rendering\n')
                    kwargs['claim']('owned.txt')
                    (project/'owned.txt').write_text('broken missing input\n')
                return 'synthetic implementation'

        contract = admit({'tasks': [{'id': 'change', 'description': 'Stable rendering and safe input handling'}]})
        with Authority(project) as owner:
            result = Engine(owner, 'cumulative', contract, EXECUTOR, adapter=Adapter).invoke()
            chain = owner.store.review_chain('cumulative', private=True)['executions']
        self.assertEqual(result['status'], 'complete')
        self.assertEqual([item['role'] for item in chain], ['reviewer', 'fixer', 'reviewer'])
        first, repair, last = chain
        prior_head = first['references']['head']
        self.assertEqual(last['references']['diff_base'], prior_head)
        self.assertEqual(last['references']['prior_review'], first['execution_id'])
        self.assertEqual(git(project, 'rev-parse', result['sha'] + '^').decode().strip(), prior_head)
        self.assertIsNot(reviewers[0], reviewers[1])
        self.assertIn('Initial review: examine the complete requested change', prompts[0])
        self.assertIn('original stable rendering', prompts[0].split('\nDiff:\n')[1])
        self.assertIn('Review delta: ' + prior_head + '..' + repair['references']['head'], prompts[1])
        delta = prompts[1].split('\nDiff:\n')[1].split('\nAttributable task/repair checkpoints')[0]
        self.assertIn('-broken missing input', delta)
        self.assertIn('+fixed missing input', delta)
        self.assertNotIn('stable.txt', delta)
        self.assertIn(initial_coverage, prompts[1])
        self.assertIn(finding, prompts[1])
        self.assertIn('affected interactions', prompts[1])
        self.assertIn('invalidated by the repair', prompts[1])
        self.assertIn('must not certify unchecked original work', prompts[1])
        self.assertNotIn('Review the complete original range and diff on every review', prompts[1])
        self.assertEqual(result['review']['coverage'], [initial_coverage, fix_coverage])
        self.assertEqual(result['review']['findings'], [])
        self.assertEqual(result['review']['coverage_gaps'], [])
        self.assertEqual(status(project, 'cumulative')['review_chain']['executions'][-1]
                         ['references']['review_summary']['coverage'], result['review']['coverage'])

        class NoReplay:
            def __init__(self, *_args, **_kwargs):
                raise AssertionError('settled review must not be replayed')
        with Authority(project) as owner:
            resumed = Engine(owner, 'cumulative', contract, EXECUTOR, adapter=NoReplay, resume=True).invoke()
        self.assertEqual(resumed['review'], result['review'])

    def test_missing_coverage_is_not_accepted_as_a_fresh_verdict(self):
        with self.assertRaisesRegex(Blocked, 'coverage and coverage_gaps'):
            Engine._review_value('{"approved":true,"findings":[]}', require_coverage=True)

    def test_unchecked_and_invalidated_conclusions_prevent_completion(self):
        for gap in ('Original persistence behavior was never reviewed',
                    'Repair invalidated the earlier rendering conclusion; not yet re-established'):
            with self.subTest(gap=gap):
                class Adapter:
                    def __init__(self, *_args, **_kwargs): pass
                    def prompt(self, _prompt, **kwargs):
                        if kwargs.get('read_only'):
                            return json.dumps({'approved': True, 'findings': [],
                                'coverage': ['Input validation examined and passing'], 'coverage_gaps': [gap]})
                        return 'no change'
                run = 'unchecked' if gap.startswith('Original') else 'invalidated'
                with Authority(self.project) as owner:
                    with self.assertRaisesRegex(Blocked, 'remaining coverage gaps'):
                        Engine(owner, run, admit({'tasks': [{'id': 't', 'description': 'Review behavior'}]}),
                               EXECUTOR, adapter=Adapter).invoke()
                    chain = owner.store.review_chain(run)['executions']
                self.assertEqual(len(chain), 1)
                self.assertEqual(chain[0]['state'], 'rejected')
                self.assertEqual(chain[0]['references']['review_summary']['coverage_gaps'], [gap])

    def test_empty_coverage_cannot_approve(self):
        value = Engine._review_value(json.dumps({'approved': True, 'findings': [],
            'coverage': [], 'coverage_gaps': []}), require_coverage=True)
        self.assertFalse(value['approved'])
        self.assertIn('No examined/passing coverage', value['coverage_gaps'][0])
