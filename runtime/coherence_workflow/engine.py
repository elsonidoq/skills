"""Sequential task/check/Git execution, with one fresh read-only final reviewer."""
import hashlib
import inspect
import json
import math
import os
import re
import uuid

from .git_effects import FocusedGit, MetricArtifactFinalizer, path_has_preexisting_changes
from .metric_artifacts import (MetricArtifactError, artifact_relative, create_artifact,
                               read_artifact, summarize_artifact)
from .metrics import interval_record
from .monitoring import Recorder, descriptor
from .pi_adapter import PiAdapter, terminal_question
from .processes import process_identity
from .sessions import select_session
from .store import Blocked, canonical, git, safe_path
from .verification import CheckFailure, commands, manual_gates, run_checks


class _ReviewFormat(Blocked):
    """An actual reviewer response could not safely yield a verdict."""


def _failure(exc):
    if isinstance(exc, (KeyboardInterrupt, SystemExit)): return 'interrupted'
    return 'transport' if isinstance(exc, Blocked) else 'unknown'


def usage_summary(project, run, expected_invocation_ids=()):
    """Project JSONL-only totals; unknown fields never become zero."""
    summary = summarize_artifact(project, run, expected_invocation_ids=expected_invocation_ids)
    fields = {'input': ('tokens', 'input'), 'output': ('tokens', 'output'),
              'cache_read': ('tokens', 'cache_read'), 'cache_write': ('tokens', 'cache_write'),
              'total_tokens': ('total_tokens',), 'estimated_usd': ('estimated_usd',)}
    expected = set(expected_invocation_ids)
    def totals(rows):
        # These are explicitly known subtotals when run coverage is partial;
        # an empty surviving group is unavailable, never a complete numeric zero.
        values, complete = {key: 0 for key in fields}, {key: bool(rows) or not expected for key in fields}
        for row in rows:
            for key, path in fields.items():
                value = row['interval']
                for part in path:
                    value = value.get(part) if isinstance(value, dict) else None
                value = value.get('value') if isinstance(value, dict) else None
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    values[key] += value
                else:
                    complete[key] = False
        return {key: values[key] if complete[key] else None for key in fields}
    rows = summary['records']
    worker_rows, reviewer_rows = ([row for row in rows if row['role'] != 'reviewer'],
                                  [row for row in rows if row['role'] == 'reviewer'])
    partial = summary['coverage'] != 'complete'
    return {**summary, 'memberships': sorted({row['task_id'] for row in rows if row['task_id'] is not None}),
            'worker_totals': totals(worker_rows), 'reviewer_totals': totals(reviewer_rows),
            'worker_totals_qualification': 'known_subtotal' if partial and worker_rows else ('unavailable' if not worker_rows and expected else 'complete'),
            'reviewer_totals_qualification': 'known_subtotal' if partial and reviewer_rows else ('unavailable' if not reviewer_rows and expected else 'complete')}


_DECISION_CONSTRAINTS = (
    'Discover the canonical save-adr decision contract from the configured/installed suite and project routing, '
    'or use supplied relevant accepted constraints. Do not ignore known accepted constraints because the contract '
    'is unavailable; report the affected evidence gap without blocking unrelated legacy work. '
)

_IMPLEMENTATION_AUTHORITY = (
    'Current execution authority: this owner-authorized workflow launch approves implementation '
    'of the assigned task within its stated scope. Historical planning-only or awaiting-implementation-approval '
    'wording in source/task artifacts is superseded for that scope, not a current prohibition. '
    'Preserve task requirements, acceptance criteria, explicit manual gates and all safety/permission '
    'boundaries; ask the owner if a material authority conflict remains.\n'
)

# Shared worker permission defaults. Edit here, not in individual task/correction prompts.
_ROUTINE_AUTHORITY = (
    'Routine authority: make ordinary scoped technical fixes; run isolated tests and local servers; perform necessary '
    'local/in-project dependency setup; and generate, rebuild, or selectively clean up current-task artifacts without '
    'an owner question. Small isolated tests and local test databases are allowed for any task; keep test data and '
    'execution bounded so they do not risk exhausting the machine\'s resources or affecting unrelated data/services. '
    'Do not ask merely because files changed. This authority is not proof that checks succeeded. '
    'A separately supplied paid scope applies only as supplied and is never inferred from credentials or task text. '
    'Ask only for product decisions, substantial planned-complexity increases, separately scoped paid usage, or actions '
    'outside this authority. It never authorizes global installs, credential changes, deployment, pushing, or deletion '
    'of unrelated or pre-existing work. '
)


