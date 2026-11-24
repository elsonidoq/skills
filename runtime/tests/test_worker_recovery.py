"""Inspected coordinator recovery in disposable projects; no live models or owner replies."""
import contextlib
import io
import hashlib
import json
import os
import sys
from unittest.mock import patch

from coherence_workflow import cli, engine

from coherence_workflow.engine import Engine
from coherence_workflow.graph import graph_recovery_action, graph_saver, run_graph, task_graph
from coherence_workflow.intake import admit
from coherence_workflow.metric_artifacts import artifact_relative
from coherence_workflow.pi_adapter import TaskOutcome, sdk_error_detail
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'worker', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'reviewer', 'effort': 'medium'},
            'implementation_fallback': {'provider': 'fixture', 'model': 'strong', 'effort': 'medium'}}
DIAGNOSIS = 'Inspected the partial implementation: missing parser; implement it using the retained source and checks.'


class GraphRecoveryTests(ProjectTest):
    def exercise(self, action, *, fail_escalation=False, fail_check=False):
        project, calls, prompts = self.project, [], []
        identity = {'id': 'saved', 'file': '/fixture/saved.jsonl'}
        class Adapter:
            def __init__(self, _project, executor, **kwargs):
                self.model, self.saved_session = executor['model'], None
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    calls.append(('review', self.model))
                    return json.dumps({'approved': True, 'findings': [], 'coverage': ['fixture'], 'coverage_gaps': []})
                calls.append(('worker', self.model))
                prompts.append(prompt)
                if len(calls) == 3:
                    self_test.assertEqual(kwargs.get('saved_session'), identity if action == 'continue' else None)
                self.saved_session = self.opened_session = kwargs.get('saved_session') or (
                    {'id': 'fresh', 'file': '/fixture/fresh.jsonl'} if len(calls) == 3 else identity)
                if 'first task' in prompt:
                    kwargs['claim']('first.txt')
                    (project/'first.txt').write_text('complete\n')
                    return 'first complete'
                kwargs['claim']('owned.txt')
                (project/'owned.txt').write_text('partial\n' if len(calls) == 2 else 'fixed\n')
                if len(calls) == 2 or fail_escalation:
                    return TaskOutcome('incomplete', 'inspected parser defect')
                return 'original acceptance verified'
        self_test = self
        contract = admit({'delivery_issue': 'https://example.invalid/issue', 'tasks': [
            {'id': 'first', 'description': 'first task', 'owned_paths': ['first.txt']},
            {'id': 'second', 'description': 'second task', 'depends': ['first'], 'owned_paths': ['owned.txt'],
             'checks': [[sys.executable, '-c', 'raise SystemExit(7)']] if fail_check else []}]})
        config = {'configurable': {'thread_id': 'graph-recovery'}}
        (project/'unrelated.txt').write_text('preserve\n')
        with Authority(project) as owner:
            owner.store.start('graph-recovery', self.base, contract=contract, executor=EXECUTOR,
                authority={'paid_scope': {'apis': []}, 'review_policy': 'owner-pair-v1'}, review_base=self.base)
            engine = Engine(owner, 'graph-recovery', contract, EXECUTOR, adapter=Adapter, paid_scope={'apis': []}, resume=True,
                            question=lambda *_a, **_k: self.fail('routine recovery asked owner'))
            with graph_saver(owner) as saver:
                graph = task_graph(engine, saver, review=True)
                with self.assertRaisesRegex(Blocked, 'incomplete'):
                    graph.invoke({}, config, durability='sync')
                self.assertIn('first', owner.store.completed_checkpoints('graph-recovery'))
            with graph_saver(owner) as saver:
                graph = task_graph(engine, saver, review=True)
                if fail_escalation or fail_check:
                    with self.assertRaisesRegex(Blocked, 'stop and notify the owner'):
                        graph_recovery_action(engine, graph, config, action, diagnosis=DIAGNOSIS)
                    with self.assertRaisesRegex(Blocked, 'owner direction required'):
                        graph_recovery_action(engine, graph, config, 'fresh', diagnosis=DIAGNOSIS)
                    self.assertEqual(calls, [('worker', 'worker'), ('worker', 'worker'), ('worker', 'strong')])
                    return
                result = graph_recovery_action(engine, graph, config, action, diagnosis=DIAGNOSIS)
                self.assertEqual(result['result']['status'], 'complete')
                self.assertEqual(result['result']['sha'], git(project, 'rev-parse', 'HEAD').decode().strip())
                failure = owner.store.db.execute("SELECT details FROM execution_history WHERE run_id='graph-recovery' AND task_id='second' AND kind='worker_invocation' AND state='failed'").fetchone()
                self.assertEqual(result['checkpoints']['second']['correction_chain'][0], json.loads(failure['details'])['invocation_id'])
            self.assertEqual(len(calls), 4)
            self.assertEqual(calls[2], ('worker', 'strong' if action == 'escalate' else 'worker'))
            self.assertEqual(calls[-1], ('review', 'reviewer'))
            if action == 'escalate':
                escalation = [json.loads(row['details']) for row in owner.store.db.execute(
                    "SELECT details FROM execution_history WHERE run_id='graph-recovery' "
                    "AND task_id='second' AND kind='implementation_escalation' ORDER BY seq")]
                self.assertEqual(escalation[0]['invocation_id'], escalation[-1]['producer_invocation_id'])
                self.assertTrue(escalation[-1]['recovery_id'])
        self.assertEqual((project/'unrelated.txt').read_text(), 'preserve\n')
        self.assertEqual(git(project, 'show', 'HEAD:first.txt'), b'complete\n')
        self.assertEqual(git(project, 'show', 'HEAD:owned.txt'), b'fixed\n')
        self.assertIn(DIAGNOSIS, prompts[2])
        self.assertIn('this owner-authorized workflow launch approves implementation', prompts[2])
        self.assertIn('Small isolated tests and local test databases', prompts[2])
        self.assertIn('second task', prompts[2])
        self.assertIn('https://example.invalid/issue', prompts[2])

    def test_action_reconciles_returned_call_without_replaying(self):
        calls, project = [], self.project
        class Adapter:
            def __init__(self, *_args, **_kwargs):
                self.saved_session = {'id': 'saved', 'file': '/fixture/saved'}
            def prompt(self, _prompt, **kwargs):
                calls.append('worker')
                kwargs['claim']('owned.txt')
                (project/'owned.txt').write_text('settled\n')
                return 'complete'
        contract = admit([{'id': 'one', 'description': 'work', 'owned_paths': ['owned.txt']}])
        config = {'configurable': {'thread_id': 'settled'}}
        with Authority(project) as owner:
            owner.store.start('settled', self.base, contract=contract, executor=EXECUTOR)
            engine = Engine(owner, 'settled', contract, EXECUTOR, adapter=Adapter, resume=True)
            original = owner.store.history
            def crash(run, task, kind, status, details=None, **kwargs):
                result = original(run, task, kind, status, details, **kwargs)
                if kind == 'worker_invocation' and status == 'returned':
                    raise KeyboardInterrupt()
                return result
            with graph_saver(owner) as saver:
                graph = task_graph(engine, saver)
                with patch.object(owner.store, 'history', side_effect=crash):
                    with self.assertRaises(KeyboardInterrupt): graph.invoke({}, config, durability='sync')
            with graph_saver(owner) as saver:
                result = graph_recovery_action(engine, task_graph(engine, saver), config, 'fresh', diagnosis=DIAGNOSIS)
                self.assertIn('one', result['checkpoints'])
        self.assertEqual(calls, ['worker'])
        self.assertEqual(git(project, 'show', 'HEAD:owned.txt'), b'settled\n')

    def test_unfinished_escalation_cannot_release_completed_task(self):
        calls = []
        class Adapter:
            def __init__(self, *_args, **_kwargs): calls.append('opened')
        contract = admit([{'id': 'one', 'description': 'work'}])
        config = {'configurable': {'thread_id': 'unsettled-escalation'}}
        with Authority(self.project) as owner:
            owner.store.start('unsettled-escalation', self.base, contract=contract, executor=EXECUTOR)
            owner.store.history('unsettled-escalation', 'one', 'implementation_escalation', 'started', {'action': 'escalate'})
            engine = Engine(owner, 'unsettled-escalation', contract, EXECUTOR, adapter=Adapter, resume=True)
            with graph_saver(owner) as saver:
                graph = task_graph(engine, saver, review=True)
                with self.assertRaisesRegex(Blocked, 'unresolved.*stop and notify'):
                    graph.invoke({}, config, durability='sync')
                with self.assertRaisesRegex(Blocked, 'owner direction required'):
                    graph_recovery_action(engine, graph, config, 'fresh', diagnosis=DIAGNOSIS)
        self.assertEqual(calls, [])

    def test_settled_sdk_error_allows_fresh_recovery_and_unattested_error_blocks(self):
        # (case, host attested settled, a session was opened before the error)
        for case, settled, opened in (('pre-session', True, False), ('overflow', True, True), ('unattested', False, True)):
            with self.subTest(case=case):
                project, calls, thread = self.project, [], 'sdk-error-' + case
                class Adapter:
                    def __init__(self, *_args, **_kwargs): self.saved_session = None
                    def prompt(self, prompt, **kwargs):
                        if kwargs.get('read_only'):
                            return json.dumps({'approved': True, 'findings': [], 'coverage': ['fixture'], 'coverage_gaps': []})
                        calls.append('worker')
                        self.saved_session = self.opened_session = (
                            {'id': thread + str(len(calls)), 'file': '/fixture/' + thread} if opened or len(calls) > 1 else None)
                        if len(calls) == 1:
                            record = {'type': 'error', 'message': 'SDK fixture failure', **({'settled': True} if settled else {})}
                            raise Blocked(sdk_error_detail(record, kwargs['pause_questions']))
                        kwargs['claim']('owned.txt')
                        (project/'owned.txt').write_text(thread + '\n')
                        return 'complete'
                contract = admit([{'id': 'one', 'description': 'parser', 'owned_paths': ['owned.txt']}])
                config = {'configurable': {'thread_id': thread}}
                with Authority(project) as owner:
                    owner.store.start(thread, self.base, contract=contract, executor=EXECUTOR)
                    engine = Engine(owner, thread, contract, EXECUTOR, adapter=Adapter, resume=True)
                    with graph_saver(owner) as saver:
                        graph = task_graph(engine, saver)
                        with self.assertRaisesRegex(Blocked, 'SDK fixture failure'):
                            graph.invoke({}, config, durability='sync')
                        if not settled:
                            for action in ('continue', 'fresh', 'escalate'):
                                with self.assertRaisesRegex(Blocked, 'effects are uncertain'):
                                    graph_recovery_action(engine, graph, config, action, diagnosis=DIAGNOSIS)
                            self.assertEqual(calls, ['worker'])
                            continue
                        if not opened:
                            with self.assertRaisesRegex(Blocked, 'needs the exact saved session'):
                                graph_recovery_action(engine, graph, config, 'continue', diagnosis=DIAGNOSIS)
                        graph_recovery_action(engine, graph, config, 'fresh', diagnosis=DIAGNOSIS)
                        self.assertIn('one', owner.store.completed_checkpoints(thread))
                        self.assertEqual(calls, ['worker', 'worker'])

    def test_effect_drift_and_unknown_diagnosis_stop_before_dispatch(self):
        calls, project = [], self.project
        class Adapter:
            def __init__(self, *_args, **_kwargs): self.saved_session = None
            def prompt(self, _prompt, **kwargs):
                calls.append('worker')
                self.saved_session = self.opened_session = {'id': 'saved', 'file': '/fixture/saved'}
                kwargs['claim']('owned.txt')
                (project/'owned.txt').write_text('partial\n')
                return TaskOutcome('incomplete', 'inspected missing parser')
        contract = admit([{'id': 'one', 'description': 'parser', 'owned_paths': ['owned.txt']}])
        config = {'configurable': {'thread_id': 'drift'}}
        with Authority(project) as owner:
            owner.store.start('drift', self.base, contract=contract, executor=EXECUTOR)
            engine = Engine(owner, 'drift', contract, EXECUTOR, adapter=Adapter, resume=True)
            with graph_saver(owner) as saver:
                graph = task_graph(engine, saver)
                with self.assertRaises(Blocked): graph.invoke({}, config, durability='sync')
                with self.assertRaisesRegex(Blocked, 'substantive'):
                    graph_recovery_action(engine, graph, config, 'fresh', diagnosis='unknown')
                with patch('coherence_workflow.processes.inspect_recorded_writers', side_effect=Blocked('live child')):
                    with self.assertRaisesRegex(Blocked, 'live child'):
                        graph_recovery_action(engine, graph, config, 'fresh', diagnosis=DIAGNOSIS)
                (project/'owned.txt').write_text('changed outside worker\n')
                with self.assertRaisesRegex(Blocked, 'effects drifted'):
                    graph_recovery_action(engine, graph, config, 'fresh', diagnosis=DIAGNOSIS)
        self.assertEqual(calls, ['worker'])

    def verification_retry(self, case):
        test, project, calls = self, self.project, []
        def head(): return git(project, 'rev-parse', 'HEAD').decode().strip()
        self.write('runbook.txt', 'offline')
        git(project, 'add', '--', 'runbook.txt')
        git(project, 'commit', '-qm', 'baseline verifier input', '--', 'runbook.txt')
        self.base = head()
        diagnosis = 'The local parser check settled without external effects; rerun all offline checks on the repaired fixture.'
        check = [sys.executable, '-c', 'from pathlib import Path; assert Path("runbook.txt").read_text() == "offline"; assert Path("other.txt").read_text() == "fixed"; print("checked fixture")']
        verifier = {'id': 'verify', 'description': 'offline verification', 'depends': ['producer'], 'checks': [check], 'paths': ['fixtures/', 'runbook.txt']}
        if case != 'undeclared':
            verifier['owned_paths'] = []
        contract = admit([{'id': 'producer', 'description': 'produce fixture', 'owned_paths': ['owned.txt']},
                          verifier, {'id': 'after', 'description': 'dependent', 'depends': ['verify']}])

        class Adapter:
            def __init__(self, *_args, **_kwargs): self.saved_session = None
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    calls.append('review')
                    test.assertIn('Original range: ' + test.base + '..' + target, prompt)
                    test.assertIn('task verify: no commit changes', prompt)
                    return json.dumps({'approved': True, 'findings': [], 'coverage': ['fixture'], 'coverage_gaps': []})
                self.saved_session = self.opened_session = {'id': str(len(calls)), 'file': '/fixture/session'}
                if 'produce fixture' in prompt:
                    calls.append('producer')
                    kwargs['claim']('owned.txt')
                    test.write('owned.txt', 'produced')
                    return 'produced fixture'
                if 'offline verification' not in prompt:
                    calls.append('after')
                    return 'dependent complete'
                calls.append('verify')
                if len(calls) == 2:
                    return TaskOutcome('failed', 'old fixture failed offline verification')
                test.assertIsNone(kwargs.get('saved_session'))
                if case == 'second repair' and len(calls) == 3:
                    return TaskOutcome('failed', 'fixture is still broken')
                test.assertIn('security/data restriction, or external-operation restriction', prompt)
                test.assertIn('explicit manual gates', prompt)
                test.assertIn('This authority is not proof that checks succeeded', prompt)
                with test.assertRaisesRegex(Blocked, 'outside optional owned_paths'):
                    kwargs['claim']('owned.txt')
                kwargs['command']('start', 'git rev-parse HEAD')
                proof = 'fresh proof at ' + head()
                kwargs['command']('end', 'git rev-parse HEAD')
                return proof

        run = 'verification'
        config = {'configurable': {'thread_id': run}}
        with Authority(project) as owner:
            def events(kind, state):
                return [json.loads(row[0]) for row in owner.store.db.execute(
                    'SELECT details FROM execution_history WHERE run_id=? AND task_id=? AND kind=? AND state=? ORDER BY seq',
                    (run, 'verify', kind, state))]
            runner = Engine(owner, run, contract, EXECUTOR, adapter=Adapter, paid_scope={'apis': []},
                            question=lambda *_: self.fail('routine verification asked owner'))
            # Model an old attempt without an optional metrics file. On retry the
            # real capture/finalizer can create a committable JSONL for the first time.
            metrics = case == 'metrics interruption'
            with (patch.object(runner, '_append_metric') if metrics else contextlib.nullcontext()), \
                 self.assertRaisesRegex(Blocked, 'explicitly failed'):
                runner.invoke()
            failed_head = head()
            before = owner.store.completed_checkpoints(run)
            failures = events('worker_invocation', 'failed')
            self.write('other.txt', 'broken' if case in ('check failure', 'second repair') else 'fixed')
            if metrics:
                self.write('.gitignore', '.coherence/workflow/\n')
            git(project, 'commit', '-qam', 'external fixture repair')
            target = head()
            runner = Engine(owner, run, contract, EXECUTOR, adapter=Adapter, paid_scope={'apis': []}, resume=True)
            with graph_saver(owner) as saver:
                graph = task_graph(runner, saver, review=True)
                def retry(commit, reason=diagnosis):
                    return graph_recovery_action(runner, graph, config, 'fresh', diagnosis=reason, target_head=commit)
                if case == 'undeclared':
                    with self.assertRaisesRegex(Blocked, 'explicit empty owned_paths'): retry(target)
                    self.assertEqual(calls, ['producer', 'verify'])
                    return
                # A verification task proves one exact HEAD: a new commit needs a pinned target.
                with self.assertRaisesRegex(Blocked, 'effects drifted'): retry(None)
                with self.assertRaisesRegex(Blocked, 'differs from HEAD'): retry(failed_head)
                if case == 'second repair':
                    with self.assertRaisesRegex(Blocked, 'explicitly failed'): retry(target)
                    first_target = target
                    self.write('other.txt', 'fixed')
                    git(project, 'commit', '-qm', 'second fixture repair', '--', 'other.txt')
                    target = head()
                    with self.assertRaisesRegex(Blocked, 'differs from HEAD'):
                        graph.invoke(None, config, durability='sync')
                    result = retry(target, 'The first local retry settled without external effects but its fixture was still broken; verify the corrected data.')
                    self.assertEqual(calls, ['producer', 'verify', 'verify', 'verify', 'after', 'review'])
                    self.assertEqual(result['checkpoints']['verify']['sha'], target)
                    refs = [row['reference'] for row in events('graph_recovery', 'recorded')]
                    self.assertEqual([(r['failed_head'], r['target_head']) for r in refs],
                                     [(failed_head, first_target), (first_target, target)])
                    self.assertEqual([r['invocation_id'] for r in refs],
                                     [row['invocation_id'] for row in events('worker_invocation', 'failed')])
                    return
                if case == 'pass':
                    self.write('runbook.txt', 'uncommitted instructions')
                    with self.assertRaisesRegex(Blocked, 'runbook.txt'): retry(target)
                    self.write('runbook.txt', 'offline')
                    self.write('other.txt', 'next repair')
                    with self.assertRaisesRegex(Blocked, 'uncommitted changes'): retry(target)
                    git(project, 'commit', '-qm', 'later fixture revision', '--', 'other.txt')
                    with self.assertRaisesRegex(Blocked, 'direct single-parent'): retry(head())
                    git(project, 'switch', '--detach', target)
                    (project/'fixtures').mkdir()
                    self.write('fixtures/new', 'new check input')
                    with self.assertRaisesRegex(Blocked, 'fixtures/new'): retry(target)
                    (project/'fixtures/new').unlink()
                    self.write('STATE.md', 'unrelated staged')
                    git(project, 'add', '--', 'STATE.md')
                    (project/'STATE.md').unlink()
                    self.write('notes.tmp', 'unrelated untracked')
                if case == 'check failure':
                    with self.assertRaisesRegex(Blocked, 'required verification failed'): retry(target)
                    self.assertEqual(calls, ['producer', 'verify', 'verify'])
                    self.assertEqual(before, owner.store.completed_checkpoints(run))
                    return
                if case == 'checkpoint interruption':
                    record = owner.store.history
                    def lose_checkpoint(*args, **kwargs):
                        if args[2:4] == ('checkpoint', 'passed'): raise KeyboardInterrupt()
                        return record(*args, **kwargs)
                    with patch.object(owner.store, 'history', side_effect=lose_checkpoint), self.assertRaises(KeyboardInterrupt):
                        retry(target)
                if metrics or case == 'drift':
                    record = owner.store.history
                    def interrupt(*args, **kwargs):
                        record(*args, **kwargs)
                        if args[2:4] == ('worker_invocation', 'returned'): raise KeyboardInterrupt()
                    with patch.object(owner.store, 'history', side_effect=interrupt), self.assertRaises(KeyboardInterrupt):
                        run_graph(runner, action='fresh', diagnosis=diagnosis, target_head=target)
                    if metrics:
                        self.assertEqual(head(), target)
                        metric = artifact_relative(run)
                        self.assertEqual(git(project, 'status', '--porcelain', '--', metric).decode().strip(), '?? ' + metric)
                        row = json.loads((project/metric).read_text())
                        self.assertEqual(row['invocation_id'], events('worker_invocation', 'returned')[-1]['invocation_id'])
                if case == 'drift':
                    self.write('other.txt', 'unexpected')
                    git(project, 'commit', '-qm', 'later change', '--', 'other.txt')
                    with self.assertRaisesRegex(Blocked, 'differs from HEAD'):
                        task_graph(runner, saver, review=True).invoke(None, config, durability='sync')
                    self.assertEqual(calls, ['producer', 'verify', 'verify'])
                    self.assertEqual(before, owner.store.completed_checkpoints(run))
                    return
        # Public source CLI reopens the stopped thread with its original inputs.
        out = io.StringIO()
        with patch.object(cli, 'PiAdapter', Adapter), contextlib.redirect_stdout(out):
            args = [] if metrics or case == 'checkpoint interruption' else [
                '--recovery-action', 'fresh', '--target-head', target, '--diagnosis', diagnosis]
            self.assertEqual(cli.main(['resume', '--project', str(project), '--run', run, *args]), 0, out.getvalue())
        self.assertEqual(calls, ['producer', 'verify', 'verify', 'after', 'review'])
        self.assertEqual(head(), target)
        if case == 'pass':
            self.assertEqual(git(project, 'show', ':STATE.md'), b'unrelated staged')
            self.assertFalse((project/'STATE.md').exists())
            self.assertEqual((project/'notes.tmp').read_text(), 'unrelated untracked')
        with Authority(project) as owner:
            after = owner.store.completed_checkpoints(run)
            self.assertEqual(before, {'producer': after['producer']})
            self.assertEqual(failures, events('worker_invocation', 'failed'))
            proof, = events('worker_invocation', 'returned')
            checked, = events('graph_checks', 'recorded')
            self.assertEqual(proof['summary'], 'fresh proof at ' + target)
            self.assertEqual((proof['head'], checked['effects']['head']), (target, target))
            self.assertEqual(checked['checks'][0]['output'].strip(), 'checked fixture')
            self.assertEqual(checked['producer_invocation_id'], proof['invocation_id'])
            cp = after['verify']
            self.assertEqual((cp['baseline'], cp['sha'], cp['no_change'], cp['paths']), (target, target, True, []))
            self.assertEqual(cp['correction_chain'], [failures[0]['invocation_id'], proof['invocation_id']])
            reference = events('graph_recovery', 'recorded')[0]['reference']
            self.assertEqual((reference['failed_head'], reference['target_head']), (failed_head, target))

    def test_explicit_second_repair_after_pinned_worker_fails(self): self.verification_retry('second repair')
    def test_fresh_verification_at_repair_commit(self): self.verification_retry('pass')
    def test_pinned_interruption_leaves_real_metrics_uncommitted_on_reopen(self): self.verification_retry('metrics interruption')
    def test_target_verification_needs_empty_ownership(self): self.verification_retry('undeclared')
    def test_pinned_no_change_intent_reopens_without_replay(self): self.verification_retry('checkpoint interruption')
    def test_failed_target_check_blocks_dependent(self): self.verification_retry('check failure')
    def test_returned_verification_reopen_checks_target_without_replay(self): self.verification_retry('drift')

    def test_continue(self): self.exercise('continue')
    def test_fresh(self): self.exercise('fresh')
    def test_escalate(self): self.exercise('escalate')
    def test_failed_escalation_stops(self): self.exercise('escalate', fail_escalation=True)
    def test_escalation_check_failure_stops(self): self.exercise('escalate', fail_check=True)


