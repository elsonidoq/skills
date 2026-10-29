"""Portable packaging and entry inspection; no installation or global changes."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[2]


class PackagingTests(unittest.TestCase):
    def test_only_live_product_resources_packaged(self):
        config = tomllib.loads((ROOT/'runtime/pyproject.toml').read_text())
        self.assertEqual(config['project']['dependencies'], ['PyYAML==6.0.3'])
        self.assertEqual(config['tool']['setuptools']['package-data']['coherence_workflow'], ['schemas/*.json'])
        host_files = config['tool']['setuptools']['data-files']['share/coherence-workflow/pi-host']
        self.assertIn('pi-host/sdk-resolution.mjs', host_files)
        for path in host_files:
            self.assertTrue((ROOT/'runtime'/path).is_file())
        self.assertEqual(config['project']['scripts']['coordinate-implementation'], 'coherence_workflow.cli:main')

    def test_global_install_preserves_foreign_command_before_creating_prefix(self):
        with tempfile.TemporaryDirectory(prefix='coherence-global-conflict-') as directory:
            home = Path(directory)
            command = home / '.local/bin/coordinate-implementation'
            command.parent.mkdir(parents=True)
            command.write_text('foreign command\n')
            prefix = home / 'runtime'
            result = subprocess.run([str(ROOT/'scripts/install-workflow.sh'), '--prefix', str(prefix),
                                     '--allow-network', '--global'],
                                    env=dict(os.environ, HOME=str(home), PI_CODING_AGENT_DIR=str(home/'agent')),
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('existing/foreign destination preserved', result.stderr)
            self.assertEqual(command.read_text(), 'foreign command\n')
            self.assertFalse(prefix.exists(), 'conflicts must stop before downloads or installation')

    def test_actual_entry_help_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory(prefix='coherence-simplification-03-help-') as directory:
            result = subprocess.run([str(ROOT/'scripts/coordinate-implementation'), '--help'], cwd=directory,
                                    env=dict(os.environ, COHERENCE_PYTHON=sys.executable), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('start', result.stdout)
        self.assertNotIn('manifest', result.stdout)
