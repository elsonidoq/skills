"""Standard, private file-backed checkpoint storage for graph control state.

Callers compile their graph with the yielded saver and use a stable thread_id and
sync durability. State should contain control facts and references, not payloads.
"""
from contextlib import contextmanager
import os
from pathlib import PurePosixPath

from langgraph.checkpoint.sqlite import SqliteSaver

from .store import safe_path

# Graph state holds control references. Provider and Git effects are reconciled
# against private history; checkpoints alone never authorize effect replay.


@contextmanager
def graph_saver(authority):
    """Open a saver beside, never inside, the existing workflow history database."""
    authority.assert_held()
    root = authority.database.parent
    for suffix in ('', '-wal', '-shm', '-journal'):
        safe_path(root, 'graph.sqlite' + suffix)
    path = safe_path(root, 'graph.sqlite')
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    os.close(fd)
    with SqliteSaver.from_conn_string(str(path)) as saver:
        yield saver


from typing import Annotated, TypedDict
import json
import uuid

from langchain_core.runnables import RunnableConfig
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Send, interrupt

from .engine import (Engine, _COMPLETION_REPORTING, _DECISION_CONSTRAINTS,
                     _IMPLEMENTATION_AUTHORITY, _ROUTINE_AUTHORITY, _dirty_input, _safe_error)
from .sessions import select_session
from types import SimpleNamespace
from .git_effects import FocusedGit
from .pi_adapter import WaitingQuestion, effective_saved_session, question_context
from .trace_capture import consuming_question_context, optional_record, question_scope, record_worker_question
from .store import Blocked, canonical, git
import hashlib
import re
from .git_effects import _commit_result
from .metric_artifacts import artifact_relative
from .verification import CheckFailure, manual_gates, run_checks


def _merge_results(left, right):
    return {**left, **right}


class TaskState(TypedDict, total=False):
    task_id: str
    baseline: str
    verification_target: str | None
    invocation_id: str
    chain: list
    prompt_kind: str
    correction_id: str
    session: dict
    check_id: str
    checkpoints: dict
    next_node: str
    review_predecessor: str
    review_execution: str
    result: dict
    review_action: str
    pending_question: dict
    answer: str
    question_invocation: str
    recovery: dict
    wave: list
    wave_pending: list
    wave_results: Annotated[dict, _merge_results]
    in_wave: bool
    wave_error: str


def _wave_paths(task):
    """Return declared mutation regions, or None when they cannot be coordinated.

    Ownership is optional input, not admission. Unknown or unsafe regions simply
    mean the task cannot share a wave. Generated outputs are mutation regions too.
    """
    owned = task.get('owned_paths')
    outputs = task.get('generated_outputs', [])
    if not isinstance(owned, list) or not owned or not isinstance(outputs, list):
        return None
    result = []
    for raw in owned + outputs:
        if not isinstance(raw, str) or not raw or '\\' in raw or '\x00' in raw:
            return None
        parts = raw.rstrip('/').split('/')
        if not parts or any(part in ('', '.', '..') for part in parts):
            return None
        path = PurePosixPath(*parts)
        if path.is_absolute():
            return None
        result.append(path)
    return result


def _ready_wave(ready):
    """Choose an ordered disjoint wave without changing task intake semantics."""
    if not ready:
        return []
    selected = [ready[0]]
    regions = _wave_paths(ready[0])
    if regions is None:
        return selected
    for task in ready[1:]:
        paths = _wave_paths(task)
        if paths is None or any(a == b or a in b.parents or b in a.parents for a in regions for b in paths):
            continue
        selected.append(task)
        regions.extend(paths)
    return selected


def _head_matches(engine, expected, task=None):
    """Allow verified same-run focused checkpoints and the metric commit.

    For an implementation task's effects, also accept linear commits made outside the
    run (for example by the coordinator) that leave unfinished tasks' claimed paths
    alone; the task's checks and the final review still run on the actual HEAD.
    Review/completion targets pass no task: a commit after review must not ship
    unreviewed. Verification tasks (owned_paths: []) prove one exact HEAD, so a new
    commit still needs an explicitly pinned target.
    """
    if _own_head_matches(engine, expected):
        return True
    return task is not None and task.get('owned_paths') != [] and _external_commits_accepted(engine, expected)


def _external_commits_accepted(engine, expected):
    store, project, run = engine.authority.store, engine.authority.project, engine.run
    current = git(project, 'rev-parse', 'HEAD').decode().strip()
    try:
        git(project, 'merge-base', '--is-ancestor', expected, current)
    except Blocked:
        return False  # reset, rebase or amend: history was rewritten
    rows = git(project, 'rev-list', '--reverse', '--parents', expected + '..' + current).decode().split('\n')
    own = {item['sha'] for item in store.completed_checkpoints(run).values() if not item.get('no_change')}
    own |= {json.loads(row['details']).get('sha') for row in store.db.execute(
        "SELECT details FROM execution_history WHERE run_id=? AND kind='metric_artifact'", (run,))}
    recorded = {json.loads(row['details']).get('sha') for row in store.db.execute(
        "SELECT details FROM execution_history WHERE run_id=? AND kind='external_commit'", (run,))}
    live = {}
    for row in store.db.execute("SELECT task_id FROM execution_tasks WHERE run_id=? AND state!='complete'", (run,)):
        facts = store.task_facts(run, row['task_id'])
        for name in facts['paths'] + facts['artifacts']:
            live[name] = row['task_id']
    cursor, external = expected, []
    for row in filter(None, rows):
        sha, *parents = row.split()
        if parents != [cursor]:
            return False  # merge or non-linear history
        cursor = sha
        if sha in own:
            continue
        paths = sorted(filter(None, git(project, 'diff-tree', '--no-commit-id', '--no-renames',
                                        '--name-only', '-r', '-z', sha).decode().split('\0')))
        for name in paths:
            if name in live:
                raise Blocked('commit ' + sha + ' made outside the run includes ' + name + ', which unfinished task '
                              + live[name] + ' claimed; the run cannot verify that task\'s work. Move the path out of '
                              'that commit (for example git reset --soft ' + sha + '^, then commit without it), '
                              'or let the task finish first, then resume.')
        external.append((sha, paths))
    for sha, paths in external:
        if sha not in recorded:
            store.history(run, None, 'external_commit', 'accepted', {'sha': sha, 'paths': paths})
    return True


def _own_head_matches(engine, expected):
    store, project = engine.authority.store, engine.authority.project
    current = git(project, 'rev-parse', 'HEAD').decode().strip()
    if current == expected:
        return True
    # Serial focused sibling checkpoints can advance HEAD after a worker settles.
    # Verify actual Git parent/path facts, not just graph branch completion.
    accepted = store.completed_checkpoints(engine.run)
    cursor = expected
    by_parent = {item.get('parent'): item for item in accepted.values() if not item.get('no_change')}
    while cursor in by_parent:
        item = by_parent.pop(cursor)
        sha = item['sha']
        parents = git(project, 'rev-list', '--parents', '-n', '1', sha).decode().split()
        paths = set(filter(None, git(project, 'diff-tree', '--no-commit-id', '--no-renames',
                                    '--name-only', '-r', '-z', sha).decode().split('\0')))
        if parents != [sha, cursor] or not paths or not paths <= set(item['paths']):
            return False
        cursor = sha
        if cursor == current:
            return True
    for row in store.db.execute("SELECT state,details FROM execution_history WHERE run_id=? AND kind='metric_artifact' ORDER BY seq DESC", (engine.run,)):
        facts = json.loads(row['details'])
        if row['state'] == 'not_created' and facts == {'status': 'not_created'}:
            continue
        if (row['state'] not in ('committed', 'committed_after_reported_error')
                or facts.get('status') != row['state'] or facts.get('no_change') is not False
                or facts.get('sha') != current or facts.get('parent') != cursor
                or facts.get('path') != artifact_relative(engine.run)):
            return False
        _commit_result(project, current, cursor, artifact_relative(engine.run))
        return True
    return False


def _verify_target(engine, state, target=None):
    target = target or state.get('verification_target')
    if target is None:
        return
    project = engine.authority.project
    if git(project, 'rev-parse', 'HEAD').decode().strip() != target:
        raise Blocked('verification target differs from HEAD; inspect the pinned repair revision before continuation')
    saved = engine.authority.store.input(engine.run)
    paths = set()
    for base in (saved['review_base'], target + '^'):
        changed = git(project, 'diff', '--no-renames', '--name-only', '-z', base, target)
        paths.update(os.fsdecode(raw) for raw in changed.split(b'\0') if raw)
    for task in engine.contract['tasks']:
        for key in (('owned_paths', 'paths') if task['id'] == state['task_id'] else ('owned_paths',)):
            values = task.get(key)
            if isinstance(values, list):
                paths.update(str(PurePosixPath(p)) for p in values if isinstance(p, str) and p)
    name = _dirty_input(project, paths)
    if name:
        raise Blocked('verification input has uncommitted changes in ' + name + '; preserve and reconcile it before retrying')


