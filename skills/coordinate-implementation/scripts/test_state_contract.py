#!/usr/bin/env python3
"""Offline instruction/mutation and Git-backed scenario evidence, NOT model obedience.

The scenario decision helper is a symbolic walkthrough oracle, not coordinator code,
compaction handling, a persistence engine or a dispatch implementation. Real Git fixtures
check checkpoint ordering/dirty preservation; runtime child observations are explicitly
symbolic. Contract checks tie each scenario to its operational instruction carriers.
"""
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
COORD = ROOT / "skills/coordinate-implementation/SKILL.md"
TEXT = COORD.read_text()
LINK = "#brief-current-state-and-recovery"


def section(text, heading):
    marker = "## " + heading
    start = text.find(marker)
    if start < 0:
        return ""
    end = text.find("\n## ", start + len(marker))
    return text[start:] if end < 0 else text[start:end]


def norm(text):
    return " ".join(text.split())


# Carrying sections matter: a safety phrase in an unrelated summary does not suffice.
GUARDS = {
    "ownership": ("not a coordinator-owned tracker", "other authorized workflows",
                  "Preserve unrelated/custom content", "obtain owner approval",
                  "outside the selected project", "symlink escapes"),
    "brief": ("snapshot BRIEF", "roughly five short bullets", "omitting irrelevant fields",
              "ephemeral recovery bookmark", "goal", "source/tasks/approval links",
              "active execution/run identity", "No mandatory Git SHA", "material blocker",
              "next safe action", "conveys no authorization or acceptance",
              "never append historical ledgers", "remove verified finished items",
              "Preserve unrelated concurrent items", "An empty current block is valid",
              "Unknown completion/runtime/ownership", "without deleting durable artifacts",
              "successor must be independently current"),
    "lifecycle": ("before execution", "recovery-relevant boundaries", "Record a returned child ID immediately",
                  "Delegated briefs exclude snapshot writes", "not every dispatch or audited task/batch",
                  "Do not depend on advance compaction notification"),
    "recovery": ("After compaction, restart or uncertain execution context",
                 "Read the current snapshot", "Selectively open linked source/tasks", "current authorization",
                 "actual diffs and index/worktree ownership",
                 "verification before acceptance", "State may lag committed work",
                 "Inspect recorded delegated runs", "Do not replay every historical approval",
                 "running child means inspect/wait, not duplicate dispatch",
                 "Check for unrecorded active dispatches too",
                 "Missing runtime evidence stops replacement", "missing child ID requires runtime reconciliation",
                 "exact next action supported by reconciled current state",
                 "partial task-owned changes", "never guessed completion, blind retry or cleanup",
                 "Missing state never means no progress or no active child",
                 "Do not fabricate progress"),
    "persistence": ("No state-specific commit or evidence checkpoint is required",
                    "not a retained implementation/evidence task", "otherwise-required commit",
                    "may remain uncommitted across closeout", "Task-relative cleanliness excludes",
                    "task commit → separate run-summary/index evidence checkpoint",
                    "explicitly outside worker task/evidence paths", "Do not race Git/index commits",
                    "without coordinator waits", "safe index access",
                    "No worker task/evidence checkpoint or failure stop is waived",
                    "remove only the verified finished current item",
                    "retain paused, blocked or review/acceptance-pending work",
                    "Preserve existing dirty state", "overlap authorized",
                    "Re-read/compare", "concurrent drift, same-file ambiguity, write/check/commit failure stops",
                    "arrange a safe pause", "reconcile pending state/evidence"),
}
UNSAFE = {
    "heavy-dispatch": r"dispatch intent is checkpointed before launch|commit state before every dispatch",
    "routine-state": r"update state after every (?:task|batch|check|commit|poll)",
    "forced-refresh": r"always refresh state after recovery",
    "duplicate-dispatch": r"dispatch (?:a )?(?:new|replacement) worker while (?:the )?child is running",
    "stale-trust": r"trust (?:the )?snapshot without (?:git|evidence) reconciliation",
    "history": r"append (?:a )?(?:completed-task|historical) ledger to (?:the )?snapshot",
    "exclusive-owner": r"state\.md is (?:exclusively )?coordinator-owned",
    "terminal-retention": r"(?<!never )(?:replace (?:with|active progress with)|retain(?:ing)?(?: only)?) (?:a )?(?:short |concise )?terminal disposition",
}


