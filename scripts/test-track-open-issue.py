#!/usr/bin/env python3
"""Offline contract fixture for track-open-issue; simulated calls are not GitHub proof."""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "track-open-issue" / "SKILL.md"
TARGET = "github.com/example/project"


class SimulatedGh:
    """Controlled command transcript only; it never invokes gh or a network service."""

    def __init__(self, body, existing_body=None):
        self.body = body
        self.existing_body = existing_body
        self.calls = []

    def discover(self):
        self.calls.append(("GET", f"repos/{TARGET}/issues?state=all&per_page=100", "paginate"))
        return [
            {"number": 3, "state": "open", "body": self.existing_body},
            {"number": 4, "state": "closed", "body": "closed overlap evidence"},
            {"number": 9, "pull_request": {}, "body": self.body},
        ]

    def create(self, title, body_file):
        self.calls.append(("CREATE", TARGET, title, body_file))
        return 27

    def readback(self, number):
        self.calls.append(("GET", f"repos/{TARGET}/issues/{number}"))
        return {"number": number, "html_url": f"https://{TARGET}/issues/{number}", "body": self.body}

    def update_body(self, number, expected_body, replacement_body):
        self.calls.append(("PATCH", f"repos/{TARGET}/issues/{number}", "body-only"))
        if self.body != expected_body:
            return False
        self.body = replacement_body
        return True


def investigated_body(observations, cause, hypotheses, uncertainty, next_step):
    cause_text = cause if cause else "No verified cause established."
    return "\n".join((
        "## Original intent", "Track the reported failure without repairing the application.",
        "## Verified observations", observations,
        "## Verified cause", cause_text,
        "## Hypotheses", hypotheses,
        "## Uncertainty and next useful investigation", f"{uncertainty}\nNext: {next_step}",
    ))


def create_then_readback(gh, body):
    """Controlled ordering oracle: discovery precedes targeted create and exact GET readback."""
    issues = gh.discover()
    if any(issue.get("body") == body for issue in issues if "pull_request" not in issue):
        return "deduplicated", None
    number = gh.create("Focused investigated failure", "issue-body.md")
    return "created", gh.readback(number)


def reconcile_unknown_mutation(gh, number):
    """An unknown response reconciles exact state and full discovery; it never repeats CREATE."""
    readback = gh.readback(number)
    if readback is not None:
        return "reconciled", readback
    gh.discover()
    return "deferred", None


class SimulatedReviewer:
    """A controlled stand-in; its finding is not independent reviewer judgment."""

    configuration = {"provider": "configured-provider", "model": "configured-reviewer"}

    def __init__(self, finding=None):
        self.finding = finding
        self.contexts = []

    def review(self, context):
        self.contexts.append(context)
        return self.finding


def review_then_correct(gh, reviewer, original_intent, evidence, uncertainty, readback):
    """Mechanical ordering oracle for configured read-only review and one guarded correction."""
    if reviewer is None:
        return "incomplete", None, readback
    context = {
        "original_intent": original_intent,
        "primary_evidence": evidence,
        "uncertainty": uncertainty,
        "actual_body": readback["body"],
        "reviewer_configuration": reviewer.configuration,
    }
    finding = reviewer.review(context)
    if finding is None:
        return "complete", "clean", readback
    latest = gh.readback(readback["number"])
    if latest["body"] != readback["body"]:
        return "incomplete", "deferred-concurrent-body", latest
    corrected = latest["body"].replace(finding["before"], finding["after"])
    if not gh.update_body(readback["number"], latest["body"], corrected):
        return "incomplete", "deferred-concurrent-body", gh.readback(readback["number"])
    return "complete", finding, gh.readback(readback["number"])


