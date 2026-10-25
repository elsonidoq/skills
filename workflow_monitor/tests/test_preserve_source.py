"""Actual stopped-source capture fixtures: Git, SQLite/WAL and JSONL bytes."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))

from coherence_workflow.metric_artifacts import create_artifact
from coherence_workflow.metrics import interval_record
from coherence_workflow.store import Authority, git
from workflow_monitor.preserve_source import CaptureError, capture_stopped


class PreserveSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.main = Path(self.temp.name) / "main"; self.main.mkdir()
        git(self.main, "init", "-q"); git(self.main, "config", "user.name", "Fixture")
        git(self.main, "config", "user.email", "fixture@example.invalid")
        (self.main / "tracked").write_text("main\n"); git(self.main, "add", "tracked"); git(self.main, "commit", "-qm", "main")
        self.source = Path(self.temp.name) / "stopped"; git(self.main, "worktree", "add", "-qb", "stopped", str(self.source))
        self.base = git(self.source, "rev-parse", "HEAD").decode().strip()
        with Authority(self.source) as owner:
            owner.store.start("kept", self.base, contract={"private": "never copy"})
            owner.store.db.execute("PRAGMA journal_mode=WAL")
            owner.store.db.execute("INSERT INTO execution_monitor_runs VALUES(?,?,?,?,?)", ("kept", 1, "{}", 1.0, json.dumps({"pid": 1})))
            owner.store.db.execute("INSERT INTO execution_monitor_runs VALUES(?,?,?,?,?)", ("unknown", 9, "{}", 2.0, None))
            owner.store.db.execute("INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)", ("kept", 1, "first", "worker", None, "started", 1.0, json.dumps({"invocation_id": "call"})))
            owner.store.db.execute("INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)", ("kept", 1, "second", "worker", None, "returned", 2.0, json.dumps({"invocation_id": "call"})))
            owner.store.review_dispatch("kept", "review", review_base=self.base, review_head=self.base, input_checkpoints=[])
            owner.store.review_outcome("kept", "review", "rejected", findings=["tracked:1 - retained"])
            owner.store.history("kept", None, "worker_invocation", "started", {"invocation_id": "call"})
            owner.store.history("kept", None, "metric_artifact", "committed", {"path": ".coherence/metrics/retained.jsonl", "sha": self.base})
            owner.store.history("kept", None, "private_kind", "started", {"secret": "exclude"})
            artifact = create_artifact(self.source, "kept", authority=owner)
            artifact.append({"version": 1, "run_id": "kept", "invocation_id": "call", "task_id": None, "role": "worker", "outcome": "settled", "fixing_round": None, "review_ordinal": None, "interval": interval_record(None, None), "before": None, "after": None, "selected_session_mode": "unknown", "session_selection_reason": "fixture", "actual_session_mode": "unknown", "actual_session_id": None})
        self.db = self.source / ".coherence/workflow/workflow.sqlite"
        self.metric = self.source / ".coherence/metrics" / ("run-" + hashlib.sha256(b"kept").hexdigest() + ".jsonl")

    def _private(self, name="prepare"):
        return self.main / ".coherence" / name

    def test_capture_retains_monitor_subset_and_metric_bytes_without_source_mutation(self):
        # Keep a committed WAL frame live: the helper must project it without opening
        # source SQLite (which would create source-side coordination files).
        wal_writer = sqlite3.connect(self.db)
        self.addCleanup(wal_writer.close)
        wal_writer.execute("PRAGMA journal_mode=WAL")
        wal_writer.execute("INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)", ("kept", 1, "wal", "worker", None, "returned", 3.0, "{}"))
        wal_writer.commit()
        wal = self.db.with_name(self.db.name + "-wal")
        self.assertTrue(wal.exists())
        before = {path: path.read_bytes() for path in (self.db, wal, self.metric)}
        status = git(self.source, "status", "--porcelain")
        with capture_stopped(self.source, self._private()) as capture:
            self.assertEqual(capture.main, self.main)
            self.assertTrue(capture.origin_id)
            self.assertEqual((capture.metrics / self.metric.name).read_bytes(), before[self.metric])
            self.assertEqual(capture.summary["metrics"][self.metric.name], {"availability": "copied_unqualified", "sha256": hashlib.sha256(before[self.metric]).hexdigest()})
            self.assertEqual(capture.metric_paths[self.metric.name], capture.metrics / self.metric.name)
            with sqlite3.connect(capture.database) as copied:
                self.assertEqual([row[0] for row in copied.execute("SELECT run_id FROM execution_monitor_runs ORDER BY started_at")], ["kept", "unknown"])
                self.assertEqual([row[0] for row in copied.execute("SELECT occurrence_id FROM execution_observations ORDER BY seq")], ["first", "second", "wal"])
                self.assertEqual([row[0] for row in copied.execute("SELECT state FROM execution_review_attempts ORDER BY seq")], ["dispatched", "rejected"])
                self.assertEqual([row[0] for row in copied.execute("SELECT kind FROM execution_history ORDER BY seq")], ["worker_invocation", "metric_artifact"])
                self.assertFalse(copied.execute("SELECT 1 FROM sqlite_master WHERE name='execution_run_inputs'").fetchone())
            capture.verify_unchanged()
        self.assertEqual(before, {path: path.read_bytes() for path in before})
        self.assertEqual(status, git(self.source, "status", "--porcelain"))
        self.assertFalse((self.main / ".coherence/preserved-recordings").exists())

    def test_busy_lock_is_not_signalled_and_is_held_for_consumer(self):
        admin = Path(git(self.source, "rev-parse", "--absolute-git-dir").decode().strip())
        fd = os.open(admin / "coherence-workflow.lock", os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(CaptureError, "busy"):
                capture_stopped(self.source, self._private("busy"))
        finally:
            os.close(fd)
        with capture_stopped(self.source, self._private("held")):
            with self.assertRaisesRegex(CaptureError, "busy"):
                capture_stopped(self.source, self._private("second"))
        with capture_stopped(self.source, self._private("released")):
            pass

    def test_drift_rejects_verification_and_error_releases_lock(self):
        capture = capture_stopped(self.source, self._private("drift"))
        self.metric.write_bytes(self.metric.read_bytes() + b"partial")
        with self.assertRaisesRegex(CaptureError, "source changed"):
            capture.__exit__(None, None, None)
        with capture_stopped(self.source, self._private("released-after-error")):
            pass

    def test_database_replacement_is_not_called_consistent(self):
        capture = capture_stopped(self.source, self._private("replacement"))
        replacement = self.db.with_name("replacement.sqlite")
        replacement.write_bytes(self.db.read_bytes())
        os.replace(replacement, self.db)
        with self.assertRaisesRegex(CaptureError, "source changed"):
            capture.verify_unchanged()
        capture.__exit__(RuntimeError, RuntimeError("consumer failed"), None)

    def test_no_raw_private_database_is_copied_and_history_is_typed(self):
        with sqlite3.connect(self.db) as connection:
            connection.execute("INSERT INTO execution_history(run_id,task_id,kind,state,details,recorded_at) VALUES(?,?,?,?,?,?)", ("kept", None, "fixer_invocation", "returned", json.dumps({"invocation_id": "call", "blobs": {"PRIVATE-SENTINEL": "runnable"}}), 3.0))
            connection.execute("INSERT INTO execution_history(run_id,task_id,kind,state,details,recorded_at) VALUES(?,?,?,?,?,?)", ("kept", None, "worker_invocation", "started", json.dumps({"invocation_id": "typed", "execution_id": "exec", "role": "worker", "private_prompt": "PRIVATE-SENTINEL"}), 4.0))
            connection.execute("CREATE TABLE private_payload(secret TEXT)")
            connection.execute("INSERT INTO private_payload VALUES('PRIVATE-SENTINEL')")
        with capture_stopped(self.source, self._private("typed")) as capture:
            with sqlite3.connect(capture.database) as connection:
                rows = connection.execute("SELECT state,details FROM execution_history ORDER BY seq").fetchall()
                self.assertFalse(any(state == "returned" for state, _ in rows))
                self.assertEqual(json.loads(rows[-1][1]), {"invocation_id": "typed", "execution_id": "exec", "role": "worker"})
            self.assertNotIn(b"PRIVATE-SENTINEL", capture.database.read_bytes())
            self.assertEqual({path.name for path in capture.private_dir.iterdir()}, {"monitor.sqlite", "metrics"})
        # Failure during projection must not leave a raw runtime DB either.
        with patch("workflow_monitor.preserve_source._copy_monitor", side_effect=RuntimeError("fixture interruption")):
            with self.assertRaisesRegex(RuntimeError, "fixture interruption"):
                capture_stopped(self.source, self._private("interrupted"))
        for path in self._private("interrupted").rglob("*"):
            if path.is_file():
                self.assertNotIn(b"PRIVATE-SENTINEL", path.read_bytes())

    def test_absent_wal_is_not_created_and_existing_wal_bytes_are_unchanged(self):
        wal = self.db.with_name(self.db.name + "-wal")
        shm = self.db.with_name(self.db.name + "-shm")
        self.assertFalse(wal.exists())
        self.assertFalse(shm.exists())
        before = self.db.read_bytes(), self.metric.read_bytes()
        with capture_stopped(self.source, self._private("no-wal")):
            pass
        self.assertFalse(wal.exists())
        self.assertFalse(shm.exists())
        self.assertEqual(before, (self.db.read_bytes(), self.metric.read_bytes()))
        writer = sqlite3.connect(self.db)
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("UPDATE execution_monitor_runs SET started_at=started_at+1")
        writer.commit()
        stopped_database, stopped_wal = self.db.read_bytes(), wal.read_bytes()
        writer.close()
        # Reconstruct only this created fixture's stopped WAL state without -shm.
        self.db.write_bytes(stopped_database)
        wal.write_bytes(stopped_wal)
        self.assertFalse(shm.exists())
        with capture_stopped(self.source, self._private("wal-without-shm")) as capture:
            with sqlite3.connect(capture.database) as copied:
                self.assertEqual(copied.execute("SELECT started_at FROM execution_monitor_runs WHERE run_id='kept'").fetchone()[0], 2.0)
            self.assertEqual((self.db.read_bytes(), wal.read_bytes()), (stopped_database, stopped_wal))
        self.assertEqual((self.db.read_bytes(), wal.read_bytes()), (stopped_database, stopped_wal))
        self.assertEqual(self.metric.read_bytes(), before[1])

    def test_metric_drift_between_copy_and_fingerprint_is_rejected(self):
        from workflow_monitor import preserve_source
        original = preserve_source._source_fingerprint
        def drift(source, run_ids=None):
            if run_ids:
                self.metric.write_bytes(self.metric.read_bytes() + b"changed")
            return original(source, run_ids)
        with patch.object(preserve_source, "_source_fingerprint", drift):
            with self.assertRaisesRegex(CaptureError, "metric changed during capture"):
                capture_stopped(self.source, self._private("metric-race"))

    def test_absent_partial_and_unsafe_metrics_remain_honest(self):
        self.metric.write_bytes(self.metric.read_bytes() + b'{invalid json}\npartial')
        expected = self.metric.read_bytes()
        with capture_stopped(self.source, self._private("partial")) as capture:
            self.assertEqual((capture.metrics / self.metric.name).read_bytes(), expected)
        self.metric.unlink()  # only this test-created artifact
        with capture_stopped(self.source, self._private("absent")) as capture:
            self.assertEqual(capture.summary["metrics"][self.metric.name]["availability"], "absent")
            self.assertFalse((capture.metrics / self.metric.name).exists())
        target = self.metric.with_suffix(".fixture")
        target.write_bytes(expected)
        self.metric.symlink_to(target)
        with self.assertRaisesRegex(CaptureError, "unsafe or unreadable"):
            capture_stopped(self.source, self._private("unsafe"))
        self.assertEqual(target.read_bytes(), expected)

    def test_rejects_main_and_existing_preparation(self):
        with self.assertRaisesRegex(CaptureError, "linked worktree"):
            capture_stopped(self.main, self._private("wrong"))
        self._private("exists").mkdir(parents=True)
        with self.assertRaisesRegex(CaptureError, "already exists"):
            capture_stopped(self.source, self._private("exists"))


if __name__ == "__main__":
    unittest.main()
