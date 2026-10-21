"""Line-framed transport to the installed Pi SDK, not an execution proof gateway."""
import json
import os
import queue
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
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


class _ParentSteering:
    """Private, invocation-local bridge control; never persists direction text."""
    def __init__(self, adapter, expected):
        self.adapter, self.expected = adapter, expected
        self.socket = None
        self.target = None
        self.lock = threading.Lock()
        self.closed = False

    def _send(self, value):
        with self.lock:
            if self.closed or self.socket is None:
                return False
            try:
                self.socket.sendall((canonical(value) + '\n').encode())
                return True
            except OSError:
                self.closed = True
                return False

    def activate(self, target):
        if any(target.get(key) != self.expected.get(key) for key in self.expected) or not isinstance(target.get('session_id'), str):
            raise Blocked('SDK host advertised a different steering target')
        self.target = target
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(os.environ['COHERENCE_PARENT_BRIDGE_SOCKET'])
            self.socket = client
            request = {'type': 'steering_target', 'request_id': uuid.uuid4().hex,
                       'run_id': os.environ['COHERENCE_PARENT_BRIDGE_RUN'],
                       'session_id': os.environ['COHERENCE_PARENT_BRIDGE_SESSION'],
                       'token': os.environ['COHERENCE_PARENT_BRIDGE_TOKEN'], 'target': target}
            if not self._send(request):
                raise OSError('bridge connection closed')
        except OSError as exc:
            client.close()
            self.closed = True
            raise Blocked('parent steering bridge unavailable: ' + str(exc)) from None

        def controls():
            try:
                stream = client.makefile('r', encoding='utf-8')
                for line in stream:
                    value = json.loads(line)
                    if value.get('type') != 'steer' or not isinstance(value.get('request_id'), str):
                        continue
                    try:
                        self.adapter.steer(value['request_id'], value.get('instruction'), target=value.get('target'))
                    except Blocked:
                        # steer() reports unknown for write loss; a rejected target
                        # has no host status, so report its known unavailability.
                        self.status({'request_id': value['request_id'], 'status': 'failed-unavailable'})
            except (OSError, ValueError):
                pass
            finally:
                self.closed = True
        threading.Thread(target=controls, daemon=True).start()

    def status(self, update):
        self._send({'type': 'steering_status', 'run_id': os.environ.get('COHERENCE_PARENT_BRIDGE_RUN'),
                    'session_id': os.environ.get('COHERENCE_PARENT_BRIDGE_SESSION'),
                    'token': os.environ.get('COHERENCE_PARENT_BRIDGE_TOKEN'), 'target': self.target, **update})

    def close(self):
        self._send({'type': 'steering_closed', 'run_id': os.environ.get('COHERENCE_PARENT_BRIDGE_RUN'),
                    'session_id': os.environ.get('COHERENCE_PARENT_BRIDGE_SESSION'),
                    'token': os.environ.get('COHERENCE_PARENT_BRIDGE_TOKEN'), 'target': self.target})
        with self.lock:
            self.closed = True
            if self.socket is not None:
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                self.socket.close()


