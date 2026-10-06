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


# Instruction sensitivity only, not runtime enforcement or a routing engine.
ROUTING_GUARDS = (
    "separate family suitability and effort rationale",
    "provider-documented options", "permitted usable exact runtime",
    "current owner selection before execution", "Catalog-only availability does not prove callability",
    "unsupported runtime effort blocks", "Never silently\nreplace selected models",
    "Risk strengthens decomposition", "not automatic high effort or strongest-family selection",
    "least\nsupported effort justified as adequate after decomposition",
    "not role, family, stakes", "High-risk/strong-oracle work",
    "Weak-oracle work returns for decomposition", "No unconditional low/medium default",
    "supported no-row pairing is not automatically excluded", "complete targeted research or",
    "explicit bounded owner uncertainty decision", "gap, rationale, allowed scope",
    "runtime support, owner routing authorization or REQUIRED acceptance",
    "owner preference is a choice, not a measured score",
    "Unknown snapshot, mode, evaluation date and run\nmanifest remain unknown",
    "never fabricated exact-pair measurements", "Secondary\nlabels are not firsthand verification",
    "do not rank noncomparable percentages", "counterevidence and nonmonotonic effort results",
    "Guideline supersession/removal must not erase original source",
    "no automatic whole-CSV loading or full-dataset prompts", "matching rows on demand",
    "Routing approval and exact-content guideline approval are distinct",
    "Record approved scope and listed selections distinctly", "Missing hard gates stop readiness",
    "Inspect the failed child run and invocation", "Unknown cause",
    "No new failed-attempt commit/inverse authority",
)
UNSAFE_ROUTING = (
    "Catalog presence authorizes execution", "Unsupported runtime effort may proceed",
    "Risk always selects high effort", "Reviewer role always selects high effort",
    "Weak oracles select maximum effort", "Always default to medium effort",
    "No benchmark row forbids a supported pairing", "Estimated scores prove exact-pair success",
    "Owner preference is a measured advantage", "Rank all harness percentages together",
    "Automatically load the whole CSV", "Routing approval authorizes guideline mutation",
)


def routing_errors(text):
    body = checker.section(text, "## Family and effort routing")
    return (["missing " + clause for clause in ROUTING_GUARDS if clause not in body]
            + ["unsafe " + policy for policy in UNSAFE_ROUTING if policy.lower() in text.lower()])


