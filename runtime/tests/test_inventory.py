"""Real Git ignored nested-repository inventory, without a controller/model."""
import os
import socket
from pathlib import Path
import tempfile
import unittest

from coherence_workflow.store import Blocked, git
from coherence_workflow.tools import snapshot, reconcile


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        git(self.root, 'init', '-q')
        git(self.root, 'config', 'user.name', 'Inventory test')
        git(self.root, 'config', 'user.email', 'inventory@example.invalid')
        (self.root / '.gitignore').write_text('retained/\n.coherence/\n')
        git(self.root, 'add', '--', '.gitignore')
        git(self.root, 'commit', '-qm', 'baseline')
        self.nested = self.root / 'retained/toy'
        self.nested.mkdir(parents=True)
        git(self.nested, 'init', '-q')
        (self.nested / 'data').write_text('original')

    def test_real_directory_expansion_and_drift(self):
        raw = git(self.root, 'ls-files', '--others', '--ignored', '--exclude-standard', '-z')
        self.assertIn(b'retained/toy/\0', raw)
        baseline = snapshot(self.root, [])
        self.assertIn('retained/toy/.git/config', baseline['files'])
        self.assertEqual(baseline['files']['retained/toy']['kind'], 'directory')
        for action in ('content', 'addition', 'deletion', 'identity'):
            with self.subTest(action=action):
                path = self.nested / 'data'
                path.write_text('original')
                baseline = snapshot(self.root, [])
                if action == 'content': path.write_text('changed')
                elif action == 'addition': (self.nested / 'new').write_text('new')
                elif action == 'deletion': path.unlink()
                else:
                    path.rename(self.nested / 'old')
                    path.write_text('original')
                with self.assertRaisesRegex(Blocked, 'unrelated file drift: retained/toy/'):
                    reconcile(self.root, [], baseline)
                baseline = snapshot(self.root, [])

    def test_links_never_followed(self):
        outside = self.root.parent / (self.root.name + '-outside')
        outside.write_text('outside')
        self.addCleanup(outside.unlink)
        (self.nested / 'external').symlink_to(outside)
        (self.nested / 'broken').symlink_to('/nonexistent-inventory-target')
        (self.nested / 'cycle').symlink_to(self.nested, target_is_directory=True)
        baseline = snapshot(self.root, [])
        self.assertEqual(baseline['files']['retained/toy/external']['kind'], 'symlink')
        self.assertNotIn('retained/toy/cycle/data', baseline['files'])
        outside.write_text('not inventoried outside authority')
        self.assertEqual(reconcile(self.root, [], baseline), baseline)
        (self.nested / 'broken').unlink()
        (self.nested / 'broken').symlink_to('/different-broken-target')
        with self.assertRaisesRegex(Blocked, 'retained/toy/broken'):
            reconcile(self.root, [], baseline)

    def test_special_kind_precise_failure(self):
        os.mkfifo(self.nested / 'pipe')
        with self.assertRaisesRegex(Blocked, r'retained/toy/pipe \(fifo\)'):
            snapshot(self.root, [])

    def test_socket_and_empty_directory_drift(self):
        sock = socket.socket(socket.AF_UNIX)
        self.addCleanup(sock.close)
        sock.bind(str(self.nested / 'socket'))
        with self.assertRaisesRegex(Blocked, r'retained/toy/socket \(socket\)'):
            snapshot(self.root, [])
        (self.nested / 'socket').unlink()
        empty = self.nested / 'empty'
        empty.mkdir()
        baseline = snapshot(self.root, [])
        empty.rmdir()
        with self.assertRaisesRegex(Blocked, 'retained/toy/empty'):
            reconcile(self.root, [], baseline)

    def test_owned_parent_identity_replacement_rejected(self):
        owned = ['retained/toy/parent/owned']
        parent = self.nested / 'parent'
        parent.mkdir()
        baseline = snapshot(self.root, owned)
        parent.rename(self.nested / 'old-parent')
        parent.mkdir()
        with self.assertRaisesRegex(Blocked, 'unrelated file drift'):
            reconcile(self.root, owned, baseline)

    def test_owned_parent_creation_and_unrelated_child(self):
        owned = ['retained/toy/created/owned']
        baseline = snapshot(self.root, owned)
        parent = self.nested / 'created'
        parent.mkdir()
        (parent / 'owned').write_text('allowed')
        reconcile(self.root, owned, baseline)
        (parent / 'other').write_text('not owned')
        with self.assertRaisesRegex(Blocked, 'created/other'):
            reconcile(self.root, owned, baseline)

    def test_owned_symlink_ancestor_and_directory_rejected(self):
        (self.root / 'alias').symlink_to(self.nested, target_is_directory=True)
        for owned in (['alias/data'], ['retained/toy']):
            with self.assertRaises(Blocked): snapshot(self.root, owned)

    def test_private_root_exclusion_only(self):
        private = self.root / '.coherence/workflow'
        private.mkdir(parents=True)
        os.mkfifo(private / 'not-inventoried')
        (self.nested / '.coherence/workflow').mkdir(parents=True)
        (self.nested / '.coherence/workflow/data').write_text('nested user data')
        files = snapshot(self.root, [])['files']
        self.assertNotIn('.coherence/workflow/not-inventoried', files)
        self.assertIn('retained/toy/.coherence/workflow/data', files)


if __name__ == '__main__':
    unittest.main()
