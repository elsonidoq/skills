# Monitor data model v1 — proposed, not implemented

[Specification](spec.md) owns requirements; [monitor contract](contracts/monitor-v1.md) owns boundaries.
Existing `execution_runs` and `execution_tasks` remain latest-state records. Never reinterpret their
row order, overwritten details or legacy `wf_*` records as new-contract history.

## Minimal additive storage

Two proposed tables in the existing worktree database; no new database, workflow engine or saver.
Names below are the implementation target, not a claim that these tables already exist.

### `execution_monitor_runs`

- `run_id`: existing run identity, primary key.
- `recording_version`: 1.
- `description`: closed JSON containing retained descriptive script phases/possible branches,
  description version and runtime source revision (null with reason if unavailable), ordered task
  IDs/dependencies, optional reviewed public-safe labels/brief summaries, requested executor identity,
  and optional declared correction reference.
- `started_at`: actual recording timestamp; not retroactively reconstructed intake time.
- `runner_identity`: private PID/start/boot identity for read-only liveness observation, if available.

The description is captured from the current script's maintained phase description and admitted task
list, not parsed from retired executable YAML or resolved from whatever files exist at viewing time.
Focused engine tests exercise the actual described boundaries. It is not a second executable definition.
No full task contract, source file bodies, check commands, owner input, prompts or private filesystem
paths enter this record. Optional safe presentation is copied from explicit `monitor` metadata, not
inferred from `description`/`outcome`. Generic labels are valid when presentation is absent.

### `execution_observations`

- `seq`: database-generated monotonic primary key; order of recording, not proof of causal completion.
- `run_id`, `recording_version`.
- `occurrence_id`: stable unique phase execution identity assigned before a start; reused for its end.
- `phase`: known script phase identifier.
- `task_id`: nullable; graph review and terminal phases are run-level.
- `kind`: closed milestone enum, e.g. `started`, `returned`, `passed`, `failed`, `interrupted`,
  `question_requested`, `answer_returned`, `answer_sent`, `delivery_failed`, `abandoned`.
- `recorded_at`: actual emission time, not provider/tool execution time.
- `facts`: closed, phase-specific safe fields: execution role, check ordinal/exit code, baseline/head,
  no-change flag, review approval/finding count, parent execution occurrence for questions/checks,
  fixed error category, and recording-gap indicator. No arbitrary details/reason/metadata field.

Phase occurrences: task preparation/manual gates, worker invocation, each runner check, checkpoint,
independent review and terminal outcome. Each actual worker/reviewer `prompt()` call has its own
occurrence, even when the same role recurs. A task association is not an occurrence identity.
Terminal review is successful only after actual response validation; malformed/rejected responses
remain failed/incomplete. Retain a valid rejected review's count/range before the runner raises.

## Emission and optionality

| Existing point | Observation needed |
| --- | --- |
| `Engine.invoke` after ordinary run start | Description; terminal occurrence start; tasks known before they execute. Intake and lock acquisition predate this recording and are labelled pre-recording, not fabricated visits. |
| Task preparation / `manual_gates` | Preparation start/result, gate ordinal/outcome, no gate content. Preparation failure before worker creation remains visible. |
| Immediately around worker/reviewer `prompt` | Distinct execution start/return/failure/interruption with role; reviewer range and parsed outcome/count. Worker return is not verification. |
| `run_checks` around each actual command | Check start and exit/failure/interruption, emitted before failure propagation; command text/output withheld. No requested checks means not applicable, not verified. |
| `FocusedGit.checkpoint` call boundary | Start/result with actual baseline/head and `no_change`; failure after uncertain Git work is not a fabricated commit. |
| Wrapped question callback and `PiAdapter` send | Requested, terminal return, sent/failure; SDK question links to its execution, gate question to its gate. No answer text or answer-consumed event. |
| Run finish and explicit new-run abandon | Actual terminal state/error category/head; abandonment appends without erasing prior failure. |

