"""Actual project command behavior, not universal evidence formatting."""
from coherence_workflow.verification import run_checks
from coherence_workflow.store import Blocked
from fixtures.support import ProjectTest


class ProjectCheckTests(ProjectTest):
    def test_checks_optional_and_zero_collection_output_not_required(self):
        self.assertEqual(run_checks(self.project, {'id': 'fix'}), [])
        self.assertEqual(run_checks(self.project, {'id': 'fix', 'checks': ['true']})[0]['exit_code'], 0)

    def test_actual_argv_and_required_command_mapping(self):
        results = run_checks(self.project, {'id': 'fix', 'required': [
            {'id': 'project-check', 'check': {'argv': ['python3', '-B', '-c', 'assert 2+2 == 4']}}]})
        self.assertEqual(results[0]['exit_code'], 0)

    def test_failed_command_is_not_success(self):
        events = []
        with self.assertRaisesRegex(Blocked, 'exit 19'):
            run_checks(self.project, {'id': 'fix', 'checks': ['exit 19']}, observe=lambda *event: events.append(event))
        self.assertEqual(events, [('started', 1, None), ('failed', 1, 19)])

    def test_signalled_command_preserves_actual_exit_status(self):
        import sys
        with self.assertRaisesRegex(Blocked, 'exit -15'):
            run_checks(self.project, {'id': 'fix', 'checks': [[sys.executable, '-B', '-c',
                'import os, signal; os.kill(os.getpid(), signal.SIGTERM)']]})

    def test_outcomes_are_retained_before_later_failure_and_capture_both_streams(self):
        from coherence_workflow.verification import CheckFailure
        outcomes = []
        with self.assertRaises(CheckFailure):
            run_checks(self.project, {'id': 'tiny', 'checks': [
                "printf stdout; printf stderr >&2", "printf failed; exit 7"]},
                completed=lambda state, attempt: outcomes.append((state, attempt)))
        self.assertEqual([state for state, _ in outcomes], ['passed', 'failed'])
        self.assertEqual(outcomes[0][1]['output'], 'stdoutstderr')
        self.assertEqual(outcomes[1][1]['output'], 'failed')

    def test_bad_command_reports_actual_operation(self):
        with self.assertRaises(FileNotFoundError):
            run_checks(self.project, {'id': 'fix', 'checks': [['/nonexistent/coherence-test']]})
        with self.assertRaisesRegex(Blocked, 'command string or argv'):
            run_checks(self.project, {'id': 'fix', 'checks': [{'id': 'removed.catalogue'}]})


