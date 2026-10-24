"""Offline authority propagation fixtures; no provider request is sent."""
import json
import os
import sys
from unittest.mock import patch

from coherence_workflow.cli import main, settle_paid_scope
from coherence_workflow.engine import Engine, _ROUTINE_AUTHORITY
from coherence_workflow.intake import admit
from coherence_workflow.pi_adapter import PiAdapter
from coherence_workflow.store import Authority, Blocked
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline-not-provider-success', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}}


class RoutineDefaultsTests(ProjectTest):
    def test_routine_defaults_reach_worker_fixer_and_reviewer_without_questions(self):
        prompts, questions = [], []
        case = self

        class Capture:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, *, read_only=False, **kwargs):
                prompts.append((prompt, read_only))
                return '{"approved":true,"findings":[]}' if read_only else '{"status":"completed","summary":"offline worker"}'

        def run(run_id, contract):
            with Authority(self.project) as authority:
                return Engine(authority, run_id, admit(contract), EXECUTOR, adapter=Capture,
                              question=lambda question: questions.append(question)).invoke()

        run('worker', [{'id': 'worker', 'description': 'ordinary fixture'}])
        run('fixer', {'monitor': {'correction_of': {'run_id': 'worker', 'review_execution_id': 'review'}},
                      'tasks': [{'id': 'fixer', 'description': 'ordinary fixture'}]})
        self.assertEqual(questions, [])
        self.assertEqual(len(prompts), 4)
        for prompt, read_only in prompts:
            self.assertIn(_ROUTINE_AUTHORITY, prompt)
            self.assertIn('This authority is not proof that checks succeeded.', prompt)
            self.assertIn('Do not ask merely because files changed.', prompt)
            self.assertIn('global installs, credential changes, deployment, pushing', prompt)
            if read_only:
                self.assertIn('read-only and are NOT the implementation conversation', prompt)

    def test_zero_send_transport_carries_final_routine_authority(self):
        capture = self.root / 'provider-bound.json'
        host = self.root / 'zero_send_host.py'
        host.write_text("""import json, os
from pathlib import Path
request = json.loads(input())
Path(os.environ['CAPTURE']).write_text(json.dumps(request))
print(json.dumps({'type': 'result', 'text': 'offline'}), flush=True)
""")
        with patch('coherence_workflow.pi_adapter.host_path', return_value=host), \
             patch.dict(os.environ, {'COHERENCE_NODE': sys.executable, 'CAPTURE': str(capture)}):
            self.assertEqual(PiAdapter(self.project, EXECUTOR).prompt(_ROUTINE_AUTHORITY), 'offline')
        request = json.loads(capture.read_text())
        self.assertEqual(request['prompt'], _ROUTINE_AUTHORITY)
        self.assertFalse(request['readOnly'])


