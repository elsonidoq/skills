#!/usr/bin/env python3
"""Offline contract/scenario checks; these do not call gh or prove live API behavior."""
from pathlib import Path
import unittest


SKILL = Path(__file__).parents[1] / "SKILL.md"
TEXT = SKILL.read_text(encoding="utf-8")


class LifecycleContractTests(unittest.TestCase):
    def test_not_yet_cut_over_project_keeps_its_declared_owner(self):
        root = SKILL.resolve().parents[2]
        finish = (root / "skills/finish-session/SKILL.md").read_text()
        initialize = (root / "skills/initialize-coherence/SKILL.md").read_text()
        for text in (TEXT, finish, initialize):
            self.assertIn("Preserve the existing declared local register until approved cutover", text)
        self.assertIn("inspect open and closed entries", TEXT)
        self.assertIn("preserve unrelated entry bytes and history", TEXT)
        self.assertIn("not a fallback", TEXT)
        self.assertNotIn("use only its explicitly resolved GitHub Issues target", finish)
        self.assertIn("GitHub Issues", (root / "docs/index.md").read_text())
        self.assertIn("INCONCLUSIVE / NOT PASS", (root / "skills/import-open-issues/SKILL.md").read_text())

    def test_this_project_has_one_explicit_github_owner_and_import_support(self):
        root = SKILL.resolve().parents[2]
        for path in ("AGENTS.md", "README.md", "REQUIREMENTS.md", "docs/index.md"):
            text = (root / path).read_text()
            with self.subTest(path=path):
                self.assertIn("https://github.com/elsonidoq/skills/issues", text)
                self.assertNotIn("Canonical local register", text)
                self.assertNotIn("`docs/open_issues.md` is the canonical", text)
                self.assertNotIn("`docs/open_issues.md` holds the canonical", text)
        for path in ("scripts/check-task-commit-contract.py", "scripts/probe-pi-load.sh"):
            self.assertIn("import-open-issues", (root / path).read_text())

    def test_explicit_target_capability_and_deferred_response(self):
        for clause in (
            "Resolve `HOST`, `OWNER`, and `REPO`", "verified remote evidence",
            "gh auth status --hostname \"$HOST\"", "Do not install `gh`, refresh authentication",
            "successful reads or an ADMIN-looking field do not establish it",
            "`issue tracking: UNAVAILABLE` or `deferred`", "candidate, evidence,\nresumption condition",
            "Do not create or\nfall back to a persistent local register",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, TEXT)

    def test_discovery_is_complete_safe_and_qualified(self):
        for clause in (
            "`HOST/OWNER/REPO#N`", "bare `#N` or `OI-N` is not an identity",
            "**all open and closed issues**", "--paginate", "state=all&per_page=100",
            "Exclude pull requests", "Never deduplicate, merge, or reopen solely from a title",
            "--body-file", "do not interpolate Markdown into a shell command", "use `eval`",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, TEXT)

    def test_autonomous_issue_label_requirement_and_boundaries(self):
        for clause in (
            "rather than explicitly requested by\nthe user",
            "require the exact label `AI generated`",
            "General permission to track discovered work",
            "User-requested issues do not require this",
            "Do not relabel existing matches",
            'labels?per_page=100',
            "gh label create 'AI generated' --repo",
            "without asking for separate approval",
            "not issue creation without the\nexisting target-specific issue-write authority",
            "Do not modify an existing label's metadata",
            "defer the issue create",
            "do not create it unlabelled",
            "--body-file \"$body_file\" --label 'AI generated'",
            "independently read-back labels include the exact `AI generated` label",
            "do not create a duplicate",
            "except the required `AI generated` label below",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, TEXT)

    def test_scoped_mutation_readback_and_checkpoint_guards(self):
        for clause in (
            "immediately GET the exact issue", "preserving unknown sections",
            "comments/history, labels, assignees, or\nunrelated state",
            "not an\natomic compare-and-swap guarantee", "recorded evidence tied to the issue's problem",
            "verified recurrence or resumption basis", "independently GET the exact issue by number",
            "do not blindly retry a possibly successful mutation",
            "Separate remote operation confirmation from proof", "External-only issue work creates no empty Git commit",
            "focused task checkpoint contract", "Local small fixtures are\nallowed under routine authority",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, TEXT)


class ScenarioTests(unittest.TestCase):
    """Symbolic mutation cases assert the promised decision boundary, not gh semantics."""
    def decide(self, *, target=True, gh=True, auth=True, issues=True, write=True,
               drift=False, response_known=True, outcome_evidence=True, recurrence=False):
        if not all((target, gh, auth, issues)):
            return "UNAVAILABLE/deferred: candidate/evidence/resumption"
        if not write:
            return "deferred: candidate/evidence/resumption/write authority"
        if drift:
            return "deferred: reinspection/review; preserve unrelated fields"
        if not response_known:
            return "deferred: reconcile full listing and GET; no retry"
        if not outcome_evidence:
            return "operation-confirmed/outcome-unverified"
        if recurrence:
            return "reopen-with-recorded-basis"
        return "mutate-then-independent-readback"

    def test_missing_capabilities_never_select_local_fallback(self):
        for field in ("target", "gh", "auth", "issues", "write"):
            kwargs = {field: False}
            result = self.decide(**kwargs)
            self.assertIn("candidate/evidence/resumption", result)
            self.assertNotIn("local", result)

    def test_closeout_candidate_deferred_output_remains_qualified_and_actionable(self):
        # Base/optional-Jev routing supplies a candidate; this direct consumer owns the
        # capability boundary and must return its facts rather than a local substitute.
        result = self.decide(target=True, gh=True, auth=True, issues=True, write=False)
        self.assertEqual(result, "deferred: candidate/evidence/resumption/write authority")
        self.assertIn("`HOST/OWNER/REPO#N`", TEXT)
        self.assertIn("After every create, update, close, or reopen, independently GET", TEXT)
        self.assertNotIn("local fallback", result)

    def test_concurrent_body_change_stops_scoped_overwrite(self):
        result = self.decide(drift=True)
        self.assertEqual(result, "deferred: reinspection/review; preserve unrelated fields")

    def test_lost_response_never_retries_blindly(self):
        self.assertEqual(self.decide(response_known=False),
                         "deferred: reconcile full listing and GET; no retry")

    def test_close_without_outcome_and_verified_recurrence_are_distinct(self):
        self.assertEqual(self.decide(outcome_evidence=False), "operation-confirmed/outcome-unverified")
        self.assertEqual(self.decide(recurrence=True), "reopen-with-recorded-basis")


if __name__ == "__main__":
    unittest.main(verbosity=2)
