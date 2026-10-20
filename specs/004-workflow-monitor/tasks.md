# Tasks: Script-driven read-only workflow monitor

**Proposal only; implementation NOT authorized.** Direct owner-authorized revision of the existing
source, not a new Standard ceremony. [tasks.json](tasks.json) is the matching executable presentation.
Requirements truth: [spec](spec.md), [data model](data-model.md), [API](contracts/monitor-v1.md),
[validation](contracts/validation.md). Sequencing/context: [plan](plan.md), [quickstart](quickstart.md),
[research](research.md). Historical approvals do not authorize these bytes.

## Shared constraints

- Latest owner direction selects **Terra class, medium effort** for future work; no concrete provider/model
  ID was supplied. Do not invent a binding or edit active configuration. This supersedes older Sol intent
  for this proposal only. The coordinator resolves actual usable owner-approved configuration before launch.
- One existing script writer; normal hooks/signing, unrelated-work preservation, actual project checks and
  focused explicit-owned-path checkpoints. Fresh independent read-only final review remains separate.
- T001–T006 require separately authorized recording/range foundation work; accept its checkpoint BEFORE a fresh
  application run of T007–T016. No runtime edits during that app run. At T010 the viewer must be usable;
  genuine T011–T016 work then supplies later self-history in that SAME app run.
- Best-effort recording is optional to execution, not honest monitor acceptance. Warn without vetoing
  work or replacing original errors. Unknown/incomplete records stay unknown; no private transcript mining.
- Keep all revised SC-001–006, privacy/read-only/authorization protections and distinct actual reviewer →
  fixing-agent → checks/checkpoint → rereviewer nodes. Explicitly linked local corrections require separate
  approval and actual original-base→current-head rereview; no automatic fix/retry or cosmetic range label.
- No retired YAML/engine/proof/catalog/manifest/custody/receipt admission, PythonAnswer workaround,
  universal payload ceiling or repeated environment attestation. No install/network/auth/global activation,
  app/model launch, merge or push is authorized now. Tests/startup never install/download.
- Every task's description carries source-read instructions and inline REQUIRED item because root JSON
  metadata is not automatically given to workers. Owned paths are maximum mutation scope, not required edits;
  read other source freely. Tests/relevant docs accompany the outcome. No task owns the entire application.
- Commands below are future delivery checks; test modules/scripts must be delivered with the task. Use
  separately prepared environments. Local check servers/browser close normally. Missing capability/permission
  or failed/unrun REQUIRED evidence is NOT VERIFIED, never passed. Ordinary implementation checks have no
  invented manual STOP. Only actual implementation/setup/observer permissions and final acceptance apply.

## Early risk and delivery boundaries

No disposable prototype selected: actual permanent engine/check/Git/SQLite tests can observe the known
seams. Recording noninterference and true full-range review are consequential; T001–T006 prove them before
app reliance. T007 proves actual read-only/writer coexistence before HTTP exposure. Failed/invalidated
proof blocks affected reliance and returns to producing review/renewal; do not call a failed technique proven.
Residual reasoning: medium, chiefly history/lineage coverage and concurrent read/poll identity; bounded local
checks and explicit interfaces reduce long-agent compaction/drift. No per-task model/effort assignment.

## T001 — Closed additive recording storage and retained description

- [ ] T001 Closed additive recording storage and retained description
- **Depends**: none

Deliver the two additive monitoring tables, closed phase/task descriptor and safe best-effort append/read
helpers. Capture explicit public presentation, requested identity and declared correction context only;
generic labels replace invalid optional input. Retain runtime revision or unknown reason. Recorder
initialization and writes cannot veto ordinary progress.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** Existing Store progress schema; data-model minimal storage, emission optionality
and correction metadata; helpers consumed by T002–T006.

**Owned paths:** `runtime/coherence_workflow/monitoring.py`, `runtime/coherence_workflow/store.py`,
`runtime/tests/test_monitoring.py`, `docs/coordinate-implementation-schema.md`.

**Exclusions:** No engine instrumentation, review selection, private text, new dependencies, legacy conversion
or UI.

