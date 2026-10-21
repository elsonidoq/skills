"""Sequential task/check/Git execution, with one fresh read-only final reviewer."""
import inspect
import json
import os

from .git_effects import FocusedGit
from .monitoring import Recorder, descriptor
from .pi_adapter import PiAdapter, terminal_question
from .processes import process_identity
from .sessions import select_session
from .store import Blocked, canonical, git
from .verification import CheckFailure, manual_gates, run_checks


def _failure(exc):
    if isinstance(exc, (KeyboardInterrupt, SystemExit)): return 'interrupted'
    return 'transport' if isinstance(exc, Blocked) else 'unknown'


_DECISION_CONSTRAINTS = (
    'Discover the canonical save-adr decision contract from the configured/installed suite and project routing, '
    'or use supplied relevant accepted constraints. Do not ignore known accepted constraints because the contract '
    'is unavailable; report the affected evidence gap without blocking unrelated legacy work. '
)

_ROUTINE_AUTHORITY = (
    'Routine authority: make ordinary scoped technical fixes; run isolated tests and local servers; perform necessary '
    'local/in-project dependency setup; and generate, rebuild, or selectively clean up current-task artifacts without '
    'an owner question. Do not ask merely because files changed. This authority is not proof that checks succeeded. '
    'A separately supplied paid scope applies only as supplied and is never inferred from credentials or task text. '
    'Ask only for product decisions, substantial planned-complexity increases, separately scoped paid usage, or actions '
    'outside this authority. It never authorizes global installs, credential changes, deployment, pushing, or deletion '
    'of unrelated or pre-existing work. '
)


