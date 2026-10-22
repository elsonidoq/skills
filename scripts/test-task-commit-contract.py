#!/usr/bin/env python3
"""Static contract mutations and temporary-Git protocol fixtures, not model-obedience tests."""
import importlib.util
import re
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
            (text.replace("No skip/defer", "ask whether to skip/defer"), "coordinator checkpoint guard missing"),
            (text.replace("never adopts or commits unknown work", "may commit unknown inherited work"), "coordinator checkpoint guard missing"),
            (text.replace("Never blindly replay a Git commit", "implementer may recover"), "coordinator checkpoint guard missing"),
            (text.replace("ownership conflict block", "ownership conflict may continue"), "coordinator checkpoint guard missing"),
            (text + "\nA coordinator may proceed without per-task commits.\n", "coordinator checkpoint waiver reintroduced"),
        )
        for mutation, diagnostic in mutations:
            errors = checker.check(coordinator_text=mutation)
            self.assertTrue(any(diagnostic in error for error in errors), errors)

    def test_internal_batch_commits_do_not_require_routine_coordinator_approval(self):
        contract = " ".join(CONTRACT.read_text().split())
        coordinator = " ".join(COORDINATOR.read_text().split())
        self.assertIn("without routine coordinator approval", contract)
        self.assertEqual(checker.check(), [])
        barrier = "wait for coordinator validation before next-task writes"
        for location in ("contract", "coordinator"):
            overrides = {f"{location}_text": (contract if location == "contract" else coordinator) + "\n" + barrier}
            errors = checker.check(**overrides)
            self.assertIn("routine per-task coordinator barrier reintroduced", errors)
        for location in ("contract",):
            text = contract
            mutated = text.replace("without routine coordinator approval", "with routine coordinator approval")
            self.assertNotEqual(mutated, text)
            errors = checker.check(**{f"{location}_text": mutated})
            self.assertIn(f"{location} batch autonomy guard missing", errors)

    def test_no_automatic_state_or_second_checkpoint(self):
        text = CONTRACT.read_text()
        self.assertIn("No automatic STATE maintenance", text)
        self.assertEqual(checker.check(), [])
        errors = checker.check(contract_text=text + "\nAfter a task commit, capture its SHA and commit evidence")
        self.assertIn("routine evidence-only checkpoint reintroduced", errors)

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
        # Recovery uses the existing verified SHA, without a second repository ledger.
        commits = run(repo, "rev-list", "--count", f"{baseline}..HEAD").stdout.strip()
        self.assertEqual(commits, "1")
        self.assertEqual(run(repo, "rev-parse", "HEAD").stdout.strip(), task_sha)

    def test_same_file_ambiguity_is_a_stop_case(self):
        holder, repo = fixture_repo()
        self.addCleanup(holder.cleanup)
        (repo / "task.txt").write_text("unknown inherited change\n")
        self.assertNotEqual(run(repo, "diff", "--name-only").stdout, "")
        # The fixture deliberately does not stage or commit this ambiguous shared path.
        self.assertEqual(run(repo, "diff", "--cached", "--name-only").stdout, "")


LEGACY_BASELINE = '5ec94a87ffc4cc5747adaf93e290c2cf8526e594'
LEGACY_ROOT = 'memory/coordination/'
APPROVED_GUIDANCE = (
    'Routine task transitions/completions and steering-status updates must not wake the parent agent or require acknowledgment. '
    'Only agent questions and terminal workflow completion, whether success or error, should trigger a parent turn.'
)


def legacy_inventory():
    source = (ROOT / 'docs/plans/unified-project-memory-tinyspec.md').read_text()
    inventory = re.search(r'Exact tracked inventory .*?```text\n(.*?)\n```', source, re.S)
    if inventory is None:
        raise AssertionError('TinySpec legacy inventory missing')
    return tuple(LEGACY_ROOT + path for path in inventory.group(1).splitlines() if path)


def changed_paths(repo, baseline, *paths):
    return [line.split('\t', 1) for line in run(repo, 'diff', '--name-status', baseline, '--', *paths).stdout.splitlines()]


def assert_approved_memory_transition(case, repo, baseline, inventory):
    expected = set(inventory)
    actual = changed_paths(repo, baseline, 'memory')
    untracked = run(repo, 'ls-files', '--others', '--exclude-standard', '--', 'memory').stdout.splitlines()
    case.assertEqual(untracked, [], f'unapproved untracked memory paths: {untracked}')
    for status, path in actual:
        case.assertNotEqual(status[0], 'R', 'legacy records must not be renamed or relocated')
        if path == 'memory/MEMORY.md':
            case.assertEqual(status, 'M', 'the approved index may only be modified')
            index = (repo / path).read_text()
            case.assertIn(APPROVED_GUIDANCE, index, 'index update must retain the approved guidance')
            case.assertIn('provenance', index.lower(), 'index update must retain feedback provenance')
        else:
            case.assertIn(path, expected, f'unapproved memory change: {path}')
            case.assertEqual(status, 'D', f'legacy record may only be deleted: {path}')
    deleted = {path for status, path in actual if status == 'D'}
    case.assertTrue(deleted <= expected)
    # Every listed legacy byte is either untouched or deleted, never rewritten.
    for path in inventory:
        statuses = [status for status, changed in actual if changed == path]
        case.assertIn(statuses, ([], ['D']), f'legacy record rewritten: {path}')