**REQUIRED T001/V1** (SC-001, SC-004, SC-005): Use actual disposable SQLite Store: old progress/legacy rows
remain unchanged, descriptor survives code/presentation changes, occurrence identity/end reuse and append
order survive reopen. Closed facts reject private sentinel/arbitrary payload; invalid optional metadata
degrades safely. Inject setup/append failure and show ordinary Store progress still succeeds, safe warnings
only. Missing registration is not fabricated history.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest -v test_monitoring
```
**Capabilities / permissions:** Prepared local Python/Git/SQLite; no install or external action.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T002 — Task, worker and terminal execution observations

- [ ] T002 Task, worker and terminal execution observations
- **Depends**: T001

Wire retained registration, preparation/manual-gate, worker and run terminal boundaries into Engine. Allocate
one identity per actual prompt call; label explicitly declared correction workers without heuristic
reclassification. Preserve interrupted/failed preparation, worker return distinct from acceptance, and
terminal failures before propagation.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T001 recorder; actual Engine.invoke and manual_gates; reviewer-specific
outcome/range is delivered by T005.

**Owned paths:** `runtime/coherence_workflow/engine.py`, `runtime/coherence_workflow/monitoring.py`,
`runtime/tests/test_engine.py`, `runtime/tests/test_monitoring.py`,
`docs/coordinate-implementation-schema.md`.

**Exclusions:** No check/checkpoint internals, answer content, automatic retry or reviewer result changes.

**REQUIRED T002/V1** (SC-001, SC-002, SC-004, SC-006): Real Engine with labelled offline adapters and
disposable Git emits preparation/gate/worker/terminal rows in observed order. Repeated calls get distinct IDs;
denied gate has no invented worker; failure/interruption remains failed/incomplete. Recorder failures at
registration/mid/end do not prevent actual worker/check/Git/default review or replace original errors.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest -v test_engine test_monitoring
```
**Capabilities / permissions:** Prepared local Python/Git/SQLite; no install or external action.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T003 — Per-check and focused-checkpoint milestones

- [ ] T003 Per-check and focused-checkpoint milestones
- **Depends**: T002

Instrument each actual runner command and focused checkpoint boundary, including failure before raise,
interruption, no requested checks, no-change and uncertain Git failure. Preserve existing runner ownership,
command cancellation and check semantics.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T002 engine occurrence context; run_checks and FocusedGit.checkpoint results; no
git_effects behavior change.

**Owned paths:** `runtime/coherence_workflow/verification.py`, `runtime/coherence_workflow/engine.py`,
`runtime/coherence_workflow/monitoring.py`, `runtime/tests/test_verification.py`,
`runtime/tests/test_engine.py`, `docs/coordinate-implementation-schema.md`.

**Exclusions:** No raw commands/output/paths, receipt protocol, invented success, check deadlines or Git repair.

**REQUIRED T003/V1** (SC-002, SC-004, SC-005, SC-006): Actual successful/failing subprocess checks and
disposable Git checkpoint/no-change produce start/outcome rows with correct ordinal/exit/base/head/no_change.
Failed command is durable before exception; uncertain checkpoint is not a commit claim. Inject recorder
exceptions and prove original check/Git outcomes and errors unchanged; no-check is not verified-check success.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest -v test_verification test_engine
```
**Capabilities / permissions:** Prepared local Python/Git/SQLite; no install or external action.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T004 — Coarse owner-question delivery observations

- [ ] T004 Coarse owner-question delivery observations
- **Depends**: T002

Wrap manual-gate and SDK questions with parent occurrence references; distinguish requested, terminal answer
returned, host answer sent and delivery failure. Preserve ordinary interactive/noninteractive behavior.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T002 gate/worker identity; actual PiAdapter question callback and stdin send
boundaries; test_host.mjs regression.

**Owned paths:** `runtime/coherence_workflow/pi_adapter.py`, `runtime/coherence_workflow/engine.py`,
`runtime/coherence_workflow/monitoring.py`, `runtime/tests/test_pi_adapter.py`,
`runtime/tests/test_engine.py`, `docs/coordinate-implementation-schema.md`.

**Exclusions:** No question/answer text, mailbox, consumed claim, SDK stream mining or host protocol rewrite.

**REQUIRED T004/V1** (SC-002, SC-004, SC-005): Exercise real PiAdapter framed transport with labelled local
fake host and terminal callback: requested/returned/sent/failure states link to gate or model execution
correctly. Noninteractive refusal and broken send do not claim delivery/consumption. Synthetic private content
enters no rows/warnings; callback recorder failure cannot block actual answer send or replace its error.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest -v test_pi_adapter test_engine
node --test runtime/tests/test_host.mjs
```
**Capabilities / permissions:** Prepared Python/Node and local fake transport; no live provider or interactive
approval simulation claimed.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T005 — Actual original-range independent review and review observations