def task_graph(engine, saver, *, review=False):
    """Compile the task boundary with optional directed waves and independent review.

    The caller starts the run in Store and uses its run ID as the graph thread ID.
    Invoke with {} for a new thread, or None to resume its latest checkpoint,
    with durability='sync'. Set review=True to continue through independent review
    and scoped repair; the final verdict is in state['result']. An inspected stale
    grant can be refreshed with {'review_action': 'refresh_target'} on that thread.
    Never use graph time travel for effect recovery.
    """
    if not isinstance(engine, Engine):
        raise TypeError('task_graph requires the existing Engine helpers')
    store, project, run = engine.authority.store, engine.authority.project, engine.run
    tasks = {task['id']: task for task in engine.contract['tasks']}
    adapters = {}

    def history(task_id, kind):
        return [(row['state'], json.loads(row['details'])) for row in store.db.execute(
            'SELECT state,details FROM execution_history WHERE run_id=? AND task_id=? AND kind=? ORDER BY seq',
            (run, task_id, kind))]

    def record(task_id, kind, identity, facts):
        store.history(run, task_id, kind, 'recorded', {'id': identity, **facts})

    def read_record(task_id, kind, identity):
        found = [facts for status, facts in history(task_id, kind)
                 if status == 'recorded' and facts.get('id') == identity]
        if len(found) != 1:
            raise Blocked('graph operation record missing or ambiguous; inspect retained history before continuation')
        return found[0]

    def effects(task_id):
        facts = store.task_facts(run, task_id)
        selected = facts['paths'] + facts['artifacts']
        return {'head': git(project, 'rev-parse', 'HEAD').decode().strip(), 'paths': selected,
                'source_state': Engine._repair_source_state(project, selected),
                'index_state': Engine._repair_index_state(project, selected)}

    def verify_effects(value, task):
        if (not _head_matches(engine, value['head'], task) or
                Engine._repair_source_state(project, value['paths']) != value['source_state'] or
                Engine._repair_index_state(project, value['paths']) != value['index_state']):
            raise Blocked('task effects changed; inspect selected Git and source state before continuation')

    def focused_for(state):
        focused = FocusedGit(project, tasks[state['task_id']], store.task_facts(run, state['task_id']))
        focused.base = state['baseline']
        return focused

    def validate(config):
        _check_escalation_stop(store, run)
        if config.get('configurable', {}).get('thread_id') != run:
            raise Blocked('graph thread must use the retained run ID; select the matching thread before continuation')
        saved = store.input(run)
        if not saved or saved['contract'] != engine.contract or saved['executor'] != engine.input_executor:
            raise Blocked('graph run inputs differ from retained contract or executor; inspect original run before continuation')

    def ready(state, config: RunnableConfig):
        validate(config)
        _check_unfinished_escalation(store, run)
        complete = store.completed_checkpoints(run)
        pending = list(state.get('wave_pending') or [])
        while pending:
            item = pending.pop(0)
            if item['task_id'] not in complete:
                return {**item, 'wave_pending': pending, 'checkpoints': complete}
        remaining = [task for task in engine.contract['tasks'] if task['id'] not in complete]
        eligible = [task for task in remaining if all(dep in complete for dep in task.get('depends', []))]
        wave = _ready_wave(eligible) if engine.parallel else eligible[:1]
        if len(wave) > 1:
            prepared = [prepare(task, complete, in_wave=True) for task in wave]
            return {'wave': prepared, 'next_node': 'fanout', 'wave_pending': []}
        return prepare(wave[0], complete) if wave else no_ready(remaining, complete)

    def no_ready(remaining, complete):
        if remaining:
            raise Blocked('no dependency-ready task; inspect task dependencies and retained checkpoints')
        return {'checkpoints': complete, 'next_node': 'review_route' if review else 'end'}

    def prepare(task, complete, *, in_wave=False):
        baseline = git(project, 'rev-parse', 'HEAD').decode().strip()
        store.task(run, task['id'], 'running', baseline)
        with question_scope(task_id=task['id'], purpose='manual_gate'):
            manual_gates(task, engine.question)
        return {'task_id': task['id'], 'baseline': baseline, 'invocation_id': uuid.uuid4().hex,
                'chain': [], 'prompt_kind': 'initial', 'correction_id': '',
                'session': None, 'recovery': None, 'verification_target': None, 'checkpoints': complete, 'next_node': 'worker',
                'in_wave': in_wave, 'wave_error': None}

    def worker(state, config: RunnableConfig):
        validate(config)
        if state.get('wave_error'):
            raise Blocked('directed wave worker stopped; inspect its retained invocation before recovery: ' + state['wave_error'])
        task = tasks[state['task_id']]
        invocation = state['invocation_id']
        events = [(status, facts) for status, facts in history(task['id'], 'worker_invocation')
                  if facts.get('invocation_id') == invocation]
        if events:
            status, facts = events[-1]
            if status == 'returned' and facts.get('waiting') is True:
                verify_effects(facts['effects'], task)
                return {'session': facts['session'], 'pending_question': facts['question'], 'next_node': 'wait'}
            if status != 'returned':
                raise Blocked('graph worker call ' + invocation + ' is uncertain or unsuccessful; inspect its process, session and retained result before continuation')
            selected = facts['paths'] + facts['artifacts']
            if (not _head_matches(engine, facts['head'], task) or
                    Engine._repair_source_state(project, selected) != facts['source_state'] or
                    Engine._repair_index_state(project, selected) != facts['index_state']):
                raise Blocked('settled graph worker effects drifted; inspect Git and selected bytes before continuation')
            return {'session': facts.get('session'), 'chain': state['chain'] + [invocation], 'next_node': 'checks'}
        # A reservation can survive a crash before the started record. It is not
        # evidence that the provider was never reached. Never dispatch it again.
        if any(facts.get('invocation_id') == invocation for _, facts in history(task['id'], 'worker_dispatch')):
            raise Blocked('graph worker reservation has no settled result; inspect its process and session before continuation')
        store.task(run, task['id'], 'running', state['baseline'])
        focused = focused_for(state)
        recovery = state.get('recovery')
        profile = engine.implementation_fallback if recovery and recovery['action'] == 'escalate' else engine.executor
        if (task['id'] not in adapters or (recovery and state['prompt_kind'] == 'recovery'
                and recovery['action'] in ('fresh', 'escalate'))):
            adapters[task['id']] = engine.adapter(project, profile, question=engine.question)
        adapter = adapters[task['id']]
        def question_trace(status, **facts):
            optional_record(record_worker_question, store, run, task['id'], invocation, status, **facts)
        adapter.question_trace = question_trace
        adapter.lock_fd = engine.authority.lock.fileno()
        if state.get('session') is not None:
            adapter.saved_session = state['session']
        role = 'fixing_worker' if isinstance(engine.contract.get('monitor'), dict) and engine.contract['monitor'].get('correction_of') else 'worker'
        request, reuse_key = engine._session_request(task, role)
        # A directed wave starts distinct fresh contexts. Reuse remains available
        # at sequential task boundaries; two active branches never select one context.
        selection = select_session(request, [] if state.get('in_wave') else engine.session_candidates)
        if state['prompt_kind'] == 'initial':
            selected = next((candidate for candidate in ([] if state.get('in_wave') else engine.session_candidates)
                             if candidate['id'] == selection['session_id']), None)
            if selected:
                adapter.saved_session = selected['saved_session']
            store.history(run, task['id'], 'session', 'selected', selection)
        if state['prompt_kind'] == 'initial':
            body = ('Execute this one requested task in the current project. Read relevant files, make the smallest '
                    'correct edits and run relevant actual checks. Never stage or commit; the runner creates the focused '
                    'checkpoint. Do not install globally, refresh credentials, change global settings, delegate, or '
                    'perform unrequested external operations. Preserve unrelated and pre-existing work. '
                    'No new planning/evidence artifacts. Finish worker-owned acceptance.\n'
                    + _DECISION_CONSTRAINTS + engine.paid_authority() + '\nTask: ' + canonical(task))
        elif state['prompt_kind'] == 'correction':
            correction = read_record(task['id'], 'graph_correction', state['correction_id'])
            verify_effects(correction['effects'], task)
            body = ('A runner-owned REQUIRED check or checkpoint failed. Inspect the actual failure and make a '
                    'reasoned scoped correction; do not skip checks or bypass hooks/signing. '
                    'The runner reruns required checks before checkpointing.\nActual failure:\nActual failed attempt: ' + canonical(correction['failure'])
                    + '\n' + _DECISION_CONSTRAINTS + engine.paid_authority() + '\nTask: ' + canonical(task))
        elif state['prompt_kind'] == 'recovery':
            prior = read_record(task['id'], 'graph_recovery', recovery['id'])
            verify_effects(prior['effects'], task)
            body = ('Continue only the unfinished same-task work. Do not replay settled effects. '
                    'Apply the inspected targeted correction and preserve all original acceptance and gates.\n'
                    + 'Retained failure and diagnosis: ' + canonical(prior['reference'])
                    + '\n' + _DECISION_CONSTRAINTS + engine.paid_authority() + '\nTask: ' + canonical(task))
        if state.get('prompt_kind') == 'answer':
            settled = [facts for status, facts in history(task['id'], 'worker_invocation')
                       if status == 'returned' and facts.get('waiting') is True
                       and facts.get('invocation_id') == state['question_invocation']]
            if len(settled) != 1:
                raise Blocked('settled question evidence missing or ambiguous; inspect retained invocation')
            verify_effects(settled[0]['effects'], task)
            body = ('Continue the retained task and pending question. The prior call settled; do not repeat its effects. '
                    'The actual owner answer is data, not broader permission. Respect denial and all existing gates.\n'
                    + 'Pending question, actual answer and settled effects: ' + canonical({'invocation_id': state['question_invocation'],
                        'question': state['pending_question'], 'answer': state['answer'], 'effects': settled[0]['effects']})
                    + '\n' + _DECISION_CONSTRAINTS + engine.paid_authority() + '\nTask: ' + canonical(task))
        if state.get('verification_target'):
            body += ('\nRerun the original offline verification at ' + state['verification_target'] +
                     '. Run ordinary offline checks only; do not edit project files or perform external actions. '
                     'Return fresh results; the prior proof does not establish acceptance.')
        prompt = (_IMPLEMENTATION_AUTHORITY + _ROUTINE_AUTHORITY + _COMPLETION_REPORTING + '\n'
                  + engine._delivery_issue_context() + body)
        def claim(name):
            focused.claim(name)
            store.history(run, task['id'], 'mutation', 'claimed', focused.facts())
        def command(phase, call):
            observed = focused.command(phase, call)
            if observed['claimed']:
                store.history(run, task['id'], 'mutation', 'claimed', focused.facts())
            details = {'call': call}
            if observed['skipped']:
                details['uncommitted_changes'] = observed['skipped']
            store.history(run, task['id'], 'tool_command', 'started' if phase == 'start' else 'returned', details)
        session = effective_saved_session(state.get('session'), getattr(adapter, 'saved_session', None))
        dispatch_recovery = ({key: recovery[key] for key in ('action', 'diagnosis', 'predecessor')}
                             if recovery and state['prompt_kind'] == 'recovery'
                             and recovery['action'] in ('fresh', 'escalate') else None)
        store.reserve_worker_dispatch(run, task['id'], invocation, session, recovery=dispatch_recovery)
        if dispatch_recovery and recovery['action'] == 'escalate':
            store.history(run, task['id'], 'implementation_escalation', 'started',
                          {**dispatch_recovery, 'executor': profile, 'invocation_id': invocation})
        invocation_kind = 'corrective_worker' if state['chain'] else 'task_worker'
        store.history(run, task['id'], 'worker_invocation', 'started',
                      {'invocation_id': invocation, 'session': session, 'prompt': prompt, 'executor': profile,
                       'predecessor_invocation_id': state['chain'][-1] if state['chain'] else None,
                       'correction_id': state.get('correction_id'),
                       'recovery_id': recovery['id'] if recovery else None})
        steering = {'run_id': run, 'task_id': task['id'], 'invocation_id': invocation,
                    'role': invocation_kind}
        if getattr(adapter, 'parent_steering_available', lambda: False)():
            adapter.enable_parent_steering(steering)
        adapter.last_interval = None
        adapter.last_observation = None
        adapter.opened_session = None
        from contextlib import nullcontext
        monitoring = getattr(engine, '_local_tracing', None)
        boundary = (monitoring.boundary('worker', task_id=task['id'], invocation=True, model=profile.get('model'))
                    if monitoring else nullcontext())
        if state['prompt_kind'] == 'answer':
            question_trace('continuation_started', route='paused', tool_call_id=state['pending_question'].get('tool_call_id'),
                           predecessor_invocation_id=state['question_invocation'])
        submitted = {'submission': {'version': 1, 'report': None, 'evidence': [],
                                    'gaps': ['submission report unavailable or capture failed']}}
        def retain_submission(result):
            if not isinstance(result, WaitingQuestion):
                from .trace_capture import submission_facts
                submitted.update(submission_facts(project, task, result,
                                                  claimed_paths=focused.task_edited | focused.known_artifacts))
        with boundary:
            try:
                result = engine._prompt_worker(adapter, prompt, claim=claim, command=command,
                                               cleanup=focused.cleanup_artifact, saved_session=session, reuse_key=reuse_key,
                                               pause_questions=True, submission=retain_submission)
            except BaseException as exc:
                if state['prompt_kind'] == 'answer':
                    question_trace('continuation_failed', route='paused',
                                   tool_call_id=state['pending_question'].get('tool_call_id'),
                                   predecessor_invocation_id=state['question_invocation'],
                                   error_type=type(exc).__name__)
                actual = getattr(adapter, 'opened_session', None) or getattr(adapter, 'saved_session', None)
                if actual is not None:
                    store.bind_worker_dispatch(run, task['id'], invocation, actual)
                status = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                store.history(run, task['id'], 'worker_invocation', status,
                              {'invocation_id': invocation, 'error': _safe_error(exc), 'session': actual,
                               'effects': effects(task['id']), 'prompt': prompt,
                               'diagnostic': getattr(exc, 'diagnostic', None), **submitted})
                store.history(run, task['id'], 'worker', status, {'role': role, 'error': _safe_error(exc)})
                engine._append_metric(adapter, invocation_id=invocation, task_id=task['id'],
                                      role=role if role == 'fixing_worker' else 'corrective_worker' if state['chain'] else 'worker', outcome=status,
                                      selection=selection, continued=state['prompt_kind'] != 'initial',
                                      expected_session_id=(session or {}).get('id'))
                raise
            engine._append_metric(adapter, invocation_id=invocation, task_id=task['id'],
                                  role=role if role == 'fixing_worker' else 'corrective_worker' if state['chain'] else 'worker', outcome='settled',
                                  selection=selection, continued=state['prompt_kind'] != 'initial',
                                  expected_session_id=(session or {}).get('id'))
        store.history(run, task['id'], 'worker', 'returned', {'role': role})
        actual = getattr(adapter, 'opened_session', None) or getattr(adapter, 'saved_session', None)
        if actual is not None:
            store.bind_worker_dispatch(run, task['id'], invocation, actual)
        if state['prompt_kind'] == 'answer':
            question_trace('continuation_returned', route='paused', tool_call_id=state['pending_question'].get('tool_call_id'),
                           predecessor_invocation_id=state['question_invocation'])
        if isinstance(result, WaitingQuestion):
            question_trace('requested', route='paused', **result.question)
            facts = {'invocation_id': invocation, 'session': result.session, 'waiting': True,
                     'question': result.question, 'effects': effects(task['id'])}
            store.history(run, task['id'], 'worker_invocation', 'returned', facts)
            return {'session': result.session, 'pending_question': result.question, 'next_node': 'wait'}
        _verify_target(engine, state)
        paths, artifacts = focused.facts()['paths'], focused.facts()['artifacts']
        selected = paths + artifacts
        facts = {'invocation_id': invocation,
                 'summary': submitted.get('submission', {}).get('report') or result, 'session': actual, **submitted,
                 'head': git(project, 'rev-parse', 'HEAD').decode().strip(), 'paths': paths, 'artifacts': artifacts,
                 'source_state': Engine._repair_source_state(project, selected),
                 'index_state': Engine._repair_index_state(project, selected),
                 'observation': getattr(adapter, 'last_observation', None),
                 'reuse_key': reuse_key, 'request': request}
        store.history(run, task['id'], 'worker_invocation', 'returned', facts)
        return {'session': facts['session'], 'chain': state['chain'] + [invocation], 'next_node': 'checks'}

    def wait(state, config: RunnableConfig):
        validate(config)
        while True:
            answer = interrupt({'task_id': state['task_id'], 'invocation_id': state['invocation_id'],
                                'question': state['pending_question']})
            if (isinstance(answer, dict) and answer.get('invocation_id') == state['invocation_id']
                    and isinstance(answer.get('answer'), str) and answer['answer'].strip()):
                break
        facts = [facts for status, facts in history(state['task_id'], 'worker_invocation')
                 if status == 'returned' and facts.get('waiting') is True
                 and facts.get('invocation_id') == state['invocation_id']]
        if len(facts) != 1:
            raise Blocked('settled question evidence missing or ambiguous; inspect retained invocation')
        verify_effects(facts[0]['effects'], tasks[state['task_id']])
        optional_record(record_worker_question, store, run, state['task_id'], state['invocation_id'],
                        'resolved', route='paused', tool_call_id=state['pending_question'].get('tool_call_id'),
                        question=state['pending_question'].get('question'), resolution=answer['answer'])
        return {'answer': answer['answer'], 'prompt_kind': 'answer',
                'question_invocation': state['invocation_id'],
                'invocation_id': uuid.uuid4().hex, 'chain': [*state['chain'], state['invocation_id']],
                'next_node': 'worker'}

    def checks(state, config: RunnableConfig):
        validate(config)
        task = tasks[state['task_id']]
        returned = [facts for status, facts in history(task['id'], 'worker_invocation')
                    if status == 'returned' and facts.get('invocation_id') == state['chain'][-1]]
        if len(returned) != 1:
            raise Blocked('task worker result is missing or ambiguous; inspect retained invocation before checks')
        facts = returned[0]
        selected = facts['paths'] + facts['artifacts']
        if (not _head_matches(engine, facts['head'], task) or
                Engine._repair_source_state(project, selected) != facts['source_state'] or
                Engine._repair_index_state(project, selected) != facts['index_state']):
            raise Blocked('worker effects changed before checks; inspect Git and selected bytes before continuation')
        refs = []
        attribution = {'producer_invocation_id': state['chain'][-1], 'correction_id': state.get('correction_id')}
        if state.get('verification_target'):
            attribution['target_head'] = state['verification_target']
        def retain(status, attempt):
            store.history(run, task['id'], 'check', status,
                          {**attempt, **attribution})
            if status == 'passed':
                refs.append(store.db.execute(
                    "SELECT seq FROM execution_history WHERE run_id=? AND task_id=? AND kind='check' AND state='passed' ORDER BY seq DESC LIMIT 1",
                    (run, task['id'])).fetchone()['seq'])
        try:
            results = run_checks(project, task, lock_fd=engine.authority.lock.fileno(), completed=retain)
        except CheckFailure as exc:
            if state.get('verification_target'):
                raise Blocked('required verification failed at the pinned revision; inspect check history: ' + str(exc)) from exc
            if state.get('recovery') and state['recovery']['action'] == 'escalate':
                store.history(run, task['id'], 'implementation_escalation', 'failed', {'error': canonical(exc.attempt)})
                raise Blocked('implementation escalation required check failed; stop and notify the owner; owner direction required: ' + canonical(exc.attempt)) from exc
            previous = (read_record(task['id'], 'graph_correction', state['correction_id'])['failure']
                        if state.get('correction_id') else None)
            if exc.attempt == previous:
                raise Blocked('required check failed and remains unchanged after scoped correction: ' + canonical(exc.attempt))
            correction_id = uuid.uuid4().hex
            record(task['id'], 'graph_correction', correction_id, {
                'failure': exc.attempt, 'effects': effects(task['id']),
                'producer_invocation_id': state['chain'][-1], 'predecessor_correction_id': state.get('correction_id')})
            return {'correction_id': correction_id, 'prompt_kind': 'correction',
                    'invocation_id': uuid.uuid4().hex, 'next_node': 'worker'}
        _verify_target(engine, state)
        if state.get('verification_target'):
            # Reopen reconciles a no-change intent against the exact referenced check rows.
            results = [{**attempt, **attribution} for attempt in results]
        check_id = uuid.uuid4().hex
        record(task['id'], 'graph_checks', check_id, {'checks': results, 'check_refs': refs,
                'producer_invocation_id': state['chain'][-1], 'effects': effects(task['id'])})
        return {'check_id': check_id, 'next_node': 'checkpoint'}

    def checkpoint(state, config: RunnableConfig):
        validate(config)
        task = tasks[state['task_id']]
        recovered = store.completed_checkpoints(run)
        if task['id'] in recovered:
            return {'next_node': 'ready'}
        checked = read_record(task['id'], 'graph_checks', state['check_id'])
        verify_effects(checked['effects'], task)
        returned = [facts for status, facts in history(task['id'], 'worker_invocation')
                    if status == 'returned' and facts.get('invocation_id') == state['chain'][-1]]
        if len(returned) != 1:
            raise Blocked('task worker result missing or ambiguous before checkpoint; inspect retained history')
        summary = returned[0]['summary']
        focused = focused_for(state)
        occurrence = uuid.uuid4().hex
        def intent(value):
            if state.get('verification_target') and value['parent'] != state['verification_target']:
                raise Blocked('verification checkpoint differs from pinned revision; inspect HEAD before continuation')
            store.history(run, task['id'], 'checkpoint', 'started', {**value, 'check_refs': checked['check_refs'],
                'checks': checked['checks'], 'task_id': task['id'], 'checkpoint_occurrence_id': occurrence,
                'producer_invocation_id': state['chain'][-1], 'correction_chain': state['chain'], 'summary': summary})
        focused.before_checkpoint = intent
        focused.before_git_commit = lambda: store.history(run, task['id'], 'checkpoint', 'attempting', {'task_id': task['id']})
        try:
            result = focused.checkpoint()
        except BaseException as exc:
            result = focused.reconcile_checkpoint()
            uncertain = (isinstance(exc, (KeyboardInterrupt, SystemExit)) and
                         getattr(focused, 'git_commit_started', False))
            status = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
            store.history(run, task['id'], 'checkpoint', status,
                          {'error': str(exc), 'no_effect': result is None and not uncertain})
            if result is None:
                if state.get('verification_target'):
                    raise
                if state.get('recovery') and state['recovery']['action'] == 'escalate':
                    store.history(run, task['id'], 'implementation_escalation', 'failed', {'error': str(exc)})
                    raise Blocked('implementation escalation failed; stop and notify the owner; owner direction required: ' + str(exc)) from exc
                # A failed/uncertain Git attempt must be reconciled before any correction.
                if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                    raise
                failure = {'checkpoint_error': str(exc)}
                previous = (read_record(task['id'], 'graph_correction', state['correction_id'])['failure']
                            if state.get('correction_id') else None)
                if failure == previous:
                    raise Blocked('checkpoint remains unchanged after scoped correction: ' + str(exc))
                correction_id = uuid.uuid4().hex
                record(task['id'], 'graph_correction', correction_id, {
                    'failure': failure, 'effects': effects(task['id']),
                    'producer_invocation_id': state['chain'][-1],
                    'checkpoint_occurrence_id': occurrence, 'predecessor_correction_id': state.get('correction_id')})
                return {'correction_id': correction_id, 'prompt_kind': 'correction',
                        'invocation_id': uuid.uuid4().hex, 'next_node': 'worker'}
        result['parent'] = None if result['no_change'] else git(project, 'rev-parse', result['sha'] + '^').decode().strip()
        result.update({'task_id': task['id'], 'checkpoint_occurrence_id': occurrence,
                       'producer_invocation_id': state['chain'][-1], 'correction_chain': state['chain']})
        store.history(run, task['id'], 'checkpoint', 'passed', result)
        settled = returned[0]
        if settled.get('request') and not (state.get('recovery') and state['recovery']['action'] == 'escalate'):
            engine._settle_session(task, SimpleNamespace(saved_session=settled.get('session'),
                                   last_observation=settled.get('observation')),
                                   settled['request'], settled['reuse_key'], result)
        store.task(run, task['id'], 'complete', state['baseline'], result['sha'],
                   {'summary': summary, 'checks': checked['checks'], 'paths': result['paths'],
                    'generated_artifacts': result['artifacts']})
        if state.get('recovery') and state['recovery']['action'] == 'escalate':
            store.history(run, task['id'], 'implementation_escalation', 'completed', {'sha': result['sha'],
                'producer_invocation_id': state['chain'][-1], 'recovery_id': state['recovery']['id']})
        return {'next_node': 'ready'}

    def escalation_guard(node):
        def guarded(state, config: RunnableConfig):
            try:
                return node(state, config)
            except BaseException as exc:
                if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                    raise
                if state.get('recovery') and state['recovery']['action'] == 'escalate':
                    events = history(state['task_id'], 'implementation_escalation')
                    if not events or events[-1][0] == 'started':
                        store.history(run, state['task_id'], 'implementation_escalation', 'failed', {'error': str(exc)})
                    raise Blocked('implementation escalation failed; stop and notify the owner; owner direction required: ' + str(exc)) from exc
                raise
        return guarded

    def connected(node, phase):
        def call(state, config: RunnableConfig):
            from contextlib import nullcontext
            monitoring = getattr(engine, '_local_tracing', None)
            boundary = (monitoring.boundary(phase, task_id=state.get('task_id')
                                             if phase not in ('ready', 'join') else None)
                        if monitoring else nullcontext())
            with store.thread_connection(), boundary:
                _verify_target(engine, state)
                return node(state, config)
        return call

    def wave_worker(state, config: RunnableConfig):
        # Return terminal failure as data so all siblings settle before any shared
        # checks or Git. An uncertain/failed provider call is never retried here.
        try:
            result = escalation_guard(worker)(state, config)
        except Exception as exc:
            # Preserve the stop even if failure preceded a dispatch/terminal row.
            # Recovery must inspect operation history, never repeat this call.
            result = {'next_node': 'worker', 'wave_error': _safe_error(exc)}
        item = {**state, **result}
        return {'wave_results': {state['invocation_id']: item}}

    def wave_join(state, config: RunnableConfig):
        validate(config)
        results = [state['wave_results'][item['invocation_id']] for item in state['wave']]
        # Checkpoint successful siblings even when another branch failed. Keep the
        # failed exact invocation at the ordinary inspected worker recovery boundary.
        results.sort(key=lambda item: item['next_node'] != 'checks')
        return {'wave_pending': results, 'wave': [], 'next_node': 'ready'}

    builder = StateGraph(TaskState)
    builder.add_node('wave_worker', connected(wave_worker, 'worker'))
    builder.add_node('wave_join', connected(wave_join, 'join'))
    builder.add_edge('wave_worker', 'wave_join')
    builder.add_edge('wave_join', 'ready')
    for name, node in (('ready', ready), ('worker', worker), ('wait', wait), ('checks', checks), ('checkpoint', checkpoint)):
        builder.add_node(name, connected(escalation_guard(node) if name in ('worker', 'checks', 'checkpoint') else node,
                                         name))
    builder.add_edge(START, 'ready')
    ready_edges = {'worker': 'worker', 'checks': 'checks', 'wait': 'wait', 'end': END}
    if review:
        _add_review_nodes(builder, engine, validate)
        ready_edges['review_route'] = 'review_route'
    def route_ready(state):
        if state['next_node'] == 'fanout':
            return [Send('wave_worker', item) for item in state['wave']]
        return ready_edges[state['next_node']]
    builder.add_conditional_edges('ready', route_ready)
    builder.add_conditional_edges('worker', lambda state: state['next_node'], {'checks': 'checks', 'wait': 'wait'})
    builder.add_edge('wait', 'worker')
    builder.add_conditional_edges('checks', lambda state: state['next_node'], {'worker': 'worker', 'checkpoint': 'checkpoint'})
    builder.add_conditional_edges('checkpoint', lambda state: state['next_node'], {'worker': 'worker', 'ready': 'ready'})
    return builder.compile(checkpointer=saver)


