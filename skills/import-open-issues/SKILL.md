---
name: import-open-issues
description: Use when previewing or applying a faithful historical open-issues Markdown import to an explicitly authorized GitHub repository.
---

# Import Open Issues

Use this skill to preserve a historical register as proposed GitHub issues. It is not a
routine issue tracker: if the sibling `track-open-issue` skill is available, use it for
ordinary issue lifecycle work; otherwise stop routine tracking and report that capability
gap. Preparing a preview never authorizes an apply, a remote lookup, or any GitHub write.

## Offline preview

Supply all of these explicit inputs: source host, `OWNER/REPO`, normalized
repository-relative source path, pinned immutable revision, original Markdown bytes, and
destination `OWNER/REPO`. Call the production helper's `preview(markdown, Source(...),
destination)`. It exposes these interfaces for later reconciliation/apply stages:

- `parse_markdown` returns ordered `ParsedRecord` objects and source-location diagnostics.
- `render_record` turns one safe, mappable record into a `RenderedRecord` proposal.
- `preview` returns `Preview(records, diagnostics)` and state counts without a subprocess,
  network request, upload, shell interpolation, or external write.

A rendered proposal carries the proposed title, native `open`/`closed` state, transformed
navigable body, verbatim original Markdown excerpt, pinned revision, immutable original-entry
link, and a deterministic body marker:

```text
<!-- import-open-issues: SOURCE_HOST/OWNER/REPO:normalized/path.md:OI-N -->
```

That identity intentionally excludes title and revision, so title/revision changes can be
reconciled later, but includes source host/repository/path to prevent cross-repository OI-N
collisions. Every occurrence of a duplicate OI ID in one source is rejected with its source
line diagnostic; none is eligible for reconciliation/apply until the ambiguity is resolved.
Unaffected unique records remain eligible. Required fields are `Status`,
`Problem`, `Primary evidence`, and `Resumption condition`; unknown fields retain their order.
Multiline field values retain line boundaries, blank lines, and continuation indentation in
both transformed sections and the original excerpt.
Unknown status, missing structure, unsafe Markdown, and sensitive candidate data yield a
source line/reason diagnostic. Valid records still preview, but diagnostics mean the preview
is not a complete migration claim. Sensitive content is rejected rather than exported; this is
an explicit fidelity limitation.

Relative Markdown links are resolved from the source-file directory to immutable pinned blob
URLs with anchors and link text retained. Absolute URLs (including existing GitHub issue URLs)
remain unchanged. Anchor-only links resolve against the pinned source file, not the destination
issue. Bare OI references become source-qualified immutable source links; existing link labels
and targets are not rewritten as OI mentions. They do not create task/issue relationships.
Code spans (including Markdown-looking content) remain unchanged and are not claimed as
verified links. Nested link labels (for example `[see [OI-9]](relative.md)`) are unsupported:
public `preview` rejects the affected record with its source line and a corrective diagnostic.
Flatten the label in a reviewed source copy and preview again; never rewrite the preserved
original register merely to make an import pass. Parentheses inside link targets are also
unsupported and reject the affected record: use an explicit pinned absolute URL with
percent-encoded parentheses in a reviewed source copy, then preview again. Code spans remain
literal; unsupported structures never become successful truncated-link proposals.

For each originally closed record, preview, pending body and final body include this exact
visible disclaimer outside the unchanged original excerpt:

> Historical import: the source marked this record closed; its original closure reason is unknown. GitHub's native closure reason is platform metadata, not evidence of a verified fix. This import does not establish that the original problem was resolved.

## Read-only reconciliation

`reconcile(preview, GhApiTransport(), HOST, confirmed_mappings=None,
uncertain_identities=(), verified_observations=())` obtains one complete,
read-only destination snapshot before any future apply. Its transport uses the explicit target
only:

```text
gh api --method GET --hostname HOST --paginate --slurp \
  --header "X-GitHub-Api-Version: 2022-11-28" \
  "repos/OWNER/REPO/issues?state=all&per_page=100"
