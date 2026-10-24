# One workflow monitor for multiple projects — implementation tasks

## Source and executor

Requirements truth: [TinySpec](workflow-monitor-multiproject-tinyspec.md), acceptance A1–A6.
Source SHA256: `3d8df9845dc95bcb4108f23bdffa2b66d12cf157a35d74e038ce9322db083f84`;
source commit: `fd89605ef268557f6a9b1fcbf6d388a7e77f7030`.
Actual task-write baseline: `4623280e55d119cd6a18ee68e11737f276d37124` (concurrent
planner checkpoint inspected; source and task-owned paths unchanged).
Independent intent review: `/tmp/workflow-monitor-multiproject-intent-review.md`, ZERO findings;
source identity verified before drafting. This path is session evidence, not a durable task prerequisite.

The producer read [selected executor](../../.pi/workflow-executor.json):
`openai-codex/gpt-5.6-terra`, medium workers; `openai-codex/gpt-6.1-sol`, medium reviewers.
Saved task-producer Sol/medium binding is unchanged and is not an implementation assignment.
The [executable JSON](workflow-monitor-multiproject-tasks.json) carries inline worker context,
REQUIRED mappings, owned paths and actual command strings consumed by the runner.

## Shared worker brief

Original constraint (verbatim):
> Do not make any modification in how the website actually shows the workflow, this is just a modification to be able to run just one server and monitor all projects

Immediate children only; no backwards compatibility. Preserve graph/layout, Details, labels,
metrics, status/acceptance, inventory ordering/filtering, followups, pagination, freshness and
60-second polling. Add selection/reset behavior only. Keep read-only numeric-loopback service,
closed DTOs/errors, fixed startup assets and canonical worktree/admin/store/metric identity.
Browser inputs select discovered opaque references, never paths. No writer/runtime/schema,
store creation/mutation, migration/backfill, workflow control, aggregate view, recursive search,
watchers, dependencies/frameworks, automatic setup/install/build/deployment or old CLI/URL layer.
Explicit verification build commands below build only prepared test assets, not on launch.

[ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md): executable
instructions stay neutral and consume current launch authority, not historical phase wording.
[ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md): small isolated Git/store
fixtures and numeric-loopback test servers need no routine reapproval, but do not affect unrelated
services/data. Prepared Python/Node packages/local Chrome are required; missing prerequisites are
NOT RUN, never installed automatically or waived. No paid/provider calls, deployment or push.
Memory association: whole [memory index](../../memory/MEMORY.md) read; its only guidance is to
avoid parent wakeups for routine transitions. No technical gotchas apply and no memory write occurs.

Only task-owned paths may change for the stated outcome; shared README/test files are serially
owned through dependencies, not permission for unrelated edits. Relevant existing fixtures may
adapt constructors/URLs without retaining legacy support or weakening meaningful assertions.
Check commands run from repository root, using the prepared `workflow_monitor/.venv/bin/python`.
Keep tests/docs/teardown with delivery; report concrete observations, actual command output and
missing prerequisites. A failed isolation/safety/composed proof blocks affected reliance; correct
within scope or return material changes for affected review rather than weakening acceptance.
Focused checkpoints and fresh independent full-range final implementation review use the existing
[task-commit contract](../../skills/memory-handling/references/task-commit-contract.md).

## Boundaries and ordering

`T001 → T002 → T003 → T004 → T005`.
Registry identity/lifetime is a standalone actual-helper prerequisite. Scoped HTTP isolates all
existing run operations as one reused transport contract. Launcher is separately testable from
browser work. T004 delivers project-aware navigation/reset and composed two-project acceptance
at the first usable browser boundary; T005 delivers independently observable dynamic discovery
and unavailable-selection transitions, not a tests-only milestone. Serial dependencies also avoid
ambiguous shared README/fixture edits. These bounded interfaces keep Terra/medium from carrying
registry, backend and UI unfinished at once. No prototype is justified: permanent real-helper
proof suffices; dangerous stale A-as-B display is additionally tested in the composed browser.
No new infrastructure, exhaustive matrix, universal limits or routine manual approval gates.

## Tasks

