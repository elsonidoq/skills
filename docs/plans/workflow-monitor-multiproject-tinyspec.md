# One workflow monitor for multiple projects — TinySpec

## Outcome, provenance and authority

The beneficiary is the owner monitoring workflows across local projects: one prepared
web server, one port and one website, with project selection before the existing run
selection and workflow view.

Original owner intent (verbatim):

> The web server currently assumes it is run within a project that forces me to run one website per project. And that's annoying because I need to open many ports and I need to launch many web servers and stuff like that. I think a great modification would be to just one web server that knows where the projects are (~/projects, configurable, of course via a parameter when the webserver is launched) and is able to load everything from each project. In the webpage you are able to select the project from the project list and then within the project see the workflows that are running or have been run. Do not make any modification in how the website actually shows the workflow, this is just a modification to be able to run just one server and monitor all projects

Explicit subsequent owner decisions: discover **immediate child projects only**, not
recursively; **“no backwards compatibility”** (replace `--project`; old CLI and URLs
need not work); **TinySpec → Tasks, planning only**. The owner additionally requires a
fresh independent intent-focused read-only TinySpec review **before task production**.
That is a current additional review requirement, not a claim that TinySpec normally
requires separate source approval.

The parent planning brief supplies the bounded direction: default `~/projects`, a
`--projects-root` override, project-scoped URLs/API, independent project readers/cache,
and preservation of graph, Details, history and polling. The concrete discovery,
empty-store and routing mechanics below are repository-derived implementation choices,
not quotations or additional owner mandates. They remain subject to source review.

This is source preparation only, based on clean `main` at
`4e5c319acb5badd7290ff066ed9ea0f557e44cd3`. No artifact approval, application acceptance or
implementation authorization is implied. Separate tasks, parent inspection, the required
independent intent review and combined owner approval remain outstanding. The intended
implementation executor configuration is `.pi/workflow-executor.json`; the task producer
must read it before decomposition. The saved source-producer binding
`openai-codex/gpt-6.1-sol` / medium is not an implementation assignment.

## Scope and constraints

Include the launcher, immediate-child discovery/selection, project-qualified HTTP and
browser navigation, per-project observation state, focused regression coverage and the
necessary launch/navigation documentation update in
[the canonical monitor README](../../workflow_monitor/README.md). This source does not
change that operative README; its usage update belongs to implementation tasks.

Keep the existing per-project workflow display and interpretation unchanged: graph/layout,
node/edge Details, labels, metrics, status/acceptance semantics, run ordering/filtering,
followups, pagination, freshness and 60-second polling. Adding the project selector and
resetting obsolete project state is in scope; redesigning the workflow viewer is not.
Running and past runs remain the same recorded inventory, not a new live-only feed.

No runtime/writer changes, recording/schema changes, migrations, backfills, store creation,
workflow launch/control, global aggregate workflow view, recursive search, watchers,
project-registration persistence, dependency upgrades, new framework, automatic setup,
install, build or deployment. No old `--project` or unscoped run/API compatibility layer.
Existing stored data remains untouched. Normal prepared package launch must work without
changing into a monitored project; this is not new installation machinery.

Retain numeric loopback binding and existing request/response protections, closed DTOs,
fixed startup assets and safe canonical-worktree/store identity checks. Browser inputs
select only server-discovered opaque project references; they never supply filesystem
paths. Do not expose project absolute paths, Git internals or raw discovery errors in HTTP
responses. Do not weaken safety to make a candidate readable.

## Grounded evidence and dependency choice

Evidence is from the baseline above; spans refer to that revision.

