# Validation quickstart — future production runner

Status: design guide only. The runner/commands below are **NOT IMPLEMENTED**. No implementation,
live provider test, install or service configuration is authorized by this planning pass.
Canonical [stack proof](../../docs/evidence/workflow-stack-validation/README.md) and
[accepted SDK probe](../../docs/evidence/workflow-sdk-validation/README.md) and
[local lifecycle probe](../../docs/evidence/workflow-process-validation/README.md) and
[interactive fixture](../../docs/evidence/workflow-interaction-validation/README.md) already ran; do not
repeat their selection/telemetry experiment as a future task. Permanent checks below exercise
the shipped helper/adapter, not duplicate disposable demo scaffolding.

## Prerequisites and authority

1. Renew changed specification approval; separately generate tasks, independent overall review,
   current final artifact approval. Original request remains planning-only: obtain a **later
   explicit implementation request** before migration. Future run intake must have actual
   implementation authorization, not this draft or a fixture's schema-valid shape.
2. Approved runtime setup and available pinned dependencies, Node compatible with Pi 0.87.1
   (22.23.3 tested), Python >=3.10 (3.12.3 tested), Git identity/signing/hooks and local SQLite.
   Verify actual packaged schemas/YAML/resources/host version, not installation names alone.
   Optional `scripts/install-workflow.sh` will provision only approved isolated runtime;
   network/install permission required. No installs during planning or auto-auth refresh.
   Interactive-parent mode additionally needs its explicitly selected transport (Paseo0.9.2
   tested), launching identity/permissions/readiness and registered ask_user; core CLI has no
   Paseo requirement. Do not silently fall back to polling if interactive capability is missing.
3. Isolated disposable project/worktree with known owned paths, baseline commit and retained
   unrelated staged/unstaged/untracked/STATE/custom bytes. Never point a kill test at active
   owner work. One writer per worktree across all run dirs; status can be a separate reader.
4. Explicit permitted exact profile/effort, resource/skill hashes, read-only ready credential
   and catalog, exact registered observer mapping and tool/permission policy. Expiry blocks
   rather than refresh shared auth. Planning Sol/medium selection is not production assignment.
   Declare actual paid/service/test/network/external/mutation authority and selected profiles
   with owner approval refs before dispatch. Aggregate known gaps once before tasks; unresolved/
   denied/absent paid envelope blocks. No production amount or blanket spend is approved here;
   routine approved tests/technical work must not reask inside-envelope questions.
5. Preexisting approved containment capability for tools requiring full-subtree custody,
   and actual empty-group/quiescence checks. cgroup files/systemd-run presence is insufficient;
   owner-enabled Linux cgroup-v2 delegation and four real local lifecycle cases are now
   proven in the evidence environment. Verify approved per-project delegation in production,
   never assume that service path or configure services automatically. No PID-only fallback;
   malicious same-UID migration/remote/container tools are outside the tested boundary and
   need their own approved capability or BLOCKED.
6. Required live/paid provider calls, actual SDK reopen/pressure/compaction/retry cases,
   process-kill and external effects each need scoped permission and budget. NOT RUN/UNAVAILABLE
   remains a blocker for its dependent reliance. Schema/static success is not live proof.

## Future command interface (illustrative, not runnable today)

```sh
# Resolve launcher from the authorized suite installation; variables name explicit inputs.
coordinate-implementation start --project "$PROJECT" --workflow "$WORKFLOW" --tasks "$TASKS"
# From a different process; no host/LLM launch, no mutation or guessed background progress:
coordinate-implementation status --project "$PROJECT" --run "$RUN_ID" --json
# Pending/answer/control interfaces (illustrative future flags, not implemented):
coordinate-implementation pending --project "$PROJECT" --run "$RUN_ID"
coordinate-implementation answer --project "$PROJECT" --run "$RUN_ID" --input "$BOUND_ANSWER"
coordinate-implementation control --project "$PROJECT" --run "$RUN_ID" --input "$BOUND_CONTROL"
# Only after actual scoped external owner answer/remediation and reconciled writers:
coordinate-implementation resume --project "$PROJECT" --run "$RUN_ID" --authorization "$ANSWER"
```

