---
name: track-open-issue
description: Use when verified unresolved work needs recording in its declared issue tracker.
---

# Track Open Issue

Record a verified unresolved-work candidate in the declared canonical owner. Coherence-specific
skill or workflow problems from any working project belong in the suite's declared tracker;
application-specific problems remain in the working project's declared tracker. Include useful
available context to help reproduce and address a Coherence problem; missing reproduction details
alone do not block filing, and do not construct a reproducer or run an evaluation for filing.
If the problem origin is unclear, clarify or defer it. For a target cut over to GitHub, use its
explicitly configured GitHub Issues repository. Do not modify product code, tests, generated assets, deployment state, or
unrelated issues. A bare `#N` or `OI-N` is not an identity: report native issues as a
repository-qualified `HOST/OWNER/REPO#N` and URL.

## Declared owner before cutover

Read the relevant project or suite instructions and routing before selecting a tracker. Preserve the existing declared local register until approved cutover. This is not a fallback for a GitHub capability failure and does not create a parallel tracker. Do not infer cutover from an installed skill, repository remote, or unfinished migration proof.

If the selected owner's routing still declares an existing local register, first perform the bounded investigation below, then read it and inspect open and closed entries for the same problem/evidence before adding or narrowly updating a candidate. Retain the verified observations/cause, hypotheses, primary evidence, resumption condition, uncertainty and established identifier/format; preserve unrelated entry bytes and history. Close or reopen only with recorded problem-specific evidence and authority. Re-read before editing, stop on concurrent changes, then read back the affected entry and use the focused task checkpoint below. A missing or conflicting declared owner is deferred with the candidate/evidence/resumption and a corrective ownership action, not permission to initialize another tracker. Return after this local operation; the remote instructions below apply only to a declared GitHub owner.

## Investigate candidate, then resolve target

Read every named source artifact before creating or changing an issue. Perform a bounded,
evidence-based RCA and retain the original intent alongside four distinct kinds of information:

- **verified observations:** directly supported failure facts and primary evidence;
- **verified cause:** only a causal conclusion supported by that evidence;
- **hypotheses:** plausible but unverified explanations, clearly labelled as such; and
- **uncertainty and next useful investigation:** what remains unknown and the next action,
  prerequisite, or observation that could resolve it.

Do not promote an unverified claim to a cause. An uncertain RCA does not block tracking
indefinitely: create a focused investigation issue when the verified observations, uncertainty,
and next useful investigation establish a concrete unresolved problem. Classify it as a bug,
risk, shortcut, missing capability, or investigation only where that classification is verified
or supported.

Prepare the intended body from that investigation. It must retain the original intent, verified
problem/evidence, any verified cause separately from hypotheses, uncertainty, and resumption
condition. Keep credentials, tokens, personal data, and sensitive payloads out of both the
investigation record and body. Preserve the intended body and the independently read-back body
for the later separate read-only quality review; creation/readback is not that review.

Resolve `HOST`, `OWNER`, and `REPO` from the selected owner's instructions/configuration, then
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

The intended body states the original intent, verified problem and category where supported,
primary evidence, verified cause only when established, clearly labelled hypotheses,
uncertainty, and resumption condition. Prepare Markdown in a local body file and pass it with
`--body-file`; do not interpolate Markdown into a shell command, use `eval`, upload
attachments, or add labels (except the required `AI generated` label below), assignees,
projects, parent/blocked-by relations, or unrelated fields. An authorized create is explicitly targeted, for example:

```sh
gh issue create --repo "$HOST/$OWNER/$REPO" --title "$title" --body-file "$body_file"
```

## Label agent-initiated issues

For every new issue initiated autonomously by an agent, rather than explicitly requested by
the user, require the exact label `AI generated`. General permission to track discovered work
is not a user request to create that specific issue. User-requested issues do not require this
label under this rule. Do not relabel existing matches found during overlap discovery.

Before an autonomous create, inspect the target repository's labels with complete pagination
(`gh api --method GET --hostname "$HOST" --paginate "repos/$OWNER/$REPO/labels?per_page=100"`).
If the exact label is absent, autonomously create it without asking for separate approval:

