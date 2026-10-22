import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from import_open_issues import ApplyAuthorization, GhApiTransport, IncompleteLookup, Source, apply, preview, reconcile

ROOT = Path(__file__).resolve().parents[3]
BASELINE_SHA256 = "314b9ddd758d25923105d85c23225293d0a1398b506d1b28925d783a5c3e1c7a"
SOURCE = Source("github.com", "elsonidoq/skills", "docs/open_issues.md", "952e39b813a443caeb7417e63c170e219a433dbd")


class PreviewTests(unittest.TestCase):
    def test_actual_baseline_is_faithfully_previewed_by_production_helper(self):
        original = (ROOT / "docs/open_issues.md").read_text()
        self.assertEqual(hashlib.sha256(original.encode()).hexdigest(), BASELINE_SHA256)
        result = preview(original, SOURCE, "elsonidoq/skills")
        self.assertEqual(result.diagnostics, ())
        self.assertEqual([r.title.split(":", 1)[0] for r in result.records], ["OI-18", "OI-19", *[f"OI-{n}" for n in range(1, 18)]])
        self.assertEqual(result.counts, {"records": 19, "open": 16, "closed": 3, "unmappable": 0})
        by_id = {r.title.split(":", 1)[0]: r for r in result.records}
        self.assertEqual({key for key, value in by_id.items() if value.state == "closed"}, {"OI-6", "OI-7", "OI-12"})
        for record in result.records:
            self.assertIn(record.original_excerpt, original)
            self.assertEqual(dict(record.fields)["Status"].lower(), record.state)
            for field in ("Problem", "Primary evidence", "Resumption condition"):
                self.assertIn(field, dict(record.fields))
                self.assertIn(dict(record.fields)[field], record.body)
            self.assertIn("Original Markdown excerpt", record.body)
            self.assertIn("952e39b813a443caeb7417e63c170e219a433dbd", record.body)
        self.assertIn("Latest verification (owner-controlled assignments)", dict(by_id["OI-15"].fields))
        self.assertIn("Temporary logs may expire", by_id["OI-8"].body)
        self.assertIn("not a confirmed", by_id["OI-5"].body)
        self.assertIn("[GitHub issue #2](https://github.com/elsonidoq/skills/issues/2)", by_id["OI-4"].body)
        self.assertIn("[OI-5](https://github.com/elsonidoq/skills/blob/952e39b813a443caeb7417e63c170e219a433dbd/docs/open_issues.md)", by_id["OI-6"].body)
        self.assertTrue(by_id["OI-18"].original_entry_url.endswith("#oi-18-resumed-runs-cannot-append-to-their-existing-jsonl-metrics-artifact"))

    def test_multiline_extra_fields_links_and_identity(self):
        text = """## OI-1: Renamed title\n\n- **Status:** open\n- **Problem:** First line\n  second line with [relative](../runtime/a.py#part), [absolute #2](https://github.com/x/y/issues/2), OI-9 and `../code.py`.\n- **Primary evidence:** evidence\n- **Resumption condition:** resume\n- **History:** retained\n"""
        result = preview(text, SOURCE, "dest/repo")
        record = result.records[0]
        self.assertEqual(record.identity, "github.com/elsonidoq/skills:docs/open_issues.md:OI-1")
        self.assertIn("https://github.com/elsonidoq/skills/blob/952e39b813a443caeb7417e63c170e219a433dbd/runtime/a.py#part", record.body)
        self.assertIn("[absolute #2](https://github.com/x/y/issues/2)", record.body)
        self.assertIn("[OI-9](https://github.com/elsonidoq/skills/blob/952e39b813a443caeb7417e63c170e219a433dbd/docs/open_issues.md)", record.body)
        self.assertIn("`../code.py`", record.body)
        self.assertIn(("History", "retained"), record.fields)
        renamed = preview(text.replace("Renamed title", "Revised title"), SOURCE, "dest/repo").records[0]
        self.assertEqual(renamed.identity, record.identity)
        other = preview(text, Source("github.com", "other/repo", "docs/open_issues.md", "different-revision"), "dest/repo").records[0]
        self.assertNotEqual(other.identity, record.identity)

    def test_unmappable_duplicate_unsafe_and_sensitive_inputs_are_diagnostic(self):
        valid = """## OI-1: Valid\n- **Status:** open\n- **Problem:** safe\n- **Primary evidence:** safe\n- **Resumption condition:** safe\n"""
        bad_status = valid.replace("OI-1: Valid", "OI-2: Unknown").replace("Status:** open", "Status:** pending")
        duplicate = valid.replace("Valid", "Duplicate")
        unsafe = valid.replace("OI-1: Valid", "OI-3: Unsafe").replace("safe", "<script>alert(1)</script>", 1)
        sensitive = valid.replace("OI-1: Valid", "OI-4: Sensitive").replace("safe", "token=DO_NOT_EXPORT", 1)
        result = preview(valid + bad_status + duplicate + unsafe + sensitive, SOURCE, "dest/repo")
        self.assertEqual([r.title for r in result.records], ["OI-1: Valid"])
        reasons = "\n".join(d.reason for d in result.diagnostics)
        self.assertIn("unmappable status", reasons)
        self.assertIn("duplicate OI identity", reasons)
        self.assertIn("unsafe Markdown", reasons)
        self.assertIn("sensitive candidate data rejected", reasons)
        self.assertNotIn("DO_NOT_EXPORT", "\n".join(r.body for r in result.records))
        self.assertEqual(result.counts["unmappable"], 4)

    def test_missing_structure_does_not_drop_valid_records_or_claim_completeness(self):
        valid = """## OI-1: Good\n- **Status:** closed\n- **Problem:** p\n- **Primary evidence:** e\n- **Resumption condition:** r\n"""
        malformed = "## OI-2: Missing\n- **Status:** open\n- **Problem:** p\n"
        result = preview(valid + malformed, SOURCE, "dest/repo")
        self.assertEqual(len(result.records), 1)
        self.assertEqual(result.records[0].state, "closed")
        self.assertEqual(result.diagnostics[0].oi_id, "OI-2")
        self.assertIn("missing required", result.diagnostics[0].reason)


