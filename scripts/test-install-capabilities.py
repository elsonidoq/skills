#!/usr/bin/env python3
"""Exercise installer package reporting without installing or contacting providers."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class InstallerCapabilitiesTest(unittest.TestCase):
    def test_package_registration_is_version_independent_and_never_installs(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            suite = tmp / 'suite'
            (suite / 'scripts').mkdir(parents=True)
            for name in ('install.sh', 'install-links.py'):
                shutil.copy(ROOT / 'scripts' / name, suite / 'scripts' / name)
            lint = suite / 'scripts/check-skills-lint.sh'
            lint.write_text('#!/bin/sh\nexit 0\n')
            lint.chmod(0o755)
            (suite / 'skills/example').mkdir(parents=True)
            (suite / 'skills/example/SKILL.md').write_text('example')
            (suite / 'docs').mkdir()
            (suite / 'docs/best_practices_spec_driven_development.md').write_text('example')
            (suite / 'roles').mkdir()
            for role in ('coherence-producer', 'coherence-reviewer'):
                shutil.copy(ROOT / 'roles' / f'{role}.md', suite / 'roles' / f'{role}.md')
            bindir = tmp / 'bin'
            bindir.mkdir()
            pi = bindir / 'pi'
            pi.write_text('#!/bin/sh\ncase "$1" in --version) echo test;; list) printf "%s\\n" "$PACKAGES";; *) echo "unexpected pi operation: $1" >&2; exit 2;; esac\n')
            pi.chmod(0o755)
            env = dict(os.environ, HOME=str(tmp / 'home'), PATH=f'{bindir}:{os.environ["PATH"]}',
                       PI_CODING_AGENT_DIR=str(tmp / 'agent'))
            for packages in ('npm:pi-subagents@9.8.7\nnpm:pi-ask-user@1.2.3', ''):
                result = subprocess.run(['bash', str(suite / 'scripts/install.sh')], env={**env, 'PACKAGES': packages}, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn('unexpected pi operation', result.stderr)
                for role in ('coherence-producer', 'coherence-reviewer'):
                    installed = tmp / 'home/.agents' / f'{role}.md'
                    self.assertTrue(installed.is_symlink())
                    self.assertEqual(installed.resolve(), suite / 'roles' / f'{role}.md')
                self.assertIn('No project role activation is required', result.stdout)
                self.assertIn('fresh-session handoff', result.stdout)
                self.assertNotIn('/reload', result.stdout)
                if packages:
                    self.assertIn('package registration found: pi-subagents', result.stdout)
                    self.assertIn('package registration found: pi-ask-user', result.stdout)
                else:
                    self.assertIn('package registration not found: pi-subagents', result.stderr)
                    self.assertIn('no automatic installation', result.stderr)


if __name__ == '__main__':
    unittest.main()
