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

    def test_rejects_main_and_existing_preparation(self):
        with self.assertRaisesRegex(CaptureError, "linked worktree"):
            capture_stopped(self.main, self._private("wrong"))
        self._private("exists").mkdir(parents=True)
        with self.assertRaisesRegex(CaptureError, "already exists"):
            capture_stopped(self.source, self._private("exists"))


if __name__ == "__main__":
    unittest.main()