- [ ] T001 Discover and retain safe immediate-child project bindings
  - **Depends**: None
  - **Outcome**: Deliver workflow_monitor/projects.py: validate/expand/resolve a configured projects root without creating it; discover only regular nonsymlink immediate children that are canonical Git worktree roots, including linked worktrees. Reuse existing Reader/Git verification rather than duplicate its safety rules. Expose a small registry contract consumed by T002/T003: refreshing inventory produces deterministic label-sorted closed {ref,label} entries; opaque URL-safe refs remain stable for the same canonical child across polls/restart; resolving a discovered ref returns its retained project entry/Reader or a closed unknown/unavailable result. Retain Readers, including initial no-store bindings and unsafe/unreadable candidate qualification, rather than sharing/recreating them on refresh. Keep qualifying projects with unavailable stores listed and isolate candidate failures. Inventory refresh must not read every store snapshot. Revalidate directory/worktree/admin identity before addressed use; removed/replaced/retargeted bindings must not be silently rebound, including remove/recreate across inventory refresh. Root read errors are unavailable, not authoritative empty inventory. Add permanent actual-helper tests with tiny real Git roots/linked worktrees, not directory-list mocks as sole proof. Document discovery, binding lifetime and unavailable/empty semantics in canonical README. Exclude HTTP, launcher and browser changes; Reader internals remain unchanged.
  - **Owned paths**: `workflow_monitor/projects.py`, `workflow_monitor/tests/test_projects.py`, `workflow_monitor/README.md`
  - **Checks**:
    - `PYTHONPATH=runtime:runtime/tests workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_projects workflow_monitor.tests.test_reader`
  - **REQUIRED T001/V1** (A2; A5): Actual discovery includes canonical immediate roots, a linked worktree and no-store project; excludes nonprojects, deeper nested repositories and symlink children. Inventory is label-sorted with stable opaque refs across refresh/new registry; add/remove is observed on next refresh. Invalid/missing/unreadable/non-directory root has an actionable --projects-root diagnostic; empty root succeeds; root-read error is distinguishable from empty. **Evidence:** Permanent test_projects assertions using real temporary filesystem/Git worktrees; capture command output and example closed inventory.
  - **REQUIRED T001/V2** (A2; A3; A5): Same child retains the same Reader across polls; no-store -> first legitimate store is readable by that Reader. Unsafe/unreadable child does not block healthy inventory/use. Removal/replacement/admin retarget cannot adopt successor data or reset pinned store/metric boundaries, including across disappearance/reappearance; no arbitrary input path resolution or observation writes. **Evidence:** Actual-helper identity/failure/no-store tests plus unchanged Reader safety regressions; compare fixture DB/metric bytes and absence of newly created .coherence for no-store observation.
  - **Permissions**: Bounded isolated fixtures/databases and numeric-loopback test servers allowed under ADR-0004; prepared dependencies only, no setup/install, paid/provider calls, deployment, unrelated data/service changes or routine verification reapproval.

