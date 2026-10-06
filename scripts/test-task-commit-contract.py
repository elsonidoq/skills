#!/usr/bin/env python3
"""Static contract mutations and temporary-Git protocol fixtures, not model-obedience tests."""
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "skills/memory-handling/references/task-commit-contract.md"
COORDINATOR = ROOT / "skills/coordinate-implementation/SKILL.md"


def run(repo, *args, ok=True):
    result = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True)
    if ok and result.returncode:
        raise AssertionError(f"git {' '.join(args)} failed: {result.stderr}")
    return result


def fixture_repo():
    directory = tempfile.TemporaryDirectory()
    repo = Path(directory.name)
    run(repo, "init", "-q")
    run(repo, "config", "user.name", "Fixture")
    run(repo, "config", "user.email", "fixture@example.invalid")
    (repo / "task.txt").write_text("base\n")
    (repo / "unrelated.txt").write_text("base\n")
    run(repo, "add", "task.txt", "unrelated.txt")
    run(repo, "commit", "-qm", "base")
    return directory, repo


def focused_task_commit(repo, path="task.txt", message="task checkpoint"):
    # --only limits the commit to the task path while preserving unrelated index entries.
    run(repo, "commit", "--only", "-m", message, "--", path)
    return run(repo, "rev-parse", "HEAD").stdout.strip()


def checkpoint_status(repo, expected_path, expected_parent):
    """Protocol oracle: one focused child of baseline touching exactly expected path."""
    head = run(repo, "rev-parse", "HEAD").stdout.strip()
    parent = run(repo, "rev-parse", "HEAD^").stdout.strip()
    files = set(run(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", head).stdout.splitlines())
    return parent == expected_parent and files == {expected_path}


class StaticContractMutationTests(unittest.TestCase):
    def test_contract_and_all_active_consumers_link_canonical_owner(self):
        self.assertTrue(CONTRACT.is_file())
        for skill in (ROOT / "skills").glob("*/SKILL.md"):
            if skill.parent.name == "epics-manager":
                continue
            self.assertIn("task-commit-contract.md", skill.read_text(), skill)
        for prompt in (ROOT / ".pi/prompts").glob("speckit.*.md"):
            self.assertIn("task-commit-contract.md", prompt.read_text(), prompt)

    def test_operational_guards_are_present_and_waiver_mutations_fail(self):
        text = COORDINATOR.read_text()
        for phrase in (
            "no skip/defer question", "No-Git fallback", "never adopts or commits unknown work",
            "coordinator alone may recover", "failed recovery stops dispatch", "evidence-only checkpoint",
        ):
            self.assertIn(phrase, text)
        mutations = (
            (text.replace("no skip/defer question", "ask whether to skip/defer"), "no skip/defer question"),
            (text.replace("never adopts or commits unknown work", "may commit unknown inherited work"), "never adopts or commits unknown work"),
            (text.replace("coordinator alone may recover", "implementer may recover"), "coordinator alone may recover"),
        )
        for mutation, removed_guard in mutations:
            self.assertNotEqual(mutation, text)
            self.assertNotIn(removed_guard, mutation)

    def test_existing_speckit_hooks_remain_and_additive_prompt_link_exists(self):
        prompt = (ROOT / ".pi/prompts/speckit.implement.md").read_text()
        self.assertIn("## Pre-Execution Checks", prompt)
        self.assertIn("## Mandatory Post-Execution Hooks", prompt)
        self.assertIn("task-commit-contract.md", prompt)


class GitProtocolFixtureTests(unittest.TestCase):
    def test_focused_commit_preserves_unrelated_staged_and_unstaged_work(self):
        holder, repo = fixture_repo()
        self.addCleanup(holder.cleanup)
        baseline = run(repo, "rev-parse", "HEAD").stdout.strip()
        (repo / "task.txt").write_text("task change\n")
        (repo / "unrelated.txt").write_text("staged unrelated\n")
        run(repo, "add", "unrelated.txt")
        (repo / "scratch.txt").write_text("unstaged unrelated\n")
        focused_task_commit(repo)
        self.assertTrue(checkpoint_status(repo, "task.txt", baseline))
        self.assertIn("unrelated.txt", run(repo, "diff", "--cached", "--name-only").stdout)
        self.assertTrue((repo / "scratch.txt").is_file())

    def test_absent_incorrect_and_combined_checkpoint_are_rejected(self):
        for mode in ("absent", "incorrect", "combined"):
            holder, repo = fixture_repo()
            self.addCleanup(holder.cleanup)
            baseline = run(repo, "rev-parse", "HEAD").stdout.strip()
            (repo / "task.txt").write_text("task\n")
            if mode == "absent":
                self.assertNotEqual(run(repo, "status", "--porcelain").stdout, "")
                continue
            if mode == "incorrect":
                (repo / "unrelated.txt").write_text("wrong\n")
                focused_task_commit(repo, "unrelated.txt")
            else:
                (repo / "unrelated.txt").write_text("combined\n")
                run(repo, "add", "task.txt", "unrelated.txt")
                run(repo, "commit", "-m", "combined checkpoint")
            self.assertFalse(checkpoint_status(repo, "task.txt", baseline), mode)

    def test_failing_hook_blocks_commit_without_bypass(self):
        holder, repo = fixture_repo()
        self.addCleanup(holder.cleanup)
        (repo / "task.txt").write_text("task\n")
        hook = repo / ".git/hooks/pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        run(repo, "add", "task.txt")
        result = run(repo, "commit", "-m", "must fail", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("task.txt", run(repo, "diff", "--cached", "--name-only").stdout)

    def test_interrupted_metadata_recovers_existing_sha_without_duplicate_task_commit(self):
        holder, repo = fixture_repo()
        self.addCleanup(holder.cleanup)
        baseline = run(repo, "rev-parse", "HEAD").stdout.strip()
        (repo / "task.txt").write_text("task\n")
        task_sha = focused_task_commit(repo)
        self.assertTrue(checkpoint_status(repo, "task.txt", baseline))
        (repo / "evidence.md").write_text(f"task SHA: {task_sha}\n")
        run(repo, "add", "evidence.md")
        run(repo, "commit", "-m", "evidence checkpoint")
        commits = run(repo, "rev-list", "--count", f"{baseline}..HEAD").stdout.strip()
        self.assertEqual(commits, "2")
        self.assertEqual(run(repo, "rev-parse", "HEAD~1").stdout.strip(), task_sha)

    def test_same_file_ambiguity_is_a_stop_case(self):
        holder, repo = fixture_repo()
        self.addCleanup(holder.cleanup)
        (repo / "task.txt").write_text("unknown inherited change\n")
        self.assertNotEqual(run(repo, "diff", "--name-only").stdout, "")
        # The fixture deliberately does not stage or commit this ambiguous shared path.
        self.assertEqual(run(repo, "diff", "--cached", "--name-only").stdout, "")


if __name__ == "__main__":
    unittest.main()