Observations use short independent writes with the existing sole writer; never a transaction held across
model execution, terminal input, checks or Git. Do not alter existing progress semantics or error paths.
Recording exceptions, including optional table/description setup failures, warn through safe fixed
diagnostics and do not replace an execution error or veto work. If writing later recovers, append a gap
marker; if it never recovers there may be no durable gap marker. If initial registration fails entirely,
the run cannot be identified as eligible by the viewer; the producer warns and its monitor acceptance
is NOT VERIFIED. Missing ends, a corrupt registered description or a latest-state/history mismatch are
incomplete, not evidence that every missing event is detectable. No replay, transcript scraping or synthetic repair.
New-contract history is useful observation, not an exactly-once/effect-proof guarantee.

## Corrections and actual review coverage

Optional input context (not new startup linter checks):

```json
{
  "monitor": {
    "correction_of": {"run_id": "prior-run", "review_execution_id": "recorded-review-id"},
    "tasks": {"fix": {"label": "Fix review defects", "executive_summary": "Address the reported correctness defects."}}
  },
  "review_base": "FULL_ORIGINAL_BASE_COMMIT",
  "tasks": [{"id": "fix", "description": "Owner-authorized correction work"}]
}
```

`monitor.correction_of` is a declared relationship, **not permission or proof of causality**. The recorder
copies it without a new catalog/receipt gate. The reader resolves it only against a supported reviewer
occurrence in this same worktree; dangling/conflicting references are visible unresolved relations.
Fixing executions retain their own run/task/occurrence IDs. A task in an explicitly declared correction
run is labelled fixing worker; unrelated workers are not retroactively reclassified by heuristic.

`review_base` is different: it proposes a bounded operational option, necessary when rereview must cover
the original range rather than only the new correction commits. The future engine must actually use
that base in the independent review prompt/diff and record the actual base/head. Resolve it as a commit
and require it to be an ancestor of the run baseline using normal Git behavior. Invalid/unrelated input
fails the affected review with a corrective diagnostic, not a telemetry/admission gate. Default remains
the run baseline. Run baseline/ownership do not change. No automatic fixing, retry, state replay or
review result injection. This option requires explicit implementation approval along with recording.

The viewer marks original-range acceptance only for an approving, findings-free independent review
whose recorded range covers the required original base through the displayed current head. A later
correction-only review is labelled exactly that, not full acceptance. Newer linked work or incomplete
review invalidates a claim of current acceptance; historical review success remains visible. An earlier
run can stay failed even though its linked correction lineage later has a passing full-range review.

## Graph and public identity

One finite anchor per retained defined phase; task annotations/dependency edges; separate occurrence
nodes including all model executions; milestone details attached by explicit occurrence references.
Graph edge kinds: `possible_flow`, `task_prerequisite`, `recorded_next`, `phase_occurrence`,
`execution_milestone`, `declared_correction`, `reviewed_range`. No edge is called a proven execution
transition merely because sequence or dependencies suggest it.

Selected run is the root. Expand only explicit local correction ancestors/descendants, fetched by those
references with cycle detection and a visited set. Attribute every node to its source run; no whole-store
merge, cross-worktree traversal or inferred relation. Layout may collapse history with counts; all
records remain reachable through paging/reveal in the same graph.

Internal identity is `(run_id, occurrence_id)` or `(run_id, seq)`, not display order. Public opaque refs
are run-scoped and cannot be filesystem paths. Schema-validated hashes may be displayed; other raw IDs
may be sensitive and become opaque refs. Presentation is inert text reviewed as public-safe, not secret
redaction by regex. Brief labels/summaries may retain 80/240-character presentation choices; invalid
optional presentation becomes generic/unknown without blocking execution.

## Unknowns, liveness and freshness

Show snapshot read time separately from event record time. Read-only local process identity checks may
report live/stopped/unknown; they never signal, lock or reconcile. An unverifiable identity is unknown;
an alive process is not proof it is making progress. Retain incomplete occurrences after process loss.
Unknown metrics are not zero; no metric collection/revision schema or provider acknowledgement is added.
Actual zero exit code/finding count remains zero. API request failure preserves the last sanitized view.
