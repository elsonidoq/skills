"""Synthetic same-run resume fixtures; no real workflow run is replayed."""
import contextlib
import io
import json
import os
import subprocess
import sys
from unittest.mock import patch

from coherence_workflow import cli
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}}

# CLI resume fixtures are detached local runs, not descendants of a host's active bridge.
_DETACHED_BRIDGE = {name: '' for name in (
    'COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
    'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}


class SameRunResumeTests(ProjectTest):
    def test_checkpoint_history_survives_interruption_before_task_completion(self):
        project = self.project
        contract = {'tasks': [{'id': 'tiny', 'description': 'tiny disposable edit', 'owned_paths': ['tiny.txt']}]}
        class Adapter:
            workers = 0
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'): return '{"approved":true,"findings":[]}'
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


    def test_resume_checkpoints_already_edited_established_handoff_without_second_edit(self):
        project = self.project
        project.joinpath('recovery.txt').write_bytes(b'preserved recovery bytes\n')
        contract = admit({'paid_scope': {'approved': True, 'agent_providers': ['fixture'], 'apis': []}, 'tasks': [{
            'id': 'handoff', 'description': 'resume an exact recovery handoff',
            'owned_paths': ['recovery.txt'], 'handoff_paths': ['recovery.txt'],
        }]})

        class Interrupted:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
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
                def __init__(self, *_args, **_kwargs): pass
                def prompt(self, _prompt, **kwargs):
                    if kwargs.get('read_only'):
                        return '{"approved":true,"findings":[]}'
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
        calls = []
        saved = {'id': 'warm-review', 'file': '/private/review.jsonl',
                 'compatibility': {'readOnly': True}}
        case = self
        class Adapter:
            def __init__(self, _project, profile, **_kwargs):
                self.profile = profile
                self.saved_session = None
            def prompt(self, prompt, **kwargs):
                calls.append((self.profile, kwargs))
                if kwargs.get('read_only'):
                    if len(calls) == 2:
                        self.saved_session = saved
                        return '{"approved":false,"findings":["owned.txt:1 - fixture defect [basis: correctness]"]}'
                    case.assertIsNone(self.saved_session)
                    return '{"approved":true,"findings":[]}'
                if 'Actionable findings:' in prompt:
                    case.assertEqual(self.saved_session, saved)
                    case.assertEqual(kwargs['saved_session'], saved)
                    case.assertTrue(kwargs['review_repair'])
                    case.assertEqual(self.profile, EXECUTOR['reviewer'])
                    self.saved_session = {**saved, 'compatibility': {'readOnly': False}}
                return 'fixture'
        contract = admit([{'id': 'task', 'description': 'fixture'}])
        with Authority(self.project) as owner:
            with patch.object(Engine, 'run_fix', side_effect=KeyboardInterrupt), self.assertRaises(KeyboardInterrupt):
                Engine(owner, 'review-restart', contract, EXECUTOR, adapter=Adapter).invoke()
        # A new authority and Engine have no in-memory reviewer adapter.
        with Authority(self.project) as owner:
            owner.store.resume('review-restart')
            result = Engine(owner, 'review-restart', contract, EXECUTOR, adapter=Adapter, resume=True).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(calls), 4)

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

        class Interrupted:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
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
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    resumed_calls.append('review')
                    return '{"approved":true,"findings":[]}'
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
                Reviewer.calls += 1
                return '{"approved":true,"findings":[]}'

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
        contract = {'tasks': [{'id': 'tiny', 'description': 'tiny failure fixture'}]}
        identity = {'id': 'private-session', 'file': '/private/fixture.jsonl'}
        class Failed:
            def __init__(self, *args, **kwargs): self.saved_session = identity
            def prompt(self, prompt, **kwargs): raise Blocked('terminal unknown transport cause')
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'terminal unknown'):
                Engine(owner, 'terminal', contract, EXECUTOR, adapter=Failed).invoke()
            owner.store.resume('terminal')
            calls = []
            class Continued:
                def __init__(self, *args, **kwargs): pass
                def prompt(self, prompt, **kwargs):
                    calls.append(prompt)
                    if kwargs.get('read_only'): return '{"approved":true,"findings":[]}'
                    self_test.assertIn('terminal unknown transport cause', prompt)
                    self_test.assertIn('diagnosed fixture disconnected pipe; repaired fixture transport', prompt)
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
            self.assertIn('As coordinating agent, inspect', inspected[0])
            self.assertIn('do not ask the owner to debug routine technical failures', inspected[0])
            self.assertIn('leave empty if unknown', inspected[0])
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
                if kwargs.get('read_only'): return '{"approved":true,"findings":[]}'
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
                if kwargs.get('read_only'): return '{"approved":true,"findings":[]}'
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
                            question=lambda prompt: (self.assertIn('Actual invocation:', prompt) or
                                                     'repair.txt diff/check/checkpoint inspected')).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(calls, ['predecessor', 'unfinished', 'continued'])
        self.assertEqual(predecessor_sha, result['checkpoints'][0]['sha'])
        self.assertEqual(repair_sha, git(project, 'rev-parse', repair_sha).decode().strip())

    def test_resume_continues_saved_partial_task_without_adopting_unrelated_work(self):
        project = self.project
        contract = admit({'paid_scope': {'approved': True, 'agent_providers': ['fixture'], 'apis': []}, 'tasks': [
            {'id': 'completed', 'description': 'first synthetic task', 'owned_paths': ['one.txt']},
            {'id': 'partial', 'description': 'partial synthetic task', 'owned_paths': ['two.txt'],
             'generated_outputs': ['web/dist/'], 'checks': [[
                 'python3', '-B', '-c', "from pathlib import Path; assert Path('ready').exists(), 'synthetic setup missing'"]]}
        ]})

        class Interrupted:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
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
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
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
            self.assertEqual(cli.main(['resume', '--project', str(project), '--run', 'partial-resume']), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(project.joinpath('two.txt').read_text(), 'continued\n')
        self.assertFalse((project/'web/dist/known.js').exists())
        self.assertEqual(git(project, 'show', ':other.txt'), staged)
        self.assertEqual(project.joinpath('sentinel.txt').read_text(), 'unrelated dirty bytes\n')
        self.assertEqual(git(project, 'show', '--name-only', '--format=', 'HEAD').decode().splitlines(), ['two.txt'])
        with Authority(project) as owner:
            history = [(row['kind'], row['state'], json.loads(row['details'])) for row in owner.store.db.execute(
                "SELECT kind,state,details FROM execution_history WHERE run_id='partial-resume' ORDER BY seq")]
            first = owner.store.db.execute(
                "SELECT result FROM execution_tasks WHERE run_id='partial-resume' AND task_id='completed'").fetchone()['result']
            terminal_calls = [row['state'] for row in owner.store.db.execute(
                "SELECT state FROM execution_history WHERE run_id='partial-resume' AND task_id='partial' "
                "AND kind='worker_invocation' AND state IN ('returned','interrupted','failed') ORDER BY seq")]
        self.assertEqual(first, first_sha)
        # Initial work, interrupted check correction, resumed work, then setup correction.
        self.assertEqual(terminal_calls, ['returned', 'interrupted', 'returned', 'returned'])
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

        class Interrupted:
            def __init__(self, *_args, **_kwargs): pass
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
                def __init__(self, *_args, **_kwargs): pass
                def prompt(self, _prompt, **kwargs):
                    if kwargs.get('read_only'):
                        return '{"approved":true,"findings":[]}'
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
