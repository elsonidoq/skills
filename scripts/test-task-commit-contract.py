#!/usr/bin/env python3
"""Static contract mutations and temporary-Git protocol fixtures, not model-obedience tests."""
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "skills/memory-handling/references/task-commit-contract.md"
COORDINATOR = ROOT / "skills/coordinate-implementation/SKILL.md"
_spec = importlib.util.spec_from_file_location("task_commit_checker", ROOT / "scripts/check-task-commit-contract.py")
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)


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
    """Protocol oracle: focused child, no task-owned residual changes, and known baseline."""
    head = run(repo, "rev-parse", "HEAD").stdout.strip()
    if head == expected_parent:
        return False
    parent = run(repo, "rev-parse", "HEAD^", ok=False)
    if parent.returncode:
        return False
    files = set(run(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", head).stdout.splitlines())
    residual = set(run(repo, "diff", "--name-only").stdout.splitlines()) | set(run(repo, "diff", "--cached", "--name-only").stdout.splitlines())
    return parent.stdout.strip() == expected_parent and files == {expected_path} and expected_path not in residual


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
        self.assertEqual(checker.check(), [])
        mutations = (
            (text.replace("no skip/defer question", "ask whether to skip/defer"), "coordinator checkpoint guard missing"),
            (text.replace("never adopts or commits unknown work", "may commit unknown inherited work"), "coordinator checkpoint guard missing"),
            (text.replace("coordinator alone may recover", "implementer may recover"), "coordinator checkpoint guard missing"),
            (text.replace("failed recovery stops dispatch", "failed recovery may continue"), "coordinator checkpoint guard missing"),
            (text + "\nA coordinator may proceed without per-task commits.\n", "coordinator checkpoint waiver reintroduced"),
        )
        for mutation, diagnostic in mutations:
            errors = checker.check(coordinator_text=mutation)
            self.assertTrue(any(diagnostic in error for error in errors), errors)

    def test_architectural_planning_commit_opt_in_mutation_is_diagnostic(self):
        text = (ROOT / "skills/delegating-architectural-planning/SKILL.md").read_text()
        self.assertEqual(checker.check(), [])
        restored_opt_in = text.replace("must not push or dispatch additional agents", "Commit, push, or dispatch additional agents")
        errors = checker.check(architectural_text=restored_opt_in)
        self.assertIn("architectural planning commit opt-in reintroduced", errors)

    def test_removed_consumer_link_reports_specific_diagnostic(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        root = Path(holder.name) / "fixture"
        for skill in checker.SKILLS:
            shutil.copytree(ROOT / "skills" / skill, root / "skills" / skill)
        shutil.copytree(ROOT / ".pi/prompts", root / ".pi/prompts")
        consumer = root / "skills/brainstorming/SKILL.md"
        consumer.write_text(consumer.read_text().replace("task-commit-contract.md", "removed-contract.md"))
        errors = checker.check(root)
        self.assertIn("consumer link missing: brainstorming", errors)

    def test_existing_speckit_hook_operations_and_additive_prompt_link_are_protected(self):
        prompt = (ROOT / ".pi/prompts/speckit.implement.md").read_text()
        self.assertEqual(checker.check(), [])
        for phrase in ("hooks.before_implement", "hooks.after_implement", "MUST actually invoke the hook"):
            errors = checker.check(prompt_text=prompt.replace(phrase, "REMOVED"))
            self.assertIn(f"SpecKit hook operational guard missing: {phrase!r}", errors)
        # Preserve headings but remove both executable-body instructions.
        bodyless = prompt.replace("MUST actually invoke the hook", "MUST not invoke the hook").replace("Wait for the result of the hook command", "Do not wait")
        errors = checker.check(prompt_text=bodyless)
        self.assertIn("SpecKit hook operational guard missing: 'MUST actually invoke the hook'", errors)
        self.assertIn("SpecKit hook operational guard missing: 'Wait for the result of the hook command'", errors)


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
                self.assertFalse(checkpoint_status(repo, "task.txt", baseline))
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

    def test_residual_task_change_rejects_an_otherwise_valid_checkpoint(self):
        holder, repo = fixture_repo()
        self.addCleanup(holder.cleanup)
        baseline = run(repo, "rev-parse", "HEAD").stdout.strip()
        (repo / "task.txt").write_text("task\n")
        focused_task_commit(repo)
        (repo / "task.txt").write_text("residual task change\n")
        self.assertFalse(checkpoint_status(repo, "task.txt", baseline))

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
