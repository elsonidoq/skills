# One workflow monitor across projects and worktrees — TinySpec

## Three main goals

1. **One server shows workflows across projects and their Git worktrees.**
2. **An explicit command preserves a stopped worktree’s monitor history under main before deletion.**
3. **That history remains viewable afterward, without changing workflow presentation or damaging existing data.**

These owner-endorsed outcomes organize scope and acceptance. Supporting storage and routing
exist to deliver them, not to create a database-consolidation or importer subsystem.

## Intent, decisions and current authority

Original request (verbatim):

> The web server currently assumes it is run within a project that forces me to run one website per project. And that's annoying because I need to open many ports and I need to launch many web servers and stuff like that. I think a great modification would be to just one web server that knows where the projects are (~/projects, configurable, of course via a parameter when the webserver is launched) and is able to load everything from each project. In the webpage you are able to select the project from the project list and then within the project see the workflows that are running or have been run. Do not make any modification in how the website actually shows the workflow, this is just a modification to be able to run just one server and monitor all projects

Settled owner choices: immediate-child project discovery, **“no backwards compatibility”**,
and **TinySpec → Tasks, planning only**. Main and registered linked worktrees, including
Paseo worktrees, belong in the view. Later owner request (verbatim):

> I want to be able to merge the workflow history that was created in a worktree to the main worktree before deleting the worktree

Collision answer (verbatim):

> preserve both, create new ids using <workflow-name or hash>-<old id>

During this simplification, the parent obtained a separate explicit `ask_user` decision:
“May we store preserved worktree recordings separately under main and combine them in the
monitor, rather than physically merge database rows?” The owner selected **“Separate
recordings, combined monitor (recommended)”**. The presented scope included prefixed monitor
IDs, unchanged workflow views, survival after source deletion, a narrow Reader adaptation
and safe stopped capture. This answer—not the earlier generic agreement with the three
goals—settles the storage choice below. Internal recording IDs remain intact.

This source replaces the previous mechanism-heavy design. Physical consolidation, internal
ID/sequence rewriting, changed-history version propagation/SCC allocation, prescribed
provenance tables and runtime imported-ID guards are no longer requirements: separate
recordings remove the seam that motivated them. No automatic discovery-refresh obligation,
extra worktree navigation level, mandatory old-CLI rejection test or task-count requirement
is carried forward. Necessary preservation and security outcomes remain.

Source correction is authorized planning preparation only. Existing
[tasks](workflow-monitor-multiproject-tasks.md) and [JSON](workflow-monitor-multiproject-tasks.json)
are **stale**, read-only inputs until separately regenerated after parent inspection and
fresh independent source-intent review. Historical reviews/approvals do not cover this
revision; combined current source/task approval remains pending. Saved source/tasks producer
binding is Sol/medium; implementation settings remain in `.pi/workflow-executor.json`,
which the future task producer reads before decomposition. This source selects no executor
and authorizes no implementation, actual preservation or worktree deletion.

## Scope and boundaries

Include prepared server launch, project/worktree inventory, project-scoped combined workflow
selection and read APIs, explicit local preservation command, preserved-recording reads,
focused acceptance checks and necessary usage/storage documentation.

**Do not change workflow presentation:** retain graph/layout, nodes/edges, Details, labels,
execution versus acceptance semantics, metrics and coverage, explicit followups, history
pagination, filter/order behavior, freshness and 60-second polling. Add project selection
and concise source context outside the workflow renderer. No separate archive viewer or
mandatory worktree selection step: select a project, then its running/past workflows.

The web server remains read-only: no preservation/control route or button, store creation,
migration or repair on launch/read/poll. Only the explicitly invoked preservation command
writes its new preserved recording under main. It does not modify main's live database,
metrics, Git index or existing history, or the source recording and metric bytes.

Exclude automatic preservation, source deletion/pruning, Git branch merges, Paseo hooks,
hardcoded Paseo scans, SDK/private session copying, execution/resume changes, incremental
synchronization, automatic cleanup, dependency upgrades, new frameworks and automatic
install/build/deploy. No compatibility layer is required for the old CLI/URLs; this is not
a requirement to spend work rejecting every old form.

## Evidence and derived approach

The following are repository-derived implementation choices, not additional user requests.
They use existing interfaces and require production validation; inspection is not proof of
post-deletion preservation.