Future focused offline command after runtime implementation:
`python -m unittest discover -s runtime/tests`. Test selectors must identify the relevant
real helpers/scenarios below and collect nonzero checks. Live tests must be separately marked
and never run from ordinary offline lint. Actual shipped command names/flags/selectors are
implementation outputs; update this guide and operating docs against their real behavior.
No fake `runner.py` or simulated slash command is required to satisfy planning.

## Permanent production acceptance scenarios

| Scenario / design mapping | Smallest adequate execution and expected evidence | Gate / disproof |
| --- | --- | --- |
| Config/graph/result/roles — V-config | Schema negatives for unknown version/key/reference/outcome/unsafe path; actual LangGraph conditional routing changes for supported handler/profile/skill/edge variations; attempt provenance contains exact effective hashes. Graph validation rejects bypass of owner/checkpoint/final review and unbounded cycles before any effect | Local offline unit+real-engine integration. Registry readiness tested separately; schema pass alone not a callable-profile proof |
| Intake — V-intake | Both adapters and documented legacy fixtures preserve IDs/source/deps/context_group/ownership and REQUIRED/pass/evidence/manual/permission maps; absent/stale/denied/cancelled/ambiguous approval never dispatches. Later-numbered prerequisite blocks, not reordered | Offline fixture then actual CLI intake; no invented legacy approvals or automatic prose conversion |
| Exact binding and resources — V-binding | Shipped SDK host explicit settings/resources/tools; actual loaded skill expansion and prompt delivered, model/effort/runtime/request observations match; synthetic final transform mismatch/throw outside extension guard has zero instrumented sends, including summary route. Unsupported observer/version blocks | Offline guard-builder check plus separately authorized bounded real provider integration, not repeat toy probe. Never log full requests/auth |
| Session rotor — V-session | Every agent role uses shared Python selector, exact affinity/profile/skills/tools/permissions/trust match; original implementer repair preference; reviewer fresh-first then own eligible context; fresh-only and latest-settled/stable-ID tie. Controlled reliable threshold inputs test 150000/149999/null/disabled/stale; actual host settings model override and current-context provenance verified | Unit policy boundaries plus authorized shipped-host reuse/reopen. No token burn just to test cutoff; unknown telemetry denies reuse |
| Sequential multiple tasks — V-metrics/V-evidence | Two dependency-linked approved isolated tasks each receive real REQUIRED checks and focused task commit, optional same-group session reuse remains individual evidence. Real before/after counters and current context differ; zeros/null/stopped/orphan and reset/branch epochs handled without negative/double-counted deltas | Real engine/SQLite/Git with bounded authorized Pi calls. Killed final usage/cost is unknown, not zero |
| Custody before tools — V-custody/V-recovery | Worktree lock, durable intent, gated-start helper identity+containment registration precede release. Kill controller at intent/spawn/identity/release boundaries; restart reads same worktree DB and exact identities, drains/verifies empty containment before any replacement. Different run dirs cannot bypass lock | Isolated process/crash permission; actual supported containment required for full-subtree guarantee. No dead-host/stale-PID/quiet-file-only proof |
| Mid-tool pressure/orphans — V-recovery | Real SDK tool interrupted via supported abort/drain; SIGKILL host/controller while tool active; descendants accounted for by registered containment and persistent custody after restart. Logical completion with surviving tools emits durable ORPHAN_PROCESS and blocked replacement, independent of worker success. Idle reusable Pi host is not a task-tool orphan. No check/commit/reuse/replacement before proven quiescence and file reconciliation. Unknown external/escaped work visibly blocks | Authorized local containment/tool tests; controlled pressure signal fixtures plus actual SDK compaction/retry path at earliest feasible seam. Existing probe did not induce actual pressure/retry or durable registry recovery |
| Post-write/post-commit — V-recovery | Actual engine/SQLite process kill after write-before-success, after focused commit-before-receipt/checkpoint and app-result-before-graph-checkpoint. Resume preserves partial files/unrelated index; matching actual SHA recovered once with baseline/tree/path/operation identity; no duplicate prompt/commit or automatic reset | Local fault injection with known owned workspace, not paid blind replay. Actual reconciliation proof, not SQLite exactly-once claim |
| Independent status/projections — V-status | Separate process reads SQL without Node/LLM, sees stopped/interrupted host and exact blockers/config/checkpoints. Torn JSONL tail, append-before-cursor and stale state rebuilt by authorized publisher from committed SQL; record IDs/order deduplicate, status reports lag read-only | Offline actual SQLite/file/process integration; power loss/multi-host guarantees excluded |
| Checks/owner gates — V-evidence | Real REQUIRED oracle deliberately fails, irrelevant/missing/stale/conflicting/unrun evidence is insufficient, shared output maps all IDs, optional green cannot release. Inspectable sample STOP awaits explicit scoped answer; denial/cancel/hash/config drift invalidates only affected gate/evidence | Local mechanical checks plus real external owner-answer integration; never model-generated approval or narrative parsing |
| Repair/final review — V-review | Diagnosed in-scope failure dispatches configured repair without escalation, zero/two/exhaustion/unknown cases stop appropriately. Current independent read-only full-range review uses schema findings, each visible disposition. Authorized focused correction task+commit then affected checks and eligible reviewer loop. Scope changes gate owner | Offline budget/schema tests plus authorized real SDK review/repair integration. No mandatory per-task review; reviewer never produces fix |
| Upfront autonomy — V-authority | Missing/denied/unresolved paid profile/service/test/network/external/mutation authority blocks before send; preflight aggregates known gaps and manager-readable options. Inside-envelope technical/test actions do not trigger routine cost questions; unexpected material/safety gaps remain gated | Offline intake+actual admission/reservation helper checks. No provider call to test denied spend. Do not invent numeric hard caps; verify supported enforcement separately |
| Owner roundtrip — V-interaction | Actual registered launch captures parent/transport/question capability; code wakes that same parent which actually calls ask_user. Completed question tool→settled/drained SQL+LangGraph park; original persisted conversation answer before continuing. Duplicate/stale/wrong-session/role/source/config inputs do not dispatch; accepted answer survives failed resume without reask | Accepted interactive fixture is feasibility, not repeated PoC. Permanent shipped helpers test mixed batches, input/checkpoint/delivery crash windows, unknown/low-headroom original blocks without fresh fallback; explicit live permissions only where needed |
| Active controls/UI loss — V-control | Separate received/queued/SDK-delivered/worker-ACK and inquiry response; no private reasoning/compliance claim. Scope-changing input blocks renewal, pause abort/drains tool scopes before commit. Busy/outage/reconnect dedup and genuine ask_user receipt tested, CLI pending/answer remains independent; optional status notifications cannot replace required question transport | Controlled actual host/facade integration plus synthetic denial/binding fixtures; no arbitrary shell-preemption promise from cooperative wait. Durable gate/transport blocker instead of silent polling or success |
| Migration/rollback/docs — V-migration | Representative adopted projects retain TinySpec/Standard/legacy semantics, planning profile policy and technical gotchas/history/custom STATE. Legacy live writers reconciled before cutover; failure stops new entry, durable evidence/commits retained. Re-enabling legacy requires explicit compatible reconciled authority. Compare CLI/schema/docs and run existing focused suite guards | Offline isolated adoption/install/cutover fixtures; no mass conversion/deletion/reset/service setup |

