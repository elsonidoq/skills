# Workflow monitor simplification — tasks

## Approval record

Preparation authority: owner-selected planner + TinySpec after the Astra mockup. Fresh
source intent review completed; the run-label finding was resolved by the owner's
**Show existing identifier + folder** choice and source correction. This task production
uses saved `tinyspec-tasks`: `openai-codex/gpt-6.1-sol`, medium, unchanged.

Baseline: `4a04536b6b000f5061b49671afbc0d44b53d581b`. Source A1–A5 is the
[separate TinySpec](workflow-monitor-simplification-tinyspec.md). The exact proposed
visual reference is `b7d55c24fb45deb29622ee097ec812309d7727d3`,
[`workflow-monitor-mockup.html`](../workflow-monitor-mockup.html), SHA-256
`9f1b151b93c7d1d4158faa9b6cbd35c0edc587f17d43095bcd533b91b3ccf8ee`.

Correctness and simplicity reviews and combined owner approval of the exact
mockup/source/tasks remain pending. Neither this checkpoint nor a returned producer
call grants design approval, implementation authority or application acceptance.

## Shared worker brief

Read the entire [TinySpec](workflow-monitor-simplification-tinyspec.md). It is requirements
truth. The [executable JSON](workflow-monitor-simplification-tasks.json) contains exact
owned paths, task-local REQUIRED pass conditions and deterministic commands. This human
presentation is not a second requirements source. Commands run from the repository root;
semantic pass conditions are not shell commands.

Pass this selected executor path unchanged:
`/home/dev/.paseo/worktrees/0zfm1a0e/curvy-skunk/.pi/workflow-executor.json`.
The producer read its actual JSON: workers `openai-codex/gpt-6.1-terra`, medium;
fresh reviewers `openai-codex/gpt-6.1-sol`, medium. The planning model is not a worker
assignment. Outcomes below each pass with completed prerequisites and their own checks;
the configured sequential executor also avoids overlapping writes to shared UI/tests.

- Preserve read-only recording/history, exact refs and qualified routes, privacy/security,
  semantic topology, 60-second polling, watermarks/paging, stale fetch/layout rejection,
  ReactFlow interaction and measured ELK layout. No runtime/descriptor/persistence change,
  migration/backfill, task-file reconstruction, generated summary, naming subsystem,
  new dependency, general harness or admission framework.
- UI edits require explicit owner approval of the exact mockup first. Mechanically copy its
  visual CSS and applicable shell/JSX structure, per the
  [README boundary](../../workflow_monitor/README.md#visual-reference-and-ui-change-rule)
  and [readable reference](../workflow-monitor-mockup.jsx). Do not copy fixture data,
  coordinates, generated engine, fixture adapter, proposal banner or mockup-only styles.
  Any later unforeseen styling adjustment returns to mockup and owner before app changes.
- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md): use current
  scoped launch authority, not historical pending labels, to determine allowed work.
  Executable instructions are authorization-neutral. Returned execution is not a successful
  check, checkpoint, accepted task or accepted review. T003/T006 explicitly preserve this.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md): bounded isolated
  fixtures/local checks, ordinary scoped corrections and necessary isolated/in-project
  dependency setup during authorized implementation need no repeated permission. Use existing
  lockfiles and documented paths; do not add automatic startup installation machinery.
  Preserve material scope/product, manual, security/data/credential, paid and external-action
  gates. No global installs, credential/auth changes, uncontrolled resource expansion,
  service changes, deployment, push, real-data preservation/removal or unrelated deletion.
  Browser downloads and other separately scoped external effects retain their actual gates.
  Inspect failed expensive calls before a targeted retry; never blindly relaunch.
- Apply the [task checkpoint contract](../../skills/memory-handling/references/task-commit-contract.md):
  executable workers do not stage/commit; the runner verifies and checkpoints explicit owned
  paths before later mutation. Preserve unrelated bytes and all applicable actual checks.
  Record minimal meaningful assertions/results and limits in the existing return, not STATE
  or a new evidence ledger. No check/manual disposition can be inferred from return or color.

## Ordered outcomes

- [ ] T001 Expose safe original run labels and live worktree basenames without changing routes.
  - **Depends**: none
  - Own the public/qualification seam, its Python/API tests and matching README text.
    REQUIRED A1: meaningful/generated raw identifiers; nullable live basename versus
    preserved/no-binding unavailable; list/snapshot/cache consistency; collisions and
    unchanged opaque routing; no absolute path/private payload. Pass actual helper and
    closed HTTP tests before browser reliance. No stored-recording change.

- [ ] T002 Use faithful retained task titles and complete inert work text.
  - **Depends**: none
  - Own `taskTitle`, affected Details/history, coupled graph/execution/chain fixtures/tests
    and matching README text. REQUIRED A2: retained-label/excerpt/ellipsis/missing cases,
    meaningful prose beginning “Task”, original full inert text and stable task/correction
    numbering. Run helper tests as well as build: TypeScript's existing `include: [src]`
    does not itself admit the test fixtures. Replace obsolete fixture `summary` only where
    needed; no reconstruction or shell redesign.