CADENCE_GUARDS = (
    "Only these recovery-relevant events", "authorized work starts", "returned run identity",
    "materially changed next safe action", "verified completion",
    "Routine task or batch completion", "commits, polling", "do not trigger STATE writes",
    "healthy internal worker progress", "Skip byte-identical writes",
    "coalesce available facts", "State edits never trigger summary/index writes",
    "audited outcomes referencing worker checkpoints", "meaningful exceptions",
    "Reflection occurs once at terminal closeout or a genuine blocked pause",
    "worker task/evidence checkpoints remain unchanged",
)


def contract_errors(text):
    body = section(text, "Brief Current State and Recovery")
    errors = []
    for group, phrases in GUARDS.items():
        carrier = body
        if group in ("ownership", "brief", "lifecycle"):
            carrier = body.split("### Coordinator write boundaries", 1)[0]
        if group == "recovery":
            carrier = body.split("### Recovery before continuation", 1)[-1].split(
                "### Writes and checkpoint ordering", 1)[0] if "### Recovery before continuation" in body else ""
        elif group == "persistence":
            carrier = body.split("### Writes and checkpoint ordering", 1)[-1] if "### Writes and checkpoint ordering" in body else ""
        for phrase in phrases:
            if phrase not in norm(carrier):
                errors.append(group + ": " + phrase)
    cadence = body.split("### Coordinator write boundaries", 1)[-1].split(
        "### Recovery before continuation", 1)[0] if "### Coordinator write boundaries" in body else ""
    for phrase in CADENCE_GUARDS:
        if phrase not in norm(cadence):
            errors.append("cadence: " + phrase)
    # An ordered recovery recipe, not five disconnected mentions.
    recovery = body.split("### Recovery before continuation", 1)[-1].split("### Writes", 1)[0]
    if re.findall(r"^(\d)\. ", recovery, re.M) != ["1", "2", "3", "4", "5"]:
        errors.append("recovery-order")
    for name, pattern in UNSAFE.items():
        if re.search(pattern, norm(body).lower()):
            errors.append(name)
    if "first read the project snapshot" not in norm(text.split("## Load and Verify", 1)[0]):
        errors.append("entry-order")
    return errors


