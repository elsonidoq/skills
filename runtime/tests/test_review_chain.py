"""Synthetic store/engine review-chain retention tests; no real workflow runs."""
import json
from unittest.mock import patch

from coherence_workflow.cli import status
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, Blocked
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-review', 'effort': 'medium'}}


class ChainHistoryTests(ProjectTest):
    def test_reopen_retains_rejection_attempts_consumed_limits_and_immutable_checkpoint(self):
        with Authority(self.project) as owner:
            store = owner.store
            store.start('chain', self.base)
            store.task('chain', 'original', 'complete', self.base, self.base)
            store.review_dispatch('chain', 'review-1', review_base=self.base, review_head=self.base)
            store.review_outcome('chain', 'review-1', 'rejected', findings=['owned.txt:1 - defect'],
                                 references={'base': self.base, 'head': self.base, 'commit': self.base})
        with Authority(self.project) as owner:
            store = owner.store
            store.review_dispatch('chain', 'fix-1', role='fixer', review_ordinal=1, fixing_round=1,
                                  trigger_execution_id='review-1', predecessor_execution_id='review-1',
                                  review_base=self.base, review_head=self.base)
            store.review_outcome('chain', 'fix-1', 'approved', findings=[],
                                 references={'base': self.base, 'head': self.base})
            store.review_dispatch('chain', 'review-2', review_ordinal=2, fixing_round=1,
                                  trigger_execution_id='fix-1', predecessor_execution_id='fix-1',
                                  review_base=self.base, review_head=self.base)
            store.review_outcome('chain', 'review-2', 'rejected', findings=['owned.txt:2 - still broken'],
                                 references={'base': self.base, 'head': self.base})
            chain = store.review_chain('chain', private=True)
            self.assertEqual((chain['review_count'], chain['fixing_round_count']), (2, 1))
            self.assertEqual(chain['executions'][0]['findings'], [['owned.txt:1 - defect']])
            self.assertEqual(chain['executions'][1]['trigger_execution_id'], 'review-1')
            with self.assertRaisesRegex(Blocked, 'immutable'):
                store.task('chain', 'original', 'running', self.base)
            with self.assertRaisesRegex(Blocked, 'limit already consumed'):
                store.review_dispatch('chain', 'review-extra', review_ordinal=2, fixing_round=1,
                                      review_base=self.base, review_head=self.base)

    def test_uncertain_dispatch_blocks_replay_and_optional_monitor_gap_is_not_authority(self):
        with Authority(self.project) as owner:
            store = owner.store
            store.start('uncertain', self.base)
            store.review_dispatch('uncertain', 'review-1', review_base=self.base, review_head=self.base)
            store.review_outcome('uncertain', 'review-1', 'failed', findings=[], uncertainty=True,
                                 references={'base': self.base, 'head': self.base})
        with Authority(self.project) as owner:
            store = owner.store
            self.assertTrue(store.review_chain('uncertain')['uncertain'])
            with self.assertRaisesRegex(Blocked, 'uncertain'):
                store.review_dispatch('uncertain', 'review-2', review_ordinal=2, fixing_round=1,
                                      review_base=self.base, review_head=self.base)
            with patch.object(store, 'append_monitor_observation', side_effect=RuntimeError('optional gap')):
                # Required chain history remains usable without a monitoring write.
                store.start('separate', self.base)
                store.review_dispatch('separate', 'review-1', review_base=self.base, review_head=self.base)
                store.review_outcome('separate', 'review-1', 'approved', findings=[],
                                     references={'base': self.base, 'head': self.base})
            self.assertEqual(store.review_chain('separate')['executions'][0]['state'], 'approved')

    def test_engine_records_single_review_and_status_exposes_safe_findings_and_references(self):
        project = self.project
        class RejectedReview:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":false,"findings":["owned.txt:1 - actionable defect"]}'
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('changed\n')
                return 'PRIVATE-WORKER-ANSWER'

        contract = admit({'tasks': [{'id': 'original', 'description': 'PRIVATE-TASK-TEXT'}]})
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'actionable defect'):
                Engine(owner, 'reviewed', contract, EXECUTOR, adapter=RejectedReview,
                       paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
        observed = status(project, 'reviewed')
        review = observed['review_chain']['executions'][0]
        self.assertEqual(review['state'], 'rejected')
        self.assertEqual(review['findings'], ['owned.txt:1 - actionable defect'])
        self.assertEqual(review['references']['base'], self.base)
        rendered = json.dumps(observed)
        self.assertNotIn('PRIVATE-TASK-TEXT', rendered)
        self.assertNotIn('PRIVATE-WORKER-ANSWER', rendered)