| Inspected evidence | Consequence and check |
| --- | --- |
| [`__main__.py`](../../workflow_monitor/__main__.py), [`pyproject.toml`](../../workflow_monitor/pyproject.toml) | Existing prepared launcher binds one Reader. Replace project binding with configurable root and scoped readers; retain assets, port and safe server options → G1. |
| [`reader.py:73–125`](../../workflow_monitor/reader.py), [`reader.py:228–380`](../../workflow_monitor/reader.py) | Reader validates a real Git worktree/admin, pins the DB inode, and locates metrics by internal run-ID hash. Arbitrary archive directories are **not** supported today. Add a narrow, explicit preserved-storage binding anchored under verified main; reuse the read/normalization contract without requiring the deleted source/admin → G2/G3. |
| [`reader.py:246–370`](../../workflow_monitor/reader.py), [`store.py:95–200`](../../runtime/coherence_workflow/store.py) | Monitor needs run descriptors, observations, review executions/attempts/input checkpoints and selected dispatch/artifact history. Runtime DB also contains private inputs and unrelated tables. Capture only the monitor subset, not a raw full runtime DB → G2. `Authority` creates/migrates storage, so preservation must use the ordinary writer lock without constructing it on source. |
| [`reader.py:153–226`](../../workflow_monitor/reader.py), [`metric_artifacts.py:37–47`](../../runtime/coherence_workflow/metric_artifacts.py) | Metric files and embedded identities depend on original IDs. Preserve associated bytes and internal IDs, including partial/unknown qualifications; do not rename internal identities to public prefixes → G2/G3. |
| [`mapping.py`](../../workflow_monitor/mapping.py), [`lineage.py:14–56`](../../workflow_monitor/lineage.py), [`app.py:408–598`](../../workflow_monitor/app.py) | Normalize explicit relations inside each recording before combining inventories. Existing app has one last-safe/freshness closure; isolate it by recording. Resolve no relation merely because another recording contains the same ID. Preserve closed DTOs/protected routes → G1/G3. |
| [`main.tsx:27–126`](../../workflow_monitor/web/src/main.tsx), [navigation tests](../../workflow_monitor/web/tests/test_navigation.spec.ts), [real-storage fixture](../../workflow_monitor/web/tests/execution_fixture.py) | Existing selection generation guards, navigation and production browser fixture can cover the changed selection seam and composed outcome; reuse them, not a new harness → G1/G3. |

Use Git's registered worktree inventory (`git worktree list --porcelain`, with safe path
parsing) to include external linked paths, including `~/.paseo` locations, without scanning
that directory. Registration and canonical common/admin identity establish repository
membership; branch names, cwd and directory names do not establish main.

Reuse standard-library Git subprocesses, SQLite/file operations and locks, existing
Starlette/React and current test fixtures. Package metadata pins Starlette 0.46.2/Uvicorn
0.34.0; no new dependency/API or internet recommendation is needed for this local design.
Actual Python/Node/browser readiness and all application checks are **NOT RUN** here.
[Documentation routing](../index.md) owns discovery; later implementation updates the
[monitor README](../../workflow_monitor/README.md) and relevant
[storage contract](../coordinate-implementation-schema.md), not another research file chain.

Whole [memory index](../../memory/MEMORY.md) was read: parent-notification guidance applies
to coordination, and no technical gotcha matches. Whole [ADR index](../decisions/index.md)
and its accepted records were read. [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md)
requires authorization-neutral future task instructions and actual current authority in
worker briefs, not temporary planning status embedded as an execution prohibition.
[ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md) allows bounded isolated
Git/DB/local-server tests without repeated routine permission questions; it does not grant
this source-only run application execution or real-data write/deletion authority. Carry
these constraints into applicable task-local REQUIRED checks/briefs.

### Goal 1: One server and project-first workflow selection

Launch with `--projects-root DIRECTORY`, default expanded `~/projects`; retain prepared
`--assets`, existing numeric-loopback binding and configurable port. Launch must work from
an unrelated cwd with a prepared package. A missing/unreadable/non-directory root gets an
actionable launch error; do not create it. Empty valid root is usable.

Discover immediate-child Git worktree roots, not recursive repositories. Group registered
main/linked worktrees of the same repository under one project. Deduplicate canonical
aliases. Only Git-registered linked paths may extend outside the configured root; preserve
existing safe-path/ownership checks and do not follow arbitrary root-child symlink escapes.
Missing/unreadable sources are qualified unavailable without hiding healthy sources.
No-store sources are empty without creation and can reveal their first legitimate store
on a later read. Do not silently rebind a Reader to replaced storage.

The project's workflow inventory combines live worktree recordings and complete preserved
recordings under main. Use opaque project/recording references, source labels such as
main/linked/preserved, and recording-qualified run identities. Public IDs for preserved
workflows follow `<workflow-name or hash>-<old id>`; add stable hash disambiguation where
needed. Distinct histories with equal old IDs must remain independently selectable.
Internal IDs and recording-local links do not change. Concise source labels may distinguish
a still-present original from its preserved copy; no mandatory pre-deletion duplicate
listing or cross-recording deduplication system is required.

