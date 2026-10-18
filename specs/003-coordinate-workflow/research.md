# Coordinate Implementation — canonical architecture research

Date: 2026-10-18. Status: draft design; no production execution. Requirements truth:
[revised specification](spec.md); integration authority: [D7](decisions.md#d7--owner-selected-sdk-integration-revision).
Discoverability: [documentation index](../../docs/index.md). No memory/STATE writes.
The whole associated memory index has no entries; existing coordination guidelines say
no approved guidance. No benchmark or inferred feedback is used.

## Reuse, refresh and usable sources

Reuse the parent-accepted [candidate A report](../../stack-validation-report.md),
[semantics/reproduction owner](../../docs/evidence/workflow-stack-validation/README.md),
[harness](../../docs/evidence/workflow-stack-validation/harness.py),
[tests](../../docs/evidence/workflow-stack-validation/test_harness.py), and their linked
requirements, remote-signals, suite, real-metrics and corrections logs. Inspected locally,
not merely URL-listed. Five corrected tests historically ran in 15.252s. Real in-process
two-task reuse/telemetry/exact Sol medium is distinct from synthetic headroom/crash workers;
engine, SQLite, Git, kills and restart were real. B/C NOT RUN; selection is closed.
Those source bytes and logs remain canonical, not copied here or scheduled for repetition.

Refresh only production-load-bearing gaps: installed version-matched library source is
readable in the existing isolated Python environment and managed Pi installation. No
internet refresh, installs, auth changes or paid/live calls were necessary. Python packages
are LangGraph 1.2.16 / checkpoint-sqlite 3.1.2; Pi official package
`@earendil-works/pi-coding-agent` 0.87.1 and its installed pi-ai/pi-agent-core sources.
Paths below are relative to those distributions, not portable filesystem installation paths.
Exact local versions must be rechecked by future consumers; newer docs are not substitutes.
Primary upstream locations: [LangGraph source](https://github.com/langchain-ai/langgraph/tree/1.2.16/libs/langgraph),
[SQLite source](https://github.com/langchain-ai/langgraph/tree/main/libs/checkpoint-sqlite),
[official Pi source](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent).
The last two URLs are moving discovery links; claims below use inspected pinned installed
files, not an assertion that current main equals those files.

## Supporting spans → decisions → observable checks

| ID / classification | Actual inspected support | Derived constraint | Required check before reliance |
| --- | --- | --- | --- |
| R1 documented API behavior | LangGraph `pregel/main.py:2798–2808`: default async; `sync` persists before next step; `types.py:903–925`: interrupt resumes node **from its start**, re-executing logic | Use actual StateGraph conditional edges and SqliteSaver with `durability="sync"`; no side effect before an interrupt without durable idempotency identity; pure gate nodes validate owner input | Actual engine restart at gate and completed-node replay; no duplicate effects; invalid resume answer rejected |
| R2 documented source behavior | checkpoint-sqlite `__init__.py:134–179` WAL/tables; `188–209` locked cursor commits separately; `400–456` put checkpoint; `458–499` put_writes | One SQLite file with saver tables and runner tables, but **no claim of atomic saver+application transactions**; application operation/event transaction precedes graph result; replay reconciles ledger-first | Kill between ledger commit and graph checkpoint, and inverse pre-effect boundaries; consistent status/recovered route; SQLite integrity check |
| R3 documented protocol recommendation | Pi `docs/rpc.md:36–95`: correlate IDs, drain LF JSONL, subscribe before prompt, accepted != complete, agent_settled != agent_end; `docs/sdk.md` Session lifecycle/Prompting/Subscribing | Host subscribes before work, serializes prompt through current settlement, retains correlated responses and lifecycle independently; abort/drain before replacement | Early/stale settled, retry/compaction after agent_end, timeout/process exit; real tool quiescence before check/commit |
| R4 documented source behavior | Pi `dist/core/settings-manager.js:566–596`: exact model override→ordinary→default; `dist/core/compaction/compaction.js:194–197`: enabled and context > window−reserve; `dist/core/agent-session.js:3098–3136`: unknown current context after compaction | Host reads **actual session.settingsManager** and session model/current context. Enabled, valid reliable inputs yield threshold=window−reserve. Disabled/unknown threshold yields no reuse, not infinity. Include version/settings hashes/trust and sampling sequence | 150000/149999/unknown fixtures plus real settings composition and model override/trust tests; no advertised-window shortcut |
| R5 documented source behavior | Pi `agent-session.js:3043–3095`: counters include all persisted usage, compaction and summaries; context separately projected; `docs/rpc-commands.md:520–561` same explicit distinction | Before/after same session ID, branch/counter epoch and monotone counters required for deltas; fresh baselines on reopen; never attribute a reset to negative usage; stopped attempts retain available partial data | Two real sequential tasks, restart/reset/branch fixtures and null reasons; zero cache remains zero |
| R6 documented SDK surface | Pi `docs/sdk.md` Configuring a session; `dist/core/sdk.d.ts:12–83`: cwd/model/effort/tools/resources/session/settings supplied explicitly; `agent-session.d.ts:195–198,305–337,509–510,707`: actual settings, subscriptions, tools, abort/idle/stats; examples `04-skills.ts`, `10-settings.ts`, `11-sessions.ts` | Thin pinned SDK host, explicit loader/settings/manager/tool allowlists; open exact recorded session only after runner reconciliation, never continueRecent. Reject fallback message/model/effort mismatch. Host reports capability/resource hashes, no workflow policy | Focused real SDK composition proof; skill content actually reaches prompt, exact tools/permissions, no global settings writes, exact session reopened role-safely |
| R7 documented provider source + local design | Pi `agent-session.js:1748–1770` clamps thinking; `pi-ai/dist/api/openai-codex-responses.js:363–428` maps reasoning to outgoing `body.reasoning.effort`; `:174–180` onPayload may replace body before serialization; `pi-agent-core/dist/agent.d.ts:13,42–44` public onPayload/streamFunction; Pi `sdk.js:208–245` extension payload transform; extension runner `:961–987` catches extension exceptions | get_state/thinking selection is **not outbound evidence**. Wrap public agent.streamFunction; compose existing per-call onPayload or SDK hook FIRST, then validate final mapped model/effort before send; summary routes do not inherit agent.onPayload; do not rely on a throwing extension callback to prevent send. Pin provider-specific mapping and report request-observed vs selected vs provider-acknowledged separately | Accepted SDK probe observes six real outgoing requests, two tasks; synthetic normal/summary guard mismatch gives zero instrumented sends despite swallowed extension error. Permanent shipped-host tests required; actual retry/compaction NOT RUN. No raw payload/transcript retained. Other providers require registered tested observer or capability blocker |
| R8 repository observation | Canonical PoC `RPC.prompt`, `Engine.node/execute/status`; tests `test_00…04`, actual logs | Reuse feasibility evidence, not toy JSON receipt/subject-matching/projection design. Production receipts in SQLite; stronger Git identity/diff and worktree-wide custody needed | Real orphan-host/tool death and post-write/post-commit recoveries; unrelated staged/untracked/custom files unchanged |
| R9 repository observation | `scripts/install.sh` links skills/SDD and installs npm pins, no Python runtime; root `.gitignore` ignores package.json/locks/node_modules | Add opt-in isolated workflow runtime installation plus owned package ignore exceptions; do not turn ordinary adoption into silent installs. Python wheel includes registered graph/schema/resources; Node host exact npm lock | Offline package/discovery fixtures, clean unrelated-project start/status; explicit network/install approval for actual dependency setup |

## Resolved decisions and alternatives

- **Selected engine remains A.** Owner SDK direction changes only the Pi integration seam,
  not LangGraph routing, SQLite durability or declarative YAML. No LangChain agents or
  fourth-framework survey. SDK host is an operational dependency, not a second orchestrator.
- **Native RPC alternative assessed, not selected:** `rpc-commands.md:149–180` gives model,
  thinking and autoCompactionEnabled, not reserve/effective threshold; `520–561` gives
  occupancy/counters. A trusted extension can observe `before_provider_request`
  (`extensions/types.d.ts:534–538,994`) and emit metadata through structured notification
  records (`rpc-extension-ui.md:97–111`). Context exposes trust/model/usage but not the
  actual settings manager (`types.d.ts:195–251`). A separate SettingsManager snapshot would
  need proof of equivalence under settings/trust/overrides. SDK is simpler and direct.
  No automatic native fallback if SDK fails; inspect failure and return precise blocker.
- **Authoritative store:** SQLite application tables contain immutable receipt/event history
  and current operation aggregates in the same application transaction; LangGraph saver tables in
  that file own execution continuation. An operation result may precede its graph
  checkpoint; reconciliation handles this explicit ordering, not a custom graph scheduler.
  JSON/JSONL are rebuildable projections, never intake authority. See [data model](data-model.md).
- **Install:** choose `runtime/` packages with optional suite-relative launcher and explicit
  `--project`. No project-name/layout assumptions, daemon or automatic dependency installs.
  Use Node version satisfying pinned Pi package engines (inspect at setup; unsupported
  runtime blocks), Python >=3.10 with 3.12 tested, local SQLite on supported single host.
  Package lock/transitive dependency hashes are implementation outputs, not fabricated here.
- **Pressure/orphans:** a real long tool may outlive host termination; stale PID or exited
  host alone is never quiescence proof. Validated owned cgroup identity/kernel emptiness plus
  durable tool registry, abort/drain and file/Git reconciliation are needed; PID/PGID alone
  is diagnostic, not the production cleanup oracle. Unknown descendants or
  uninterruptible external tools block. No automatic reset, kill by unverified PID or retry.

## Assumptions with validation (not documented guarantees)

A1: The accepted SDK probe now demonstrates threshold, actual skill expansion, two real
tasks and final outbound metadata within its recorded bounds. This is not shipped-host,
permission-system or durable reattachment proof. Preserve its source/logs and make R4/R6/R7
permanent integration tests prerequisites to shipping; do not repeat the disposable probe.
No SDK factory default or hidden modelFallbackMessage may establish readiness.

A2: The supported single-host lock plus delegated cgroup-v2 local trusted-tool mechanism
can establish scoped quiescence. Accepted SDK probe disproves host-death quiescence; R12
now proves minimal kernel-membership/empty and separate-controller cleanup feasibility.
Production authenticated durable registry/tool gateway and crash phases still must be proven;
unsupported platforms/network filesystems or escaped descendants stop before mutation.
Multi-host and physical power-loss/fsync claims are excluded; process-crash durability is
required. SQLite synchronization/backup settings must be tested/documented, not inferred
from WAL alone.

A3: Public streamFunction wrapping with composed onPayload sees provider-final mapped
effort for registered profiles; **onPayload alone is insufficient** for summaries. R7 and
accepted synthetic real-provider-builder routes support the path, not all provider plugins; cold-cache, retry and
compaction requests must also be accounted for without launching unsolicited warming.
Disable unapproved background cache-warming/model operations in effective settings. If a
request's operation attribution is ambiguous, record it as unattributed, block reuse and
investigate rather than fabricate task deltas.

## Proof selection, lifetime and authority

The originally selected consequential SDK experiment is now completed and parent-accepted;
[canonical report](../../docs/evidence/workflow-sdk-validation/stack-integration-report.md),
[semantics](../../docs/evidence/workflow-sdk-validation/README.md),
[host](../../docs/evidence/workflow-sdk-validation/poc/host.mjs),
[controller](../../docs/evidence/workflow-sdk-validation/poc/controller.py), tests,
[guard regression](../../docs/evidence/workflow-sdk-validation/logs/guard-regression.jsonl),
[file observations](../../docs/evidence/workflow-sdk-validation/logs/file-observations.json) and
[source manifest](../../docs/evidence/workflow-sdk-validation/source-manifest.json) were read.
Parent independently reran no-paid settings/unit/retained-file/process checks. It is not a
future task, production scaffolding or proof of all recovery. Production remaining risk
reduction is permanent actual-helper launch/custody/restart and real pressure/reattachment
integration before those consumers rely on them. No extra disposable experiment is presently
justified; failure/new consequential uncertainty returns through producing/owner gates.

Retain canonical PoC and new applicable proof through consumers and permanent production
validation. Invalidated versions/resources/permissions require only affected reruns. Failed,
unrun or unavailable proof blocks the dependent seam; diagnose before retry, return changed
scope to owner/producing review and renewed approval. No production result is claimed here.

## R10 — Accepted SDK experiment changes production constraints

**Repository-derived from executed evidence, not a library guarantee:** parent accepted
commit `6939f113c199c557f8b6c2b3afacc5cfb81a78a0` within tested bounds after the owner chose
“Run the focused PoC (recommended)”. Two real tasks used one session; actual skill loading
and expansion, effective threshold 483616, context 0→452→725 and cumulative total 2232 were
observed. Six real outgoing requests (four short-task turns + abort + kill) used exact Sol
medium. Killed final usage/cost is unknown, not zero. Boundary headroom remains synthetic.

`host.mjs` wraps public streamFunction, preserving SDK hook; `agent-session.js:1842–1845,
2938,3181` routes summaries through that stream, while compaction.js:484–508 does not inherit
agent.onPayload. Extension runner :961–987 catches errors, so final guard belongs outside.
Synthetic mismatch/summary route produced two errors and zero instrumented sends, not a
real compaction/overflow/retry claim. Cache-warmer.js:91–93,114–118 supports off; credential
helper/store use in host forbids refresh/persistence and reads catalog privately. Production
must resolve installed packages/catalog/credentials portably, pin hashes and block unsupported
version/auth expiry rather than use the probe's machine paths or mutate shared credentials.

**Negative finding to preserve:** kill log/results/file observations show real host SIGKILL
left detached bash descendants writing 1→4 bytes. SDK abort/waitForIdle drained ordinary
bounded descendants (1→1), but SIGKILL cannot execute cleanup. Controller recorded PID/start
ancestry/PGID **before death**, killed that proven-owned group, verified no live group and
stable partial bytes, then admitted replacement. This is not a durable cross-restart process
registry, arbitrary-client protocol, escaped-group/remote/container/malicious-tool sandbox,
resumed Pi session, power-loss or multi-host guarantee.

**Implementation constraint:** install worktree-wide lock and durable gated-launch registry
before mutation. Host custom mutation/process tools delegate to runner-owned operations;
only registered contained tool capabilities are eligible. Unknown ownership/quiescence blocks
replacement. Persist intent before spawn, persist observed child identity before release,
reconcile all registered groups across restart. See data model for the no-release-before-
identity handshake. Real restart and fault-boundary tests of those helpers must precede
reliance; a quiet file window, old PID, dead host or lock release is insufficient alone.

No new network/source refresh or experiment run by this planning producer on resumption.
Canonical SDK evidence remains read-only, not copied into production or retrospectively
claimed as part of the original LangGraph PoC.

## R11 — Initial containment discovery (historical; superseded by R12)

The parent reports Linux cgroup v2 exists and current service cgroup has procs/kill/events
files but none is writable; systemd-run is present but delegation/user-service usability
is unproven. This is **UNAVAILABLE containment**, not permission to configure system services.
PID/PGID enumeration from R10 cannot prove no escape/race. Full-subtree guarantees require
an approved usable kernel containment capability with empty-group proof. Block affected
tools when unavailable; do not silently downgrade to PID-only tracking or add a generalized
supervision platform. Any platform/install/service remedy goes to owner before adoption.
This observation refines existing FR-006/015–017/025 safety constraints, not a new broad
security product or a claim that arbitrary remote effects can be tracked.

## R12 — Accepted minimal local lifecycle proof supersedes capability blocker

**Repository observation:** owner requested sleep60-survivor alarm and minimal feasible
coverage, then administratively enabled delegation and answered “Done”. Parent verified
own-child controls and accepted evidence commit `00b7a4d908a9ab2a6bb650deb6803b7ebe6947de`;
[README](../../docs/evidence/workflow-process-validation/README.md),
[222-line stdlib source](../../docs/evidence/workflow-process-validation/script.py) and
[55 timestamped events](../../docs/evidence/workflow-process-validation/run.jsonl) were read
fully here. Parent independently reran the same four cases with new scratch and PASS.
No experiment/probe rerun by this producer. R11's initial unavailable capability is now
historical, **resolved for this environment**, not universal deployment availability.

| Inspected source/event span | Derived constraint | Permanent production check |
| --- | --- | --- |
| `validate`, `create`, `start`, `worker`: exact parent/name/UID/device/inode; worker joins before tools, controller verifies then releases | Persist trusted own-child receipt before release; never target service root/ancestor/unknown group. Project-configured delegated cgroup v2 for trusted local tools, no hardcoded service path or root privilege assumption | Actual durable registry/gated-launch helper crash before placement/registration/release; invalid/replaced receipt and unavailable permission block before mutation |
| `case_run` exit0/exit1 and forced setsid grandchild ignores TERM; `ORPHAN_PROCESS` events precede CGROUP_KILL and RECONCILED | Survivor alarms durable and blocked regardless of logical success. PID/PGID is not emptiness oracle; use cgroup.events populated | Shipped task-tool completion, failure, kill and controller restart cannot release on success with live tools; persisted alarm/status/result visible separately |
| `run` host subprocess then separate `recover`; recovery validates receipt and independently observes live group | Reentry does not depend on old Python object/PID; reconcile actual group plus partial files/Git before continuation | Production SQLite operation receipt/application+graph checkpoint lag and restarted controller, no duplicate tool/task/commit |
| `drain` cgroup.kill→actual populated=0→RECONCILED; sentinel alive through all four; CLEANUP empty | Only scoped own children killed, history retained; empty necessary, not sufficient for task acceptance. Idle reusable Pi host is a separate lifetime, not task-tool orphan | Correct host/task scope separation, sentinel/unrelated protection, REQUIRED/file/Git gates still block after empty |

Four real cooperating Linux local cases clear lifecycle feasibility, so do **not** repeat
an equivalent proof as a future task. Missing/denied controls in log were explicit synthetic
admission tests, not real permission sabotage. Placement-before-tools is demonstrated but
atomic OS spawn/assign and production authenticated/durable receipt/fsync/reboot are not.
Malicious same-UID children may migrate via writable ancestor controls; this is not that
security sandbox. Remote/container/different-user/adversarial effects require an explicit
approved lifecycle capability or BLOCKED. No automatic services, cgroup/global configuration
or additional platform adoption. Production verifies actual child-control readiness and
retains fail-closed ownership/quiescence checks without downgrading to PID-only.
