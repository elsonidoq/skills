# Control state and data ownership

This is a design, not a database migration. Requirements remain in [spec.md](spec.md).
[Plan](plan.md) owns architecture; [research](research.md) owns dependency evidence.

## Graph state

Use ordinary typed dictionaries and standard LangGraph serialization. Keep runtime objects
(adapter, subprocess, locks, open SQLite connection, credentials) out of checkpoint state.
No message-history reducer or custom serializer is needed.

| Entity | Minimal values and relations | Owner / invariant |
| --- | --- | --- |
| Run | stable run ID/thread ID, original input reference, backend `langgraph-v1`, task IDs/dependencies, accepted checkpoint references, current wave, selected phase | Graph control; original contract/executor/authority remain in existing private run inputs. No repeated transcript/history in graph state. |
| Task execution | task ID, current phase, invocation/result reference, selected session reference, claimed-path/history reference, check outcome, focused checkpoint reference | One task owns its paths. Result-map reducer merges distinct task IDs. A conflicting update to the same active task is a coordination error, not last-write-wins acceptance. |
| Invocation | opaque internal invocation ID, task/role, requested executor, prior invocation relation, saved session reference, terminal status/result reference | Existing private history. Retain `started` before dispatch, terminal result before reliance. Unknown terminal result does not authorize redispatch. Saved session path stays private. |
| Pending question | framework interrupt ID, task/invocation target, operation/gate category, private question, required authority kind, actual reply when supplied | Graph checkpoint. Wait node has no provider/Git effect. A worker question also refers to a settled host pause result. Reply belongs to this target, not a reusable grant to unrelated work. |
| Checkpoint attempt | task ID, actual selected paths, attempted parent, expected selected content, check references; successful SHA or genuine no-change | Existing operation-local history plus actual Git. Persist before Git; re-read actual effect after uncertain return. Not a new receipt table. |
| Review | execution ID, exact base/head, attributable task/repair checkpoint references, findings/coverage/gaps and prior review reference | Existing private review/history records. Graph chooses the next node. A reviewer return or SQL row alone does not accept a delivery. |

Task phases are `prepare → gate/dispatch → waiting or returned → checks → checkpoint →
accepted`. Failed checks route to a targeted same-task correction. A known unsuccessful
provider result requires inspected diagnosis before cause-specific continuation. An uncertain
provider/Git result stops that affected effect until reconciled. Wave results can be retained
while another branch waits/fails; dependency readiness uses accepted checkpoints only.

Run phases are active, waiting, failed/interrupted, internally complete or abandoned.
A graph END at internally complete is not owner acceptance. Retain existing compatible
status names where practical; the public projection can expose waiting separately without
serializing private question contents.

## Persistence boundaries

- `.coherence/workflow/graph.sqlite`: standard saver tables, private filesystem protection
  consistent with current workflow storage; sync durability and stable thread identity.
  No automatic time travel, retention purge or graph-state upload.
- `.coherence/workflow/workflow.sqlite`: retain existing tables/rows and read APIs. New run
  inputs identify their backend in the existing authority JSON. Store holds original inputs,
  actual invocation/check/commit/review facts; it no longer selects orchestration stages.
- SQLite operations use connections in their owning threads, short transactions and normal
  saver locking. The existing inherited worktree lock excludes conflicting controllers.
- A saver failure cannot mean that an external effect failed. Reconcile existing operation
  history and actual SDK/Git results before rerunning an interrupted node. A history-write
  failure cannot be hidden by a graph checkpoint. Preserve partial work and report the
  affected persistence operation if its outcome cannot be established.
- Legacy inputs without a graph marker remain legacy. No inferred initial graph state,
  mass conversion, table deletion or changed historical success. Compatible old-runtime
  continuation is specified in [plan](plan.md#recovery-and-legacy-compatibility).
- Existing optional metric JSONL and read projections remain; no second local trace store.
  After released monitor cutover, stop new monitor-only writes without deleting old tables.

## Outbound observation

A safe observation is constructed afresh, not obtained by deleting a few keys from raw
Pi records. It has opaque run/task/invocation/session IDs, parent relation, fixed role/name,
model, safe outcome/category, timestamps/elapsed time and only known qualified numeric
usage/cost. Map caller-supplied identifying strings to UUIDs in private run context so an
issue title, task path or arbitrary run name cannot become outbound metadata. SDK wire
fields required for hierarchy/time/project routing are allowed; private graph state is not.

Unknown usage/cost is absent, not zero. A reused session requires a continuous exclusive
before/after interval. A reset/discontinuity or missing end means unknown. Do not aggregate
local cumulative totals into an invocation or silently use LangSmith-estimated pricing as
known local cost. Metadata-only chain spans need no prompt/output messages.

## Delivery and assessment (no new runtime tables)

- **Delivery issue:** qualified tracker URL/identity; optional `delivery_issue` context is
  carried in planning/task inputs. The issue owns intent, artifacts, executive summaries,
  feedback, corrections and acceptance. A summary references the exact presented commit
  plus attributable checkpoints; unrelated integration context is labelled as such.
- **Delivery revision:** presented commit, verification/limits, review outcome and purpose-
  classified correction links. States in the issue/chat are awaiting acceptance, correction
  requested, accepted, and closed when separately authorized/confirmed. A newer revision
  does not inherit acceptance of an older one.
- **Assessment:** source issue links, evidence/gaps, classification and grouped proposal in
  the issue trail and current response. No labels means unassessed; proposed/addressed/
  no-change labels are defined in [interfaces](contracts/interfaces.md#manual-assessment).
  Addressed requires delivered improvement evidence. Analysis is not delivery, and issue
  acceptance is not assessment eligibility. No separate learning ledger or automatic edits.
