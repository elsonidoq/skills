"""Production consuming-input seam; isolated SQLite/Git, no paid provider or remote effects."""
import io
import json
import sys
from unittest.mock import Mock, patch

from coherence_workflow.cli import settle_paid_scope
from coherence_workflow.engine import Engine
from coherence_workflow.graph import answer_graph_question
from coherence_workflow.intake import admit
from coherence_workflow.pi_adapter import PiAdapter, parent_question
from coherence_workflow.store import Authority, Blocked
from coherence_workflow.trace_capture import capture_questions, persist_parent_events
from fixtures.support import ProjectTest

EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'reviewer', 'effort': 'medium'}}


class TerminalTraceTests(ProjectTest):
    def engine(self, authority, run='terminal', **kwargs):
        return Engine(authority, run, admit([{'id': 'one', 'description': 'fixture'}]),
                      EXECUTOR, **kwargs)

    def rows(self, authority, run='terminal'):
        return [(row['state'], json.loads(row['details'])) for row in authority.store.db.execute(
            "SELECT state,details FROM execution_history WHERE run_id=? AND kind='consuming_question_trace' ORDER BY seq", (run,))]

    def test_actual_input_answer_denial_and_once_only_wrapper(self):
        with Authority(self.project) as owner:
            owner.store.start('terminal', self.base)
            engine = self.engine(owner)
            self.assertIs(capture_questions(engine.question, owner.store, 'terminal'), engine.question)
            with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', side_effect=['yes', 'no']) as actual:
                self.assertEqual(engine.question('Actual approval?'), 'yes')
                self.assertEqual(engine.question('Actual denial?', owner_only=True,
                                                decision_context={'scope': 'fixture'}), 'no')
            self.assertEqual([call.args[0] for call in actual.call_args_list],
                             ['Actual approval?\n> ', 'Actual denial?\n> '])
            rows = self.rows(owner)
            self.assertEqual([facts['answer'] for _, facts in rows], ['yes', 'no'])
            self.assertEqual([facts['prompt'] for _, facts in rows], ['Actual approval?', 'Actual denial?'])
            self.assertTrue(all(state == 'answered' and facts['responder_class'] == 'owner' for state, facts in rows))
            self.assertTrue(rows[1][1]['owner_only'])
            self.assertNotEqual(rows[0][1]['question_id'], rows[1][1]['question_id'])

    def test_input_exception_identity_and_recording_failure_do_not_change_operation(self):
        with Authority(self.project) as owner:
            owner.store.start('terminal', self.base)
            engine = self.engine(owner)
            error = KeyboardInterrupt('actual cancellation')
            with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', side_effect=error):
                with self.assertRaises(KeyboardInterrupt) as raised:
                    engine.question('Interrupt?')
            self.assertIs(raised.exception, error)
            state, facts = self.rows(owner)[0]
            self.assertEqual((state, facts['error_type'], facts['error']),
                             ('exception', 'KeyboardInterrupt', 'actual cancellation'))
            with patch('coherence_workflow.trace_capture.record_consuming_question', side_effect=OSError('capture failed')), \
                 patch('sys.stdin.isatty', return_value=True), patch('sys.stderr', new_callable=io.StringIO) as warning, \
                 patch('builtins.input', side_effect=['no', error]) as actual:
                self.assertEqual(engine.question('Still deny?'), 'no')
                with self.assertRaises(KeyboardInterrupt) as raised:
                    engine.question('Still interrupt?')
                self.assertIs(raised.exception, error)
                self.assertEqual(actual.call_count, 2)
                self.assertEqual(warning.getvalue().count('question trace capture gap:'), 2)
            self.assertEqual(len(self.rows(owner)), 1)

    def test_known_transport_credential_is_filtered_without_changing_real_input(self):
        with Authority(self.project) as owner:
            owner.store.start('terminal', self.base)
            engine = self.engine(owner)
            with patch.dict('os.environ', {'COHERENCE_PARENT_BRIDGE_TOKEN': 'credential-sentinel'}), \
                 patch('sys.stdin.isatty', return_value=True), \
                 patch('builtins.input', return_value='ordinary answer credential-sentinel'):
                self.assertEqual(engine.question('ordinary question credential-sentinel'),
                                 'ordinary answer credential-sentinel')
            facts = self.rows(owner)[0][1]
            self.assertEqual(facts['prompt'], 'ordinary question [excluded credential]')
            self.assertEqual(facts['answer'], 'ordinary answer [excluded credential]')
            self.assertTrue(facts['gaps'])

    def test_noninteractive_absence_and_eof_are_exceptions_not_answers(self):
        with Authority(self.project) as owner:
            owner.store.start('terminal', self.base)
            engine = self.engine(owner)
            with patch('sys.stdin.isatty', return_value=False), patch('builtins.input') as actual:
                with self.assertRaisesRegex(Blocked, 'unavailable'):
                    engine.question('Unavailable?')
                actual.assert_not_called()
            with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', side_effect=EOFError):
                with self.assertRaisesRegex(Blocked, 'lost'):
                    engine.question('Lost input?')
            rows = self.rows(owner)
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(state == 'exception' and 'answer' not in facts for state, facts in rows))

    def test_production_manual_gate_denial_keeps_gate_and_task_binding(self):
        contract = admit([{'id': 'one', 'description': 'fixture', 'gates': ['Manual inspection']}])
        adapter = Mock(side_effect=AssertionError('denied gate must not launch a worker'))
        with Authority(self.project) as owner:
            engine = Engine(owner, 'terminal', contract, EXECUTOR, adapter=adapter)
            with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', return_value='no') as actual:
                with self.assertRaisesRegex(Blocked, 'manual gate not approved'):
                    engine.invoke()
            adapter.assert_not_called()
            actual.assert_called_once_with('Manual inspection\nApprove this gate? [yes/no]\n> ')
            state, facts = self.rows(owner)[0]
            self.assertEqual((state, facts['answer'], facts['task_id'], facts['purpose']),
                             ('answered', 'no', 'one', 'manual_gate'))

    def test_reopened_run_and_paused_question_keep_exact_context(self):
        with Authority(self.project) as owner:
            owner.store.start('terminal', self.base)
        pending = {'task_id': 'one', 'invocation_id': 'original-call',
                   'question': {'question': 'Retained question?', 'tool_call_id': 'exact-tool'}}
        graph = Mock()
        graph.get_state.return_value.interrupts = [Mock(value=pending)]
        graph.invoke.return_value = 'continued'
        with Authority(self.project) as owner:
            engine = self.engine(owner, resume=True)
            with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', return_value='actual reopened answer'):
                self.assertEqual(answer_graph_question(graph, {}, engine.question), 'continued')
        with Authority(self.project) as owner:
            facts = self.rows(owner)[0][1]
            self.assertEqual((facts['task_id'], facts['invocation_id'], facts['tool_call_id'], facts['route']),
                             ('one', 'original-call', 'exact-tool', 'paused'))
            self.assertEqual(facts['answer'], 'actual reopened answer')

    def test_synchronous_adapter_keeps_caller_identity_and_actual_terminal_answer(self):
        host = self.root / 'controlled_host.py'
        host.write_text("import json\nrequest=json.loads(input())\n"
                        "print(json.dumps({'type':'question','request_id':'callback','tool_call_id':'exact-tool','question':'Actual worker question?'}),flush=True)\n"
                        "assert json.loads(input()) == {'type':'reply','request_id':'callback','reply':{'answer':'no'}}\n"
                        "print(json.dumps({'type':'result','text':'actual denial delivered'}),flush=True)\n")
        with Authority(self.project) as owner:
            owner.store.start('terminal', self.base)
            engine = self.engine(owner)
            adapter = PiAdapter(self.project, EXECUTOR, question=engine.question)
            with patch('coherence_workflow.pi_adapter.host_path', return_value=host), \
                 patch.dict('os.environ', {'COHERENCE_NODE': sys.executable}), \
                 patch('sys.stdin.isatty', return_value=True), patch('builtins.input', return_value='no'):
                result = adapter.prompt('offline fixture', steering={
                    'run_id': 'terminal', 'task_id': 'one', 'invocation_id': 'current-call', 'role': 'worker'})
            self.assertEqual(result, 'actual denial delivered')
            facts = self.rows(owner)[0][1]
            self.assertEqual((facts['task_id'], facts['invocation_id'], facts['tool_call_id']),
                             ('one', 'current-call', 'exact-tool'))
            self.assertEqual((facts['answer'], facts['responder_class'], facts['route']), ('no', 'owner', 'synchronous'))
            self.assertEqual(facts['callback_request_id'], 'callback')

    def test_paid_before_run_is_not_attributed_but_run_bound_paid_is_captured(self):
        with Authority(self.project) as owner:
            engine = self.engine(owner)
            with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', return_value='yes') as actual:
                settle_paid_scope({'paid_apis': ['fixture API']}, EXECUTOR, engine.question)
                self.assertEqual(self.rows(owner), [])
                owner.store.start('terminal', self.base)
                settle_paid_scope({'paid_apis': ['fixture API']}, EXECUTOR, engine.question)
                self.assertEqual(actual.call_count, 2)
            self.assertEqual(len(self.rows(owner)), 1)
            self.assertEqual(self.rows(owner)[0][1]['prompt'], 'Approve paid application/test APIs: fixture API. [yes/no]')

    def test_attached_reply_is_coordinator_not_duplicate_owner_answer(self):
        # The actual parent consumer uses the controlled socket; owner facts still use T001.
        client = Mock()
        socket_context = Mock()
        socket_context.__enter__ = Mock(return_value=client)
        socket_context.__exit__ = Mock(return_value=False)
        sent = []
        client.sendall.side_effect = lambda body: sent.append(json.loads(body))
        client.makefile.side_effect = lambda *args, **kwargs: io.StringIO(json.dumps({
            'request_id': sent[-1]['request_id'], 'answer': 'coordinator resolution, not owner wording'}))
        env = {'COHERENCE_PARENT_BRIDGE_SOCKET': '/fixture/socket', 'COHERENCE_PARENT_BRIDGE_TOKEN': 'credential-sentinel',
               'COHERENCE_PARENT_BRIDGE_SESSION': 'parent', 'COHERENCE_PARENT_BRIDGE_RUN': 'terminal'}
        with Authority(self.project) as owner:
            owner.store.start('terminal', self.base)
            event = {'version': 1, 'id': 'owner-event', 'kind': 'tool_result', 'toolCallId': 'owner-tool',
                     'answer': 'actual owner wording'}
            persist_parent_events(owner.store, 'terminal', [event])
            engine = self.engine(owner, question=parent_question)
            with patch.dict('os.environ', env), patch('coherence_workflow.pi_adapter.socket.socket', return_value=socket_context):
                self.assertEqual(engine.question('Attached question?'), 'coordinator resolution, not owner wording')
            rows = self.rows(owner)
            self.assertEqual(len(rows), 1)
            facts = rows[0][1]
            self.assertEqual(facts['responder_class'], 'coordinator')
            self.assertEqual(facts['parent_request_id'], sent[0]['request_id'])
            self.assertNotIn('credential-sentinel', json.dumps(rows))
            parent_rows = owner.store.db.execute("SELECT details FROM execution_history WHERE kind='parent_trace'").fetchall()
            self.assertEqual(len(parent_rows), 1)
            self.assertEqual(json.loads(parent_rows[0][0])['event']['answer'], 'actual owner wording')