class ReconciliationTests(unittest.TestCase):
    def _proposal(self):
        text = """## OI-1: One
- **Status:** open
- **Problem:** p
- **Primary evidence:** e
- **Resumption condition:** r
## OI-2: Two
- **Status:** closed
- **Problem:** p
- **Primary evidence:** e
- **Resumption condition:** r
"""
        return preview(text, SOURCE, "dest/repo")

    def test_complete_explicit_get_excludes_prs_and_finds_closed_second_page(self):
        proposal = self._proposal()
        one, two = proposal.records
        calls = []

        def fake_gh(argv, stdin):
            calls.append((argv, stdin))
            self.assertEqual(argv[argv.index("--method") + 1], "GET")
            self.assertNotIn("POST", argv)
            return json.dumps([[
                {"number": 1, "state": "open", "body": one.body},
                {"number": 2, "state": "open", "body": two.marker.replace("OI-2", "OI-20")},
                {"number": 3, "state": "open", "body": two.body, "pull_request": {"url": "x"}},
                {"number": 4, "state": "open", "body": None},
            ], [{"number": 9, "state": "closed", "body": two.body}]])

        result = reconcile(proposal, GhApiTransport(fake_gh), "github.com")
        self.assertEqual([item.outcome for item in result.records], ["no-op", "no-op"])
        argv, stdin = calls[0]
        self.assertEqual(stdin, None)
        self.assertEqual(argv, (
            "gh", "api", "--method", "GET", "--hostname", "github.com", "--paginate", "--slurp",
            "--header", "X-GitHub-Api-Version: 2022-11-28",
            "repos/dest/repo/issues?state=all&per_page=100",
        ))

    def test_failed_middle_page_is_incomplete_not_create_eligible_and_never_writes(self):
        proposal = self._proposal()
        calls = []

        def failed_second_page(argv, stdin):
            calls.append((argv, stdin))
            if "--method" not in argv or argv[argv.index("--method") + 1] != "GET":
                raise AssertionError("mutating gh method rejected")
            raise IncompleteLookup("page 2 rate limit")

        result = reconcile(proposal, GhApiTransport(failed_second_page), "github.com")
        self.assertEqual([item.outcome for item in result.records], ["incomplete lookup", "incomplete lookup"])
        self.assertIn("page 2 rate limit", result.lookup_error)
        self.assertEqual(len(calls), 1)
        self.assertIsNone(calls[0][1])

    def test_reruns_divergence_duplicates_and_reviewed_mapping_are_record_specific(self):
        proposal = self._proposal()
        one, two = proposal.records

        def snapshot(argv, stdin):
            return json.dumps([[
                {"number": 1, "state": "open", "body": one.body},
                {"number": 2, "state": "open", "body": "human issue #2, no import marker"},
                {"number": 3, "state": "closed", "body": two.body + "\nhuman edit"},
                {"number": 4, "state": "closed", "body": two.body},
            ]])

        result = reconcile(proposal, GhApiTransport(snapshot), "github.com", {one.identity: 2})
        self.assertEqual(result.records[0].outcome, "no-op")  # exact marker wins over title/mapping
        self.assertEqual(result.records[1].outcome, "conflict")  # changed body plus a second exact marker
        mapped = reconcile(preview("""## OI-4: Overlap
- **Status:** open
- **Problem:** p
- **Primary evidence:** e
- **Resumption condition:** r
""", SOURCE, "dest/repo"), GhApiTransport(snapshot), "github.com", {"github.com/elsonidoq/skills:docs/open_issues.md:OI-4": 2})
        self.assertEqual(mapped.records[0].outcome, "existing-issue mapping")
        self.assertEqual(mapped.records[0].issue.number, 2)

        changed = preview("""## OI-1: One
- **Status:** closed
- **Problem:** revised
- **Primary evidence:** e
- **Resumption condition:** r
""", Source("github.com", "elsonidoq/skills", "docs/open_issues.md", "new-revision"), "dest/repo")
        divergent = reconcile(changed, GhApiTransport(snapshot), "github.com")
        self.assertEqual(divergent.records[0].outcome, "conflict")
        self.assertIn("diverges", divergent.records[0].detail)

        def unknown_state(argv, stdin):
            return json.dumps([[{"number": 8, "state": "unknown", "body": one.body}]])

        unknown = reconcile(proposal, GhApiTransport(unknown_state), "github.com")
        self.assertEqual(unknown.records[0].outcome, "conflict")
        self.assertIn("close ownership", unknown.records[0].detail)