| Inspected source | Observation → design consequence → acceptance |
| --- | --- |
| [`__main__.py:23–35`](../../workflow_monitor/__main__.py) and [`pyproject.toml`](../../workflow_monitor/pyproject.toml) | Required `--project` constructs one Reader; console entry point already exists. Replace only project binding with a root registry, retain assets/port and safe Uvicorn options; prepared launch outside a target cwd is A1. |
| [`reader.py:37–113,228–250`](../../workflow_monitor/reader.py) | Reader verifies canonical Git root/admin identity, tolerates absent initial store, pins a present database and checks on reads. Discover actual worktree roots (including linked worktrees), retain Readers across polls, let an absent store appear later without creating it: A2/A3/A5. |
| [`reader.py:175–217`](../../workflow_monitor/reader.py), [`test_reader.py:58–135,192 onward`](../../workflow_monitor/tests/test_reader.py) | Metric append boundaries and DB identity are per Reader; existing tests cover append versus substitution/read-only access. Never share or periodically recreate those bindings: A3/A5. |
| [`app.py:408–460,463–547`](../../workflow_monitor/app.py) | One closure owns Reader, last-safe snapshot and last-success time; all endpoint selection is unscoped. Move that observation state to each project and resolve it before every existing run operation: A3. |
| [`app.py:78–102,550–598`](../../workflow_monitor/app.py), [`test_http.py`](../../workflow_monitor/tests/test_http.py) | Raw run-component validation, fixed assets, closed errors and same-origin loopback checks already exist. Adapt shell validation for a project prefix without broad HTML fallback or path opening: A4/A5. |
| [`web/src/main.tsx:27–42,84–126`](../../workflow_monitor/web/src/main.tsx), [`test_navigation.spec.ts`](../../workflow_monitor/web/tests/test_navigation.spec.ts) | Routes use displayed run IDs; selection has fetch/layout generations, paging and history. Include project identity in location, API requests and stale-result guards; preserve the renderer: A4/A6. |
| [`web/tests/execution_fixture.py:43–45,211`](../../workflow_monitor/web/tests/execution_fixture.py) and [`web/playwright.config.ts`](../../workflow_monitor/web/playwright.config.ts) | Existing temporary real Git/store fixture serves production assets through the actual app/Reader; existing Playwright uses local Chrome. Extend that seam to two projects rather than add infrastructure: A6. |

Version evidence: [Python metadata](../../workflow_monitor/pyproject.toml) and
[lock](../../workflow_monitor/requirements.lock) pin Starlette 0.46.2 and Uvicorn 0.34.0;
HTTP-test dependency is httpx 0.28.1. [Web metadata](../../workflow_monitor/web/package.json)
and [lock](../../workflow_monitor/web/package-lock.json) currently resolve React/React DOM
19.3.1, ReactFlow 12.12.0, ELK 0.11.1, Vite 7.3.7, TypeScript 5.9.3 and Playwright 1.64.1.
These are declarations/resolutions, not a claim that every tool is installed or checks ran.

**Repository-derived choice:** reuse existing standard-library filesystem/Git inspection,
Starlette routes, React location/history state and polling, with no new dependencies.
Existing [monitor guidance](../../workflow_monitor/README.md), actual routing/Reader code
and focused fixtures adequately cover this ordinary selection/wiring change. New internet
research is skipped: there is no new dependency API, layout algorithm, concurrency model
or version-sensitive technique to establish. No new reusable external recommendation was
found that requires a technical-guidance write. Refresh only if implementation encounters
a consequential dependency unknown; do not silently substitute recollection for evidence.
The README remains the technical owner, discoverable via [documentation routing](../index.md).

Applicable accepted decisions, read in full after the [whole ADR index](../decisions/index.md):
[ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md) requires
future executable tasks/check permissions to be authorization-neutral; phase status belongs
in the approval record, and later explicit launch authority must be carried into worker
briefs. This source's preparation status is not a permanent execution prohibition.
[ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md) permits bounded
isolated fixture databases/local servers under shared runtime defaults, not changes to
unrelated data/services or automatic global setup. A6 uses those existing defaults;
actual required checks remain required. Neither ADR overrides this run's source-only scope.
The whole associated [memory index](../../memory/MEMORY.md) contains only parent-notification
guidance; it affects routine reporting, not the product design. No memory write is needed.

## Bounded approach and observable behavior

### Root and project inventory

Replace `--project` with optional `--projects-root DIRECTORY`, defaulting to the current
user's expanded `~/projects`. Retain required `--assets`, existing port default and safe
server options. Expand `~` and resolve the configured root at startup. A missing,
unreadable or non-directory root stops launch before binding, with a diagnostic naming
`--projects-root` and how to choose/create the intended directory; never create it.
An empty valid root is a usable server with an honest empty-project state.

Discover only regular immediate child directories that are themselves canonical Git
worktree roots, using the existing Git-root verification rather than assuming `.git` is
a directory. Ignore nonprojects, nested repositories below those children and symlink
children (the latter is a cheap server-root escape protection, not an owner discovery rule).
List all qualifying projects, even before their first workflow store exists. A candidate's
unreadable/unsafe monitor data does not take other projects offline. Serve a deterministic
label-sorted inventory of closed entries `{ref, label}` where label is the child directory
name and ref is a URL-safe opaque server-generated reference, stable across polls/restart
for the same canonical child. No browser-provided path is resolved. Unknown refs are closed
404s, not a search or fallback to another project.

