# Tasks: Script-driven read-only workflow monitor

**Status: proposal only; implementation NOT authorized.** [tasks.json](tasks.json) is the matching
machine task list. Source owners: [spec](spec.md), [plan](plan.md), [data model](data-model.md),
[monitor contract](contracts/monitor-v1.md), [validation](contracts/validation.md), [quickstart](quickstart.md).
Historical four-task approvals and prerequisite tasks do not authorize this revised three-outcome plan.

## Shared constraints

Each worker first reads this file and the linked spec/plan/data/API/validation sources, then follows
these shared constraints and its task-local pass conditions. Root JSON planning metadata is not a
runtime enforcement mechanism; task descriptions explicitly carry this reading instruction.

- Future executor: owner-selected `openai-codex/gpt-6.1-sol`, effort `medium`; no substitution.
- One existing script writer, actual requested project checks, explicit owned-path checkpoint after each
  outcome, normal hooks/signing, unrelated dirty-work preservation and fresh read-only final review.
- No retired engine/YAML execution, catalog/manifest/custody/receipt admission, PythonAnswer workaround,
  universal payload ceiling, frozen dependency descriptor or repeated environment attestation.
- Recording is optional to execution, not to honest monitor acceptance. A recording failure warns but
  cannot veto work; missing history is incomplete/unknown. No private transcript mining or reconstruction.
- No automatic correction cycle. The graph MUST contain distinct reviewer, fixing-agent, checks/checkpoint
  and rereviewer occurrences when those executions occur, including explicitly linked local fresh runs.
- No install/network/auth refresh/global activation, application/model launch or external action from
  these proposal artifacts. Explicit future implementation/setup/launch approval is still required.

## T001 — Recording and original-range correction-review foundation

**Depends:** none. **Delivery:** separate approved runtime change BEFORE the app-build run.

Implement minimal retained phase/task description and append-only closed observations in the existing
DB, keeping current progress rows and all legacy rows unchanged. Emit at task preparation/manual gates,
worker calls, each runner check, checkpoint, independent review, question terminal/host-send boundaries,
terminal outcomes and explicit abandon. Record failures before raising and distinguish no-change.

Every actual worker/reviewer call gets a distinct occurrence identity/role. Retain actual review range,
approval/finding count, not raw findings. Optional `monitor.correction_of` records a declared local
relationship and safe presentation. Extend script status/history sufficiently to obtain actual recording
occurrence IDs without private transcripts; these CLI results are not the browser API.

Add bounded optional `review_base` so a separately approved fixing run's fresh independent reviewer
actually inspects original-base→current-head. Validate with ordinary Git commit/ancestor operations;
invalid range fails the affected review, not all telemetry. Default range and task ownership stay unchanged.
No auto-fixes/retries, reviewer result injection, task rewriting, old-run adaptation or new dependency.

**Owned paths:**
- `runtime/coherence_workflow/monitoring.py`
- `runtime/coherence_workflow/store.py`
- `runtime/coherence_workflow/engine.py`
- `runtime/coherence_workflow/verification.py`
- `runtime/coherence_workflow/pi_adapter.py`
- `runtime/coherence_workflow/cli.py`
- `runtime/tests/test_monitoring.py`
- `runtime/tests/test_engine.py`
- `runtime/tests/test_pi_adapter.py`
- `runtime/tests/test_recovery.py`
- `runtime/tests/test_verification.py`
- `runtime/tests/test_cli.py`
- `docs/coordinate-implementation.md`
- `docs/coordinate-implementation-schema.md`

