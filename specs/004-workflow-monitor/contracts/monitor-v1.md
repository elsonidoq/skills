# Read-only monitoring contract v1

Status: designed, NOT implemented/accepted. [Data model](../data-model.md) supplies exact semantic rules; [research](../research.md) supplies APIs/evidence; [validation](validation.md) supplies REQUIRED proofs.

## Process boundary and named seams

`workflow_monitor` is a new top-level application, outside `runtime/coherence_workflow`. Public observer entry constructs a canonical worktree-bound reader and serves static production UI. It cannot import/construct `Coordinate`, `Authority`, `Store`, `Engine`, `Gateway`, `OwnerChannel`, `Interaction`, `Publisher`, PiAdapter, SDK host or SqliteSaver. Import-time effects, process/model launch and dynamic plugin imports are forbidden. Static app launch is distinct from execution CLI, never invokes start/resume/control.

- `reader.open_snapshot(project) -> RawSnapshot`: private backend-only fixed SQL SELECTs in bounded mode=ro transaction.
- `pins.resolve(raw_snapshot) -> VerifiedDefinition, SafePresentation`: exact marked sources, raw hashes, strict parsing and actual run-binding config digest equality. No current-YAML fallback.
- `mapping.normalize(raw_snapshot,pins) -> MonitorSnapshotV1`: source-derived nodes/visits/edges/status/metrics, explicit unknowns, complete counts and provenance. Trusted internal structs never serialized wholesale.
- `public.minimize(normalized) -> PublicSnapshotV1`: allowlist and bound every field; schema validation last, no arbitrary mapping extras. No raw text “reason” escape hatch.
- `http.create_app(reader,assets) -> ASGI`: closed same-origin GET routes, bounded in-memory sanitized snapshot cache, immutable versioned DTOs. Synchronous DB work runs on bounded thread worker, connection created/closed there; no shared connection/cursor.
- `graph.layout(topology,dimensions,generation)`: frontend-only positions/routes on copy; React Flow uses stable IDs. Layout never changes domain topology.

Separate contexts explicitly enforce absence of a viewer→runtime effect route. Versioned monitoring schema belongs to app, not existing projection schema or runner DDL. All worker-managed source/test/doc/config/lock files must be strictly <32768 UTF-8 bytes; the separately approved prerequisite adds actual byte guards without increasing transport/file limits.

## Eligible runs and pin proof

Require unique source conventions described in [data model](../data-model.md): `monitor-workflow/v1` and `monitor-presentation/v1` on kind=config sources. Load source contract from `wf_run_inputs.contract`, cross-check `wf_run_bindings` source digest against contract sources and config digest against retained strict YAML. Raw SHA of both files must match source pins, presentation.workflow_sha256 must match YAML, task IDs must agree.

Git-addressable retained bytes must exist before app run starts and remain retrievable. Prefer the actual initial task baseline Git tree; while no baseline exists, hash-verified current source is temporary observation, explicitly labelled. At baseline admission resolve committed blob; no shell, arbitrary revision expression, hook, textconv or broad history traversal. Safe source path components checked without following symlinks, and `.git`/private workflow/approval/session paths forbidden as presentation/config content. Hash mismatch, lost objects or changed actual config prevents full mapped graph reliance. Config source may point to existing accepted YAML if approved pins match; do not mutate that YAML to add monitoring fields.

No marker → not eligible; list does not expose old run records or old-run count/metadata. Partial marker/unsupported new version → eligible candidate with safe unavailable classification, not silent old-run filtering. No DB → `no_store`; no eligible rows → `no_monitored_runs`. Corrupt/future new inputs yield safe explicit failure, never migration/downgrade.

## SQL read/noninterference contract

Resolve exact canonical worktree root and Git admin read-only; reject ambient Git authority override, symlink/hardlink/private-file identity violations, wrong owner/permissions or cross-worktree binding. Inspect existing binding read-only; never instantiate Authority or create storage. Fixed DB path `.coherence/workflow/workflow.sqlite`, validated identity before/after connection; sidecars validated when present/required. Missing WAL/SHM prerequisites mean unavailable, not create/chmod/repair. Active reads never use immutable/nolock or copying just main DB.

Open URI `mode=ro`, explicit query_only and deny-by-default authorizer. Never ATTACH, DDL, write PRAGMA, VACUUM, checkpoint, backup, projection publish, extension load or saver table SELECT/deserialization. Query only required application tables/columns, all run filters parameterized. Schema support is **app schema1 plus recognized table/column shapes**, not version1 alone; additive unknown record fields never blindly decoded. Optional missing table yields explicit unknown facet only if allowed by supported shape; required missing structure unavailable.

One short deferred `BEGIN`, fetch bounded rows and liveness facts, then ROLLBACK/close before network response/layout. Busy timeout250ms and wall/VM budget<=500ms initial engineering bounds, cancellable; tuning may change only with observed same-seam noninterference proof, not weakening approximate freshness or silent omission. Cap concurrent readers and snapshot bytes; no request-driven uncontrolled full scans. SQL watermark and all rows from one snapshot; process liveness may change independently and carries observation time/unknown. Cache sanitized immutable snapshots by run/watermark/controller generation, expire promptly, discard on DB identity change. No persistent monitor DB/cache.

