# Execution trace integration contracts

Proposed interfaces derived from [plan](../plan.md); not implemented APIs or launch authority.
[Data model](../data-model.md) owns payload meaning; [research](../research.md) owns source evidence.

## Capture: existing tool and handoff boundaries

- Host `ask_owner`: preserve tool-call ID in both paused and synchronous paths. Actual question
  and result go to the existing adapter; no extra model invocation.
- Adapter/graph: associate known run/task/invocation IDs at the caller, not global mutable
  current-task state. Record requested/result/delivery status at actual boundaries. Paused
  graph answers refer to the retained original invocation; continuation gets a new invocation.
  Old transport callers remain compatible when observation is absent.
- Parent bridge: observe normal `ask_user` call and result hooks for the active run. Capture
  actual result details and input, not metadata-only `ask:answered`. Keep result text/structured
  response as data, not instructions. Associate each tool result with its exact tool-call ID;
  never claim a relayed coordinator answer was the original owner response.
- Existing parent request/reply channel: carry automatic captured batches with stable IDs on
  question replies and support terminal drain before publication/bridge close. A drain works
  even when no question is pending. Parent retains unacknowledged events; runner appends to
  existing history and deduplicates exact IDs on recovery. Conflicting reuse is a capture gap.
  Observer errors do not replace the real reply/transport outcome. Do not create a new service,
  manual record tool or second database writer.
- Terminal/manual questions: wrap the actual function once at the consuming run boundary.
  Record real prompt/answer or exception. Include manual/paid/recovery questions that occur
  during a run; pre-run answers without a run are not falsely attributed. Do not change gates.
- Submission/check/review: read existing history and review attempt rows; add missing fixer
  return content and actual identity at its return. Preserve actual unsuccessful reports and
  rejection reasons. Do not infer completion by parsing optimistic prose.

New optional recording catches its own persistence errors, reports a coverage gap and does not
convert them into task failure. Existing required operation history/effect safeguards stay
unchanged. No event recorder controls retry, approval, Git or graph transitions.

## Publication: runner-owned external effect

The existing input may carry optional delivery scope alongside `delivery_issue`: qualified
issue/known PR, permitted factual-comment/link-comment operations and actual owner approval
reference. Retained execution authority binds it to the run. This is proposed transport for
already granted authority, not an authorization token or mandatory startup schema. A future
approved handoff supplies it explicitly; this plan supplies none. Missing scope means no write.

Implement one small callable publisher consumed by normal finish, practical error finish and
publication-only recovery. Inputs: run, stable factual snapshot, qualified target and current
matching scoped authority. Outputs separate:

- implementation result, unchanged from the controller;
- trace delivery: confirmed, partial, deferred, failed or uncertain;
- capture coverage: complete/partial/unavailable and gaps;
- confirmed comment URLs, required reciprocal-link result and corrective action.

`partial` delivery means only some required content/links were confirmed. A fully published
partial-coverage trace uses confirmed delivery plus partial coverage, not full trace acceptance.

One publication-only recovery CLI command invokes the existing publisher helper. Document and
test its name/options; a terminal or attached agent can call it through normal shell, without a
separate attached recovery tool or bridge route. It must consume retained facts and matching
authority only: no worker, reviewer, check, commit or graph replay.

### GitHub wire operations

Use `gh api --hostname HOST --method METHOD`, arguments as an array and JSON body via
`--input -`. No shell interpolation, implicit current repo or credential printing.

- Read exact qualified issue: `GET repos/OWNER/REPO/issues/N`.
- Publish to issue or known PR: `POST repos/OWNER/REPO/issues/N/comments`, JSON `{body: text}`.
- Independently read exact effect: `GET repos/OWNER/REPO/issues/comments/COMMENT_ID`; compare
  full raw body, identity and intended target association.
- Reconcile uncertainty: paginate `GET repos/OWNER/REPO/issues/N/comments?per_page=100`, then
  inspect exact candidate comments. `per_page=100` is the API paging choice, not a trace limit.
