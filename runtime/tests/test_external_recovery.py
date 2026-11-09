"""Real local Git/Engine recovery; fake adapters never call a provider."""
import contextlib
import hashlib
import io
import json
from unittest.mock import patch

from coherence_workflow import cli
from coherence_workflow.engine import Engine
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest
from test_resume import EXECUTOR


class ExternalRecoveryTests(ProjectTest):
    def fail_run(self, checks=None, gates=None):
        project, calls = self.project, []
        class Adapter:
            def __init__(self, *_args, **_kwargs): self.saved_session = None
            def prompt(self, _prompt, **kwargs):
                calls.append('old')
                self.saved_session = self.opened_session = {'id': 'exhausted', 'file': '/private/fixture'}
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('partial\n')
                raise Blocked('inspected incomplete transport integration')
        contract = {'tasks': [
            {'id': 'one', 'description': 'original semantic acceptance', 'owned_paths': ['owned.txt'],
             'gates': gates or [], 'checks': checks or [['/bin/sh', '-c', 'test "$(cat owned.txt)" = recovered']]},
            {'id': 'two', 'description': 'dependent', 'depends': ['one'], 'owned_paths': ['next.txt']}]}
        for attempt in range(3):
            with Authority(project) as owner:
                if attempt: owner.store.resume('run')
                with self.assertRaisesRegex(Blocked, 'incomplete transport'):
                    Engine(owner, 'run', contract, EXECUTOR, adapter=Adapter, paid_scope={'agent_providers': ['fixture'], 'apis': []}, resume=bool(attempt),
                           question=lambda prompt: 'yes' if 'Approve this gate?' in prompt else 'inspected failure; targeted transport correction').invoke()
        self.assertEqual(calls, ['old'] * 3)
        self.write('owned.txt', 'recovered\n')
        self.write('other.txt', 'unknown unrelated bytes\n')
        with Authority(project) as owner:
            prior = owner.store.db.execute("SELECT details FROM execution_history WHERE kind='worker_invocation' ORDER BY seq DESC LIMIT 1").fetchone()
            invocation = json.loads(prior['details'])['invocation_id']
        self.contract, self.old_adapter, self.calls = contract, Adapter, calls
        return {'task_id': 'one', 'invocation_id': invocation, 'head': self.base,
                'diagnosis': 'Inspected exact exhausted session: incomplete transport integration; external same-task fix completed.',
                'worker': 'owner-authorized external fixture/alternate/medium',
                'summary': 'Original semantic acceptance completed externally; runner checks and review remain.',
                'paths': {'owned.txt': {'sha256': hashlib.sha256(b'recovered\n').hexdigest(), 'mode': 420}}}

    def recover(self, owner, transfer, authorized=True, question=lambda _: 'yes'):
        return Engine(owner, 'run', self.contract, EXECUTOR, adapter=self.old_adapter, resume=True,
                      question=question, paid_scope={'agent_providers': ['fixture'], 'apis': []}).recover_task(transfer, owner_authorized=authorized)

    def test_exhausted_external_completion_checkpoint_then_same_run(self):
        transfer = self.fail_run()
        git(self.project, 'add', '--', 'other.txt')
        with Authority(self.project) as owner:
            original = [tuple(row) for row in owner.store.db.execute(
                "SELECT * FROM execution_history WHERE kind IN ('worker_dispatch','worker_invocation')")]
            owner.store.resume('run')
            with self.assertRaisesRegex(Blocked, 'allowance exhausted'):
                Engine(owner, 'run', self.contract, EXECUTOR, adapter=self.old_adapter, paid_scope={'agent_providers': ['fixture'], 'apis': []}, resume=True,
                       question=lambda _: 'inspected targeted correction').invoke()
            result = self.recover(owner, transfer)
            self.assertFalse(result['no_change'])
            self.assertEqual(result['paths'], ['owned.txt'])
            self.assertEqual([tuple(row) for row in owner.store.db.execute(
                "SELECT * FROM execution_history WHERE kind IN ('worker_dispatch','worker_invocation')")], original)
            self.assertEqual(self.recover(owner, transfer)['sha'], result['sha'])
        calls, project = [], self.project
        class Healthy:
            def __init__(self, _project, executor, **_kwargs): calls.append(executor)
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    self_test.assertIn(self_test.base, prompt)
                    self_test.assertIn('external fixture/alternate/medium', prompt)
                    return '{"approved":true,"coverage":["full original range"],"coverage_gaps":[],"findings":[]}'
                kwargs['claim']('next.txt')
                project.joinpath('next.txt').write_text('next\n')
                return 'dependent done'
        self_test = self
        with Authority(project) as owner:
            owner.store.resume('run')
            outcome = Engine(owner, 'run', self.contract, EXECUTOR, adapter=Healthy, resume=True).invoke()
            self.assertEqual(outcome['status'], 'complete')
            self.assertEqual(owner.store.input('run')['executor'], EXECUTOR)
            reviewed = owner.store.db.execute(
                "SELECT review_base,review_head FROM execution_review_executions WHERE role='reviewer'").fetchone()
            self.assertEqual(reviewed['review_base'], self.base)
            self.assertEqual(reviewed['review_head'], outcome['sha'])
            self.assertNotEqual(reviewed['review_head'], result['sha'])
        self.assertEqual(self.calls, ['old'] * 3)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0]['model'], EXECUTOR['model'])
        self.assertEqual(calls[1], EXECUTOR['reviewer'])
        self.assertEqual(git(project, 'show', result['sha'] + ':owned.txt'), b'recovered\n')
        self.assertEqual(project.joinpath('other.txt').read_text(), 'unknown unrelated bytes\n')
        self.assertEqual(git(project, 'rev-list', '--count', self.base + '..HEAD').strip(), b'2')
        self.assertEqual(git(project, 'diff', '--cached', '--name-only').strip(), b'other.txt')

    def test_authority_drift_uncertainty_and_required_checks_block(self):
        transfer = self.fail_run()
        with Authority(self.project) as owner:
            with self.assertRaisesRegex(Blocked, 'owner authorization'):
                self.recover(owner, transfer, authorized=False)
            self.write('owned.txt', 'changed after transfer\n')
            with self.assertRaisesRegex(Blocked, 'bytes|drift'):
                self.recover(owner, transfer)
            self.write('owned.txt', 'recovered\n')
            with patch('coherence_workflow.processes.inspect_recorded_writers', side_effect=Blocked('unknown live worker')):
                with self.assertRaisesRegex(Blocked, 'unknown live worker'):
                    self.recover(owner, transfer)
            owner.store.history('run', 'one', 'worker_invocation', 'started', {'invocation_id': 'uncertain'})
            with self.assertRaisesRegex(Blocked, 'uncertain|terminal'):
                self.recover(owner, transfer)
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_failed_original_check_is_retained_without_provider_or_checkpoint(self):
        transfer = self.fail_run(checks=[['/bin/sh', '-c', 'echo original-failure; exit 7']])
        with Authority(self.project) as owner:
            with self.assertRaises(Blocked):
                self.recover(owner, transfer)
            check = owner.store.db.execute("SELECT details FROM execution_history WHERE kind='check' AND state='failed'").fetchone()
            self.assertIn('original-failure', check['details'])
            self.assertEqual(owner.store.db.execute("SELECT state FROM execution_tasks WHERE task_id='one'").fetchone()['state'], 'failed')
        self.assertEqual(self.calls, ['old'] * 3)
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_cli_requires_explicit_owner_flag(self):
        transfer = self.fail_run()
        path = self.root / 'transfer.json'
        path.write_text(json.dumps(transfer))
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(cli.main(['recover-task', '--project', str(self.project), '--run', 'run', '--recovery', str(path)]), 2)
            self.assertEqual(cli.main(['recover-task', '--project', str(self.project), '--run', 'run', '--recovery', str(path), '--owner-authorized']), 0)
        self.assertNotIn(transfer['summary'], output.getvalue())
        status = cli.status(self.project, 'run')
        self.assertIn(transfer['invocation_id'], json.dumps(status))
        self.assertNotIn(transfer['diagnosis'], json.dumps(status))
        self.assertNotIn(transfer['summary'], json.dumps(status))

    def test_manual_gate_denial_retains_uncommitted_recovery(self):
        transfer = self.fail_run(gates=['Required manual acceptance'])
        with Authority(self.project) as owner:
            with self.assertRaisesRegex(Blocked, 'manual gate not approved'):
                self.recover(owner, transfer, question=lambda _: 'no')
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        self.assertEqual(self.calls, ['old'] * 3)

    def test_checks_cannot_change_transferred_bytes(self):
        transfer = self.fail_run(checks=[['/bin/sh', '-c', 'echo drift > owned.txt']])
        with Authority(self.project) as owner:
            with self.assertRaisesRegex(Blocked, 'changed pre-transfer bytes'):
                self.recover(owner, transfer)
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_completed_commit_is_reconciled_after_missing_checkpoint_write(self):
        transfer = self.fail_run()
        with Authority(self.project) as owner:
            history = owner.store.history
            def fail_checkpoint(run, task, kind, state, *args, **kwargs):
                if kind == 'checkpoint' and state == 'passed':
                    raise Blocked('fixture result persistence unavailable')
                return history(run, task, kind, state, *args, **kwargs)
            with patch.object(owner.store, 'history', side_effect=fail_checkpoint):
                with self.assertRaisesRegex(Blocked, 'persistence unavailable'):
                    self.recover(owner, transfer)
            sha = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        with Authority(self.project) as owner:
            result = self.recover(owner, transfer)
            self.assertEqual(result['sha'], sha)
            self.assertEqual(owner.store.completed_checkpoints('run')['one']['sha'], sha)
        self.assertEqual(git(self.project, 'rev-list', '--count', self.base + '..HEAD').strip(), b'1')
        self.assertEqual(self.calls, ['old'] * 3)

    def test_failed_git_hook_does_not_complete_or_dispatch(self):
        transfer = self.fail_run()
        hook = self.project / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o755)
        with Authority(self.project) as owner:
            with self.assertRaises(Blocked):
                self.recover(owner, transfer)
            self.assertNotIn('one', owner.store.completed_checkpoints('run'))
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        self.assertEqual(self.calls, ['old'] * 3)

    def test_missing_task_projection_keeps_external_attribution(self):
        transfer = self.fail_run()
        with Authority(self.project) as owner:
            with patch.object(owner.store, 'task', side_effect=Blocked('fixture completion write interrupted')):
                with self.assertRaisesRegex(Blocked, 'completion write interrupted'):
                    self.recover(owner, transfer)
        with Authority(self.project) as owner:
            result = self.recover(owner, transfer)
            self.assertEqual(owner.store.completed_checkpoints('run')['one']['sha'], result['sha'])
            details = json.loads(owner.store.db.execute("SELECT details FROM execution_tasks WHERE task_id='one'").fetchone()['details'])
            self.assertIn(transfer['worker'], details['summary'])
        self.assertEqual(git(self.project, 'rev-list', '--count', self.base + '..HEAD').strip(), b'1')
