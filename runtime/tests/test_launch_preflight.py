"""Launch preflight, executor drift and baseline checks; offline, no provider requests."""
import contextlib
import io
import json
import os
import sys
from unittest.mock import patch

from coherence_workflow.cli import main, status
from coherence_workflow.store import Authority, Blocked
from fixtures.support import ProjectTest


PROFILE = {'provider': 'fixture-bridge', 'model': 'fixture-model', 'effort': 'medium'}
NO_BRIDGE = {key: '' for key in ('COHERENCE_PARENT_BRIDGE_SOCKET', 'COHERENCE_PARENT_BRIDGE_TOKEN',
                                  'COHERENCE_PARENT_BRIDGE_SESSION', 'COHERENCE_PARENT_BRIDGE_RUN')}
# Registers an offline provider only; the provider must never be called.
EXTENSION = """export default function (pi) {
  pi.registerProvider('fixture-bridge', {baseUrl: 'fixture', apiKey: 'not-used', api: 'fixture-bridge',
    models: [{id: 'fixture-model', name: 'Fixture', reasoning: true, input: ['text'],
      cost: {input: 0, output: 0, cacheRead: 0, cacheWrite: 0}, contextWindow: 100000, maxTokens: 1000}],
    streamSimple: () => { throw new Error('fixture provider must not be called'); }});
}
"""


class LaunchPreflightTests(ProjectTest):
    def setUp(self):
        super().setUp()
        self.extension = self.root / 'fixture-provider.mjs'
        self.extension.write_text(EXTENSION)
        self.tasks = self.root / 'tasks.json'
        self.tasks.write_text(json.dumps([{'id': 'one', 'description': 'scoped work', 'owned_paths': ['owned.txt']}]))
        self.executor = self.root / 'executor.json'

    def start(self, executor, run='run'):
        self.executor.write_text(json.dumps(executor))
        with patch.dict(os.environ, NO_BRIDGE), contextlib.redirect_stdout(io.StringIO()) as out, \
                contextlib.redirect_stderr(io.StringIO()) as err:
            code = main(['start', '--project', str(self.project), '--tasks', str(self.tasks),
                         '--executor', str(self.executor), '--run', run])
        return code, out.getvalue(), err.getvalue()

    def assert_no_run_state(self):
        self.assertFalse((self.project / '.coherence/workflow/workflow.sqlite').exists())

    def test_missing_extension_or_model_stops_start_before_run_state(self):
        listed = {**PROFILE, 'extensions': [str(self.extension)]}
        cases = {
            'missing extension': ({**PROFILE, 'reviewer': listed}, 'worker: .*Provider fixture-bridge is not registered'
                                  '.*add the extension that registers it to this profile\'s \\\\"extensions\\\\" list'),
            'missing model': ({**listed, 'reviewer': listed, 'implementation_fallback': {**listed, 'model': 'absent'}},
                              'implementation_fallback: .*Model absent is not in provider fixture-bridge\'s catalog'
                              ' \\(Pi SDK [^ ]+ at [^;]+; available: fixture-model\\)'),
        }
        for case, (executor, pattern) in cases.items():
            with self.subTest(case=case):
                code, out, _err = self.start(executor)
                self.assertEqual(code, 2, out)
                self.assertRegex(out, 'executor preflight failed; no run state was created')
                self.assertRegex(out, pattern)
                self.assert_no_run_state()

    def test_malformed_fallback_is_named_before_preflight(self):
        listed = {**PROFILE, 'extensions': [str(self.extension)]}
        with patch('coherence_workflow.cli.PiAdapter.preflight', side_effect=AssertionError('preflight ran')):
            code, out, _err = self.start({**listed, 'reviewer': listed, 'implementation_fallback': {'provider': 'p'}})
        self.assertEqual(code, 2, out)
        self.assertIn('implementation_fallback needs provider, model and effort strings', out)
        self.assert_no_run_state()

    def test_resolved_sdk_is_recorded_and_reported_in_status(self):
        listed = {**PROFILE, 'extensions': [str(self.extension)]}

        def stop(*_args, **_kwargs):
            raise Blocked('controlled offline stop before worker')
        with patch('coherence_workflow.graph.task_graph', side_effect=stop):
            code, out, err = self.start({**listed, 'reviewer': listed})
        self.assertEqual(code, 2, out)
        self.assertIn('controlled offline stop before worker', out)
        result = status(self.project, 'run')
        self.assertTrue(os.path.isdir(result['sdk']['package_dir']), result['sdk'])
        self.assertIsInstance(result['sdk']['version'], str)
        self.assertIn('Pi SDK ' + result['sdk']['version'] + ' at ' + result['sdk']['package_dir'], err)
        launch = [item for item in result['history'] if item['kind'] == 'launch_environment']
        self.assertEqual(launch[0]['details']['executor_path'], str(self.executor.resolve()))


