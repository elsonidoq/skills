# Validation guide

This guide schedules later implementation validation. **No runtime integration, provider,
tracker write, Phoenix launch or metadata export was run during planning.** Requirements and
gates remain in [spec](spec.md); [plan](plan.md) owns design and [interfaces](contracts/interfaces.md)
owns proposed CLI/Pi/lifecycle behavior.

## Prerequisites

Use reviewed tasks, current implementation authority and the selected executor. Consume
applicable final approval as described in [approval reuse](plan.md#approval-reuse-in-task-handoff);
do not ask again for unchanged amendments. Actual outstanding external/live gates remain.
Resolve the complete compatible hashed Python lock during authorized setup; use the selected
environment and usable Pi capabilities, not a required agent version.

Local checks use existing SDK fixture providers and temporary Git/SQLite state. They exercise
actual mechanisms without paid model traffic, but do not prove live model behavior or local UI
usability. No runtime or live checks were run during this planning correction.

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

## Trace privacy before real metadata export

Use the actual selected OTel SDK/exporter with an intercepted final HTTP transport. Put private
sentinels in prompts, responses, raw exceptions, tool payloads, paths, caller IDs, process resource
metadata, baggage and ambient headers/tracing configuration. Decode final OTLP protobuf bodies
and inspect destinations/headers for ordinary completion and error paths, not just a mapper mock.
Only allowlisted span/resource attributes and necessary safe protocol fields may remain. Automatic
exception events/status descriptions and raw graph state must be absent.

Set ambient LangSmith/OTLP remote endpoints, OTLP headers and HTTP proxy configuration in the
isolated test environment. With monitoring disabled, assert zero monitoring requests; with it
enabled, permit only the selected numeric loopback endpoint and safe headers. Exercise a redirect
response: no follow-up to a remote host. This checks actual SDK/session defaults, including
resource detectors, header merging and internal metrics, without sending sentinels to a real
collector. Existing Pi/model-provider network traffic is independent, not prohibited by this
monitoring-only assertion. No whole-process firewall or credential logging.

Use a reused-session interval and a missing/discontinuous end observation. Known usage remains
invocation-local; unknown fields are absent, not zero. Inspect run→task→invocation parentage,
opaque IDs, safe status and elapsed time. No per-tool/per-token instrumentation. Exporter init,
serialization and unavailable-collector failures must report a safe visibility gap while actual
checks/commits and otherwise safe execution continue. Prove these controls before real metadata
export; an environment flag or HTTP status alone is not evidence of privacy.

## Live replacement and monitor retirement — explicit gate

Under future scoped implementation authority, use the single-container settings/storage in
[interfaces](contracts/interfaces.md#local-monitoring-configuration). Local setup does not need
cloud account/project/region/pricing/upload consent. Preserve genuine uncovered external/paid/
security/data gates if introduced; real Pi calls use their existing scoped authority. Confirm
applicable final-wire privacy evidence for the actual adapter/dependencies before export.

At actual setup inspect local service/port/storage ownership, pin the selected image and verify
its effective version/settings and persistent SQLite path. No unknown existing asset is adopted
or stopped. Publish only loopback HTTP 6006; do not expose gRPC or ancillary ports. Check server
and browser network behavior with analytics/external resources disabled: no monitoring analytics,
fonts, model-price fetch, hosted tracing or other third-party monitoring request. Flags alone do
not establish the result. No provider integration is configured in Phoenix. Preserve the local
storage path/recovery instructions outside disposable worktrees; do not add an archive registry.

Observe one representative actual CLI graph run in local Phoenix **while it is still evolving**.
Use completed invocation/task or small graph-boundary spans, normal batch export/boundary flush,
and the selected UI's actual refresh behavior. Before root completion, inspect useful incremental
progress and graph/task/invocation relationships, role/model/status/time and honest known/unknown
usage/cost. Record the observed update/refresh limitations and concise evidence in normal delivery
evidence, without private payloads. A final ended-root trace, successful ingestion or an offline
fixture is insufficient. Open-span timers/dashboard parity and latency are not promised or tested
by assumption. If selected UI behavior is inadequate, report the concrete gap and retain the
monitor; do not build a custom UI, heartbeat or event-log framework to hide the gap.

T021 consumes the applicable successful T020 observation; do not ask the owner to recertify it.
Missing or invalidated evidence still blocks removal, not unrelated safe execution. Keep monitor
source/tests until this actual local replacement proof passes. Do not stop existing services,
delete databases, migrate history or close related issues as part of source retirement. Verify
relevant packaging/import/documentation callers after removal, retaining historical read access
and acceptance limits. No runtime, local service, exporter or UI acceptance has run in this plan.

## Issue delivery and manual assessment

Observe normal coordinator/finish-session delivery after actual checks and fresh independent
review. Use its existing issue or real no-issue intake path as applicable; publish the exact-
commit executive summary in the actual issue and current chat, then await owner review and
acceptance. This is a final delivery obligation, not a separate worker task or unrelated test
issue. [Interfaces](contracts/interfaces.md#delivery-issue-and-acceptance) define the content,
attribution and partial-publication handling.

When actual feedback occurs, inspect the linked corrections and refreshed presented commit.
When explicit acceptance and closure authority occur, retain the acceptance trace and read
back the closed state. Otherwise report those branches NOT VERIFIED; do not force a correction,
acceptance or closure exercise. Cheap inspection/walkthroughs may check handling of absent
branches, missing access or publication failure, but are not real owner/tracker actions.
Publication and acceptance-before-closure remain required; internal completion is not acceptance.

For manual assessment, perform one owner-selected real assessment. Complete discovery across
all actual pages and open/closed states in the selected repository, excluding PRs and without
requiring acceptance records for eligibility. Inspect the selected issues and available source
evidence; retain source links, evidence gaps and uncertain attribution. Reuse applicable T015
local pagination/classification evidence for cases absent from the live set. Report those absent
categories and the limits of live coverage; do not fabricate cases or block a meaningful
assessment merely because the repository lacks them.

Present supported grouped minimal proposals or a justified no-change conclusion, keeping
proposed and no-change status distinct. Actual GitHub label/comment operations require scoped
authority and readback. Any addressed label requires actual delivered improvement evidence;
if no such transition occurs, report it as unobserved (NOT VERIFIED). Do not create unrelated
improvements merely to test that transition. No automatic assessment at acceptance, skill edit
or PR.

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