Keep routes project-scoped: project inventory, selected-project run inventory, then the
existing snapshot/history/record/followup operations addressed by qualified run reference.
Browser URLs carry project and qualified run identity without a worktree hierarchy.
Preserve direct-open/reload/Back/Forward, exactly-once run-ID decoding, local filter and
newest finite-time default selection within the chosen project. Unknown addressed data
remains unavailable, never silently substitutes another workflow. Project/recording/run
switches invalidate old async fetch/layout results and selection-local state; same-run
status refresh retains viewport/drag/selection behavior. Isolate fallback, pages, metrics
and freshness per recording. No all-project snapshot scan is needed for root inventory.

Keep existing 60-second workflow polling. Initial launch/page loading may discover project
and worktree inventories; automatic discovery of newly added projects/worktrees on every
poll is not an acceptance requirement. A page reload can refresh inventory. Newly completed
preservations must be visible on reload without modifying them or restarting a writer.

Retain loopback-only binding, fixed startup assets, Host/same-origin protections, closed
DTOs/errors and raw shell validation. Browser-supplied values never become filesystem
paths; absolute paths, Git internals, private payloads and raw exceptions stay private.

### Goal 2: Explicit stopped-source preservation

Provide a prepared local CLI operation, conceptually
`workflow-monitor-preserve --source-worktree PATH`. Infer and report the registered main
destination; source and main must be distinct worktrees of the same repository. This is a
stopped-source capture for the owner's pre-deletion workflow, not a sync service. The owner
stops the writer first. Reuse its ordinary per-worktree writer lock to reject an active
writer without signalling it; keep the lock through capture and verification. Do not demand
a terminal-success run: failed/interrupted/unknown recorded histories are eligible. Process
liveness is not completion, and unavailable liveness telemetry is not alone a new blocker.
Detect source replacement/change during capture and fail safely rather than claim consistency.

Capture the monitor recording as a separate self-contained store under main's
`.coherence` area, with its associated per-run metric files and enough origin identity for
stable qualification/repeat detection. Exact directory/file naming and minimal metadata
serialization are implementation details. The preserved Reader must no longer depend on
the source worktree/admin/metric paths or source process existence. Do not use a symlink
back to source. Do not insert recording rows into main's live runtime DB.

Retain monitor run descriptors, observations (including unknown/incomplete records), review
executions/attempts/input checkpoints and the dispatch/metric-artifact facts consumed by
Reader, in their original internal identity/order. Copy only the typed fields needed from
mixed-purpose `execution_history`, not private prompt/session payloads. Do not copy runnable
progress, `execution_run_inputs`, unrelated legacy tables or SDK session files. Preserve
cross-run correction references within that same recording without ID rewriting; unresolved,
conflicting and cyclic references remain qualified, never bind to main or another capture.

Read SQLite consistently, including committed WAL data; a raw main-file copy is not sufficient.
Capture associated metric bytes without silently discarding partial tails or unavailable/
invalid evidence. Missing metrics remain explicitly missing; partial/malformed evidence stays
partial/malformed through the existing reader, not fabricated zero or complete coverage.
If an existing associated artifact cannot be safely read/copied, fail preservation with an
actionable error; do not report successful preservation while losing it. Stored original
commitment references remain historical facts: copying an artifact is not a new main Git
commit/review. Qualify preserved runner liveness as historical/unknown, not a live main runner;
retain recorded execution/acceptance facts without making up completion or acceptance.

Publish only a complete verified capture. Use a small private preparation area and a
no-overwrite completion boundary so readers cannot list partially copied data as preserved
history. Reopen through the preserved Reader and verify the retained monitor facts and metric
availability before reporting success. Implementation chooses the smallest sufficient
publication mechanism; no prescribed new provenance schema, multi-DB transaction protocol or
general importer framework. Interrupted/uncertain completion must not overwrite existing
bytes or create duplicate complete captures on retry. Exact repeat verifies/reuses the
existing capture. Source changes after that stopped capture are not incremental updates:
report the mismatch and retain source and prior capture for inspection rather than silently
replace, combine or version them. The diagnostic must explain that the source differs from
the preserved capture and must be retained while the difference is resolved.

On success report preserved workflow identities, metric availability/qualification and verified
readback. On failure identify affected operation and corrective action (for example stop the
writer, restore permissions or retain source while resolving drift); never say deletion is safe.
No command deletes/prunes source or stages/commits files. Owner deletion is a separate action;
only data covered by the verified stopped capture has been preserved.

### Goal 3: The same viewer after source deletion, without data damage

Read preserved recordings alongside main and registered worktrees under the same project's
ordinary workflow selector, even after source directory/admin registration are gone. Feed
each recording through existing normalization/public mapping before project aggregation;
qualify only public selection/routing identities. This keeps internal run IDs, metric hashes,
review chains and recorded cross-run relationships intact without propagating translated IDs.
A public reference for another recording cannot address its data, cursor or record.

