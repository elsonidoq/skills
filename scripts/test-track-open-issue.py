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


class SimulatedPlannerLifecycle:
    """Offline expected-order fixture, NOT a planner implementation or live GitHub proof."""

    def __init__(self, *, brainstorm=False, target=True, capability=True, auth=True,
                 scope=True, complete=True, overlap=None, uncertain=False, reviewer=True):
        self.options = locals().copy()
        self.events = []
        self.url = None

    def run(self):
        o, events = self.options, self.events
        events.append('understand')
        if o['brainstorm']:
            events.extend(('owner-question', 'actual-owner-answer'))
        events.append('depth-selection')  # Not issue-create authority.
        for prerequisite in ('target', 'capability', 'auth'):
            events.append('verify-' + prerequisite)
            if not o[prerequisite]:
                return 'pending: restore ' + prerequisite
        events.append('all-open-closed-pages-excluding-prs')
        if not o['complete']:
            return 'pending: finish overlap pagination'
        if o['overlap'] in ('open', 'closed'):
            events.extend(('compare-intent-scope-evidence', 'exact-GET-body-identity-state'))
            self.url = f'https://{TARGET}/issues/3'
            events.append('reuse-' + o['overlap'])
        elif o['overlap'] == 'ambiguous':
            return 'pending: inspect ambiguous overlap'
        else:
            if not o['scope']:
                return 'pending: obtain target/issue-create scope'
            events.append('CREATE-once-with-body-file')
            if o['uncertain']:
                events.extend(('reconcile-all-open-closed-pages', 'exact-candidate-GET'))
                return 'pending: resolve uncertain create; no retry'
            events.append('independent-GET-body-identity-state')
            self.url = f'https://{TARGET}/issues/27'
            if not o['reviewer']:
                return 'pending: resume body review on existing issue'
            events.append('separate-quality-review-complete')
        events.append(('artifacts-with-url', self.url))
        return 'ready'


class PlannerAssociationFixtureTests(unittest.TestCase):
    """Coupled by the planner carrier tests; simulated transcripts are not model obedience."""

    def test_needed_dialogue_create_readback_review_then_artifacts(self):
        flow = SimulatedPlannerLifecycle(brainstorm=True)
        self.assertEqual(flow.run(), 'ready')
        self.assertEqual(flow.events, [
            'understand', 'owner-question', 'actual-owner-answer', 'depth-selection',
            'verify-target', 'verify-capability', 'verify-auth',
            'all-open-closed-pages-excluding-prs', 'CREATE-once-with-body-file',
            'independent-GET-body-identity-state', 'separate-quality-review-complete',
            ('artifacts-with-url', f'https://{TARGET}/issues/27')])
        self.assertFalse(any('creation-question' in str(event) for event in flow.events))

    def test_exact_open_and_closed_reuse_needs_no_write_scope_or_reopen(self):
        for state in ('open', 'closed'):
            with self.subTest(state=state):
                flow = SimulatedPlannerLifecycle(overlap=state, scope=False, reviewer=False)
                self.assertEqual(flow.run(), 'ready')
                self.assertEqual(flow.url, f'https://{TARGET}/issues/3')
                self.assertIn('exact-GET-body-identity-state', flow.events)
                self.assertIn('reuse-' + state, flow.events)
                self.assertFalse(any('CREATE' in str(e) or 'reopen' in str(e) for e in flow.events))
                self.assertEqual(flow.events[-1], ('artifacts-with-url', flow.url))

    def test_missing_prerequisites_partial_pages_and_ambiguous_effects_stop_artifacts(self):
        for options, correction in (
            ({'target': False}, 'restore target'),
            ({'capability': False}, 'restore capability'),
            ({'auth': False}, 'restore auth'),
            ({'scope': False}, 'obtain target/issue-create scope'),
            ({'complete': False}, 'finish overlap pagination'),
            ({'overlap': 'ambiguous'}, 'inspect ambiguous overlap'),
            ({'uncertain': True}, 'resolve uncertain create; no retry'),
            ({'reviewer': False}, 'resume body review on existing issue'),
        ):
            with self.subTest(options=options):
                flow = SimulatedPlannerLifecycle(**options)
                self.assertEqual(flow.run(), 'pending: ' + correction)
                self.assertFalse(any(isinstance(e, tuple) for e in flow.events))
                creates = flow.events.count('CREATE-once-with-body-file')
                self.assertEqual(creates, int('uncertain' in options or 'reviewer' in options))
                if 'uncertain' in options:
                    self.assertEqual(flow.events[-2:], [
                        'reconcile-all-open-closed-pages', 'exact-candidate-GET'])
                if 'reviewer' in options:
                    self.assertEqual(flow.url, f'https://{TARGET}/issues/27')


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

    def test_linkage_carrier_preserves_scope_reconciliation_and_review_separation(self):
        # Inspect the actual operation, not an inert whole-file summary.
        text = ' '.join(self.text.split('## Confirm delivery issue/PR links\n', 1)[1]
                        .split('\n## ', 1)[0].split())
        for clause in (
            'known qualified delivery issue and known PR URLs',
            'each PR\'s issue and pull-request identities on their explicit host/repository',
            'all comment pages', 'regardless of trace host',
            'issue links to every confirmed trace part',
            'Reuse verified body/comment links',
            '`link_comment` operation-scoped authority for each destination',
            '`trace_comment` authority, issue context, read access and credentials do not grant link writes',
            'durable intent, complete pagination reconciliation',
            'independent full-body/identity/target comment readback',
            'reconcile all destination pages and exact candidate bodies/identities',
            'a collision or incomplete scan stops new comments',
            'Late PR discovery establishes only missing reciprocal links',
            'no trace resend, implementation replay or reopened review',
            'partial effects or failed readback are incomplete linkage, not success',
            'Link/trace comments need no separate problem-body quality reviewer',
            'retain that reviewer for new or substantively changed problem bodies',
            'Link confirmation is not owner acceptance or closure authority',
            'Do not create PRs, push, replace issue/PR bodies, close or reopen',
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

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
