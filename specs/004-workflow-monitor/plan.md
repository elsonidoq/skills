# Implementation Plan: Read-only Workflow Monitor

**Status:** revised proposal, not implementation approval. Requirements: [spec](spec.md).
Owner authorized direct artifact revision in this session and explicitly retained fixing-agent nodes.
Historical approvals/research setup do not establish current execution permission or acceptance.

## Recommended architecture

1. **Existing script + small recording seam:** keep `execution_runs`/`execution_tasks`, sequential
   tasks, actual project checks, focused Git and fresh independent review. Add retained descriptive
   run metadata and append-only boundary observations as specified in [data model](data-model.md).
   This supplies missing history; no legacy graph execution, saver, proof system or generic telemetry.
2. **Separate read-only application:** short parameterized `mode=ro` SQLite snapshots → closed mapping
   → minimized versioned DTO → same-origin polling. No imports of runner/controller/SDK/writer objects,
   projection publication or database mutation. Writer-side recording never runs in the viewer.
3. **One graph:** retained script-phase anchors, task prerequisite annotations and actual occurrences,
   including model execution nodes. Review, explicitly linked fixing execution, checks/checkpoint and
   rereview remain navigable in this graph with source-run attribution and actual review ranges.
4. **Local UI:** React/React Flow, ELK for organized layout, Starlette/Uvicorn for closed GET routes.
   Keep the existing library choices as proposals; conventional manifests/locks and explicit setup
   authority replace the frozen-tree descriptor protocol. [Research](research.md) preserves useful
   official references without claiming the old scratch installations are current dependencies.

## Boundaries and compatibility

Only new recording-contract runs in the viewed worktree. No conversion/import or legacy incomplete
fallback. Retired `monitor-workflow.yaml` is a non-executable retirement notice, not the script's
configuration. `monitor-presentation.json` supplies example public-safe labels for the revised tasks;
no workflow digest or source-binding proof is required. The recording description is retained with
runs so later code/presentation changes do not rewrite history.

Best-effort observations cannot gate normal execution. Missing records warn, never fabricate visits.
Ordinary progress/check/Git errors keep their existing behavior. Privacy is enforced before storage
of monitoring facts and again before HTTP exposure. Arbitrary worker text/errors/findings/commands
remain private. Requested executor identity is not observed/provider-acknowledged identity.

The current engine stops on review findings. Corrections remain separately owner-authorized fresh
runs, optionally carrying a `monitor.correction_of` reference. A small explicit `review_base` option
is proposed for original-range rereview; it changes the actual review diff/prompt, not merely a label.
It does not change the task baseline, writer ownership or automatically launch fixes. Its exact scope,
recording changes and tests must be approved before implementation. No full finding-disposition ledger.

## Proposed source layout

```text
runtime/coherence_workflow/
  monitoring.py                 # proposed closed descriptor/emitter; not executable workflow
  store.py / engine.py          # additive tables and actual execution boundaries
  verification.py / pi_adapter.py # per-check and coarse question observations
  cli.py                        # optional correction-review context, honest status as needed
runtime/tests/                  # focused emission/error/privacy/range regressions
workflow_monitor/
  reader.py / mapping.py / public.py
  app.py / __main__.py
  pyproject.toml / dependency lock
  web/package.json / package-lock.json / src/ / tests/
  tests/ / README.md
```

Keep modules small as needed; this is a seam map, not a mandate to create every module. App owns its
manifests/locks; runtime dependency/SDK changes are not needed. No new dependencies solely for recording.
Existing ignore rules may need a narrow application-manifest exception, never blanket ignore removal.

## Bounded outcome delivery

The owner rejected three coarse milestones because long-agent compaction/drift risk needs smaller
verifiable work units. [Tasks](tasks.md) and matching [JSON](tasks.json) now define 16 bounded outcomes;
this is not a quota or a new Standard planning ceremony. Tests and relevant docs remain with each outcome.

- **T001–T006, separate foundation:** additive closed storage/description; engine task/worker/terminal
  boundaries; actual checks/checkpoints; question delivery; real original-range review; CLI ID lookup and
  abandon retention. Accept this foundation before starting the application run. No future app result is
  required to verify these producers. Runtime changes remain separately approval-gated.
- **T007–T010, early usable app:** read-only snapshot reader, faithful minimized mapping, guarded production
  HTTP/launcher and usable browser graph. At T010 checkpoint the operator can inspect THIS application's
  earlier records and keep a separately authorized independently owned observer open.
- **T011–T016, genuine later work in that SAME app run:** stable layout/polls, snapshot-bound history
  navigation, explicit correction resolver/range acceptance, lineage graph, honest liveness/read recovery,
  and shippable local package/operating acceptance. No artificial work to extend observation.

Prepared split: ordinary foundation input T001–T006, then fresh ordinary app input T007–T016. Remove
only T007's satisfied T006 dependency, placing accepted foundation SHA/recording version in T007's own
brief. Retain internal dependencies/owned paths/checks/REQUIRED items and copy matching public-safe
presentation to root monitor.tasks. No unsupported subset flag or automatic run orchestrator.

Final fresh independent review follows T016, covering the full application baseline→head. T016 does
not require that future result to finish. Operator then inspects its actual recorded outcome; findings
require separately authorized linked correction executions and actual full-original-range rereview.
No task/checkpoint/worker success alone establishes application acceptance.

## Validation and operation

[Validation contract](contracts/validation.md) maps SC-001–006 to focused tests. Ordinary Python,
Node/build and browser commands replace registered PythonAnswer and its deadline workarounds. Use
available dependencies or request the actual missing setup permission; no automatic install/download,
auth refresh or global changes. Ordinary temporary output and normal teardown are sufficient; no
source-copy hash custody, dependency-tree inventory gate or repeated environment attestation.

Short read transactions, SQLite locking, mode=ro, query_only and parameterized queries preserve active
writer progress. Exact 250/500ms budgets are not product requirements; tune only if observed contention
requires it. About-two-second display is the owner's approximate target, not a percentile SLA. No
universal payload/file ceiling is introduced; paginate history without silent omission.

Keep numeric-loopback Host/Origin defenses, safe text/CSP, no CORS/control/write endpoints or raw file
serving. Standard local trusted-operator scope is not protection from a malicious same-UID process.
Reader failures preserve last safe state with warnings, never repair or restart execution.

## Approval, ownership and rollback

Future executor is owner-selected Terra class, effort `medium`; no concrete provider/model ID was
supplied. Resolve the actual binding before approved launch; do not invent it or edit active configuration. Verify actual usable
capabilities before their stage, preserving current terminal authority, sole-writer lock, unrelated work,
normal hooks/signing, explicit path checkpoints and fresh independent read-only final review. No
catalog/manifest/receipt/containment/binding admission is revived.

Current scope is artifacts only. Review revised sources/tasks and explicitly approve recording plus
review-range changes before T001–T006; approve app execution/setup/observer launch before applicable work.
Historical `specification-approval.md`, prerequisite tasks/approval and overall review stay historical.

Stopping the viewer disables observation only. Preserve progress/history/Git/partial work. No downgrade,
cleanup of old rows, projection rebuild, runtime restoration, process signalling or legacy restart.
If recording is unavailable, the script continues and monitor acceptance remains NOT VERIFIED.
