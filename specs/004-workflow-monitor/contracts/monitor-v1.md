# Monitoring contract v1 — proposed, not implemented

[Data model](../data-model.md) owns record identities/emission points; [spec](../spec.md) owns outcomes.
This version replaces the retired `wf_*`/executable-YAML design. It is not an existing API.

## Producer boundary

Only the existing script writer creates `execution_monitor_runs` and `execution_observations`.
Record closed run descriptions and phase-specific facts, never arbitrary SDK event dictionaries.
No private prompt/result/summary/error/command/finding/question/answer content enters monitoring rows.
Recording failure emits a safe warning, never blocks execution or replaces its original exception.
No observer dependency, network, subprocess or new package is needed for the emitter.

Optional `monitor` input provides explicit public-safe presentation and a declared correction reference;
invalid optional metadata loses that facet with a warning, not the work. It grants no permissions.
Optional operational `review_base` is separate: the future reviewer must actually inspect the specified
valid ancestor range or report the actual review error. The viewer cannot select/change that option.
The script remains sequential, with a fresh independent reviewer and no automatic correction loop.

## Reader and mapping boundary

- `reader.open_snapshot(project, run_ref, cursor)`: private SELECTs from the fixed existing worktree DB.
- `mapping.normalize(snapshot)`: phase definitions, task annotations, occurrences, milestones and
  explicitly resolved local correction references; no saver deserialization or legacy history adapter.
- `public.minimize(normalized)`: construct closed public objects explicitly; never serialize raw rows.
- `http.create_app(reader, assets)`: same-origin read-only JSON and fixed production assets only.

Viewer imports no Authority/Store/Engine/PiAdapter/SDK/controller/publisher entry and cannot start one.
No startup DDL, implicit migration, projection writes or installation. Database absence is `no_store`;
no description-v1 runs is `no_monitored_runs`. An initial registration failure can leave no marker:
the producer warns, but the viewer cannot identify that run as eligible or promise its history. A marked
supported candidate with corrupt/missing data is unavailable/incomplete, not silently hidden or mapped
from old rows. Unknown recording versions
are unsupported, not decoded by guessing. Existing `wf_*` history is neither exposed nor converted.

Canonical worktree and its Git-admin identity are selected by trusted CLI once; browser input cannot
select paths, databases, roots or SQL. Refuse symlink/path escape, unsafe private-file ownership or
cross-worktree substitution; recheck file identity when reopening/changing stores, not as a repeated
full-environment attestation. Open URI mode=ro, query_only and a SELECT-only SQLite authorizer;
parameterize run/cursor filters. No ATTACH, extension loading, checkpoint, DDL, saver or write PRAGMA.
Normal SQLite WAL/SHM bookkeeping may occur; do not require nonexistent historical sidecars or repair
unsafe ones. Never use immutable/nolock on an active database. Authoritative rows must not change.

Fetch within short thread-owned snapshot transactions; close before HTTP/layout. Use ordinary busy/error
handling and pagination, not fixed 250/500ms admission. No transaction held across requests. No copied
main-DB snapshot that loses WAL changes. Supported columns are explicitly selected; raw execution
`details`/`error` are private and not forwarded. Unknown observation kind retains opaque identity/order
and an unsupported badge, never its arbitrary payload or raw name. Completeness counts include it.

Read process identity locally only when available to distinguish live/stopped/unknown; never signal,
acquire the writer lock or reconcile. Fresh read time is not proof the runner is making progress.

## Public DTOs

All objects closed, no arbitrary `metadata`, `details`, reason text or extra payload. IDs/cursors are
opaque, typed and scoped to the selected worktree/run. Safe hashes are validated before display.
Optional reviewed presentation is inert text (labels 80 characters, summaries/descriptions 240);
invalid/missing text uses fixed generic labels. No private task description fallback or regex promise
of secret detection. No arbitrary URL/path fields or file/transcript/output downloads.

- **Envelope:** monitor_version, snapshot_ref/revision, selected run ref, observation, warnings,
  inventory and pagination. No raw database/source objects.
- **Observation:** observed_at, last_success_at, last_recorded_at, source_seq, read_state and separately
  observed runner state with unknown reason. No fabricated timestamps, heartbeat or projection cursor.
- **Run:** opaque ref, safe label, baseline/result SHA if available, stored state, description version,
  requested executor identity (known supported values only, otherwise unknown), recorded start/end,
  recording completeness and review acceptance summary with actual base/head. No raw error text.
- **Phase:** ref, fixed role/description, possible branches, pre-recording flag, occurrence counts and
  status summary. Pre-start intake/ownership checks are not fabricated executed visits.
