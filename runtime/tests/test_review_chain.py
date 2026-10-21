"""Synthetic store/engine review-chain retention tests; no real workflow runs."""
import json
from unittest.mock import patch

from coherence_workflow.cli import status
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.monitoring import Recorder, descriptor
from coherence_workflow.store import Authority, Blocked
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-review', 'effort': 'medium'}}


class ChainRecordingTests(ProjectTest):
    def test_closed_recording_round_trips_actual_chain_ids_without_inventing_stages(self):
        contract = {'tasks': [{'id': 'fix', 'depends': []}]}
        with Authority(self.project) as owner:
            store = owner.store
            store.start('recorded', self.base)
            recorder = Recorder(store, 'recorded')
            self.assertTrue(recorder.register(descriptor(contract, EXECUTOR, self.base)))

            store.review_dispatch('recorded', 'review-1', review_base=self.base, review_head=self.base)
            store.review_outcome('recorded', 'review-1', 'rejected', findings=['PRIVATE first rejection'],
                                 references={'base': self.base, 'head': self.base, 'commit': self.base})
            recorder.emit('review-1', 'review', 'failed', facts={
                'role': 'reviewer', 'execution_id': 'review-1', 'review_ordinal': 1,
                'review_base': self.base, 'review_head': self.base, 'approved': False,
                'outcome': 'rejected', 'finding_count': 1,
            })
            store.review_dispatch('recorded', 'fix-1', role='fixer', review_ordinal=1, fixing_round=1,
                                  trigger_execution_id='review-1', predecessor_execution_id='review-1',
                                  review_base=self.base, review_head=self.base)
            recorder.emit('fix-1', 'worker', 'started', task_id='fix', facts={
                'role': 'fixing_worker', 'execution_id': 'fix-1',
                'trigger_execution_id': 'review-1', 'predecessor_execution_id': 'review-1',
            })
            recorder.emit('check-1', 'check', 'passed', task_id='fix', facts={
                'ordinal': 1, 'exit_code': 0, 'execution_id': 'fix-1',
            })
            recorder.emit('checkpoint-1', 'checkpoint', 'passed', task_id='fix', facts={
                'baseline': self.base, 'head': self.base, 'no_change': False, 'execution_id': 'fix-1',
            })
            store.review_outcome('recorded', 'fix-1', 'approved', findings=[],
                                 references={'base': self.base, 'head': self.base, 'commit': self.base})
            store.review_dispatch('recorded', 'review-2', review_ordinal=2, fixing_round=1,
                                  trigger_execution_id='fix-1', predecessor_execution_id='fix-1',
                                  review_base=self.base, review_head=self.base)
            recorder.emit('review-2', 'review', 'passed', facts={
                'role': 'reviewer', 'execution_id': 'review-2', 'review_ordinal': 2,
                'trigger_execution_id': 'fix-1', 'predecessor_execution_id': 'fix-1',
                'review_base': self.base, 'review_head': self.base, 'approved': True,
                'outcome': 'approved', 'finding_count': 0,
            })
            store.review_outcome('recorded', 'review-2', 'approved', findings=[],
                                 references={'base': self.base, 'head': self.base, 'commit': self.base})

            # Question parenting is callback lineage only, never execution causality.
            recorder.emit('question-1', 'review', 'question_requested', facts={
                'parent_occurrence_id': 'review-1',
            })
            self.assertIsNone(recorder.emit('bad', 'review', 'passed', facts={
                'role': 'reviewer', 'execution_id': 'review-3', 'review_ordinal': 3,
                'review_base': self.base, 'review_head': self.base, 'outcome': 'approved',
                'private_payload': 'PRIVATE',
            }))
            rows = [(row['occurrence_id'], row['phase'], json.loads(row['facts']))
                    for row in store.monitor('recorded')['observations']]
            self.assertEqual(store.monitor('recorded')['run']['recording_version'], 1)
            self.assertEqual(rows[0][2]['outcome'], 'rejected')
            self.assertEqual(rows[1][2]['trigger_execution_id'], 'review-1')
            self.assertEqual(rows[2][2]['execution_id'], 'fix-1')
            self.assertEqual(rows[3][2]['head'], self.base)
            self.assertEqual(rows[4][2]['predecessor_execution_id'], 'fix-1')
            self.assertEqual(rows[5][2], {'parent_occurrence_id': 'review-1'})
            self.assertNotIn('review-3', [row[0] for row in rows])
            self.assertNotIn('PRIVATE first rejection', json.dumps(rows))
            chain = store.review_chain('recorded', private=True)
            self.assertEqual(chain['executions'][0]['findings'], [['PRIVATE first rejection']])
            self.assertEqual([item['state'] for item in chain['executions']], ['rejected', 'approved', 'approved'])

    def test_optional_recording_failure_adds_gap_without_changing_required_chain(self):
        with Authority(self.project) as owner:
            store = owner.store
            store.start('gap', self.base)
            recorder = Recorder(store, 'gap')
            self.assertTrue(recorder.register(descriptor({'tasks': []}, EXECUTOR, self.base)))
            store.review_dispatch('gap', 'review-1', review_base=self.base, review_head=self.base)
            store.review_outcome('gap', 'review-1', 'rejected', findings=['retained'],
                                 references={'base': self.base, 'head': self.base})
            with patch.object(store, 'append_monitor_observation', side_effect=RuntimeError('optional unavailable')):
                self.assertIsNone(recorder.emit('review-1', 'review', 'failed', facts={
                    'role': 'reviewer', 'execution_id': 'review-1', 'review_ordinal': 1,
                    'review_base': self.base, 'review_head': self.base, 'outcome': 'rejected', 'finding_count': 1,
                }))
            with patch('coherence_workflow.monitoring.uuid.uuid4', side_effect=RuntimeError('id unavailable')):
                self.assertIsNone(recorder.occurrence())
            recorder.emit('later', 'terminal', 'passed', facts={'head': self.base})
            self.assertEqual(store.review_chain('gap')['executions'][0]['state'], 'rejected')
            self.assertIn('gap', [row['kind'] for row in store.monitor('gap')['observations']])


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


