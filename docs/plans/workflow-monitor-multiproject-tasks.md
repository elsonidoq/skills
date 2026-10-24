# One workflow monitor across projects and worktrees — tasks

## Requirements and approval record

Requirements truth: the whole [simplified TinySpec](workflow-monitor-multiproject-tinyspec.md),
organized around **G1 one server**, **G2 explicit stopped-source preservation**, and
**G3 unchanged viewing after removal without data damage**.
Source baseline: `0b690eafe4b202db073924de8df260fb95da310b`.
Source SHA256: `02ef30d6e4c291b7d732c22cd86ed7c9a2c8b55beedca0592928ed45648f57c4`.
[Executable JSON](workflow-monitor-multiproject-tasks.json) replaces the stale native-DB
merge decomposition. These seven IDs describe this revision, not historical assignments.

**Approval record:** owner selected **“Approve planning handoff”** through `ask_user`
after the parent presented the three goals, all seven task outcomes, exclusions, review
results and planning-only boundary. This approves planner/TinySpec source and tasks as a
planning handoff only, not implementation or actual preservation/removal. Reviewed content
at `c54602b9efa5b3f0b88f5bf1ddb6f0860a50d075`:

- Source SHA256: `02ef30d6e4c291b7d732c22cd86ed7c9a2c8b55beedca0592928ed45648f57c4`.
- Task Markdown before this approval-record update SHA256:
  `6cd2998420ad2be3e4597382423b3810390b1b9119330007116592aef912bcdf`.
- Executable JSON SHA256:
  `c8d93c7e9b8ef5a9d306d2d69dbc78ff3cc55b376c0e607843f96c759658791f`.

Fresh independent source-intent review reported zero findings. Independent task review
reported **ONE P1**: separate consistent/private capture from publication/repeat/readback
plus CLI. The producer corrected that boundary at the reviewed revision; parent inspected
the actual diff and disposed the finding as addressed. No new zero-findings task-review
verdict is claimed. JSON/Markdown dependency validation passed; application checks remain
NOT RUN. This update changes approval/status text only, not source or task contracts.
The source's stale-task statement records its earlier production stage; this record owns
current task approval. Later implementation needs explicit current launch authority.

Producer reread [the actual executor](../../.pi/workflow-executor.json) before this correction:
`openai-codex/gpt-5.6-terra` / medium workers, fresh
`openai-codex/gpt-6.1-sol` / medium reviewers. Saved tinyspec-tasks Sol/medium is unchanged;
it is the producer assignment, not an implementation binding.

## Shared scope and execution boundaries

Owner constraints (verbatim):

> Do not make any modification in how the website actually shows the workflow

> I want to be able to merge the workflow history that was created in a worktree to the main worktree before deleting the worktree

> preserve both, create new ids using <workflow-name or hash>-<old id>

Owner-selected meaning: **separate preserved recordings under main, combined monitor**, not
physical consolidation. Preserve internal IDs/relationships/metric hashes; qualify public IDs
and routing only. Preserve graph/layout, nodes/edges, Details, labels, execution versus
acceptance, metrics/coverage, explicit followups, pagination/filter/order, freshness and
60-second polling. Project selection/source context stays outside the renderer.

Immediate-child projects plus Git-registered linked worktrees, including external/spaced
Paseo paths; default expanded `~/projects` with `--projects-root`. No recursive/Paseo scan,
arbitrary symlink escape, automatic discovery-refresh obligation or worktree navigation level.
Read-only loopback web retains safe ownership/binding checks, fixed assets, protected routes,
closed DTOs/errors and raw shell validation. Browser values select opaque refs, never paths;
no absolute paths, Git internals, private payloads or raw exceptions are public. No store
creation/migration/repair or preservation/control route on launch/read/poll.

Only explicit stopped capture writes new command-owned separate storage under verified main,
with ordinary lock coordination. Preserve source/main native DB/files/metrics/private data/Git
index and existing history/captures. No native-live-DB imports, internal-ID translation,
runtime imported-ID guards, SCC/version propagation, incremental synchronization, generalized
archive/import framework, automatic preservation/deletion/pruning, Git merges, SDK session
copying, runtime/resume redesign, legacy rejection machinery, dependency upgrades or automatic
setup/install/build/deploy/provider calls. Explicit verification builds below are not startup
builds. Storage naming/routes/module factoring are bounded implementation choices.

[ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md): use current
runner launch authority, not historical phase restrictions. Executable instructions are neutral.
[ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md): bounded isolated
Git/SQLite/WAL/JSONL/local-server/browser fixtures, including removal of explicitly created
fixture worktrees only, need no routine reapproval. No actual owner-data preserve/removal,
paid/live workflows, unrelated service/data operations, push or deployment. Use prepared
Python/Node/browser; missing prerequisites/checks are NOT RUN, failures block affected reliance,
not unrelated seams. Correct ordinary in-scope failures; material requirement/scope changes
return to existing review/approval rather than weakening evidence.

Whole [memory index](../../memory/MEMORY.md), [ADR index](../decisions/index.md) and both
accepted ADRs were read. Only routine-parent-notification guidance matched; no technical
gotcha or memory write applies. JSON outcomes inline necessary constraints, pass conditions,
commands/evidence and permissions because workers do not receive top-level metadata.
Workers stay in explicit owned paths and preserve unrelated work; **no worker stages,
commits or delegates**. Runner owns focused verified checkpoints and fresh independent
read-only final review under the [shared checkpoint contract](../../skills/memory-handling/references/task-commit-contract.md).
Commands run from repository root. New helper/test paths below are deliverables, not asserted
existing prerequisites. Owned directory `web/tests` permits bounded adaptations in the existing
harness, not a new harness; shared-file edits follow predecessors.

## Goal-oriented delivery and dependencies

G1 is delivered by T001 → T005 → T006 → T007. G2 by T002 → T003 → T004.
G3 consumes that preserved binding/capture/publication in T005 and closes viewing in T007.
T001 and T002 are independent; T003 consumes both for verified stopped-source capture.
T004 consumes T003 Capture and T002 Reader for publication/repeat/readback plus thin CLI.
T005 depends on T001 and completed T004, then T006 → T007. This single split corrects
review P1 at a real capture contract, without other substantive decomposition changes.

The consequential risk is complete/private consistent capture reopened without source paths.
Permanent actual preserved-Reader tests in T002, helper WAL/JSONL/privacy/lock tests in T003
and publication/repeat/readback/CLI tests in T004 establish separately checkpointable seams
before HTTP/browser reliance. Known bounded Git/SQLite/file APIs need no disposable
prototype/proof/consumer/cleanup chain. T007 runs composed
CLI → preserved Reader → project HTTP → production browser after isolated source removal
at the first usable browser boundary. Tests, docs and routine teardown stay with each outcome.

### G1 foundation: live project recordings

- [ ] T001 Discover projects and registered live recordings
  - **Depends**: none
  - **Outcome**: deliver `projects.py` inventory/resolution using canonical Git common/admin
    identity, safe registered-path parsing and stable opaque project/recording refs. Group
    main/linked sources, derive main from registration, deduplicate aliases. Root validation,
    empty/no-store/unavailable states remain honest; retain Readers, reveal first legitimate
    store later and never silently rebind replaced storage. Project listing does not scan
    snapshots. Exclude HTTP/UI/capture writes. README follows actual discovery behavior.
  - **Owned paths**: `workflow_monitor/projects.py`, `workflow_monitor/tests/test_projects.py`,
    `workflow_monitor/README.md`.
  - **REQUIRED G1 pass/evidence**: real tiny two-repository Git/SQLite fixtures with registered
    external spaced worktree, colliding IDs, canonical aliases, nested/symlink exclusions,
    unhealthy source alongside healthy, no-store-to-store and replacement checks; compare
    existing bytes/no creations. No routine fixture gate; no owner-data actions.
  - **Check**: `PYTHONPATH=runtime:runtime/tests workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_projects workflow_monitor.tests.test_reader`.

### G2 foundation: source-independent preserved readback

