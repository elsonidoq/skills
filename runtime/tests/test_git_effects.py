"""Action-scoped focused commits preserve unrelated Git and filesystem work."""
import os
import subprocess
import sys
import tempfile
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
                path.write_bytes(before + b'intended correction\n')
                result = f.checkpoint()
                self.assertEqual(result['paths'], [name])
                self.assertEqual(git(self.project, 'show', 'HEAD:' + name), before + b'intended correction\n')
                self.assertEqual(git(self.project, 'show', ':other.txt'), staged)
                self.assertEqual((self.project/'unrelated.txt').read_bytes(), b'unrelated unstaged\n')

    def test_edit_only_checkpoint_excludes_inherited_bytes_and_preserves_staged_work(self):
        self.write('owned.txt', 'base\ninherited\n')
        self.write('other.txt', 'unrelated staged\n')
        git(self.project, 'add', '--', 'other.txt')
        staged = git(self.project, 'show', ':other.txt')
        f = self.focused(owned_paths=['owned.txt'])
        f.authorize_edit_only(['owned.txt'])
        f.claim('owned.txt')
        self.write('owned.txt', 'task change\ninherited\n')
        result = f.checkpoint()
        self.assertEqual(git(self.project, 'show', result['sha'] + ':owned.txt'), b'task change\n')
        self.assertEqual((self.project/'owned.txt').read_bytes(), b'task change\ninherited\n')
        self.assertEqual(git(self.project, 'show', ':other.txt'), staged)
        self.assertEqual(git(self.project, 'show', ':owned.txt'), b'task change\n')
        self.assertTrue(git(self.project, 'diff', '--', 'owned.txt'))

    def test_edit_only_resume_retains_start_and_clean_claim_and_materializes_candidate(self):
        self.write('owned.txt', 'base\ninherited\n')
        f = self.focused(owned_paths=['owned.txt', 'clean.txt'])
        f.claim('clean.txt')
        self.write('clean.txt', 'clean task\n')
        f.authorize_edit_only(['owned.txt'])
        f.claim('owned.txt')
        original = f.facts()
        self.write('owned.txt', 'task change\ninherited\n')
        resumed = FocusedGit(self.project, {'id': 'fix', 'owned_paths': ['owned.txt', 'clean.txt']}, original)
        resumed.claim('owned.txt')
        self.assertEqual(resumed.facts()['edit_only'], original['edit_only'])
        with tempfile.TemporaryDirectory() as temp:
            resumed.materialize_candidates(temp)
            from pathlib import Path
            self.assertEqual((Path(temp)/'owned.txt').read_bytes(), b'task change\n')
            self.assertEqual((Path(temp)/'clean.txt').read_bytes(), b'clean task\n')
        result = resumed.checkpoint()
        self.assertEqual(set(result['paths']), {'owned.txt', 'clean.txt'})
        self.assertEqual(git(self.project, 'show', 'HEAD:owned.txt'), b'task change\n')
        self.assertEqual(git(self.project, 'show', 'HEAD:clean.txt'), b'clean task\n')
        self.assertEqual((self.project/'owned.txt').read_bytes(), b'task change\ninherited\n')

    def test_materialized_edit_only_candidate_runs_without_inherited_behavior(self):
        self.write('script.py', 'value = 1\nprint(value)\n')
        git(self.project, 'add', '--', 'script.py')
        git(self.project, 'commit', '-qm', 'script baseline')
        self.write('script.py', 'value = 1\nprint(value)\nprint("inherited")\n')
        f = self.focused(owned_paths=['script.py'])
        f.authorize_edit_only(['script.py'])
        f.claim('script.py')
        self.write('script.py', 'value = 2\nprint(value)\nprint("inherited")\n')
        with tempfile.TemporaryDirectory() as temp:
            f.materialize_candidates(temp)
            from pathlib import Path
            candidate = subprocess.run([sys.executable, str(Path(temp)/'script.py')], capture_output=True, check=True).stdout
        mixed = subprocess.run([sys.executable, str(self.project/'script.py')], capture_output=True, check=True).stdout
        self.assertEqual(candidate, b'2\n')
        self.assertEqual(mixed, b'2\ninherited\n')
        result = f.checkpoint()
        self.assertEqual(git(self.project, 'show', result['sha'] + ':script.py'), b'value = 2\nprint(value)\n')

    def test_edit_only_unique_context_allows_repeated_closing_line_insertion(self):
        base = 'header\n  };\nunique progress();\n  };\n  };\nfooter\n'
        self.write('owned.txt', base)
        git(self.project, 'add', '--', 'owned.txt')
        git(self.project, 'commit', '-qm', 'context baseline')
        start = base.replace('header\n', 'inherited header\n')
        self.write('owned.txt', start)
        f = self.focused(owned_paths=['owned.txt'])
        f.authorize_edit_only(['owned.txt'])
        f.claim('owned.txt')
        mixed = start.replace('unique progress();\n', 'unique progress();\nobserve();\n')
        self.write('owned.txt', mixed)
        result = f.checkpoint()
        self.assertEqual(git(self.project, 'show', result['sha'] + ':owned.txt'),
                         base.replace('unique progress();\n', 'unique progress();\nobserve();\n').encode())
        self.assertEqual((self.project/'owned.txt').read_text(), mixed)

    def test_edit_only_unique_context_allows_repeated_line_replacement(self):
        base = 'header\n  };\nunique progress();\n  };\n  };\nfooter\n'
        self.write('owned.txt', base)
        git(self.project, 'add', '--', 'owned.txt')
        git(self.project, 'commit', '-qm', 'context baseline')
        start = base.replace('header\n', 'inherited header\n')
        self.write('owned.txt', start)
        f = self.focused(owned_paths=['owned.txt'])
        f.authorize_edit_only(['owned.txt'])
        f.claim('owned.txt')
        mixed = start.replace('unique progress();\n  };\n', 'unique progress();\n  changed();\n')
        self.write('owned.txt', mixed)
        result = f.checkpoint()
        self.assertEqual(git(self.project, 'show', result['sha'] + ':owned.txt'),
                         base.replace('unique progress();\n  };\n', 'unique progress();\n  changed();\n').encode())
        self.assertEqual((self.project/'owned.txt').read_text(), mixed)

    def test_edit_only_rejects_ambiguous_repeated_block_deletion(self):
        base = 'header\nbegin\nend\nbegin\nend\nfooter\n'
        self.write('owned.txt', base)
        git(self.project, 'add', '--', 'owned.txt')
        git(self.project, 'commit', '-qm', 'repeat baseline')
        start = base.replace('header\n', 'inherited header\n')
        self.write('owned.txt', start)
        f = self.focused(owned_paths=['owned.txt'])
        f.authorize_edit_only(['owned.txt'])
        f.claim('owned.txt')
        mixed = start.replace('begin\nend\nbegin\nend\n', 'begin\nend\n')
        self.write('owned.txt', mixed)
        before = git(self.project, 'rev-parse', 'HEAD')
        with self.assertRaisesRegex(Blocked, 'ambiguous'):
            f.checkpoint()
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD'), before)
        self.assertEqual((self.project/'owned.txt').read_text(), mixed)

    def test_edit_only_rejects_inherited_repeated_block_with_ambiguous_origin(self):
        base = 'header\nbegin\nend\nbegin\nend\nfooter\n'
        self.write('owned.txt', base)
        git(self.project, 'add', '--', 'owned.txt')
        git(self.project, 'commit', '-qm', 'repeat baseline')
        start = base.replace('begin\nend\nbegin\nend\n', 'begin\nend\nbegin\nend\nbegin\nend\n')
        self.write('owned.txt', start)
        f = self.focused(owned_paths=['owned.txt'])
        f.authorize_edit_only(['owned.txt'])
        f.claim('owned.txt')
        mixed = start.replace('header\nbegin\n', 'header\ntask\n')
        self.write('owned.txt', mixed)
        before = git(self.project, 'rev-parse', 'HEAD')
        with self.assertRaisesRegex(Blocked, 'ambiguous'):
            f.checkpoint()
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD'), before)
        self.assertEqual((self.project/'owned.txt').read_text(), mixed)

    def test_edit_only_rejects_overlap_index_mode_and_symlink_without_losing_work(self):
        for kind in ('overlap', 'index', 'mode', 'symlink'):
            with self.subTest(kind=kind):
                self.write('owned.txt', 'inherited\n')
                f = self.focused(owned_paths=['owned.txt'])
                f.authorize_edit_only(['owned.txt'])
                f.claim('owned.txt')
                self.write('owned.txt', 'task\n')
                path = self.project/'owned.txt'
                if kind == 'index':
                    git(self.project, 'add', '--', 'owned.txt')
                elif kind == 'mode':
                    path.chmod(0o755)
                elif kind == 'symlink':
                    path.unlink()
                    path.symlink_to(self.project/'other.txt')
                before = git(self.project, 'rev-parse', 'HEAD')
                with self.assertRaises(Blocked):
                    f.checkpoint()
                self.assertEqual(git(self.project, 'rev-parse', 'HEAD'), before)
                if kind == 'symlink':
                    self.assertTrue(path.is_symlink())
                    path.unlink()
                else:
                    self.assertEqual(path.read_text(), 'task\n')
                    path.chmod(0o644)
                if kind == 'index':
                    git(self.project, 'restore', '--staged', '--', 'owned.txt')

    def test_edit_only_hook_failure_and_post_commit_reconciliation_preserve_state(self):
        self.write('owned.txt', 'base\ninherited\n')
        f = self.focused(owned_paths=['owned.txt'])
        f.authorize_edit_only(['owned.txt'])
        f.claim('owned.txt')
        self.write('owned.txt', 'task\ninherited\n')
        hook = self.project/'.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\necho edit-only-hook-failure >&2\nexit 1\n')
        hook.chmod(0o755)
        with self.assertRaisesRegex(Blocked, 'edit-only-hook-failure'):
            f.checkpoint()
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        self.assertEqual((self.project/'owned.txt').read_bytes(), b'task\ninherited\n')
        hook.unlink()
        original = f._advance_real_index
        with patch.object(f, '_advance_real_index', side_effect=KeyboardInterrupt), self.assertRaises(KeyboardInterrupt):
            f.checkpoint()
        self.assertNotEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        with patch.object(f, '_advance_real_index', wraps=original):
            result = f.reconcile_checkpoint()
        self.assertEqual(git(self.project, 'show', result['sha'] + ':owned.txt'), b'task\n')
        self.assertEqual(git(self.project, 'show', ':owned.txt'), b'task\n')
        self.assertEqual((self.project/'owned.txt').read_bytes(), b'task\ninherited\n')

    def test_edit_only_cannot_hide_removal_of_inherited_changes_as_no_change(self):
        self.write('owned.txt', 'base\ninherited\n')
        f = self.focused(owned_paths=['owned.txt'])
        f.authorize_edit_only(['owned.txt'])
        f.claim('owned.txt')
        self.write('owned.txt', 'base\n')
        with self.assertRaisesRegex(Blocked, 'overlapping or ambiguous'):
            f.checkpoint()
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        self.assertEqual(f.facts()['edit_only']['owned.txt']['start'], 'YmFzZQppbmhlcml0ZWQK')

    def test_edit_only_hook_sees_candidate_not_inherited_worktree(self):
        self.write('owned.txt', 'base\ninherited\n')
        f = self.focused(owned_paths=['owned.txt'])
        f.authorize_edit_only(['owned.txt'])
        f.claim('owned.txt')
        self.write('owned.txt', 'task\ninherited\n')
        hook = self.project/'.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\ngrep -q inherited owned.txt && exit 1\ngit add -- owned.txt\n')
        hook.chmod(0o755)
        result = f.checkpoint()
        self.assertEqual(git(self.project, 'show', result['sha'] + ':owned.txt'), b'task\n')
        self.assertEqual((self.project/'owned.txt').read_bytes(), b'task\ninherited\n')

    def test_edit_only_signing_failure_preserves_work_and_index(self):
        self.write('owned.txt', 'base\ninherited\n')
        self.write('other.txt', 'staged elsewhere\n')
        git(self.project, 'add', '--', 'other.txt')
        staged = git(self.project, 'show', ':other.txt')
        signer = self.root/'fail-signer'
        signer.write_text('#!/bin/sh\necho fixture-signing-failure >&2\nexit 1\n')
        signer.chmod(0o755)
        git(self.project, 'config', 'commit.gpgsign', 'true')
        git(self.project, 'config', 'gpg.program', str(signer))
        f = self.focused(owned_paths=['owned.txt'])
        f.authorize_edit_only(['owned.txt'])
        f.claim('owned.txt')
        self.write('owned.txt', 'task\ninherited\n')
        with self.assertRaises(Blocked):
            f.checkpoint()
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        self.assertEqual(git(self.project, 'show', ':other.txt'), staged)
        self.assertEqual(git(self.project, 'show', ':owned.txt'), b'base\n')
        self.assertEqual((self.project/'owned.txt').read_bytes(), b'task\ninherited\n')

    def test_edit_only_rejects_scope_and_head_drift(self):
        self.write('owned.txt', 'base\ninherited\n')
        f = self.focused(owned_paths=['owned.txt'])
        with self.assertRaisesRegex(Blocked, 'outside owned_paths'):
            f.authorize_edit_only(['other.txt'])
        f.authorize_edit_only(['owned.txt'])
        f.claim('owned.txt')
        self.write('owned.txt', 'task\ninherited\n')
        self.write('owned.txt', 'incoming\n')
        git(self.project, 'add', '--', 'owned.txt')
        git(self.project, 'commit', '-qm', 'incoming')
        self.write('owned.txt', 'task\ninherited\n')
        with self.assertRaisesRegex(Blocked, 'HEAD/index drift'):
            f.checkpoint()
        self.assertEqual((self.project/'owned.txt').read_bytes(), b'task\ninherited\n')
        self.assertEqual(git(self.project, 'show', 'HEAD:owned.txt'), b'incoming\n')

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
