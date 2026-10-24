# One workflow monitor for projects and worktrees — TinySpec

## Outcome, provenance and authority

One prepared server, port and website lets the owner select a local project and monitor
its main and registered linked-worktree workflows without changing the workflow viewer.
An explicit separate CLI operation preserves a linked worktree's workflow history in the
main worktree **before the owner deletes the linked worktree**.

Original owner intent (verbatim):

> The web server currently assumes it is run within a project that forces me to run one website per project. And that's annoying because I need to open many ports and I need to launch many web servers and stuff like that. I think a great modification would be to just one web server that knows where the projects are (~/projects, configurable, of course via a parameter when the webserver is launched) and is able to load everything from each project. In the webpage you are able to select the project from the project list and then within the project see the workflows that are running or have been run. Do not make any modification in how the website actually shows the workflow, this is just a modification to be able to run just one server and monitor all projects

Still-settled owner decisions: **immediate top-level child projects only**, no recursive
project scan; **“no backwards compatibility”** (replace `--project`, no old CLI/URL
compatibility); **TinySpec → Tasks, planning only**. Default `~/projects` and configurable
`--projects-root` remain the bounded launch direction.

Subsequent scope clarification (verbatim):

> I want to be able to merge the workflow history that was created in a worktree to the main worktree before deleting the worktree

The parent proposed Git-registered worktree discovery instead of a hardcoded Paseo root,
and a separate explicit merge retaining recordings, metrics and source identity, safe
repetition, verification, no source deletion or destination-history overwrite. The owner
answered **“It makes sense. How do you propose to amend the spec? Resume the same agent or
launch a new one?”**, authorized **“ok, resume the worker to incorporate that into the
spec”**, then **“sorry, do the steps you recommend, which involves first inspecting the
recording schema and Git worktree discovery.”** Those inspections precede this amendment.
One project entry combining main and linked workflows is the parent's proposed approach,
not an original owner mandate; the design below adopts it with explicit source identity.

A material run-ID collision choice was returned through the parent. The actual owner
answer via `ask_user`, relayed to this producer, is verbatim:

> preserve both, create new ids using <workflow-name or hash>-<old id>

Therefore distinct histories with equal original IDs must both survive. A refusal-only
collision policy is not acceptable. Prefix allocation, typed identity translation and
stable origin mappings below are derived mechanics implementing that answer.

Amendment baseline is clean `main` at `34a8c31edc774853ffa948451c155187bdd310df`.
Original source checkpoint `fd89605` / SHA256
`3d8df9845dc95bcb4108f23bdffa2b66d12cf157a35d74e038ce9322db083f84` and its ZERO-finding
intent review cover **only the old scope**. The combined approval question was cancelled;
no source/task approval exists. Existing [tasks](workflow-monitor-multiproject-tasks.md)
and [JSON](workflow-monitor-multiproject-tasks.json) are stale and must be revised after
parent inspection and a **fresh independent intent-focused read-only source review**.
This amendment is preparation only, not implementation or real-data merge permission.
The saved source-producer binding remains `openai-codex/gpt-6.1-sol` / medium, separate
from the intended implementation executor `.pi/workflow-executor.json`, which the task
producer must read before decomposition. Combined owner artifact approval is still required.

## Scope and preserved boundaries

Include root/project/worktree discovery, scoped read-only observation and selection,
an explicit CLI-only history merge into main storage, focused checks and necessary usage
updates in [monitor README](../../workflow_monitor/README.md) and storage-contract updates
in [schema owner](../coordinate-implementation-schema.md). Implementation may add only the
small merge/provenance storage and narrowly necessary reader/runtime interfaces described
below; this is not a runtime redesign. This source-writing run edits neither technical owner.

Preserve graph/layout, node/edge Details, labels, status/acceptance, metrics, followups,
history/pagination, freshness, run ordering/filtering and 60-second polling. Add project
and source-worktree selection context outside that renderer, not a graph/Details redesign.
Running and past recorded workflows remain visible, not just live runs.

