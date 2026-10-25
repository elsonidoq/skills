"""Offline adapters exercise real Engine/Git records through the shipped monitor HTTP path."""
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

from starlette.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from coherence_workflow.engine import Engine
from coherence_workflow.store import Authority, Blocked, git
from workflow_monitor.app import create_app
from workflow_monitor.mapping import normalize
from workflow_monitor.reader import Reader

EXECUTOR = {"provider": "offline", "model": "lineage-fixture", "effort": "medium",
            "reviewer": {"provider": "offline", "model": "lineage-review-fixture", "effort": "medium"}}


class LineageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name) / "project"; self.project.mkdir()
        git(self.project, "init", "-q"); git(self.project, "config", "user.name", "Fixture"); git(self.project, "config", "user.email", "fixture@example.invalid")
        (self.project / "tracked").write_text("base\n"); git(self.project, "add", "tracked"); git(self.project, "commit", "-qm", "base")
        self.base = git(self.project, "rev-parse", "HEAD").decode().strip()
        self.assets = Path(self.tmp.name) / "assets"; self.assets.mkdir(); (self.assets / "index.html").write_text("safe")

    def _run(self, run_id, contract, approved):
        project = self.project
        class OfflineAdapter:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get("read_only"):
                    return '{"approved":true,"findings":[]}' if approved else '{"approved":false,"findings":["tracked@1:1 - fixture defect impacts workflow lineage"]}'
                kwargs["claim"](run_id + ".txt")
                (project / (run_id + ".txt")).write_text("changed\n")
                return "offline adapter"
        with Authority(project) as owner:
            return Engine(owner, run_id, contract, EXECUTOR, adapter=OfflineAdapter).invoke()

    def test_real_rejected_and_full_range_rereview_flow_through_reader_mapper_and_http(self):
        with self.assertRaisesRegex(Blocked, "owner authorization unavailable"):
            self._run("original", {"tasks": [{"id": "original", "description": "Original"}]}, False)
        with sqlite3.connect(self.project / ".coherence/workflow/workflow.sqlite") as db:
            review_id = db.execute("SELECT occurrence_id FROM execution_observations WHERE run_id='original' AND phase='review' AND kind='failed'").fetchone()[0]
            original_terminal = [row[0] for row in db.execute("SELECT kind FROM execution_observations WHERE run_id='original' AND phase='terminal'")]
        self.assertIn("failed", original_terminal)
        self.assertEqual(self._run("fixing", {"monitor": {"correction_of": {"run_id": "original", "review_execution_id": review_id}}, "review_base": self.base,
                                                "tasks": [{"id": "fix", "description": "Fix", "checks": [[sys.executable, "-B", "-c", "assert True"]]}]}, True)["status"], "complete")
        reader = Reader(self.project)
        graph = normalize(reader.open_snapshot())
        self.assertEqual(graph["followups"], [{"run_id": "fixing", "source_run_id": "original", "review_occurrence_id": review_id, "resolution": "resolved"}])
        self.assertEqual(graph["review_acceptance"]["original"]["state"], "accepted_full_range")
        self.assertEqual(graph["review_acceptance"]["original"]["base"], self.base)
        client = TestClient(create_app(reader, self.assets, 8765), base_url="http://127.0.0.1:8765")
        headers = {"sec-fetch-site": "same-origin", "x-workflow-monitor": "1"}
        runs = client.get("/api/monitor/v1/runs", headers=headers).json()["runs"]
        original = next(item for item in runs if item["review_acceptance"]["state"] == "accepted_full_range")
        view = client.get(f"/api/monitor/v1/runs/{original['ref']}/snapshot", headers=headers).json()
        followups = client.get(f"/api/monitor/v1/runs/{original['ref']}/followups?snapshot={view['snapshot_ref']}", headers=headers)
        self.assertEqual(followups.status_code, 200)
        self.assertEqual(followups.json()["followups"][0]["resolution"], "resolved")
        self.assertNotIn("fixture defect", str(view))
        with sqlite3.connect(self.project / ".coherence/workflow/workflow.sqlite") as db:
            fixing_review = db.execute("SELECT occurrence_id FROM execution_observations WHERE run_id='fixing' AND phase='review' AND kind='passed'").fetchone()[0]
        self.assertEqual(self._run("later", {"monitor": {"correction_of": {"run_id": "fixing", "review_execution_id": fixing_review}},
                                               "tasks": [{"id": "later", "description": "Later"}]}, True)["status"], "complete")
        self.assertEqual(normalize(reader.open_snapshot())["review_acceptance"]["original"]["state"], "correction_only")

    def test_reviewer_only_or_no_check_corrections_cannot_accept_a_repair_chain(self):
        def rejected(name):
            with self.assertRaisesRegex(Blocked, "owner authorization unavailable"):
                self._run(name, {"tasks": [{"id": name, "description": "Original"}]}, False)
            with sqlite3.connect(self.project / ".coherence/workflow/workflow.sqlite") as db:
                occurrence, facts = db.execute("SELECT occurrence_id, facts FROM execution_observations WHERE run_id=? AND phase='review' AND kind='failed'", (name,)).fetchone()
                return occurrence, json.loads(facts)["review_base"]

        reviewer_only_review, reviewer_only_base = rejected("reviewer-only-original")
        self.assertEqual(self._run("reviewer-only", {"monitor": {"correction_of": {"run_id": "reviewer-only-original", "review_execution_id": reviewer_only_review}},
                                                       "review_base": reviewer_only_base, "tasks": []}, True)["status"], "complete")
        no_check_review, no_check_base = rejected("no-check-original")
        self.assertEqual(self._run("no-check", {"monitor": {"correction_of": {"run_id": "no-check-original", "review_execution_id": no_check_review}},
                                                  "review_base": no_check_base, "tasks": [{"id": "fix", "description": "Fix"}]}, True)["status"], "complete")
        acceptance = normalize(Reader(self.project).open_snapshot())["review_acceptance"]
        self.assertEqual(acceptance["reviewer-only-original"]["state"], "unknown")
        self.assertEqual(acceptance["no-check-original"]["state"], "unknown")

    def test_dangling_wrong_and_cyclic_declarations_never_accept(self):
        def description(correction):
            return json.dumps({"version": 1, "description_version": 3,
                               "phases": [{"id": "review", "label": "Review", "possible_branches": [], "pre_recording": False}],
                               "tasks": [{"id": "fixture", "depends": [], "label": "Fixture", "work_description": None}],
                               "initial_review": {"planned": True}, "requested_executor": {}, "correction_of": correction})
        sha = "a" * 40
        snapshot = {"state": "ok", "runs": [
            {"run_id": "source", "description": description(None), "started_at": 1},
            {"run_id": "dangling", "description": description({"run_id": "source", "review_execution_id": "missing"}), "started_at": 2},
            {"run_id": "wrong", "description": description({"run_id": "outside", "review_execution_id": "review"}), "started_at": 3},
            {"run_id": "also-dangling", "description": description({"run_id": "source", "review_execution_id": "missing"}), "started_at": 3},
            {"run_id": "conflict-one", "description": description({"run_id": "source", "review_execution_id": "review"}), "started_at": 3},
            {"run_id": "conflict-two", "description": description({"run_id": "source", "review_execution_id": "review"}), "started_at": 3},
            {"run_id": "one", "description": description({"run_id": "two", "review_execution_id": "two-review"}), "started_at": 4},
            {"run_id": "two", "description": description({"run_id": "one", "review_execution_id": "one-review"}), "started_at": 5}], "observations": [
            {"seq": 1, "run_id": "source", "occurrence_id": "review", "phase": "review", "task_id": None, "kind": "failed", "recorded_at": 1, "facts": json.dumps({"role": "reviewer", "review_base": sha, "review_head": sha, "approved": False, "finding_count": 1})},
            {"seq": 2, "run_id": "one", "occurrence_id": "one-review", "phase": "review", "task_id": None, "kind": "passed", "recorded_at": 2, "facts": json.dumps({"role": "reviewer", "review_base": sha, "review_head": sha, "approved": True, "finding_count": 0})},
            {"seq": 3, "run_id": "two", "occurrence_id": "two-review", "phase": "review", "task_id": None, "kind": "passed", "recorded_at": 3, "facts": json.dumps({"role": "reviewer", "review_base": sha, "review_head": sha, "approved": True, "finding_count": 0})}]}
        graph = normalize(snapshot)
        self.assertEqual({item["resolution"] for item in graph["followups"]}, {"unresolved", "conflicting", "cyclic"})
        self.assertNotIn("accepted_full_range", {item["state"] for item in graph["review_acceptance"].values()})


if __name__ == "__main__":
    unittest.main()