class CheckOwnershipTests(ProjectTest):
    """Real disposable check processes; synchronization, not delayed-write sleeps."""

    def start_check(self, *, shell=False, background=False, exit_code=0):
        import os
        import shlex
        import subprocess
        import sys
        import json
        from pathlib import Path
        release = self.project/'release'
        os.mkfifo(release)
        fd = os.open(release, os.O_RDWR)
        self.addCleanup(os.close, fd)
        child = self.project/'check.py'
        child.write_text("""import os, signal, sys
from pathlib import Path
pid = os.fork()
if pid:
    os.waitpid(pid, 0)
    sys.exit(0)
signal.signal(signal.SIGTERM, signal.SIG_IGN)
Path('child-ready').touch()
with open('release') as release:
    release.readline()
Path('late.txt').write_text('old check wrote')
""")
        argv = [sys.executable, '-B', str(child)]
        command = shlex.join(argv) if shell else argv
        if background:
            command += ' & exit ' + str(exit_code)
        # Observe the real waitid, without replacing process/kill behavior. This
        # lets the test cancel *after* the shell leader has actually exited.
        script = """
import json, os, signal, sys
from coherence_workflow.store import Authority, Blocked
from coherence_workflow.verification import run_checks
waitid = os.waitid
def observed_wait(*args):
    result = waitid(*args)
    print('leader-exited', flush=True)
    return result
os.waitid = observed_wait
def cancel(*args): raise KeyboardInterrupt()
signal.signal(signal.SIGTERM, cancel)
try:
    with Authority(sys.argv[1]) as owner:
        result = run_checks(owner.project, {'id':'check', 'checks':[json.loads(sys.argv[2])]},
                            lock_fd=owner.lock.fileno(),
                            completed=lambda state, attempt: print(json.dumps({'state': state, **attempt}), flush=True))
        print(json.dumps(result), flush=True)
except KeyboardInterrupt:
    print('cancelled', flush=True)
    sys.exit(130)
except Blocked as exc:
    print(str(exc), flush=True)
    sys.exit(1)
"""
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]))
        proc = subprocess.Popen([sys.executable, '-B', '-c', script, str(self.project), json.dumps(command)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, env=env)
        def cleanup():
            os.write(fd, b'release\n')
            if proc.poll() is None:
                proc.terminate()
            proc.communicate(timeout=10)
        self.addCleanup(cleanup)
        import time
        deadline = time.monotonic() + 10
        while not (self.project/'child-ready').exists():
            if time.monotonic() > deadline: self.fail('child did not start')
            time.sleep(0.01)
        (self.project/'child-ready').unlink()
        return proc, fd

    def line(self, proc):
        import select
        self.assertTrue(select.select([proc.stdout], [], [], 10)[0], 'owned check did not synchronize')
        return proc.stdout.readline().decode().strip()

    def test_cancellation_stops_shell_and_argv_descendants_before_replacement(self):
        import os
        import signal
        from coherence_workflow.store import Authority
        for shell in (False, True):
            for sig in (signal.SIGINT, signal.SIGTERM):
                with self.subTest(shell=shell, signal=sig):
                    proc, release = self.start_check(shell=shell)
                    proc.send_signal(sig)
                    output, errors = proc.communicate(timeout=10)
                    self.assertEqual(proc.returncode, 130, errors.decode())
                    self.assertIn(b'cancelled', output)
                    self.assertIn(b'"state": "interrupted"', output)
                    self.assertIn(b'"exit_code": -9', output)
                    with Authority(self.project):
                        os.write(release, b'write-now\n')
                        self.assertFalse((self.project/'late.txt').exists())
                    (self.project/'release').unlink()

    def test_exited_shell_descendant_keeps_check_and_ownership_active(self):
        import os
        from coherence_workflow.store import Authority
        for code in (0, 19):
            with self.subTest(exit_code=code):
                proc, release = self.start_check(shell=True, background=True, exit_code=code)
                self.assertEqual(self.line(proc), 'leader-exited')
                self.assertIsNone(proc.poll())
                with self.assertRaisesRegex(Blocked, 'writer lock already held'):
                    Authority(self.project)
                os.write(release, b'write-now\n')
                output, errors = proc.communicate(timeout=10)
                self.assertEqual(proc.returncode, 0 if code == 0 else 1, errors.decode())
                self.assertIn(b'"exit_code": 0' if code == 0 else b'exit 19', output)
                with Authority(self.project):
                    self.assertEqual((self.project/'late.txt').read_text(), 'old check wrote')
                (self.project/'late.txt').unlink()
                (self.project/'release').unlink()

    def test_cancel_after_shell_exit_stops_remaining_descendant(self):
        import os
        from coherence_workflow.store import Authority
        proc, release = self.start_check(shell=True, background=True)
        self.assertEqual(self.line(proc), 'leader-exited')
        proc.terminate()
        _, errors = proc.communicate(timeout=10)
        self.assertEqual(proc.returncode, 130, errors.decode())
        with Authority(self.project):
            os.write(release, b'write-now\n')
            self.assertFalse((self.project/'late.txt').exists())

    def test_unexpected_runner_death_leaves_inherited_lock_until_check_exits(self):
        import os
        from coherence_workflow.store import Authority
        proc, release = self.start_check(shell=True, background=True)
        self.assertEqual(self.line(proc), 'leader-exited')
        proc.kill()  # This fixture runner only, never an application/service.
        proc.wait(timeout=10)
        with self.assertRaisesRegex(Blocked, 'writer lock already held'):
            Authority(self.project)
        os.write(release, b'write-now\n')
        proc.communicate(timeout=10)
        # Captured check output no longer inherits the runner's stdout pipe.
        import time
        deadline = time.monotonic() + 10
        while True:
            try:
                owner = Authority(self.project)
                break
            except Blocked:
                if time.monotonic() > deadline: raise
                time.sleep(0.01)
        with owner:
            self.assertEqual((self.project/'late.txt').read_text(), 'old check wrote')
