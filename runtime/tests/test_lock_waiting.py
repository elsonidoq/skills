"""Synthetic production-CLI coverage for the inherited implementation lock."""
import json
import os
import sqlite3
import subprocess
import sys
import time

from fixtures.support import ProjectTest


class LockBusyTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.tasks = self.root / 'tasks.json'
        self.executor = self.root / 'executor.json'
        self.tasks.write_text(json.dumps({
            'paid_scope': {'approved': True, 'agent_providers': ['fixture'], 'apis': []},
            'tasks': [{'id': 'synthetic', 'description': 'Synthetic disposable lock fixture'}],
        }))
        self.executor.write_text(json.dumps({'provider': 'fixture', 'model': 'offline', 'effort': 'medium'}))

    def hold_lock(self):
        code = """\
import sys
from coherence_workflow.store import Authority
with Authority(sys.argv[1]):
    print('locked', flush=True)
    sys.stdin.read()
"""
        process = subprocess.Popen([sys.executable, '-B', '-c', code, str(self.project)],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, env=os.environ.copy())
        self.assertEqual(process.stdout.readline().strip(), 'locked')
        self.addCleanup(self.stop, process)
        return process

    @staticmethod
    def stop(process):
        if process.poll() is None:
            process.stdin.close()
            process.wait(timeout=10)
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream and not stream.closed:
                stream.close()

    @staticmethod
    def cli_environment():
        env = os.environ.copy()
        env.update({key: '' for key in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                                        'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')})
        return env

    def cli(self, run):
        code = """\
import coherence_workflow.cli as cli
class Offline:
    def __init__(self, project, profile, **kwargs): pass
    def prompt(self, prompt, **kwargs):
        return '{"approved":true,"findings":[]}' if kwargs.get('read_only') else 'synthetic no-change fixture'
cli.PiAdapter = Offline
raise SystemExit(cli.main())
"""
        return subprocess.Popen([sys.executable, '-B', '-c', code, 'start', '--project', str(self.project),
                                 '--tasks', str(self.tasks), '--executor', str(self.executor), '--run', run],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=self.cli_environment())

    def test_waiting_cli_cancellation_does_not_create_failed_run(self):
        holder = self.hold_lock()
        waiting = self.cli('waiting-cancelled')
        try:
            time.sleep(.1)  # Fixture observation only: the CLI must still be in kernel lock wait.
            self.assertIsNone(waiting.poll())
            waiting.terminate()
            output, errors = waiting.communicate(timeout=10)
            self.assertEqual(waiting.returncode, 130, errors)
            result = json.loads(output)
            self.assertEqual(result['status'], 'interrupted')
            self.assertIn('waiting for implementation writer', result['reason'])
            with sqlite3.connect(self.project / '.coherence/workflow/workflow.sqlite') as db:
                self.assertIsNone(db.execute('SELECT 1 FROM execution_runs WHERE run_id=?', ('waiting-cancelled',)).fetchone())
        finally:
            self.stop(holder)

    def test_waiting_cli_enters_after_holder_releases(self):
        holder = self.hold_lock()
        waiting = self.cli('waiting-release')
        try:
            time.sleep(.1)  # Fixture observation only, never a workflow timeout.
            self.assertIsNone(waiting.poll())
            self.stop(holder)
            output, errors = waiting.communicate(timeout=10)
            self.assertEqual(waiting.returncode, 0, output + errors)
            self.assertEqual(json.loads(output)['status'], 'complete')
        finally:
            self.stop(holder)
