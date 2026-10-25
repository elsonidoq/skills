"""Actual subprocess publication tests over the stopped-source Git/SQLite fixture."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sqlite3
import sys
from unittest.mock import patch

from workflow_monitor.tests.test_preserve_source import PreserveSourceTests
from workflow_monitor.reader import Reader
from workflow_monitor import preserve as preserve_module

ROOT = Path(__file__).resolve().parents[2]


class PreserveCommandTests(PreserveSourceTests):
    def _command(self):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = os.pathsep.join(filter(None, [str(ROOT), str(ROOT / "runtime"), environment.get("PYTHONPATH")]))
        return subprocess.run([sys.executable, "-B", "-m", "workflow_monitor.preserve", "--source-worktree", str(self.source)],
                              capture_output=True, text=True, env=environment, cwd=ROOT)

    def _published(self):
        root = self.main / ".coherence" / "preserved-recordings"
        entries = [path for path in root.iterdir() if path.is_dir()]
        self.assertEqual(len(entries), 1)
        return entries[0]

    def test_subprocess_publishes_complete_reader_verified_capture_and_exact_repeat_reuses_it(self):
        source_before = {path: path.read_bytes() for path in (self.db, self.metric)}
        main_before = (self.main / "tracked").read_bytes()
        index_before = subprocess.check_output(["git", "-C", str(self.main), "diff", "--cached", "--binary"])
        first = self._command()
        self.assertEqual(first.returncode, 0, first.stderr)
        result = json.loads(first.stdout.removeprefix("preserved "))
        self.assertFalse(result["reused"])
        self.assertEqual(result["readback"], "verified")
        directory = self._published()
        self.assertEqual(json.loads((directory / "recording.json").read_text())["state"], "complete")
        self.assertEqual(Reader.preserved(self.main, result["recording_id"]).open_snapshot()["state"], "ok")
        published_before = {path.relative_to(directory): path.read_bytes() for path in directory.rglob("*") if path.is_file()}
        second = self._command()
        self.assertEqual(second.returncode, 0, second.stderr)
        repeated = json.loads(second.stdout.removeprefix("preserved "))
        self.assertTrue(repeated["reused"])
        self.assertEqual(repeated["recording_id"], result["recording_id"])
        self.assertEqual(published_before, {path.relative_to(directory): path.read_bytes() for path in directory.rglob("*") if path.is_file()})
        self.assertEqual(source_before, {path: path.read_bytes() for path in source_before})
        self.assertEqual(main_before, (self.main / "tracked").read_bytes())
        self.assertEqual(index_before, subprocess.check_output(["git", "-C", str(self.main), "diff", "--cached", "--binary"]))

    def test_changed_source_reports_retained_mismatch_without_overwriting_prior_capture(self):
        self.assertEqual(self._command().returncode, 0)
        directory = self._published()
        before = {path.relative_to(directory): path.read_bytes() for path in directory.rglob("*") if path.is_file()}
        # A changed stopped source is not an incremental update.  Alter an actual source
        # metric byte so the T003 fingerprint and command's content-derived ID differ.
        self.metric.write_bytes(self.metric.read_bytes() + b"partial")
        result = self._command()
        self.assertEqual(result.returncode, 2)
        self.assertIn("source differs from a prior stopped capture", result.stderr)
        self.assertIn("retain both source and prior capture", result.stderr)
        self.assertEqual(before, {path.relative_to(directory): path.read_bytes() for path in directory.rglob("*") if path.is_file()})
        self.assertTrue(self.source.exists())

    def test_final_source_drift_after_readback_cannot_report_success(self):
        original = preserve_module._readback

        def drift_after_readback(*args, **kwargs):
            result = original(*args, **kwargs)
            self.metric.write_bytes(self.metric.read_bytes() + b"partial")
            return result

        with patch.object(preserve_module, "_readback", drift_after_readback):
            with self.assertRaisesRegex(preserve_module.PreserveError, "source changed after capture"):
                preserve_module.preserve(self.source)
        # The no-overwrite boundary may leave completed bytes for inspection, but the
        # source remains and callers received no preservation success.
        self.assertTrue(self.source.exists())
        self.assertTrue((self.main / ".coherence" / "preserved-recordings").exists())

    def test_repeat_rejects_same_count_fact_and_metric_tampering(self):
        first = self._command()
        self.assertEqual(first.returncode, 0, first.stderr)
        directory = self._published()
        database = directory / "monitor.sqlite"
        before = database.read_bytes()
        with sqlite3.connect(database) as connection:
            connection.execute("UPDATE execution_observations SET facts='{}' WHERE occurrence_id='first'")
        tampered = database.read_bytes()
        result = self._command()
        self.assertEqual(result.returncode, 2)
        self.assertIn("retained monitor facts differ", result.stderr)
        self.assertEqual(database.read_bytes(), tampered)
        database.write_bytes(before)  # restore only this test-created capture
        metric = directory / "metrics" / self.metric.name
        metric.write_bytes(metric.read_bytes() + b"partial")
        tampered_metric = metric.read_bytes()
        result = self._command()
        self.assertEqual(result.returncode, 2)
        self.assertIn("metric bytes differ", result.stderr)
        self.assertEqual(metric.read_bytes(), tampered_metric)
        self.assertTrue(self.source.exists())

    def test_repeat_is_content_based_and_unknown_observations_are_retained(self):
        with sqlite3.connect(self.db) as connection:
            connection.execute("INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?)", ("unknown", 9, "future", "future", "future", 3.0, '{malformed'))
        first = self._command()
        self.assertEqual(first.returncode, 0, first.stderr)
        with sqlite3.connect(self.db) as connection:
            connection.execute("CREATE TABLE unrelated(secret TEXT)")
            connection.execute("INSERT INTO unrelated VALUES('private')")
        repeat = self._command()
        self.assertEqual(repeat.returncode, 0, repeat.stderr)
        self.assertTrue(json.loads(repeat.stdout.removeprefix("preserved "))["reused"])
        directory = self._published()
        with sqlite3.connect(directory / "monitor.sqlite") as connection:
            self.assertEqual(connection.execute("SELECT facts FROM execution_observations WHERE occurrence_id='future'").fetchone()[0], '{malformed')
            self.assertIsNone(connection.execute("SELECT name FROM sqlite_master WHERE name='unrelated'").fetchone())

    def test_interruption_before_complete_metadata_stays_invisible_and_retry_does_not_overwrite(self):
        from workflow_monitor.projects import Projects
        with patch.object(preserve_module, "_write_metadata", side_effect=OSError("fixture interruption")):
            with self.assertRaisesRegex(preserve_module.PreserveError, "cannot publish complete capture"):
                preserve_module.preserve(self.source)
        directory = self._published()
        before = {path.relative_to(directory): path.read_bytes() for path in directory.rglob("*") if path.is_file()}
        project = Projects(self.main.parent).inventory()[0]
        self.assertNotIn("preserved", {recording.label for recording in project.recordings})
        retry = self._command()
        self.assertEqual(retry.returncode, 2)
        self.assertIn("incomplete or unsafe", retry.stderr)
        self.assertEqual(before, {path.relative_to(directory): path.read_bytes() for path in directory.rglob("*") if path.is_file()})
        self.assertFalse((directory / "recording.json").exists())
        self.assertTrue(self.source.exists())

    def test_existing_conflicting_target_is_not_overwritten_and_pending_is_not_reader_visible(self):
        # A private command-owned preparation directory is not under the public root.
        private = self.main / ".coherence" / "preserve-pending"
        private.mkdir(parents=True)
        self.assertFalse((self.main / ".coherence" / "preserved-recordings").exists())
        self.assertEqual(self._command().returncode, 0)
        directory = self._published()
        database = directory / "monitor.sqlite"
        before = database.read_bytes()
        # An uncertain retry facing an existing complete capture verifies it instead of
        # copying over its bytes.
        self.assertEqual(self._command().returncode, 0)
        self.assertEqual(before, database.read_bytes())
        self.assertEqual(hashlib.sha256(before).digest(), hashlib.sha256(database.read_bytes()).digest())


if __name__ == "__main__":
    import unittest
    unittest.main()
