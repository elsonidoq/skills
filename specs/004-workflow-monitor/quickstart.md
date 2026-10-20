# Proposed monitor setup and acceptance guide

**Not delivered commands or passing application results.** See [plan](plan.md), [contract](contracts/monitor-v1.md)
and [required validation](contracts/validation.md). Historical launch IDs, external scratch descriptors
and approvals are not current prerequisites or execution permission.

## Before implementation

Review the revised spec/tasks and explicitly approve T001 recording plus bounded original-range review
support. Future executor stays `openai-codex/gpt-6.1-sol`, effort `medium`. Verify actual available Python,
Git/SQLite, Node/Pi SDK and relevant project tools; do not install, refresh auth, reload or substitute a
model automatically. Preserve unrelated work, existing writer ownership and normal Git configuration.

T001 adds the small recording seam, focused tests and actual runtime operating/schema documentation.
It is delivered and validated **before** the new application-build run. Do not expect existing
`execution_runs`/`execution_tasks` or legacy `wf_*` rows to supply new history.

## Application build

After T001 acceptance and separate application execution approval, execute T002/T003 as one fresh run
through `scripts/coordinate-implementation`, using the ordinary tasks object, `--tasks`, `--executor`,
`--project` and a fresh `--run`. Root proposal metadata is not an execution envelope. For the application
build, select only those approved task records; do not rerun T001 inside the same build. The runtime
CLI has no task-subset flag: prepare a separate ordinary task file containing T002/T003, with T002's
already-satisfied T001 dependency removed and its prerequisite checkpoint noted as context. Copy the
matching T002/T003 safe entries from `monitor-presentation.json` into root `monitor.tasks`; the future
recorder retains those brief labels/summaries, not the private task work descriptions.

Use ordinary application `pyproject.toml`/lock and web `package.json`/package-lock. No external frozen
tree, descriptor hash, custody inventory, manifest or launch receipts. Existing environments may be
used after relevant compatibility checks. Dependency installation, network and browser provisioning
need explicit separate permission; tests/startup never install. Do not assume historical `/tmp` setup
or exact versions from old research remain available. Record actual selected compatible locks during
implementation; dependency/API changes receive affected review.

Proposed delivered app checks (NOT RUN now):

```sh
python -B -m unittest discover -v -s workflow_monitor/tests
npm --prefix workflow_monitor/web run build
npm --prefix workflow_monitor/web test
```

Browser tests use the installed locked local test tool/browser; no automatic download, private browser
profile, CDN or sandbox-disabling workaround. Build output/caches use ordinary ignored or temporary
locations. Generated assets are not committed; manifests/locks/source/tests are.

## Early usable viewer and own-build observation

After the T002 focused checkpoint, the operator may separately authorize a read-only viewer launch
using the delivered app environment and production assets. Proposed interface, confirmed by the future
application README before use:

```sh
python -B -m workflow_monitor --project /absolute/viewed-worktree \
  --assets /absolute/production-assets --port PORT
```

Use the actual numeric `127.0.0.1:PORT` origin. No dev server, reload, remote binding, public service or
execution controls. Viewer startup neither builds assets nor starts/resumes execution. An independently
operator-owned viewer can remain open while the runner performs genuine T003 work; task/check-owned
servers/browsers must close normally before their checks end.

Select **that same application run**: inspect earlier T002 records retrospectively and later T003
work live. Retain safe run/occurrence references and record/read/display timing in ordinary acceptance
output. No fixture/different-run replacement or artificial work to extend the live interval. Missing
same-run observation is SC-006 NOT VERIFIED.

## Reviewing fixes in the graph

An independent review finding defects remains visible. A separately authorized fresh correction task
file may include root context:

```json
{
  "monitor": {
    "correction_of": {"run_id": "original-run", "review_execution_id": "actual-review-occurrence"},
    "tasks": {"fix": {"label": "Fix review defects", "executive_summary": "Address the reported defects."}}
  },
  "review_base": "ACTUAL_FULL_ORIGINAL_BASE_SHA",
  "tasks": [{"id": "fix", "description": "Explicitly approved correction work and relevant checks"}]
}
```

These are proposed T001 interfaces, not current CLI capabilities. The reference declares the review
relationship; it never grants permission. `review_base` must actually drive the independent review's
range; it is not a cosmetic monitor field. Default review still covers only that run's baseline→head.
Get actual occurrence IDs via the delivered script status/history interface; browser opaque refs are
not raw recording IDs. Do not guess IDs from names or read private transcripts to find them.

Expand explicit local followups inside the selected root graph: original reviewer, fixing-agent
execution, checks/checkpoint, rereviewer. Verify each actual range and run badge. A correction-only
review is not full-range acceptance. Original failed run remains failed; lineage review acceptance is
shown separately. No automated correction or expensive retry loop is introduced.

## Validate, report and disable

Follow SC-001–006 in the validation contract. Real isolated script emission/readback and concurrent
reader checks supplement deterministic fixtures; real browser tests cover graph interaction and private
output exclusion. Offline adapters are not live-provider evidence. Report missing capabilities or
permissions exactly, without turning setup into an owner-question courier or execution gate.

After T003, fresh independent review checks the full application range. Observe its final result
separately; no task check depends on a future review result. Keep all actual failures and any explicitly
linked corrections. No application completion/acceptance is claimed by this guide.

Stop only the viewer to disable observation. Preserve the runtime database/history, Git, partial work
and private records. Never reset/convert old rows, repair projections, abandon runs from the viewer,
signal the writer or restart legacy execution. No global configuration/skill changes are part of this
proposal, so it needs no global activation or `/reload`.