- [ ] T005 Actual original-range independent review and review observations
- **Depends**: T003, T004

Add optional review_base to the actual independent review diff/prompt. Resolve normal Git commit and require
ancestor of run baseline; reject invalid/unrelated range at affected review. Record distinct reviewer
occurrence, actual base/head, parsed approval/finding count or malformed/interrupted outcome before raise.
Default review/run baseline/ownership remain unchanged.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T003 checkpoint head, T004 reviewer question support; data-model review coverage
contract; Engine currently uses run baseline.

**Owned paths:** `runtime/coherence_workflow/engine.py`, `runtime/coherence_workflow/monitoring.py`,
`runtime/tests/test_engine.py`, `runtime/tests/test_monitoring.py`, `docs/coordinate-implementation.md`,
`docs/coordinate-implementation-schema.md`.

**Exclusions:** No auto-fix/retry, supplied reviewer verdict, full finding ledger, default range change or
telemetry admission gate.

**REQUIRED T005/V1** (SC-002, SC-004, SC-006): Run actual isolated Engine/check/Git original rejection then
separately declared local fixing run using labelled offline adapters. Inspect distinct
reviewer/fixing-worker/rereviewer calls and DB rows; rereviewer prompt/diff really contains
original-base→new-head including original commits. Original remains failed. Default prompt unchanged;
invalid/nonancestor base fails review without rewriting work. Malformed/rejected response retains honest
outcome, no private findings; recorder failure does not alter review.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest -v test_engine test_monitoring
```
**Capabilities / permissions:** Prepared local Python/Git/SQLite; no install or external action.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T006 — Script recording identity lookup and explicit abandon history

- [ ] T006 Script recording identity lookup and explicit abandon history
- **Depends**: T005

Extend actual status/history to expose recording occurrence IDs and safe recorded review ranges for operator
correction references; preserve ordinary progress/legacy interfaces. Append explicit abandon observation for
registered new runs without erasing prior failure. Complete foundation operating/schema guide and validate
composed recording seam before the app run.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T001–T005 implemented recorder and review range; existing CLI
status/history/abandon. Script output is not browser DTO.

**Owned paths:** `runtime/coherence_workflow/cli.py`, `runtime/coherence_workflow/store.py`,
`runtime/coherence_workflow/monitoring.py`, `runtime/tests/test_cli.py`, `runtime/tests/test_recovery.py`,
`runtime/tests/test_monitoring.py`, `docs/coordinate-implementation.md`,
`docs/coordinate-implementation-schema.md`.

**Exclusions:** No browser API, old-run mutation/adaptation, automatic abandon, new task linter rules or
transcripts.

**REQUIRED T006/V1** (SC-001, SC-002, SC-004, SC-005, SC-006): Actual CLI lookup returns the emitted review
occurrence ID used to resolve a declared correction; abandon retains prior observations and actual failure.
Absent/corrupt monitoring remains unknown, recorder failure does not veto abandon. Full runtime/host
regression checks pass with no legacy row rewrite. Docs flags/examples match actual CLI and expose recording
version/occurrence IDs; docs identify the separate post-checkpoint foundation acceptance boundary before app
build.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -B -m unittest discover -v -s runtime/tests
node --test runtime/tests/test_host.mjs
```
**Capabilities / permissions:** Prepared local Python/Node/Git/SQLite and local fake SDK transport; no
install, live provider or external action.

**Verification effort:** Focused local seam tests; full related suite only at this integration boundary.

**Delivery note:** Foundation completion gate: separately review/accept recording and review_base
implementation before approving the fresh app run; no future app acceptance is a check here. Full runtime
suite is justified by cross-cutting Engine/Store/adapter changes.

