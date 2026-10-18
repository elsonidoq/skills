# Executed interactive workflow fixture

**Result: PASS for the bounded integrated fixture; not production implementation or plan approval.**
Baseline: `d6acc130a1dd9f407b5da4a8698b07f9960a6991` (initially clean index/worktree).
Only this new evidence directory is retained. Existing code, specifications, plans, indices and previous evidence were read-only.

## What actually ran

Python **3.12.3**, LangGraph **1.2.16**, checkpoint-sqlite **3.1.2**, Node **22.23.3**, official Pi SDK **0.87.1**, Paseo CLI **0.9.2**. Existing dependencies only; no installation, global settings, credential refresh or alternative model. PyYAML 6.0.3/jsonschema 4.26.0 available but unnecessary. Native supervisor coordination package 0.73.1 was used by the coding child; actual `ask_user` remained the parent's already available tool.

```
parent conversation READY -> delegated deterministic runner launch
LangGraph ask -> real Pi request_owner_input -> completed terminating tool result
await prompt + waitForIdle -> SQLite park interrupt -> worker host exits
runner callback -> public paseo send --no-wait -> SAME idle parent wakes
parent status -> actual ask_user -> bound answer CLI -> persisted answer
NEW runner/host -> SessionManager.open(ORIGINAL file) -> answer user message
controlled_wait -> callback wakes parent -> status -> bound fixed steer CLI
SDK steer enqueue -> release wait -> next execution boundary -> write_note ACK
await prompt + idle -> checkpoint END -> completion callback
```

The callback is deterministic code, not the coding LLM reading a log and forwarding a question. Actual **Paseo UI adapter**, not a generic native Pi plugin. Public CLI help and exact agent inspection were checked before sending. Inspection verified agent ID, provider, model/effort and cwd. Pi session identity was separately confirmed by the parent witness; Paseo inspection does not itself prove that underlying identity.

### Identity and receipts

| Fact | Observed value |
| --- | --- |
| Run / task / gate | `interaction-20261018-1` / `toy-note` / `note-title` |
| Launching parent Pi session | `01a14fcd-f377-746e-853f-6c8a53cf6b29` |
| Existing parent Paseo agent | `defb1061-11f1-4b12-b07f-dbe45cebd27b` |
| ORIGINAL worker Pi session, before AND after answer | `01a15165-1154-75e1-bf2c-08f70a57a9df` |
| Parked host / resumed host PID | `3054291` / `3054460` |
| Question nonce | `1c8b785b4aaaa76fecb65122ab8e51f2` (fixture binding, not a secret/auth credential) |
| Approved fixture source SHA256 | `fc1c0e0c7ae8690bf702ade724d2543f81603a03b3956338f76ddef54ad713b9` |
| Actual parent tool return | `User answered: Release note` |
| Answer / steering IDs | `answer-1` / `steering-1` |
| Actual toy output | `Release note\nSteering received.\n` |

The source hash covers the exact bytes in [approved-source.txt](poc/approved-source.txt), not an application specification or all implementation files. Runner checks those bytes on input. Implementation digests are separately recorded in [validation.json](recorded/validation.json).

## Behavior matrix

