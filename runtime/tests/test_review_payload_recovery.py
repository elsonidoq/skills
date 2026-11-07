"""Isolated review delivery and same-stage pre-output failure continuation."""
import json
import re
from pathlib import Path
from unittest.mock import patch

from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest

EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-review', 'effort': 'medium'}}


class ReviewPayloadRecoveryTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.calls, self.prompts = [], []
        self.contract = admit({'tasks': [{'id': 'task', 'description': 'fixture', 'owned_paths': ['owned.txt'],
            'checks': [['python3', '-c', "print('X'*90000);print('END-OF-OUTPUT')"]]}]})

    def adapter(self):
        fixture = self
        class Adapter:
            reviews = 0
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    Adapter.reviews += 1
                    fixture.calls.append('review')
                    fixture.prompts.append(prompt)
                    if Adapter.reviews == 1:
                        return json.dumps({'approved': False, 'findings': ['owned.txt:1 - bad value crashes requests'],
                                           'coverage': ['initial producer checked'], 'coverage_gaps': ['consumer unchecked']})
                    if Adapter.reviews == 2:
                        assert len(prompt) > 30000
                        raise Blocked("SDK operation failed: Codex error: Invalid response.create payload: Invalid 'input[0].content[0].text': string too long. Expected a string with maximum length 30000, but got a string with length " + str(len(prompt)) + ' instead.')
                    paths = re.findall(r'private full output file (\S+\.txt)', prompt)
                    assert paths and all(Path(path).read_text().endswith('END-OF-OUTPUT\n') for path in paths)
                    assert 'consumer unchecked' in prompt and 'initial producer checked' in prompt
                    return json.dumps({'approved': True, 'findings': [], 'coverage': ['producer and consumer checked'], 'coverage_gaps': []})
                fixture.calls.append('worker' if len(fixture.calls) == 0 else 'fixer')
                kwargs['claim']('owned.txt')
                fixture.project.joinpath('owned.txt').write_text('output ' + str(len(fixture.calls)) + '\n')
                return 'done'
        return Adapter

    def start_failed(self):
        adapter = self.adapter()
        evidence = Engine._review_check_evidence
        def old_evidence(engine, **_kwargs):
            return evidence(engine)
        with Authority(self.project) as owner:
            with patch.object(Engine, '_review_check_evidence', old_evidence):
                with self.assertRaisesRegex(Blocked, 'string too long'):
                    Engine(owner, 'run', self.contract, EXECUTOR, adapter=adapter).invoke()
            chain = owner.store.review_chain('run', private=True)
            self.assertEqual([x['state'] for x in chain['executions']], ['rejected', 'approved', 'failed'])
        return adapter

    def test_compact_recovery_consumes_full_evidence_without_replaying_work(self):
        adapter = self.start_failed()
        with Authority(self.project) as owner:
            owner.store.resume('run')
            result = Engine(owner, 'run', self.contract, EXECUTOR, adapter=adapter, resume=True).invoke()
            chain = owner.store.review_chain('run', private=True)
            attempts = [row['state'] for row in owner.store.db.execute(
                'select state from execution_review_attempts where run_id=? and execution_id=? order by seq',
                ('run', chain['executions'][-1]['execution_id']))]
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(self.calls, ['worker', 'review', 'fixer', 'review', 'review'])
        self.assertEqual(attempts, ['dispatched', 'failed', 'dispatched', 'approved'])
        self.assertLess(len(self.prompts[-1]), 30000)
        self.assertGreater(len(self.prompts[-2]), 30000)
        self.assertEqual(chain['executions'][-1]['review_ordinal'], 2)
        self.assertEqual(chain['executions'][-1]['fixing_round'], 1)

    def test_unknown_transport_and_wrong_scope_remain_blocked(self):
        adapter = self.start_failed()
        with Authority(self.project) as owner:
            row = owner.store.db.execute("select seq,details from execution_history where run_id='run' and kind='invocation' and state='failed' order by seq desc limit 1").fetchone()
            facts = json.loads(row['details'])
            facts['error'] = 'SDK operation failed: unknown transport'
            owner.store.db.execute('update execution_history set details=? where seq=?', (json.dumps(facts), row['seq']))
            owner.store.resume('run')
            with self.assertRaisesRegex(Blocked, 'not an actionable rejection'):
                Engine(owner, 'run', self.contract, EXECUTOR, adapter=adapter, resume=True).invoke()
        self.assertEqual(self.calls, ['worker', 'review', 'fixer', 'review'])

    def test_missing_check_output_remains_blocked_before_dispatch(self):
        adapter = self.start_failed()
        with Authority(self.project) as owner:
            row = owner.store.db.execute("select seq,details from execution_history where run_id='run' and kind='check' and state='passed' order by seq limit 1").fetchone()
            facts = json.loads(row['details'])
            del facts['output']
            owner.store.db.execute('update execution_history set details=? where seq=?', (json.dumps(facts), row['seq']))
            owner.store.resume('run')
            with self.assertRaisesRegex(Blocked, 'check output is missing'):
                Engine(owner, 'run', self.contract, EXECUTOR, adapter=adapter, resume=True).invoke()
            chain = owner.store.review_chain('run', private=True)
            self.assertEqual(chain['executions'][-1]['attempt_count'], 2)
        self.assertEqual(self.calls, ['worker', 'review', 'fixer', 'review'])

    def test_wrong_scope_remains_blocked(self):
        adapter = self.start_failed()
        altered = admit({'tasks': [{'id': 'task', 'description': 'different scope'}]})
        with Authority(self.project) as owner:
            owner.store.resume('run')
            with self.assertRaisesRegex(Blocked, 'not an actionable rejection'):
                Engine(owner, 'run', altered, EXECUTOR, adapter=adapter, resume=True).invoke()
        self.assertEqual(self.calls, ['worker', 'review', 'fixer', 'review'])

    def test_target_drift_remains_blocked(self):
        adapter = self.start_failed()
        git(self.project, 'commit', '--allow-empty', '-qm', 'drift')
        with Authority(self.project) as owner:
            owner.store.resume('run')
            with self.assertRaisesRegex(Blocked, 'target drifted'):
                Engine(owner, 'run', self.contract, EXECUTOR, adapter=adapter, resume=True).invoke()
        self.assertEqual(self.calls, ['worker', 'review', 'fixer', 'review'])