- [ ] T002 Read one explicit preserved recording without its source
  - **Depends**: none
  - **Outcome**: explicit safe preserved binding anchored under verified main `.coherence`,
    minimal metadata/identity/path and preparation-versus-complete contract in `recordings.py`.
    Adapt Reader narrowly; it cannot currently read arbitrary archives. Reuse read/normalize
    behavior without source/admin/process/metric paths. Internal IDs/order/review/followup
    links and metric hashes stay intact; historical commitments remain facts, liveness is
    historical/unknown. No generalized archive layer or changed mapping/renderer semantics.
    Update only affected recording-storage guidance.
  - **Owned paths**: `workflow_monitor/recordings.py`, `workflow_monitor/reader.py`,
    `workflow_monitor/tests/test_recordings.py`, `workflow_monitor/tests/test_reader.py`,
    `docs/coordinate-implementation-schema.md`.
  - **REQUIRED G2/G3 pass/evidence**: permanent real SQLite/JSONL round trip through Reader
    and existing normalize/minimize after removal of isolated source/registration; complete
    binding survives, pending is ineligible, unsafe/replaced storage not adopted, unknown/
    unsupported/partial/malformed/absent evidence remains qualified, recorded relationships
    cannot bind elsewhere, no reads write data. Compare original source/main bytes.
    ADR-0004 fixture removal allowed; failed seam proof blocks capture reliance.
  - **Check**: `PYTHONPATH=runtime:runtime/tests workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_recordings workflow_monitor.tests.test_reader workflow_monitor.tests.test_mapping workflow_monitor.tests.test_lineage`.

### G2 capture: consistent private stopped-source contract

- [ ] T003 Capture a consistent private stopped-source recording
  - **Depends**: T001, T002
  - **Outcome**: deliver `preserve_source.py`, excluding publication/retry/CLI. Infer distinct
    registered same-repository main via T001; use T002 prepared recording layout. Small
    context-managed `capture_stopped(source_worktree, private_dir)` returns Capture containing
    verified main/origin identity, prepared monitor SQLite/associated metric paths, stable
    origin/content fingerprint, retained-facts/metric-qualification summary and
    `verify_unchanged()`. `private_dir` is new command-owned preparation under verified main,
    invisible to complete discovery. This local helper result is not a persisted interchange
    schema/framework or disposable subsystem. Capture owns ordinary source writer lock until
    context exit, including consumer publication and final readback; check source identity/
    content before publication and finally on successful context exit after readback, before
    lock release.
    No source `Authority` construction/migration or writer signalling. Consistent committed
    SQLite including WAL; monitor-only descriptors, ordered observations including unknown/
    incomplete, reviews/attempts/input checkpoints and typed dispatch/metric-artifact history.
    No raw runtime DB/mixed-purpose private history, runnable inputs/progress, unrelated or
    session data. Keep internal identity/relationships/hashes/historical commitment facts.
    Exact JSONL bytes including partial/malformed tails; absent honest, existing unreadable/
    unsafe artifact fails. Failed/interrupted/unknown eligible, absent liveness telemetry
    alone not blocking. Errors name operation/correction, retain source, never deletion-safe.
    README/storage guidance covers actual subset/privacy/layout/lock lifetime.
  - **Owned paths**: `workflow_monitor/preserve_source.py`,
    `workflow_monitor/tests/test_preserve_source.py`, `workflow_monitor/README.md`,
    `docs/coordinate-implementation-schema.md`.
  - **REQUIRED G2/G3 pass/evidence**: permanent actual helper real Git/SQLite/WAL/JSONL tests
    compare retained facts/order/reviews/followups/dispatch, metric bytes/coverage, unknown/
    unsupported qualifications, private exclusion and preexisting source/main rows/files/
    index/history. Actual busy lock, consumer-lifetime contention, source SQLite/metric drift/
    replacement and exit/error tests prove held lock, checks and release. Preparation stays
    invisible; no prior bytes change. Checkpoint this outcome without publisher/CLI. No
    exhaustive fault framework; ADR-0004 isolated fixtures only, no owner-data actions;
    failed capture evidence blocks T004 reliance.
  - **Check**: `PYTHONPATH=runtime:runtime/tests workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_preserve_source workflow_monitor.tests.test_recordings workflow_monitor.tests.test_reader`.

### G2 delivery: complete publication and verified explicit command