class WorkerRecoveryTests(ProjectTest):
    def adapter(self, calls, *, failure=None):
        project = self.project
        class Adapter:
            def __init__(self, _project, executor, **_kwargs):
                self.model = executor['model']
                self.saved_session = None
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    calls.append(('review', self.model))
                    return json.dumps({'approved': True, 'findings': [], 'coverage': ['fixture'], 'coverage_gaps': []})
                self.saved_session = self.opened_session = kwargs.get('saved_session') or self.saved_session or {
                    'id': self.model + '-' + str(len(calls)), 'file': '/fixture/' + self.model + '.jsonl'}
                calls.append(('worker', self.model))
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('partial\n' if len(calls) == 1 else 'implemented\n')
                if len(calls) == 1:
                    return TaskOutcome('incomplete', 'parser missing')
                if failure:
                    return TaskOutcome('failed', failure)
                return 'implemented parser and verified fixture'
        return Adapter

    def contract(self, checks=None):
        return {'tasks': [{'id': 'one', 'description': 'implement parser', 'owned_paths': ['owned.txt'],
                           'checks': checks or []},
                          {'id': 'two', 'description': 'dependent', 'depends': ['one'], 'owned_paths': ['owned.txt']}]}

    def start_failure(self, owner, contract, adapter, executor=EXECUTOR, paid_scope=None):
        with self.assertRaises(Blocked):
            Engine(owner, 'recovery', contract, executor, adapter=adapter, paid_scope=paid_scope).invoke()
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def no_owner_question(self, prompt):
        self.fail('routine recovery must not ask for owner input: ' + prompt)

    def test_fresh_context_keeps_partial_ownership_checkpoints_history_and_review(self):
        calls, contract = [], self.contract()
        adapter = self.adapter(calls)
        self.project.joinpath('unrelated.txt').write_text('preserve me\n')
        with Authority(self.project) as owner:
            self.start_failure(owner, contract, adapter)
            owner.store.resume('recovery')
            result = Engine(owner, 'recovery', contract, EXECUTOR, adapter=adapter, resume=True,
                            question=self.no_owner_question,
                            worker_recovery={'action': 'fresh', 'diagnosis': DIAGNOSIS}).invoke()
            history = [dict(row) for row in owner.store.db.execute(
                "SELECT kind,state,details FROM execution_history WHERE run_id='recovery'")]
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(calls, [('worker', 'worker')] * 3 + [('review', 'reviewer')])
        self.assertEqual(self.project.joinpath('unrelated.txt').read_text(), 'preserve me\n')
        self.assertEqual(git(self.project, 'show', 'HEAD:owned.txt'), b'implemented\n')
        self.assertEqual(sum(row['kind'] == 'worker_invocation' and row['state'] == 'failed' for row in history), 1)
        reservation = next(json.loads(row['details']) for row in history
                           if row['kind'] == 'worker_dispatch' and 'recovery' in json.loads(row['details']))
        self.assertEqual(reservation['recovery']['action'], 'fresh')

    def test_escalation_uses_configured_implementation_profile_not_reviewer(self):
        calls, contract = [], self.contract()
        adapter = self.adapter(calls)
        with Authority(self.project) as owner:
            self.start_failure(owner, contract, adapter)
            owner.store.resume('recovery')
            result = Engine(owner, 'recovery', contract, EXECUTOR, adapter=adapter, resume=True,
                            question=self.no_owner_question,
                            worker_recovery={'action': 'escalate', 'diagnosis': DIAGNOSIS}).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(calls, [('worker', 'worker'), ('worker', 'strong'), ('worker', 'worker'), ('review', 'reviewer')])

    def test_failed_escalation_stops_and_plain_resume_cannot_retry(self):
        calls, contract = [], self.contract()
        adapter = self.adapter(calls, failure='strong worker could not resolve parser')
        with Authority(self.project) as owner:
            self.start_failure(owner, contract, adapter)
            owner.store.resume('recovery')
            with self.assertRaisesRegex(Blocked, 'escalation failed.*stop and notify the owner.*owner direction required'):
                Engine(owner, 'recovery', contract, EXECUTOR, adapter=adapter, resume=True,
                       question=self.no_owner_question,
                       worker_recovery={'action': 'escalate', 'diagnosis': DIAGNOSIS}).invoke()
        # Reopen storage to prove the stop is durable, not an in-memory flag.
        with Authority(self.project) as owner:
            owner.store.resume('recovery')
            with self.assertRaisesRegex(Blocked, 'stop and notify the owner.*owner direction required'):
                Engine(owner, 'recovery', contract, EXECUTOR, adapter=adapter, resume=True,
                       question=self.no_owner_question,
                       worker_recovery={'action': 'fresh', 'diagnosis': DIAGNOSIS}).invoke()
            self.assertFalse(owner.store.completed_checkpoints('recovery'))
        self.assertEqual(calls, [('worker', 'worker'), ('worker', 'strong')])
        self.assertEqual(self.project.joinpath('owned.txt').read_text(), 'implemented\n')

    def test_escalation_required_check_failure_never_dispatches_correction_or_dependent(self):
        calls = []
        contract = self.contract([[sys.executable, '-c', 'raise SystemExit(7)']])
        adapter = self.adapter(calls)
        with Authority(self.project) as owner:
            self.start_failure(owner, contract, adapter)
            owner.store.resume('recovery')
            with self.assertRaisesRegex(Blocked, 'escalation required check failed; stop and notify'):
                Engine(owner, 'recovery', contract, EXECUTOR, adapter=adapter, resume=True,
                       worker_recovery={'action': 'escalate', 'diagnosis': DIAGNOSIS}).invoke()
            self.assertFalse(owner.store.completed_checkpoints('recovery'))
        self.assertEqual(calls, [('worker', 'worker'), ('worker', 'strong')])

    def test_escalation_without_explicit_profile_is_not_reviewer_fallback(self):
        calls, contract = [], self.contract()
        adapter = self.adapter(calls)
        executor = {key: value for key, value in EXECUTOR.items() if key != 'implementation_fallback'}
        with Authority(self.project) as owner:
            self.start_failure(owner, contract, adapter, executor)
            owner.store.resume('recovery')
            with self.assertRaisesRegex(Blocked, 'no permitted fallback'):
                Engine(owner, 'recovery', contract, executor, adapter=adapter, resume=True,
                       worker_recovery={'action': 'escalate', 'diagnosis': DIAGNOSIS}).invoke()
        self.assertEqual(calls, [('worker', 'worker')])

    def test_exhausted_session_can_be_replaced_without_resetting_history(self):
        calls, contract = [], self.contract()
        base_adapter = self.adapter(calls)
        class Adapter(base_adapter):
            def prompt(self, prompt, **kwargs):
                result = super().prompt(prompt, **kwargs)
                if not kwargs.get('read_only') and len(calls) <= 3:
                    return TaskOutcome('incomplete', 'inspected parser missing')
                return result
        adapter = Adapter
        with Authority(self.project) as owner:
            self.start_failure(owner, contract, adapter)
            for _ in range(2):
                owner.store.resume('recovery')
                with self.assertRaisesRegex(Blocked, 'incomplete'):
                    Engine(owner, 'recovery', contract, EXECUTOR, adapter=adapter, resume=True,
                           worker_recovery={'action': 'continue', 'diagnosis': DIAGNOSIS}).invoke()
            row = owner.store.db.execute("SELECT details FROM execution_history WHERE kind='worker_invocation' AND state='failed' ORDER BY seq DESC LIMIT 1").fetchone()
            identity = json.loads(row['details'])['session']
            with self.assertRaisesRegex(Blocked, 'allowance exhausted'):
                owner.store.reserve_worker_dispatch('recovery', 'one', 'fourth', identity)
            owner.store.resume('recovery')
            result = Engine(owner, 'recovery', contract, EXECUTOR, adapter=adapter, resume=True,
                            question=self.no_owner_question,
                            worker_recovery={'action': 'fresh', 'diagnosis': DIAGNOSIS}).invoke()
            count = owner.store.db.execute("SELECT count(*) FROM execution_history WHERE task_id='one' AND kind='worker_dispatch' AND state='reserved'").fetchone()[0]
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(count, 4)

    def test_cli_routes_recovery_without_owner_or_replacement_inputs(self):
        calls, contract = [], self.contract()
        adapter = self.adapter(calls)
        with Authority(self.project) as owner:
            self.start_failure(owner, contract, adapter, paid_scope={'apis': []})
        env = {key: '' for key in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                                  'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}
        output = io.StringIO()
        with patch.dict(os.environ, env), patch.object(cli, 'PiAdapter', adapter), contextlib.redirect_stdout(output):
            code = cli.main(['resume', '--project', str(self.project), '--run', 'recovery',
                             '--recovery-action', 'escalate', '--diagnosis', DIAGNOSIS])
        self.assertEqual(code, 0, output.getvalue())
        self.assertEqual(calls, [('worker', 'worker'), ('worker', 'strong'), ('worker', 'worker'), ('review', 'reviewer')])

    def test_escalation_checkpoint_failure_stops_without_corrective_dispatch(self):
        calls, contract = [], self.contract()
        adapter = self.adapter(calls)
        with Authority(self.project) as owner:
            self.start_failure(owner, contract, adapter)
            owner.store.resume('recovery')
            with patch.object(engine.FocusedGit, 'checkpoint', side_effect=Blocked('fixture hook failure')):
                with self.assertRaisesRegex(Blocked, 'escalation failed.*stop and notify.*hook failure'):
                    Engine(owner, 'recovery', contract, EXECUTOR, adapter=adapter, resume=True,
                           worker_recovery={'action': 'escalate', 'diagnosis': DIAGNOSIS}).invoke()
        self.assertEqual(calls, [('worker', 'worker'), ('worker', 'strong')])
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def post_checkpoint_failure(self, *, interrupt, dependent):
        calls, contract = [], self.contract()
        if not dependent:
            contract['tasks'] = contract['tasks'][:1]
        adapter = self.adapter(calls)
        with Authority(self.project) as owner:
            self.start_failure(owner, contract, adapter)
            owner.store.resume('recovery')
            original_task = owner.store.task
            def failed_completion(*args, **kwargs):
                if args[1:3] == ('one', 'complete'):
                    if interrupt:
                        raise KeyboardInterrupt('fixture post-checkpoint interruption')
                    raise OSError('fixture task-completion write failed')
                return original_task(*args, **kwargs)
            expected = KeyboardInterrupt if interrupt else Blocked
            with patch.object(owner.store, 'task', side_effect=failed_completion), self.assertRaises(expected):
                Engine(owner, 'recovery', contract, EXECUTOR, adapter=adapter, resume=True,
                       worker_recovery={'action': 'escalate', 'diagnosis': DIAGNOSIS}).invoke()
            checkpoint = git(self.project, 'rev-parse', 'HEAD')
            self.assertNotEqual(checkpoint.decode().strip(), self.base)
            self.assertTrue(owner.store.db.execute(
                "SELECT 1 FROM execution_history WHERE kind='checkpoint' AND state='passed'").fetchone())
        with Authority(self.project) as owner:
            owner.store.resume('recovery')
            with self.assertRaisesRegex(Blocked, 'stop and notify the owner.*owner direction required'):
                Engine(owner, 'recovery', contract, EXECUTOR, adapter=adapter, resume=True,
                       question=self.no_owner_question).invoke()
            state = owner.store.db.execute("SELECT state FROM execution_runs WHERE run_id='recovery'").fetchone()[0]
        self.assertEqual(state, 'failed')
        self.assertEqual(calls, [('worker', 'worker'), ('worker', 'strong')])
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD'), checkpoint)

    def test_post_checkpoint_escalation_completion_failure_blocks_dependent_dispatch(self):
        self.post_checkpoint_failure(interrupt=False, dependent=True)

    def test_post_checkpoint_escalation_interruption_blocks_final_review(self):
        self.post_checkpoint_failure(interrupt=True, dependent=False)

    def external_completion_after_escalation(self, *, check_passes):
        calls = []
        check = [sys.executable, '-c', 'from pathlib import Path; assert Path("owned.txt").read_text() == "external\\n"']
        contract = self.contract([check])
        adapter = self.adapter(calls, failure='strong worker failed')
        with Authority(self.project) as owner:
            self.start_failure(owner, contract, adapter)
            owner.store.resume('recovery')
            with self.assertRaisesRegex(Blocked, 'escalation failed'):
                Engine(owner, 'recovery', contract, EXECUTOR, adapter=adapter, resume=True,
                       worker_recovery={'action': 'escalate', 'diagnosis': DIAGNOSIS}).invoke()
            last = owner.store.db.execute(
                "SELECT details FROM execution_history WHERE kind='worker_invocation' ORDER BY seq DESC LIMIT 1").fetchone()
            content = b'external\n' if check_passes else b'still broken\n'
            self.project.joinpath('owned.txt').write_bytes(content)
            transfer = {'task_id': 'one', 'invocation_id': json.loads(last['details'])['invocation_id'],
                        'head': self.base, 'diagnosis': DIAGNOSIS, 'worker': 'owner-authorized external fixture',
                        'summary': 'External implementation with original acceptance; independent review remains.',
                        'paths': {'owned.txt': {'sha256': hashlib.sha256(content).hexdigest(),
                                               'mode': self.project.joinpath('owned.txt').stat().st_mode & 0o777}}}
            runner = Engine(owner, 'recovery', contract, EXECUTOR, resume=True)
            if not check_passes:
                with self.assertRaises(Blocked):
                    runner.recover_task(transfer, owner_authorized=True)
                owner.store.resume('recovery')
            test = self
            class Healthy:
                def __init__(self, *_args, **_kwargs):
                    self.saved_session = self.opened_session = {'id': 'healthy', 'file': '/fixture/healthy'}
                def prompt(self, _prompt, **kwargs):
                    if kwargs.get('read_only'):
                        calls.append(('review', 'reviewer'))
                        return json.dumps({'approved': True, 'findings': [], 'coverage': ['original range'], 'coverage_gaps': []})
                    calls.append(('dependent', 'worker'))
                    test.assertTrue(check_passes, 'unchecked external completion must not dispatch')
                    return 'dependent no-change'
            continuation = Engine(owner, 'recovery', contract, EXECUTOR, adapter=Healthy, resume=True,
                                  question=self.no_owner_question)
            if check_passes:
                with graph_saver(owner) as saver:
                    graph = task_graph(continuation, saver, review=True)
                    config = {'configurable': {'thread_id': 'recovery'}}
                    checkpoint = graph_recovery_action(continuation, graph, config, 'external',
                                                       transfer=transfer, owner_authorized=True)
                    self.assertEqual(checkpoint['paths'], ['owned.txt'])
                    self.assertEqual(calls, [('worker', 'worker'), ('worker', 'strong')])
                    result = graph.invoke(None, config, durability='sync')
                self.assertEqual(result['result']['status'], 'complete')
                self.assertEqual(result['checkpoints']['one']['paths'], ['owned.txt'])
                self.assertEqual(calls, [('worker', 'worker'), ('worker', 'strong'),
                                         ('dependent', 'worker'), ('review', 'reviewer')])
                self.assertTrue(owner.store.db.execute(
                    "SELECT 1 FROM execution_history WHERE kind='implementation_escalation' AND state='failed'").fetchone())
            else:
                with self.assertRaisesRegex(Blocked, 'owner direction required'):
                    continuation.invoke()
                self.assertEqual(calls, [('worker', 'worker'), ('worker', 'strong')])

    def test_owner_authorized_checked_external_completion_releases_escalation_stop(self):
        self.external_completion_after_escalation(check_passes=True)

    def test_failed_external_completion_does_not_release_escalation_stop(self):
        self.external_completion_after_escalation(check_passes=False)

    def test_recovery_requires_diagnosis_and_exact_settled_history(self):
        with Authority(self.project) as owner:
            for diagnosis in ('', 'retry', 'unknown'):
                with self.assertRaisesRegex(Blocked, 'substantive cause-specific'):
                    Engine(owner, 'recovery', self.contract(), EXECUTOR, resume=True,
                           worker_recovery={'action': 'fresh', 'diagnosis': diagnosis})
            owner.store.start('recovery', self.base)
            owner.store.reserve_worker_dispatch('recovery', 'one', 'uncertain', None)
            with self.assertRaisesRegex(Blocked, 'unbound fresh session'):
                owner.store.reserve_worker_dispatch('recovery', 'one', 'replacement', None,
                    recovery={'action': 'fresh', 'diagnosis': DIAGNOSIS, 'predecessor': 'uncertain'})
