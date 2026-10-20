"""Line-framed transport to the installed Pi SDK, not an execution proof gateway."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from .store import Blocked, canonical


def host_path():
    source = Path(__file__).resolve().parents[1] / 'pi-host/host.mjs'
    return source if source.exists() else Path(sys.prefix) / 'share/coherence-workflow/pi-host/host.mjs'


class PiAdapter:
    def __init__(self, project, executor, *, question=None, observe=None):
        self.project, self.executor = Path(project), executor
        self.lock_fd = None
        self.question = question or terminal_question
        self.observe = observe or (lambda value: print(canonical(value), file=sys.stderr, flush=True))

    def prompt(self, prompt, *, claim=None, command=None, read_only=False):
        request = {'project': str(self.project), 'executor': self.executor,
                   'prompt': prompt, 'readOnly': read_only}
        with tempfile.TemporaryFile(mode='w+t') as errors:
            proc = subprocess.Popen([os.environ.get('COHERENCE_NODE', 'node'), str(host_path())],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors,
                                    text=True, encoding='utf-8', cwd=self.project,
                                    pass_fds=() if self.lock_fd is None else (self.lock_fd,))
            try:
                def send(value):
                    proc.stdin.write(canonical(value) + '\n')
                    proc.stdin.flush()
                send(request)
                result = None
                for line in proc.stdout:
                    try:
                        value = json.loads(line)
                    except ValueError as exc:
                        raise Blocked('invalid SDK transport JSON: ' + str(exc)) from None
                    kind = value.get('type') if isinstance(value, dict) else None
                    if kind == 'event':
                        try:
                            self.observe(value)
                        except Exception:
                            pass  # Optional display must not interrupt coding or SDK compaction.
                    elif kind == 'claim':
                        try:
                            if claim is None or read_only:
                                raise Blocked('this session cannot edit files')
                            claim(value['path'])
                            send({'ok': True})
                        except (Blocked, ValueError, KeyError) as exc:
                            send({'error': str(exc)})
                    elif kind == 'command':
                        try:
                            if command is None or read_only:
                                raise Blocked('this session cannot run commands')
                            command(value['phase'], value['call'])
                            send({'ok': True})
                        except (Blocked, ValueError, KeyError) as exc:
                            send({'error': str(exc)})
                    elif kind == 'question':
                        send({'answer': self.question(value['question'])})
                    elif kind == 'result':
                        if not isinstance(value.get('text'), str):
                            raise Blocked('SDK result text must be a string')
                        result = value['text']
                    elif kind == 'error':
                        raise Blocked('SDK operation failed: ' + str(value.get('message')))
                    else:
                        raise Blocked('unknown SDK transport record: ' + str(kind))
                code = proc.wait()
                if code or result is None:
                    errors.seek(0)
                    raise Blocked('SDK host exited without a result (exit ' + str(code) + '): ' + errors.read())
                return result
            finally:
                # Release an unanswered UI/tool request before awaiting SDK abort.
                # Otherwise an ask_owner waiting on stdin could keep the host alive.
                try:
                    proc.stdin.close()
                except BrokenPipeError:
                    pass
                if proc.poll() is None:
                    # Only our Popen child; SDK abort handles its active tools.
                    proc.terminate()
                    proc.wait()
                proc.stdout.close()


def terminal_question(question):
    if not sys.stdin.isatty():
        raise Blocked('owner input needed: ' + question + '; run interactively to answer; partial work retained')
    return input(question + '\n> ')
