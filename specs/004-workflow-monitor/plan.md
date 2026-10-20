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

## Outcome-based delivery

### T001 — Recording and correction-review foundation, before the app run

Deliver additive metadata/observations at existing execution boundaries, explicit correction relation
and bounded actual original-range review support. Include emission/readback, failed-check retention,
review findings, question delivery/error paths, recording failure noninterference and existing runtime
regressions; update operating/schema owners for actual delivered behavior. No application launch or
automatic review/fix loop. This is separately approved implementation work, not authorized now.

After validation and a focused checkpoint, record the delivered recording-version/runtime revision.
Only then start a fresh run containing **T002 and T003**. T001 is not retroactively part of that
recorded application build; its history is not substituted for self-history.

### T002 — Early usable selected-run monitor

Deliver safe reader/mapping, local production API/assets and graph/details/polling together with
focused reader/browser/concurrent-writer checks. Already expose recorded occurrences, failure history,
unknowns and review nodes; not a disposable task-status UI. Normal app manifests/locks accompany source.
At its focused checkpoint the operator can inspect that same application's earlier steps and keep an
independently owned read-only viewer open during genuine T003 work.

### T003 — Complete review/fix history, composed acceptance and operation

Complete correction-lineage expansion/reveal, adversarial privacy/error checks, stale/liveness behavior
and composed review→fixing-worker→checks/checkpoint→rereview tests. Include actual same-build live
observation and operating documentation. Tests/docs remain with this coherent faithful-observation
outcome, not a separate evidence/cleanup task. Do not create artificial work to keep the run alive.

Final fresh independent review follows task delivery. T003 cannot require the future final review to
have passed before it can finish. Operator acceptance observes that final outcome afterward; unresolved
findings require separately authorized linked corrections and full-range rereview, not auto-retry.

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

Future executor remains owner-selected `openai-codex/gpt-6.1-sol`, effort `medium`. Verify actual usable
capabilities before their stage, preserving current terminal authority, sole-writer lock, unrelated work,
normal hooks/signing, explicit path checkpoints and fresh independent read-only final review. No
catalog/manifest/receipt/containment/binding admission is revived.

Current scope is artifacts only. Review revised sources/tasks and explicitly approve recording plus
review-range changes before T001; approve app execution/setup/observer launch before applicable work.
Historical `specification-approval.md`, prerequisite tasks/approval and overall review stay historical.

Stopping the viewer disables observation only. Preserve progress/history/Git/partial work. No downgrade,
cleanup of old rows, projection rebuild, runtime restoration, process signalling or legacy restart.
If recording is unavailable, the script continues and monitor acceptance remains NOT VERIFIED.