def _validate_verification_retry(engine, state, status, failure, target_head):
    project, store, run = engine.authority.project, engine.authority.store, engine.run
    task_id, value = state['task_id'], failure['effects']
    task = next(task for task in engine.contract['tasks'] if task['id'] == task_id)
    # Use the retained _UnsuccessfulOutcome, not optional submission capture or an SDK error.
    if (status != 'failed' or failure.get('error') != 'worker explicitly failed; partial work retained'
            or not failure.get('session')):
        raise Blocked('verification needs an explicitly returned failed outcome; inspect the settled worker call')
    if (task.get('owned_paths') != [] or task.get('generated_outputs') or task.get('handoff_paths')
            or any(store.task_facts(run, task_id).values())
            or value != {'head': state['baseline'], 'paths': [], 'source_state': {}, 'index_state': {}}):
        raise Blocked('verification needs explicit empty owned_paths and no write effects; inspect the task and retained claims')
    _verify_target(engine, state, target_head)
    parents = git(project, '--no-replace-objects', 'rev-list', '--parents', '-1', target_head).decode().split()
    if parents != [target_head, value['head']]:
        raise Blocked('verification target must be a direct single-parent repair; inspect the failed revision and HEAD')
    with question_scope(task_id=task_id, purpose='manual_gate'):
        manual_gates(task, engine.question)