Refresh discovery when the project inventory is requested; the browser requests it at
startup and at the existing 60-second cadence. No watcher or all-project snapshot scan is
needed. New qualifying children appear on the next successful inventory poll without a
server restart. Removed children cease being selectable on that poll. If a selected
project disappears, retain its address with a project-unavailable state and clear its
viewer, rather than silently selecting another project. A root read failure yields an
honest unavailable/error state, not an authoritative empty inventory. Revalidate discovered
bindings before use; removal/replacement/retargeting must not silently bind an existing
project session to successor data. Keep existing worktree/admin/database/metric identity
protections; a changed binding requires corrective operator action/restart, not automatic
Reader replacement. Error responses remain sanitized.

### Per-project observation and HTTP boundary

A small in-memory registry owns each project's long-lived Reader and observation cache.
Refactor the app's current snapshot closure into project-local state (Reader, last-safe
sanitized result, last-success timestamp). Resolve the registry entry first, then reuse
existing snapshot/normalization/minimization/paging/followup behavior inside that project.
Only read workflow data for addressed projects. Identical run IDs, opaque run refs,
snapshot tokens or record refs in different worktrees must never cause cache merging,
last-safe fallback, pagination, metric or followup lookup across projects. Do not change
the underlying run/record identity contracts merely to qualify their HTTP context.

Use this bounded route shape:

- `GET /api/monitor/v1/projects` → `{monitor_version: 1, projects: [{ref, label}]}`.
- `/api/monitor/v1/projects/{project_ref}/runs` and the existing run suffixes below it:
  `/{run_ref}/snapshot`, `/{run_ref}/history`, `/{run_ref}/records/{record_ref}` and
  `/{run_ref}/followups`, with existing snapshot/cursor/limit semantics.
- Browser shells: `/`, `/projects/{project_ref}` and
  `/projects/{project_ref}/runs/id-<percent-encoded actual run ID>`.

The server must validate shell structure/raw encoded components before decoded slashes can
be mistaken for extra path segments. Run ID decoding remains exactly once. Serve only the
inventoried `index.html` for those shell shapes and existing fixed assets; APIs, malformed
paths and unknown assets must not acquire an HTML catch-all. Old unscoped routes are not
supported and must not route to an implicit project.

For a project with no store, show no recorded runs without creating `.coherence` or a DB;
its runs inventory can return an empty list. On later polls the same Reader can bind its
first legitimate store and show runs. A valid empty store behaves similarly. Unsupported,
unsafe or unreadable stores retain honest closed unavailable/unsupported behavior. A read
failure after success may retain that project's sanitized last-safe snapshot with the
existing warning/freshness semantics; it cannot borrow another project's data or present
successor data as the original binding.

### Browser selection without a renderer change

At `/`, show the project list and ask the user to select a project; do not guess one.
Selecting a project pushes its project URL and loads that project's runs. A bare project
URL uses the existing newest-run rule, replacing that location with its scoped run URL
when nonempty; otherwise show the empty/no-runs state. Within a project, retain sorting,
filtering, exact run lookup and selection-preserving polling. Project labels/selection
must be visible above the run list so the owner knows which project is being observed.

Project/run direct opens, reloads and Back/Forward restore the addressed project and run.
Unknown/removed project or run addresses stay in the address bar with an honest unavailable
state, never silently substituting another selection. Project switches clear obsolete runs,
run filter, graph/Details, history/lineage, pending layout measurements/positions and
selection-local viewport state. Scope all API calls, including followups and both history
paths. Invalidate asynchronous run-inventory, snapshot, history and layout results by
project **and** run selection, including when two projects have the same run ref. Preserve
within-project status-only refresh behavior. Project discovery failure must not replace a
selected project with another. Workflow rendering functions/layout and graph/Details
content remain unchanged.

## Acceptance and smallest sufficient verification

These are production requirements for later tasks, not claims of checks executed now.
Carry each relevant criterion into task-local REQUIRED checks and worker/reviewer briefs;
record exact commands, actual results and any unavailable prerequisite. One composed
check can satisfy several mappings without duplicate runs.

