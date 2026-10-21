"""Offline authority propagation fixtures; no provider request is sent."""
import json
import os
import sys
from unittest.mock import patch

from coherence_workflow.engine import Engine, _ROUTINE_AUTHORITY
from coherence_workflow.intake import admit
from coherence_workflow.pi_adapter import PiAdapter
from coherence_workflow.store import Authority
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline-not-provider-success', 'effort': 'medium'}


class RoutineDefaultsTests(ProjectTest):
    def test_routine_defaults_reach_worker_fixer_and_reviewer_without_questions(self):
        prompts, questions = [], []
        case = self

        class Capture:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, *, read_only=False, **kwargs):
                prompts.append((prompt, read_only))
                return '{"approved":true,"findings":[]}' if read_only else 'offline worker'

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
