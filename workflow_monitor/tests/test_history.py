"""Snapshot-bound history checks use a local SQLite writer fixture; no provider is invoked."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from coherence_workflow.monitoring import Recorder, descriptor
from coherence_workflow.store import Authority, git
from workflow_monitor.app import create_app
from workflow_monitor.reader import Reader


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "project"; self.project.mkdir()
        git(self.project, "init", "-q"); git(self.project, "config", "user.name", "Fixture"); git(self.project, "config", "user.email", "fixture@example.invalid")
        (self.project / "tracked").write_text("fixture\n"); git(self.project, "add", "tracked"); git(self.project, "commit", "-qm", "fixture")
        base = git(self.project, "rev-parse", "HEAD").decode().strip()
        with Authority(self.project) as owner:
            owner.store.start("history", base)
            recorder = Recorder(owner.store, "history")
            recorder.register(descriptor({"tasks": [{"id": "one", "depends": []}]}, {}))
            for number in range(51):
                occurrence = recorder.occurrence()
                recorder.emit(occurrence, "worker", "started", task_id="one", facts={"role": "worker"})
                recorder.emit(occurrence, "worker", "failed" if number == 0 else "passed", task_id="one", facts={"role": "worker"})
            owner.store.db.execute("INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)", ("history", 1, "future", "worker", None, "future_kind", 1.0, json.dumps({"PRIVATE-SENTINEL": "never public"})))
        assets = Path(self.tmp.name) / "assets"; assets.mkdir(); (assets / "index.html").write_text("ok")
        self.client = TestClient(create_app(Reader(self.project), assets, 8765), base_url="http://127.0.0.1:8765")
        self.headers = {"sec-fetch-site": "same-origin", "x-workflow-monitor": "1"}

    def test_pages_reconcile_and_reveal_every_retained_record(self):
        run = self.client.get("/api/monitor/v1/runs", headers=self.headers).json()["runs"][0]["ref"]
        initial = self.client.get(f"/api/monitor/v1/runs/{run}/snapshot", headers=self.headers)
        self.assertEqual(initial.status_code, 200); first = initial.json()
        self.assertEqual((first["inventory"]["total_count"], first["inventory"]["loaded_count"], first["inventory"]["hidden_count"], first["inventory"]["unsupported_count"]), (103, 50, 53, 1))
        pages = [first]
        while pages[-1]["next_cursor"]:
            page = self.client.get(f"/api/monitor/v1/runs/{run}/history?snapshot={pages[-1]['snapshot_ref']}&cursor={pages[-1]['next_cursor']}", headers=self.headers)
            self.assertEqual(page.status_code, 200); pages.append(page.json())
        retained = [item for page in pages for item in page["records"] + page["unknown_records"]]
        self.assertEqual(len(retained), 103)
        for item in retained:
            detail = self.client.get(f"/api/monitor/v1/runs/{run}/records/{item['ref']}?snapshot={pages[-1]['snapshot_ref']}", headers=self.headers)
            self.assertEqual(detail.status_code, 200)
            self.assertEqual(detail.json()["ref"], item["ref"])
            self.assertNotIn("PRIVATE-SENTINEL", detail.text)
        self.assertTrue(any(item["kind"] == "failed" for item in retained if "kind" in item))

    def test_conflict_and_bad_or_cross_run_detail_are_rejected(self):
        run = self.client.get("/api/monitor/v1/runs", headers=self.headers).json()["runs"][0]["ref"]
        view = self.client.get(f"/api/monitor/v1/runs/{run}/snapshot", headers=self.headers).json()
        self.assertEqual(self.client.get(f"/api/monitor/v1/runs/{run}/history?snapshot=stale&cursor={view['next_cursor']}", headers=self.headers).status_code, 409)
        self.assertEqual(self.client.get(f"/api/monitor/v1/runs/{run}/history?snapshot={view['snapshot_ref']}&cursor=bad", headers=self.headers).status_code, 400)
        self.assertEqual(self.client.get(f"/api/monitor/v1/runs/{run}/records/record_not_this_run?snapshot={view['snapshot_ref']}", headers=self.headers).status_code, 404)


if __name__ == "__main__":
    unittest.main()