class ApplyTests(unittest.TestCase):
    def _proposal(self):
        return preview("""## OI-1: One
- **Status:** open
- **Problem:** p
- **Primary evidence:** e
- **Resumption condition:** r
## OI-2: Two
- **Status:** open
- **Problem:** p
- **Primary evidence:** e
- **Resumption condition:** r
## OI-3: Historical closed
- **Status:** closed
- **Problem:** p
- **Primary evidence:** e
- **Resumption condition:** r
""", SOURCE, "dest/repo")

    def _transport(self, issues, calls, lose_create=None, incomplete_list=False, unreadable=None):
        next_number = [10]

        def fake_gh(argv, stdin):
            calls.append((argv, stdin))
            method = argv[argv.index("--method") + 1]
            path = argv[-1]
            if method == "GET" and path.endswith("issues?state=all&per_page=100"):
                if incomplete_list:
                    raise IncompleteLookup("listing visibility uncertain")
                return json.dumps([issues])
            if method == "POST":
                payload = json.loads(stdin)
                issue = {"number": next_number[0], "state": "open", "body": payload["body"]}
                next_number[0] += 1
                issues.append(issue)
                if lose_create == payload["title"]:
                    raise IncompleteLookup("response interrupted after create")
                return json.dumps(issue)
            if method == "PATCH" and "/issues/" in path:
                number = int(path.rsplit("/", 1)[1])
                payload = json.loads(stdin)
                self.assertEqual(payload["state_reason"], None)
                issue = next(issue for issue in issues if issue["number"] == number)
                issue.update({"body": payload["body"], "state": payload["state"], "state_reason": payload["state_reason"]})
                return json.dumps(issue)
            if method == "GET" and "/issues/" in path:
                number = int(path.rsplit("/", 1)[1])
                if unreadable == number:
                    raise IncompleteLookup("readback visibility uncertain")
                return json.dumps(next(issue for issue in issues if issue["number"] == number))
            raise AssertionError(argv)

        return GhApiTransport(fake_gh)

    def test_apply_uses_reviewed_exact_preview_and_independent_readback(self):
        proposal = self._proposal()
        calls, issues = [], []
        transport = self._transport(issues, calls)
        reviewed = reconcile(proposal, transport, "github.com")
        calls.clear()
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("dest/repo", "write only these reviewed open records"))
        self.assertEqual([item.outcome for item in result.records], ["created", "created", "closed"])
        methods = [argv[argv.index("--method") + 1] for argv, _ in calls]
        self.assertEqual(methods, ["GET", "POST", "GET", "POST", "GET", "POST", "GET", "GET", "PATCH", "GET"])
        posts = [(argv, json.loads(stdin)) for argv, stdin in calls if "POST" in argv]
        self.assertEqual([payload for _, payload in posts], [{"title": r.title, "body": r.body} for r in proposal.records[:2]] + [{"title": proposal.records[2].title, "body": proposal.records[2].pending_close_body}])
        self.assertTrue(all(argv[-1] == "repos/dest/repo/issues" for argv, _ in posts))
        self.assertEqual(len(issues), 3)

        rerun = reconcile(proposal, transport, "github.com")
        calls.clear()
        second = apply(rerun, transport, "github.com", ApplyAuthorization("dest/repo", "reviewed rerun"))
        self.assertEqual([item.outcome for item in second.records], ["deferred", "deferred", "deferred"])
        self.assertNotIn("POST", [part for argv, _ in calls for part in argv])

    def test_actual_original_register_preserves_full_lifecycle_and_overlap_boundary(self):
        original = (ROOT / "docs/open_issues.md").read_text()
        proposal = preview(original, SOURCE, "dest/repo")
        self.assertEqual(proposal.counts, {"records": 19, "open": 16, "closed": 3, "unmappable": 0})
        by_id = {record.title.split(":", 1)[0]: record for record in proposal.records}
        # An existing historical #2 reference is never an implicit adoption.  A reviewer
        # mapping makes that one record non-createable and leaves the foreign body intact.
        issues = [{"number": 2, "state": "closed", "body": "human issue #2, no import marker"}]
        calls = []
        transport = self._transport(issues, calls, lose_create=by_id["OI-1"].title)
        mapped = reconcile(proposal, transport, "github.com", {by_id["OI-4"].identity: 2})
        self.assertEqual(next(item for item in mapped.records if item.record is by_id["OI-4"]).outcome,
                         "existing-issue mapping")
        self.assertEqual(issues[0], {"number": 2, "state": "closed", "body": "human issue #2, no import marker"})

        reviewed = reconcile(proposal, transport, "github.com")
        calls.clear()
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("dest/repo", "reviewed original register"))
        self.assertEqual([item.outcome for item in result.records].count("created"), 16)
        self.assertEqual([item.outcome for item in result.records].count("closed"), 3)
        self.assertEqual([json.loads(stdin)["title"] for argv, stdin in calls if "POST" in argv],
                         [record.title for record in proposal.records])
        self.assertEqual(sum("POST" in argv for argv, _ in calls), 19)
        self.assertEqual(issues[0], {"number": 2, "state": "closed", "body": "human issue #2, no import marker"})
        for record in proposal.records:
            remote = next(issue for issue in issues if issue.get("body") == record.body)
            self.assertEqual(remote["state"], record.state)
            self.assertIn(record.original_excerpt, remote["body"])

        # The lost OI-1 POST response was reconciled, not reposted; a later unchanged
        # review remains safe and emits no further mutation.
        rerun = reconcile(proposal, transport, "github.com")
        calls.clear()
        repeated = apply(rerun, transport, "github.com", ApplyAuthorization("dest/repo", "unchanged rerun"))
        self.assertTrue(all(item.outcome == "deferred" for item in repeated.records))
        self.assertFalse(any(method in argv for argv, _ in calls for method in ("POST", "PATCH")))

    def test_changed_review_or_remote_content_defers_without_overwrite(self):
        proposal = self._proposal()
        calls, issues = [], []
        transport = self._transport(issues, calls)
        reviewed = reconcile(proposal, transport, "github.com")
        issues.append({"number": 7, "state": "open", "body": proposal.records[0].body + "\nhuman update"})
        calls.clear()
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("dest/repo", "scoped write"))
        self.assertEqual(result.records[0].outcome, "deferred")
        self.assertIn("reinspection changed", result.records[0].detail)
        self.assertEqual(result.records[1].outcome, "created")
        self.assertNotIn("POST", [part for argv, _ in calls[:1] for part in argv])
        with self.assertRaisesRegex(ValueError, "matching destination"):
            apply(reviewed, transport, "github.com", ApplyAuthorization("other/repo", "wrong target"))

        # A revised source/preview retains its identity marker but changes the exact body;
        # it must reconcile as a conflict rather than overwrite the older import.
        changed_source = Source(SOURCE.host, SOURCE.repository, SOURCE.path, "new-revision")
        changed_preview = preview("""## OI-1: One
- **Status:** open
- **Problem:** revised source
- **Primary evidence:** e
- **Resumption condition:** r
""", changed_source, "dest/repo")
        changed_reviewed = reconcile(changed_preview, transport, "github.com")
        self.assertEqual(changed_reviewed.records[0].outcome, "conflict")
        calls.clear()
        changed_result = apply(changed_reviewed, transport, "github.com", ApplyAuthorization("dest/repo", "changed preview review"))
        self.assertEqual(changed_result.records[0].outcome, "deferred")
        self.assertNotIn("POST", [part for argv, _ in calls for part in argv])

    def test_partial_failure_and_lost_create_are_reconciled_without_second_post(self):
        proposal = self._proposal()
        calls, issues = [], []
        transport = self._transport(issues, calls, lose_create="OI-2: Two")
        reviewed = reconcile(proposal, transport, "github.com")
        calls.clear()
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("dest/repo", "scoped write"))
        self.assertEqual([item.outcome for item in result.records], ["created", "created", "closed"])
        post_titles = [json.loads(stdin)["title"] for argv, stdin in calls if "POST" in argv]
        self.assertEqual(post_titles, ["OI-1: One", "OI-2: Two", "OI-3: Historical closed"])
        self.assertEqual(len([call for call in calls if "POST" in call[0]]), 3)
        # The second POST succeeded remotely but its response was lost. Recovery lists
        # open+closed pages and independently GETs the single marker candidate.
        self.assertEqual([argv[argv.index("--method") + 1] for argv, _ in calls], ["GET", "POST", "GET", "POST", "GET", "GET", "POST", "GET", "GET", "PATCH", "GET"])

    def test_uncertain_listing_or_readback_never_retries_a_post(self):
        proposal = self._proposal()
        calls, issues = [], []
        transport = self._transport(issues, calls, incomplete_list=True)
        reviewed = reconcile(proposal, transport, "github.com")
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("dest/repo", "scoped write"))
        self.assertTrue(all(item.outcome == "deferred" for item in result.records))
        self.assertNotIn("POST", [part for argv, _ in calls for part in argv])

        calls, issues = [], []
        transport = self._transport(issues, calls, unreadable=10)
        reviewed = reconcile(proposal, transport, "github.com")
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("dest/repo", "scoped write"))
        self.assertEqual(result.records[0].outcome, "deferred")
        self.assertEqual(len([call for call in calls if "POST" in call[0]]), 3)
        self.assertIn("response was lost", result.records[0].detail)


