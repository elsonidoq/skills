"""The internal production task graph, using real saver, checks and Git."""
from unittest.mock import patch

from coherence_workflow.engine import Engine
from coherence_workflow.graph import graph_saver, task_graph
from coherence_workflow.intake import admit
from coherence_workflow.pi_adapter import TaskOutcome
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest

EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'reviewer', 'effort': 'medium'}}


class GraphExecutionTests(ProjectTest):
    def start(self, owner, run, tasks, adapter):
        contract = admit(tasks)
        owner.store.start(run, self.base, contract=contract, executor=EXECUTOR)
        return Engine(owner, run, contract, EXECUTOR, adapter=adapter, paid_scope={'apis': []})

    def test_dependency_checks_correction_and_focused_commits(self):
        project, calls, active = self.project, [], []
        (project/'STATE.md').write_text('unrelated staged\n')
        git(project, 'add', '--', 'STATE.md')
        (project/'sentinel.txt').write_text('unrelated dirty\n')
        class Worker:
            def __init__(self, *args, **kwargs):
                self.saved_session = {'id': 'fixture', 'file': str(project/'session')}
            def prompt(self, prompt, **kwargs):
                self_case.assertFalse(active)
                active.append(True)
                try:
                    calls.append(prompt)
                    if 'consumer' in prompt and 'Task: ' in prompt:
                        self_case.assertEqual(git(project, 'show', 'HEAD:owned.txt'), b'good\n')
                        kwargs['claim']('other.txt')
                        (project/'other.txt').write_text('consumer\n')
                    else:
                        kwargs['claim']('owned.txt')
                        (project/'owned.txt').write_text('good\n' if 'Actual failure:' in prompt else 'bad\n')
                    return 'done'
                finally:
                    active.pop()
        self_case = self
        tasks = [{'id': 'consumer', 'description': 'consumer', 'depends': ['producer'], 'owned_paths': ['other.txt']},
                 {'id': 'producer', 'description': 'producer', 'owned_paths': ['owned.txt'],
                  'checks': [['python3', '-B', '-c', "from pathlib import Path; assert Path('owned.txt').read_text() == 'good\\n'"]]}]
        with Authority(project) as owner:
            engine = self.start(owner, 'graph', tasks, Worker)
            with graph_saver(owner) as saver:
                result = task_graph(engine, saver).invoke({}, {'configurable': {'thread_id': 'graph'}}, durability='sync')
            self.assertEqual(set(result['checkpoints']), {'producer', 'consumer'})
            events = [(r['task_id'], r['kind'], r['state']) for r in owner.store.db.execute(
                "SELECT task_id,kind,state FROM execution_history WHERE run_id='graph' ORDER BY seq")]
        self.assertEqual(len(calls), 3)
        self.assertLess(events.index(('producer', 'checkpoint', 'passed')), events.index(('consumer', 'worker_invocation', 'started')))
        self.assertEqual(git(project, 'rev-list', '--count', self.base + '..HEAD'), b'2\n')
        self.assertEqual(git(project, 'diff', '--cached', '--name-only'), b'STATE.md\n')
        self.assertEqual((project/'sentinel.txt').read_text(), 'unrelated dirty\n')
        for prompt in calls:
            self.assertIn('Current execution authority', prompt)
            self.assertIn('small isolated tests and local test databases', prompt.lower())
            self.assertIn('manual gate', prompt.lower())
            self.assertIn('save-adr', prompt)

    def test_settled_result_reused_after_crash_before_graph_checkpoint(self):
        project, calls = self.project, []
        class Worker:
            def __init__(self, *args, **kwargs):
                self.saved_session = {'id': 'saved', 'file': str(project/'session')}
            def prompt(self, prompt, **kwargs):
                calls.append(prompt)
                kwargs['claim']('owned.txt')
                (project/'owned.txt').write_text('settled\n')
                return 'done'
        with Authority(project) as owner:
            engine = self.start(owner, 'crash', [{'id': 'one', 'description': 'work', 'owned_paths': ['owned.txt']}], Worker)
            original = owner.store.history
            def crash(run, task, kind, state, details=None, **kwargs):
                result = original(run, task, kind, state, details, **kwargs)
                if kind == 'worker_invocation' and state == 'returned':
                    raise KeyboardInterrupt()
                return result
            config = {'configurable': {'thread_id': 'crash'}}
            with graph_saver(owner) as saver:
                with patch.object(owner.store, 'history', side_effect=crash):
                    with self.assertRaises(KeyboardInterrupt):
                        task_graph(engine, saver).invoke({}, config, durability='sync')
            with graph_saver(owner) as saver:
                result = task_graph(engine, saver).invoke(None, config, durability='sync')
            self.assertIn('one', result['checkpoints'])
        self.assertEqual(len(calls), 1)
        self.assertEqual(git(project, 'rev-list', '--count', self.base + '..HEAD'), b'1\n')

    def test_checkpoint_hook_failure_returns_to_scoped_worker(self):
        project, calls = self.project, []
        hook = project/'.git/hooks/pre-commit'
        hook.write_text("#!/bin/sh\ngrep -q '^good$' owned.txt || exit 23\n")
        hook.chmod(0o755)
        class Worker:
            def __init__(self, *args, **kwargs):
                self.saved_session = {'id': 'hook', 'file': str(project/'session')}
            def prompt(self, prompt, **kwargs):
                calls.append(prompt)
                kwargs['claim']('owned.txt')
                (project/'owned.txt').write_text('bad\n' if len(calls) == 1 else 'good\n')
                return 'done'
        with Authority(project) as owner:
            engine = self.start(owner, 'hook', [{'id': 'one', 'description': 'work', 'owned_paths': ['owned.txt']}], Worker)
            with graph_saver(owner) as saver:
                result = task_graph(engine, saver).invoke({}, {'configurable': {'thread_id': 'hook'}}, durability='sync')
            self.assertIn('one', result['checkpoints'])
        self.assertEqual(len(calls), 2)
        self.assertIn('checkpoint_error', calls[1])
        self.assertEqual(git(project, 'show', 'HEAD:owned.txt'), b'good\n')
        self.assertEqual(git(project, 'rev-list', '--count', self.base + '..HEAD'), b'1\n')

    def test_resumed_pending_correction_retains_authority(self):
        project, calls = self.project, []
        class Worker:
            def __init__(self, *args, **kwargs):
                self.saved_session = {'id': 'resume', 'file': str(project/'session')}
            def prompt(self, prompt, **kwargs):
                calls.append(prompt)
                kwargs['claim']('owned.txt')
                (project/'owned.txt').write_text('bad\n' if len(calls) == 1 else 'good\n')
                return 'done'
        task = {'id': 'one', 'description': 'work', 'owned_paths': ['owned.txt'],
                'checks': [['python3', '-B', '-c', "from pathlib import Path; assert Path('owned.txt').read_text() == 'good\\n'"]]}
        with Authority(project) as owner:
            engine = self.start(owner, 'resume', [task], Worker)
            original = owner.store.reserve_worker_dispatch
            def interrupted(run, task_id, invocation_id, session, **kwargs):
                if len(calls) == 1:
                    raise OSError('interrupted before correction reservation')
                return original(run, task_id, invocation_id, session, **kwargs)
            config = {'configurable': {'thread_id': 'resume'}}
            with graph_saver(owner) as saver:
                with patch.object(owner.store, 'reserve_worker_dispatch', side_effect=interrupted):
                    with self.assertRaisesRegex(OSError, 'interrupted before correction reservation'):
                        task_graph(engine, saver).invoke({}, config, durability='sync')
            with graph_saver(owner) as saver:
                result = task_graph(engine, saver).invoke(None, config, durability='sync')
            self.assertIn('one', result['checkpoints'])
        self.assertEqual(len(calls), 2)
        self.assertIn('Current execution authority', calls[1])
        self.assertIn('small isolated tests and local test databases', calls[1].lower())
        self.assertIn('save-adr', calls[1])
        self.assertIn('manual gate', calls[1].lower())

    def test_lost_result_stops_before_redispatch(self):
        project, calls = self.project, []
        class Worker:
            def __init__(self, *args, **kwargs):
                self.saved_session = {'id': 'uncertain', 'file': str(project/'session')}
            def prompt(self, prompt, **kwargs):
                calls.append(prompt)
                return 'done'
        with Authority(project) as owner:
            engine = self.start(owner, 'uncertain', [{'id': 'one', 'description': 'work'}], Worker)
            original = owner.store.history
            def lost(run, task, kind, state, details=None, **kwargs):
                if kind == 'worker_invocation' and state == 'returned':
                    raise OSError('result persistence failed')
                return original(run, task, kind, state, details, **kwargs)
            config = {'configurable': {'thread_id': 'uncertain'}}
            with graph_saver(owner) as saver:
                graph = task_graph(engine, saver)
                with patch.object(owner.store, 'history', side_effect=lost):
                    with self.assertRaisesRegex(OSError, 'result persistence failed'):
                        graph.invoke({}, config, durability='sync')
                with self.assertRaisesRegex(Blocked, 'uncertain or unsuccessful'):
                    graph.invoke(None, config, durability='sync')
            self.assertFalse(owner.store.completed_checkpoints('uncertain'))
        self.assertEqual(len(calls), 1)

    def test_checkpoint_commit_reconciled_after_lost_history(self):
        project, calls = self.project, []
        class Worker:
            def __init__(self, *args, **kwargs):
                self.saved_session = {'id': 'git', 'file': str(project/'session')}
            def prompt(self, prompt, **kwargs):
                calls.append(prompt)
                kwargs['claim']('owned.txt')
                (project/'owned.txt').write_text('committed\n')
                return 'done'
        with Authority(project) as owner:
            engine = self.start(owner, 'git-crash', [{'id': 'one', 'description': 'work', 'owned_paths': ['owned.txt']}], Worker)
            original = owner.store.history
            def lost(run, task, kind, state, details=None, **kwargs):
                if kind == 'checkpoint' and state == 'passed':
                    raise OSError('lost checkpoint result')
                return original(run, task, kind, state, details, **kwargs)
            config = {'configurable': {'thread_id': 'git-crash'}}
            with graph_saver(owner) as saver:
                with patch.object(owner.store, 'history', side_effect=lost):
                    with self.assertRaisesRegex(OSError, 'lost checkpoint result'):
                        task_graph(engine, saver).invoke({}, config, durability='sync')
            with graph_saver(owner) as saver:
                result = task_graph(engine, saver).invoke(None, config, durability='sync')
            self.assertIn('one', result['checkpoints'])
        self.assertEqual(len(calls), 1)
        self.assertEqual(git(project, 'rev-list', '--count', self.base + '..HEAD'), b'1\n')

    def test_manual_gate_denial_prevents_dispatch(self):
        calls = []
        class Worker:
            def __init__(self, *args, **kwargs):
                calls.append('opened')
        with Authority(self.project) as owner:
            engine = self.start(owner, 'gate', [{'id': 'one', 'description': 'work', 'gates': ['Owner gate']}], Worker)
            engine.question = lambda text: 'no'
            with graph_saver(owner) as saver:
                with self.assertRaisesRegex(Blocked, 'manual gate not approved'):
                    task_graph(engine, saver).invoke({}, {'configurable': {'thread_id': 'gate'}}, durability='sync')
        self.assertEqual(calls, [])

    def test_uncertain_or_unsuccessful_worker_never_redispatched(self):
        project, calls = self.project, []
        class Worker:
            def __init__(self, *args, **kwargs):
                self.saved_session = {'id': 'failed', 'file': str(project/'session')}
            def prompt(self, prompt, **kwargs):
                calls.append(prompt)
                return TaskOutcome('incomplete', 'unfinished')
        with Authority(project) as owner:
            engine = self.start(owner, 'failed', [{'id': 'one', 'description': 'work'}], Worker)
            config = {'configurable': {'thread_id': 'failed'}}
            with graph_saver(owner) as saver:
                graph = task_graph(engine, saver)
                with self.assertRaises(Blocked):
                    graph.invoke({}, config, durability='sync')
                with self.assertRaisesRegex(Blocked, 'uncertain or unsuccessful'):
                    graph.invoke(None, config, durability='sync')
            self.assertFalse(owner.store.completed_checkpoints('failed'))
        self.assertEqual(len(calls), 1)