def graph_recovery_action(engine, graph, config, action, *, diagnosis=None, target_head=None, transfer=None,
                          owner_authorized=False):
    """Apply an inspected action; external transfer stops before further dispatch.

    Explicit continuation actions resume the retained thread. A failed invocation
    is never replayed. Completed Git effects are reconciled first.
    """
    from .processes import inspect_recorded_writers
    store, run, project = engine.authority.store, engine.run, engine.authority.project
    engine.authority.assert_held()
    if config.get('configurable', {}).get('thread_id') != run:
        raise Blocked('graph recovery needs the retained run thread; select the matching thread')
    saved = store.input(run)
    if not saved or saved['contract'] != engine.contract or saved['executor'] != engine.input_executor:
        raise Blocked('graph recovery inputs differ from retained run; restore the original contract and executor')
    retained_paid = saved['authority'].get('paid_scope') if isinstance(saved['authority'], dict) else None
    if retained_paid is not None and retained_paid != engine.paid_scope:
        raise Blocked('graph recovery paid scope differs from retained run; restore original scope')
    inspect_recorded_writers(store.db, 'graph recovery')
    if target_head is not None and action != 'fresh':
        raise Blocked('--target-head requires fresh verification; inspect the failed offline invocation')
    if action == 'external':
        snapshot = graph.get_state(config)
        if (not isinstance(transfer, dict) or snapshot.values.get('task_id') != transfer.get('task_id')
                or snapshot.interrupts or not set(snapshot.next).intersection({'worker', 'checks', 'checkpoint'})):
            raise Blocked('external recovery needs the matching stopped task without a pending question; inspect the retained graph before continuation')
        checkpoint = engine.recover_task(transfer, owner_authorized=owner_authorized)
        _check_escalation_stop(store, run)
        graph.update_state(config, {'next_node': 'ready', 'recovery': None}, as_node='checkpoint')
        return checkpoint
    _check_escalation_stop(store, run)
    _check_unfinished_escalation(store, run)
    snapshot = graph.get_state(config)
    state = snapshot.values
    selecting_target = target_head is not None and tuple(snapshot.next) == ('worker',)
    if not selecting_target and set(snapshot.next).intersection({'worker', 'checks', 'checkpoint', 'ready'}):
        _verify_target(engine, state)
    completed = store.completed_checkpoints(run)
    if action == 'refresh-review-target':
        if len(completed) != len(engine.contract['tasks']) or snapshot.interrupts or 'review_route' not in graph.nodes:
            raise Blocked('review target refresh needs completed tasks and an unpaused review graph; reconcile unfinished work first')
        graph.update_state(config, {'checkpoints': completed, 'next_node': 'review_route',
                                    'review_action': 'refresh_target'}, as_node='ready')
        return graph.invoke(None, config, durability='sync')
    if action not in ('continue', 'fresh', 'escalate'):
        raise Blocked('unknown graph recovery action; select an inspected recovery action')
    if not isinstance(diagnosis, str) or diagnosis.strip().lower() in ('', 'unknown', 'retry', 'yes'):
        raise Blocked('graph recovery needs a substantive inspected diagnosis and targeted correction')
    task_id = state.get('task_id')
    if task_id in completed:
        if target_head is not None:
            raise Blocked('verification task already checkpointed; inspect its result instead of retrying')
        graph.update_state(config, {'next_node': 'ready', 'recovery': None}, as_node='checkpoint')
        return graph.invoke(None, config, durability='sync')
    if snapshot.interrupts:
        raise Blocked('graph recovery needs the failed worker boundary, but a worker question is pending; '
                      'answer it with plain resume, without --recovery-action')
    if tuple(snapshot.next) != ('worker',):
        raise Blocked('graph recovery needs the failed worker boundary, but the run stopped after it (next: ' +
                      (', '.join(snapshot.next) or 'none') + '), for example at a failed required check; '
                      'correct the cause (for example a defect outside the task\'s owned paths), then use plain '
                      'resume, without --recovery-action, to rerun that stage')
    rows = list(store.db.execute("SELECT state,details FROM execution_history WHERE run_id=? AND task_id=? AND kind='worker_invocation' ORDER BY seq", (run, task_id)))
    if rows and rows[-1]['state'] == 'returned':
        returned = json.loads(rows[-1]['details'])
        if target_head is not None:
            raise Blocked('verification needs a failed invocation; reconcile the returned call with plain resume')
        if returned.get('invocation_id') == state.get('invocation_id'):
            return graph.invoke(None, config, durability='sync')
    if rows and rows[-1]['state'] == 'returned':
        raise Blocked('graph recovery needs an inspected terminal worker failure, but the last worker call returned; '
                      'reconcile it with plain resume, without --recovery-action')
    if not rows or rows[-1]['state'] not in ('failed', 'interrupted'):
        raise Blocked('graph recovery needs an inspected terminal worker failure; the last worker call is live or '
                      'uncertain, so inspect its process and saved session before continuation')
    failure = json.loads(rows[-1]['details'])
    if 'effects are uncertain' in failure.get('error', ''):
        raise Blocked('worker settlement and effects are uncertain; inspect the saved operation before any continuation')
    predecessor = failure.get('invocation_id')
    if predecessor != state.get('invocation_id') or not isinstance(failure.get('effects'), dict):
        raise Blocked('graph recovery failure lacks exact invocation/effect evidence; inspect retained call before continuation')
    value = failure['effects']
    if target_head is not None:
        _validate_verification_retry(engine, state, rows[-1]['state'], failure, target_head)
    elif (not _head_matches(engine, value['head'], next((item for item in engine.contract['tasks'] if item['id'] == task_id), None)) or
            Engine._repair_source_state(project, value['paths']) != value['source_state'] or
            Engine._repair_index_state(project, value['paths']) != value['index_state']):
        raise Blocked('failed worker effects drifted; inspect selected Git and source state before continuation')
    escalations = list(store.db.execute("SELECT state FROM execution_history WHERE run_id=? AND task_id=? AND kind='implementation_escalation' ORDER BY seq", (run, task_id)))
    if escalations and escalations[-1]['state'] != 'completed':
        raise Blocked('implementation escalation is unresolved; stop and notify the owner; owner direction required')
    if action == 'continue' and not failure.get('session'):
        raise Blocked('continued recovery needs the exact saved session, but the failed worker opened no session; '
                      'use --recovery-action fresh with the inspected diagnosis')
    if action == 'escalate' and engine.implementation_fallback is None:
        raise Blocked('implementation escalation has no permitted fallback; configure it at launch, or use '
                      '--recovery-action ' + ('continue' if failure.get('session') else 'fresh') + ' with the inspected diagnosis')
    identity = uuid.uuid4().hex
    recovery = {'id': identity, 'action': action, 'diagnosis': diagnosis, 'predecessor': predecessor}
    reference = {'invocation_id': predecessor, 'error': failure.get('error'),
                 'saved_session_id': (failure.get('session') or {}).get('id'), 'targeted_correction': diagnosis}
    update = {}
    if target_head is not None:
        reference.update(failed_head=value['head'], target_head=target_head)
        value = {**value, 'head': target_head}
        update = {'baseline': target_head, 'verification_target': target_head}
    store.history(run, task_id, 'graph_recovery', 'recorded', {'id': identity, 'action': action, 'effects': value, 'reference': reference})
    chain = list(state.get('chain') or [])
    if predecessor not in chain:
        chain.append(predecessor)
    graph.update_state(config, {**update, 'prompt_kind': 'recovery', 'recovery': recovery, 'chain': chain, 'wave_error': None,
                               'invocation_id': uuid.uuid4().hex,
                               'session': failure.get('session') if action == 'continue' else None,
                               'next_node': 'worker'}, as_node='ready')
    return graph.invoke(None, config, durability='sync')