- [ ] T003 Project semantic execution states to exactly four existing color classes.
  - **Depends**: T002
  - Own `graphFor` presentation, graph/execution tests and matching README semantics.
    REQUIRED A3 helper/node boundary: pending/running/success/failed only; waiting and
    unknown remain truthful red text; returned rejection stays green with changes requested.
    Preserve node identities/endpoints/relation evidence and independent acceptance.
    Existing failed CSS is sufficient here; uniform edge styling belongs to T005.

- [ ] T004 Display and filter original identifier plus folder using stable separate route identities.
  - **Depends**: T001
  - Own rail/heading formatter and Run DTO consumer, navigation/multiproject tests,
    necessary existing production fixture support and matching README text. REQUIRED A1
    browser boundary: identical rail/heading, generated identifiers, honest unavailable
    folder, stable collision-safe qualifiers, local filter and unchanged exact routes,
    selection/poll/Back/Forward. This is usable before the full shell copy.

- [ ] T005 Mechanically copy the approved visual shell while preserving measured graph interaction.
  - **Depends**: T002, T003, T004
  - Own shell/CSS and necessary measurement fallback support, coupled existing browser
    selectors/fixtures and README presentation. REQUIRED A3 edge boundary/A4: exact copied
    CSS/class structure, four-chip legend, one solid edge style even selected/focused,
    initial closed Details/Close/full width and stacked layout. Actual production rendering
    must preserve measured bounds, pan/node/attached-edge movement, auto-pan, zoom/Controls,
    initial/explicit Fit, viewport/moved positions through selection/Close/polls and stale
    fetch/layout guards. Keep evidence visible; disclosures are T006. Compare copy and
    record only binding differences; no independent styling.

- [ ] T006 Disclose secondary evidence without hiding material warnings or acceptance.
  - **Depends**: T005
  - Own Details/evidence disclosure wiring, coupled existing browser assertions/fixtures
    and README behavior. REQUIRED A5 plus composed A1–A4: complete inert description,
    state/blocker/findings/material qualifications lead; metrics scopes/session separation,
    coverage/checks/checkpoints/reviews and selected/correction paging remain accessible.
    Closed disclosures must not hide real stale/read/partial-plan/rejection warnings.
    Verify beyond-page-one acceptance, not just loaded history. The existing owner same-Mac
    interactive final acceptance is a REQUIRED post-result manual gate, separate from
    mockup approval and synthetic browser evidence. Report pending if it cannot be run.

## Proof selection and execution prerequisites

No prototype or research chain: false attribution/privacy, misleading color and interaction
loss are known bounded seams. Permanent actual-helper/API/browser assertions prove them at
their first usable boundaries. Reuse the existing
[technical guidance](../../workflow_monitor/README.md#graph-layout-technical-guidance),
package declarations and lockfiles: ReactFlow 12.12.0, React/ReactDOM 19.3.1, ELK 0.11.1,
Vite 7.3.7, Playwright 1.64.1 and TypeScript 5.9.3. These are inspected lock resolutions,
not installed-capability claims or new runtime version mandates. No new dependency API
needs internet research. Changed mapping/DTO/layout invalidates affected proof only.

Observed during authoring: Python 3.12.3, Node v24.21.0 and npm 11.19.0 respond to version
queries. `/usr/bin/google-chrome` resolves to an executable local Chrome; no browser was
launched. **The selected checkout lacks `workflow_monitor/.venv/bin/python` and
`workflow_monitor/web/node_modules`.** Python tests/build/browser checks were not run.
Before T001 relies on Python evidence, use or prepare the isolated environment matching
`workflow_monitor/requirements.lock` at the documented path and verify imports. Before
T002–T006 rely on web evidence, use or prepare the locked web tools at the documented path
and verify local Chrome launch. Authorized implementation may perform this ordinary bounded
isolated/in-project setup under ADR-0004 without a separate setup task, handoff or renewed
owner permission. Do not silently substitute interpreters or edit configs. Report unavailable
setup and the precise correction only when it genuinely falls outside existing authority;
retain separately scoped browser-download/external-effect gates. This is not automatic
startup installation. The task-authoring/review stage remains no-install; source-stage
no-install wording does not remove later routine implementation authority. Capability failure
is not a pass or a new startup ceremony.

`test_graph.spec.ts` imports actual graph/layout helpers. Execution/navigation/multiproject
suites use the existing disposable `execution_fixture.py`, actual production HTTP and built
assets; it imports runtime test support under its explicit PYTHONPATH and uses offline
adapters, not models. Keep its `admit` checks, privacy/readback assertions and scoped teardown.
`test_chain` exercises the production renderer through Vite; observation/history/lineage use
closed fixture APIs. They complement, not replace, production HTTP/browser acceptance.
The existing Playwright configuration uses one worker, Chrome and loopback fixtures on
4174/4175; free those fixture ports without stopping unrelated services. Build assets before
production-fixture tests. No broad runtime suite, real recordings or persistent server needed.

T005's copied sizing can expose the old 180px fallback in main.tsx despite the 208px CSS;
verify measurement before layout reliance rather than copying fixture coordinates. T006's
same-Mac gate requires owner access to the final production build; browser output cannot
satisfy it. Missing browser/manual evidence leaves affected acceptance pending.
