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
from coherence_workflow.pi_adapter import TaskOutcome
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'worker', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'reviewer', 'effort': 'medium'},
            'implementation_fallback': {'provider': 'fixture', 'model': 'strong', 'effort': 'medium'}}
DIAGNOSIS = 'Inspected the partial implementation: missing parser; implement it using the retained source and checks.'


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
        adapter = self.adapter(calls)
        with Authority(self.project) as owner:
            self.start_failure(owner, contract, adapter)
            row = owner.store.db.execute("SELECT details FROM execution_history WHERE kind='worker_invocation' AND state='failed'").fetchone()
            identity = json.loads(row['details'])['saved_session']
            for ordinal in range(2):
                invocation = 'retained-correction-' + str(ordinal)
                owner.store.reserve_worker_dispatch('recovery', 'one', invocation, identity)
                owner.store.history('recovery', 'one', 'worker_invocation', 'failed',
                                    {'invocation_id': invocation, 'saved_session': identity,
                                     'reuse_key': json.loads(row['details'])['reuse_key']})
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
                        'paths': {'owned.txt': {'sha256': hashlib.sha256(content).hexdigest(), 'mode': 420}}}
            runner = Engine(owner, 'recovery', contract, EXECUTOR, resume=True)
            if check_passes:
                checkpoint = runner.recover_task(transfer, owner_authorized=True)
                self.assertEqual(checkpoint['paths'], ['owned.txt'])
            else:
                with self.assertRaises(Blocked):
                    runner.recover_task(transfer, owner_authorized=True)
            owner.store.resume('recovery')
            test = self
            class Healthy:
                def __init__(self, *_args, **_kwargs): pass
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
                self.assertEqual(continuation.invoke()['status'], 'complete')
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
