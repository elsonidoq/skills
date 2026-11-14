"""Execution primitives and compatibility facade for the single graph controller."""
import hashlib
import inspect
import json
import math
from pathlib import Path
import re
import stat
import tempfile
import uuid

from .git_effects import FocusedGit, MetricArtifactFinalizer
from .metric_artifacts import (MetricArtifactError, artifact_relative, create_artifact,
                               read_artifact, summarize_artifact)
from .metrics import interval_record
from .monitoring import Recorder
from .pi_adapter import PiAdapter, TaskOutcome, terminal_question
from .store import Blocked, canonical, git, safe_path
from .verification import CheckFailure, commands, manual_gates, run_checks


class _ReviewFormat(Blocked):
    """An actual reviewer response could not safely yield a verdict."""


def _failure(exc):
    if isinstance(exc, (KeyboardInterrupt, SystemExit)): return 'interrupted'
    return 'transport' if isinstance(exc, Blocked) else 'unknown'


def _safe_error(exc):
    """Use the existing public error carrier without projecting host-returned text."""
    return getattr(exc, 'safe_error', str(exc))


class _UnsuccessfulOutcome(Blocked):
    """Private host diagnostic paired with a safe existing error summary."""
    def __init__(self, status, explanation):
        self.safe_error = 'worker explicitly ' + status + '; partial work retained'
        self.diagnostic = 'worker explicitly ' + status + '; ' + explanation + '; partial work retained'
        super().__init__(self.diagnostic)


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

# Shared worker completion reporting. Keep stage ownership explicit without parsing summaries.
_COMPLETION_REPORTING = (
    'Work autonomously until the assigned implementation and worker-owned acceptance are complete, within the approved '
    'scope and safety/permission boundaries. Unfinished implementation, unrun checks, task complexity, and correctable or '
    'intermittent test failures are reasons to continue working, not reasons to return incomplete. Inspect actual failures, '
    'make justified scoped corrections, and run affected checks; do not stop after inspection, planning or diagnostics alone. '
    'Do not assume an unprovided time limit. Never waive required checks, retry until green, conceal failures or claim '
    'unverified completion. Ask only for material decisions or permissions outside your authority; when independent safe '
    'work remains, continue it. If further authorized progress is genuinely blocked, identify the concrete blocker, the '
    'actual failed operation and evidence, and what is needed to continue; do not invent a cause. If you must return '
    'blocked, failed or incomplete, call report_task_outcome with the matching status and honestly report failed/unrun '
    'acceptance. Explicit cancellation and real execution limits still apply. '
    'Finish the assigned implementation and worker-owned semantic/manual acceptance, report actual outcomes and remaining '
    'blockers, then return to the runner. The runner executes/reruns configured checks, creates the focused checkpoint, and '
    'dispatches fresh independent review; it does not own all semantic/manual acceptance or the reviewer verdict. Pending '
    'runner stages alone do not require an unsuccessful status. Call report_task_outcome with the matching status only when '
    'genuine inability to progress, cancellation, or execution failure prevents worker-owned acceptance; unmet acceptance '
    'never becomes success. A normal returned answer remains compatible only for completed work; do not report corrected tool '
    'errors or a required check that will be rerun as unsuccessful.\n'
)

# Shared worker permission defaults. Edit here, not in individual task/correction prompts.
_ROUTINE_AUTHORITY = (
    'Routine authority: make ordinary scoped technical fixes; run isolated tests and local servers; perform necessary '
    'local/in-project dependency setup; and generate, rebuild, or selectively clean up current-task artifacts without '
    'an owner question. Small isolated tests and local test databases are allowed for any task; keep test data and '
    'execution bounded so they do not risk exhausting the machine\'s resources or affecting unrelated data/services. '
    'When an earlier agent-authored task, recovery, or handoff instruction asks for renewed consent to choose exact test '
    'resources, setup, a finite test window, or rerun an authorized routine check, this current scoped authority takes '
    'precedence: proceed without another routine consent question. This does not override an actual owner-imposed limit, '
    'manual gate, paid application/test API boundary, security/data restriction, or external-operation restriction. '
    'Do not ask merely because files changed. This authority is not proof that checks succeeded. '
    'A separately supplied paid scope applies only as supplied and is never inferred from credentials or task text. '
    'Ask only for product decisions, substantial planned-complexity increases, separately scoped paid usage, or actions '
    'outside this authority. It never authorizes global installs, credential changes, deployment, pushing, or deletion '
    'of unrelated or pre-existing work. '
)