The **web server stays read-only**: no merge route/button, execution/control, source/DB
creation, migration or repair on startup or polls. Only the explicitly invoked merge CLI
may add imported history/metrics and its bounded provenance/recovery records to main.
Existing main history/files and source content are never overwritten or deleted. Preserve
unrelated legacy tables. Existing prohibitions on **automatic** migration/backfill remain;
they do not prohibit this newly owner-requested explicit merge. No inferred missing events,
fabricated success/acceptance, imported resume authority or automatic launch.

No automatic merge, worktree deletion/pruning, Paseo hooks, filesystem watcher, background
cleanup service, generalized importer framework, cross-repository import, dependency
upgrade, new framework, automatic setup/install/build/deploy or compatibility layer.
Normal prepared package launch works independently of any monitored project's cwd.
Retain loopback-only binding, closed DTOs/errors, same-origin protections and fixed startup
assets. Browser requests use discovered opaque references, never filesystem paths.
Canonical worktree/admin/store/metric identity and safe-path checks remain necessary;
Git registration, not arbitrary browser input, authorizes reading linked paths outside
`--projects-root`. Do not expose absolute paths, private inputs, Git internals or raw errors.

## Inspected evidence and dependency decisions

Evidence spans below refer to the amendment baseline. Parent read-only discovery observed
that this repository's `git worktree list --porcelain` includes main plus linked worktrees
under `/home/dev/.paseo/worktrees/`, including nested and differently named locations.
These observed local paths are evidence, **not configuration or scan roots**.