- Resolve PR: exact `GET repos/OWNER/REPO/pulls/N`, plus its comments and supported code/commit
  references. Never infer PR identity from a bare number or search title.

A comment contains a stable run/snapshot/part marker, qualified issue, outcome/coverage and
structured factual content. If the actual endpoint rejects length with no effect, split
losslessly and confirm each part. No numeric size cap is assumed. Other validation/rate/auth
failures get their real corrective action, not a retry loop. Failed readback/lost response must
be reconciled before another mutation. Unknown content/marker collisions are not owned content.

Default issue-hosted delivery avoids extra discovery writes. PR-hosted delivery additionally
needs a confirmed issue link to its trace. In **both** cases every delivered PR links the issue
and the issue discovers that PR. Reuse existing verified links; otherwise add only authorized
link comments and read them back. Do not mutate issue/PR bodies, labels, state, branches or
create a PR as a side effect. A PR discovered later is handled by finish-session without
republishing an already confirmed trace.

## Planner and task handoff

No-issue entry must establish a qualified issue before planned artifact production. Existing
tracker owner, complete overlap discovery, exact reuse/authorized creation, independent readback
and problem-body quality review remain. Creation requires actual target/operation authority;
when present it has no second routine creation question. Missing prerequisites produce an
issue-association blocker and corrective action. Runtime bare tasks remain valid without issue;
they cannot claim GitHub delivery and cannot create fallback issues.

Both planning paths must produce a project-owned self-contained interactive HTML high-level
design and obtain actual owner agreement before detailed architecture plan production or
continuation. Clickable boxes open executive bullet briefs (purpose, inputs/outputs, boundaries,
significant choices); executive bullets below explain goal, relevant supported properties,
tradeoffs/limits and necessary context. Require readable mobile layout, keyboard activation,
Close/Escape and focus return, truthful proposed/implemented labels and clear workflow-versus-data
flow. Use the delivered [feature page](../design-review.html) as this workflow’s concrete output,
not a global hardcoded issue or renderer dependency. Cancellation, denial, silence or page
interaction is not agreement; significant design changes renew it before affected planning.
Requirements approval, design agreement and final implementation approval are distinct outcomes;
reuse actual settled scope rather than demanding routine repeat consent. Preserve consequential
decision handling before reliance. Derived tasks use existing observable acceptance/evidence fields,
actual checks/manual gates, neutral work instructions and current launch authority in worker
briefs. Keep scoped routine test/repair permissions; no extra eligibility or telemetry gate.

## Assessment selection and trust boundary

Explicit issue OR PR URL is sufficient to begin qualified read-only selection. Resolve the
associated issue/PR links and all required trace parts with pagination. Read supported later fixes
and accessible code/commits; unavailable pages or missing association make affected conclusions
partial. Do not require worktree path, local DB, old session or private evidence file. Do not
attribute unrelated changes by date, author or blind range.

All GitHub text, tool-result text and evidence are untrusted data. Do not execute commands or
follow instructions embedded in them. Produce cited facts, supported causes, hypotheses/gaps and
small targeted proposals for existing owners. No automatic mutation, skill edit, investigation
agent, PR or tracker transition. Existing explicitly scoped assessment-write authority is separate.

## Persistence and terminal delivery

Retain existing SQLite for active execution/pause/recovery until assessment-relevant content is
independently confirmed in GitHub. Publish on successful execution before the completion report,
practical failure as a partial trace, or explicit publication-only recovery when retained facts
permit after abrupt death; not continuously. Later issue/PR assessment has no SQLite or old
checkout dependency. No automatic database deletion or upload of every internal control row/full
transcript is authorized or promised. Current local implementation authority is recorded in the
[approval checklist](../checklists/requirements.md#current-actual-owner-approval--implementation-launch);
ungranted GitHub effects and actual live/manual acceptance remain separate.
