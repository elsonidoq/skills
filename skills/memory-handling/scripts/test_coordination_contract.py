#!/usr/bin/env python3
"""Offline instruction sensitivity + explicitly simulated filesystem examples.

No production persistence/approval engine, model obedience or real SpecKit execution.
The fixtures carry out prescribed examples directly; safety enforcement is checked by
mutating actual instruction carriers, not by pretending these examples execute skills.
"""
import importlib.util
from pathlib import Path
import tempfile
import subprocess
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("planner_checker", ROOT / "scripts/check-planner-workflow.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CoordinationContractTests(unittest.TestCase):
    def setUp(self):
        self.texts = checker.load_texts()

    def assert_rejected(self, key, heading, clause, label):
        changed = dict(self.texts)
        carrier = checker.section(changed[key], heading)
        self.assertEqual(carrier.count(clause), 1, clause)
        changed[key] = changed[key].replace(carrier, carrier.replace(clause, "", 1), 1)
        errors = checker.check_contracts(changed)
        self.assertTrue(any(e.startswith(label + ":") for e in errors), errors)

    def test_A1_A2_early_association_and_both_route_direct_constraints(self):
        self.assertEqual(checker.check_contracts(self.texts), [])
        cases = (
            ("planner", "## Discovery and capability boundary", "`GUIDELINES.md` before brainstorming, scope assessment and depth choice", "coordination-early"),
            ("planner", "## Discovery and capability boundary", "initialize missing files, notify the user and commit only initialization files", "coordination-early"),
            ("planner", "## Discovery and capability boundary", "required gotcha-memory stops remain", "coordination-early"),
            ("planner", "## Selected production and stage handoffs", "both TinySpec and Standard stage briefs", "coordination-handoff"),
            ("planner", "## Selected production and stage handoffs", "task dependencies, checkpoints, verification and coordinator handoff", "coordination-handoff"),
            ("tiny", "## Inputs and preflight", "including direct/standalone entry", "coordination-tiny"),
            ("tasks", "## Preconditions and adapters", "including direct entry without planner", "coordination-tasks"),
            ("tasks", "## Preconditions and adapters", "checkpoints and REQUIRED verification/acceptance", "coordination-tasks"),
            ("coordination", "## Project-local initialization", "No separate setup approval is required", "coordination-initialization"),
            ("coordination", "## Project-local initialization", "commit only those new files", "coordination-initialization"),
        )
        for case in cases:
            with self.subTest(clause=case[2]):
                self.assert_rejected(*case)

    def test_A1_late_discovery_with_summary_intact_is_rejected(self):
        changed = dict(self.texts)
        body = checker.section(changed["planner"], "## Discovery and capability boundary")
        begin = body.index("Apply the shared [project coordination contract]")
        end = body.index("Verify callable question capability", begin)
        hook = body[begin:end]
        changed["planner"] = changed["planner"].replace(hook, "", 1) + "\n## Late memory summary\n" + hook
        self.assertIn("before brainstorming", changed["planner"])
        self.assertTrue(any(e.startswith("coordination-early:") for e in checker.check_contracts(changed)))

    def test_A3_A4_A5_factual_checkpoint_and_index_removals(self):
        for clause in (
            "failed, blocked or partial work and manual/user", "exact selected and observed profile",
            "individual check results, reviewer findings", "Unknown is not success",
            "reuse on resume, never overwrite another run", "sole evidence file for each new run",
            "before refreshing its index row after every evidence", "no duplicate rows",
            "reconcile interrupted summary/index updates", "retaining prior attempts", "never a no-write fallback",
        ):
            with self.subTest(clause=clause):
                self.assert_rejected("coordinator", "### Coordination evidence checkpoint", clause, "coordination-checkpoint")
        for clause in ("Evidence is factual and append-oriented:", "run record before its index entry", "Keep one row per run", "sensitive payloads"):
            self.assert_rejected("coordination", "## Separate factual evidence", clause, "coordination-evidence")

    def test_item_disposition_and_escalation_removals(self):
        for key, heading, clause, label in (
            ("coordinator", "### Coordination evidence checkpoint", "batch/task item dispositions and proof references", "verification-feedback"),
            ("coordinator", "### Coordination evidence checkpoint", "exact escalation reason", "verification-feedback"),
            ("coordination", "## Separate factual evidence", "batch/task item dispositions and proof references", "verification-feedback-owner"),
            ("coordination", "## Separate factual evidence", "next selected profile or pending selection", "verification-feedback-owner"),
        ):
            self.assert_rejected(key, heading, clause, label)

    def test_A6_reflection_uncertainty_and_no_update_removals(self):
        for clause in (
            "nine reflection questions", "project-specific versus general", "reusable versus incidental",
            "reinforcement; contradiction", "guideline support versus evidence-only", "delegation lessons; manual validation",
            "surprises needing qualification/more evidence", "insufficient and conflicting", "same run `SUMMARY.md`",
            "Older runs with `REFLECTION.md` remain", "supporting/contradicting pointers",
            "no update proposed", "not a universal ban or permanent routing rule",
        ):
            with self.subTest(clause=clause):
                self.assert_rejected("coordinator", "## Coordination reflection and guideline approval", clause, "coordination-reflection")

    def test_A7_A8_A9_exact_approval_rejection_and_drift_removals(self):
        for clause in (
            "executive brief and exact candidate diff", "existing `ask_user`", "accept, edit, reject, or add",
            "approval is not guideline approval", "Explicit accepted/edited/added resulting content",
            "comparable baseline/proposed content evidence", "Pending, unavailable, cancelled or ambiguous answers leave guidelines unchanged",
            "Rejection leaves guideline bytes identical", "rejection disposition",
            "Immediately before applying only approved changes, re-read",
            "compare with the approved baseline: concurrent drift stops application", "renewed review/approval",
            "Re-check relevant guidance after", "Report implementation/feature acceptance separately",
        ):
            with self.subTest(clause=clause):
                self.assert_rejected("coordinator", "## Coordination reflection and guideline approval", clause, "coordination-approval")
        self.assert_rejected("coordination", "## Exact guideline approval", "resulting content must be explicitly approved", "coordination-exact-write")

    def test_A10_selective_index_first_and_no_match_removals(self):
        for clause in (
            "Ordinary planning reads guidelines, not", "justified only", "ambiguous/tentative/conflicting",
            "user request", "new contradictory", "read the compact evidence index first",
            "only those selected records", "Do not recursively", "Unrelated records\nstay unread",
            "no relevant evidence means proceed retaining uncertainty",
        ):
            with self.subTest(clause=clause):
                self.assert_rejected("coordination", "## Selective historical retrieval", clause, "coordination-selective")

    def test_A11_profile_selection_and_inspected_cause_removals(self):
        for clause in (
            "usable owner-selected", "independent family/effort rationales",
            "Never silently replace selected models",
            "Inspect the failed child run, invocation, partial commits and check evidence",
            "unrelated\nchanges and prior attempt evidence", "affected dependencies and invalidated REQUIRED items",
            "raise effort, change model or both", "no fixed profile ladder",
            "permitted callable binding, supported effort, tools and owner-selection gates",
            "safe task-owned state stops", "unknown cause stops blind restart",
            "complete batch contract", "rerun every invalidated item", "Retain both attempts",
        ):
            with self.subTest(clause=clause):
                self.assert_rejected("coordinator", "## Select Execution Capability", clause, "coordination-routing")

    def test_unsafe_bulk_silent_drift_class_retry_and_single_outcome_policies(self):
        for policy in (
            "Always read the entire evidence directory", "Read coordination history on every request",
            "Automatically apply guideline proposals", "Implementation approval authorizes guideline writes",
            "Ignore concurrent guideline drift", "Automatically downgrade approved classes",
            "Retry without inspecting the failed invocation", "One failure permanently bans a model",
            "Without association/write authority", "offer future bounded setup",
            "Undeclared optional memory preserves existing behavior",
        ):
            changed = dict(self.texts)
            changed["coordination"] += "\n" + policy
            self.assertTrue(any(e.startswith("coordination-unsafe:") for e in checker.check_contracts(changed)), policy)

    def test_A12_existing_execution_safeguards_survive_mutations(self):
        for clause, diagnostic in (
            ("Commit each task's verified changes as one focused commit", "execution-checkpoints:"),
            ("only asynchronously in the background", "execution-sequential:"),
            ("never\n   run implementation batches in parallel", "execution-sequential:"),
            ("Copy the owner-selected binding and effort unchanged", "execution-selection:"),
            ("separate evidence-only checkpoint", "execution-checkpoints:"),
        ):
            changed = dict(self.texts)
            self.assertIn(clause, changed["coordinator"])
            changed["coordinator"] = changed["coordinator"].replace(clause, "", 1)
            self.assertTrue(any(e.startswith(diagnostic) for e in checker.check_contracts(changed)), clause)

    def test_required_links_and_missing_carrier_in_isolated_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in set(checker.PATHS.values()):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text((ROOT / path).read_text())
            checker.load_texts(root)
            for key in ("memory", "planner", "tiny", "tasks", "coordinator"):
                with self.subTest(consumer=key):
                    p = root / checker.PATHS[key]
                    original = p.read_text()
                    p.write_text(original.replace("references/project-coordination.md", "references/wrong.md"))
                    with self.assertRaisesRegex(ValueError, "coordination-reference: " + key):
                        checker.load_texts(root)
                    p.write_text(original)
            (root / checker.PATHS["coordination"]).unlink()
            with self.assertRaisesRegex(ValueError, "coordination-reference:"):
                checker.load_texts(root)


    def test_mandatory_initialization_preservation_commit_and_blocker_removals(self):
        for clause in (
            "one mandatory lifecycle in every entry point", "<project-root>/memory/coordination/",
            "create only missing", "Preserve every existing file byte-for-byte",
            "partial stores get only their missing files", "Repeated entry is idempotent",
            "Tell the user", "path-limited commit", "Preserve unrelated working-tree and staged",
            "report the exact blocker and stop", "finish its missing commit",
            "initialization/commit and factual evidence/index/reflection persistence",
        ):
            with self.subTest(clause=clause):
                self.assert_rejected("coordination", "## Project-local initialization", clause, "coordination-initialization")
        for key, heading, clause, diagnostic in (
            ("tiny", "## Inputs and preflight", "without a setup approval gate", "coordination-tiny"),
            ("tasks", "## Preconditions and adapters", "without a setup approval gate", "coordination-tasks"),
            ("coordinator", "## Load and Verify", "without a setup approval gate", "coordination-intake"),
        ):
            self.assert_rejected(key, heading, clause, diagnostic)

    def test_blocked_preselection_evidence_is_permitted_without_planning_authority(self):
        # Concrete reviewed boundary: initialization succeeded, ask_user unavailable.
        self.assertEqual(checker.check_contracts(self.texts), [])
        for key, heading, clause, diagnostic in (
            ("coordination", "## Project-local initialization", "blocked before depth selection", "coordination-initialization"),
            ("coordination", "## Project-local initialization", "unapproved learned-guideline write authority", "coordination-initialization"),
            ("planner", "## Before selection:", "including blocked runs before depth selection", "coordination-preselection"),
            ("planner", "## Selected production and stage handoffs", "including blocked preselection", "coordination-preselection"),
        ):
            with self.subTest(carrier=key, clause=clause):
                self.assert_rejected(key, heading, clause, diagnostic)


class SimulatedFilesystemExamples(unittest.TestCase):
    """Prescribed portable examples, NOT an implementation of the skill lifecycle."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.root = self.project / "memory" / "coordination"
        self.root.mkdir(parents=True)
        self.guidelines = self.root / "GUIDELINES.md"
        self.baseline = ("# Fictional project guidance — simulated, not global policy\n"
                         "- Scope: heuristic implementation. Require a manual output checkpoint.\n"
                         "  Status: owner-supplied; origin: fictional owner, no supporting run.\n").encode()
        self.guidelines.write_bytes(self.baseline)
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        self.run = self.evidence / "simulated-2026-01-01-heuristic"
        self.run.mkdir()
        self.summary = self.run / "SUMMARY.md"
        self.summary.write_text("# Simulated run\nAreas/tags: heuristic\nOutcome: partial; manual validation pending\n"
            "Task T001: tags: heuristic; baseline: fixture-base; result: fixture-commit; evidence: fixture-evidence\n"
            "residual_reasoning: medium — executable output oracle\n"
            "selected profile: fictional-option-A/medium; role: worker; observed model/effort: unknown\n"
            "Attempt 1: FAIL; check: output mismatch; cause: inspected missed boundary\n"
            "Reviewer findings: unknown; manual validation: pending, not success\n"
            "Correction: authorized failed-task isolation; unrelated work preserved\n"
            "Repair: inspected missed boundary; verified exact profile selected by fictional owner\n"
            "Attempt 2: automated PASS; model: fictional-option-B; effort: unknown\n"
            "Manual validation: FAIL — visually implausible output; outcome: partial\n"
            "Surprise: automation missed manual defect; no permanent routing rule\n")
        self.index = self.evidence / "INDEX.md"
        self.row = "| [simulated-2026-01-01-heuristic](simulated-2026-01-01-heuristic/SUMMARY.md) | 2026-01-01 | heuristic | manual checkpoint | partial |\n"
        self.index.write_text("# Simulated evidence index\n" + self.row)
        self.reflection = self.summary  # Reflection and decisions share the sole run record.

    def test_A1_A2_simulated_early_guideline_handoff_and_empty_store(self):
        read = self.guidelines.read_bytes()
        # Explicit example handoff, not a model-generated source/task artifact.
        for route in ("TinySpec/direct", "Standard/SpecKit (simulated only)"):
            handoff = {"route": route, "constraint": read, "checkpoint": "manual output", "before_choice": True}
            self.assertEqual(handoff["constraint"], self.baseline)
            self.assertTrue(handoff["before_choice"])
        self.assertIn("No separate setup approval is required", checker.load_texts()["coordination"])
        # No knowledge is invented when automatically initialized guidelines are empty.
        empty = self.project / "empty-project" / "memory" / "coordination"
        (empty / "evidence").mkdir(parents=True)
        (empty / "GUIDELINES.md").write_text("# Project coordination guidelines\n\nNo approved project coordination guidelines yet.\n")
        (empty / "evidence" / "INDEX.md").write_text("# Execution evidence index\n")
        self.assertIn("No approved", (empty / "GUIDELINES.md").read_text())
        self.assertEqual(list((empty / "evidence").iterdir()), [empty / "evidence" / "INDEX.md"])

    def test_missing_files_initialization_commit_preserves_staged_work_and_repeat(self):
        # Prescribed skill operations in a real temporary Git repo, not an agent runtime.
        project = self.project / "new-project"
        project.mkdir()
        def git(*args):
            return subprocess.check_output(["git", "-C", str(project), *args], stderr=subprocess.STDOUT)
        git("init", "-q")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        (project / "unrelated.txt").write_text("unrelated staged work\n")
        git("add", "--", "unrelated.txt")
        root = project / "memory" / "coordination"
        (root / "evidence").mkdir(parents=True)
        files = [root / "GUIDELINES.md", root / "evidence" / "INDEX.md"]
        files[0].write_text("# Project coordination guidelines\n\nNo approved project coordination guidelines yet.\n")
        files[1].write_text("# Execution evidence index\n\n| Run | Date | Areas / tags | Relevant patterns | Outcome |\n| --- | --- | --- | --- | --- |\n")
        paths = [str(p.relative_to(project)) for p in files]
        notification = "Initialized project-local coordination files: " + ", ".join(paths)
        self.assertIn("GUIDELINES.md", notification)
        git("add", "--", *paths)
        git("commit", "--only", "-qm", "chore: initialize project coordination memory", "--", *paths)
        committed = git("ls-tree", "-r", "--name-only", "HEAD").decode().splitlines()
        self.assertEqual(set(committed), set(paths))
        self.assertEqual(git("diff", "--cached", "--name-only").decode().strip(), "unrelated.txt")
        baseline = {p: p.read_bytes() for p in files}
        head = git("rev-parse", "HEAD")
        # Repeated entry: no missing files -> no write/commit. Partial recovery only
        # creates the missing index, preserving a manually maintained guideline.
        self.assertFalse([p for p in files if not p.exists()])
        self.assertEqual(git("rev-parse", "HEAD"), head)
        files[1].unlink()
        missing = [p for p in files if not p.exists()]
        self.assertEqual(missing, [files[1]])
        missing[0].write_bytes(baseline[missing[0]])
        self.assertEqual(files[0].read_bytes(), baseline[files[0]])

    def test_A3_A4_simulated_two_runs_multiple_tasks_failed_partial_manual_unknown(self):
        with self.summary.open("a") as f:
            f.write("Task T002: outcome blocked; capability unknown; baseline fixture-evidence; check NOT RUN\n")
        second = self.evidence / "simulated-2026-01-02-other"
        second.mkdir()
        (second / "SUMMARY.md").write_text("# Simulated unrelated run\nTags: other; outcome: PASS\n")
        with (second / "SUMMARY.md").open("a") as f:
            f.write("Task T001: outcome PASS; effort unknown; result fixture-second\n")
        with self.index.open("a") as f:
            f.write("| [simulated-2026-01-02-other](simulated-2026-01-02-other/SUMMARY.md) | 2026-01-02 | other | unrelated | PASS |\n")
        self.assertEqual(len(list(self.evidence.glob("*/SUMMARY.md"))), 2)
        self.assertEqual(len(list(self.evidence.glob("*/T*.md"))), 0)
        first = self.summary.read_text()
        for fact in ("Attempt 1: FAIL", "Attempt 2:", "effort: unknown", "Manual validation: FAIL", "outcome: partial", "no permanent routing rule"):
            self.assertIn(fact, first)
        self.assertNotIn("Attempt 1", self.index.read_text())
        self.assertEqual(self.guidelines.read_bytes(), self.baseline)

    def test_bounded_same_summary_item_attempt_record(self):
        before = self.summary.read_text()
        self.summary.write_text(before +
            "B01/T001/V1 first: failed; proof fixture-output@sha-1/offline\n"
            "B01/T001/V1 final: satisfied; proof fixture-correction@sha-2/offline\n"
            "Exact escalation reason: inspected missing boundary; next selected profile fictional-option-B\n"
            "Reused: T001/V2@sha-1; invalidated/rerun: T001/V1@sha-2\n"
            "First/final observed effort: unknown; contract strength: concrete manual oracle\n")
        self.index.write_text(self.index.read_text().replace("manual checkpoint", "item dispositions; exact-gap repair"))
        record = self.summary.read_text()
        self.assertTrue(record.startswith(before))
        for proof in ("fixture-output@sha-1/offline", "fixture-correction@sha-2/offline", "invalidated/rerun: T001/V1@sha-2", "observed effort: unknown"):
            self.assertIn(proof, record)
        self.assertEqual(self.index.read_text().count("](simulated-2026-01-01-heuristic/SUMMARY.md)"), 1)
        self.assertEqual(list(self.run.glob("*.md")), [self.summary])
        self.assertEqual(self.guidelines.read_bytes(), self.baseline)

    def test_A5_simulated_resume_interrupted_record_then_index_repair(self):
        prior = self.evidence / "simulated-prior"
        prior.mkdir()
        (prior / "SUMMARY.md").write_text("# Simulated earlier run\nOutcome: unknown\n")
        prior_row = "| [prior](simulated-prior/SUMMARY.md) | 2025-12-31 | other | unrelated | unknown |\n"
        with self.index.open("a") as f:
            f.write(prior_row)
        prior_bytes = (prior / "SUMMARY.md").read_bytes()
        old_index = self.index.read_text()
        self.summary.write_text(self.summary.read_text() +
                                "Resume correction: manual output now validated PASS\n"
                                "Resume: manual PASS; overall PASS\n")
        # Deliberately interrupted example: record exists but row is stale.
        self.assertEqual(self.index.read_text(), old_index)
        updated = self.row.replace("| partial |", "| PASS after resume |")
        self.index.write_text(old_index.replace(self.row, updated))
        # A second reconciliation of the same row is byte-idempotent.
        self.index.write_text(self.index.read_text().replace(self.row, updated))
        self.assertEqual(self.index.read_text().count("](simulated-2026-01-01-heuristic/SUMMARY.md)"), 1)
        self.assertIn("Attempt 1: FAIL", self.summary.read_text())
        self.assertIn("Resume correction", self.summary.read_text())
        self.assertIn(prior_row, self.index.read_text())
        self.assertEqual((prior / "SUMMARY.md").read_bytes(), prior_bytes)

    def test_A6_simulated_reflection_evidence_only_tentative_contrary_no_update(self):
        self.reflection.write_text(self.reflection.read_text() +
            "\n## Reflection (not planner guidance)\n"
            "Direct observation: manual FAIL in T001; automation missed it\n"
            "Tentative scoped caution: heuristic outputs need manual validation\n"
            "Supporting: T001 attempt 2; contrary: later valid output\n"
            "Insufficient evidence: one failure cannot support universal delegation ban\n"
            "Repeated/stable pattern: unknown; evidence-only, not promoted\n"
            "Disposition: no update proposed (existing owner guideline covers checkpoint)\n")
        self.index.write_text(self.index.read_text().replace(self.row, self.row.replace("manual checkpoint", "reflection evidence-only; no update")))
        self.assertIn("reflection evidence-only; no update", self.index.read_text())
        self.assertIn("no update proposed", self.reflection.read_text())
        self.assertEqual(self.guidelines.read_bytes(), self.baseline)

    def test_A7_A9_simulated_pending_unavailable_cancelled_ambiguous_rejected_bytes(self):
        # No gate is executed here. Each prescribed decision record is evidence only.
        for state in ("pending", "unavailable", "cancelled", "ambiguous", "reject"):
            with self.subTest(state=state):
                self.reflection.write_text(self.reflection.read_text() + "\nDecision: " + state + "\nGuidelines unchanged; implementation approval is not memory approval\n")
                self.index.write_text("# Simulated evidence index\n" + self.row.replace("manual checkpoint", "decision " + state))
                self.assertEqual(self.guidelines.read_bytes(), self.baseline)
                self.assertIn(state, self.reflection.read_text())
                self.assertEqual(list(self.run.glob("*.md")), [self.summary])

    def test_A8_simulated_exact_accept_edit_add_content_and_baseline_evidence(self):
        for decision, statement in (
            ("accept", b"- Scope: heuristic outputs; tentative: inspect an edge-case output manually.\n"),
            ("edit", b"- Scope: heuristic boundary outputs only; owner-supplied: manual checkpoint.\n"),
            ("add", b"- Scope: heuristic verification; owner-supplied: record manual findings separately.\n"),
        ):
            with self.subTest(decision=decision):
                self.guidelines.write_bytes(self.baseline)
                approved_result = self.baseline + statement
                self.reflection.write_text(self.reflection.read_text() + "\nDecision: " + decision + "\nBaseline:\n" + self.baseline.decode() + "Approved resulting content:\n" + approved_result.decode())
                immediately_reread = self.guidelines.read_bytes()
                self.assertEqual(immediately_reread, self.baseline)
                self.guidelines.write_bytes(approved_result)  # prescribed example, not gate logic
                self.index.write_text("# Simulated evidence index\n" + self.row.replace("manual checkpoint", "approved " + decision))
                self.assertEqual(self.guidelines.read_bytes(), approved_result)
                self.assertIn(approved_result.decode(), self.reflection.read_text())

    def test_A8_simulated_concurrent_drift_preserved_and_renewal_pending(self):
        self.reflection.write_text(self.reflection.read_text() + "\nApproved baseline:\n" + self.baseline.decode())
        concurrent = self.baseline + b"- Concurrent fictional owner addition.\n"
        self.guidelines.write_bytes(concurrent)
        immediately_reread = self.guidelines.read_bytes()
        self.assertNotEqual(immediately_reread, self.baseline)
        with self.reflection.open("a") as f:
            f.write("Disposition: drift; stop application; renewed review/approval pending\n")
        self.index.write_text("# Simulated evidence index\n" + self.row.replace("partial", "drift; pending renewal"))
        self.assertEqual(self.guidelines.read_bytes(), concurrent)
        self.assertIn("renewed review/approval pending", self.reflection.read_text())

    def test_A10_simulated_index_first_relevant_only_and_no_match_uncertainty(self):
        unrelated = self.evidence / "simulated-unrelated"
        unrelated.mkdir()
        (unrelated / "SUMMARY.md").write_text("# Simulated unrelated\nTags: billing\n")
        with self.index.open("a") as f:
            f.write("| [unrelated](simulated-unrelated/SUMMARY.md) | 2026-01-02 | billing | unrelated | unknown |\n")
        # Explicit selected reads; no recursive loader or fake history selection engine.
        reads = []
        original_read = Path.read_text
        def observed_read(path, *args, **kwargs):
            reads.append(path)
            return original_read(path, *args, **kwargs)
        with mock.patch.object(Path, "read_text", new=observed_read):
            index_text = self.index.read_text()
            self.assertIn("heuristic", index_text)
            self.summary.read_text()
        self.assertEqual(reads, [self.index, self.summary])
        self.assertNotIn(unrelated / "SUMMARY.md", reads)
        # For a no-match request, index alone is read, uncertainty retained.
        reads.clear()
        with mock.patch.object(Path, "read_text", new=observed_read):
            text = self.index.read_text()
            self.assertNotIn("storage-migration", text)
            knowledge = "unknown — no relevant evidence"
        self.assertEqual(reads, [self.index])
        self.assertIn("unknown", knowledge)


if __name__ == "__main__":
    unittest.main()
