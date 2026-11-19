import contextlib
import io
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from coherence_workflow import status_cli

RUNTIME = Path(__file__).resolve().parents[1]


class StatusCliTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.repo, self.linked, self.outside = (root / name for name in ('main', 'linked worktree', 'outside'))
        self.outside.mkdir()
        self.env = dict(os.environ, PYTHONPATH=str(RUNTIME), XDG_CONFIG_HOME=str(root / 'config'))
        self.git('init', '-q', str(self.repo))
        self.git('-C', str(self.repo), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture', '--allow-empty')
        self.git('-C', str(self.repo), 'worktree', 'add', '-q', '--detach', str(self.linked))
        self.config = root / 'config/coherence/status-projects'
        self.config.parent.mkdir(parents=True)
        self.config.write_text(f'# Registered checkouts\n{self.repo}\n{self.linked}\n')
        self.database = self.create_store(self.linked)

    def git(self, *args):
        subprocess.run(['git', *args], cwd=self.outside, env=self.env, check=True, capture_output=True)

    def create_store(self, project):
        path = project / '.coherence/workflow/workflow.sqlite'
        path.parent.mkdir(parents=True)
        with contextlib.closing(sqlite3.connect(path)) as db, db:
            db.executescript('''
                CREATE TABLE execution_runs (run_id, state, baseline, result, error);
                CREATE TABLE execution_tasks (run_id, task_id, state, baseline, result, details);
                INSERT INTO execution_runs VALUES ('named-run', 'running', NULL, NULL, NULL);
                INSERT INTO execution_tasks VALUES ('named-run', 'T001', 'complete', NULL, NULL, NULL);
                INSERT INTO execution_tasks VALUES ('named-run', 'T002', 'running', NULL, NULL, NULL);
            ''')
        return path

    def run_status(self, *args):
        return subprocess.run([sys.executable, '-B', '-m', 'coherence_workflow.status_cli', *args],
                              cwd=self.outside, env=self.env, text=True, capture_output=True)

    def test_run_from_outside_repo_finds_linked_worktree_once(self):
        before = self.database.read_bytes()
        result = self.run_status('named-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, f'Worktree: {self.linked}\nnamed-run: running\n  T001\tcomplete\n  T002\trunning\n')
        self.assertEqual(self.database.read_bytes(), before)
        self.assertFalse((self.repo / '.coherence').exists())

    def test_ambiguous_run_lists_worktrees_explicit_project_bypasses_config(self):
        self.create_store(self.repo)
        result = self.run_status('named-run')
        self.assertEqual(result.returncode, 1)
        self.assertIn('matches multiple worktrees; pass --project', result.stderr)
        self.assertIn(str(self.repo), result.stderr)
        self.assertIn(str(self.linked), result.stderr)
        self.config.unlink()
        result = self.run_status('named-run', '--project', str(self.linked))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'Worktree: {self.linked}', result.stdout)

    def test_project_rejects_database_outside_registered_worktree_root(self):
        for project in (self.outside, self.repo / 'subdirectory'):
            with self.subTest(project=project):
                self.create_store(project)
                result = self.run_status('named-run', '--project', str(project))
                self.assertEqual(result.returncode, 1)
                self.assertIn('registered Git worktree root', result.stderr)
                self.assertEqual(result.stdout, '')

    def test_stale_nested_worktree_is_not_a_status_source(self):
        self.git('-C', str(self.repo), 'worktree', 'lock', str(self.linked))
        for state in ('unlocked', 'locked'):
            with self.subTest(state=state):
                nested = self.repo / f'stale {state} worktree'
                self.git('-C', str(self.repo), 'worktree', 'add', '-q', '--detach', str(nested))
                if state == 'locked':
                    self.git('-C', str(self.repo), 'worktree', 'lock', str(nested))
                (nested / '.git').unlink()
                self.create_store(nested)
                result = self.run_status('named-run', '--project', str(nested))
                self.assertEqual(result.returncode, 1)
                self.assertIn('registered Git worktree root', result.stderr)
        result = self.run_status('named-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'Worktree: {self.linked}', result.stdout)

    def test_relative_xdg_config_uses_home_default(self):
        home = self.config.parents[2] / 'home'
        home_config = home / '.config/coherence/status-projects'
        home_config.parent.mkdir(parents=True)
        self.config.rename(home_config)
        relative_config = self.outside / 'config/coherence/status-projects'
        relative_config.parent.mkdir(parents=True)
        relative_config.write_text('invalid-relative-checkout\n')
        self.env.update(HOME=str(home), XDG_CONFIG_HOME='config')
        result = self.run_status('named-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'Worktree: {self.linked}', result.stdout)

    def test_missing_run_and_config_are_actionable(self):
        result = self.run_status('missing-run')
        self.assertEqual(result.returncode, 1)
        self.assertIn('not found in configured worktrees', result.stderr)
        self.config.unlink()
        result = self.run_status('named-run')
        self.assertEqual(result.returncode, 1)
        self.assertIn(str(self.config), result.stderr)
        self.assertIn('--project PATH', result.stderr)

    def test_watch_reloads_state_and_stops_on_interrupt(self):
        def update(seconds):
            self.assertEqual(seconds, 5)
            if sleep.call_count == 1:
                with contextlib.closing(sqlite3.connect(self.database)) as db, db:
                    db.execute("UPDATE execution_runs SET state='complete'")
                    db.execute("UPDATE execution_tasks SET state='complete'")
            elif sleep.call_count == 3:
                raise KeyboardInterrupt

        output = io.StringIO()
        with patch.object(status_cli.time, 'sleep', side_effect=update) as sleep, contextlib.redirect_stdout(output):
            result = status_cli.main(['named-run', '--project', str(self.linked), '--watch'])
        self.assertEqual(result, 0)
        self.assertIn('named-run: running', output.getvalue())
        self.assertEqual(output.getvalue().count('named-run: complete'), 1)
        self.assertIn('  T002\tcomplete', output.getvalue())