class PiAdapter:
    def __init__(self, project, executor, *, question=None, observe=None, observe_question=None,
                 steering_status=None):
        self.project, self.executor = Path(project), executor
        self.lock_fd = None
        self.question = question or terminal_question
        self.observe = observe or (lambda value: print(canonical(value), file=sys.stderr, flush=True))
        self.observe_question = observe_question or (lambda state: None)
        self.steering_status = steering_status or (lambda value: None)
        self.saved_session = None
        self.last_observation = None
        self.last_interval = None
        # Only the current host's explicit opened-session record confirms opening.
        self.opened_session = None
        # These are invocation-local and intentionally never persist a session
        # identity, direction text, or a target for a later prompt.
        self.active_target = None
        self.steering_states = {}
        self._send_control = None
        self._control_lock = threading.Lock()
        self._parent_steering = None

    def parent_steering_available(self):
        """Whether this attached parent can receive active-target updates."""
        return all(os.environ.get(name) for name in (
            'COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
            'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN'))

    def enable_parent_steering(self, target):
        """Limit bridge control to this one runner-created invocation target."""
        if not self.parent_steering_available():
            return False
        if not isinstance(target, dict) or any(not isinstance(target.get(key), str) or not target[key]
                                               for key in ('run_id', 'task_id', 'invocation_id', 'role')):
            raise Blocked('parent steering needs an exact runner-created target')
        self._parent_steering = _ParentSteering(self, target)
        return True

    def steer(self, request_id, instruction, *, target=None):
        """Send one exact-target direction to the currently active host only."""
        with self._control_lock:
            active, send = self.active_target, self._send_control
        if not isinstance(request_id, str) or not request_id:
            raise Blocked('steering request ID must be a nonempty string')
        if not isinstance(instruction, str):
            raise Blocked('steering instruction must be text')
        if target is None:
            target = active
        if not isinstance(target, dict) or target != active or send is None:
            raise Blocked('steering target is unavailable')
        try:
            send({'type': 'steer', 'request_id': request_id, 'target': target, 'instruction': instruction})
        except (BrokenPipeError, OSError, ValueError) as exc:
            # Input loss cannot prove that the host did not receive the control.
            self.steering_states[request_id] = 'unknown'
            try:
                self.steering_status({'request_id': request_id, 'status': 'unknown'})
            except Exception:
                pass
            raise Blocked('steering target is unavailable: ' + str(exc)) from None

    def prompt(self, prompt, *, claim=None, command=None, cleanup=None, read_only=False, saved_session=None,
               reuse_key=None, steering=None):
        """Run one prompt, optionally reopening only a runner-provided private session."""
        self.last_interval = None
        self.last_observation = None
        self.opened_session = None
        if steering is not None and not isinstance(steering, dict):
            raise Blocked('steering target must be runner-provided')
        request = {'project': str(self.project), 'executor': self.executor,
                   'prompt': prompt, 'readOnly': read_only,
                   # A standalone session record is a newer host extension.
                   # Explicit opt-in keeps an updated host compatible with
                   # controllers that predate this transport record.
                   'sessionObservations': True}
        if steering is not None:
            # This is deliberately independent from sessionObservations: only
            # this adapter opts into the multiplexed callback/control protocol.
            request['steering'] = steering
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
            write_lock = threading.Lock()
            callbacks = queue.Queue()
            worker_error = []
            worker_error_lock = threading.Lock()
            result = []

            def send(value):
                with write_lock:
                    proc.stdin.write(canonical(value) + '\n')
                    proc.stdin.flush()

            def close_input():
                with write_lock:
                    try:
                        proc.stdin.close()
                    except (BrokenPipeError, OSError):
                        pass

            def response(record, value):
                if steering is not None:
                    request_id = record.get('request_id')
                    if not isinstance(request_id, str):
                        raise Blocked('SDK callback lacks a correlation ID')
                    send({'type': 'reply', 'request_id': request_id, 'reply': value})
                else:
                    send(value)

            def callback(record):
                try:
                    kind = record['type']
                    if kind == 'claim':
                        if claim is None or read_only:
                            raise Blocked('this session cannot edit files')
                        claim(record['path'])
                        response(record, {'ok': True})
                    elif kind == 'command':
                        if command is None or read_only:
                            raise Blocked('this session cannot run commands')
                        command(record['phase'], record['call'])
                        response(record, {'ok': True})
                    elif kind == 'cleanup':
                        if cleanup is None or read_only:
                            raise Blocked('this session cannot clean generated artifacts')
                        cleanup(record['path'])
                        response(record, {'ok': True})
                    elif kind == 'question':
                        def observe_question(state):
                            try:
                                self.observe_question(state)
                            except Exception:
                                pass  # Recording is never transport control flow.
                        observe_question('requested')
                        try:
                            answer = self.question(record['question'])
                        except BaseException:
                            observe_question('delivery_failed')
                            raise
                        observe_question('returned')
                        try:
                            response(record, {'answer': answer})
                        except BaseException:
                            observe_question('delivery_failed')
                            raise
                        observe_question('sent')
                except (Blocked, ValueError, KeyError, OSError) as exc:
                    # A failed owner question has no safe synthetic answer. Close
                    # the host input so its pending callback rejects rather than
                    # leaving the one decoder waiting forever.
                    if record.get('type') == 'question':
                        with worker_error_lock:
                            worker_error.append(exc)
                        close_input()
                        return
                    try:
                        response(record, {'error': str(exc)})
                    except BaseException as send_error:
                        with worker_error_lock:
                            worker_error.append(send_error)
                except BaseException as exc:
                    with worker_error_lock:
                        worker_error.append(exc)

            def decode():
                try:
                    for line in proc.stdout:
                        try:
                            value = json.loads(line)
                        except ValueError as exc:
                            raise Blocked('invalid SDK transport JSON: ' + str(exc)) from None
                        kind = value.get('type') if isinstance(value, dict) else None
                        if kind in ('event', 'question', 'claim', 'command', 'cleanup'):
                            # Store-backed callbacks belong to the prompt caller. The
                            # decoder remains free to service controls even while that
                            # caller waits for an owner answer or a command.
                            callbacks.put(value)
                        elif kind == 'target':
                            target = value.get('target')
                            if value.get('status') != 'active' or not isinstance(target, dict):
                                raise Blocked('SDK host returned an invalid steering target')
                            with self._control_lock:
                                self.active_target = target
                                self._send_control = send
                            if self._parent_steering is not None:
                                self._parent_steering.activate(target)
                        elif kind == 'steer':
                            request_id = value.get('request_id')
                            status = value.get('status')
                            if not isinstance(request_id, str) or not isinstance(status, str):
                                raise Blocked('SDK host returned an invalid steering status')
                            self.steering_states[request_id] = status
                            update = {'request_id': request_id, 'status': status}
                            try:
                                self.steering_status(update)
                            except Exception:
                                pass
                            if self._parent_steering is not None:
                                self._parent_steering.status(update)
                        elif kind == 'session':
                            session = value.get('session')
                            if not (isinstance(session, dict) and isinstance(session.get('id'), str)
                                    and isinstance(session.get('file'), str)):
                                raise Blocked('SDK session record has an invalid saved session identity')
                            self.saved_session = session
                            self.opened_session = session
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
                            result.append(value['text'])
                            # Multiplexed host input intentionally remains open
                            # for controls; the result is its terminal boundary.
                            close_input()
                        elif kind == 'error':
                            raise Blocked('SDK operation failed: ' + str(value.get('message')))
                        else:
                            raise Blocked('unknown SDK transport record: ' + str(kind))
                except BaseException as exc:
                    with worker_error_lock:
                        worker_error.append(exc)
                finally:
                    callbacks.put(None)

            with self._control_lock:
                self.active_target = None
                self.steering_states = {}
                self._send_control = send if steering is not None else None
            reader = threading.Thread(target=decode)
            try:
                send(request)
                reader.start()
                while True:
                    record = callbacks.get()
                    if record is None:
                        break
                    if record['type'] == 'event':
                        try:
                            self.observe(record)
                        except Exception:
                            pass
                    else:
                        callback(record)
                        if worker_error:
                            close_input()
                            break
                reader.join()
                with worker_error_lock:
                    if worker_error:
                        raise worker_error[0]
                code = proc.wait()
                if code or not result:
                    errors.seek(0)
                    raise Blocked('SDK host exited without a result (exit ' + str(code) + '): ' + errors.read())
                return result[0]
            finally:
                # An active target is valid only for this host invocation.
                with self._control_lock:
                    self.active_target = None
                    self._send_control = None
                if self._parent_steering is not None:
                    self._parent_steering.close()
                    self._parent_steering = None
                close_input()
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait()
                proc.stdout.close()


def terminal_question(question):
    if not sys.stdin.isatty():
        raise Blocked('owner input needed: ' + question + '; run interactively to answer; partial work retained')
    return input(question + '\n> ')
