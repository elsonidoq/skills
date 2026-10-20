"""Real Git ignored nested-repository inventory, without a controller/model."""
import contextlib
import io
import json
import os
import socket
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from coherence_workflow.store import Authority, Blocked, canonical, digest, git
from coherence_workflow.tools import snapshot, reconcile
from coherence_workflow.cli import Coordinate, main
from coherence_workflow.engine import Engine
from coherence_workflow.intake import content_hash
from coherence_workflow.pi_adapter import host_resource
from fixtures.support import make_project
from coherence_workflow.git_effects import inventory_preflight
from test_intake import approved_fixture


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

    def test_root_and_ordinary_untracked_ignored_fifos_fail_closed(self):
        for relative in ('root-pipe', 'untracked/pipe', 'retained/ordinary/pipe'):
            with self.subTest(relative=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                os.mkfifo(path)
                try:
                    with self.assertRaisesRegex(Blocked, relative + r' \(fifo\)'):
                        snapshot(self.root, [])
                finally:
                    path.unlink()

    def test_root_socket_and_unreadable_file_fail_closed(self):
        sock = socket.socket(socket.AF_UNIX)
        self.addCleanup(sock.close)
        sock.bind(str(self.root / 'root-socket'))
        with self.assertRaisesRegex(Blocked, r'root-socket \(socket\)'):
            snapshot(self.root, [])
        (self.root / 'root-socket').unlink()
        unreadable = self.root / 'unreadable'
        unreadable.write_text('must not silently omit')
        unreadable.chmod(0)
        self.addCleanup(unreadable.chmod, 0o600)
        with self.assertRaisesRegex(Blocked, r'unreadable \(PermissionError\)'):
            snapshot(self.root, [])

    def test_ordinary_empty_directory_and_owned_ancestor_drift(self):
        owned = ['ordinary/owned']
        baseline = snapshot(self.root, owned)
        parent = self.root / 'ordinary'
        parent.mkdir()
        (parent / 'owned').write_text('allowed')
        now = reconcile(self.root, owned, baseline)
        (parent / 'unrelated-empty').mkdir()
        with self.assertRaisesRegex(Blocked, 'ordinary/unrelated-empty'):
            reconcile(self.root, owned, now)

    def test_tracked_deletion_and_current_index_still_audited(self):
        path = self.root / 'tracked'
        path.write_text('tracked')
        git(self.root, 'add', '--', 'tracked')
        git(self.root, 'commit', '-qm', 'tracked deletion fixture')
        baseline = snapshot(self.root, [])
        path.unlink()
        self.assertIsNone(snapshot(self.root, [])['files']['tracked'])
        with self.assertRaisesRegex(Blocked, 'unrelated file drift: tracked'):
            reconcile(self.root, [], baseline)
        git(self.root, 'add', '-A', '--', 'tracked')
        with self.assertRaisesRegex(Blocked, 'HEAD/index drift'):
            reconcile(self.root, [], baseline)

    def test_root_links_and_git_admin_exclusion_do_not_follow(self):
        (self.root / 'external-link').symlink_to('/nonexistent-inventory-target')
        (self.root / 'directory-link').symlink_to(self.nested, target_is_directory=True)
        os.mkfifo(self.root / '.git/excluded-pipe')
        files = snapshot(self.root, [])['files']
        self.assertEqual(files['external-link']['kind'], 'symlink')
        self.assertEqual(files['directory-link']['kind'], 'symlink')
        self.assertNotIn('directory-link/data', files)
        self.assertNotIn('.git', files)
        self.assertNotIn('.git/excluded-pipe', files)

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

    def test_preflight_cli_no_authority_or_storage_and_matches_selection(self):
        contract, _ = approved_fixture(self.root, 'isolated')
        tasks = self.root / 'tasks.json'
        tasks.write_text(json.dumps(contract))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(['preflight', '--project', str(self.root), '--tasks', str(tasks)])
        self.assertEqual(result, 0, output.getvalue())
        report = json.loads(output.getvalue())
        observed = inventory_preflight(self.root, contract['tasks'])
        self.assertEqual(report['entries'], len(observed['files']))
        from coherence_workflow.store import digest
        self.assertEqual(report['inventory_hash'], digest(observed['files']))
        self.assertFalse((self.root / '.coherence').exists())
        self.assertFalse((self.root / '.git/coherence-workflow.lock').exists())
        (self.root / 'owned.txt').write_text('preexisting dirt')
        with self.assertRaisesRegex(Blocked, 'dirty owned overlap: owned.txt'):
            inventory_preflight(self.root, contract['tasks'])

    def test_preflight_owned_kind_overlap_and_fsmonitor_fail_closed(self):
        os.mkfifo(self.root / 'owned-pipe')
        with self.assertRaisesRegex(Blocked, r'owned-pipe \(fifo\)'):
            inventory_preflight(self.root, [{'owned_paths':['owned-pipe']}])
        with self.assertRaisesRegex(Blocked, 'overlapping owned'):
            inventory_preflight(self.root, [{'owned_paths':['new', 'new/child']}])
        sentinel = self.root / 'must-not-run'
        hook = self.root / 'fsmonitor-hook'
        hook.write_text('#!/bin/sh\ntouch ' + str(sentinel) + '\n')
        hook.chmod(0o700)
        git(self.root, 'config', 'core.fsmonitor', str(hook))
        with self.assertRaisesRegex(Blocked, 'fsmonitor process capability unavailable'):
            inventory_preflight(self.root, [{'owned_paths':[]}])
        self.assertFalse(sentinel.exists())

    def test_startup_fails_closed_before_authority_for_special_kind(self):
        contract, _ = approved_fixture(self.root, 'isolated')
        tasks = self.root / 'tasks.json'
        tasks.write_text(json.dumps(contract))
        manifest = self.root / 'manifest.json'
        manifest.write_text('{}')
        os.mkfifo(self.nested / 'pipe')
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as catalog:
            catalog.write('{}'); catalog.flush()
            output = io.StringIO()
            suite = Path(__file__).resolve().parents[2]
            with contextlib.redirect_stdout(output):
                result = main(['start', '--project', str(self.root), '--tasks', str(tasks),
                    '--owner-catalog', catalog.name, '--manifest', str(manifest),
                    '--workflow', str(suite / 'runtime/coherence_workflow/workflows/coordinate.yaml'),
                    '--suite-root', str(suite), '--containment', '/unused', '--run', 'no-dispatch'])
        self.assertEqual(result, 2, output.getvalue())
        self.assertIn('retained/toy/pipe (fifo)', json.loads(output.getvalue())['reason'])
        self.assertFalse((self.root / '.coherence').exists())
        self.assertFalse((self.root / '.git/coherence-workflow.lock').exists())

    def test_private_root_exclusion_only(self):
        private = self.root / '.coherence/workflow'
        private.mkdir(parents=True)
        os.mkfifo(private / 'not-inventoried')
        (self.nested / '.coherence/workflow').mkdir(parents=True)
        (self.nested / '.coherence/workflow/data').write_text('nested user data')
        files = snapshot(self.root, [])['files']
        self.assertNotIn('.coherence/workflow/not-inventoried', files)
        self.assertIn('retained/toy/.coherence/workflow/data', files)


class LeanScopeTests(InventoryTests):
    def test_owned_edit_preserves_ignored_material_and_rejects_escape(self):
        from coherence_workflow.tools import owned_file
        ignored=self.nested/'data'
        before=snapshot(self.root,['owned.txt'])
        (self.root/'owned.txt').write_text('owned edit')
        after=snapshot(self.root,['owned.txt'])
        self.assertEqual(before['files']['retained/toy/data'],after['files']['retained/toy/data'])
        with self.assertRaisesRegex(Blocked,'unsafe relative path'):
            owned_file(self.root,'../escape')


class ResumeInventoryTests(unittest.TestCase):
    """Actual CLI/Engine/Coordinate recovery, without an SDK host or worker."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = make_project(self.root / 'project')
        self.suite = Path(__file__).resolve().parents[2]
        self.parent = os.environ['COHERENCE_TEST_CGROUP_PARENT']
        self.config = yaml.safe_load((self.suite / 'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
        self.contract, self.catalog = approved_fixture(self.project, digest(self.config))
        self.environment = {k:v for k,v in os.environ.items() if k in
            ('PATH','HOME','PYTHONPATH','PYTHONDONTWRITEBYTECODE','TMPDIR','PI_OFFLINE')}
        self.args = ['--project',str(self.project),'--run','partial',
            '--suite-root',str(self.suite),'--containment',self.parent]
        for flag, name, value in [('workflow','workflow.yaml',yaml.safe_dump(self.config)),
                ('tasks','tasks.json',canonical(self.contract)),
                ('owner-catalog','catalog.json',canonical(self.catalog)),
                ('manifest','manifest.json','{}')]:
            path = self.root / name
            path.write_text(value); path.chmod(0o600)
            self.args += ['--' + flag, str(path)]
        # Admit/select with real original authority and a real saved baseline. No
        # graph effect/SDK operation is fabricated or replayed; this fixture tests
        # the existing reconciliation gate, not recovery of an unknown SDK turn.
        with Authority(self.project) as owner:
            coordinate = self.coordinate(owner)
            maximum = max([self.config['defaults']['max_repair_attempts'],
                *[n.get('max_repair_attempts',0) for n in self.config['nodes']]])
            engine = Engine(owner,'partial',self.config,coordinate.registry(),self.suite,
                boundary_hook=coordinate.controls_boundary,
                max_task_visits=len(self.contract['tasks'])*(maximum+1)+maximum+1,
                input_identity={'contract':self.contract,'catalog_hash':digest(self.catalog),
                    'manifest':{},'environment':self.environment,'host_hash':content_hash(host_resource())})
            try:
                coordinate.publish_run_binding()
                coordinate.intake({})
                self.assertEqual(coordinate.select({}), {'outcome':'work'})
                self.saved_baseline = owner.store.db.execute(
                    "SELECT baseline FROM wf_tasks WHERE run_id='partial' AND task_id='A'").fetchone()[0]
                self.authorization = {'action':'reconcile','run_id':'partial','config_hash':engine.hash,
                    'operations':[],'actor':'isolated fixture owner','provenance':'current isolated recovery test'}
            finally:
                engine.close()
        (self.project / 'owned.txt').write_text('retained owned partial')
        self.auth_path = self.root / 'recovery.json'
        self.auth_path.write_text(canonical(self.authorization)); self.auth_path.chmod(0o600)

    def coordinate(self, owner):
        return Coordinate(owner,'partial',self.contract,self.catalog,self.config,self.parent,{},self.environment)

    def resume(self):
        output = io.StringIO()
        # A deterministic stop AFTER real recovery, BEFORE any graph/worker
        # dispatch. No mocked recovery or invented mechanical acceptance.
        with patch.object(Engine,'invoke',side_effect=Blocked('isolated stop after recovery')) as invoke:
            with contextlib.redirect_stdout(output):
                result = main(['resume',*self.args,'--resume-authority',str(self.auth_path)])
        self.assertEqual(result, 2, output.getvalue())
        self.assertEqual((self.project / 'owned.txt').read_text(), 'retained owned partial')
        return json.loads(output.getvalue())['reason'], invoke.call_count

    def test_partial_owned_resume_reconciles_before_any_dispatch(self):
        reason, calls = self.resume()
        self.assertEqual(reason, 'isolated stop after recovery')
        self.assertEqual(calls, 1)
        with Authority(self.project) as owner:
            self.assertEqual(owner.store.db.execute(
                "SELECT baseline FROM wf_tasks WHERE run_id='partial' AND task_id='A'").fetchone()[0], self.saved_baseline)
            self.assertEqual(owner.store.db.execute("SELECT COUNT(*) FROM wf_events WHERE kind='recovery_authorized'").fetchone()[0], 1)
            self.assertEqual(owner.store.db.execute("SELECT COUNT(*) FROM wf_operations WHERE kind IN ('process','sdk-turn')").fetchone()[0], 0)

    def test_partial_resume_still_requires_original_external_authority(self):
        self.auth_path.write_text('{}')
        reason, calls = self.resume()
        self.assertEqual(reason, 'current scoped external recovery authority required')
        self.assertEqual(calls, 0)
        with Authority(self.project) as owner:
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_controllers').fetchone()[0], 0)
            self.assertEqual(owner.store.db.execute("SELECT COUNT(*) FROM wf_events WHERE kind='recovery_authorized'").fetchone()[0], 0)

    def test_partial_resume_unrelated_drift_rejected_by_original_reconciliation(self):
        (self.project / 'other.txt').write_text('unrelated drift')
        reason, calls = self.resume()
        self.assertIn('unrelated file drift: other.txt', reason)
        self.assertEqual(calls, 0)
        self.assertEqual((self.project / 'other.txt').read_text(), 'unrelated drift')

    def test_partial_resume_root_fifo_fails_before_recovery(self):
        os.mkfifo(self.project / 'root-pipe')
        reason, calls = self.resume()
        self.assertIn('root-pipe (fifo)', reason)
        self.assertEqual(calls, 0)
        with Authority(self.project) as owner:
            self.assertEqual(owner.store.db.execute("SELECT COUNT(*) FROM wf_events WHERE kind='recovery_authorized'").fetchone()[0], 0)

    def test_partial_resume_unsupported_kind_fails_before_recovery(self):
        nested = self.project / 'untracked-repo'
        nested.mkdir()
        git(nested, 'init', '-q')
        os.mkfifo(nested / 'unsafe-pipe')
        reason, calls = self.resume()
        self.assertIn('untracked-repo/unsafe-pipe (fifo)', reason)
        self.assertEqual(calls, 0)
        with Authority(self.project) as owner:
            self.assertEqual(owner.store.db.execute("SELECT COUNT(*) FROM wf_events WHERE kind='recovery_authorized'").fetchone()[0], 0)

    def test_fresh_start_and_pending_selection_still_require_clean_owned_paths(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(['start',*self.args])
        self.assertEqual(result, 2)
        self.assertIn('preexisting dirty owned overlap: owned.txt', output.getvalue())
        (self.project / 'second.txt').write_text('not an admitted task baseline')
        with Authority(self.project) as owner:
            coordinate = self.coordinate(owner)
            with self.assertRaisesRegex(Blocked, 'preexisting dirty owned overlap: second.txt'):
                coordinate.git.begin(self.contract['tasks'][1])


if __name__ == '__main__':
    unittest.main()
