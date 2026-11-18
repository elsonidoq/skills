"""Offline operation fixtures exercise real task/check/Git ordering, not provider success."""
import json
import os
import sys
from unittest.mock import patch

from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.pi_adapter import PiAdapter, TaskOutcome
from coherence_workflow.store import Authority, Blocked, canonical, git
from fixtures.support import ProjectTest

EXECUTOR = {'provider': 'fixture', 'model': 'offline-not-provider-success', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}}


class OwnerAssignmentExecutionRoleTests(ProjectTest):
    def test_reviewer_is_required_and_profiles_remain_role_specific(self):
        worker = {'provider': 'fixture', 'model': 'worker', 'effort': 'medium'}
        reviewer = {'provider': 'fixture', 'model': 'reviewer', 'effort': 'medium'}
        for invalid in (worker, {**worker, 'reviewer': None}, {**worker, 'reviewer': {}}):
            with self.subTest(invalid=invalid):
                with Authority(self.project) as owner:
                    with self.assertRaisesRegex(Blocked, 'reviewer needs provider, model and effort'):
                        Engine(owner, 'invalid-reviewer', admit([]), invalid)

        calls, sessions = [], []
        class Adapter:
            def __init__(self, _project, profile, **_kwargs):
                self.profile = profile
                sessions.append(self)
            def prompt(self, _prompt, **kwargs):
                calls.append((self.profile, kwargs.get('read_only', False)))
                if not kwargs.get('read_only'):
                    return 'offline worker'
                return ('{"approved":false,"coverage":["fixture examined"],"coverage_gaps":[],"findings":["fixture.txt:1 - fixture finding"]}'
                        if len([call for call in calls if call[1]]) == 1 else '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}')

        executor = {**worker, 'reviewer': reviewer}
        with Authority(self.project) as owner:
            result = Engine(owner, 'role-propagation', admit([{'id': 'task', 'description': 'fixture'}]),
                            executor, adapter=Adapter).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(calls, [(worker, False), (reviewer, True), (reviewer, False), (reviewer, True)])
        self.assertEqual(len({id(session) for session in sessions}), 3)

        shared = {**worker, 'reviewer': dict(worker)}
        with Authority(self.project) as owner:
            engine = Engine(owner, 'shared-roles', admit([]), shared)
        self.assertEqual(engine.executor, worker)
        self.assertEqual(engine.reviewer_executor, worker)
        self.assertIsNot(engine.executor, engine.reviewer_executor)