Every scenario maps into future stable task-local REQUIRED IDs with criterion, smallest
check, pass condition, concrete output refs/current revisions/environment and original gates.
Tests/evidence/docs normally remain inside their coherent outcome; do not split tasks merely
for a workflow noun or another report. Reuse confirmed applicable proof; rerun only invalidated
versions/resources/permissions/seams. Failed experiments remain counterevidence, never erased.

## Completion report expected from production execution

Return task/attempt IDs, requested vs actual observed profiles/resources, run/config hashes,
all REQUIRED dispositions and gate evidence, ordered baseline/result SHAs, actual focused
owned diffs, metrics with unknown reasons, status/checkpoint/event refs, remaining blockers
and containment/telemetry limits. Distinguish implementation completion, independent review
and final acceptance. No narrative STATE, coordination memory paperwork, model-routing
optimizer, escalation, background deciding LLM or daemon promise. Notify `/reload` after
future global skills change; this planning bundle changes none.


Interactive fixture used compaction off and a deliberate forced cosmetic choice: neither is
production question/threshold policy. Reopened original conversation there does not prove
normal pressure recovery; queued steering is not worker acknowledgement. Read R13 for two
inspected local failures, actual five requests/cumulative usage and limits. Do not repeat the
completed fixture or send to its historical parent. Future runtime must persist environment/
original-session/authority before dispatch; no extension reload/install is presumed.
