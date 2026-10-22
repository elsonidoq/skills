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
collisions. A duplicate OI ID in one source is rejected. Required fields are `Status`,
`Problem`, `Primary evidence`, and `Resumption condition`; unknown fields retain their order.
Unknown status, missing structure, unsafe Markdown, and sensitive candidate data yield a
source line/reason diagnostic. Valid records still preview, but diagnostics mean the preview
is not a complete migration claim. Sensitive content is rejected rather than exported; this is
an explicit fidelity limitation.

Relative Markdown links are resolved from the source-file directory to immutable pinned blob
URLs with anchors and link text retained. Absolute URLs (including existing GitHub issue URLs)
remain unchanged. OI references become source-qualified immutable source links; they do not
create task/issue relationships. Inline code paths are retained as code and are not claimed
as verified links.

## Read-only reconciliation

`reconcile(preview, GhApiTransport(), HOST, confirmed_mappings=None)` obtains one complete,
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

The snapshot excludes REST items with `pull_request`. It compares each raw, exact body marker
(no title/search/near-match adoption): unchanged body and native open/closed state is `no-op`;
no marker is `planned create`; body/state divergence, duplicate marker, or unknown close state
is an affected-record `conflict` requiring inspection. It does not reset stale source state,
merge titles, overwrite human edits, or claim close ownership. A `confirmed_mappings` identity
→ issue-number input reports an `existing-issue mapping` only when a reviewer has explicitly
chosen that visible non-PR issue; it preserves its body/state and is nonauthoritative. In
particular an historical link to issue #2 is not a mapping by itself.

Reconciliation is preview-only: it sends no stdin/body, uses no shell, and performs no labels,
assignments, uploads, relationships, create, edit, close, or reopen. Its result is the
read-before-write interface for later stages. One cooperating apply operator per source and
destination is expected; immediate readback/best-effort concurrent-edit detection is still
needed, and no exactly-once guarantee or repository-wide lock exists for simultaneous importers.

## Apply boundary

`apply(reviewed, GhApiTransport(), HOST, ApplyAuthorization(DESTINATION, WRITE_SCOPE))`
creates only records that were reviewed as `planned create`, remain `planned create` after an
immediate complete reinspection of that same explicit destination, and have native `open`
state. The authorization destination must exactly equal the preview destination and its write
scope must be non-empty; this is the real write boundary, not an implication of previewing.
For an originally closed record, create uses an explicit `pending` closure provenance marker,
then independently reads that exact open staged body before one `PATCH` atomically replaces it
with the final `closed` marker/body and `{"state":"closed","state_reason":null}`. A final
GET must prove one marker, exact final content, `closed`, and null reason before the report says
`closed`. The source status remains verbatim in the rendered content; null is used only because
no historical closure reason is specified. No fix, actor, or timestamp is invented.

Only the exact pending marker/body plus open state is known import-owned unfinished closure and
can resume on a later reviewed apply. A final imported body that is later open, an edited pending
body, duplicate marker, unexpected state/reason, pull request, failed listing/readback, or any
other ambiguity is `conflict`/`deferred`: never reset a possible human close/reopen. The helper
never adopts a title/near match, changes labels/assignees, or modifies existing overlap such as
issue #2.

A create sends the reviewed title and body to the explicit `repos/OWNER/REPO/issues` endpoint,
then independently GETs it. A lost POST response is permanently uncertain: the helper performs
a complete all-state marker listing and independently GETs one exact candidate, but never retries
that POST. A lost close response is similarly resolved only by its final GET, never a second
PATCH. Earlier verified results remain in the report if a later record fails. There is no remote
rollback: code rollback cannot undo a create/update/close, and recovery reconciles rather than
deletes or silently restoring local authority.

## Operational walkthrough

The production interface is Python: import `preview`, `reconcile`, and `apply` from
`scripts/import_open_issues.py`; it has no standalone CLI. Default operation is offline
`preview`; `reconcile` is an explicit read-only target lookup; only `apply` with an exact
`ApplyAuthorization(destination, write_scope)` can write. Before a future real apply, obtain
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
candidate despite the suppressed POST response. Do not retry or rely on uncertain-create/closure
behavior without review/renewed proof authority. This was not a historical apply and made no
change to #2; no proof issue is automatically deleted.

The required proof command path remains `python3` importing this helper with that one synthetic
record, `GhApiTransport()`, helper-boundary response suppression, independent `list_issues`
(open+closed, excluding PRs), and `get_issue` of exactly one marker candidate. Record
before/after count, identity/body/state/reason, visibility/concurrency limits, and actual output
before relying on uncertain-create/closure behavior. Do not run a real register migration or
delete a proof issue automatically.

Preview and reconciliation otherwise have zero external writes. Keep the original Markdown
intact; no source archive/delete or local tracking database is part of this skill.
