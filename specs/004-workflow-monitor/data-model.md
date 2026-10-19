# Monitor data model v1

Derived from [approved spec](spec.md), [research](research.md) and [runtime schema owner](../../docs/coordinate-implementation-schema.md). This is an observer model, **not new runtime DDL**. Exact external fields are in [monitor contract](contracts/monitor-v1.md). Never deserialize saver checkpoints or open an authoritative writer.

## Identity and provenance

Use tagged identities, never display-position/task-name-derived identity:

| Entity | Stable internal identity | Relations / invariant |
|---|---|---|
| Worktree | canonical Git worktree/admin identity | Fixed at server start, one `.coherence/workflow/workflow.sqlite`; no browser-selected project/path |
| Run | SQL `wf_runs.run_id` | All queries additionally bound to selected run; API returns opaque run ref mapped only in this process |
| Definition | run + retained workflow raw SHA256 | Parsed canonical config digest must equal `wf_run_bindings.binding.config_hash`; Engine combined hash is separate |
| Definition node | run + definition hash + exact node id | One finite anchor per actual definition node, whether visited or not; not a task container |
| Visit | run + graph operation UUID | `wf_operations.kind='graph'`; logical node/visit index is validated metadata, not primary identity |
| SDK invocation | run + sdk-turn UUID | Optional task/role/attempt/session relations from actual intent/result; never assumed one per graph visit |
| Semantic record | run + SQL event UUID or typed table PK | Distinct type/shape from visit/definition; some records have no graph operation |
| Task | run + task contract id | Declared depends are prerequisites only; correction has explicit original task relation |
| Question/input | run + gate/input PK | Distinct park/accepted/queued/delivered/continuation-entered/request-observed facts, no content |
| Check evidence | run + evidence_id + item_id | Immutable status/applicability/revision/environment facts, not raw output/args |
| Review/finding | run + review_id + finding_id | Base/head/rereview/correction disposition remains historical |
| Metric revision | original event/op-derived metric ID | supersedes relation, null reasons, zero and four binding provenance classes |
| Snapshot | process-random token + database identity + watermark | Short-lived sanitized in-memory DTOs; no DB transaction across HTTP requests |

Browser IDs are bounded opaque encoded/HMAC refs over typed keys (ephemeral server key); raw stored arbitrary strings are not routing paths/URLs. Restart may invalidate refs; stable domain identity lets UI warn/reselect, not cross-wire history. Identifiers that could contain paths/secrets are represented by opaque refs; approved presentation may supply separately validated safe labels. Safe UUID/commit/hash values may be shown when type/length validated. No raw paths/session filenames/approval refs/OS identities are public.

## Required new-contract sources

One source `kind=config,section=monitor-workflow/v1` and one `kind=config,section=monitor-presentation/v1` in the admitted contract. Section is a convention; the runner hashes the **whole file**, not that section. Presentation v1 is a closed JSON document:

- `monitor_version:1`.
- `workflow_sha256`: exact retained workflow raw digest.
- `tasks`: exact original task IDs to `{label, executive_summary}`; approved brief text, not arbitrary `task.outcome`. Label<=80 Unicode characters; summary<=240, normally one sentence. No required LLM generation.
- `nodes`: optional exact definition node IDs to approved descriptions<=240; supported handler/version default descriptions cover the shipped inventory. Unknown custom handler uses generic “Unsupported recorded stage”, not invented business explanation.
- `safe_evidence_labels`: optional declared opaque reference labels; never target filenames/URLs or content gateways.

Reject unknown keys, duplicate IDs, excessive sizes, control characters, invalid hashes and task/definition mismatches. Presentation text must be reviewed explicitly as public-safe; a schema/regex cannot determine arbitrary secrets. Raw values from DB are never substituted when presentation unavailable. Detect corrupt new pins with explicit unavailable/unsupported state, not legacy conversion. Strict YAML forbids tags/aliases/duplicates and arbitrary imports; bound input262144 bytes/node128, matching shipped validation bounds. Never execute it.

Retain committed source objects before the actual app build. Match raw hash at resolution and actual SQL canonical config hash; Git blob lookup uses validated revision/path, no hooks/textconv/external diff, no shell interpolation, no worktree writes. Stored contract source paths remain private resolver inputs. Cache only verified content identities. A run with no monitoring marker is not eligible and its history is not exposed.

## Graph and execution edge derivation

