#!/usr/bin/env python3
"""Context-first symbolic recovery and temporary-Git preservation, not live compaction."""
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
TEXT = (ROOT / "skills/coordinate-implementation/SKILL.md").read_text()


def contract_errors(text):
    start = text.find("## Recover Context")
    end = text.find("## Prepare Approved Execution", start)
    body = " ".join(text[start:end].split()) if start >= 0 else ""
    clauses = (
        "available conversation summary/recent context", "do not assume retained tokens",
        "Selectively reconstruct only uncertain authorization, completion",
        "Git HEAD/diffs/index ownership", "actual check/commit evidence",
        "Unknown approval/completion blocks", "never guess completion or repeat commits",
        "recorded and unrecorded active children", "running child means inspect/wait, not duplicate dispatch",
        "unknown child status", "missing runtime evidence stops replacement",
        "Inspect a failed run and its invocation", "unknown cause stops blind retries",
        "Preserve partial and unrelated work",
    )
    errors = ["recovery: missing " + c for c in clauses if c not in body]
    for unsafe in ("Automatically create STATE.md", "Update STATE after child-ID return",
                   "Remove finished STATE items", "Require a recovery snapshot before continuation",
                   "dispatch replacement while child is running", "Retry unknown failure"):
        if unsafe.lower() in text.lower():
            errors.append("recovery: forbidden " + unsafe)
    return errors


def walkthrough(*, context="sufficient", authority=True, evidence=True, partial=False,
                runtime="idle", failure=None, inspected=False):
    """Authored symbolic decisions, not a runtime recovery implementation."""
    if not authority or not evidence:
        return "STOP: reconcile approval/evidence"
    if runtime == "unknown":
        return "STOP: reconcile runtime before dispatch"
    if runtime in ("running", "unrecorded-running"):
        return "INSPECT/WAIT: existing child"
    if partial:
        return "STOP: reconcile partial task diff/checks/checkpoint"
    if failure and (not inspected or failure == "unknown"):
        return "STOP: inspect failure/cause"
    if context in ("insufficient", "fresh"):
        return "RECONSTRUCT: selective authority/Git/check/runtime facts"
    return "CONTINUE: verified dependency-ready action"


class RecoveryContractTests(unittest.TestCase):
    def test_context_first_carrier(self):
        self.assertEqual(contract_errors(TEXT), [])

    def test_every_recovery_guard_is_section_bound(self):
        for error in contract_errors(""):
            clause = error.removeprefix("recovery: missing ")
            normalized = " ".join(TEXT.split())
            self.assertIn(clause, normalized)
            altered = normalized.replace(clause, "REMOVED", 1) + " ## Footer " + clause
            # Reconstruct normal heading boundaries for the scoped check.
            altered = altered.replace(" ## ", "\n## ")
            self.assertIn(error, contract_errors(altered))

    def test_automatic_writes_duplicate_dispatch_and_blind_retry_fail(self):
        for unsafe in ("Automatically create STATE.md", "Update STATE after child-ID return",
                       "Remove finished STATE items", "Require a recovery snapshot before continuation",
                       "dispatch replacement while child is running", "Retry unknown failure"):
            self.assertIn("recovery: forbidden " + unsafe, contract_errors(TEXT + "\n" + unsafe))

    def test_summary_insufficient_fresh_and_uncertain_context(self):
        self.assertTrue(walkthrough().startswith("CONTINUE"))
        for context in ("insufficient", "fresh"):
            self.assertTrue(walkthrough(context=context).startswith("RECONSTRUCT"))
        for gap in ({"authority": False}, {"evidence": False}, {"partial": True}):
            self.assertTrue(walkthrough(**gap).startswith("STOP"))

    def test_active_unrecorded_unknown_and_inspected_failure(self):
        for runtime in ("running", "unrecorded-running"):
            self.assertTrue(walkthrough(runtime=runtime).startswith("INSPECT/WAIT"))
        self.assertTrue(walkthrough(runtime="unknown").startswith("STOP"))
        self.assertTrue(walkthrough(failure="timeout").startswith("STOP"))
        self.assertTrue(walkthrough(failure="unknown", inspected=True).startswith("STOP"))
        self.assertTrue(walkthrough(failure="known-tool-gap", inspected=True).startswith("CONTINUE"))


class GitScenarioTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        (self.root / "task.txt").write_text("baseline\n")
        (self.root / "STATE.md").write_text("# Custom state\n- Unrelated ongoing work\n")
        self.git("add", "task.txt", "STATE.md")
        self.git("commit", "-qm", "baseline")
        self.state = (self.root / "STATE.md").read_bytes()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True, stderr=subprocess.STDOUT)

    def verified_task(self):
        (self.root / "task.txt").write_text("verified result\n")
        self.git("commit", "--only", "-qm", "task checkpoint", "--", "task.txt")
        return self.git("rev-parse", "HEAD").strip()

    def assert_state_preserved(self):
        self.assertEqual((self.root / "STATE.md").read_bytes(), self.state)
        self.assertFalse((self.root / "SUMMARY.md").exists())

    def test_compaction_after_verified_checkpoint_no_duplicate_commit(self):
        sha = self.verified_task()
        count = self.git("rev-list", "--count", "HEAD")
        self.assertTrue(walkthrough().startswith("CONTINUE"))
        self.assertEqual(self.git("show", sha + ":task.txt"), "verified result\n")
        self.assertEqual(self.git("rev-list", "--count", "HEAD"), count)
        self.assertEqual(count.strip(), "2")
        self.assert_state_preserved()

    def test_compaction_while_worker_running_no_state_or_summary_write(self):
        self.verified_task()
        self.assertTrue(walkthrough(runtime="running").startswith("INSPECT/WAIT"))
        self.assert_state_preserved()

    def test_stale_snapshot_does_not_override_actual_commit(self):
        sha = self.verified_task()
        self.assertNotIn(sha.encode(), self.state)
        self.assertTrue(walkthrough().startswith("CONTINUE"))
        self.assert_state_preserved()

    def test_partial_owned_changes_preserved_on_stop(self):
        (self.root / "task.txt").write_text("partial\n")
        before = self.git("diff")
        self.assertTrue(walkthrough(partial=True).startswith("STOP"))
        self.assertEqual(self.git("diff"), before)
        self.assert_state_preserved()

    def test_fresh_missing_state_and_store_are_not_initialized(self):
        (self.root / "STATE.md").unlink()
        self.assertTrue(walkthrough(context="fresh").startswith("RECONSTRUCT"))
        self.assertFalse((self.root / "STATE.md").exists())
        self.assertFalse((self.root / "memory").exists())

    def test_custom_dirty_state_and_unrelated_index_survive_task(self):
        (self.root / "STATE.md").write_bytes(self.state + b"owner unsaved edit\n")
        self.state = (self.root / "STATE.md").read_bytes()
        (self.root / "unrelated.txt").write_text("staged unrelated\n")
        self.git("add", "unrelated.txt")
        self.verified_task()
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "unrelated.txt\n")
        self.assert_state_preserved()

    def test_completion_and_review_leave_all_custom_state_untouched(self):
        self.verified_task()
        for event in ("task completion", "review", "closeout", "paused"):
            with self.subTest(event=event):
                self.assert_state_preserved()
                self.assertEqual(self.git("diff", "--name-only"), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