| Behavior | Result / evidence |
| --- | --- |
| Real SDK worker inside actual LangGraph/checkpoint workflow | **PASS**: [events](recorded/events.jsonl), [checkpoints](recorded/checkpoints.json), [session metadata](recorded/session-metadata.json). Five real assistant requests, not mocked helpers. |
| Automatic SAME launching parent wake | **PASS, Paseo-specific**: probe 1, question 2, active 3, done 4; queued send receipts plus [parent witness](recorded/parent-witness.json). Probe ACK only after actual message receipt. No owner polling/manual log forwarding caused those wakes. |
| Actual parent `ask_user` product roundtrip | **PASS**: parent witness and [answer](recorded/answer.json) contain actual returned text/provenance, not a fabricated opaque tool ID. Setup permission for an unused extension was NOT counted as the product test. |
| Question safely parked / durable without live worker | **PASS at tested boundary**: tool result completes with `terminate:true`; `tool_execution_end`, `agent_settled`, awaited prompt+idle, SQLite interrupt, host exit. Separate process status sees pending/next=park. No half-completed question tool held open. |
| Reentry / original persisted conversation | **PASS**: new PID opens exact original session file, seven stored messages; answer is in persisted user context BEFORE the next request. Answer retained across a runner failure, resumed without asking again. Same session does not mean same OS process. |
| Live steering / actual acknowledgement | **PASS**: parent separate-process status active; fixed steer CLI queues; host SDK enqueue is separate; after controlled wait returns, next request sees steering; `write_note` tool arguments acknowledge both receipt IDs, output matches; final conversation flags true. No claim enqueue guarantees understanding, intention or future compliance. |
| Duplicate/wrong/stale answer | **PASS, actual CLI**: [negative inputs](recorded/negative-inputs.json), four rejected inputs, event ledger unchanged/no worker dispatch. Source/session/nonce/parent binding and pending checkpoint required. |
| Preapproved tiny tests / preflight / question categories | **PASS, synthetic policy checks**: approved profile proceeds without a cost/technical owner question; declared missing permission or approval blocks before dispatch. Product-only cosmetic validator rejects technical/scope-change category. Unknown-headroom/missing-original no-substitution rule also tested only as an explicit synthetic policy assertion. |
| Parent absent, normal compaction pressure, crash windows, arbitrary pause/steer UX | **INCONCLUSIVE / NOT RUN**: durable checkpoint + CLI are implemented, but no absent-parent outage, real pressure/compaction, arbitrary-tool interruption or exhaustive crash test. |
| Production launch tool / generic Pi-native wake plugin | **NOT IMPLEMENTED**: parent-authorized delegated launch tested, not registered production launch command. Pi extension alternative syntax-loaded only; never loaded in parent and removed. |

## Exact pause/delivery semantics and limits

- `request_owner_input` returns a normal tool result with `terminate:true`. Public tool contract terminates automatic follow-up only if **all** tools in that batch agree. Fixture tools are sequential and the observed batch contains just the question. The runner admits a gate only after prompt+idle settlement, not on `agent_end` or the first gate event.
- Parked assistant stop reason is `toolUse`, not `stop`; that is expected for completed terminating tool results. The next answer is a new user envelope in the same persisted conversation, not a delayed result to an unfinished tool call. No abort was needed for the question. Arbitrary batches/crashes before checkpoint commit are not proven safe.
- The bounded cooperative `controlled_wait` tool waits up to 120 seconds for the explicit steering file. SDK `steer()` queues at an execution boundary; it does not preempt an arbitrary shell/tool. The host releases the wait only after enqueue returns. Only `write_note` acknowledgement/output and persisted incoming user message establish observed receipt. No shell/file-execution tool is exposed to this worker.
- `agent_settled` was observed; runner still awaits `prompt()` and `waitForIdle()`. Subscriptions installed before prompt. Public `agent.streamFunction` guard invokes any existing per-call/agent transform **first**, then checks outgoing model/effort; no onPayload-only summary assumption. No new compaction/summary burn was run.
- Compaction is **disabled in this isolated fixture**. Unknown headroom synthetic assertions are not integrated real admission measurements; no >=150k or normal pressure guarantee. Missing original session blocks resume; no fresh session fallback exists. A production implementation still needs explicit safe headroom/resume/recovery gates.
- Single trusted local caller fixture, not production authorization: parent ID/nonce/hash flags bind inputs but do not authenticate OS users. No exactly-once claim, notification retry/outbox service, full transaction spanning SDK/SQLite/files, or hardening against arbitrary concurrent clients. There are crash windows before gate checkpoint or after toy write and before graph commit; inspect/block rather than blindly replay.
- `status` and bound `answer` are standalone CLI operations, independent of parent LLM availability. Unanswered question is persisted externally; UI/notification is not decision authority. Actual absent-parent/reconnect notification behavior remains untested.
- The forced cosmetic question is deliberately manager-answerable for **this test**, not a recommendation to ask owners about every cosmetic default. Category/explanation/options/impact validation cannot universally infer semantic relevance or prevent hallucinated questions. Scope-changing instructions cannot enter this fixed harmless steering CLI; material scope approval machinery is not implemented here.

## Failures inspected before targeted retry

