"""Real existing entry: minimal intake/start, empty no-op and passive status."""
import contextlib
import io
import json
import os
import subprocess
import sys
from unittest.mock import patch

from coherence_workflow.cli import main, ROOT, status
from coherence_workflow.store import Authority
from fixtures.support import ProjectTest


class CliTests(ProjectTest):
    def test_minimal_start_uses_selected_executor_no_manifest_or_cgroup(self):
        tasks = self.root/'tasks.json'
        tasks.write_text('{"paid_scope":{"approved":true,"agent_providers":["fixture"],"apis":["fixture test API"]},"tasks":[{"id":"fix","description":"Fix"}]}')
        executor = self.root/'executor.json'
        executor.write_text('{"provider":"fixture","model":"offline-no-provider-call","effort":"medium","reviewer":{"provider":"fixture","model":"offline-reviewer","effort":"medium"}}')
        seen = []
        class Boundary:
            def __init__(self, project, executor, **kwargs): seen.append(executor)
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'): return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                return 'read only offline fixture'
        with patch('coherence_workflow.cli.PiAdapter', Boundary), contextlib.redirect_stdout(io.StringIO()) as out, \
             patch.dict(os.environ, {key: '' for key in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                                                          'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}):
            code = main(['start', '--project', str(self.project), '--tasks', str(tasks), '--executor', str(executor), '--run', 'minimal'])
        self.assertEqual(code, 0, out.getvalue())
        self.assertEqual(seen[0], {'provider': 'fixture', 'model': 'offline-no-provider-call', 'effort': 'medium'})
        self.assertEqual(json.loads(out.getvalue())['checkpoints'][0]['no_change'], True)
        observed = status(self.project, 'minimal')
        self.assertEqual(observed['run']['state'], 'complete')
        self.assertEqual(observed['monitoring']['recording_version'], 1)
        self.assertTrue(any(row['phase'] == 'review' for row in observed['monitoring']['observations']))

    def test_task_handoff_paths_reach_real_cli_execution_input(self):
        tasks, executor = self.root/'tasks.json', self.root/'executor.json'
        tasks.write_text(json.dumps({'tasks': [{'id': 'recover', 'description': 'Correct named recovery file',
                                                  'owned_paths': ['recovery.txt'], 'handoff_paths': ['recovery.txt']}]}))
        executor.write_text('{"provider":"fixture","model":"offline-worker","effort":"medium","reviewer":{"provider":"fixture","model":"offline-reviewer","effort":"medium"}}')
        (self.project/'recovery.txt').write_bytes(b'preexisting recovery\n')
        case = self
        class Boundary:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                case.assertIn('"handoff_paths":["recovery.txt"]', prompt)
                kwargs['claim']('recovery.txt')
                (case.project/'recovery.txt').write_bytes(b'preexisting recovery\nintended edit\n')
                return 'corrected'
        with patch('coherence_workflow.cli.PiAdapter', Boundary), contextlib.redirect_stdout(io.StringIO()) as out, \
             patch.dict(os.environ, {key: '' for key in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                                                          'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}):
            code = main(['start', '--project', str(self.project), '--tasks', str(tasks), '--executor', str(executor), '--run', 'handoff'])
        self.assertEqual(code, 0, out.getvalue())
        checkpoint = json.loads(out.getvalue())['checkpoints'][0]
        self.assertEqual(checkpoint['paths'], ['recovery.txt'])
        from coherence_workflow.store import git
        self.assertEqual(git(self.project, 'show', checkpoint['sha'] + ':recovery.txt'), b'preexisting recovery\nintended edit\n')

    def test_selected_reviewer_profile_reaches_only_fresh_read_only_session(self):
        tasks, executor = self.root/'tasks.json', self.root/'executor.json'
        tasks.write_text('{"paid_scope":{"approved":true,"agent_providers":["fixture"],"apis":["fixture test API"]},"tasks":[{"id":"dummy","description":"Synthetic no-change fixture"}]}')
        worker = {'provider': 'fixture', 'model': 'offline-worker', 'effort': 'medium'}
        reviewer = {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}
        executor.write_text(json.dumps(dict(worker, reviewer=reviewer)))
        sessions, calls = [], []
        class Boundary:
            def __init__(self, project, profile, **kwargs):
                self.profile = profile
                sessions.append(self)
            def prompt(self, prompt, **kwargs):
                calls.append((self.profile, kwargs.get('read_only', False)))
                return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}' if kwargs.get('read_only') else 'synthetic no-change fixture'
        with patch('coherence_workflow.cli.PiAdapter', Boundary), contextlib.redirect_stdout(io.StringIO()) as out, \
             patch.dict(os.environ, {key: '' for key in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                                                          'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}):
            code = main(['start', '--project', str(self.project), '--tasks', str(tasks),
                         '--executor', str(executor), '--run', 'separate-reviewer'])
        self.assertEqual(code, 0, out.getvalue())
        self.assertEqual(calls, [(worker, False), (reviewer, True)])
        self.assertIsNot(sessions[0], sessions[1])
        self.assertTrue(json.loads(out.getvalue())['checkpoints'][0]['no_change'])

    def test_invalid_explicit_reviewer_does_not_fall_back_or_launch(self):
        tasks, executor = self.root/'tasks.json', self.root/'executor.json'
        tasks.write_text('[{"id":"dummy","description":"Synthetic no-change fixture"}]')
        for reviewer in (None, {}, {'provider': 'fixture', 'model': 'offline', 'effort': ''}):
            with self.subTest(reviewer=reviewer):
                executor.write_text(json.dumps({'provider': 'fixture', 'model': 'offline-worker',
                                                'effort': 'medium', 'reviewer': reviewer}))
                with patch('coherence_workflow.cli.PiAdapter') as adapter, contextlib.redirect_stdout(io.StringIO()) as out:
                    code = main(['start', '--project', str(self.project), '--tasks', str(tasks),
                                 '--executor', str(executor), '--run', 'invalid-reviewer'])
                self.assertEqual(code, 2)
                self.assertIn('correct the reviewer profile', json.loads(out.getvalue())['reason'])
                adapter.assert_not_called()

    def test_bad_attached_configuration_stops_before_storage_or_sdk(self):
        tasks, executor = self.root/'tasks.json', self.root/'executor.json'
        tasks.write_text('{"paid_scope":{"approved":true,"agent_providers":["fixture"],"apis":["fixture test API"]},"tasks":[{"id":"smoke","description":"No changes"}]}')
        executor.write_text('{"provider":"fixture","model":"offline","effort":"medium","reviewer":{"provider":"fixture","model":"offline-reviewer","effort":"medium"}}')
        prefix = 'COHERENCE_PARENT_BRIDGE_'
        base_env = {k: v for k, v in os.environ.items() if not k.startswith(prefix)}
        cases = [({'TOKEN': 'partial'}, 'run mismatch'),
                 ({'RUN': 'attached'}, 'bridge unavailable'),
                 ({'RUN': 'attached', 'SOCKET': str(self.root/'absent.sock'),
                   'SESSION': 'parent', 'TOKEN': 'token'}, 'bridge unavailable')]
        for values, error in cases:
            with self.subTest(values=values):
                env = base_env | {prefix+k: v for k, v in values.items()}
                result = subprocess.run([str(ROOT/'scripts/coordinate-implementation'), 'start',
                    '--project', str(self.project), '--tasks', str(tasks), '--executor', str(executor),
                    '--run', 'attached'], env=env | {'COHERENCE_PYTHON': sys.executable}, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(error, json.loads(result.stdout)['reason'])
                self.assertFalse((self.project/'.coherence').exists())

    def test_authorize_routine_repairs_records_only_current_matching_scope(self):
        with Authority(self.project) as owner:
            owner.store.start('retained', self.base, contract={'tasks': []},
                              executor={'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
                                        'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}},
                              authority={'paid_scope': {'agent_providers': ['fixture'], 'apis': []},
                                         'review_policy': 'owner-pair-v1'}, review_base=self.base)
            owner.store.finish('retained', 'failed', self.base, 'stopped fixture')
            original = owner.store.input('retained')
            scope = owner.store.review_scope('retained')
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(main(['authorize-routine-repairs', '--project', str(self.project), '--run', 'retained', '--scope', scope]), 0)
        self.assertEqual(json.loads(out.getvalue())['original_scope'], scope)
        with Authority(self.project) as owner:
            self.assertEqual(owner.store.input('retained'), original)
            self.assertTrue(owner.store.routine_review_authority('retained', scope))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(main(['authorize-routine-repairs', '--project', str(self.project), '--run', 'retained', '--scope', 'wrong']), 2)
        self.assertIn('does not match', json.loads(out.getvalue())['reason'])

    def test_attached_resume_uses_ready_parent_bridge_for_recovery_questions(self):
        paid_scope = {'agent_providers': ['fixture'], 'apis': []}
        with Authority(self.project) as owner:
            owner.store.start('attached-resume', self.base, contract={'tasks': []},
                              executor={'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
                                        'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}},
                              authority={'paid_scope': paid_scope}, review_base=self.base)
            owner.store.finish('attached-resume', 'failed', self.base, 'fixture interruption')
        env = {f'COHERENCE_PARENT_BRIDGE_{key}': value for key, value in
               {'SOCKET': '/fixture/socket', 'TOKEN': 'fixture', 'SESSION': 'parent', 'RUN': 'attached-resume'}.items()}
        with patch.dict(os.environ, env), patch('coherence_workflow.cli.parent_question', return_value='diagnosed correction') as question, \
             patch('coherence_workflow.cli.Engine') as engine, contextlib.redirect_stdout(io.StringIO()) as out:
            engine.return_value.invoke.side_effect = lambda: engine.call_args.kwargs['question']('recovery diagnosis')
            code = main(['resume', '--project', str(self.project), '--run', 'attached-resume'])
        self.assertEqual(code, 0, out.getvalue())
        self.assertEqual(question.call_args_list[0].args, (None,))
        self.assertEqual(question.call_args_list[0].kwargs, {'ready': True})
        self.assertEqual(question.call_args_list[1].args, ('recovery diagnosis',))
        self.assertEqual(engine.call_args.kwargs['paid_scope'], paid_scope)
        self.assertTrue(engine.call_args.kwargs['resume'])

    def test_invalid_saved_reviewer_does_not_mark_legacy_run_running(self):
        legacy_executor = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium'}
        with Authority(self.project) as owner:
            owner.store.start('legacy-reviewer', self.base, contract={'tasks': []}, executor=legacy_executor,
                              authority={'paid_scope': {'agent_providers': ['fixture'], 'apis': []}}, review_base=self.base)
            owner.store.finish('legacy-reviewer', 'failed', self.base, 'legacy interruption')
        with patch.dict(os.environ, {key: '' for key in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                                                          'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            code = main(['resume', '--project', str(self.project), '--run', 'legacy-reviewer'])
        self.assertEqual(code, 2)
        self.assertIn('correct the reviewer profile', json.loads(out.getvalue())['reason'])
        with Authority(self.project) as owner:
            state = owner.store.db.execute("SELECT state,error FROM execution_runs WHERE run_id='legacy-reviewer'").fetchone()
            invocations = list(owner.store.db.execute(
                "SELECT state FROM execution_history WHERE run_id='legacy-reviewer' AND kind='invocation' ORDER BY seq"))
            self.assertEqual(owner.store.input('legacy-reviewer')['executor'], legacy_executor)
        self.assertEqual(tuple(state), ('failed', 'legacy interruption'))
        self.assertEqual([row['state'] for row in invocations], ['started', 'failed'])

    def test_attached_resume_rejects_wrong_run_before_recovery(self):
        with patch.dict(os.environ, {'COHERENCE_PARENT_BRIDGE_RUN': 'other-run'}), \
             patch('coherence_workflow.cli.Engine') as engine, contextlib.redirect_stdout(io.StringIO()) as out:
            code = main(['resume', '--project', str(self.project), '--run', 'requested-run'])
        self.assertEqual(code, 2)
        self.assertIn('parent owner bridge run mismatch', json.loads(out.getvalue())['reason'])
        engine.assert_not_called()
        self.assertFalse((self.project/'.coherence').exists())

    def test_actual_script_empty_task_does_not_create_storage(self):
        tasks = self.root/'empty.yaml'
        tasks.write_text('[]')
        result = subprocess.run([str(ROOT/'scripts/coordinate-implementation'), 'start', '--project', str(self.project),
                                 '--tasks', str(tasks)], env=dict(os.environ, COHERENCE_PYTHON=sys.executable),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'status': 'no tasks'})
        self.assertFalse((self.project/'.coherence').exists())

    def test_abandon_appends_monitoring_without_erasing_failure(self):
        from coherence_workflow.monitoring import Recorder, descriptor
        with Authority(self.project) as owner:
            owner.store.start('recorded', self.base)
            recorder = Recorder(owner.store, 'recorded')
            recorder.register(descriptor({'tasks': []}, {}))
            recorder.emit('review-id', 'review', 'failed', facts={'role': 'reviewer', 'review_base': self.base, 'review_head': self.base})
            owner.store.finish('recorded', 'failed', self.base, 'ordinary failure')
            owner.store.abandon('recorded')
        observed = status(self.project, 'recorded')
        self.assertEqual(observed['run']['error'], 'ordinary failure')
        self.assertIn('review-id', [row['occurrence_id'] for row in observed['monitoring']['observations']])
        self.assertEqual(observed['monitoring']['observations'][-1]['kind'], 'abandoned')

    def test_status_read_only_db_bytes_unchanged(self):
        with Authority(self.project) as owner:
            owner.store.start('test', self.base)
            owner.store.finish('test', 'failed', self.base, 'actual API error')
            database = owner.database
        before = database.read_bytes()
        self.assertEqual(status(self.project, 'test')['run']['error'], 'actual API error')
        self.assertEqual(database.read_bytes(), before)

    def test_actual_cli_sigterm_cancels_owned_host_and_records_interruption(self):
        import time
        host = self.root/'waiting_host.py'
        ready = self.root/'ready'
        host.write_text("import json,signal,sys\nfrom pathlib import Path\njson.loads(input())\nsignal.signal(signal.SIGTERM,lambda *args: None)\nPath(" + repr(str(ready)) + ").write_text('ready')\nsys.stdin.read()\n")
        tasks = self.root/'tasks.json'
        tasks.write_text('{"paid_scope":{"approved":true,"agent_providers":["fixture"],"apis":["fixture test API"]},"tasks":[{"id":"fix","description":"Fix"}]}')
        executor = self.root/'executor.json'
        executor.write_text('{"provider":"fixture","model":"offline-no-provider-call","effort":"medium","reviewer":{"provider":"fixture","model":"offline-reviewer","effort":"medium"}}')
        code = "from pathlib import Path; import coherence_workflow.pi_adapter as a; a.host_path=lambda:Path(" + repr(str(host)) + "); from coherence_workflow.cli import main; raise SystemExit(main())"
        process = subprocess.Popen([sys.executable, '-B', '-c', code, 'start', '--project', str(self.project),
                                    '--tasks', str(tasks), '--executor', str(executor), '--run', 'cancelled'],
                                   env=dict(os.environ, COHERENCE_NODE=sys.executable,
                                            COHERENCE_PARENT_BRIDGE_SOCKET='', COHERENCE_PARENT_BRIDGE_TOKEN='',
                                            COHERENCE_PARENT_BRIDGE_SESSION='', COHERENCE_PARENT_BRIDGE_RUN=''), stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 10  # Test harness only, not a workflow deadline.
            while not ready.exists():
                if process.poll() is not None or time.monotonic() > deadline:
                    self.fail('offline host did not reach the owned cancellation fixture')
                time.sleep(.01)
            process.terminate()  # This test-owned Popen only.
            out, err = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 130, out+err)
            self.assertEqual(json.loads(out)['status'], 'interrupted')
            self.assertEqual(status(self.project, 'cancelled')['run']['state'], 'interrupted')
            self.assertEqual(status(self.project, 'cancelled')['tasks'][0]['state'], 'interrupted')
            with Authority(self.project): pass
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate(timeout=10)