def answer_graph_question(graph, config, question, *, trace_observer=None):
    """Present the retained question through a terminal or attached consumer.

    No input leaves the checkpoint paused. The invocation identity binds the reply
    to the precise settled call; private question/session data is not status output.
    """
    snapshot = graph.get_state(config)
    interrupts = snapshot.interrupts
    if len(interrupts) != 1:
        raise Blocked('no single pending graph question; inspect the retained graph before answering')
    pending = interrupts[0].value
    def trace(status, **facts):
        optional_record(trace_observer, pending, status, **facts)
    token = question_context.set(trace)
    context_token = consuming_question_context.set({
        'task_id': pending.get('task_id'), 'invocation_id': pending['invocation_id'],
        'tool_call_id': pending['question'].get('tool_call_id'), 'route': 'paused'})
    try:
        try:
            answer = question(pending['question']['question'])
        except (Blocked, EOFError) as exc:
            trace('unanswered', error_type=type(exc).__name__)
            return None
        except BaseException as exc:
            trace('unanswered', error_type=type(exc).__name__)
            raise
    finally:
        consuming_question_context.reset(context_token)
        question_context.reset(token)
    if not isinstance(answer, str) or not answer.strip():
        trace('unanswered')
        return None
    return graph.invoke(Command(resume={'invocation_id': pending['invocation_id'], 'answer': answer}),
                        config, durability='sync')


