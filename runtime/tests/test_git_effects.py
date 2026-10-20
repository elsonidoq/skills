"""Real focused commits, dirty preservation, paths, hooks and signing failures."""
import os
from pathlib import Path
from unittest.mock import patch

from coherence_workflow.git_effects import FocusedGit, editable_path
from coherence_workflow.store import Blocked, git
from fixtures.support import ProjectTest


class FocusedCheckpointTests(ProjectTest):
    def focused(self, **context):
        return FocusedGit(self.project, {'id': 'fix', 'description': 'Fix', **context})

    def test_actual_commit_preserves_unrelated_staged_unstaged_untracked(self):
        self.write('other.txt', 'staged\n')
        git(self.project, 'add', '--', 'other.txt')
        self.write('other.txt', 'unstaged\n')
        self.write('unknown.txt', 'untracked\n')
        before_index = git(self.project, 'show', ':other.txt')
        f = self.focused()
        f.claim('owned.txt')
        self.write('owned.txt', 'fixed\n')
        result = f.checkpoint()
        self.assertEqual(result['paths'], ['owned.txt'])
        self.assertNotEqual(result['sha'], self.base)
        self.assertEqual(git(self.project, 'show', ':other.txt'), before_index)
        self.assertEqual((self.project/'other.txt').read_text(), 'unstaged\n')
        self.assertEqual((self.project/'unknown.txt').read_text(), 'untracked\n')
        self.assertEqual(git(self.project, 'show', 'HEAD:STATE.md'), b'custom\n')

    def test_no_change_no_empty_commit(self):
        self.assertTrue(self.focused().checkpoint()['no_change'])
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_command_edits_derive_owned_paths(self):
        f = self.focused()
        f.command('start', 'fixture-command')
        self.write('new.txt', 'new\n')
        f.command('end', 'fixture-command')
        self.assertEqual(f.checkpoint()['paths'], ['new.txt'])

    def test_optional_limits_prevent_out_of_scope_commit(self):
        f = self.focused(owned_paths=['owned.txt'])
        with self.assertRaisesRegex(Blocked, 'outside optional'):
            f.claim('other.txt')
        self.write('other.txt', 'out of scope\n')
        with self.assertRaisesRegex(Blocked, 'unclaimed changes'):
            f.checkpoint()
        self.assertEqual(git(self.project, 'diff', '--cached'), b'')

    def test_dirty_path_never_claimed_or_adopted(self):
        self.write('owned.txt', 'prior work\n')
        f = self.focused()
        with self.assertRaisesRegex(Blocked, 'pre-existing dirty'):
            f.claim('owned.txt')
        self.write('owned.txt', 'changed unknown work\n')
        with self.assertRaisesRegex(Blocked, 'pre-existing work changed'):
            f.checkpoint()

    def test_index_or_head_changes_stop_commit(self):
        f = self.focused()
        f.claim('owned.txt')
        self.write('owned.txt', 'fixed\n')
        git(self.project, 'add', '--', 'owned.txt')
        with self.assertRaisesRegex(Blocked, 'index changed'):
            f.checkpoint()

    def test_symlink_traversal_and_administrative_paths_refused(self):
        (self.project/'link').symlink_to(self.root, target_is_directory=True)
        for path in ('link/outside', '../outside', '/tmp/outside', '.git/config', '.coherence/state'):
            with self.assertRaises(Blocked, msg=path):
                editable_path(self.project, path)

    def test_hook_failure_honored_no_configure_around(self):
        hook = self.project/'.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\necho actual-hook-failure >&2\nexit 23\n')
        hook.chmod(0o755)
        f = self.focused()
        f.claim('owned.txt')
        self.write('owned.txt', 'fixed\n')
        with self.assertRaisesRegex(Blocked, 'actual-hook-failure'):
            f.checkpoint()
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        self.assertEqual((self.project/'owned.txt').read_text(), 'fixed\n')
        self.assertEqual(hook.read_text().splitlines()[-1], 'exit 23')

    def test_signing_failure_honored_no_disable_or_retry(self):
        git(self.project, 'config', 'commit.gpgsign', 'true')
        git(self.project, 'config', 'gpg.program', '/nonexistent/coherence-signing-program')
        f = self.focused()
        f.claim('owned.txt')
        self.write('owned.txt', 'fixed\n')
        with self.assertRaisesRegex(Blocked, 'Git operation failed'):
            f.checkpoint()
        self.assertEqual(git(self.project, 'config', '--get', 'commit.gpgsign'), b'true\n')
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_ambient_git_override_refused(self):
        with patch.dict(os.environ, {'GIT_INDEX_FILE': str(self.root/'foreign-index')}):
            with self.assertRaisesRegex(Blocked, 'ambient Git'):
                self.focused()

    def test_unrelated_post_selection_changes_are_not_adopted(self):
        f = self.focused()
        self.write('unknown.txt', 'external change\n')
        with self.assertRaisesRegex(Blocked, 'unclaimed changes'):
            f.checkpoint()
        self.assertEqual(git(self.project, 'diff', '--cached'), b'')
        self.assertEqual((self.project/'unknown.txt').read_text(), 'external change\n')

    def test_unrelated_symlink_and_fifo_are_preserved_without_following(self):
        (self.project/'link').symlink_to(self.root/'unknown-target')
        os.mkfifo(self.project/'pipe')
        f = self.focused()
        f.claim('owned.txt')
        self.write('owned.txt', 'fixed\n')
        self.assertEqual(f.checkpoint()['paths'], ['owned.txt'])
        self.assertTrue((self.project/'link').is_symlink())
        self.assertTrue((self.project/'pipe').exists())

    def test_owned_deletion_is_a_real_focused_commit(self):
        f = self.focused()
        f.claim('owned.txt')
        (self.project/'owned.txt').unlink()
        self.assertEqual(f.checkpoint()['paths'], ['owned.txt'])
        self.assertNotIn('owned.txt', git(self.project, 'ls-tree', '--name-only', 'HEAD').decode().splitlines())
