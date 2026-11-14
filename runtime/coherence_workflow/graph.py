"""Standard, private file-backed checkpoint storage for graph control state.

Callers compile their graph with the yielded saver and use a stable thread_id and
sync durability. State should contain control facts and references, not payloads.
"""
from contextlib import contextmanager
import os

from langgraph.checkpoint.sqlite import SqliteSaver

from .store import safe_path

# Task execution is internal until the public controller cutover.  Its state contains
# control references; provider and Git effects are reconciled against private history.


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


from typing import TypedDict
import json
import uuid

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from .engine import (Engine, _COMPLETION_REPORTING, _DECISION_CONSTRAINTS,
                     _IMPLEMENTATION_AUTHORITY, _ROUTINE_AUTHORITY)
from .git_effects import FocusedGit
from .pi_adapter import effective_saved_session
from .store import Blocked, canonical, git
from .verification import CheckFailure, manual_gates, run_checks


class TaskState(TypedDict, total=False):
    task_id: str
    baseline: str
    invocation_id: str
    chain: list
    prompt_kind: str
    correction_id: str
    session: dict
    check_id: str
    checkpoints: dict
    next_node: str


def task_graph(engine, saver):
    """Compile the sequential task boundary, without review or public routing.

    The caller starts the run in Store and uses its run ID as the graph thread ID.
    Invoke with {} for a new thread, or None to resume its latest checkpoint,
    with durability='sync'. Never use graph time travel for effect recovery.
    """
    if not isinstance(engine, Engine):
        raise TypeError('task_graph requires the existing Engine helpers')
    store, project, run = engine.authority.store, engine.authority.project, engine.run
    tasks = {task['id']: task for task in engine.contract['tasks']}

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

    def verify_effects(value):
        if (git(project, 'rev-parse', 'HEAD').decode().strip() != value['head'] or
                Engine._repair_source_state(project, value['paths']) != value['source_state'] or
                Engine._repair_index_state(project, value['paths']) != value['index_state']):
            raise Blocked('task effects changed; inspect selected Git and source state before continuation')

    def focused_for(state):
        focused = FocusedGit(project, tasks[state['task_id']], store.task_facts(run, state['task_id']))
        focused.base = state['baseline']
        return focused

    def validate(config):
        if config.get('configurable', {}).get('thread_id') != run:
            raise Blocked('graph thread must use the retained run ID; select the matching thread before continuation')
        saved = store.input(run)
        if not saved or saved['contract'] != engine.contract or saved['executor'] != engine.input_executor:
            raise Blocked('graph run inputs differ from retained contract or executor; inspect original run before continuation')

    def ready(state, config: RunnableConfig):
        validate(config)
        complete = store.completed_checkpoints(run)
        remaining = [task for task in engine.contract['tasks'] if task['id'] not in complete]
        if not remaining:
            return {'checkpoints': complete, 'next_node': 'end'}
        task = next((item for item in remaining if all(dep in complete for dep in item.get('depends', []))), None)
        if task is None:
            raise Blocked('no dependency-ready task; inspect task dependencies and retained checkpoints')
        baseline = git(project, 'rev-parse', 'HEAD').decode().strip()
        store.task(run, task['id'], 'running', baseline)
        manual_gates(task, engine.question)
        return {'task_id': task['id'], 'baseline': baseline, 'invocation_id': uuid.uuid4().hex,
                'chain': [], 'prompt_kind': 'initial', 'correction_id': '',
                'session': None, 'checkpoints': complete, 'next_node': 'worker'}

    def worker(state, config: RunnableConfig):
        validate(config)
        task = tasks[state['task_id']]
        invocation = state['invocation_id']
        events = [(status, facts) for status, facts in history(task['id'], 'worker_invocation')
                  if facts.get('invocation_id') == invocation]
        if events:
            status, facts = events[-1]
            if status != 'returned':
                raise Blocked('graph worker call ' + invocation + ' is uncertain or unsuccessful; inspect its process, session and retained result before continuation')
            selected = facts['paths'] + facts['artifacts']
            if (git(project, 'rev-parse', 'HEAD').decode().strip() != facts['head'] or
                    Engine._repair_source_state(project, selected) != facts['source_state'] or
                    Engine._repair_index_state(project, selected) != facts['index_state']):
                raise Blocked('settled graph worker effects drifted; inspect Git and selected bytes before continuation')
            return {'session': facts.get('session'), 'chain': state['chain'] + [invocation], 'next_node': 'checks'}
        # A reservation can survive a crash before the started record. It is not
        # evidence that the provider was never reached. Never dispatch it again.
        if any(facts.get('invocation_id') == invocation for _, facts in history(task['id'], 'worker_dispatch')):
            raise Blocked('graph worker reservation has no settled result; inspect its process and session before continuation')
        focused = focused_for(state)
        adapter = engine.adapter(project, engine.executor, question=engine.question)
        adapter.lock_fd = engine.authority.lock.fileno()
        if state.get('session') is not None:
            adapter.saved_session = state['session']
        request, reuse_key = engine._session_request(task)
        if state['prompt_kind'] == 'initial':
            body = ('Execute this one requested task in the current project. Read relevant files, make the smallest '
                    'correct edits and run relevant actual checks. Never stage or commit; the runner creates the focused '
                    'checkpoint. Do not install globally, refresh credentials, change global settings, delegate, or '
                    'perform unrequested external operations. Preserve unrelated and pre-existing work. '
                    'No new planning/evidence artifacts. Finish worker-owned acceptance.\n'
                    + _DECISION_CONSTRAINTS + engine.paid_authority() + '\nTask: ' + canonical(task))
        else:
            correction = read_record(task['id'], 'graph_correction', state['correction_id'])
            verify_effects(correction['effects'])
            body = ('A runner-owned required check or checkpoint failed. Inspect the actual failure and make a '
                    'reasoned scoped correction; do not skip checks or bypass hooks/signing. '
                    'The runner reruns required checks before checkpointing.\nActual failure: ' + canonical(correction['failure'])
                    + '\n' + _DECISION_CONSTRAINTS + engine.paid_authority() + '\nTask: ' + canonical(task))
        prompt = (_IMPLEMENTATION_AUTHORITY + _ROUTINE_AUTHORITY + _COMPLETION_REPORTING + '\n'
                  + engine._delivery_issue_context() + body)
        def claim(name):
            focused.claim(name)
            store.history(run, task['id'], 'mutation', 'claimed', focused.facts())
        def command(phase, call):
            focused.command(phase, call)
            store.history(run, task['id'], 'tool_command', 'started' if phase == 'start' else 'returned', {'call': call})
        session = effective_saved_session(state.get('session'), getattr(adapter, 'saved_session', None))
        store.reserve_worker_dispatch(run, task['id'], invocation, session)
        store.history(run, task['id'], 'worker_invocation', 'started', {'invocation_id': invocation, 'session': session})
        try:
            result = engine._prompt_worker(adapter, prompt, claim=claim, command=command,
                                           cleanup=focused.cleanup_artifact, saved_session=session, reuse_key=reuse_key)
        except BaseException as exc:
            actual = getattr(adapter, 'opened_session', None) or getattr(adapter, 'saved_session', None)
            if actual is not None:
                store.bind_worker_dispatch(run, task['id'], invocation, actual)
            store.history(run, task['id'], 'worker_invocation', 'failed',
                          {'invocation_id': invocation, 'error': str(exc), 'session': actual})
            raise
        actual = getattr(adapter, 'opened_session', None) or getattr(adapter, 'saved_session', None)
        if actual is not None:
            store.bind_worker_dispatch(run, task['id'], invocation, actual)
        paths, artifacts = focused.facts()['paths'], focused.facts()['artifacts']
        selected = paths + artifacts
        facts = {'invocation_id': invocation, 'summary': result, 'session': getattr(adapter, 'saved_session', None),
                 'head': git(project, 'rev-parse', 'HEAD').decode().strip(), 'paths': paths, 'artifacts': artifacts,
                 'source_state': Engine._repair_source_state(project, selected),
                 'index_state': Engine._repair_index_state(project, selected)}
        store.history(run, task['id'], 'worker_invocation', 'returned', facts)
        return {'session': facts['session'], 'chain': state['chain'] + [invocation], 'next_node': 'checks'}

    def checks(state, config: RunnableConfig):
        validate(config)
        task = tasks[state['task_id']]
        returned = [facts for status, facts in history(task['id'], 'worker_invocation')
                    if status == 'returned' and facts.get('invocation_id') == state['chain'][-1]]
        if len(returned) != 1:
            raise Blocked('task worker result is missing or ambiguous; inspect retained invocation before checks')
        facts = returned[0]
        selected = facts['paths'] + facts['artifacts']
        if (git(project, 'rev-parse', 'HEAD').decode().strip() != facts['head'] or
                Engine._repair_source_state(project, selected) != facts['source_state'] or
                Engine._repair_index_state(project, selected) != facts['index_state']):
            raise Blocked('worker effects changed before checks; inspect Git and selected bytes before continuation')
        refs = []
        def retain(status, attempt):
            store.history(run, task['id'], 'check', status, attempt)
            if status == 'passed':
                refs.append(store.db.execute(
                    "SELECT seq FROM execution_history WHERE run_id=? AND task_id=? AND kind='check' AND state='passed' ORDER BY seq DESC LIMIT 1",
                    (run, task['id'])).fetchone()['seq'])
        try:
            results = run_checks(project, task, lock_fd=engine.authority.lock.fileno(), completed=retain)
        except CheckFailure as exc:
            previous = (read_record(task['id'], 'graph_correction', state['correction_id'])['failure']
                        if state.get('correction_id') else None)
            if exc.attempt == previous:
                raise Blocked('required check remains unchanged after scoped correction: ' + canonical(exc.attempt))
            correction_id = uuid.uuid4().hex
            record(task['id'], 'graph_correction', correction_id, {'failure': exc.attempt, 'effects': effects(task['id'])})
            return {'correction_id': correction_id, 'prompt_kind': 'correction',
                    'invocation_id': uuid.uuid4().hex, 'next_node': 'worker'}
        check_id = uuid.uuid4().hex
        record(task['id'], 'graph_checks', check_id, {'checks': results, 'check_refs': refs,
                                                       'effects': effects(task['id'])})
        return {'check_id': check_id, 'next_node': 'checkpoint'}

    def checkpoint(state, config: RunnableConfig):
        validate(config)
        task = tasks[state['task_id']]
        recovered = store.completed_checkpoints(run)
        if task['id'] in recovered:
            return {'next_node': 'ready'}
        checked = read_record(task['id'], 'graph_checks', state['check_id'])
        verify_effects(checked['effects'])
        returned = [facts for status, facts in history(task['id'], 'worker_invocation')
                    if status == 'returned' and facts.get('invocation_id') == state['chain'][-1]]
        if len(returned) != 1:
            raise Blocked('task worker result missing or ambiguous before checkpoint; inspect retained history')
        summary = returned[0]['summary']
        focused = focused_for(state)
        occurrence = uuid.uuid4().hex
        def intent(value):
            store.history(run, task['id'], 'checkpoint', 'started', {**value, 'check_refs': checked['check_refs'],
                'checks': checked['checks'], 'task_id': task['id'], 'checkpoint_occurrence_id': occurrence,
                'producer_invocation_id': state['chain'][-1], 'correction_chain': state['chain'], 'summary': summary})
        focused.before_checkpoint = intent
        focused.before_git_commit = lambda: store.history(run, task['id'], 'checkpoint', 'attempting', {'task_id': task['id']})
        try:
            result = focused.checkpoint()
        except BaseException as exc:
            result = focused.reconcile_checkpoint()
            if result is None:
                # A failed/uncertain Git attempt must be reconciled before any correction.
                uncertain = (isinstance(exc, (KeyboardInterrupt, SystemExit)) and
                             getattr(focused, 'git_commit_started', False))
                store.history(run, task['id'], 'checkpoint', 'failed', {'error': str(exc), 'no_effect': not uncertain})
                if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                    raise
                failure = {'checkpoint_error': str(exc)}
                previous = (read_record(task['id'], 'graph_correction', state['correction_id'])['failure']
                            if state.get('correction_id') else None)
                if failure == previous:
                    raise Blocked('checkpoint remains unchanged after scoped correction: ' + str(exc))
                correction_id = uuid.uuid4().hex
                record(task['id'], 'graph_correction', correction_id, {'failure': failure, 'effects': effects(task['id'])})
                return {'correction_id': correction_id, 'prompt_kind': 'correction',
                        'invocation_id': uuid.uuid4().hex, 'next_node': 'worker'}
        result['parent'] = None if result['no_change'] else git(project, 'rev-parse', result['sha'] + '^').decode().strip()
        result.update({'task_id': task['id'], 'checkpoint_occurrence_id': occurrence,
                       'producer_invocation_id': state['chain'][-1], 'correction_chain': state['chain']})
        store.history(run, task['id'], 'checkpoint', 'passed', result)
        store.task(run, task['id'], 'complete', state['baseline'], result['sha'],
                   {'summary': summary, 'checks': checked['checks'], 'paths': result['paths'],
                    'generated_artifacts': result['artifacts']})
        return {'next_node': 'ready'}

    builder = StateGraph(TaskState)
    for name, node in (('ready', ready), ('worker', worker), ('checks', checks), ('checkpoint', checkpoint)):
        builder.add_node(name, node)
    builder.add_edge(START, 'ready')
    builder.add_conditional_edges('ready', lambda state: state['next_node'], {'worker': 'worker', 'end': END})
    builder.add_edge('worker', 'checks')
    builder.add_conditional_edges('checks', lambda state: state['next_node'], {'worker': 'worker', 'checkpoint': 'checkpoint'})
    builder.add_conditional_edges('checkpoint', lambda state: state['next_node'], {'worker': 'worker', 'ready': 'ready'})
    return builder.compile(checkpointer=saver)
