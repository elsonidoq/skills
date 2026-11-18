"""Offline explicit recovery of an initial review format failure."""
import json
from unittest.mock import patch

from coherence_workflow.engine import Engine, _ReviewFormat
from coherence_workflow.intake import admit
from coherence_workflow.graph import graph_saver, task_graph
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-review', 'effort': 'medium'}}


class ReviewFormatRecoveryTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.calls = []
        self.artifact = self.root / 'review.jsonl'
        self.verdict = {'approved': False, 'findings': ['owned.txt:1-2 and 4-5 - invalid data crashes requests',
                         'owned.txt:7 - missing value corrupts output'] +
                         [f'owned.txt:{n} and {n+1}-{n+2} - defect {n} breaks output' for n in range(10, 17)],
                        'coverage': ['producer checked'],
                        'coverage_gaps': ['consumer untested'], 'suggestions': ['rename later']}
        self.contract = admit({'tasks': [{'id': 'task', 'description': 'fixture', 'owned_paths': ['owned.txt']}]})

    def start_failed(self, delete_path=None):
        fixture = self
        class Adapter:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                fixture.calls.append(('review' if kwargs.get('read_only') else 'writer', prompt))
                if kwargs.get('read_only'):
                    entries = [{'type': 'session', 'id': 'session', 'cwd': str(fixture.project)},
                        {'type': 'message', 'id': 'user', 'parentId': None, 'message': {'role': 'user',
                         'content': [{'type': 'text', 'text': prompt}]}},
                        {'type': 'message', 'id': 'answer', 'parentId': 'user', 'message': {'role': 'assistant',
                         'stopReason': 'stop', 'content': [{'type': 'thinking', 'thinking': 'review reasoning'},
                                                             {'type': 'text', 'text': json.dumps(fixture.verdict)}]}}]
                    fixture.artifact.write_text(''.join(json.dumps(x) + '\n' for x in entries))
                    return json.dumps(fixture.verdict)
                kwargs['claim']('owned.txt')
                fixture.project.joinpath('owned.txt').write_text('task output\n')
                if delete_path:
                    kwargs['claim'](delete_path)
                    fixture.project.joinpath(delete_path).unlink()
                return 'done'
        parse = Engine._review_value
        def old_parser(text, **kwargs):
            value = parse(text, **kwargs)
            if any(' and ' in finding for finding in value['findings']):
                raise _ReviewFormat('old parser rejected compound location')
            return value
        with Authority(self.project) as owner:
            with patch.object(Engine, '_review_value', side_effect=old_parser):
                with self.assertRaises(_ReviewFormat):
                    Engine(owner, 'fixture', self.contract, EXECUTOR, adapter=Adapter).invoke()
            chain = owner.store.review_chain('fixture', private=True)
            self.assertTrue(chain['uncertain'])
            self.assertEqual(chain['executions'][0]['attempt_count'], 2)
        return Adapter

    def test_graph_explicit_format_recovery_continues_without_replaying_review(self):
        fixture = self
        class Adapter:
            def __init__(self, *_args, **_kwargs):
                self.saved_session = None
            def prompt(self, prompt, **kwargs):
                fixture.calls.append(('review' if kwargs.get('read_only') else 'writer', prompt))
                if kwargs.get('read_only'):
                    if sum(kind == 'review' for kind, _ in fixture.calls) == 1:
                        entries = [{'type': 'session', 'id': 'session', 'cwd': str(fixture.project)},
                            {'type': 'message', 'id': 'user', 'parentId': None, 'message': {'role': 'user', 'content': [{'type': 'text', 'text': prompt}]}},
                            {'type': 'message', 'id': 'answer', 'parentId': 'user', 'message': {'role': 'assistant', 'stopReason': 'stop', 'content': [{'type': 'text', 'text': json.dumps(fixture.verdict)}]}}]
                        fixture.artifact.write_text(''.join(json.dumps(x) + '\n' for x in entries))
                        return json.dumps(fixture.verdict)
                    return json.dumps({'approved': True, 'findings': [], 'coverage': ['producer and consumer checked'], 'coverage_gaps': []})
                kwargs['claim']('owned.txt')
                fixture.project.joinpath('owned.txt').write_text('repaired\n' if 'Continue the rejecting review' in prompt else 'task output\n')
                return 'done'
        parse = Engine._review_value
        def old_parser(text, **kwargs):
            value = parse(text, **kwargs)
            if any(' and ' in finding for finding in value['findings']):
                raise _ReviewFormat('old parser rejected compound location')
            return value
        config = {'configurable': {'thread_id': 'graph-format'}}
        with Authority(self.project) as owner:
            owner.store.start('graph-format', self.base, contract=self.contract, executor=EXECUTOR,
                authority={'review_policy': 'owner-pair-v1', 'routine_authority': True}, review_base=self.base)
            engine = Engine(owner, 'graph-format', self.contract, EXECUTOR, adapter=Adapter)
            with graph_saver(owner) as saver, patch.object(Engine, '_review_value', side_effect=old_parser):
                with self.assertRaises(_ReviewFormat):
                    task_graph(engine, saver, review=True).invoke({}, config, durability='sync')
        with Authority(self.project) as owner:
            engine = Engine(owner, 'graph-format', self.contract, EXECUTOR, adapter=Adapter, resume=True,
                            question=lambda _: str(self.artifact))
            with graph_saver(owner) as saver:
                result = task_graph(engine, saver, review=True).invoke(None, config, durability='sync')
            chain = owner.store.review_chain('graph-format', private=True)['executions']
        self.assertEqual(result['result']['status'], 'complete')
        self.assertEqual([item['state'] for item in chain], ['rejected', 'approved', 'approved'])
        self.assertEqual([kind for kind, _ in self.calls], ['writer', 'review', 'writer', 'review'])
        self.assertIn('consumer untested', self.calls[-1][1])

    def test_explicit_recovery_preserves_failure_and_continues_existing_lifecycle(self):
        self.start_failed()
        self.write('other.txt', 'staged owner bytes\n')
        git(self.project, 'add', '--', 'other.txt')
        self.write('other.txt', 'working owner bytes\n')
        staged = git(self.project, 'show', ':other.txt')
        fixture = self
        class Adapter:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                fixture.calls.append(('review' if kwargs.get('read_only') else 'fixer', prompt))
                if kwargs.get('read_only'):
                    return json.dumps({'approved': True, 'findings': [], 'coverage': ['producer and consumer checked'],
                                       'coverage_gaps': []})
                kwargs['claim']('owned.txt')
                fixture.project.joinpath('owned.txt').write_text('repaired\n')
                return 'repaired'
        with Authority(self.project) as owner:
            owner.store.resume('fixture')
            result = Engine(owner, 'fixture', self.contract, EXECUTOR, adapter=Adapter, resume=True,
                            question=lambda _: str(self.artifact)).invoke()
            chain = owner.store.review_chain('fixture', private=True)
            attempts = [row['state'] for row in owner.store.db.execute(
                'select state from execution_review_attempts where run_id=? and execution_id=? order by seq',
                ('fixture', chain['executions'][0]['execution_id']))]
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(git(self.project, 'show', ':other.txt'), staged)
        self.assertEqual(self.project.joinpath('other.txt').read_text(), 'working owner bytes\n')
        self.assertEqual(attempts, ['dispatched', 'failed', 'rejected'])
        first = chain['executions'][0]
        self.assertEqual(first['findings'][-1], self.verdict['findings'])
        self.assertEqual(first['suggestions'][-1], self.verdict['suggestions'])
        self.assertEqual(first['references']['review_summary'], {k: self.verdict[k] for k in ('coverage', 'coverage_gaps')})
        self.assertEqual([kind for kind, _ in self.calls], ['writer', 'review', 'fixer', 'review'])
        self.assertIn('consumer untested', self.calls[-1][1])
        self.assertEqual([x['role'] for x in chain['executions']], ['reviewer', 'fixer', 'reviewer'])

    def test_unrelated_tracked_and_index_bytes_survive_actual_recovery(self):
        self.start_failed()
        self.write('other.txt', 'staged owner bytes\n')
        git(self.project, 'add', '--', 'other.txt')
        self.write('other.txt', 'working owner bytes\n')
        before = git(self.project, 'show', ':other.txt')
        with Authority(self.project) as owner:
            owner.store.resume('fixture')
            chain = owner.store.review_chain('fixture', private=True)
            engine = Engine(owner, 'fixture', self.contract, EXECUTOR, resume=True,
                            question=lambda _: str(self.artifact))
            self.assertTrue(engine._recover_format_rejection(chain, self.base))
            recovered = owner.store.review_chain('fixture', private=True)['executions'][0]
        self.assertEqual(recovered['findings'][-1], self.verdict['findings'])
        self.assertEqual(recovered['references']['review_summary'],
                         {k: self.verdict[k] for k in ('coverage', 'coverage_gaps')})
        self.assertEqual(git(self.project, 'show', ':other.txt'), before)
        self.assertEqual(self.project.joinpath('other.txt').read_text(), 'working owner bytes\n')
        self.assertEqual([kind for kind, _ in self.calls], ['writer', 'review'])

    def test_reviewed_target_drift_in_worktree_or_index_is_refused(self):
        self.start_failed()
        with Authority(self.project) as owner:
            owner.store.resume('fixture')
        for mode in ('working', 'index', 'during_question'):
            with self.subTest(mode=mode):
                if mode != 'during_question':
                    self.write('owned.txt', 'drift\n')
                    if mode == 'index':
                        git(self.project, 'add', '--', 'owned.txt')
                        self.write('owned.txt', 'task output\n')
                def question(_):
                    if mode == 'during_question':
                        self.write('owned.txt', 'drift\n')
                    return str(self.artifact)
                with Authority(self.project) as owner:
                    chain = owner.store.review_chain('fixture', private=True)
                    with self.assertRaisesRegex(Blocked, 'target has changes'):
                        Engine(owner, 'fixture', self.contract, EXECUTOR, resume=True,
                               question=question)._recover_format_rejection(chain, self.base)
                if mode == 'index':
                    git(self.project, 'restore', '--staged', '--', 'owned.txt')
                self.write('owned.txt', 'task output\n')

    def test_unchanged_range_but_dirty_additional_owned_path_is_refused(self):
        self.contract = admit({'tasks': [{'id': 'task', 'description': 'fixture',
                                          'owned_paths': ['owned.txt', 'other.txt']}]})
        self.start_failed()
        self.write('other.txt', 'owner collision\n')
        with Authority(self.project) as owner:
            owner.store.resume('fixture')
            chain = owner.store.review_chain('fixture', private=True)
            with self.assertRaisesRegex(Blocked, 'target has changes in other.txt'):
                Engine(owner, 'fixture', self.contract, EXECUTOR, resume=True,
                       question=lambda _: str(self.artifact))._recover_format_rejection(chain, self.base)

    def test_deleted_review_target_refuses_parent_file_or_symlink_not_nearby_name(self):
        parent = self.project / 'protected'
        parent.mkdir()
        (parent / 'file').write_text('tracked before deletion\n')
        git(self.project, 'add', '--', 'protected/file')
        git(self.project, 'commit', '-qm', 'fixture protected file')
        self.base = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        self.contract = admit({'tasks': [{'id': 'task', 'description': 'fixture',
                                          'owned_paths': ['owned.txt', 'protected/file']}]})
        self.start_failed(delete_path='protected/file')
        if parent.exists():
            parent.rmdir()
        with Authority(self.project) as owner:
            owner.store.resume('fixture')
            chain = owner.store.review_chain('fixture', private=True)
            engine = Engine(owner, 'fixture', self.contract, EXECUTOR, resume=True,
                            question=lambda _: '')
            nearby = self.project / 'protected-nearby'
            nearby.write_text('unrelated\n')
            with self.assertRaisesRegex(Blocked, 'needs the exact completed reviewer transcript'):
                engine._recover_format_rejection(chain, self.base)
            for mode in ('file', 'symlink'):
                with self.subTest(mode=mode):
                    if mode == 'file':
                        parent.write_text('replacement\n')
                    else:
                        parent.symlink_to('protected-nearby')
                    with self.assertRaisesRegex(Blocked, 'target has changes in protected;'):
                        engine._recover_format_rejection(chain, self.base)
                    parent.unlink()
            self.assertEqual(nearby.read_text(), 'unrelated\n')
            self.assertTrue(owner.store.review_chain('fixture')['uncertain'])

    def test_single_text_only_transcript_remains_compatible(self):
        self.start_failed()
        entries = [json.loads(x) for x in self.artifact.read_text().splitlines()]
        entries[-1]['message']['content'].pop(0)
        self.artifact.write_text(''.join(json.dumps(x) + '\n' for x in entries))
        with Authority(self.project) as owner:
            owner.store.resume('fixture')
            chain = owner.store.review_chain('fixture', private=True)
            self.assertTrue(Engine(owner, 'fixture', self.contract, EXECUTOR, resume=True,
                                   question=lambda _: str(self.artifact))._recover_format_rejection(chain, self.base))

    def test_parser_accepts_single_comma_and_and_rejects_malformed_locations(self):
        for location in ('owned.txt:1', 'owned.txt:1-2,4-5', 'owned.txt:1-2 and 4-5',
                         'owned.txt:1, 3 and 5-6', 'owned.txt:1-2 and 4-5, interacting with other.txt:7-9'):
            finding = location + ' - concrete defect'
            value = dict(self.verdict, findings=[finding])
            self.assertEqual(Engine._review_value(json.dumps(value), require_coverage=True)['findings'], [finding])
        for location in ('owned.txt:1 and other.txt:2', 'owned.txt:1 and', 'owned.txt:1,,2',
                         'owned.txt:1, interacting with other.txt', 'owned.txt:1, arbitrary words other.txt:2'):
            with self.subTest(location=location), self.assertRaises(_ReviewFormat):
                Engine._review_value(json.dumps(dict(self.verdict, findings=[location + ' - defect'])), require_coverage=True)

    def start_followup_failed(self, restore_base=False):
        self.start_failed()
        fixture = self
        verdict = {'approved': False, 'findings': [
            'owned.txt:1-2 and 4-5, interacting with other.txt:1-2 - defect breaks output',
            'owned.txt:7 - another defect', 'owned.txt:8 - third defect', 'owned.txt:9 - fourth defect'],
            'coverage': ['passing prior work', 'repair examined', 'source checked', 'tests checked', 'scope checked'],
            'coverage_gaps': ['unverified consumer', 'integration gap'], 'suggestions': ['later']}
        class Adapter:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                fixture.calls.append(('review' if kwargs.get('read_only') else 'fixer', prompt))
                if kwargs.get('read_only'):
                    entries = [{'type': 'session', 'id': 'followup', 'cwd': str(fixture.project)},
                        {'type': 'message', 'id': 'user', 'parentId': None, 'message': {'role': 'user',
                         'content': [{'type': 'text', 'text': prompt}]}},
                        {'type': 'message', 'id': 'answer', 'parentId': 'user', 'message': {'role': 'assistant',
                         'stopReason': 'stop', 'content': [{'type': 'thinking', 'thinking': 'reasoning'},
                                                           {'type': 'text', 'text': json.dumps(verdict)}]}}]
                    fixture.followup.write_text(''.join(json.dumps(x) + '\n' for x in entries))
                    return json.dumps(verdict)
                kwargs['claim']('owned.txt')
                fixture.project.joinpath('owned.txt').write_text('base\n' if restore_base else 'repaired\n')
                return 'repaired'
        self.followup = self.root / 'followup.jsonl'
        parse = Engine._review_value
        def old_parser(text, **kwargs):
            if 'interacting with' in text:
                raise _ReviewFormat('old parser rejected interaction')
            return parse(text, **kwargs)
        with Authority(self.project) as owner:
            owner.store.resume('fixture')
            with patch.object(Engine, '_review_value', side_effect=old_parser):
                with self.assertRaises(_ReviewFormat):
                    Engine(owner, 'fixture', self.contract, EXECUTOR, adapter=Adapter, resume=True,
                           question=lambda _: str(self.artifact)).invoke()
        return verdict, Adapter

    def test_followup_recovery_preserves_history_and_requires_actual_owner_pair(self):
        verdict, adapter = self.start_followup_failed()
        asked = []
        def question(prompt, **kwargs):
            asked.append((prompt, kwargs))
            return 'no' if kwargs.get('owner_only') else str(self.followup)
        with Authority(self.project) as owner:
            original = owner.store.review_chain('fixture', private=True)
            owner.store.resume('fixture')
            with self.assertRaisesRegex(Blocked, 'owner did not authorize'):
                Engine(owner, 'fixture', self.contract, EXECUTOR, adapter=adapter, resume=True,
                       question=question).invoke()
            chain = owner.store.review_chain('fixture', private=True)
            attempts = [r['state'] for r in owner.store.db.execute(
                'select state from execution_review_attempts where run_id=? and execution_id=? order by seq',
                ('fixture', chain['executions'][-1]['execution_id']))]
            grants = owner.store.db.execute("select count(*) from execution_history where run_id='fixture' and kind='review_pair_grant'").fetchone()[0]
        self.assertEqual(original['executions'][:2], chain['executions'][:2])
        self.assertEqual(attempts, ['dispatched', 'failed', 'rejected'])
        self.assertEqual(chain['executions'][-1]['findings'][-1], verdict['findings'])
        self.assertEqual(chain['executions'][-1]['references']['review_summary'],
                         {key: verdict[key] for key in ('coverage', 'coverage_gaps')})
        self.assertEqual(grants, 0)
        self.assertTrue(any(kwargs.get('owner_only') for _, kwargs in asked))
        self.assertEqual([kind for kind, _ in self.calls], ['writer', 'review', 'fixer', 'review'])

    def test_followup_rejects_verdict_already_accepted_by_prior_parser(self):
        self.start_followup_failed()
        entries = [json.loads(x) for x in self.followup.read_text().splitlines()]
        verdict = json.loads(entries[-1]['message']['content'][-1]['text'])
        verdict['findings'] = ['owned.txt:1 and 3 - previously accepted defect']
        entries[-1]['message']['content'][-1]['text'] = json.dumps(verdict)
        self.followup.write_text(''.join(json.dumps(x) + '\n' for x in entries))
        with Authority(self.project) as owner:
            owner.store.resume('fixture')
            chain = owner.store.review_chain('fixture', private=True)
            with self.assertRaisesRegex(Blocked, 'not an actionable compound-location rejection'):
                Engine(owner, 'fixture', self.contract, EXECUTOR, resume=True,
                       question=lambda _: str(self.followup))._recover_format_rejection(chain, self.base)
            self.assertTrue(owner.store.review_chain('fixture')['uncertain'])

    def test_followup_blocks_dirty_repair_delta_path_restored_to_original_base(self):
        self.contract = admit({'tasks': [{'id': 'task', 'description': 'fixture'}]})
        self.start_followup_failed(restore_base=True)
        head = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        self.assertEqual(git(self.project, 'diff', '--name-only', self.base + '..' + head), b'')
        with Authority(self.project) as owner:
            owner.store.resume('fixture')
            chain = owner.store.review_chain('fixture', private=True)
            prior_head = chain['executions'][0]['references']['head']
            self.assertIn(b'owned.txt', git(self.project, 'diff', '--name-only', prior_head + '..' + head))
            engine = Engine(owner, 'fixture', self.contract, EXECUTOR, resume=True,
                            question=lambda _: str(self.followup))
            for mode in ('worktree', 'index'):
                with self.subTest(mode=mode):
                    self.write('owned.txt', 'drift\n')
                    if mode == 'index':
                        git(self.project, 'add', '--', 'owned.txt')
                        self.write('owned.txt', 'base\n')
                    with self.assertRaisesRegex(Blocked, 'target has changes in owned.txt'):
                        engine._recover_format_rejection(chain, self.base)
                    if mode == 'index':
                        git(self.project, 'restore', '--staged', '--', 'owned.txt')
                    self.write('owned.txt', 'base\n')
            self.assertTrue(owner.store.review_chain('fixture')['uncertain'])
            self.assertTrue(engine._recover_format_rejection(chain, self.base))

    def test_followup_recovery_honors_existing_scoped_routine_authority(self):
        verdict, adapter = self.start_followup_failed()
        asked = []
        def question(prompt, **kwargs):
            asked.append((prompt, kwargs))
            return str(self.followup)
        with Authority(self.project) as owner:
            owner.store.authorize_routine_review_continuation('fixture', owner.store.review_scope('fixture'))
            owner.store.resume('fixture')
            with patch.object(Engine, 'run_fix', side_effect=Blocked('fixture stop before fixer')) as fixer:
                with self.assertRaisesRegex(Blocked, 'fixture stop before fixer'):
                    Engine(owner, 'fixture', self.contract, EXECUTOR, adapter=adapter, resume=True,
                           question=question).invoke()
            chain = owner.store.review_chain('fixture', private=True)
            grants = list(owner.store.db.execute("select state,details from execution_history where run_id='fixture' and kind='review_pair_grant'"))
        self.assertEqual(chain['executions'][-1]['findings'][-1], verdict['findings'])
        self.assertEqual(len(grants), 1)
        self.assertEqual(grants[0]['state'], 'authorized')
        self.assertEqual(json.loads(grants[0]['details'])['rejecting_execution_id'], chain['executions'][-1]['execution_id'])
        self.assertEqual(fixer.call_count, 1)
        self.assertFalse(any(kwargs.get('owner_only') for _, kwargs in asked))
        self.assertEqual([kind for kind, _ in self.calls], ['writer', 'review', 'fixer', 'review'])

    def test_followup_context_and_predecessor_mismatch_stay_blocked(self):
        self.start_followup_failed()
        original = [json.loads(x) for x in self.followup.read_text().splitlines()]
        with Authority(self.project) as owner:
            owner.store.authorize_routine_review_continuation('fixture', owner.store.review_scope('fixture'))
            owner.store.resume('fixture')
            engine = Engine(owner, 'fixture', self.contract, EXECUTOR, resume=True,
                            question=lambda _: str(self.followup))
            chain = owner.store.review_chain('fixture', private=True)
            for mode in ('delta', 'prior', 'incomplete', 'unsafe', 'predecessor', 'head'):
                with self.subTest(mode=mode):
                    entries = json.loads(json.dumps(original))
                    candidate = json.loads(json.dumps(chain))
                    if mode == 'delta':
                        entries[1]['message']['content'][0]['text'] = entries[1]['message']['content'][0]['text'].replace('Review delta:', 'Wrong delta:')
                    elif mode == 'prior':
                        entries[1]['message']['content'][0]['text'] = entries[1]['message']['content'][0]['text'].replace('Prior review:', 'Wrong review:')
                    elif mode == 'incomplete':
                        entries[-1]['message']['stopReason'] = 'aborted'
                    elif mode == 'unsafe':
                        entries[-1]['message']['content'].append({'type': 'toolCall', 'name': 'write'})
                    elif mode == 'predecessor':
                        candidate['executions'][-1]['predecessor_execution_id'] = 'wrong'
                    else:
                        candidate['executions'][1]['references']['head'] = 'wrong'
                    self.followup.write_text(''.join(json.dumps(x) + '\n' for x in entries))
                    with self.assertRaises(Blocked):
                        engine._recover_format_rejection(candidate, self.base)
            self.assertTrue(owner.store.review_chain('fixture')['uncertain'])
            self.assertEqual(owner.store.db.execute("select count(*) from execution_history where run_id='fixture' and kind='review_pair_grant'").fetchone()[0], 0)

    def test_incomplete_and_non_rejection_artifacts_stay_blocked(self):
        self.start_failed()
        original = [json.loads(x) for x in self.artifact.read_text().splitlines()]
        for mode in ('interrupted', 'approval', 'write_tool', 'earlier_write_tool', 'multiple_text', 'no_text', 'unknown_part'):
            with self.subTest(mode=mode):
                entries = json.loads(json.dumps(original))
                if mode == 'interrupted':
                    entries[-1]['message']['stopReason'] = 'aborted'
                elif mode == 'approval':
                    value = dict(self.verdict, approved=True)
                    entries[-1]['message']['content'][-1]['text'] = json.dumps(value)
                elif mode == 'write_tool':
                    entries[-1]['message']['content'].append({'type': 'toolCall', 'name': 'write'})
                elif mode == 'earlier_write_tool':
                    entries.insert(-1, {'type': 'message', 'id': 'unsafe', 'parentId': 'user',
                                        'message': {'role': 'assistant', 'content': [{'type': 'toolCall', 'name': 'write'}]}})
                    entries[-1]['parentId'] = 'unsafe'
                elif mode == 'multiple_text':
                    entries[-1]['message']['content'].append({'type': 'text', 'text': '{}'})
                elif mode == 'no_text':
                    entries[-1]['message']['content'].pop()
                else:
                    entries[-1]['message']['content'].append({'type': 'unknown'})
                self.artifact.write_text(''.join(json.dumps(x) + '\n' for x in entries))
                with Authority(self.project) as owner:
                    owner.store.resume('fixture')
                    with self.assertRaisesRegex(Blocked, 'artifact is invalid or incompatible'):
                        Engine(owner, 'fixture', self.contract, EXECUTOR, resume=True,
                               question=lambda _: str(self.artifact)).invoke()
                    self.assertTrue(owner.store.review_chain('fixture')['uncertain'])
        self.assertEqual([kind for kind, _ in self.calls], ['writer', 'review'])

    def test_unknown_failure_cause_stays_blocked(self):
        self.start_failed()
        with Authority(self.project) as owner:
            owner.store.db.execute("UPDATE execution_review_attempts SET reference_json=json_remove(reference_json, '$.failure_category') WHERE run_id='fixture' AND state='failed'")
            owner.store.db.execute("DELETE FROM execution_observations WHERE run_id='fixture' AND phase='review' AND kind='failed'")
            owner.store.resume('fixture')
            with self.assertRaisesRegex(Blocked, 'failure cause is not known'):
                Engine(owner, 'fixture', self.contract, EXECUTOR, resume=True,
                       question=lambda _: str(self.artifact)).invoke()
            self.assertTrue(owner.store.review_chain('fixture')['uncertain'])
        self.assertEqual([kind for kind, _ in self.calls], ['writer', 'review'])

    def test_incompatible_artifact_and_target_drift_stay_blocked(self):
        self.start_failed()
        entries = [json.loads(x) for x in self.artifact.read_text().splitlines()]
        entries[1]['message']['content'][0]['text'] = 'wrong scope'
        self.artifact.write_text(''.join(json.dumps(x) + '\n' for x in entries))
        with Authority(self.project) as owner:
            owner.store.resume('fixture')
            with self.assertRaisesRegex(Blocked, 'artifact is invalid or incompatible'):
                Engine(owner, 'fixture', self.contract, EXECUTOR, resume=True,
                       question=lambda _: str(self.artifact)).invoke()
            self.assertTrue(owner.store.review_chain('fixture')['uncertain'])
        git(self.project, 'commit', '--allow-empty', '-qm', 'drift')
        with Authority(self.project) as owner:
            owner.store.resume('fixture')
            with self.assertRaisesRegex(Blocked, 'target drifted'):
                Engine(owner, 'fixture', self.contract, EXECUTOR, resume=True,
                       question=lambda _: str(self.artifact)).invoke()
            self.assertTrue(owner.store.review_chain('fixture')['uncertain'])
        self.assertEqual([kind for kind, _ in self.calls], ['writer', 'review'])
