"""Local writer/reader observation checks; all writer fixtures are offline."""
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest

from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from coherence_workflow.monitoring import Recorder, descriptor
from coherence_workflow.store import Authority, git
from workflow_monitor.app import create_app
from workflow_monitor.reader import Reader


def identity(pid: int) -> dict[str, object]:
    stat = Path(f"/proc/{pid}/stat").read_text()
    fields = stat[stat.rindex(")") + 2:].split()
    return {"pid": pid, "start": fields[19], "boot": Path("/proc/sys/kernel/random/boot_id").read_text().strip(), "uid": os.geteuid()}


class FlakyReader:
    def __init__(self, reader): self.reader, self.fail = reader, False
    def open_snapshot(self):
        if self.fail: raise OSError("PRIVATE-SENTINEL")
        return self.reader.open_snapshot()


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "project"; self.project.mkdir()
        git(self.project, "init", "-q"); git(self.project, "config", "user.name", "Fixture"); git(self.project, "config", "user.email", "fixture@example.invalid")
        (self.project / "tracked").write_text("fixture\n"); git(self.project, "add", "tracked"); git(self.project, "commit", "-qm", "fixture")
        self.base = git(self.project, "rev-parse", "HEAD").decode().strip()
        with Authority(self.project) as owner:
            owner.store.start("live", self.base)
            recorder = Recorder(owner.store, "live")
            recorder.register(descriptor({"tasks": [{"id": "one", "depends": []}]}, {}), identity(os.getpid()))
            self.occurrence = recorder.occurrence()
            recorder.emit(self.occurrence, "worker", "started", task_id="one", facts={"role": "worker"})
        assets = Path(self.tmp.name) / "assets"; assets.mkdir(); (assets / "index.html").write_text("safe")
        self.flaky = FlakyReader(Reader(self.project))
        self.client = TestClient(create_app(self.flaky, assets, 8765), base_url="http://127.0.0.1:8765")
        self.headers = {"sec-fetch-site": "same-origin", "x-workflow-monitor": "1"}

    def _snapshot(self):
        run = self.client.get("/api/monitor/v1/runs", headers=self.headers).json()["runs"][0]["ref"]
        response = self.client.get(f"/api/monitor/v1/runs/{run}/snapshot", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_failed_read_keeps_safe_view_and_recovery_refreshes(self):
        initial = self._snapshot()
        self.assertEqual(initial["observation"]["read_state"], "current")
        self.assertEqual(initial["runs"][0]["runner_state"]["state"], "live")
        self.assertEqual(initial["occurrences"][0]["completeness"], "incomplete")
        self.flaky.fail = True
        failed = self._snapshot()
        self.assertEqual(failed["observation"]["read_state"], "unavailable")
        self.assertEqual(failed["observation"]["last_success_at"], initial["observation"]["last_success_at"])
        self.assertEqual(failed["records"], initial["records"])
        self.assertIn("read_unavailable", failed["observation"]["warnings"])
        self.assertNotIn("PRIVATE-SENTINEL", str(failed))
        self.flaky.fail = False
        with Authority(self.project) as owner:
            owner.store.append_monitor_observation("live", self.occurrence, "worker", None, "passed", {"role": "worker"})
        recovered = self._snapshot()
        self.assertEqual(recovered["observation"]["read_state"], "current")
        self.assertEqual([row["kind"] for row in recovered["records"]], ["started", "passed"])
        self.assertNotIn("incomplete_history", recovered["observation"]["warnings"])

    def test_stopped_unknown_zero_and_gap_remain_distinct_without_repair(self):
        database = self.project / ".coherence/workflow/workflow.sqlite"
        with Authority(self.project) as owner:
            owner.store.db.execute("UPDATE execution_monitor_runs SET runner_identity=? WHERE run_id='live'", (json.dumps({"pid": 999999, "start": "1", "boot": identity(os.getpid())["boot"], "uid": os.geteuid()}),))
            owner.store.append_monitor_observation("live", self.occurrence, "check", None, "passed", {"exit_code": 0})
            owner.store.append_monitor_observation("live", "gap", "terminal", None, "gap", {"recording_gap": True})
        stopped = self._snapshot()
        self.assertEqual(stopped["runs"][0]["runner_state"]["state"], "stopped")
        self.assertEqual(next(row["exit_code"] for row in stopped["records"] if row["kind"] == "passed"), 0)
        self.assertIn("gap", [row["kind"] for row in stopped["records"]])
        with Authority(self.project) as owner:
            owner.store.db.execute("UPDATE execution_monitor_runs SET runner_identity='not-json' WHERE run_id='live'")
        before = database.read_bytes()
        unknown = self._snapshot()
        self.assertEqual(unknown["runs"][0]["runner_state"]["state"], "unknown")
        self.assertEqual(database.read_bytes(), before)

    def test_concurrent_writer_read_has_no_writer_stall(self):
        ready, done, failures = threading.Event(), threading.Event(), []
        def writer():
            try:
                with Authority(self.project) as owner:
                    ready.set()
                    for number in range(8):
                        owner.store.append_monitor_observation("live", f"writer-{number}", "worker", None, "returned", {"role": "worker"})
                        time.sleep(.01)
            except BaseException as exc: failures.append(exc)
            finally: done.set()
        thread = threading.Thread(target=writer); thread.start(); self.assertTrue(ready.wait(5))
        reader = Reader(self.project)
        while not done.is_set(): self.assertEqual(reader.open_snapshot("live")["state"], "ok")
        thread.join(5); self.assertFalse(failures)
        self.assertGreaterEqual(len(reader.open_snapshot("live")["observations"]), 9)


if __name__ == "__main__":
    unittest.main()