- [ ] T002 Serve isolated project-scoped read-only HTTP contracts
  - **Depends**: T001
  - **Outcome**: Consume T001 registry resolution/lifetime contract. Change create_app to consume registry rather than one Reader; move last-safe sanitized result and last-success timestamp into each retained project entry/observation state. Resolve project before every existing run operation and reuse normalization/minimization/execution qualification/paging/followups unchanged. Add GET /api/monitor/v1/projects returning {monitor_version:1,projects:[{ref,label}]}, refreshed per request; implement /api/monitor/v1/projects/{project_ref}/runs and existing /{run_ref}/snapshot, /history, /records/{record_ref}, /followups suffixes with unchanged query semantics. No-store/valid empty-store inventory returns no runs without store creation; unsupported/unreadable stays honest and isolated. Implement only browser shells /, /projects/{project_ref}, /projects/{project_ref}/runs/id-<percent-encoded actual run ID>. Validate raw shell structure/components before routing decode; run ID decoding stays exactly once. APIs/malformed paths/unknown assets must never get HTML fallback; remove old unscoped routes, not implicit selection. Preserve fixed asset inventory and all request/response protections. Adapt existing Python create_app callers and scoped fixture URLs with this interface change, including the execution_fixture.py app binding (browser test URL adaptation remains T004) and inherited HTTP presentation/history/lineage/observation tests; retain their meaningful assertions. Use registry injection only for existing targeted flaky-reader tests, not as sole two-project isolation proof. Add actual registry/Reader/two-store HTTP tests with colliding identities, distinguishable facts and failed-read last-safe freshness. Document new HTTP/shell/security/rollback contract in README. Exclude launcher and browser changes.
  - **Owned paths**: `workflow_monitor/app.py`, `workflow_monitor/projects.py`, `workflow_monitor/tests/test_projects.py`, `workflow_monitor/tests/test_http.py`, `workflow_monitor/tests/test_reader.py`, `workflow_monitor/tests/test_chain_mapping.py`, `workflow_monitor/tests/test_execution_presentation.py`, `workflow_monitor/tests/test_history.py`, `workflow_monitor/tests/test_lineage.py`, `workflow_monitor/tests/test_observation.py`, `workflow_monitor/tests/test_delivery.py`, `workflow_monitor/web/tests/execution_fixture.py`, `workflow_monitor/README.md`
  - **Checks**:
    - `PYTHONPATH=runtime:runtime/tests workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_projects workflow_monitor.tests.test_http workflow_monitor.tests.test_reader workflow_monitor.tests.test_chain_mapping workflow_monitor.tests.test_execution_presentation workflow_monitor.tests.test_history workflow_monitor.tests.test_lineage workflow_monitor.tests.test_observation workflow_monitor.tests.test_delivery`
  - **REQUIRED T002/V1** (A2; A3; A6): Actual HTTP inventory refresh uses registry and discloses only version/ref/label. Two real project stores with identical run IDs/refs (and representative matching record/token identities) remain isolated in runs/snapshot, paged history, record and followup lookup. Failure after success retains only addressed project sanitized data/last-success/warning; unsupported/unreadable other project cannot break healthy project. Retained no-store Reader sees first store on later request. Inventory requests do not scan all project snapshots. **Evidence:** Permanent registry/HTTP tests over actual Readers and distinguishable DB/metric facts, asserting representative per-endpoint facts and freshness values; output identifies these cases, not merely generic green.
  - **REQUIRED T002/V2** (A5; A6): Scoped raw shell accepts encoded slash run ID as one component with exactly-once decode, rejects malformed encoding/extra segments/traversal; unknown project refs at the API are closed 404s and cannot open paths/another project; structurally valid unknown-project browser shells remain available for the client to show the addressed unavailable state. Old unscoped API/run shells do not select a project. Root/project/run shells serve only fixed index; API/unknown assets are not HTML. Existing Host, Fetch Metadata, required header, closed error/DTO, response protections and asset-substitution assertions remain effective; removed/replaced binding is not adopted and observation leaves DB/metrics unchanged. **Evidence:** Adapted focused HTTP raw-path (including real server where needed), boundary and read-only tests; inspect response keys/errors for no absolute paths/Git internals/raw discovery errors, plus byte comparisons of observed fixture data.
  - **Permissions**: Bounded isolated fixtures/databases and numeric-loopback test servers allowed under ADR-0004; prepared dependencies only, no setup/install, paid/provider calls, deployment, unrelated data/service changes or routine verification reapproval.

- [ ] T003 Launch one root-configured server outside monitored projects
  - **Depends**: T002
  - **Outcome**: Consume T001 registry and T002 create_app contracts. Replace required --project with optional --projects-root DIRECTORY defaulting to expanded ~/projects; preserve required --assets, existing port default and all safe Uvicorn arguments. Validate invalid root before binding with actionable --projects-root correction and never create root/store. Empty valid root must launch. Preserve prepared module and declared console-entry behavior without new packaging/install machinery. Adapt actual launcher tests for default expansion, override, help/legacy rejection and safe Uvicorn arguments. Add bounded prepared-module/package subprocess from unrelated temporary cwd using prepared interpreter and absolute assets/package availability (explicit PYTHONPATH for the uninstalled module is acceptable); reach real registry/app on one numeric-loopback port with two temporary project children and verify inventory, then tear down only that child server. Update README launch examples/console equivalence, cwd-independent prepared use, defaults, root errors and no-compatibility/rollback instructions. Exclude frontend and runtime/store changes.
  - **Owned paths**: `workflow_monitor/__main__.py`, `workflow_monitor/tests/test_launch.py`, `workflow_monitor/README.md`
  - **Checks**:
    - `PYTHONPATH=runtime:runtime/tests workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_launch workflow_monitor.tests.test_delivery`
  - **REQUIRED T003/V1** (A1; A5; A6): Launcher defaults to current user expanded ~/projects, accepts override, retains assets/port options and numeric 127.0.0.1 plus existing no-reload/no-proxy/no-access-log safe options. --project is rejected. Missing/unreadable/nondirectory roots fail before bind with named actionable --projects-root diagnostic, no directory/store creation; empty valid root serves. **Evidence:** Actual launcher tests and captured --help/error output, with root/default argument assertions and Uvicorn call inspection.
  - **REQUIRED T003/V2** (A1; A6): Prepared subprocess started from unrelated cwd reaches real app/registry and returns both projects on one loopback port; no chdir into either target, no install/build-on-launch, no writer started. README commands/flags/default/cwd and stop-monitor-only rollback match delivered CLI. **Evidence:** Bounded subprocess test in test_launch using explicit prepared interpreter/absolute paths, captured inventory/exit/teardown result; README-to-help comparison. Missing prepared prerequisites are NOT RUN, not waived.
  - **Permissions**: Bounded isolated fixtures/databases and numeric-loopback test servers allowed under ADR-0004; prepared dependencies only, no setup/install, paid/provider calls, deployment, unrelated data/service changes or routine verification reapproval.

