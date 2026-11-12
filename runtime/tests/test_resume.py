"""Synthetic same-run resume fixtures; no real workflow run is replayed."""
import base64
import contextlib
import io
import json
import os
import sqlite3
import subprocess
import sys
from unittest.mock import patch

from coherence_workflow import cli, engine
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.pi_adapter import PiAdapter, TaskOutcome, effective_saved_session
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}}

# CLI resume fixtures are detached local runs, not descendants of a host's active bridge.
_DETACHED_BRIDGE = {name: '' for name in (
    'COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
    'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}


class WorkerDispatchRegressionTests(ProjectTest):
    def test_missing_reservation_history_stops_production_resume_before_adapter(self):
        calls, identity = [], {'id': 'missing-history', 'file': '/private/missing.jsonl'}
        class Adapter:
            def __init__(self, *_args, **_kwargs): self.saved_session = identity
            def prompt(self, _prompt, **_kwargs):
                calls.append('provider')
                raise Blocked('inspected local transport failure')
        contract = {'tasks': [{'id': 'task', 'description': 'history fixture'}]}
        with Authority(self.project) as owner:
            with self.assertRaisesRegex(Blocked, 'local transport failure'):
                Engine(owner, 'missing-dispatch', contract, EXECUTOR, adapter=Adapter).invoke()
            original = [tuple(row) for row in owner.store.db.execute(
                "SELECT state,details FROM execution_history WHERE run_id='missing-dispatch' AND kind='worker_invocation'")]
            # Remove only fixture reservation data in this disposable test database.
            owner.store.db.execute("DELETE FROM execution_history WHERE run_id='missing-dispatch' AND kind='worker_dispatch'")
        with Authority(self.project) as owner:
            owner.store.resume('missing-dispatch')
            with self.assertRaisesRegex(Blocked, 'dispatch history is missing'):
                Engine(owner, 'missing-dispatch', contract, EXECUTOR, adapter=Adapter, resume=True,
                       question=lambda _prompt: 'inspected local failure; targeted transport correction').invoke()
            retained = [tuple(row) for row in owner.store.db.execute(
                "SELECT state,details FROM execution_history WHERE run_id='missing-dispatch' AND kind='worker_invocation'")]
        self.assertEqual(calls, ['provider'])
        self.assertEqual(retained, original)

    def test_fresh_binding_and_common_check_and_checkpoint_allowance_survive_reopen(self):
        for mode in ('check', 'checkpoint'):
            with self.subTest(mode=mode):
                project, calls = self.project, []
                identity = {'id': mode + '-fresh', 'file': '/private/' + mode + '.jsonl'}
                name, run = mode + '.txt', mode + '-allowance'
                class Adapter:
                    def __init__(self, *_args, **_kwargs): self.saved_session = None
                    def prompt(self, prompt, **kwargs):
                        self.saved_session = self.opened_session = identity
                        calls.append(prompt)
                        kwargs['claim'](name)
                        project.joinpath(name).write_text(str(len(calls)) + '\n')
                        return 'corrected fixture'
                contract = {'tasks': [{'id': 'task', 'description': 'allowance fixture', 'owned_paths': [name],
                    'checks': [['/bin/sh', '-c', 'cat ' + name + '; exit 1']] if mode == 'check' else []}]}
                failures = []
                def checkpoint_failure(_focused):
                    failures.append('checkpoint')
                    raise Blocked('correctable fixture checkpoint ' + str(len(failures)))
                head = git(project, 'rev-parse', 'HEAD')
                with Authority(project) as owner:
                    fault = patch.object(engine.FocusedGit, 'checkpoint', checkpoint_failure) if mode == 'checkpoint' else contextlib.nullcontext()
                    with fault, self.assertRaisesRegex(Blocked, 'allowance exhausted for task task session ' + identity['id']):
                        Engine(owner, run, contract, EXECUTOR, adapter=Adapter).invoke()
                    rows = [json.loads(row['details']) for row in owner.store.db.execute(
                        "SELECT details FROM execution_history WHERE run_id=? AND kind='worker_dispatch' AND state='reserved'", (run,))]
                    bound = [json.loads(row['details']) for row in owner.store.db.execute(
                        "SELECT details FROM execution_history WHERE run_id=? AND kind='worker_dispatch' AND state='bound'", (run,))]
                self.assertEqual(len(calls), 3)
                self.assertEqual([row['session'] for row in rows], [None, identity, identity])
                self.assertEqual([row['session'] for row in bound], [identity] * 3)
                self.assertEqual(project.joinpath(name).read_text(), '3\n')
                self.assertEqual(git(project, 'rev-parse', 'HEAD'), head)
                with Authority(project) as owner:
                    owner.store.resume(run)
                    with self.assertRaisesRegex(Blocked, 'allowance exhausted'):
                        Engine(owner, run, contract, EXECUTOR, adapter=Adapter, resume=True).invoke()
                self.assertEqual(len(calls), 3)
                self.assertEqual(project.joinpath(name).read_text(), '3\n')
                self.assertEqual(git(project, 'rev-parse', 'HEAD'), head)

    def test_production_explicit_identity_precedes_adapter_held_identity(self):
        explicit = {'id': 'explicit', 'file': '/private/explicit.jsonl'}
        held = {'id': 'held', 'file': '/private/held.jsonl'}
        calls = []
        class Adapter:
            def __init__(self, *_args, **_kwargs): self.saved_session = held
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture"],"coverage_gaps":[],"findings":[]}'
                calls.append(kwargs['saved_session'])
                self.saved_session = self.opened_session = effective_saved_session(kwargs['saved_session'], self.saved_session)
                return 'no-change'
        with Authority(self.project) as owner:
            runner = Engine(owner, 'explicit-dispatch', {'tasks': [{'id': 'task', 'description': 'identity fixture'}]},
                            EXECUTOR, adapter=Adapter)
            runner.session_candidates = [{'id': explicit['id'], 'saved_session': explicit}]
            with patch.object(engine, 'select_session', return_value={
                    'session_id': explicit['id'], 'reason': 'fixture selection', 'rejected': []}):
                self.assertEqual(runner.invoke()['status'], 'complete')
            reserved = json.loads(owner.store.db.execute(
                "SELECT details FROM execution_history WHERE run_id='explicit-dispatch' AND kind='worker_dispatch' AND state='reserved'").fetchone()['details'])
        self.assertEqual(calls, [explicit])
        self.assertEqual(reserved['session'], explicit)

    def test_distinct_reservations_not_duplicate_observations_consume_task_session_allowance(self):
        identity = {'id': 'shared-session', 'file': '/private/shared.jsonl'}
        other = {'id': 'other-session', 'file': '/private/other.jsonl'}
        with Authority(self.project) as owner:
            store = owner.store
            store.start('counts', self.base)
            for ordinal in range(3):
                invocation = 'call-' + str(ordinal)
                store.reserve_worker_dispatch('counts', 'task', invocation, identity)
                store.bind_worker_dispatch('counts', 'task', invocation, identity)
                store.history('counts', 'task', 'worker_dispatch', 'reserved', {'invocation_id': invocation, 'session': identity})
                for state in ('started', 'failed'):
                    store.history('counts', 'task', 'worker_invocation', state, {'invocation_id': invocation, 'saved_session': identity})
        with Authority(self.project) as owner:
            store = owner.store
            with self.assertRaisesRegex(Blocked, 'allowance exhausted'):
                store.reserve_worker_dispatch('counts', 'task', 'fourth', identity)
            store.reserve_worker_dispatch('counts', 'another-task', 'another-task-initial', identity)
            with self.assertRaisesRegex(Blocked, 'invocation history is missing or uncertain'):
                store.reserve_worker_dispatch('counts', 'another-task', 'unsettled-call', identity)
            store.reserve_worker_dispatch('counts', 'task', 'other-session-initial', other)
            store.reserve_worker_dispatch('counts', 'fresh-task', 'unbound-initial', None)
            with self.assertRaisesRegex(Blocked, 'unbound fresh session'):
                store.reserve_worker_dispatch('counts', 'fresh-task', 'unknown-continuation', identity)


class SameRunResumeTests(ProjectTest):
    def test_dispatch_reservation_reconciles_after_write_fault_before_single_provider_call(self):
        calls, identity = [], {'id': 'reservation-session', 'file': '/private/reservation.jsonl'}
        class Adapter:
            def __init__(self, *_args, **_kwargs): self.saved_session = identity
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture"],"coverage_gaps":[],"findings":[]}'
                calls.append('provider')
                return 'no-change dispatch'
        with Authority(self.project) as owner:
            original, faulted = owner.store._history_insert, [False]
            def interrupted_write(*args):
                original(*args)
                if args[3:5] == ('worker_dispatch', 'reserved') and not faulted[0]:
                    faulted[0] = True
                    raise sqlite3.OperationalError('after-write fixture fault')
            with patch.object(owner.store, '_history_insert', side_effect=interrupted_write):
                result = Engine(owner, 'reservation-fault', {'tasks': [{'id': 'one', 'description': 'direct dispatch'}]},
                                EXECUTOR, adapter=Adapter).invoke()
            reservations = owner.store.db.execute(
                "SELECT details FROM execution_history WHERE run_id='reservation-fault' AND kind='worker_dispatch' "
                "AND state='reserved'").fetchall()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(calls, ['provider'])
        self.assertEqual(len(reservations), 1)

    def test_checkpoint_history_survives_interruption_before_task_completion(self):
        project = self.project
        contract = {'tasks': [{'id': 'tiny', 'description': 'tiny disposable edit', 'owned_paths': ['tiny.txt']}]}
        class Adapter:
            workers = 0
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'): return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                Adapter.workers += 1
                kwargs['claim']('tiny.txt')
                (project/'tiny.txt').write_text('done')
                return 'done'
        with Authority(project) as owner:
            original_task = owner.store.task
            def interrupted(*args, **kwargs):
                if args[2] == 'complete': raise KeyboardInterrupt
                return original_task(*args, **kwargs)
            with patch.object(owner.store, 'task', side_effect=interrupted), self.assertRaises(KeyboardInterrupt):
                Engine(owner, 'lost-completion', contract, EXECUTOR, adapter=Adapter).invoke()
            checkpoint = git(project, 'rev-parse', 'HEAD').decode().strip()
            self.assertNotEqual(checkpoint, self.base)
            owner.store.resume('lost-completion')
            result = Engine(owner, 'lost-completion', contract, EXECUTOR, adapter=Adapter, resume=True).invoke()
            self.assertEqual(Adapter.workers, 1)
            self.assertEqual(result['checkpoints'][0]['sha'], checkpoint)
            self.assertEqual(result['sha'], checkpoint)
            self.assertEqual(owner.store.db.execute("SELECT state,result FROM execution_tasks WHERE run_id='lost-completion'").fetchone()[:], ('complete', checkpoint))


    def test_structured_coordinator_continuation_authorizes_edit_only_and_restores_private_claim(self):
        project = self.project
        project.joinpath('owned.txt').write_bytes(b'base\ninherited-private\n')
        identity = {'id': 'edit-only-session', 'file': '/private/edit-only.jsonl'}
        contract = {'tasks': [{'id': 'task', 'description': 'fixture', 'owned_paths': ['owned.txt', 'clean.txt']}]}
        class Adapter:
            calls = 0
            def __init__(self, *_args, **_kwargs): self.saved_session = identity
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture"],"coverage_gaps":[],"findings":[]}'
                Adapter.calls += 1
                if Adapter.calls == 1:
                    kwargs['claim']('clean.txt')
                    project.joinpath('clean.txt').write_text('clean task\n')
                    kwargs['claim']('owned.txt')
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_bytes(b'task\ninherited-private\n')
                return 'done'
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'pre-existing dirty'):
                Engine(owner, 'edit-only', contract, EXECUTOR, adapter=Adapter).invoke()
            owner.store.resume('edit-only')
            result = Engine(owner, 'edit-only', contract, EXECUTOR, adapter=Adapter, resume=True,
                            question=lambda _: json.dumps({'diagnosis': 'inspected dirty claim; use authorized edit only',
                                                          'edit_only_paths': ['owned.txt']})).invoke()
            facts = owner.store.task_facts('edit-only', 'task')
            self.assertEqual(set(facts['paths']), {'owned.txt', 'clean.txt'})
            self.assertEqual(facts['edit_only']['owned.txt']['start'], 'YmFzZQppbmhlcml0ZWQtcHJpdmF0ZQo=')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(git(project, 'show', 'HEAD:owned.txt'), b'task\n')
        self.assertEqual(project.joinpath('owned.txt').read_bytes(), b'task\ninherited-private\n')
        status = cli.status(project, 'edit-only')
        self.assertNotIn('YmFzZQppbmhlcml0ZWQtcHJpdmF0ZQo=', json.dumps(status))
        self.assertNotIn('inherited-private', json.dumps(status))

    def test_edit_only_interrupted_worker_resumes_original_baseline_and_clean_claim(self):
        project = self.project
        project.joinpath('owned.txt').write_bytes(b'base\ninherited\n')
        identity = {'id': 'edit-only-interrupted', 'file': '/private/edit-only-interrupted.jsonl'}
        contract = {'tasks': [{'id': 'task', 'description': 'fixture', 'owned_paths': ['owned.txt', 'clean.txt']}]}
        class Adapter:
            calls = 0
            def __init__(self, *_args, **_kwargs): self.saved_session = identity
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture"],"coverage_gaps":[],"findings":[]}'
                Adapter.calls += 1
                if Adapter.calls == 1:
                    kwargs['claim']('clean.txt')
                    project.joinpath('clean.txt').write_text('clean task\n')
                    kwargs['claim']('owned.txt')
                kwargs['claim']('owned.txt')
                if Adapter.calls == 2:
                    project.joinpath('owned.txt').write_bytes(b'task\ninherited\n')
                    raise KeyboardInterrupt
                return 'resume existing edits'
        with Authority(project) as owner:
            with self.assertRaises(Blocked):
                Engine(owner, 'edit-interrupt', contract, EXECUTOR, adapter=Adapter).invoke()
            owner.store.resume('edit-interrupt')
            with self.assertRaises(KeyboardInterrupt):
                Engine(owner, 'edit-interrupt', contract, EXECUTOR, adapter=Adapter, resume=True,
                       question=lambda _: json.dumps({'diagnosis': 'scoped edit', 'edit_only_paths': ['owned.txt']})).invoke()
            saved = owner.store.task_facts('edit-interrupt', 'task')
        with Authority(project) as owner:
            owner.store.resume('edit-interrupt')
            self.assertEqual(saved, owner.store.task_facts('edit-interrupt', 'task'))
            result = Engine(owner, 'edit-interrupt', contract, EXECUTOR, adapter=Adapter, resume=True).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(git(project, 'show', 'HEAD:owned.txt'), b'task\n')
        self.assertEqual(git(project, 'show', 'HEAD:clean.txt'), b'clean task\n')
        self.assertEqual(project.joinpath('owned.txt').read_bytes(), b'task\ninherited\n')

    def test_unresolved_edit_only_checkpoint_stops_resume_before_worker(self):
        calls = []
        class Adapter:
            def __init__(self, *_args, **_kwargs):
                self.saved_session = {'id': 'pending', 'file': '/private/pending.jsonl'}
            def prompt(self, _prompt, **_kwargs):
                calls.append('worker')
                raise Blocked('fixture failure')
        contract = {'tasks': [{'id': 'task', 'description': 'fixture'}]}
        with Authority(self.project) as owner:
            with self.assertRaisesRegex(Blocked, 'fixture failure'):
                Engine(owner, 'pending-edit', contract, EXECUTOR, adapter=Adapter).invoke()
            owner.store.history('pending-edit', 'task', 'edit_only_checkpoint', 'started',
                                {'parent': self.base, 'tree': 'fixture-tree', 'paths': ['owned.txt']})
            owner.store.resume('pending-edit')
            with self.assertRaisesRegex(Blocked, 'unfinished edit-only checkpoint.*inspect retained parent/tree'):
                Engine(owner, 'pending-edit', contract, EXECUTOR, adapter=Adapter, resume=True).invoke()
        self.assertEqual(calls, ['worker'])
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_assigned_fixer_resumes_edit_only_from_original_task_authority(self):
        self._assigned_fixer_edit_only(fail_before_doc=False)

    def test_assigned_fixer_first_claims_edit_only_after_failed_partial_repair(self):
        self._assigned_fixer_edit_only(fail_before_doc=True)

    def _assigned_fixer_edit_only(self, *, fail_before_doc):
        project = self.project
        self.write('owned.txt', 'first\nsecond\nend\n')
        git(project, 'add', '--', 'owned.txt')
        git(project, 'commit', '-qm', 'fixture baseline')
        self.write('owned.txt', 'first\nsecond\nend\ninherited-private\n')
        self.write('other.txt', 'unrelated staged\n')
        git(project, 'add', '--', 'other.txt')
        staged = git(project, 'show', ':other.txt')
        contract = {'tasks': [{'id': 'task', 'description': 'fixture',
                               'owned_paths': ['owned.txt', 'clean.txt', 'other.txt']}]}
        identity = {'id': 'fix-edit-only', 'file': '/private/fix-edit-only.jsonl'}
        calls = {'task': 0, 'review': 0, 'fix': 0}
        class Adapter:
            def __init__(self, *_args, **_kwargs): self.saved_session = identity
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    calls['review'] += 1
                    if calls['review'] == 1:
                        return '{"approved":false,"coverage":["fixture"],"coverage_gaps":[],"findings":["owned.txt:2 - repair required"]}'
                    return '{"approved":true,"coverage":["fixture"],"coverage_gaps":[],"findings":[]}'
                if 'Actionable findings:' in prompt:
                    calls['fix'] += 1
                    with self_test.assertRaisesRegex(Blocked, 'pre-existing dirty'):
                        kwargs['claim']('other.txt')
                    kwargs['claim']('clean.txt')
                    if calls['fix'] == 1:
                        project.joinpath('clean.txt').write_text('partial clean\n')
                        if fail_before_doc:
                            return TaskOutcome('failed', 'fixture needs final correction')
                    kwargs['claim']('owned.txt')
                    if calls['fix'] == 1 or fail_before_doc:
                        row = owner.store.db.execute("SELECT details FROM execution_history WHERE kind='fixer_mutation' AND state='claimed' ORDER BY seq DESC LIMIT 1").fetchone()
                        claim = json.loads(row['details'])['edit_only']['owned.txt']
                        self_test.assertEqual(base64.b64decode(claim['start']), project.joinpath('owned.txt').read_bytes())
                        if calls['fix'] == 1:
                            project.joinpath('owned.txt').write_text('task first\nrepair partial\nend\ninherited-private\n')
                            return TaskOutcome('failed', 'fixture needs final correction')
                    project.joinpath('owned.txt').write_text('task first\nrepair complete\nend\ninherited-private\n')
                    return 'repair complete'
                calls['task'] += 1
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('task first\nsecond\nend\ninherited-private\n')
                return 'task complete'
        self_test = self
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'pre-existing dirty'):
                Engine(owner, 'fix-edit', contract, EXECUTOR, adapter=Adapter).invoke()
            owner.store.resume('fix-edit')
            with self.assertRaisesRegex(Blocked, 'fixture needs final correction'):
                Engine(owner, 'fix-edit', contract, EXECUTOR, adapter=Adapter, resume=True,
                       question=lambda _: json.dumps({'diagnosis': 'scoped edit', 'edit_only_paths': ['owned.txt']})).invoke()
            first_commit = git(project, 'rev-parse', 'HEAD').decode().strip()
            self.assertEqual(git(project, 'show', first_commit + ':owned.txt'), b'task first\nsecond\nend\n')
            row = owner.store.db.execute("SELECT details FROM execution_history WHERE kind='fixer_invocation' AND state='failed' ORDER BY seq DESC LIMIT 1").fetchone()
            saved = json.loads(row['details'])['edit_only'].get('owned.txt')
            if fail_before_doc:
                self.assertIsNone(saved)
            else:
                self.assertEqual(base64.b64decode(saved['start']), b'task first\nsecond\nend\ninherited-private\n')
        with Authority(project) as owner:
            owner.store.resume('fix-edit')
            result = Engine(owner, 'fix-edit', contract, EXECUTOR, adapter=Adapter, resume=True).invoke()
            rows = owner.store.db.execute("SELECT details FROM execution_history WHERE kind='fixer_mutation' AND state='claimed' ORDER BY seq").fetchall()
            facts = [json.loads(row['details']) for row in rows]
            found = [fact['edit_only']['owned.txt'] for fact in facts if 'owned.txt' in fact.get('edit_only', {})]
            self.assertTrue(found)
            if saved is not None:
                self.assertTrue(all(fact == saved for fact in found))
            saved = found[0]
            self.assertEqual(base64.b64decode(saved['start']), b'task first\nsecond\nend\ninherited-private\n')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(calls, {'task': 2, 'review': 2, 'fix': 2})
        self.assertEqual(git(project, 'show', 'HEAD:owned.txt'), b'task first\nrepair complete\nend\n')
        self.assertEqual(git(project, 'show', 'HEAD:clean.txt'), b'partial clean\n')
        self.assertEqual(project.joinpath('owned.txt').read_bytes(), b'task first\nrepair complete\nend\ninherited-private\n')
        self.assertEqual(git(project, 'show', ':other.txt'), staged)
        self.assertNotIn(saved['start'], json.dumps(cli.status(project, 'fix-edit')))

    def test_unresolved_edit_only_fixer_checkpoint_stops_recovery(self):
        contract = {'tasks': [{'id': 'task', 'description': 'fixture'}]}
        with Authority(self.project) as owner:
            store = owner.store
            store.start('pending-fix', self.base, contract=contract, executor=EXECUTOR,
                        authority={'review_policy': 'owner-pair-v1'}, review_base=self.base)
            store.review_dispatch('pending-fix', 'review', review_base=self.base, review_head=self.base)
            store.review_outcome('pending-fix', 'review', 'rejected', findings=['owned.txt:1 - fixture'],
                                 references={'base': self.base, 'head': self.base})
            store.review_dispatch('pending-fix', 'fix', role='fixer', review_ordinal=1, fixing_round=1,
                                  trigger_execution_id='review', predecessor_execution_id='review',
                                  review_base=self.base, review_head=self.base)
            store.history('pending-fix', None, 'fixer_edit_only_checkpoint', 'started',
                          {'execution_id': 'fix', 'parent': self.base, 'tree': 'fixture', 'paths': ['owned.txt']})
            item = next(item for item in store.review_chain('pending-fix', private=True)['executions']
                        if item['execution_id'] == 'fix')
            runner = Engine(owner, 'pending-fix', contract, EXECUTOR, resume=True)
            with self.assertRaisesRegex(Blocked, 'unfinished edit-only repair checkpoint'):
                runner._recover_assigned_fix(item, self.base)
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_resume_checkpoints_already_edited_established_handoff_without_second_edit(self):
        project = self.project
        project.joinpath('recovery.txt').write_bytes(b'preserved recovery bytes\n')
        contract = admit({'paid_scope': {'approved': True, 'agent_providers': ['fixture'], 'apis': []}, 'tasks': [{
            'id': 'handoff', 'description': 'resume an exact recovery handoff',
            'owned_paths': ['recovery.txt'], 'handoff_paths': ['recovery.txt'],
        }]})

        identity = {'id': 'handoff-session', 'file': '/private/handoff.jsonl'}
        class Interrupted:
            def __init__(self, *_args, **_kwargs): self.saved_session = identity
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                kwargs['claim']('recovery.txt')
                project.joinpath('recovery.txt').write_bytes(b'preserved recovery bytes\nintended correction\n')
                raise KeyboardInterrupt

        with Authority(project) as owner:
            with self.assertRaises(KeyboardInterrupt):
                Engine(owner, 'handoff-resume', contract, EXECUTOR, adapter=Interrupted,
                       paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            owner.store.resume('handoff-resume')

            class Continued:
                calls = 0
                def __init__(self, *_args, **_kwargs): self.saved_session = identity
                def prompt(self, _prompt, **kwargs):
                    if kwargs.get('read_only'):
                        return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                    Continued.calls += 1
                    kwargs['claim']('recovery.txt')
                    return 'checkpoint the already intended handoff edit'

            result = Engine(owner, 'handoff-resume', contract, EXECUTOR, adapter=Continued,
                            paid_scope={'agent_providers': ['fixture'], 'apis': []}, resume=True).invoke()
        self.assertEqual(Continued.calls, 1)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['checkpoints'][0]['paths'], ['recovery.txt'])
        self.assertEqual(git(project, 'show', 'HEAD:recovery.txt'),
                         b'preserved recovery bytes\nintended correction\n')


    def test_review_repair_reopens_persisted_reviewer_after_process_restart(self):
        self._settled_fixer_restart()

    def test_settled_fixer_returned_correction_resumes_checks_without_provider_replay(self):
        self._settled_fixer_restart(interrupt='fixer_checks')

    def test_settled_fixer_checkpoint_resumes_without_provider_or_commit_replay(self):
        self._settled_fixer_restart(interrupt='fixer_checkpoint')

    def test_settled_fixer_check_failure_then_returned_correction_ignores_old_stage(self):
        self._settled_fixer_restart(interrupt='fixer_invocation', prior_stage='check')

    def test_settled_fixer_checkpoint_failure_then_returned_correction_ignores_old_stage(self):
        self._settled_fixer_restart(interrupt='fixer_invocation', prior_stage='checkpoint')

    def test_settled_fixer_source_drift_preserves_unknown_bytes_without_dispatch(self):
        self._settled_fixer_restart(drift='bytes')

    def test_settled_fixer_index_drift_preserves_staged_and_working_bytes_without_dispatch(self):
        self._settled_fixer_restart(index_drift=True)

    def test_settled_fixer_filter_equivalent_bytes_stop_before_dispatch(self):
        self._settled_fixer_restart(drift='crlf')

    def test_settled_fixer_mode_drift_stops_before_dispatch(self):
        self._settled_fixer_restart(drift='mode')

    def test_settled_fixer_head_drift_stops_before_dispatch(self):
        self._settled_fixer_restart(drift='head')

    def test_settled_fixer_returned_mode_drift_stops_before_ownership_restore(self):
        self._settled_fixer_restart(interrupt='fixer_invocation', returned_drift='mode')

    def test_settled_fixer_returned_filter_equivalent_drift_stops_before_ownership_restore(self):
        self._settled_fixer_restart(interrupt='fixer_invocation', returned_drift='crlf')

    def test_settled_fixer_checked_mode_drift_stops_before_ownership_restore(self):
        self._settled_fixer_restart(interrupt='fixer_checks', returned_drift='mode')

    def test_settled_fixer_checked_filter_equivalent_drift_stops_before_ownership_restore(self):
        self._settled_fixer_restart(interrupt='fixer_checks', returned_drift='crlf')

    def _settled_fixer_restart(self, *, interrupt=None, drift=None, prior_stage=None, returned_drift=None, index_drift=False):
        """Actual adapter restart seam; scripted output proves mechanics, not judgment."""
        host, state = self.root / 'repair_resume_host.py', self.root / 'repair_resume_state.json'
        state.write_text('{}')
        failed_phase = 2 if prior_stage else 1
        if prior_stage == 'checkpoint':
            hook = self.project / '.git/hooks/pre-commit'
            hook.write_text('#!/bin/sh\ntest "$(git show :owned.txt)" != broken\n')
            hook.chmod(0o755)
        if drift == 'crlf' or returned_drift == 'crlf':
            git(self.project, 'config', 'core.autocrlf', 'true')
        host.write_text("""import json
from pathlib import Path
request = json.loads(input())
state_path = Path(STATE)
state = json.loads(state_path.read_text())
prompt = request['prompt']
def count(name):
    state[name] = state.get(name, 0) + 1
    state_path.write_text(json.dumps(state))
    return state[name]
def result(text, outcome='completed', session=None):
    payload = {'type': 'result', 'text': text, 'outcome': outcome}
    if session: payload['session'] = session
    print(json.dumps(payload), flush=True)
saved = {'id': 'warm-review', 'file': '/private/review.jsonl', 'compatibility': {'readOnly': True}}
if 'Independently review' in prompt:
    if count('review') == 1:
        result('{"approved":false,"coverage":["fixture examined"],"coverage_gaps":[],"findings":["owned.txt:1 - fixture defect [basis: correctness]"]}', session=saved)
    else:
        result('{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}', session=saved)
elif any(marker in prompt for marker in ('Actionable findings:', 'Actual failed attempt:', 'Actual checkpoint error:')):
    phase = count('fix')
    assert request.get('savedSession', {}).get('id') == 'warm-review'
    if phase == FAILED_PHASE + 1:
        assert 'BENIGN-FIXER-REASON: inspect then repair' in prompt
        assert 'retained head and selected source/artifact bytes still match Git' in prompt
        assert 'never repeat the previous attempt unchanged' in prompt
        assert 'partial' in prompt
        assert 'Current execution authority:' in prompt
        assert 'Routine authority:' in prompt
        assert 'Required/manual acceptance is not waived' in prompt
    print(json.dumps({'type': 'claim', 'path': 'owned.txt'}), flush=True)
    assert json.loads(input()) == {'ok': True}
    Path(request['project'], 'owned.txt').write_text(
        'partial\\n' if phase == FAILED_PHASE else ('broken\\n' if phase < FAILED_PHASE else 'repaired\\n'))
    result('BENIGN-FIXER-REASON: inspect then repair' if phase == FAILED_PHASE else 'repair complete',
           'failed' if phase == FAILED_PHASE else 'completed', saved)
else:
    print(json.dumps({'type': 'claim', 'path': 'owned.txt'}), flush=True)
    assert json.loads(input()) == {'ok': True}
    Path(request['project'], 'owned.txt').write_text('initial\\n')
    result('task complete')
""".replace("STATE", repr(str(state))).replace('FAILED_PHASE', str(failed_phase)))
        check_source = "from pathlib import Path; assert Path('owned.txt').exists()"
        if prior_stage == 'check':
            check_source += "; assert Path('owned.txt').read_text() != 'broken\\n'"
        contract = admit([{'id': 'task', 'description': 'fixture', 'owned_paths': ['owned.txt'],
                          'check': [sys.executable, '-B', '-c', check_source]}])
        environment = {'COHERENCE_NODE': sys.executable, **_DETACHED_BRIDGE}
        with patch('coherence_workflow.pi_adapter.host_path', return_value=host), patch.dict(os.environ, environment):
            with Authority(self.project) as owner:
                with self.assertRaisesRegex(Blocked, 'BENIGN-FIXER-REASON'):
                    Engine(owner, 'review-restart', contract, EXECUTOR, adapter=PiAdapter).invoke()
            # A new Authority and Engine have no in-memory adapter; the persisted reviewer
            # session, failed-call diagnosis, and claimed path are the consumed resume facts.
            owned = self.project.joinpath('owned.txt')
            normalized_before = git(self.project, 'hash-object', '--path=owned.txt', '--', 'owned.txt')
            if drift == 'crlf':
                owned.write_bytes(b'partial\r\n')
                self.assertEqual(git(self.project, 'hash-object', '--path=owned.txt', '--', 'owned.txt'), normalized_before)
            elif drift == 'mode':
                owned.chmod(owned.stat().st_mode ^ 0o100)
                self.assertEqual(git(self.project, 'hash-object', '--path=owned.txt', '--', 'owned.txt'), normalized_before)
            elif drift == 'bytes':
                owned.write_text('unknown incoming bytes\n')
            elif drift == 'head':
                self.project.joinpath('other.txt').write_text('incoming commit\n')
                git(self.project, 'add', '--', 'other.txt')
                git(self.project, 'commit', '-qm', 'incoming unrelated work')
            if index_drift:
                owned.write_text('UNRELATED-STAGED-CONTENT\n')
                git(self.project, 'add', '--', 'owned.txt')
                staged_before = git(self.project, 'ls-files', '--stage', '--', 'owned.txt')
                owned.write_text('partial\n')
            before_resume = git(self.project, 'rev-parse', 'HEAD')
            before_bytes, before_mode = owned.read_bytes(), owned.stat().st_mode
            with Authority(self.project) as owner:
                owner.store.resume('review-restart')
                # No bridge or injected diagnosis: standalone/noninteractive resume must
                # not route routine diagnosis to terminal owner input.
                if drift or index_drift:
                    with self.assertRaisesRegex(Blocked, 'target/source bytes drifted' if drift else 'index entries drifted'):
                        Engine(owner, 'review-restart', contract, EXECUTOR, adapter=PiAdapter, resume=True).invoke()
                    self.assertEqual(json.loads(state.read_text()), {'review': 1, 'fix': 1})
                    self.assertEqual(git(self.project, 'rev-parse', 'HEAD'), before_resume)
                    self.assertEqual(owned.read_bytes(), before_bytes)
                    self.assertEqual(owned.stat().st_mode, before_mode)
                    if index_drift:
                        self.assertEqual(git(self.project, 'ls-files', '--stage', '--', 'owned.txt'), staged_before)
                        self.assertEqual(git(self.project, 'show', ':owned.txt'), b'UNRELATED-STAGED-CONTENT\n')
                    return
                original_history = owner.store.history
                def interrupted_history(run, task, kind, status, details):
                    original_history(run, task, kind, status, details)
                    if kind == interrupt and status == ('returned' if interrupt == 'fixer_invocation' else 'passed'):
                        raise KeyboardInterrupt
                if interrupt:
                    with patch.object(owner.store, 'history', side_effect=interrupted_history), self.assertRaises(KeyboardInterrupt):
                        Engine(owner, 'review-restart', contract, EXECUTOR, adapter=PiAdapter, resume=True).invoke()
                    settled_head = git(self.project, 'rev-parse', 'HEAD')
                    self.assertEqual(json.loads(state.read_text()), {'review': 1, 'fix': failed_phase + 1})
                else:
                    result = Engine(owner, 'review-restart', contract, EXECUTOR, adapter=PiAdapter, resume=True).invoke()
            if interrupt:
                # Reopen after the successful corrective provider return. Retained old
                # failure history must not win stage selection over that return.
                if returned_drift:
                    normalized = git(self.project, 'hash-object', '--path=owned.txt', '--', 'owned.txt')
                    if returned_drift == 'mode':
                        owned.chmod(owned.stat().st_mode ^ 0o100)
                    else:
                        owned.write_bytes(b'repaired\r\n')
                    self.assertEqual(git(self.project, 'hash-object', '--path=owned.txt', '--', 'owned.txt'), normalized)
                    incoming_bytes, incoming_mode = owned.read_bytes(), owned.stat().st_mode
                with Authority(self.project) as owner:
                    owner.store.resume('review-restart')
                    if returned_drift:
                        before_history = owner.store.db.execute('SELECT COUNT(*) FROM execution_history').fetchone()[0]
                        with self.assertRaisesRegex(Blocked, 'source bytes drifted or file modes changed'):
                            Engine(owner, 'review-restart', contract, EXECUTOR, adapter=PiAdapter, resume=True).invoke()
                        self.assertEqual(json.loads(state.read_text()), {'review': 1, 'fix': failed_phase + 1})
                        self.assertEqual(git(self.project, 'rev-parse', 'HEAD'), settled_head)
                        self.assertEqual(owned.read_bytes(), incoming_bytes)
                        self.assertEqual(owned.stat().st_mode, incoming_mode)
                        new_stages = owner.store.db.execute(
                            "SELECT kind FROM execution_history ORDER BY seq LIMIT -1 OFFSET ?", (before_history,)).fetchall()
                        self.assertFalse(any(row['kind'] in ('fixer_checks', 'fixer_checkpoint', 'fixer_invocation')
                                             for row in new_stages))
                        return
                    result = Engine(owner, 'review-restart', contract, EXECUTOR, adapter=PiAdapter, resume=True).invoke()
                    if interrupt == 'fixer_checkpoint':
                        self.assertEqual(git(self.project, 'rev-parse', 'HEAD'), settled_head)
            with Authority(self.project) as owner:
                history = [dict(row) for row in owner.store.db.execute(
                    "SELECT kind,state,details FROM execution_history WHERE run_id='review-restart' ORDER BY seq")]
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(json.loads(state.read_text()), {'review': 2, 'fix': failed_phase + 1})
        failure = next(json.loads(row['details']) for row in history
                       if row['kind'] == 'fixer_invocation' and row['state'] == 'failed')
        self.assertEqual(failure['paths'], ['owned.txt'])
        self.assertIn('owned.txt', failure['source_state'])
        self.assertEqual(set(failure['source_state']['owned.txt']), {'sha256', 'mode'})
        self.assertEqual(len(failure['index_state']['owned.txt']), 1)
        self.assertTrue(failure['head'])
        latest_return = max(index for index, row in enumerate(history)
                            if row['kind'] == 'fixer_invocation' and row['state'] == 'returned')
        local_history = history[latest_return + 1:]
        check_pass = next(index for index, row in enumerate(local_history)
                          if row['kind'] == 'fixer_checks' and row['state'] == 'passed')
        checkpoint_pass = next(index for index, row in enumerate(local_history)
                               if row['kind'] == 'fixer_checkpoint' and row['state'] == 'passed')
        self.assertLess(check_pass, checkpoint_pass)
        self.assertEqual([row['state'] for row in history if row['kind'] == 'fixer_invocation' and row['state'] != 'started'],
                         (['returned'] if prior_stage else []) + ['failed', 'returned'])
        if prior_stage == 'check':
            failed_check = next(json.loads(row['details']) for row in history
                                if row['kind'] == 'fixer_check' and row['state'] == 'failed')
            self.assertNotEqual(failed_check['exit_code'], 0)
        elif prior_stage == 'checkpoint':
            self.assertTrue(any(row['kind'] == 'fixer_checkpoint' and row['state'] == 'failed' for row in history))
        self.assertEqual(git(self.project, 'rev-list', '--count', self.base + '..HEAD'), b'2\n')

    def test_persisted_approval_never_accepts_incoming_commits(self):
        for ordinal in (1, 2):
            with self.subTest(ordinal=ordinal), Authority(self.project) as owner:
                run = 'approved-' + str(ordinal)
                reviewed = git(self.project, 'rev-parse', 'HEAD').decode().strip()
                contract = {'tasks': []}
                store = owner.store
                store.start(run, reviewed, contract=contract, executor=EXECUTOR,
                            authority={}, review_base=self.base)
                store.review_dispatch(run, 'r1', review_base=self.base, review_head=reviewed)
                store.review_outcome(run, 'r1', 'approved' if ordinal == 1 else 'rejected',
                    findings=[] if ordinal == 1 else ['work.txt:1 - defect'],
                    references={'base': self.base, 'head': reviewed})
                if ordinal == 2:
                    store.review_dispatch(run, 'fix', role='fixer', fixing_round=1,
                        trigger_execution_id='r1', predecessor_execution_id='r1',
                        review_base=self.base, review_head=reviewed)
                    store.review_outcome(run, 'fix', 'approved', findings=[], references={'head': reviewed})
                    store.review_dispatch(run, 'r2', review_ordinal=2, fixing_round=1,
                        trigger_execution_id='fix', predecessor_execution_id='fix',
                        review_base=self.base, review_head=reviewed)
                    store.review_outcome(run, 'r2', 'approved', findings=[], references={'head': reviewed})
                store.finish(run, 'interrupted', reviewed, 'after review outcome')
                (self.project/'incoming.txt').write_text(str(ordinal))
                git(self.project, 'add', '--', 'incoming.txt')
                git(self.project, 'commit', '-m', 'unreviewed incoming')
                store.resume(run)
                def forbidden(*args, **kwargs):
                    self.fail('persisted approval must not launch another session')
                result = Engine(owner, run, contract, EXECUTOR, resume=True, adapter=forbidden).invoke()
                self.assertEqual(result['sha'], reviewed)
                self.assertNotEqual(result['sha'], git(self.project, 'rev-parse', 'HEAD').decode().strip())
                self.assertEqual(store.db.execute('SELECT result FROM execution_runs WHERE run_id=?', (run,)).fetchone()[0], reviewed)

    def test_cli_resume_skips_recovered_checkpoint_and_retains_original_range(self):
        project, initial_calls, resumed_calls = self.project, [], []
        contract = admit({'paid_scope': {'approved': True, 'agent_providers': ['fixture'], 'apis': []}, 'tasks': [
            {'id': 'first', 'description': 'synthetic first', 'owned_paths': ['one.txt']},
            {'id': 'second', 'description': 'synthetic second', 'owned_paths': ['two.txt']},
        ]})

        identity = {'id': 'cli-resume-session', 'file': '/private/cli-resume.jsonl'}
        class Interrupted:
            def __init__(self, *_args, **_kwargs): self.saved_session = identity
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                initial_calls.append('worker')
                if len(initial_calls) == 2:
                    raise KeyboardInterrupt
                kwargs['claim']('one.txt')
                project.joinpath('one.txt').write_text('one\n')
                return 'first'

        with Authority(project) as owner:
            with self.assertRaises(KeyboardInterrupt):
                Engine(owner, 'resume-run', contract, EXECUTOR, adapter=Interrupted,
                       paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
        original_head = self.base
        tasks = self.root / 'ignored-tasks.json'
        executor = self.root / 'ignored-executor.json'
        tasks.write_text('[]')
        executor.write_text(json.dumps(EXECUTOR))

        class Resumed:
            def __init__(self, *_args, **_kwargs): self.saved_session = identity
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    resumed_calls.append('review')
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                resumed_calls.append('worker')
                kwargs['claim']('two.txt')
                project.joinpath('two.txt').write_text('two\n')
                return 'second'

        output = io.StringIO()
        with patch.dict(os.environ, _DETACHED_BRIDGE), patch.object(cli, 'PiAdapter', Resumed), contextlib.redirect_stdout(output):
            self.assertEqual(cli.main(['resume', '--project', str(project), '--run', 'resume-run']), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(initial_calls, ['worker', 'worker'])
        self.assertEqual(resumed_calls, ['worker', 'review'])
        self.assertEqual(len(result['checkpoints']), 2)
        self.assertEqual(project.joinpath('one.txt').read_text(), 'one\n')
        self.assertEqual(project.joinpath('two.txt').read_text(), 'two\n')
        self.assertEqual(result['baseline'], original_head)
        with Authority(project) as owner:
            history = [dict(row) for row in owner.store.db.execute(
                "SELECT kind,state,details FROM execution_history WHERE run_id='resume-run' ORDER BY seq")]
        self.assertTrue(any(row['kind'] == 'invocation' and row['state'] == 'resumed' for row in history))

    def test_resume_reassesses_same_head_evidence_gap_without_fixer_or_task_replay(self):
        contract = {'tasks': [{'id': 'done', 'description': 'synthetic'}]}
        calls = []
        with Authority(self.project) as owner:
            store = owner.store
            store.start('evidence-resume', self.base, contract=contract, executor=EXECUTOR,
                        authority={'paid_scope': {'agent_providers': ['fixture'], 'apis': []},
                                   'review_policy': 'owner-pair-v1'}, review_base=self.base)
            store.task('evidence-resume', 'done', 'complete', self.base, self.base)
            store.history('evidence-resume', 'done', 'checkpoint', 'passed',
                          {'sha': self.base, 'paths': [], 'artifacts': [], 'no_change': True})
            store.review_dispatch('evidence-resume', 'review-gap', review_base=self.base, review_head=self.base)
            store.review_outcome('evidence-resume', 'review-gap', 'rejected', findings=[], references={
                'base': self.base, 'head': self.base,
                'review_summary': {'coverage': ['source inspected'], 'coverage_gaps': ['required check evidence needs review']},
                'check_evidence_digest': 'old-evidence'})
            store.finish('evidence-resume', 'failed', self.base, 'coverage evidence pending')
        self.assertEqual(cli.status(self.project, 'evidence-resume')['review_authorization']['next_stage'],
                         'coordinator_evidence_reassessment')

        class Reviewer:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                self_test.assertTrue(kwargs['read_only'])
                calls.append(prompt)
                self_test.assertIn('Evidence reassessment:', prompt)
                self_test.assertIn('diagnosis ties retained check evidence to the outstanding gap', prompt)
                return '{"approved":true,"coverage":["source inspected","required check evidence evaluated"],"coverage_gaps":[],"findings":[]}'

        self_test = self
        with Authority(self.project) as owner:
            saved = owner.store.resume('evidence-resume')['input']
            result = Engine(owner, 'evidence-resume', saved['contract'], saved['executor'], adapter=Reviewer,
                            paid_scope=saved['authority']['paid_scope'], resume=True,
                            question=lambda _prompt: 'diagnosis ties retained check evidence to the outstanding gap').invoke()
            chain = owner.store.review_chain('evidence-resume', private=True)
            basis = [json.loads(row['details']) for row in owner.store.db.execute(
                "SELECT details FROM execution_history WHERE run_id='evidence-resume' AND kind='evidence_reassessment'")]
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(calls), 1)
        self.assertEqual([(item['role'], item['state']) for item in chain['executions']],
                         [('reviewer', 'rejected'), ('reviewer', 'approved')])
        self.assertEqual([item['references']['head'] for item in chain['executions']], [self.base, self.base])
        self.assertEqual(basis[0]['rejecting_execution_id'], 'review-gap')
        observed = cli.status(self.project, 'evidence-resume')
        self.assertNotIn('diagnosis ties retained check evidence', json.dumps(observed))
        self.assertEqual(observed['review_authorization']['next_stage'], 'complete')

    def test_resume_continues_only_eligible_second_review(self):
        contract = {'tasks': [{'id': 'done', 'description': 'synthetic'}]}
        with Authority(self.project) as owner:
            store = owner.store
            store.start('review-resume', self.base, contract=contract, executor=EXECUTOR,
                        authority={'paid_scope': {'agent_providers': ['fixture'], 'apis': []}}, review_base=self.base)
            store.task('review-resume', 'done', 'complete', self.base, self.base)
            store.history('review-resume', 'done', 'checkpoint', 'passed',
                          {'sha': self.base, 'paths': [], 'artifacts': [], 'no_change': True})
            store.review_dispatch('review-resume', 'review-1', review_base=self.base, review_head=self.base)
            store.review_outcome('review-resume', 'review-1', 'rejected', findings=['x:1 - synthetic'],
                                 references={'base': self.base, 'head': self.base})
            store.review_dispatch('review-resume', 'fix-1', role='fixer', review_ordinal=1, fixing_round=1,
                                  trigger_execution_id='review-1', predecessor_execution_id='review-1',
                                  review_base=self.base, review_head=self.base)
            store.review_outcome('review-resume', 'fix-1', 'approved', findings=[],
                                 references={'base': self.base, 'head': self.base})
            store.finish('review-resume', 'failed', self.base, 'interrupted after fixer')

        class Reviewer:
            calls = 0
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                assert kwargs['read_only']
                assert 'Historical review has no explicit coverage' in _prompt
                assert 'establish original coverage before approval' in _prompt
                Reviewer.calls += 1
                return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'

        with Authority(self.project) as owner:
            saved = owner.store.resume('review-resume')['input']
            result = Engine(owner, 'review-resume', saved['contract'], saved['executor'], adapter=Reviewer,
                            paid_scope=saved['authority']['paid_scope'], resume=True).invoke()
            chain = owner.store.review_chain('review-resume', private=True)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(Reviewer.calls, 1)
        self.assertEqual((chain['review_count'], chain['fixing_round_count']), (2, 1))
        self.assertEqual(chain['executions'][0]['findings'], [['x:1 - synthetic']])


class UnfinishedTaskResumeTests(ProjectTest):
    def test_terminal_failure_requires_inspection_and_targeted_saved_continuation(self):
        from coherence_workflow.store import Blocked
        project = self.project
        prior_prompt_sentinel = 'PRIOR-FULL-PROMPT-SENTINEL-resume'
        contract = {'tasks': [{'id': 'tiny', 'description': 'tiny failure fixture'}]}
        identity = {'id': 'private-session', 'file': '/private/fixture.jsonl'}
        class Failed:
            def __init__(self, *args, **kwargs): self.saved_session = identity
            def prompt(self, prompt, **kwargs): raise Blocked('terminal unknown transport cause')
        with Authority(project) as owner:
            with patch.object(engine, '_IMPLEMENTATION_AUTHORITY',
                              engine._IMPLEMENTATION_AUTHORITY + prior_prompt_sentinel):
                with self.assertRaisesRegex(Blocked, 'terminal unknown'):
                    Engine(owner, 'terminal', contract, EXECUTOR, adapter=Failed).invoke()
            retained_details = owner.store.db.execute(
                "SELECT details FROM execution_history WHERE run_id='terminal' AND task_id='tiny' "
                "AND kind='worker_invocation' AND state='failed'").fetchone()['details']
            self.assertIn(prior_prompt_sentinel, retained_details)
            owner.store.resume('terminal')
            calls = []
            class Continued:
                def __init__(self, *args, **kwargs): pass
                def prompt(self, prompt, **kwargs):
                    calls.append(prompt)
                    if kwargs.get('read_only'): return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                    self_test.assertIn('terminal unknown transport cause', prompt)
                    self_test.assertIn('diagnosed fixture disconnected pipe; repaired fixture transport', prompt)
                    self_test.assertIn('Retained history reference:', prompt)
                    self_test.assertNotIn(prior_prompt_sentinel, prompt)
                    self_test.assertEqual(kwargs['saved_session'], identity)
                    return 'continued targeted work'
            self_test = self
            with self.assertRaisesRegex(Blocked, 'remains unknown'):
                Engine(owner, 'terminal', contract, EXECUTOR, adapter=Continued, resume=True,
                       question=lambda text: 'unknown').invoke()
            self.assertEqual(calls, [])
            owner.store.resume('terminal')
            inspected = []
            def inspect(text):
                inspected.append(text)
                return 'diagnosed fixture disconnected pipe; repaired fixture transport'
            result = Engine(owner, 'terminal', contract, EXECUTOR, adapter=Continued, resume=True,
                            question=inspect).invoke()
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(len(inspected), 1)
            self.assertIn('private-session', inspected[0])
            self.assertIn('tiny', inspected[0])
            self.assertIn('Preserve its existing requirements, authority, and acceptance constraints', inspected[0])
            self.assertIn('As coordinating agent, inspect', inspected[0])
            self.assertIn('do not ask the owner to debug routine technical failures', inspected[0])
            self.assertIn('leave empty if unknown', inspected[0])
            self.assertNotIn(prior_prompt_sentinel, inspected[0])
            self.assertEqual(owner.store.db.execute(
                "SELECT details FROM execution_history WHERE run_id='terminal' AND task_id='tiny' "
                "AND kind='worker_invocation' AND state='failed'").fetchone()['details'], retained_details)
            self.assertEqual(len(calls), 2)


    def test_inspected_external_repair_checkpoint_precedes_retained_continuation_without_replay(self):
        """Mechanical fixture only; coordinator/delegation autonomy remains a separate V3 exercise."""
        from coherence_workflow.store import Blocked
        project, calls = self.project, []
        saved = {'id': 'blocked-worker', 'file': '/private/blocked.jsonl'}
        contract = admit({'paid_scope': {'approved': True, 'agent_providers': ['fixture'], 'apis': []}, 'tasks': [
            {'id': 'predecessor', 'description': 'completed predecessor', 'owned_paths': ['predecessor.txt']},
            {'id': 'unfinished', 'description': 'blocked unfinished worker', 'owned_paths': ['worker.txt'],
             'checks': [[sys.executable, '-B', '-c', "from pathlib import Path; assert Path('repair.txt').read_text() == 'repaired\\n'"]]},
        ]})

        class BlockedWorker:
            def __init__(self, *_args, **_kwargs): self.saved_session = saved
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'): return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                calls.append('predecessor' if 'completed predecessor' in prompt else 'unfinished')
                if 'completed predecessor' in prompt:
                    kwargs['claim']('predecessor.txt')
                    project.joinpath('predecessor.txt').write_text('complete\n')
                    return 'predecessor complete'
                raise Blocked('diagnosed blocker requires coordinator repair.txt outside worker paths')

        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'requires coordinator repair.txt'):
                Engine(owner, 'scoped-repair', contract, EXECUTOR, adapter=BlockedWorker,
                       paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            predecessor_sha = owner.store.db.execute(
                "SELECT result FROM execution_tasks WHERE run_id='scoped-repair' AND task_id='predecessor'").fetchone()['result']

        # This models the separately assigned coordinator repair: exact out-of-worker path,
        # relevant check, and focused Git checkpoint before the unfinished run is continued.
        project.joinpath('repair.txt').write_text('repaired\n')
        subprocess.run(["git", "add", "--", "repair.txt"], cwd=project, check=True)
        subprocess.run(["git", "commit", "-m", "fixture scoped repair", "--", "repair.txt"], cwd=project, check=True)
        repair_sha = git(project, 'rev-parse', 'HEAD').decode().strip()
        self.assertEqual(git(project, 'show', '--name-only', '--format=', repair_sha).decode().splitlines(), ['repair.txt'])
        subprocess.run([sys.executable, '-B', '-c', "from pathlib import Path; assert Path('repair.txt').read_text() == 'repaired\\n'"], cwd=project, check=True)

        class Continued:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'): return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                calls.append('continued')
                self_test.assertIn('Continue only the unfinished same-task work.', prompt)
                self_test.assertEqual(kwargs['saved_session'], saved)
                kwargs['claim']('worker.txt')
                project.joinpath('worker.txt').write_text('continued\n')
                return 'continued after inspected repair'

        self_test = self
        with Authority(project) as owner:
            owner.store.resume('scoped-repair')
            result = Engine(owner, 'scoped-repair', contract, EXECUTOR, adapter=Continued, resume=True,
                            paid_scope={'agent_providers': ['fixture'], 'apis': []},
                            question=lambda prompt: (self.assertIn('Retained history reference:', prompt) or
                                                     'repair.txt diff/check/checkpoint inspected')).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(calls, ['predecessor', 'unfinished', 'continued'])
        self.assertEqual(predecessor_sha, result['checkpoints'][0]['sha'])
        self.assertEqual(repair_sha, git(project, 'rev-parse', repair_sha).decode().strip())

    def test_resume_refuses_fourth_same_session_dispatch_without_adopting_unrelated_work(self):
        project = self.project
        contract = admit({'paid_scope': {'approved': True, 'agent_providers': ['fixture'], 'apis': []}, 'tasks': [
            {'id': 'completed', 'description': 'first synthetic task', 'owned_paths': ['one.txt']},
            {'id': 'partial', 'description': 'partial synthetic task', 'owned_paths': ['two.txt'],
             'generated_outputs': ['web/dist/'], 'checks': [[
                 'python3', '-B', '-c', "from pathlib import Path; assert Path('ready').exists(), 'synthetic setup missing'"]]}
        ]})

        identity = {'id': 'partial-resume-session', 'file': '/private/partial-resume.jsonl'}
        class Interrupted:
            def __init__(self, *_args, **_kwargs): self.saved_session = identity
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                if 'Actual failed attempt:' in prompt and not prompt.startswith('Continue only'):
                    raise KeyboardInterrupt
                if 'first synthetic task' in prompt:
                    kwargs['claim']('one.txt')
                    project.joinpath('one.txt').write_text('complete\n')
                    return 'first complete'
                kwargs['claim']('two.txt')
                project.joinpath('two.txt').write_text('partial\n')
                (project/'web/dist').mkdir(parents=True)
                kwargs['claim']('web/dist/known.js')
                project.joinpath('web/dist/known.js').write_text('generated\n')
                return 'partial work'

        with Authority(project) as owner:
            with self.assertRaises(KeyboardInterrupt):
                Engine(owner, 'partial-resume', contract, EXECUTOR, adapter=Interrupted,
                       paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
            first_sha = owner.store.db.execute(
                "SELECT result FROM execution_tasks WHERE run_id='partial-resume' AND task_id='completed'").fetchone()['result']

        project.joinpath('other.txt').write_text('unrelated staged\n')
        git(project, 'add', '--', 'other.txt')
        staged = git(project, 'show', ':other.txt')
        project.joinpath('sentinel.txt').write_text('unrelated dirty bytes\n')
        tasks, executor = self.root / 'ignored-tasks.json', self.root / 'ignored-executor.json'
        tasks.write_text('[]')
        executor.write_text(json.dumps(EXECUTOR))

        class Resumed:
            def __init__(self, *_args, **_kwargs): self.saved_session = identity
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                if 'Actual failed attempt:' in prompt and not prompt.startswith('Continue only'):
                    project.joinpath('ready').write_text('ready\n')
                    return 'corrected setup'
                assert 'cleanup' in kwargs
                kwargs['claim']('two.txt')
                project.joinpath('two.txt').write_text('continued\n')
                kwargs['cleanup']('web/dist/known.js')
                return 'continued partial task'

        output = io.StringIO()
        with patch.dict(os.environ, _DETACHED_BRIDGE), patch.object(cli, 'PiAdapter', Resumed), contextlib.redirect_stdout(output):
            self.assertEqual(cli.main(['resume', '--project', str(project), '--run', 'partial-resume']), 2)
        self.assertEqual(project.joinpath('two.txt').read_text(), 'continued\n')
        self.assertFalse((project/'web/dist/known.js').exists())
        self.assertEqual(git(project, 'show', ':other.txt'), staged)
        self.assertEqual(project.joinpath('sentinel.txt').read_text(), 'unrelated dirty bytes\n')
        self.assertEqual(git(project, 'show', '--name-only', '--format=', 'HEAD').decode().splitlines(), ['one.txt'])
        with Authority(project) as owner:
            history = [(row['kind'], row['state'], json.loads(row['details'])) for row in owner.store.db.execute(
                "SELECT kind,state,details FROM execution_history WHERE run_id='partial-resume' ORDER BY seq")]
            first = owner.store.db.execute(
                "SELECT result FROM execution_tasks WHERE run_id='partial-resume' AND task_id='completed'").fetchone()['result']
            terminal_calls = [row['state'] for row in owner.store.db.execute(
                "SELECT state FROM execution_history WHERE run_id='partial-resume' AND task_id='partial' "
                "AND kind='worker_invocation' AND state IN ('returned','interrupted','failed') ORDER BY seq")]
            task_error = owner.store.db.execute(
                "SELECT details FROM execution_tasks WHERE run_id='partial-resume' AND task_id='partial'").fetchone()['details']
            partial_dispatches = [json.loads(row['details']) for row in owner.store.db.execute(
                "SELECT details FROM execution_history WHERE run_id='partial-resume' AND task_id='partial' "
                "AND kind='worker_dispatch' AND state='reserved' ORDER BY seq")]
        self.assertEqual(first, first_sha)
        # Initial work, interrupted correction, and resumed work consume the allowance;
        # the fourth correction is refused before the adapter is invoked.
        self.assertEqual(terminal_calls, ['returned', 'interrupted', 'returned'])
        self.assertEqual([facts['session']['id'] for facts in partial_dispatches], [identity['id']] * 3)
        self.assertIn('allowance exhausted for task partial session partial-resume-session', task_error)
        self.assertTrue(any(kind == 'check' and state == 'failed' and details['exit_code'] == 1
                            for kind, state, details in history))
        self.assertTrue(any(kind == 'mutation' and state == 'claimed' and details['artifacts'] == ['web/dist/known.js']
                            for kind, state, details in history))


class CancelledPartialResumeTests(ProjectTest):
    def test_owned_cancellation_drains_fixture_tool_before_same_run_continuation(self):
        project = self.project
        contract = admit({'paid_scope': {'approved': True, 'agent_providers': ['fixture'], 'apis': []}, 'tasks': [{
            'id': 'cancelled-partial', 'description': 'synthetic owned cancellation fixture',
            'owned_paths': ['work.txt'], 'generated_outputs': ['web/dist/'],
            'checks': [[sys.executable, '-B', '-c', "from pathlib import Path; assert Path('work.txt').read_text() == 'continued\\n'"]],
        }]})
        tool = []
        identity = {'id': 'cancelled-partial-session', 'file': '/private/cancelled-partial.jsonl'}

        class Interrupted:
            def __init__(self, *_args, **_kwargs): self.saved_session = identity
            def prompt(self, _prompt, **kwargs):
                kwargs['claim']('work.txt')
                project.joinpath('work.txt').write_text('partial\n')
                (project/'web/dist').mkdir(parents=True)
                kwargs['claim']('web/dist/known.js')
                project.joinpath('web/dist/known.js').write_text('generated\n')
                kwargs['command']('start', 'synthetic-tool')
                child = subprocess.Popen([sys.executable, '-B', '-c', 'import time; time.sleep(60)'])
                tool.append(child)
                child.terminate()
                child.wait()
                raise KeyboardInterrupt

        with Authority(project) as owner:
            with self.assertRaises(KeyboardInterrupt):
                Engine(owner, 'cancelled-partial', contract, EXECUTOR, adapter=Interrupted,
                       paid_scope={'agent_providers': ['fixture'], 'apis': []}).invoke()
        self.assertIsNotNone(tool[0].returncode, 'test-owned tool must drain before the writer lock releases')
        with Authority(project) as owner:
            history = [(row['kind'], row['state'], json.loads(row['details'])) for row in owner.store.db.execute(
                "SELECT kind,state,details FROM execution_history WHERE run_id='cancelled-partial' ORDER BY seq")]
            self.assertTrue(any(kind == 'tool_command' and state == 'started' and details['call'] == 'synthetic-tool'
                                for kind, state, details in history))
            self.assertTrue(any(kind == 'worker' and state == 'interrupted' for kind, state, _ in history))
            self.assertTrue(any(kind == 'mutation' and details['artifacts'] == ['web/dist/known.js']
                                for kind, _, details in history))
            saved = owner.store.resume('cancelled-partial')['input']

            class Continued:
                def __init__(self, *_args, **_kwargs): self.saved_session = identity
                def prompt(self, _prompt, **kwargs):
                    if kwargs.get('read_only'):
                        return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                    kwargs['claim']('work.txt')
                    project.joinpath('work.txt').write_text('continued\n')
                    kwargs['cleanup']('web/dist/known.js')
                    return 'continued after owned cancellation'

            result = Engine(owner, 'cancelled-partial', saved['contract'], saved['executor'], adapter=Continued,
                            paid_scope=saved['authority']['paid_scope'], resume=True).invoke()
            chain = owner.store.review_chain('cancelled-partial', private=True)
            terminal_calls = [row['state'] for row in owner.store.db.execute(
                "SELECT state FROM execution_history WHERE run_id='cancelled-partial' AND task_id='cancelled-partial' "
                "AND kind='worker_invocation' AND state IN ('returned','interrupted','failed') ORDER BY seq")]
        self.assertEqual(result['status'], 'complete')
        self.assertFalse((project/'web/dist/known.js').exists())
        self.assertEqual(terminal_calls, ['interrupted', 'returned'])
        self.assertEqual((chain['review_count'], chain['fixing_round_count']), (1, 0))
        self.assertEqual(len(result['checkpoints']), 1)