class ClosedResumeTests(unittest.TestCase):
    def _proposal(self):
        return preview("""## OI-9: Historical closed
- **Status:** closed
- **Problem:** p
- **Primary evidence:** e
- **Resumption condition:** r
""", SOURCE, "dest/repo")

    def test_known_pending_close_resumes_once_but_human_reopen_or_unknown_ownership_defers(self):
        proposal = self._proposal()
        record = proposal.records[0]
        issues = [{"number": 9, "state": "open", "body": record.pending_close_body}]
        calls = []

        def gh(argv, stdin):
            calls.append((argv, stdin))
            method, path = argv[argv.index("--method") + 1], argv[-1]
            if method == "GET" and path.endswith("issues?state=all&per_page=100"):
                return json.dumps([issues])
            if method == "GET":
                return json.dumps(issues[0])
            if method == "PATCH":
                payload = json.loads(stdin)
                self.assertEqual(payload, {"body": record.body, "state": "closed", "state_reason": None})
                issues[0].update({"body": record.body, "state": "closed", "state_reason": None})
                return json.dumps(issues[0])
            raise AssertionError(argv)

        transport = GhApiTransport(gh)
        reviewed = reconcile(proposal, transport, "github.com")
        self.assertEqual(reviewed.records[0].outcome, "pending close")
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("dest/repo", "resume one known pending close"))
        self.assertEqual(result.records[0].outcome, "closed")
        self.assertEqual(issues[0]["state_reason"], None)
        self.assertNotIn("POST", [part for argv, _ in calls for part in argv])

        # A final import body reopened by a human (or a body with no recognized pending
        # provenance) is never reset by stale historical source state.
        issues[0].update({"body": record.body, "state": "open"})
        reopened = reconcile(proposal, transport, "github.com")
        self.assertEqual(reopened.records[0].outcome, "conflict")
        self.assertIn("diverges", reopened.records[0].detail)
        issues[0].update({"body": record.pending_close_body + "\nhuman edit", "state": "open"})
        unknown = reconcile(proposal, transport, "github.com")
        self.assertEqual(unknown.records[0].outcome, "conflict")

    def test_lost_create_and_close_response_or_readback_never_create_twice(self):
        proposal = self._proposal()
        record = proposal.records[0]
        issues, calls = [], []
        phase = {"close_lost": True, "readback_fails": False}

        def gh(argv, stdin):
            calls.append((argv, stdin))
            method, path = argv[argv.index("--method") + 1], argv[-1]
            if method == "GET" and path.endswith("issues?state=all&per_page=100"):
                return json.dumps([issues])
            if method == "POST":
                issues.append({"number": 10, "state": "open", "body": record.pending_close_body})
                raise IncompleteLookup("create response lost after create")
            if method == "PATCH":
                issues[0].update({"body": record.body, "state": "closed", "state_reason": None})
                if phase["close_lost"]:
                    raise IncompleteLookup("close response lost after close")
                return json.dumps(issues[0])
            if method == "GET":
                if phase["readback_fails"]:
                    raise IncompleteLookup("final readback unavailable")
                return json.dumps(issues[0])
            raise AssertionError(argv)

        transport = GhApiTransport(gh)
        reviewed = reconcile(proposal, transport, "github.com")
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("dest/repo", "one closed proof fixture"))
        self.assertEqual(result.records[0].outcome, "closed")
        self.assertEqual(len([1 for argv, _ in calls if "POST" in argv]), 1)
        self.assertEqual(issues[0]["state"], "closed")

        # An unavailable final readback is deferred, not converted into a second create.
        issues[:] = [{"number": 11, "state": "open", "body": record.pending_close_body}]
        phase.update(close_lost=False, readback_fails=True)
        calls.clear()
        pending = reconcile(proposal, transport, "github.com")
        deferred = apply(pending, transport, "github.com", ApplyAuthorization("dest/repo", "one pending close fixture"))
        self.assertEqual(deferred.records[0].outcome, "deferred")
        self.assertNotIn("POST", [part for argv, _ in calls for part in argv])


if __name__ == "__main__":
    unittest.main()
