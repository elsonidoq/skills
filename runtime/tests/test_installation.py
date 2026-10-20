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
        for path in config['tool']['setuptools']['data-files']['share/coherence-workflow/pi-host']:
            self.assertTrue((ROOT/'runtime'/path).is_file())
        self.assertEqual(config['project']['scripts']['coordinate-implementation'], 'coherence_workflow.cli:main')

    def test_actual_entry_help_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory(prefix='coherence-simplification-03-help-') as directory:
            result = subprocess.run([str(ROOT/'scripts/coordinate-implementation'), '--help'], cwd=directory,
                                    env=dict(os.environ, COHERENCE_PYTHON=sys.executable), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('start', result.stdout)
        self.assertNotIn('manifest', result.stdout)
