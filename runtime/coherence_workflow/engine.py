"""Sequential task/check/Git execution, with one fresh read-only final reviewer."""
import json

from .git_effects import FocusedGit
from .monitoring import Recorder, descriptor
from .pi_adapter import PiAdapter, terminal_question
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
        recorder.register(descriptor(self.contract, self.executor, base))
        terminal = recorder.occurrence()
        recorder.emit(terminal, 'terminal', 'started', facts={'baseline': base})
        checkpoints = []
        try:
            for task in self.contract['tasks']:
                focused = FocusedGit(project, task)
                store.task(self.run, task['id'], 'running', focused.base)
                preparation = recorder.occurrence()
                recorder.emit(preparation, 'prepare', 'started', task_id=task['id'])
                try:
                    recorder.emit(preparation, 'prepare', 'passed', task_id=task['id'])
                    gate_number = [0]
                    def gate_question(text):
                        gate_number[0] += 1
                        occurrence = recorder.occurrence()
                        recorder.emit(occurrence, 'gate', 'started', task_id=task['id'], facts={'ordinal': gate_number[0]})
                        try:
                            answer = self.question(text)
                        except BaseException as exc:
                            recorder.emit(occurrence, 'gate', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', task_id=task['id'], facts={'ordinal': gate_number[0], 'error_category': type(exc).__name__})
                            raise
                        recorder.emit(occurrence, 'gate', 'returned', task_id=task['id'], facts={'ordinal': gate_number[0]})
                        return answer
                    manual_gates(task, gate_question)
                    worker_occurrence = recorder.occurrence()
                    role = 'fixing_worker' if isinstance(self.contract.get('monitor'), dict) and self.contract['monitor'].get('correction_of') else 'worker'
                    recorder.emit(worker_occurrence, 'worker', 'started', task_id=task['id'], facts={'role': role})
                    worker = self.adapter(project, self.executor, question=self.question)
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
                    checks = run_checks(project, task, lock_fd=self.authority.lock.fileno())
                    focused.command('end', 'runner-checks')
                    checkpoint = focused.checkpoint()
                    checkpoints.append(checkpoint)
                    store.task(self.run, task['id'], 'complete', focused.base, checkpoint['sha'],
                               {'summary': text, 'checks': checks, 'paths': checkpoint['paths']})
                except BaseException as exc:
                    recorder.emit(preparation, 'prepare', 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed', task_id=task['id'], facts={'error_category': type(exc).__name__})
                    state = 'interrupted' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed'
                    store.task(self.run, task['id'], state, focused.base, details={'error': str(exc)})
                    raise
            head = git(project, 'rev-parse', 'HEAD').decode().strip()
            diff = git(project, 'diff', '--no-ext-diff', '--no-textconv', base + '..' + head).decode(errors='replace')
            reviewer_occurrence = recorder.occurrence()
            recorder.emit(reviewer_occurrence, 'review', 'started', facts={'role': 'reviewer', 'review_base': base, 'review_head': head})
            reviewer = self.adapter(project, self.executor, question=self.question)
            reviewer.lock_fd = self.authority.lock.fileno()
            review = reviewer.prompt('Independently review the actual committed range below against the requested tasks. You are read-only and are NOT the implementation conversation. Inspect relevant source with read/search tools; continue long reads with offsets. Identify concrete correctness, scope or data-safety defects, not missing workflow ceremony. Return only a JSON object {"approved":true,"findings":[]} or {"approved":false,"findings":["path:line - defect"]}. Never approve if there is a material unresolved finding.\nTasks: ' + canonical(self.contract['tasks']) + '\nRange: ' + base + '..' + head + '\nDiff:\n' + diff, read_only=True)
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