- [ ] T004 Publish verified captures with repeat-safe readback and explicit CLI
  - **Depends**: T002, T003
  - **Outcome**: deliver `preserve.py` prepared module/console command
    `workflow-monitor-preserve --source-worktree PATH`, consuming T003 Capture rather than
    reimplementing source capture, and T002 preserved Reader. Report inferred main. Within
    Capture context retain its source lock through `verify_unchanged()` before complete-only
    no-overwrite publication under main `.coherence`, reopened Reader comparison to retained-
    facts/metric summary and final drift check on successful context exit; only then
    report success. If final drift check fails, no successful-preservation claim or automatic
    rollback/deletion; retain source and any newly completed bytes for inspection. Pending
    private preparation is invisible. Stable origin/content identity makes exact repeat
    verify/reuse without duplicate, including interrupted/uncertain publication retry.
    Changed stopped source is mismatch, not incremental sync/version: retain both and tell
    owner source differs and must be retained pending resolution. Distinct colliding old IDs
    survive with `<workflow-name or hash>-<old id>` public IDs and stable hash disambiguation;
    internal IDs/relationships/metric hashes unchanged. Source-independent preserved Reader
    verifies facts/metric qualifications; commitments remain historical, liveness unknown.
    Success reports identities/metrics/verified readback; failures identify operation/correction,
    never deletion-safe. README/storage docs match actual stopped/repeat/errors/no-delete/
    no-resume command and limits, with no broader schema/framework.
  - **Owned paths**: `workflow_monitor/preserve.py`, `workflow_monitor/recordings.py`,
    `workflow_monitor/tests/test_preserve.py`, `workflow_monitor/tests/test_recordings.py`,
    `workflow_monitor/pyproject.toml`, `workflow_monitor/README.md`,
    `docs/coordinate-implementation-schema.md`.
  - **REQUIRED G2/G3 pass/evidence**: permanent actual publication/subprocess CLI real Git/
    SQLite/WAL/JSONL tests reuse T003 capture proof and compare facts/bytes/coverage/private
    exclusion plus source/main/index/prior-history invariants. Collisions, repeat/reopen,
    publication interruption/uncertain completion prove pending invisible and no overwrite/
    duplicate. Controlled source drift during final Reader verification prevents success;
    later-source mismatch retains both with actionable retain-source diagnostic. Actual
    Reader readback does not depend on source paths; no fabricated success/acceptance/
    liveness/new commitment. No exhaustive fault framework. ADR-0004 fixture capture/removal
    only, no owner-data actions; failed safety/readback blocks dependent acceptance.
  - **Check**: `PYTHONPATH=runtime:runtime/tests workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_preserve workflow_monitor.tests.test_preserve_source workflow_monitor.tests.test_recordings workflow_monitor.tests.test_reader`.

### G1/G3 delivery: scoped combined observation

- [ ] T005 Serve project-scoped combined live and preserved workflows
  - **Depends**: T001, T004
  - **Outcome**: scoped project inventory, combined run inventory and existing snapshot/
    history/record/followup operations using recording-qualified refs. Normalize per recording
    before public qualification; preserve local relationship/metric meaning. Per-recording
    fallback/last-success/freshness/pages, unknown address never substitutes. Reload reveals
    completed captures; pending invisible, healthy sources survive unavailable peers. Project
    plus qualified-run browser shell, raw validation/exactly-once decode, no worktree hierarchy.
    Retain closed protected read-only DTOs/assets/errors and privacy; adapt existing Python
    app consumers and production fixture transport without dropping substantive assertions.
  - **Owned paths**: `workflow_monitor/app.py`, `workflow_monitor/projects.py`,
    `workflow_monitor/tests/test_projects.py`, `workflow_monitor/tests/test_http.py`,
    `workflow_monitor/tests/test_reader.py`, `workflow_monitor/tests/test_chain_mapping.py`,
    `workflow_monitor/tests/test_execution_presentation.py`, `workflow_monitor/tests/test_history.py`,
    `workflow_monitor/tests/test_lineage.py`, `workflow_monitor/tests/test_observation.py`,
    `workflow_monitor/tests/test_delivery.py`, `workflow_monitor/web/tests/execution_fixture.py`,
    `workflow_monitor/README.md`.
  - **REQUIRED G1/G3 pass/evidence**: actual two-project/main/external-linked/preserved
    colliding histories through production HTTP. CLI capture then fixture source removal
    still serves snapshot/pages/record/followup/metrics and unchanged main; cross-recording
    refs/cursors/caches/fallback cannot leak. Historical liveness honest, reload sees complete
    capture, pending invisible. Retain HTTP/path/asset security checks and byte/no-write
    comparisons. Bounded fixture server/removal allowed; no owner-data actions.
  - **Check**: `PYTHONPATH=runtime:runtime/tests workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_projects workflow_monitor.tests.test_http workflow_monitor.tests.test_reader workflow_monitor.tests.test_chain_mapping workflow_monitor.tests.test_execution_presentation workflow_monitor.tests.test_history workflow_monitor.tests.test_lineage workflow_monitor.tests.test_observation workflow_monitor.tests.test_delivery`.

