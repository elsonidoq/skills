"""Focused reader boundary tests; runtime fixtures are labelled offline/local."""
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))

from coherence_workflow.store import Authority, git  # local actual script writer fixture
from workflow_monitor.reader import Reader


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "project"
        self.project.mkdir()
        git(self.project, "init", "-q")
        git(self.project, "config", "user.name", "Fixture")
        git(self.project, "config", "user.email", "fixture@example.invalid")
        (self.project / "tracked").write_text("fixture\n")
        git(self.project, "add", "tracked")
        git(self.project, "commit", "-qm", "fixture")
        self.base = git(self.project, "rev-parse", "HEAD").decode().strip()

    def _record(self, run="run", version=1):
        with Authority(self.project) as writer:
            writer.store.start(run, self.base)
            writer.store.db.execute("PRAGMA journal_mode=WAL")
            writer.store.db.execute(
                "INSERT INTO execution_monitor_runs(run_id,recording_version,description,started_at,runner_identity) VALUES(?,?,?,?,?)",
                (run, version, "{}", 1.0, None),
            )
            writer.store.db.execute(
                "INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)",
                (run, version, "occurrence", "worker", None, "started", 2.0, "{}"),
            )

    def test_wal_snapshot_reads_actual_writer_updates_without_mutation(self):
        self._record()
        database = self.project / ".coherence/workflow/workflow.sqlite"
        with sqlite3.connect(database) as check:
            before = list(check.execute("SELECT run_id, recording_version, description FROM execution_monitor_runs"))
        reader = Reader(self.project)
        self.assertEqual(reader.open_snapshot()["state"], "ok")
        with Authority(self.project) as writer:
            writer.store.append_monitor_observation("run", "next", "worker", None, "returned", {})
        snapshot = reader.open_snapshot("run")
        self.assertEqual([row["occurrence_id"] for row in snapshot["observations"]], ["occurrence", "next"])
        with sqlite3.connect(database) as check:
            self.assertEqual(list(check.execute("SELECT run_id, recording_version, description FROM execution_monitor_runs")), before)

    def test_writer_progresses_while_reader_reopens_short_snapshots(self):
        self._record()
        ready, done, failure = threading.Event(), threading.Event(), []

        def writer():
            try:
                with Authority(self.project) as owner:
                    ready.set()
                    for number in range(20):
                        owner.store.append_monitor_observation("run", "w" + str(number), "worker", None, "returned", {})
                done.set()
            except BaseException as exc:  # assertion reported by test thread
                failure.append(exc)
                done.set()

        thread = threading.Thread(target=writer)
        thread.start()
        self.assertTrue(ready.wait(5))
        reader = Reader(self.project)
        while not done.is_set():
            self.assertEqual(reader.open_snapshot("run")["state"], "ok")
        thread.join(5)
        self.assertFalse(failure)
        self.assertEqual(len(reader.open_snapshot("run")["observations"]), 21)

    def test_missing_unsupported_and_forbidden_sql_are_closed(self):
        self.assertEqual(Reader(self.project).open_snapshot()["state"], "no_store")
        self.assertFalse((self.project / ".coherence/workflow/workflow.sqlite").exists())
        self._record("newer", version=2)
        reader = Reader(self.project)
        snapshot = reader.open_snapshot()
        self.assertEqual(snapshot["state"], "unsupported")
        self.assertEqual(snapshot["unsupported_run_ids"], ["newer"])
        database = self.project / ".coherence/workflow/workflow.sqlite"
        connection = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)
        try:
            connection.execute("PRAGMA query_only=ON")
            connection.set_authorizer(reader._authorizer)
            with self.assertRaises(sqlite3.DatabaseError):
                connection.execute("DELETE FROM execution_monitor_runs")
            with self.assertRaises(sqlite3.DatabaseError):
                connection.execute("ATTACH DATABASE ':memory:' AS forbidden")
        finally:
            connection.close()

    def test_review_attempt_history_is_retained_in_order(self):
        self._record()
        with Authority(self.project) as writer:
            writer.store.review_dispatch('run', 'review', review_base=self.base, review_head=self.base)
            writer.store.review_outcome('run', 'review', 'rejected', findings=['tracked:1 - safe finding'])
            writer.store.review_outcome('run', 'review', 'approved', findings=[])
        details = Reader(self.project).open_snapshot('run')['review_details']
        self.assertEqual([item['outcome'] for item in details], ['dispatched', 'rejected', 'approved'])
        self.assertEqual(details[1]['findings'], ['tracked:1 - safe finding'])

    def test_symlink_ownership_and_substitution_are_rejected(self):
        self._record()
        database = self.project / ".coherence/workflow/workflow.sqlite"
        reader = Reader(self.project)
        replacement = database.with_name("replacement.sqlite")
        replacement.write_bytes(database.read_bytes())
        os.replace(replacement, database)
        self.assertEqual(reader.open_snapshot()["state"], "unavailable")

        # A newly selected symlinked store and an unsafe permission mode are both rejected.
        other = self.project / "other.sqlite"
        other.write_text("not a database")
        database.unlink()
        database.symlink_to(other)
        with self.assertRaises(Exception):
            Reader(self.project)
        database.unlink()
        other.replace(database)
        database.chmod(0o666)
        with self.assertRaises(Exception):
            Reader(self.project)


if __name__ == "__main__":
    unittest.main()
