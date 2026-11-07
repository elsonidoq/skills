"""Offline explicit recovery of an initial review format failure."""
import json
from unittest.mock import patch

from coherence_workflow.engine import Engine, _ReviewFormat
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-review', 'effort': 'medium'}}


class ReviewFormatRecoveryTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.calls = []
        self.artifact = self.root / 'review.jsonl'
        self.verdict = {'approved': False, 'findings': ['owned.txt:1-2,4-5 - invalid data crashes requests',
                         'owned.txt:7 - missing value corrupts output'], 'coverage': ['producer checked'],
                        'coverage_gaps': ['consumer untested'], 'suggestions': ['rename later']}
        self.contract = admit({'tasks': [{'id': 'task', 'description': 'fixture', 'owned_paths': ['owned.txt']}]})

    def start_failed(self):
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
                         'stopReason': 'stop', 'content': [{'type': 'text', 'text': json.dumps(fixture.verdict)}]}}]
                    fixture.artifact.write_text(''.join(json.dumps(x) + '\n' for x in entries))
                    return json.dumps(fixture.verdict)
                kwargs['claim']('owned.txt')
                fixture.project.joinpath('owned.txt').write_text('task output\n')
                return 'done'
        parse = Engine._review_value
        def old_parser(text, **kwargs):
            value = parse(text, **kwargs)
            if any(',4-5' in finding for finding in value['findings']):
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

    def test_explicit_recovery_preserves_failure_and_continues_existing_lifecycle(self):
        self.start_failed()
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
        self.assertEqual(attempts, ['dispatched', 'failed', 'rejected'])
        first = chain['executions'][0]
        self.assertEqual(first['findings'][-1], self.verdict['findings'])
        self.assertEqual(first['suggestions'][-1], self.verdict['suggestions'])
        self.assertEqual(first['references']['review_summary'], {k: self.verdict[k] for k in ('coverage', 'coverage_gaps')})
        self.assertEqual([kind for kind, _ in self.calls], ['writer', 'review', 'fixer', 'review'])
        self.assertIn('consumer untested', self.calls[-1][1])
        self.assertEqual([x['role'] for x in chain['executions']], ['reviewer', 'fixer', 'reviewer'])

    def test_incomplete_and_non_rejection_artifacts_stay_blocked(self):
        self.start_failed()
        original = [json.loads(x) for x in self.artifact.read_text().splitlines()]
        for mode in ('interrupted', 'approval', 'write_tool'):
            with self.subTest(mode=mode):
                entries = json.loads(json.dumps(original))
                if mode == 'interrupted':
                    entries[-1]['message']['stopReason'] = 'aborted'
                elif mode == 'approval':
                    value = dict(self.verdict, approved=True)
                    entries[-1]['message']['content'][0]['text'] = json.dumps(value)
                else:
                    entries[-1]['message']['content'].append({'type': 'toolCall', 'name': 'write'})
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