## T007 — Worktree-scoped read-only SQLite snapshot reader

- [ ] T007 Worktree-scoped read-only SQLite snapshot reader
- **Depends**: T006

Deliver app Python manifest/lock and fixed-worktree reader using short thread-owned snapshots, parameterized
explicit SELECT columns, mode=ro/query_only/SELECT authorizer and normal SQLite locking. Bind canonical
Git-admin/database identity and safe ownership; recheck on reopen/substitution. Read only new supported
recording-contract runs, retain unavailable/unsupported states.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** Accepted T006 recording version/checkpoint; data-model tables and API reader
boundary; no runtime writer imports.

**Owned paths:** `workflow_monitor/pyproject.toml`, `workflow_monitor/requirements.lock`,
`workflow_monitor/__init__.py`, `workflow_monitor/reader.py`, `workflow_monitor/tests/__init__.py`,
`workflow_monitor/tests/test_reader.py`, `workflow_monitor/README.md`.

**Exclusions:** No Authority/Store/SDK imports, DDL/ATTACH/extensions/write pragma, immutable/nolock, copied
main DB, legacy fallback or process signalling.

**REQUIRED T007/V1** (SC-004, SC-005, SC-006): Actual T006-compatible isolated database read sees WAL updates
and preserves authoritative rows; actual script writer progresses while reader opens/closes snapshots. Attempt
forbidden SQL, symlink/ownership/cross-worktree substitution and missing store/version cases; safely reject or
report closed unavailable state without creating/mutating DB. Compare authoritative rows at quiescent points,
not active database bytes.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
python3 -B -m unittest -v workflow_monitor.tests.test_reader
```
**Capabilities / permissions:** Accepted foundation; prepared Python/SQLite and separately authorized
manifest/lock resolution if needed; no install from tests.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T008 — Faithful graph mapping and minimized public identities

- [ ] T008 Faithful graph mapping and minimized public identities
- **Depends**: T007

Deliver production mapper and closed public DTO construction for phase anchors, tasks/prerequisites, all
occurrences/model roles, typed edges, milestones and inventory. Include opaque scoped refs, validated hashes,
safe optional brief text and honest incomplete/unsupported/unknown states. No raw-row serialization.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T007 snapshot rows; data model graph/public identity and monitor-v1 DTO schema;
followup expansion comes in T013.

**Owned paths:** `workflow_monitor/mapping.py`, `workflow_monitor/public.py`,
`workflow_monitor/tests/test_mapping.py`, `workflow_monitor/tests/test_public.py`,
`workflow_monitor/README.md`.

**Exclusions:** No SQL/control routes, private description/error fallback, inferred causal execution or
correction heuristics.

**REQUIRED T008/V1** (SC-001, SC-002, SC-004, SC-005): Feed actual emitted T006-compatible records and focused
fixtures through actual mapper/minimizer. Compare complete phase/occurrence/observation IDs/counts and edge
types including repeats/run-level/unvisited/unknown records. Zero/null/no-change/question sent/requested
identity remain distinct; unsupported payload/name and synthetic private sentinel never appear. Scope opaque
refs so another run cannot address records; retained first failure stays red after success.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
python3 -B -m unittest -v workflow_monitor.tests.test_mapping workflow_monitor.tests.test_public
```
**Capabilities / permissions:** Prepared local Python/Git/SQLite; no install or external action.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T009 — Guarded loopback production HTTP and local launch

- [ ] T009 Guarded loopback production HTTP and local launch
- **Depends**: T008

Deliver Starlette/Uvicorn closed GET snapshot/run/history/details routes and initial trusted python -m
workflow_monitor launcher serving fixed production assets. Enforce numeric loopback, exact Host/port, API
same-origin headers/Fetch Metadata, no CORS/control methods, safe errors/logs and CSP. Add narrowly needed
manifest/output ignore rules.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T007 reader/T008 public DTO; monitor-v1 routes/assets/errors; followups route
remains unavailable until T013, no invented lineage.

**Owned paths:** `workflow_monitor/app.py`, `workflow_monitor/__main__.py`, `workflow_monitor/pyproject.toml`,
`workflow_monitor/requirements.lock`, `workflow_monitor/tests/test_http.py`,
`workflow_monitor/tests/test_launch.py`, `workflow_monitor/README.md`, `.gitignore`, `docs/index.md`.

