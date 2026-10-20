"""Transport framing, local edit errors, current questions, and owned cancellation."""
import json
from pathlib import Path
import sys
from unittest.mock import patch

from coherence_workflow.pi_adapter import PiAdapter, terminal_question
from coherence_workflow.store import Blocked
from fixtures.support import ProjectTest


class SDKTransportTests(ProjectTest):
    def fixture(self, body):
        host = self.root/'offline_host.py'
        host.write_text('import json,sys\nrequest=json.loads(input())\n' + body)
        return patch('coherence_workflow.pi_adapter.host_path', return_value=host), patch.dict(
            'os.environ', {'COHERENCE_NODE': sys.executable})

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