class TrackOpenIssueContractTests(unittest.TestCase):
    def setUp(self):
        self.text = SKILL.read_text()

    def test_source_contract_requires_investigation_before_create_and_readback(self):
        text = " ".join(self.text.split())
        clauses = (
            "Perform bounded evidence-based RCA", "verified observations",
            "verified cause only when causally established", "labelled hypotheses",
            "uncertainty and the next useful investigation",
            "Uncertain cause is not an indefinite filing block",
            "retain both intended and actual read-back body for quality review",
            "Creation/readback is not independent quality review",
            "separate fresh read-only quality reviewer",
            "selected reviewer configuration, preserving its model/effort; do not hardcode",
            "original user intent, primary evidence, uncertainty/next investigation and actual read-back body",
            "ambiguity/conflict, omission, promoted-assumption, scope-creep",
            "over-prescribed-mechanism/check findings", "immediately GET, compare with the reviewed body",
            "No automatic multi-round review loop",
            "After every create, update, close or reopen, independently GET the exact issue",
            "Do not blindly retry a possibly successful mutation",
        )
        for clause in clauses:
            self.assertIn(clause, text)
        order = (
            "Perform bounded evidence-based RCA", "inspect overlaps by problem",
            "## Make the scoped effect and read it back",
            "After every create, update, close or reopen",
            "## Review a recorded problem body", "For one ordinary in-scope wording correction",
        )
        positions = [self.text.index(clause) for clause in order]
        self.assertEqual(positions, sorted(positions))

    def test_simulated_rca_create_and_exact_readback_preserve_actual_body(self):
        body = investigated_body(
            "Command exits nonzero with recorded stderr.",
            "The failing command is verified to receive an invalid argument.",
            "A dependency regression may also contribute.",
            "The dependency version was not inspected.",
            "inspect the resolved dependency version",
        )
        gh = SimulatedGh(body)
        outcome, readback = create_then_readback(gh, body)
        self.assertEqual(outcome, "created")
        self.assertEqual(readback["body"], body)
        self.assertEqual(gh.calls, [
            ("GET", f"repos/{TARGET}/issues?state=all&per_page=100", "paginate"),
            ("CREATE", TARGET, "Focused investigated failure", "issue-body.md"),
            ("GET", f"repos/{TARGET}/issues/27"),
        ])
        self.assertIn("## Original intent", readback["body"])
        self.assertIn("## Verified cause", readback["body"])
        self.assertIn("## Hypotheses", readback["body"])

    def test_simulated_read_only_review_gets_actual_body_and_one_narrow_correction(self):
        body = investigated_body("Observed failure.", None, "No alternative.", "Trace absent.", "collect trace")
        gh = SimulatedGh(body)
        _, readback = create_then_readback(gh, body)
        reviewer = SimulatedReviewer({"before": "No alternative.", "after": "One unverified alternative exists."})
        result, finding, final = review_then_correct(
            gh, reviewer, "Track the failure without repairing the application.", "Observed failure.",
            "Trace absent.", readback,
        )
        self.assertEqual(result, "complete")
        self.assertEqual(final["body"], body.replace(finding["before"], finding["after"]))
        self.assertEqual(reviewer.contexts, [{
            "original_intent": "Track the failure without repairing the application.",
            "primary_evidence": "Observed failure.",
            "uncertainty": "Trace absent.",
            "actual_body": body,
            "reviewer_configuration": reviewer.configuration,
        }])
        self.assertEqual(gh.calls[-3:], [
            ("GET", f"repos/{TARGET}/issues/27"),
            ("PATCH", f"repos/{TARGET}/issues/27", "body-only"),
            ("GET", f"repos/{TARGET}/issues/27"),
        ])

    def test_unavailable_or_concurrent_review_is_incomplete_without_overwrite(self):
        body = investigated_body("Observed failure.", None, "No alternative.", "Trace absent.", "collect trace")
        gh = SimulatedGh(body)
        _, readback = create_then_readback(gh, body)
        self.assertEqual(review_then_correct(gh, None, "intent", "evidence", "uncertainty", readback)[0], "incomplete")

        reviewer = SimulatedReviewer({"before": "No alternative.", "after": "corrected"})
        original_readback = gh.readback
        calls = 0
        def concurrent_readback(number):
            nonlocal calls
            calls += 1
            result = original_readback(number)
            if calls == 1:
                result = dict(result, body="concurrent content")
            return result
        gh.readback = concurrent_readback
        result, finding, final = review_then_correct(gh, reviewer, "intent", "evidence", "uncertainty", readback)
        self.assertEqual((result, finding, final["body"]), ("incomplete", "deferred-concurrent-body", "concurrent content"))
        self.assertEqual(gh.body, body)

    def test_unknown_mutation_response_reconciles_without_blind_repeat(self):
        gh = SimulatedGh("read-back body")
        gh.readback = lambda number: (gh.calls.append(("GET", f"repos/{TARGET}/issues/{number}")) or None)
        outcome, readback = reconcile_unknown_mutation(gh, 27)
        self.assertEqual((outcome, readback), ("deferred", None))
        self.assertEqual(gh.calls, [
            ("GET", f"repos/{TARGET}/issues/27"),
            ("GET", f"repos/{TARGET}/issues?state=all&per_page=100", "paginate"),
        ])
        self.assertFalse(any(call[0] == "CREATE" for call in gh.calls))

    def test_exact_duplicate_is_not_recreated_and_pull_requests_are_excluded(self):
        body = investigated_body("Observed failure.", None, "No alternative.", "No trace.", "collect trace")
        gh = SimulatedGh(body, existing_body=body)
        outcome, readback = create_then_readback(gh, body)
        self.assertEqual((outcome, readback), ("deduplicated", None))
        self.assertEqual(gh.calls, [("GET", f"repos/{TARGET}/issues?state=all&per_page=100", "paginate")])

    def test_uncertain_rca_remains_trackable_in_the_simulated_transcript(self):
        body = investigated_body(
            "The failure report has a reproducible timestamp.",
            None,
            "The remote service may have rejected a malformed request.",
            "No request trace is available.",
            "obtain a redacted request trace",
        )
        gh = SimulatedGh(body)
        outcome, readback = create_then_readback(gh, body)
        self.assertEqual(outcome, "created")
        self.assertEqual(readback["body"], body)
        self.assertIn("No verified cause established.", body)
        self.assertIn("Next: obtain a redacted request trace", body)

    def test_retained_safeguards_are_explicit(self):
        text = " ".join(self.text.split())
        safeguards = (
            "confirm the same target from verified remote evidence",
            "verify usable `gh`, authentication for that explicit host",
            "Current write authority must explicitly cover this target and operation",
            "across **all open and closed issues**", "Exclude pull requests",
            "`--body-file`", "credentials, tokens, personal data and sensitive payloads",
            "make only the narrowly authorized change",
            "Immediately before a body overwrite or state transition, GET the exact issue",
            "Preserve unknown sections",
            "Changed content, ambiguity or uncertain preservation stops the overwrite/transition",
            "reconcile complete open+closed listings and exact GET before any retry",
            "never create a persistent local fallback or write a historical register",
        )
        for safeguard in safeguards:
            self.assertIn(safeguard, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
