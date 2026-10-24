"""Actual preserved-store Reader fixtures, never a generic archive reader."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))

from coherence_workflow.metric_artifacts import create_artifact
from coherence_workflow.metrics import interval_record
from coherence_workflow.store import Authority, git
from workflow_monitor.mapping import normalize
from workflow_monitor.public import minimize
from workflow_monitor.reader import Reader, ReaderError


class PreservedRecordingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.main = Path(self.tmp.name) / "main"; self.main.mkdir()
        git(self.main, "init", "-q"); git(self.main, "config", "user.name", "Fixture")
        git(self.main, "config", "user.email", "fixture@example.invalid")
        (self.main / "tracked").write_text("main\n")
        git(self.main, "add", "tracked"); git(self.main, "commit", "-qm", "main")
        self.source = Path(self.tmp.name) / "stopped source"
        git(self.main, "worktree", "add", "-qb", "stopped", str(self.source))
        self.base = git(self.source, "rev-parse", "HEAD").decode().strip()
        with Authority(self.source) as owner:
            owner.store.start("kept", self.base)
            owner.store.db.execute("INSERT INTO execution_monitor_runs(run_id,recording_version,description,started_at,runner_identity) VALUES(?,?,?,?,?)", ("kept", 1, "{}", 1.0, json.dumps({"pid": 1})))
            owner.store.db.execute("INSERT INTO execution_monitor_runs(run_id,recording_version,description,started_at,runner_identity) VALUES(?,?,?,?,?)", ("unsupported", 2, "{}", 2.0, None))
            owner.store.db.execute("INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)", ("kept", 1, "first", "worker", None, "started", 1.0, json.dumps({"invocation_id": "call", "role": "worker"})))
            owner.store.db.execute("INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)", ("kept", 1, "second", "worker", None, "returned", 2.0, json.dumps({"invocation_id": "call", "role": "worker"})))
            owner.store.review_dispatch("kept", "review", review_base=self.base, review_head=self.base)
            owner.store.review_outcome("kept", "review", "rejected", findings=["tracked:1 - preserved finding"])
            artifact = create_artifact(self.source, "kept", authority=owner)
            artifact.append({"version": 1, "run_id": "kept", "invocation_id": "call", "task_id": None,
                             "role": "worker", "outcome": "settled", "fixing_round": None, "review_ordinal": None,
                             "interval": interval_record(None, None), "before": None, "after": None,
                             "selected_session_mode": "unknown", "actual_session_mode": "unknown",
                             "session_selection_reason": "fixture", "actual_session_id": None})
        self.source_db = self.source / ".coherence/workflow/workflow.sqlite"
        self.source_metric = self.source / ".coherence" / "metrics" / ("run-" + hashlib.sha256(b"kept").hexdigest() + ".jsonl")

    def _publish_fixture(self, state="complete"):
        directory = self.main / ".coherence/preserved-recordings/capture-1"
        (directory / "metrics").mkdir(parents=True)
        shutil.copyfile(self.source_db, directory / "monitor.sqlite")
        shutil.copyfile(self.source_metric, directory / "metrics" / self.source_metric.name)
        (directory / "recording.json").write_text(json.dumps({"version": 1, "state": state, "recording_id": "capture-1", "origin_id": "origin-1"}))
        return directory

    def test_complete_reader_survives_removed_source_and_does_not_write(self):
        directory = self._publish_fixture()
        source_bytes = {path: path.read_bytes() for path in (self.source_db, self.source_metric)}
        source_snapshot = Reader(self.source).open_snapshot()
        main_tracked = (self.main / "tracked").read_bytes()
        self.assertEqual(source_bytes, {path: path.read_bytes() for path in source_bytes})
        git(self.main, "worktree", "remove", "--force", str(self.source))
        self.assertFalse(self.source.exists())
        reader = Reader.preserved(self.main, "capture-1")
        before = {path: path.read_bytes() for path in directory.rglob("*") if path.is_file()}
        snapshot = reader.open_snapshot()
        public = minimize(normalize(snapshot))
        self.assertEqual(reader.recording_identity, ("capture-1", "origin-1"))
        self.assertEqual([row["run_id"] for row in snapshot["runs"]], ["kept"])
        self.assertEqual(snapshot["unsupported_run_ids"], ["unsupported"])
        self.assertEqual([row["seq"] for row in snapshot["observations"]], sorted(row["seq"] for row in snapshot["observations"]))
        self.assertIsNone(snapshot["runs"][0]["runner_identity"])
        self.assertEqual(snapshot["review_details"][1]["findings"], ["tracked:1 - preserved finding"])
        self.assertEqual(public["state"], "ok")
        self.assertEqual(snapshot["metrics"]["kept"], source_snapshot["metrics"]["kept"])
        self.assertEqual((self.main / "tracked").read_bytes(), main_tracked)
        self.assertEqual(before, {path: path.read_bytes() for path in directory.rglob("*") if path.is_file()})
        # The source bytes were copied, never adopted or rewritten before removal.
        self.assertTrue(all(value for value in source_bytes.values()))

    def test_pending_unsafe_and_replaced_recordings_are_not_adopted(self):
        directory = self._publish_fixture("preparing")
        with self.assertRaisesRegex(ReaderError, "invalid preserved metadata"):
            Reader.preserved(self.main, "capture-1")
        (directory / "recording.json").write_text(json.dumps({"version": 1, "state": "complete", "recording_id": "capture-1", "origin_id": "origin-1"}))
        reader = Reader.preserved(self.main, "capture-1")
        replacement = directory / "replacement.sqlite"
        replacement.write_bytes((directory / "monitor.sqlite").read_bytes())
        replacement.replace(directory / "monitor.sqlite")
        self.assertEqual(reader.open_snapshot()["state"], "unavailable")

    def test_partial_malformed_and_absent_metrics_remain_qualified(self):
        directory = self._publish_fixture()
        metric = directory / "metrics" / self.source_metric.name
        metric.write_bytes(metric.read_bytes() + b'{not json}\npartial')
        snapshot = Reader.preserved(self.main, "capture-1").open_snapshot("kept")
        self.assertEqual(snapshot["metrics"]["kept"]["coverage"], "partial")
        self.assertIn("invalid_record", snapshot["metrics"]["kept"]["reasons"])
        self.assertIn("incomplete_tail", snapshot["metrics"]["kept"]["reasons"])
        metric.unlink()
        absent = Reader.preserved(self.main, "capture-1").open_snapshot("kept")["metrics"]["kept"]
        self.assertEqual(absent["coverage"], "unavailable")
        self.assertIn("metric_artifact_missing", absent["reasons"])


if __name__ == "__main__":
    unittest.main()
