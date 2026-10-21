"""Action-scoped focused commits preserve unrelated Git and filesystem work."""
import os
from unittest.mock import patch

from coherence_workflow.git_effects import FocusedGit, editable_path
from coherence_workflow.store import Blocked, git
from fixtures.support import ProjectTest


class FocusedCheckpointTests(ProjectTest):
    def focused(self, **context):
        return FocusedGit(self.project, {'id': 'fix', 'description': 'Fix', **context})

    def test_explicit_source_claim_commits_only_source_and_preserves_staged_unknown_work(self):
        self.write('other.txt', 'staged\n')
        git(self.project, 'add', '--', 'other.txt')
        staged = git(self.project, 'show', ':other.txt')
        f = self.focused(owned_paths=['owned.txt'], generated_outputs=['web/dist/'])
        f.claim('owned.txt')
        self.write('owned.txt', 'fixed\n')
        # A synthetic build may create both declared and undeclared output.  Neither
        # is adopted merely because it appears after a command.
        (self.project/'web/dist').mkdir(parents=True)
        f.claim('web/dist/app.js')
        self.write('web/dist/app.js', 'generated\n')
        self.write('undeclared.log', 'ignored by checkpoint\n')
        result = f.checkpoint()
        self.assertEqual(result['paths'], ['owned.txt'])
        self.assertEqual(result['artifacts'], ['web/dist/app.js'])
        self.assertEqual(git(self.project, 'show', ':other.txt'), staged)
        self.assertEqual((self.project/'web/dist/app.js').read_text(), 'generated\n')
        self.assertEqual((self.project/'undeclared.log').read_text(), 'ignored by checkpoint\n')
        self.assertNotIn('web/dist/app.js', git(self.project, 'show', '--name-only', '--format=', 'HEAD').decode())

    def test_unrelated_changes_and_incoming_commit_do_not_stop_checkpoint(self):
        f = self.focused()
        f.claim('owned.txt')
        self.write('owned.txt', 'fixed\n')
        self.write('new-planning-document.md', 'unrelated\n')
        self.write('other.txt', 'unrelated staged change\n')
        git(self.project, 'add', '--', 'other.txt')
        staged = git(self.project, 'show', ':other.txt')
        self.write('incoming.txt', 'incoming\n')
        git(self.project, 'add', '--', 'incoming.txt')
        git(self.project, 'commit', '--only', '-qm', 'incoming', '--', 'incoming.txt')
        incoming = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        result = f.checkpoint()
        self.assertEqual(result['paths'], ['owned.txt'])
        self.assertEqual(result['sha'], git(self.project, 'rev-parse', 'HEAD').decode().strip())
        self.assertEqual(git(self.project, 'rev-parse', result['sha'] + '^').decode().strip(), incoming)
        self.assertEqual((self.project/'new-planning-document.md').read_text(), 'unrelated\n')
        self.assertEqual(git(self.project, 'show', ':other.txt'), staged)
        self.assertEqual(git(self.project, 'show', incoming + ':incoming.txt'), b'incoming\n')

    def test_no_explicit_source_has_no_empty_commit(self):
        self.assertTrue(self.focused().checkpoint()['no_change'])

    def test_actual_write_boundary_preserves_preexisting_target_and_scope(self):
        self.write('owned.txt', 'prior work\n')
        with self.assertRaisesRegex(Blocked, 'pre-existing dirty'):
            self.focused().claim('owned.txt')
        with self.assertRaisesRegex(Blocked, 'outside optional'):
            self.focused(owned_paths=['owned.txt']).claim('other.txt')

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

    def test_ambient_git_override_refused(self):
        with patch.dict(os.environ, {'GIT_INDEX_FILE': str(self.root/'foreign-index')}):
            with self.assertRaisesRegex(Blocked, 'ambient Git'):
                self.focused()