**Exclusions:** No dev server/reload/proxy/debug, raw file routes, writer SDK imports,
install/build-at-startup, external bind or automatic observer launch.

**REQUIRED T009/V1** (SC-004, SC-005): Actual local HTTP/CLI tests with controlled assets exercise allowed
reads and denied Host/Origin/method/traversal/symlink/sourcemap/raw-ref paths, all response/header/log
surfaces including actual500. Sentinels never escape; exact closed error codes and no-store/CSP protections
hold. Viewer startup creates no store, invokes no runner and performs no builds/installs; README/help flags
agree.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
python3 -B -m unittest -v workflow_monitor.tests.test_http workflow_monitor.tests.test_launch
```
**Capabilities / permissions:** Prepared locked Python web dependencies; local test servers only and normal
teardown; dependency/network setup separately authorized.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T010 — Early usable selected-run browser graph

- [ ] T010 Early usable selected-run browser graph
- **Depends**: T009

Deliver conventional web manifest/lock, React/React Flow production UI with left run selector, one graph,
brief node/edge details, typed edge legend, pan/zoom and simple polling. Distinct worker/reviewer nodes and
all existing inventory/history are accessible, not just task status. Deliver usable build/launch instructions
now, so an independently owned observer can inspect this very app run before T011–T016.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T009 production HTTP/CLI + T008 DTO. Initial history can be fully loaded;
inventory must disclose/offer existing page retrieval, no silent omission. Later T012 improves history
navigation.

**Owned paths:** `workflow_monitor/web/package.json`, `workflow_monitor/web/package-lock.json`,
`workflow_monitor/web/index.html`, `workflow_monitor/web/vite.config.ts`,
`workflow_monitor/web/tsconfig.json`, `workflow_monitor/web/src/`, `workflow_monitor/web/tests/`,
`workflow_monitor/web/playwright.config.ts`, `workflow_monitor/README.md`.

**Exclusions:** No lineage inferred from name/time, editing/control affordances, CDN/HTML execution, browser
install/download or same-build evidence claimed from fixtures.

**REQUIRED T010/V1** (SC-001, SC-003, SC-004, SC-005, SC-006): Build production assets and use actual
installed local browser against production HTTP: switch same-spec runs, select real DOM nodes/edges/details,
pan/zoom and reach every current inventory record. Compare distinct model nodes/ranges and retained failures
with DB. Malicious labels remain inert. Poll actual isolated writer and retain record/read/display timing
normally about2s, deviations explicit. Usable README command opens this app; this check does not require
future live work or final review.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
npm --prefix workflow_monitor/web run build
npm --prefix workflow_monitor/web test
```
**Capabilities / permissions:** Prepared Node/web dependencies/local browser and T009 server environment;
setup and independent operator observer launch need separate permission. No test-side downloads.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

**Delivery note:** Early usable checkpoint. After it, an explicitly authorized independent observer can remain
open while genuinely later tasks execute in the SAME application run; observation is not a task execution
gate.

## T011 — Stable live graph navigation and organized layout

- [ ] T011 Stable live graph navigation and organized layout
- **Depends**: T010

Add organized local ELK layout and generation-safe polling/run switching. Preserve IDs, selection, viewport
and positions on status-only updates; topology changes can be organized without changing semantic
endpoints/types. Discard old-run fetch/layout completions.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T010 usable graph and polls; research React Flow/ELK guidance, monitor UI
invariants.

**Owned paths:** `workflow_monitor/web/src/`, `workflow_monitor/web/tests/test_navigation.spec.ts`,
`workflow_monitor/web/package.json`, `workflow_monitor/web/package-lock.json`, `workflow_monitor/README.md`.

**Exclusions:** No edge semantic rewriting, remote layout/telemetry or extra execution effects.

