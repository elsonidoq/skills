"""Checkpoint failures return to the same synthetic task and reconcile real commits."""
import json
import sqlite3
from unittest.mock import patch

from coherence_workflow.engine import Engine
from coherence_workflow.git_effects import FocusedGit
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}}


class CheckpointRecoveryTests(ProjectTest):
    def test_hook_failure_returns_to_worker_reruns_check_and_checkpoints(self):
        project, prompts = self.project, []
        hook = project/'.git/hooks/pre-commit'
        hook.write_text("#!/bin/sh\ngrep -q '^good$' owned.txt || { echo source-not-corrected >&2; exit 23; }\n")
        hook.chmod(0o755)

        class Worker:
            def __init__(self, *args, **kwargs):
                self.saved_session = {'id': 'checkpoint-correction', 'file': str(project/'checkpoint-correction.jsonl')}
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                prompts.append(prompt)
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('bad\n' if len(prompts) == 1 else 'good\n')
                return 'corrected'

        task = {'id': 'hook', 'description': 'Synthetic hook correction', 'owned_paths': ['owned.txt'],
                'checks': [["python3", "-B", "-c", "from pathlib import Path; assert Path('owned.txt').exists()"]]}
        with Authority(project) as owner:
            result = Engine(owner, 'hook-recovery', admit([task]), EXECUTOR, adapter=Worker).invoke()

        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(prompts), 2)
        self.assertEqual(project.joinpath('owned.txt').read_text(), 'good\n')
        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        rows = [(kind, state, json.loads(details)) for kind, state, details in db.execute(
            "SELECT kind,state,details FROM execution_history WHERE run_id='hook-recovery' ORDER BY seq")]
        db.close()
        self.assertTrue(any(kind == 'checkpoint' and state == 'failed' and 'source-not-corrected' in details['error']
                            for kind, state, details in rows))
        self.assertGreaterEqual(sum(kind == 'check' and state == 'passed' for kind, state, _ in rows), 2)
        self.assertEqual(git(project, 'show', '--name-only', '--format=', 'HEAD').decode().splitlines(), ['owned.txt'])

    def test_reported_failed_commit_is_reconciled_without_duplicate_commit(self):
        project = self.project

        class Worker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('committed\n')
                return 'work'

        original = FocusedGit.checkpoint
        def reported_failure(focused):
            original(focused)
            raise Blocked('reported failure after actual commit')

        with Authority(project) as owner, patch.object(FocusedGit, 'checkpoint', reported_failure):
            result = Engine(owner, 'commit-reconcile', admit([{'id': 'commit', 'description': 'Synthetic commit',
                'owned_paths': ['owned.txt']}]), EXECUTOR, adapter=Worker).invoke()
            rows = [(state, json.loads(details)) for state, details in owner.store.db.execute(
                "SELECT state,details FROM execution_history WHERE run_id='commit-reconcile' AND kind='checkpoint' ORDER BY seq")]

        self.assertEqual(result['status'], 'complete')
        self.assertEqual(git(project, 'rev-list', '--count', self.base + '..HEAD'), b'1\n')
        self.assertEqual(result['checkpoints'][0]['sha'], git(project, 'rev-parse', 'HEAD').decode().strip())
        self.assertEqual(result['checkpoints'][0]['parent'], self.base)
        self.assertEqual([state for state, _ in rows], ['started', 'attempting', 'failed', 'passed'])
        self.assertIn('reported failure after actual commit', rows[2][1]['error'])

    def test_failed_history_write_is_corrected_without_repeating_commit(self):
        project, failed = self.project, []
        class Worker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('one commit\n')
                return 'done'
        with Authority(project) as owner:
            insert = owner.store._history_insert
            def fail_once(db, run, task, kind, state, details, recorded_at):
                if kind == 'checkpoint' and state == 'passed' and not failed:
                    failed.append(True)
                    raise sqlite3.OperationalError('fixture one-time history failure')
                return insert(db, run, task, kind, state, details, recorded_at)
            with patch.object(owner.store, '_history_insert', side_effect=fail_once):
                result = Engine(owner, 'retry-history', admit([{'id': 'one', 'description': 'checkpoint'}]),
                                EXECUTOR, adapter=Worker).invoke()
        self.assertEqual(failed, [True])
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(git(project, 'rev-list', '--count', self.base + '..HEAD'), b'1\n')

    def test_failed_check_is_corrected_before_checkpoint_intent(self):
        project, calls = self.project, []
        class Worker:
            def __init__(self, *args, **kwargs):
                self.saved_session = {'id': 'check-fix', 'file': str(project/'check-fix.jsonl')}
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                calls.append(prompt)
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('bad\n' if len(calls) == 1 else 'good\n')
                return 'done'
        task = {'id': 'check', 'description': 'correct failed check', 'owned_paths': ['owned.txt'],
                'checks': [['python3', '-B', '-c', "from pathlib import Path; assert Path('owned.txt').read_text() == 'good\\n'"]]}
        with Authority(project) as owner:
            result = Engine(owner, 'check-fix', admit([task]), EXECUTOR, adapter=Worker).invoke()
            events = [(row['state'], json.loads(row['details'])) for row in owner.store.db.execute(
                "SELECT state,details FROM execution_history WHERE run_id='check-fix' AND kind='check' ORDER BY seq")]
            intent = json.loads(owner.store.db.execute("SELECT details FROM execution_history WHERE run_id='check-fix' AND kind='checkpoint' AND state='started'").fetchone()[0])
        self.assertEqual([state for state, _ in events], ['failed', 'passed'])
        self.assertEqual(len(intent['check_refs']), 1)
        self.assertEqual(len(calls), 2)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(git(project, 'show', 'HEAD:owned.txt'), b'good\n')

    def test_lost_checkpoint_history_reopens_original_commit_after_head_advances(self):
        project, calls = self.project, []
        self.write('other.txt', 'unrelated staged\n')
        git(project, 'add', '--', 'other.txt')
        staged = git(project, 'show', ':other.txt')
        class Worker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                calls.append('worker')
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('actual checkpoint\n')
                return 'finished semantic acceptance'
        contract = admit([{'id': 'one', 'description': 'checkpoint', 'owned_paths': ['owned.txt'],
                           'checks': [['python3', '-B', '-c', 'pass']]}])
        with Authority(project) as owner:
            insert = owner.store._history_insert
            def fail_pass(db, run, task, kind, state, details, recorded_at):
                if kind == 'checkpoint' and state == 'passed':
                    raise sqlite3.OperationalError('fixture checkpoint history unavailable')
                return insert(db, run, task, kind, state, details, recorded_at)
            with patch.object(owner.store, '_history_insert', side_effect=fail_pass):
                with self.assertRaisesRegex(Blocked, 'history unavailable'):
                    Engine(owner, 'lost', contract, EXECUTOR, adapter=Worker).invoke()
            original = git(project, 'rev-parse', 'HEAD').decode().strip()
            self.assertEqual(git(project, 'show', ':other.txt'), staged)
        self.write('later.txt', 'later unrelated commit\n')
        git(project, 'add', '--', 'later.txt')
        git(project, 'commit', '--only', '-qm', 'later', '--', 'later.txt')
        self.write('unrelated.txt', 'untracked bytes\n')
        with Authority(project) as owner:
            owner.store.resume('lost')
            result = Engine(owner, 'lost', contract, EXECUTOR, adapter=Worker, resume=True).invoke()
            intent = json.loads(owner.store.db.execute("SELECT details FROM execution_history WHERE run_id='lost' AND kind='checkpoint' AND state='started'").fetchone()[0])
        self.assertEqual(len(intent['check_refs']), 1)
        self.assertEqual(result['checkpoints'][0]['sha'], original)
        self.assertEqual(calls, ['worker'])
        self.assertEqual(git(project, 'rev-list', '--count', self.base + '..HEAD'), b'2\n')
        self.assertEqual(git(project, 'show', ':other.txt'), staged)
        self.assertEqual((project/'unrelated.txt').read_text(), 'untracked bytes\n')

    def test_lost_checkpoint_history_rejects_a_check_reference_that_does_not_match(self):
        project = self.project
        class Worker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('actual checkpoint\n')
                return 'finished semantic acceptance'
        contract = admit([{'id': 'one', 'description': 'checkpoint', 'owned_paths': ['owned.txt'],
                           'checks': [['python3', '-B', '-c', 'pass']]}])
        for wrong in ({'command': ['python3', '-B', '-c', 'pass'], 'exit_code': 0, 'output': 'other'}, {}):
            with self.subTest(wrong=wrong), Authority(project) as owner:
                run = 'mismatch-' + str(len(wrong))
                insert = owner.store._history_insert
                def fail_pass(db, run, task, kind, state, details, recorded_at):
                    if kind == 'checkpoint' and state == 'passed':
                        raise sqlite3.OperationalError('fixture checkpoint history unavailable')
                    return insert(db, run, task, kind, state, details, recorded_at)
                with patch.object(owner.store, '_history_insert', side_effect=fail_pass):
                    with self.assertRaisesRegex(Blocked, 'history unavailable'):
                        Engine(owner, run, contract, EXECUTOR, adapter=Worker).invoke()
                row = owner.store.db.execute("SELECT seq,details FROM execution_history WHERE run_id=? AND kind='checkpoint' AND state='started'", (run,)).fetchone()
                intent = json.loads(row['details'])
                intent['checks'] = [wrong]
                owner.store.db.execute('UPDATE execution_history SET details=? WHERE seq=?', (json.dumps(intent), row['seq']))
                owner.store.db.commit()
                with self.assertRaisesRegex(Blocked, 'check references are invalid'):
                    owner.store.completed_checkpoints(run)

    def test_repair_commit_history_loss_reconciles_after_head_advances(self):
        project, calls = self.project, []
        class Adapter:
            reviews = 0
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    Adapter.reviews += 1
                    calls.append('review')
                    if Adapter.reviews == 1:
                        return '{"approved":false,"coverage":["fixture"],"coverage_gaps":[],"findings":["owned.txt:1 - incorrect content causes failure"]}'
                    return '{"approved":true,"coverage":["fixture"],"coverage_gaps":[],"findings":[]}'
                kwargs['claim']('owned.txt')
                if 'Actionable findings:' in prompt:
                    calls.append('fix')
                    project.joinpath('owned.txt').write_text('fixed\n')
                else:
                    calls.append('worker')
                    project.joinpath('owned.txt').write_text('initial\n')
                return 'done'
        contract = admit([{'id': 'one', 'description': 'fixture', 'owned_paths': ['owned.txt'],
                           'checks': [['python3', '-B', '-c', 'pass']]}])
        with Authority(project) as owner:
            history = owner.store.history
            def fail_fix_pass(run, task, kind, state, details=None, **kwargs):
                if kind == 'fixer_checkpoint' and state == 'passed':
                    raise Blocked('fixture lost fixer history')
                return history(run, task, kind, state, details, **kwargs)
            with patch.object(owner.store, 'history', side_effect=fail_fix_pass), self.assertRaisesRegex(Blocked, 'lost fixer history'):
                Engine(owner, 'fix-lost', contract, EXECUTOR, adapter=Adapter).invoke()
            original = git(project, 'rev-parse', 'HEAD').decode().strip()
        self.write('incoming.txt', 'independent\n')
        git(project, 'add', '--', 'incoming.txt')
        git(project, 'commit', '--only', '-qm', 'incoming', '--', 'incoming.txt')
        with Authority(project) as owner:
            owner.store.resume('fix-lost')
            result = Engine(owner, 'fix-lost', contract, EXECUTOR, adapter=Adapter, resume=True).invoke()
            fixed = json.loads(owner.store.db.execute("SELECT details FROM execution_history WHERE run_id='fix-lost' AND kind='fixer_checkpoint' AND state='passed'").fetchone()[0])
        self.assertEqual(fixed['sha'], original)
        self.assertEqual(calls, ['worker', 'review', 'fix', 'review'])
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(git(project, 'rev-list', '--count', self.base + '..HEAD'), b'3\n')

    def test_unrelated_or_mismatched_direct_child_stops_reopen(self):
        for mismatch in ('path', 'content', 'mode'):
            with self.subTest(mismatch=mismatch):
                # A fresh parent for each case; no commit or work is reset.
                parent = git(self.project, 'rev-parse', 'HEAD').decode().strip()
                name = 'intended-' + mismatch + '.txt'
                self.write(name, 'expected\n')
                focused = FocusedGit(self.project, {'id': mismatch}, {'paths': [name]})
                with Authority(self.project) as owner:
                    run = 'mismatch-' + mismatch
                    owner.store.start(run, parent, contract={'tasks': []}, executor={}, authority={})
                    owner.store.task(run, mismatch, 'running', parent)
                    def interrupt(intent):
                        owner.store.history(run, mismatch, 'checkpoint', 'started', {
                            **intent, 'task_id': mismatch, 'check_refs': [], 'checks': [],
                            'checkpoint_occurrence_id': 'occ', 'producer_invocation_id': 'worker',
                            'correction_chain': ['worker']})
                        raise KeyboardInterrupt()
                    with self.assertRaises(KeyboardInterrupt):
                        focused.checkpoint(interrupt)
                    owner.store.history(run, mismatch, 'checkpoint', 'attempting', {})
                    owner.store.finish(run, 'interrupted', parent, 'fixture')
                if mismatch == 'path':
                    other = 'wrong-' + mismatch + '.txt'
                    self.write(other, 'other\n')
                    git(self.project, 'add', '--', other)
                    git(self.project, 'commit', '--only', '-qm', 'wrong path', '--', other)
                else:
                    if mismatch == 'content':
                        self.write(name, 'wrong content\n')
                    else:
                        (self.project/name).chmod(0o755)
                    git(self.project, 'add', '--', name)
                    git(self.project, 'commit', '--only', '-qm', 'wrong content or mode', '--', name)
                head = git(self.project, 'rev-parse', 'HEAD')
                with Authority(self.project) as owner:
                    with self.assertRaisesRegex(Blocked, 'unexpected paths|content or mode differs'):
                        owner.store.completed_checkpoints(run)
                self.assertEqual(git(self.project, 'rev-parse', 'HEAD'), head)
                self.assertTrue((self.project/name).exists())

    def test_unsettled_attempt_at_parent_stops_without_recommit(self):
        project = self.project
        self.write('owned.txt', 'retained work\n')
        focused = FocusedGit(project, {'id': 'uncertain'}, {'paths': ['owned.txt']})
        with Authority(project) as owner:
            owner.store.start('uncertain', self.base, contract={'tasks': []}, executor={}, authority={})
            owner.store.task('uncertain', 'uncertain', 'running', self.base)
            def started(intent):
                owner.store.history('uncertain', 'uncertain', 'checkpoint', 'started', {
                    **intent, 'task_id': 'uncertain', 'check_refs': [], 'checks': [],
                    'checkpoint_occurrence_id': 'occ', 'producer_invocation_id': 'worker',
                    'correction_chain': ['worker']})
            def attempting():
                owner.store.history('uncertain', 'uncertain', 'checkpoint', 'attempting', {})
                raise KeyboardInterrupt()
            focused.before_git_commit = attempting
            with self.assertRaises(KeyboardInterrupt):
                focused.checkpoint(started)
            owner.store.finish('uncertain', 'interrupted', self.base, 'fixture')
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'outcome is uncertain'):
                owner.store.completed_checkpoints('uncertain')
        self.assertEqual(git(project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        self.assertEqual((project/'owned.txt').read_text(), 'retained work\n')
        self.assertEqual(git(project, 'show', ':owned.txt'), b'retained work\n')

    def test_no_change_lost_history_reopens_without_commit(self):
        project, calls = self.project, []
        class Worker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                calls.append('worker')
                return 'no changes needed'
        contract = admit([{'id': 'none', 'description': 'no changes'}])
        with Authority(project) as owner:
            history = owner.store.history
            def fail_pass(run, task, kind, state, details=None, **kwargs):
                if kind == 'checkpoint' and state == 'passed':
                    raise Blocked('fixture lost no-change history')
                return history(run, task, kind, state, details, **kwargs)
            with patch.object(owner.store, 'history', side_effect=fail_pass), self.assertRaises(Blocked):
                Engine(owner, 'no-change', contract, EXECUTOR, adapter=Worker).invoke()
        with Authority(project) as owner:
            owner.store.resume('no-change')
            result = Engine(owner, 'no-change', contract, EXECUTOR, adapter=Worker, resume=True).invoke()
        self.assertTrue(result['checkpoints'][0]['no_change'])
        self.assertEqual(result['checkpoints'][0]['sha'], self.base)
        self.assertEqual(git(project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        self.assertEqual(calls, ['worker'])
