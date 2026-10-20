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
