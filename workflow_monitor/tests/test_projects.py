"""Actual Git/SQLite fixtures for read-only multi-worktree discovery."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))

from coherence_workflow.store import Authority, git
from workflow_monitor.app import create_app
from workflow_monitor.projects import Projects
from workflow_monitor.reader import Reader


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "projects"
        self.root.mkdir()
        self.alpha = self._repository(self.root / "alpha")
        self.beta = self._repository(self.root / "beta")
        self.external = self.base / "external linked worktree"
        git(self.alpha, "worktree", "add", "-qb", "external", str(self.external))
        # This registered immediate child makes discovery encounter the same canonical
        # worktree list twice; it must not create alias recordings.
        self.inside = self.root / "alpha linked"
        git(self.alpha, "worktree", "add", "-qb", "inside", str(self.inside))

    def _repository(self, path: Path) -> Path:
        path.mkdir()
        git(path, "init", "-q")
        git(path, "config", "user.name", "Fixture")
        git(path, "config", "user.email", "fixture@example.invalid")
        (path / "tracked").write_text("fixture\n")
        git(path, "add", "tracked")
        git(path, "commit", "-qm", "fixture")
        return path

    def _record(self, project: Path, run_id: str) -> None:
        commit = git(project, "rev-parse", "HEAD").decode().strip()
        with Authority(project) as owner:
            owner.store.start(run_id, commit)
            owner.store.db.execute(
                "INSERT INTO execution_monitor_runs(run_id,recording_version,description,started_at,runner_identity) VALUES(?,?,?,?,?)",
                (run_id, 1, "{}", 1.0, None),
            )
            owner.store.db.execute(
                "INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)",
                (run_id, 1, "one", "worker", None, "started", 1.0, "{}"),
            )

    def _bytes(self) -> dict[Path, bytes]:
        return {path.relative_to(self.base): path.read_bytes() for path in self.base.rglob("*") if path.is_file() and not path.is_symlink()}

    def test_registered_groups_are_opaque_and_discovery_does_not_read_or_write_snapshots(self):
        self._record(self.alpha, "same")
        self._record(self.external, "same")
        self._record(self.beta, "same")
        self._record(self.inside, "same")
        (self.inside / ".coherence/workflow/workflow.sqlite").chmod(0o666)
        nested = self.alpha / "nested"
        self._repository(nested)
        escape = self.base / "escape"
        self._repository(escape)
        (self.root / "escaped link").symlink_to(escape, target_is_directory=True)
        before = self._bytes()

        with patch.object(Reader, "open_snapshot", side_effect=AssertionError("inventory must not scan snapshots")):
            inventory = Projects(self.root).inventory()

        self.assertEqual(len(inventory), 2)
        alpha_project = next(project for project in inventory if any(recording.worktree == self.alpha for recording in project.recordings))
        self.assertEqual({recording.worktree for recording in alpha_project.recordings}, {self.alpha, self.inside, self.external})
        self.assertEqual([recording.label for recording in alpha_project.recordings].count("main"), 1)
        self.assertEqual({recording.label for recording in alpha_project.recordings}, {"main", "linked"})
        self.assertEqual(next(recording.state for recording in alpha_project.recordings if recording.worktree == self.inside), "unavailable")
        self.assertTrue(all("/" not in project.ref and "/" not in recording.ref for project in inventory for recording in project.recordings))
        self.assertEqual(before, self._bytes())
        self.assertTrue(any(recording.reader is not None and recording.worktree == self.alpha
                            for project in inventory for recording in project.recordings))

        main = next(recording for recording in alpha_project.recordings if recording.label == "main")
        linked = next(recording for recording in alpha_project.recordings if recording.worktree == self.external)
        self.assertEqual(main.reader.open_snapshot("same")["state"], "ok")
        self.assertEqual(linked.reader.open_snapshot("same")["state"], "ok")
        self.assertEqual(projects := Projects(self.root).main_for(self.external).worktree, self.alpha)
        # The same inventory resolves opaque project/recording references without paths.
        listed = Projects(self.root)
        chosen = next(project for project in listed.inventory() if project.common_dir == alpha_project.common_dir)
        chosen_linked = next(recording for recording in chosen.recordings if recording.worktree == self.external)
        self.assertIs(listed.resolve_recording(chosen.ref, chosen_linked.ref), chosen_linked)

    def test_stale_registered_path_does_not_hide_healthy_main(self):
        # This is only an explicitly created linked fixture; a stale registration must
        # not make discovery recursively search for it or discard the healthy main.
        (self.external / ".git").rename(self.external / ".git.removed")
        inventory = Projects(self.root).inventory()
        alpha_project = next(project for project in inventory if any(recording.worktree == self.alpha for recording in project.recordings))
        self.assertIn(self.alpha, {recording.worktree for recording in alpha_project.recordings})
        self.assertNotIn(self.external, {recording.worktree for recording in alpha_project.recordings})

    def test_cached_inventory_keeps_readers_for_no_store_and_rejects_replacement(self):
        projects = Projects(self.root)
        alpha_project = next(project for project in projects.inventory() if any(recording.worktree == self.alpha for recording in project.recordings))
        alpha = next(recording for recording in alpha_project.recordings if recording.worktree == self.alpha)
        self.assertEqual(alpha.state, "no_store")
        self.assertEqual(alpha.reader.open_snapshot()["state"], "no_store")
        self._record(self.alpha, "first")
        refreshed = next(recording for project in projects.refresh() for recording in project.recordings
                         if recording.worktree == self.alpha)
        self.assertIs(refreshed.reader, alpha.reader)
        self.assertEqual(refreshed.state, "available")
        self.assertEqual(alpha.reader.open_snapshot("first")["state"], "ok")
        database = self.alpha / ".coherence/workflow/workflow.sqlite"
        replacement = database.with_suffix(".replacement")
        replacement.write_bytes(database.read_bytes())
        os.replace(replacement, database)
        self.assertEqual(alpha.reader.open_snapshot("first")["state"], "unavailable")
        rejected = next(recording for project in projects.refresh() for recording in project.recordings
                        if recording.worktree == self.alpha)
        self.assertIs(rejected.reader, alpha.reader)
        self.assertEqual(rejected.state, "unavailable")

    def test_refresh_retries_an_initially_unsafe_binding_after_permission_repair(self):
        self._record(self.alpha, "first")
        database = self.alpha / ".coherence/workflow/workflow.sqlite"
        database.chmod(0o666)
        projects = Projects(self.root)
        initial = next(recording for project in projects.inventory() for recording in project.recordings
                       if recording.worktree == self.alpha)
        self.assertEqual(initial.state, "unavailable")
        self.assertIsNone(initial.reader)
        database.chmod(0o600)
        before = self._bytes()
        repaired = next(recording for project in projects.refresh() for recording in project.recordings
                        if recording.worktree == self.alpha)
        self.assertEqual(repaired.state, "available")
        self.assertIsNotNone(repaired.reader)
        self.assertEqual(repaired.reader.open_snapshot("first")["state"], "ok")
        self.assertEqual(before, self._bytes())

    def test_project_http_qualifies_collisions_and_keeps_preserved_source_after_removal(self):
        from starlette.testclient import TestClient
        self._record(self.alpha, "same")
        self._record(self.external, "same")
        capture = self.alpha / ".coherence/preserved-recordings/capture-1"
        (capture / "metrics").mkdir(parents=True)
        shutil.copyfile(self.external / ".coherence/workflow/workflow.sqlite", capture / "monitor.sqlite")
        (capture / "recording.json").write_text(json.dumps({"version": 1, "state": "complete", "recording_id": "capture-1", "origin_id": "origin-1"}))
        assets = self.base / "assets"; assets.mkdir(); (assets / "index.html").write_text("safe")
        projects = Projects(self.root)
        client = TestClient(create_app(projects, assets, 8765), base_url="http://127.0.0.1:8765")
        headers = {"sec-fetch-site": "same-origin", "x-workflow-monitor": "1"}
        listed = client.get("/api/monitor/v1/projects", headers=headers)
        self.assertEqual(listed.status_code, 200)
        alpha = next(item for item in listed.json()["projects"] if len(item["recordings"]) == 4)
        runs = client.get(f"/api/monitor/v1/projects/{alpha['ref']}/runs", headers=headers)
        self.assertEqual(runs.status_code, 200)
        values = runs.json()["runs"]
        self.assertEqual(len({item["ref"] for item in values}), len(values))
        self.assertEqual(len({item["display_id"] for item in values}), len(values))
        recording = next(item for item in alpha["recordings"] if item["label"] == "preserved")
        preserved = next(item for item in values if item["display_id"] == recording["ref"].split("_", 1)[1] + "-same")
        snapshot = client.get(f"/api/monitor/v1/projects/{alpha['ref']}/runs/{preserved['ref']}/snapshot", headers=headers)
        self.assertEqual(snapshot.status_code, 200)
        self.assertIn(preserved["display_id"], {item["display_id"] for item in snapshot.json()["runs"]})
        git(self.alpha, "worktree", "remove", "--force", str(self.external))
        refreshed = Projects(self.root)
        client = TestClient(create_app(refreshed, assets, 8765), base_url="http://127.0.0.1:8765")
        alpha = next(item for item in client.get("/api/monitor/v1/projects", headers=headers).json()["projects"] if item["ref"] == alpha["ref"])
        self.assertIn("preserved", {item["label"] for item in alpha["recordings"]})
        self.assertEqual(client.get(f"/api/monitor/v1/projects/{alpha['ref']}/runs/{preserved['ref']}/snapshot", headers=headers).status_code, 200)

    def _client(self):
        from starlette.testclient import TestClient
        assets = self.base / "assets"
        assets.mkdir(exist_ok=True)
        (assets / "index.html").write_text("safe")
        projects = Projects(self.root)
        client = TestClient(create_app(projects, assets, 8765), base_url="http://127.0.0.1:8765")
        return projects, client, {"sec-fetch-site": "same-origin", "x-workflow-monitor": "1"}

    def test_project_shell_preserves_raw_encoded_component_and_project_switch_route(self):
        _, client, headers = self._client()
        project = client.get("/api/monitor/v1/projects", headers=headers).json()["projects"][0]
        prefix = "/projects/" + project["ref"]
        for suffix in ("/runs", "/runs/id-slash%2F%25%3F%20%23%E6%9D%B1%E4%BA%AC", "/runs/id-once%252F", "/runs/id-actual(run)"):
            response = client.get(prefix + suffix)
            self.assertEqual(response.status_code, 200, suffix)
            self.assertEqual(response.text, "safe")
        for suffix in ("/runs/id-a/b", "/runs/id-%GG", "/runs/id-", "/runs/id-%FF"):
            self.assertEqual(client.get(prefix + suffix).status_code, 404, suffix)

    def test_reload_discovers_capture_and_keeps_live_binding_and_public_ids_stable(self):
        from workflow_monitor.preserve import preserve
        self._record(self.alpha, "same")
        projects, client, headers = self._client()
        project = next(item for item in client.get("/api/monitor/v1/projects", headers=headers).json()["projects"] if item["label"] == "alpha")
        route = "/api/monitor/v1/projects/" + project["ref"] + "/runs"
        before = client.get(route, headers=headers).json()["runs"][0]
        binding = projects.resolve_recording(project["ref"], before["ref"].split(".")[0])
        self._record(self.external, "same")
        result = preserve(self.external)
        git(self.alpha, "worktree", "remove", "--force", str(self.external))
        client.get("/api/monitor/v1/projects", headers=headers)
        after = client.get(route, headers=headers).json()["runs"]
        self.assertIn(before, after)
        preserved = next(item for item in after if item["source"] == "preserved")
        self.assertEqual(len(after), 2)
        self.assertTrue(result["readback"] == "verified")
        self.assertIs(binding, projects.resolve_recording(project["ref"], binding.ref))
        response = client.get(route + "/" + preserved["ref"] + "/snapshot", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(next(run["runner_state"]["state"] for run in response.json()["runs"] if run["ref"] == preserved["ref"]), "unknown")
        # Explicit refresh must not silently adopt a replacement DB.
        database = binding.reader.database
        replacement = database.with_suffix(".replacement")
        replacement.write_bytes(database.read_bytes())
        os.replace(replacement, database)
        client.get("/api/monitor/v1/projects", headers=headers)
        failed = client.get(route + "/" + before["ref"] + "/snapshot", headers=headers).json()
        self.assertEqual(failed["observation"]["read_state"], "unavailable")
        self.assertEqual(failed["runs"][0]["runner_state"]["state"], "unknown")
        healthy = client.get(route + "/" + preserved["ref"] + "/snapshot", headers=headers).json()
        self.assertEqual(healthy["observation"]["read_state"], "current")

    def test_normalize_before_qualification_and_cross_recording_pages_do_not_leak(self):
        from coherence_workflow.monitoring import descriptor
        def populate(worktree, *, source_run=True):
            commit = git(worktree, "rev-parse", "HEAD").decode().strip()
            with Authority(worktree) as owner:
                for run_id in (["original", "fixing"] if source_run else ["fixing"]):
                    contract = {"tasks": [{"id": "original", "description": "original"}]}
                    if run_id == "fixing":
                        contract["monitor"] = {"correction_of": {"run_id": "original", "review_execution_id": "review"}}
                    description = descriptor(contract, {}, commit)
                    owner.store.db.execute("INSERT INTO execution_monitor_runs VALUES(?,?,?,?,?)", (run_id, 1, json.dumps(description), 1.0, None))
                    for seq in range(52):
                        facts = {"role": "worker", "invocation_id": "original", "invocation_kind": "task_worker", "selected_input_checkpoints": [], "correction_chain": ["original"]}
                        phase, kind, occurrence = "worker", "started", "original"
                        if run_id == "original" and seq == 51:
                            phase, kind, occurrence = "review", "failed", "review"
                            facts = {"role": "reviewer", "approved": False, "finding_count": 1, "review_base": commit, "review_head": commit}
                        owner.store.db.execute("INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)", (run_id, 1, occurrence, phase, None, kind, float(seq), json.dumps(facts)))
        populate(self.alpha)
        populate(self.external)
        populate(self.inside, source_run=False)
        projects, client, headers = self._client()
        project = next(item for item in client.get("/api/monitor/v1/projects", headers=headers).json()["projects"] if item["label"] == "alpha")
        route = "/api/monitor/v1/projects/" + project["ref"] + "/runs"
        runs = client.get(route, headers=headers).json()["runs"]
        pages = {}
        for run in runs:
            page = client.get(route + "/" + run["ref"] + "/snapshot", headers=headers).json()
            pages[run["ref"]] = page
            self.assertTrue(all(row["run_ref"] == run["ref"] for row in page["records"]))
            self.assertEqual(page["activities"][0]["invocation_id"], "original")
            self.assertEqual(page["activities"][0]["correction_chain"], [page["activities"][0]["ref"]])
            self.assertEqual(page["tasks"][0]["task_id"], "original")
            own_prefix = run["ref"].split(".")[0]
            self.assertTrue(all(item["source_run_ref"].startswith(own_prefix + ".") for item in page["followups"]))
            if run["display_id"].endswith("-fixing"):
                expected = "unresolved" if projects.resolve_recording(project["ref"], own_prefix).worktree == self.inside else "resolved"
                self.assertEqual(page["followups"][0]["resolution"], expected)
        first, other = [run for run in runs if run["display_id"].endswith("-original")]
        a, b = pages[first["ref"]], pages[other["ref"]]
        self.assertNotEqual(a["snapshot_ref"], b["snapshot_ref"])
        base = route + "/" + other["ref"]
        response = client.get(base + "/history", params={"snapshot": b["snapshot_ref"], "cursor": a["next_cursor"]}, headers=headers)
        self.assertEqual(response.status_code, 400)
        response = client.get(base + "/records/" + a["records"][0]["ref"], params={"snapshot": b["snapshot_ref"]}, headers=headers)
        self.assertEqual(response.status_code, 404)
        response = client.get(base + "/history", params={"snapshot": b["snapshot_ref"], "cursor": b["next_cursor"]}, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["inventory"]["loaded_count"], 2)

    def test_empty_and_invalid_roots_are_honest(self):
        empty = self.base / "empty"
        empty.mkdir()
        self.assertEqual(Projects(empty).inventory(), ())
        with self.assertRaisesRegex(ValueError, "projects root"):
            Projects(self.base / "missing")


if __name__ == "__main__":
    unittest.main()