class PaidScopeTests(ProjectTest):
    def test_selected_worker_and_reviewer_need_no_separate_consent(self):
        executor = {**EXECUTOR, 'reviewer': {**{key: value for key, value in EXECUTOR.items() if key != 'reviewer'},
                                              'provider': 'other'}}
        with patch('coherence_workflow.cli.Engine') as engine, \
             patch('coherence_workflow.cli.terminal_question', side_effect=lambda text: self.fail(text)):
            engine.return_value.invoke.return_value = {'status': 'completed'}
            tasks, config = self.root/'tasks.json', self.root/'executor.json'
            tasks.write_text('{"tasks":[{"id":"dummy","description":"Synthetic fixture"}]}')
            config.write_text(json.dumps(executor))
            self.assertEqual(main(['start', '--project', str(self.project), '--tasks', str(tasks),
                                   '--executor', str(config), '--run', 'ordinary']), 0)
            self.assertEqual(engine.call_args.kwargs['paid_scope'],
                             {'agent_providers': ['fixture', 'other'], 'apis': []})

    def test_approved_apis_do_not_depend_on_model_provider_list(self):
        scope = {'approved': True, 'agent_providers': ['old-provider'], 'apis': ['paid API']}
        result = settle_paid_scope({'paid_scope': scope}, EXECUTOR, lambda text: self.fail(text))
        self.assertEqual(result, {'agent_providers': ['fixture'], 'apis': ['paid API']})

    def test_new_or_unapproved_apis_still_ask(self):
        for contract in ({'paid_apis': ['new API']},
                         {'paid_scope': {'approved': False, 'apis': ['new API']}},
                         {'paid_scope': {'approved': True, 'apis': ['old API']}, 'paid_apis': ['new API']}):
            with self.subTest(contract=contract):
                questions = []
                result = settle_paid_scope(contract, EXECUTOR, lambda text: questions.append(text) or 'yes')
                self.assertEqual(len(questions), 1)
                self.assertIn('new API', questions[0])
                self.assertIn('new API', result['apis'])
                self.assertNotIn('agent-provider', questions[0])

    def test_missing_or_denied_scope_stops_before_provider_or_storage(self):
        tasks, executor = self.root/'tasks.json', self.root/'executor.json'
        tasks.write_text('{"paid_apis":["fixture test API"],"tasks":[{"id":"dummy","description":"Synthetic fixture"}]}')
        executor.write_text(json.dumps(EXECUTOR))
        for answer in ('no', None):
            with self.subTest(answer=answer), patch('coherence_workflow.cli.PiAdapter') as adapter:
                asked = []
                def question(text):
                    asked.append(text)
                    if answer is None:
                        raise Blocked('owner input unavailable')
                    return answer
                with patch('coherence_workflow.cli.terminal_question', side_effect=question), \
                     patch.dict(os.environ, {key: '' for key in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                                                                  'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}):
                    code = main(['start', '--project', str(self.project), '--tasks', str(tasks),
                                 '--executor', str(executor), '--run', 'scope-' + str(answer)])
                self.assertEqual(code, 2)
                self.assertEqual(len(asked), 1)
                self.assertIn('Approve paid application/test APIs:', asked[0])
                self.assertIn('fixture test API', asked[0])
                adapter.assert_not_called()
                self.assertFalse((self.project/'.coherence').exists())

    def test_granted_scope_reaches_every_role_and_provider_bound_request(self):
        prompts, questions = [], []
        scope = {'agent_providers': ['fixture'], 'apis': ['fixture test API']}
        class Capture:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, *, read_only=False, **kwargs):
                prompts.append((prompt, read_only))
                return '{"approved":true,"findings":[]}' if read_only else '{"status":"completed","summary":"offline worker"}'
        with Authority(self.project) as authority:
            Engine(authority, 'granted', admit([{'id': 'dummy', 'description': 'Synthetic fixture'}]),
                   EXECUTOR, adapter=Capture, paid_scope=scope,
                   question=lambda text: questions.append(text)).invoke()
        self.assertEqual(questions, [])
        self.assertEqual(len(prompts), 2)
        granted = 'Paid application/test APIs approved for this unchanged run only: fixture test API.'
        self.assertTrue(all('Ask before using any additional paid application/test API' in prompt for prompt, _ in prompts))
        self.assertTrue(all(granted in prompt for prompt, _ in prompts))

        capture = self.root / 'paid-provider-bound.json'
        host = self.root / 'paid_zero_send_host.py'
        host.write_text("""import json, os
from pathlib import Path
request = json.loads(input())
Path(os.environ['CAPTURE']).write_text(json.dumps(request))
print(json.dumps({'type': 'result', 'text': 'offline'}), flush=True)
""")
        with patch('coherence_workflow.pi_adapter.host_path', return_value=host), \
             patch.dict(os.environ, {'COHERENCE_NODE': sys.executable, 'CAPTURE': str(capture)}):
            self.assertEqual(PiAdapter(self.project, EXECUTOR).prompt(granted), 'offline')
        self.assertEqual(json.loads(capture.read_text())['prompt'], granted)