def run_graph(engine, *, action=None, diagnosis=None, target_head=None, transfer=None, owner_authorized=False):
    """Run with isolated local tracing and scoped suppression of hosted graph tracing."""
    from langsmith import tracing_context
    try:
        from .tracing import configured_tracing
        monitoring = configured_tracing(engine.contract)
    except Exception:
        try:
            import sys
            print('coherence tracing: initialization unavailable', file=sys.stderr)
        except Exception:
            pass
        monitoring = None
    engine._local_tracing = monitoring
    try:
        with tracing_context(enabled=False, parent=False):
            try:
                result = _run_graph(engine, action=action, diagnosis=diagnosis, target_head=target_head, transfer=transfer,
                                    owner_authorized=owner_authorized)
            except BaseException as exc:
                # The original exception remains authoritative, even if history,
                # capture, publication or the status callback is unavailable.
                report = engine.finish_delivery_trace(error=exc)
                try:
                    import sys
                    print('coherence trace finish: ' + json.dumps(report), file=sys.stderr, flush=True)
                except BaseException:
                    pass
                raise
            waiting = isinstance(result, dict) and result.get('status') == 'waiting'
            report = engine.finish_delivery_trace(waiting=waiting)
            return {**result, 'trace': report} if isinstance(result, dict) else result
    finally:
        if monitoring is not None:
            try:
                monitoring.close()
            except BaseException:
                pass
        engine._local_tracing = None


def _run_graph(engine, *, action=None, diagnosis=None, target_head=None, transfer=None, owner_authorized=False):
    """Run the public graph against its retained input and checkpoint."""
    store, project, run = engine.authority.store, engine.authority.project, engine.run
    if engine.resume:
        saved = store.input(run)
        authority = saved.get('authority') if saved else None
        if not isinstance(authority, dict) or authority.get('backend') != 'langgraph-v1':
            raise Blocked('run is not a retained LangGraph thread; use retained revision 4c1725ebded2f89dec6933b8d193bf34997c62ce with its compatible environment and original arguments, without conversion')
        if saved['contract'] != engine.contract or saved['executor'] != engine.input_executor:
            raise Blocked('graph run inputs differ from retained contract or executor; restore the original run inputs before continuation')
        engine.parallel = authority.get('parallel', False)
        engine.delivery_scope = authority.get('delivery_scope')
        if authority.get('paid_scope') != engine.paid_scope:
            raise Blocked('graph paid scope differs from retained launch; restore the original scope')
    if not engine.resume:
        baseline = git(project, 'rev-parse', 'HEAD').decode().strip()
        requested = engine.contract.get('review_base', baseline)
        if not isinstance(requested, str) or not requested:
            raise Blocked('review_base must be a Git commit')
        try:
            review_base = git(project, 'rev-parse', '--verify', requested + '^{commit}').decode().strip()
            git(project, 'merge-base', '--is-ancestor', review_base, baseline)
        except Blocked:
            raise Blocked('review_base must resolve to an ancestor of the run baseline') from None
        store.start(run, baseline, contract=engine.contract, executor=engine.input_executor,
                    authority={'backend': 'langgraph-v1', 'paid_scope': engine.paid_scope, 'parallel': engine.parallel,
                               'routine_authority': True, 'review_policy': 'owner-pair-v1',
                               **({'delivery_scope': engine.delivery_scope} if engine.delivery_scope is not None else {})},
                    review_base=review_base)
        if getattr(engine, 'launch', None):
            store.history(run, None, 'launch_environment', 'recorded', engine.launch)
    config = {'configurable': {'thread_id': run}, 'recursion_limit': max(100, len(engine.contract['tasks']) * 20 + 50)}
    may_have_pin = target_head is not None
    try:
        with graph_saver(engine.authority) as saver:
            graph = task_graph(engine, saver, review=True)
            snapshot = graph.get_state(config)
            may_have_pin = may_have_pin or bool(snapshot.values.get('verification_target'))
            if engine.resume and not snapshot.values and not snapshot.next:
                raise Blocked('graph checkpoint is missing; inspect retained run and graph storage before continuation')
            if (engine.resume and not snapshot.next and (snapshot.values.get('result') or {}).get('status') == 'rejected'):
                graph.update_state(config, {'result': None, 'review_action': None, 'next_node': 'review_route'}, as_node='ready')
            if action:
                result = graph_recovery_action(engine, graph, config, action, diagnosis=diagnosis, target_head=target_head,
                                               transfer=transfer, owner_authorized=owner_authorized)
            elif snapshot.interrupts:
                def trace_pending(pending, status, **facts):
                    optional_record(record_worker_question, engine.authority.store, engine.run,
                                    pending['task_id'], pending['invocation_id'], status, route='paused',
                                    **pending['question'], **facts)
                result = answer_graph_question(graph, config, engine.question, trace_observer=trace_pending)
            else:
                try:
                    result = graph.invoke(None if engine.resume else {}, config, durability='sync')
                except GraphRecursionError as exc:
                    rounds = store.review_chain(run)['fixing_round_count']
                    raise Blocked('run stopped at the graph step limit after ' + str(rounds) + ' repair rounds without '
                                  'approval, so repairs are not making progress. Inspect the review findings and fixer '
                                  'returns with history (for example, a file changed outside edit/write is never '
                                  'committed); correct the cause, then abandon this run and start a new run for the '
                                  'remaining work.') from exc
            snapshot = graph.get_state(config)
            if snapshot.interrupts:
                pending = snapshot.interrupts[0].value
                identity = pending.get('invocation_id', 'unknown')
                store.history(run, pending.get('task_id'), 'graph_wait', 'waiting', {'invocation_id': identity})
                store.finish(run, 'interrupted', git(project, 'rev-parse', 'HEAD').decode().strip(), 'waiting for owner answer')
                return {'status': 'waiting', 'run_id': run, 'question_id': identity,
                        'reason': 'Run ' + run + ' is waiting for ' + identity + '; resume interactively or through the attached parent to answer the pending operation.'}
            if isinstance(result, dict) and isinstance(result.get('result'), dict):
                public = dict(result['result'])
                if public.get('status') == 'complete' and not _head_matches(engine, public.get('sha')):
                    raise Blocked('approved review target drifted; inspect the actual reviewed head before completion')
                if isinstance(public.get('checkpoints'), dict):
                    public['checkpoints'] = list(public['checkpoints'].values())
                public['baseline'] = store.db.execute('SELECT baseline FROM execution_runs WHERE run_id=?', (run,)).fetchone()['baseline']
                public['usage'] = engine.usage_summary()
                return engine._finalize_metric_artifact(public)
            return result
    except BaseException as exc:
        state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
        try:
            active = store.db.execute("SELECT task_id,baseline FROM execution_tasks WHERE run_id=? AND state='running'", (run,)).fetchall()
            for item in active:
                store.task(run, item['task_id'], state, item['baseline'], details={'error': _safe_error(exc)})
            head = git(project, 'rev-parse', 'HEAD').decode().strip()
            retained = store.db.execute('SELECT state,result,error FROM execution_runs WHERE run_id=?', (run,)).fetchone()
            if retained is not None and tuple(retained) != (state, head, _safe_error(exc)):
                store.finish(run, state, head, _safe_error(exc))
            # Do not advance a pinned application HEAD to commit optional telemetry on failure.
            pinned = False
            if may_have_pin and engine.metric_artifact is not None:
                with graph_saver(engine.authority) as saver:
                    pending = task_graph(engine, saver, review=True).get_state(config).values
                pinned = pending.get('verification_target')
            if not pinned:
                engine._finalize_metric_artifact()
        except BaseException:
            # Failed failure-bookkeeping cannot mask the operation that failed.
            pass
        raise


def _check_escalation_stop(store, run):
    """Preserve the owner-direction stop before any task or review dispatch."""
    for row in store.db.execute("SELECT seq,task_id FROM execution_history WHERE run_id=? AND kind='implementation_escalation' AND state='failed'", (run,)):
        later = [(r['kind'], r['state'], json.loads(r['details'])) for r in store.db.execute(
            "SELECT kind,state,details FROM execution_history WHERE run_id=? AND task_id=? AND seq>? AND kind IN ('external_recovery','checkpoint') ORDER BY seq", (run, row['task_id'], row['seq']))]
        if not any(c.get('external_recovery_id') == x.get('recovery_id') and x.get('recovery_id') and c.get('sha') == x.get('sha')
                   for k, s, c in later if k == 'checkpoint' and s == 'passed'
                   for k2, s2, x in later if k2 == 'external_recovery' and s2 == 'completed'):
            raise Blocked('implementation escalation failed for task ' + row['task_id'] + '; stop and notify the owner; owner direction required')


