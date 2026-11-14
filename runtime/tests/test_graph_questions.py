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
                    self.assertIsNone(answer_graph_question(graph, config, lambda _: ''))
                    self.assertTrue(graph.get_state(config).interrupts)
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
                    if answer == 'actual consent':
                        with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', return_value=answer):
                            result = answer_graph_question(graph, config, terminal_question)
                    else:
                        endpoint = str(self.root/'bridge.sock')
                        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        server.bind(endpoint)
                        server.listen(1)
                        def respond():
                            conn, _ = server.accept()
                            with conn, conn.makefile('r') as stream:
                                request = json.loads(stream.readline())
                                conn.sendall((json.dumps({'request_id': request['request_id'], 'answer': answer}) + '\n').encode())
                            server.close()
                        thread = threading.Thread(target=respond)
                        thread.start()
                        with patch.dict(os.environ, {'COHERENCE_PARENT_BRIDGE_SOCKET': endpoint,
                                'COHERENCE_PARENT_BRIDGE_TOKEN': 'token', 'COHERENCE_PARENT_BRIDGE_SESSION': 'parent',
                                'COHERENCE_PARENT_BRIDGE_RUN': 'question'}):
                            result = answer_graph_question(graph, config, parent_question)
                        thread.join()
                    self.assertIn('one', result['checkpoints'])
                    rows = list(owner.store.db.execute("SELECT state FROM execution_history WHERE run_id='question' AND kind='worker_invocation' ORDER BY seq"))
                    self.assertEqual([r['state'] for r in rows], ['started', 'returned', 'started', 'returned'])
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
