"""Optional, private execution-history capture; never controls the observed operation."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import json
import uuid
import os
import sys
import time

from .store import canonical

# Known credential values must be collected before their fields are discarded.
_CREDENTIALS = {'token', 'bridge_token', 'transport_token', 'coherence_parent_bridge_token',
            'authorization', 'auth_header', 'auth_headers', 'api_key', 'apikey', 'password',
            'secret', 'credentials'}
# Exclude these containers/paths too, but do not treat generic config text as a secret.
_PRIVATE = _CREDENTIALS | {'environment', 'env', 'config_dump', 'credential_file'}


def _public(value, gaps, secrets):
    credentials = set(secrets)

    def collect(item):
        if isinstance(item, dict):
            for key, child in item.items():
                if (key.lower().replace('-', '_') in _CREDENTIALS and
                        isinstance(child, str) and child):
                    credentials.add(child)
                collect(child)
        elif isinstance(item, list):
            for child in item:
                collect(child)

    collect(value)
    return _filtered(value, gaps, sorted(credentials, key=lambda item: (-len(item), item)))


def _filtered(value, gaps, secrets):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key.lower().replace('-', '_') in _PRIVATE:
                gaps.append('credential or transport field excluded')
            else:
                result[key] = _filtered(item, gaps, secrets)
        return result
    if isinstance(value, list):
        return [_filtered(item, gaps, secrets) for item in value]
    if isinstance(value, str):
        for secret in secrets:
            if secret in value:
                value = value.replace(secret, '[excluded credential]')
                gaps.append('credential or transport field excluded')
    return value


def submission_facts(project, task, result, *, claimed_paths=()):
    """Snapshot explicit report links only, within the assignment's existing ownership.

    Markdown links and backtick-quoted file paths are explicit references, not a
    request to scan the checkout. Never follow external URLs or credential files.
    """
    import re
    from pathlib import Path
    from .pi_adapter import TaskOutcome
    from .store import safe_path

    report = result.explanation if isinstance(result, TaskOutcome) else result
    status = result.status if isinstance(result, TaskOutcome) else 'submitted'
    gaps, evidence = [], []
    secrets = [value for value in (os.environ.get('COHERENCE_PARENT_BRIDGE_TOKEN'),) if value]
    if not isinstance(report, str):
        return {'submission': {'version': 1, 'status': status, 'report': None,
                               'evidence': [], 'gaps': ['meaningful submission report unavailable']}}
    refs = re.findall(r'\[[^\]]*\]\(([^)]+)\)', report)
    refs += re.findall(r'(?im)^\s*evidence:\s*`([^`]+)`', report)
    refs += [value for value in re.findall(r'`([^`\s]+)`', report)
             if '/' in value or re.search(r'\.[A-Za-z0-9_-]+$', value)]
    for reference in dict.fromkeys(refs):
        if reference.startswith('#'):
            continue
        if '://' in reference:
            gaps.append('submitted external evidence content not collected: ' + reference)
            continue
        name = reference.split('#', 1)[0]
        try:
            path = safe_path(project, name)
            relative = path.relative_to(Path(project).resolve()).as_posix()
            owned = task.get('owned_paths', []) + task.get('generated_outputs', []) + list(claimed_paths)
            if not any(relative == item.rstrip('/') or relative.startswith(item.rstrip('/') + '/') for item in owned):
                raise ValueError('outside assigned owned paths')
            if any(part.lower() in _PRIVATE or part.lower() == '.env' or part.lower().startswith('.env.') or
                   part.lower() in ('credentials.json', 'auth.json', 'id_rsa', 'id_ed25519', '.netrc', '.npmrc', '.pypirc')
                   for part in path.parts):
                raise ValueError('credential file excluded')
            if not path.is_file():
                raise ValueError('not an available regular file')
            content = path.read_text()
        except Exception as exc:
            # Do not expose filesystem/credential details from arbitrary submitted paths.
            gaps.append('submitted evidence unavailable: ' + reference + ' (' +
                        (str(exc) if isinstance(exc, ValueError) else type(exc).__name__) + ')')
            continue
        evidence.append({'reference': reference, 'content': content})
    safe = _public({'version': 1, 'status': status, 'report': report, 'evidence': evidence}, gaps, secrets)
    safe['gaps'] = _public(sorted(set(gaps)), [], secrets)
    return {'submission': safe}


def persist_parent_events(store, run, events):
    """Atomically retain an exact batch or raise; callers acknowledge only on success.

    Existing event IDs must have identical original content, including excluded fields.
    Only a digest of that original content is retained for comparison.
    """
    import hashlib
    prepared = []
    secrets = [value for value in (os.environ.get('COHERENCE_PARENT_BRIDGE_TOKEN'),) if value]
    for event in events:
        if not isinstance(event, dict) or event.get('version') != 1 or not isinstance(event.get('id'), str) or not event['id']:
            raise ValueError('invalid parent trace event')
        digest = hashlib.sha256(canonical(event).encode()).hexdigest()
        gaps = []
        safe = _public(event, gaps, secrets)
        prepared.append({'version': 1, 'event': safe, 'source_digest': digest, 'gaps': sorted(set(gaps))})
    with store.transaction() as db:
        existing = {}
        for row in db.execute("SELECT details FROM execution_history WHERE run_id=? AND kind='parent_trace'", (run,)):
            details = json.loads(row[0])
            existing[details['event']['id']] = details
        for item in prepared:
            event_id = item['event']['id']
            prior = existing.get(event_id)
            if prior is not None:
                if prior != item:
                    raise ValueError('conflicting parent trace event ID: ' + event_id)
                continue
            store._history_insert(db, run, None, 'parent_trace', item['event']['kind'], canonical(item), time.time())
            existing[event_id] = item


def record_worker_question(store, run, task, invocation, state, **facts):
    """Retain an optional worker observation without exposing transport credentials."""
    gaps = []
    secrets = [value for value in (os.environ.get('COHERENCE_PARENT_BRIDGE_TOKEN'),) if value]
    details = _public({'version': 1, 'run_id': run, 'task_id': task,
                       'invocation_id': invocation, **facts}, gaps, secrets)
    details['gaps'] = sorted(set(gaps))
    store.history(run, task, 'worker_question_trace', state, details)


consuming_question_context = ContextVar('consuming_question_context', default=None)


@contextmanager
def question_scope(**facts):
    """Supply caller-known identity without changing the input callback interface."""
    token = consuming_question_context.set({**(consuming_question_context.get() or {}), **facts})
    try:
        yield
    finally:
        consuming_question_context.reset(token)


def record_consuming_question(store, run, task, state, **facts):
    """Capture only existing-run input, using the same private filtering as parent facts."""
    if not store.db.execute('SELECT 1 FROM execution_runs WHERE run_id=?', (run,)).fetchone():
        return
    gaps = []
    secrets = [value for value in (os.environ.get('COHERENCE_PARENT_BRIDGE_TOKEN'),) if value]
    details = _public({'version': 1, 'run_id': run, 'task_id': task, **facts}, gaps, secrets)
    details['gaps'] = sorted(set(gaps))
    store.history(run, task, 'consuming_question_trace', state, details)


def capture_questions(question, store, run):
    """Wrap the actual consumer once; never invent an owner reply from a parent resolution.

    Worker lifecycle observations remain separate, linked by the available exact IDs.
    Attached owner-tool events belong to parent_trace; this records only the coordinator
    reply consumed here, not a second owner answer.
    """
    from .pi_adapter import parent_question, question_context, terminal_question
    if getattr(question, '_question_capture_binding', None) == (store, run):
        return question
    responder = ('coordinator' if question is parent_question else
                 'owner' if question is terminal_question else 'unknown')

    @wraps(question)
    def consume(prompt, **kwargs):
        context = dict(consuming_question_context.get() or {})
        facts = {'question_id': uuid.uuid4().hex, **context, 'prompt': prompt,
                 'responder_class': responder, 'owner_only': kwargs.get('owner_only', False)}
        if kwargs.get('decision_context') is not None:
            facts['decision_context'] = kwargs['decision_context']
        previous = question_context.get()

        def observe(state, **extra):
            if state == 'parent_request':
                facts.update(extra)
            optional_record(previous, state, **extra)

        def record(state, **outcome):
            if not optional_record(record_consuming_question, store, run, context.get('task_id'), state,
                                   **{key: value for key, value in facts.items() if key != 'task_id'}, **outcome):
                try:
                    print('question trace capture gap: input outcome could not be retained; inspect workflow storage',
                          file=sys.stderr, flush=True)
                except Exception:
                    pass

        token = question_context.set(observe)
        try:
            try:
                if question is parent_question:
                    kwargs = {**kwargs, 'trace_observer': parent_observer(store, run)}
                answer = question(prompt, **kwargs)
            except BaseException as exc:
                record('exception', error_type=type(exc).__name__, error=str(exc))
                raise
            record('answered', answer=answer)
            return answer
        finally:
            question_context.reset(token)

    consume._question_capture_binding = (store, run)
    return consume


def parent_observer(store, run):
    """Bind transport capture to this run, never to an untrusted returned identity."""
    def observe(observed_run, events):
        if observed_run != run:
            raise ValueError('parent trace run differs from active workflow')
        persist_parent_events(store, run, events)
    return observe


def finish_parent_capture(store, run, *, final):
    """Drain even with no pending worker. Acknowledgement follows durable persistence."""
    from .pi_adapter import drain_parent_trace
    available = all(os.environ.get(key) for key in (
        'COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
        'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN'))
    drained = drain_parent_trace(parent_observer(store, run), final=final) if available else False
    gaps = ['Optional capture can miss events before persistence, including abrupt process death.']
    if not drained:
        gaps.append('Parent capture unavailable.' if not available else
                    'Parent drain, persistence or acknowledgement failed; inspect retained bridge/storage before recovery.')
    coverage = {'state': 'partial' if drained else 'unavailable', 'parent_acknowledged': drained,
                'gaps': gaps}
    # Use the established producer shape so gaps survive the ordinary projector.
    optional_record(persist_parent_events, store, run, [
        {'version': 1, 'id': uuid.uuid4().hex, 'kind': 'gap', 'reason': gap} for gap in gaps])
    return coverage


def optional_record(observer, *args, **kwargs):
    """Recording failure cannot replace the actual question or transport result."""
    if observer is None:
        return False
    try:
        observer(*args, **kwargs)
        return True
    except Exception:
        return False