Load-bearing table allowlist (columns containing private JSON are parsed **privately** by closed decoders, never passed through):

| Table | Permitted semantic extraction / excluded content |
|---|---|
| wf_meta, wf_runs | supported version, run identity/config Engine hash/state; no reservation control |
| wf_run_inputs, wf_run_bindings | typed source/config/task identity for pin proof only; no approval/envelope/catalog content export |
| wf_operations, wf_events | typed IDs/kind/phase/seq; closed graph result/outcome/input-hash, SDK segment observations; no arbitrary intent/result/payload, args/env/tool/prompt text |
| wf_tasks | task ID/order/deps, baseline/checkpoint SHA and state; presentation supplies summary; no owned-path/file snapshots/contract prose |
| wf_checks, wf_gates | item IDs, recorded status/applicability/ref/revision/time; safe gate pending/approve/deny/cancel; no output/args/answer/sample paths/approval artifacts |
| wf_controllers, wf_processes, wf_alarms | liveness/custody state, opaque process/alarm refs, resolved history; no PID/path/nonce/containment identities public |
| wf_questions, wf_question_parks, wf_owner_inputs, wf_controls, wf_outbox | stage/typed binding refs/park and delivery receipts existence; no question/options/answer/message/nonce/file content |
| wf_reviews, wf_findings, wf_corrections, wf_repair_budgets | range base/head, role-independent proof presence, disposition, criterion and opaque refs, original-task/correction/budget relationships; no finding observation/action/location prose or authority JSON |
| wf_parent_preflight, wf_parent_delivery, wf_parent_attempts | supported stages and typed transport blockers/attempt counts only; no recipient/session-file/actual approval/tool receipts |
| wf_projections | publication seq only; derived files never required or written |

Unknown event kind retains opaque ref/sequence plus “Unsupported record; details withheld”; arbitrary raw kind/value may itself be sensitive, so only known kind names public. Unknown graph operation is a distinct unresolved visit with opaque identity and null definition relation. Missing/conflicting transition proof yields unresolved edge warning, not invented chain. Full coverage count includes these records.

## HTTP interface

Trusted CLI: `python -m workflow_monitor --project CANONICAL_WORKTREE --assets VERIFIED_BUILD_ROOT [--port PORT]`. No host/address/database/query/plugin/resource/auth override. Bind preselected free numeric loopback port, record actual bound port in exact-host middleware, no reload/background controller. Asset root must be independently built verified app output (not arbitrary directory server); manifest names/content hashes/types determine routes. Observer never builds/installs on startup. No broad filesystem routes, symlink files, sourcemaps, directory listing, raw DB/download/export or external detail links.

GET only (HEAD allowed for static assets with no data body). API GET requires custom header `X-Coherence-Monitor:1`, `Sec-Fetch-Site:same-origin`, exact Host `127.0.0.1:<bound-port>`, and if Origin present exact same origin. Reject duplicate/ambiguous Host, foreign/same-site/none API fetch metadata, forwarded spoofing, encoded separator/traversal/NUL, unknown/duplicate query keys, unbounded cursor/ID values and request bodies. No CORS/OPTIONS grant, websocket, write verbs or redirects. Reject unsupported headers/input before DB read. Non-browser same-UID clients can spoof headers: **not authentication or local-client isolation**.

| Route | Success shape and paging |
|---|---|
| `/`, fixed manifest asset paths | static app only; no run data embedded; no API fallback to HTML |
| `/api/monitor/v1/runs?cursor=&limit=` | envelope + eligible run summaries, bounded limit<=100, opaque cursor, explicit next cursor; never old rows |
| `/api/monitor/v1/runs/{ref}/snapshot` | envelope + full definition anchors/allowed transitions/task annotations and visit/event counts/ranges; initial bounded history window<=200 records with continuation; optional unchanged revision response still includes fresh liveness/read observation |
| `/api/monitor/v1/runs/{ref}/history?snapshot=&cursor=&limit=` | same sanitized snapshot identity, next bounded window; no long read transaction; expired snapshot409 requiring refresh, never mix watermarks |
| `/api/monitor/v1/runs/{ref}/records/{ref}?snapshot=` | one safe detail DTO and explicit typed links within graph only; selected hidden visit can be found/revealed without loading every record |

No arbitrary SQL/search/path URL. Ref lookup is bound to selected run and safe cache, cannot authorize file access. IDs/cursors are opaque length-bounded tokens; malformed400, unknown404, expired409, unsupported source/schema422, temporary read/budget unavailable503. Error body only `{monitor_version:1,error:{code,public_message,retryable},observation:{...}}`, fixed messages no interpolation. Endpoint path/query never echoed in errors/logs. Server logs allowlisted error codes/request counts only, no exception/traceback/request content; Uvicorn access logging off and sanitizing error logging mandatory.

