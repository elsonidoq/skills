"""Durable question delivery through the real graph, SDK fixture and Git."""
import json
import os
import socket
import threading
from pathlib import Path
from unittest.mock import patch

from langgraph.types import Command
from coherence_workflow.engine import Engine
from coherence_workflow.graph import answer_graph_question, graph_saver, task_graph
from coherence_workflow.intake import admit
from coherence_workflow.pi_adapter import parent_question, terminal_question
from coherence_workflow.cli import status
from coherence_workflow.store import Authority, git
from coherence_workflow.trace_capture import optional_record, persist_parent_events, record_worker_question
from fixtures.support import ProjectTest

EXECUTOR = {'provider': 'openai', 'model': 'gpt-4o-mini', 'effort': 'off',
            'reviewer': {'provider': 'openai', 'model': 'gpt-4o-mini', 'effort': 'off'}}


class GraphQuestionTests(ProjectTest):
    def exercise(self, answer):
        preload = Path(__file__).parent / 'fixtures' / 'steering_adapter_fixture.mjs'
        env = {'COHERENCE_HOST_PRELOAD': '1', 'NODE_OPTIONS': '--import=' + str(preload),
               'COHERENCE_STEERING_CALLBACK': 'graph-pause', 'PI_CODING_AGENT_DIR': str(self.root/'private-agent')}
        contract = admit([{'id': 'one', 'description': 'ask before effect', 'owned_paths': ['prior.txt', 'steering-owned.txt']}])
        config = {'configurable': {'thread_id': 'question'}}
        with patch.dict(os.environ, env):
            with Authority(self.project) as owner:
                owner.store.start('question', self.base, contract=contract, executor=EXECUTOR)
                engine = Engine(owner, 'question', contract, EXECUTOR, paid_scope={'apis': []})
                with graph_saver(owner) as saver:
                    graph = task_graph(engine, saver)
                    graph.invoke({}, config, durability='sync')
                    pending = graph.get_state(config).interrupts[0].value
                    self.assertEqual(pending['question']['question'], 'fixture callback')
                    def trace_pending(pending, state, **facts):
                        record_worker_question(owner.store, 'question', pending['task_id'],
                                               pending['invocation_id'], state, route='paused',
                                               **pending['question'], **facts)
                    self.assertIsNone(answer_graph_question(graph, config, lambda _: '', trace_observer=trace_pending))
                    def cancel(_):
                        raise EOFError('cancelled')
                    self.assertIsNone(answer_graph_question(graph, config, cancel, trace_observer=trace_pending))
                    self.assertTrue(graph.get_state(config).interrupts)
                    unanswered = [(r['state'], json.loads(r['details'])) for r in owner.store.db.execute(
                        "SELECT state, details FROM execution_history WHERE run_id='question' AND kind='worker_question_trace' ORDER BY seq")]
                    self.assertEqual([s for s, _ in unanswered], ['requested', 'unanswered', 'unanswered'])
                    self.assertTrue(all('resolution' not in d for _, d in unanswered))
                    private = graph.get_state(config).values['session']['file']
                    public = json.dumps(status(self.project, 'question'))
                    self.assertNotIn(private, public)
                    self.assertNotIn('fixture callback', public)
                    self.assertEqual((self.project/'prior.txt').read_text(), 'settled once\n')
            with Authority(self.project) as owner:
                engine = Engine(owner, 'question', contract, EXECUTOR, paid_scope={'apis': []}, resume=True)
                with graph_saver(owner) as saver:
                    graph = task_graph(engine, saver)
                    self.assertEqual(graph.get_state(config).interrupts[0].value, pending)
                    graph.invoke(Command(resume={'invocation_id': 'stale', 'answer': answer}), config, durability='sync')
                    self.assertTrue(graph.get_state(config).interrupts)
                    self.assertEqual(owner.store.db.execute(
                        "SELECT count(*) FROM execution_history WHERE run_id='question' AND kind='worker_question_trace' AND state='resolved'").fetchone()[0], 0)
                    if answer == 'actual consent':
                        with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', return_value=answer):
                            result = answer_graph_question(graph, config, terminal_question)
                    else:
                        endpoint = str(self.root/'bridge.sock')
                        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        server.bind(endpoint)
                        server.listen(3)
                        def respond():
                            parent_id = None
                            for _ in range(3):
                                conn, _ = server.accept()
                                with conn, conn.makefile('r') as stream:
                                    request = json.loads(stream.readline())
                                    if request['type'] == 'question':
                                        parent_id = request['request_id']
                                        reply = {'answer': answer}
                                    elif request['type'] == 'trace_drain':
                                        reply = {'events': [{'version': 1, 'id': 'owner-result', 'kind': 'owner_result',
                                                 'tool_call_id': 'owner-tool', 'request_id': parent_id,
                                                 'content': 'actual owner words'}]}
                                    else:
                                        reply = {'acknowledged': True}
                                    conn.sendall((json.dumps({'request_id': request['request_id'], **reply}) + '\n').encode())
                            server.close()
                        thread = threading.Thread(target=respond)
                        thread.start()
                        with patch.dict(os.environ, {'COHERENCE_PARENT_BRIDGE_SOCKET': endpoint,
                                'COHERENCE_PARENT_BRIDGE_TOKEN': 'token', 'COHERENCE_PARENT_BRIDGE_SESSION': 'parent',
                                'COHERENCE_PARENT_BRIDGE_RUN': 'question'}):
                            def trace_pending(pending, state, **facts):
                                optional_record(record_worker_question, owner.store, 'question', pending['task_id'],
                                                pending['invocation_id'], state, route='paused',
                                                **pending['question'], **facts)
                            def attached(text):
                                return parent_question(text, trace_observer=lambda run, events:
                                                       persist_parent_events(owner.store, run, events))
                            result = answer_graph_question(graph, config, attached, trace_observer=trace_pending)
                        thread.join()
                    self.assertIn('one', result['checkpoints'])
                    rows = list(owner.store.db.execute("SELECT state FROM execution_history WHERE run_id='question' AND kind='worker_invocation' ORDER BY seq"))
                    self.assertEqual([r['state'] for r in rows], ['started', 'returned', 'started', 'returned'])
                    traces = [(r['state'], json.loads(r['details'])) for r in owner.store.db.execute(
                        "SELECT state, details FROM execution_history WHERE run_id='question' AND kind='worker_question_trace' ORDER BY seq")]
                    requested = next(d for s, d in traces if s == 'requested')
                    resolved = next(d for s, d in traces if s == 'resolved')
                    continued = next(d for s, d in traces if s == 'continuation_returned')
                    self.assertEqual(requested['tool_call_id'], 'callback-tool')
                    self.assertEqual(requested['question'], 'fixture callback')
                    self.assertEqual(resolved['invocation_id'], pending['invocation_id'])
                    self.assertEqual(resolved['resolution'], answer)
                    self.assertEqual(continued['predecessor_invocation_id'], pending['invocation_id'])
                    self.assertNotEqual(continued['invocation_id'], pending['invocation_id'])
                    if answer != 'actual consent':
                        parent = next(d for s, d in traces if s == 'parent_request')
                        self.assertTrue(parent['parent_request_id'])
                        self.assertEqual(parent['invocation_id'], pending['invocation_id'])
                        owner_event = json.loads(owner.store.db.execute(
                            "SELECT details FROM execution_history WHERE run_id='question' AND kind='parent_trace'").fetchone()[0])['event']
                        self.assertEqual(owner_event['request_id'], parent['parent_request_id'])
                        self.assertEqual(owner_event['content'], 'actual owner words')
                        self.assertNotEqual(owner_event['content'], resolved['resolution'])
        session_text = Path(private).read_text()
        self.assertGreaterEqual(session_text.count('Current execution authority'), 2)
        self.assertGreaterEqual(session_text.lower().count('small isolated tests and local test databases'), 2)
        self.assertIn('Pending question, actual answer and settled effects', session_text)
        self.assertIn(answer, session_text)
        self.assertEqual(session_text.count('"id":"prior-tool"'), 1)
        self.assertFalse((self.project/'premature.txt').exists())
        if answer == 'actual consent':
            self.assertEqual(git(self.project, 'show', 'HEAD:steering-owned.txt'), b'consented\n')
        else:
            self.assertFalse((self.project/'steering-owned.txt').exists())

    def test_consent(self):
        self.exercise('actual consent')

    def test_denial(self):
        self.exercise('actual denial')