- [ ] T004 Select and navigate projects without changing the workflow viewer
  - **Depends**: T003
  - **Outcome**: Consume T002 scoped HTTP/shell contract and T003 usable launcher. Add visible project labels/selector above run list: / requests inventory and asks for selection, never guesses. Selection pushes project URL; bare project URL applies existing newest-run rule via replace when nonempty, otherwise honest empty state. Scope every run API call, followup and both normal/linked history paths; direct project/run opens, reload, Back/Forward restore exact addressed selection. Unknown/removed/unavailable project/run retains address and clears viewer rather than selecting substitute. Key all inventory/snapshot/history/layout generations by project and run (colliding run refs must still reset); project switches clear runs/filter/graph/Details/history/lineage/pending layout/measurements/positions and viewport-local selection state. Keep current within-project ordering/filtering and 60-second run/snapshot polling/status-only viewport reuse. Extend existing execution_fixture.py to real two child projects with distinguishable records and same run ID; adapt existing browser fixture setup, readiness probes and URLs to scoped contract, not compatibility. At this first usable browser boundary run composed production-asset acceptance: select/switch, direct open/reload/Back/Forward, representative Details/history/followups and delayed old-project response discarded. Preserve rendering functions, graph.ts/layout.ts and graph/Details presentation; no redesign or new harness. Update README selection/navigation/URL/state guidance. Periodic discovery and dynamic root inventory UI transitions belong to T005, not a requirement for this static-inventory outcome.
  - **Owned paths**: `workflow_monitor/web/src/main.tsx`, `workflow_monitor/web/src/style.css`, `workflow_monitor/web/tests/execution_fixture.py`, `workflow_monitor/web/tests/test_chain.spec.ts`, `workflow_monitor/web/tests/test_execution.spec.ts`, `workflow_monitor/web/tests/test_graph.spec.ts`, `workflow_monitor/web/tests/test_history.spec.ts`, `workflow_monitor/web/tests/test_lineage.spec.ts`, `workflow_monitor/web/tests/test_navigation.spec.ts`, `workflow_monitor/web/tests/test_observation.spec.ts`, `workflow_monitor/README.md`
  - **Checks**:
    - `npm --prefix workflow_monitor/web run build`
    - `npm --prefix workflow_monitor/web test -- test_navigation.spec.ts test_execution.spec.ts test_chain.spec.ts test_history.spec.ts test_lineage.spec.ts test_observation.spec.ts test_graph.spec.ts`
  - **REQUIRED T004/V1** (A4; A6): Built production browser over actual two-project registry/Reader/HTTP starts at explicit project selection, then scoped newest-run selection and exact run filtering/navigation. Colliding run IDs show distinguishable selected project data, representative unchanged graph/Details/history/followups, direct reload and Back/Forward restore exact selection. Empty/unknown/removed addresses stay honest without fallback. Delayed previous-project inventory/snapshot/history result cannot overwrite current project, including identical run refs; switching clears filter and viewer/layout/viewport-local state. **Evidence:** Extend existing navigation fixture/Playwright assertions; return composed scenario result with distinct data observed and delayed-response assertion. Existing execution/chain/history/lineage/observation renderer checks adapt routes/fixtures, retain geometry/content/status/metric semantics. No screenshot-only or mocked-API-only proof.
  - **REQUIRED T004/V2** (A4; A5; A6): Run polling remains 60000 ms and selection-preserving, with within-project status-only viewport/drag/selection behavior unchanged. All requests including linked history/followups are project-qualified and stale layout/history cannot cross project; renderer/layout algorithm/graph/Details content are unchanged. README URLs/selection match browser; no runtime/store/schema or dependency changes. **Evidence:** Build/type output and affected existing representative geometry/navigation/history/metric tests, scoped network assertions and focused diff inspection. Advance test clock instead of waiting a minute; record actual unchanged-view regression result alongside composed result.
  - **Permissions**: Bounded isolated fixtures/databases and numeric-loopback test servers allowed under ADR-0004; prepared dependencies only, no setup/install, paid/provider calls, deployment, unrelated data/service changes or routine verification reapproval.