class ExecutorDriftTests(ProjectTest):
    def test_changed_executor_file_is_reported_and_run_keeps_recorded_executor(self):
        tasks, executor = self.root / 'tasks.json', self.root / 'executor.json'
        tasks.write_text(json.dumps([{'id': 'one', 'description': 'scoped work'}]))
        recorded = {**PROFILE, 'reviewer': PROFILE}
        executor.write_text(json.dumps(recorded))
        seen = []

        def stop(engine, *_args, **_kwargs):
            seen.append(engine.input_executor)
            raise Blocked('controlled offline stop before worker')
        with patch('coherence_workflow.graph.task_graph', side_effect=stop), \
                patch('coherence_workflow.cli.PiAdapter.preflight', return_value=None), \
                patch.dict(os.environ, NO_BRIDGE), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['start', '--project', str(self.project), '--tasks', str(tasks),
                                   '--executor', str(executor), '--run', 'drift']), 2)
            # Unchanged file: no drift report.
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(main(['resume', '--project', str(self.project), '--run', 'drift']), 2)
            self.assertNotIn('Executor drift', err.getvalue())
            executor.write_text(json.dumps({**recorded, 'extensions': ['/fixture/bridge.mjs'],
                                            'reviewer': {**PROFILE, 'model': 'other'}}))
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(main(['resume', '--project', str(self.project), '--run', 'drift']), 2)
        self.assertIn('Executor drift', err.getvalue())
        self.assertEqual(seen, [recorded, recorded, recorded])
        reports = [item['details'] for item in status(self.project, 'drift')['history'] if item['kind'] == 'executor_drift']
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]['changed_fields'], ['extensions', 'reviewer.model'])
        self.assertEqual(reports[0]['executor_path'], str(executor.resolve()))
        self.assertIn('keeps its recorded executor', reports[0]['correction'])
        self.assertIn('start a new run for the remaining tasks', reports[0]['correction'])


class BaselineCheckTests(ProjectTest):
    def test_failing_baseline_check_is_reported_once_without_run_state(self):
        failing = [sys.executable, '-c', 'import sys; print("pre-existing defect"); sys.exit(3)']
        passing = [sys.executable, '-c', 'pass']
        tasks = self.root / 'tasks.json'
        tasks.write_text(json.dumps([
            {'id': 'one', 'description': 'first', 'checks': [failing, passing]},
            {'id': 'two', 'description': 'second', 'checks': [failing]}]))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = main(['baseline-checks', '--project', str(self.project), '--tasks', str(tasks)])
        self.assertEqual(code, 1)
        report = json.loads(out.getvalue())
        self.assertEqual(report['head'], self.base)
        self.assertEqual(report['failed'], 1)
        self.assertEqual([(item['command'], item['tasks'], item['exit_code']) for item in report['checks']],
                         [(failing, ['one', 'two'], 3), (passing, ['one'], 0)])
        self.assertIn('pre-existing defect', report['checks'][0]['output'])
        self.assertFalse((self.project / '.coherence/workflow/workflow.sqlite').exists())

    def test_malformed_argv_is_reported_not_raised(self):
        tasks = self.root / 'tasks.json'
        tasks.write_text(json.dumps([{'id': 'one', 'description': 'first', 'checks': [[sys.executable, 3]]}]))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = main(['baseline-checks', '--project', str(self.project), '--tasks', str(tasks)])
        self.assertEqual(code, 2)
        self.assertIn('argv list of strings', json.loads(out.getvalue())['reason'])
