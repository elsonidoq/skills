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
    def test_public_cli_framed_adapter_terminal_reply_and_real_git(self):
        """Reproducible local-mechanism proof; no live model or owner approval."""
        import pty
        from pathlib import Path
        from coherence_workflow.store import git
        tasks, executor, host = (self.root/name for name in ('tasks.json', 'executor.json', 'fixture_host.py'))
        tasks.write_text(json.dumps([
            {'id': 'B', 'description': 'fixture consumer', 'depends': ['A'], 'owned_paths': ['consumer.txt'],
             'checks': [[sys.executable, '-B', '-c', "assert open('consumer.txt').read() == 'answered\\n'"]]},
            {'id': 'A', 'description': 'fixture producer', 'owned_paths': ['producer.txt'],
             'checks': [[sys.executable, '-B', '-c', "assert open('producer.txt').read() == 'producer\\n'"]]}]))
        executor.write_text(json.dumps({'provider': 'fixture', 'model': 'worker', 'effort': 'medium',
                                       'reviewer': {'provider': 'fixture', 'model': 'reviewer', 'effort': 'medium'}}))
        host.write_text('''import json, sys, subprocess
from pathlib import Path
request = json.loads(input())
project, prompt = Path(request['project']), request['prompt']
assert request['executor']['provider'] == 'fixture'
assert request['executor']['effort'] == 'medium'
session = {'id': 'fixture-consumer', 'file': str(project / '.coherence/fixture-session')}
def emit(value): print(json.dumps(value), flush=True)
if request['readOnly']:
    assert request['executor']['model'] == 'reviewer'
    assert 'savedSession' not in request
    emit({'type': 'result', 'text': json.dumps({'approved': True, 'findings': [], 'coverage': ['local fixture'], 'coverage_gaps': []})})
elif '"id":"A"' in prompt:
    emit({'type': 'claim', 'path': 'producer.txt'})
    assert json.loads(input()) == {'ok': True}
    (project / 'producer.txt').write_text('producer\\n')
    emit({'type': 'result', 'text': 'fixture producer complete'})
else:
    assert subprocess.check_output(['git', 'show', 'HEAD:producer.txt'], cwd=project) == b'producer\\n'
    if 'savedSession' not in request:
        emit({'type': 'result', 'text': 'fixture waiting', 'outcome': 'waiting', 'session': session,
              'question': {'tool_call_id': 'fixture-question', 'question': 'Fixture: continue consumer?'}})
    else:
        assert request['savedSession'] == session
        assert 'actual-terminal-fixture-reply' in prompt
        emit({'type': 'claim', 'path': 'consumer.txt'})
        assert json.loads(input()) == {'ok': True}
        (project / 'consumer.txt').write_text('answered\\n')
        emit({'type': 'result', 'text': 'fixture consumed actual terminal reply', 'session': session})
''')
        # Inject only the provider host. CLI parsing, PiAdapter framing, saver, checks,
        # writer lock, terminal input, read-only reviewer and Git are real.
        entry = ('import sys; from pathlib import Path; from coherence_workflow import cli, pi_adapter; '
                 'pi_adapter.host_path=lambda: Path(sys.argv[1]); '
                 'raise SystemExit(cli.main(sys.argv[2:]))')
        env = {**os.environ, 'PYTHONPATH': str(ROOT/'runtime'), 'PYTHONDONTWRITEBYTECODE': '1',
               'COHERENCE_NODE': sys.executable,
               **{key: '' for key in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                                      'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}}
        prefix = [sys.executable, '-B', '-c', entry, str(host)]
        start = [*prefix, 'start', '--project', str(self.project), '--tasks', str(tasks),
                 '--executor', str(executor), '--run', 'terminal-fixture']
        first = subprocess.run(start, env=env, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(first.stdout)['status'], 'waiting')
        self.assertFalse((self.project/'consumer.txt').exists())
        self.assertEqual(git(self.project, 'rev-list', '--count', self.base+'..HEAD'), b'1\n')
        before = git(self.project, 'rev-parse', 'HEAD')
        master, slave = pty.openpty()
        try:
            resumed = subprocess.Popen([*prefix, 'resume', '--project', str(self.project), '--run', 'terminal-fixture'],
                                       env=env, stdin=slave, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            os.close(slave)
            slave = None
            os.write(master, b'actual-terminal-fixture-reply\n')
            output, error = resumed.communicate(timeout=30)
        finally:
            os.close(master)
            if slave is not None:
                os.close(slave)
        self.assertEqual(resumed.returncode, 0, output+error)
        result = json.loads(output.splitlines()[-1].removeprefix('> '))
        self.assertEqual(result['status'], 'complete')
        self.assertEqual([item['task_id'] for item in result['checkpoints']], ['A', 'B'])
        self.assertEqual(git(self.project, 'rev-list', '--count', self.base+'..HEAD'), b'2\n')
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD^'), before)
        self.assertEqual((self.project/'consumer.txt').read_text(), 'answered\n')
        print('T011 local fixture-provider proof; not live model judgment. Public start output:\n'+first.stdout)
        print('Public terminal resume output:\n'+output)
        print('Actual fixture Git commits:\n'+git(self.project, 'log', '-2', '--format=%H %P %s', '--name-only').decode())

    def test_public_cli_uncertain_provider_and_git_stop_without_replay(self):
        from coherence_workflow.store import git
        from coherence_workflow import git_effects
        tasks, executor = self.root/'tasks.json', self.root/'executor.json'
        executor.write_text(json.dumps({'provider': 'fixture', 'model': 'worker', 'effort': 'medium',
                                       'reviewer': {'provider': 'fixture', 'model': 'reviewer', 'effort': 'medium'}}))
        project = self.project
        env = {key: '' for key in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                                   'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}
        for boundary in ('provider', 'git'):
            calls, commits = [], []
            name = boundary+'.txt'
            tasks.write_text(json.dumps([{'id': 'one', 'description': 'uncertain fixture', 'owned_paths': [name]}]))
            class Adapter:
                def __init__(self, *args, **kwargs): pass
                def prompt(self, prompt, **kwargs):
                    calls.append('worker')
                    if boundary == 'provider':
                        from coherence_workflow.store import Blocked
                        raise Blocked('SDK fixture settlement and effects are uncertain; inspect saved operation')
                    kwargs['claim'](name)
                    (project/name).write_text('preserved uncertain Git bytes\n')
                    return 'fixture done'
            def uncertain_git(where, *arguments, **kwargs):
                if arguments[0] == 'commit':
                    commits.append('attempted')
                    raise KeyboardInterrupt('fixture lost Git completion at attempted parent')
                return git(where, *arguments, **kwargs)
            start = ['start', '--project', str(project), '--tasks', str(tasks), '--executor', str(executor), '--run', boundary]
            with patch.dict(os.environ, env), patch('coherence_workflow.cli.PiAdapter', Adapter), \
                 patch.object(git_effects, 'git', side_effect=uncertain_git), contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(main(start), 2 if boundary == 'provider' else 130)
                first = out.getvalue()
                self.assertEqual(main(['resume', '--project', str(project), '--run', boundary]), 2)
                transcript = out.getvalue()
            self.assertEqual(calls, ['worker'])
            self.assertEqual(commits, [] if boundary == 'provider' else ['attempted'])
            self.assertIn('uncertain', transcript)
            self.assertEqual(git(project, 'rev-parse', 'HEAD').decode().strip(), self.base)
            print('T011 '+boundary+' uncertainty fixture; no replay. Public CLI output:\n'+transcript)
            if boundary == 'git':
                self.assertTrue((project/name).exists())

    def test_graph_cli_dependent_commits_and_fresh_review(self):
        from coherence_workflow.store import git
        tasks, executor = self.root/'tasks.json', self.root/'executor.json'
        tasks.write_text(json.dumps([
            {'id': 'second', 'description': 'consumer', 'depends': ['first'], 'owned_paths': ['second.txt'],
             'checks': [['python3', '-B', '-c', "from pathlib import Path; assert Path('second.txt').read_text() == 'consumer\\n'"]]},
            {'id': 'first', 'description': 'producer', 'owned_paths': ['first.txt'],
             'checks': [['python3', '-B', '-c', "from pathlib import Path; assert Path('first.txt').read_text() == 'producer\\n'"]]}]))
        executor.write_text(json.dumps({'provider': 'fixture', 'model': 'worker', 'effort': 'medium',
                                       'reviewer': {'provider': 'fixture', 'model': 'reviewer', 'effort': 'medium'}}))
        project, calls = self.project, []
        class Boundary:
            def __init__(self, _project, profile, **kwargs): self.profile = profile
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    calls.append(('review', self.profile['model'], self.profile['effort']))
                    return json.dumps({'approved': True, 'findings': [], 'coverage': ['fixture'], 'coverage_gaps': []})
                if '"id":"first"' in prompt:
                    name, content = 'first.txt', 'producer\n'
                else:
                    self_case.assertEqual(git(project, 'show', 'HEAD:first.txt'), b'producer\n')
                    name, content = 'second.txt', 'consumer\n'
                calls.append((name, self.profile['model'], self.profile['effort']))
                kwargs['claim'](name)
                (project/name).write_text(content)
                return 'fixture complete'
        self_case = self
        env = {key: '' for key in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                                    'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}
        with patch.dict(os.environ, env), patch('coherence_workflow.cli.PiAdapter', Boundary), contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(main(['start', '--project', str(project), '--tasks', str(tasks), '--executor', str(executor), '--run', 'dependent']), 0, out.getvalue())
        result = json.loads(out.getvalue())
        self.assertEqual(result['status'], 'complete')
        self.assertEqual([item['task_id'] for item in result['checkpoints']], ['first', 'second'])
        self.assertEqual(calls, [('first.txt', 'worker', 'medium'), ('second.txt', 'worker', 'medium'), ('review', 'reviewer', 'medium')])
        self.assertEqual(git(project, 'rev-list', '--count', self.base + '..HEAD'), b'2\n')

    def test_graph_cli_pause_reopen_and_answer(self):
        from coherence_workflow.pi_adapter import WaitingQuestion
        tasks, executor = self.root/'tasks.json', self.root/'executor.json'
        tasks.write_text(json.dumps([{'id': 'one', 'description': 'fixture', 'owned_paths': ['owned.txt']}]))
        executor.write_text(json.dumps({'provider': 'fixture', 'model': 'worker', 'effort': 'medium',
                                       'reviewer': {'provider': 'fixture', 'model': 'reviewer', 'effort': 'medium'}}))
        calls, project = [], self.project
        class Boundary:
            def __init__(self, *args, **kwargs):
                self.saved_session = None
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    calls.append('review')
                    return json.dumps({'approved': True, 'findings': [], 'coverage': ['fixture'], 'coverage_gaps': []})
                calls.append(prompt)
                self.saved_session = {'id': 'fixture-session', 'file': str(project/'fixture-session')}
                if len(calls) == 1:
                    return WaitingQuestion({'question': 'Fixture question?'}, self.saved_session)
                self_case.assertIn('actual fixture answer', prompt)
                kwargs['claim']('owned.txt')
                (project/'owned.txt').write_text('answered\n')
                return 'done'
        self_case = self
        env = {key: '' for key in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                                    'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}
        with patch.dict(os.environ, env), patch('coherence_workflow.cli.PiAdapter', Boundary), contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(main(['start', '--project', str(project), '--tasks', str(tasks), '--executor', str(executor), '--run', 'pause']), 0)
            self.assertEqual(json.loads(out.getvalue())['status'], 'waiting')
        self.assertEqual(status(project, 'pause')['waiting']['task_id'], 'one')
        with patch.dict(os.environ, env), patch('coherence_workflow.cli.PiAdapter', Boundary), \
             patch('coherence_workflow.engine.terminal_question', return_value='actual fixture answer'), \
             patch('coherence_workflow.cli.Engine') as constructor:
            from coherence_workflow.engine import Engine
            constructor.side_effect = lambda *a, **k: Engine(*a, **{**k, 'question': lambda _: 'actual fixture answer'})
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(main(['resume', '--project', str(project), '--run', 'pause']), 0, out.getvalue())
            self.assertEqual(json.loads(out.getvalue())['status'], 'complete')
        self.assertEqual((project/'owned.txt').read_text(), 'answered\n')
        self.assertEqual(len(calls), 3)

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
        self.assertEqual(observed['monitoring'], {'state': 'unknown'})
        self.assertEqual(observed['review_chain']['executions'][0]['state'], 'approved')

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
                   'SESSION': 'parent', 'TOKEN': 'token'}, 'parent channel was lost; reconnect through the parent-session bridge')]
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
                              authority={'backend': 'langgraph-v1', 'paid_scope': {'agent_providers': ['fixture'], 'apis': []},
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
                              authority={'backend': 'langgraph-v1', 'paid_scope': paid_scope}, review_base=self.base)
            owner.store.finish('attached-resume', 'failed', self.base, 'fixture interruption')
        env = {f'COHERENCE_PARENT_BRIDGE_{key}': value for key, value in
               {'SOCKET': '/fixture/socket', 'TOKEN': 'fixture', 'SESSION': 'parent', 'RUN': 'attached-resume'}.items()}
        with patch.dict(os.environ, env), patch('coherence_workflow.cli.parent_question', return_value='diagnosed correction') as question, \
             patch('coherence_workflow.cli.Engine') as engine, \
             patch('coherence_workflow.cli.run_graph') as graph, contextlib.redirect_stdout(io.StringIO()) as out:
            graph.side_effect = lambda _engine, **kwargs: engine.call_args.kwargs['question']('recovery diagnosis')
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
        self.assertIn('is legacy, not a LangGraph thread', json.loads(out.getvalue())['reason'])
        self.assertIn('4c1725ebded2f89dec6933b8d193bf34997c62ce', json.loads(out.getvalue())['reason'])
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

    def test_abandon_preserves_historical_monitoring_and_failure(self):
        with Authority(self.project) as owner:
            owner.store.start('recorded', self.base)
            owner.store.db.execute('INSERT INTO execution_monitor_runs(run_id,recording_version,description,started_at) VALUES(?,?,?,?)',
                                   ('recorded', 1, '{}', 1))
            owner.store.db.execute('INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)',
                                   ('recorded', 1, 'review-id', 'review', None, 'failed', 1, '{}'))
            owner.store.finish('recorded', 'failed', self.base, 'ordinary failure')
            owner.store.abandon('recorded')
        observed = status(self.project, 'recorded')
        self.assertEqual(observed['run']['error'], 'ordinary failure')
        self.assertEqual([row['occurrence_id'] for row in observed['monitoring']['observations']], ['review-id'])

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
