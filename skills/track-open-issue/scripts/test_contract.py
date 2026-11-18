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
        self.assertIn("preserve unrelated entry bytes and history", " ".join(TEXT.split()))
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

    def assert_contract(self, clauses):
        normalized = " ".join(TEXT.split())
        for clause in clauses:
            with self.subTest(clause=clause):
                self.assertIn(clause, normalized)

    def test_explicit_target_capability_and_deferred_response(self):
        self.assert_contract((
            "resolve `HOST`, `OWNER`, and `REPO`", "verified remote evidence",
            'gh auth status --hostname "$HOST"', "Do not install `gh`, refresh authentication",
            "successful reads or an ADMIN-looking field do not grant it",
            "`issue tracking: UNAVAILABLE` or `deferred`", "candidate/operation, evidence, resumption condition",
            "never create a persistent local fallback or write a historical register",
        ))

    def test_discovery_is_complete_safe_and_qualified(self):
        self.assert_contract((
            "`HOST/OWNER/REPO#N`", "A bare `#N` or `OI-N` is not an identity",
            "**all open and closed issues**", "--paginate", "state=all&per_page=100",
            "Exclude pull requests", "Never deduplicate, merge or reopen solely by title or partial similarity",
            "--body-file", "do not interpolate Markdown into shell commands or use `eval`",
        ))

    def test_autonomous_issue_label_requirement_and_boundaries(self):
        self.assert_contract((
            "autonomously agent-initiated new issue", "require the exact label `AI generated`",
            "General permission to track findings is not a user request for that specific issue",
            "User-requested issues need no label", "do not relabel existing overlap matches",
            "labels?per_page=100", "gh label create 'AI generated' --repo",
            "without separate approval", "does not grant issue-write authority",
            "do not alter existing label metadata", "defer creation", "do not create unlabelled",
            "--body-file \"$body_file\" --label 'AI generated'",
            "confirm the exact `AI generated` label", "never create a duplicate",
            "labels (except `AI generated` below)",
        ))

    def test_scoped_mutation_readback_and_checkpoint_guards(self):
        self.assert_contract((
            "Immediately before a body overwrite or state transition, GET the exact issue",
            "Preserve unknown sections, comments/history, labels, assignees and unrelated state",
            "not atomic compare-and-swap", "recorded evidence tied to the problem",
            "verified recurrence/resumption", "independently GET the exact issue by number",
            "Do not blindly retry a possibly successful mutation",
            "Operation confirmation is distinct from proof that the underlying problem is resolved",
            "External-only work makes no empty Git commit", "focused task checkpoint contract",
            "Routine small local fixtures", "do not prove live GitHub behavior",
        ))

    def test_operation_selection_and_quality_review_are_separate(self):
        self.assert_contract((
            "An ordinary delivery comment does not require fresh candidate RCA, overlap discovery or issue-body quality review",
            "A substantive problem-body change does",
            "After successful candidate issue-body readback", "separate fresh read-only quality reviewer",
            "selected reviewer configuration, preserving its model/effort",
            "`coherence-reviewer`", "`subagent` `get`", "actual read-back body",
            "must not create product requirements or mutate issues",
            "one ordinary in-scope wording correction", "compare with the reviewed body",
            "material outcome changes need owner action", "No automatic multi-round review loop",
            "preserve the mutation/readback outcome and report review incomplete",
            "inspect the failed invocation before any targeted retry",
        ))
        self.assertLess(TEXT.index("## Investigate and compare candidates"),
                        TEXT.index("## Make the scoped effect and read it back"))
        self.assertLess(TEXT.index("## Make the scoped effect and read it back"),
                        TEXT.index("## Review a recorded problem body"))

    def test_delivery_consumes_content_owner_but_keeps_closure_guard(self):
        self.assert_contract((
            "../finish-session/SKILL.md#issue-linked-delivery",
            "Consume its meaningful executive text", "explicit acceptance of the presented revision",
            "operation-scoped closure authority", "independently read back closure",
            "Acceptance of an earlier revision does not accept a corrected revision",
            "partial result", "retry only the missing operation after inspection",
            "not an authorized chat report", "`NOT VERIFIED`",
        ))


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
        self.assertIn("After every create, update, close or reopen, independently GET", TEXT)
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
