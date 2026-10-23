"""Historical records stay readable and untouched; no automatic effect replay."""
import json
import os
import sqlite3
from unittest.mock import patch

from coherence_workflow.cli import status
from coherence_workflow.store import Authority, Blocked, canonical, git
from coherence_workflow.processes import process_identity
from fixtures.support import ProjectTest


class HistoricalProgressTests(ProjectTest):
    def legacy(self, owner, *, live=False):
        db = owner.store.db
        db.executescript('''
        CREATE TABLE wf_meta(version INTEGER); INSERT INTO wf_meta VALUES(1);
        CREATE TABLE wf_runs(run_id TEXT PRIMARY KEY,config_hash TEXT,state TEXT,reservation INTEGER);
        CREATE UNIQUE INDEX wf_one_reservation ON wf_runs(reservation) WHERE reservation=1;
        INSERT INTO wf_runs VALUES('old','old-identity','running',1);
        CREATE TABLE wf_operations(op_id TEXT PRIMARY KEY,run_id TEXT,node_id TEXT,kind TEXT,phase TEXT);
        INSERT INTO wf_operations VALUES('uncertain','old','implement','sdk-turn','intent');
        CREATE TABLE wf_events(seq INTEGER PRIMARY KEY,event_id TEXT,run_id TEXT,op_id TEXT,kind TEXT,payload TEXT);
        CREATE TABLE wf_controllers(run_id TEXT,identity TEXT,phase TEXT);
        CREATE TABLE wf_processes(op_id TEXT,identity TEXT,containment TEXT);
        CREATE TABLE wf_alarms(alarm_id TEXT,state TEXT);
        INSERT INTO wf_alarms VALUES('old-alarm','active');
        ''')
        if live:
            db.execute('INSERT INTO wf_controllers VALUES(?,?,?)', ('old', canonical(process_identity(os.getpid(), 'fixture')), 'stopped'))
        return db

    def test_historical_status_read_only_and_abandon_preserves_incomplete_rows(self):
        with Authority(self.project) as owner:
            db = self.legacy(owner)
            operations = db.execute('SELECT * FROM wf_operations').fetchall()
            alarms = db.execute('SELECT * FROM wf_alarms').fetchall()
            with self.assertRaisesRegex(Blocked, 'run not found: old'):
                status(self.project, 'old')
            self.assertFalse(db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_attempts'").fetchone())
            owner.store.abandon('old')
            self.assertEqual(db.execute('SELECT state,reservation FROM wf_runs').fetchone()[:], ('ABANDONED', 0))
            self.assertEqual(db.execute('SELECT * FROM wf_operations').fetchall(), operations)
            self.assertEqual(db.execute('SELECT * FROM wf_alarms').fetchall(), alarms)
            owner.store.start('new', self.base)
            owner.store.finish('new', 'failed', self.base, 'ordinary SDK error')
            owner.store.start('new-again', self.base)
            self.assertEqual(db.execute('SELECT phase FROM wf_operations').fetchone()[0], 'intent')
        self.assertEqual(status(self.project, 'new')['run']['state'], 'failed')

    def test_old_incomplete_history_does_not_veto_new_progress_or_reconcile_it(self):
        with Authority(self.project) as owner:
            db = self.legacy(owner)
            before = tuple(db.execute('SELECT * FROM wf_operations').fetchone())
            owner.store.start('fresh', self.base)
            self.assertEqual(tuple(db.execute('SELECT * FROM wf_operations').fetchone()), before)
            self.assertEqual(db.execute('SELECT reservation FROM wf_runs').fetchone()[0], 1)

    def test_live_recorded_controller_refuses_abandon_without_signal(self):
        with Authority(self.project) as owner:
            db = self.legacy(owner, live=True)
            with self.assertRaisesRegex(Blocked, 'live controller'):
                owner.store.abandon('old')
            with self.assertRaisesRegex(Blocked, 'start refused: live controller'):
                owner.store.start('new', self.base)
            self.assertEqual(db.execute('SELECT reservation FROM wf_runs').fetchone()[0], 1)

    def test_live_recorded_child_refuses_abandon(self):
        with Authority(self.project) as owner:
            db = self.legacy(owner)
            db.execute('INSERT INTO wf_processes VALUES(?,?,NULL)', ('uncertain', canonical(process_identity(os.getpid(), 'child'))))
            with self.assertRaisesRegex(Blocked, 'live child'):
                owner.store.abandon('old')
            with self.assertRaisesRegex(Blocked, 'start refused: live child'):
                owner.store.start('new', self.base)

    def test_abandon_unknown_run_reports_operation_error(self):
        with Authority(self.project) as owner:
            with self.assertRaisesRegex(Blocked, 'unknown run'):
                owner.store.abandon('absent')

    def test_held_writer_lock_cannot_be_replaced(self):
        with Authority(self.project):
            with self.assertRaisesRegex(Blocked, 'writer lock already held'):
                Authority(self.project)

    def test_existing_schema_version_and_invalid_bindings_do_not_gate_execution(self):
        # Historical metadata is not parsed by new execution; it also isn't rewritten.
        with Authority(self.project) as owner:
            db = owner.store.db
            db.executescript('CREATE TABLE wf_meta(version INTEGER); INSERT INTO wf_meta VALUES(999);')
            binding = self.project/'.git/coherence-workflow.binding'
            binding.write_text('old optional binding no longer executable')
            owner.store.start('normal', self.base)
            self.assertEqual(db.execute('SELECT version FROM wf_meta').fetchone()[0], 999)
            self.assertEqual(binding.read_text(), 'old optional binding no longer executable')

    def test_new_run_abandon_retains_error_and_partial_work(self):
        self.write('owned.txt', 'partial\n')
        with Authority(self.project) as owner:
            owner.store.start('new', self.base)
            owner.store.finish('new', 'failed', self.base, 'SDK error')
            result = owner.store.abandon('new')
            self.assertEqual(result['state'], 'abandoned')
            self.assertEqual(result['error'], 'SDK error')
        self.assertEqual((self.project/'owned.txt').read_text(), 'partial\n')

    def test_live_host_inherits_writer_lock_after_controller_closes(self):
        import subprocess
        import sys
        owner = Authority(self.project)
        child = subprocess.Popen([sys.executable, '-B', '-c',
            "import sys; print('ready',flush=True); sys.stdin.read()"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, pass_fds=(owner.lock.fileno(),))
        try:
            self.assertEqual(child.stdout.readline().strip(), 'ready')
            owner.close()
            with self.assertRaisesRegex(Blocked, 'writer lock already held'):
                Authority(self.project)
        finally:
            child.stdin.close()
            child.wait()
            child.stdout.close()
            if not owner.lock.closed: owner.close()
        with Authority(self.project): pass

    def test_recorded_scope_membership_guards_start_and_abandon_with_absent_leader(self):
        from pathlib import Path
        with Authority(self.project) as owner:
            db = self.legacy(owner)
            scope = Path('/sys/fs/cgroup/coherence-fix02-offline-fixture')
            leader = process_identity(os.getpid(), 'absent-leader')
            leader['pid'] = 999999999
            db.execute('INSERT INTO wf_processes VALUES(?,?,?)', ('uncertain', canonical(leader), canonical(
                {'parent': str(scope.parent), 'name': scope.name})))
            before = list(db.iterdump())
            original_exists, original_stat, original_read = Path.exists, Path.stat, Path.read_text
            def exists(path):
                if path == Path('/proc/999999999'): return False
                return original_exists(path)
            def stat(path, *args, **kwargs):
                if path == scope:
                    if state == 'missing': raise FileNotFoundError(str(path))
                    if state == 'unreadable-stat': raise PermissionError(str(path))
                    return original_stat(scope.parent, *args, **kwargs)
                return original_stat(path, *args, **kwargs)
            def read(path, *args, **kwargs):
                if path == scope/'cgroup.events':
                    if state == 'unreadable-events': raise PermissionError(str(path))
                    if state == 'invalid-events': return 'malformed event data\n'
                    return 'populated 1\n' if state == 'populated' else 'populated 0\n'
                if path == scope/'cgroup.procs':
                    if state == 'unreadable-members': raise PermissionError(str(path))
                    return '123\n' if state == 'members' else ''
                return original_read(path, *args, **kwargs)
            with patch.object(Path, 'exists', exists), patch.object(Path, 'stat', stat), patch.object(Path, 'read_text', read):
                for state, message in (
                        ('populated', 'refused: populated child scope'),
                        ('members', 'refused: populated child scope'),
                        ('unreadable-stat', 'cannot read recorded scope'),
                        ('unreadable-events', 'cannot read recorded scope'),
                        ('unreadable-members', 'cannot read recorded scope'),
                        ('invalid-events', 'cannot determine scope membership')):
                    for operation in ('start', 'abandon'):
                        with self.subTest(state=state, operation=operation):
                            with self.assertRaisesRegex(Blocked, operation + ' ' + message):
                                if operation == 'start': owner.store.start('new', self.base)
                                else: owner.store.abandon('old')
                            self.assertEqual(list(db.iterdump()), before)
                for state in ('empty', 'missing'):
                    with self.subTest(state=state):
                        owner.store.start('new-' + state, self.base)
                        self.assertEqual(db.execute('SELECT reservation FROM wf_runs').fetchone()[0], 1)
                        self.assertEqual(db.execute('SELECT phase FROM wf_operations').fetchone()[0], 'intent')
                owner.store.abandon('old')
            self.assertEqual(db.execute('SELECT phase FROM wf_operations').fetchone()[0], 'intent')

    def test_reused_recorded_pid_does_not_veto_fresh_start(self):
        with Authority(self.project) as owner:
            db = self.legacy(owner)
            identity = process_identity(os.getpid(), 'reused-pid')
            identity['start'] = 'different-start'
            db.execute('INSERT INTO wf_processes VALUES(?,?,NULL)', ('uncertain', canonical(identity)))
            owner.store.start('new', self.base)
            self.assertEqual(db.execute('SELECT reservation FROM wf_runs').fetchone()[0], 1)
            self.assertEqual(db.execute('SELECT phase FROM wf_operations').fetchone()[0], 'intent')

    def test_old_run_id_not_shadowed_by_new_history(self):
        with Authority(self.project) as owner:
            self.legacy(owner)
            with self.assertRaisesRegex(Blocked, 'fresh run ID'):
                owner.store.start('old', self.base)
        with self.assertRaisesRegex(Blocked, 'run not found: old'):
            status(self.project, 'old')