class Engine:
    def __init__(self, authority, run, contract, executor, *, adapter=PiAdapter, question=terminal_question, paid_scope=None, resume=False):
        self.authority, self.run, self.contract, self.resume = authority, run, contract, resume
        self.input_executor = executor
        self.executor = {key: value for key, value in executor.items() if key != 'reviewer'}
        self.reviewer_executor = executor.get('reviewer')
        if not isinstance(self.reviewer_executor, dict) or any(
            not isinstance(self.reviewer_executor.get(key), str) or not self.reviewer_executor[key]
            for key in ('provider', 'model', 'effort')
        ):
            raise Blocked('reviewer needs provider, model and effort strings; correct the reviewer profile in --executor JSON')
        self.adapter, self.question, self.paid_scope = adapter, question, paid_scope
        # Private, run-local facts only. A failed or unfinished worker is never added.
        self.session_candidates = []
        self.session_settlement_sequence = 0
        self.metric_artifact = None
        self.metric_invocation_ids = []

    @staticmethod
    def _snapshot(observation):
        """Project only the closed metric snapshot vocabulary."""
        if not isinstance(observation, dict):
            return None
        def number(value):
            return value if (isinstance(value, (int, float)) and not isinstance(value, bool)
                             and math.isfinite(value) and value >= 0) else None
        def boolean(value):
            return value if type(value) is bool else None
        counters = observation.get('counters') if isinstance(observation.get('counters'), dict) else {}
        headroom = observation.get('headroom') if isinstance(observation.get('headroom'), dict) else {}
        entries = observation.get('compaction_entries') if isinstance(observation.get('compaction_entries'), list) else []
        return {'counters': {name: number(counters.get(name)) for name in ('input', 'output', 'cacheRead', 'cacheWrite', 'total')},
                'estimated_usd': number((observation.get('costs') or {}).get('estimated_usd')),
                'context': {name: (boolean(headroom.get(name)) if name in ('compaction_enabled', 'compaction_applicable')
                                    else number(headroom.get(name)))
                            for name in ('context_window', 'effective_reserve', 'occupancy',
                                         'compaction_enabled', 'compaction_applicable')},
                'compaction_entry_ids': sorted(entry['id'] for entry in entries
                                                if isinstance(entry, dict) and isinstance(entry.get('id'), str) and entry['id'])}

    @staticmethod
    def _selected_session(selection, *, continued=False):
        if continued:
            return 'continued_same_task', selection.get('reason')
        return ('reused_from_earlier_task' if selection.get('session_id') else 'fresh', selection.get('reason'))

    def _append_metric(self, worker, *, invocation_id, task_id, role, outcome, selection, continued=False,
                       expected_session_id=None, fixing_round=None, review_ordinal=None):
        """Best-effort terminal-call JSONL; never changes the execution result."""
        self.metric_invocation_ids.append(invocation_id)
        selected_mode, reason = self._selected_session(selection, continued=continued)
        observation = getattr(worker, 'last_observation', None)
        before = observation.get('before') if isinstance(observation, dict) else None
        after = observation.get('after') if isinstance(observation, dict) else None
        interval = interval_record(before, after, outcome=outcome)
        if not isinstance(before, dict) and not isinstance(after, dict):
            # Offline adapters may provide the already-derived closed interval only.
            interval = getattr(worker, 'last_interval', None) or interval
        opened = getattr(worker, 'opened_session', None)
        actual_id = opened.get('id') if isinstance(opened, dict) and isinstance(opened.get('id'), str) else None
        expected = expected_session_id if continued else selection.get('session_id')
        actual_mode = (selected_mode if actual_id is not None and
                       ((selected_mode == 'fresh' and expected is None) or
                        (selected_mode != 'fresh' and actual_id == expected)) else 'unknown')
        record = {'version': 1, 'run_id': self.run, 'invocation_id': invocation_id, 'task_id': task_id,
                  'role': role, 'outcome': outcome, 'fixing_round': fixing_round,
                  'review_ordinal': review_ordinal, 'interval': interval,
                  'before': self._snapshot(before), 'after': self._snapshot(after),
                  'selected_session_mode': selected_mode, 'session_selection_reason': reason,
                  'actual_session_mode': actual_mode, 'actual_session_id': actual_id}
        try:
            if self.metric_artifact is None:
                self.metric_artifact = create_artifact(self.authority.project, self.run, authority=self.authority)
            self.metric_artifact.append(record)
        except (MetricArtifactError, OSError, ValueError):
            pass

    def usage_summary(self):
        return usage_summary(self.authority.project, self.run, self.metric_invocation_ids)

    def _finalize_metric_artifact(self, result=None):
        """Commit only this run's closed JSONL after every worker/reviewer call drained."""
        artifact = {'status': 'not_created'}
        if self.metric_artifact is not None:
            finalizer = None
            try:
                finalizer = MetricArtifactFinalizer(
                    self.authority.project, artifact_relative(self.run),
                    lambda: read_artifact(self.authority.project, self.run, strict=True),
                    expected_identity=self.metric_artifact.identity,
                    expected_bytes=self.metric_artifact.path.read_bytes())
                committed = finalizer.commit()
            except BaseException as exc:
                # A hook may have committed before reporting failure. Inspect once, never retry.
                try:
                    committed = finalizer.reconcile() if finalizer is not None else None
                except BaseException as reconcile_error:
                    committed = None
                    exc = reconcile_error
                if committed is None:
                    artifact = {'status': 'failed', 'path': artifact_relative(self.run),
                                'error': str(exc) or type(exc).__name__}
                else:
                    artifact = {'status': 'committed_after_reported_error', **committed}
            else:
                artifact = {'status': 'committed' if not committed['no_change'] else 'no_content', **committed}
        try:
            self.authority.store.history(self.run, None, 'metric_artifact', artifact['status'], artifact)
        except BaseException:
            # Metric reporting remains optional and must not replace the original result.
            pass
        if result is not None:
            return {**result, 'metric_artifact': artifact}
        return artifact

    def _session_request(self, task, role='worker'):
        authority = canonical({'paid_scope': self.paid_scope, 'routine_authority': True,
                               'task_authority': task.get('authority')})
        request = {
            'run_id': self.run, 'role': role, 'context_group': task.get('context_group'),
            'worktree': str(self.authority.project), 'executor': self.executor,
            'resources': task.get('resources', {'tools': 'worker'}),
            'instructions': 'worker-routine-authority-v1',
            'settings': task.get('settings', {}), 'authority': authority,
            'fresh_only': task.get('fresh_only') is True,
        }
        return request, canonical({key: request[key] for key in (
            'role', 'worktree', 'executor', 'resources', 'instructions', 'settings', 'authority')})

    @staticmethod
    def _prompt_worker(worker, prompt, **kwargs):
        """Keep older offline adapters usable while the real adapter gets reuse facts."""
        parameters = inspect.signature(worker.prompt).parameters.values()
        accepts_keywords = any(parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in parameters)
        if not accepts_keywords:
            names = {parameter.name for parameter in parameters}
            kwargs = {key: value for key, value in kwargs.items() if key in names}
        return worker.prompt(prompt, **kwargs)

    @staticmethod
    def _headroom(observation):
        if not isinstance(observation, dict):
            return None
        headroom = observation.get('headroom')
        return headroom if isinstance(headroom, dict) else None

    def _settle_session(self, task, worker, request, reuse_key, checkpoint):
        session = getattr(worker, 'saved_session', None)
        observation = getattr(worker, 'last_observation', None)
        after = observation.get('after') if isinstance(observation, dict) else None
        headroom = self._headroom(after)
        if not isinstance(session, dict) or not isinstance(session.get('id'), str) or not headroom:
            self.authority.store.history(self.run, task['id'], 'session', 'unavailable',
                                         {'reason': 'missing_saved_identity_or_headroom'})
            return
        self.session_settlement_sequence += 1
        candidate = {**request, 'id': session['id'], 'saved_session': session,
                     'settled': True, 'idle': True, 'checkpoint_verified': True,
                     'settled_at': self.session_settlement_sequence, 'headroom': headroom,
                     'checkpoint_sha': checkpoint['sha'], 'reuse_key': reuse_key}
        self.session_candidates[:] = [item for item in self.session_candidates if item['id'] != session['id']]
        self.session_candidates.append(candidate)
        self.authority.store.history(self.run, task['id'], 'session', 'settled',
                                     {'session_id': session['id'], 'checkpoint_sha': checkpoint['sha']})

    def paid_authority(self):
        if self.paid_scope is None:
            return 'Paid scope: not supplied to this direct engine fixture; production CLI settles it before provider launch. '
        return ('Selected worker/reviewer models are authorized by the implementation launch. '
                'Paid application/test APIs approved for this unchanged run only: ' +
                (', '.join(self.paid_scope['apis']) if self.paid_scope['apis'] else 'none declared') +
                '. Ask before using any additional paid application/test API, including one discovered '
                'during execution; do not ask again for unchanged scope. ')

    @staticmethod
    def _repair_blobs(project, paths):
        """Capture only already selected repair paths, never discover ownership."""
        return {name: (git(project, 'hash-object', '--path=' + name, '--', name).decode().strip()
                       if safe_path(project, name).exists() else None) for name in paths}

    def run_fix(self, findings, *, trigger_execution_id, review_base, recorder, execution_id,
                review_ordinal=1, fixing_round=1, predecessor_execution_id=None, terminal_stop=None,
                recovered=None):
        """Run one already-authorized repair assignment without selecting another round.

        The caller supplies the rejecting review, assigned fixer identity, and (where
        applicable) its retained round. This primitive deliberately leaves original task
        rows/checkpoints alone: it records a distinct fixer execution, its scoped checks,
        and its focused repair checkpoint. Lifecycle/grant selection remains its caller.
        """
        if (not isinstance(findings, list) or not findings or any(not isinstance(item, str) or not item for item in findings)
                or not isinstance(trigger_execution_id, str) or not trigger_execution_id
                or not isinstance(execution_id, str) or not execution_id
                or not isinstance(review_ordinal, int) or review_ordinal < 1
                or not isinstance(fixing_round, int) or fixing_round < 1):
            raise Blocked('fixing execution needs actionable findings, explicit execution IDs, and positive assigned rounds')
        predecessor_execution_id = predecessor_execution_id or trigger_execution_id
        if not isinstance(predecessor_execution_id, str) or not predecessor_execution_id:
            raise Blocked('fixing execution needs an explicit predecessor execution ID')
        project, store = self.authority.project, self.authority.store
        original_tasks = self.contract['tasks']
        paths = []
        artifacts = []
        checks = []
        gates = []
        for task in original_tasks:
            paths.extend(task.get('owned_paths', []))
            artifacts.extend(task.get('generated_outputs', []))
            checks.extend(commands(task))
            gates.extend(task.get('gates', []))
        fix_task = {'id': 'fix-' + execution_id, 'description': 'Correct actionable independent review findings.',
                    'checks': checks, 'gates': gates, 'generated_outputs': sorted(set(artifacts)),
                    'context_group': 'review-fix'}
        if any('owned_paths' in task for task in original_tasks):
            fix_task['owned_paths'] = sorted(set(paths))
        head = git(project, 'rev-parse', 'HEAD').decode().strip()
        if recovered is None:
            store.review_dispatch(self.run, execution_id, role='fixer', review_ordinal=review_ordinal, fixing_round=fixing_round,
                                  trigger_execution_id=trigger_execution_id, predecessor_execution_id=predecessor_execution_id,
                                  review_base=review_base, review_head=head)
        focused = FocusedGit(project, fix_task, resume_facts=(recovered or {}).get('facts'))
        if recovered and recovered.get('baseline'):
            focused.base = recovered['baseline']
        claimed_paths = set()
        def claim(name):
            if name not in claimed_paths:
                focused.claim(name)
                claimed_paths.add(name)
        def gate_question(text):
            return self.question(text)
        try:
            if not recovered or not recovered.get('returned'):
                manual_gates(fix_task, gate_question)
            # Continue the actual reviewer, not a task-worker context. On process
            # restart the private review outcome supplies the same SDK session.
            worker = getattr(self, '_review_workers', {}).get(trigger_execution_id)
            review = next((item for item in store.review_chain(self.run, private=True)['executions']
                           if item['execution_id'] == trigger_execution_id), None)
            saved = review['references'].get('saved_session') if review else None
            if worker is None:
                worker = self.adapter(project, self.reviewer_executor, question=self.question)
                worker.saved_session = saved
            worker.lock_fd = self.authority.lock.fileno()
            saved = getattr(worker, 'saved_session', None)
            reuse_key = None
            selection = {'session_id': saved.get('id') if saved else None,
                         'reason': 'reviewer_repair' if saved else 'legacy_reviewer_repair_fresh', 'rejected': []}
            store.history(self.run, None, 'fixer', 'selected', {'execution_id': execution_id,
                          'trigger_execution_id': trigger_execution_id, **selection})
            fixer_chain = list((recovered or {}).get('invocations', []))
            last_fixer_invocation = [fixer_chain[-1] if fixer_chain else None]
            repair_context = (
                'Stay within the original approved task contracts and explicit owned paths. First make a concise '
                'correction plan; examine directly related adverse failure paths and the integrated result against '
                'the original acceptance, then make only bounded fixes. This assigned repair is not independent '
                'acceptance, a new task, routing operation, or permission expansion. Material scope, complexity, '
                'verification, or permission expansion must stop for the owner; do not speculate or rewrite broadly. '
                'The runner owns required/manual checks and the focused checkpoint: never stage or commit, bypass '
                'checks/hooks/signing, or adopt unrelated/pre-existing bytes.\n'
                + _DECISION_CONSTRAINTS + self.paid_authority() + '\nOriginal task contracts: '
                + canonical(original_tasks) + '\n')
            def prompt_fix(prompt, **kwargs):
                prompt = _IMPLEMENTATION_AUTHORITY + _ROUTINE_AUTHORITY + '\n' + repair_context + prompt
                invocation_id = uuid.uuid4().hex
                predecessor = last_fixer_invocation[0]
                chain = [*fixer_chain, invocation_id]
                occurrence = recorder.occurrence()
                public = {
                    'role': 'fixing_worker', 'execution_id': execution_id, 'invocation_id': invocation_id,
                    'invocation_kind': 'corrective_worker' if predecessor else 'task_worker',
                    'selected_input_checkpoints': [], 'correction_chain': chain, 'fixing_round': fixing_round,
                    'trigger_execution_id': trigger_execution_id, 'predecessor_execution_id': predecessor_execution_id,
                }
                if predecessor:
                    public['predecessor_invocation_id'] = predecessor
                store.history(self.run, fix_task['id'], 'fixer_invocation', 'started',
                              {'invocation_id': invocation_id, 'execution_id': execution_id})
                recorder.emit(occurrence, 'worker', 'started', task_id=fix_task['id'], facts=public)
                outcome = 'settled'
                expected_session_id = (getattr(worker, 'saved_session', {}) or {}).get('id')
                # Do not attribute the previous prompt's observations to a failed call.
                worker.last_interval = None
                worker.last_observation = None
                worker.opened_session = None
                steering = {'run_id': self.run, 'task_id': fix_task['id'], 'invocation_id': invocation_id,
                            'role': 'fixer'}
                if getattr(worker, 'parent_steering_available', lambda: False)():
                    worker.enable_parent_steering(steering)
                    kwargs['steering'] = steering
                session = getattr(worker, 'saved_session', None)
                if session and session.get('compatibility', {}).get('readOnly') is True:
                    kwargs['review_repair'] = True
                try:
                    result = self._prompt_worker(worker, prompt, **kwargs)
                except BaseException as exc:
                    outcome = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                    if terminal_stop is not None:
                        terminal_stop[0] = invocation_id
                    store.history(self.run, fix_task['id'], 'fixer_invocation', outcome,
                                  {'invocation_id': invocation_id, 'execution_id': execution_id})
                    recorder.emit(occurrence, 'worker', outcome, task_id=fix_task['id'], facts={
                        **public, 'stopped_by_invocation_id': invocation_id, 'error_category': _failure(exc)})
                    raise
                else:
                    store.history(self.run, fix_task['id'], 'fixer_invocation', 'returned',
                                  {'invocation_id': invocation_id, 'execution_id': execution_id,
                                   'baseline': focused.base, 'head': git(project, 'rev-parse', 'HEAD').decode().strip(),
                                   **focused.facts(), 'blobs': self._repair_blobs(project, focused.task_edited)})
                    recorder.emit(occurrence, 'worker', 'returned', task_id=fix_task['id'], facts=public)
                    fixer_chain[:] = chain
                    last_fixer_invocation[0] = invocation_id
                    return result
                finally:
                    self._append_metric(worker, invocation_id=invocation_id, task_id=fix_task['id'],
                                        role='fixing_worker', outcome=outcome, selection=selection,
                                        continued=predecessor is not None, expected_session_id=expected_session_id,
                                        fixing_round=fixing_round)
            prompt = ('Continue the rejecting review in this assigned repair round. Keep the configured reviewer '
                      'executor and its scoped writer transition.\nActionable findings: ' + canonical(findings))
            text = '' if recovered and recovered.get('returned') else prompt_fix(
                prompt, claim=claim, command=focused.command, cleanup=focused.cleanup_artifact,
                saved_session=saved, reuse_key=reuse_key)
            check_occurrences = {}
            def observe(kind, ordinal, code):
                occurrence = check_occurrences.setdefault(ordinal, recorder.occurrence())
                facts = {'ordinal': ordinal, 'execution_id': execution_id}
                if code is not None:
                    facts['exit_code'] = code
                recorder.emit(occurrence, 'check', kind, task_id=fix_task['id'], facts=facts)
            def correct_checks():
                nonlocal text
                previous = None
                while True:
                    try:
                        store.history(self.run, None, 'fixer_checks', 'started', {'execution_id': execution_id})
                        results = run_checks(project, fix_task, lock_fd=self.authority.lock.fileno(), observe=observe,
                            completed=lambda state, attempt: store.history(self.run, None, 'fixer_check', state,
                                {'execution_id': execution_id, **attempt}))
                        store.history(self.run, None, 'fixer_checks', 'passed', {
                            'execution_id': execution_id, 'head': git(project, 'rev-parse', 'HEAD').decode().strip(),
                            'blobs': self._repair_blobs(project, focused.task_edited)})
                        return results
                    except CheckFailure as failure:
                        if failure.attempt == previous:
                            raise Blocked('fixing required check remains unchanged after scoped correction: ' + canonical(failure.attempt))
                        previous = failure.attempt
                        text = prompt_fix(
                            'A runner-owned REQUIRED check in this assigned fixing round failed. Make a reasoned, '
                            'authorized scoped correction, then return; the runner will rerun the affected command '
                            'before checkpointing. Do not skip it, claim success, start another fixing round, or adopt '
                            'unrelated work. Actual failed attempt: ' + canonical(failure.attempt),
                            claim=claim, command=focused.command, cleanup=focused.cleanup_artifact, reuse_key=reuse_key)
            check_results = correct_checks()
            checkpoint_error = None
            while True:
                checkpoint_occurrence = recorder.occurrence()
                recorder.emit(checkpoint_occurrence, 'checkpoint', 'started', task_id=fix_task['id'], facts={
                    'baseline': focused.base, 'execution_id': execution_id})
                try:
                    selected = sorted(name for name in focused.task_edited if path_has_preexisting_changes(project, name))
                    blobs = self._repair_blobs(project, selected)
                    store.history(self.run, None, 'fixer_checkpoint', 'started', {
                        'execution_id': execution_id, 'baseline': focused.base,
                        'parent': git(project, 'rev-parse', 'HEAD').decode().strip(),
                        'paths': selected, 'artifacts': sorted(focused.known_artifacts), 'blobs': blobs})
                    checkpoint = focused.checkpoint()
                except BaseException as exc:
                    store.history(self.run, None, 'fixer_checkpoint', 'failed',
                                  {'execution_id': execution_id, 'error': str(exc)})
                    recorder.emit(checkpoint_occurrence, 'checkpoint', 'failed', task_id=fix_task['id'], facts={
                        'baseline': focused.base, 'execution_id': execution_id, 'error_category': _failure(exc)})
                    checkpoint = focused.reconcile_checkpoint()
                    if checkpoint is not None:
                        break
                    if isinstance(exc, (KeyboardInterrupt, SystemExit)) or str(exc) == checkpoint_error:
                        raise
                    checkpoint_error = str(exc)
                    text = prompt_fix(
                        'A runner-owned focused repair checkpoint failed. Make a reasoned authorized scoped correction; '
                        'do not bypass hooks/signing or adopt unrelated work. The runner will rerun affected required '
                        'checks and checkpoint. Actual checkpoint error: ' + str(exc),
                        claim=claim, command=focused.command, cleanup=focused.cleanup_artifact, reuse_key=reuse_key)
                    check_results = correct_checks()
                    continue
                break
            checkpoint['parent'] = (None if checkpoint['no_change'] else
                                    git(project, 'rev-parse', checkpoint['sha'] + '^').decode().strip())
            store.history(self.run, None, 'fixer_checkpoint', 'passed', {'execution_id': execution_id, **checkpoint})
            checkpoint_facts = {'baseline': focused.base, 'head': checkpoint['sha'], 'no_change': checkpoint['no_change'],
                                'execution_id': execution_id}
            if last_fixer_invocation[0] is not None:
                checkpoint_facts.update({'producer_invocation_id': last_fixer_invocation[0],
                                         'correction_chain': list(fixer_chain)})
            recorder.emit(checkpoint_occurrence, 'checkpoint', 'passed', task_id=fix_task['id'], facts=checkpoint_facts)
            head = git(project, 'rev-parse', 'HEAD').decode().strip()
            store.review_outcome(self.run, execution_id, 'approved', findings=[],
                                 references={'base': review_base, 'head': head, 'commit': checkpoint['sha']})
            return {'execution_id': execution_id, 'checkpoint': checkpoint, 'checks': check_results, 'summary': text}
        except BaseException as exc:
            outcome = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
            store.review_outcome(self.run, execution_id, outcome, findings=[], uncertainty=False,
                                 references={'base': review_base, 'head': git(project, 'rev-parse', 'HEAD').decode().strip()})
            raise

    def _recover_assigned_fix(self, item, review_base):
        """Reconcile only an additional reserved repair, never replay a paid call."""
        project, store = self.authority.project, self.authority.store
        execution_id = item['execution_id']
        trigger = next((entry for entry in store.review_chain(self.run, private=True)['executions']
                        if entry['execution_id'] == item['trigger_execution_id']), None)
        grant = store.owner_pair_for_rejection(self.run, rejecting_execution_id=item['trigger_execution_id'],
            review_base=review_base, review_head=trigger['references'].get('head') if trigger else None,
            original_scope=store.review_scope(self.run))
        if grant is None or grant['fixer_execution_id'] != execution_id or grant['state'] != 'fixer_reserved':
            raise Blocked('retained repair lacks its exact consumed owner grant; inspect authorization before continuation')
        events = []
        for row in store.db.execute('SELECT kind,state,details FROM execution_history WHERE run_id=? ORDER BY seq', (self.run,)):
            facts = json.loads(row['details'])
            if facts.get('execution_id') == execution_id:
                events.append((row['kind'], row['state'], facts))
        calls = {}
        for kind, state, facts in events:
            if kind == 'fixer_invocation':
                calls[facts['invocation_id']] = (state, facts)
        if any(state != 'returned' for state, _ in calls.values()):
            raise Blocked('assigned repair invocation is uncertain or failed; inspect its recorded cause before targeted continuation')
        head = git(project, 'rev-parse', 'HEAD').decode().strip()
        if not calls:
            if head != item['references'].get('head'):
                raise Blocked('reserved repair target drifted; inspect affected continuation before dispatch')
            return {}
        returned = list(calls.values())[-1][1]
        if not all(key in returned for key in ('paths', 'artifacts', 'baseline', 'head', 'blobs')):
            raise Blocked('returned repair is missing owned-path/effect facts; inspect it without replaying the fixer')
        limits = [path for task in self.contract['tasks'] for path in task.get('owned_paths', [])]
        if any('owned_paths' in task for task in self.contract['tasks']):
            if any(not any(name == path.rstrip('/') or name.startswith(path.rstrip('/') + '/') for path in limits)
                   for name in returned['paths']):
                raise Blocked('retained repair paths exceed original scope; inspect ownership before continuation')
        recovered = {'returned': True, 'baseline': returned['baseline'], 'invocations': list(calls),
                     'facts': {'paths': returned['paths'], 'artifacts': returned['artifacts']}}
        checkpoints = [(state, facts) for kind, state, facts in events if kind == 'fixer_checkpoint']
        check_events = [(state, facts) for kind, state, facts in events if kind == 'fixer_checks']
        checks = [state for state, _ in check_events]
        if checkpoints:
            state, checkpoint = checkpoints[-1]
            if state not in ('passed', 'started') or not checks or checks[-1] != 'passed':
                raise Blocked('repair checks/checkpoint are incomplete or failed; inspect actual effects before targeted continuation')
            if state == 'passed':
                if head != checkpoint['sha'] or not set(checkpoint['paths']) <= set(returned['paths']):
                    raise Blocked('retained repair checkpoint target/paths drifted; inspect the exact SHA and ownership')
                focused = FocusedGit(project, {}, resume_facts=recovered['facts'])
                focused.base = checkpoint['baseline']
                if checkpoint['no_change']:
                    if head != checkpoint['baseline']:
                        raise Blocked('no-change repair checkpoint drifted; inspect retained head')
                else:
                    focused._checkpoint_result(head, checkpoint['parent'], checkpoint['paths'])
            else:
                if not set(checkpoint['paths']) <= set(returned['paths']):
                    raise Blocked('repair checkpoint paths do not match returned ownership; inspect retained effects')
                if head == checkpoint['parent']:
                    # Ownership will restore every returned path, including paths that
                    # were unchanged and therefore absent from the checkpoint selection.
                    effects = check_events[-1][1]
                    if (effects.get('head') != head or
                            self._repair_blobs(project, returned['paths']) != effects.get('blobs')):
                        raise Blocked('repair checkpoint source bytes drifted; preserve them and inspect ownership before continuation')
                    if self._repair_blobs(project, checkpoint['paths']) != checkpoint.get('blobs'):
                        raise Blocked('repair checkpoint source bytes drifted; preserve them and inspect ownership before continuation')
                    return recovered
                focused = FocusedGit(project, {}, resume_facts=recovered['facts'])
                focused.base = checkpoint['baseline']
                focused.checkpoint_parent, focused.checkpoint_paths = checkpoint['parent'], checkpoint['paths']
                matched = focused.reconcile_checkpoint()
                if matched is None:
                    raise Blocked('repair commit effects are missing or uncertain; inspect actual parent/SHA without recommitting')
                for name, expected in checkpoint.get('blobs', {}).items():
                    entries = git(project, 'ls-tree', head, '--', name).decode().split()
                    actual = entries[2] if entries else None
                    if actual != expected:
                        raise Blocked('repair commit bytes differ from retained checkpoint intent; inspect target drift')
                if 'blobs' not in checkpoint:
                    raise Blocked('repair checkpoint lacks exact content facts; inspect effects without recommitting')
                checkpoint = {**matched, 'parent': checkpoint['parent']}
                store.history(self.run, None, 'fixer_checkpoint', 'passed', {'execution_id': execution_id, **checkpoint})
            store.review_outcome(self.run, execution_id, 'approved', findings=[],
                                 references={'base': review_base, 'head': head, 'commit': checkpoint['sha']})
            return None
        if head != returned['head']:
            raise Blocked('returned repair target drifted; inspect effects before checks/checkpoint')
        if checks and checks[-1] != 'passed':
            raise Blocked('repair check completion is uncertain; inspect actual check effects before targeted continuation')
        effects = check_events[-1][1] if check_events else returned
        if (effects.get('head') != head or self._repair_blobs(project, returned['paths']) != effects.get('blobs')):
            raise Blocked('returned repair source bytes drifted; preserve them and inspect ownership before continuation')
        return recovered

    @staticmethod
    def _review_value(text):
        """Parse an actual reviewer verdict; fenced JSON is safe normalization only."""
        if not isinstance(text, str):
            raise _ReviewFormat('reviewer result must be text')
        normalized = text.strip()
        if normalized.startswith('```') and normalized.endswith('```'):
            normalized = normalized.split('\n', 1)[1] if '\n' in normalized else ''
            normalized = normalized.rsplit('```', 1)[0].strip()
        try:
            value = json.loads(normalized)
        except ValueError:
            raise _ReviewFormat('reviewer returned invalid JSON; review remains incomplete: ' + text) from None
        findings, suggestions = value.get('findings') if isinstance(value, dict) else None, value.get('suggestions', []) if isinstance(value, dict) else None
        if (not isinstance(value, dict) or type(value.get('approved')) is not bool
                or not isinstance(findings, list) or not isinstance(suggestions, list)
                or any(not isinstance(item, str) or not item.strip() for item in findings + suggestions)):
            raise _ReviewFormat('reviewer result needs boolean approved, findings string list, and optional suggestions string list')
        # Findings are repair dispatch inputs, not a severity vocabulary.  Each must say
        # where the defect is, its concrete impact, and why it violates accepted work.
        pattern = re.compile(r'^\S+:\d+\s+-\s+\S')
        if any(not pattern.match(item.strip()) for item in findings):
            raise _ReviewFormat('review blocker needs a path:line location and concrete defect/impact')
        # Basis is described in ordinary defect prose, not a mandatory suffix.
        return {'approved': value['approved'], 'findings': findings, 'suggestions': suggestions}

    @staticmethod
    def _review_inputs(checkpoints):
        """Retain all-and-only runner-selected completed task outputs, or no claim."""
        selected = []
        for item in checkpoints:
            value = {key: item.get(key) for key in
                     ('checkpoint_occurrence_id', 'task_id', 'producer_invocation_id', 'correction_chain')}
            if (not all(isinstance(value[key], str) and value[key] for key in
                        ('checkpoint_occurrence_id', 'task_id', 'producer_invocation_id')) or
                    not isinstance(value['correction_chain'], list) or not value['correction_chain'] or
                    any(not isinstance(part, str) or not part for part in value['correction_chain']) or
                    value['correction_chain'][-1] != value['producer_invocation_id']):
                return None
            selected.append(value)
        return selected

    def _review(self, *, recorder, review_base, head, ordinal, fixing_round=0,
                trigger_execution_id=None, predecessor_execution_id=None, input_checkpoints=None,
                execution_id=None):
        """Dispatch exactly one fresh read-only reviewer and retain its actual outcome."""
        store = self.authority.store
        execution_id = execution_id or uuid.uuid4().hex
        store.review_dispatch(self.run, execution_id, role='reviewer', review_ordinal=ordinal,
                              fixing_round=fixing_round, trigger_execution_id=trigger_execution_id,
                              predecessor_execution_id=predecessor_execution_id,
                              input_checkpoints=input_checkpoints,
                              review_base=review_base, review_head=head)
        review_facts = {
            'role': 'reviewer', 'execution_id': execution_id, 'review_ordinal': ordinal,
            'review_base': review_base, 'review_head': head,
        }
        if trigger_execution_id is not None:
            review_facts['trigger_execution_id'] = trigger_execution_id
            review_facts['predecessor_execution_id'] = predecessor_execution_id
        if input_checkpoints is not None:
            review_facts['selected_input_checkpoints'] = input_checkpoints
        recorder.emit(execution_id, 'review', 'started', facts=review_facts)
        reviewer = self.adapter(self.authority.project, self.reviewer_executor, question=self.question)
        reviewer.lock_fd = self.authority.lock.fileno()
        diff = git(self.authority.project, 'diff', '--no-ext-diff', '--no-textconv', review_base + '..' + head).decode(errors='replace')
        try:
            text = reviewer.prompt('Independently review the actual committed range below against the requested tasks. '
                'You are read-only and are NOT the implementation conversation. Skills are disabled for this reviewer, '
                'so locate and read the canonical contract as a file with read/search tools; continue long reads with offsets. '
                + _DECISION_CONSTRAINTS + _ROUTINE_AUTHORITY + self.paid_authority()
                + 'Identify concrete correctness, scope or data-safety defects, not missing workflow ceremony. '
                'Return only JSON: {"approved":true,"findings":[],"suggestions":[]} (suggestions may be omitted) or '
                '{"approved":false,"findings":["path:line - concrete defect, impact and accepted basis in ordinary prose"]}. '
                'Use findings only for blockers: each needs a location, concrete impact, and basis of requirement, correctness, security, or data-safety. '
                'Put only nonblocking advice in suggestions; crashes, hangs, target/credential risks, and false-unavailable observations are blockers. Never approve when blockers exist.\n'
                'Tasks: ' + canonical(self.contract['tasks']) + '\nRange: ' + review_base + '..' + head + '\nDiff:\n' + diff,
                read_only=True)
            value = self._review_value(text)
        except BaseException as exc:
            state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
            store.review_outcome(self.run, execution_id, state, findings=[], suggestions=[],
                                 uncertainty=state != 'failed' or isinstance(exc, _ReviewFormat),
                                 references={'base': review_base, 'head': head})
            recorder.emit(execution_id, 'review', state, facts={
                'role': 'reviewer', 'execution_id': execution_id, 'review_ordinal': ordinal,
                'review_base': review_base, 'review_head': head, 'outcome': state,
                'error_category': 'malformed' if isinstance(exc, _ReviewFormat) else _failure(exc),
            })
            self._append_metric(reviewer, invocation_id=execution_id, task_id=None, role='reviewer',
                                outcome=state, selection={'session_id': None, 'reason': 'reviewer_fresh'},
                                review_ordinal=ordinal)
            raise
        self._append_metric(reviewer, invocation_id=execution_id, task_id=None, role='reviewer',
                            outcome='settled', selection={'session_id': None, 'reason': 'reviewer_fresh'},
                            review_ordinal=ordinal)
        state = 'approved' if value['approved'] and not value['findings'] else 'rejected'
        if not hasattr(self, '_review_workers'):
            self._review_workers = {}
        self._review_workers[execution_id] = reviewer
        store.review_outcome(self.run, execution_id, state, findings=value['findings'], suggestions=value['suggestions'],
                             references={'base': review_base, 'head': head,
                                         'saved_session': getattr(reviewer, 'saved_session', None)})
        review_facts.update({'approved': value['approved'], 'outcome': state,
                             'finding_count': len(value['findings'])})
        recorder.emit(execution_id, 'review', 'passed' if state == 'approved' else 'failed', facts=review_facts)
        return execution_id, value, state

    def _finish_reviews(self, *, recorder, terminal, checkpoints, base, review_base, terminal_stop=None):
        """Select the last eligible persisted stage; owner grants add one pair only."""
        store = self.authority.store
        policy = store.review_policy(self.run)
        scope = hashlib.sha256(canonical(self.contract['tasks']).encode()).hexdigest()

        def value(item):
            return {'approved': item['state'] == 'approved',
                    'findings': item['findings'][-1] if item.get('findings') else [],
                    'suggestions': item['suggestions'][-1] if item.get('suggestions') else []}

        def complete(item, review):
            head = item['references'].get('head')
            if not isinstance(head, str) or not head:
                raise Blocked('approved review is missing its actually reviewed head; inspect retained review history')
            store.finish(self.run, 'complete', head)
            recorder.emit(terminal, 'terminal', 'passed', facts={'head': head})
            return {'status': 'complete', 'run_id': self.run, 'baseline': base, 'sha': head,
                    'checkpoints': checkpoints, 'review': review, 'usage': self.usage_summary()}

        while True:
            chain = store.review_chain(self.run, private=True)
            if chain['uncertain']:
                raise Blocked('review invocation outcome is uncertain; inspect it before any replay')
            executions = chain['executions']
            if not executions:
                head = git(self.authority.project, 'rev-parse', 'HEAD').decode().strip()
                self._review(recorder=recorder, review_base=review_base, head=head, ordinal=1,
                             input_checkpoints=self._review_inputs(checkpoints))
                continue
            last = executions[-1]
            if (policy == 'owner-pair-v1' and last['role'] == 'fixer' and
                    last['fixing_round'] > 1 and last['state'] == 'dispatched'):
                recovered = self._recover_assigned_fix(last, review_base)
                if recovered is not None:
                    rejection = next(item for item in executions if item['execution_id'] == last['trigger_execution_id'])
                    self.run_fix(value(rejection)['findings'], trigger_execution_id=rejection['execution_id'],
                        review_base=review_base, recorder=recorder, execution_id=last['execution_id'],
                        review_ordinal=last['review_ordinal'], fixing_round=last['fixing_round'],
                        predecessor_execution_id=last['predecessor_execution_id'], terminal_stop=terminal_stop,
                        recovered=recovered)
                continue
            review = value(last)
            if last['role'] == 'reviewer':
                if last['state'] == 'approved':
                    return complete(last, review)
                if last['state'] != 'rejected' or review['approved'] or not review['findings']:
                    raise Blocked('independent review was not an actionable rejection (commits retained): ' + canonical(review))
                ordinal, round_ = last['review_ordinal'], last['fixing_round'] + 1
                if policy == 'historical-two-review-one-fixer' and ordinal != 1:
                    raise Blocked('independent final review findings (commits retained): ' + canonical(review))
                fixer_id = uuid.uuid4().hex
                grant = None
                if policy == 'owner-pair-v1' and ordinal > 1:
                    head = last['references'].get('head')
                    grant = store.owner_pair_for_rejection(self.run, rejecting_execution_id=last['execution_id'],
                                                           review_base=review_base, review_head=head, original_scope=scope)
                    if grant is None:
                        context = {'rejecting_execution': last['execution_id'], 'review_base': review_base,
                                   'review_head': head, 'scope': scope,
                                   'effect': 'Authorize exactly one scoped repair and one fresh full-range review; no repeat grant.'}
                        question = ('Independent review rejected execution ' + last['execution_id'] + ' for original range ' +
                                    review_base + '..' + head + ', original task scope ' + scope +
                                    '. Authorize exactly one scoped repair plus fresh full-range review with the configured models, '
                                    'not a repeat grant? [yes/no]')
                        try:
                            answer = self.question(question, owner_only=True, decision_context=context)
                        except BaseException as exc:
                            store.history(self.run, None, 'review_pair_decision', 'unavailable', context)
                            raise Blocked('owner authorization unavailable; no repair/review pair dispatched: ' + str(exc)) from exc
                        if not isinstance(answer, str) or answer.strip().lower() not in ('yes', 'y'):
                            store.history(self.run, None, 'review_pair_decision', 'denied', context)
                            raise Blocked('owner did not authorize an additional repair/review pair; blockers retained')
                        grant = store.authorize_owner_pair(self.run, uuid.uuid4().hex,
                            rejecting_execution_id=last['execution_id'], review_base=review_base, review_head=head,
                            original_scope=scope, fixer_execution_id=fixer_id, reviewer_execution_id=uuid.uuid4().hex)
                    fixer_id = grant['fixer_execution_id']
                    current = git(self.authority.project, 'rev-parse', 'HEAD').decode().strip()
                    if current != grant['review_head']:
                        raise Blocked('review target drifted after owner authorization; inspect and renew affected authority before dispatch')
                    store.reserve_owner_pair_fixer(self.run, grant['grant_id'], rejecting_execution_id=last['execution_id'],
                                                   review_base=review_base, review_head=grant['review_head'], original_scope=scope)
                self.run_fix(review['findings'], trigger_execution_id=last['execution_id'], review_base=review_base,
                             recorder=recorder, execution_id=fixer_id, review_ordinal=ordinal,
                             fixing_round=round_, predecessor_execution_id=last['execution_id'], terminal_stop=terminal_stop)
                continue
            # A successful fixer alone never accepts delivery: reserve/dispatch its exact fresh reviewer.
            if last['state'] != 'approved':
                raise Blocked('fixing round remains incomplete or failed; commits retained')
            ordinal, round_ = last['review_ordinal'] + 1, last['fixing_round']
            reviewer_id = None
            if policy == 'owner-pair-v1' and round_ > 1:
                grant = next((item for item in reversed(executions) if item['role'] == 'reviewer' and
                              item['execution_id'] == last['trigger_execution_id']), None)
                if grant is None:
                    raise Blocked('assigned fixer has no retained rejecting review')
                facts = store.owner_pair_for_rejection(self.run, rejecting_execution_id=grant['execution_id'],
                    review_base=review_base, review_head=grant['references'].get('head'), original_scope=scope)
                if facts is None:
                    raise Blocked('assigned fixer has no retained owner pair grant')
                reviewer_id = store.reserve_owner_pair_reviewer(self.run, facts['grant_id'], fixer_execution_id=last['execution_id'])['reviewer_execution_id']
            head = git(self.authority.project, 'rev-parse', 'HEAD').decode().strip()
            repaired_head = last['references'].get('head')
            if not isinstance(repaired_head, str) or head != repaired_head:
                raise Blocked('review target drifted after repair; inspect affected continuation before dispatch')
            self._review(recorder=recorder, review_base=review_base, head=head, ordinal=ordinal, fixing_round=round_,
                         trigger_execution_id=last['execution_id'], predecessor_execution_id=last['execution_id'], execution_id=reviewer_id)

    def invoke(self):
        project, store = self.authority.project, self.authority.store
        recovered = store.completed_checkpoints(self.run) if self.resume else {}
        base = store.db.execute('SELECT baseline FROM execution_runs WHERE run_id=?', (self.run,)).fetchone()['baseline'] if self.resume else git(project, 'rev-parse', 'HEAD').decode().strip()
        requested_review_base = store.input(self.run)['review_base'] if self.resume else self.contract.get('review_base', base)
        if not isinstance(requested_review_base, str) or not requested_review_base:
            raise Blocked('review_base must be a Git commit')
        try:
            review_base = git(project, 'rev-parse', '--verify', requested_review_base + '^{commit}').decode().strip()
            git(project, 'merge-base', '--is-ancestor', review_base, base)
        except Blocked:
            raise Blocked('review_base must resolve to an ancestor of the run baseline') from None
        if not self.resume:
            store.start(self.run, base, contract=self.contract, executor=self.input_executor,
                        authority={'paid_scope': self.paid_scope, 'routine_authority': True,
                                   'review_policy': 'owner-pair-v1'}, review_base=review_base)
        recorder = Recorder(store, self.run)
        try:
            identity = process_identity(os.getpid(), self.run)
        except Exception:
            identity = None
        if not self.resume:
            recorder.register(descriptor(self.contract, self.executor, base), identity)
        else:
            recorder.resume()
        checkpoints = list(recovered.values())
        terminal = recorder.occurrence()
        terminal_stop = [None]
        recorder.emit(terminal, 'terminal', 'started', facts={'baseline': base})
        try:
            for task in self.contract['tasks']:
                if task['id'] in recovered:
                    continue
                preparation = recorder.occurrence()
                recorder.emit(preparation, 'prepare', 'started', task_id=task['id'])
                focused = None
                try:
                    focused = FocusedGit(project, task, store.task_facts(self.run, task['id']) if self.resume else None)
                    store.task(self.run, task['id'], 'running', focused.base)
                    recorder.emit(preparation, 'prepare', 'passed', task_id=task['id'])
                    gate_number = [0]
                    def gate_question(text):
                        gate_number[0] += 1
                        gate_occurrence, question_occurrence = recorder.occurrence(), recorder.occurrence()
                        facts = {'ordinal': gate_number[0]}
                        recorder.emit(gate_occurrence, 'gate', 'started', task_id=task['id'], facts=facts)
                        recorder.emit(question_occurrence, 'gate', 'question_requested', task_id=task['id'], facts={**facts, 'parent_occurrence_id': gate_occurrence})
                        try:
                            answer = self.question(text)
                        except BaseException as exc:
                            recorder.emit(question_occurrence, 'gate', 'delivery_failed', task_id=task['id'], facts={**facts, 'parent_occurrence_id': gate_occurrence, 'error_category': 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'blocked'})
                            recorder.emit(gate_occurrence, 'gate', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', task_id=task['id'], facts={**facts, 'error_category': 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'blocked'})
                            raise
                        recorder.emit(question_occurrence, 'gate', 'answer_returned', task_id=task['id'], facts={**facts, 'parent_occurrence_id': gate_occurrence})
                        recorder.emit(gate_occurrence, 'gate', 'passed' if answer.strip().lower() in ('yes', 'y') else 'failed', task_id=task['id'], facts=facts)
                        return answer
                    manual_gates(task, gate_question)
                    role = 'fixing_worker' if isinstance(self.contract.get('monitor'), dict) and self.contract['monitor'].get('correction_of') else 'worker'
                    active_occurrence, invocation_chain, last_invocation = [None], [], [None]
                    question_occurrence = [None]
                    def worker_question(state):
                        mapping = {'requested': 'question_requested', 'returned': 'answer_returned', 'sent': 'answer_sent', 'delivery_failed': 'delivery_failed'}
                        if active_occurrence[0] is not None:
                            if state == 'requested' or question_occurrence[0] is None:
                                question_occurrence[0] = recorder.occurrence()
                            recorder.emit(question_occurrence[0], 'worker', mapping[state], task_id=task['id'],
                                          facts={'parent_occurrence_id': active_occurrence[0]})
                            if state in {'sent', 'delivery_failed'}:
                                question_occurrence[0] = None
                    session_request, reuse_key = self._session_request(task, role)
                    selection = select_session(session_request, self.session_candidates)
                    selected = next((candidate for candidate in self.session_candidates
                                     if candidate['id'] == selection['session_id']), None)
                    store.history(self.run, task['id'], 'session', 'selected', {
                        'session_id': selection['session_id'], 'reason': selection['reason'],
                        'rejected': selection['rejected'],
                    })
                    worker = self.adapter(project, self.executor, question=self.question, observe_question=worker_question)
                    worker.lock_fd = self.authority.lock.fileno()
                    continuation = None
                    if self.resume:
                        row = store.db.execute(
                            "SELECT state,details FROM execution_history WHERE run_id=? AND task_id=? "
                            "AND kind='worker_invocation' ORDER BY seq DESC LIMIT 1", (self.run, task['id'])).fetchone()
                        if row:
                            continuation = {'state': row['state'], **json.loads(row['details'])}
                            if row['state'] == 'started':
                                raise Blocked('unfinished worker invocation has no terminal outcome; inspect its saved call before continuation')
                            if row['state'] == 'failed':
                                if not continuation.get('saved_session'):
                                    raise Blocked('terminal worker failure has no saved session; inspect the failed invocation/cause before any relaunch: '
                                                  + str(continuation.get('invocation_id', 'unknown')))
                                correction = self.question(
                                    'As coordinating agent, inspect this terminal worker invocation and its saved session before continuing. '
                                    'Provide the inspected diagnosis and a targeted correction justifying safe continuation '
                                    '(not an unchanged retry); do not ask the owner to debug routine technical failures; leave empty if unknown. '
                                    'Actual invocation: ' + canonical(continuation))
                                if not correction.strip() or correction.strip().lower() in ('unknown', 'retry', 'yes'):
                                    raise Blocked('terminal worker cause/targeted correction remains unknown; no worker relaunched')
                                continuation['targeted_correction'] = correction
                            if continuation.get('saved_session'):
                                if continuation.get('reuse_key') != reuse_key:
                                    raise Blocked('saved unfinished worker authority/resources are incompatible; inspect before continuation')
                                worker.saved_session = continuation['saved_session']
                            # Retain only the recorded terminal invocation sequence for this
                            # same task. It is the evidence for a resumed correction's direct
                            # predecessor; malformed or incomplete optional history stays unknown.
                            retained = []
                            for prior in store.db.execute(
                                "SELECT details FROM execution_history WHERE run_id=? AND task_id=? "
                                "AND kind='worker_invocation' AND state IN ('returned','failed','interrupted') ORDER BY seq",
                                (self.run, task['id'])):
                                try:
                                    invocation_id = json.loads(prior['details']).get('invocation_id')
                                except (TypeError, ValueError):
                                    retained = []
                                    break
                                if not isinstance(invocation_id, str) or not invocation_id or invocation_id in retained:
                                    retained = []
                                    break
                                retained.append(invocation_id)
                            if retained and retained[-1] == continuation.get('invocation_id'):
                                invocation_chain[:] = retained
                                last_invocation[0] = retained[-1]
                        else:
                            prior = store.db.execute(
                                "SELECT 1 FROM execution_history WHERE run_id=? AND task_id=? AND kind='worker' LIMIT 1",
                                (self.run, task['id'])).fetchone()
                            if prior:
                                raise Blocked('unfinished worker lacks retained invocation/cause; inspect legacy history before any relaunch')
                    def selected_inputs():
                        # Only checkpoints the sequential runner selected from declared prerequisites
                        # are relations; absent recording remains absent rather than guessed.
                        return [{'checkpoint_occurrence_id': item['checkpoint_occurrence_id'], 'task_id': item['task_id'],
                                 'producer_invocation_id': item['producer_invocation_id'],
                                 'correction_chain': item['correction_chain']}
                                for item in checkpoints if item.get('task_id') in task.get('depends', [])
                                and isinstance(item.get('checkpoint_occurrence_id'), str)
                                and isinstance(item.get('producer_invocation_id'), str)]

                    def invoke_worker(prompt, **kwargs):
                        nonlocal continuation
                        prompt = _IMPLEMENTATION_AUTHORITY + _ROUTINE_AUTHORITY + '\n' + prompt
                        if continuation is not None:
                            prompt = ('Continue only the unfinished same-task work. Inspect the prior invocation/cause below; '
                                      'do not replay completed effects. Apply only the justified targeted correction; '
                                      'unknown terminal causes are not retry permission.\nRetained invocation: '
                                      + canonical(continuation) + '\n' + prompt)
                            continuation = None
                        invocation_id = uuid.uuid4().hex
                        predecessor = last_invocation[0]
                        chain = [*invocation_chain, invocation_id]
                        invocation_kind = 'corrective_worker' if predecessor else 'task_worker'
                        occurrence = recorder.occurrence()
                        active_occurrence[0] = occurrence
                        public = {'role': role, 'invocation_id': invocation_id, 'invocation_kind': invocation_kind,
                                  'selected_input_checkpoints': selected_inputs(), 'correction_chain': chain}
                        if predecessor:
                            public['predecessor_invocation_id'] = predecessor
                        facts = {'invocation_id': invocation_id, 'role': role, 'prompt': prompt, 'reuse_key': reuse_key,
                                 'saved_session': getattr(worker, 'saved_session', None)}
                        store.history(self.run, task['id'], 'worker_invocation', 'started', facts)
                        recorder.emit(occurrence, 'worker', 'started', task_id=task['id'], facts=public)
                        steering = {'run_id': self.run, 'task_id': task['id'], 'invocation_id': invocation_id,
                                    'role': invocation_kind}
                        if getattr(worker, 'parent_steering_available', lambda: False)():
                            worker.enable_parent_steering(steering)
                            kwargs['steering'] = steering
                        expected_session_id = (getattr(worker, 'saved_session', {}) or {}).get('id')
                        # Clear every optional observation before this actual call.
                        worker.last_interval = None
                        worker.last_observation = None
                        worker.opened_session = None
                        try:
                            result = self._prompt_worker(worker, prompt, **kwargs)
                            # A normal transport return is not itself task acceptance. Adapters
                            # may return an explicit failure object after delivering a question
                            # answer; preserve that reported blocker instead of checkpointing it.
                            # This deliberately does not interpret summary prose or require a
                            # result format: ordinary text remains the existing completion path.
                            if isinstance(result, BaseException):
                                raise result
                            if result is None:
                                raise Blocked('worker returned without completing the task; partial work retained')
                        except BaseException as exc:
                            state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                            store.history(self.run, task['id'], 'worker_invocation', state,
                                {**facts, 'error': str(exc) or type(exc).__name__,
                                 'saved_session': getattr(worker, 'saved_session', None)})
                            terminal_stop[0] = invocation_id
                            recorder.emit(occurrence, 'worker', state, task_id=task['id'],
                                          facts={**public, 'stopped_by_invocation_id': invocation_id,
                                                 'error_category': _failure(exc)})
                            self._append_metric(worker, invocation_id=invocation_id, task_id=task['id'],
                                                role=(role if role == 'fixing_worker' else 'corrective_worker' if predecessor else 'worker'), outcome=state,
                                                selection=selection, continued=predecessor is not None,
                                                expected_session_id=expected_session_id)
                            raise
                        store.history(self.run, task['id'], 'worker_invocation', 'returned',
                                      {**facts, 'saved_session': getattr(worker, 'saved_session', None)})
                        recorder.emit(occurrence, 'worker', 'returned', task_id=task['id'], facts=public)
                        self._append_metric(worker, invocation_id=invocation_id, task_id=task['id'],
                                            role=(role if role == 'fixing_worker' else 'corrective_worker' if predecessor else 'worker'), outcome='settled',
                                            selection=selection, continued=predecessor is not None,
                                            expected_session_id=expected_session_id)
                        invocation_chain[:] = chain
                        last_invocation[0] = invocation_id
                        return result
                    claimed_paths = set()
                    def claim(name):
                        if name not in claimed_paths:
                            focused.claim(name)
                            store.history(self.run, task['id'], 'mutation', 'claimed', focused.facts())
                            claimed_paths.add(name)
                    def command(phase, call):
                        focused.command(phase, call)
                        store.history(self.run, task['id'], 'tool_command',
                                      'started' if phase == 'start' else 'returned',
                                      {'call': call})
                    try:
                        text = invoke_worker(
                            'Execute this one requested task in the current project. Read the relevant files, '
                            'make the smallest correct edits, run relevant actual project checks and fix ordinary '
                            'tool/read/argument/check errors in this conversation. Never stage or commit: the runner '
                            'will inspect and create the focused commit. Do not install globally, refresh credentials, '
                            'change global settings, delegate, or perform unrequested external operations. '
                            'Preserve all unrelated and pre-existing dirty work. Ask the owner for material scope '
                            'or permission questions. No new planning/evidence artifacts. '
                            'Return an honest concise summary and check outcomes.\n'
                            + _DECISION_CONSTRAINTS + self.paid_authority() + '\n'
                            'Select source edit and commit paths explicitly; preserve unknown and pre-existing bytes. '
                            'Generated outputs are cleanup guidance, never a registration or command prerequisite.\n'
                            'Task: ' + canonical(task), claim=claim, command=command,
                            cleanup=focused.cleanup_artifact, saved_session=(continuation.get('saved_session') if continuation else
                                selected['saved_session'] if selected else None), reuse_key=reuse_key)
                    except BaseException as exc:
                        state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                        store.history(self.run, task['id'], 'worker', state, {'role': role, 'error': str(exc)})
                        raise
                    store.history(self.run, task['id'], 'worker', 'returned', {'role': role})
                    check_occurrences = {}
                    def check_observe(kind, ordinal, code):
                        occurrence = check_occurrences.setdefault(ordinal, recorder.occurrence())
                        facts = {'ordinal': ordinal}
                        if code is not None: facts['exit_code'] = code
                        recorder.emit(occurrence, 'check', kind, task_id=task['id'], facts=facts)
                    def run_required_checks():
                        return run_checks(project, task, lock_fd=self.authority.lock.fileno(), observe=check_observe,
                            completed=lambda state, attempt: store.history(self.run, task['id'], 'check', state, attempt))
                    def correct_required_checks():
                        nonlocal text
                        previous_failed_attempt = None
                        while True:
                            try:
                                checks = run_required_checks()
                                return checks
                            except CheckFailure as failure:
                                if failure.attempt == previous_failed_attempt:
                                    raise Blocked('required check failed and remains unchanged after same-task correction: ' + canonical(failure.attempt))
                                previous_failed_attempt = failure.attempt
                                try:
                                    text = invoke_worker(
                                        'A runner-owned REQUIRED check for this same task failed. Make a reasoned, '
                                        'authorized scoped source or local-setup correction if one is safe, then return. '
                                        'Do not claim success, skip the command, or ask merely because files changed. '
                                        'If no safe correction remains or a material decision is needed, state that blocker. '
                                        'The runner will rerun the affected required command before checkpointing.\n'
                                        'Actual failed attempt: ' + canonical(failure.attempt),
                                        claim=claim, command=command, cleanup=focused.cleanup_artifact, reuse_key=reuse_key)
                                except BaseException as exc:
                                    state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                                    store.history(self.run, task['id'], 'worker', state, {'role': role, 'correction': True, 'error': str(exc)})
                                    raise
                                store.history(self.run, task['id'], 'worker', 'returned', {'role': role, 'correction': True})

                    checks = correct_required_checks()
                    previous_checkpoint_error = None
                    while True:
                        checkpoint_occurrence = recorder.occurrence()
                        recorder.emit(checkpoint_occurrence, 'checkpoint', 'started', task_id=task['id'], facts={'baseline': focused.base})
                        try:
                            checkpoint = focused.checkpoint()
                        except BaseException as exc:
                            state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                            recorder.emit(checkpoint_occurrence, 'checkpoint', state, task_id=task['id'], facts={'baseline': focused.base, 'error_category': _failure(exc)})
                            store.history(self.run, task['id'], 'checkpoint', state, {'error': str(exc)})
                            checkpoint = focused.reconcile_checkpoint()
                            if checkpoint is not None:
                                break
                            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                                raise
                            if str(exc) == previous_checkpoint_error:
                                raise Blocked('checkpoint failed and remains unchanged after same-task correction: ' + str(exc))
                            previous_checkpoint_error = str(exc)
                            try:
                                text = invoke_worker(
                                    'A runner-owned checkpoint for this same task failed. Make a reasoned, authorized '
                                    'scoped correction if one is safe. Do not bypass hooks or signing, reset, rebase, '
                                    'or adopt unrelated work. The runner will rerun affected REQUIRED checks and the '
                                    'checkpoint with normal Git configuration intact.\nActual checkpoint error: ' + str(exc),
                                    claim=claim, command=command, cleanup=focused.cleanup_artifact, reuse_key=reuse_key)
                            except BaseException as correction_error:
                                correction_state = 'interrupted' if isinstance(correction_error, (KeyboardInterrupt, SystemExit)) else 'failed'
                                store.history(self.run, task['id'], 'worker', correction_state, {'role': role, 'correction': True, 'error': str(correction_error)})
                                raise
                            store.history(self.run, task['id'], 'worker', 'returned', {'role': role, 'correction': True})
                            checks = correct_required_checks()
                            continue
                        break
                    checkpoint['parent'] = (None if checkpoint['no_change'] else
                                            git(project, 'rev-parse', checkpoint['sha'] + '^').decode().strip())
                    checkpoint.update({'task_id': task['id'], 'checkpoint_occurrence_id': checkpoint_occurrence,
                                       'producer_invocation_id': last_invocation[0],
                                       'correction_chain': list(invocation_chain)})
                    checkpoint_facts = {'baseline': focused.base, 'head': checkpoint['sha'], 'no_change': checkpoint['no_change']}
                    if last_invocation[0] is not None:
                        checkpoint_facts.update({'producer_invocation_id': last_invocation[0],
                                                 'correction_chain': list(invocation_chain)})
                    recorder.emit(checkpoint_occurrence, 'checkpoint', 'passed', task_id=task['id'], facts=checkpoint_facts)
                    store.history(self.run, task['id'], 'checkpoint', 'passed', checkpoint)
                    checkpoints.append(checkpoint)
                    self._settle_session(task, worker, session_request, reuse_key, checkpoint)
                    store.task(self.run, task['id'], 'complete', focused.base, checkpoint['sha'],
                               {'summary': text, 'checks': checks, 'paths': checkpoint['paths'],
                                'generated_artifacts': checkpoint['artifacts']})
                except BaseException as exc:
                    recorder.emit(preparation, 'prepare', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', task_id=task['id'], facts={'error_category': _failure(exc)})
                    state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                    store.task(self.run, task['id'], state, focused.base if focused else base, details={'error': str(exc)})
                    raise
            result = self._finish_reviews(recorder=recorder, terminal=terminal, checkpoints=checkpoints,
                                          base=base, review_base=review_base, terminal_stop=terminal_stop)
            return self._finalize_metric_artifact(result)
        except BaseException as exc:
            head = git(project, 'rev-parse', 'HEAD').decode().strip()
            store.finish(self.run, 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', head, str(exc))
            terminal_facts = {'head': head, 'error_category': _failure(exc)}
            if terminal_stop[0] is not None:
                terminal_facts['stopped_by_invocation_id'] = terminal_stop[0]
            recorder.emit(terminal, 'terminal', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', facts=terminal_facts)
            self._finalize_metric_artifact()
            raise