class SequentialExecutionTests(ProjectTest):
    def execute(self, tasks, adapter, **kwargs):
        with Authority(self.project) as owner:
            return Engine(owner, 'fixture', admit(tasks), EXECUTOR, adapter=adapter, **kwargs).invoke()

    def test_dependencies_real_checks_focused_commits_and_independent_read_only_review(self):
        sessions, prompts = [], []
        project = self.project
        case = self
        class OfflineOperations:
            def __init__(self, project, executor, **kwargs):
                case.assertEqual(executor, {key: value for key, value in EXECUTOR.items() if key != 'reviewer'}
                                 if len(sessions) < 2 else EXECUTOR['reviewer'])
                sessions.append(self)
            def prompt(self, prompt, *, claim=None, command=None, read_only=False):
                prompts.append((prompt, read_only))
                if read_only:
                    case.assertIn('Diff:', prompt)
                    case.assertIn('consumer', prompt)
                    case.assertEqual(git(project, 'show', 'HEAD:new.txt'), b'consumer\n')
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                if len(sessions) == 1:
                    claim('owned.txt')
                    (project/'owned.txt').write_text('producer\n')
                else:
                    case.assertEqual(git(project, 'show', 'HEAD:owned.txt'), b'producer\n')
                    claim('new.txt')
                    (project/'new.txt').write_text('consumer\n')
                return 'offline operation fixture'
        result = self.execute([
            {'id': 'consumer', 'description': 'Consume', 'depends': ['producer'],
             'checks': [['python3', '-B', '-c', "assert open('new.txt').read() == 'consumer\\n'"],
                        ['python3', '-B', '-c',
                         "import os; assert os.path.realpath('.git/coherence-workflow.lock') in "
                         "[os.path.realpath('/proc/self/fd/'+fd) for fd in os.listdir('/proc/self/fd')]"]]},
            {'id': 'producer', 'description': 'Produce'}], OfflineOperations)
        self.assertEqual(result['status'], 'complete')
        worker_prompts = [prompt for prompt, read_only in prompts if not read_only]
        review_prompts = [prompt for prompt, read_only in prompts if read_only]
        instruction = ('Discover the canonical save-adr decision contract from the configured/installed suite and project routing, '
                       'or use supplied relevant accepted constraints.')
        self.assertEqual(len(worker_prompts), 2)
        self.assertEqual(len(review_prompts), 1)
        self.assertTrue(all(instruction in prompt for prompt in worker_prompts + review_prompts))
        self.assertIn('Task: {"description":"Produce","id":"producer"}', worker_prompts[0])
        self.assertIn('Skills are disabled for this reviewer, so locate and read the canonical contract as a file with read/search tools;', review_prompts[0])
        self.assertIn('Original range: ' + self.base + '..', review_prompts[0])
        self.assertEqual(len(sessions), 3)
        self.assertEqual(len({id(s) for s in sessions}), 3)
        self.assertEqual(len(result['checkpoints']), 2)
        self.assertEqual(git(project, 'rev-list', '--count', self.base+'..HEAD'), b'2\n')
        import sqlite3
        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        history = list(db.execute("SELECT kind,task_id,state FROM execution_history WHERE run_id='fixture' ORDER BY seq"))
        review_base, review_started = db.execute("SELECT review_base,dispatched_at FROM execution_review_executions WHERE run_id='fixture'").fetchone()
        checkpoint_passed = db.execute("SELECT recorded_at FROM execution_history WHERE run_id='fixture' AND task_id='consumer' AND kind='checkpoint' AND state='passed'").fetchone()[0]
        db.close()
        self.assertLess(history.index(('worker', 'consumer', 'returned')),
                        history.index(('check', 'consumer', 'passed')))
        self.assertLess(history.index(('check', 'consumer', 'passed')),
                        history.index(('checkpoint', 'consumer', 'passed')))
        self.assertEqual(review_base, self.base)
        self.assertLessEqual(checkpoint_passed, review_started)

    def test_exact_handoff_input_claims_preserved_recovery_bytes_and_checkpoints_only_owned_results(self):
        project = self.project
        (project/'tracked.txt').write_text('baseline\n')
        git(project, 'add', '--', 'tracked.txt')
        git(project, 'commit', '-qm', 'tracked baseline')
        (project/'tracked.txt').write_bytes(b'tracked recovery\n')
        (project/'untracked.txt').write_bytes(b'untracked recovery\n')
        (project/'other.txt').write_bytes(b'unrelated staged\n')
        git(project, 'add', '--', 'other.txt')
        staged = git(project, 'show', ':other.txt')
        seen = []
        class HandoffOperations:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                name = 'untracked.txt' if '"id":"handoff-untracked"' in prompt else 'tracked.txt'
                before = (project/name).read_bytes()
                seen.append((name, before))
                kwargs['claim'](name)
                (project/name).write_bytes(before + b'intended edit\n')
                return 'corrected recovery file'
        result = self.execute([
            {'id': 'handoff-tracked', 'description': 'Correct tracked recovery', 'depends': ['handoff-untracked'],
             'owned_paths': ['tracked.txt'], 'handoff_paths': ['tracked.txt']},
            {'id': 'handoff-untracked', 'description': 'Correct untracked recovery',
             'owned_paths': ['untracked.txt'], 'handoff_paths': ['untracked.txt']}], HandoffOperations)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(seen, [('untracked.txt', b'untracked recovery\n'), ('tracked.txt', b'tracked recovery\n')])
        checkpoints = {item['task_id']: item for item in result['checkpoints']}
        self.assertEqual(git(project, 'show', checkpoints['handoff-untracked']['sha'] + ':untracked.txt'),
                         b'untracked recovery\nintended edit\n')
        self.assertEqual(git(project, 'show', checkpoints['handoff-tracked']['sha'] + ':tracked.txt'),
                         b'tracked recovery\nintended edit\n')
        self.assertEqual(git(project, 'show', ':other.txt'), staged)

    def test_failed_check_not_passed_no_commit_or_automatic_retry(self):
        project = self.project
        calls = []
        class OfflineFailure:
            def __init__(self, *args, **kwargs):
                self.saved_session = {'id': 'failed-check', 'file': '/private/failed-check.jsonl'}
            def prompt(self, prompt, **kwargs):
                calls.append(prompt)
                kwargs['claim']('owned.txt')
                (project/'owned.txt').write_text('partial\n')
                return 'worker claims done but actual command fails'
        with self.assertRaisesRegex(Blocked, 'check failed'):
            self.execute([{'id': 'fix', 'description': 'Fix', 'checks': [['python3', '-B', '-c', 'raise SystemExit(7)']]}], OfflineFailure)
        self.assertEqual(len(calls), 2)
        self.assertEqual(git(project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        self.assertEqual((project/'owned.txt').read_text(), 'partial\n')
        from coherence_workflow.cli import status
        self.assertEqual(status(project, 'fixture')['run']['state'], 'failed')
        self.assertEqual(status(project, 'fixture')['tasks'][0]['state'], 'failed')

    def test_explicit_unaccepted_worker_return_preserves_partial_work_without_success_dispatch(self):
        """Composed V1: transport return cannot release an explicitly failed task."""
        project = self.project
        for label, returned, partial in (
            ('blocked', TaskOutcome('blocked'), False),
            ('failed', TaskOutcome('failed'), True),
            ('incomplete', TaskOutcome('incomplete'), True),
            ('unmet-acceptance', TaskOutcome('failed'), True),
        ):
            with self.subTest(label=label):
                calls, answers = [], []
                class ExplicitReturn:
                    def __init__(self, *args, **kwargs): self.question = kwargs.get('question')
                    def prompt(self, prompt, **kwargs):
                        calls.append((prompt, kwargs.get('read_only', False)))
                        if kwargs.get('read_only'):
                            self_case.fail('success-path review must not dispatch')
                        if '"id":"B"' in prompt:
                            self_case.fail('dependent B must not dispatch')
                        # A delivered answer is not controller cancellation; the worker can
                        # still explicitly return its blocker after receiving it.
                        if label == 'blocked':
                            answers.append(self.question('fixture question'))
                        if partial:
                            kwargs['claim']('partial-' + label + '.txt')
                            (project / ('partial-' + label + '.txt')).write_text(label + '\n')
                        return returned
                self_case = self
                with Authority(project) as owner:
                    with self.assertRaises(Blocked):
                        Engine(owner, 'unaccepted-' + label, admit([
                            {'id': 'A', 'description': 'A' + ('; only runner review remains' if label == 'incomplete' else ''),
                             'owned_paths': ['partial-' + label + '.txt']},
                            {'id': 'B', 'description': 'B', 'depends': ['A']}]), EXECUTOR,
                            adapter=ExplicitReturn, question=lambda prompt: answers.append(prompt) or 'answered').invoke()
                self.assertEqual(len([entry for entry in calls if not entry[1]]), 1)
                self.assertIn('Work autonomously until the assigned implementation and worker-owned acceptance are complete', calls[0][0])
                self.assertIn('Unfinished implementation, unrun checks, task complexity, and correctable or intermittent test failures are reasons to continue working', calls[0][0])
                self.assertIn('genuine inability to progress, cancellation, or execution failure prevents worker-owned acceptance', calls[0][0])
                self.assertIn('unmet acceptance never becomes success', calls[0][0])
                if label == 'incomplete':
                    self.assertIn('only runner review remains', calls[0][0])
                if label == 'blocked':
                    self.assertEqual(len(answers), 2)
                if partial:
                    self.assertEqual((project / ('partial-' + label + '.txt')).read_text(), label + '\n')
                import sqlite3
                db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
                tasks = dict(db.execute("SELECT task_id,state FROM execution_tasks WHERE run_id=?", ('unaccepted-' + label,)))
                history = list(db.execute("SELECT kind,state FROM execution_history WHERE run_id=?", ('unaccepted-' + label,)))
                db.close()
                self.assertEqual(tasks, {'A': 'failed'})
                self.assertIn(('worker_invocation', 'failed'), history)
                self.assertNotIn(('checkpoint', 'passed'), history)
                self.assertEqual(git(project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_actual_adapter_transport_outcome_blocks_before_checkpoint_or_dispatch(self):
        """The host result, not a Python exception fixture, carries unsuccessful work."""
        host = self.root / 'blocked_host.py'
        host.write_text("""import json
from pathlib import Path
request = json.loads(input())
print(json.dumps({'type': 'claim', 'path': 'partial.txt'}), flush=True)
assert json.loads(input()) == {'ok': True}
Path(request['project'], 'partial.txt').write_text('partial\\n')
print(json.dumps({'type': 'result', 'text': 'BENIGN-TASK-REASON: correct fixture input', 'outcome': 'blocked'}), flush=True)
""")
        with patch('coherence_workflow.pi_adapter.host_path', return_value=host), \
             patch.dict(os.environ, {'COHERENCE_NODE': sys.executable,
                                    'COHERENCE_PARENT_BRIDGE_SOCKET': '', 'COHERENCE_PARENT_BRIDGE_TOKEN': '',
                                    'COHERENCE_PARENT_BRIDGE_SESSION': '', 'COHERENCE_PARENT_BRIDGE_RUN': ''}):
            with Authority(self.project) as owner:
                with self.assertRaisesRegex(Blocked, 'worker explicitly blocked; BENIGN-TASK-REASON: correct fixture input'):
                    Engine(owner, 'host-outcome', admit([
                        {'id': 'A', 'description': 'A', 'owned_paths': ['partial.txt']},
                        {'id': 'B', 'description': 'B', 'depends': ['A']}]), EXECUTOR).invoke()
        self.assertEqual((self.project / 'partial.txt').read_text(), 'partial\n')
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        import sqlite3
        db = sqlite3.connect(self.project / '.coherence/workflow/workflow.sqlite')
        tasks = dict(db.execute("SELECT task_id,state FROM execution_tasks WHERE run_id='host-outcome'"))
        history = list(db.execute("SELECT kind,state,details FROM execution_history WHERE run_id='host-outcome'"))
        db.close()
        self.assertEqual(tasks, {'A': 'failed'})
        failed = next(row for row in history if row[0:2] == ('worker_invocation', 'failed'))
        self.assertIn('BENIGN-TASK-REASON: correct fixture input', json.loads(failed[2])['diagnostic'])
        from coherence_workflow.cli import status
        self.assertNotIn('BENIGN-TASK-REASON: correct fixture input', canonical(status(self.project, 'host-outcome')))
        self.assertNotIn(('checkpoint', 'passed'), history)

    def test_actual_adapter_outcome_text_fallback_success_and_invalid_controls(self):
        """Actual adapter keeps status-only callers, successful text, and transport refusal compatible."""
        host = self.root / 'outcome_controls_host.py'
        def prompt(record):
            host.write_text("""import json
json.loads(input())
print(json.dumps(RECORD), flush=True)
""".replace('RECORD', repr(record)))
            return PiAdapter(self.project, EXECUTOR).prompt('fixture')
        with patch('coherence_workflow.pi_adapter.host_path', return_value=host), \
             patch.dict(os.environ, {'COHERENCE_NODE': sys.executable,
                                    'COHERENCE_PARENT_BRIDGE_SOCKET': '', 'COHERENCE_PARENT_BRIDGE_TOKEN': '',
                                    'COHERENCE_PARENT_BRIDGE_SESSION': '', 'COHERENCE_PARENT_BRIDGE_RUN': ''}):
            empty = prompt({'type': 'result', 'text': '', 'outcome': 'failed'})
            with self.assertRaisesRegex(Blocked, 'worker explicitly failed; no explanation returned'):
                Engine._prompt_worker(type('Offline', (), {'prompt': lambda _self, _prompt: empty})(), 'fixture')
            self.assertEqual(prompt({'type': 'result', 'text': 'ordinary completed text', 'outcome': 'completed'}),
                             'ordinary completed text')
            with self.assertRaisesRegex(Blocked, 'SDK result has an invalid outcome'):
                prompt({'type': 'result', 'text': 'ignored', 'outcome': 'invalid'})
            with self.assertRaisesRegex(Blocked, 'SDK result text must be a string'):
                prompt({'type': 'result', 'text': None, 'outcome': 'failed'})

    def test_synchronous_fixer_question_trace_uses_current_invocation(self):
        """Production run_fix binds every real adapter call, including restored review sessions."""
        import socket
        import threading
        from contextlib import nullcontext
        from coherence_workflow.pi_adapter import parent_question
        from coherence_workflow.trace_capture import persist_parent_events

        host = self.root / 'fix_question_host.py'
        host.write_text("""import json, sys
from pathlib import Path
request = json.loads(input())
with Path(LOG).open('a') as log:
    log.write(json.dumps(request) + '\\n')
if request['readOnly']:
    session = {'id': 'saved-reviewer', 'file': 'private-review.jsonl', 'compatibility': {'readOnly': True}}
else:
    assert request['savedSession']['id'] == 'saved-reviewer'
    corrective = 'Actual failed attempt:' in request['prompt']
    if not corrective:
        assert request['reviewRepair'] is True
    tool = 'corrective-tool' if corrective else 'initial-tool'
    print(json.dumps({'type': 'question', 'request_id': tool, 'tool_call_id': tool, 'question': 'Worker asks ' + tool}), flush=True)
    answer = sys.stdin.readline()
    if not answer:
        sys.exit(0)
    answer = json.loads(answer)
    assert answer == {'type': 'reply', 'request_id': tool, 'reply': {'answer': 'coordinator resolution'}}
    if corrective:
        Path(MARKER).write_text('corrected')
    session = {'id': 'saved-reviewer', 'file': 'private-review.jsonl', 'compatibility': {'readOnly': False}}
print(json.dumps({'type': 'result', 'text': 'real adapter result', 'session': session}), flush=True)
""".replace('LOG', repr(str(self.root / 'fix-questions.jsonl')))
           .replace('MARKER', repr(str(self.root / 'corrected'))))
        log, marker = self.root / 'fix-questions.jsonl', self.root / 'corrected'
        for cached in (True, False):
            for mode in ('recorded', 'capture-failure', 'cancel-capture-failure'):
                with self.subTest(cached=cached, mode=mode):
                    if marker.exists():
                        marker.unlink()
                    log.write_text('')
                    run = 'fix-question-' + str(cached) + '-' + mode
                    contract = admit([{'id': 'original', 'description': 'Offline repair', 'owned_paths': [],
                        'check': [sys.executable, '-B', '-c',
                                  'from pathlib import Path; assert Path(' + repr(str(marker)) + ').exists()']}])
                    env = {'COHERENCE_NODE': sys.executable, 'COHERENCE_PARENT_BRIDGE_SOCKET': '',
                           'COHERENCE_PARENT_BRIDGE_TOKEN': '', 'COHERENCE_PARENT_BRIDGE_SESSION': '',
                           'COHERENCE_PARENT_BRIDGE_RUN': ''}
                    with patch('coherence_workflow.pi_adapter.host_path', return_value=host), patch.dict(os.environ, env):
                        with Authority(self.project) as owner:
                            owner.store.start(run, self.base, contract=contract, executor=EXECUTOR,
                                              authority={}, review_base=self.base)
                            worker = PiAdapter(self.project, EXECUTOR['reviewer'])
                            self.assertEqual(worker.prompt('review', read_only=True), 'real adapter result')
                            owner.store.review_dispatch(run, 'review', review_base=self.base, review_head=self.base)
                            owner.store.review_outcome(run, 'review', 'rejected', findings=['fixture defect'],
                                references={'base': self.base, 'head': self.base, 'saved_session': worker.saved_session})
                        # Reopen the store; only the cached case retains the actual adapter.
                        with Authority(self.project) as owner:
                            cancelled = Blocked('actual question cancelled')
                            def cancel(_):
                                raise cancelled
                            endpoint = str(self.root / 'fix-question.sock')
                            server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                            server.bind(endpoint)
                            server.listen(3)
                            server.settimeout(10)
                            bridge_errors = []
                            def respond():
                                try:
                                    for call in range(2):
                                        parent_id = None
                                        for _ in range(3):
                                            conn, _ = server.accept()
                                            with conn, conn.makefile('r') as stream:
                                                request = json.loads(stream.readline())
                                                if request['type'] == 'question':
                                                    parent_id = request['request_id']
                                                    reply = {'answer': 'coordinator resolution'}
                                                elif request['type'] == 'trace_drain':
                                                    reply = {'events': [{'version': 1, 'id': 'owner-' + str(call),
                                                        'kind': 'owner_result', 'tool_call_id': 'owner-tool-' + str(call),
                                                        'request_id': parent_id, 'content': 'actual owner answer'}]}
                                                else:
                                                    reply = {'acknowledged': True}
                                                conn.sendall((json.dumps({'request_id': request['request_id'], **reply}) + '\n').encode())
                                except Exception as exc:
                                    bridge_errors.append(exc)
                                finally:
                                    server.close()
                            thread = None
                            if not mode.startswith('cancel'):
                                thread = threading.Thread(target=respond)
                                thread.start()
                            def attached(text):
                                return parent_question(text, trace_observer=lambda run, events:
                                    persist_parent_events(owner.store, run, events))
                            engine = Engine(owner, run, contract, EXECUTOR, question=cancel if mode.startswith('cancel') else attached)
                            if cached:
                                worker.question = engine.question
                                worker.question_trace = lambda *a, **k: self.fail('stale reviewer observer used')
                                engine._review_workers = {'review': worker}
                            capture = (nullcontext() if mode == 'recorded' else patch(
                                'coherence_workflow.trace_capture.record_worker_question', side_effect=RuntimeError('optional capture failed')))
                            try:
                                with capture, patch.dict(os.environ, {'COHERENCE_PARENT_BRIDGE_SOCKET': endpoint,
                                        'COHERENCE_PARENT_BRIDGE_TOKEN': 'token', 'COHERENCE_PARENT_BRIDGE_SESSION': 'parent',
                                        'COHERENCE_PARENT_BRIDGE_RUN': run}):
                                    if mode.startswith('cancel'):
                                        with self.assertRaises(Blocked) as raised:
                                            engine.run_fix(['fixture defect'], trigger_execution_id='review',
                                                review_base=self.base, execution_id='fixer')
                                        self.assertIs(raised.exception, cancelled)
                                    else:
                                        result = engine.run_fix(['fixture defect'], trigger_execution_id='review',
                                            review_base=self.base, execution_id='fixer')
                                        self.assertEqual(result['summary'], 'real adapter result')
                                        self.assertTrue(result['checkpoint']['no_change'])
                            finally:
                                if thread:
                                    thread.join(12)
                                    self.assertFalse(thread.is_alive())
                                else:
                                    server.close()
                                os.unlink(endpoint)
                            self.assertEqual(bridge_errors, [])
                            rows = [(r['kind'], r['state'], json.loads(r['details'])) for r in owner.store.db.execute(
                                'SELECT kind,state,details FROM execution_history WHERE run_id=? ORDER BY seq', (run,))]
                            invocations = [d['invocation_id'] for k, s, d in rows if k == 'fixer_invocation' and s == 'started']
                            self.assertEqual(len(invocations), 1 if mode.startswith('cancel') else 2)
                            self.assertEqual(len(set(invocations)), len(invocations))
                            traces = [(s, d) for k, s, d in rows if k == 'worker_question_trace']
                            if mode == 'recorded':
                                self.assertEqual([s for s, d in traces], ['requested', 'parent_request', 'resolved', 'sent'] * 2)
                                for index, tool in enumerate(('initial-tool', 'corrective-tool')):
                                    group = traces[index * 4:(index + 1) * 4]
                                    for state, facts in group:
                                        self.assertEqual((facts['run_id'], facts['task_id'], facts['invocation_id']),
                                                         (run, 'fix-fixer', invocations[index]))
                                        self.assertEqual(facts['tool_call_id'], tool)
                                        self.assertEqual(facts['question'], 'Worker asks ' + tool)
                                    self.assertEqual(group[2][1]['resolution'], 'coordinator resolution')
                                    event = next(d['event'] for k, s, d in rows if k == 'parent_trace' and d['event']['id'] == 'owner-' + str(index))
                                    self.assertEqual(event['request_id'], group[1][1]['parent_request_id'])
                                    self.assertNotEqual(event['tool_call_id'], tool)
                                    self.assertNotEqual(event['content'], group[2][1]['resolution'])
                            else:
                                self.assertEqual(traces, [])
                    requests = [json.loads(line) for line in log.read_text().splitlines()]
                    self.assertEqual(len(requests), 2 if mode.startswith('cancel') else 3)
                    self.assertTrue(requests[0]['readOnly'])
                    self.assertTrue(all(not r['readOnly'] and r['savedSession']['id'] == 'saved-reviewer' for r in requests[1:]))

    def test_actual_adapter_unsuccessful_fixer_stops_before_checkpoint_and_rereview(self):
        """Synthetic host responses traverse the real adapter and repair consumer."""
        host, dispatches = self.root / 'repair_host.py', self.root / 'dispatches.jsonl'
        for outcome in ('blocked', 'failed', 'incomplete'):
            for partial in (False, True):
                with self.subTest(outcome=outcome, partial=partial):
                    name = 'repair-' + outcome + '-' + str(partial) + '.txt'
                    host.write_text("""import json
from pathlib import Path
request = json.loads(input())
with Path(DISPATCHES).open('a') as log:
    log.write(json.dumps({'read_only': request['readOnly'], 'prompt': request['prompt']}) + '\\n')
if request['readOnly']:
    text, outcome = '{"approved":false,"coverage":["fixture examined"],"coverage_gaps":[],"findings":["owned.txt:1 - fixture defect"]}', 'completed'
elif 'Actionable findings:' in request['prompt']:
    if PARTIAL:
        print(json.dumps({'type': 'claim', 'path': NAME}), flush=True)
        assert json.loads(input()) == {'ok': True}
        Path(request['project'], NAME).write_text('partial repair\\n')
    text, outcome = 'BENIGN-FIXER-REASON: correct fixture acceptance', OUTCOME
else:
    text, outcome = 'Completed no-change task', 'completed'
print(json.dumps({'type': 'result', 'text': text, 'outcome': outcome}), flush=True)
""".replace('DISPATCHES', repr(str(dispatches))).replace('PARTIAL', repr(partial))
                        .replace('NAME', repr(name)).replace('OUTCOME', repr(outcome)))
                    dispatches.write_text('')
                    run = 'repair-outcome-' + outcome + '-' + str(partial)
                    with patch('coherence_workflow.pi_adapter.host_path', return_value=host), \
                         patch.dict(os.environ, {'COHERENCE_NODE': sys.executable,
                                                'COHERENCE_PARENT_BRIDGE_SOCKET': '', 'COHERENCE_PARENT_BRIDGE_TOKEN': '',
                                                'COHERENCE_PARENT_BRIDGE_SESSION': '', 'COHERENCE_PARENT_BRIDGE_RUN': ''}):
                        with Authority(self.project) as owner:
                            with self.assertRaisesRegex(Blocked, 'worker explicitly ' + outcome + '; BENIGN-FIXER-REASON: correct fixture acceptance'):
                                Engine(owner, run, admit([{
                                    'id': 'A', 'description': 'Completed no-change fixture', 'owned_paths': [name],
                                    'check': [sys.executable, '-B', '-c', "print('baseline green')"],
                                }]), EXECUTOR).invoke()
                            chain = owner.store.review_chain(run)
                            self.assertEqual([(item['role'], item['state']) for item in chain['executions']],
                                             [('reviewer', 'rejected'), ('fixer', 'failed')])
                            history = list(owner.store.db.execute(
                                'SELECT kind,state,details FROM execution_history WHERE run_id=?', (run,)))
                            failed = next(row for row in history if row['kind'] == 'fixer_invocation' and row['state'] == 'failed')
                            self.assertIn('BENIGN-FIXER-REASON: correct fixture acceptance', json.loads(failed['details'])['diagnostic'])
                            from coherence_workflow.cli import status
                            self.assertNotIn('BENIGN-FIXER-REASON: correct fixture acceptance', canonical(status(self.project, run)))
                            self.assertFalse(any(row['kind'] in ('fixer_checks', 'fixer_checkpoint') for row in history))
                    calls = [json.loads(line) for line in dispatches.read_text().splitlines()]
                    self.assertEqual([call['read_only'] for call in calls], [False, True, False])
                    self.assertIn('Work autonomously until the assigned implementation and worker-owned acceptance are complete', calls[-1]['prompt'])
                    self.assertIn('Unfinished implementation, unrun checks, task complexity, and correctable or intermittent test failures are reasons to continue working', calls[-1]['prompt'])
                    self.assertIn('genuine inability to progress, cancellation, or execution failure prevents worker-owned acceptance', calls[-1]['prompt'])
                    self.assertIn('unmet acceptance never becomes success', calls[-1]['prompt'])
                    self.assertEqual((self.project / name).exists(), partial)
                    if partial:
                        self.assertEqual((self.project / name).read_text(), 'partial repair\n')
                    self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_findings_honestly_reported_commits_retained_no_disposition_database(self):
        project = self.project
        class OfflineReview:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, *, read_only=False, claim=None, command=None):
                if read_only:
                    return '{"approved":false,"coverage":["fixture examined"],"coverage_gaps":[],"findings":["owned.txt:1 - defect"]}'
                claim('owned.txt')
                (project/'owned.txt').write_text('changed\n')
                return 'changed'
        with patch('sys.stdin.isatty', return_value=False), \
                self.assertRaisesRegex(Blocked, 'owner authorization unavailable'):
            self.execute([{'id': 'fix', 'description': 'Fix'}], OfflineReview)
        self.assertNotEqual(git(project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_manual_gate_uses_current_answer_without_receipt(self):
        answers = []
        def deny(question):
            answers.append(question)
            return 'no'
        class Never:
            def __init__(self, *a, **k): raise AssertionError('worker launched')
        with self.assertRaisesRegex(Blocked, 'manual gate not approved'):
            self.execute([{'id': 'fix', 'description': 'Fix', 'gates': [{'question': 'Proceed?'}]}], Never, question=deny)
        self.assertEqual(len(answers), 1)
        import sqlite3
        db = sqlite3.connect(self.project/'.coherence/workflow/workflow.sqlite')
        history = list(db.execute("SELECT kind,state FROM execution_history WHERE run_id='fixture' ORDER BY seq"))
        state = db.execute("SELECT state FROM execution_runs WHERE run_id='fixture'").fetchone()[0]
        db.close()
        self.assertFalse(any(kind in ('worker_dispatch', 'worker_invocation') for kind, _ in history))
        self.assertEqual(state, 'failed')
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_real_framed_question_send_failure_is_retained_without_public_payload(self):
        import os, sys
        from pathlib import Path
        host, closed = self.root/'broken_answer_host.py', self.root/'stdin-closed'
        host.write_text("""import json, sys, time
from pathlib import Path
request = json.loads(input())
if request['readOnly']:
    print(json.dumps({'type':'result','text':'{\\\"approved\\\":true,\\\"findings\\\":[]}'}), flush=True)
else:
    print(json.dumps({'type':'question','question':'PRIVATE-SENTINEL'}), flush=True)
    import os
    os.close(0)
    Path(""" + repr(str(closed)) + """).write_text('closed')
    time.sleep(1)
""")
        contract = admit([{'id': 'fix', 'description': 'Fix'}])
        with patch('coherence_workflow.pi_adapter.host_path', return_value=host), patch.dict(
                os.environ, {'COHERENCE_NODE': sys.executable, 'COHERENCE_PARENT_BRIDGE_SOCKET': '',
                             'COHERENCE_PARENT_BRIDGE_TOKEN': '', 'COHERENCE_PARENT_BRIDGE_SESSION': '',
                             'COHERENCE_PARENT_BRIDGE_RUN': ''}):
            with Authority(self.project) as owner:
                with self.assertRaises((BrokenPipeError, OSError)):
                    def answer(text):
                        import time
                        deadline = time.monotonic() + 5
                        while not closed.exists() and time.monotonic() < deadline: time.sleep(.01)
                        self.assertTrue(closed.exists())
                        return 'yes'
                    Engine(owner, 'broken-send', contract, EXECUTOR, adapter=__import__('coherence_workflow.pi_adapter', fromlist=['PiAdapter']).PiAdapter, question=answer).invoke()
        import sqlite3
        db = sqlite3.connect(self.project/'.coherence/workflow/workflow.sqlite')
        states = [row[0] for row in db.execute("SELECT state FROM execution_history WHERE run_id='broken-send' AND kind='worker_invocation' ORDER BY seq")]
        db.close()
        self.assertIn('failed', states)
        from coherence_workflow.cli import status
        self.assertNotIn('PRIVATE-SENTINEL', canonical(status(self.project, 'broken-send')))

    def test_review_base_must_be_ancestor_and_actual_prompt_uses_it(self):
        project = self.project
        prompts = []
        class Offline:
            def __init__(self, *a, **k): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    prompts.append(prompt)
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                return 'offline worker'
        contract = admit({'review_base': self.base, 'tasks': [{'id': 'fix', 'description': 'Fix'}]})
        with Authority(project) as owner:
            Engine(owner, 'range', contract, EXECUTOR, adapter=Offline).invoke()
        self.assertIn('Original range: ' + self.base + '..', prompts[0])
        bad = admit({'review_base': 'not-a-commit', 'tasks': [{'id': 'again', 'description': 'Again'}]})
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'ancestor'):
                Engine(owner, 'bad-range', bad, EXECUTOR, adapter=Offline).invoke()

    def test_rejected_original_and_declared_fix_use_full_original_review_range(self):
        project, prompts = self.project, []
        class OfflineReviewCycle:
            def __init__(self, *a, **k): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    prompts.append(prompt)
                    return '{"approved":false,"coverage":["fixture examined"],"coverage_gaps":[],"findings":["fix.txt:1 - original defect"]}' if len(prompts) == 1 else '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                if 'Continue the rejecting review' in prompt:
                    raise Blocked('original defect')
                if '"id":"fix"' in prompt:
                    kwargs['claim']('fix.txt')
                    (project/'fix.txt').write_text('corrected\\n')
                return 'offline worker'
        original = admit({'tasks': [{'id': 'original', 'description': 'Original'}]})
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'original defect'):
                Engine(owner, 'original', original, EXECUTOR, adapter=OfflineReviewCycle).invoke()
        fixing = admit({'monitor': {'correction_of': {'run_id': 'original', 'review_execution_id': 'review-id'}}, 'review_base': self.base, 'tasks': [{'id': 'fix', 'description': 'Fix'}]})
        with Authority(project) as owner:
            Engine(owner, 'fixing', fixing, EXECUTOR, adapter=OfflineReviewCycle).invoke()
        self.assertIn('Original range: ' + self.base + '..', prompts[1])
        self.assertIn('fix.txt', prompts[1])
        self.assertTrue(all('Initial review: examine the complete requested change' in prompt and
                            'Attributable task/repair checkpoints (verified against Git):' in prompt
                            for prompt in prompts))
        import sqlite3
        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        original_state = db.execute("SELECT state FROM execution_runs WHERE run_id='original'").fetchone()[0]
        roles = [json.loads(row[0]).get('role') for row in db.execute("SELECT details FROM execution_history WHERE run_id='fixing' AND kind='worker'")]
        review_bases = [row[0] for row in db.execute("SELECT review_base FROM execution_review_executions WHERE run_id='fixing'")]
        db.close()
        self.assertEqual(original_state, 'failed')
        self.assertIn('fixing_worker', roles)
        self.assertTrue(review_bases)
        self.assertTrue(all(base == self.base for base in review_bases))

    def test_review_transport_failure_records_selected_range(self):
        project = self.project
        class Offline:
            def __init__(self, *a, **k): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'): raise Blocked('transport failed')
                return 'worker'
        contract = admit({'review_base': self.base, 'tasks': [{'id': 'fix', 'description': 'Fix'}]})
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'transport failed'):
                Engine(owner, 'review-failure', contract, EXECUTOR, adapter=Offline).invoke()
        import sqlite3
        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        review_base = db.execute("SELECT review_base FROM execution_review_executions WHERE run_id='review-failure'").fetchone()[0]
        attempts = [row[0] for row in db.execute("SELECT state FROM execution_review_attempts WHERE run_id='review-failure'")]
        db.close()
        self.assertEqual(review_base, self.base)
        self.assertIn('failed', attempts)

    def test_worker_check_review_and_git_errors_are_preserved(self):
        project = self.project
        class WorkerFailure:
            def __init__(self, *a, **k): pass
            def prompt(self, *a, **k): raise Blocked('original worker failure')
        class ReviewFailure:
            def __init__(self, *a, **k):
                self.saved_session = {'id': 'append-review', 'file': '/private/append-review.jsonl'}
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'): return '{"approved":false,"coverage":["fixture examined"],"coverage_gaps":[],"findings":["review.txt:1 - original review failure"]}'
                return 'worker'
        for run, task, adapter, reason in (
            ('append-worker', admit([{'id': 'worker', 'description': 'Worker'}]), WorkerFailure, 'original worker failure'),
            ('append-check', admit([{'id': 'check', 'description': 'Check', 'checks': ['exit 23']}]), ReviewFailure, 'exit 23'),
            ('append-review', admit([{'id': 'review', 'description': 'Review'}]), ReviewFailure, 'owner authorization unavailable')):
            with self.subTest(run=run), Authority(project) as owner:
                with patch('sys.stdin.isatty', return_value=False), self.assertRaisesRegex(Blocked, reason):
                    Engine(owner, run, task, EXECUTOR, adapter=adapter).invoke()
        class GitFailure:
            def __init__(self, *a, **k):
                self.saved_session = {'id': 'append-git', 'file': '/private/append-git.jsonl'}
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'): return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                kwargs['claim']('git-failure.txt')
                project.joinpath('git-failure.txt').write_text('partial\n')
                return 'worker'
        hook = project/'.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 9\n')
        hook.chmod(0o755)
        self.addCleanup(lambda: hook.unlink(missing_ok=True))
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'Git operation failed'):
                Engine(owner, 'append-git', admit([{'id': 'git', 'description': 'Git'}]), EXECUTOR, adapter=GitFailure).invoke()

    def test_sdk_error_retains_partial_work_and_releases_writer_lock(self):
        project = self.project
        class OfflineSDKError:
            def __init__(self, *a, **k): pass
            def prompt(self, *a, **k):
                (project/'owned.txt').write_text('partial\n')
                raise Blocked('actual provider operation error')
        with self.assertRaisesRegex(Blocked, 'actual provider'):
            self.execute([{'id': 'fix', 'description': 'Fix'}], OfflineSDKError)
        with Authority(project): pass
        self.assertEqual((project/'owned.txt').read_text(), 'partial\n')
