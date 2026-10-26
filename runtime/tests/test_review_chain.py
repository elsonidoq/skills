"""Synthetic store/engine review-chain retention tests; no real workflow runs."""
import contextlib
import io
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
            recorder.emit('fix-call-1', 'worker', 'started', task_id='fix', facts={
                'role': 'fixing_worker', 'execution_id': 'fix-1', 'invocation_id': 'fix-call-1',
                'invocation_kind': 'task_worker', 'selected_input_checkpoints': [],
                'correction_chain': ['fix-call-1'], 'fixing_round': 1,
                'trigger_execution_id': 'review-1', 'predecessor_execution_id': 'review-1',
            })
            recorder.emit('check-1', 'check', 'passed', task_id='fix', facts={
                'ordinal': 1, 'exit_code': 0, 'execution_id': 'fix-1',
            })
            recorder.emit('checkpoint-1', 'checkpoint', 'passed', task_id='fix', facts={
                'baseline': self.base, 'head': self.base, 'no_change': False, 'execution_id': 'fix-1',
                'producer_invocation_id': 'fix-call-1', 'correction_chain': ['fix-call-1'],
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


class OwnerPairPrimitiveTests(ProjectTest):
    def _rejection(self, store, run='pair'):
        store.review_dispatch(run, 'review-1', review_base=self.base, review_head=self.base)
        store.review_outcome(run, 'review-1', 'rejected', findings=['owned.txt:1 - requests crash'],
                             references={'base': self.base, 'head': self.base})
        store.review_dispatch(run, 'fix-1', role='fixer', review_ordinal=1, fixing_round=1,
                              trigger_execution_id='review-1', predecessor_execution_id='review-1',
                              review_base=self.base, review_head=self.base)
        store.review_outcome(run, 'fix-1', 'approved', findings=[], references={'base': self.base, 'head': self.base})
        store.review_dispatch(run, 'review-2', review_ordinal=2, fixing_round=1,
                              trigger_execution_id='fix-1', predecessor_execution_id='fix-1',
                              review_base=self.base, review_head=self.base)
        store.review_outcome(run, 'review-2', 'rejected', findings=['owned.txt:1 - retained defect'],
                             references={'base': self.base, 'head': self.base})

    def test_owner_pair_grant_is_durable_and_consumed_once_for_assigned_identities(self):
        authority = {'review_policy': 'owner-pair-v1'}
        with Authority(self.project) as owner:
            store = owner.store
            store.start('pair', self.base, authority=authority)
            self._rejection(store)
            grant = store.authorize_owner_pair('pair', 'grant-1', rejecting_execution_id='review-2',
                                               review_base=self.base, review_head=self.base, original_scope=store.review_scope('pair'),
                                               fixer_execution_id='fix-2', reviewer_execution_id='review-3')
            reserved = store.reserve_owner_pair_fixer('pair', 'grant-1', rejecting_execution_id='review-2',
                                                       review_base=self.base, review_head=self.base, original_scope=store.review_scope('pair'))
            self.assertEqual((grant['grant_id'], reserved['fixer_execution_id']), ('grant-1', 'fix-2'))
        with Authority(self.project) as owner:
            store = owner.store
            self.assertEqual(store.review_policy('pair'), 'owner-pair-v1')
            self.assertEqual(store.reserve_owner_pair_fixer('pair', 'grant-1', rejecting_execution_id='review-2',
                                                             review_base=self.base, review_head=self.base,
                                                             original_scope=store.review_scope('pair'))['fixer_execution_id'], 'fix-2')
            with self.assertRaisesRegex(Blocked, 'scope'):
                store.reserve_owner_pair_fixer('pair', 'grant-1', rejecting_execution_id='review-2', review_base=self.base,
                                               review_head=self.base, original_scope='wrong-scope')
            rows = list(store.db.execute("SELECT state FROM execution_history WHERE run_id='pair' AND kind='review_pair_reservation'"))
            self.assertEqual([row['state'] for row in rows], ['fixer_reserved'])

    def test_pair_reviewer_requires_same_grant_successful_fixer_and_unknown_policy_stops(self):
        with Authority(self.project) as owner:
            store = owner.store
            store.start('pair', self.base, authority={'review_policy': 'owner-pair-v1'})
            self._rejection(store)
            store.authorize_owner_pair('pair', 'grant', rejecting_execution_id='review-2', review_base=self.base,
                                       review_head=self.base, original_scope=store.review_scope('pair'), fixer_execution_id='fix-2', reviewer_execution_id='review-3')
            store.reserve_owner_pair_fixer('pair', 'grant', rejecting_execution_id='review-2', review_base=self.base,
                                           review_head=self.base, original_scope=store.review_scope('pair'))
            with self.assertRaisesRegex(Blocked, 'successful fixer'):
                store.reserve_owner_pair_reviewer('pair', 'grant', fixer_execution_id='fix-2')
            store.review_dispatch('pair', 'fix-2', role='fixer', review_ordinal=2, fixing_round=2,
                                  trigger_execution_id='review-2', predecessor_execution_id='review-2',
                                  review_base=self.base, review_head=self.base)
            store.review_outcome('pair', 'fix-2', 'approved', findings=[], references={'base': self.base, 'head': self.base})
            self.assertEqual(store.reserve_owner_pair_reviewer('pair', 'grant', fixer_execution_id='fix-2')['reviewer_execution_id'], 'review-3')
            store.start('unknown', self.base, contract={'tasks': []}, authority={'review_policy': 'future-policy'})
            store.finish('unknown', 'failed', error='interrupted fixture')
            with self.assertRaisesRegex(Blocked, 'unsupported retained review policy'):
                store.resume('unknown')


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
                    return '{"approved":false,"findings":["owned.txt:1 - actionable defect [basis: correctness]"]}'
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('changed\n')
                return 'PRIVATE-WORKER-ANSWER'

        contract = admit({'tasks': [{'id': 'original', 'description': 'PRIVATE-TASK-TEXT'}]})
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'owner authorization unavailable'):
                Engine(owner, 'reviewed', contract, EXECUTOR, adapter=RejectedReview,
                       paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
        observed = status(project, 'reviewed')
        review = observed['review_chain']['executions'][0]
        self.assertEqual(review['state'], 'rejected')
        self.assertEqual(review['findings'], ['owned.txt:1 - actionable defect [basis: correctness]'])
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

    def test_risk_word_suggestions_are_nonblocking_and_status_projects_them_separately(self):
        suggestions = ['consider crash regression coverage', 'consider hang regression coverage',
                       'Consider adding regression coverage for invalid credentials',
                       'consider target risk regression coverage',
                       'consider false unavailable regression coverage']
        calls = []
        class Adapter:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                calls.append(kwargs.get('read_only', False))
                return json.dumps({'approved': True, 'findings': [], 'suggestions': suggestions}) if kwargs.get('read_only') else 'worker answer'
        contract = admit({'tasks': [{'id': 'private', 'description': 'PRIVATE task text'}]})
        with Authority(self.project) as owner:
            result = Engine(owner, 'suggestions-only', contract, EXECUTOR, adapter=Adapter).invoke()
        observed = status(self.project, 'suggestions-only')
        review = observed['review_chain']['executions'][0]
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(calls, [False, True])
        self.assertEqual(review['findings'], [])
        self.assertEqual(review['suggestions'], suggestions)
        self.assertNotIn('PRIVATE task text', json.dumps(observed))

    def test_risk_word_suggestions_are_valid_parser_output(self):
        suggestions = ['crash', 'hang', 'credential', 'target risk', 'false unavailable']
        self.assertEqual(Engine._review_value(json.dumps({'approved': True, 'findings': [], 'suggestions': suggestions})),
                         {'approved': True, 'findings': [], 'suggestions': suggestions})

    def test_positive_blockers_and_negative_empty_stop_without_a_fixer(self):
        for name, verdict in (
            ('positive-crash', '{"approved":true,"findings":["owned.txt:1 - crashes on missing input"]}'),
            ('positive-hang', '{"approved":true,"findings":["owned.txt:1 - hangs while waiting for input"]}'),
            ('positive-credential', '{"approved":true,"findings":["owned.txt:1 - exposes credentials in output"]}'),
            ('positive-target', '{"approved":true,"findings":["owned.txt:1 - applies changes to the wrong target"]}'),
            ('positive-data-safety', '{"approved":true,"findings":["owned.txt:1 - corrupts saved state [basis: data-safety]"]}'),
            ('negative-empty', '{"approved":false,"findings":[],"suggestions":["consider naming cleanup"]}'),
        ):
            with self.subTest(name=name):
                calls = []
                class Adapter:
                    def __init__(self, *_args, **_kwargs): pass
                    def prompt(self, _prompt, **kwargs):
                        calls.append(kwargs.get('read_only', False))
                        return verdict if kwargs.get('read_only') else 'worker answer'
                with Authority(self.project) as owner:
                    with self.assertRaisesRegex(Blocked, 'owner authorization unavailable|actionable rejection'):
                        Engine(owner, name, admit({'tasks': [{'id': 'task', 'description': 'fixture'}]}),
                               EXECUTOR, adapter=Adapter).invoke()
                    chain = owner.store.review_chain(name)
                if name.startswith('positive-'):
                    self.assertEqual(calls, [False, True, False, True])
                    self.assertEqual(chain['fixing_round_count'], 1)
                else:
                    self.assertEqual(calls, [False, True])
                    self.assertEqual(chain['fixing_round_count'], 0)

    def test_malformed_review_types_stop_without_fixer(self):
        malformed = ('not-json',
                     '{"approved":"yes","findings":[]}',
                     '{"approved":true,"findings":"not a list"}',
                     '{"approved":true,"findings":[],"suggestions":"not a list"}',
                     '{"approved":false,"findings":["no location or concrete impact"]}',
                     '{"approved":true,"findings":[],"suggestions":[""]}')
        for ordinal, verdict in enumerate(malformed):
            with self.subTest(verdict=verdict):
                calls = []
                class Adapter:
                    def __init__(self, *_args, **_kwargs): pass
                    def prompt(self, _prompt, **kwargs):
                        calls.append(kwargs.get('read_only', False))
                        return verdict if kwargs.get('read_only') else 'worker answer'
                with Authority(self.project) as owner:
                    with self.assertRaisesRegex(Blocked, 'reviewer returned invalid JSON|reviewer result|review blocker'):
                        Engine(owner, 'malformed-' + str(ordinal), admit({'tasks': [{'id': 'task', 'description': 'fixture'}]}),
                               EXECUTOR, adapter=Adapter).invoke()
                    chain = owner.store.review_chain('malformed-' + str(ordinal))
                self.assertEqual(calls, [False, True])
                self.assertTrue(chain['uncertain'])
                self.assertEqual(chain['fixing_round_count'], 0)

    def test_interrupted_review_is_uncertain_and_never_dispatches_fixer(self):
        calls = []
        class Adapter:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                calls.append(kwargs.get('read_only', False))
                if kwargs.get('read_only'):
                    raise KeyboardInterrupt
                return 'worker answer'
        with Authority(self.project) as owner:
            with self.assertRaises(KeyboardInterrupt):
                Engine(owner, 'interrupted-review', admit({'tasks': [{'id': 'task', 'description': 'fixture'}]}),
                       EXECUTOR, adapter=Adapter).invoke()
            chain = owner.store.review_chain('interrupted-review')
        self.assertEqual(calls, [False, True])
        self.assertTrue(chain['uncertain'])
        self.assertEqual(chain['fixing_round_count'], 0)

    def test_single_line_and_range_citations_reach_repair_unchanged(self):
        for location in ('717', '717-723'):
            with self.subTest(location=location):
                project, repair_inputs = self.project, []
                finding = f'owned.txt:{location} - synthetic defect [basis: correctness]'

                class Adapter:
                    reviews = 0
                    def __init__(self, *_args, **_kwargs): pass
                    def prompt(self, prompt, **kwargs):
                        if kwargs.get('read_only'):
                            Adapter.reviews += 1
                            return (json.dumps({'approved': False, 'findings': [finding]})
                                    if Adapter.reviews == 1 else '{"approved":true,"findings":[]}')
                        if 'Actionable findings:' in prompt:
                            repair_inputs.append(prompt)
                            kwargs['claim']('owned.txt')
                            project.joinpath('owned.txt').write_text('repaired\n')
                        else:
                            kwargs['claim']('owned.txt')
                            project.joinpath('owned.txt').write_text('initial\n')
                        return 'synthetic worker'

                contract = admit({'tasks': [{'id': 'dummy', 'description': 'synthetic',
                                             'owned_paths': ['owned.txt'],
                                             'checks': [['/bin/sh', '-c', 'test -f owned.txt']]}]})
                with Authority(project) as owner:
                    result = Engine(owner, 'citation-' + location, contract, EXECUTOR, adapter=Adapter,
                                    paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
                    chain = owner.store.review_chain('citation-' + location)
                self.assertEqual(result['status'], 'complete')
                self.assertEqual([(item['role'], item['state']) for item in chain['executions']],
                                 [('reviewer', 'rejected'), ('fixer', 'approved'), ('reviewer', 'approved')])
                self.assertEqual(chain['executions'][0]['findings'], [finding])
                self.assertEqual(len(repair_inputs), 1)
                self.assertIn(finding, repair_inputs[0])

    def test_actionable_rejection_repairs_once_then_fresh_rereview(self):
        project, calls = self.project, []
        project.joinpath('unrelated.txt').write_text('intervening\n')
        from coherence_workflow.store import git
        git(project, 'add', '--', 'unrelated.txt')
        git(project, 'commit', '-qm', 'unrelated integration context')
        unrelated = git(project, 'rev-parse', 'HEAD').decode().strip()
        class Adapter:
            reviews = 0
            fixer_prompts = 0
            instances = []
            def __init__(self, *_args, **_kwargs):
                Adapter.instances.append(self)
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    Adapter.reviews += 1
                    calls.append(('review', id(self), kwargs, _prompt))
                    return '```json\n{"approved":false,"findings":["owned.txt:1 - synthetic defect [basis: correctness]"]}\n```' if Adapter.reviews == 1 else '{"approved":true,"findings":[]}'
                if 'Actionable findings:' in _prompt:
                    Adapter.fixer_prompts += 1
                    kwargs['claim']('owned.txt')
                    project.joinpath('owned.txt').write_text('broken\n')
                elif '"id":"task"' in _prompt:
                    kwargs['claim']('owned.txt')
                    project.joinpath('owned.txt').write_text('initial\n')
                return 'synthetic worker'
        contract = admit({'review_base': self.base, 'tasks': [
            {'id': 'no-change', 'description': 'synthetic no-change'},
            {'id': 'task', 'description': 'synthetic', 'depends': ['no-change'], 'owned_paths': ['owned.txt'],
             'checks': [['/bin/sh', '-c', 'test -f owned.txt']]}
        ]})
        with Authority(project) as owner:
            result = Engine(owner, 'repaired', contract, EXECUTOR, adapter=Adapter,
                            paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            chain = owner.store.review_chain('repaired')
            observations = owner.store.monitor('repaired')['observations']
        self.assertEqual(result['status'], 'complete')
        self.assertEqual([(item['role'], item['state']) for item in chain['executions']],
                         [('reviewer', 'rejected'), ('fixer', 'approved'), ('reviewer', 'approved')])
        self.assertEqual(Adapter.fixer_prompts, 1)
        self.assertEqual(len(calls), 2)
        self.assertNotEqual(calls[0][1], calls[1][1])
        self.assertTrue(all(call[2]['read_only'] for call in calls))
        review_prompts = [call[3] for call in calls]
        self.assertTrue(all('Range: ' + self.base + '..' in prompt and 'Diff:' in prompt for prompt in review_prompts))
        self.assertTrue(all('do not reject unrelated context solely for task-path scope' in prompt and
                            'causal integration defects affecting the requested result remain blockers' in prompt.lower() and
                            'independently unrelated defects with their ownership/repair limit' in prompt
                            for prompt in review_prompts))
        self.assertIn('Intervening unrelated or unattributed integration context:', review_prompts[0])
        self.assertIn('commit ' + unrelated, review_prompts[0])
        self.assertIn('no retained task/repair attribution: ownership unknown', review_prompts[0])
        self.assertIn('no-change: no commit changes (recorded checkpoint ' + unrelated + ')', review_prompts[0])
        task_checkpoint = next(item for item in result['checkpoints'] if item['task_id'] == 'task')
        repair = next(item for item in chain['executions'] if item['role'] == 'fixer')
        repair_sha = repair['references']['commit']
        repair_parent = git(project, 'rev-parse', repair_sha + '^').decode().strip()
        self.assertIn('task task: commit ' + task_checkpoint['sha'] + ', parent ' + task_checkpoint['parent'] +
                      ', changed paths ["owned.txt"]', review_prompts[0])
        self.assertIn('repair ' + repair['execution_id'] + ': commit ' + repair_sha + ', parent ' + repair_parent +
                      ', changed paths ["owned.txt"]', review_prompts[1])

        if any(row['phase'] == 'review' and row['kind'] == 'started' and
               'selected_input_checkpoints' in json.loads(row['facts']) for row in observations):
            # Optional recording loss cannot alter the required chain.
            checkpoints = [row for row in observations if row['phase'] == 'checkpoint' and row['kind'] == 'passed'
                           and row['task_id'] in ('no-change', 'task')]
            first_review = next(row for row in observations
                                if row['phase'] == 'review' and row['kind'] == 'started'
                                and json.loads(row['facts'])['review_ordinal'] == 1)
            first_facts = json.loads(first_review['facts'])
            self.assertEqual(first_facts['selected_input_checkpoints'], [{
                'checkpoint_occurrence_id': checkpoint['occurrence_id'], 'task_id': checkpoint['task_id'],
                'producer_invocation_id': json.loads(checkpoint['facts'])['producer_invocation_id'],
                'correction_chain': json.loads(checkpoint['facts'])['correction_chain'],
            } for checkpoint in checkpoints])
            self.assertEqual(chain['executions'][0]['input_checkpoints'], first_facts['selected_input_checkpoints'])
            fixer_calls = [json.loads(row['facts']) for row in observations
                           if row['phase'] == 'worker' and row['kind'] == 'started'
                           and json.loads(row['facts']).get('role') == 'fixing_worker']
            self.assertEqual(len(fixer_calls), 1)
            self.assertEqual(fixer_calls[0]['trigger_execution_id'], chain['executions'][0]['execution_id'])
            self.assertEqual(fixer_calls[0]['correction_chain'], [fixer_calls[0]['invocation_id']])
            self.assertEqual(fixer_calls[0]['fixing_round'], 1)

    def test_reviewer_context_and_model_survive_repair_and_check_correction(self):
        project, calls, instances = self.project, [], []
        case = self
        class Adapter:
            def __init__(self, _project, executor, **_kwargs):
                self.executor = executor
                self.saved_session = None
                instances.append(self)
            def prompt(self, prompt, **kwargs):
                calls.append((self, kwargs))
                if kwargs.get('read_only'):
                    case.assertIsNone(self.saved_session)  # Both reviews start fresh.
                    if 'owned.txt' not in project.joinpath('owned.txt').read_text():
                        self.saved_session = {'id': 'review-context', 'file': '/private/review.jsonl',
                                              'compatibility': {'readOnly': True}}
                        return '{"approved":false,"findings":["owned.txt:1 - defect [basis: correctness]"]}'
                    return '{"approved":true,"findings":[]}'
                if 'Actionable findings:' in prompt or 'Actual failed attempt:' in prompt:
                    case.assertIn('Current execution authority:', prompt)
                    case.assertIn('Historical planning-only', prompt)
                    case.assertIn('explicit manual gates', prompt)
                    case.assertIn('Routine authority:', prompt)
                    case.assertIn('never authorizes global installs', prompt)
                    case.assertIn('concise correction plan', prompt)
                    case.assertIn('directly related adverse failure paths', prompt)
                    case.assertIn('integrated result against the original acceptance', prompt)
                    case.assertIn('Original task contracts:', prompt)
                    case.assertIn('Paid application/test APIs approved for this unchanged run only', prompt)
                    case.assertIn('not independent acceptance', prompt)
                    case.assertIn('Finish the assigned implementation and worker-owned semantic/manual acceptance', prompt)
                    case.assertIn('The runner executes/reruns configured checks, creates the focused checkpoint', prompt)
                    case.assertIn('it does not own all semantic/manual acceptance or the reviewer verdict', prompt)
                    case.assertIn('Pending runner stages alone do not require an unsuccessful status', prompt)
                if 'Actionable findings:' in prompt:
                    case.assertEqual(self.saved_session['id'], 'review-context')
                    case.assertTrue(kwargs['review_repair'])
                    case.assertIn('correction plan', prompt)
                    self.saved_session = {**self.saved_session, 'compatibility': {'readOnly': False}}
                    kwargs['claim']('owned.txt')
                    project.joinpath('owned.txt').write_text('broken\n')
                elif 'Actual failed attempt:' in prompt:
                    case.assertNotIn('review_repair', kwargs)
                    project.joinpath('owned.txt').write_text('owned.txt fixed\n')
                else:
                    kwargs['claim']('owned.txt')
                    project.joinpath('owned.txt').write_text('initial\n')
                return 'fixture'
        contract = admit([{'id': 'task', 'description': 'fixture', 'owned_paths': ['owned.txt'],
                           'checks': [['/bin/sh', '-c', '! grep -q broken owned.txt']]}])
        with Authority(project) as owner:
            result = Engine(owner, 'warm-review', contract, EXECUTOR, adapter=Adapter,
                            paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            public = owner.store.review_chain('warm-review')
            private = owner.store.review_chain('warm-review', private=True)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(instances), 3)  # Worker, reviewer/repairer, final reviewer.
        self.assertIs(calls[1][0], calls[2][0])
        self.assertIs(calls[2][0], calls[3][0])
        self.assertEqual(calls[2][0].executor, EXECUTOR['reviewer'])
        self.assertIsNot(calls[1][0], calls[4][0])
        self.assertTrue(calls[4][1]['read_only'])
        self.assertNotIn('saved_session', public['executions'][0]['references'])
        self.assertEqual(private['executions'][0]['references']['saved_session']['id'], 'review-context')

    def test_final_rejection_stops_after_two_reviews_and_one_fixer(self):
        class Adapter:
            reviews = 0
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    Adapter.reviews += 1
                    return ('{"approved":false,"findings":["owned.txt:1 - first [basis: correctness]"]}' if Adapter.reviews == 1
                            else '{"approved":false,"findings":["owned.txt:2 - final [basis: correctness]"]}')
                return 'synthetic worker'
        with Authority(self.project) as owner:
            with self.assertRaisesRegex(Blocked, 'owner authorization unavailable'):
                Engine(owner, 'final-rejection', admit({'tasks': [{'id': 'dummy', 'description': 'synthetic'}]}),
                       EXECUTOR, adapter=Adapter, paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            chain = owner.store.review_chain('final-rejection')
        self.assertEqual((chain['review_count'], chain['fixing_round_count']), (2, 1))
        self.assertEqual(chain['executions'][-1]['findings'], ['owned.txt:2 - final [basis: correctness]'])

    def test_unrecoverable_fixer_failure_never_launches_second_review(self):
        class Adapter:
            reviews = 0
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    Adapter.reviews += 1
                    return '{"approved":false,"findings":["owned.txt:1 - defect [basis: correctness]"]}'
                if 'Actionable findings:' in _prompt:
                    raise Blocked('synthetic fixer failure')
                return 'synthetic worker'
        with Authority(self.project) as owner:
            with self.assertRaisesRegex(Blocked, 'synthetic fixer failure'):
                Engine(owner, 'fixer-failure', admit({'tasks': [{'id': 'dummy', 'description': 'synthetic'}]}),
                       EXECUTOR, adapter=Adapter, paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            from coherence_workflow.metric_artifacts import read_artifact
            usage = [row for row in read_artifact(self.project, 'fixer-failure')['records']
                     if row['role'] == 'fixing_worker']
            self.assertEqual([(row['outcome'], row['after']) for row in usage], [('failed', None)])
            chain = owner.store.review_chain('fixer-failure')
            observations = owner.store.monitor('fixer-failure')['observations']
        self.assertEqual(Adapter.reviews, 1)
        self.assertEqual([(item['role'], item['state']) for item in chain['executions']],
                         [('reviewer', 'rejected'), ('fixer', 'failed')])
        failed = next(json.loads(row['facts']) for row in observations
                      if row['phase'] == 'worker' and row['kind'] == 'failed')
        terminal = next(json.loads(row['facts']) for row in observations
                        if row['phase'] == 'terminal' and row['kind'] == 'failed')
        self.assertEqual(terminal['stopped_by_invocation_id'], failed['invocation_id'])

    def test_new_policy_authorizes_one_later_pair_and_fresh_full_range_review(self):
        calls, decisions = [], []
        class Adapter:
            reviews = 0
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    Adapter.reviews += 1
                    calls.append(('review', id(self)))
                    if Adapter.reviews < 3:
                        return '{"approved":false,"findings":["owned.txt:1 - defect [basis: correctness]"]}'
                    return '{"approved":true,"findings":[]}'
                calls.append(('fix-or-worker', id(self)))
                return 'fixture'
        def owner_question(question, **kwargs):
            decisions.append((question, kwargs))
            return 'yes'
        contract = admit({'tasks': [{'id': 'task', 'description': 'fixture'}]})
        with Authority(self.project) as owner:
            result = Engine(owner, 'owner-pair-lifecycle', contract, EXECUTOR, adapter=Adapter,
                            question=owner_question).invoke()
            chain = owner.store.review_chain('owner-pair-lifecycle', private=True)
            saved = owner.store.input('owner-pair-lifecycle')
            grants = [json.loads(row['details']) for row in owner.store.db.execute(
                "SELECT details FROM execution_history WHERE run_id='owner-pair-lifecycle' AND kind='review_pair_grant'")]
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(saved['authority']['review_policy'], 'owner-pair-v1')
        self.assertEqual([(item['role'], item['state']) for item in chain['executions']], [
            ('reviewer', 'rejected'), ('fixer', 'approved'), ('reviewer', 'rejected'),
            ('fixer', 'approved'), ('reviewer', 'approved')])
        self.assertEqual([item['review_ordinal'] for item in chain['executions'] if item['role'] == 'reviewer'], [1, 2, 3])
        self.assertEqual([item['fixing_round'] for item in chain['executions'] if item['role'] == 'fixer'], [1, 2])
        self.assertEqual(len(decisions), 1)
        self.assertTrue(decisions[0][1]['owner_only'])
        self.assertEqual(len(grants), 1)
        self.assertEqual(grants[0]['rejecting_execution_id'], chain['executions'][2]['execution_id'])
        self.assertTrue(all(item['references']['base'] == self.base for item in chain['executions'] if item['role'] == 'reviewer'))


class ReviewBoundaryRegressionTests(ProjectTest):
    """Exercise the actual store/engine boundary with disposable Git and reopen."""
    _rejection = OwnerPairPrimitiveTests._rejection
    def test_dispatch_requires_causal_grant_and_single_pair(self):
        with Authority(self.project) as owner:
            store = owner.store
            store.start('pair', self.base, authority={'review_policy': 'owner-pair-v1'})
            self._rejection(store)
            kwargs = dict(role='fixer', review_ordinal=2, fixing_round=2,
                          trigger_execution_id='review-2', predecessor_execution_id='review-2',
                          review_base=self.base, review_head=self.base)
            with self.assertRaisesRegex(Blocked, 'grant/reservation'):
                store.review_dispatch('pair', 'unapproved', **kwargs)
            grant = dict(rejecting_execution_id='review-2', review_base=self.base, review_head=self.base,
                         original_scope=store.review_scope('pair'), fixer_execution_id='fix-2', reviewer_execution_id='review-3')
            with self.assertRaisesRegex(Blocked, 'scope'):
                store.authorize_owner_pair('pair', 'wrong-scope', **{**grant, 'original_scope': 'different'})
            store.authorize_owner_pair('pair', 'grant', **grant)
            with self.assertRaisesRegex(Blocked, 'already authorized'):
                store.authorize_owner_pair('pair', 'duplicate', **{**grant, 'fixer_execution_id': 'other-fix', 'reviewer_execution_id': 'other-review'})
            with self.assertRaisesRegex(Blocked, 'grant/reservation'):
                store.review_dispatch('pair', 'fix-2', **kwargs)
            store.reserve_owner_pair_fixer('pair', 'grant', **{key: grant[key] for key in
                ('rejecting_execution_id', 'review_base', 'review_head', 'original_scope')})
            with self.assertRaisesRegex(Blocked, 'grant/reservation'):
                store.review_dispatch('pair', 'wrong-fixer', **kwargs)
            with self.assertRaisesRegex(Blocked, 'causal'):
                store.review_dispatch('pair', 'fix-2', **{**kwargs, 'predecessor_execution_id': 'review-1'})
            store.review_dispatch('pair', 'fix-2', **kwargs)
            with self.assertRaisesRegex(Blocked, 'successful fixer'):
                store.reserve_owner_pair_reviewer('pair', 'grant', fixer_execution_id='fix-2')
            store.review_outcome('pair', 'fix-2', 'failed', findings=[], suggestions=['optional naming cleanup'],
                                 references={'base': self.base, 'head': self.base, 'saved_session': 'PRIVATE-SAVED-SESSION'})
            with self.assertRaisesRegex(Blocked, 'started, failed, or completed'):
                store.reserve_owner_pair_fixer('pair', 'grant', **{key: grant[key] for key in
                    ('rejecting_execution_id', 'review_base', 'review_head', 'original_scope')})
            with self.assertRaisesRegex(Blocked, 'causal'):
                store.review_dispatch('pair', 'review-3', review_ordinal=3, fixing_round=2,
                    trigger_execution_id='fix-2', predecessor_execution_id='fix-2', review_base=self.base, review_head=self.base)
        self.assertEqual(status(self.project, 'pair')['review_authorization']['next_stage'], 'blocked')
        from coherence_workflow.cli import main
        for action in ('status', 'history'):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main([action, '--project', str(self.project), '--run', 'pair']), 0)
            rendered = output.getvalue()
            observed = json.loads(rendered)
            self.assertEqual(observed['review_authorization']['next_stage'], 'blocked')
            self.assertEqual(observed['review_chain']['executions'][-1]['suggestions'], ['optional naming cleanup'])
            self.assertEqual(observed['review_chain']['executions'][-1]['findings'], [])
            self.assertNotIn('PRIVATE-SAVED-SESSION', rendered)

    def test_compatible_findings_need_no_literal_basis_suffix(self):
        finding = 'file.py:12 - dereferencing the missing record crashes requests'
        self.assertEqual(Engine._review_value(json.dumps({'approved': False, 'findings': [finding]})),
                         {'approved': False, 'findings': [finding], 'suggestions': []})

    def test_owner_only_transport_never_retries_as_routine(self):
        for mode in ('legacy', 'internal-error', 'no', '', 'cancel', 'ambiguous'):
            run, calls, questions = 'owner-' + mode, [], []
            class Adapter:
                reviews = 0
                def __init__(self, *_args, **_kwargs): pass
                def prompt(self, _prompt, **kwargs):
                    calls.append(kwargs.get('read_only', False))
                    if kwargs.get('read_only'):
                        return '{"approved":false,"findings":["owned.txt:1 - requests crash on missing record"]}'
                    return 'fixture'
            def question(text, **kwargs):
                questions.append(kwargs)
                if mode == 'internal-error':
                    raise TypeError('owner capability failed internally')
                return mode
            if mode == 'legacy':
                def question(text):
                    questions.append({})
                    return 'yes'  # A routine callback must never be invoked for consent.
            with Authority(self.project) as owner:
                with self.assertRaisesRegex(Blocked, 'owner authorization unavailable|did not authorize'):
                    Engine(owner, run, admit([{'id': 'task', 'description': 'fixture'}]), EXECUTOR,
                           adapter=Adapter, question=question).invoke()
                self.assertEqual(owner.store.review_chain(run)['fixing_round_count'], 1)
                self.assertEqual(owner.store.db.execute("SELECT count(*) FROM execution_history WHERE run_id=? AND kind='review_pair_grant'", (run,)).fetchone()[0], 0)
            self.assertEqual(calls, [False, True, False, True])
            self.assertEqual(len(questions), 0 if mode == 'legacy' else 1)
            if questions:
                self.assertTrue(questions[0]['owner_only'])

    def test_additional_round_reopen_boundaries_retain_exact_pair_and_effects(self):
        # Each subcase has its own run and chain; a simulated process death suppresses
        # exception-handler outcome writes, just as an actual killed process would.
        from coherence_workflow.git_effects import FocusedGit
        from coherence_workflow.store import git
        class ProcessDeath(BaseException): pass
        boundaries = ('authorized', 'reserved', 'dispatched', 'invocation_started', 'returned',
                      'check_started', 'checks_passed', 'commit', 'checkpoint_passed', 'fixer_complete', 'reviewer_reserved',
                      'review_complete', 'missing_facts', 'source_drift', 'commit_drift',
                      'checkpoint_started', 'checkpoint_unselected_drift', 'checkpoint_unselected_delete')
        for boundary in boundaries:
            with self.subTest(boundary=boundary):
                # Use a separate disposable repo per scenario, including unrelated index bytes.
                case = ProjectTest()
                case.setUp()
                self.addCleanup(case.doCleanups)
                project, base = case.project, case.base
                calls, questions, crashed = [], [], [False]
                checkpoint_start = boundary in ('checkpoint_started', 'checkpoint_unselected_drift',
                                                'checkpoint_unselected_delete')
                contract = admit([{'id': 'original', 'description': 'fixture',
                                   'owned_paths': ['owned.txt', 'STATE.md'],
                                   'checks': [['/bin/sh', '-c', 'test -s owned.txt']]}])
                class Adapter:
                    reviews = 0
                    fixes = 0
                    def __init__(self, *_args, **_kwargs): pass
                    def prompt(self, prompt, **kwargs):
                        if kwargs.get('read_only'):
                            Adapter.reviews += 1
                            calls.append(('review', Adapter.reviews, prompt))
                            return ('{"approved":false,"findings":["owned.txt:1 - crashes on adjacent missing input"]}'
                                    if Adapter.reviews < 3 else '{"approved":true,"findings":[],"suggestions":["optional cleanup"]}')
                        if 'Actionable findings:' in prompt:
                            Adapter.fixes += 1
                            calls.append(('fix', Adapter.fixes, prompt))
                            kwargs['claim']('owned.txt')
                            project.joinpath('owned.txt').write_text('repair-' + str(Adapter.fixes) + '\n')
                            if checkpoint_start and Adapter.fixes == 2:
                                # Selected for repair, but unchanged at checkpoint intent.
                                kwargs['claim']('STATE.md')
                                project.joinpath('STATE.md').write_text('custom\n')
                        else:
                            calls.append(('worker', 0, prompt))
                            kwargs['claim']('owned.txt')
                            project.joinpath('owned.txt').write_text('initial\n')
                        return 'PRIVATE repair answer'
                def question(text, **kwargs):
                    questions.append(kwargs)
                    return 'yes'
                def die():
                    crashed[0] = True
                    raise ProcessDeath(boundary)
                project.joinpath('other.txt').write_text('unrelated staged sentinel\n')
                git(project, 'add', '--', 'other.txt')
                project.joinpath('untracked-sentinel').write_text('untracked sentinel\n')
                with Authority(project) as owner:
                    store = owner.store
                    original_history, original_dispatch = store.history, store.review_dispatch
                    original_outcome = store.review_outcome
                    original_authorize, original_reserve = store.authorize_owner_pair, store.reserve_owner_pair_fixer
                    original_reviewer_reserve = store.reserve_owner_pair_reviewer
                    original_checkpoint = FocusedGit.checkpoint
                    def is_extra(execution_id):
                        row = store.db.execute('SELECT fixing_round FROM execution_review_executions WHERE run_id=? AND execution_id=?', ('recovery', execution_id)).fetchone()
                        return row is not None and row['fixing_round'] == 2
                    def history(run, task, kind, state, details):
                        if crashed[0]:
                            raise ProcessDeath(boundary)
                        extra = is_extra(details.get('execution_id'))
                        if extra and boundary == 'missing_facts' and (kind, state) == ('fixer_invocation', 'returned'):
                            details = {key: value for key, value in details.items() if key != 'paths'}
                        result = original_history(run, task, kind, state, details)
                        names = {('fixer_invocation', 'started'): 'invocation_started',
                                 ('fixer_invocation', 'returned'): 'returned', ('fixer_checks', 'passed'): 'checks_passed',
                                 ('fixer_checks', 'started'): 'check_started', ('fixer_checkpoint', 'passed'): 'checkpoint_passed',
                                 ('fixer_checkpoint', 'started'): 'checkpoint_started'}
                        selected = ('checkpoint_started' if checkpoint_start else
                                    'returned' if boundary in ('missing_facts', 'source_drift') else boundary)
                        if not crashed[0] and extra and names.get((kind, state)) == selected:
                            die()
                        return result
                    def dispatch(run, execution_id, **kwargs):
                        result = original_dispatch(run, execution_id, **kwargs)
                        if not crashed[0] and boundary == 'dispatched' and kwargs.get('role') == 'fixer' and kwargs['fixing_round'] == 2:
                            die()
                        return result
                    def outcome(run, execution_id, state, **kwargs):
                        if crashed[0]:
                            raise ProcessDeath(boundary)
                        result = original_outcome(run, execution_id, state, **kwargs)
                        if is_extra(execution_id) and state == 'approved':
                            role = store.db.execute('SELECT role FROM execution_review_executions WHERE execution_id=?', (execution_id,)).fetchone()['role']
                            if boundary == ('fixer_complete' if role == 'fixer' else 'review_complete'):
                                die()
                        return result
                    def authorize(*args, **kwargs):
                        result = original_authorize(*args, **kwargs)
                        if boundary == 'authorized': die()
                        return result
                    def reserve(*args, **kwargs):
                        result = original_reserve(*args, **kwargs)
                        if boundary == 'reserved': die()
                        return result
                    def reserve_reviewer(*args, **kwargs):
                        result = original_reviewer_reserve(*args, **kwargs)
                        if boundary == 'reviewer_reserved': die()
                        return result
                    def checkpoint(focused):
                        result = original_checkpoint(focused)
                        if boundary in ('commit', 'commit_drift') and focused.task['id'].startswith('fix-') and Adapter.fixes == 2:
                            die()
                        return result
                    with patch.object(store, 'history', side_effect=history), patch.object(store, 'review_dispatch', side_effect=dispatch), \
                         patch.object(store, 'review_outcome', side_effect=outcome), patch.object(store, 'authorize_owner_pair', side_effect=authorize), \
                         patch.object(store, 'reserve_owner_pair_fixer', side_effect=reserve), \
                         patch.object(store, 'reserve_owner_pair_reviewer', side_effect=reserve_reviewer), patch.object(FocusedGit, 'checkpoint', checkpoint):
                        with self.assertRaises(ProcessDeath):
                            Engine(owner, 'recovery', contract, EXECUTOR, adapter=Adapter, question=question).invoke()
                    before = git(project, 'rev-parse', 'HEAD').decode().strip()
                    initial_checkpoints = store.completed_checkpoints('recovery')
                    initial_grants = [row['details'] for row in store.db.execute("SELECT details FROM execution_history WHERE kind='review_pair_grant'")]
                    if checkpoint_start:
                        intent = json.loads(store.db.execute(
                            "SELECT details FROM execution_history WHERE kind='fixer_checkpoint' AND state='started' ORDER BY seq DESC LIMIT 1"
                        ).fetchone()['details'])
                        returned = json.loads(store.db.execute(
                            "SELECT details FROM execution_history WHERE kind='fixer_invocation' AND state='returned' ORDER BY seq DESC LIMIT 1"
                        ).fetchone()['details'])
                        self.assertEqual(intent['paths'], ['owned.txt'])
                        self.assertEqual(returned['paths'], ['STATE.md', 'owned.txt'])
                if boundary == 'source_drift':
                    project.joinpath('owned.txt').write_text('unrelated later bytes\n')
                if boundary == 'checkpoint_unselected_drift':
                    project.joinpath('STATE.md').write_text('unrelated later bytes\n')
                if boundary == 'checkpoint_unselected_delete':
                    project.joinpath('STATE.md').unlink()
                if boundary == 'commit_drift':
                    git(project, 'commit', '--allow-empty', '--only', '-m', 'incoming unrelated commit')
                with Authority(project) as owner:
                    engine = Engine(owner, 'recovery', contract, EXECUTOR, adapter=Adapter, question=question, resume=True)
                    blocked = {'invocation_started': 'uncertain or failed', 'check_started': 'check completion is uncertain',
                               'missing_facts': 'missing owned-path', 'source_drift': 'source bytes drifted',
                               'commit_drift': 'commit effects are missing or uncertain',
                               'checkpoint_unselected_drift': 'source bytes drifted',
                               'checkpoint_unselected_delete': 'source bytes drifted'}
                    if boundary in blocked:
                        before_resume_head = git(project, 'rev-parse', 'HEAD').decode().strip()
                        before_calls = len(calls)
                        with self.assertRaisesRegex(Blocked, blocked[boundary]):
                            engine.invoke()
                        self.assertEqual(len(calls), before_calls)
                        self.assertEqual(Adapter.fixes, 1 if boundary == 'invocation_started' else 2)
                        if boundary == 'invocation_started':
                            self.assertEqual(status(project, 'recovery')['review_authorization']['next_stage'], 'blocked')
                        self.assertEqual(git(project, 'rev-parse', 'HEAD').decode().strip(), before_resume_head)
                        if boundary == 'source_drift':
                            self.assertEqual(project.joinpath('owned.txt').read_text(), 'unrelated later bytes\n')
                        if boundary == 'checkpoint_unselected_drift':
                            self.assertEqual(project.joinpath('STATE.md').read_text(), 'unrelated later bytes\n')
                        if boundary == 'checkpoint_unselected_delete':
                            self.assertFalse(project.joinpath('STATE.md').exists())
                    else:
                        result = engine.invoke()
                        self.assertEqual(result['status'], 'complete')
                        self.assertEqual((Adapter.fixes, Adapter.reviews, len(questions)), (2, 3, 1))
                        if boundary in ('commit', 'checkpoint_passed', 'fixer_complete', 'reviewer_reserved', 'review_complete'):
                            self.assertEqual(result['sha'], before)
                        chain = owner.store.review_chain('recovery')
                        self.assertEqual((chain['review_count'], chain['fixing_round_count']), (3, 2))
                        self.assertEqual(chain['executions'][-1]['references'], {'base': base, 'head': result['sha']})
                        self.assertEqual(status(project, 'recovery')['review_authorization']['next_stage'], 'complete')
                        self.assertIn('Range: ' + base + '..' + result['sha'], [entry[2] for entry in calls if entry[:2] == ('review', 3)][0])
                        self.assertEqual(git(project, 'rev-list', '--count', base + '..' + result['sha']).decode().strip(), '3')
                    self.assertEqual(owner.store.completed_checkpoints('recovery'), initial_checkpoints)
                    self.assertEqual([row['details'] for row in owner.store.db.execute("SELECT details FROM execution_history WHERE kind='review_pair_grant'")], initial_grants)
                self.assertEqual(project.joinpath('other.txt').read_text(), 'unrelated staged sentinel\n')
                self.assertEqual(git(project, 'diff', '--cached', '--name-only').decode().strip(), 'other.txt')
                self.assertEqual(project.joinpath('untracked-sentinel').read_text(), 'untracked sentinel\n')


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
            from coherence_workflow.metric_artifacts import read_artifact
            usage = [row for row in read_artifact(self.project, 'fix-run')['records']
                     if row['role'] == 'fixing_worker']
            self.assertEqual(len(usage), 2)
            self.assertEqual(len({row['invocation_id'] for row in usage}), 2)
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
