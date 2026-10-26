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


class TrackOpenIssueContractTests(unittest.TestCase):
    def setUp(self):
        self.text = SKILL.read_text()

    def test_source_contract_requires_investigation_before_create_and_readback(self):
        clauses = (
            "Perform a bounded,\nevidence-based RCA",
            "**verified observations:**",
            "**verified cause:**",
            "**hypotheses:**",
            "**uncertainty and next useful investigation:**",
            "An uncertain RCA does not block tracking\nindefinitely",
            "Preserve the intended body and the independently read-back body",
            "creation/readback is not that review",
            "After every create, update, close, or reopen, independently GET the exact issue",
            "do not blindly retry a possibly successful mutation",
        )
        for clause in clauses:
            self.assertIn(clause, self.text)
        self.assertLess(self.text.index("Perform a bounded,"), self.text.index("## Discover overlap"))
        self.assertLess(self.text.index("## Discover overlap"), self.text.index("## Create, scoped change"))

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
        safeguards = (
            "confirm the same target from verified remote evidence",
            "check that `gh` is usable, authenticated for the explicit host",
            "current authorization to write issues must be explicit",
            "across **all open and closed issues**",
            "Exclude pull requests",
            "`--body-file`",
            "credentials, tokens, personal data, and sensitive payloads",
            "only a narrowly authorized\nchange to the intended fields",
            "immediately GET the exact issue",
            "preserving unknown sections",
            "If the issue changed, is ambiguous, or cannot be safely preserved, stop that",
            "GET/list complete open+closed\nresults",
            "Do not create or\nfall back to a persistent local register",
        )
        for safeguard in safeguards:
            self.assertIn(safeguard, self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