class FamilyEffortContractTests(unittest.TestCase):
    def test_old_class_rule_is_not_current_routing_authority(self):
        requirements = (ROOT / "REQUIREMENTS.md").read_text()
        self.assertIn("## Model family and independent effort", requirements)
        for old in ("Routing retains approved sonnet/opus classes", "two-class configuration", "deepseek/"):
            self.assertNotIn(old, requirements)
        for name in ("Luna", "Terra", "Sol", "Astra"):
            self.assertIn(name, requirements)

    def test_independent_rubric_hard_gates_and_no_row_guard_deletions(self):
        text = checker.load_texts()["coordination"]
        self.assertEqual(routing_errors(text), [])
        for guard in ROUTING_GUARDS:
            with self.subTest(guard=guard):
                self.assertEqual(text.count(guard), 1)
                self.assertIn("missing " + guard, routing_errors(text.replace(guard, "", 1)))

    def test_named_unsafe_support_risk_role_no_row_and_evidence_mutations(self):
        text = checker.load_texts()["coordination"]
        for policy in UNSAFE_ROUTING:
            with self.subTest(policy=policy):
                self.assertIn("unsafe " + policy, routing_errors(text + "\n" + policy))

    def test_source_discovery_and_exact_guideline_gate_survive_supersession(self):
        text = checker.load_texts()["coordination"]
        for clause in ("source\nfacts, unknown metadata or discovery links", "source archive → matching rows on demand"):
            self.assertIn(clause, text)
        exact = checker.section(text, "## Exact guideline approval")
        for clause in ("resulting content must be explicitly approved", "Rejection leaves guidelines byte-identical",
                       "compare with the approved baseline", "drift stops"):
            self.assertIn(clause, exact)


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
            "failed, blocked or partial work and manual/user", "role/model/reasoning effort (or `unknown`)",
            "individual attempt/check results, reviewer findings, inspected failure cause", "Unknown is not success",
            "reuse on resume, never overwrite another run", "separate summary/task records", "before refreshing",
            "after every evidence write", "no duplicate rows", "reconcile interrupted record/index updates",
            "retaining existing runs", "never a no-write fallback",
        ):
            with self.subTest(clause=clause):
                self.assert_rejected("coordinator", "### Coordination evidence checkpoint", clause, "coordination-checkpoint")
        for clause in ("append-oriented", "run record before its index entry", "Keep one row per run", "sensitive payloads"):
            self.assert_rejected("coordination", "## Separate factual evidence", clause, "coordination-evidence")

    def test_A6_reflection_uncertainty_and_no_update_removals(self):
        for clause in (
            "nine reflection questions", "project-specific versus general", "reusable versus incidental",
            "reinforcement; contradiction", "guideline support versus evidence-only", "delegation lessons; manual validation",
            "surprises needing qualification/more evidence", "insufficient and conflicting", "separately from `REFLECTION.md`",
            "supporting/contradicting pointers", "no update\nproposed", "not a universal ban or permanent routing rule",
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

    def test_A11_routing_selection_class_and_inspected_cause_removals(self):
        for clause in (
            "usable owner-selected options", "Low favors a cheaper", "strong executable acceptance oracle",
            "stronger verification/review", "not forced opus", "reclassification or share-gate bypass",
            "Never silently\nreplace selected models, weaken approved classes",
            "inspect the child run and failed invocation first", "unrelated workspace changes",
            "architecture and authority permit", "verified stronger capability and owner-selection gates",
            "Unknown cause", "unestablished clean state stops", "Record both attempts",
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
        for clause in (
            "Commit each task's verified changes as one focused commit", "only asynchronously in the background",
            "Run all batches sequentially", "never silently switch models or downgrade task classes",
            "Inspect the failed run and tool invocation before retry or relaunch", "fresh independent",
            "REQUIRED checks remain required",
        ):
            changed = dict(self.texts)
            self.assertIn(clause, changed["coordinator"])
            changed["coordinator"] = changed["coordinator"].replace(clause, "", 1)
            self.assertTrue(any(e.startswith("execution-freeze:") for e in checker.check_contracts(changed)), clause)

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
        self.summary.write_text("# Simulated run\nAreas/tags: heuristic\nOutcome: partial; manual validation pending\n")
        (self.run / "T001.md").write_text(
            "# Simulated T001 implementation; tags: heuristic\n"
            "residual_reasoning: medium — executable output oracle\n"
            "approved family: fictional-family; role: worker; model: fictional-option-A; effort: unknown\n"
            "Attempt 1: FAIL; check: output mismatch; cause: inspected missed boundary\n"
            "Reviewer findings: unknown; manual validation: pending, not success\n"
            "Correction: authorized failed-task isolation; unrelated work preserved\n"
            "Escalation: verified usable owner-selected option selected by fictional owner\n"
            "Attempt 2: automated PASS; model: fictional-option-B; effort: unknown\n"
            "Manual validation: FAIL — visually implausible output; outcome: partial\n"
            "Surprise: automation missed manual defect; no permanent routing rule\n")
        self.index = self.evidence / "INDEX.md"
        self.row = "| [simulated-2026-01-01-heuristic](simulated-2026-01-01-heuristic/SUMMARY.md) | 2026-01-01 | heuristic | manual checkpoint | partial |\n"
        self.index.write_text("# Simulated evidence index\n" + self.row)
        self.reflection = self.run / "REFLECTION.md"

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
        (self.run / "T002.md").write_text("# Simulated T002 verification\nOutcome: blocked; capability unknown\n")
        second = self.evidence / "simulated-2026-01-02-other"
        second.mkdir()
        (second / "SUMMARY.md").write_text("# Simulated unrelated run\nTags: other; outcome: PASS\n")
        (second / "T001.md").write_text("# Simulated independent task\nOutcome: PASS; effort: unknown\n")
        with self.index.open("a") as f:
            f.write("| [simulated-2026-01-02-other](simulated-2026-01-02-other/SUMMARY.md) | 2026-01-02 | other | unrelated | PASS |\n")
        self.assertEqual(len(list(self.evidence.glob("*/SUMMARY.md"))), 2)
        self.assertEqual(len(list(self.evidence.glob("*/T*.md"))), 3)
        first = (self.run / "T001.md").read_text()
        for fact in ("Attempt 1: FAIL", "Attempt 2:", "effort: unknown", "Manual validation: FAIL", "outcome: partial", "no permanent routing rule"):
            self.assertIn(fact, first)
        self.assertNotIn("Attempt 1", self.index.read_text())
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
        with (self.run / "T001.md").open("a") as f:
            f.write("Resume correction: manual output now validated PASS\n")
        self.summary.write_text(self.summary.read_text() + "Resume: manual PASS; overall PASS\n")
        # Deliberately interrupted example: record exists but row is stale.
        self.assertEqual(self.index.read_text(), old_index)
        updated = self.row.replace("| partial |", "| PASS after resume |")
        self.index.write_text(old_index.replace(self.row, updated))
        # A second reconciliation of the same row is byte-idempotent.
        self.index.write_text(self.index.read_text().replace(self.row, updated))
        self.assertEqual(self.index.read_text().count("](simulated-2026-01-01-heuristic/SUMMARY.md)"), 1)
        self.assertIn("Attempt 1: FAIL", (self.run / "T001.md").read_text())
        self.assertIn("Resume correction", (self.run / "T001.md").read_text())
        self.assertIn(prior_row, self.index.read_text())
        self.assertEqual((prior / "SUMMARY.md").read_bytes(), prior_bytes)

    def test_A6_simulated_reflection_evidence_only_tentative_contrary_no_update(self):
        self.reflection.write_text(
            "# Simulated reflection, not planner guidance\n"
            "Direct observation: manual FAIL in T001.md; automation missed it\n"
            "Tentative scoped caution: heuristic outputs need manual validation\n"
            "Supporting: T001.md attempt 2; contrary: later valid output\n"
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
                self.reflection.write_text("# Simulated proposal\nDecision: " + state + "\nGuidelines unchanged; implementation approval is not memory approval\n")
                self.index.write_text("# Simulated evidence index\n" + self.row.replace("manual checkpoint", "decision " + state))
                self.assertEqual(self.guidelines.read_bytes(), self.baseline)
                self.assertIn(state, self.reflection.read_text())
                self.assertTrue((self.run / "T001.md").exists())

    def test_A8_simulated_exact_accept_edit_add_content_and_baseline_evidence(self):
        for decision, statement in (
            ("accept", b"- Scope: heuristic outputs; tentative: inspect an edge-case output manually.\n"),
            ("edit", b"- Scope: heuristic boundary outputs only; owner-supplied: manual checkpoint.\n"),
            ("add", b"- Scope: heuristic verification; owner-supplied: record manual findings separately.\n"),
        ):
            with self.subTest(decision=decision):
                self.guidelines.write_bytes(self.baseline)
                approved_result = self.baseline + statement
                self.reflection.write_text("# Simulated exact decision\nDecision: " + decision + "\nBaseline:\n" + self.baseline.decode() + "Approved resulting content:\n" + approved_result.decode())
                immediately_reread = self.guidelines.read_bytes()
                self.assertEqual(immediately_reread, self.baseline)
                self.guidelines.write_bytes(approved_result)  # prescribed example, not gate logic
                self.index.write_text("# Simulated evidence index\n" + self.row.replace("manual checkpoint", "approved " + decision))
                self.assertEqual(self.guidelines.read_bytes(), approved_result)
                self.assertIn(approved_result.decode(), self.reflection.read_text())

    def test_A8_simulated_concurrent_drift_preserved_and_renewal_pending(self):
        self.reflection.write_text("# Simulated pending exact diff\nApproved baseline:\n" + self.baseline.decode())
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
            (self.run / "T001.md").read_text()
        self.assertEqual(reads, [self.index, self.summary, self.run / "T001.md"])
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