```sh
gh label create 'AI generated' --repo "$HOST/$OWNER/$REPO"
```

This rule authorizes only that label creation and assignment, not issue creation without the
existing target-specific issue-write authority. Do not modify an existing label's metadata.
If label creation fails or its response is unknown, re-read the labels to reconcile a possible
successful or concurrent creation; do not blindly retry. If the required label remains unavailable,
defer the issue create and report the failure and corrective action; do not create it unlabelled.
Once the label exists, include it in the issue creation operation:

```sh
gh issue create --repo "$HOST/$OWNER/$REPO" --title "$title" --body-file "$body_file" --label 'AI generated'
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

Confirm the exact qualified URL/identity, original intent, intended problem/evidence/cause-or-
hypothesis/uncertainty/resumption content, and intended state. For an agent-initiated create,
also confirm that the independently read-back labels include the exact `AI generated` label.
If missing, apply only that label to the exact issue and independently GET it again; report
any failure as incomplete labelling, not successful compliance, and do not create a duplicate.
Keep the actual read-back body
available with the original intent and investigation evidence for the separate read-only review;
do not represent creation/readback as independent review. Readback failure or unknown mutation
response leaves verification unknown: do not blindly retry a possibly successful mutation.
Instead return the qualified candidate and reconciliation action (GET/list complete open+closed
results, then inspect the exact issue). Separate remote operation confirmation from proof that
the underlying problem is resolved.

## Separate read-only quality review and one correction

After successful issue-body readback, use a separate read-only reviewer context. Read the
project's selected reviewer configuration; do not hardcode a provider or model. Dispatch the suite-owned `coherence-reviewer`
global user-agent role in a fresh context, with that model/effort unchanged. Use the
`subagent` tool `get` action to inspect its user source, effective prompt and read-only tools.
If it is missing or its effective configuration conflicts with the review boundary, report
review incomplete with the [suite setup correction](../../README.md#coherence-role-activation),
not a substitute reviewer or project activation. Give that
reviewer only the original user intent, primary evidence, uncertainty/next investigation, and
the actual read-back body. Ask it to identify downstream ambiguity or conflicts, omissions,
promoted assumptions, scope creep, and over-prescribed mechanisms or checks. It must not author
new product requirements or mutate the issue.

Evaluate each finding against the original intent and evidence. A clean review is a distinct
result, not a substitute for evaluating an actionable finding. For an ordinary in-scope wording
correction, retain the existing scoped mutation authority: immediately GET the exact issue,
compare the body used for review, preserve unknown content and change only the narrow affected
field. If the body changed, preservation is uncertain, or the proposed correction would
materially change the outcome, do not overwrite it; report `deferred` and either reinspection or
owner action as appropriate. After an authorized correction, independently GET the exact issue
again and report the before/after narrow content and final observed body. Do not run an automatic
multi-round review loop or add planning/approval ceremony for an ordinary correction.

If the reviewer is unavailable or fails, preserve the create/readback outcome and report the
review as incomplete with the capability/failure and resumption action. Do not fabricate an
assessment or blindly retry an expensive reviewer invocation; inspect a failed invocation before
any targeted retry. Actual reviewer judgment requires usable selected reviewer/delegation
capability, just as actual issue mutation requires exact target and operation authority.

## Report and checkpoint boundary

Report exactly one creation outcome: `created`, `updated`, `deduplicated`, `deferred`, or `not recorded`.
Include the qualified target/URL when known, original intent, verified observations/cause,
hypotheses, uncertainty/next investigation, intended and observed state, and required owner
action. Separately report mutation/readback outcome and review result (`complete`, `incomplete`,
or `not run`), including any finding evaluation, correction/readback, and whether GitHub and
reviewer actors were actual or simulated.

External-only issue work creates no empty Git commit. If this skill produces an authorized
retained repository deliverable, follow the focused task checkpoint contract at
[`task-commit-contract`](../memory-handling/references/task-commit-contract.md); preserve real
manual gates, explicit authority, unrelated work, hooks, and signing. Local small fixtures are
allowed under routine authority, but they do not prove live GitHub behavior or grant external
write authority.
