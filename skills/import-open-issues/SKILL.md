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

## Apply boundary

Preview is the default and has zero external writes. Remote lookup, reconciliation, and apply
are intentionally not implemented by this offline stage. Before a future apply, require an
explicit named destination/write scope, reviewed preview, complete open-and-closed marker
reconciliation, independent readback, and a reviewed choice for any pre-existing overlap.
Never infer a fix, actor, timestamp, closure reason, or target availability from the
historical text. Keep the original Markdown intact; no source
archive/delete or local tracking database is part of this skill.