```

The installed `gh` 2.102.0 help confirms that `--paginate` follows every page, `--slurp`
returns page arrays, and field flags otherwise change the default method to POST. Keep the
explicit GET even though this lookup has no fields. The explicit REST version is `2022-11-28`;
a target that rejects it, any auth/rate-limit error, malformed result, missing page, failed
readback, or uncertain visibility is `incomplete lookup`, never evidence that a marker is
absent or that a create is eligible. Do not refresh auth. This is version-sensitive operational
guidance, not a claim that an untested target supports another version.

The snapshot excludes REST items with `pull_request` and compares raw exact body markers
(no title/search/near-match adoption). No marker is `planned create`, unless the identity is
still uncertain. `no-op` requires exact reviewed title/full body/marker/provenance/native state
and equality with a retained independently verified issue observation, including native reason.
Supply those prior GET results from the existing operational return as
`VerifiedIssueObservation(HOST, DESTINATION, API_VERSION, remote_issue)` in
`verified_observations`; do not invent evidence or introduce a tracking database. Host,
repository, API version and issue number must match. Missing prior observation, changed reason
(even between otherwise admissible values), title/body/state divergence, duplicate marker or
unknown state is an affected-record `conflict` with a review action. Never normalize away a
disclaimer, unknown sections or human edits. Same-valued intervening human actions cannot be
excluded by equality alone; this is best-effort observation, not atomic history proof.

For closed records, `completed` is admitted only for the observed github.com / API
`2022-11-28` mapping. Null readback requires actual independently verified closed/null evidence
for that same destination/API; nullable close input is not such evidence. `not_planned`,
`duplicate`, `reopened` and unknown values are not admitted: inspect the affected identity/value
and review mapping or human changes before further mutation. Other host/API mappings are not
guessed. No-op still requires the same exact prior observation, not merely an admitted value.
It does not reset stale source state, merge titles, overwrite human edits, or claim close ownership.
After a confirmed create/close, `ApplyResult.issue` is its independent GET observation; retain
it with the host/destination/API in the existing operation return for a later unchanged rerun.
For a discovered prior issue without that evidence, independently GET and review it rather
than treating the current listing itself as prior history. A `confirmed_mappings` identity
→ issue-number input reports an `existing-issue mapping` only when a reviewer has explicitly
chosen that visible non-PR issue; it preserves its body/state and is nonauthoritative. In
particular an historical link to issue #2 is not a mapping by itself.

Reconciliation is preview-only: it sends no stdin/body, uses no shell, and performs no labels,
assignments, uploads, relationships, create, edit, close, or reopen. Its result is the
read-before-write interface for later stages. One cooperating apply operator per source and
destination is expected; immediate readback/best-effort concurrent-edit detection is still
needed, and no exactly-once guarantee or repository-wide lock exists for simultaneous importers.

## Apply boundary

`apply(reviewed, GhApiTransport(), HOST, ApplyAuthorization(HOST, DESTINATION, WRITE_SCOPE))`
creates only records that were reviewed as `planned create` and remain `planned create` after
an immediate complete reinspection of that same explicit destination; it can also finish an
exact reviewed import-owned pending close. Originally closed records need an applicable native
reason mapping before any write. The reviewed host, apply `HOST`, authorization host, and authorization destination must
all exactly match the reviewed `HOST/OWNER/REPO`; the write scope must be non-empty. This is the
real write boundary, not an implication of previewing.
For an originally closed record, create uses an explicit `pending` closure provenance marker,
then independently reads that exact open staged body before one `PATCH` atomically replaces it
with the final `closed` marker/body and `{"state":"closed","state_reason":null}`. A final
GET must prove exact title, one marker, full final disclaimer-bearing body/provenance,
`closed` and an admitted native reason before the report says `closed`. Null input means
unspecified; it does not promise null readback. Native `completed` under the bounded mapping
is platform metadata, never original history or verified resolution. The source status remains
verbatim; its original closure reason is unknown. No fix, actor, or timestamp is invented.

Only the exact pending marker/body plus open state and null reason is known import-owned unfinished closure and
can resume on a later reviewed apply. A final imported body that is later open, an edited pending
body, duplicate marker, unexpected state/reason, pull request, failed listing/readback, or any
other ambiguity is `conflict`/`deferred`: never reset a possible human close/reopen. The helper
never adopts a title/near match, changes labels/assignees, or modifies existing overlap such as
issue #2.

A create sends the reviewed title and body to the explicit `repos/OWNER/REPO/issues` endpoint,
then independently GETs it, confirming exact title as well as marker/body/state. A lost POST
response is permanently uncertain: the helper performs a complete all-state marker listing and
independently GETs one exact candidate, but never retries that POST. Carry every deferred
uncertain identity into a later `reconcile(..., uncertain_identities={...})`; an absent marker
for one of those identities remains deferred until explicit human resolution, never a new create.
A lost close response is similarly resolved only by its final GET, never a second PATCH. Earlier verified results remain in the report if a later record fails. There is no remote
rollback: code rollback cannot undo a create/update/close, and recovery reconciles rather than
deletes or silently restoring local authority.

## Operational walkthrough

The production interface is Python: import `preview`, `reconcile`, and `apply` from
`scripts/import_open_issues.py`; it has no standalone CLI. Default operation is offline
`preview`; `reconcile` is an explicit read-only target lookup; only `apply` with an exact
`ApplyAuthorization(host, destination, write_scope)` matching the reviewed host and destination
can write. Before a future real apply, obtain
explicit destination/scope authority, review dry-run diagnostics/counts, choose any OI-4/#2
overlap mapping, run complete open+closed reconciliation, and independently map full
content/state/count readback. Human-confirmed adoption preserves existing content: no automatic
merge or close of #2. Keep the original Markdown intact; optional static mappings are
nonauthoritative.

T005/V2 selected proof (2026-10-22): **INCONCLUSIVE / NOT PASS.** The owner-authorized
`python3` helper invocation used one synthetic closed `OI-9005` record with
`Source("github.com", "elsonidoq/skills", "proof/t005-live-proof.md",
"t005-live-proof-20261022")`, destination `elsonidoq/skills`, and a wrapper that suppressed a
successful POST response only at the helper boundary. `gh version 2.102.0 (2026-09-30)` and REST
API version `2022-11-28` were used. Independent complete non-PR counts were 1 before and 1 after;
the helper reported `deferred`, suppression occurred, and an independent all-state marker lookup
found 0 candidates, so no candidate GET/body/state/reason result exists. The first invocation
exposed null issue bodies in real listing (now normalized to empty); the second was rejected with
HTTP 422 (`links/0/schema` nil); after adding `gh api --input -`, the third still had no visible
candidate despite the suppressed POST response. A later owner-approved recovery was limited to
existing issue #3's exact pending-close path (no new POST or other issue mutation). Its
read-only GET observed the old final body/title and `closed`, but GitHub reported
`state_reason: "completed"`, not null. These are old-render observations, not proof of the
amended disclaimer-bearing render. Original T005/V2 remains INCONCLUSIVE / NOT PASS under its
original criterion. The prospectively approved native-reason mapping does not retroactively
change that result. This was not a historical apply and made no change to #2; no proof issue
is automatically deleted.

Reassess retained invocation/recovery traces before considering a repeat. Retained actual
helper observations show suppressed successful POST → invisible marker/deferred result, then
later exact pending issue #3 → authorized helper close/independent GET, one matching identity
and no second POST in that recovery. The old invocations did not pass the later-added explicit
`uncertain_identities` input through another still-invisible apply; permanent composed fixtures
cover that carry-forward behavior, not a new real visibility experiment.

Before the body-only update below, read-only amended reassessment used the actual helper's
complete `list_issues` and #3 `get_issue`, reconstructing the unchanged excerpt with the recorded
Source above. It observed 2 non-PR issues, exactly one marker candidate (#3), exact retained
title, closed/completed, old body SHA256 `faff577298861a5b3550c90b762462d9f8f8d2189c26559bbf1c46d25c3bca17`.
That body lacked the new disclaimer; revised rendering differed only by its addition.
Actual `reconcile` with that GET and uncertain identity correctly returned body-divergence
`conflict`, not no-op. Offline fixtures prove exact revised body transmission/readback and
invisible→carried uncertainty→same-identity recovery, not new remote observations.

A subsequent owner answer, **“Authorize the body-only update to #3”**, allowed exactly one
body-only PATCH on github.com/elsonidoq/skills#3, preserving closed/completed, then independent
GET/full-list verification. The actual Python invocation (`python3 /tmp/sol-native-body-only-3.py`,
ephemeral command artifact) used this production transport, immediate exact-old-body/title/
marker/state/reason drift checks and JSON `{"body": revised_body}` only. It asserted the render
differed solely by the approved disclaimer and preserved the original excerpt. No POST,
reopen/close replay, #2 mutation or migration occurred. `gh` 2.102.0, API `2022-11-28`; counts
were 2→2 non-PR issues, one candidate (#3). Independent GET and complete listing confirmed
exact revised title/body/marker, unchanged excerpt, closed/completed and body SHA256
`e88c4cd85e742d9ebbe1bd87218854ff7fe1cf16c5b5bbbe9577a2b46d330550`.
Actual helper reconciliation with that independent observation returned `no-op`, with no
normalization of the old body. This supplies the revised body/readback observation, not a
new create or closure-transition experiment; the earlier drift observation remains historical.

Independent assessment must compose the retained real invisible-marker deferral and later
same-identity pending-close recovery with this revised exact live body/readback. Permanent
actual-helper fixtures establish the explicit uncertainty-input wiring; the old live run did
not exercise another still-invisible rerun using that later-added input. Do not force a new
invisibility episode merely as ceremony, or claim it was observed. Fresh independent review
of the retained sessions, body-only invocation, current actual-helper GET/list/reconciliation
and composed fixture found revised A4 **sufficient within these tested
bounds**. The review is supplied in `/tmp/github-open-issues-native-boundary-review.md`
(ephemeral review artifact); it is not self-certification or full migration acceptance.
Applicable unchanged observations may be reused for conditional consumer cutover; no additional
invisibility episode or new platform experiment is required. Original T005/V2
remains INCONCLUSIVE / NOT PASS under its original criterion. No further live mutation is
authorized. Retain the declared local owner until boundary acceptance and usable consistent
routing; reuse sufficient evidence rather than replaying proof or migrating real records.

Preview and reconciliation otherwise have zero external writes. Keep the original Markdown
intact; no source archive/delete or local tracking database is part of this skill. For an
authorized retained repository deliverable, follow the focused
[`task-commit-contract`](../memory-handling/references/task-commit-contract.md); external-only
work creates no empty commit and current runner ownership may retain staging/commit authority.
