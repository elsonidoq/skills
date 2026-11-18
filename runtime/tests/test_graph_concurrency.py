"""Production storage primitives for directed graph execution."""
import threading
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
import unittest
from concurrent.futures import ThreadPoolExecutor

from coherence_workflow.graph import _ready_wave, graph_saver, task_graph
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.pi_adapter import PiAdapter
from coherence_workflow.store import Blocked, git
from coherence_workflow.store import Authority
from fixtures.support import ProjectTest


class WaveSelectionTests(unittest.TestCase):
    def test_overlap_outputs_and_unknown_ownership_are_serialized(self):
        tasks = [
            {'id': 'A', 'owned_paths': ['src/a'], 'generated_outputs': ['build/shared']},
            {'id': 'B', 'owned_paths': ['src/b'], 'generated_outputs': ['build/shared/file']},
            {'id': 'C', 'owned_paths': ['src/c']},
            {'id': 'D'},
            {'id': 'E', 'owned_paths': ['src/a/child']},
        ]
        self.assertEqual([task['id'] for task in _ready_wave(tasks)], ['A', 'C'])
        self.assertEqual([task['id'] for task in _ready_wave([tasks[3], tasks[2]])], ['D'])
        self.assertEqual([task['id'] for task in _ready_wave([{'id': 'unsafe', 'owned_paths': ['/tmp']}, tasks[2]])], ['unsafe'])


class ConcurrentStoreTests(ProjectTest):
    def test_thread_owned_connections_release_transactions_before_wait(self):
        with Authority(self.project) as authority:
            store = authority.store
            store.start('threads', self.base)
            barrier = threading.Barrier(2)
            connections = []

            def worker(task):
                with store.thread_connection() as db:
                    connections.append(db)
                    store.history('threads', task, 'fixture', 'started')
                    self.assertFalse(db.in_transaction)
                    barrier.wait(timeout=5)
                    store.history('threads', task, 'fixture', 'returned')
                    self.assertFalse(db.in_transaction)

            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(worker, task) for task in ('A', 'B')]
                for future in futures:
                    future.result()
            self.assertIsNot(connections[0], connections[1])
            rows = store.db.execute("SELECT task_id,state FROM execution_history WHERE run_id='threads' AND kind='fixture'").fetchall()
            self.assertEqual({(row['task_id'], row['state']) for row in rows},
                             {(task, state) for task in ('A', 'B') for state in ('started', 'returned')})


EXECUTOR = {'provider': 'openai', 'model': 'gpt-4o-mini', 'effort': 'off',
            'reviewer': {'provider': 'openai', 'model': 'gpt-4o-mini', 'effort': 'off'}}