- [ ] T005 Refresh project inventory and unavailable selections honestly
  - **Depends**: T004
  - **Outcome**: Consume T004 project-aware selection/reset/async contract and T002 refreshing inventory endpoint. Request project inventory at the existing 60-second cadence without an all-project snapshot scan or new timer framework. Add new children to selector on next successful poll; remove disappeared entries. If selected project disappears retain its scoped address, clear obsolete viewer and show project-unavailable rather than selecting another. Root discovery failure is honest unavailable/error, not authoritative empty inventory; do not let failed inventory or delayed old-project requests replace selection. Preserve run/snapshot poll cadence, within-project status-only selection/viewport behavior, initial empty-root usability and no-store -> first-store appearance without restart. Extend same bounded production fixture/test seam to change temporary child/store availability and advance clock; no watchers/new infrastructure/exhaustive matrix. Document discovery refresh, empty/no-store and disappearance/error behavior in README. Complete A1–A6 composition by reusing still-valid T001–T004 evidence, rerunning only changed-state-invalidated proofs. This task delivers dynamic project lifecycle behavior, not a separate verification milestone.
  - **Owned paths**: `workflow_monitor/web/src/main.tsx`, `workflow_monitor/web/tests/execution_fixture.py`, `workflow_monitor/web/tests/test_navigation.spec.ts`, `workflow_monitor/web/tests/test_observation.spec.ts`, `workflow_monitor/README.md`
  - **Checks**:
    - `npm --prefix workflow_monitor/web run build`
    - `npm --prefix workflow_monitor/web test -- test_navigation.spec.ts test_observation.spec.ts`
    - `PYTHONPATH=runtime:runtime/tests workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_projects workflow_monitor.tests.test_http workflow_monitor.tests.test_launch`
  - **REQUIRED T005/V1** (A2; A3; A4; A6): Production browser startup/60000-ms inventory requests observe new and removed immediate child projects without restart; selected removal retains address and clears viewer with unavailable state, no substitute. Empty root shows honest empty project list; no-store project shows no runs then legitimate first store appears via same Reader on later selected poll. Root read failure is not an authoritative empty list or selection switch; late responses cannot resurrect removed/project-obsolete view. **Evidence:** Focused permanent two-project production navigation/observation cases reuse existing fixture with bounded local lifecycle changes; advance clock and assert requested route/cadence and displayed facts. T001/T002 helper/HTTP evidence reused for unchanged safety, not replaced by mocks.
  - **REQUIRED T005/V2** (A1–A6; ADR-0003; ADR-0004): Dynamic refresh preserves T004 two-project composed navigation and unchanged-view behavior; no renderer/runtime/schema/store-writing/dependency scope expansion. README launch/URLs/discovery/refresh/no-store/error/security/rollback statements match delivered behavior. Existing check failures/gaps are reported honestly; ordinary fixture/server tests require no routine reapproval. **Evidence:** Actual listed command output and T004 still-applicable composed/renderer evidence (rerun affected cases if changed); inspect focused delivery diff and README against commands/routes/browser. Return source A1–A6 mapping and gaps for fresh independent read-only full-range implementation review, not an implementation-acceptance claim.
  - **Permissions**: Bounded isolated fixtures/databases and numeric-loopback test servers allowed under ADR-0004; prepared dependencies only, no setup/install, paid/provider calls, deployment, unrelated data/service changes or routine verification reapproval.

## Source coverage

| Source | REQUIRED task-local mappings |
| --- | --- |
| A1 launch/default/override/cwd | T003/V1–V2; T005/V2 composition |
| A2 immediate discovery/stable refs/refresh | T001/V1–V2; T002/V1; T005/V1 |
| A3 isolated APIs/fallback/no-store | T001/V2; T002/V1; T005/V1 |
| A4 browser/navigation/stale/polling/unchanged view | T004/V1–V2; T005/V1 |
| A5 read-only/loopback/closed safety/identities | T001/V1–V2; T002/V2; T003/V1; T004/V2 |
| A6 usable composed feature/docs/prepared checks | T002/V1–V2; T003/V1–V2; T004/V1–V2; T005/V1–V2 |

Each REQUIRED item is repeated verbatim in executable JSON; shared instructions are inlined
there so a worker receives meaningful boundaries without top-level metadata propagation.
One check may satisfy several mappings; do not duplicate runs when evidence remains valid.

## Human approval record

Task preparation authorized by owner's **TinySpec → Tasks** selection. Planning-only session:
independent source intent review completed with ZERO findings at the identity above; parent
artifact inspection, task review and combined owner source/task approval remain pending.
No source/task approval, workflow launch, application acceptance, setup or implementation is
claimed. Parent presents every task outcome separately for combined approval. Temporary phase
status is confined to this section; executable tasks remain authorization-neutral.