**Checks:**
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -v -s runtime/tests
node --test runtime/tests/test_host.mjs
```
Use the explicitly prepared environment; do not install missing requirements from a check.

**Required pass conditions (SC-001/002/004/005/006 foundation):** actual engine→DB emission/readback
with disposable Git/check operations and labelled offline adapters; distinct worker/reviewer/fixing
occurrences; failed check retained before raise; rejected/invalid review, interruption, gate/question
send/error, no-change/uncertain checkpoint and abandonment preserve history. Privacy sentinels never
enter monitoring rows. Injected recorder failures never block SDK/check/Git/review, replace actual
errors or fabricate completion. Default review unchanged; linked correction rereview actually receives
original base→new head, with invalid base rejected for that review. No automatic retry or legacy mutation.
Docs describe actual delivered interfaces and non-guarantees. Commit and accept this foundation before
starting a fresh application run of T002/T003.

## T002 — Early usable safe selected-run graph

**Depends:** T001 accepted checkpoint. **Delivery:** first task of the new recorded application build.

Deliver reader/mapping/minimization, loopback production API/assets, left run selector, one graph and
brief details. Retained phase anchors, prerequisites and observed occurrences are distinct; every actual
model execution is a node. Already support recorded failures/milestones, unknowns and core review ranges,
not merely a status list. Provide stable polling/navigation and complete inventory with history reveal.

New-contract worktree runs only, read-only SQLite snapshots, no writer/SDK/runtime launch imports or
control endpoints. Minimize before exposure; no raw private error/summary/commands/findings/paths.
Conventional app manifests/locks, existing selected library choices, ordinary build/browser setup under
separate authority. No forensic environment protocol. Deliver focused tests and early README/launch
instructions so the independently owned observer can open THIS run after the task checkpoint.

**Owned paths:** `.gitignore`, `workflow_monitor/`, `docs/index.md`.
Narrow ignore edits only for actual app manifests/generated outputs; preserve unrelated patterns/work.

**Checks:**
```sh
python3 -B -m unittest discover -v -s workflow_monitor/tests
npm --prefix workflow_monitor/web run build
npm --prefix workflow_monitor/web test
```
Deliver these suites/scripts; local browser/tool only, no test-side install/download.

**Required pass conditions (SC-001/003/004/005/006 core):** production mapper expected-vs-observed
inventory/IDs/typed edges, unsupported/missing records and null/zero/no-change semantics. Actual isolated
script writer/read-only reader compose without authoritative mutation or writer stall. Real browser
node/edge/details selection, run switching, pan/zoom/history reveal and stable status polls work. About2s
timing recorded without invented percentile. Host/Origin/method/path guards, safe text/private-sentinel
exclusion and actual error paths tested. No execution/control effect from viewer. App tests, dependency
locks and usable instructions accompany source. Focused checkpoint makes the actual app build inspectable
retrospectively before genuine T003 work; observer launch remains separately authorized, not a hidden gate.

## T003 — Faithful review/fix lineage, live acceptance and operating guide

**Depends:** T002. **Delivery:** genuine later work in that SAME recorded application build.

Complete explicit local correction-lineage expansion in the one graph: rejected reviewer → declared
follow-up → fixing-agent execution → checks/checkpoint → rereviewer. Source-run attribution and actual
reviewed ranges remain visible, including original failed state after linked success. Missing/conflicting
references cannot create acceptance; cycles terminate honestly. All hidden/unsupported history is reachable.

Complete composed privacy, stale/liveness/recording-gap cases and browser regressions; document delivered
setup/launch/permissions/trust/limits, correction/run context and rollback. Observe same-build retrospective
and subsequent live work under explicit operator viewer authority; no artificial busywork or demo
substitution. Include real isolated review/fix/rereview integration with labelled offline adapters plus
actual shipped engine/check/Git paths. Preserve actual build failures if any; no production fault injection.

**Owned paths:** `workflow_monitor/`, `docs/index.md`.

**Checks:** same three ordinary app/build/browser commands as T002, now with composed/full-history cases.

**Required pass conditions (SC-001–006 completion):** all revised criteria pass with actual source/readback
and browser evidence. Distinct model nodes, retained first review failure and full-range rereview must be
navigable together. Sentinels leak nowhere, viewer has zero execution/write effects, record/read/display
pairs and last-success warnings are correct. Same application run ID has retrospective T002 and live T003
observations; absent interval is NOT VERIFIED. Tests/docs verify exact delivered flags and commands.
No future final-review result is required to complete this task: after checkpoint, the runner performs
fresh independent full-range review, and operator acceptance inspects that recorded result separately.

## Handoff and verification boundaries

T001 implementation requires explicit recording/review-range approval. After it is delivered/accepted,
prepare an ordinary application task input containing T002/T003 only: remove T002's already-satisfied
T001 dependency and note the foundation checkpoint as context. Keep T003→T002. Copy matching T002/T003
safe presentation entries from `monitor-presentation.json` into root `monitor.tasks` for retained brief
details. No unsupported CLI subset flag or automatic multi-run orchestrator is assumed. See quickstart for operation.

The application's final independent review and actual same-build operator observation remain required.
Review findings require separately approved linked fixes and actual full-original-range rereview. A passing
correction-only review is labelled as such, not silently accepted. Final report maps every SC to actual
commands/evidence or FAIL/NOT VERIFIED. Historical approvals, fixtures and prior scratch setup are not
substitutes. No implementation, launch, installation, merge or push is authorized in this revision session.
