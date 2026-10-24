"""Execution-only readers and startup quarantine, using disposable SQLite files."""
import contextlib
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from unittest.mock import patch

from coherence_workflow.cli import main, status
from coherence_workflow.store import Authority, Blocked, canonical, execution_schema
from coherence_workflow.processes import process_identity
from fixtures.support import ProjectTest


class DatabaseCompatibilityTests(ProjectTest):
    def setUp(self):
        super().setUp()
        # These CLI/database tests exercise unattached operation.  A parent-session bridge
        # inherited from the surrounding test runner is an unrelated transport input.
        self.bridge_environment = patch.dict(os.environ, {
            'COHERENCE_PARENT_BRIDGE_SOCKET': '', 'COHERENCE_PARENT_BRIDGE_TOKEN': '',
            'COHERENCE_PARENT_BRIDGE_SESSION': '', 'COHERENCE_PARENT_BRIDGE_RUN': '',
        })
        self.bridge_environment.start()
        self.addCleanup(self.bridge_environment.stop)
        self.database = self.project / '.coherence/workflow/workflow.sqlite'
        self.database.parent.mkdir(parents=True)

    def unsupported(self):
        with sqlite3.connect(self.database) as db:
            db.executescript("CREATE TABLE wf_meta(version); INSERT INTO wf_meta VALUES(1); "
                             "CREATE TABLE retained(value); INSERT INTO retained VALUES('history');")

    def archives(self):
        return list(self.database.parent.glob('quarantine-*'))

    def test_execution_status_and_missing_run_are_read_only(self):
        with Authority(self.project) as owner:
            owner.store.start('current', self.base)
            owner.store.finish('current', 'failed', self.base, 'retained error')
        before = self.database.read_bytes()
        self.assertEqual(status(self.project, 'current')['run']['state'], 'failed')
        with self.assertRaisesRegex(Blocked, 'run not found: absent'):
            status(self.project, 'absent')
        self.assertEqual(self.database.read_bytes(), before)
        self.assertEqual(self.archives(), [])

    def test_unsupported_read_and_nonstartup_operations_do_not_replace_storage(self):
        self.unsupported()
        before = self.database.read_bytes()
        for command in ('status', 'history', 'resume', 'abandon'):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                result = main([command, '--project', str(self.project), '--run', 'old'])
            self.assertEqual(result, 2)
            self.assertIn('unsupported workflow database format', output.getvalue())
            self.assertEqual(self.database.read_bytes(), before)
            self.assertEqual(self.archives(), [])

    def test_startup_quarantines_and_creates_clean_storage_without_resuming(self):
        self.unsupported()
        before = self.database.read_bytes()
        with Authority(self.project, quarantine_unsupported=True) as owner:
            archive = owner.quarantined_database
            self.assertEqual((archive / self.database.name).read_bytes(), before)
            self.assertTrue(execution_schema(owner.store.db))
            self.assertIsNone(owner.store.db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_meta'").fetchone())
            self.assertEqual(owner.store.db.execute('SELECT count(*) FROM execution_runs').fetchone()[0], 0)
            with self.assertRaisesRegex(Blocked, 'existing run'):
                owner.store.resume('old')
        self.assertEqual(len(self.archives()), 1)
        with Authority(self.project, quarantine_unsupported=True) as owner:
            self.assertIsNone(owner.quarantined_database)
        self.assertEqual(len(self.archives()), 1)

    def test_minimal_execution_history_needs_no_legacy_metadata(self):
        with Authority(self.project) as owner:
            owner.store.db.execute('INSERT INTO execution_runs VALUES(?,?,?,?,?)',
                                   ('early', 'failed', self.base, None, 'retained'))
            owner.store.db.execute('DROP TABLE execution_history')
        self.assertEqual(status(self.project, 'early')['run']['state'], 'failed')
        self.assertEqual(self.archives(), [])

    def test_incompatible_execution_columns_are_quarantined(self):
        with sqlite3.connect(self.database) as db:
            db.execute('CREATE TABLE execution_runs(incompatible)')
        with Authority(self.project, quarantine_unsupported=True) as owner:
            archive = owner.quarantined_database / self.database.name
            self.assertTrue(execution_schema(owner.store.db))
        with sqlite3.connect(archive) as db:
            self.assertEqual(db.execute('PRAGMA table_info(execution_runs)').fetchone()[1], 'incompatible')

    def test_live_recorded_writer_prevents_quarantine(self):
        self.unsupported()
        with sqlite3.connect(self.database) as db:
            db.execute('CREATE TABLE wf_controllers(identity)')
            db.execute('INSERT INTO wf_controllers VALUES(?)',
                       (canonical(process_identity(os.getpid(), 'live')),))
        before = self.database.read_bytes()
        with self.assertRaisesRegex(Blocked, 'quarantine refused: live controller'):
            Authority(self.project, quarantine_unsupported=True)
        self.assertEqual(self.database.read_bytes(), before)
        self.assertEqual(self.archives(), [])

    def test_failed_quarantine_does_not_initialize_over_original(self):
        self.unsupported()
        before = self.database.read_bytes()
        with patch.object(Path, 'rename', side_effect=OSError('fixture move failure')):
            with self.assertRaisesRegex(Blocked, 'quarantine incomplete.*fixture move failure'):
                Authority(self.project, quarantine_unsupported=True)
        self.assertEqual(self.database.read_bytes(), before)
        with sqlite3.connect(self.database) as db:
            self.assertFalse(execution_schema(db))
            self.assertEqual(db.execute('SELECT value FROM retained').fetchone()[0], 'history')

    def test_existing_archives_are_not_overwritten(self):
        previous = self.database.parent / 'quarantine-previous'
        previous.mkdir()
        (previous / self.database.name).write_bytes(b'previous history')
        self.unsupported()
        with Authority(self.project, quarantine_unsupported=True) as owner:
            self.assertNotEqual(owner.quarantined_database, previous)
        self.assertEqual((previous / self.database.name).read_bytes(), b'previous history')
        self.assertEqual(len(self.archives()), 2)

    def test_committed_wal_history_survives_quarantine(self):
        # Abrupt exit leaves committed pages in WAL without a live SQLite user.
        subprocess.run([sys.executable, '-c', '''
import os, sqlite3, sys
db = sqlite3.connect(sys.argv[1], isolation_level=None)
db.execute('PRAGMA journal_mode=WAL')
db.executescript("CREATE TABLE retained(value); INSERT INTO retained VALUES('wal history');")
os._exit(0)
''', str(self.database)], check=True)
        self.assertTrue(Path(str(self.database) + '-wal').stat().st_size)
        with Authority(self.project, quarantine_unsupported=True) as owner:
            archive = owner.quarantined_database / self.database.name
        with sqlite3.connect(archive.as_uri() + '?mode=ro', uri=True) as db:
            self.assertEqual(db.execute('SELECT value FROM retained').fetchone()[0], 'wal history')

    def test_busy_wal_is_not_quarantined(self):
        writer = sqlite3.connect(self.database, isolation_level=None)
        self.addCleanup(writer.close)
        writer.execute('PRAGMA journal_mode=WAL')
        writer.execute('CREATE TABLE retained(value)')
        reader = sqlite3.connect(self.database, isolation_level=None)
        self.addCleanup(reader.close)
        reader.execute('BEGIN')
        reader.execute('SELECT * FROM retained').fetchall()
        writer.execute("INSERT INTO retained VALUES('new history')")
        with self.assertRaisesRegex(Blocked, 'database is busy'):
            Authority(self.project, quarantine_unsupported=True)
        self.assertEqual(self.archives(), [])
        self.assertEqual(writer.execute('SELECT value FROM retained').fetchone()[0], 'new history')

    def test_held_worktree_lock_prevents_quarantine(self):
        with Authority(self.project):
            with self.assertRaisesRegex(Blocked, 'writer lock already held'):
                Authority(self.project, quarantine_unsupported=True)
        self.assertEqual(self.archives(), [])

    def test_sidecar_symlink_is_not_followed(self):
        self.unsupported()
        unrelated = self.root / 'unrelated'
        unrelated.write_bytes(b'preserve')
        Path(str(self.database) + '-wal').symlink_to(unrelated)
        with self.assertRaisesRegex(Blocked, 'symlink'):
            Authority(self.project, quarantine_unsupported=True)
        self.assertEqual(unrelated.read_bytes(), b'preserve')
        self.assertEqual(self.archives(), [])

    def test_start_cli_reports_archive_before_provider_execution(self):
        self.unsupported()
        tasks = self.root / 'tasks.json'
        tasks.write_text(json.dumps([{'id': 'task', 'description': 'scoped work'}]))
        executor = self.root / 'executor.json'
        profile = {'provider': 'test', 'model': 'test', 'effort': 'medium'}
        executor.write_text(json.dumps({**profile, 'reviewer': profile}))
        with patch('coherence_workflow.cli.Engine', side_effect=Blocked('stop before provider')) as engine:
            with contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()) as diagnostics:
                result = main(['start', '--project', str(self.project), '--tasks', str(tasks),
                               '--executor', str(executor), '--run', 'new'])
        self.assertEqual(result, 2)
        engine.assert_called_once()
        self.assertIn('stop before provider', output.getvalue())
        self.assertIn(str(self.archives()[0]), diagnostics.getvalue())
        with sqlite3.connect(self.database) as db:
            self.assertTrue(execution_schema(db))
