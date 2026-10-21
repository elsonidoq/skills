"""Transport framing, local edit errors, current questions, and owned cancellation."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
from unittest.mock import patch

from coherence_workflow.pi_adapter import PiAdapter, parent_question, terminal_question
from coherence_workflow.store import Blocked
from fixtures.support import ProjectTest


class SDKTransportTests(ProjectTest):
    def fixture(self, body):
        host = self.root/'offline_host.py'
        host.write_text('import json,sys\nrequest=json.loads(input())\n' + body)
        return patch('coherence_workflow.pi_adapter.host_path', return_value=host), patch.dict(
            'os.environ', {'COHERENCE_NODE': sys.executable})

    def test_pre_steering_transport_with_opt_in_host(self):
        """Frozen pre-change framing reaches the changed production host dispatcher."""
        host = Path(__file__).resolve().parents[1] / 'pi-host' / 'host.mjs'
        preload = Path(__file__).with_name('cleanup_adapter_fixture.mjs')
        env = {**os.environ, 'COHERENCE_HOST_PRELOAD': '1',
               'NODE_OPTIONS': '--import=' + str(preload),
               'PI_CODING_AGENT_DIR': str(self.root/'private-agent')}
        proc = subprocess.Popen(['node', str(host)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, encoding='utf-8', cwd=self.project, env=env)
        try:
            # This deliberately predates sessionObservations and steering: it is
            # the original one-request/one-uncorrelated-callback transport.
            request = {'project': str(self.project), 'executor': {'provider': 'openai', 'model': 'gpt-4o-mini',
                       'effort': 'medium'}, 'prompt': 'ordinary prompt', 'readOnly': False,
                       # Existing observation opt-in is deliberately not steering consent.
                       'sessionObservations': True}
            proc.stdin.write(json.dumps(request) + '\n')
            proc.stdin.flush()
            records = []
            while True:
                line = proc.stdout.readline()
                if not line:
                    self.fail('production host ended before a transport record: ' + proc.stderr.read())
                record = json.loads(line)
                records.append(record)
                if record['type'] == 'session':
                    self.assertIn('session', record)
                elif record['type'] == 'question':
                    # Original replies have no correlation wrapper.
                    self.assertNotIn('request_id', record)
                    proc.stdin.write(json.dumps({'answer': 'ordinary callback'}) + '\n')
                    proc.stdin.flush()
                elif record['type'] == 'result':
                    self.assertEqual(record['text'], 'legacy complete')
                    break
                else:
                    self.fail('unexpected legacy record: ' + repr(record))
            self.assertEqual([record['type'] for record in records], ['session', 'question', 'result'])
            self.assertEqual(proc.wait(timeout=10), 0, proc.stderr.read())
        finally:
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=10)
            proc.stdout.close()
            proc.stderr.close()

    def test_local_path_error_can_be_corrected_same_host_conversation(self):
        body = '''print(json.dumps({'type':'claim','path':'bad.txt'}),flush=True)
a=json.loads(input());assert 'error' in a
print(json.dumps({'type':'claim','path':'owned.txt'}),flush=True)
assert json.loads(input()) == {'ok':True}
print(json.dumps({'type':'result','text':'corrected'}),flush=True)
'''
        claimed = []
        def claim(name):
            if name == 'bad.txt': raise Blocked('outside task paths')
            claimed.append(name)
        a, b = self.fixture(body)
        with a, b:
            self.assertEqual(PiAdapter(self.project, {}).prompt('fixture', claim=claim), 'corrected')
        self.assertEqual(claimed, ['owned.txt'])

    def test_current_ui_question_no_receipts_or_transcript_proof(self):
        a, b = self.fixture("print(json.dumps({'type':'question','question':'PRIVATE-SENTINEL'}),flush=True)\nassert json.loads(input()) == {'answer':'yes'}\nprint(json.dumps({'type':'result','text':'answered'}),flush=True)\n")
        events = []
        with a, b:
            self.assertEqual(PiAdapter(self.project, {}, question=lambda q: 'yes', observe_question=events.append).prompt('fixture'), 'answered')
        self.assertEqual(events, ['requested', 'returned', 'sent'])
        self.assertNotIn('PRIVATE-SENTINEL', str(events))

    def test_repeated_framed_questions_use_the_same_callback(self):
        body = "for question in ('First?', 'Second?'):\n print(json.dumps({'type':'question','question':question}),flush=True); assert json.loads(input()) == {'answer': question + ' answer'}\nprint(json.dumps({'type':'result','text':'sent'}),flush=True)\n"
        a, b = self.fixture(body)
        with a, b:
            self.assertEqual(PiAdapter(self.project, {}, question=lambda question: question + ' answer').prompt('fixture'), 'sent')

    def test_parent_question_requires_correlated_bridge_response(self):
        endpoint = str(self.root/'bridge.sock')
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(endpoint)
        server.listen(1)
        received = []
        def serve():
            client, _ = server.accept()
            with client:
                request = json.loads(client.makefile('r', encoding='utf-8').readline())
                received.append(request)
                client.sendall((json.dumps({'request_id': request['request_id'], 'answer': 'yes'}) + '\n').encode())
            server.close()
        thread = threading.Thread(target=serve)
        thread.start()
        values = {'COHERENCE_PARENT_BRIDGE_SOCKET': endpoint, 'COHERENCE_PARENT_BRIDGE_TOKEN': 'token',
                  'COHERENCE_PARENT_BRIDGE_SESSION': 'session', 'COHERENCE_PARENT_BRIDGE_RUN': 'run'}
        with patch.dict(os.environ, values, clear=False):
            self.assertEqual(parent_question('PRIVATE-SENTINEL'), 'yes')
        thread.join()
        self.assertEqual(received[0]['run_id'], 'run')
        self.assertNotIn('PRIVATE-SENTINEL', str(received[0] | {'question': '<redacted>'}))

    def test_parent_readiness_requires_positive_correlated_response(self):
        for ready, correlate in [(True, True), (False, True), (True, False)]:
            with self.subTest(ready=ready, correlate=correlate):
                endpoint = str(self.root/('ready-' + str(ready) + str(correlate) + '.sock'))
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
                    server.bind(endpoint)
                    server.listen(1)
                    received = []
                    def serve():
                        client, _ = server.accept()
                        with client:
                            request = json.loads(client.makefile('r', encoding='utf-8').readline())
                            received.append(request)
                            response = {'request_id': request['request_id'] if correlate else 'wrong', 'ready': ready}
                            client.sendall((json.dumps(response) + '\n').encode())
                    thread = threading.Thread(target=serve)
                    thread.start()
                    values = {'COHERENCE_PARENT_BRIDGE_SOCKET': endpoint, 'COHERENCE_PARENT_BRIDGE_TOKEN': 'token',
                              'COHERENCE_PARENT_BRIDGE_SESSION': 'session', 'COHERENCE_PARENT_BRIDGE_RUN': 'run'}
                    with patch.dict(os.environ, values):
                        if ready and correlate:
                            self.assertIsNone(parent_question(None, ready=True))
                        else:
                            with self.assertRaises(Blocked): parent_question(None, ready=True)
                    thread.join()
                    self.assertEqual(received[0]['type'], 'ready')

    def test_parent_question_reports_unavailable_bridge(self):
        with patch.dict(os.environ, {'COHERENCE_PARENT_BRIDGE_SOCKET': str(self.root/'missing.sock'),
                                     'COHERENCE_PARENT_BRIDGE_TOKEN': 'token',
                                     'COHERENCE_PARENT_BRIDGE_SESSION': 'session',
                                     'COHERENCE_PARENT_BRIDGE_RUN': 'run'}, clear=False):
            with self.assertRaisesRegex(Blocked, 'parent owner bridge unavailable'):
                parent_question('Scope?')

    def test_question_recorder_failure_does_not_block_framed_answer_send(self):
        body = "print(json.dumps({'type':'question','question':'PRIVATE-SENTINEL'}),flush=True)\nassert json.loads(input()) == {'answer':'yes'}\nprint(json.dumps({'type':'result','text':'sent'}),flush=True)\n"
        a, b = self.fixture(body)
        with a, b:
            self.assertEqual(PiAdapter(self.project, {}, question=lambda q: 'yes', observe_question=lambda state: (_ for _ in ()).throw(RuntimeError('recorder'))).prompt('fixture'), 'sent')

    def test_callback_failure_does_not_replace_broken_answer_send(self):
        import time
        closed = self.root/'closed'
        body = "from pathlib import Path\nimport os,time\nprint(json.dumps({'type':'question','question':'PRIVATE-SENTINEL'}),flush=True)\nos.close(0)\nPath(" + repr(str(closed)) + ").write_text('closed')\ntime.sleep(1)\n"
        a, b = self.fixture(body)
        def answer(question):
            deadline = time.monotonic() + 5
            while not closed.exists() and time.monotonic() < deadline: time.sleep(.01)
            return 'yes'
        with a, b, self.assertRaises(BrokenPipeError):
            PiAdapter(self.project, {}, question=answer, observe_question=lambda state: (_ for _ in ()).throw(RuntimeError('recorder'))).prompt('fixture')

    def test_noninteractive_question_stops_without_fabricating_answer(self):
        with patch('sys.stdin.isatty', return_value=False):
            with self.assertRaisesRegex(Blocked, 'owner input needed'):
                terminal_question('Real scope decision?')

    def test_large_result_not_transport_cap(self):
        a, b = self.fixture("print(json.dumps({'type':'result','text':'a'*600000}),flush=True)\n")
        with a, b:
            self.assertEqual(len(PiAdapter(self.project, {}).prompt('fixture')), 600000)

    def test_eof_and_protocol_errors_report_actual_operation(self):
        for body, reason in [("pass\n", 'without a result'), ("print('not-json')\n", 'invalid SDK transport'),
                             ("print(json.dumps({'type':'unknown'}))\n", 'unknown SDK transport'),
                             ("print(json.dumps({'type':'error','message':'actual SDK failure'}))\n", 'actual SDK failure')]:
            a, b = self.fixture(body)
            with a, b, self.assertRaisesRegex(Blocked, reason):
                PiAdapter(self.project, {}).prompt('fixture')

    def test_optional_observer_failure_does_not_interrupt_sdk_prompt(self):
        a, b = self.fixture("print(json.dumps({'type':'event','event':'auto_compaction_start'}),flush=True)\nprint(json.dumps({'type':'result','text':'continued'}),flush=True)\n")
        def broken_observer(value): raise RuntimeError('optional display unavailable')
        with a, b:
            self.assertEqual(PiAdapter(self.project, {}, observe=broken_observer).prompt('fixture'), 'continued')

    def test_unanswered_question_closes_input_before_waiting_for_owned_host(self):
        a, b = self.fixture("import signal\nsignal.signal(signal.SIGTERM,lambda *args: None)\nprint(json.dumps({'type':'question','question':'Scope?'}),flush=True)\nassert sys.stdin.read() == ''\n")
        def pending(question): raise Blocked('owner input needed: ' + question)
        with a, b, self.assertRaisesRegex(Blocked, 'owner input needed: Scope'):
            PiAdapter(self.project, {}, question=pending).prompt('fixture')