class ContractTests(unittest.TestCase):
    def test_complete_operational_contract(self):
        self.assertEqual(contract_errors(TEXT), [])

    def test_consumers_use_same_owner_and_closeout_stays_brief(self):
        for path in ("skills/finish-session/SKILL.md", "skills/initialize-coherence/SKILL.md",
                     "skills/memory-handling/references/project-coordination.md",
                     "skills/memory-handling/references/task-commit-contract.md",
                     "README.md", "REQUIREMENTS.md", "AGENTS.md", "docs/index.md"):
            with self.subTest(path=path):
                content = (ROOT / path).read_text()
                self.assertIn(LINK, content)
                for target in re.findall(r"\]\(([^)]+" + re.escape(LINK) + r")\)", content):
                    self.assertEqual(((ROOT / path).parent / target.split("#")[0]).resolve(), COORD)
        finish = section((ROOT / "skills/finish-session/SKILL.md").read_text(), "Step 6: Reconcile Brief Current State")
        for clause in ("Keep the current block BRIEF", "remove the verified finished item",
                       "finished planner spec", "empty current block", "exact next safe action",
                       "Reconcile any active child", "unresolved review/acceptance remains a gate",
                       "Preserve custom headers", "no mandatory Git SHAs or commands/results catalogue", "Never chase its own commit",
                       "never compete to write", "Do not append history"):
            self.assertIn(clause, norm(finish))
        self.assertNotIn("commands actually run", finish)
        self.assertIsNone(re.search(UNSAFE["terminal-retention"], norm(finish).lower()))

    def test_closeout_mutations_are_section_bound(self):
        text = (ROOT / "skills/finish-session/SKILL.md").read_text()
        heading = "Step 6: Reconcile Brief Current State"
        for phrase in ("remove the verified finished item", "finished planner spec",
                       "unrelated concurrent current-state content", "empty current block",
                       "cannot authorize deletion"):
            with self.subTest(phrase=phrase):
                body = section(text, heading)
                altered = norm(body).replace(phrase, "REMOVED", 1)
                mutated = text.replace(body, altered, 1) + "\n## Footer\n" + phrase
                self.assertNotIn(phrase, norm(section(mutated, heading)))
        mutated = section(text, heading) + "\nRetain a concise terminal disposition."
        self.assertIsNotNone(re.search(UNSAFE["terminal-retention"], norm(mutated).lower()))

    def test_deleted_recovery_not_rescued_by_summary(self):
        body = section(TEXT, "Brief Current State and Recovery")
        recovery = body.split("### Recovery before continuation", 1)[1].split("### Writes", 1)[0]
        mutated = TEXT.replace(recovery, "\n", 1) + "\nSummary: " + recovery
        self.assertTrue(any(e.startswith("recovery") for e in contract_errors(mutated)))

    def test_targeted_mutations_have_named_diagnostics(self):
        for group in ("ownership", "brief", "lifecycle", "recovery", "persistence"):
            for phrase in GUARDS[group]:
                pattern = r"\s+".join(re.escape(word) for word in phrase.split())
                body = section(TEXT, "Brief Current State and Recovery")
                altered, count = re.subn(pattern, "[removed guard]", body, count=1)
                mutated = TEXT.replace(body, altered, 1)
                with self.subTest(group=group, phrase=phrase):
                    self.assertEqual(count, 1)
                    self.assertIn(group + ": " + phrase, contract_errors(mutated))
        for event in ("task", "batch", "check", "commit", "poll"):
            mutated = TEXT.replace("### Recovery before continuation", f"Update STATE after every {event}.\n### Recovery before continuation", 1)
            self.assertIn("routine-state", contract_errors(mutated))
        for diagnostic, unsafe in (
            ("heavy-dispatch", "Dispatch intent is checkpointed before launch."),
            ("routine-state", "Update STATE after every task."),
            ("forced-refresh", "Always refresh STATE after recovery."),
            ("duplicate-dispatch", "Dispatch a new worker while the child is running."),
            ("stale-trust", "Trust the snapshot without Git reconciliation."),
            ("history", "Append a completed-task ledger to the snapshot."),
            ("exclusive-owner", "STATE.md is exclusively coordinator-owned."),
            ("terminal-retention", "Replace active progress with a short terminal disposition."),
        ):
            with self.subTest(diagnostic=diagnostic):
                mutated = TEXT.replace("### Recovery before continuation", unsafe + "\n### Recovery before continuation", 1)
                self.assertIn(diagnostic, contract_errors(mutated))

    def test_reordered_recovery_is_rejected(self):
        mutated = TEXT.replace("2. Selectively", "3. Selectively", 1).replace("3. Inspect", "2. Inspect", 1)
        self.assertIn("recovery-order", contract_errors(mutated))


