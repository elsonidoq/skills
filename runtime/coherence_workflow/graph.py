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
from langgraph.types import Command, interrupt

from .engine import (Engine, _COMPLETION_REPORTING, _DECISION_CONSTRAINTS,
                     _IMPLEMENTATION_AUTHORITY, _ROUTINE_AUTHORITY)
from .git_effects import FocusedGit
from .pi_adapter import WaitingQuestion, effective_saved_session
from .store import Blocked, canonical, git
from .monitoring import Recorder
import hashlib
import re
from .git_effects import _commit_result
from .metric_artifacts import artifact_relative
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
    review_predecessor: str
    review_execution: str
    result: dict
    review_action: str
    pending_question: dict
    answer: str
    question_invocation: str
    recovery: dict


def task_graph(engine, saver, *, review=False):
    """Compile the internal sequential task boundary, optionally including review.

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
        remaining = [task for task in engine.contract['tasks'] if task['id'] not in complete]
        if not remaining:
            return {'checkpoints': complete, 'next_node': 'review_route' if review else 'end'}
        task = next((item for item in remaining if all(dep in complete for dep in item.get('depends', []))), None)
        if task is None:
            raise Blocked('no dependency-ready task; inspect task dependencies and retained checkpoints')
        baseline = git(project, 'rev-parse', 'HEAD').decode().strip()
        store.task(run, task['id'], 'running', baseline)
        manual_gates(task, engine.question)
        return {'task_id': task['id'], 'baseline': baseline, 'invocation_id': uuid.uuid4().hex,
                'chain': [], 'prompt_kind': 'initial', 'correction_id': '',
                'session': None, 'recovery': None, 'checkpoints': complete, 'next_node': 'worker'}

    def worker(state, config: RunnableConfig):
        validate(config)
        task = tasks[state['task_id']]
        invocation = state['invocation_id']
        events = [(status, facts) for status, facts in history(task['id'], 'worker_invocation')
                  if facts.get('invocation_id') == invocation]
        if events:
            status, facts = events[-1]
            if status == 'returned' and facts.get('waiting') is True:
                verify_effects(facts['effects'])
                return {'session': facts['session'], 'pending_question': facts['question'], 'next_node': 'wait'}
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
        recovery = state.get('recovery')
        profile = engine.implementation_fallback if recovery and recovery['action'] == 'escalate' else engine.executor
        adapter = engine.adapter(project, profile, question=engine.question)
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
        elif state['prompt_kind'] == 'correction':
            correction = read_record(task['id'], 'graph_correction', state['correction_id'])
            verify_effects(correction['effects'])
            body = ('A runner-owned required check or checkpoint failed. Inspect the actual failure and make a '
                    'reasoned scoped correction; do not skip checks or bypass hooks/signing. '
                    'The runner reruns required checks before checkpointing.\nActual failure: ' + canonical(correction['failure'])
                    + '\n' + _DECISION_CONSTRAINTS + engine.paid_authority() + '\nTask: ' + canonical(task))
        elif state['prompt_kind'] == 'recovery':
            prior = read_record(task['id'], 'graph_recovery', recovery['id'])
            verify_effects(prior['effects'])
            body = ('Continue only the unfinished same-task work; do not replay settled effects. '
                    'Apply the inspected targeted correction and preserve all original acceptance and gates.\n'
                    + 'Retained failure and diagnosis: ' + canonical(prior['reference'])
                    + '\n' + _DECISION_CONSTRAINTS + engine.paid_authority() + '\nTask: ' + canonical(task))
        if state.get('prompt_kind') == 'answer':
            settled = [facts for status, facts in history(task['id'], 'worker_invocation')
                       if status == 'returned' and facts.get('waiting') is True
                       and facts.get('invocation_id') == state['question_invocation']]
            if len(settled) != 1:
                raise Blocked('settled question evidence missing or ambiguous; inspect retained invocation')
            verify_effects(settled[0]['effects'])
            body = ('Continue the retained task and pending question. The prior call settled; do not repeat its effects. '
                    'The actual owner answer is data, not broader permission. Respect denial and all existing gates.\n'
                    + 'Pending question, actual answer and settled effects: ' + canonical({'invocation_id': state['question_invocation'],
                        'question': state['pending_question'], 'answer': state['answer'], 'effects': settled[0]['effects']})
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
        dispatch_recovery = ({key: recovery[key] for key in ('action', 'diagnosis', 'predecessor')}
                             if recovery and state['prompt_kind'] == 'recovery'
                             and recovery['action'] in ('fresh', 'escalate') else None)
        store.reserve_worker_dispatch(run, task['id'], invocation, session, recovery=dispatch_recovery)
        if dispatch_recovery and recovery['action'] == 'escalate':
            store.history(run, task['id'], 'implementation_escalation', 'started',
                          {**dispatch_recovery, 'executor': profile})
        store.history(run, task['id'], 'worker_invocation', 'started', {'invocation_id': invocation, 'session': session})
        try:
            result = engine._prompt_worker(adapter, prompt, claim=claim, command=command,
                                           cleanup=focused.cleanup_artifact, saved_session=session, reuse_key=reuse_key,
                                           pause_questions=True)
        except BaseException as exc:
            actual = getattr(adapter, 'opened_session', None) or getattr(adapter, 'saved_session', None)
            if actual is not None:
                store.bind_worker_dispatch(run, task['id'], invocation, actual)
            status = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
            store.history(run, task['id'], 'worker_invocation', status,
                          {'invocation_id': invocation, 'error': str(exc), 'session': actual,
                           'effects': effects(task['id'])})
            raise
        actual = getattr(adapter, 'opened_session', None) or getattr(adapter, 'saved_session', None)
        if actual is not None:
            store.bind_worker_dispatch(run, task['id'], invocation, actual)
        if isinstance(result, WaitingQuestion):
            facts = {'invocation_id': invocation, 'session': result.session, 'waiting': True,
                     'question': result.question, 'effects': effects(task['id'])}
            store.history(run, task['id'], 'worker_invocation', 'returned', facts)
            return {'session': result.session, 'pending_question': result.question, 'next_node': 'wait'}
        paths, artifacts = focused.facts()['paths'], focused.facts()['artifacts']
        selected = paths + artifacts
        facts = {'invocation_id': invocation, 'summary': result, 'session': getattr(adapter, 'saved_session', None),
                 'head': git(project, 'rev-parse', 'HEAD').decode().strip(), 'paths': paths, 'artifacts': artifacts,
                 'source_state': Engine._repair_source_state(project, selected),
                 'index_state': Engine._repair_index_state(project, selected)}
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
        verify_effects(facts[0]['effects'])
        return {'answer': answer['answer'], 'prompt_kind': 'answer',
                'question_invocation': state['invocation_id'],
                'invocation_id': uuid.uuid4().hex, 'next_node': 'worker'}

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
            if state.get('recovery') and state['recovery']['action'] == 'escalate':
                store.history(run, task['id'], 'implementation_escalation', 'failed', {'error': canonical(exc.attempt)})
                raise Blocked('implementation escalation required check failed; stop and notify the owner; owner direction required: ' + canonical(exc.attempt)) from exc
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
                if state.get('recovery') and state['recovery']['action'] == 'escalate':
                    store.history(run, task['id'], 'implementation_escalation', 'failed', {'error': str(exc)})
                    raise Blocked('implementation escalation failed; stop and notify the owner; owner direction required: ' + str(exc)) from exc
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
        if state.get('recovery') and state['recovery']['action'] == 'escalate':
            store.history(run, task['id'], 'implementation_escalation', 'completed', {'sha': result['sha']})
        return {'next_node': 'ready'}

    def escalation_guard(node):
        def guarded(state, config: RunnableConfig):
            try:
                return node(state, config)
            except BaseException as exc:
                if state.get('recovery') and state['recovery']['action'] == 'escalate':
                    events = history(state['task_id'], 'implementation_escalation')
                    if not events or events[-1][0] == 'started':
                        store.history(run, state['task_id'], 'implementation_escalation', 'failed', {'error': str(exc)})
                    raise Blocked('implementation escalation failed; stop and notify the owner; owner direction required: ' + str(exc)) from exc
                raise
        return guarded

    builder = StateGraph(TaskState)
    for name, node in (('ready', ready), ('worker', worker), ('wait', wait), ('checks', checks), ('checkpoint', checkpoint)):
        builder.add_node(name, escalation_guard(node) if name in ('worker', 'checks', 'checkpoint') else node)
    builder.add_edge(START, 'ready')
    ready_edges = {'worker': 'worker', 'end': END}
    if review:
        _add_review_nodes(builder, engine, validate)
        ready_edges['review_route'] = 'review_route'
    builder.add_conditional_edges('ready', lambda state: state['next_node'], ready_edges)
    builder.add_conditional_edges('worker', lambda state: state['next_node'], {'checks': 'checks', 'wait': 'wait'})
    builder.add_edge('wait', 'worker')
    builder.add_conditional_edges('checks', lambda state: state['next_node'], {'worker': 'worker', 'checkpoint': 'checkpoint'})
    builder.add_conditional_edges('checkpoint', lambda state: state['next_node'], {'worker': 'worker', 'ready': 'ready'})
    return builder.compile(checkpointer=saver)


def graph_recovery_action(engine, graph, config, action, *, diagnosis=None, transfer=None,
                          owner_authorized=False, scope=None):
    """Apply one inspected action to the retained graph, then continue its current thread.

    This is an internal interface; public routing remains with the cutover. A failed
    invocation is never replayed. Completed Git effects are reconciled first.
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
    if action == 'external':
        snapshot = graph.get_state(config)
        if (not isinstance(transfer, dict) or snapshot.values.get('task_id') != transfer.get('task_id')
                or snapshot.interrupts or not set(snapshot.next).intersection({'worker', 'checks', 'checkpoint'})):
            raise Blocked('external recovery needs the matching stopped task without a pending question; inspect the retained graph before continuation')
        engine.recover_task(transfer, owner_authorized=owner_authorized)
        _check_escalation_stop(store, run)
        graph.update_state(config, {'next_node': 'ready', 'recovery': None}, as_node='checkpoint')
        return graph.invoke(None, config, durability='sync')
    _check_escalation_stop(store, run)
    _check_unfinished_escalation(store, run)
    completed = store.completed_checkpoints(run)
    snapshot = graph.get_state(config)
    state = snapshot.values
    if action == 'authorize-routine-repairs':
        return store.authorize_routine_review_continuation(run, scope)
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
        graph.update_state(config, {'next_node': 'ready', 'recovery': None}, as_node='checkpoint')
        return graph.invoke(None, config, durability='sync')
    if snapshot.interrupts or tuple(snapshot.next) != ('worker',):
        raise Blocked('graph recovery needs the failed worker boundary; inspect the retained graph and pending effects')
    rows = list(store.db.execute("SELECT state,details FROM execution_history WHERE run_id=? AND task_id=? AND kind='worker_invocation' ORDER BY seq", (run, task_id)))
    if rows and rows[-1]['state'] == 'returned':
        returned = json.loads(rows[-1]['details'])
        if returned.get('invocation_id') == state.get('invocation_id'):
            return graph.invoke(None, config, durability='sync')
    if not rows or rows[-1]['state'] != 'failed':
        raise Blocked('graph recovery needs an inspected terminal worker failure; reconcile any live or settled call first')
    failure = json.loads(rows[-1]['details'])
    if 'effects are uncertain' in failure.get('error', ''):
        raise Blocked('worker settlement and effects are uncertain; inspect the saved operation before any continuation')
    predecessor = failure.get('invocation_id')
    if predecessor != state.get('invocation_id') or not isinstance(failure.get('effects'), dict):
        raise Blocked('graph recovery failure lacks exact invocation/effect evidence; inspect retained call before continuation')
    value = failure['effects']
    if (git(project, 'rev-parse', 'HEAD').decode().strip() != value['head'] or
            Engine._repair_source_state(project, value['paths']) != value['source_state'] or
            Engine._repair_index_state(project, value['paths']) != value['index_state']):
        raise Blocked('failed worker effects drifted; inspect selected Git and source state before continuation')
    escalations = list(store.db.execute("SELECT state FROM execution_history WHERE run_id=? AND task_id=? AND kind='implementation_escalation' ORDER BY seq", (run, task_id)))
    if escalations and escalations[-1]['state'] != 'completed':
        raise Blocked('implementation escalation is unresolved; stop and notify the owner; owner direction required')
    if action == 'continue' and not failure.get('session'):
        raise Blocked('continued recovery needs the exact saved session; inspect the failure or select justified fresh recovery')
    if action == 'escalate' and engine.implementation_fallback is None:
        raise Blocked('implementation escalation has no permitted fallback; configure it at launch')
    identity = uuid.uuid4().hex
    recovery = {'id': identity, 'action': action, 'diagnosis': diagnosis, 'predecessor': predecessor}
    reference = {'invocation_id': predecessor, 'error': failure.get('error'),
                 'saved_session_id': (failure.get('session') or {}).get('id'), 'targeted_correction': diagnosis}
    store.history(run, task_id, 'graph_recovery', 'recorded', {'id': identity, 'effects': value, 'reference': reference})
    chain = list(state.get('chain') or [])
    if predecessor not in chain:
        chain.append(predecessor)
    graph.update_state(config, {'prompt_kind': 'recovery', 'recovery': recovery, 'chain': chain,
                               'invocation_id': uuid.uuid4().hex,
                               'session': failure.get('session') if action == 'continue' else None,
                               'next_node': 'worker'}, as_node='ready')
    return graph.invoke(None, config, durability='sync')