1. Build finite actual definition anchors/allowed outcome transitions from retained YAML. Distinct gray/dashed definition links are possibilities, never claims of execution.
2. Enumerate **all** run graph operations and events ordered by SQL seq. Visit index suffix parsed only against known node IDs; unknown operations remain opaque unresolved recorded visits, not dropped.
3. For each graph visit, reconstruct completed trace prefix as Engine does: exact node/handler/profile/skill/config hash/operation_id. Recompute operation args hash for `{config_hash: wf_runs.config_hash,node: actual_node,trace: prefix}` and compare intent input hash and event proof. Result outcome must be permitted by pinned node transitions. Only a verified chain justifies a recorded transition to the next matching visit; sequence alone gives “recorded before”, not causal transition.
4. Intent without completion is an attempted/incomplete visit; **not confirmed failure**. A later block/alarm may attach causally only through exact references. Result `ok` in an implement node means worker stage returned, not final acceptance. Result `repair` from verify is failed-check/repair-needed, not success because handler completed.
5. Owner-input interrupt executes before graph intent; `wf_question_parks` supplies explicit park semantic record linked to original graph op and definition gate. Show waiting on anchor plus that record, never invent graph UUID/visit. Saver state is not read. A recovered identical op returns same visit UUID, not a duplicate.
6. Task associations require actual task_selected/SDK/check/checkpoint/question/correction references. Reconstruct sequential selected-task interval only where those proofs agree. Select can have no current task or precede selection event; authority/custody/review/terminal nodes may be run-level. Uncertain associations null with reason. Task-spanning nodes accept plural refs.
7. Prerequisites connect task annotations attached within the same graph, visually distinct from definition/recorded/semantic links. They never determine trace prefix or execution order.

Every event is covered by a known semantic decoder or opaque unsupported-record badge/ref/count. Unknown event payload is not exported. Visible history windows are views over a declared complete inventory, not silently truncated graphs. Collapsed history aggregates counts by failed/waiting/blocked/unknown, exposes hidden count and paged reveal/find by stable ref. Layout copies cannot mutate domain identities/endpoints/types.

## Recorded status, not observer authority

Store status dimensions separately: `visit_phase`, `milestone`, `disposition`, `controller`, `evidence`, `freshness`; do not flatten to a universal done boolean.

- Definition anchor without visits: gray “Not started”. Finite loop, no infinitely unfolded planned visits.
- Active SDK/process/graph intent **and** live controller evidence: blue “Running/worker active”. Controller stopped/dead/unknown overrides active-progress claim; historical operation remains incomplete with interruption/unknown warning.
- Confirmed check fail/explicit failed outcome: red “Failed check/visit”. Preserve failed historical record after later repair success. Insufficient/missing/stale evidence: warning “Not verified”, not red failure.
- Question parked pending: amber “Waiting for owner”. Answer accepted: amber “Accepted; delivery pending”. Queued original vs actual `original_answer_entry` and continuation-entered/request-start/completed shown separately. No answer/control content or button.
- ORPHAN_PROCESS, unmet gate, unresolved finding, unsupported/uncertain recovery: amber “Blocked” with distinct typed reason; confirmed final_failure red. Unknown reason remains unknown; no inference from exception prose.
- Completed implementation stage: green “Worker finished”; successful current recorded checks green “Verified”; checkpoint receipt green “Committed/read-only complete”; independent review pass green “Review passed at <head>”; exact `workflow_accepted` reference green “Finally accepted at <head>”. These are separate badges and references, never interchangeable.
- Acceptance current only when latest acceptance is not superseded by recorded blocker, pending question/control stop, active alarm, unmet gate/unresolved finding or newer recorded task/checkpoint/review head inconsistent with acceptance. Conflicts/incomplete evidence warn “Acceptance not established”, no authority/check rerun. Preserve historical accepted event independently.

Descriptions are trusted versioned handler dictionary plus approved presentation. Current shipped mapping: intake validates source/task intake; authority checks capabilities/approval; custody checks writer/process custody; select chooses next task/end; dispatch chooses implementation/repair; implement produces work; repair addresses diagnosed original failure; owner-input-* parks that role; continue-* continues original conversation; verify checks REQUIRED evidence; checkpoint records focused Git; review/continue-review judge original full range; authorize-correction admits scoped correction; complete audits final acceptance; failure represents blocked terminal. Inventory still comes from YAML, not this description list.

## Metrics and freshness

Metric values use `{value,source,unknown_reason}`; value null requires nonempty reason, zero is valid. `supersedes` selects current revision per invocation, never summed across revisions. Distinguish requested profile, SDK runtime observation, final request observation, provider acknowledgement. Unknown acknowledgement stays null. Reopen/session epoch change does not join counters. Non-agent stages have no fabricated sessions/tokens. Costs remain unknown if source segment does not retain them; no recalculation from current prices.

Snapshot records observation wall/monotonic time, per-run SQL high-watermark, projection cursor/lag if present and controller observation independently. Original events often have **no timestamp**; seq is order only, use null/reason. SDK/check timing can be actual recorded nanoseconds. Freshness timestamp is not execution timestamp. Clock skew/unknown age is explicit. Failed poll retains last sanitized data plus visible last-success/read-error warning, never replaces it with fake empty success. No raw state.json/event payload forwarding.
