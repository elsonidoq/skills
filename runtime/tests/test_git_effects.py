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

    def test_repeated_source_claims_allow_task_edits_and_focused_checkpoint(self):
        f = self.focused(owned_paths=['owned.txt', 'new.txt'])
        for name in ('owned.txt', 'new.txt'):
            with self.subTest(name=name):
                f.claim(name)
                self.write(name, 'first edit\n')
                f.claim(name)
                self.write(name, 'second edit\n')
        result = f.checkpoint()
        self.assertEqual(result['paths'], ['new.txt', 'owned.txt'])
        self.assertEqual(f.facts()['paths'], ['new.txt', 'owned.txt'])
        for name in result['paths']:
            self.assertEqual(git(self.project, 'show', 'HEAD:' + name), b'second edit\n')
        self.assertEqual(git(self.project, 'status', '--porcelain'), b'')

    def test_repeated_claim_keeps_unknown_dirty_scope_and_safe_path_checks(self):
        f = self.focused(owned_paths=['owned.txt', 'other.txt', 'unknown.txt'])
        f.claim('owned.txt')
        self.write('owned.txt', 'first edit\n')
        self.write('other.txt', 'prior work\n')
        self.write('unknown.txt', 'unknown work\n')
        for name in ('other.txt', 'unknown.txt'):
            with self.assertRaisesRegex(Blocked, 'pre-existing dirty'):
                f.claim(name)
        with self.assertRaisesRegex(Blocked, 'outside optional'):
            f.claim('outside.txt')
        (self.project/'owned.txt').unlink()
        (self.project/'owned.txt').symlink_to(self.root/'outside')
        for name in ('owned.txt', '.git/config', '.coherence/state', '../outside'):
            with self.assertRaises(Blocked, msg=name):
                f.claim(name)
        self.assertEqual(f.facts()['paths'], ['owned.txt'])

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

    def test_pathspec_metacharacters_select_only_literal_owned_path(self):
        f = self.focused()
        f.claim('a[1].txt')
        self.write('a[1].txt', 'owned\n')
        self.write('a1.txt', 'unrelated\n')
        result = f.checkpoint()
        self.assertEqual(result['paths'], ['a[1].txt'])
        self.assertEqual(git(self.project, 'show', 'HEAD:a[1].txt'), b'owned\n')
        self.assertEqual((self.project/'a1.txt').read_text(), 'unrelated\n')

    def test_staged_only_owned_path_is_genuine_no_change_and_preserved(self):
        f = self.focused()
        f.claim('owned.txt')
        self.write('owned.txt', 'staged only\n')
        git(self.project, 'add', '--', 'owned.txt')
        self.write('owned.txt', 'base\n')
        staged = git(self.project, 'show', ':owned.txt')
        intent = []
        result = f.checkpoint(intent.append)
        self.assertTrue(result['no_change'])
        self.assertTrue(intent[0]['no_change'])
        self.assertEqual(git(self.project, 'show', ':owned.txt'), staged)
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_actual_write_boundary_preserves_preexisting_target_and_scope(self):
        self.write('owned.txt', 'prior work\n')
        with self.assertRaisesRegex(Blocked, 'pre-existing dirty'):
            self.focused().claim('owned.txt')
        with self.assertRaisesRegex(Blocked, 'outside optional'):
            self.focused(owned_paths=['owned.txt']).claim('other.txt')

    def test_exact_handoff_transfers_untracked_and_tracked_dirty_bytes_to_focused_checkpoints(self):
        self.write('tracked.txt', 'base\n')
        git(self.project, 'add', '--', 'tracked.txt')
        git(self.project, 'commit', '-qm', 'tracked baseline')
        self.write('tracked.txt', 'recovery tracked\n')
        self.write('untracked.txt', 'recovery untracked\n')
        self.write('other.txt', 'unrelated staged\n')
        git(self.project, 'add', '--', 'other.txt')
        staged = git(self.project, 'show', ':other.txt')
        self.write('unrelated.txt', 'unrelated unstaged\n')
        for name, before in (('tracked.txt', b'recovery tracked\n'), ('untracked.txt', b'recovery untracked\n')):
            with self.subTest(name=name):
                f = self.focused(owned_paths=['tracked.txt', 'untracked.txt'], handoff_paths=[name])
                f.claim(name)
                self.assertEqual(f.facts()['handoff_paths'], [name])
                path = self.project / name
                self.assertEqual(path.read_bytes(), before)
                path.write_bytes(before + b'first correction\n')
                f.claim(name)
                path.write_bytes(before + b'intended correction\n')
                result = f.checkpoint()
                self.assertEqual(result['paths'], [name])
                self.assertEqual(git(self.project, 'show', 'HEAD:' + name), before + b'intended correction\n')
                self.assertEqual(git(self.project, 'show', ':other.txt'), staged)
                self.assertEqual((self.project/'unrelated.txt').read_bytes(), b'unrelated unstaged\n')

    def test_checkpoint_includes_unchanged_exact_transfer_without_fake_edit(self):
        self.write('owned.txt', 'partial source\n')
        self.write('transferred.txt', 'complete supporting source\n')
        self.write('other.txt', 'unrelated staged\n')
        git(self.project, 'add', '--', 'other.txt')
        staged = git(self.project, 'ls-files', '--stage', '--', 'other.txt')
        f = self.focused(owned_paths=['owned.txt', 'transferred.txt'],
                         handoff_paths=['owned.txt', 'transferred.txt'])
        f.claim('owned.txt')
        self.write('owned.txt', 'meaningful correction\n')
        transferred = self.project / 'transferred.txt'
        identity = transferred.stat()
        intents = []
        result = f.checkpoint(intents.append)
        self.assertEqual(result['paths'], ['owned.txt', 'transferred.txt'])
        self.assertEqual(intents[0]['paths'], result['paths'])
        self.assertEqual(f.facts()['paths'], ['owned.txt'])  # No invented edit claim.
        self.assertEqual(transferred.stat(), identity)
        self.assertEqual(git(self.project, 'show', 'HEAD:owned.txt'), b'meaningful correction\n')
        self.assertEqual(git(self.project, 'show', 'HEAD:transferred.txt'), b'complete supporting source\n')
        self.assertEqual(git(self.project, 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').decode().splitlines(), result['paths'])
        self.assertEqual(git(self.project, 'ls-files', '--stage', '--', 'other.txt'), staged)
        self.assertEqual(git(self.project, 'diff', '--cached', '--name-only').strip(), b'other.txt')

    def test_unclaimed_handoff_outside_scope_cannot_be_checkpointed(self):
        self.write('other.txt', 'not task-owned\n')
        with self.assertRaisesRegex(Blocked, 'outside optional'):
            self.focused(owned_paths=['owned.txt'], handoff_paths=['other.txt']).checkpoint()
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_unclaimed_handoff_drift_blocks_checkpoint_and_retry(self):
        self.write('owned.txt', 'authorized transfer\n')
        f = self.focused(handoff_paths=['owned.txt'])
        self.write('owned.txt', 'unknown drift\n')
        for _ in range(2):
            with self.assertRaisesRegex(Blocked, 'changed pre-transfer bytes'):
                f.checkpoint()
        self.assertEqual(f.facts()['paths'], [])
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_unclaimed_handoff_drift_after_preview_is_not_adopted(self):
        self.write('owned.txt', 'authorized transfer\n')
        f = self.focused(handoff_paths=['owned.txt'])
        with self.assertRaisesRegex(Blocked, 'changed pre-transfer bytes'):
            f.checkpoint(lambda _intent: self.write('owned.txt', 'late drift\n'))
        with self.assertRaisesRegex(Blocked, 'changed pre-transfer bytes'):
            f.checkpoint()
        self.assertEqual(git(self.project, 'show', ':owned.txt'), b'base\n')
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_unclaimed_handoff_mode_drift_at_commit_boundary_blocks(self):
        self.write('owned.txt', 'authorized transfer\n')
        f = self.focused(handoff_paths=['owned.txt'])
        f.before_git_commit = lambda: (self.project / 'owned.txt').chmod(0o755)
        with self.assertRaisesRegex(Blocked, 'changed pre-transfer bytes'):
            f.checkpoint()
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        self.assertEqual(git(self.project, 'show', ':owned.txt'), b'authorized transfer\n')
        self.assertEqual(f.facts()['paths'], [])

    def test_unclaimed_generated_handoff_is_not_adopted_as_source(self):
        self.write('generated.txt', 'build output\n')
        f = self.focused(generated_outputs=['generated.txt'], handoff_paths=['generated.txt'])
        self.assertTrue(f.checkpoint()['no_change'])
        self.assertEqual(f.facts()['paths'], [])
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_handoff_refuses_broad_scope_and_pretransfer_drift(self):
        (self.project/'recovery').mkdir()
        self.write('recovery/dirty.txt', 'recovery bytes\n')
        with self.assertRaisesRegex(Blocked, r'cannot claim pre-existing dirty path recovery/dirty.txt: operation claim requires an exact handoff_paths entry'):
            self.focused(owned_paths=['recovery/']).claim('recovery/dirty.txt')
        f = self.focused(handoff_paths=['recovery/dirty.txt'])
        self.write('recovery/dirty.txt', 'unknown drift\n')
        with self.assertRaisesRegex(Blocked, r'cannot claim handoff path recovery/dirty.txt: operation claim found changed pre-transfer bytes'):
            f.claim('recovery/dirty.txt')

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