class CadenceTests(unittest.TestCase):
    """Bounded rule-to-action walkthroughs, not a coordinator persistence engine."""
    def test_cadence_mutations_are_section_bound(self):
        body = section(TEXT, "Brief Current State and Recovery")
        for phrase in CADENCE_GUARDS:
            pattern = r"\s+".join(re.escape(word) for word in phrase.split())
            altered, count = re.subn(pattern, "REMOVED", body)
            with self.subTest(phrase=phrase):
                self.assertGreaterEqual(count, 1)
                # A footer/summary cannot rescue the missing operational boundary.
                self.assertIn("cadence: " + phrase, contract_errors(TEXT.replace(body, altered, 1) + "\n## Footer\n" + phrase))

    def test_symbolic_write_schedule_coalesces_and_skips_routine_work(self):
        self.assertEqual(contract_errors(TEXT), [])
        triggers = {"start", "child-id", "material-next-action", "completion"}
        for events, changed, state_write in (
            ({"start", "dispatch"}, True, True),
            ({"child-id"}, True, True),
            ({"audit", "dispatch"}, True, False),
            ({"blocker", "material-next-action"}, True, True),
            ({"review", "material-next-action"}, True, True),
            ({"completion"}, True, True),
            ({"recovery"}, True, False),
            ({"local-task", "commit", "batch-complete"}, True, False),
            ({"poll", "wait", "passing-check", "worker-task"}, True, False),
            ({"material-next-action"}, False, False),
            ({"blocker"}, False, False),
            ({"healthy-worker-progress"}, True, False),
        ):
            with self.subTest(events=events, changed=changed):
                self.assertEqual(changed and bool(events & triggers), state_write)
                # No dedicated commit/evidence cycle follows any bookmark edit.
                self.assertIn("State edits never trigger summary/index writes", norm(section(TEXT, "Brief Current State and Recovery")))

    def test_relevant_proof_reuse_and_affected_invalidation(self):
        from test_batching_contract import dispatch_seam_errors
        self.assertEqual(dispatch_seam_errors(TEXT), [])
        carrier = section(TEXT, "Select Execution Capability")
        for phrase in ("compare relevant scope/revision/environment", "refresh only affected proof"):
            self.assertIn(phrase, norm(carrier))
            altered = norm(TEXT).replace(phrase, "REMOVED", 1)
            # Explicit carrier check; unchanged valid examples cannot rescue a removed instruction.
            self.assertNotIn(phrase, norm(section(altered, "Select Execution Capability")).split(
                "## Execute and Integrate", 1)[0])
        proof = {"scope": "dispatch carrier", "revision": "carrier-r1", "environment": "python-local-1"}
        for event, current, refresh in (
            ("unchanged pass", dict(proof), False),
            ("administrative evidence commit", dict(proof), False),
            ("affected revision", dict(proof, revision="carrier-r2"), True),
            ("affected environment", dict(proof, environment="python-local-2"), True),
            ("unrelated revision", dict(proof), False),
        ):
            with self.subTest(event=event):
                invalidated = [key for key in proof if proof[key] != current[key]]
                self.assertEqual(bool(invalidated), refresh)
                outputs = {"dispatch proof": "refresh" if invalidated else "reuse", "unaffected intake proof": "reuse"}
                self.assertEqual(outputs["unaffected intake proof"], "reuse")
                self.assertEqual(outputs["dispatch proof"], "refresh" if refresh else "reuse")


# Deliberately symbolic: represents a manual rule-to-action walkthrough, NOT real runtime.
def walkthrough(*, authority=True, evidence=True, partial=False, runtime="idle",
                state="current", custom=False, dirty=False, owned=False, overlap=False,
                concurrent=False, persistence=True, all_done=False, reviewed=False):
    if not authority or not evidence:
        return "STOP: reconcile approval/evidence"
    if concurrent or (custom and not owned) or (dirty and not overlap):
        return "STOP: preserve state and resolve ownership/drift"
    if not persistence:
        return "STOP: persistence failure; inspect/pause any active child"
    if runtime == "unknown":
        return "STOP: reconcile runtime before dispatch"
    if runtime == "running":
        return "INSPECT/WAIT: existing child; audit on return"
    if partial:
        return "STOP: reconcile partial task diff/checks/checkpoint"
    if state in ("missing", "lagging"):
        return "RECONCILE: necessary project/Git/runtime facts; update only changed next action"
    if all_done:
        return "REMOVE: verified finished item" if reviewed else "REVIEW: acceptance remains gated"
    return "CONTINUE: verified dependency-ready action"


