"""Production recovery CLI with real SQLite and offline gh subprocess effects."""
import contextlib
import io
import json
import os
from unittest.mock import patch

from coherence_workflow.cli import main
from coherence_workflow.trace_capture import (capture_questions, persist_parent_events,
                                              record_worker_question, submission_facts)
from coherence_workflow.trace_projection import project_trace
from coherence_workflow.store import Authority
from coherence_workflow.trace_publication import Gh, LengthProof, digest, publish_trace
from fixtures.support import ProjectTest
from test_graph_execution import EXECUTOR
from test_trace_publication import API, FAKE, ISSUE, PR, LENGTH_ERROR


class TraceRecoveryTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.grant = {'run_id': 'run', 'target': ISSUE, 'operations': ['trace_comment'],
                      'approval_ref': 'offline fixture only'}
        self.scope = {'target': ISSUE, 'authority': self.grant, 'known_linked_prs': []}
        with Authority(self.project) as owner:
            owner.store.start('run', self.base, contract={'tasks': [], 'delivery_issue': ISSUE},
                              executor=EXECUTOR, authority={'delivery_scope': self.scope})
            owner.store.history('run', 'T', 'worker_invocation', 'returned', {
                'invocation_id': 'original', 'submission': {'report': 'Retained meaningful answer',
                                                          'evidence': [], 'gaps': []}})
            owner.store.db.execute("UPDATE execution_runs SET state='complete' WHERE run_id='run'")
            database = owner.store.path
        self.remote_path = self.root/'remote.json'
        self.update(calls=[], posts=0, next_id=10, comments=[])
        executable = self.root/'gh'
        executable.write_text(FAKE); executable.chmod(0o700)
        self.gh = Gh(executable)
        for mock in (patch.dict(os.environ, {'TRACE_FAKE_STATE': str(self.remote_path),
                                            'TRACE_FAKE_DB': str(database)}),
                     patch('coherence_workflow.trace_publication.Gh', return_value=self.gh)):
            mock.start(); self.addCleanup(mock.stop)

    def remote(self):
        return json.loads(self.remote_path.read_text())

    def update(self, **values):
        data = self.remote() if self.remote_path.exists() else {}
        self.remote_path.write_text(json.dumps({**data, **values}))

    def recover(self, *options, project=None):
        # These are real forbidden production entries, not a replacement recovery route.
        with contextlib.ExitStack() as stack:
            for name in ('coherence_workflow.cli.run_graph', 'coherence_workflow.cli.Engine',
                         'coherence_workflow.cli.PiAdapter', 'coherence_workflow.engine.Engine.invoke',
                         'coherence_workflow.graph.run_graph', 'coherence_workflow.store.git'):
                if name.endswith('store.git'):
                    # Writer locking uses read-only Git identity; commits remain forbidden.
                    from coherence_workflow.store import git
                    def safe_git(project, *args, **kwargs):
                        if args[0] != 'rev-parse':
                            raise AssertionError('recovery attempted Git mutation/check: ' + str(args))
                        return git(project, *args, **kwargs)
                    stack.enter_context(patch(name, side_effect=safe_git))
                else:
                    stack.enter_context(patch(name, side_effect=AssertionError('forbidden replay: ' + name)))
            stack.enter_context(patch('coherence_workflow.verification.run_checks', side_effect=AssertionError('check replay')))
            stack.enter_context(patch('coherence_workflow.git_effects.FocusedGit.checkpoint', side_effect=AssertionError('checkpoint replay')))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main(['recover-publication', '--project', str(project or self.project), '--run', 'run', *options])
        return code, json.loads(output.getvalue())

    def test_lost_response_reconciles_exact_snapshot_and_repeat_does_not_send(self):
        self.update(lost_response=True)
        with Authority(self.project) as owner:
            first = publish_trace(owner.store, 'run', authority=self.grant, gh=self.gh)
            self.assertEqual(first['state'], 'uncertain')
            owner.store.history('run', None, 'later_fact', 'observed', {'text': 'Not in original snapshot'})
        original = self.remote()['comments'][0]['body']
        code, result = self.recover()
        self.assertEqual(code, 0, result)
        self.assertEqual(result['implementation'], {'state': 'complete', 'replayed': False})
        self.assertEqual(result['publication']['snapshot_id'], first['snapshot_id'])
        self.assertEqual(self.remote()['posts'], 1)
        self.assertEqual(self.remote()['comments'][0]['body'], original)
        self.assertNotIn('Not in original snapshot', original)
        self.assertEqual(self.recover()[0], 0)
        self.assertEqual(self.remote()['posts'], 1)

    def test_actual_github_length_diagnostic_automatically_splits_in_default_cli(self):
        self.update(length_error=LENGTH_ERROR)
        with Authority(self.project) as owner:
            owner.store.history('run', 'T', 'worker_invocation', 'returned', {
                'invocation_id': 'large', 'submission': {
                    'report': 'Ordinary question? Answer “yes” 🦊漢字\n' * 4200,
                    'evidence': [], 'gaps': []}})
        code, result = self.recover()
        self.assertEqual(code, 0, result)
        self.assertEqual(result['implementation'], {'state': 'complete', 'replayed': False})
        with Authority(self.project) as owner:
            rows = [{**json.loads(r['details']), 'state': r['state']}
                    for r in owner.store.trace_publication_history('run')]
            original = next(r for r in rows if r['type'] == 'snapshot')
            parts = [r for r in rows if r['type'] == 'part' and r['state'] == 'confirmed']
            self.assertEqual(''.join(r['chunk'] for r in parts), original['text'])
            owner.store.history('run', None, 'later_fact', 'observed', {'text': 'Not in fixed snapshot'})
        remote = self.remote()
        self.assertGreater(len(parts), 1)
        self.assertEqual([r['body'] for r in parts], [c['body'] for c in remote['comments']])
        self.assertTrue(all(len(c['body']) <= 65536 for c in remote['comments']))
        for c in remote['comments']:
            self.assertTrue(c['body'].startswith('<!-- coherence-trace:'))
            self.assertTrue(any(call['method'] == 'GET' and
                call['endpoint'].endswith('/issues/comments/' + str(c['id']))
                for call in remote['calls']))
        posts = remote['posts']
        code, again = self.recover()
        self.assertEqual(code, 0, again)
        self.assertEqual(again['publication']['snapshot_id'], original['snapshot_id'])
        self.assertEqual(self.remote()['posts'], posts)
        self.assertEqual(self.remote()['comments'], remote['comments'])

    def test_old_status_only_rejection_uses_default_recovery_and_preserves_root(self):
        self.update(post_error=422)  # Historical publisher retained status, not cause.
        code, first = self.recover()
        self.assertEqual(code, 2)
        with Authority(self.project) as owner:
            rows = [json.loads(r['details']) for r in owner.store.trace_publication_history('run')]
            root = next(r for r in rows if r['type'] == 'snapshot')
            self.assertNotIn('length_diagnostic', rows[-1])
            owner.store.history('run', None, 'later_fact', 'observed', {'text': 'Not in root snapshot'})
        root_body = self.remote()['calls'][-1]['stdin']['body']
        self.update(post_error=None, length_error=LENGTH_ERROR, length_limit=len(root_body)-1)
        code, result = self.recover()
        self.assertEqual(code, 0, result)
        self.assertEqual(result['publication']['snapshot_id'], first['publication']['snapshot_id'])
        self.assertEqual(self.remote()['posts'], 4)
        self.assertEqual(''.join(c['body'].split('without added separators.\n', 1)[1]
                                 for c in self.remote()['comments']), root['text'])
        self.assertEqual(self.recover()[0], 0)
        self.assertEqual(self.remote()['posts'], 4)

    def test_known_credentials_are_removed_before_capture_loses_their_fields(self):
        secret, bridge = 'named-credential-sentinel', 'bridge-credential-sentinel'
        event = {'version': 1, 'id': 'owner-event', 'kind': 'owner_call',
                 'tool_call_id': 'owner-tool',
                 'content': 'Ordinary owner question? ' + secret + ' ' + bridge,
                 'nested': [{'API-Key': secret}, {'token': secret},
                            {'password': '', 'secret': None, 'authorization': 42}],
                 'env': 'ordinary environment label', 'config_dump': 'ordinary config label',
                 'ordinary': 'ordinary environment label; ordinary config label; token discussion'}
        with patch.dict(os.environ, {'COHERENCE_PARENT_BRIDGE_TOKEN': bridge}):
            with Authority(self.project) as owner:
                persist_parent_events(owner.store, 'run', [event, event])
                persist_parent_events(owner.store, 'run', [event])
                # Equal public output is not equal source content. The batch remains atomic.
                with self.assertRaisesRegex(ValueError, 'conflicting parent trace event ID'):
                    persist_parent_events(owner.store, 'run', [
                        {**event, 'id': 'must-not-persist'},
                        {**event, 'nested': [{'API-Key': 'different-credential'},
                                            *event['nested'][1:]]}])
                rows = owner.store.db.execute(
                    "SELECT details FROM execution_history WHERE kind='parent_trace'").fetchall()
                self.assertEqual(len(rows), 1)
                captured = json.loads(rows[0][0])
                self.assertTrue(captured['gaps'])
                self.assertEqual(len(captured['source_digest']), 64)
                self.assertEqual(captured['event']['ordinary'], event['ordinary'])
                record_worker_question(owner.store, 'run', 'T', 'original', 'resolved',
                                       tool_call_id='worker-tool', token=secret,
                                       answer='Ordinary worker answer ' + secret)
                def question(prompt, **kwargs):
                    return 'Ordinary consumed answer ' + secret
                consume = capture_questions(question, owner.store, 'run')
                self.assertEqual(consume('Ordinary consumed question?',
                    decision_context={'credentials': {'api_key': secret}}),
                    'Ordinary consumed answer ' + secret)
                facts = submission_facts(self.project, {'owned_paths': []},
                                         'Ordinary report ' + bridge)
                owner.store.history('run', 'T', 'worker_invocation', 'returned',
                                    {'invocation_id': 'submission', **facts})
        # No credential environment or discarded source fields are available on recovery.
        with patch.dict(os.environ, {'COHERENCE_PARENT_BRIDGE_TOKEN': ''}):
            with Authority(self.project) as owner:
                retained = [row[0] for row in owner.store.db.execute(
                    "SELECT details FROM execution_history WHERE run_id='run'")]
                snapshot = project_trace(owner.store, 'run')
            code, result = self.recover()
            self.assertEqual(code, 0, result)
            body = self.remote()['comments'][0]['body']
            for payload in ('\n'.join(retained), json.dumps(snapshot), body):
                self.assertNotIn(secret, payload)
                self.assertNotIn(bridge, payload)
                for ordinary in ('Ordinary owner question?', 'Ordinary worker answer',
                                 'Ordinary consumed question?', 'Ordinary consumed answer',
                                 'Ordinary report', event['ordinary']):
                    self.assertIn(ordinary, payload)
            self.assertEqual(self.recover()[0], 0)
            self.assertEqual(self.remote()['posts'], 1)

    def test_incomplete_scan_blocks_new_effect(self):
        self.update(lost_response=True)
        with Authority(self.project) as owner:
            publish_trace(owner.store, 'run', authority=self.grant, gh=self.gh)
        self.update(pages={'1': [], '2': []}, incomplete_page=True)
        code, result = self.recover()
        self.assertEqual(code, 2)
        self.assertEqual(result['publication']['state'], 'uncertain')
        self.assertIn('reconcile', result['publication']['correction'])
        self.assertEqual(self.remote()['posts'], 1)

    def test_complete_scan_precedes_missing_write(self):
        self.update(post_error=503)
        with Authority(self.project) as owner:
            self.assertEqual(publish_trace(owner.store, 'run', authority=self.grant,
                                           gh=self.gh)['state'], 'failed')
        self.update(post_error=None)
        code, result = self.recover()
        self.assertEqual(code, 0, result)
        calls = self.remote()['calls']
        post = [i for i, call in enumerate(calls) if call['method'] == 'POST'][-1]
        self.assertIn('/comments?per_page=100&page=1', calls[post-1]['endpoint'])
        self.assertEqual(self.remote()['posts'], 2)

    def test_split_parts_preserve_confirmed_child(self):
        self.update(post_error=422, error_on=1, error_message='fixture length rejected; no effect')
        underlying = self.gh
        proofs = []
        test = self
        class SplitThenFail:
            def request(self, target, method, endpoint, body=None):
                if method == 'POST' and ':1.2 -->' in body['body']:
                    test.update(post_error=403, error_on=test.remote()['posts']+1)
                response = underlying.request(target, method, endpoint, body)
                if method == 'POST' and response['status'] == 422:
                    proofs.append(LengthProof(digest(body['body']), digest(response['raw']),
                        'test_trace_publication.py: FAKE no-effect contract',
                        'Inspected fixture rejects before creation.', True))
                return response
        with Authority(self.project) as owner:
            first = publish_trace(owner.store, 'run', authority=self.grant,
                                  gh=SplitThenFail(), length_proofs=proofs)
        self.assertEqual(first['state'], 'partial', first)
        original = self.remote()['comments'][0]
        self.update(post_error=None)
        code, result = self.recover('--snapshot', first['snapshot_id'])
        self.assertEqual(code, 0, result)
        self.assertEqual(self.remote()['comments'][0], original)
        self.assertEqual(len(self.remote()['comments']), 2)
        self.assertEqual(self.remote()['posts'], 4)
        self.assertEqual(self.recover()[0], 0)
        self.assertEqual(self.remote()['posts'], 4)

    def test_missing_scope_drift_and_target_drift(self):
        code, result = self.recover('--delivery-scope', json.dumps({**self.scope, 'target': PR}))
        self.assertEqual(code, 2)
        self.assertIn('drifted', result['publication']['correction'])
        self.assertEqual(self.remote()['calls'], [])
        with Authority(self.project) as owner:
            owner.store.db.execute("UPDATE execution_run_inputs SET authority='{}' WHERE run_id='run'")
        self.assertEqual(self.recover()[0], 2)
        self.assertEqual(self.remote()['calls'], [])
        self.update(target_drift=True)
        code, result = self.recover('--delivery-scope', json.dumps(self.scope))
        self.assertEqual(code, 2)
        self.assertIn('drifted', result['publication']['correction'])
        self.assertEqual(self.remote()['posts'], 0)

    def test_retained_facts_without_prepared_snapshot_publish_once(self):
        code, result = self.recover()
        self.assertEqual(code, 0, result)
        self.assertIn('Retained meaningful answer', self.remote()['comments'][0]['body'])
        self.assertEqual(self.recover()[0], 0)
        self.assertEqual(self.remote()['posts'], 1)

    def test_existing_supported_links_survive_repeated_recovery_without_link_writes(self):
        scope = {**self.scope, 'known_linked_prs': [PR]}
        with Authority(self.project) as owner:
            owner.store.db.execute(
                "UPDATE execution_run_inputs SET authority=? WHERE run_id='run'",
                (json.dumps({'delivery_scope': scope}),))
        links = [{'id': identity, 'url': API+'/issues/comments/'+str(identity),
                  'html_url': target+'#issuecomment-'+str(identity),
                  'issue_url': API+'/issues/'+target.rsplit('/', 1)[1], 'body': body}
                 for identity, target, body in ((1, ISSUE, 'Delivery PR: '+PR),
                                                (2, PR, 'Delivery issue: '+ISSUE))]
        self.update(comments=links)
        for _ in range(2):
            code, result = self.recover()
            self.assertEqual(code, 0, result)
            self.assertEqual(result['linkage']['associations'], [{'issue': ISSUE, 'pr': PR}])
            self.assertEqual(self.remote()['comments'][:2], links)
            self.assertEqual(self.remote()['posts'], 1)  # Trace only; no link grant.
        with Authority(self.project) as owner:
            self.assertEqual(owner.store.db.execute(
                "SELECT state FROM execution_runs WHERE run_id='run'").fetchone()['state'], 'complete')

    def test_missing_database_reports_separate_outcomes_without_creating_storage(self):
        project = self.root/'missing-project'
        code, result = self.recover(project=project)
        self.assertEqual(code, 2)
        self.assertEqual(result['implementation'], {'state': 'unavailable', 'replayed': False})
        self.assertEqual(result['publication']['state'], 'deferred')
        self.assertIn('restore the original database', result['publication']['correction'])
        self.assertFalse(project.exists())
        self.assertEqual(self.remote()['calls'], [])

    def test_missing_input_reports_retained_implementation_without_network(self):
        with Authority(self.project) as owner:
            owner.store.db.execute("DELETE FROM execution_run_inputs WHERE run_id='run'")
        code, result = self.recover()
        self.assertEqual(code, 2)
        self.assertEqual(result['implementation'], {'state': 'complete', 'replayed': False})
        self.assertIn('Retained run input unavailable', result['publication']['correction'])
        self.assertEqual(self.remote()['calls'], [])

    def test_missing_snapshot_and_run_are_actionable_without_network(self):
        code, result = self.recover('--snapshot', 'absent')
        self.assertEqual(code, 2)
        self.assertIn('snapshot unavailable', result['publication']['correction'])
        with Authority(self.project) as owner:
            owner.store.db.execute("DELETE FROM execution_runs WHERE run_id='run'")
        code, result = self.recover()
        self.assertEqual(code, 2)
        self.assertEqual(result['implementation']['state'], 'unavailable')
        self.assertEqual(self.remote()['calls'], [])
