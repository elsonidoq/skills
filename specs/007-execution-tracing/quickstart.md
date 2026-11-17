# Validation guide — future implementation

This guide schedules validation. The feature is not implemented or accepted by this plan.
Use [contracts](contracts/README.md), [data model](data-model.md) and [acceptance mapping](plan.md#observable-acceptance-mappings).
No provider call, GitHub write, installation, branch creation or worktree deletion was run here.

## Prerequisites

- Current local launch authority is recorded in the [approval checklist](checklists/requirements.md#current-actual-owner-approval--implementation-launch). Parent targeted alignment inspection precedes launch; no repeated approval for the same settled scope. Use the exact selected executor, not the planning model. Actual runtime/SDK and ordinary isolated fixtures remain necessary.
- For external proof, actual authority for the named test target and operations, usable gh and
  authenticated read/write capability. Issue #45 is the feature association, not blanket test-write
  permission. No auth refresh/install or fallback issue.
- A long-lived attached parent session with bridge and ask_user, or an actual terminal for the
  direct path. Changed global tools/skills require a fresh-session handoff, not automatic reload.
- Preserve real manual/paid/security gates, focused checkpoints and fresh independent review.

## Existing focused checks to extend

These commands target existing production seams. Add relevant assertions to these tests or focused
new neighboring tests; task production must supply exact new test selectors after naming them.
Do not claim existing green output alone proves the new feature.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_graph_questions.py'
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_pi_adapter.py'
node --test runtime/tests/test_question_triage.mjs runtime/tests/test_bridge.mjs
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_check_correction.py'
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_worker_authority.py'
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_database_compatibility.py'
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -s runtime/tests -p 'test_graph_concurrency.py'
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime python3 -B -m unittest discover -s runtime/tests -p 'test_tracing.py'
python3 scripts/check-planner-workflow.py
python3 scripts/test-planner-workflow.py
python3 scripts/test-track-open-issue.py
```

Missing applicable installed dependencies report the actual missing operation; do not install
under planning authority. Use the already prepared validation interpreter documented in the
[runtime guide](../../docs/coordinate-implementation.md#setup-and-verification) if required by
that approved execution environment. Test runtime changes proportionately, retaining relevant
review/checkpoint/transport regressions rather than an exhaustive historical replay.

## Earliest production-seam proofs

1. **Actual hooks → history**: before formatter reliance, drive the installed SDK tool-call/result
   path with a controlled owner-tool result and the existing bridge. Use different owner-question
   wording, actual answer and worker-resolution wording. Check exact identity/content, denied and
   cancelled outcomes, missing result, reply failure, paused reopen, and final drain with no pending
   worker. No manual coordinator log. A fake metadata broadcast alone must not pass.
2. **Outcome projection**: show a rejected submission, actual failed configured check, inspected
   retry/escalation, fixer report, eventual pass/checkpoint and independent review. All earlier
   facts survive. Count logical events once; unknown historic coverage is not zero. Repeat the
   reader after reopening storage and with interleaved worker events.
3. **Publisher adapter**: use fake gh responses at the real subprocess boundary. Confirm whole
   body round trip, missing authority/target/auth with no write, partial multi-part failure, body
   mismatch, accepted-send/lost-response reconciliation, incomplete comment scan and known no-effect
   length rejection. No duplicate effect or dropped text. Inject credential sentinels in forbidden
   transport fields; none enters the payload. Ordinary Q/A must remain present.
4. **Terminal integration**: success and practical error paths drain, snapshot and publish under
   actual conveyed scope. Recording/export failure leaves implementation status and original error
   intact. Publication-only recovery must invoke no provider/check/Git action. Abrupt death without
   retained facts is an explicit gap, not a fabricated partial trace.

For each changed observable, demonstrate the smallest fail-then-pass regression of the actual
production helper. Mocks establish branch behavior only; they do not establish human participation,
SDK live behavior, permission or durable GitHub delivery.

## Genuine live acceptance (NOT RUN; separate scope required)

Use one representative authorized execution with actual owner and worker/coordinator questions,
a rejected completion, failed attempt, inspected retry/escalation and eventual completion. Observe
actual tools and record evidence through the feature, not a manual coordinator log or extra analysis
agent. Check available task/worker/attempt identities and links against observed occurrences. If
some required occurrence did not happen, report it untested; do not manufacture success.

Run through the existing entry after approval (placeholders refer to the approved actual handoff):

```sh
scripts/coordinate-implementation start --project "$PROJECT" --tasks "$TASKS" --executor "$EXECUTOR" --run "$RUN"
scripts/coordinate-implementation status --project "$PROJECT" --run "$RUN"
```

The task/input carrier must contain the actual approved target and publication scope once implemented;
these existing commands do not currently confer it. For attached proof, use the loaded
`coordinate_implementation_start` facade in a long-lived session. Verify a practical failure/partial
publication as well as normal finish; readback failure is not successful delivery. Do not blindly
retry an expensive failed run; inspect it and use existing cause-specific recovery authority.

After scoped publication, use a different context with **no access to the execution checkout**.
Worktree deletion itself is unnecessary and not authorized by this test. Starting only with the issue
URL, read all comments/parts, follow PR links and retrieve actual Q/A, meaningful evidence, rejection,
check/failure/retry details, counts, coverage and available code references. Repeat starting from PR.
Read-only commands for the selected real target include:

```sh
gh api --method GET --hostname "$HOST" "repos/$OWNER/$REPO/issues/$ISSUE"
gh api --method GET --hostname "$HOST" --paginate "repos/$OWNER/$REPO/issues/$ISSUE/comments?per_page=100"
gh api --method GET --hostname "$HOST" "repos/$OWNER/$REPO/pulls/$PR"
gh api --method GET --hostname "$HOST" --paginate "repos/$OWNER/$REPO/issues/$PR/comments?per_page=100"
```

Independently compare exact confirmed comment bodies, not only URLs/counts. Verify both issue-hosted
and PR-hosted association behavior at focused fixtures; live evidence must demonstrate genuine
navigation and durability for the selected scenario. Inaccessible code or missing content is a gap,
not inferred availability. Do not copy secrets into output.

## Planning and assessment acceptance

- Inspect bounded actual TinySpec and Standard examples: project-owned HTML design and explicit owner agreement precede detailed architecture plan production or continuation. Every clickable box opens component executive bullets (purpose, inputs/outputs, boundaries, choices); bullets below explain goal, supported properties, tradeoffs/limits and necessary context. Inspect the delivered [page](design-review.html) in a real browser: desktop/mobile readability, every box by pointer and keyboard, Close/Escape and return focus, truthful proposed labels and workflow/data-flow distinction. JS/DOM-stub success is supplemental; browser visuals remain NOT RUN until observed.
- Verify cancellation/denial/no agreement blocks affected details; opening/clicking grants no consent and significant changes renew agreement. Keep source, design and final implementation approval outcomes distinct, without repeated consent for the same settled shown scope. Significant choices need actual agreement, routine mechanics stay autonomous and every task retains evidence/gates.
- Under separately granted tracker scope, demonstrate no-issue planner understanding/brainstorming,
  exact overlap reuse or creation plus independent readback and body review. Do not create an issue
  for this existing #45 flow. Missing prerequisites must stop association without local fallback;
  closed exact overlap is not automatically reopened.
- Explicitly request assessment once from issue and once from PR in a checkout-independent context.
  Inspect supported later fixes. Findings cite evidence and separate reusable weaknesses, user-omitted
  requirements, hypotheses and gaps. No skill edits, automatic implementation or tracker writes.
- Confirm every delivered PR has a qualified issue link and the issue discovers it, regardless of
  trace location. Missing/unconfirmed link is incomplete linkage.

## Completion evidence and limits

Retain actual command/results, attributable task/repair SHAs, exact reviewed revision, independent
review findings and live readback URLs/content in the existing task/delivery evidence. Keep implementation,
trace delivery, coverage and owner acceptance distinct. No new ledger or startup check. A passing fixture
or returned worker cannot release a source-required live/manual/permission gate. Unavailable live scope
leaves those criteria NOT RUN; final feature acceptance stays pending.
