"""Actual Git/SQLite fixtures for read-only multi-worktree discovery."""
from __future__ import annotations

import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))

from coherence_workflow.store import Authority, git
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
        self.assertEqual(alpha.reader.open_snapshot("first")["state"], "ok")
        database = self.alpha / ".coherence/workflow/workflow.sqlite"
        replacement = database.with_suffix(".replacement")
        replacement.write_bytes(database.read_bytes())
        os.replace(replacement, database)
        self.assertEqual(alpha.reader.open_snapshot("first")["state"], "unavailable")

    def test_empty_and_invalid_roots_are_honest(self):
        empty = self.base / "empty"
        empty.mkdir()
        self.assertEqual(Projects(empty).inventory(), ())
        with self.assertRaisesRegex(ValueError, "projects root"):
            Projects(self.base / "missing")


if __name__ == "__main__":
    unittest.main()