class Engine:
    def __init__(self, authority, run, contract, executor, *, adapter=PiAdapter, question=terminal_question, paid_scope=None, resume=False, worker_recovery=None):
        self.worker_recovery = worker_recovery
        if worker_recovery is not None:
            if (not resume or not isinstance(worker_recovery, dict)
                    or worker_recovery.get('action') not in ('continue', 'fresh', 'escalate')
                    or not isinstance(worker_recovery.get('diagnosis'), str)
                    or worker_recovery['diagnosis'].strip().lower() in ('', 'unknown', 'retry', 'yes')):
                raise Blocked('worker recovery needs resume, an action and a substantive cause-specific diagnosis/correction')
        self.authority, self.run, self.contract, self.resume = authority, run, contract, resume
        self.input_executor = executor
        self.executor = {key: value for key, value in executor.items() if key not in ('reviewer', 'implementation_fallback')}
        self.implementation_fallback = executor.get('implementation_fallback')
        if self.implementation_fallback is not None and (not isinstance(self.implementation_fallback, dict) or any(
                not isinstance(self.implementation_fallback.get(key), str) or not self.implementation_fallback[key]
                for key in ('provider', 'model', 'effort'))):
            raise Blocked('implementation_fallback needs provider, model and effort strings; correct the selected executor')
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

    def _delivery_issue_context(self):
        issue = self.contract.get('delivery_issue')
        return 'Delivery issue context: ' + canonical(issue) + '\n' if issue is not None else ''

    @staticmethod
    def _prompt_worker(worker, prompt, **kwargs):
        """Keep older offline adapters usable while the real adapter gets reuse facts."""
        parameters = inspect.signature(worker.prompt).parameters.values()
        accepts_keywords = any(parameter.kind is inspect.Parameter.VAR_KEYWORD for parameter in parameters)
        if not accepts_keywords:
            names = {parameter.name for parameter in parameters}
            kwargs = {key: value for key, value in kwargs.items() if key in names}
        result = worker.prompt(prompt, **kwargs)
        # Task and repair consumers share this boundary: transport resolution is
        # not acceptance. Ordinary text remains the compatible completion path.
        if isinstance(result, TaskOutcome):
            explanation = result.explanation if isinstance(result.explanation, str) and result.explanation.strip() else 'no explanation returned'
            raise _UnsuccessfulOutcome(result.status, explanation)
        if isinstance(result, BaseException):
            raise result
        if result is None:
            raise Blocked('worker returned without completing the task; partial work retained')
        return result

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

    @staticmethod
    def _repair_source_state(project, paths):
        """Compare exact working bytes/modes before restoring failed-repair ownership."""
        result = {}
        for name in paths:
            path = safe_path(project, name)
            try:
                info = path.stat()
            except FileNotFoundError:
                result[name] = None
                continue
            if not stat.S_ISREG(info.st_mode):
                raise Blocked('repair source is not a regular file: ' + name + '; preserve it and inspect ownership before continuation')
            result[name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                            'mode': stat.S_IMODE(info.st_mode)}
        return result

    @staticmethod
    def _repair_index_state(project, paths):
        """Capture Git's staged entries for already-selected repair paths only."""
        result = {}
        for name in paths:
            entries = []
            for entry in git(project, 'ls-files', '--stage', '-z', '--', name).split(b'\0'):
                if entry:
                    entries.append(entry.split(b'\t', 1)[0].decode('ascii'))
            result[name] = entries
        return result

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
                'The runner executes/reruns configured required checks and creates the focused checkpoint; it does not own all '
                'semantic/manual acceptance or the reviewer verdict. Finish worker-owned semantic/manual acceptance, never stage '
                'or commit, bypass checks/hooks/signing, or adopt unrelated/pre-existing bytes.\n'
                + _DECISION_CONSTRAINTS + self.paid_authority() + '\nOriginal task contracts: '
                + canonical(original_tasks) + '\n' + self._delivery_issue_context())
            def prompt_fix(prompt, **kwargs):
                prompt = _IMPLEMENTATION_AUTHORITY + _ROUTINE_AUTHORITY + _COMPLETION_REPORTING + '\n' + repair_context + prompt
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
                    details = {'invocation_id': invocation_id, 'execution_id': execution_id,
                               'error': _safe_error(exc) or type(exc).__name__}
                    if isinstance(exc, _UnsuccessfulOutcome):
                        details.update({'diagnostic': exc.diagnostic, 'baseline': focused.base,
                                        'head': git(project, 'rev-parse', 'HEAD').decode().strip(),
                                        **focused.facts(),
                                        'source_state': self._repair_source_state(project, focused.task_edited | focused.known_artifacts),
                                        'index_state': self._repair_index_state(project, focused.task_edited | focused.known_artifacts)})
                    store.history(self.run, fix_task['id'], 'fixer_invocation', outcome, details)
                    recorder.emit(occurrence, 'worker', outcome, task_id=fix_task['id'], facts={
                        **public, 'stopped_by_invocation_id': invocation_id, 'error_category': _failure(exc)})
                    raise
                else:
                    store.history(self.run, fix_task['id'], 'fixer_invocation', 'returned',
                                  {'invocation_id': invocation_id, 'execution_id': execution_id,
                                   'baseline': focused.base, 'head': git(project, 'rev-parse', 'HEAD').decode().strip(),
                                   **focused.facts(), 'blobs': self._repair_blobs(project, focused.task_edited),
                                   'source_state': self._repair_source_state(project, focused.task_edited | focused.known_artifacts),
                                   'index_state': self._repair_index_state(project, focused.task_edited | focused.known_artifacts)})
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
            if recovered and recovered.get('diagnosis'):
                prompt += '\nInspected prior settled unsuccessful fixer diagnosis and targeted correction: ' + recovered['diagnosis']
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
                            'blobs': self._repair_blobs(project, focused.task_edited),
                            'source_state': self._repair_source_state(project, focused.task_edited | focused.known_artifacts),
                            'index_state': self._repair_index_state(project, focused.task_edited | focused.known_artifacts)})
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
                def retain_fix_intent(intent):
                    check_ref = store.db.execute("SELECT seq FROM execution_history WHERE run_id=? AND task_id IS NULL AND kind='fixer_checks' AND state='passed' ORDER BY seq DESC LIMIT 1", (self.run,)).fetchone()
                    if not check_ref:
                        raise Blocked('repair checkpoint lacks its passing check reference; rerun required checks')
                    store.history(self.run, None, 'fixer_checkpoint', 'started', {
                        **intent, 'execution_id': execution_id, 'check_ref': check_ref['seq'],
                        'checks': check_results})
                focused.before_checkpoint = retain_fix_intent
                focused.before_git_commit = lambda: store.history(self.run, None, 'fixer_checkpoint', 'attempting',
                                                                   {'execution_id': execution_id})
                try:
                    checkpoint = focused.checkpoint()
                except BaseException as exc:
                    recorder.emit(checkpoint_occurrence, 'checkpoint', 'failed', task_id=fix_task['id'], facts={
                        'baseline': focused.base, 'execution_id': execution_id, 'error_category': _failure(exc)})
                    checkpoint = focused.reconcile_checkpoint()
                    no_effect = (checkpoint is None and not (isinstance(exc, (KeyboardInterrupt, SystemExit))
                                 and getattr(focused, 'git_commit_started', False)))
                    store.history(self.run, None, 'fixer_checkpoint', 'failed',
                                  {'execution_id': execution_id, 'error': str(exc), 'no_effect': no_effect})
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
        """Reconcile one assigned repair; explicit failed returns need a diagnosis, never a blind replay."""
        project, store = self.authority.project, self.authority.store
        execution_id = item['execution_id']
        trigger = next((entry for entry in store.review_chain(self.run, private=True)['executions']
                        if entry['execution_id'] == item['trigger_execution_id']), None)
        if item['review_ordinal'] > 1:
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
        # Inspect every call for uncertainty, but select only the latest unresolved
        # stage. An earlier explicit failure must not replay a later returned call.
        if any(state not in ('returned', 'failed') for state, _ in calls.values()):
            raise Blocked('assigned repair invocation is uncertain or failed; inspect its recorded cause before targeted continuation')
        for state, facts in calls.values():
            if state == 'failed' and not (isinstance(facts.get('diagnostic'), str) and facts['diagnostic']):
                raise Blocked('assigned repair failure has no settled unsuccessful diagnosis; inspect its recorded call before continuation')
        if calls and list(calls.values())[-1][0] == 'failed':
            failure = list(calls.values())[-1][1]
            if not all(key in failure for key in ('paths', 'artifacts', 'baseline', 'head', 'source_state', 'index_state')):
                raise Blocked('settled repair failure lacks owned-path/index effect facts; inspect its retained effects without replaying the fixer')
            limits = [path for task in self.contract['tasks'] for path in task.get('owned_paths', [])]
            if any('owned_paths' in task for task in self.contract['tasks']) and any(
                    not any(name == path.rstrip('/') or name.startswith(path.rstrip('/') + '/') for path in limits)
                    for name in failure['paths']):
                raise Blocked('settled repair failure claimed paths outside original scope; inspect ownership before continuation')
            head = git(project, 'rev-parse', 'HEAD').decode().strip()
            selected = sorted(set(failure['paths']) | set(failure['artifacts']))
            if head != failure['head'] or self._repair_source_state(project, selected) != failure['source_state']:
                raise Blocked('settled repair failure target/source bytes drifted; preserve them and inspect ownership before continuation')
            if self._repair_index_state(project, selected) != failure['index_state']:
                raise Blocked('settled repair failure index entries drifted; preserve staged and working bytes and inspect ownership before continuation')
            # Explicit resume selects this same settled assignment, not an automatic
            # retry. Feed the actual cause and reconciled effects to its corrective
            # context; routine diagnosis never requires human terminal input.
            correction = (
                'The prior call explicitly returned unsuccessful, not an uncertain transport failure. '
                'Its retained head and selected source/artifact bytes still match Git. '
                'Inspect the actual failed call below and the retained partial diff before editing. '
                'Diagnose the reported unmet acceptance, make a concise targeted correction plan, and correct only '
                'that cause in this same assignment; never repeat the previous attempt unchanged. '
                'If no safe correction exists, report the actual blocker; do not ask the owner to debug routine errors. '
                'Required/manual acceptance is not waived. Actual failed fixer: ' + canonical(failure) +
                '\nRetained partial diff:\n' + (git(project, 'diff', 'HEAD', '--', *selected).decode() if selected else ''))
            return {'failed': True, 'baseline': failure['baseline'], 'invocations': list(calls),
                    'facts': {'paths': failure['paths'], 'artifacts': failure['artifacts']},
                    'diagnosis': correction}
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
        # Earlier local failures remain history, not stages of this returned
        # correction. Only reconcile checks/checkpoints begun after its return;
        # every call above still participates in the uncertain-call guard.
        returned_index = max(index for index, (kind, state, facts) in enumerate(events)
                             if kind == 'fixer_invocation' and state == 'returned'
                             and facts['invocation_id'] == returned['invocation_id'])
        local_events = events[returned_index + 1:]
        checkpoints = [(state, facts) for kind, state, facts in local_events if kind == 'fixer_checkpoint']
        check_events = [(state, facts) for kind, state, facts in local_events if kind == 'fixer_checks']
        checks = [state for state, _ in check_events]
        def verify_working_state(effects):
            if 'source_state' not in effects or 'index_state' not in effects:
                raise Blocked('returned repair lacks exact working-byte/mode or index facts; inspect its owned effects before restoring ownership without replaying the fixer')
            selected = set(returned['paths']) | set(returned['artifacts'])
            if self._repair_source_state(project, selected) != effects['source_state']:
                raise Blocked('returned repair source bytes drifted or file modes changed; preserve them and inspect ownership before continuation')
            if self._repair_index_state(project, selected) != effects['index_state']:
                raise Blocked('returned repair index entries drifted; preserve staged and working bytes and inspect ownership before continuation')
        if checkpoints:
            state, checkpoint = checkpoints[-1]
            latest_intent = next((facts for event_state, facts in reversed(checkpoints)
                                  if event_state == 'started' and 'entries' in facts), None)
            if latest_intent and state != 'passed' and not checkpoint.get('no_effect'):
                ref = store.db.execute("SELECT details FROM execution_history WHERE seq=? AND run_id=? AND kind='fixer_checks' AND state='passed'", (latest_intent.get('check_ref'), self.run)).fetchone()
                if not ref or json.loads(ref['details']).get('execution_id') != execution_id or not checks or checks[-1] != 'passed':
                    raise Blocked('repair checkpoint lacks its passing check reference; inspect retained history')
                focused = FocusedGit(project, {})
                if latest_intent.get('no_change') is True and not latest_intent.get('paths'):
                    checkpoint = {'baseline': latest_intent['baseline'], 'sha': latest_intent['parent'],
                                  'parent': None, 'paths': [], 'artifacts': latest_intent['artifacts'], 'no_change': True}
                else:
                    start_index = max(index for index, (event_state, _) in enumerate(checkpoints)
                                      if event_state == 'started')
                    attempted = any(event_state == 'attempting' for event_state, _ in checkpoints[start_index + 1:])
                    try:
                        if not attempted and head != latest_intent['parent']:
                            raise Blocked('repair checkpoint parent changed before Git attempt; preserve work and inspect Git effects')
                        checkpoint = focused.reconcile_intent(latest_intent)
                    except (KeyError, TypeError, ValueError) as exc:
                        raise Blocked('repair checkpoint intent is invalid; inspect retained history') from exc
                    if checkpoint is None:
                        if attempted:
                            raise Blocked('repair checkpoint outcome is uncertain at its attempted parent; inspect Git effects before continuation')
                        # No commit is visible. Restore the returned repair only when its
                        # full checked working state and the staged selection still match.
                        effects = check_events[-1][1]
                        selected = set(returned['paths']) | set(returned['artifacts'])
                        if self._repair_source_state(project, selected) != effects.get('source_state'):
                            raise Blocked('returned repair source bytes drifted; preserve them and inspect ownership before continuation')
                        unselected = selected - set(latest_intent['paths'])
                        expected_index = effects.get('index_state', {})
                        if self._repair_index_state(project, unselected) != {name: expected_index.get(name) for name in unselected}:
                            raise Blocked('returned repair index entries drifted; preserve them and inspect ownership before continuation')
                        actual_index = self._repair_index_state(project, latest_intent['paths'])
                        staged = {name: ([] if entry is None else [' '.join(entry) + ' 0'])
                                  for name, entry in latest_intent['entries'].items()}
                        checked = {name: expected_index.get(name) for name in latest_intent['paths']}
                        if actual_index != staged and actual_index != checked:
                            raise Blocked('repair checkpoint index entries drifted; preserve them and inspect ownership before continuation')
                        return recovered
                store.history(self.run, None, 'fixer_checkpoint', 'passed', {'execution_id': execution_id, **checkpoint})
                if item['review_ordinal'] > 1 and head != checkpoint['sha']:
                    raise Blocked('repair commit effects are missing or uncertain for the granted review target after HEAD advanced; recovered checkpoint retained, inspect target before continuation')
                store.review_outcome(self.run, execution_id, 'approved', findings=[],
                                     references={'base': review_base, 'head': head, 'commit': checkpoint['sha']})
                return None
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
                    verify_working_state(effects)
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
        verify_working_state(effects)
        if (effects.get('head') != head or self._repair_blobs(project, returned['paths']) != effects.get('blobs')):
            raise Blocked('returned repair source bytes drifted; preserve them and inspect ownership before continuation')
        return recovered

    @staticmethod
    def _review_value(text, *, require_coverage=False):
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
        pattern = re.compile(r'^\S+:\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*\s+-\s+\S')
        if any(not pattern.match(item.strip()) for item in findings):
            raise _ReviewFormat('review blocker needs a path:line or path:start-end[,start-end] location and concrete defect/impact')
        # Basis is described in ordinary defect prose, not a mandatory suffix.
        result = {'approved': value['approved'], 'findings': findings, 'suggestions': suggestions}
        if require_coverage or 'coverage' in value or 'coverage_gaps' in value:
            for key in ('coverage', 'coverage_gaps'):
                items = value.get(key)
                if not isinstance(items, list) or any(not isinstance(item, str) or not item.strip() for item in items):
                    raise _ReviewFormat('reviewer result needs coverage and coverage_gaps string lists; report examined/passing areas and unchecked or invalidated conclusions')
                result[key] = items
            if not result['coverage'] and not result['coverage_gaps']:
                result['coverage_gaps'] = ['No examined/passing coverage recorded; establish requested-change coverage before approval.']
            if result['coverage_gaps']:
                result['approved'] = False
        return result

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

    def _review_check_evidence(self, *, output_dir=None):
        """Give reviewers private retained check facts, never inferred completion claims."""
        rows = []
        for row in self.authority.store.db.execute(
                "SELECT seq,task_id,kind,state,details FROM execution_history WHERE run_id=? "
                "AND kind IN ('check','fixer_check','checkpoint','fixer_checkpoint') ORDER BY seq", (self.run,)):
            try:
                details = json.loads(row['details'])
            except (TypeError, ValueError):
                details = None
            rows.append({**dict(row), 'details': details})
        tasks = {task['id']: task for task in self.contract['tasks']}
        checkpoints = [row for row in rows if row['kind'] in ('checkpoint', 'fixer_checkpoint')
                       and row['state'] == 'passed' and isinstance(row['details'], dict)]
        sections = []
        for checkpoint in checkpoints:
            details, is_repair = checkpoint['details'], checkpoint['kind'] == 'fixer_checkpoint'
            execution_id = details.get('execution_id') if is_repair else None
            if is_repair:
                label = 'repair ' + (execution_id if isinstance(execution_id, str) and execution_id else 'unknown')
                required = [command for task in self.contract['tasks'] for command in commands(task)]
                attempts = [row for row in rows if row['kind'] == 'fixer_check' and row['seq'] < checkpoint['seq']
                            and isinstance(row['details'], dict) and row['details'].get('execution_id') == execution_id]
            else:
                task_id = checkpoint['task_id']
                label = 'task ' + str(task_id)
                required = commands(tasks[task_id]) if task_id in tasks else []
                attempts = [row for row in rows if row['kind'] == 'check' and row['task_id'] == task_id
                            and row['seq'] < checkpoint['seq'] and isinstance(row['details'], dict)]
            sha, parent, paths = details.get('sha'), details.get('parent'), details.get('paths')
            verified = isinstance(sha, str) and isinstance(parent, str) and isinstance(paths, list)
            if verified:
                try:
                    verified = (git(self.authority.project, 'rev-parse', sha + '^').decode().strip() == parent and
                                sorted(filter(None, git(self.authority.project, 'diff-tree', '--no-commit-id',
                                    '--name-only', '-r', '-z', sha).decode().split('\0'))) == sorted(paths))
                except Blocked:
                    verified = False
            association = ('verified checkpoint ' + str(sha) + ' (parent ' + str(parent) + ')' if verified else
                           'checkpoint association is missing or cannot be verified; do not infer it from HEAD')
            section = [label + ': ' + association + '.', 'Required commands: ' + canonical(required) + '.']
            if not required:
                section.append('No required command is configured for this checkpoint.')
            for configured in required:
                # Match the executable value retained by verification.run_checks,
                # including its supported command/argv object forms.
                command = configured.get('command', configured.get('argv')) if isinstance(configured, dict) else configured
                matching = [row for row in attempts if row['details'].get('command') == command]
                if not matching:
                    section.append('GAP: no retained execution for required command ' + canonical(command) + '.')
                    continue
                for attempt in matching:
                    fact = attempt['details']
                    output = fact.get('output')
                    if output_dir is None:
                        output_ref = canonical(output)
                    else:
                        if not isinstance(output, str):
                            raise Blocked('retained check output is missing or invalid; inspect required check history before review')
                        path = Path(output_dir) / ('check-' + str(attempt['seq']) + '.txt')
                        if not path.exists():
                            path.write_text(output, encoding='utf-8')
                        output_ref = 'private full output file ' + str(path)
                    section.append('Retained ' + attempt['state'] + ' execution: command ' + canonical(fact.get('command')) +
                                   ', exit ' + str(fact.get('exit_code')) + ', output ' + output_ref + '.')
                if not any(attempt['state'] == 'passed' for attempt in matching):
                    section.append('GAP: required command has no retained passing execution; a zero exit or clean tree is not substituted.')
            sections.append('\n'.join(section))
        if not sections:
            return ('Retained required-check evidence (private): no completed task/repair checkpoint has usable retained '
                    'check evidence; do not infer execution from worker text, clean tree, or exit status outside a retained attempt.')
        return ('Retained required-check evidence (private; raw command output must not enter status/monitor projections):\n' +
                '\n'.join('- ' + section.replace('\n', '\n  ') for section in sections))

    def _review_worker_evidence(self):
        """Return private completed-task reports, never unsuccessful invocation diagnostics."""
        rows = {row['task_id']: row for row in self.authority.store.db.execute(
            "SELECT task_id,state,result,details FROM execution_tasks WHERE run_id=?", (self.run,))}
        sections, applicable = [], []
        for task in self.contract['tasks']:
            task_id = task['id']
            row = rows.get(task_id)
            if row is None or row['state'] != 'complete':
                continue
            try:
                details = json.loads(row['details'])
            except (TypeError, ValueError):
                details = None
            summary = details.get('summary') if isinstance(details, dict) else None
            result = row['result']
            label = 'task ' + str(task_id) + ', result checkpoint ' + (result if isinstance(result, str) and result else 'unavailable')
            if isinstance(summary, str) and summary.strip() and isinstance(result, str) and result:
                sections.append('- ' + label + ': ' + canonical(summary))
                applicable.append([task_id, result, summary])
            else:
                sections.append('- ' + label + ': worker return unavailable.')
        return ('Completed task returns (private, worker-reported; not verified check passes or Git facts):\n' +
                ('\n'.join(sections) if sections else '- No completed task return available.')), applicable

    def _review_evidence_digest(self):
        """Keep the historical check-only digest when no usable return is available."""
        checks = self._review_check_evidence()
        _, returns = self._review_worker_evidence()
        evidence = checks if not returns else checks + '\nCompleted worker returns: ' + canonical(returns)
        return hashlib.sha256(evidence.encode()).hexdigest()

    def _review_attribution(self, review_base, head):
        """Describe verified run checkpoints without assigning intervening commits to a task."""
        project = self.authority.project
        retained = []
        for row in self.authority.store.db.execute(
                "SELECT task_id,kind,details FROM execution_history WHERE run_id=? "
                "AND kind IN ('checkpoint','fixer_checkpoint') AND state='passed' ORDER BY seq", (self.run,)):
            try:
                details = json.loads(row['details'])
            except (TypeError, ValueError):
                continue
            role = ('task ' + row['task_id']) if row['kind'] == 'checkpoint' else ('repair ' + str(details.get('execution_id', 'unknown')))
            retained.append((role, details))
        attributed, lines, gaps = set(), [], []
        for role, item in retained:
            sha, parent, paths, no_change = item.get('sha'), item.get('parent'), item.get('paths'), item.get('no_change')
            if no_change is True:
                lines.append('- ' + role + ': no commit changes (recorded checkpoint ' + str(sha) + '); this does not attribute HEAD or another commit.')
                continue
            if not (isinstance(sha, str) and isinstance(parent, str) and isinstance(paths, list) and
                    all(isinstance(path, str) for path in paths)):
                gaps.append('- ' + role + ': retained attribution is missing or ambiguous; ownership is unknown.')
                continue
            try:
                actual_parent = git(project, 'rev-parse', sha + '^').decode().strip()
                actual_paths = sorted(filter(None, git(project, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', sha).decode().split('\0')))
            except Blocked:
                gaps.append('- ' + role + ': retained commit cannot be verified; ownership is unknown.')
                continue
            if actual_parent != parent or actual_paths != sorted(paths):
                gaps.append('- ' + role + ': retained parent/paths do not match Git; ownership is unknown.')
                continue
            attributed.add(sha)
            lines.append('- ' + role + ': commit ' + sha + ', parent ' + parent + ', changed paths ' + canonical(actual_paths) + '.')
        commits = git(project, 'rev-list', '--reverse', review_base + '..' + head).decode().split()
        context = []
        for sha in commits:
            if sha in attributed:
                continue
            parent = git(project, 'rev-parse', sha + '^').decode().strip()
            paths = sorted(filter(None, git(project, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', sha).decode().split('\0')))
            context.append('- commit ' + sha + ', parent ' + parent + ', changed paths ' + canonical(paths) + '; no retained task/repair attribution: ownership unknown.')
        return ('Attributable task/repair checkpoints (verified against Git):\n' + ('\n'.join(lines) or '- none retained.') +
                '\nIntervening unrelated or unattributed integration context:\n' + ('\n'.join(context) or '- none.') +
                '\nMissing or ambiguous attribution:\n' + ('\n'.join(gaps) if gaps else '- none beyond the explicitly unknown intervening context above.'))

    def _review(self, *, recorder, review_base, head, ordinal, fixing_round=0,
                trigger_execution_id=None, predecessor_execution_id=None, input_checkpoints=None,
                execution_id=None, refresh_target=False, retry_limit=None):
        """Dispatch exactly one fresh read-only reviewer and retain its actual outcome."""
        store = self.authority.store
        execution_id = execution_id or uuid.uuid4().hex
        if refresh_target:
            refreshed = store.refresh_review_target_dispatch(self.run, execution_id, review_base=review_base,
                                                             review_head=head)
            ordinal, fixing_round = refreshed['review_ordinal'], refreshed['fixing_round']
            trigger_execution_id = predecessor_execution_id = refreshed['trigger_execution_id']
        elif retry_limit is None:
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
        # Retain the original base for authority/attribution, but review the repair
        # delta against the latest settled reviewer, never a fixer's self-assessment.
        previous = next((item for item in reversed(store.review_chain(self.run, private=True)['executions'])
                         if item['execution_id'] != execution_id and item['role'] == 'reviewer'
                         and item['state'] in ('approved', 'rejected') and not item['uncertain']), None)
        diff_base = review_base
        review_context = 'Initial review: examine the complete requested change and report actual passing coverage and all remaining coverage gaps.\n'
        evidence_reassessment = None
        if previous is not None:
            prior_head = previous['references'].get('head')
            if not isinstance(prior_head, str) or not prior_head:
                raise Blocked('prior review has no reviewed head; inspect retained review history before repair review')
            try:
                git(self.authority.project, 'merge-base', '--is-ancestor', prior_head, head)
            except Blocked:
                raise Blocked('prior reviewed head is not an ancestor of the current target; reconcile target drift before repair review') from None
            diff_base = prior_head
            prior_summary = previous['references'].get('review_summary')
            evidence_reassessment = store.evidence_reassessment_for_rejection(
                self.run, previous['execution_id'], review_base=review_base, review_head=head)
            review_context = (
                ('Evidence reassessment: independently evaluate only the prior outstanding evidence/coverage gaps and conclusions affected by the retained coordinator basis below. '
                 'Do not rereview unaffected passing work or infer unchecked original coverage. Coordinator basis: ' +
                 canonical({'diagnosis': evidence_reassessment['diagnosis'], 'evidence_digest': evidence_reassessment['evidence_digest']}) + '\n'
                 if evidence_reassessment is not None else '') +
                'Repair review: independently examine the actual changes since the prior reviewed head and their affected interactions. '
                'Confirm each addressed finding; retain unresolved findings. Carry forward previously examined, unaffected passing coverage, '
                'rather than rereviewing the original change wholesale. Revisit any earlier conclusion invalidated by the repair, '
                'explain why, and remove it from passing coverage until re-established. Inspect integration context as needed. '
                'Return cumulative coverage and remaining coverage_gaps, not merely coverage of this delta. '
                'A focused repair review must not certify unchecked original work: examine any outstanding gaps or leave them explicit and do not approve.\n'
                'Prior review: ' + canonical({'execution_id': previous['execution_id'], 'head': prior_head,
                    'findings': previous['findings'][-1] if previous['findings'] else [],
                    'summary': prior_summary if prior_summary is not None else {
                        'coverage': [], 'coverage_gaps': ['Historical review has no explicit coverage; establish original coverage before approval.']}}) + '\n')
        diff = git(self.authority.project, 'diff', '--no-ext-diff', '--no-textconv', diff_base + '..' + head).decode(errors='replace')
        evidence_dir = tempfile.mkdtemp(prefix='coherence-review-')
        retry_dispatched = False
        try:
            prompt = ('Independently review the actual committed range below against the requested tasks. '
                'You are read-only and are NOT the implementation conversation. Skills are disabled for this reviewer, '
                'so locate and read the canonical contract as a file with read/search tools; continue long reads with offsets. '
                + _DECISION_CONSTRAINTS + _ROUTINE_AUTHORITY + self.paid_authority()
                + 'Identify concrete correctness, scope or data-safety defects, not missing workflow ceremony. '
                'Return only JSON with boolean approved, findings, coverage, coverage_gaps, and optional suggestions string lists. '
                'Example: {"approved":true,"findings":[],"coverage":["area examined and why it works"],"coverage_gaps":[],"suggestions":[]}. '
                'For rejection use findings like "path:line[-end_line] - concrete defect, impact and accepted basis in ordinary prose". '
                'Always distinguish examined/passing areas from what must be fixed or remains unchecked. Never approve with coverage gaps. '
                'Use findings only for blockers: each needs a location, concrete impact, and basis of requirement, correctness, security, or data-safety. '
                'Put only nonblocking advice in suggestions; crashes, hangs, target/credential risks, and false-unavailable observations are blockers. Never approve when blockers exist.\n'
                + review_context +
                'Attribution below is integration context: do not reject unrelated context solely for task-path scope, and do not certify it as task delivery. Causal integration defects affecting the requested result remain blockers and must cite the interaction/accepted basis. Report independently unrelated defects with their ownership/repair limit; do not expand fixer authority.\n'
                'Evaluate retained check evidence semantically: distinguish actual passing execution, failed or missing required execution, and an inability to rerun because you are read-only. Do not invent a live check; a read-only inability to rerun does not negate a valid retained pass.\n'
                + self._delivery_issue_context() + 'Tasks: ' + canonical(self.contract['tasks']) + '\nOriginal range: ' + review_base + '..' + head +
                '\nReview delta: ' + diff_base + '..' + head + '\nDiff:\n' + diff + '\n' + self._review_attribution(review_base, head) +
                '\nFull check outputs are in the private files referenced below; read relevant files with the read tool and continue long reads with offsets. '
                + self._review_check_evidence(output_dir=evidence_dir) + '\n' + self._review_worker_evidence()[0])
            if retry_limit is not None:
                if len(prompt) > retry_limit:
                    raise Blocked('corrected review payload still exceeds the reported provider field limit; inspect retained evidence delivery')
                store.review_size_retry_dispatch(self.run, execution_id, review_base=review_base, review_head=head)
                retry_dispatched = True
            text = reviewer.prompt(prompt, read_only=True)
            value = self._review_value(text, require_coverage=True)
        except BaseException as exc:
            if retry_limit is not None and not retry_dispatched:
                raise
            state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
            store.review_outcome(self.run, execution_id, state, findings=[], suggestions=[],
                                 uncertainty=state != 'failed' or isinstance(exc, _ReviewFormat),
                                 references={'base': review_base, 'head': head,
                                             'failure_category': 'malformed' if isinstance(exc, _ReviewFormat) else _failure(exc)})
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
                                         'saved_session': getattr(reviewer, 'saved_session', None),
                                         'review_summary': {key: value[key] for key in ('coverage', 'coverage_gaps')},
                                         'check_evidence_digest': self._review_evidence_digest(),
                                         'diff_base': diff_base,
                                         'prior_review': previous['execution_id'] if previous else None})
        review_facts.update({'approved': value['approved'], 'outcome': state,
                             'finding_count': len(value['findings'])})
        recorder.emit(execution_id, 'review', 'passed' if state == 'approved' else 'failed', facts=review_facts)
        return execution_id, value, state

    def _recover_format_rejection(self, chain, review_base):
        """Recover only an explicitly supplied compatible completed initial review artifact."""
        items = chain['executions']
        if not self.resume or len(items) != 1:
            return False
        item = items[0]
        if (item['role'] != 'reviewer' or item['review_ordinal'] != 1 or item['fixing_round'] != 0 or
                item['state'] != 'failed' or not item['uncertain'] or item['attempt_count'] != 2 or
                item['references'].get('base') != review_base):
            return False
        head = item['references'].get('head')
        store = self.authority.store
        dispatch = store.db.execute('SELECT review_base,review_head,trigger_execution_id,predecessor_execution_id '
            'FROM execution_review_executions WHERE run_id=? AND execution_id=?',
            (self.run, item['execution_id'])).fetchone()
        attempts = store.db.execute('SELECT state,uncertainty FROM execution_review_attempts '
            'WHERE run_id=? AND execution_id=? ORDER BY seq', (self.run, item['execution_id'])).fetchall()
        if (dispatch is None or tuple(dispatch) != (review_base, head, None, None) or
                [tuple(row) for row in attempts] != [('dispatched', 0), ('failed', 1)]):
            raise Blocked('review recovery dispatch or failed attempt mismatch; inspect retained review history')
        # A retained failure category establishes the cause, not session identity.
        # Older attempts may have only an observation of that category.
        categories = [item['references'].get('failure_category')]
        observations = store.db.execute('SELECT facts FROM execution_observations WHERE run_id=? '
            "AND occurrence_id=? AND phase='review' AND kind='failed'", (self.run, item['execution_id'])).fetchall()
        for row in observations:
            try:
                categories.append(json.loads(row['facts']).get('error_category'))
            except (ValueError, TypeError, AttributeError):
                pass
        categories = [category for category in categories if category is not None]
        if not categories or any(category != 'malformed' for category in categories):
            raise Blocked('review recovery failure cause is not known to be format-related; inspect the original transport')
        project = self.authority.project
        if not isinstance(head, str) or git(project, 'rev-parse', 'HEAD').decode().strip() != head:
            raise Blocked('review recovery target drifted; inspect the original reviewed head before continuation')
        if git(project, 'status', '--porcelain=v1', '--untracked-files=no'):
            raise Blocked('review recovery target has tracked changes; preserve and reconcile them before continuation')
        path = self.question('A first read-only review has an uncertain failed outcome. If inspection found its exact completed '
            'reviewer transcript with a compound-location format failure, provide its path; otherwise leave empty to stop. '
            'The artifact will be checked against the original task scope, review range and committed diff; this does not '
            'assert a historically retained session link. Execution: ' + item['execution_id'])
        if not isinstance(path, str) or not path.strip():
            raise Blocked('review recovery needs the exact completed reviewer transcript; inspect the failed invocation')
        try:
            entries = [json.loads(line) for line in Path(path.strip()).read_text(encoding='utf-8').splitlines()]
            if len(entries) < 3 or entries[0].get('type') != 'session' or Path(entries[0].get('cwd', '')).resolve() != Path(project).resolve():
                raise ValueError('session or project mismatch')
            previous = None
            for entry in entries[1:]:
                if not isinstance(entry, dict) or not isinstance(entry.get('id'), str) or entry.get('parentId') != previous:
                    raise ValueError('ambiguous transcript chain')
                previous = entry['id']
            messages = [entry.get('message') for entry in entries if entry.get('type') == 'message']
            if not all(isinstance(message, dict) for message in messages):
                raise ValueError('invalid transcript message')
            users = [message for message in messages if message.get('role') == 'user']
            final = messages[-1]
            if len(users) != 1 or final.get('role') != 'assistant' or final.get('stopReason') != 'stop':
                raise ValueError('missing completed reviewer return')
            user_content, final_content = users[0].get('content'), final.get('content')
            if (not isinstance(user_content, list) or len(user_content) != 1 or user_content[0].get('type') != 'text' or
                    not isinstance(final_content, list) or len(final_content) != 1 or final_content[0].get('type') != 'text'):
                raise ValueError('ambiguous reviewer prompt or return')
            prompt, text = user_content[0]['text'], final_content[0]['text']
            if not isinstance(prompt, str) or not isinstance(text, str):
                raise ValueError('invalid reviewer prompt or return')
            for message in messages:
                if message.get('role') == 'assistant':
                    for part in message.get('content', []):
                        if part.get('type') == 'toolCall' and part.get('name') not in ('read', 'grep', 'find', 'ls'):
                            raise ValueError('review used a non-read-only tool')
            diff = git(project, 'diff', '--no-ext-diff', '--no-textconv', review_base + '..' + head).decode(errors='replace')
            scope = ('Tasks: ' + canonical(self.contract['tasks']) + '\nOriginal range: ' + review_base + '..' + head +
                     '\nReview delta: ' + review_base + '..' + head + '\nDiff:\n' + diff + '\n')
            if (not prompt.startswith('Independently review the actual committed range below against the requested tasks.') or
                    'You are read-only and are NOT the implementation conversation.' not in prompt or
                    'Initial review: examine the complete requested change' not in prompt or prompt.count(scope) != 1):
                raise ValueError('initial review scope, range, or diff mismatch')
            raw = text.strip()
            if raw.startswith('```') and raw.endswith('```'):
                raw = raw.split('\n', 1)[1].rsplit('```', 1)[0].strip()
            original = json.loads(raw)
            value = self._review_value(text, require_coverage=True)
            legacy = re.compile(r'^\S+:\d+(?:-\d+)?\s+-\s+\S')
            if (original.get('approved') is not False or not value['findings'] or
                    any(original.get(key) != value[key] for key in ('coverage', 'coverage_gaps')) or
                    all(legacy.match(finding.strip()) for finding in value['findings'])):
                raise ValueError('not an actionable compound-location rejection')
        except (OSError, UnicodeError, ValueError, TypeError, KeyError, IndexError, AttributeError, _ReviewFormat) as exc:
            raise Blocked('review recovery artifact is invalid or incompatible; inspect the exact completed reviewer transcript: ' + str(exc)) from None
        if git(project, 'rev-parse', 'HEAD').decode().strip() != head or git(project, 'status', '--porcelain=v1', '--untracked-files=no'):
            raise Blocked('review recovery target drifted during inspection; reconcile before continuation')
        store.review_outcome(self.run, item['execution_id'], 'rejected', findings=value['findings'],
            suggestions=value['suggestions'], references={'base': review_base, 'head': head,
                'review_summary': {key: value[key] for key in ('coverage', 'coverage_gaps')},
                'diff_base': review_base, 'prior_review': None,
                'recovery': 'coordinator supplied compatible completed initial review artifact; original session linkage not retained'})
        return True


    def recover_task(self, recovery, *, owner_authorized=False):
        """Verify/checkpoint an explicit external same-task completion; never replay its SDK call."""
        from .processes import inspect_recorded_writers
        if owner_authorized is not True:
            raise Blocked('external task recovery requires actual owner authorization; obtain it and supply --owner-authorized')
        project, store = self.authority.project, self.authority.store
        inspect_recorded_writers(store.db, 'external task recovery')
        saved = store.input(self.run)
        run = store.db.execute('SELECT state FROM execution_runs WHERE run_id=?', (self.run,)).fetchone()
        if not saved or not run or run['state'] not in ('failed', 'interrupted'):
            raise Blocked('external task recovery needs a retained failed/interrupted run; inspect status/history first')
        store.review_policy(self.run)
        if not isinstance(recovery, dict) or any(not isinstance(recovery.get(key), str) or not recovery[key].strip()
                for key in ('task_id', 'invocation_id', 'head', 'diagnosis', 'worker', 'summary')):
            raise Blocked('external task recovery needs task_id, invocation_id, head, inspected diagnosis, external worker attribution and acceptance summary; correct --recovery JSON')
        paths = recovery.get('paths')
        if not isinstance(paths, dict) or not paths or any(not isinstance(name, str) or not name or
                not isinstance(value, dict) or set(value) != {'sha256', 'mode'} or
                not isinstance(value['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', value['sha256']) or
                type(value['mode']) is not int for name, value in paths.items()):
            raise Blocked('external task recovery needs exact regular-file paths with sha256 and mode; correct the explicit transfer')
        task_id = recovery['task_id']
        task = next((task for task in saved['contract']['tasks'] if task['id'] == task_id), None)
        if task is None:
            raise Blocked('external recovery task is not in retained input; select the exact unfinished task')
        recovery_id = hashlib.sha256(canonical(recovery).encode()).hexdigest()
        prior = [(row['state'], json.loads(row['details'])) for row in store.db.execute(
            "SELECT state,details FROM execution_history WHERE run_id=? AND task_id=? AND kind='external_recovery' ORDER BY seq",
            (self.run, task_id))]
        completed = store.completed_checkpoints(self.run)
        if task_id in completed:
            if any(state == 'authorized' and facts.get('recovery_id') == recovery_id for state, facts in prior) and completed[task_id].get('external_recovery_id') == recovery_id:
                return completed[task_id]
            raise Blocked('external recovery cannot replace a completed task; retain its checkpoint')
        first = next((item['id'] for item in saved['contract']['tasks']
                      if item['id'] not in completed and all(dep in completed for dep in item.get('depends', []))), None)
        if first != task_id:
            raise Blocked('external recovery must checkpoint the next dependency-ready unfinished task; inspect retained progress')
        calls = {}
        for row in store.db.execute("SELECT state,details FROM execution_history WHERE run_id=? AND task_id=? AND kind='worker_invocation' ORDER BY seq", (self.run, task_id)):
            facts = json.loads(row['details'])
            calls[facts.get('invocation_id')] = (row['state'], facts)
        if not calls or any(state not in ('failed', 'interrupted', 'returned') for state, _ in calls.values()):
            raise Blocked('external recovery has uncertain worker terminal history; reconcile the saved invocation before transfer')
        last_id = next(reversed(calls))
        if last_id != recovery['invocation_id']:
            raise Blocked('external recovery invocation is not the latest inspected task call; correct the transfer reference')
        # A checkpoint may have completed before its result write. Reconcile only this
        # retained operation's exact parent, paths and content, never arbitrary HEAD.
        intent = next((facts for state, facts in reversed(prior) if state == 'checkpoint_started'), None)
        head = git(project, 'rev-parse', 'HEAD').decode().strip()
        if head != recovery['head']:
            if not intent or intent.get('recovery_id') != recovery_id:
                raise Blocked('external recovery HEAD drifted; inspect the target before a new exact transfer')
            focused = FocusedGit(project, {**task, 'handoff_paths': []})
            focused.base = recovery['head']
            focused.checkpoint_parent, focused.checkpoint_paths = recovery['head'], sorted(paths)
            checkpoint = focused.reconcile_checkpoint()
            if checkpoint is None or any(git(project, 'rev-parse', head + ':' + name).decode().strip() != blob
                                         for name, blob in intent['blobs'].items()):
                raise Blocked('external recovery checkpoint does not match retained intent; inspect actual Git effects without replay')
            checks = intent['checks']
        else:
            # No prior claim is restored here: every transferred byte is explicitly
            # selected anew by the owner, including same-task partial work.
            focused = FocusedGit(project, {**task, 'handoff_paths': sorted(paths)})
            focused.accept_completed_handoff(paths)
            index = self._repair_index_state(project, paths)
            store.history(self.run, task_id, 'external_recovery', 'authorized', {
                'recovery_id': recovery_id, 'decision': 'affirmative_actual_owner', 'transfer': recovery})
            manual_gates(task, self.question)
            checks = run_checks(project, task, lock_fd=self.authority.lock.fileno(),
                completed=lambda state, attempt: store.history(self.run, task_id, 'check', state, attempt))
            focused.accept_completed_handoff(paths)
            if git(project, 'rev-parse', 'HEAD').decode().strip() != recovery['head'] or self._repair_index_state(project, paths) != index:
                raise Blocked('external recovery target/index drifted during verification; inspect before checkpointing')
            blobs = self._repair_blobs(project, paths)
            store.history(self.run, task_id, 'external_recovery', 'checkpoint_started', {
                'recovery_id': recovery_id, 'checks': checks, 'blobs': blobs})
            try:
                checkpoint = focused.checkpoint()
            except BaseException:
                checkpoint = focused.reconcile_checkpoint()
                if checkpoint is None:
                    raise
            if any(git(project, 'rev-parse', checkpoint['sha'] + ':' + name).decode().strip() != blob
                   for name, blob in blobs.items()):
                raise Blocked('external recovery committed bytes differ from the transfer; inspect actual Git effects without replay')
        if self._repair_source_state(project, paths) != paths:
            raise Blocked('external recovery working bytes drifted at checkpoint; inspect actual Git effects before continuation')
        for name, expected in paths.items():
            mode = git(project, 'ls-tree', checkpoint['sha'], '--', name).split()[0].decode()
            if mode != ('100755' if expected['mode'] & 0o111 else '100644'):
                raise Blocked('external recovery committed mode differs for ' + name + '; inspect actual Git effects before continuation')
        summary = 'External recovery by ' + recovery['worker'] + ': ' + recovery['summary']
        checkpoint.update({'parent': recovery['head'], 'task_id': task_id, 'external_recovery_id': recovery_id})
        store.history(self.run, task_id, 'checkpoint', 'passed', checkpoint)
        store.task(self.run, task_id, 'complete', focused.base, checkpoint['sha'], {
            'summary': summary,
            'external_recovery_id': recovery_id, 'checks': checks, 'paths': checkpoint['paths'], 'generated_artifacts': []})
        store.history(self.run, task_id, 'external_recovery', 'completed', {'recovery_id': recovery_id, 'sha': checkpoint['sha']})
        return checkpoint

    def refresh_review_target(self):
        """Compatibility facade; target refresh uses the same graph transitions."""
        from .graph import run_graph
        return run_graph(self, action='refresh-review-target')

    def invoke(self):
        """Compatibility facade for the single graph controller; never replay legacy runs."""
        from .graph import run_graph
        recovery = self.worker_recovery or {}
        return run_graph(self, action=recovery.get("action"), diagnosis=recovery.get("diagnosis"))
