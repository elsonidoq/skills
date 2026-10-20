"""Sequential task/check/Git execution, with one fresh read-only final reviewer."""
import json
import os

from .git_effects import FocusedGit
from .monitoring import Recorder, descriptor
from .pi_adapter import PiAdapter, terminal_question
from .processes import process_identity
from .store import Blocked, canonical, git
from .verification import manual_gates, run_checks


class Engine:
    def __init__(self, authority, run, contract, executor, *, adapter=PiAdapter, question=terminal_question):
        self.authority, self.run, self.contract = authority, run, contract
        self.executor, self.adapter, self.question = executor, adapter, question

    def invoke(self):
        project, store = self.authority.project, self.authority.store
        base = git(project, 'rev-parse', 'HEAD').decode().strip()
        store.start(self.run, base)
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
                    worker = self.adapter(project, self.executor, question=self.question, observe_question=worker_question)
                    worker.lock_fd = self.authority.lock.fileno()
                    try:
                        text = worker.prompt(
                            'Execute this one requested task in the current project. Read the relevant files, '
                            'make the smallest correct edits, run relevant actual project checks and fix ordinary '
                            'tool/read/argument/check errors in this conversation. Never stage or commit: the runner '
                            'will inspect and create the focused commit. Do not install, refresh credentials, '
                            'change global settings, delegate, or perform unrequested external operations. '
                            'Preserve all unrelated and pre-existing dirty work. Ask the owner for material scope '
                            'or permission questions. No new planning/evidence artifacts. '
                            'Return an honest concise summary and check outcomes.\n'
                            'Pre-existing dirty paths (do not edit): ' + canonical(sorted(focused.dirty)) + '\n'
                            'Task: ' + canonical(task), claim=focused.claim, command=focused.command)
                    except BaseException as exc:
                        recorder.emit(worker_occurrence, 'worker', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', task_id=task['id'], facts={'role': role, 'error_category': type(exc).__name__})
                        raise
                    recorder.emit(worker_occurrence, 'worker', 'returned', task_id=task['id'], facts={'role': role})
                    focused.command('start', 'runner-checks')
                    check_occurrences = {}
                    def check_observe(kind, ordinal, code):
                        occurrence = check_occurrences.setdefault(ordinal, recorder.occurrence())
                        facts = {'ordinal': ordinal}
                        if code is not None: facts['exit_code'] = code
                        recorder.emit(occurrence, 'check', kind, task_id=task['id'], facts=facts)
                    checks = run_checks(project, task, lock_fd=self.authority.lock.fileno(), observe=check_observe)
                    focused.command('end', 'runner-checks')
                    checkpoint_occurrence = recorder.occurrence()
                    recorder.emit(checkpoint_occurrence, 'checkpoint', 'started', task_id=task['id'], facts={'baseline': focused.base})
                    try:
                        checkpoint = focused.checkpoint()
                    except BaseException as exc:
                        recorder.emit(checkpoint_occurrence, 'checkpoint', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', task_id=task['id'], facts={'baseline': focused.base, 'error_category': type(exc).__name__})
                        raise
                    recorder.emit(checkpoint_occurrence, 'checkpoint', 'passed', task_id=task['id'], facts={'baseline': focused.base, 'head': checkpoint['sha'], 'no_change': checkpoint['no_change']})
                    checkpoints.append(checkpoint)
                    store.task(self.run, task['id'], 'complete', focused.base, checkpoint['sha'],
                               {'summary': text, 'checks': checks, 'paths': checkpoint['paths']})
                except BaseException as exc:
                    recorder.emit(preparation, 'prepare', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', task_id=task['id'], facts={'error_category': type(exc).__name__})
                    state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                    store.task(self.run, task['id'], state, focused.base if focused else base, details={'error': str(exc)})
                    raise
            head = git(project, 'rev-parse', 'HEAD').decode().strip()
            review_base = self.contract.get('review_base', base)
            if not isinstance(review_base, str) or not review_base:
                raise Blocked('review_base must be a Git commit')
            try:
                review_base = git(project, 'rev-parse', '--verify', review_base + '^{commit}').decode().strip()
                git(project, 'merge-base', '--is-ancestor', review_base, base)
            except Blocked:
                raise Blocked('review_base must resolve to an ancestor of the run baseline') from None
            diff = git(project, 'diff', '--no-ext-diff', '--no-textconv', review_base + '..' + head).decode(errors='replace')
            reviewer_occurrence = recorder.occurrence()
            recorder.emit(reviewer_occurrence, 'review', 'started', facts={'role': 'reviewer', 'review_base': review_base, 'review_head': head})
            review_question_occurrence = recorder.occurrence()
            def review_question(state):
                recorder.emit(review_question_occurrence, 'review', state, facts={'parent_occurrence_id': reviewer_occurrence})
            reviewer = self.adapter(project, self.executor, question=self.question, observe_question=review_question)
            reviewer.lock_fd = self.authority.lock.fileno()
            review = reviewer.prompt('Independently review the actual committed range below against the requested tasks. You are read-only and are NOT the implementation conversation. Inspect relevant source with read/search tools; continue long reads with offsets. Identify concrete correctness, scope or data-safety defects, not missing workflow ceremony. Return only a JSON object {"approved":true,"findings":[]} or {"approved":false,"findings":["path:line - defect"]}. Never approve if there is a material unresolved finding.\nTasks: ' + canonical(self.contract['tasks']) + '\nRange: ' + review_base + '..' + head + '\nDiff:\n' + diff, read_only=True)
            try:
                value = json.loads(review)
            except ValueError:
                recorder.emit(reviewer_occurrence, 'review', 'failed', facts={'role': 'reviewer', 'review_base': base, 'review_head': head, 'error_category': 'malformed'})
                raise Blocked('reviewer returned invalid JSON; review remains incomplete: ' + review) from None
            if (not isinstance(value, dict) or type(value.get('approved')) is not bool or not isinstance(value.get('findings'), list) or any(not isinstance(f, str) for f in value['findings'])):
                recorder.emit(reviewer_occurrence, 'review', 'failed', facts={'role': 'reviewer', 'review_base': base, 'review_head': head, 'error_category': 'malformed'})
                raise Blocked('reviewer result needs boolean approved and a list of findings')
            recorder.emit(reviewer_occurrence, 'review', 'passed' if value['approved'] and not value['findings'] else 'failed', facts={'role': 'reviewer', 'review_base': base, 'review_head': head, 'approved': value['approved'], 'finding_count': len(value['findings'])})
            if not value['approved'] or value['findings']:
                raise Blocked('independent review findings (commits retained): ' + canonical(value))
            store.finish(self.run, 'complete', head)
            recorder.emit(terminal, 'terminal', 'passed', facts={'head': head})
            return {'status': 'complete', 'run_id': self.run, 'baseline': base, 'sha': head, 'checkpoints': checkpoints, 'review': value}
        except BaseException as exc:
            head = git(project, 'rev-parse', 'HEAD').decode().strip()
            store.finish(self.run, 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', head, str(exc))
            recorder.emit(terminal, 'terminal', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', facts={'head': head, 'error_category': type(exc).__name__})
            raise