| ID | Observable pass criterion | Smallest sufficient REQUIRED evidence |
| --- | --- | --- |
| A1 | One prepared launch defaults to `~/projects`, accepts `--projects-root`, and serves multiple projects on one numeric-loopback port without a target-project cwd. Invalid roots stop with actionable launch errors; an empty root starts. No legacy `--project` support or automatic setup. | Adapt actual launcher tests for default expansion/override and Uvicorn arguments; a bounded prepared-package/module subprocess check from an unrelated temporary cwd reaches the intended root/app (no install). Inspect help and documented command. |
| A2 | Inventory includes immediate canonical child worktrees (including a linked worktree and one with no store), excludes nonprojects/nested/symlink children, and has stable refs/deterministic labels. A new child appears and a removed child disappears on the next successful inventory request/poll. | Permanent focused tests of the actual discovery helper with small temporary Git worktrees, plus an HTTP inventory request through the actual registry; no mocked directory list as the sole oracle. |
| A3 | Every run API and fallback is project-local, even for identical run IDs/refs. First legitimate store creation is seen on a later read without restart; an unsupported/unreadable project does not break a healthy one. | Actual two-project registry/HTTP tests with distinguishable store facts and colliding run identities: selected snapshot, representative paged/record/followup lookup and failed-read last-safe/freshness remain from the addressed project; test absent-store → first store using the retained Reader. Reuse unchanged Reader safety tests for unchanged internals. |
| A4 | Project selector, scoped direct opens/reload/Back/Forward, run selection/filter/history/followups and 60-second polling work without stale cross-project results. Empty/unknown/removed selections are honest. The existing graph and Details presentation is unchanged. | Extend the existing production-asset navigation fixture to two real project stores; one composed Playwright navigation check observes distinct project data (including the same run ID), switching and history/direct reload, representative Details/history, and a delayed old-project response discarded after switching. Advance the existing timer in the test rather than wait a minute. Existing representative renderer checks remain applicable after fixture/route adaptation. |
| A5 | Read-only store/worktree/metric safety, fixed assets, raw path handling and protected loopback API boundaries remain effective for the new project routes. Browser path/traversal/unknown-ref input cannot open another directory; replaced bindings are not silently adopted. | Adapt focused HTTP/launcher/Reader boundary tests to scoped routes, including a raw encoded run ID containing a slash, malformed/extra-segment routes, unknown project ref and an unsafe/replaced project binding. Verify fixture DB/metric contents are not mutated by observation. Preserve existing Host/Fetch Metadata/header, closed error/DTO and asset-substitution assertions rather than build a new security matrix. |
| A6 | The feature is usable and documented as one server for multiple projects, with no runtime/store or workflow-renderer redesign. | Prepared-environment Python focused tests covering changed discovery/HTTP/launch seams; `npm --prefix workflow_monitor/web run build` and focused existing Playwright navigation plus affected renderer cases. Inspect diff boundaries and update canonical README launch, selection/URLs, refresh/empty states and security/rollback text together with delivery. Record two-project composed result and unchanged-view regression result, not only a generic suite pass. |

No separate prototype is justified: discovery, Reader isolation and route selection are
known bounded behavior with inspectable interfaces and permanent actual-helper tests.
The concrete expensive failure is project A's stale/cache result appearing as project B,
which isolated green helpers cannot exclude; the composed two-project production-browser
check is therefore necessary. Keep ordinary evidence inside delivery, not a
prototype/consumer/cleanup chain or exhaustive scenario matrix. Verification effort is
focused local tests plus adapting the existing fixture, not new test infrastructure.

Dependency ordering is real but small: registry/reference and scoped HTTP contracts must
exist before the browser relies on them; composed acceptance needs both. Task generation
owns executor-sized outcomes, not this source. Existing tests/fixtures that use the old
internal app binding or URLs must be adapted with the corresponding interface change,
not preserved as a compatibility requirement. Keep any additional regression optional
unless inspection exposes a concrete affected contract.

## Risks, gates and reversibility

No unresolved material product decision or explicit owner deferral remains in this source.
Ordinary implementation details (module name for the registry, safe-ref hashing helper,
React state factoring) remain open within the behavior above. Assumptions requiring
validation are stable canonical-reference generation, no-store → first-store reuse and
project-aware async invalidation; A2–A4 provide their oracles. Discovery can involve many
local directories, but no scale/performance target was requested: avoid reading all stores
on every inventory poll and do not invent project caps, eviction or throttling.

Required browser/build checks depend on the prepared Python/Node packages and existing
local Chrome. Their availability/execution is **NOT RUN** during source-only preparation;
missing prerequisites must be reported before affected acceptance, never installed as a
side effect here or represented as waived. Bounded offline fixtures/local servers in later
authorized execution use ADR-0004 defaults. No live workflow, paid-provider, deployment or
same-Mac visual evaluation is necessary to prove this selection-only change; unrelated
historical visual/live gates are not claimed satisfied by it.

A failed isolation/safety/composed check blocks reliance on the affected seam. Correct
within scope, or return material behavior/dependency changes for affected source/task
review and renewed approval; never weaken acceptance after failure. Tests are permanent
and remain applicable to the delivered code/environment; rerun only when changed state
invalidates their evidence. Rollback stops/reverts the monitor application only: there is
no data migration to undo and no writer/runtime to restart.