All responses including errors: JSON correct content type/nosniff, Cache-Control:no-store; Referrer-Policy:no-referrer, frame denial and CSP. CSP: default-src none; script-src self; connect-src self; worker-src self; style-src self; style-src-attr unsafe-inline for library numeric positions only; img-src self if used; object-src none; base-uri none; form-action none; frame-ancestors none. No eval/inline scripts/HTML/remote assets. No cookies, local/session storage, service worker, shared auth or telemetry.

## Public DTO field allowlist

All objects closed; unknown fields rejected before exposure. Strings/arrays/counts have explicit bounds; canonical hashing rejects NaN/Infinity. Public IDs opaque; strings from reviewed presentation are inert text, never URLs/HTML/style/component code. Runtime-derived reason/status/kind/provider/model/effort values pass versioned known-value allowlists; unrecognized free text becomes null plus fixed reason code, never an error/metric backdoor. No “metadata:any”, “details:any”, raw message or exception field.

- Envelope: `monitor_version=1`, `snapshot_ref`, `run_ref|null`, `source_revision` (monotonic per-process revision), `topology_revision`, `observation` and `warnings` closed code/count objects.
- Observation: `observed_at` actual wall ISO time, `observed_monotonic_ms`, `last_success_at|null`, `source_seq`, `projection_seq|null`, `projection_lag|null`, `controller={state:live|stopped|dead|unknown,observed_at,unknown_reason|null}`, `read_state:current|failed|budget_exceeded`, `unknown_reason|null`. No fabricated event timestamp or controller-progress implication.
- Run summary: `id`, approved `label|null`, `spec_ref` opaque, `engine_hash`, `workflow_hash`, `presentation_hash`, `recorded_status` enum, `acceptance` enum/ref/head|null, observed start/end nullable reasoned values, historical failure/wait/unknown counts. Same-spec runs have distinct identities.
- Definition node: `id`, approved label, description, `node_type:code|gate|agent|terminal|unsupported`, supported role|null, `task_refs[]`, `visit_count`, `hidden_counts`, status summary. Definition ID stays distinct from visit ID.
- Visit: `id`, `definition_ref|null`, `logical_index|null`, `operation_ref`, `task_refs[]`, `phase:intent|completed|unsupported`, `outcome` known enum|null, `milestones[]`, `disposition`, `started_at/ended_at` observed values+reasons, `evidence_refs[]`, `relation_refs[]`, `warnings[]`. No raw handler output.
- Semantic record: `id`, known `kind` enum or unsupported, seq, optional visit/task/invocation refs, typed stage/disposition, safe refs, nullable observed timestamp/reason. **Not a visit** merely because displayed in graph.
- Edge: `id`, `source`, `target`, `type:allowed_transition|recorded_transition|task_prerequisite|semantic_relation|definition_visit`, known outcome/relation label|null, `proof_refs[]`, uncertainty flag. No inferred execution order from prerequisite. Semantic and definition association connectors never masquerade as execution.
- Detail: repeats safe entity fields plus milestone/check/gate/review/correction/question-stage/metric arrays of closed typed summaries. Each evidence ref opens only another minimized record, never raw file/transcript/output. Commit refs are validated SHA text, no filesystem links.
- Metrics: integer/finite number/null observations with source and unknown reason; four independent binding observations; invocation/session opaque refs, retry/repair counts only where recorded, supersedes/current flag. Non-agent nulls and observed zero preserved.
- Inventory: definition/visit/semantic totals, supported/unsupported counts, loaded ranges and next cursor. Every omitted-from-window item must remain retrievable/revealable, or response fails explicit budget error; no count pretending all loaded.

## UI and compatibility invariants

Run list stays left; one selected-run graph right, details panel/drawer within it. Switching run replaces graph, no merged views. Narrow width uses collapsible left rail and detail drawer, not a second primary task/workflow screen. Native mouse/keyboard selection, pan/zoom, legend, explicit organize, search/reveal and finite definition anchors are REQUIRED design behavior; no answer/pause/cancel/edit/connect/delete controls. Focus descriptions and text/icons supplement colors. Recovered current badge never recolors historical red visit green.

React Flow grouping and ELK cycle breaking are visual only. Layout worker receives minimized graph, not private data; stable viewport/selection preserved across status polling, stale generations ignored. A hidden failure/wait remains on aggregate with count, and find/reveal brings it back in this same graph. Pagination/windowing cannot claim completeness unless inventory and record access prove it.

Monitor API versions independently of runtime/projection schema. Unknown monitor version fails closed with incompatible-client warning; no silent downgrade. Server restart/expired refs require explicit refresh/reselection. New missing/corrupt/incompatible records fail safe while preserving last sanitized view and honest freshness; observer never repairs data. Rollback stops only viewer, retains runtime DB/Git/records and normal execution authority, never starts legacy or resets state.
