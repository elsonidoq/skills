---
name: track-open-issue
description: Use when verified unresolved work needs recording, or an existing issue needs an authorized delivery comment or state change in its declared tracker.
---

# Track Open Issue

Resolve the declared tracker, make only the authorized effect, and independently read it back.
Choose the operation first:

- **Record a candidate or change its problem body:** investigate the candidate and discover overlap
  below; preserve the intended body for the separate quality review.
- **Publish delivery or change state:** use the known qualified issue and recorded delivery/outcome
  evidence. An ordinary delivery comment does not require fresh candidate RCA, overlap discovery
  or issue-body quality review. A substantive problem-body change does.

Do not modify product code, tests, generated assets, deployment state or unrelated issues. Keep
credentials, tokens, personal data and sensitive payloads out of all records. A bare `#N` or
`OI-N` is not an identity: report native issues as `HOST/OWNER/REPO#N` and URL.

## Resolve the owner and authority

Read project/suite instructions and routing. Coherence skill/workflow problems belong in the
suite's declared tracker; application problems belong in the working project's tracker. Clarify
or defer unclear origin. Include available reproduction context, but missing detail alone does
not block filing; do not build a reproducer or run an evaluation just to file.

Preserve the existing declared local register until approved cutover. Installed skills, repository
remotes or unfinished migration proof do not establish cutover. A declared local register is
not a fallback for GitHub failure. For local candidate work, perform the investigation below,
then inspect open and closed entries for the same problem/evidence. Retain its identifier/format,
intent, observations/cause, hypotheses, evidence, uncertainty and resumption condition; preserve
unrelated entry bytes and history. For local delivery, consume the delivery contract below.
Close/reopen only with recorded problem-specific evidence and scoped authority; delivery closure
also needs acceptance of the presented revision. Re-read before editing, stop on concurrent
changes, read back the affected entry and apply the focused checkpoint. Return after the local
operation; the remote procedure does not apply. Missing/conflicting ownership defers the operation
with evidence, resumption condition and corrective ownership action, never a new tracker.

For GitHub, resolve `HOST`, `OWNER`, and `REPO` from the selected owner's configuration/instructions
and confirm the same target from verified remote evidence. Never infer it from a bare number,
`origin` alone or another repository's issue URL. Ask only about the target if evidence conflicts
or is missing. Before remote operations, verify usable `gh`, authentication for that explicit host
and read capability for its issues, without printing tokens. For example:

```sh
gh auth status --hostname "$HOST"
gh api --method GET --hostname "$HOST" "repos/$OWNER/$REPO/issues?per_page=1"
```

Do not install `gh`, refresh authentication, change credentials or use an implicit default repo.
Current write authority must explicitly cover this target and operation; successful reads or an
ADMIN-looking field do not grant it. Missing target, capability, authentication or required authority
returns `issue tracking: UNAVAILABLE` or `deferred`: candidate/operation, evidence, resumption
condition, missing requirement and corrective action. For GitHub ownership, never create a persistent
local fallback or write a historical register.

## Investigate and compare candidates

Read every named source artifact. Perform bounded evidence-based RCA and prepare one body that
retains original intent, verified problem/category (bug, risk, shortcut, missing capability or
investigation where supported), primary evidence and resumption condition. Distinguish:

- verified observations from directly supported evidence;
- verified cause only when causally established;
- labelled hypotheses, not promoted assumptions;
- uncertainty and the next useful investigation, prerequisite or observation.

Uncertain cause is not an indefinite filing block: concrete observations, uncertainty and next
investigation can support a focused investigation issue.

With usable read capability, inspect overlaps by problem, affected area and primary evidence across
**all open and closed issues**, with complete pagination:

```sh
gh api --method GET --hostname "$HOST" --paginate \
  "repos/$OWNER/$REPO/issues?state=all&per_page=100"
```

Exclude pull requests. Inspect every page and likely bodies/comments as needed; an open-only or
limited listing is not full discovery. Never deduplicate, merge or reopen solely by title or partial
similarity. Report closed overlaps without automatically reopening. Create only with current explicit
write authority and no exact match; for an exact match, report `deduplicated` or make only the
narrowly authorized change.

## Make the scoped effect and read it back

Prepare Markdown in a local body file and use `--body-file`; do not interpolate Markdown into shell
commands or use `eval`. No attachment uploads, labels (except `AI generated` below), assignees,
projects, parent/blocked-by relations or unrelated fields are authorized by candidate recording.

For every autonomously agent-initiated new issue, require the exact label `AI generated`. General
permission to track findings is not a user request for that specific issue. User-requested issues
need no label under this rule; do not relabel existing overlap matches. Before autonomous creation,
inspect all label pages:

```sh
gh api --method GET --hostname "$HOST" --paginate "repos/$OWNER/$REPO/labels?per_page=100"
```

If absent, create only that label without separate approval; do not alter existing label metadata:

```sh
gh label create 'AI generated' --repo "$HOST/$OWNER/$REPO"
```