**REQUIRED T011/V1** (SC-001, SC-003, SC-005): Real browser selects node/edge, pans/zooms, polls changed
status and switches runs while old responses/layout finish. Assert selected identity/viewport/unchanged
positions survive and stale generations cannot replace new root. Organize changes coordinates only;
loops/typed edges/model nodes remain complete. Assets/worker remain local and navigation has no write/control
requests.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
npm --prefix workflow_monitor/web run build
npm --prefix workflow_monitor/web test
```
**Capabilities / permissions:** Prepared locked web build and local browser; local servers closed normally.
Optional broad runtime regression is not required for UI-only change.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T012 — Complete snapshot-bound history navigation

- [ ] T012 Complete snapshot-bound history navigation
- **Depends**: T011

Deliver incremental history browsing/reveal and detail lookup at a consistent watermark, with inventory
loaded/hidden/unsupported counts and accessible collapsed failure/wait badges. Add expiry/conflict refresh
behavior without mixing old/new snapshot pages or silently dropping records.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T007–T010 existing snapshot/history routes and complete baseline inventory; T011
stable selections.

**Owned paths:** `workflow_monitor/reader.py`, `workflow_monitor/mapping.py`, `workflow_monitor/public.py`,
`workflow_monitor/app.py`, `workflow_monitor/tests/test_history.py`, `workflow_monitor/web/src/`,
`workflow_monitor/web/tests/test_history.spec.ts`, `workflow_monitor/README.md`.

**Exclusions:** No fixed universal byte cap, whole-store merge, payload exposure, fake executed branches or
inaccessible hidden model nodes.

**REQUIRED T012/V1** (SC-001, SC-002, SC-004, SC-005): Actual DB plus browser with multi-page
repeated/failed/unsupported observations: total/loaded/hidden counts reconcile and every retained item is
revealable with correct details/identity. Append while paging; pages either keep original watermark or
explicitly refresh on409, never mix. Collapse retains distinct discoverable model executions/failure badges.
Corrupt cursor/other-run detail is safely rejected; no private text leaks.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
python3 -B -m unittest -v workflow_monitor.tests.test_history
npm --prefix workflow_monitor/web run build
npm --prefix workflow_monitor/web test
```
**Capabilities / permissions:** Prepared Python/Git/SQLite, locked web dependencies and installed local
browser; local servers use normal teardown. No install/download or external action.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T013 — Explicit local correction resolution and range acceptance

- [ ] T013 Explicit local correction resolution and range acceptance
- **Depends**: T012

Deliver bounded local ancestor/descendant correction traversal, followups endpoint and review-coverage
summaries. Resolve only explicit supported reviewer references with cycle detection/source-run attribution.
Full-range acceptance requires an actual approving findings-free independent review covering original base
through displayed current head; newer linked work/incomplete review invalidates current acceptance, not
historical success.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T005 actual review range, T006 raw ID lookup, T012 snapshot/paging; monitor-v1
followups route/data-model correction rules.

**Owned paths:** `workflow_monitor/reader.py`, `workflow_monitor/lineage.py`, `workflow_monitor/mapping.py`,
`workflow_monitor/public.py`, `workflow_monitor/app.py`, `workflow_monitor/tests/test_lineage.py`,
`workflow_monitor/README.md`.

**Exclusions:** No automatic fixing, cross-worktree search, authorization by link, ancestry/name/time
inference or correction-only acceptance.

**REQUIRED T013/V1** (SC-001, SC-002, SC-004, SC-005, SC-006): Real isolated shipped Engine/check/Git original
rejected review and separately declared fixing run/rereview with labelled offline adapters flow through
production reader/mapper/HTTP. Assert original failed state retained; distinct calls/rows, source runs and
actual full-original-range prompt/records. Test dangling/wrong-worktree/conflicting/cyclic refs and later
linked changes: bounded unresolved/unknown, never fabricated acceptance; correction-only range labelled
honestly. Sentinels withheld.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
python3 -B -m unittest -v workflow_monitor.tests.test_lineage
```
**Capabilities / permissions:** Prepared local Python/Git/SQLite; no install or external action.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T014 — Navigable reviewer–fixing-agent–rereviewer lineage

- [ ] T014 Navigable reviewer–fixing-agent–rereviewer lineage
- **Depends**: T013

Expand explicit followups within the one selected-root graph, showing original reviewer, declared relation,
distinct fixing-agent execution, checks/checkpoint and subsequent reviewer with source-run badges and actual
ranges. Preserve original failures and historical review success independently of current lineage acceptance.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T013 minimized followup graph and acceptance; T011–T012 stable selection/history.
Root is never replaced by a merged project graph.

**Owned paths:** `workflow_monitor/web/src/`, `workflow_monitor/web/tests/test_lineage.spec.ts`,
`workflow_monitor/README.md`.

**Exclusions:** No launch/fix controls, heuristic relations, hidden first rejection or green task completion
equated with final acceptance.

**REQUIRED T014/V1** (SC-001, SC-002, SC-004, SC-005): Actual browser loads production emitted isolated linked
histories from T013 fixture setup, navigates first rejection→fixing model→checks/checkpoint→rereviewer with
all source refs/ranges. Assert original remains failed after full-range success; correction-only, unresolved
and cyclic lineages cannot display accepted current head. All hidden/unsupported records remain reachable and
separate model executions survive collapse.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
npm --prefix workflow_monitor/web run build
npm --prefix workflow_monitor/web test
```
**Capabilities / permissions:** Prepared Python/Git/SQLite, locked web dependencies and installed local
browser; local servers use normal teardown. No install/download or external action.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T015 — Honest runner liveness and resilient read recovery

