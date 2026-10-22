"""T008 offline transport seam: private saved identity is reopened, not ambiently adopted."""
import json
import sys
from pathlib import Path
from unittest.mock import patch

from coherence_workflow.pi_adapter import PiAdapter
from fixtures.support import ProjectTest


class SavedSessionTransportTests(ProjectTest):
    def test_actual_host_cleanup_tool_reaches_adapter_selective_cleanup(self):
        from coherence_workflow.git_effects import FocusedGit
        outputs = self.project/'web/dist'
        outputs.mkdir(parents=True)
        (outputs/'known.js').write_text('generated')
        (outputs/'sentinel.js').write_text('unrelated')
        focused = FocusedGit(self.project, {'generated_outputs': ['web/dist/']},
                             {'artifacts': ['web/dist/known.js']})
        host = Path(__file__).with_name('cleanup_adapter_fixture.mjs')
        from coherence_workflow.engine import Engine
        from coherence_workflow.sessions import select_session
        from coherence_workflow.store import Authority
        executor = {'provider': 'openai', 'model': 'gpt-4.1', 'effort': 'off',
                    'reviewer': {'provider': 'openai', 'model': 'gpt-4.1', 'effort': 'off'}}
        task = {'id': 'tiny', 'description': 'zero-send SDK boundary', 'context_group': 'dummy'}
        (self.project/'.pi').mkdir()
        (self.project/'.pi/settings.json').write_text(json.dumps({'compaction': {'enabled': True}}))
        with Authority(self.project) as owner, patch('coherence_workflow.pi_adapter.host_path', return_value=host), patch.dict(
                'os.environ', {'PI_CODING_AGENT_DIR': str(self.root/'private-agent')}):
            owner.store.start('sdk-boundary', self.base)
            engine = Engine(owner, 'sdk-boundary', {'tasks': [task]}, executor)
            request, reuse_key = engine._session_request(task)
            worker = PiAdapter(self.project, executor)
            self.assertEqual(worker.prompt('dummy cleanup', cleanup=focused.cleanup_artifact, reuse_key=reuse_key), 'cleaned')
            # Feed real production SDK observations through the consumer that
            # previously rejected every production result as missing headroom.
            checkpoint = focused.checkpoint()
            engine._settle_session(task, worker, request, reuse_key, checkpoint)
            selected = select_session(request, engine.session_candidates)
            self.assertEqual(selected['session_id'], worker.saved_session['id'])
        self.assertFalse((outputs/'known.js').exists())
        self.assertEqual((outputs/'sentinel.js').read_text(), 'unrelated')
        self.assertIsInstance(worker.last_observation['after']['headroom'], dict)


    def test_reopen_retains_only_identity_and_fresh_observations(self):
        host = self.root / 'saved_host.py'
        host.write_text('''import json, sys
request = json.loads(input())
if request.get("savedSession"):
    assert request["savedSession"] == {"id":"session-1", "file":"/private/session-1.jsonl"}
    assert request["prompt"] == "second"
else:
    assert request["prompt"] == "first"
print(json.dumps({"type":"result", "text":"ok", "session":{"id":"session-1", "file":"/private/session-1.jsonl"}, "before":{"session_id":"session-1", "branch":"session-1", "epoch":"fresh", "entry":"before", "counters":{"input":1}}, "after":{"session_id":"session-1", "branch":"session-1", "epoch":"fresh", "entry":"after", "counters":{"input":2}}}), flush=True)
''')
        adapter = PiAdapter(self.project, {})
        with patch('coherence_workflow.pi_adapter.host_path', return_value=host), patch.dict(
                'os.environ', {'COHERENCE_NODE': sys.executable}):
            self.assertEqual(adapter.prompt('first'), 'ok')
            first = adapter.saved_session
            self.assertEqual(adapter.prompt('second', saved_session=first), 'ok')
        self.assertEqual(adapter.saved_session, first)
        self.assertEqual(adapter.last_observation['before']['entry'], 'before')
        self.assertEqual(adapter.last_observation['after']['entry'], 'after')

    def test_updated_adapter_opts_into_standalone_saved_session_observations(self):
        host = self.root / 'observing_host.py'
        host.write_text('''import json
request = json.loads(input())
assert request["sessionObservations"] is True
session = {"id":"session-1", "file":"/private/session-1.jsonl"}
print(json.dumps({"type":"session", "session":session, "before":{"entry":"opened"}}), flush=True)
print(json.dumps({"type":"result", "text":"ok", "session":session, "before":{"entry":"opened"}, "after":{"entry":"settled"}}), flush=True)
''')
        adapter = PiAdapter(self.project, {})
        with patch('coherence_workflow.pi_adapter.host_path', return_value=host), patch.dict(
                'os.environ', {'COHERENCE_NODE': sys.executable}):
            self.assertEqual(adapter.prompt('fixture'), 'ok')
        self.assertEqual(adapter.saved_session['id'], 'session-1')
        self.assertEqual(adapter.opened_session['id'], 'session-1')
        self.assertEqual(adapter.last_observation['after']['entry'], 'settled')

    def test_invalid_saved_identity_is_not_sent_to_the_host(self):
        with self.assertRaisesRegex(Exception, 'runner-provided'):
            PiAdapter(self.project, {}).prompt('fixture', saved_session='ambient-session')