class BoundedChainTests(ProjectTest):
    def test_optional_identity_failure_does_not_block_required_chain(self):
        with patch.object(Recorder, 'occurrence', return_value=None):
            self.test_actionable_rejection_repairs_once_then_fresh_rereview()


    def test_immediate_approval_skips_fixer_and_rereview(self):
        calls = []
        class Adapter:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                calls.append(kwargs.get('read_only', False))
                return '{"approved":true,"findings":[]}' if kwargs.get('read_only') else 'synthetic worker'
        with Authority(self.project) as owner:
            result = Engine(owner, 'approved', admit({'tasks': [{'id': 'dummy', 'description': 'synthetic'}]}),
                            EXECUTOR, adapter=Adapter, paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(calls, [False, True])

    def test_actionable_rejection_repairs_once_then_fresh_rereview(self):
        project, calls = self.project, []
        class Adapter:
            reviews = 0
            fixer_prompts = 0
            instances = []
            def __init__(self, *_args, **_kwargs):
                Adapter.instances.append(self)
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    Adapter.reviews += 1
                    calls.append(('review', id(self), kwargs))
                    return '```json\n{"approved":false,"findings":["owned.txt:1 - synthetic defect"]}\n```' if Adapter.reviews == 1 else '{"approved":true,"findings":[]}'
                if 'Actionable findings:' in _prompt:
                    Adapter.fixer_prompts += 1
                    kwargs['claim']('owned.txt')
                    project.joinpath('owned.txt').write_text('broken\n')
                elif 'Actual failed attempt:' in _prompt:
                    Adapter.fixer_prompts += 1
                    project.joinpath('owned.txt').write_text('fixed\n')
                else:
                    kwargs['claim']('owned.txt')
                    project.joinpath('owned.txt').write_text('fixed\n')
                return 'synthetic worker'
        contract = admit({'tasks': [{'id': 'dummy', 'description': 'synthetic', 'owned_paths': ['owned.txt'],
                                     'checks': [['/bin/sh', '-c', 'test "$(cat owned.txt)" = fixed']]}]})
        with Authority(project) as owner:
            result = Engine(owner, 'repaired', contract, EXECUTOR, adapter=Adapter,
                            paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            chain = owner.store.review_chain('repaired')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual([(item['role'], item['state']) for item in chain['executions']],
                         [('reviewer', 'rejected'), ('fixer', 'approved'), ('reviewer', 'approved')])
        self.assertEqual(Adapter.fixer_prompts, 2)
        self.assertEqual(len(calls), 2)
        self.assertNotEqual(calls[0][1], calls[1][1])
        self.assertTrue(all(call[2]['read_only'] for call in calls))

    def test_final_rejection_stops_after_two_reviews_and_one_fixer(self):
        class Adapter:
            reviews = 0
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    Adapter.reviews += 1
                    return ('{"approved":false,"findings":["owned.txt:1 - first"]}' if Adapter.reviews == 1
                            else '{"approved":false,"findings":["owned.txt:2 - final"]}')
                return 'synthetic worker'
        with Authority(self.project) as owner:
            with self.assertRaisesRegex(Blocked, 'final'):
                Engine(owner, 'final-rejection', admit({'tasks': [{'id': 'dummy', 'description': 'synthetic'}]}),
                       EXECUTOR, adapter=Adapter, paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            chain = owner.store.review_chain('final-rejection')
        self.assertEqual((chain['review_count'], chain['fixing_round_count']), (2, 1))
        self.assertEqual(chain['executions'][-1]['findings'], ['owned.txt:2 - final'])

    def test_unrecoverable_fixer_failure_never_launches_second_review(self):
        class Adapter:
            reviews = 0
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    Adapter.reviews += 1
                    return '{"approved":false,"findings":["owned.txt:1 - defect"]}'
                if 'Actionable findings:' in _prompt:
                    raise Blocked('synthetic fixer failure')
                return 'synthetic worker'
        with Authority(self.project) as owner:
            with self.assertRaisesRegex(Blocked, 'synthetic fixer failure'):
                Engine(owner, 'fixer-failure', admit({'tasks': [{'id': 'dummy', 'description': 'synthetic'}]}),
                       EXECUTOR, adapter=Adapter, paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            usage = owner.store.db.execute(
                "SELECT outcome,unknown_reason FROM execution_usage_intervals WHERE run_id='fixer-failure' AND role='fixing_worker'").fetchall()
            self.assertEqual([tuple(row) for row in usage], [('failed', 'usage_observation_unavailable')])
            chain = owner.store.review_chain('fixer-failure')
        self.assertEqual(Adapter.reviews, 1)
        self.assertEqual([(item['role'], item['state']) for item in chain['executions']],
                         [('reviewer', 'rejected'), ('fixer', 'failed')])


class FixExecutionTests(ProjectTest):
    def test_fixer_corrects_a_required_check_and_records_its_own_checkpoint(self):
        project = self.project
        class Fixer:
            prompts = []
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                self.prompts.append(prompt)
                if len(self.prompts) == 1:
                    kwargs['claim']('owned.txt')
                    project.joinpath('owned.txt').write_text('broken\n')
                else:
                    project.joinpath('owned.txt').write_text('fixed\n')
                return 'fixed'

        contract = {'tasks': [{
            'id': 'original', 'description': 'synthetic original work', 'owned_paths': ['owned.txt'],
            'checks': [['/bin/sh', '-c', 'test "$(cat owned.txt)" = fixed']],
        }]}
        self.project.joinpath('other.txt').write_text('unrelated dirty bytes\n')
        with Authority(project) as owner:
            owner.store.start('fix-run', self.base, contract=contract, executor=EXECUTOR,
                              authority={}, review_base=self.base)
            recorder = Recorder(owner.store, 'fix-run')
            self.assertTrue(recorder.register(descriptor(contract, EXECUTOR, self.base)))
            result = Engine(owner, 'fix-run', contract, EXECUTOR, adapter=Fixer,
                            paid_scope={'agent_providers': ['fixture'], 'apis': []}).run_fix(
                                ['owned.txt:1 - synthetic defect'], trigger_execution_id='review-1',
                                review_base=self.base, recorder=recorder, execution_id='fix-1')
            usage = [dict(row) for row in owner.store.db.execute(
                "SELECT * FROM execution_usage_intervals WHERE run_id='fix-run'")]
            self.assertEqual(len(usage), 2)
            self.assertEqual(len({row['occurrence_id'] for row in usage}), 2)
            self.assertTrue(all(row['role'] == 'fixing_worker' for row in usage))
            chain = owner.store.review_chain('fix-run', private=True)
            history = [dict(row) for row in owner.store.db.execute(
                "SELECT kind,state,details FROM execution_history WHERE run_id='fix-run' ORDER BY seq")]
            observations = [(row['phase'], json.loads(row['facts']))
                            for row in owner.store.monitor('fix-run')['observations']]

        self.assertEqual(result['checkpoint']['paths'], ['owned.txt'])
        self.assertEqual(self.project.joinpath('other.txt').read_text(), 'unrelated dirty bytes\n')
        self.assertEqual([(item['role'], item['state']) for item in chain['executions']], [('fixer', 'approved')])
        self.assertEqual(chain['executions'][0]['trigger_execution_id'], 'review-1')
        self.assertTrue(any(item['kind'] == 'fixer_check' and item['state'] == 'failed' for item in history))
        self.assertTrue(any(item['kind'] == 'fixer_checkpoint' and item['state'] == 'passed' for item in history))
        self.assertTrue(any(phase == 'check' and facts.get('execution_id') == 'fix-1' and facts.get('exit_code') == 1
                            for phase, facts in observations))
        self.assertTrue(any(phase == 'checkpoint' and facts.get('execution_id') == 'fix-1' and facts.get('head') == result['checkpoint']['sha']
                            for phase, facts in observations))
        self.assertIn('Actionable findings', Fixer.prompts[0])
        self.assertIn('Actual failed attempt', Fixer.prompts[1])
