"""Real existing entry: minimal intake/start, empty no-op and passive status."""
import contextlib
import io
import json
import os
import subprocess
import sys
from unittest.mock import patch

from coherence_workflow.cli import main, ROOT, status
from coherence_workflow.store import Authority
from fixtures.support import ProjectTest


class CliTests(ProjectTest):
    def test_minimal_start_uses_selected_executor_no_manifest_or_cgroup(self):
        tasks = self.root/'tasks.json'
        tasks.write_text('[{"id":"fix","description":"Fix"}]')
        executor = self.root/'executor.json'
        executor.write_text('{"provider":"fixture","model":"offline-no-provider-call","effort":"medium"}')
        seen = []
        class Boundary:
            def __init__(self, project, executor, **kwargs): seen.append(executor)
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'): return '{"approved":true,"findings":[]}'
                return 'read only offline fixture'
        with patch('coherence_workflow.cli.PiAdapter', Boundary), contextlib.redirect_stdout(io.StringIO()) as out:
            code = main(['start', '--project', str(self.project), '--tasks', str(tasks), '--executor', str(executor), '--run', 'minimal'])
        self.assertEqual(code, 0, out.getvalue())
        self.assertEqual(seen[0], json.loads(executor.read_text()))
        self.assertEqual(json.loads(out.getvalue())['checkpoints'][0]['no_change'], True)
        observed = status(self.project, 'minimal')
        self.assertEqual(observed['run']['state'], 'complete')
        self.assertEqual(observed['monitoring']['recording_version'], 1)
        self.assertTrue(any(row['phase'] == 'review' for row in observed['monitoring']['observations']))

    def test_selected_reviewer_profile_reaches_only_fresh_read_only_session(self):
        tasks, executor = self.root/'tasks.json', self.root/'executor.json'
        tasks.write_text('[{"id":"dummy","description":"Synthetic no-change fixture"}]')
        worker = {'provider': 'fixture', 'model': 'offline-worker', 'effort': 'medium'}
        reviewer = {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}
        executor.write_text(json.dumps(dict(worker, reviewer=reviewer)))
        sessions, calls = [], []
        class Boundary:
            def __init__(self, project, profile, **kwargs):
                self.profile = profile
                sessions.append(self)
            def prompt(self, prompt, **kwargs):
                calls.append((self.profile, kwargs.get('read_only', False)))
                return '{"approved":true,"findings":[]}' if kwargs.get('read_only') else 'synthetic no-change fixture'
        with patch('coherence_workflow.cli.PiAdapter', Boundary), contextlib.redirect_stdout(io.StringIO()) as out:
            code = main(['start', '--project', str(self.project), '--tasks', str(tasks),
                         '--executor', str(executor), '--run', 'separate-reviewer'])
        self.assertEqual(code, 0, out.getvalue())
        self.assertEqual(calls, [(worker, False), (reviewer, True)])
        self.assertIsNot(sessions[0], sessions[1])
        self.assertTrue(json.loads(out.getvalue())['checkpoints'][0]['no_change'])

    def test_invalid_explicit_reviewer_does_not_fall_back_or_launch(self):
        tasks, executor = self.root/'tasks.json', self.root/'executor.json'
        tasks.write_text('[{"id":"dummy","description":"Synthetic no-change fixture"}]')
        for reviewer in (None, {}, {'provider': 'fixture', 'model': 'offline', 'effort': ''}):
            with self.subTest(reviewer=reviewer):
                executor.write_text(json.dumps({'provider': 'fixture', 'model': 'offline-worker',
                                                'effort': 'medium', 'reviewer': reviewer}))
                with patch('coherence_workflow.cli.PiAdapter') as adapter, contextlib.redirect_stdout(io.StringIO()) as out:
                    code = main(['start', '--project', str(self.project), '--tasks', str(tasks),
                                 '--executor', str(executor), '--run', 'invalid-reviewer'])
                self.assertEqual(code, 2)
                self.assertIn('correct the reviewer profile', json.loads(out.getvalue())['reason'])
                adapter.assert_not_called()

    def test_bad_attached_configuration_stops_before_storage_or_sdk(self):
        tasks, executor = self.root/'tasks.json', self.root/'executor.json'
        tasks.write_text('[{"id":"smoke","description":"No changes"}]')
        executor.write_text('{"provider":"fixture","model":"offline","effort":"medium"}')
        prefix = 'COHERENCE_PARENT_BRIDGE_'
        base_env = {k: v for k, v in os.environ.items() if not k.startswith(prefix)}
        cases = [({'TOKEN': 'partial'}, 'run mismatch'),
                 ({'RUN': 'attached'}, 'bridge unavailable'),
                 ({'RUN': 'attached', 'SOCKET': str(self.root/'absent.sock'),
                   'SESSION': 'parent', 'TOKEN': 'token'}, 'bridge unavailable')]
        for values, error in cases:
            with self.subTest(values=values):
                env = base_env | {prefix+k: v for k, v in values.items()}
                result = subprocess.run([str(ROOT/'scripts/coordinate-implementation'), 'start',
                    '--project', str(self.project), '--tasks', str(tasks), '--executor', str(executor),
                    '--run', 'attached'], env=env | {'COHERENCE_PYTHON': sys.executable}, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(error, json.loads(result.stdout)['reason'])
                self.assertFalse((self.project/'.coherence').exists())

    def test_actual_script_empty_task_does_not_create_storage(self):
        tasks = self.root/'empty.yaml'
        tasks.write_text('[]')
        result = subprocess.run([str(ROOT/'scripts/coordinate-implementation'), 'start', '--project', str(self.project),
                                 '--tasks', str(tasks)], env=dict(os.environ, COHERENCE_PYTHON=sys.executable),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'status': 'no tasks'})
        self.assertFalse((self.project/'.coherence').exists())

    def test_abandon_appends_monitoring_without_erasing_failure(self):
        from coherence_workflow.monitoring import Recorder, descriptor
        with Authority(self.project) as owner:
            owner.store.start('recorded', self.base)
            recorder = Recorder(owner.store, 'recorded')
            recorder.register(descriptor({'tasks': []}, {}))
            recorder.emit('review-id', 'review', 'failed', facts={'role': 'reviewer', 'review_base': self.base, 'review_head': self.base})
            owner.store.finish('recorded', 'failed', self.base, 'ordinary failure')
            owner.store.abandon('recorded')
        observed = status(self.project, 'recorded')
        self.assertEqual(observed['run']['error'], 'ordinary failure')
        self.assertIn('review-id', [row['occurrence_id'] for row in observed['monitoring']['observations']])
        self.assertEqual(observed['monitoring']['observations'][-1]['kind'], 'abandoned')

    def test_status_read_only_db_bytes_unchanged(self):
        with Authority(self.project) as owner:
            owner.store.start('test', self.base)
            owner.store.finish('test', 'failed', self.base, 'actual API error')
            database = owner.database
        before = database.read_bytes()
        self.assertEqual(status(self.project, 'test')['run']['error'], 'actual API error')
        self.assertEqual(database.read_bytes(), before)

    def test_actual_cli_sigterm_cancels_owned_host_and_records_interruption(self):
        import time
        host = self.root/'waiting_host.py'
        ready = self.root/'ready'
        host.write_text("import json,signal,sys\nfrom pathlib import Path\njson.loads(input())\nsignal.signal(signal.SIGTERM,lambda *args: None)\nPath(" + repr(str(ready)) + ").write_text('ready')\nsys.stdin.read()\n")
        tasks = self.root/'tasks.json'
        tasks.write_text('[{"id":"fix","description":"Fix"}]')
        executor = self.root/'executor.json'
        executor.write_text('{"provider":"fixture","model":"offline-no-provider-call","effort":"medium"}')
        code = "from pathlib import Path; import coherence_workflow.pi_adapter as a; a.host_path=lambda:Path(" + repr(str(host)) + "); from coherence_workflow.cli import main; raise SystemExit(main())"
        process = subprocess.Popen([sys.executable, '-B', '-c', code, 'start', '--project', str(self.project),
                                    '--tasks', str(tasks), '--executor', str(executor), '--run', 'cancelled'],
                                   env=dict(os.environ, COHERENCE_NODE=sys.executable), stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 10  # Test harness only, not a workflow deadline.
            while not ready.exists():
                if process.poll() is not None or time.monotonic() > deadline:
                    self.fail('offline host did not reach the owned cancellation fixture')
                time.sleep(.01)
            process.terminate()  # This test-owned Popen only.
            out, err = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 130, out+err)
            self.assertEqual(json.loads(out)['status'], 'interrupted')
            self.assertEqual(status(self.project, 'cancelled')['run']['state'], 'interrupted')
            self.assertEqual(status(self.project, 'cancelled')['tasks'][0]['state'], 'interrupted')
            with Authority(self.project): pass
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate(timeout=10)
