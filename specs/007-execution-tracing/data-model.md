# Factual trace data model

Derived from [specification entities](spec.md#key-entities-include-if-feature-involves-data).
See [plan](plan.md) for boundaries and [research](research.md) for evidence. This is a proposed
logical payload, not a new database or required task schema.

## Existing owners

`execution_run_inputs` retains contract/executor/current authority. `execution_history.seq`
orders private operation facts. `execution_review_executions` and append-only
`execution_review_attempts` own review/fixer identities, findings and range. The graph saver
owns control state, including paused questions. Do not copy these tables or rewrite old rows.

## Trace event

Use existing history columns `run_id`, nullable `task_id`, `kind`, `state`, `details`,
`recorded_at`. New trace-specific details have a version and stable event ID. Derived events
from old operational rows use their table/row identity instead of a new duplicate append.

Required meaningful fields depend on kind, not universal metadata eligibility:

| Kind | Meaningful content and relations |
| --- | --- |
| Worker question | Actual question; invocation/tool-call/request IDs where known; intended receiver; task/worker attribution. |
| Owner question | Actual ask_user or terminal wording, meaningful context/options, actual tool-call identity; known routing context. |
| Resolution | Original question ID; actual answer/resolution, selection/freeform/comment; actual responder class (owner/coordinator/unknown); delivery outcome. |
| Submission | Actual worker/fixer report and relevant evidence content or explicit evidence gap; producing invocation ID. Submission is not acceptance. |
| Validation | Actual command/check, exit/outcome, meaningful output; task/repair and known producing invocation/checkpoint relation. |
| Rejection/review | Actual findings, reason and coverage gaps; reviewed range, execution ID and predecessor; keep earlier attempts. |
| Failure/retry/escalation | Actual failure or unsuccessful outcome, inspected diagnosis/action when supplied, prior/new invocation identities and available executor facts. No inferred cause. |
| Checkpoint/reference | Verified SHA/parent/owned paths and associated checks/producer, or explicit no-change/unavailable; known issue/PR/code URLs. |
| Capture gap | Affected boundary/interval, known loss or unavailable facts and corrective action. Never synthesize events. |

Worker identity uses actual opened session/logical worker attribution if available, not requested
model alone. Public payload excludes private session paths. Unknown values are explicit null or
`unavailable` with reason; zero counts require known complete coverage of that event class.

A question has factual stages: requested → answered/resolved → sent, or requested → cancelled,
unanswered, denied, failed/unknown delivery. Denial is actual answer content, never permission.
An answer observed but not delivered remains retained, with unsuccessful delivery; it must not
be called an unresolved *owner choice* when the actual choice is known. A pending question with
no result cannot receive a synthetic answer. Event IDs survive bridge re-drain and run reopen.

Ordering is stored sequence with source-local sequence/identity where available. Interleaved
workers pair by explicit IDs. Arrival order is not total real-time causality. Owner events during
triage can have a contextual request link; never equate the owner question with the worker's
wording or infer answer equality. Unknown task or causal link stays unknown.

## Execution trace projection

A trace snapshot identifies qualified issue, run ID, fixed source boundary, actual implementation
outcome, coverage by event class, events, counts and supported references. Count logical question
or attempt identities, not each lifecycle row. Include previous failed attempts and all review
attempts, not just current task state or latest review. Preserve worker-claimed evidence separately
from runner-observed checks, independent-review verdict and owner acceptance (`NOT VERIFIED`
unless actual evidence exists).

Project only facts needed for later assessment. Exclude raw prompts, environment, transport
envelopes, credentials and unrelated files. Do not drop ordinary Q/A or failed details to make
a short body. Resolve relevant submitted evidence while accessible; an unresolved local path is
a coverage gap. GitHub content, not an opaque digest or old worktree location, is the durable owner.

## Publication operation

Store publication facts in existing history under a distinct kind. Logical fields:

- exact qualified target and optional known delivery PR;
- actual run-scoped authority reference and allowed operations (never credential values);
- stable snapshot ID/source boundary and part index/identity;
- intended content digest and content or reproducible source references sufficient for recovery;
- actual returned comment ID/URL and independent readback result;
- linkage verification and concrete error/correction where applicable.

Lifecycle: prepared → sending → confirmed, or failed/uncertain/deferred. A sent response alone
is not confirmed. A snapshot is delivered only when all assessment-relevant parts and required
discovery links are read back. Distinguish **delivery confirmation** from **capture coverage**:
a confirmed partial trace is useful but not complete feature evidence. New events on resume
produce a new snapshot/update with links to previous evidence; do not erase earlier failure.
No durable publication snapshot includes its own publication-history rows recursively.

Existing worktree lock serializes this controller's publication. No network call holds a database
transaction. Marker plus intended-body equality supports reconciliation, not server-side
idempotency. A remote duplicate/conflict or incomplete scan remains uncertain.

## Assessment proposal

Ephemeral analysis output has selected issue/PR, evidence URLs, observed facts, supported cause
or labelled hypothesis, missing evidence, reusable versus issue-specific classification, proposed
existing owner/change and limits. It creates no analysis DB/ledger. Recording a result or changing
labels requires separately scoped tracker authority; skill edits and implementation are never
an automatic consequence.

## Compatibility and rollback

New payload versions are additive. Readers tolerate absent/unknown trace kinds and explicitly
report unsupported coverage. Historical operational history stays readable and is not backfilled.
No migration, table deletion or legacy replay. Disabling the new integration leaves retained rows
and remote comments intact; existing runtime continuation rules still govern operational recovery.