- **Task:** opaque ref, safe brief presentation, declared prerequisite refs and actual order declaration.
- **Occurrence:** ref, source run ref, phase/task refs, role worker|fixing_worker|reviewer|non_model,
  milestone/outcome, recorded timestamps, check ordinal/exit code, checkpoint no_change/baseline/head,
  review approved/finding_count/base/head and safe parent refs where applicable. Fields are typed,
  phase-specific and nullable with fixed unknown reasons; no model response or findings text.
- **Edge:** ref, endpoints, type possible_flow|task_prerequisite|recorded_next|phase_occurrence|
  execution_milestone|declared_correction|reviewed_range, fixed label and resolution state. A declaration
  is not observed causality or authorization. A recorded sequence is not an effect-proof transition.
- **Unknown record:** opaque ref, source run, sequence, unsupported/incomplete code; payload withheld.
- **Inventory:** total phase/occurrence/observation counts, supported/unsupported/hidden counts,
  loaded sequence ranges and next cursor. Every hidden item remains retrievable.

Current task/run rows may corroborate latest state, never fill missing history. Resolve acceptance from
actual independent review outcomes and range coverage; worker/checkpoint/task completion alone is
insufficient. Review findings block acceptance even if commits exist. A later linked correction never
rewrites the original failed run. Incomplete/contradictory records yield unknown acceptance.

## HTTP and assets

Proposed trusted CLI: `python -m workflow_monitor --project CANONICAL_WORKTREE --assets BUILD_ROOT
[--port PORT]`. Numeric 127.0.0.1 only; no database/host/plugin overrides, reload, proxy trust or debugger.
Production build root serves only known asset files, no directory listings, symlinks, sourcemaps or
arbitrary filesystem access. Startup does not build, install or start execution.

| GET route | Result |
| --- | --- |
| `/` and fixed build assets | Static application only; no embedded private/run data. |
| `/api/monitor/v1/runs?cursor=&limit=` | New-contract run summaries, next cursor. |
| `/api/monitor/v1/runs/{ref}/snapshot` | Phase/task graph, initial history, complete inventory and observation. |
| `/api/monitor/v1/runs/{ref}/history?snapshot=&cursor=&limit=` | Next history page at the same watermark; expired snapshot asks client to refresh. |
| `/api/monitor/v1/runs/{ref}/records/{ref}?snapshot=` | One minimized detail record. |
| `/api/monitor/v1/runs/{ref}/followups?snapshot=&cursor=&limit=` | Explicitly linked local correction/review occurrences for in-graph expansion, with source-run attribution. |

Follow-up traversal uses explicit references, cycle detection and run-scoped queries, not broad project
scanning. Paging counts disclose unloaded records; no new universal byte ceiling or silent truncation.
Normal request/page sizing is an implementation detail, not an execution gate. Snapshot pages cannot
silently mix watermarks; refresh on expiry/conflict. No arbitrary search, SQL, path or URL endpoint.

GET only (HEAD for static assets); no write/control routes or websocket. Require exact bound Host:port
and API same-origin Fetch Metadata/custom header; reject foreign Origin, ambiguous inputs/traversal and
cross-origin preflight, enable no CORS. Browser origin defenses are not authentication against malicious
same-UID clients. Request input never selects a worktree or triggers a model/process action.

Use no-store, nosniff, no-referrer and frame denial; CSP allows only local scripts/connect/workers/styles,
no eval/inline script/remote assets. Library-calculated geometry styles may be allowed without accepting
stored styles. Text rendering only; no stored HTML/Markdown/link/component execution. No cookies,
browser persistence, service worker, telemetry or private-profile reuse.

Errors: closed code/public_message/retryable plus safe observation; fixed messages only. Bad input400,
unknown404, expired/conflicting snapshot409, unsupported422, unavailable503. Logs contain safe codes,
not request content, raw IDs, exceptions or tracebacks. Disable access/debug leakage, including actual500
paths. No private text in response headers, links, assets or logs.

## UI invariants

Left run list, one graph right and brief detail panel/drawer. Switching runs replaces the selected root;
only explicit local followups expand into that graph. Distinct model execution nodes survive collapsing;
hidden failures/waits retain badges/counts. Every record can be found/revealed, including earlier rejected
review and its fixing/rereview lineage. No answer/edit/connect/delete/launch/control affordance.

Stable identities, keyboard/click node and edge selection, pan/zoom/organize; layout changes coordinates
only. Preserve selection/viewport/positions on status polls; discard old-run layout results. Gray possible
flow/prerequisite edges are visually distinct from recorded sequence and declared followups. About-two-
second updates are approximate; errors retain the last safe view with warnings. Stop viewer only to
roll back; never mutate/reset/restart runtime state.