class ProductionWaveTests(ProjectTest):
    def environment(self, *, barrier=False, fail=''):
        # These subprocesses own isolated runs, not the invoking agent's bridge.
        environment = dict(os.environ)
        for name in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                     'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN'):
            environment.pop(name, None)
        return {**environment, 'PYTHONDONTWRITEBYTECODE': '1',
                'PYTHONPATH': str(Path(__file__).resolve().parents[1]),
                'COHERENCE_HOST_PRELOAD': '1',
                'NODE_OPTIONS': '--import=' + str(Path(__file__).parent/'fixtures/steering_adapter_fixture.mjs'),
                'COHERENCE_STEERING_CALLBACK': 'graph-parallel',
                'PI_CODING_AGENT_DIR': str(self.root/'private-agent'),
                'COHERENCE_WAVE_EVENTS': str(self.root/'events'),
                'COHERENCE_WAVE_BARRIER': '1' if barrier else '0', 'COHERENCE_WAVE_FAIL': fail}

    def tasks(self):
        events = str(self.root/'events')
        # Shared acceptance and Git hooks see all siblings settled, never half a wave.
        check = ['python3', '-B', '-c',
                 f"from pathlib import Path; s=Path({events!r}).read_text(); "
                 "assert all(('finish '+x+'\\n') in s or ('failed '+x+'\\n') in s for x in ('A','B')); "
                 f"Path({events!r}).open('a').write('check\\n')"]
        return [{'id': 'C', 'description': 'accepted join', 'depends': ['A', 'B'], 'owned_paths': ['c.txt']},
                {'id': 'A', 'description': 'first fixture', 'owned_paths': ['a.txt'], 'checks': [check]},
                {'id': 'B', 'description': 'second fixture', 'owned_paths': ['b.txt'], 'checks': [check]}]

    def cli(self, *args, env):
        result = subprocess.run([sys.executable, '-B', '-m', 'coherence_workflow.cli', *args,
                                 '--project', str(self.project)], env=env, capture_output=True, text=True)
        self.assertTrue(result.stdout.strip(), result.stderr)
        return result, json.loads(result.stdout.splitlines()[-1])

    def inputs(self):
        tasks, executor = self.root/'tasks.json', self.root/'executor.json'
        tasks.write_text(json.dumps(self.tasks()))
        executor.write_text(json.dumps(EXECUTOR))
        (self.project/'other.txt').write_text('unrelated staged bytes\n')
        git(self.project, 'add', '--', 'other.txt')
        self.staged = git(self.project, 'diff', '--cached', '--binary')
        # This hook is part of temporary test Git only, never production policy.
        hook = self.project/'.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\n' + 'python3 -B -c ' + __import__('shlex').quote(
            f"from pathlib import Path; p=Path({str(self.root/'events')!r}); s=p.read_text(); "
            "assert all('finish '+x+'\\n' in s or 'failed '+x+'\\n' in s for x in ('A','B')); "
            "p.open('a').write('git\\n')") + '\n')
        hook.chmod(0o700)
        return ['--tasks', str(tasks), '--executor', str(executor), '--run', 'wave']

    def assert_checkpoints(self):
        self.assertEqual(git(self.project, 'diff', '--cached', '--binary'), self.staged)
        commits = git(self.project, 'rev-list', '--reverse', self.base+'..HEAD').decode().splitlines()
        changed = [git(self.project, 'diff-tree', '--no-commit-id', '--name-only', '-r', sha).decode().splitlines()
                   for sha in commits]
        self.assertEqual(changed, [['a.txt'], ['b.txt'], ['c.txt']])
        return commits

    def test_public_cli_directed_sdk_overlap_and_accepted_join(self):
        args = self.inputs()
        env = self.environment(barrier=True)
        result, output = self.cli('start', *args, '--parallel', env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(output['status'], 'complete')
        commits = self.assert_checkpoints()
        history_result, history = self.cli('history', '--run', 'wave', env=env)
        self.assertEqual(history_result.returncode, 0, history_result.stderr)
        self.assertEqual(history['run']['state'], 'complete')
        events = (self.root/'events').read_text().splitlines()
        self.assertEqual(set(events[:2]), {'start A', 'start B'})
        self.assertLess(events.index('finish A'), events.index('check'))
        self.assertLess(events.index('finish B'), events.index('check'))
        self.assertEqual(events[:events.index('start C')].count('git'), 2)
        with Authority(self.project) as owner:
            self.assertTrue(owner.store.input('wave')['authority']['parallel'])
            checkpoints = owner.store.completed_checkpoints('wave')
            self.assertEqual(set(checkpoints), {'A', 'B', 'C'})
            sessions = [json.loads(row['details'])['session']['id'] for row in owner.store.db.execute(
                "SELECT details FROM execution_history WHERE kind='worker_dispatch' AND state='bound'")]
            self.assertEqual(len(sessions), len(set(sessions)))
        print('T013 FIXTURE-ONLY CLI/GIT EVIDENCE ' + json.dumps({'command': 'start --parallel; history',
              'events': events, 'focused_commits': commits, 'changed_paths': [['a.txt'], ['b.txt'], ['c.txt']],
              'result': output['status'], 'history_state': history['run']['state'],
              'accepted_join': checkpoints['C'], 'unrelated_index': 'unchanged'}))

    def test_public_default_sequential(self):
        args = self.inputs()
        # Sequential checks must not expect the second worker before it starts.
        tasks = self.tasks()
        for task in tasks:
            task.pop('checks', None)
        (self.root/'tasks.json').write_text(json.dumps(tasks))
        (self.project/'.git/hooks/pre-commit').unlink()
        result, output = self.cli('start', *args, env=self.environment())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(output['status'], 'complete')
        self.assertEqual((self.root/'events').read_text().splitlines(),
                         ['start A', 'finish A', 'start B', 'finish B', 'start C', 'finish C'])
        self.assert_checkpoints()

    def test_production_path_overlap_and_shared_outputs_do_not_fan_out(self):
        for shared_output in (False, True):
            with self.subTest(shared_output=shared_output):
                (self.root/'events').write_text('')
                tasks = [{'id': 'A', 'description': 'first', 'owned_paths': ['left.txt' if shared_output else 'shared.txt']},
                         {'id': 'B', 'description': 'second', 'owned_paths': ['right.txt' if shared_output else 'shared.txt']}]
                if shared_output:
                    for task in tasks:
                        task['generated_outputs'] = ['build/shared']
                contract = admit(tasks)
                run = 'overlap-' + str(shared_output)
                with patch.dict(os.environ, self.environment()), Authority(self.project) as owner:
                    owner.store.start(run, git(self.project, 'rev-parse', 'HEAD').decode().strip(),
                                      contract=contract, executor=EXECUTOR)
                    engine = Engine(owner, run, contract, EXECUTOR, parallel=True, paid_scope={'apis': []})
                    with graph_saver(owner) as saver:
                        task_graph(engine, saver).invoke({}, {'configurable': {'thread_id': run}}, durability='sync')
                self.assertEqual((self.root/'events').read_text().splitlines(),
                                 ['start A', 'finish A', 'start B', 'finish B'])

    def test_settled_wave_source_and_head_drift_stop_without_provider_replay(self):
        for drift in ('source', 'head'):
            with self.subTest(drift=drift):
                (self.root/'events').write_text('')
                contract = admit(self.tasks())
                run = 'drift-' + drift
                with patch.dict(os.environ, self.environment(barrier=True)), Authority(self.project) as owner:
                    owner.store.start(run, git(self.project, 'rev-parse', 'HEAD').decode().strip(),
                                      contract=contract, executor=EXECUTOR)
                    connections = []
                    case = self
                    class ObservedAdapter(PiAdapter):
                        def prompt(self, *args, **kwargs):
                            connection = owner.store.db
                            connections.append(connection)
                            case.assertFalse(connection.in_transaction)
                            try:
                                return super().prompt(*args, **kwargs)
                            finally:
                                case.assertFalse(connection.in_transaction)
                    engine = Engine(owner, run, contract, EXECUTOR, adapter=ObservedAdapter,
                                    parallel=True, paid_scope={'apis': []})
                    config = {'configurable': {'thread_id': run}}
                    with graph_saver(owner) as saver:
                        graph = task_graph(engine, saver)
                        with patch('coherence_workflow.graph.run_checks', side_effect=Blocked('fixture stop after wave settlement')):
                            with self.assertRaisesRegex(Blocked, 'fixture stop'):
                                graph.invoke({}, config, durability='sync')
                        before = (self.root/'events').read_text()
                        if drift == 'source':
                            (self.project/'a.txt').write_text('unauthorized drift\n')
                        else:
                            (self.project/'drift.txt').write_text('unexpected target\n')
                            git(self.project, 'add', '--', 'drift.txt')
                            git(self.project, 'commit', '-qm', 'unrelated target drift')
                        with self.assertRaisesRegex(Blocked, 'effects changed'):
                            graph.invoke(None, config, durability='sync')
                        self.assertEqual((self.root/'events').read_text(), before)
                        self.assertEqual(owner.store.completed_checkpoints(run), {})
                        self.assertEqual(len(connections), 2)
                        self.assertIsNot(connections[0], connections[1])
                # Restore only these test-owned files for the next subcase.
                for name in ('a.txt', 'b.txt'):
                    (self.project/name).unlink()

    def test_failed_wave_reopen_retains_success_and_focused_commits(self):
        args = self.inputs()
        env = self.environment(barrier=True, fail='A')
        result, output = self.cli('start', *args, '--parallel', env=env)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(output['status'], 'failed')
        self.assertEqual(git(self.project, 'show', 'HEAD:b.txt'), b'fixture B\n')
        self.assertFalse((self.project/'c.txt').exists())
        b_sha = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        env = self.environment()
        result, output = self.cli('resume', '--run', 'wave', '--recovery-action', 'continue',
                                 '--diagnosis', 'Inspected explicit fixture outcome; continue A retained context without failure injection', env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(output['status'], 'complete')
        events = (self.root/'events').read_text().splitlines()
        self.assertEqual(events.count('start A'), 1)
        self.assertEqual(events.count('start B'), 1)
        self.assertEqual(events.count('finish B'), 1)
        self.assertEqual(git(self.project, 'diff', '--cached', '--binary'), self.staged)
        commits = git(self.project, 'rev-list', '--reverse', self.base+'..HEAD').decode().splitlines()
        self.assertEqual(commits[0], b_sha)
        self.assertEqual([git(self.project, 'diff-tree', '--no-commit-id', '--name-only', '-r', sha).decode().strip()
                          for sha in commits], ['b.txt', 'a.txt', 'c.txt'])


if __name__ == '__main__':
    unittest.main()
