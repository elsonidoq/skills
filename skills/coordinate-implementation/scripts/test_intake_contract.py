#!/usr/bin/env python3
"""Scoped instruction mutations; not runtime obedience proof."""
from pathlib import Path
import unittest
import re

TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text()


def section(text, heading):
    marker = "## " + heading
    start = text.find(marker)
    if start < 0:
        return ""
    match = re.search(r"(?:\n| )## ", text[start + len(marker):])
    end = start + len(marker) + match.start() if match else -1
    return " ".join((text[start:] if end < 0 else text[start:end]).split())


GUARDS = {
    "Load and Verify": (
        "current-content review/scope authorization", "Missing, stale or unverifiable approval",
        "TinySpec needs separate source/tasks", "Standard needs specification/plan/tasks, both current approvals",
        "required SpecKit stage evidence", "legacy source shape", "approval/recovery mapping",
        "baseline HEAD", "allowed paths", "index/ worktree ownership", "required check baseline",
        "never adopts or commits unknown work", "No automatic STATE creation, editing or removal",
        "Missing coordination store or STATE is nonblocking",
    ),
    "Prepare Approved Execution": (
        "fresh independent reviewer", "No unauthorized local fallback",
        "complete approved implementation task list", "including completed tasks",
        "Up to three bounded tasks", "More than three require delegation",
        "observed context", "All implementation batches execute sequentially, never in parallel",
        "use `ask_user`", "explicit batch/profile approval before writes or dispatch",
        "Reuse verified unchanged approval", "supported effort", "callable binding",
        "at assignment and dispatch", "no silent settings/agent override",
        "unobservable actual binding/effort is unknown",
    ),
    "Delegate": (
        "whole unchanged REQUIRED union before coding", "smallest check", "expected proof and pass condition",
        "permission/manual gates", "without routine coordinator approval",
        "Once required preparation is satisfied, dispatch", "Reopen only affected decisions/checks",
        "concrete contradiction", "failed prerequisite", "material scope change",
        "ownership, permission, profile, runtime", "Reuse unchanged applicable proof",
        "routine progress is not invalidation",
    ),
    "Execute and Integrate": (
        "actual diff", "focused commit/SHA", "REQUIRED outputs", "residual owned changes",
        "Only satisfied REQUIRED items and fulfilled original gates release dependents",
        "No extra evidence-only checkpoint", "no skip/defer question", "No-Git fallback",
        "coordinator alone may recover", "failed recovery stops dispatch",
        "same original contracts", "Clean retry is exceptional", "Unknown cause blocks blind restart",
        "Representative-sample manual STOP", "optional checks cannot compensate",
    ),
    "Review and Acceptance": (
        "No per-task reviews", "one fresh independent final review", "not an implementation session",
        "full committed revision range", "Missing reviewer blocks final acceptance",
        "every REQUIRED item disposition", "selected versus observed profile",
    ),
}


def contract_errors(text):
    errors = []
    for heading, clauses in GUARDS.items():
        body = section(text, heading)
        errors.extend(f"{heading}: missing {clause}" for clause in clauses if clause not in body)
    for unsafe in ("Always replan approved tasks", "Repeat unchanged preflight before every task",
                   "Accept the worker report without inspecting evidence",
                   "wait for coordinator validation before next-task writes"):
        if unsafe in text:
            errors.append("plan-trust: " + unsafe)
    return errors


class IntakeContractTests(unittest.TestCase):
    def test_self_contained_approved_intake_to_final_review(self):
        self.assertEqual(contract_errors(TEXT), [])

    def test_each_actionable_guard_removal_fails_in_its_carrier(self):
        for heading, clauses in GUARDS.items():
            for clause in clauses:
                with self.subTest(heading=heading, clause=clause):
                    # Moving a rule to a footer cannot replace its actionable boundary.
                    body = section(TEXT, heading)
                    normalized = " ".join(TEXT.split())
                    altered = normalized.replace(body, body.replace(clause, "REMOVED"), 1)
                    errors = contract_errors(altered + " ## Footer " + clause)
                    self.assertTrue(any(e.startswith(heading + ":") for e in errors), errors)

    def test_family_shortlist_accounts_for_plausible_omissions(self):
        # Static carrier sensitivity and authored shortlist cases, not live routing proof.
        rubric = (Path(__file__).parents[1] / "references" / "batch-routing.md").read_text()
        heading = "Provisional family and effort choices"
        clauses = (
            "Build the suitability shortlist across the rubric's family options, not a habitual two-family subset",
            "Briefly explain omissions of other plausible families",
            "Do not enumerate every model variant or force diversity",
        )
        body = section(rubric, heading)
        for clause in clauses:
            with self.subTest(clause=clause):
                self.assertIn(clause, body)
                altered = " ".join(rubric.split()).replace(clause, "REMOVED", 1)
                self.assertNotIn(clause, section(altered + " ## Footer " + clause, heading))
        # A plausible third family needs consideration or a reason, not a launch.
        plausible = {"Luna", "Sol", "Terra"}
        for considered, omitted_reasons, complete in (
            ({"Luna", "Sol"}, {}, False),
            ({"Luna", "Sol", "Terra"}, {}, True),
            ({"Luna", "Sol"}, {"Terra": "no additional task-fit benefit identified"}, True),
            ({"Luna", "Sol"}, {"Terra": ""}, False),
        ):
            accounted = considered | {family for family, reason in omitted_reasons.items() if reason.strip()}
            self.assertEqual(plausible <= accounted, complete)
        # One selected family still suffices; variants outside the plausible set add no quota.
        self.assertIn("Model variety is not itself a goal", body)

    def test_administrative_loops_and_trust_only_acceptance_fail(self):
        for unsafe in ("Always replan approved tasks", "Repeat unchanged preflight before every task",
                       "Accept the worker report without inspecting evidence"):
            self.assertIn("plan-trust: " + unsafe, contract_errors(TEXT + "\n" + unsafe))

    def test_rubric_recipe_is_canonical_and_not_rescued_by_consumer_footer(self):
        # Static carrier check: consumers link the owner; this does not prove live reasoning.
        rubric = (Path(__file__).parents[1] / "references" / "batch-routing.md").read_text()
        heading = "First proposal recipe"
        clauses = (
            "actual invocation demands and verification boundaries",
            "Before comparing candidates, inspect only the retained evidence materially needed",
            "Then compare plausible adequate families and effort separately, and only then make a provisional proposal",
            "one plausible adequate alternative",
            "specific selection difference, or `no established difference`",
        )
        body = section(rubric, heading)
        for clause in clauses:
            with self.subTest(clause=clause):
                self.assertIn(clause, body)
                altered = " ".join(rubric.split()).replace(clause, "REMOVED", 1)
                self.assertNotIn(clause, section(altered + " ## Footer " + clause, heading))
        self.assertIn("references/batch-routing.md", TEXT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