This does not grant issue-write authority. On failure/unknown response, re-read labels to reconcile
successful or concurrent creation, never blindly retry. If still unavailable, defer creation with
the failure/corrective action; do not create unlabelled. Use an explicit target, adding the label
only when required:

```sh
gh issue create --repo "$HOST/$OWNER/$REPO" --title "$title" --body-file "$body_file" --label 'AI generated'
```

Immediately before a body overwrite or state transition, GET the exact issue and compare with the
content/state inspected for that operation. Preserve unknown sections, comments/history, labels,
assignees and unrelated state. Changed content, ambiguity or uncertain preservation stops the
overwrite/transition: report `deferred` and reinspection/review action. This is not atomic compare-and-swap.
Close only with recorded evidence tied to the problem and current close authority; reopen only
with verified recurrence/resumption and current reopen authority. Record the basis in intended fields.
An authorized close without outcome evidence confirms an operation, not a verified fix.

After every create, update, close or reopen, independently GET the exact issue by number:

```sh
gh api --method GET --hostname "$HOST" "repos/$OWNER/$REPO/issues/$number"
```

Confirm qualified identity/URL, intended content and state. For a candidate body, compare all
investigation fields above and retain both intended and actual read-back body for quality review.
For autonomous creation, confirm the exact `AI generated` label; if missing, apply only that label
to the exact issue and GET again. Report failure as incomplete labelling, not compliance, and never
create a duplicate. For comments, read back the exact comment effect as well.

Unknown response or failed readback leaves verification unknown. Inspect the exact issue/comments;
for uncertain creation reconcile complete open+closed listings and exact GET before any retry.
Do not blindly retry a possibly successful mutation. Operation confirmation is distinct from proof
that the underlying problem is resolved.

## Reviewed issue-linked delivery

Load [finish-session's delivery contract](../finish-session/SKILL.md#issue-linked-delivery) when
publishing implementation delivery. Consume its meaningful executive text, attribution, evidence,
exact reviewed revision, feedback/correction links and acceptance trace for the issue and owner chat;
do not repeat an implementation review or invent missing evidence. If unavailable, defer delivery
with the missing contract and corrective action.

Keep this local guard: close only after explicit acceptance of the presented revision and current
operation-scoped closure authority, then independently read back closure. Acceptance of an earlier
revision does not accept a corrected revision; acceptance alone grants no closure, RCA, skill edit,
PR or unrelated issue change.

If publication is uncertain, inspect the exact issue/comments before retrying. If issue or chat alone
succeeded, report the partial result and retry only the missing operation after inspection. Missing
capability or authority defers the tracker effect with corrective action, not an authorized chat
report. Unobserved feedback, acceptance and closure are `NOT VERIFIED`.

## Review a recorded problem body

After successful candidate issue-body readback, use a separate fresh read-only quality reviewer.
Read the project's selected reviewer configuration, preserving its model/effort; do not hardcode
or substitute a provider/model. Inspect the suite-owned `coherence-reviewer` global user-agent with
`subagent` `get`: user source, effective prompt and read-only tools. Verify usable selected reviewer/
delegation capability. If absent or conflicting, report review incomplete with the
[suite setup correction](../../README.md#coherence-role-activation), not project activation or a
substitute reviewer.

Give it only original user intent, primary evidence, uncertainty/next investigation and actual
read-back body. Request ambiguity/conflict, omission, promoted-assumption, scope-creep and
over-prescribed-mechanism/check findings. It must not create product requirements or mutate issues.
Creation/readback is not independent quality review.

Evaluate each finding against intent/evidence; a clean review is a distinct result, not a substitute
for evaluating actionable findings. For one ordinary in-scope wording correction, retain existing
scoped authority: immediately GET, compare with the reviewed body, preserve unknown content and
change only the affected field. Drift or uncertain preservation defers to reinspection; material
outcome changes need owner action. After correction, GET again and report narrow before/after content
and the final observed body. No automatic multi-round review loop or extra planning/approval ceremony
for an ordinary correction.

If review is unavailable or fails, preserve the mutation/readback outcome and report review incomplete
with failure/capability and resumption action. Do not fabricate assessment or blindly retry an
expensive reviewer; inspect the failed invocation before any targeted retry.

## Return the observed result

For candidate recording report one outcome: `created`, `updated`, `deduplicated`, `deferred` or
`not recorded`. Include qualified target/URL when known, intent, observations/cause, hypotheses,
uncertainty/next investigation, intended/observed state and required owner action. For delivery/state
operations, report that operation's observed result rather than inventing a creation outcome.
Separately report mutation/readback and review (`complete`, `incomplete` or `not run`), finding
evaluation/correction/readback and whether tracker/reviewer actors were actual or simulated.

External-only work makes no empty Git commit. Authorized retained repository deliverables use the
[focused task checkpoint contract](../memory-handling/references/task-commit-contract.md), preserving
manual gates, explicit authority, unrelated work, hooks and signing. Routine small local fixtures do
not prove live GitHub behavior or grant external write authority.
