"""Run actual optional project commands; no registered check/evidence catalogue."""
import os
import signal
import subprocess

from .store import Blocked


def commands(task):
    values = list(task.get('checks', []))
    for item in task.get('required', []):
        if 'check' in item:
            values.append(item['check'])
    if 'check' in task:
        values.append(task['check'])
    return values


def _run_check(project, command, lock_fd):
    # A private session makes cancellation specific to this check, not the runner
    # or its siblings. Keep its leader unreaped until cleanup so its PGID cannot
    # be reused. The inherited pipe also waits for ordinary shell descendants
    # after the shell exits; EOF is lifetime observation, not a check result.
    reader, writer = os.pipe()
    proc = None
    cancellation = {signal.SIGINT, signal.SIGTERM}
    try:
        try:
            proc = subprocess.Popen(command, cwd=project, shell=isinstance(command, str),
                                    start_new_session=True,
                                    pass_fds=(writer,) if lock_fd is None else (writer, lock_fd))
        finally:
            os.close(writer)
        os.waitid(os.P_PID, proc.pid, os.WEXITED | os.WNOWAIT)
        while os.read(reader, 4096):
            pass
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
            signal.pthread_sigmask(signal.SIG_SETMASK, previous)
    return proc.returncode


def run_checks(project, task, *, lock_fd=None, observe=None):
    results = []
    for ordinal, value in enumerate(commands(task), 1):
        command = value.get('command', value.get('argv')) if isinstance(value, dict) else value
        if not isinstance(command, (str, list)) or not command or (isinstance(command, list) and
                any(not isinstance(arg, str) for arg in command)):
            raise Blocked('task ' + task['id'] + ' check needs a command string or argv list; registered check IDs are no longer executable')
        # No workflow deadline or output cap. Preserve normal shell/project behavior.
        if observe: observe('started', ordinal, None)
        try:
            code = _run_check(project, command, lock_fd)
        except BaseException:
            if observe: observe('interrupted', ordinal, None)
            raise
        results.append({'command': command, 'exit_code': code})
        if observe: observe('passed' if code == 0 else 'failed', ordinal, code)
        if code:
            raise Blocked('task ' + task['id'] + ' check failed (exit ' + str(code) + '): ' + str(command))
    return results


def manual_gates(task, question):
    for gate in task.get('gates', []):
        text = gate if isinstance(gate, str) else gate.get('question', gate.get('description'))
        if not isinstance(text, str):
            raise Blocked('manual gate needs a question or description for task ' + task['id'])
        answer = question(text + '\nApprove this gate? [yes/no]')
        if answer.strip().lower() not in ('yes', 'y'):
            raise Blocked('manual gate not approved for task ' + task['id'])