Preserve all preexisting source/main DB rows, files, unrelated/private data and Git state.
Apart from ordinary lock coordination, only new command-owned capture files may be written;
existing conflicting/changed captures produce actionable errors, not replacement. The server
only observes them. Stopping/reverting
the server does not remove preserved data; no automatic rollback/deletion is introduced.

## Observable acceptance and smallest sufficient REQUIRED checks

These are future production checks, **NOT RUN** by source preparation. Tasks must organize
around the three goals and carry the relevant pass conditions/gates, not reproduce the old
task count or obsolete merge mechanisms. A single focused check can cover several mappings.

| ID | Observable outcome | Smallest sufficient REQUIRED evidence |
| --- | --- | --- |
| G1 | One prepared server/port defaults to `~/projects`, accepts a configured root from unrelated cwd, and lets the owner select a project then its main/registered external-linked running/past workflows. Empty/no-store/error states are honest. Project/run navigation and stale-result isolation work without workflow presentation changes. | Actual discovery/launcher/HTTP tests with two immediate-child repositories and a real registered external worktree (including a spaced path); equal run IDs prove isolation. Extend existing production navigation fixture for project switch, direct open/reload/Back/Forward, stale response and representative same-run viewport/poll behavior. Reuse existing HTTP/path/asset safety assertions at the changed boundary. Build current web assets; inspect renderer/dependency diff for unchanged presentation. |
| G2 | Explicit command captures stopped source monitor history and associated metrics under verified main. Source/main native data and private inputs remain untouched; distinct collisions survive with prefixed public IDs; exact repeats do not duplicate. Busy/change/error/interruption cannot publish false completion or overwrite existing data. | Permanent actual preservation-helper/CLI tests with real Git worktrees, SQLite (including committed WAL) and JSONL. Compare retained descriptors, ordered observations, review/followup/dispatch facts and metric bytes/coverage; include partial/absent metrics and unsupported/unknown qualification. Compare preexisting DB/files/Git state and absence of private runnable/session data in capture. Exercise actual busy lock, source drift, collision/repeat/reopen and interruption at publication/uncertain completion. Verify pending data is invisible and retry is safe. No exhaustive fault framework. |
| G3 | After successful capture and deletion of only the isolated fixture source, one server's project selector still opens both main's original history and preserved colliding workflows with the same graph/Details/history/review/followup/metrics meaning. No fabricated liveness, success, acceptance or Git commitment; no reference/cache leakage. | Smallest composed CLI → preserved Reader → project HTTP → production-browser check using the current real-storage fixture. Remove the isolated source and registration, reload project inventory and inspect representative rejection→fix→rereview, explicit cross-run followup, paged history and call/run metrics/qualifiers. Assert original main workflow unchanged and preserved routes independent of removed paths. Reuse G1/G2 coverage rather than another harness. Update README/storage contract with actual launch/preservation usage, scope, errors, stopped-source/repeat limits and no automatic deletion/resume. |

## Risks, dependencies and gates

The consequential seam is a **consistent, private monitor-only capture that the adapted
Reader can reopen after source removal**. Inspecting Reader established the adaptation need,
not its correctness. Prove that actual storage round trip and safe publication in the
preservation delivery before browser/real-data reliance. Known Git/SQLite/file interfaces
need permanent focused helper/integration tests, not an obligatory disposable prototype or
a separate proof/consumer/cleanup chain. Read-only discovery inspection is sufficient for
mechanical names/types; it is not durability proof.

Recording-qualified identity and scoped Reader interfaces precede their HTTP/browser
consumers. Capture/readback validation precedes the composed deletion-fixture check. Separate
task generation chooses granular executor-sized outcomes and places these real dependencies
without bundling the feature into one milestone or resurrecting obsolete translation tasks.

No material storage choice remains hidden: separate preserved recordings are owner-selected.
Module factoring, public route spelling, capture naming/serialization and publication primitive
are bounded implementation choices. Assumptions needing G2/G3 validation are complete monitor
field coverage, safe stable identity/repeat detection and preservation of unknown/metric
qualifications across the adapted Reader. Insufficient/failed REQUIRED evidence blocks
reliance on that seam; material discoveries return through existing source/task review and
affected approval, not weakened acceptance or blind retry.

Use small isolated Git/DB/local-server/browser fixtures under ADR-0004 when implementation
is authorized; do not merge/delete real owner data or invoke paid/live workflows for acceptance.
Missing prepared dependencies/browser are reported, not automatically installed under this
source-writing authority. This run does no application testing, setup or preservation.
Parent inspection and fresh independent source-intent review precede separate task
regeneration; combined owner approval remains planning-only unless separately authorized.