1. [First failure](recorded/first-failure.json): Python logger `dict(at=..., **row)` raised duplicate-keyword `TypeError`, closing the pipe; host exited with EPIPE. Inspecting PID/session metadata showed one real tiny call (235 tokens, $0.000886), no tool/file effects. Source inspection also found `tools:[]` excluded custom tools. Fixed dictionary merge, explicit custom allowlist and active-tool assertion. Reopened the **same failed persisted session**, never launched an unexplained fresh expensive worker. First guard event was lost to the logger; its model/usage provenance is persisted session metadata, not invented outbound observation.
2. [Second failure](recorded/second-failure.json): parent's separate CLI environment lacked `PI_PACKAGE_DIR`; resume raised `KeyError` **before** subprocess/API dispatch. Answer was already checkpointed at `continue_original`. Persisted read-only runtime input paths, then explicit inspected retry of that node using the existing answer/session. No repeated owner answer or extra API call for this failure. This correction was exercised by actual successful reentry.

Neither failure is hidden or evidence that SDK/LangGraph lacks interactive support. The execution was repaired within the approved tiny test envelope, not repeated blindly.

## Bridge research and authority boundary

Installed `pi-subagents` 0.73.1 public `control-channel` exports stop requests; `intercom-bridge` exports session-target resolution, not a standalone programmatic supervisor sender. Complete native-supervisor-channel implementation was read-only inspected: child `contact_supervisor` depends on host-injected metadata and private channel files; those internals were **not imported or written**. `pi.events` is documented in-process only. Coding child's native coordination tool was used for readiness and factual witness, never counted as deterministic workflow-question transport.

Read complete installed Pi SDK, extensions, RPC, sessions and session-format docs; relevant session/extensions examples and exact declarations. A parent extension could use documented `pi.sendMessage(..., {triggerTurn:true, deliverAs:'followUp'})`, lifecycle cleanup, and delivery cursor. A temporary `.pi/extensions/interaction-probe.ts` was explicitly authorized, official-loader syntax/discovery checked, but Paseo owner could not `/reload`; it was removed unchanged without ever loading into parent. No production/global extension/config change remains. Generic Pi adapter would require explicitly loading a trusted local extension into the launching runtime (`--extension` on startup/resume or approved project extension plus idle `/reload`). That alternative is **not empirically proven here**. Public Paseo `send --no-wait` was the actual tested deterministic adapter, approved by parent after inspecting CLI/agent.

## Validation / reproduction without paid calls

From repository root, using the existing venv (no installs):

```sh
export PYTHONDONTWRITEBYTECODE=1
export POC_EVIDENCE_DIR="$PWD/docs/evidence/workflow-interaction-validation/recorded"
.pi/workflow-validation/venv/bin/python docs/evidence/workflow-interaction-validation/poc/test_validation.py -v
.pi/workflow-validation/venv/bin/python docs/evidence/workflow-interaction-validation/poc/runner.py negative-tests
node --check docs/evidence/workflow-interaction-validation/poc/host.mjs
git diff --check
```

Seven tests pass. Offline evidence mode checks retained records; live scratch mode additionally executes four actual rejected CLI inputs. It is not a paid model rerun. Retained JSON/session metadata omit private reasoning, raw transcripts, credentials and personal home paths; `<RUN_ROOT>` denotes scratch root. Raw session and SQLite remain ignored local scratch only.

### Authorized live reproduction only

Do **not** replay messages to the recorded parent. The retained adapter has a post-run safety interlock (unit-tested, no paid rerun) preventing any default notification. Live tests require fresh explicit authorized recipient/run identities, exact existing launching parent's Pi session ID, same cwd, ready selected credential/catalog, actual parent `ask_user` capability and a renewed small-test envelope. No fake response is allowed. No installs/refresh/fallback. The retained source also adds environment overrides for these fixture identities and a catch/log wrapper for optional notification failure after the live run. The latter is synthetic-tested so UI loss cannot itself decide workflow state or prevent CLI input; no real parent-outage rerun was performed. The successful adapter path is unchanged; these additions were not a second live test.

