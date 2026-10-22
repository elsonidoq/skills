import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from import_open_issues import ApplyAuthorization, GhApiTransport, IncompleteLookup, Source, VerifiedIssueObservation, apply, preview, reconcile

ROOT = Path(__file__).resolve().parents[3]
BASELINE_SHA256 = "314b9ddd758d25923105d85c23225293d0a1398b506d1b28925d783a5c3e1c7a"
SOURCE = Source("github.com", "elsonidoq/skills", "docs/open_issues.md", "952e39b813a443caeb7417e63c170e219a433dbd")


def retained_observations(issues):
    """Fixture equivalents of independently read-back results in the prior return."""
    return tuple(VerifiedIssueObservation("github.com", "dest/repo", "2022-11-28",
                                         GhApiTransport._issue(issue, "fixture prior GET")) for issue in issues)


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

    def test_closed_disclaimer_is_exact_visible_and_outside_original_excerpt(self):
        disclaimer = ("Historical import: the source marked this record closed; its original closure reason is unknown. "
                      "GitHub's native closure reason is platform metadata, not evidence of a verified fix. "
                      "This import does not establish that the original problem was resolved.")
        original = (ROOT / "docs/open_issues.md").read_text()
        for record in preview(original, SOURCE, "dest/repo").records:
            before, excerpt = record.body.split("## Original Markdown excerpt\n", 1)
            if record.state == "closed":
                self.assertEqual(before.count(disclaimer), 1)
                self.assertIn(disclaimer, record.pending_close_body)
            else:
                self.assertNotIn(disclaimer, before)
            self.assertNotIn(disclaimer, excerpt)
            self.assertEqual(excerpt, "```markdown\n" + record.original_excerpt + "\n```")

    def test_multiline_fields_keep_exact_line_boundaries_in_transformed_sections(self):
        value = "first\nsecond\n\n  - nested item\n  - another\n\n```text\ncode line\n```"
        text = ("## OI-1: Multiline\n- **Status:** open\n- **Problem:** " + value
                + "\n- **Primary evidence:** evidence\ncontinuation\n- **Resumption condition:** resume\n")
        result = preview(text, SOURCE, "dest/repo")
        self.assertEqual(result.diagnostics, ())
        record = result.records[0]
        self.assertEqual(dict(record.fields)["Problem"], value)
        self.assertEqual(dict(record.fields)["Primary evidence"], "evidence\ncontinuation")
        transformed = record.body.split("## Original Markdown excerpt", 1)[0]
        self.assertIn("## Problem\n" + value + "\n\n## Primary evidence\nevidence\ncontinuation\n", transformed)
        self.assertEqual(record.original_excerpt, text.rstrip("\n"))

    def test_existing_links_source_anchors_and_code_are_not_rewritten_as_oi_mentions(self):
        value = ('[OI-9](relative.md#part) [OI-8](#source-anchor) '
                 '[OI-7](https://example.org/OI-7) OI-6 '
                 '`[OI-5](relative.md) OI-4` ``[OI-3](#part) `OI-2` ``')
        text = ("## OI-1: Links\n- **Status:** open\n- **Problem:** " + value
                + "\n- **Primary evidence:** e\n- **Resumption condition:** r\n")
        record = preview(text, SOURCE, "dest/repo").records[0]
        transformed = record.body.split("## Original Markdown excerpt", 1)[0]
        base = SOURCE.blob_url.rsplit("/", 1)[0]
        expected = (f'[OI-9]({base}/relative.md#part) [OI-8]({SOURCE.blob_url}#source-anchor) '
                    f'[OI-7](https://example.org/OI-7) [OI-6]({SOURCE.blob_url}) '
                    '`[OI-5](relative.md) OI-4` ``[OI-3](#part) `OI-2` ``')
        self.assertIn("## Problem\n" + expected + "\n", transformed)
        self.assertNotIn("[[OI-", transformed)
        self.assertIn(value, record.original_excerpt)

    def test_nested_labels_are_actionable_public_preview_diagnostics(self):
        for value in ("[see [OI-9]](relative.md)", "[see [deep [OI-9]]](relative.md#part)"):
            with self.subTest(value=value):
                text = ("## OI-1: Nested\n- **Status:** open\n- **Problem:** " + value
                        + "\n- **Primary evidence:** e\n- **Resumption condition:** r\n")
                result = preview(text, SOURCE, "dest/repo")
                self.assertEqual(result.records, ())
                self.assertEqual(len(result.diagnostics), 1)
                diagnostic = result.diagnostics[0]
                self.assertEqual((diagnostic.oi_id, diagnostic.line), ("OI-1", 1))
                self.assertIn("unsupported nested link label", diagnostic.reason)
                self.assertIn("flatten the label", diagnostic.reason)
                self.assertIn("preview again", diagnostic.reason)
        # Markdown-looking code remains literal; normal adjacent links are not nested.
        text = ("## OI-1: Literal\n- **Status:** open\n- **Problem:** "
                "`[see [OI-9]](relative.md)` [one](one.md) [two](two.md)\n"
                "- **Primary evidence:** e\n- **Resumption condition:** r\n")
        result = preview(text, SOURCE, "dest/repo")
        self.assertEqual(result.diagnostics, ())
        self.assertIn("`[see [OI-9]](relative.md)`", result.records[0].body)

    def test_parenthesized_link_target_is_an_actionable_public_preview_diagnostic(self):
        value = "[design](../docs/design(v2).md#part)"
        text = ("## OI-1: Design\n- **Status:** open\n- **Problem:** " + value
                + "\n- **Primary evidence:** e\n- **Resumption condition:** r\n")
        result = preview(text, SOURCE, "dest/repo")
        self.assertEqual(result.records, ())
        self.assertEqual(len(result.diagnostics), 1)
        diagnostic = result.diagnostics[0]
        self.assertEqual((diagnostic.oi_id, diagnostic.line), ("OI-1", 1))
        self.assertIn("unsupported parentheses in link target", diagnostic.reason)
        self.assertIn("percent-encode", diagnostic.reason)
        self.assertIn("preview again", diagnostic.reason)
        pinned = SOURCE.blob_url.rsplit("/", 1)[0] + "/design%28v2%29.md#part"
        encoded = preview(text.replace("../docs/design(v2).md#part", pinned), SOURCE, "dest/repo")
        self.assertEqual(encoded.diagnostics, ())
        self.assertIn("[design](" + pinned + ")", encoded.records[0].body)
        literal = preview(text.replace(value, "`" + value + "`"), SOURCE, "dest/repo")
        self.assertEqual(literal.diagnostics, ())
        self.assertIn("`" + value + "`", literal.records[0].body)

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
        self.assertEqual(result.records, ())
        reasons = "\n".join(d.reason for d in result.diagnostics)
        self.assertIn("unmappable status", reasons)
        self.assertIn("duplicate OI identity", reasons)
        self.assertIn("unsafe Markdown", reasons)
        self.assertIn("sensitive candidate data rejected", reasons)
        self.assertNotIn("DO_NOT_EXPORT", reasons)
        self.assertNotIn("DO_NOT_EXPORT", "\n".join(r.body for r in result.records))
        status_secret = preview(valid.replace("Status:** open", "Status:** token=DO_NOT_EXPORT"), SOURCE, "dest/repo")
        self.assertEqual(status_secret.records, ())
        self.assertEqual(status_secret.diagnostics[0].reason, "sensitive candidate data rejected; fidelity is unavailable")
        self.assertEqual(result.counts["unmappable"], 5)
        self.assertEqual([d.line for d in result.diagnostics if d.oi_id == "OI-1"], [1, 11])

    def test_all_duplicate_occurrences_are_excluded_before_reconciliation_and_apply(self):
        first = "## OI-1: First\n- **Status:** open\n- **Problem:** p\n- **Primary evidence:** e\n- **Resumption condition:** r\n"
        second = first.replace("First", "Second").replace("Status:** open", "Status:** closed")
        third = first.replace("First", "Third")
        unique = first.replace("OI-1: First", "OI-2: Unique")
        proposal = preview(first + unique + second + third, SOURCE, "dest/repo")
        self.assertEqual([record.title for record in proposal.records], ["OI-2: Unique"])
        self.assertEqual([(d.oi_id, d.line) for d in proposal.diagnostics], [("OI-1", 1), ("OI-1", 11), ("OI-1", 16)])
        calls, issues = [], []
        transport = ApplyTests()._transport(issues, calls)
        reviewed = reconcile(proposal, transport, "github.com")
        self.assertEqual([item.record.title for item in reviewed.records], ["OI-2: Unique"])
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "offline fixture"))
        self.assertEqual([item.record.title for item in result.records], ["OI-2: Unique"])
        self.assertEqual([issue["title"] for issue in issues], ["OI-2: Unique"])
        self.assertTrue(all("OI-1" not in (stdin or "") for _, stdin in calls))

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
                {"number": 1, "title": one.title, "state": "open", "body": one.body},
                {"number": 2, "title": two.title, "state": "open", "body": two.marker.replace("OI-2", "OI-20")},
                {"number": 3, "title": two.title, "state": "open", "body": two.body, "pull_request": {"url": "x"}},
                {"number": 4, "title": "unrelated", "state": "open", "body": None},
            ], [{"number": 9, "title": two.title, "state": "closed", "body": two.body, "state_reason": "completed"}]])

        prior = retained_observations((
            {"number": 1, "title": one.title, "state": "open", "body": one.body},
            {"number": 9, "title": two.title, "state": "closed", "body": two.body, "state_reason": "completed"},
        ))
        result = reconcile(proposal, GhApiTransport(fake_gh), "github.com", verified_observations=prior)
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
                {"number": 1, "title": one.title, "state": "open", "body": one.body},
                {"number": 2, "title": "human issue #2", "state": "open", "body": "human issue #2, no import marker"},
                {"number": 3, "title": two.title, "state": "closed", "body": two.body + "\nhuman edit"},
                {"number": 4, "title": two.title, "state": "closed", "body": two.body},
            ]])

        prior = retained_observations(json.loads(snapshot((), None))[0])
        result = reconcile(proposal, GhApiTransport(snapshot), "github.com", {one.identity: 2}, verified_observations=prior)
        self.assertEqual(result.records[0].outcome, "no-op")  # exact marker wins over title/mapping
        self.assertEqual(result.records[1].outcome, "conflict")
        title_changed = json.loads(snapshot((), None))
        title_changed[0][0]["title"] = "human title edit"
        title_conflict = reconcile(proposal, GhApiTransport(lambda _argv, _stdin: json.dumps(title_changed)), "github.com")
        self.assertEqual(title_conflict.records[0].outcome, "conflict")
        self.assertIn("title diverges", title_conflict.records[0].detail)  # changed body plus a second exact marker
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
            return json.dumps([[{"number": 8, "title": one.title, "state": "unknown", "body": one.body}]])

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
                issue = {"number": next_number[0], "title": payload["title"], "state": "open", "body": payload["body"]}
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
                issue.update({"body": payload["body"], "state": payload["state"], "state_reason": "completed"})
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
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "write only these reviewed open records"))
        self.assertEqual([item.outcome for item in result.records], ["created", "created", "closed"])
        methods = [argv[argv.index("--method") + 1] for argv, _ in calls]
        self.assertEqual(methods, ["GET", "POST", "GET", "POST", "GET", "POST", "GET", "GET", "PATCH", "GET"])
        posts = [(argv, json.loads(stdin)) for argv, stdin in calls if "POST" in argv]
        self.assertEqual([payload for _, payload in posts], [{"title": r.title, "body": r.body} for r in proposal.records[:2]] + [{"title": proposal.records[2].title, "body": proposal.records[2].pending_close_body}])
        self.assertTrue(all(argv[-1] == "repos/dest/repo/issues" for argv, _ in posts))
        self.assertEqual(len(issues), 3)

        rerun = reconcile(proposal, transport, "github.com", verified_observations=retained_observations(issues))
        self.assertTrue(all(item.outcome == "no-op" for item in rerun.records))
        calls.clear()
        second = apply(rerun, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "reviewed rerun"))
        self.assertEqual([item.outcome for item in second.records], ["deferred", "deferred", "deferred"])
        self.assertNotIn("POST", [part for argv, _ in calls for part in argv])

    def test_actual_original_register_preserves_full_lifecycle_and_overlap_boundary(self):
        original = (ROOT / "docs/open_issues.md").read_text()
        proposal = preview(original, SOURCE, "dest/repo")
        self.assertEqual(proposal.counts, {"records": 19, "open": 16, "closed": 3, "unmappable": 0})
        by_id = {record.title.split(":", 1)[0]: record for record in proposal.records}
        # An existing historical #2 reference is never an implicit adoption.  A reviewer
        # mapping makes that one record non-createable and leaves the foreign body intact.
        issues = [{"number": 2, "title": "human issue #2", "state": "closed", "body": "human issue #2, no import marker"}]
        calls = []
        transport = self._transport(issues, calls, lose_create=by_id["OI-1"].title)
        mapped = reconcile(proposal, transport, "github.com", {by_id["OI-4"].identity: 2})
        self.assertEqual(next(item for item in mapped.records if item.record is by_id["OI-4"]).outcome,
                         "existing-issue mapping")
        self.assertEqual(issues[0], {"number": 2, "title": "human issue #2", "state": "closed", "body": "human issue #2, no import marker"})

        reviewed = reconcile(proposal, transport, "github.com")
        calls.clear()
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "reviewed original register"))
        self.assertEqual([item.outcome for item in result.records].count("created"), 16)
        self.assertEqual([item.outcome for item in result.records].count("closed"), 3)
        self.assertEqual([json.loads(stdin)["title"] for argv, stdin in calls if "POST" in argv],
                         [record.title for record in proposal.records])
        self.assertEqual(sum("POST" in argv for argv, _ in calls), 19)
        self.assertEqual(issues[0], {"number": 2, "title": "human issue #2", "state": "closed", "body": "human issue #2, no import marker"})
        for record in proposal.records:
            remote = next(issue for issue in issues if issue.get("body") == record.body)
            self.assertEqual(remote["state"], record.state)
            self.assertIn(record.original_excerpt, remote["body"])

        # The lost OI-1 POST response was reconciled, not reposted; a later unchanged
        # review carries independently read-back observations from the previous return.
        rerun = reconcile(proposal, transport, "github.com", verified_observations=retained_observations(issues))
        self.assertTrue(all(item.outcome == "no-op" for item in rerun.records))
        calls.clear()
        repeated = apply(rerun, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "unchanged rerun"))
        self.assertTrue(all(item.outcome == "deferred" for item in repeated.records))
        self.assertFalse(any(method in argv for argv, _ in calls for method in ("POST", "PATCH")))

    def test_changed_review_or_remote_content_defers_without_overwrite(self):
        proposal = self._proposal()
        calls, issues = [], []
        transport = self._transport(issues, calls)
        reviewed = reconcile(proposal, transport, "github.com")
        issues.append({"number": 7, "title": proposal.records[0].title, "state": "open", "body": proposal.records[0].body + "\nhuman update"})
        calls.clear()
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "scoped write"))
        self.assertEqual(result.records[0].outcome, "deferred")
        self.assertIn("reinspection changed", result.records[0].detail)
        self.assertEqual(result.records[1].outcome, "created")
        self.assertNotIn("POST", [part for argv, _ in calls[:1] for part in argv])
        with self.assertRaisesRegex(ValueError, "matching host, destination"):
            apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "other/repo", "wrong target"))
        with self.assertRaisesRegex(ValueError, "matching host, destination"):
            apply(reviewed, transport, "github.com", ApplyAuthorization("github.example", "dest/repo", "wrong host"))
        with self.assertRaisesRegex(ValueError, "matching host, destination"):
            apply(reviewed, transport, "github.example", ApplyAuthorization("github.example", "dest/repo", "unreviewed host"))

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
        changed_result = apply(changed_reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "changed preview review"))
        self.assertEqual(changed_result.records[0].outcome, "deferred")
        self.assertNotIn("POST", [part for argv, _ in calls for part in argv])

    def test_uncertain_create_identity_blocks_a_later_planned_create(self):
        proposal = preview("""## OI-1: One
- **Status:** open
- **Problem:** p
- **Primary evidence:** e
- **Resumption condition:** r
""", SOURCE, "dest/repo")
        record = proposal.records[0]
        calls = []

        def gh(argv, stdin):
            calls.append((argv, stdin))
            method = argv[argv.index("--method") + 1]
            if method == "GET":
                return json.dumps([[]])
            if method == "POST":
                raise IncompleteLookup("response interrupted after possible create")
            raise AssertionError(argv)

        transport = GhApiTransport(gh)
        reviewed = reconcile(proposal, transport, "github.com")
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "scoped write"))
        self.assertEqual(result.records[0].outcome, "deferred")
        self.assertEqual(len([1 for argv, _ in calls if "POST" in argv]), 1)

        # A later reconciliation must carry the returned uncertain identity; even when
        # listing has recovered and finds no marker, it cannot send a second POST.
        blocked = reconcile(proposal, transport, "github.com", uncertain_identities={record.identity})
        self.assertEqual(blocked.records[0].outcome, "deferred")
        calls.clear()
        blocked_apply = apply(blocked, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "scoped retry"))
        self.assertEqual(blocked_apply.records[0].outcome, "deferred")
        self.assertNotIn("POST", [part for argv, _ in calls for part in argv])

    def test_partial_failure_and_lost_create_are_reconciled_without_second_post(self):
        proposal = self._proposal()
        calls, issues = [], []
        transport = self._transport(issues, calls, lose_create="OI-2: Two")
        reviewed = reconcile(proposal, transport, "github.com")
        calls.clear()
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "scoped write"))
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
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "scoped write"))
        self.assertTrue(all(item.outcome == "deferred" for item in result.records))
        self.assertNotIn("POST", [part for argv, _ in calls for part in argv])

        calls, issues = [], []
        transport = self._transport(issues, calls, unreadable=10)
        reviewed = reconcile(proposal, transport, "github.com")
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "scoped write"))
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

    def test_invisible_closed_create_carries_uncertainty_then_resumes_same_identity(self):
        proposal = self._proposal()
        record = proposal.records[0]
        issues, calls = [], []
        visible = False
        base = ApplyTests()._transport(issues, calls, lose_create=record.title)
        def gh(argv, stdin):
            if "--paginate" in argv and not visible:
                calls.append((argv, stdin))
                return json.dumps([[]])
            return base._execute(argv, stdin)
        transport = GhApiTransport(gh)
        reviewed = reconcile(proposal, transport, "github.com")
        first = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "fixture"))
        self.assertEqual(first.records[0].outcome, "deferred")
        self.assertEqual(len(issues), 1)
        uncertain = {first.records[0].record.identity}
        missing = reconcile(proposal, transport, "github.com", uncertain_identities=uncertain)
        self.assertEqual(missing.records[0].outcome, "deferred")
        blocked = apply(missing, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "fixture"))
        self.assertEqual(blocked.records[0].outcome, "deferred")
        visible = True
        later = reconcile(proposal, transport, "github.com", uncertain_identities=uncertain)
        self.assertEqual(later.records[0].outcome, "pending close")
        recovered = apply(later, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "fixture"))
        self.assertEqual(recovered.records[0].outcome, "closed")
        self.assertEqual(recovered.records[0].issue.number, issues[0]["number"])
        self.assertEqual(issues[0]["body"], record.body)
        self.assertEqual(issues[0]["state_reason"], "completed")
        self.assertEqual(sum("POST" in argv for argv, _ in calls), 1)
        self.assertEqual(sum("PATCH" in argv for argv, _ in calls), 1)
        retained = retained_observations(issues)
        rerun = reconcile(proposal, transport, "github.com", verified_observations=retained)
        self.assertEqual(rerun.records[0].outcome, "no-op")

    def test_unmapped_host_or_api_defers_closed_writes(self):
        proposal = self._proposal()
        for host, version in (("other.example", "2022-11-28"), ("github.com", "different-api")):
            calls = []
            def gh(argv, stdin):
                calls.append(argv)
                self.assertIn("GET", argv)
                return json.dumps([[]])
            transport = GhApiTransport(gh)
            transport.api_version = version
            reviewed = reconcile(proposal, transport, host)
            result = apply(reviewed, transport, host, ApplyAuthorization(host, "dest/repo", "fixture"))
            self.assertEqual(result.records[0].outcome, "deferred")
            self.assertIn("mapping", result.records[0].detail)
            self.assertTrue(all("GET" in argv for argv in calls))

    def test_reason_conflicts_remain_conflicts_on_rerun_without_writes(self):
        proposal = self._proposal()
        record = proposal.records[0]
        for body, state, reason, expected in (
            (record.body, "closed", None, "conflict"),
            (record.body, "closed", "completed", "conflict"),
            (record.body, "closed", "not_planned", "conflict"),
            (record.pending_close_body, "open", None, "pending close"),
            (record.pending_close_body, "open", "reopened", "conflict"),
            (record.pending_close_body, "closed", "completed", "conflict"),
            (record.body, "open", "reopened", "conflict"),
        ):
            with self.subTest(state=state, reason=reason, pending=body != record.body):
                calls = []
                issue = {"number": 3, "title": record.title, "body": body, "state": state, "state_reason": reason}
                def gh(argv, stdin):
                    calls.append(argv)
                    self.assertIn("GET", argv)
                    return json.dumps([[issue]])
                transport = GhApiTransport(gh)
                reviewed = reconcile(proposal, transport, "github.com")
                self.assertEqual(reviewed.records[0].outcome, expected)
                if expected == "conflict":
                    result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "offline fixture"))
                    self.assertEqual(result.records[0].outcome, "deferred")
                    self.assertTrue(all("GET" in argv for argv in calls))

    def test_native_completed_close_and_verified_reason_equivalence(self):
        from import_open_issues import HISTORICAL_CLOSURE_DISCLAIMER
        proposal = self._proposal()
        record = proposal.records[0]
        issues, calls = [], []
        transport = ApplyTests()._transport(issues, calls)
        reviewed = reconcile(proposal, transport, "github.com")
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "fixture"))
        self.assertEqual(result.records[0].outcome, "closed")
        final = result.records[0].issue
        self.assertEqual(final.state_reason, "completed")
        evidence = VerifiedIssueObservation("github.com", "dest/repo", transport.api_version, final)
        rerun = reconcile(proposal, transport, "github.com", verified_observations=(evidence,))
        self.assertEqual(rerun.records[0].outcome, "no-op")
        missing = reconcile(proposal, transport, "github.com")
        self.assertEqual(missing.records[0].outcome, "conflict")
        self.assertIn("prior independently verified", missing.records[0].detail)
        # Even an otherwise admissible reason cannot replace a verified reason silently.
        issues[0]["state_reason"] = None
        drift = reconcile(proposal, transport, "github.com", verified_observations=(evidence,))
        self.assertEqual(drift.records[0].outcome, "conflict")
        self.assertIn("reason", drift.records[0].detail)
        # Matching independent null evidence is admitted only for that observed target/API.
        null_issue = transport.get_issue("github.com", "dest/repo", final.number)
        null_evidence = VerifiedIssueObservation("github.com", "dest/repo", transport.api_version, null_issue)
        exact_null = reconcile(proposal, transport, "github.com", verified_observations=(null_evidence,))
        self.assertEqual(exact_null.records[0].outcome, "no-op")
        issues[0]["state_reason"] = "completed"
        back_drift = reconcile(proposal, transport, "github.com", verified_observations=(null_evidence,))
        self.assertEqual(back_drift.records[0].outcome, "conflict")
        for reason in ("not_planned", "duplicate", "reopened", "unknown"):
            issues[0]["state_reason"] = reason
            observed = transport.get_issue("github.com", "dest/repo", final.number)
            unsupported = reconcile(proposal, transport, "github.com", verified_observations=(
                VerifiedIssueObservation("github.com", "dest/repo", transport.api_version, observed),))
            self.assertEqual(unsupported.records[0].outcome, "conflict")
            self.assertIn(reason, unsupported.records[0].detail)
        issues[0]["state_reason"] = "completed"
        for host, version, destination in (("other.example", transport.api_version, "dest/repo"),
                                           ("github.com", "different-api", "dest/repo"),
                                           ("github.com", transport.api_version, "other/repo")):
            wrong = VerifiedIssueObservation(host, destination, version, final)
            mismatch = reconcile(proposal, transport, host, verified_observations=(wrong,))
            self.assertEqual(mismatch.records[0].outcome, "conflict")
        calls.clear()
        for edit in ({"title": "human title"}, {"body": record.body + "\nhuman section"},
                     {"body": record.body.replace(HISTORICAL_CLOSURE_DISCLAIMER + "\n", "")},
                     {"body": record.body.replace("Historical import:", "Edited history:")},
                     {"state": "open", "state_reason": "reopened"}):
            issues[0] = {"number": final.number, "title": record.title, "body": record.body,
                         "state": "closed", "state_reason": "completed", **edit}
            changed = reconcile(proposal, transport, "github.com", verified_observations=(evidence,))
            self.assertEqual(changed.records[0].outcome, "conflict")
            report = apply(changed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "fixture"))
            self.assertEqual(report.records[0].outcome, "deferred")
        self.assertFalse(any("PATCH" in argv or "POST" in argv for argv, _ in calls))

    def test_null_close_readback_requires_applicable_prior_target_evidence(self):
        proposal = self._proposal()
        record = proposal.records[0]
        for evidence_present in (False, True):
            issues, calls = [], []
            base = ApplyTests()._transport(issues, calls)
            def gh(argv, stdin):
                response = base._execute(argv, stdin)
                if "PATCH" in argv:
                    issues[0]["state_reason"] = None
                    response = json.dumps(issues[0])
                return response
            transport = GhApiTransport(gh)
            evidence = retained_observations((
                {"number": 99, "title": "previous independent null observation", "body": "retained content",
                 "state": "closed", "state_reason": None},)) if evidence_present else ()
            reviewed = reconcile(proposal, transport, "github.com", verified_observations=evidence)
            report = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "fixture"))
            self.assertEqual(report.records[0].outcome, "closed" if evidence_present else "deferred")
            self.assertEqual(issues[0]["body"], record.body)
            self.assertEqual(sum("PATCH" in argv for argv, _ in calls), 1)

    def test_pending_readback_reason_drift_does_not_close_human_reopen(self):
        proposal = self._proposal()
        record = proposal.records[0]
        issue = {"number": 3, "title": record.title, "body": record.pending_close_body, "state": "open", "state_reason": None}
        def gh(argv, stdin):
            self.assertIn("GET", argv)  # Any PATCH/POST fails this fixture.
            if "--paginate" in argv:
                return json.dumps([[issue]])
            return json.dumps({**issue, "state_reason": "reopened"})
        transport = GhApiTransport(gh)
        reviewed = reconcile(proposal, transport, "github.com")
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "offline fixture"))
        self.assertEqual(result.records[0].outcome, "deferred")
        self.assertIn("state reason diverges", result.records[0].detail)

    def test_known_pending_close_resumes_once_but_human_reopen_or_unknown_ownership_defers(self):
        proposal = self._proposal()
        record = proposal.records[0]
        issues = [{"number": 9, "title": record.title, "state": "open", "body": record.pending_close_body}]
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
                issues[0].update({"body": record.body, "state": "closed", "state_reason": "completed"})
                return json.dumps(issues[0])
            raise AssertionError(argv)

        transport = GhApiTransport(gh)
        reviewed = reconcile(proposal, transport, "github.com")
        self.assertEqual(reviewed.records[0].outcome, "pending close")
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "resume one known pending close"))
        self.assertEqual(result.records[0].outcome, "closed")
        self.assertEqual(issues[0]["state_reason"], "completed")
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
                issues.append({"number": 10, "title": record.title, "state": "open", "body": record.pending_close_body})
                raise IncompleteLookup("create response lost after create")
            if method == "PATCH":
                issues[0].update({"body": record.body, "state": "closed", "state_reason": "completed"})
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
        result = apply(reviewed, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "one closed proof fixture"))
        self.assertEqual(result.records[0].outcome, "closed")
        self.assertEqual(len([1 for argv, _ in calls if "POST" in argv]), 1)
        self.assertEqual(issues[0]["state"], "closed")

        # An unavailable final readback is deferred, not converted into a second create.
        issues[:] = [{"number": 11, "title": record.title, "state": "open", "body": record.pending_close_body}]
        phase.update(close_lost=False, readback_fails=True)
        calls.clear()
        pending = reconcile(proposal, transport, "github.com")
        deferred = apply(pending, transport, "github.com", ApplyAuthorization("github.com", "dest/repo", "one pending close fixture"))
        self.assertEqual(deferred.records[0].outcome, "deferred")
        self.assertNotIn("POST", [part for argv, _ in calls for part in argv])


if __name__ == "__main__":
    unittest.main()
