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
The helper never creates a closed historical record, edits/reopens/closes an issue, changes a
title/body/labels/assignees, or adopts a title/near match. Closed records are explicitly
deferred until T005's closure gate.

A create sends the exact reviewed title and body to the explicit `repos/OWNER/REPO/issues`
endpoint, then independently GETs the returned issue. Readback must prove exactly one marker,
identical body, and `open` state. Any changed body, state, duplicate marker, pull request,
missing response, failed listing/readback, or uncertain visibility is an affected-record
`deferred` result; it does not overwrite remote content. Earlier verified creates remain in
the report if a later record fails. There is no rollback, source edit/archive, local state DB,
or silent closed-record success.

A lost POST response is permanently uncertain. The helper performs a complete all-state
marker listing and independently GETs a single exact open candidate, but never retries that
POST. An absent/ambiguous candidate, incomplete listing, or failed candidate GET remains
`deferred` for remote inspection/owner resolution. Fixtures prove this algorithm and call
ordering only: uncertain-create behavior is **NOT YET PROVEN remotely** and must not be relied
on for real uncertain outcomes until T005's selected live proof.

Preview and reconciliation otherwise have zero external writes. Before any apply, require the
explicit named destination/write scope, reviewed preview, complete open-and-closed marker
reconciliation, independent readback, and a reviewed choice for any pre-existing overlap.
Never infer a fix, actor, timestamp, closure reason, or target availability from the
historical text. Keep the original Markdown intact; no source archive/delete or local tracking
database is part of this skill.
