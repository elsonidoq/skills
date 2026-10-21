"""Line-framed transport to the installed Pi SDK, not an execution proof gateway."""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import uuid

from .metrics import interval_record
from .store import Blocked, canonical


def host_path():
    source = Path(__file__).resolve().parents[1] / 'pi-host/host.mjs'
    return source if source.exists() else Path(sys.prefix) / 'share/coherence-workflow/pi-host/host.mjs'


def parent_question(question, *, ready=False):
    """Use the existing parent socket for readiness or an owner question."""
    endpoint = os.environ.get('COHERENCE_PARENT_BRIDGE_SOCKET')
    token = os.environ.get('COHERENCE_PARENT_BRIDGE_TOKEN')
    session = os.environ.get('COHERENCE_PARENT_BRIDGE_SESSION')
    run = os.environ.get('COHERENCE_PARENT_BRIDGE_RUN')
    if not all((endpoint, token, session, run)):
        raise Blocked('parent owner bridge unavailable; launch through the parent-session bridge')
    request_id = uuid.uuid4().hex
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(endpoint)
            client.sendall((canonical({'type': 'ready' if ready else 'question', 'request_id': request_id, 'run_id': run,
                                      'session_id': session, 'token': token, 'question': question}) + '\n').encode())
            stream = client.makefile('r', encoding='utf-8')
            try:
                line = stream.readline()
            finally:
                stream.close()
    except OSError as exc:
        raise Blocked('parent owner bridge unavailable: ' + str(exc)) from None
    if not line:
        raise Blocked('parent owner bridge unavailable: connection closed before an owner reply')
    try:
        response = json.loads(line)
    except ValueError as exc:
        raise Blocked('parent owner bridge returned invalid response: ' + str(exc)) from None
    if not isinstance(response, dict) or response.get('request_id') != request_id:
        raise Blocked('parent owner bridge returned an uncorrelated response')
    if isinstance(response.get('error'), str):
        raise Blocked('parent owner bridge unavailable: ' + response['error'])
    if ready:
        if response.get('ready') is not True:
            raise Blocked('parent owner bridge not ready; start from a session with the reply tool enabled')
        return
    if not isinstance(response.get('answer'), str):
        raise Blocked('parent owner bridge returned an invalid answer')
    return response['answer']


class PiAdapter:
    def __init__(self, project, executor, *, question=None, observe=None, observe_question=None):
        self.project, self.executor = Path(project), executor
        self.lock_fd = None
        self.question = question or terminal_question
        self.observe = observe or (lambda value: print(canonical(value), file=sys.stderr, flush=True))
        self.observe_question = observe_question or (lambda state: None)
        self.saved_session = None
        self.last_observation = None
        self.last_interval = None

    def prompt(self, prompt, *, claim=None, command=None, read_only=False, saved_session=None, reuse_key=None):
        """Run one prompt, optionally reopening only a runner-provided private session."""
        self.last_interval = None
        self.last_observation = None
        request = {'project': str(self.project), 'executor': self.executor,
                   'prompt': prompt, 'readOnly': read_only,
                   # A standalone session record is a newer host extension.
                   # Explicit opt-in keeps an updated host compatible with
                   # controllers that predate this transport record.
                   'sessionObservations': True}
        if reuse_key is not None:
            if not isinstance(reuse_key, str):
                raise Blocked('saved session reuse key must be a stable runner string')
            request['reuseKey'] = reuse_key
        if saved_session is None:
            saved_session = self.saved_session
        if saved_session is not None:
            if not isinstance(saved_session, dict):
                raise Blocked('saved session identity must be runner-provided')
            request['savedSession'] = saved_session
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
                        def observe_question(state):
                            try:
                                self.observe_question(state)
                            except Exception:
                                pass  # Recording is never transport control flow.
                        observe_question('requested')
                        try:
                            answer = self.question(value['question'])
                        except BaseException:
                            observe_question('delivery_failed')
                            raise
                        observe_question('returned')
                        try:
                            send({'answer': answer})
                        except BaseException:
                            observe_question('delivery_failed')
                            raise
                        observe_question('sent')
                    elif kind == 'session':
                        session = value.get('session')
                        if not (isinstance(session, dict) and isinstance(session.get('id'), str)
                                and isinstance(session.get('file'), str)):
                            raise Blocked('SDK session record has an invalid saved session identity')
                        self.saved_session = session
                        self.last_observation = {'before': value.get('before'), 'after': None}
                    elif kind == 'result':
                        if not isinstance(value.get('text'), str):
                            raise Blocked('SDK result text must be a string')
                        session = value.get('session')
                        if session is not None:
                            if not (isinstance(session, dict) and isinstance(session.get('id'), str)
                                    and isinstance(session.get('file'), str)):
                                raise Blocked('SDK result has an invalid saved session identity')
                            self.saved_session = session
                        observations = {'before': value.get('before'), 'after': value.get('after')}
                        self.last_observation = observations if all(isinstance(item, dict) for item in observations.values()) else None
                        self.last_interval = (interval_record(**observations)
                                              if self.last_observation is not None else None)
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
                    # Only our Popen child. SIGTERM makes the host abort its active
                    # SDK tools; wait for that host to exit before releasing our
                    # inherited writer lock to a same-run continuation.
                    proc.terminate()
                    proc.wait()
                proc.stdout.close()


def terminal_question(question):
    if not sys.stdin.isatty():
        raise Blocked('owner input needed: ' + question + '; run interactively to answer; partial work retained')
    return input(question + '\n> ')
