# Validation guide

This guide schedules later implementation validation. **No runtime integration, provider,
tracker write or LangSmith upload was run during planning.** Requirements and gates remain
in [spec](spec.md); [plan](plan.md) owns design and [interfaces](contracts/interfaces.md)
owns proposed CLI/Pi/lifecycle behavior.

## Prerequisites

Use an authorized implementation scope, the reviewed tasks and selected executor. Obtain
explicit approval of the plan's operative amendments before affected behavior relies on
them. Use existing usable Pi SDK/subagents/ask-user capabilities, without a required agent
version. Resolve/install new Python dependencies only under implementation setup authority;
update `runtime/requirements.lock` with the full compatible hashed wheel set, not just three
new top-level lines. Use the selected environment with `COHERENCE_PYTHON` where necessary.
No automatic install, credential change, authentication refresh or global reload.

Use a temporary Git repository and small isolated SQLite state for local checks. Preserve
normal hooks/signing and unknown/unrelated files. Existing SDK fixture providers exercise
actual host/adapter mechanisms without paid model traffic. Their results are not live model
obedience or LangSmith account usability. Live project/SDK invocations need the actual
implementation launch scope; application paid APIs and tracker/upload actions keep their
separate gates.

## Local command families

These existing entry points are inspected, not invented new test selectors:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime python3 -m unittest discover -s runtime/tests -p 'test_*.py'
node --test runtime/tests/test_host.mjs runtime/tests/test_bridge.mjs runtime/tests/test_saved_sessions.mjs
python3 scripts/check-planner-workflow.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-planner-workflow.py
bash scripts/check-skills-lint.sh
```

Select the smallest relevant test classes/files for each changed seam; run the composed
runtime collection at integration when appropriate. Update retained tests for the real
changed contracts, not to preserve obsolete sequential-controller assertions. After retiring
the RPC driver, planner tests must import and run without it. A failed applicable existing
check is not permission to skip it. New graph/privacy tests should join the existing test
owners; do not create a synthetic behavioral comparison programme. These commands require
their actual dependencies and are not application startup eligibility.

## Composed execution and recovery

After implementation, using approved task/executor inputs and an explicit test project:

```sh
scripts/coordinate-implementation intake --tasks "$TASKS"
scripts/coordinate-implementation start --project "$PROJECT" --tasks "$TASKS" --executor "$EXECUTOR" --run "$RUN"
scripts/coordinate-implementation status --project "$PROJECT" --run "$RUN"
scripts/coordinate-implementation history --project "$PROJECT" --run "$RUN"
scripts/coordinate-implementation resume --project "$PROJECT" --run "$RUN"
```

`TASKS`, `PROJECT`, `EXECUTOR` and `RUN` are operator-selected test inputs, not repository
assumptions. The new `--parallel` option is used only in the explicitly authorized fork/join
scenario, not silently added to normal launch. Use actual fixture/provider integration for
local deterministic tests; do not launch a real configured model merely to test parsing.

Observe these actual seams through permanent production helpers/CLI integration:

- A dependency waits for its producer's checks and focused commit; no issue is required by
  intake. Fresh independent review receives the exact attributable checkpoints and real
  command output. Inspect graph wiring to show the old engine is not a hidden second loop.
- Manual gate and in-call worker question: pause, drain host to idle, close/reopen the run,
  present the same pending question, answer through terminal and attached parent separately,
  and observe the reply in the actual saved-session continuation. Denial performs no gated
  effect. No prior settled tool/provider call repeats. A stale reply is not consumed.
- Inject loss before/after dispatch result and between Git success and history persistence.
  Verify the matching actual SHA is reused without recommit. An unknown live/provider
  effect stops before redispatch. Preserve unrelated staged/unstaged bytes and failed checks.
- Demonstrate explicit disjoint worker overlap then a quiescent check/commit barrier, one
  focused commit per task and a dependent join only after both checkpoints. Fail one branch;
  preserve the other's completed result and do not replay it on reopen. Overlap in owned
  paths/shared outputs requires coordination. Default launch never overlaps workers.
- Fail a required check or hook, make an ordinary scoped correction with current authority,
  rerun affected checks and checkpoint normally. Check initial/corrective/resumed prompt
  authority, permitted small local databases, preserved real gates and failure diagnosis.
- Read retained legacy rows with the new CLI; attempt legacy resume and verify the explicit
  compatible-runtime diagnostic, not automatic conversion. Exercise that old-runtime route
  against a suitable isolated legacy fixture/environment when available. Preserve old bytes.

These outcomes establish recovery within tested boundaries, not exactly-once external effects
in general. A failed/unrun composed seam blocks consumers that rely on it, not unrelated work.

## Trace privacy before any upload

Use the actual selected LangSmith SDK with a local intercepted transport. Put distinctive
private sentinels in prompts, responses, raw exceptions, tool data, paths, caller IDs and
ambient tracing metadata. Inspect all actual outgoing request bodies and relevant URL/header
content for create/update/error paths. Only the closed approved observation plus necessary
safe SDK protocol fields may be sent. Turn ambient tracing on while application authority
is off and assert zero network submission. Exercise SDK initialization/submission failure:
execution still checks/commits safely and reports a visibility gap.

Use a reused-session interval and a missing/discontinuous end observation. Known local
usage stays invocation-local; unknown fields are absent, not zero. Inspect run→task→
invocation parentage, opaque identities, safe outcome and elapsed time. No raw graph state
or per-tool/per-token spans. This check is of final SDK serialization, not just a mapper mock.

## Live replacement and monitor retirement — explicit gate

Before a real call, obtain the selected LangSmith account/project/region/access, pricing
acceptance and network/upload authority. Confirm the local privacy checks passed for the
same adapter/dependencies. Run one otherwise authorized real Pi invocation through the
actual CLI graph, then inspect the LangSmith UI for usable graph/task/invocation relationships,
model/role/outcome/time and qualified known/unknown usage. Record the concise observation
and limitations in the existing delivery evidence, without private payloads.

Only that observed live result releases monitor-only source/dependency removal. HTTP success,
an offline fixture or missing account authority does not release it. Keep monitor tests and
source until then. Do not stop an existing service, delete databases, migrate history or close
related issues as part of source retirement. Verify relevant packaging/import/documentation
callers after removal and retain historical read access and acceptance limits.

## Issue delivery and manual assessment

Use one explicitly authorized issue for the real delivery scenario: start without an issue,
associate/create through declared ownership, retain planning links, finish reviewed work,
publish matching issue/chat summaries for an exact commit, link an owner correction by
purpose, refresh the summary and obtain explicit acceptance before authorized closure.
Inspect both publications and closure readback. Also exercise missing tracker access and a
partial publication failure without inventing success or a local fallback.

For manual assessment, use a bounded owner-selected representative issue set. Include more
than one page, open and closed issues, a PR to exclude, missing acceptance/artifacts, an
unrelated concurrent commit, a changed requirement, a genuine supported omission and a
previously assessed issue. Inspect all pages and source evidence. Verify grouped minimal
proposals, uncertainty, and proposed/no-change status; addressed requires actual delivered
improvement evidence. Local retained-reader tests/walkthroughs can establish selection and
instruction limits, but actual authorized GitHub label/comment effects need readback. No
automatic assessment at acceptance, skill edit or PR.

## Retirement and final delivery checks

Verify the five named files (four evaluation documents plus the RPC driver), its `rpc` import
and driver-only test class are removed; active evaluation/smoke mandates are superseded at
the named owners. Preserve historical observations and NOT RUN records. Run relevant retained
static/runtime/security checks and inspect changed links. Keep monitor-specific deletion
separate from this behavioral retirement until its live gate is met.

Before final owner delivery: inspect every focused task checkpoint, actual checks, composed
acceptance and outstanding gates, then obtain fresh independent review. Report PASS/FAIL/
NOT RUN/UNAVAILABLE accurately. Do not call an internally complete run accepted. Changed
global skills/extensions in Paseo need a fresh-session handoff that verifies revision,
current approval and loaded capabilities; never instruct `/reload` or restart automatically.