```sh
# Supply actual authorized values; do not use recorded IDs for a fresh run.
export POC_REPO="$PWD" POC_RUN_ID="<new-safe-run-name>"
export POC_NOTIFY_AGENT="<actual-existing-launching-Paseo-agent-uuid>"
export POC_PARENT_SESSION="<that-agent-current-Pi-session-uuid>"
export POC_ALLOW_NOTIFY_AGENT="$POC_NOTIFY_AGENT"  # explicit opt-in, not authentication
export PI_PACKAGE_DIR="<existing-installed-pi-coding-agent-package-root>"
export PI_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
python3 docs/evidence/workflow-interaction-validation/poc/notify.py probe
# Parent must observe actual automatic probe callback while idle, then:
python3 docs/evidence/workflow-interaction-validation/poc/notify.py ack \
  --nonce 0123456789abcdef0123456789abcdef --parent "$POC_PARENT_SESSION"
.pi/workflow-validation/venv/bin/python docs/evidence/workflow-interaction-validation/poc/runner.py launch
```

Use the **same exported fixture environment** for every standalone CLI, including parent's inputs. The first host persists nonsecret SDK/auth/catalog paths for cross-process reentry; existing auth/catalog default to the current user's Pi agent directory and are read-only. Runtime files go under `.pi/workflow-validation/interaction-poc/$POC_RUN_ID`. Never substitute a new session while answering.

On actual question callback parent runs `runner.py status`, asks actual `ask_user`, then `runner.py answer --session <observed> --nonce <observed> --source-hash <observed> --parent "$POC_PARENT_SESSION" --choice '<actual choice>' --reference '<truthful tool-response provenance>'`. On actual active callback run status then `runner.py steer` with same four binding flags. Fixed preapproved sentence is internal; no arbitrary message option. Inspect output/result/events after actual done callback. `resume` is an **explicit** recovery command only after inspecting a mechanical failure and confirming original checkpoint/conversation ownership; it is not automatic replay authorization.

## Cost and smallest next correction

Actual worker persisted session: **5 real requests, 3,641 cumulative tokens (3,445 input; 196 output), $0.00885 SDK catalog estimate**. Includes first failed call; do not add earlier cumulative snapshot totals again. Coding-child/parent/UI costs not separately measured, and this is not an invoice. Short prompts, low verbosity, 30-second provider timeout, zero retries and five calls per host were configured; inspected Codex request builder does **not** honor generic `maxTokens`, so no hard token/dollar cap is claimed. Max5 is per host, not a crash-proof run-wide budget. Operational overhead included native coordination, one real product popup, and two inspected local bug repairs; no fabricated total-time estimate.

Smallest plan correction: treat notification/UI adapter as explicit preflight capability (Paseo proven, generic Pi extension not proven), persist runtime/session/input authority before dispatch, park via completed terminating result + checkpoint, and separate input accepted / SDK enqueued / observed worker acknowledgement. Then renew owner approval of corrected originating plan before task generation; no architecture implementation here.

## Explicit owner directions to preserve in the corrected plan

- Launch from parent conversation/status interface; automatic worker question reaches **that same** launching/status agent's actual `ask_user`; worker never calls it. Interface only relays events/input/status, not autonomous LLM orchestration; deterministic runner owns transitions, persistence, authorization and IDs.
- Owner can inquire/steer/pause active work anytime; delivery happens at supported boundaries, not instant shell preemption. Queue/delivery/worker acknowledgement are separate; no thought/compliance guarantees.
- Pending question pins ORIGINAL persisted conversation, not OS process. Never automatically substitute fresh session at 150k while answering. Missing/unsafe resume blocks for owner recovery; unanswered gates durable/reentry-safe, duplicate/stale/wrong inputs reject, no duplicate worker.
- CLI can list/answer without parent. UI absence leaves durable pending; optional notification is not authority. Source/scope-changing instruction must hit approval, not bypass current approved source.
- **Maximum autonomy**: technical mechanics, implementation choices and approved tiny isolated tests are worker-owned. Ask only manager-answerable product/priority decisions or genuinely unexpected material scope/complexity/time/cost changes, with options and impacts—not routine debugging. This forced title fixture is not a blanket cosmetic-question policy.
- Declare spend/test/capability authority in plan/preflight; do not reask within approved envelope. Catch known missing permissions/paid needs before dispatch; unexpected out-of-envelope runtime condition blocks/asks rather than silently spending. No fabricated estimates, universal thresholds, complexity-model routing or extra bureaucracy. Fixture approval is not production blanket spend authority.