def assert_recovery_semantics(case, source):
    clauses = (
        'return earliest invalid gate',
        'Return earliest affected Standard stage and renew affected approvals',
        'producing review/approval gate for correction and renewed affected approval',
        'Preserve original source/approval origin',
        'active/unknown legacy writers first',
    )
    for clause in clauses:
        case.assertIn(clause, source)


class RuntimePolicyCompatibilityTests(GitProtocolFixtureTests):
    def memory_fixture_repo(self, inventory):
        holder, repo = fixture_repo()
        self.addCleanup(holder.cleanup)
        (repo / 'memory').mkdir()
        (repo / 'memory/MEMORY.md').write_text('gotcha index\n')
        (repo / 'memory/custom-history.md').write_text('custom bytes\n')
        for path in inventory:
            target = repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f'legacy bytes: {path}\n')
        run(repo, 'add', 'memory')
        run(repo, 'commit', '-qm', 'memory baseline')
        return repo, run(repo, 'rev-parse', 'HEAD').stdout.strip()

    def test_historical_custom_and_original_source_bytes_preserved(self):
        inventory = legacy_inventory()
        self.assertEqual(len(inventory), 41)
        self.assertEqual(
            set(inventory),
            set(run(ROOT, 'ls-tree', '-r', '--name-only', LEGACY_BASELINE, '--', 'memory/coordination').stdout.splitlines()),
        )
        paths = ['.pi/STATE.md', 'specs/003-coordinate-workflow/tasks.json',
                 'specs/003-coordinate-workflow/spec.md', 'specs/003-coordinate-workflow/planning-approval.md',
                 'specs/003-coordinate-workflow/spec-approval.md', 'docs/evidence',
                 'skills/initialize-coherence/scripts/fixtures/old-initialize-coherence.txt']
        self.assertEqual(run(ROOT, 'diff', LEGACY_BASELINE, '--', *paths).stdout, '')
        assert_approved_memory_transition(self, ROOT, LEGACY_BASELINE, inventory)

        source = (ROOT / 'skills/planner/references/approval-and-recovery.md').read_text()
        assert_recovery_semantics(self, source)
        for clause in ('return earliest invalid gate', 'renew affected approvals', 'original source/approval origin', 'active/unknown legacy writers'):
            with self.subTest(removed=clause), self.assertRaises(AssertionError):
                assert_recovery_semantics(self, source.replace(clause, 'REMOVED'))

        contract = CONTRACT.read_text()
        self.assertIn('workers may propose/produce owned task changes but do not stage, commit', contract)
        self.assertTrue(any('executable checkpoint responsibility' in error for error in
            checker.check(contract_text=contract.replace('do not stage, commit', 'may stage and commit'))))
        self.assertIn('Unknown/live work, missing verification/Git authority', contract)
        self.assertIn('Planning/standalone retained artifacts continue', contract)
        self.assertEqual(checker.check(), [])

    def test_scoped_memory_preservation_accepts_only_pre_or_approved_post_cleanup(self):
        inventory = legacy_inventory()
        repo, baseline = self.memory_fixture_repo(inventory)
        assert_approved_memory_transition(self, repo, baseline, inventory)

        (repo / 'memory/MEMORY.md').write_text(
            f'owner guidance\n\n{APPROVED_GUIDANCE}\n\nCurrent-conversation provenance.\n'
        )
        for path in inventory:
            (repo / path).unlink()
        assert_approved_memory_transition(self, repo, baseline, inventory)

    def test_scoped_memory_preservation_rejects_rewrites_and_unapproved_changes(self):
        inventory = legacy_inventory()
        cases = (
            ('legacy rewrite', inventory[0], 'rewritten legacy bytes\n'),
            ('unapproved index rewrite', 'memory/MEMORY.md', 'arbitrary index rewrite\n'),
            ('extra memory addition', 'memory/extra.md', 'extra bytes\n'),
            ('custom historical deletion', 'memory/custom-history.md', None),
        )
        for label, path, content in cases:
            with self.subTest(label=label):
                repo, baseline = self.memory_fixture_repo(inventory)
                target = repo / path
                if content is None:
                    target.unlink()
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(content)
                with self.assertRaises(AssertionError):
                    assert_approved_memory_transition(self, repo, baseline, inventory)


if __name__ == "__main__":
    unittest.main()
