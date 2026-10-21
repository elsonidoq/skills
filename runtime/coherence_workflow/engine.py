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
from .verification import CheckFailure, commands, manual_gates, run_checks


class _ReviewFormat(Blocked):
    """An actual reviewer response could not safely yield a verdict."""


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
    def __init__(self, authority, run, contract, executor, *, adapter=PiAdapter, question=terminal_question, paid_scope=None, resume=False):
        self.authority, self.run, self.contract, self.resume = authority, run, contract, resume
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

    def run_fix(self, findings, *, trigger_execution_id, review_base, recorder, execution_id):
        """Run the one already-authorized review repair without routing another workflow.

        The caller supplies the actual first-review execution and fixer identity.  This
        method deliberately leaves original task rows/checkpoints alone: it records a
        distinct fixer execution, its scoped checks, and its focused repair checkpoint.
        """
        if (not isinstance(findings, list) or not findings or any(not isinstance(item, str) or not item for item in findings)
                or not isinstance(trigger_execution_id, str) or not trigger_execution_id
                or not isinstance(execution_id, str) or not execution_id):
            raise Blocked('fixing execution needs actionable findings and explicit execution IDs')
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
        store.review_dispatch(self.run, execution_id, role='fixer', review_ordinal=1, fixing_round=1,
                              trigger_execution_id=trigger_execution_id, predecessor_execution_id=trigger_execution_id,
                              review_base=review_base, review_head=head)
        recorder.emit(execution_id, 'worker', 'started', task_id=fix_task['id'], facts={
            'role': 'fixing_worker', 'execution_id': execution_id,
            'trigger_execution_id': trigger_execution_id, 'predecessor_execution_id': trigger_execution_id,
        })
        focused = FocusedGit(project, fix_task)
        claimed_paths = set()
        def claim(name):
            if name not in claimed_paths:
                focused.claim(name)
                claimed_paths.add(name)
        def gate_question(text):
            return self.question(text)
        try:
            manual_gates(fix_task, gate_question)
            request, reuse_key = self._session_request(fix_task, 'fixing_worker')
            selection = select_session(request, self.session_candidates)
            selected = next((candidate for candidate in self.session_candidates
                             if candidate['id'] == selection['session_id']), None)
            store.history(self.run, None, 'fixer', 'selected', {'execution_id': execution_id,
                          'trigger_execution_id': trigger_execution_id, 'session_id': selection['session_id'],
                          'reason': selection['reason'], 'rejected': selection['rejected']})
            worker = self.adapter(project, self.executor, question=self.question)
            worker.lock_fd = self.authority.lock.fileno()
            prompt = ('Correct the actionable findings from one independent review within the original approved '
                      'task contracts. This is the one assigned fixing round, not a new task, routing operation, '
                      'or permission expansion. Keep the configured executor and authority. Select only explicit '
                      'source/artifact paths from those contracts; preserve unrelated and pre-existing bytes. Run '
                      'applicable required checks. Never stage or commit: the runner owns the focused repair checkpoint.\n'
                      + _DECISION_CONSTRAINTS + _ROUTINE_AUTHORITY + self.paid_authority() + '\n'
                      'Original task contracts: ' + canonical(original_tasks) + '\nActionable findings: ' + canonical(findings))
            text = self._prompt_worker(worker, prompt, claim=claim, command=focused.command,
                                       saved_session=selected['saved_session'] if selected else None, reuse_key=reuse_key)
            recorder.emit(execution_id, 'worker', 'returned', task_id=fix_task['id'], facts={
                'role': 'fixing_worker', 'execution_id': execution_id,
                'trigger_execution_id': trigger_execution_id, 'predecessor_execution_id': trigger_execution_id,
            })
            store.usage_interval(self.run, execution_id, role='fixing_worker', outcome='settled',
                                 interval=getattr(worker, 'last_interval', None))
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
                        results = run_checks(project, fix_task, lock_fd=self.authority.lock.fileno(), observe=observe,
                            completed=lambda state, attempt: store.history(self.run, None, 'fixer_check', state,
                                {'execution_id': execution_id, **attempt}))
                        return results
                    except CheckFailure as failure:
                        if failure.attempt == previous:
                            raise Blocked('fixing required check remains unchanged after scoped correction: ' + canonical(failure.attempt))
                        previous = failure.attempt
                        text = self._prompt_worker(worker,
                            'A runner-owned REQUIRED check in this assigned fixing round failed. Make a reasoned, '
                            'authorized scoped correction, then return; the runner will rerun the affected command '
                            'before checkpointing. Do not skip it, claim success, start another fixing round, or adopt '
                            'unrelated work. Actual failed attempt: ' + canonical(failure.attempt),
                            claim=claim, command=focused.command, reuse_key=reuse_key)
            check_results = correct_checks()
            checkpoint_error = None
            while True:
                checkpoint_occurrence = recorder.occurrence()
                recorder.emit(checkpoint_occurrence, 'checkpoint', 'started', task_id=fix_task['id'], facts={
                    'baseline': focused.base, 'execution_id': execution_id})
                try:
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
                    text = self._prompt_worker(worker,
                        'A runner-owned focused repair checkpoint failed. Make a reasoned authorized scoped correction; '
                        'do not bypass hooks/signing or adopt unrelated work. The runner will rerun affected required '
                        'checks and checkpoint. Actual checkpoint error: ' + str(exc),
                        claim=claim, command=focused.command, reuse_key=reuse_key)
                    check_results = correct_checks()
                    continue
                break
            checkpoint['parent'] = (None if checkpoint['no_change'] else
                                    git(project, 'rev-parse', checkpoint['sha'] + '^').decode().strip())
            store.history(self.run, None, 'fixer_checkpoint', 'passed', {'execution_id': execution_id, **checkpoint})
            recorder.emit(checkpoint_occurrence, 'checkpoint', 'passed', task_id=fix_task['id'], facts={
                'baseline': focused.base, 'head': checkpoint['sha'], 'no_change': checkpoint['no_change'],
                'execution_id': execution_id})
            head = git(project, 'rev-parse', 'HEAD').decode().strip()
            store.review_outcome(self.run, execution_id, 'approved', findings=[],
                                 references={'base': review_base, 'head': head, 'commit': checkpoint['sha']})
            self._settle_session(fix_task, worker, request, reuse_key, checkpoint)
            return {'execution_id': execution_id, 'checkpoint': checkpoint, 'checks': check_results, 'summary': text}
        except BaseException as exc:
            outcome = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
            store.review_outcome(self.run, execution_id, outcome, findings=[], uncertainty=False,
                                 references={'base': review_base, 'head': git(project, 'rev-parse', 'HEAD').decode().strip()})
            recorder.emit(execution_id, 'worker', outcome, task_id=fix_task['id'], facts={
                'role': 'fixing_worker', 'execution_id': execution_id,
                'trigger_execution_id': trigger_execution_id, 'predecessor_execution_id': trigger_execution_id,
                'error_category': _failure(exc),
            })
            raise

    @staticmethod
    def _review_value(text):
        """Parse only an actual reviewer verdict; fenced JSON is a safe normalization."""
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
        if (not isinstance(value, dict) or type(value.get('approved')) is not bool
                or not isinstance(value.get('findings'), list)
                or any(not isinstance(item, str) or not item.strip() for item in value['findings'])):
            raise _ReviewFormat('reviewer result needs boolean approved and a nonempty-string list of findings')
        return value

    def _review(self, *, recorder, review_base, head, ordinal, fixing_round=0,
                trigger_execution_id=None, predecessor_execution_id=None):
        """Dispatch exactly one fresh read-only reviewer and retain its actual outcome."""
        store = self.authority.store
        execution_id = recorder.occurrence()
        store.review_dispatch(self.run, execution_id, role='reviewer', review_ordinal=ordinal,
                              fixing_round=fixing_round, trigger_execution_id=trigger_execution_id,
                              predecessor_execution_id=predecessor_execution_id,
                              review_base=review_base, review_head=head)
        review_facts = {
            'role': 'reviewer', 'execution_id': execution_id, 'review_ordinal': ordinal,
            'review_base': review_base, 'review_head': head,
        }
        if trigger_execution_id is not None:
            review_facts['trigger_execution_id'] = trigger_execution_id
            review_facts['predecessor_execution_id'] = predecessor_execution_id
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
                'Return only a JSON object {"approved":true,"findings":[]} or '
                '{"approved":false,"findings":["path:line - defect"]}. Never approve if there is a material unresolved finding.\n'
                'Tasks: ' + canonical(self.contract['tasks']) + '\nRange: ' + review_base + '..' + head + '\nDiff:\n' + diff,
                read_only=True)
            value = self._review_value(text)
        except BaseException as exc:
            state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
            store.review_outcome(self.run, execution_id, state, findings=[], uncertainty=state != 'failed',
                                 references={'base': review_base, 'head': head})
            recorder.emit(execution_id, 'review', state, facts={
                'role': 'reviewer', 'execution_id': execution_id, 'review_ordinal': ordinal,
                'review_base': review_base, 'review_head': head, 'outcome': state,
                'error_category': 'malformed' if isinstance(exc, _ReviewFormat) else _failure(exc),
            })
            store.usage_interval(self.run, execution_id, role='reviewer', outcome=state,
                                 interval=getattr(reviewer, 'last_interval', None))
            raise
        store.usage_interval(self.run, execution_id, role='reviewer', outcome='settled',
                             interval=getattr(reviewer, 'last_interval', None))
        state = 'approved' if value['approved'] and not value['findings'] else 'rejected'
        store.review_outcome(self.run, execution_id, state, findings=value['findings'],
                             references={'base': review_base, 'head': head})
        review_facts.update({'approved': value['approved'], 'outcome': state,
                             'finding_count': len(value['findings'])})
        recorder.emit(execution_id, 'review', 'passed' if state == 'approved' else 'failed', facts=review_facts)
        return execution_id, value, state

    def _finish_reviews(self, *, recorder, terminal, checkpoints, base, review_base):
        """Continue the one persisted review/fix chain without consuming a new slot."""
        store = self.authority.store
        chain = store.review_chain(self.run, private=True)
        if chain['uncertain']:
            raise Blocked('review invocation outcome is uncertain; inspect it before any replay')
        reviews = [item for item in chain['executions'] if item['role'] == 'reviewer']
        fixers = [item for item in chain['executions'] if item['role'] == 'fixer']
        head = git(self.authority.project, 'rev-parse', 'HEAD').decode().strip()
        if not reviews:
            review_id, review, state = self._review(recorder=recorder, review_base=review_base, head=head, ordinal=1)
        else:
            review_id, review, state = reviews[0]['execution_id'], {'approved': reviews[0]['state'] == 'approved',
                'findings': reviews[0]['findings'][-1] if reviews[0].get('findings') else []}, reviews[0]['state']
        if not reviews:
            reviews = [item for item in store.review_chain(self.run, private=True)['executions'] if item['role'] == 'reviewer']
        if state == 'approved':
            if len(reviews) != 1:
                raise Blocked('review chain has no eligible completion stage')
            store.finish(self.run, 'complete', head)
            recorder.emit(terminal, 'terminal', 'passed', facts={'head': head})
            return {'status': 'complete', 'run_id': self.run, 'baseline': base, 'sha': head,
                    'checkpoints': checkpoints, 'review': review, 'usage': store.usage_summary(self.run)}
        if state != 'rejected' or review['approved'] or not review['findings']:
            raise Blocked('independent review was not an actionable rejection (commits retained): ' + canonical(review))
        if not fixers:
            fix_id = recorder.occurrence()
            self.run_fix(review['findings'], trigger_execution_id=review_id, review_base=review_base,
                         recorder=recorder, execution_id=fix_id)
            fixers = [item for item in store.review_chain(self.run, private=True)['executions'] if item['role'] == 'fixer']
        fixer = fixers[0]
        if fixer['state'] != 'approved':
            raise Blocked('fixing round remains incomplete or failed; commits retained')
        if len(reviews) == 1:
            head = git(self.authority.project, 'rev-parse', 'HEAD').decode().strip()
            _, final_review, final_state = self._review(recorder=recorder, review_base=review_base, head=head,
                                                         ordinal=2, fixing_round=1,
                                                         trigger_execution_id=fixer['execution_id'], predecessor_execution_id=fixer['execution_id'])
        else:
            final_review, final_state = {'approved': reviews[1]['state'] == 'approved',
                'findings': reviews[1]['findings'][-1] if reviews[1].get('findings') else []}, reviews[1]['state']
        if final_state != 'approved':
            raise Blocked('independent final review findings (commits retained): ' + canonical(final_review))
        store.finish(self.run, 'complete', head)
        recorder.emit(terminal, 'terminal', 'passed', facts={'head': head})
        return {'status': 'complete', 'run_id': self.run, 'baseline': base, 'sha': head,
                'checkpoints': checkpoints, 'review': final_review, 'usage': store.usage_summary(self.run)}

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
                        authority={'paid_scope': self.paid_scope, 'routine_authority': True}, review_base=review_base)
        recorder = Recorder(store, self.run)
        try:
            identity = process_identity(os.getpid(), self.run)
        except Exception:
            identity = None
        if not self.resume:
            recorder.register(descriptor(self.contract, self.executor, base), identity)
        checkpoints = list(recovered.values())
        terminal = recorder.occurrence()
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
                    worker_occurrence = recorder.occurrence()
                    role = 'fixing_worker' if isinstance(self.contract.get('monitor'), dict) and self.contract['monitor'].get('correction_of') else 'worker'
                    recorder.emit(worker_occurrence, 'worker', 'started', task_id=task['id'], facts={'role': role})
                    # Membership is one dispatched (run, task) pair, independent of
                    # corrective prompts and never inferred from review references.
                    store.usage_membership(self.run, task['id'])
                    def record_usage(occurrence, outcome):
                        # Optional telemetry must not replace the task/check/Git outcome.
                        store.usage_interval(self.run, occurrence, task=task['id'], role=role,
                                             outcome=outcome, interval=getattr(worker, 'last_interval', None))
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
                            store.history(self.run, task['id'], 'mutation', 'claimed', focused.facts())
                            claimed_paths.add(name)
                    def command(phase, call):
                        focused.command(phase, call)
                        store.history(self.run, task['id'], 'tool_command',
                                      'started' if phase == 'start' else 'returned',
                                      {'call': call})
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
                            'Task: ' + canonical(task), claim=claim, command=command,
                            cleanup=focused.cleanup_artifact, saved_session=selected['saved_session'] if selected else None, reuse_key=reuse_key)
                    except BaseException as exc:
                        state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                        recorder.emit(worker_occurrence, 'worker', state, task_id=task['id'], facts={'role': role, 'error_category': _failure(exc)})
                        store.history(self.run, task['id'], 'worker', state, {'role': role, 'error': str(exc)})
                        record_usage(worker_occurrence, state)
                        raise
                    recorder.emit(worker_occurrence, 'worker', 'returned', task_id=task['id'], facts={'role': role})
                    record_usage(worker_occurrence, 'settled')
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
                                        claim=claim, command=command, cleanup=focused.cleanup_artifact, reuse_key=reuse_key)
                                except BaseException as exc:
                                    state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                                    recorder.emit(corrective_occurrence, 'worker', state, task_id=task['id'], facts={'role': role, 'error_category': _failure(exc)})
                                    store.history(self.run, task['id'], 'worker', state, {'role': role, 'correction': True, 'error': str(exc)})
                                    record_usage(corrective_occurrence, state)
                                    raise
                                recorder.emit(corrective_occurrence, 'worker', 'returned', task_id=task['id'], facts={'role': role})
                                record_usage(corrective_occurrence, 'settled')
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
                                    claim=claim, command=command, cleanup=focused.cleanup_artifact, reuse_key=reuse_key)
                            except BaseException as correction_error:
                                correction_state = 'interrupted' if isinstance(correction_error, (KeyboardInterrupt, SystemExit)) else 'failed'
                                recorder.emit(corrective_occurrence, 'worker', correction_state, task_id=task['id'], facts={'role': role, 'error_category': _failure(correction_error)})
                                store.history(self.run, task['id'], 'worker', correction_state, {'role': role, 'correction': True, 'error': str(correction_error)})
                                record_usage(corrective_occurrence, correction_state)
                                raise
                            recorder.emit(corrective_occurrence, 'worker', 'returned', task_id=task['id'], facts={'role': role})
                            record_usage(corrective_occurrence, 'settled')
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
            return self._finish_reviews(recorder=recorder, terminal=terminal, checkpoints=checkpoints,
                                        base=base, review_base=review_base)
        except BaseException as exc:
            head = git(project, 'rev-parse', 'HEAD').decode().strip()
            store.finish(self.run, 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', head, str(exc))
            recorder.emit(terminal, 'terminal', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', facts={'head': head, 'error_category': _failure(exc)})
            raise
