"""Composed offline run -> socket drain -> SQLite -> projection -> gh subprocess.

The socket supplies the established bridge protocol, not synthetic live-owner proof.
Installed SDK hook applicability is covered by test_parent_trace.mjs (T001).
"""
import contextlib
import io
import json
import os
import sqlite3
import socketserver
import threading
from unittest.mock import patch

from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.pi_adapter import parent_question
from coherence_workflow.store import Authority, Blocked
from coherence_workflow.trace_capture import capture_questions
from coherence_workflow.trace_publication import Gh, LengthProof, digest, publish_trace
from fixtures.support import ProjectTest
from test_graph_execution import EXECUTOR
from test_trace_publication import FAKE, ISSUE


class TraceFinishTests(ProjectTest):
    def setUp(self):
        super().setUp()
        env = patch.dict(os.environ, {key: '' for key in (
            'COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
            'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')})
        env.start(); self.addCleanup(env.stop)

    def bridge(self, store, *, ack=True):
        requests = []
        events = [
            {'version': 1, 'id': 'call-event', 'kind': 'owner_call',
             'tool_call_id': 'actual-call', 'input': {'question': 'Owner wording?'}},
            {'version': 1, 'id': 'result-event', 'kind': 'owner_result',
             'tool_call_id': 'actual-call', 'details': {'answer': 'Actual owner answer'}}]
        test = self
        class Handler(socketserver.StreamRequestHandler):
            def handle(self):
                request = json.loads(self.rfile.readline())
                requests.append(request)
                response = {'request_id': request['request_id']}
                if request['type'] == 'trace_drain':
                    response['events'] = events
                elif request['type'] == 'trace_ack':
                    # Persistence must already be independently visible before ack.
                    with sqlite3.connect(store.path) as db:
                        rows = db.execute("SELECT details FROM execution_history WHERE kind='parent_trace'").fetchall()
                    test.assertTrue(any('Actual owner answer' in row[0] for row in rows))
                    response['acknowledged'] = ack
                else:
                    response.update(answer='Distinct coordinator resolution', run_id='run',
                                    session_id='parent-session')
                self.wfile.write((json.dumps(response) + '\n').encode())
        server = socketserver.UnixStreamServer(str(self.root/'bridge.sock'), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(thread.join)
        self.addCleanup(server.shutdown)
        env = patch.dict(os.environ, {
            'COHERENCE_PARENT_BRIDGE_SOCKET': str(self.root/'bridge.sock'),
            'COHERENCE_PARENT_BRIDGE_TOKEN': 'transport-credential',
            'COHERENCE_PARENT_BRIDGE_SESSION': 'parent-session',
            'COHERENCE_PARENT_BRIDGE_RUN': 'run'})
        env.start(); self.addCleanup(env.stop)
        return requests

    def setup_remote(self, owner, **state):
        path = self.root/'remote.json'
        path.write_text(json.dumps({'calls': [], 'posts': 0, 'next_id': 10, 'comments': [], **state}))
        executable = self.root/'gh'
        executable.write_text(FAKE); executable.chmod(0o700)
        env = patch.dict(os.environ, {'TRACE_FAKE_STATE': str(path), 'TRACE_FAKE_DB': str(owner.store.path)})
        env.start(); self.addCleanup(env.stop)
        factory = patch('coherence_workflow.trace_publication.Gh', return_value=Gh(executable))
        factory.start(); self.addCleanup(factory.stop)
        return path

    def engine(self, owner, *, error=None, scope=True):
        calls = []
        class Adapter:
            def __init__(self, *a, **k): pass
            def prompt(self, prompt, **kwargs):
                calls.append('review' if kwargs.get('read_only') else 'worker')
                if error: raise error
                return (json.dumps({'approved': True, 'findings': [], 'coverage': ['fixture'], 'coverage_gaps': []})
                        if kwargs.get('read_only') else 'Actual worker submission')
        contract = admit({'delivery_issue': ISSUE, 'tasks': [{'id': 'one', 'description': 'bounded offline task'}]})
        grant = {'target': ISSUE, 'authority': {'run_id': 'run', 'target': ISSUE,
                 'operations': ['trace_comment'], 'approval_ref': 'offline fixture grant'}} if scope else None
        return Engine(owner, 'run', contract, EXECUTOR, adapter=Adapter, delivery_scope=grant), calls

    def test_normal_success_drains_before_full_body_publication_without_pending_worker(self):
        with Authority(self.project) as owner:
            remote = self.setup_remote(owner)
            requests = self.bridge(owner.store)
            engine, calls = self.engine(owner)
            result = engine.invoke()
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(calls, ['worker', 'review'])
            self.assertEqual([r['type'] for r in requests], ['trace_drain', 'trace_ack'])
            self.assertTrue(requests[0]['final'])
            self.assertTrue(result['trace']['capture']['parent_acknowledged'])
            self.assertEqual(result['trace']['publication']['state'], 'confirmed')
            state = json.loads(remote.read_text())
            body = state['comments'][0]['body']
            self.assertIn('Actual owner answer', body)
            self.assertIn('Actual worker submission', body)
            self.assertIn('abrupt process death', body)
            self.assertNotIn('transport-credential', body)
            self.assertEqual(state['posts'], 1)
            self.assertTrue(any('/issues/comments/10' in r['endpoint'] for r in state['calls']))
            self.assertEqual(result['trace']['linkage']['state'], 'confirmed')

    def test_failure_keeps_original_exception_and_publishes_retained_failure(self):
        error = Blocked('original worker failure')
        with Authority(self.project) as owner:
            remote = self.setup_remote(owner)
            engine, _ = self.engine(owner, error=error)
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(Blocked) as caught:
                engine.invoke()
            self.assertIs(caught.exception, error)
            self.assertEqual(engine.trace_finish['publication']['state'], 'confirmed')
            body = json.loads(remote.read_text())['comments'][0]['body']
            self.assertIn(str(error), body)
            self.assertIn('Parent capture unavailable', body)

    def test_cancellation_does_not_become_completion(self):
        with Authority(self.project) as owner:
            self.setup_remote(owner)
            error = KeyboardInterrupt('cancelled worker')
            engine, _ = self.engine(owner, error=error)
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(KeyboardInterrupt) as caught:
                engine.invoke()
            self.assertIs(caught.exception, error)
            self.assertEqual(owner.store.db.execute("SELECT state FROM execution_runs WHERE run_id='run'").fetchone()[0], 'interrupted')
            self.assertEqual(engine.trace_finish['publication']['state'], 'confirmed')

    def test_missing_scope_does_not_send_or_change_success(self):
        with Authority(self.project) as owner:
            remote = self.setup_remote(owner)
            engine, _ = self.engine(owner, scope=False)
            result = engine.invoke()
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(result['trace']['publication']['state'], 'deferred')
            self.assertEqual(json.loads(remote.read_text())['calls'], [])

    def test_export_readback_loss_is_uncertain_not_implementation_failure(self):
        with Authority(self.project) as owner:
            remote = self.setup_remote(owner, lost_response=True)
            engine, _ = self.engine(owner)
            result = engine.invoke()
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(result['trace']['publication']['state'], 'uncertain')
            self.assertEqual(json.loads(remote.read_text())['posts'], 1)

    def test_storage_and_optional_export_errors_do_not_mask_original_failure(self):
        with Authority(self.project) as owner:
            error = ValueError('original operation')
            engine, _ = self.engine(owner, error=error)
            with patch.object(owner.store, 'finish', side_effect=OSError('storage unavailable')), \
                 patch('coherence_workflow.trace_projection.project_trace', side_effect=OSError('export unavailable')), \
                 contextlib.redirect_stderr(io.StringIO()), self.assertRaises(ValueError) as caught:
                engine.invoke()
            self.assertIs(caught.exception, error)
            self.assertEqual(engine.trace_finish['publication']['state'], 'uncertain')

    def test_normal_parent_question_binds_observer_without_changing_resolution(self):
        with Authority(self.project) as owner:
            engine, _ = self.engine(owner)
            owner.store.start('run', self.base, contract=engine.contract, executor=EXECUTOR)
            requests = self.bridge(owner.store)
            consume = capture_questions(parent_question, owner.store, 'run')
            self.assertEqual(consume('Coordinator request'), 'Distinct coordinator resolution')
            rows = owner.store.db.execute("SELECT details FROM execution_history WHERE kind='parent_trace'").fetchall()
            self.assertTrue(any('Actual owner answer' in row[0] for row in rows))
            self.assertEqual([r['type'] for r in requests], ['question', 'trace_drain', 'trace_ack'])

    def test_failed_ack_is_a_published_gap_not_a_failed_implementation(self):
        with Authority(self.project) as owner:
            remote = self.setup_remote(owner)
            self.bridge(owner.store, ack=False)
            engine, _ = self.engine(owner)
            result = engine.invoke()
            self.assertEqual(result['status'], 'complete')
            self.assertFalse(result['trace']['capture']['parent_acknowledged'])
            self.assertEqual(result['trace']['publication']['state'], 'confirmed')
            body = json.loads(remote.read_text())['comments'][0]['body']
            self.assertIn('Actual owner answer', body)
            self.assertIn('acknowledgement failed', body)

    def test_parent_observer_storage_error_preserves_real_question_reply(self):
        with Authority(self.project) as owner:
            engine, _ = self.engine(owner)
            owner.store.start('run', self.base, contract=engine.contract, executor=EXECUTOR)
            requests = self.bridge(owner.store)
            consume = capture_questions(parent_question, owner.store, 'run')
            with patch('coherence_workflow.trace_capture.persist_parent_events', side_effect=OSError('capture failed')), \
                 contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(consume('Coordinator request'), 'Distinct coordinator resolution')
            self.assertEqual([r['type'] for r in requests], ['question', 'trace_drain'])

    def test_optional_capture_storage_failure_publishes_honest_gap(self):
        with Authority(self.project) as owner:
            remote = self.setup_remote(owner)
            self.bridge(owner.store)
            engine, _ = self.engine(owner)
            with patch('coherence_workflow.trace_capture.persist_parent_events', side_effect=OSError('capture failed')):
                result = engine.invoke()
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(result['trace']['publication']['state'], 'confirmed')
            self.assertFalse(result['trace']['capture']['parent_acknowledged'])
            self.assertIn('acknowledgement failed', json.loads(remote.read_text())['comments'][0]['body'])

    def test_optional_export_exception_preserves_success(self):
        with Authority(self.project) as owner:
            engine, _ = self.engine(owner)
            with patch('coherence_workflow.trace_projection.project_trace', side_effect=RuntimeError('export failed')):
                result = engine.invoke()
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(result['trace']['publication']['state'], 'uncertain')

    def test_partial_parts_keep_confirmed_url_and_original_success(self):
        with Authority(self.project) as owner:
            remote = self.setup_remote(owner, post_error=422, error_message='fixture length rejected; no effect')
            engine, _ = self.engine(owner)
            proofs = []
            original = engine.publish_delivery_trace
            # Supply the T006 verified diagnostic input at its existing boundary.
            # It is proof for this inspected offline API only, not a GitHub limit.
            def publish(**kwargs):
                return original(**kwargs, length_proofs=proofs)
            gh = Gh(self.root/'gh')
            def request(target, method, endpoint, body=None):
                response = gh.request(target, method, endpoint, body)
                if method == 'POST' and response['status'] == 422:
                    proofs.append(LengthProof(digest(body['body']), digest(response['raw']),
                                  'test_trace_publication.FAKE', 'Inspected fake rejects before effect.', True))
                    state = json.loads(remote.read_text())
                    state.update(post_error=503, error_on=3)
                    remote.write_text(json.dumps(state))
                return response
            with patch.object(engine, 'publish_delivery_trace', side_effect=publish), \
                 patch('coherence_workflow.trace_publication.Gh', return_value=type('Transport', (), {'request': staticmethod(request)})()):
                result = engine.invoke()
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(result['trace']['publication']['state'], 'partial')
            self.assertEqual(len(result['trace']['publication']['urls']), 1)
            self.assertEqual(json.loads(remote.read_text())['posts'], 3)

    def test_linkage_exception_does_not_erase_confirmed_publication(self):
        with Authority(self.project) as owner:
            self.setup_remote(owner)
            engine, _ = self.engine(owner)
            with patch('coherence_workflow.trace_publication.confirm_delivery_links', side_effect=OSError('link storage failed')):
                result = engine.invoke()
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(result['trace']['publication']['state'], 'confirmed')
            self.assertEqual(result['trace']['linkage']['state'], 'incomplete')

    def test_publication_precedes_optional_monitoring_teardown(self):
        with Authority(self.project) as owner:
            remote = self.setup_remote(owner)
            engine, _ = self.engine(owner)
            closed = []
            class Monitoring:
                def boundary(self, *args, **kwargs):
                    return contextlib.nullcontext()
                def close(self):
                    closed.append((json.loads(remote.read_text())['posts'], engine.trace_finish['publication']['state']))
                    raise OSError('optional exporter close failed')
            with patch('coherence_workflow.tracing.configured_tracing', return_value=Monitoring()):
                result = engine.invoke()
            self.assertEqual(result['status'], 'complete')
            self.assertIsNone(engine._local_tracing)
            self.assertEqual(closed, [(1, 'confirmed')])

    def test_missing_pr_link_authority_reports_incomplete_linkage(self):
        from test_trace_publication import PR
        with Authority(self.project) as owner:
            remote = self.setup_remote(owner)
            engine, _ = self.engine(owner)
            engine.delivery_scope['known_linked_prs'] = [PR]
            result = engine.invoke()
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(result['trace']['publication']['state'], 'confirmed')
            self.assertEqual(result['trace']['linkage']['state'], 'incomplete')
            self.assertIn('link_comment authority', result['trace']['linkage']['correction'])
            self.assertEqual(json.loads(remote.read_text())['posts'], 1)

    def test_waiting_drains_without_finalizing_or_publishing(self):
        from coherence_workflow.graph import run_graph
        with Authority(self.project) as owner:
            engine, calls = self.engine(owner)
            owner.store.start('run', self.base, contract=engine.contract, executor=EXECUTOR)
            remote = self.setup_remote(owner)
            requests = self.bridge(owner.store)
            with patch('coherence_workflow.graph._run_graph', return_value={'status': 'waiting'}):
                result = run_graph(engine)
            self.assertEqual(result['status'], 'waiting')
            self.assertFalse(requests[0]['final'])
            self.assertEqual(result['trace']['publication']['state'], 'deferred')
            self.assertEqual(json.loads(remote.read_text())['posts'], 0)
            self.assertEqual(calls, [])