- [ ] T015 Honest runner liveness and resilient read recovery
- **Depends**: T014

Add read-only local recorded-process identity liveness, explicit read/last-success/last-recorded time,
stopped/unknown qualification and recoverable unavailable/incomplete warnings. Preserve last sanitized view on
failed reads and correctly refresh after recovery; recording gaps never trigger repair.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T007 recorded identity/private reader and T014 graph; data-model
unknowns/liveness; never import runtime processes/controller.

**Owned paths:** `workflow_monitor/reader.py`, `workflow_monitor/liveness.py`, `workflow_monitor/public.py`,
`workflow_monitor/app.py`, `workflow_monitor/tests/test_observation.py`, `workflow_monitor/web/src/`,
`workflow_monitor/web/tests/test_observation.spec.ts`, `workflow_monitor/README.md`.

**Exclusions:** No signal/lock/reconcile, guessed heartbeat, process-alive means progress, private error
display or reconstructed missing events.

**REQUIRED T015/V1** (SC-003, SC-004, SC-005, SC-006): Actual concurrent isolated script writer/reader/browser
shows record/read/display timing normally about2s (retain deviations). Force read failure/stale response,
process exit/unverifiable identity, missing end and recording gap; assert last safe view/last-success and
incomplete/live/stopped/unknown remain distinct, no mutation or writer stall. Test zero vs unknown and no
durable gap marker; scan all HTTP/browser/log surfaces for synthetic private sentinels.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
python3 -B -m unittest -v workflow_monitor.tests.test_observation
npm --prefix workflow_monitor/web run build
npm --prefix workflow_monitor/web test
```
**Capabilities / permissions:** Prepared Python/Git/SQLite, locked web dependencies and installed local
browser; local servers use normal teardown. No install/download or external action.

**Verification effort:** Focused local seam tests; no broad unrelated regression required; optional broader
checks are nonblocking.

## T016 — Shippable local package and same-build operating acceptance

- [ ] T016 Shippable local package and same-build operating acceptance
- **Depends**: T015

Finish reproducible production package/resource discovery and actionable safe launch diagnostics using
existing manifests/locks and local assets. Deliver actual setup/launch/trust/permissions/correction
lookup/rollback operating guide and docs routing. Exercise delivered build-to-serve interface and finish
same-build retrospective/live acceptance using genuine later T011–T016 work, never synthetic busywork.

**Read first:** specs/004-workflow-monitor/tasks.md Shared constraints and this task entry, spec.md (FR/SC),
data-model.md, contracts/monitor-v1.md and contracts/validation.md; paths are relative to
specs/004-workflow-monitor unless repository-root paths are given. Read predecessor interfaces/tests and
relevant actual source before relying on them. Root JSON context is not handed to the worker.

**Interfaces/predecessors:** T009 launcher/T010 usable checkpoint and T011–T015 later genuine work; quickstart
and validation SC006. Final reviewer executes only AFTER this checkpoint.

**Owned paths:** `workflow_monitor/pyproject.toml`, `workflow_monitor/requirements.lock`,
`workflow_monitor/__main__.py`, `workflow_monitor/app.py`, `workflow_monitor/tests/test_launch.py`,
`workflow_monitor/tests/test_delivery.py`, `workflow_monitor/README.md`, `docs/index.md`.

**Exclusions:** No setup at startup, hidden installs, external bind, task-owned daemon left alive, final
review as task predecessor, demo replacement, runtime edits or global config.

**REQUIRED T016/V1** (SC-001, SC-002, SC-003, SC-004, SC-005, SC-006): Actual production build/local package
launch from documented command serves locked local assets, rejects missing/unsafe assets with safe actionable
diagnostics and performs no install/build/runtime control. Docs/help/route tests agree, viewer stop leaves
authoritative rows/Git/writer intact. Full focused app/build/browser checks pass; compare docs to delivered
interfaces. Under separately explicit operator authority retain SAME app run ID with retrospective T010 and
genuine later live T011–T016 interval/timing; absent interval is SC006 NOT VERIFIED, not passed. No future
final-review success is required here.

**Checks / evidence:** Actual output plus the bounded assertions above (offline adapters labelled).
```sh
python3 -B -m unittest discover -v -s workflow_monitor/tests
npm --prefix workflow_monitor/web run build
npm --prefix workflow_monitor/web test
```
**Capabilities / permissions:** Prepared locked Python/Node/local browser; separately authorized operator
observer launch and actual approved app SDK run. Missing observation/permission is NOT VERIFIED, not an
optional-recording execution veto.

**Verification effort:** Focused local seam tests; full related suite only at this integration boundary.

**Delivery note:** Full app suite is proportionate here because packaging serves all graph/privacy boundaries.
Fresh independent full-application-range final review and inspection of its recorded outcome follow this task
checkpoint, distinct from task completion.

## Mapping and prepared split-run handoff

| Previous coarse task | Bounded replacement | Boundary |
| --- | --- | --- |
| old T001 | T001–T006 | Storage, execution boundaries, check/Git, questions, actual review range, operator lookup/abandon. |
| old T002 | T007–T010 | Reader, mapper/minimization, production HTTP, early usable browser. |
| old T003 | T011–T016 | Stable layout/polls, history reveal, resolved lineage, lineage graph, liveness/recovery, production delivery/own-build acceptance. |

Prepare ordinary JSON inputs after current-content review/implementation approval (no subset CLI flag):
foundation = T001–T006; application = T007–T016. In app input remove ONLY T007→T006 as already satisfied,
retain all internal dependencies and task-local read instructions/REQUIRED items/owned paths/checks. Put
accepted foundation SHA/recording version in T007 description, not merely root context. Copy matching safe
presentation entries from [monitor-presentation.json](monitor-presentation.json) to root `monitor.tasks`.
No automatic launch or executor resolution. `scripts/coordinate-implementation intake --tasks FILE`
validates only; `start` is not authorized here. Final independent review follows T016, covering the full app
baseline→head; operator inspects its actual recorded outcome afterward. Findings require separately approved
linked fixes with original-range review, never correction-only acceptance. Historical failures stay visible.

SC006 operator acceptance needs the same actual app run ID: retrospectively inspect T007–T010, observe
later genuine T011–T016 work, retain safe occurrence/time references and timing. T010 requires only its
already achievable usable-viewer check, not future observation. If observer permission/interval is missing,
SC006 remains NOT VERIFIED; seek explicit acceptance decision before replacement demonstration. No artificial
pauses/tasks/faults. Recording failure never becomes an execution veto. Final review is not a task check.

## Revision validation and approval state

This revision targets baseline `66070858dd6e9956c992f4d9a0820b868647a9f8`. Revision checks PASS: Python
3.12.3; both task-order validators;
actual runtime `intake` (16 tasks); exact nonempty Markdown/JSON ID/outcome/dependency parity; prepared
6-task foundation and 10-task application intake; 107 local links; `git diff --check`; five protected
historical files byte-identical; stories/FR/SC/reconciliation byte-unchanged. Current content is identified by
that commit and Git blob IDs; report holds actual command results. Source SC meanings unchanged; historical
approval/prerequisite/review bytes preserved. No application/runtime acceptance or implementation approval
is claimed. Any missing/weakened REQUIRED contract returns to producing review before dispatch.