- [ ] T006 Launch one prepared server from an unrelated cwd
  - **Depends**: T005
  - **Outcome**: replace project binding with `--projects-root DIRECTORY`, expanded `~/projects`
    default; retain prepared `--assets`, port and safe numeric-loopback options. Unrelated cwd
    launch works; actionable bad root error without creation, empty root usable. Update
    README invocation/default/error/stop behavior; no install/build/runtime on launch.
  - **Owned paths**: `workflow_monitor/__main__.py`, `workflow_monitor/tests/test_launch.py`,
    `workflow_monitor/tests/test_delivery.py`, `workflow_monitor/README.md`.
  - **REQUIRED G1 pass/evidence**: actual prepared module/entry-equivalent subprocess and HTTP
    from unrelated cwd with isolated HOME/two-repository root; default/configured root,
    one port, empty/bad root, assets/security assertions and no-write comparisons.
    No mandatory legacy-rejection campaign. Isolated local server/teardown allowed.
  - **Check**: `PYTHONPATH=runtime:runtime/tests workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_launch workflow_monitor.tests.test_delivery workflow_monitor.tests.test_http`.

### G1–G3 production acceptance: unchanged viewer after fixture removal

- [ ] T007 Select projects in the unchanged viewer and prove post-removal history
  - **Depends**: T006
  - **Outcome**: project selector then combined workflows in existing browser, source context
    outside renderer, project/qualified-run URLs. Preserve direct-open/reload/Back/Forward,
    exactly-once decoding, local substring filter/newest finite default, honest unknown URLs.
    Invalidate stale fetch/layout and selection-local history/metrics on switches; same-run
    refresh preserves viewport/drag/selection and 60-second polling. Adapt existing production
    navigation/storage harness and route fixtures without weakening assertions. At this first
    usable boundary compose actual CLI → preserved Reader → scoped HTTP → production browser,
    removing only isolated source/registration then reloading inventory. README/storage docs
    follow actual launch/selection/preserve/readback/repeat/mismatch/error/no-delete/no-resume.
  - **Owned paths**: `workflow_monitor/web/src/main.tsx`, `workflow_monitor/web/src/style.css`,
    `workflow_monitor/web/tests`, `workflow_monitor/README.md`,
    `docs/coordinate-implementation-schema.md`. CSS only for selection/context, not workflow
    styling; graph/layout/dependencies excluded.
  - **REQUIRED G1 pass/evidence**: one production server/browser, two immediate-child projects
    and real external/spaced linked worktree, colliding selections, navigation/reload/stale
    response/filter/default/unknown URL and representative same-run viewport/poll checks.
    Build actual assets; inspect renderer/graph/layout/dependency diff for unchanged presentation.
  - **REQUIRED G2/G3 pass/evidence**: real CLI fixture capture then isolated source/admin
    removal; ordinary project selector still opens unchanged main and independently prefixed
    colliding preserved workflows. Inspect graph/Details, rejection→fix→rereview, explicit
    cross-run followup within recording, paged history, call/run metrics and partial/unknown
    qualifications. No fabricated liveness/success/acceptance/commitment or ref/cache leakage;
    original bytes/main unchanged, no private capture payloads, observation restart removes
    nothing. Reuse T003 capture/T004 publication safety proof and existing browser harness,
    not mocks/screenshots alone.
    Bounded fixture removal/servers allowed; no owner-data actions or prerequisite downloads.
    Failed composed proof blocks G3 acceptance/real-data reliance.
  - **Checks**:
    - `PYTHONPATH=runtime:runtime/tests workflow_monitor/.venv/bin/python -B -m unittest discover -s workflow_monitor/tests -t . -v`
    - `npm --prefix workflow_monitor/web run build`
    - `npm --prefix workflow_monitor/web test` (existing fixture invokes prepared `.venv/bin/python`).

## Validation and next gate

The task producer validates JSON/Markdown task parsing/dependencies, human–machine outcome/
owned-path/check equivalence, source digest, G1–G3 coverage, local links and focused diff.
These are planning checks only. Actual application tests/build/browser/setup/preservation/
removal are NOT RUN by task preparation. Parent inspection/disposition and combined owner
planning approval are complete as recorded above. Implementation remains separately
authorized; no automatic rereview loop or implementation launch is implied. JSON `required`
mappings provide compact pass/evidence/permission summaries; task-local outcomes independently
carry executable context.