class GitScenarioTests(unittest.TestCase):
    """Real isolated Git/dirty-state checks plus explicit symbolic runtime observations."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-q")
        self.put("task.txt", "baseline\n")
        self.commit("task.txt", message="baseline")
        self.baseline = self.git("rev-parse", "HEAD").strip()
        self.put("STATE.md", "# Current state\n\n- Goal: finish task\n- Authority: tasks.md\n- Next: continue ready tasks\n")
        self.commit("STATE.md", message="initial state")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True, stderr=subprocess.STDOUT)

    def put(self, path, content):
        (self.root / path).write_text(content)

    def commit(self, *paths, message):
        self.git("add", "--", *paths)
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                 "commit", "--only", "-qm", message, "--", *paths)
        return self.git("rev-parse", "HEAD").strip()

    def verified_task(self):
        self.put("task.txt", "verified result\n")
        result = self.commit("task.txt", message="task checkpoint")
        self.put("SUMMARY.md", "- Task: " + result + "; check PASS (fixture)\n")
        evidence = self.commit("SUMMARY.md", message="separate evidence checkpoint")
        return result, evidence

    def assert_contract(self):
        self.assertEqual(contract_errors(TEXT), [])

    def test_compaction_after_verified_checkpoint(self):
        self.assert_contract()
        before = (self.root / "STATE.md").read_text()
        initial_count = int(self.git("rev-list", "--count", "HEAD"))
        result, evidence = self.verified_task()
        count = self.git("rev-list", "--count", "HEAD")
        self.assertEqual(int(count), initial_count + 2)  # Task and evidence only.
        # Task/evidence commits do not require a bookmark rewrite or state commit.
        self.assertEqual((self.root / "STATE.md").read_text(), before)
        self.assertEqual(self.git("rev-list", "--count", "HEAD"), count)
        self.assertEqual(self.git("show", result + ":task.txt"), "verified result\n")
        self.assertIn(result, self.git("show", evidence + ":SUMMARY.md"))
        self.assertNotIn(result, (self.root / "STATE.md").read_text())
        self.assertEqual(walkthrough(), "CONTINUE: verified dependency-ready action")
        self.assertEqual(self.git("status", "--short"), "")

    def test_compaction_while_worker_running(self):
        self.assert_contract()
        self.put("STATE.md", "- Child: symbolic-worker-17, running\n- Next: inspect child and audit on return\n")
        # Parent ID update remains pending, explicitly outside worker scope.
        self.put("task.txt", "worker result\n")
        result = self.commit("task.txt", message="worker task")
        self.put("SUMMARY.md", "- Worker task: " + result + "\n")
        self.commit("SUMMARY.md", message="worker evidence")
        self.assertEqual(self.git("status", "--short"), " M STATE.md\n")
        self.assertEqual(walkthrough(runtime="running"), "INSPECT/WAIT: existing child; audit on return")
        self.assertEqual(walkthrough(runtime="unknown"), "STOP: reconcile runtime before dispatch")
        self.assertEqual(walkthrough(persistence=False, runtime="running"),
                         "STOP: persistence failure; inspect/pause any active child")
        # Include pending state only in an otherwise-required owned evidence commit.
        self.put("SUMMARY.md", "- Worker audit: " + result + "; satisfied\n")
        self.commit("SUMMARY.md", "STATE.md", message="required audit evidence with pending bookmark")
        self.assertEqual(self.git("status", "--short"), "")

    def test_state_lagging_committed_work(self):
        self.assert_contract()
        result, evidence = self.verified_task()
        before = (self.root / "STATE.md").read_text()
        self.assertNotIn(self.baseline, before)
        self.assertNotEqual(result, self.baseline)
        self.assertEqual(self.git("merge-base", "--is-ancestor", result, evidence), "")
        count = self.git("rev-list", "--count", "HEAD")
        self.assertEqual(walkthrough(state="lagging"), "RECONCILE: necessary project/Git/runtime facts; update only changed next action")
        self.assertEqual(self.git("rev-list", "--count", "HEAD"), count)  # No duplicate task commit.
        self.assertEqual((self.root / "STATE.md").read_text(), before)  # No forced recovery refresh.

    def test_partial_task_owned_changes_with_stale_state(self):
        self.assert_contract()
        self.put("task.txt", "unfinished changes\n")
        before = self.git("diff", "--", "task.txt")
        self.assertEqual(walkthrough(partial=True, state="lagging"),
                         "STOP: reconcile partial task diff/checks/checkpoint")
        self.assertEqual(self.git("diff", "--", "task.txt"), before)
        self.assertEqual(self.git("status", "--short"), " M task.txt\n")

    def test_missing_state_or_conflicting_authority_evidence(self):
        self.assert_contract()
        (self.root / "STATE.md").unlink()
        self.assertEqual(walkthrough(state="missing"), "RECONCILE: necessary project/Git/runtime facts; update only changed next action")
        for gap in ({"authority": False}, {"evidence": False}, {"runtime": "unknown"}):
            with self.subTest(gap=gap):
                self.assertTrue(walkthrough(state="missing", **gap).startswith("STOP:"))
        self.assertFalse((self.root / "STATE.md").exists())  # No fabricated snapshot.

    def test_existing_custom_dirty_and_concurrent_state(self):
        self.assert_contract()
        custom = "# Project state\n\nCustom owner map: docs/\n\n<!-- current -->\n- Next: reconcile\n<!-- end -->\n"
        self.put("STATE.md", custom)
        self.commit("STATE.md", message="custom state")
        dirty = custom.replace("reconcile", "owner unsaved edit")
        self.put("STATE.md", dirty)
        self.put("unrelated.txt", "unrelated staged change\n")
        self.git("add", "--", "unrelated.txt")
        for context in ({"custom": True}, {"custom": True, "owned": True, "dirty": True},
                        {"owned": True, "overlap": True, "concurrent": True}):
            self.assertEqual(walkthrough(**context), "STOP: preserve state and resolve ownership/drift")
            self.assertEqual((self.root / "STATE.md").read_text(), dirty)
        # Explicit known block + approved dirty overlap, no drift: bounded update preserves header/index.
        self.assertEqual(walkthrough(custom=True, owned=True, dirty=True, overlap=True),
                         "CONTINUE: verified dependency-ready action")
        self.put("STATE.md", dirty.replace("owner unsaved edit", "inspect verified checkpoint"))
        count = self.git("rev-list", "--count", "HEAD")
        # STATE-only update: no task/evidence checkpoint, unrelated index survives.
        self.assertEqual(self.git("rev-list", "--count", "HEAD"), count)
        self.assertIn("Custom owner map: docs/", (self.root / "STATE.md").read_text())
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "unrelated.txt\n")

    def test_completion_closeout_removes_without_history(self):
        self.assert_contract()
        self.assertEqual(walkthrough(all_done=True), "REVIEW: acceptance remains gated")
        self.assertEqual(walkthrough(all_done=True, reviewed=True), "REMOVE: verified finished item")
        empty = "# Current state\n\n"
        self.put("STATE.md", empty)
        first = self.git("rev-parse", "HEAD").strip()
        count = self.git("rev-list", "--count", "HEAD")
        self.put("STATE.md", empty)  # Repeat: unchanged bytes, no extra checkpoint.
        self.assertEqual(self.git("status", "--short"), " M STATE.md\n")
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), first)
        self.assertEqual(self.git("rev-list", "--count", "HEAD"), count)
        self.assertEqual((self.root / "STATE.md").read_text(), empty)

    def test_finished_spec_removal_preserves_concurrent_and_durable_work(self):
        self.assert_contract()
        header = "# Project state\n\nCustom owner map: docs/\n\n"
        finished = "- Spec A: planning, pending review\n"
        concurrent = "- Implementation B: active, separately authorized\n- Investigation C: blocked\n"
        for path in ("source.md", "tasks.md", "SUMMARY.md"):
            self.put(path, "durable " + path + "\n")
        durable = {p: (self.root / p).read_bytes() for p in ("source.md", "tasks.md", "SUMMARY.md")}
        self.put("STATE.md", header + finished + concurrent)
        self.commit("STATE.md", "source.md", "tasks.md", "SUMMARY.md", message="mixed current work")
        before = (self.root / "STATE.md").read_text()
        # Explicit symbolic rule-to-action walkthrough, not a production state reconciler.
        self.assertEqual(walkthrough(all_done=True, reviewed=True), "REMOVE: verified finished item")
        self.put("STATE.md", before.replace(finished, "", 1))
        # Finished-entry removal alone does not create a commit.
        self.assertIn("STATE.md", self.git("diff", "--name-only"))
        self.assertEqual((self.root / "STATE.md").read_text(), header + concurrent)
        self.assertEqual({p: (self.root / p).read_bytes() for p in durable}, durable)
        self.assertNotIn("Implementation A", (self.root / "STATE.md").read_text())
        # No successor is invented when the spec was the only current item.
        self.put("STATE.md", header + finished)
        self.put("STATE.md", (self.root / "STATE.md").read_text().replace(finished, "", 1))
        self.assertEqual((self.root / "STATE.md").read_text(), header)

    def test_unfinished_or_uncertain_items_cannot_be_removed(self):
        self.assert_contract()
        for label, context in (
            ("paused", {}), ("blocked", {}), ("review-pending", {"all_done": True}),
            ("acceptance-pending", {"all_done": True, "reviewed": False}),
            ("runtime-unknown", {"runtime": "unknown"}),
            ("running-child", {"runtime": "running"}),
            ("ownership-unknown", {"custom": True}),
            ("drift", {"concurrent": True}), ("partial", {"partial": True}),
            ("completion-unknown", {"evidence": False}),
        ):
            with self.subTest(label=label):
                current = "# Current state\n\n- Spec A: " + label + "\n"
                self.put("STATE.md", current)
                self.assertNotEqual(walkthrough(**context), "REMOVE: verified finished item")
                self.assertEqual((self.root / "STATE.md").read_text(), current)


if __name__ == "__main__":
    unittest.main()