class Engine:
    def __init__(self, authority, run, contract, executor, *, adapter=PiAdapter, question=terminal_question, paid_scope=None):
        self.authority, self.run, self.contract = authority, run, contract
        self.input_executor = executor
        self.executor = {key: value for key, value in executor.items() if key != 'reviewer'}
        self.reviewer_executor = executor.get('reviewer', self.executor)
        if not isinstance(self.reviewer_executor, dict) or any(
            not isinstance(self.reviewer_executor.get(key), str) or not self.reviewer_executor[key]
            for key in ('provider', 'model', 'effort')
        ):
            raise Blocked('reviewer needs provider, model and effort strings; correct the reviewer profile in --executor JSON')
        self.adapter, self.question, self.paid_scope = adapter, question, paid_scope
        # Private, run-local facts only. A failed or unfinished worker is never added.
        self.session_candidates = []
        self.session_settlement_sequence = 0

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
        return ('Paid scope approved for this unchanged run only: selected agent-provider(s): ' +
                ', '.join(self.paid_scope['agent_providers']) + '; application/test APIs: ' +
                (', '.join(self.paid_scope['apis']) if self.paid_scope['apis'] else 'none declared') +
                '. Do not expand this scope or ask again while it is unchanged. ')

    def invoke(self):
        project, store = self.authority.project, self.authority.store
        base = git(project, 'rev-parse', 'HEAD').decode().strip()
        requested_review_base = self.contract.get('review_base', base)
        if not isinstance(requested_review_base, str) or not requested_review_base:
            raise Blocked('review_base must be a Git commit')
        try:
            review_base = git(project, 'rev-parse', '--verify', requested_review_base + '^{commit}').decode().strip()
            git(project, 'merge-base', '--is-ancestor', review_base, base)
        except Blocked:
            raise Blocked('review_base must resolve to an ancestor of the run baseline') from None
        store.start(self.run, base, contract=self.contract, executor=self.input_executor,
                    authority={'paid_scope': self.paid_scope, 'routine_authority': True}, review_base=review_base)
        recorder = Recorder(store, self.run)
        try:
            identity = process_identity(os.getpid(), self.run)
        except Exception:
            identity = None
        recorder.register(descriptor(self.contract, self.executor, base), identity)
        terminal = recorder.occurrence()
        recorder.emit(terminal, 'terminal', 'started', facts={'baseline': base})
        checkpoints = []
        try:
            for task in self.contract['tasks']:
                preparation = recorder.occurrence()
                recorder.emit(preparation, 'prepare', 'started', task_id=task['id'])
                focused = None
                try:
                    focused = FocusedGit(project, task)
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
                    worker_occurrence = recorder.occurrence()
                    role = 'fixing_worker' if isinstance(self.contract.get('monitor'), dict) and self.contract['monitor'].get('correction_of') else 'worker'
                    recorder.emit(worker_occurrence, 'worker', 'started', task_id=task['id'], facts={'role': role})
                    question_occurrence = [None]
                    def worker_question(state):
                        mapping = {'requested': 'question_requested', 'returned': 'answer_returned', 'sent': 'answer_sent', 'delivery_failed': 'delivery_failed'}
                        if state == 'requested' or question_occurrence[0] is None:
                            question_occurrence[0] = recorder.occurrence()
                        recorder.emit(question_occurrence[0], 'worker', mapping[state], task_id=task['id'], facts={'parent_occurrence_id': worker_occurrence})
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
                    claimed_paths = set()
                    def claim(name):
                        if name not in claimed_paths:
                            focused.claim(name)
                            claimed_paths.add(name)
                    try:
                        text = self._prompt_worker(worker,
                            'Execute this one requested task in the current project. Read the relevant files, '
                            'make the smallest correct edits, run relevant actual project checks and fix ordinary '
                            'tool/read/argument/check errors in this conversation. Never stage or commit: the runner '
                            'will inspect and create the focused commit. Do not install, refresh credentials, '
                            'change global settings, delegate, or perform unrequested external operations. '
                            'Preserve all unrelated and pre-existing dirty work. Ask the owner for material scope '
                            'or permission questions. No new planning/evidence artifacts. '
                            'Return an honest concise summary and check outcomes.\n'
                            + _DECISION_CONSTRAINTS + _ROUTINE_AUTHORITY + self.paid_authority() + '\n'
                            'Select source edit and commit paths explicitly; preserve unknown and pre-existing bytes. '
                            'Generated outputs are cleanup guidance, never a registration or command prerequisite.\n'
                            'Task: ' + canonical(task), claim=claim, command=focused.command,
                            saved_session=selected['saved_session'] if selected else None, reuse_key=reuse_key)
                    except BaseException as exc:
                        state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                        recorder.emit(worker_occurrence, 'worker', state, task_id=task['id'], facts={'role': role, 'error_category': _failure(exc)})
                        store.history(self.run, task['id'], 'worker', state, {'role': role, 'error': str(exc)})
                        raise
                    recorder.emit(worker_occurrence, 'worker', 'returned', task_id=task['id'], facts={'role': role})
                    store.history(self.run, task['id'], 'worker', 'returned', {'role': role})
                    check_occurrences = {}
                    def check_observe(kind, ordinal, code):
                        occurrence = check_occurrences.setdefault(ordinal, recorder.occurrence())
                        facts = {'ordinal': ordinal}
                        if code is not None: facts['exit_code'] = code
                        recorder.emit(occurrence, 'check', kind, task_id=task['id'], facts=facts)
                    def run_required_checks():
                        return run_checks(project, task, lock_fd=self.authority.lock.fileno(), observe=check_observe)
                    def correct_required_checks():
                        nonlocal text
                        previous_failed_attempt = None
                        while True:
                            try:
                                checks = run_required_checks()
                                for attempt in checks:
                                    store.history(self.run, task['id'], 'check', 'passed', attempt)
                                return checks
                            except CheckFailure as failure:
                                if failure.attempt == previous_failed_attempt:
                                    raise Blocked('required check failed and remains unchanged after same-task correction: ' + canonical(failure.attempt))
                                previous_failed_attempt = failure.attempt
                                store.history(self.run, task['id'], 'check', 'failed', failure.attempt)
                                corrective_occurrence = recorder.occurrence()
                                recorder.emit(corrective_occurrence, 'worker', 'started', task_id=task['id'], facts={'role': role})
                                try:
                                    text = self._prompt_worker(worker,
                                        'A runner-owned REQUIRED check for this same task failed. Make a reasoned, '
                                        'authorized scoped source or local-setup correction if one is safe, then return. '
                                        'Do not claim success, skip the command, or ask merely because files changed. '
                                        'If no safe correction remains or a material decision is needed, state that blocker. '
                                        'The runner will rerun the affected required command before checkpointing.\n'
                                        'Actual failed attempt: ' + canonical(failure.attempt),
                                        claim=claim, command=focused.command, reuse_key=reuse_key)
                                except BaseException as exc:
                                    state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                                    recorder.emit(corrective_occurrence, 'worker', state, task_id=task['id'], facts={'role': role, 'error_category': _failure(exc)})
                                    store.history(self.run, task['id'], 'worker', state, {'role': role, 'correction': True, 'error': str(exc)})
                                    raise
                                recorder.emit(corrective_occurrence, 'worker', 'returned', task_id=task['id'], facts={'role': role})
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
                            corrective_occurrence = recorder.occurrence()
                            recorder.emit(corrective_occurrence, 'worker', 'started', task_id=task['id'], facts={'role': role})
                            try:
                                text = self._prompt_worker(worker,
                                    'A runner-owned checkpoint for this same task failed. Make a reasoned, authorized '
                                    'scoped correction if one is safe. Do not bypass hooks or signing, reset, rebase, '
                                    'or adopt unrelated work. The runner will rerun affected REQUIRED checks and the '
                                    'checkpoint with normal Git configuration intact.\nActual checkpoint error: ' + str(exc),
                                    claim=claim, command=focused.command, reuse_key=reuse_key)
                            except BaseException as correction_error:
                                correction_state = 'interrupted' if isinstance(correction_error, (KeyboardInterrupt, SystemExit)) else 'failed'
                                recorder.emit(corrective_occurrence, 'worker', correction_state, task_id=task['id'], facts={'role': role, 'error_category': _failure(correction_error)})
                                store.history(self.run, task['id'], 'worker', correction_state, {'role': role, 'correction': True, 'error': str(correction_error)})
                                raise
                            recorder.emit(corrective_occurrence, 'worker', 'returned', task_id=task['id'], facts={'role': role})
                            store.history(self.run, task['id'], 'worker', 'returned', {'role': role, 'correction': True})
                            checks = correct_required_checks()
                            continue
                        break
                    checkpoint['parent'] = (None if checkpoint['no_change'] else
                                            git(project, 'rev-parse', checkpoint['sha'] + '^').decode().strip())
                    recorder.emit(checkpoint_occurrence, 'checkpoint', 'passed', task_id=task['id'], facts={'baseline': focused.base, 'head': checkpoint['sha'], 'no_change': checkpoint['no_change']})
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
            head = git(project, 'rev-parse', 'HEAD').decode().strip()
            diff = git(project, 'diff', '--no-ext-diff', '--no-textconv', review_base + '..' + head).decode(errors='replace')
            reviewer_occurrence = recorder.occurrence()
            # Required ordinary chain history, not optional monitoring, records the actual
            # invocation before launch so an uncertain reviewer cannot be replayed.
            store.review_dispatch(self.run, reviewer_occurrence, role='reviewer', review_ordinal=1,
                                  fixing_round=0, review_base=review_base, review_head=head)
            recorder.emit(reviewer_occurrence, 'review', 'started', facts={
                'role': 'reviewer', 'execution_id': reviewer_occurrence, 'review_ordinal': 1,
                'review_base': review_base, 'review_head': head,
            })
            review_question_occurrence = [None]
            def review_question(state):
                mapping = {'requested': 'question_requested', 'returned': 'answer_returned', 'sent': 'answer_sent', 'delivery_failed': 'delivery_failed'}
                if state == 'requested' or review_question_occurrence[0] is None:
                    review_question_occurrence[0] = recorder.occurrence()
                recorder.emit(review_question_occurrence[0], 'review', mapping[state], facts={'parent_occurrence_id': reviewer_occurrence})
            reviewer = self.adapter(project, self.reviewer_executor, question=self.question, observe_question=review_question)
            reviewer.lock_fd = self.authority.lock.fileno()
            try:
                review = reviewer.prompt('Independently review the actual committed range below against the requested tasks. You are read-only and are NOT the implementation conversation. Skills are disabled for this reviewer, so locate and read the canonical contract as a file with read/search tools; continue long reads with offsets. ' + _DECISION_CONSTRAINTS + _ROUTINE_AUTHORITY + self.paid_authority() + 'Identify concrete correctness, scope or data-safety defects, not missing workflow ceremony. Return only a JSON object {"approved":true,"findings":[]} or {"approved":false,"findings":["path:line - defect"]}. Never approve if there is a material unresolved finding.\nTasks: ' + canonical(self.contract['tasks']) + '\nRange: ' + review_base + '..' + head + '\nDiff:\n' + diff, read_only=True)
            except BaseException as exc:
                store.review_outcome(self.run, reviewer_occurrence, 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed',
                                     findings=[], uncertainty=True, references={'base': review_base, 'head': head})
                recorder.emit(reviewer_occurrence, 'review', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', facts={
                    'role': 'reviewer', 'execution_id': reviewer_occurrence, 'review_ordinal': 1,
                    'review_base': review_base, 'review_head': head,
                    'outcome': 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed',
                    'error_category': _failure(exc),
                })
                raise
            try:
                value = json.loads(review)
            except ValueError:
                store.review_outcome(self.run, reviewer_occurrence, 'failed', findings=[], references={'base': review_base, 'head': head})
                recorder.emit(reviewer_occurrence, 'review', 'failed', facts={
                    'role': 'reviewer', 'execution_id': reviewer_occurrence, 'review_ordinal': 1,
                    'review_base': review_base, 'review_head': head, 'outcome': 'failed', 'error_category': 'malformed',
                })
                raise Blocked('reviewer returned invalid JSON; review remains incomplete: ' + review) from None
            if (not isinstance(value, dict) or type(value.get('approved')) is not bool or not isinstance(value.get('findings'), list) or any(not isinstance(f, str) for f in value['findings'])):
                store.review_outcome(self.run, reviewer_occurrence, 'failed', findings=[], references={'base': review_base, 'head': head})
                recorder.emit(reviewer_occurrence, 'review', 'failed', facts={
                    'role': 'reviewer', 'execution_id': reviewer_occurrence, 'review_ordinal': 1,
                    'review_base': review_base, 'review_head': head, 'outcome': 'failed', 'error_category': 'malformed',
                })
                raise Blocked('reviewer result needs boolean approved and a list of findings')
            review_state = 'approved' if value['approved'] and not value['findings'] else 'rejected'
            store.review_outcome(self.run, reviewer_occurrence, review_state, findings=value['findings'],
                                 references={'base': review_base, 'head': head})
            recorder.emit(reviewer_occurrence, 'review', 'passed' if review_state == 'approved' else 'failed', facts={
                'role': 'reviewer', 'execution_id': reviewer_occurrence, 'review_ordinal': 1,
                'review_base': review_base, 'review_head': head, 'approved': value['approved'],
                'outcome': review_state, 'finding_count': len(value['findings']),
            })
            if not value['approved'] or value['findings']:
                raise Blocked('independent review findings (commits retained): ' + canonical(value))
            store.finish(self.run, 'complete', head)
            recorder.emit(terminal, 'terminal', 'passed', facts={'head': head})
            return {'status': 'complete', 'run_id': self.run, 'baseline': base, 'sha': head, 'checkpoints': checkpoints, 'review': value}
        except BaseException as exc:
            head = git(project, 'rev-parse', 'HEAD').decode().strip()
            store.finish(self.run, 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', head, str(exc))
            recorder.emit(terminal, 'terminal', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', facts={'head': head, 'error_category': _failure(exc)})
            raise
