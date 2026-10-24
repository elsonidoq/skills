"""Offline subprocess checks for deterministic project-local executor resolution."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / 'scripts/resolve-workflow-executor.py'
PROFILE = {'provider': 'fixture', 'model': 'selected-model', 'effort': 'medium'}


class ExecutorResolutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'
        self.project.mkdir()

    def write_config(self, path, value=PROFILE):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))
        return path

    def resolve(self, *args):
        # Deliberately run outside the project: overrides must not use cwd.
        return subprocess.run([sys.executable, str(SCRIPT), '--project', str(self.project), *args],
                              cwd=self.root, capture_output=True, text=True)

    def assert_success(self, result, path):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, str(path.resolve()) + '\n')
        self.assertEqual(result.stderr, '')

    def assert_failure(self, result, path):
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        self.assertIn(str(path.resolve()), result.stderr)
        self.assertIn('--executor PATH', result.stderr)
        self.assertIn('No fallback was attempted', result.stderr)

    def test_default_and_clean_stdout(self):
        path = self.write_config(self.project / '.pi/workflow-executor.json')
        self.assert_success(self.resolve(), path)

    def test_absolute_and_project_relative_overrides(self):
        self.write_config(self.project / '.pi/workflow-executor.json', {})
        path = self.write_config(self.project / 'config/selected.json',
                                 dict(PROFILE, reviewer=dict(PROFILE, model='selected-reviewer')))
        for override in (str(path), 'config/selected.json'):
            with self.subTest(override=override):
                self.assert_success(self.resolve('--executor', override), path)

    def test_missing_default_does_not_use_neighbor_or_cwd(self):
        self.write_config(self.root / 'neighbor/.pi/workflow-executor.json')
        self.write_config(self.root / '.pi/workflow-executor.json')
        self.assert_failure(self.resolve(), self.project / '.pi/workflow-executor.json')

    def test_missing_override_does_not_use_valid_default(self):
        self.write_config(self.project / '.pi/workflow-executor.json')
        self.assert_failure(self.resolve('--executor', 'missing.json'), self.project / 'missing.json')

    def test_malformed_json(self):
        self.write_config(self.project / '.pi/workflow-executor.json')
        path = self.project / 'broken.json'
        path.write_text('{')
        self.assert_failure(self.resolve('--executor', str(path)), path)

    def test_invalid_fields(self):
        self.write_config(self.project / '.pi/workflow-executor.json')
        invalid = [[], {}, dict(PROFILE, model=''), dict(PROFILE, effort=3),
                   dict(PROFILE, reviewer=None), dict(PROFILE, reviewer={}),
                   dict(PROFILE, reviewer=dict(PROFILE, provider=False))]
        for value in invalid:
            with self.subTest(value=value):
                path = self.write_config(self.project / 'invalid.json', value)
                self.assert_failure(self.resolve('--executor', str(path)), path)

    def test_unreadable_file_operation(self):
        # A directory reliably fails read_text, even when tests run as root.
        self.assert_failure(self.resolve('--executor', '.'), self.project)

    def test_help_and_required_project(self):
        result = subprocess.run([sys.executable, str(SCRIPT), '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('--project', result.stdout)
        self.assertIn('--executor', result.stdout)
        self.assertEqual(result.stderr, '')
        result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