def _check_unfinished_escalation(store, run):
    """Do not release later tasks after an escalation lost its terminal record."""
    rows = store.db.execute("SELECT seq,task_id,state FROM execution_history WHERE run_id=? AND kind='implementation_escalation' ORDER BY seq", (run,)).fetchall()
    latest = {row['task_id']: row for row in rows}
    for task, row in latest.items():
        if row['state'] != 'started':
            continue
        later = [(item['kind'], item['state'], json.loads(item['details'])) for item in store.db.execute(
            "SELECT kind,state,details FROM execution_history WHERE run_id=? AND task_id=? AND seq>? AND kind IN ('external_recovery','checkpoint') ORDER BY seq", (run, task, row['seq']))]
        if not any(c.get('external_recovery_id') == x.get('recovery_id') and x.get('recovery_id') and c.get('sha') == x.get('sha')
                   for k, s, c in later if k == 'checkpoint' and s == 'passed'
                   for k2, s2, x in later if k2 == 'external_recovery' and s2 == 'completed'):
            raise Blocked('implementation escalation is unresolved for task ' + task + '; stop and notify the owner; owner direction required')


def _add_review_nodes(builder, engine, validate):
    """Attach review transitions to the internal task graph, not the legacy controller."""
    store, project, run = engine.authority.store, engine.authority.project, engine.run
    scope = hashlib.sha256(canonical(engine.contract['tasks']).encode()).hexdigest()

    def retained():
        return store.review_chain(run, private=True)

    def base():
        return store.input(run)['review_base']

    def value(item):
        return {'approved': item['state'] == 'approved',
                'findings': item['findings'][-1] if item.get('findings') else [],
                'suggestions': item['suggestions'][-1] if item.get('suggestions') else [],
                **item['references'].get('review_summary', {})}

    def route(state, config: RunnableConfig):
        validate(config)
        if state.get('review_action'):
            if state['review_action'] != 'refresh_target':
                raise Blocked('unknown graph review action; select the inspected target refresh action')
            return {'next_node': 'review_refresh', 'review_execution': uuid.uuid4().hex}
        chain = retained()
        if chain['uncertain']:
            if engine._recover_format_rejection(chain, base()):
                chain = retained()
            else:
                raise Blocked('review invocation outcome is uncertain; inspect it before any replay')
        items = chain['executions']
        if not items:
            return {'next_node': 'review_dispatch', 'review_predecessor': None,
                    'review_execution': uuid.uuid4().hex}
        last = items[-1]
        if last['role'] == 'reviewer':
            review = value(last)
            if last['state'] == 'approved':
                head = last['references'].get('head')
                if not isinstance(head, str) or not head or not _head_matches(engine, head):
                    raise Blocked('approved review target drifted or is missing; inspect the reviewed head before completion')
                store.finish(run, 'complete', head)
                return {'next_node': 'end', 'result': {'status': 'complete', 'run_id': run,
                        'sha': head, 'checkpoints': state['checkpoints'], 'review': review}}
            if (engine.resume and last['state'] == 'failed' and not last['uncertain'] and
                    last['references'].get('failure_category') == 'transport'):
                return {'next_node': 'review_payload', 'review_predecessor': last['execution_id']}
            if last['state'] != 'rejected' or review['approved']:
                raise Blocked('independent review was not an actionable rejection; inspect retained failure and coverage before continuation: ' + canonical(review))
            if not review['findings']:
                if not engine.resume or store.review_policy(run) != 'owner-pair-v1' or not review.get('coverage_gaps'):
                    raise Blocked('independent review has remaining coverage gaps; inspect retained evidence before reassessment: ' + canonical(review))
                return {'next_node': 'review_evidence', 'review_predecessor': last['execution_id']}
            if store.review_policy(run) == 'historical-two-review-one-fixer' and last['review_ordinal'] != 1:
                raise Blocked('independent final review findings (commits retained): ' + canonical(review))
            return {'next_node': 'review_repair', 'review_predecessor': last['execution_id'],
                    'review_execution': uuid.uuid4().hex}
        if last['role'] != 'fixer':
            raise Blocked('unknown retained review role; inspect review history')
        if last['state'] != 'approved':
            if not engine.resume:
                raise Blocked('repair did not settle; inspect its invocation before continuation')
            return {'next_node': 'review_recover_repair', 'review_predecessor': last['execution_id']}
        return {'next_node': 'review_dispatch', 'review_predecessor': last['execution_id'],
                'review_execution': uuid.uuid4().hex}

    def review_dispatch(state, config: RunnableConfig):
        validate(config)
        items = retained()['executions']
        # If the graph checkpoint was lost after the SDK outcome, route from the
        # retained result; a dispatched/failed call is never automatically repeated.
        if any(item['execution_id'] == state['review_execution'] for item in items):
            return {'next_node': 'review_route'}
        predecessor = state.get('review_predecessor')
        if (predecessor is not None and items and items[-1]['role'] == 'reviewer'
                and items[-1]['trigger_execution_id'] == predecessor):
            return {'next_node': 'review_route'}
        if predecessor is None:
            if items:
                raise Blocked('review history changed before initial dispatch; inspect retained chain')
            _verify_target(engine, state)
            ordinal, round_, reviewer_id = 1, 0, state['review_execution']
            inputs = engine._review_inputs(list(state['checkpoints'].values()))
        else:
            if not items or items[-1]['execution_id'] != predecessor or items[-1]['role'] != 'fixer' or items[-1]['state'] != 'approved':
                raise Blocked('repair predecessor changed before review; inspect retained chain')
            fix = items[-1]
            ordinal, round_, reviewer_id, inputs = fix['review_ordinal'] + 1, fix['fixing_round'], state['review_execution'], None
            if store.review_policy(run) == 'owner-pair-v1' and fix['review_ordinal'] > 1:
                rejection = next((item for item in items if item['execution_id'] == fix['trigger_execution_id']), None)
                grant = store.owner_pair_for_rejection(run, rejecting_execution_id=fix['trigger_execution_id'], review_base=base(),
                    review_head=rejection['references'].get('head') if rejection else None, original_scope=scope)
                if grant is None:
                    raise Blocked('assigned fixer has no retained owner pair grant; inspect authorization')
                reviewer_id = store.reserve_owner_pair_reviewer(run, grant['grant_id'], fixer_execution_id=predecessor)['reviewer_execution_id']
                if any(item['execution_id'] == reviewer_id for item in items):
                    return {'next_node': 'review_route'}
        head = git(project, 'rev-parse', 'HEAD').decode().strip()
        if predecessor is not None and items[-1]['references'].get('head') != head:
            raise Blocked('review target drifted after repair; inspect affected continuation before dispatch')
        try:
            engine._review(review_base=base(), head=head, ordinal=ordinal, fixing_round=round_,
                           trigger_execution_id=predecessor, predecessor_execution_id=predecessor,
                           input_checkpoints=inputs, execution_id=reviewer_id)
        except BaseException as exc:
            store.finish(run, 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed',
                         head, _safe_error(exc))
            raise
        return {'next_node': 'review_route'}

    def repair(state, config: RunnableConfig):
        validate(config)
        items = retained()['executions']
        if any(item['execution_id'] == state['review_execution'] for item in items):
            return {'next_node': 'review_route'}
        rejection = items[-1]
        if rejection['execution_id'] != state['review_predecessor'] or rejection['state'] != 'rejected':
            raise Blocked('rejecting review changed before repair; inspect retained chain')
        head = rejection['references'].get('head')
        if not head or git(project, 'rev-parse', 'HEAD').decode().strip() != head:
            raise Blocked('review target drifted before repair; inspect and refresh the affected target')
        fixer = state['review_execution']
        if store.review_policy(run) == 'owner-pair-v1' and rejection['review_ordinal'] > 1:
            grant = store.owner_pair_for_rejection(run, rejecting_execution_id=rejection['execution_id'],
                                                    review_base=base(), review_head=head, original_scope=scope)
            if grant is None:
                grant = store.authorize_owner_pair(run, uuid.uuid4().hex, rejecting_execution_id=rejection['execution_id'],
                    review_base=base(), review_head=head, original_scope=scope, fixer_execution_id=fixer, reviewer_execution_id=uuid.uuid4().hex)
            if git(project, 'rev-parse', 'HEAD').decode().strip() != grant['review_head']:
                raise Blocked('review target drifted after pair assignment; inspect the affected target before dispatch')
            fixer = store.reserve_owner_pair_fixer(run, grant['grant_id'], rejecting_execution_id=rejection['execution_id'],
                                                   review_base=base(), review_head=head, original_scope=scope)['fixer_execution_id']
            if any(item['execution_id'] == fixer for item in items):
                return {'next_node': 'review_route'}
        engine.run_fix(value(rejection)['findings'], trigger_execution_id=rejection['execution_id'], review_base=base(),
                       execution_id=fixer, review_ordinal=rejection['review_ordinal'],
                       fixing_round=rejection['fixing_round'] + 1, predecessor_execution_id=rejection['execution_id'])
        return {'next_node': 'review_route'}

    def recover_repair(state, config: RunnableConfig):
        validate(config)
        items = retained()['executions']
        item = items[-1]
        if item['execution_id'] != state['review_predecessor'] or item['state'] == 'approved':
            return {'next_node': 'review_route'}
        recovered = engine._recover_assigned_fix(item, base())
        if recovered is not None:
            rejection = next(entry for entry in items if entry['execution_id'] == item['trigger_execution_id'])
            engine.run_fix(value(rejection)['findings'], trigger_execution_id=rejection['execution_id'], review_base=base(),
                           execution_id=item['execution_id'], review_ordinal=item['review_ordinal'],
                           fixing_round=item['fixing_round'], predecessor_execution_id=item['predecessor_execution_id'], recovered=recovered)
        return {'next_node': 'review_route'}

    def evidence(state, config: RunnableConfig):
        validate(config)
        items = retained()['executions']
        last = items[-1]
        if last['execution_id'] != state['review_predecessor']:
            return {'next_node': 'review_route'}
        head = last['references'].get('head')
        current = git(project, 'rev-parse', 'HEAD').decode().strip()
        if not head:
            raise Blocked('evidence-only review target missing; inspect the reviewed target before reassessment')
        if current != head:
            # Only the retained same-run metric finalizer is permitted between the
            # reviewed head and evidence reassessment; verify its actual Git effect.
            rows = store.db.execute("SELECT state,details FROM execution_history WHERE run_id=? AND kind='metric_artifact' ORDER BY seq DESC", (run,))
            facts, status = None, None
            for row in rows:
                try:
                    candidate = json.loads(row['details'])
                except (TypeError, ValueError):
                    candidate = None
                if row['state'] == 'not_created' and candidate == {'status': 'not_created'}:
                    continue
                facts, status = candidate, row['state']
                break
            path = artifact_relative(run)
            if (not isinstance(facts, dict) or status not in ('committed', 'committed_after_reported_error') or
                    facts.get('status') != status or facts.get('no_change') is not False or
                    facts.get('sha') != current or facts.get('parent') != head or facts.get('path') != path):
                raise Blocked('evidence-only review target drifted; inspect finalizer history and reconcile the reviewed target')
            _commit_result(project, current, head, path)
        digest = engine._review_evidence_digest()
        authorized = store.evidence_reassessment_for_rejection(run, last['execution_id'], review_base=base(), review_head=head)
        if authorized is None:
            try:
                diagnosis = engine.question(
                    'As coordinator, inspect the settled evidence/coverage-only review rejection, retained worker returns and check evidence. '
                    'Diagnose routine technical gaps autonomously and use supported explicit continuation; do not ask the owner to debug or for renewed consent solely because files changed. Preserve material scope, paid/external, security/data, manual and uncertain-authority gates. '
                    'Supply a substantive targeted diagnosis for the outstanding gaps, or leave empty only when newly applicable retained evidence changed. '
                    'Do not request a fixer, replay task work, or invent approval. Retained review: ' + canonical(value(last)))
            except BaseException as exc:
                raise Blocked('coordinator evidence reassessment diagnosis unavailable; no reviewer dispatched: ' + str(exc)) from exc
            authorized = store.authorize_evidence_reassessment(run, uuid.uuid4().hex, rejecting_execution_id=last['execution_id'],
                review_base=base(), review_head=head, diagnosis=diagnosis if isinstance(diagnosis, str) else '', evidence_digest=digest)
        if any(item['execution_id'] == authorized['execution_id'] for item in items):
            return {'next_node': 'review_route'}
        _, result, status = engine._review(review_base=base(), head=head,
            ordinal=last['review_ordinal'] + 1, fixing_round=last['fixing_round'], trigger_execution_id=last['execution_id'],
            predecessor_execution_id=last['execution_id'], execution_id=authorized['execution_id'])
        if status == 'rejected' and not result['findings']:
            raise Blocked('evidence reassessment retains coverage gaps; investigate them before another explicit resume: ' + canonical(result['coverage_gaps']))
        return {'next_node': 'review_route'}

    def refresh(state, config: RunnableConfig):
        validate(config)
        if any(item['execution_id'] == state['review_execution'] for item in retained()['executions']):
            return {'next_node': 'review_route', 'review_action': None}
        head = git(project, 'rev-parse', 'HEAD').decode().strip()
        _, review, status = engine._review(review_base=base(), head=head, ordinal=0,
                                          execution_id=state['review_execution'], refresh_target=True)
        if status == 'rejected':
            store.finish(run, 'failed', head, 'fresh current-target review rejected; inspect findings before explicit resume')
            return {'next_node': 'end', 'review_action': None,
                    'result': {'status': 'rejected', 'run_id': run, 'sha': head,
                               'checkpoints': state['checkpoints'], 'review': review}}
        return {'next_node': 'review_route', 'review_action': None}

    def payload_recovery(state, config: RunnableConfig):
        """Repeat only the same, inspected provider field-size rejection."""
        validate(config)
        items = retained()['executions']
        last = items[-1]
        if last['execution_id'] != state['review_predecessor']:
            return {'next_node': 'review_route'}
        head = last['references'].get('head')
        attempts = store.db.execute('SELECT state,uncertainty,recorded_at FROM execution_review_attempts WHERE run_id=? AND execution_id=? ORDER BY seq', (run, last['execution_id'])).fetchall()
        failure = store.db.execute("SELECT state,details,recorded_at FROM execution_history WHERE run_id=? AND kind='invocation' AND recorded_at>=? ORDER BY seq LIMIT 1", (run, attempts[-1]['recorded_at'])).fetchone() if attempts else None
        try:
            details = json.loads(failure['details']) if failure and failure['state'] == 'failed' else {}
        except (TypeError, ValueError):
            details = {}
        match = re.fullmatch(r"SDK operation failed: Codex error: Invalid response\.create payload: Invalid 'input\[0\]\.content\[0\]\.text': string too long\. Expected a string with maximum length (\d+), but got a string with length (\d+) instead\.", details.get('error', ''))
        dispatch = store.db.execute('SELECT review_base,review_head FROM execution_review_executions WHERE run_id=? AND execution_id=?', (run, last['execution_id'])).fetchone()
        saved = store.input(run)
        predecessor = items[-2] if len(items) > 1 else None
        causal = ((predecessor is None and last['review_ordinal'] == 1 and last['fixing_round'] == 0 and last['trigger_execution_id'] is None and last['predecessor_execution_id'] is None) or
                  (predecessor is not None and predecessor['role'] == 'fixer' and predecessor['state'] == 'approved' and
                   last['trigger_execution_id'] == predecessor['execution_id'] and last['predecessor_execution_id'] == predecessor['execution_id'] and
                   last['review_ordinal'] == predecessor['review_ordinal'] + 1 and last['fixing_round'] == predecessor['fixing_round'] and predecessor['references'].get('head') == head))
        if not (last['attempt_count'] == 2 and match and int(match.group(2)) > int(match.group(1)) and
                [tuple(row)[:2] for row in attempts] == [('dispatched', 0), ('failed', 0)] and
                dispatch is not None and tuple(dispatch) == (base(), head) and failure['recorded_at'] >= attempts[-1]['recorded_at'] and
                details.get('result') == head and last['references'].get('base') == base() and saved and
                saved['contract'] == engine.contract and saved['review_base'] == base() and causal):
            raise Blocked('review transport failure has no inspected matching payload-size diagnosis; inspect the original call before continuation')
        if git(project, 'rev-parse', 'HEAD').decode().strip() != head or git(project, 'status', '--porcelain=v1', '--untracked-files=no'):
            raise Blocked('review delivery target drifted; inspect the reviewed target before continuation')
        engine._review(review_base=base(), head=head, ordinal=last['review_ordinal'],
            fixing_round=last['fixing_round'], trigger_execution_id=last['trigger_execution_id'],
            predecessor_execution_id=last['predecessor_execution_id'], input_checkpoints=last.get('input_checkpoints'),
            execution_id=last['execution_id'], retry_limit=int(match.group(1)))
        return {'next_node': 'review_route'}

    def traced_review(node, phase):
        def call(state, config: RunnableConfig):
            from contextlib import nullcontext
            monitoring = getattr(engine, '_local_tracing', None)
            boundary = (monitoring.boundary(phase) if monitoring else nullcontext())
            with boundary:
                return node(state, config)
        return call

    for name, node in (('review_route', route), ('review_dispatch', review_dispatch), ('review_repair', repair),
                       ('review_recover_repair', recover_repair), ('review_evidence', evidence),
                       ('review_payload', payload_recovery), ('review_refresh', refresh)):
        phase = 'repair' if name in ('review_repair', 'review_recover_repair') else 'review'
        builder.add_node(name, traced_review(node, phase))
    builder.add_conditional_edges('review_route', lambda state: state['next_node'], {
        'review_dispatch': 'review_dispatch', 'review_repair': 'review_repair',
        'review_recover_repair': 'review_recover_repair', 'review_evidence': 'review_evidence',
        'review_payload': 'review_payload', 'review_refresh': 'review_refresh', 'end': END})
    for name in ('review_dispatch', 'review_repair', 'review_recover_repair', 'review_evidence', 'review_payload'):
        builder.add_edge(name, 'review_route')
    builder.add_conditional_edges('review_refresh', lambda state: state['next_node'],
                                  {'end': END, 'review_route': 'review_route'})
