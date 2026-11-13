# Control state and data ownership

This is a design, not a database migration. Requirements remain in [spec.md](spec.md).
[Plan](plan.md) owns architecture; [research](research.md) owns dependency evidence.

## Graph state

Proposed representation: ordinary typed dictionaries and standard LangGraph serialization.
Equivalent simpler representation follows the [design boundary](plan.md#requirements-versus-proposed-mechanisms).
Keep runtime objects (adapter, subprocess, locks, open SQLite connection, credentials)
out of checkpoint state.
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

Proposed placement: standard saver tables in `.coherence/workflow/graph.sqlite`; existing
private inputs/effect history in `.coherence/workflow/workflow.sqlite`; existing metric
JSONL remains readable. File arrangement and backend-marker encoding are derived choices,
not owner requirements. The [plan](plan.md#recovery-and-legacy-compatibility) owns recovery
routing. Preserve old rows and private filesystem protection; no automatic conversion,
retention purge or state upload. Store facts support reconciliation, not a second controller.

Saver/history disagreement cannot prove an external effect failed. Retain partial work and
reconcile before mutation. Standard thread-safe connection/transaction handling is needed,
not a new receipt database. Graph state holds control references, not duplicate transcripts.

## Outbound observation

Approved observation fields are the opaque identities/parent relation, role/model, safe
outcome/category, time and known invocation-local usage/cost from FR-009–010. Private state
never becomes an outbound record. Unknown numeric values are omitted, not zero. SDK protocol
routing fields do not authorize private payloads. [Research](research.md#metadata-only-langsmith-submission)
owns mapping/SDK choices; [quickstart](quickstart.md#trace-privacy-before-any-upload) owns
final-wire privacy and usage verification.

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