| Source evidence | Derived constraint → observable check |
| --- | --- |
| [`__main__.py:23–35`](../../workflow_monitor/__main__.py), [`pyproject.toml`](../../workflow_monitor/pyproject.toml) | Existing prepared module/console launcher binds one Reader; replace project binding with root discovery, retain assets/port/safe server options → A1. |
| [`reader.py:37–113,175–217,228–380`](../../workflow_monitor/reader.py) | Reader pins canonical root/admin/DB and append-only metric identity, tolerates initial no-store; reads monitoring, observations, reviews and dispatch/artifact history, not runtime inputs → retain one Reader/cache per source; native main monitoring import is feasible without making runs resumable → A2/A3/A7/A9. |
| [`app.py:408–598`](../../workflow_monitor/app.py), [`test_http.py`](../../workflow_monitor/tests/test_http.py) | Reader, last-safe and last-success are one closure today; raw shell validation and fixed protected APIs already exist → scope observation by project/worktree, retain security → A3/A5. |
| [`main.tsx:27–126`](../../workflow_monitor/web/src/main.tsx), [`test_navigation.spec.ts`](../../workflow_monitor/web/tests/test_navigation.spec.ts), [`execution_fixture.py:43–45,211`](../../workflow_monitor/web/tests/execution_fixture.py) | Existing run URLs/generation guards, real temporary Git/store fixture, production assets and Playwright → extend selection identity and composed fixture, not renderer/framework → A4/A6/A9. |
| [`store.py:95–200`](../../runtime/coherence_workflow/store.py) | Ordinary per-worktree admin `coherence-workflow.lock` uses flock; `Authority` also CREATES dirs/DB/tables. Run IDs are per-DB PKs; observations/history/review attempts have independent integer seq → use lock-only acquisition, native merge with explicit run/sequence mappings, never Authority for source or preview → A7/A8. |
| [`monitoring.py:61–128,164–198`](../../runtime/coherence_workflow/monitoring.py), [`lineage.py:14–56`](../../workflow_monitor/lineage.py), [`reader.py:277–370`](../../workflow_monitor/reader.py) | Typed invocation/checkpoint links are run-local; descriptor `correction_of.run_id` is cross-run; ordered history supplies dispatch/metric facts → convert only schema-defined run references, retain local identity/ordering and complete review relations → A7/A8. |
| [`metric_artifacts.py:37–47,132–155,220–264`](../../runtime/coherence_workflow/metric_artifacts.py), [storage schema](../coordinate-implementation-schema.md#metric-artifact-jsonl-v1) | Metric path hashes exact run ID; rows retain run/invocation identity; files can already be tracked, partial or conflicting → translated filenames and typed row run IDs, no overwrite, no invented destination Git commitment → A7/A8. |
| [`store.py:259–310`](../../runtime/coherence_workflow/store.py), [`cli.py:160–194`](../../runtime/coherence_workflow/cli.py) | Resume needs execution progress plus private original inputs/authority. Monitoring history alone cannot authorize it → do not import runnable progress/inputs/session files; reserve imported IDs against new execution reuse → A7/A8. |

Dependency evidence is unchanged: Python metadata/lock pin Starlette 0.46.2, Uvicorn
0.34.0 and HTTP-test httpx 0.28.1; web lock resolves React/DOM 19.3.1, ReactFlow 12.12.0,
ELK 0.11.1, Vite 7.3.7, TypeScript 5.9.3, Playwright 1.64.1. Reuse existing Git discovery,
standard-library SQLite transactions/files/hashing/flock, Starlette/React and current test
fixtures. No new external dependency or uninspected internet recommendation is required.
Existing code/schema are adequate evidence for these primitives; multi-file publication
is **not** proved atomic by a SQLite transaction and gets actual interruption/reopen tests.
No external research or new canonical guidance write is justified at source preparation;
the affected usage/storage contracts must be updated with implementation, not another
research-document chain. [Documentation routing](../index.md) remains discovery authority.

Whole [memory index](../../memory/MEMORY.md) has only parent-notification guidance, no
applicable technical gotcha. Whole [ADR index](../decisions/index.md) and both accepted
records were reread: [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md)
requires authorization-neutral executable tasks and current launch authority in briefs;
phase status belongs here/in approval records. [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md)
permits bounded isolated Git/DB/local-server checks under shared defaults, not unrelated
real-data writes, installs or global changes. Map both into task-local REQUIRED briefs;
neither supplies implementation/real-data merge authority for this preparation run.

## Bounded design

### Root, project and registered-worktree inventory

Replace `--project` with optional `--projects-root DIRECTORY`, default expanded `~/projects`;
keep required `--assets`, port default and safe Uvicorn options. Resolve the root at startup.
Missing/unreadable/non-directory root fails before binding with `--projects-root` and a
concrete corrective action; never create it. Empty valid root is usable with no projects.

Discover regular nonsymlink immediate-child canonical Git worktree roots only, not nested
repositories. For each repository, inspect Git's machine-readable registered-worktree list
and common/admin identity; group main plus registered linked worktrees into **one project**.
Deduplicate aliases to the same repository/source. Derive main from Git registration/common
directory, not branch name, directory name or cwd. Parse paths safely (NUL-capable porcelain
where used), including spaces. Include linked worktrees outside the root, including Paseo,
without hardcoded Paseo paths or recursive scanning. Missing/prunable/unreadable entries
are unavailable, not grounds to scan for replacements or run `prune`. Validate every
present source with existing canonical Reader safety; a bad linked source cannot hide main
or another healthy source. Ordinary nonsymlink-child restriction is a cheap root-escape
protection, not a blanket ban on Git-registered external worktrees.

Closed project inventory retains `{ref,label}`; source inventory adds opaque source ref,
human label and main/linked qualification, never absolute paths. Stable refs derive from
canonical repository/source identity, not run ID alone. Keep sources with no store listed.
Refresh discovery on inventory requests and browser startup/60-second polling, including
new registered worktrees; no all-store snapshot read at root discovery. New/removed project
or worktree appears/disappears on the next successful poll. Root/Git discovery errors are
unavailable, not authoritative empty inventories. Missing addressed sources retain their
URL with honest unavailable state, not a substitute. Revalidate pinned identities before
use; never silently adopt a replaced admin/DB/metric file by recreating a Reader on poll.

### Read-only observation, routes and unchanged viewer

Retain one long-lived Reader, sanitized last-safe cache and last-success time **per source
worktree**, not per repository. A project's run list includes main and linked-source runs,
with source context visible in selection labels. Use a source-qualified selection key even
when displayed run ID, opaque run/record ref or snapshot token is identical elsewhere.
Followups remain only explicit relations in that source's snapshot; do not infer relations
across worktrees or borrow another source's fallback, pages or metric evidence.

Derived route shape (no old-route compatibility required):

- `GET /api/monitor/v1/projects` and `/api/monitor/v1/projects/{project_ref}/worktrees`.
- `/api/monitor/v1/projects/{project_ref}/runs`: grouped project's run inventory, each run
  qualified by its source ref/label; disclose per-source unavailable states without hiding
  healthy workflows. Read this project's sources only, not all projects' snapshots.
- `/api/monitor/v1/projects/{project_ref}/worktrees/{source_ref}/runs/{run_ref}/snapshot`,
  `/history`, `/records/{record_ref}` and `/followups` (each suffix below that run prefix);
  existing snapshot/cursor/limit semantics stay intact.
- Browser `/`, `/projects/{project_ref}` and
  `/projects/{project_ref}/worktrees/{source_ref}/runs/id-<percent-encoded actual run ID>`.

Run IDs decode exactly once; adapt raw shell validation before slash decoding, not an HTML
catch-all. Unknown refs/invalid structure/API paths/unknown assets get closed errors.
Only fixed startup assets and validated shells serve `index.html`. Keep all Host,
Fetch Metadata/header, CSP/no-store and other current protections. No write HTTP operation.

At `/`, request explicit project selection. Bare project URL applies the existing newest
finite-time rule across its available source-qualified runs (deterministic ties), then
replaces with the full run URL. Within that selection retain local filtering, direct open,
reload, Back/Forward, selected run on polls and existing viewer semantics. Source labels
outside the renderer distinguish otherwise identical workflow names/IDs. Project/source/run
switch invalidates pending inventory/snapshot/history/layout results and clears obsolete
selection-local runs/filter/graph/Details/lineage/layout measurements/positions/viewport.
Status-only refresh within the same source/run retains current viewport/drag/selection.

No-store/empty-store source shows no runs without creation; the same Reader sees the first
legitimate store on a later selected read. Unsupported/unreadable data stays qualified;
after successful reads only that source's sanitized last-safe view may remain with warning.
Imported copies are normal main-worktree history, not a second archive viewer. Retain origin
metadata outside the renderer. While source still exists, its original and main's imported
copy may both be listed with distinct source/ID context; no cross-worktree deduplication
framework is needed. Repeating a merge must not create another imported copy in main.

### Explicit history merge into main

Add a narrowly scoped prepared CLI operation, conceptually
`workflow-monitor-merge --source-worktree PATH [--dry-run]`: explicit local CLI paths, not
browser paths; infer and report the verified registered main destination from Git. No
merge on server launch/poll, no automatic worktree removal. The command merges the selected
source's recorded workflow history into main's **existing native monitoring tables** (or
creates only the necessary destination monitor storage if absent), so normal main Reader
and viewer work after source removal. It is not an archive-only side database or symlink.
It does not merge Git branches, copy SDK session files or make historical work resumable.
Source and target must be distinct registered worktrees of the same repository; a dry-run
validates and describes planned IDs/data/conflicts without creating storage or lock files.
Preview is informational; apply reacquires locks and revalidates, never trusts a stale preview.

Merge the source's monitor runs, observations, review executions/attempts/inputs and history
needed for recorded dispatch/metric facts. Retain the historical monitoring payload/order,
including qualified incomplete/failed runs; do not require workflow success. Do not copy
`execution_run_inputs` (contract/executor/paid authority), runnable `execution_runs` or
`execution_tasks`, unrelated private prompt/session history, legacy usage or `wf_*` tables.
For `execution_history`, copy only the typed `worker_invocation`/`fixer_invocation` started
dispatch identity fields consumed by Reader and `metric_artifact` facts, not their private
prompt/session payloads. No original event is rewritten to claim completion or acceptance.
Imported runner identity is provenance, not a live main runner: qualify current liveness as
unknown/historical rather than transferring a process-presence claim to main.
A minimal imported-ID reservation check at normal start prevents a new run from reusing
an imported monitoring ID; resume rejects imports without launching or mutating history.
No broader runtime behavior change is authorized.

**Identity and ordering.** Every imported run receives `<workflow-name or hash>-<old id>`.
Use a safe readable source/workflow prefix where unambiguous, otherwise stable origin/hash
disambiguation. Save a small destination provenance map of repository/source identity,
original run ID, per-run retained-payload/metric snapshot digest, chosen imported ID and
relevant sequence mappings. Unrelated new source runs must not duplicate unchanged imports.
Generate mappings for the whole source set before translating links. Same origin + exact
source payload reuses its verified mapping as a no-op; distinct origins or changed source
snapshots get distinct deterministic hash-qualified IDs, preserving earlier imports and
main history. Actual occupied IDs/files, including preexisting tracked/dirty artifacts,
trigger deterministic disambiguation, never overwrite/adoption of unknown bytes. Persist
chosen allocation so an interrupted retry cannot allocate another duplicate. Missing or
changed already-imported destination content is an actionable integrity error, not a
successful repeat or permission to overwrite it.

Translate only schema-defined run references: table `run_id`, descriptor
`correction_of.run_id`, metric row `run_id` and run-ID-derived artifact path. Map a correction
reference only to its identified source origin; unresolved/out-of-set references stay
qualified unresolved and cannot accidentally bind to an unrelated native main run with the
same old ID. Preserve task/occurrence/execution/invocation/checkpoint/correction-chain,
session/branch/epoch and Git commit identities exactly where run-local; do not globally
replace text, task prose, session IDs or hashes. Keep source integer seq as provenance;
allocate destination seq preserving within-source observation/history/attempt order without
renumbering existing destination rows. Review trigger/predecessor, selected checkpoints,
rejection/fix/rereview chain, followups and acceptance must survive translation. Unsupported
identity-bearing versions/fields stop only their affected merge with the schema/operation
and corrective action; do not invent conversions or blanket-reject compatible recordings.

**Metrics.** Copy associated metric evidence into main independently of source lifetime,
using the exact imported-run-ID hash filename and typed row run-ID transformation. Preserve
invocation membership, values, before/after context, recorded source commitment references
and coverage qualifiers; absent metrics remain absent/qualified, never zero/full. An invalid
or unterminated artifact is not silently truncated or counted complete: report that run's
preservation blocker so the owner retains source and can correct/decide before deletion.
Keep original origin/hash/status facts as provenance and distinguish them from destination
file state: rewriting/copying a source-committed artifact does **not** mean the new main file
was Git committed/reviewed. No automatic Git stage/commit, branch merge or dirty-file repair
belongs to the merge command. Existing main tracked/staged/dirty metric bytes stay untouched.
No successful report may omit an associated source artifact that is required for its view.

**Consistency, publication and retry.** Acquire source and target's ordinary per-worktree
writer locks in stable order with a lock-only helper; do not construct source `Authority`
or run its storage/quarantine setup. Busy active writer means fail promptly with “wait for
the source/main writer, then retry”, never signal/abandon it. A quiescent failed/interrupted
recording is eligible; a recorded live writer/unknown changing file cannot be called a
consistent deletion-ready snapshot merely because its lock was momentarily obtainable.
Use a read-only SQLite transaction/backup view for source (including committed WAL data),
safe regular-file reads and identity/content rechecks for metrics; hold locks through
publication and final verification. Preserve source DB/metrics and do not checkpoint,
repair or migrate them. Target SQLite writes use transactions on its existing inode,
not a whole-DB replacement that bypasses Reader identity checks. Keep unrelated tables/rows.

A DB transaction alone cannot atomically publish JSONL files. Use bounded private staging
and minimal destination pending-import/provenance records: reserve the exact origin→IDs,
prepare translated evidence, publish only new no-overwrite metric files with ordinary
durable file/parent flushes, then insert the complete imported monitoring set and mark it
visible/complete in one target transaction. Readers must not see pending imports as complete
workflows. Verify files before DB visibility, retain normal SQLite durability, and reopen
for final readback before reporting success. Interruption can leave owned pending records/
files, never a falsely complete import: exact retry reconciles those owned bytes and final
DB state, completing the same import or reporting its precise blocker. Never delete unknown
files, duplicate a committed import after uncertain completion, or roll back unrelated
work. No cross-file atomicity or arbitrary power-loss guarantee is claimed.

Report imported IDs/origins, preserved counts, metric availability and verified outcome
using closed diagnostics, not private payloads. On busy/schema/permission/drift/conversion/
publication/readback failure report the affected operation and corrective action, retain
source and existing destination history, exit unsuccessfully, and never say deletion is
safe. Success requires verified usable destination history/metrics; it never deletes the
source or grants authority to delete it. Any later source writes are not covered by that
verified snapshot; rerun explicit merge before relying on preservation of newer history.

## Acceptance and smallest sufficient REQUIRED evidence

These are later production criteria, **NOT RUN** in this planning-only amendment. Carry
each applicable mapping/pass condition/check into task-local REQUIRED worker/reviewer
briefs. Use bounded actual-helper/real-Git/SQLite fixtures and existing composed browser
checks; one check may establish several criteria without repeated evidence ceremonies.

| ID | Observable completion | Smallest sufficient REQUIRED check |
| --- | --- | --- |
| A1 | One prepared server defaults to `~/projects`, supports `--projects-root`, serves multiple projects from unrelated cwd on numeric loopback; invalid root is actionable, empty root usable; no old `--project` or auto setup. | Adapt actual launcher/help tests and one bounded prepared-module/console subprocess with absolute assets/package availability, two temporary child repositories and safe Uvicorn assertions. |
| A2 | Immediate-child project selection includes main plus Git-registered external/Paseo-style linked-worktree workflows under one project, no hardcoded root/recursive scan. Refs/source labels are stable and new/removed registrations refresh next poll; broken source does not hide healthy data. | Permanent actual discovery-helper and inventory HTTP tests with real Git worktrees outside root, a spaced path, absent store and prunable/missing registration. Assert repository grouping, source identity and no all-project store scan; no directory-list mock as sole oracle. |
| A3 | Project/source-qualified run APIs, histories, followups, metric caches/fallback/freshness are isolated even for identical IDs/tokens/refs. No-store first creation appears via retained Reader; unavailable one does not break healthy sources. | Two-project plus main/linked real Reader/HTTP fixtures with distinguishable records and collisions; representative snapshot/page/record/followup and failed-read fallback checks; retain DB/metric identity/read-only tests. |
| A4 | Visible project/source context, direct opens/reload/Back/Forward, filtering/history and 60-second polling work with unchanged graph/Details. Stale project/source/run results cannot overwrite new selection. | Extend existing production fixture/navigation Playwright to main + external linked source and another project; observe distinct data with equal IDs, delayed old-source response rejection, representative unchanged Details/history/followups and viewport refresh; advance clock, not a minute wait. |
| A5 | Server remains protected read-only HTTP with fixed assets, raw exactly-once run-ID handling and no arbitrary browser filesystem paths or merge/control routes; drift never silently rebinds. | Adapt focused HTTP/launcher/Reader boundary tests: raw encoded slash, malformed/extra segments/unknown refs, replacement, Host/Fetch Metadata/header, closed DTO/errors and asset substitution. Compare observed source DB/metric content; keep existing safety assertions rather than new exhaustive matrix. |
| A6 | Prepared delivery and docs accurately describe project/worktree selection and separate merge operation; no workflow renderer/runtime redesign or dependency churn. | Focused prepared Python tests, `npm --prefix workflow_monitor/web run build`, affected existing Playwright cases and boundary diff inspection. Update canonical monitor README and storage schema with actual CLI/options/paths, origin/visibility, errors, recovery, no-resume/source-retention and durability limits. |
| A7 | Explicit CLI merge preserves source recorded workflows/review/followup/order/metrics in native main history; successful readback is unchanged in meaning after source removal, and main's preexisting history stays intact. Imported runs cannot resume/launch or claim new success/acceptance/Git artifact commitment. | Actual merge helper/CLI over real Git-linked worktrees and SQLite + JSONL: representative rejection→fix→rereview, followup and multi-page history. Reopen main Reader, compare translated logical facts, ranges, metrics/coverage and ordered evidence; then remove only the isolated test source and read main again. Assert old target rows/files/legacy data unchanged, no private authority/session copy and imported resume/start-ID reservation behavior. No real owner worktree removal. |
| A8 | Both distinct equal-ID histories survive with prefixed imported IDs. Typed cross-run/metric identities stay correct; exact repeats do not duplicate. Changed snapshots and occupied prefixes/artifacts preserve both versions without overwrite. Busy/change/error/interruption never reports false completion or destroys source/target history. | Permanent actual merge tests with colliding run IDs and source-linked relations, preexisting tracked/dirty destination metrics, deterministic allocation/repeat/reopen, changed source snapshot and unresolved reference. Focused interruption at metric publication and DB completion plus uncertain-return reconciliation; busy source/target locks, WAL source snapshot and a changing metric exercise actual boundaries. Assert source unchanged, pending invisible, no arbitrary replacement, actionable failure and exact retry convergence. |
| A9 | Owner's whole outcome works: choose project, see main and Paseo-style linked workflows unchanged; explicitly merge, remove isolated source, then see preserved history/metrics from main with no duplicate imports from repeated merge. | Smallest composed CLI→real main Reader/HTTP→production-browser extension of current fixture. Observe translated colliding workflows, representative graph/Details/history/review and metrics before/after isolated source removal, plus original destination workflow. Assert ordinary server polling publishes only verified complete imports and old source failures never leak across selection. Reuse A4/A7 proof where still valid; no extra harness. |

## Risk selection, sequencing and gates

No disposable prototype is automatically warranted. Git discovery and SQLite/file/identity
mechanics are bounded known interfaces; use permanent tests of the actual helpers. The
new consequential seam is **typed identity/sequence translation plus DB/JSONL publication**,
not a name/type unknown. Prove a representative full round trip, collision and interrupted
retry in its delivery before downstream browser/real-data reliance. Mock-only green parts
cannot prove preservation after source deletion: A7/A8 use real storage; A9 composes the
actual CLI/Reader/web boundary. These tests remain production regression coverage, not a
prototype/consumer/cleanup task chain or a generalized import programme.

Registry/source identity precedes scoped HTTP/browser use; translation/provenance contracts
precede merge publication; publication/readback checks precede A9 and any real merge/deletion
reliance. Task producer owns granular executor-sized outcomes and adapts old tasks/fixtures
rather than preserving obsolete single-source interfaces. Existing source/task review is
invalid for expanded merge/linked-discovery scope; fresh intent review and regenerated tasks
must cover A1–A9 before renewed combined approval. No implementation or real-data command
was run to produce this source.

No remaining material owner choice is hidden: the prefix-preserve-both decision is settled.
Exact module factoring, helper names and canonical digest serialization remain bounded
implementation details. Source-origin/digest stability, schema-specific reference coverage,
file/DB interruption recovery and main-only readback after removal are assumptions requiring
A2/A7–A9 evidence, not proven claims. If inspection finds an unknown identity-bearing payload
that cannot be safely translated, stop that affected conversion with the exact field/version
and return material scope alternatives through review; do not fabricate a broad migration.

Prepared Python/Node/local Chrome availability and all application checks are **NOT RUN**
under source-only authority. Missing prerequisites are reported, not auto-installed or waived.
Later bounded isolated checks use ADR-0004; no paid/live workflow/Paseo service or real owner
worktree deletion is required for acceptance. Actual data merge/deletion requires its own
current authority; this source never deletes sources. Keep source available until verified
main readback; after a successful merge, stopping/reverting the viewer does not undo imported
history. No automatic rollback/deletion of imported or unrelated rows/files is in scope.
Failed required proof blocks affected reliance and returns material changes for renewed
source/task review, not weakened acceptance or blind retries.
