---
name: track-open-issue
description: Use when verified unresolved work needs recording in the project's declared issue tracker.
---

# Track Open Issue

Record a verified unresolved-work candidate in the project's declared canonical owner.
For a project cut over to GitHub, use the explicitly configured GitHub Issues repository. Do not modify product code, tests, generated assets, deployment state, or
unrelated issues. A bare `#N` or `OI-N` is not an identity: report native issues as a
repository-qualified `HOST/OWNER/REPO#N` and URL.

## Declared owner before cutover

Read project instructions and routing before selecting a tracker. Preserve the existing declared local register until approved cutover. This is not a fallback for a GitHub capability failure and does not create a parallel tracker. Do not infer cutover from an installed skill, repository remote, or unfinished migration proof.

If project routing still declares an existing local register, read it and inspect open and closed entries for the same problem/evidence before adding or narrowly updating a candidate. Retain the verified problem, primary evidence, resumption condition, uncertainty and established identifier/format; preserve unrelated entry bytes and history. Close or reopen only with recorded problem-specific evidence and authority. Re-read before editing, stop on concurrent changes, then read back the affected entry and use the focused task checkpoint below. A missing or conflicting declared owner is deferred with the candidate/evidence/resumption and a corrective ownership action, not permission to initialize another tracker. Return after this local operation; the remote instructions below apply only to a declared GitHub owner.

## Candidate and target

Read every named source artifact. Retain, or ask only for, the minimum candidate facts:

- a concrete unresolved problem, classified as a bug, risk, shortcut, missing capability,
  or investigation where that classification is verified or supported;
- primary evidence for the problem (or for the uncertainty and needed evidence); and
- a resumption condition: the next action, prerequisite, or observation.

Keep uncertainty explicit; do not promote an unverified claim to fact or include credentials,
tokens, personal data, or sensitive payloads.

Resolve `HOST`, `OWNER`, and `REPO` from current project instructions/configuration, then
confirm the same target from verified remote evidence. Do not infer a target from a bare
number, an `origin` name alone, or another repository's issue URL. Missing or conflicting
target evidence requires a concise question about that target only.

Before any remote operation, check that `gh` is usable, authenticated for the explicit host,
and can read the target's issues without printing token values. For example, use
`gh auth status --hostname "$HOST"` and an explicit `gh api --method GET` target query.
Do not install `gh`, refresh authentication, change credentials, or use an implicit default
repository. A current authorization to write issues must be explicit for this target and
operation; successful reads or an ADMIN-looking field do not establish it.

If target, `gh`, authentication, issue capability, or required write authority is unavailable,
return `issue tracking: UNAVAILABLE` or `deferred`, together with the candidate, evidence,
resumption condition, missing capability/authority, and corrective action. Do not create or
fall back to a persistent local register.

## Discover overlap

For a verified candidate and usable read capability, inspect likely overlaps by problem,
affected area, and primary evidence across **all open and closed issues**. Use the explicit
target and complete pagination, for example:

```sh
gh api --method GET --hostname "$HOST" --paginate \
  "repos/$OWNER/$REPO/issues?state=all&per_page=100"
```

Exclude pull requests from this REST listing. Inspect every returned page and likely issue
body/comments as needed; GitHub's default open-only listing and a result limit are not full
discovery. Never deduplicate, merge, or reopen solely from a title or partial similarity.
A closed overlap remains evidence for the report and is not automatically reopened.

The intended body states the verified problem and category where supported, primary evidence,
resumption condition, and uncertainty. Prepare Markdown in a local body file and pass it with
`--body-file`; do not interpolate Markdown into a shell command, use `eval`, upload
attachments, or add labels, assignees, projects, parent/blocked-by relations, or unrelated
fields. An authorized create is explicitly targeted, for example:

```sh
gh issue create --repo "$HOST/$OWNER/$REPO" --title "$title" --body-file "$body_file"
```

## Create, scoped change, and state transitions

Create only when there is current explicit issue-write authority for this target and no exact
existing match. For an exact match, report `deduplicated`, or make only a narrowly authorized
change to the intended fields.

Before any scoped body overwrite or state transition, immediately GET the exact issue and
compare it with the content/state inspected for the proposed operation. Build a replacement
body by preserving unknown sections; do not erase comments/history, labels, assignees, or
unrelated state. If the issue changed, is ambiguous, or cannot be safely preserved, stop that
overwrite and report `deferred` with reinspection/review action. This read/check is not an
atomic compare-and-swap guarantee.

Close only with recorded evidence tied to the issue's problem and current close authority.
Reopen only with a verified recurrence or resumption basis and current reopen authority. Record
the basis in the intended issue fields and do not change unrelated issues. An authorized close
without outcome evidence is an operation confirmation, not a verified fix.

After every create, update, close, or reopen, independently GET the exact issue by number:

```sh
gh api --method GET --hostname "$HOST" "repos/$OWNER/$REPO/issues/$number"
```

Confirm the exact qualified URL/identity, intended problem/evidence/resumption content, and
intended state. Readback failure or unknown mutation response leaves verification unknown:
do not blindly retry a possibly successful mutation. Instead return the qualified candidate and
reconciliation action (GET/list complete open+closed results, then inspect the exact issue).
Separate remote operation confirmation from proof that the underlying problem is resolved.

## Report and checkpoint boundary

Report exactly one outcome: `created`, `updated`, `deduplicated`, `deferred`, or `not recorded`.
Include the qualified target/URL when known, candidate/evidence/resumption, intended and observed
state, any uncertainty, and required owner action.

External-only issue work creates no empty Git commit. If this skill produces an authorized
retained repository deliverable, follow the focused task checkpoint contract at
[`task-commit-contract`](../memory-handling/references/task-commit-contract.md); preserve real
manual gates, explicit authority, unrelated work, hooks, and signing. Local small fixtures are
allowed under routine authority, but they do not prove live GitHub behavior or grant external
write authority.
