"""Run actual optional project commands; no registered check/evidence catalogue."""
import os
import signal
import subprocess
import tempfile

from .store import Blocked


class CheckFailure(Blocked):
    """A real failed command returned to the task worker for scoped correction."""
    def __init__(self, task_id, attempt):
        self.task_id, self.attempt = task_id, attempt
        super().__init__('task ' + task_id + ' check failed (exit ' + str(attempt['exit_code']) + '): ' + str(attempt['command']))


def commands(task):
    values = list(task.get('checks', []))
    for item in task.get('required', []):
        if 'check' in item:
            values.append(item['check'])
    if 'check' in task:
        values.append(task['check'])
    return values


def _run_check(project, command, lock_fd, completed):
    # A private session makes cancellation specific to this check, not the runner
    # or its siblings. Keep its leader unreaped until cleanup so its PGID cannot
    # be reused. The inherited pipe also waits for ordinary shell descendants
    # after the shell exits; EOF is lifetime observation, not a check result.
    reader, writer = os.pipe()
    proc = None
    error = None
    cancellation = {signal.SIGINT, signal.SIGTERM}
    with tempfile.TemporaryFile() as output:
        try:
            try:
                proc = subprocess.Popen(command, cwd=project, shell=isinstance(command, str),
                                        start_new_session=True, stdout=output, stderr=output,
                                        pass_fds=(writer,) if lock_fd is None else (writer, lock_fd))
            finally:
                os.close(writer)
            os.waitid(os.P_PID, proc.pid, os.WEXITED | os.WNOWAIT)
            while os.read(reader, 4096):
                pass
        except BaseException as exc:
            error = exc
            raise
        finally:
            # No grace deadline/watchdog: stop only our group, even on normal exit
            # (a background descendant may have closed its inherited descriptors).
            # Keep the leader unreaped until signalling; block repeated cancellation
            # during cleanup. Inherited lock holders also exclude replacement if the
            # runner dies. Deliberate session escapes/closing the lock are not fenced.
            previous = signal.pthread_sigmask(signal.SIG_BLOCK, cancellation)
            try:
                if proc is not None:
                    os.killpg(proc.pid, signal.SIGKILL)
                    while os.read(reader, 4096):
                        pass
                    proc.wait()
            finally:
                os.close(reader)
                try:
                    output.seek(0)
                    attempt = {'command': command, 'exit_code': proc.returncode if proc else None,
                               'output': output.read().decode(errors='replace')}
                    if error is not None:
                        attempt['error'] = str(error) or type(error).__name__
                    completed('interrupted' if error is not None else
                              ('passed' if proc.returncode == 0 else 'failed'), attempt)
                finally:
                    signal.pthread_sigmask(signal.SIG_SETMASK, previous)
        output.seek(0)
        return proc.returncode, output.read().decode(errors='replace')


def run_checks(project, task, *, lock_fd=None, observe=None, completed=None):
    results = []
    for ordinal, value in enumerate(commands(task), 1):
        command = value.get('command', value.get('argv', value.get('check'))) if isinstance(value, dict) else value
        if not isinstance(command, (str, list)) or not command or (isinstance(command, list) and
                any(not isinstance(arg, str) for arg in command)):
            raise Blocked('task ' + task['id'] + ' check needs a command string or argv list; registered check IDs are no longer executable')
        # No workflow deadline or output cap. Preserve normal shell/project behavior.
        if observe: observe('started', ordinal, None)
        try:
            code, output = _run_check(project, command, lock_fd, completed or (lambda state, attempt: None))
        except BaseException:
            if observe: observe('interrupted', ordinal, None)
            raise
        results.append({'command': command, 'exit_code': code, 'output': output})
        if observe: observe('passed' if code == 0 else 'failed', ordinal, code)
        if code:
            # The failed attempt is data for the engine's same-task corrective
            # continuation, not a terminal verdict or a suggestion-only prompt.
            raise CheckFailure(task['id'], results[-1])
    return results


def manual_gates(task, question):
    for gate in task.get('gates', []):
        text = gate if isinstance(gate, str) else gate.get('question', gate.get('description'))
        if not isinstance(text, str):
            raise Blocked('manual gate needs a question or description for task ' + task['id'])
        answer = question(text + '\nApprove this gate? [yes/no]')
        if answer.strip().lower() not in ('yes', 'y'):
            raise Blocked('manual gate not approved for task ' + task['id'])