def answer_graph_question(graph, config, question):
    """Present the retained question through a terminal or attached consumer.

    No input leaves the checkpoint paused. The invocation identity binds the reply
    to the precise settled call; private question/session data is not status output.
    """
    snapshot = graph.get_state(config)
    interrupts = snapshot.interrupts
    if len(interrupts) != 1:
        raise Blocked('no single pending graph question; inspect the retained graph before answering')
    pending = interrupts[0].value
    try:
        answer = question(pending['question']['question'])
    except (Blocked, EOFError):
        return None
    if not isinstance(answer, str) or not answer.strip():
        return None
    return graph.invoke(Command(resume={'invocation_id': pending['invocation_id'], 'answer': answer}),
                        config, durability='sync')


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
    recorder = Recorder(store, run)
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
                if not isinstance(head, str) or not head or git(project, 'rev-parse', 'HEAD').decode().strip() != head:
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
        if predecessor is None:
            if items:
                raise Blocked('review history changed before initial dispatch; inspect retained chain')
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
            engine._review(recorder=recorder, review_base=base(), head=head, ordinal=ordinal, fixing_round=round_,
                           trigger_execution_id=predecessor, predecessor_execution_id=predecessor,
                           input_checkpoints=inputs, execution_id=reviewer_id)
        except BaseException as exc:
            store.history(run, None, 'invocation', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed',
                          {'error': str(exc), 'result': head})
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
            if grant is None and store.routine_review_authority(run, scope):
                grant = store.authorize_owner_pair(run, uuid.uuid4().hex, rejecting_execution_id=rejection['execution_id'],
                    review_base=base(), review_head=head, original_scope=scope, fixer_execution_id=fixer, reviewer_execution_id=uuid.uuid4().hex)
            if grant is None:
                context = {'rejecting_execution': rejection['execution_id'], 'review_base': base(), 'review_head': head, 'scope': scope,
                           'effect': 'Authorize exactly one scoped repair and one fresh cumulative repair review; no repeat grant.'}
                try:
                    answer = engine.question('Authorize exactly one scoped repair and fresh cumulative review for ' + canonical(context) + '? [yes/no]',
                                             owner_only=True, decision_context=context)
                except BaseException as exc:
                    store.history(run, None, 'review_pair_decision', 'unavailable', context)
                    raise Blocked('owner authorization unavailable; no repair/review pair dispatched: ' + str(exc)) from exc
                if not isinstance(answer, str) or answer.strip().lower() not in ('yes', 'y'):
                    store.history(run, None, 'review_pair_decision', 'denied', context)
                    raise Blocked('owner did not authorize an additional repair/review pair; blockers retained')
                grant = store.authorize_owner_pair(run, uuid.uuid4().hex, rejecting_execution_id=rejection['execution_id'],
                    review_base=base(), review_head=head, original_scope=scope, fixer_execution_id=fixer, reviewer_execution_id=uuid.uuid4().hex)
            if git(project, 'rev-parse', 'HEAD').decode().strip() != grant['review_head']:
                raise Blocked('review target drifted after owner authorization; inspect and renew affected authority before dispatch')
            fixer = store.reserve_owner_pair_fixer(run, grant['grant_id'], rejecting_execution_id=rejection['execution_id'],
                                                   review_base=base(), review_head=head, original_scope=scope)['fixer_execution_id']
            if any(item['execution_id'] == fixer for item in items):
                return {'next_node': 'review_route'}
        engine.run_fix(value(rejection)['findings'], trigger_execution_id=rejection['execution_id'], review_base=base(),
                       recorder=recorder, execution_id=fixer, review_ordinal=rejection['review_ordinal'],
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
                           recorder=recorder, execution_id=item['execution_id'], review_ordinal=item['review_ordinal'],
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
            diagnosis = engine.question('Inspect the retained evidence-only rejection and provide a targeted diagnosis for its outstanding gaps, or leave empty only when retained evidence changed: ' + canonical(value(last)))
            authorized = store.authorize_evidence_reassessment(run, uuid.uuid4().hex, rejecting_execution_id=last['execution_id'],
                review_base=base(), review_head=head, diagnosis=diagnosis if isinstance(diagnosis, str) else '', evidence_digest=digest)
        if any(item['execution_id'] == authorized['execution_id'] for item in items):
            return {'next_node': 'review_route'}
        _, result, status = engine._review(recorder=recorder, review_base=base(), head=head,
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
        engine._review(recorder=recorder, review_base=base(), head=head, ordinal=0,
                       execution_id=state['review_execution'], refresh_target=True)
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
        engine._review(recorder=recorder, review_base=base(), head=head, ordinal=last['review_ordinal'],
            fixing_round=last['fixing_round'], trigger_execution_id=last['trigger_execution_id'],
            predecessor_execution_id=last['predecessor_execution_id'], input_checkpoints=last.get('input_checkpoints'),
            execution_id=last['execution_id'], retry_limit=int(match.group(1)))
        return {'next_node': 'review_route'}

    for name, node in (('review_route', route), ('review_dispatch', review_dispatch), ('review_repair', repair),
                       ('review_recover_repair', recover_repair), ('review_evidence', evidence),
                       ('review_payload', payload_recovery), ('review_refresh', refresh)):
        builder.add_node(name, node)
    builder.add_conditional_edges('review_route', lambda state: state['next_node'], {
        'review_dispatch': 'review_dispatch', 'review_repair': 'review_repair',
        'review_recover_repair': 'review_recover_repair', 'review_evidence': 'review_evidence',
        'review_payload': 'review_payload', 'review_refresh': 'review_refresh', 'end': END})
    for name in ('review_dispatch', 'review_repair', 'review_recover_repair', 'review_evidence', 'review_payload', 'review_refresh'):
        builder.add_edge(name, 'review_route')
