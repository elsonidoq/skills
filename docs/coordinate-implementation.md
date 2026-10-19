# Coordinate Implementation runtime

## Current delivery: opt-in standalone task execution

The legacy skill remains the default; there is no global entry cutover. The standalone
`scripts/coordinate-implementation` composes the foundation and pinned SDK with structured
intake, authority preflight, real registered checks and focused runner checkpoints.
The packaged task-progress graph uses bounded logical visits in the same LangGraph,
not a separate scheduler. Bounded diagnosed repairs and fresh independent read-only
full-range review now compose that graph. `implementation_complete` is not acceptance:
only current REQUIRED/gates, focused checkpoints, resolved findings and an exact current
full-range independent pass permit acceptance. Interaction commands explicitly block
until their interaction capability is delivered. `load_workflow(Registry())` still blocks
without concrete registered task-handler capabilities. Its selected
profile is a declaration, not proof of a usable model or permission to send requests.
The schema-file settings manifest is only a pinned declaration resource, not effective
Pi settings. No agents or tools launch on import or configuration validation.

Requirements and approved sequencing remain in [the specification](../specs/003-coordinate-workflow/spec.md)
and [T001](../specs/003-coordinate-workflow/tasks.md). Database and public contract ownership
is [the schema reference](coordinate-implementation-schema.md). Existing historical
PoCs remain evidence for their original bounds, not production implementation.

## Explicit setup and capabilities

Python >=3.10 syntax is used; validation is on Python 3.12/Linux, local SQLite and Git.
`runtime/pyproject.toml` pins LangGraph 1.2.16, checkpoint-sqlite 3.1.2, PyYAML 6.0.3,
jsonschema 4.26.0 and build tools. `runtime/requirements.lock` pins/hashes the complete
resolved environment, including required upstream transitive packages. No LangChain agent
abstractions are instantiated. The wheel contains Python helpers, one YAML and eight schemas.
The supplied lock hashes cover the tested CPython 3.12 Linux x86_64 wheels; other wheel
platforms require a separately validated lock, not an unhashed fallback.

Dependency fetching/installation is an explicit authorized setup action, never performed
by normal library calls. For an approved isolated setup, create a project-local virtual
environment, then install with `python -m pip install --require-hashes -r runtime/requirements.lock`
and build/install the local package without unpinned build isolation (`--no-build-isolation`).
No global installation, credentials, services, settings or Git identity are changed.
The Python foundation has no Paseo dependency. SDK use additionally requires Node
22.23.3–22.x and the exact local official Pi SDK 0.87.1 lock under `runtime/pi-host/`.
With explicit setup/network permission, run `npm ci --prefix runtime/pi-host --ignore-scripts`
using worktree-local TMPDIR/npm cache. No installation runs on import or host startup.
The host is a separate source asset, not bundled into the Python wheel yet; installed
Python callers must pass its verified `host_path` explicitly.

## Actual interfaces and custody

- `engine.load_workflow(registry, source=None, resource_root=...)` loads bounded, strict
  safe YAML and validates packaged draft-2020-12 schemas, trusted versioned references,
  hashes, paths and actual edge safety. Trusted code registers handlers, exact profiles,
  skills, permissions/tools and containment capabilities; YAML cannot import/eval code.
- `store.Authority(canonical_project, run_root=None)` acquires the per-worktree advisory
  lock and binds one private database. Different run roots cannot select other stores.
  Scope is a canonical Git root; symlinks/ambient Git authority overrides block.
- `engine.Engine(authority, run_id, config, registry, resource_root, phase_hook=None)`
  compiles actual StateGraph conditional edges with sync SqliteSaver. `invoke()` starts
  or reconciles continuation from the same run. `close()` releases its saver connection.
  The trusted fault hook exists for isolated tests, never YAML execution.
- `tools.ProcessTool` registers a closed argument schema, trusted argv builder, explicit
  file ownership and environment. `Gateway(authority, run, approved_parent, tools)` is
  the only process-tool launcher. `launch(...)` returns operation ID and Popen;
  `settle(op, exit_code)` always checks the kernel group, not only the exit code.
  `recover()` observes durable operations; it never releases or replays a tool.
  `resolve(op)` drains only proven-owned containment and reconciles partial files/Git.

These are trusted runner interfaces, **not agent-exposed authority APIs**. T003 must
validate external requests and owner scope before connecting task execution to this library. Production
registry entries remain unavailable until their real implementations and capability proof
exist. Fixture handlers used in engine tests are deliberately not Pi/approval certification.

Every successful graph route must traverse intake → authority → custody → verification →
checkpoint → independent review before a registered success terminal. Other terminals may
block early. T001 supports acyclic graphs only; loops/retries are rejected until registered
progress/reconciliation capabilities exist. Definition order is not scheduling; configured
handlers/outcome edges/profile/skill bindings determine actual LangGraph routes. Reviewer
nodes are read-only and role isolated; first-session independence still requires the future
SDK/session capability, not a green synthetic handler. Runtime configuration/registry/source
and schema identities are pinned; changed inputs cannot silently apply to an existing run.

## Storage, launch and failure rules

The canonical store is `.coherence/workflow/workflow.sqlite`, with per-worktree admin
`coherence-workflow.lock` and private `coherence-workflow.binding`. Setup excludes runtime
state from Git explicitly; the library never edits project ignore files. Paths to different
stores are rejected; moving storage needs a separately implemented/approved migration.
Never put this trusted private database/checkpoints under agent mutation tools. A durable
reservation survives process/lock exit, including a parked run. There is no automatic
reservation-clearing, schema migration, downgrade or legacy restart API in this foundation.
Unresolved legacy/external writers must be reconciled by the operator before opt-in use;
legacy agents do not participate in the new lock protocol. Do not run both against a project.

App intent commits before child creation; the fresh UUID own-child UID/device/inode/name,
parent and boot receipt commits before helper spawn. The helper joins the child before
reporting PID/start/boot/nonce/parent identity and waits on an inherited pipe. Registration
and release intent commit before the nonce is sent. EOF/wrong nonce executes no tool.
Release intent without observed work is uncertain, never authorization to resend. A crash
before durable helper registration blocks replacement/adoption even when a child looks
empty; there is no unsafe automatic recovery override. Known registered groups may be
reconciled across controller restart. No process/group is adopted by a guessed name/PID.

A logical exit 0, exit 1 or host/worker kill with surviving task tools writes
`ORPHAN_PROCESS`, an active alarm and blocked state in one application transaction.
`replacement_allowed=false` blocks further checks, commit, reuse or launch. Only a validated
`cgroup.events populated=0` receipt **and** actual partial-file/HEAD/index/unrelated-work
audit resolve the alarm. History remains; resolution is not acceptance or automatic resume.
Host scopes may remain idle separately; the SDK adapter uses that distinct lifetime.

Baseline capture rejects preexisting dirty owned overlap, symlink/authority paths, unknown
path identity changes and unrelated drift. All tracked and untracked/ignored user files
(except private runtime storage), index entries/modes/blobs and HEAD are fingerprinted;
unrelated STATE/custom content is preserved. Registered tools are trusted to respect owned
paths; containment is not a filesystem sandbox. Inventory uses no optional Git locks;
configured fsmonitor process hooks are unavailable rather than run outside custody.
Git commits/recovery are not implemented here: uncertain Git effects always block and
must never be replayed blindly. Future commits must retain signing/hooks and focused scope.

## Containment and supported limits

The caller supplies an approved existing Linux cgroup-v2 delegated parent. No environment-
specific service path is built into production code. Actual fresh child controls, membership,
identity and kernel emptiness are required; no service provisioning, ancestor/service-root
kills, PID/PGID-only fallback or quiet-file-window substitute exists. Unsupported/unknown
capability blocks. This is single-host, trusted same-UID local-tool containment, **not** a
malicious same-UID sandbox, remote/container security, multihost or physical power-loss
promise. Owner approval alone does not prove delegation readiness.

## Focused validation

From the repository root with the explicitly prepared pinned Python environment:

```sh
PYTHONPATH=runtime:runtime/tests python -m unittest test_engine.ConfigGraphTests test_engine.LedgerCheckpointTests -v
# Only after isolated process-kill authority and approval of the existing delegated parent:
COHERENCE_TEST_CGROUP_PARENT="$APPROVED_PARENT" PYTHONPATH=runtime:runtime/tests \
  python -m unittest test_custody.CustodyTests test_custody.LaunchCrashTests -v
```

The required process tests fail (not skip) if delegation is absent. They create isolated Git
projects, UUID child scopes and an outside sentinel; SIGKILL actual controllers/helpers at
launch boundaries and test setsid/TERM-resistant survivors, restart, alarms, empty receipts
and dirty/index/custom preservation. Cleanup touches only validated test-owned children.
Engine tests use actual StateGraph/SQLite saver and process death after app result before
checkpoint. Printed hashes/routes/phase receipts are item-mapped proof, not live SDK proof.

Rollout remains opt-in. On failure stop dispatch, preserve DB/evidence/partial work/commits,
reconcile only owned scopes and leave unknowns blocked. Do not reset Git, erase history,
auto-resume legacy, install services or claim later task acceptance. No existing workflow
skill or operative policy was changed by T001/T002.

## T002 SDK/session seam (trusted library, not a task runner)

`pi_adapter.PiAdapter(gateway, manifest, node=..., environment=...,
session_context={role, affinity, review_lineage}, reopen_from=None, host_path=None)`
launches one official SDK session through the existing gated-start custody protocol.
The environment is an explicit trusted allowlist. Agent/session directories must be private,
canonical children of `.coherence/workflow/`; credentials and cached catalog are read-only
references. The host uses in-memory settings, private credential/catalog views, network
catalog discovery disabled and no credential refresh/write path. Expired credentials block.
Only explicit skills, system prompt and registered proxy tools load: no discovered project
extensions/settings/packages, unrestricted SDK bash, worker Git, or `ask_user`.

The closed manifest in `host.mjs` pins SDK version; canonical cwd/agent/session directories;
exact profile/observer; skill paths/content hashes; tool names, versions, descriptions,
parameter schemas and permission references; settings/hash; explicit-resources-only trust;
resource hash; auth/catalog paths; system prompt; and pressure policy. Resource hash covers
skills/tools/permissions/trust/system prompt. Settings are explicit compaction/retry,
`cacheWarming: off`, `transport: sse`; provider retries are zero, while observable SDK agent
retries are bounded by the supplied policy. Supported observer is currently only
`observer_id: codex-final-payload`, `observer_version: '1'` for exact `openai-codex/gpt-6.1-sol:medium`. This is a tested binding,
**not a default production profile or permission to dispatch**. Other mappings block.

`prompt(node, task_id, attempt_id, role, text, skill, contract_hash, selection, ...)` forces
actual `/skill:name` expansion. `selection` is a recorded runner decision, not worker text.
The final public stream wrapper composes per-call/SDK payload transforms first, then checks
final model/effort, normal-versus-summary tool loadout and normal skill delivery. It forces
SSE/provider-retry-zero on summary paths as well. Extension exceptions are not a guard.
Requested/runtime/final-outgoing/provider-acknowledged observations remain separate;
unobserved provider model/effort acknowledgements stay null. No raw provider payload,
reasoning, transcript or credentials enter telemetry. Conversation files themselves remain
private SDK storage and may contain model/tool text.

Commands/events use bounded UTF-8 LF JSON records (262144 bytes), inherited anonymous pipes,
private bootstrap nonce, host/run/request/attempt/operation/session IDs, monotonic sequence
and prompt generation. Std streams are not a protocol, and no socket/CLI endpoint is added.
Create/open/prompt/telemetry/abort/drain/close, correlated tool replies and T006's bound
owner_answer/steer/follow_up commands are supported. Workers never receive ask_user. Prompt acceptance and
`agent_end` never release completion. Current prompt promise + current `agent_settled` +
idle/no queued work + completed kernel-empty task-tool audits are all required.

`telemetry()` requires a known idle boundary. Actual SettingsManager model override and
current SDK projected occupancy determine threshold = window − reserve and headroom =
threshold − occupancy. Cumulative usage is separate. The pressure policy supplies a bounded
10–10000 ms monitor interval and minimum headroom; safe request boundaries check again.
Low/unknown pressure or compaction stops ordinary continuation and aborts/drains, then
blocks for recovery. No token-burn pressure guarantee or universal interrupt deadline is
claimed. The explicit `interrupt` callback is a trusted controlled-test/control seam, not
worker input. It is not evidence of naturally occurring high pressure.

`abort()` poisons reuse, drains registered task scopes using T001's kernel-empty/partial-work
oracle, and requests actual SDK abort/idle. Host death never proves tool quiescence. A live
survivor still records `ORPHAN_PROCESS` before release; resolving it does not resume the run.
`close(force=True)` drains only its validated own host scope, not guessed PIDs. Close/reopen
retains durable receipts; cleanup of fixture groups is separately validated test cleanup.
Concurrent tool batches are not supported: an overlapping gateway operation blocks and
drains rather than opening a second writer. T002 host lifetime audit accepts only a complete,
applicable same-run task-tool baseline→result chain; unexplained files, active alarms,
incomplete/forged receipts and HEAD/index changes block. Runner Git effects across an idle
host lifetime still need T003's explicit integration.

`Gateway.launch` now accepts trusted `scope_kind`, anonymous `inherited_fds` and explicit
`admitted_host_ops`; defaults remain task-tools/DEVNULL/no exemption. Store admission checks
every allowed host's released same-run durable identity and actual live cgroup membership.
The adapter uses this for either the exact current-generation tool request or a settled idle
boundary. It is not permission to dispatch a second task while a host is active. Unknown,
dead, unregistered hosts, active task tools and orphan alarms remain blockers. Engine default
admission stays strict until the task-runner integration.

### One all-role deterministic selector

`sessions.select_session(request, candidates, now_ns, max_age_ns,
min_free_tokens_before_compaction=150000)` is the shared mechanical policy. Inputs are trusted
runner facts: readiness/authorization/reconciliation, role, context affinity, exact profile,
skill/tool/permission/trust/settings/worktree identities, settled sequence and fresh telemetry.
No code/gate Pi sessions are invented. Unsettled/poisoned custody blocks fresh replacement.
At reliable headroom 150000 reuse is eligible; 149999/null/stale/disabled/unknown is not.
Role isolation is mandatory; implement/repair share a family, never reviewer history.
Fresh-only wins ordinary reuse. First independent review is fresh, later review requires its
own exact lineage. Repair prefers the eligible original implementer; remaining candidates
sort latest-settled then stable ID ascending. Reasons and rejected candidates are returned.
An original-question pin outranks greedy selection and **blocks**, never substitutes fresh,
if the original is missing/incompatible/low/unknown. The delivered standalone protocol is below.

Exact reopen requires the original completed host operation, its private saved file/leaf/hash,
matching role/resource/worktree identity and durable last-settled telemetry, followed by new
actual telemetry and normal headroom validation. It never uses continueRecent. Reopen creates
a new counter epoch/baseline even for the same saved counters. T002 supports orderly exact
reopen, not automatic crash recovery or workflow continuation after an unknown operation.

### Focused T002 validation

With the approved private environment, read-only auth/catalog paths, isolated TMPDIR and
explicit existing cgroup/test/live permission, run:

```sh
COHERENCE_LIVE=1 COHERENCE_AUTH_PATH="$READ_ONLY_AUTH" \
COHERENCE_CATALOG_PATH="$READ_ONLY_CATALOG" COHERENCE_TEST_CGROUP_PARENT="$APPROVED_PARENT" \
PYTHONPATH=runtime:runtime/tests python -m unittest \
  test_pi_adapter.BindingTests test_sessions.SessionPolicyTests \
  test_pi_adapter.LifecycleTests test_metrics.UsageSegmentsTests -v
```

Required live/custody cases fail rather than skip when prerequisites are absent. Node
provider-builder negatives intercept fetch (zero network); actual SDK summary/retry tests
inject one 503 then use the authorized actual model. The failure is injected, SDK retry and
summary execution are real. Controlled-pressure abort and real mid-tool host death use actual
SDK gateway tools/cgroups with outside sentinels; synthetic cutoff fixtures do not claim real
high-pressure behavior. No provider calls test separately chargeable-service denial here;
that authority belongs to T003. Normal model traffic has no financial/token reservation gate.
EOF/deadline/pressure/failed settlement leave null final usage/cost and poisoned reuse.

## Standalone task commands and authority

Use the approved Python environment explicitly; the launcher never installs dependencies:

```sh
COHERENCE_PYTHON=/approved/venv/bin/python scripts/coordinate-implementation start \
  --project /canonical/project --run RUN_ID --workflow /approved/workflow.yaml \
  --tasks /approved/tasks.json --owner-catalog /private/owner-catalog.json \
  --manifest /approved/sdk-manifest.json --containment /approved/delegated-parent
scripts/coordinate-implementation status --project /canonical/project --run RUN_ID
```

`intake --project PATH --tasks FILE --owner-catalog FILE --config-hash HASH` performs
non-dispatching structured intake and returns source/contract/scope hashes and task IDs.
The catalog is explicit trusted operator input: a private, owned, single-link regular
file **outside** the agent worktree. Keys are authority refs; values contain exact actor,
record_ref, record_sha256, scope_hash, gate_kind and action. It must represent genuine
external owner evidence, never a worker-created approved file. This is a trusted local
operator interface, not authentication against malicious same-UID processes. The runner
also verifies referenced record bytes and current sources. Specification scope is its
spec source hash; overall/combined/documented legacy scope is the source-list digest;
implementation scope is `approval_scope(contract, config_hash)`. Gate-specific records
bind the exact gate without approval_ref, task ID and config hash. Deny/cancel/drift blocks.
Planning approval alone cannot provide the separate implementation approval.

TinySpec retains separate source/tasks and combined authority; Standard needs spec/plan/
tasks/review plus specification/overall/implementation authority. Structured documented
legacy admits only through a caller-verified settled origin; CLI legacy start currently
blocks rather than inventing a settlement receipt. There is no prose conversion or Epic.
Each dependency must occur earlier; whole REQUIRED/manual/permission contracts survive.

The SDK manifest uses the already delivered explicit settings/resources/auth/catalog
contract. Exact graph profile and skill hashes must agree with delivered SDK resources.
Current node policy may choose fresh-only; this standalone composition closes its settled
host before runner Git effects. Registered `read_file` returns bounded actual authorized
bytes through the gateway; `write_file` has explicit task paths and bounded text. No SDK
built-in shell, Git or ask_user is exposed. Repeated owned writes require the immutable
task-origin baseline plus the complete kernel-empty registered tool audit chain; unexplained
dirty ownership never becomes implicitly admitted. This is not an OS filesystem sandbox.

Preflight aggregates known registered capability, permission, profile, REQUIRED-check and
gate gaps before any task. Ordinary approved-profile model traffic/retries/summaries have
no financial cap or approval/reservation. Separately chargeable service actions require
purpose/cost-impact/scoped authority and durable intent before sending; uncertain/attempted
external effects cannot blindly resend. They are not exposed as generic model tools.

`workflow.FileBytes` is a real exact-file oracle. Registered versioned unittest selectors
are closed code capabilities, not task-supplied shell commands. Missing/unrun/empty/stale/
conflicting proof remains insufficient; optional output cannot release it. Evidence is
persisted by item, environment and final owned bytes; shared checks run once with all item
mappings. Scoped sample STOP APIs persist inspectable bytes/nonce and require an external
owner answer; approval of a sample does not turn an unrun check into success.

Runner Git intent captures baseline, complete files/index, expected tree entries and
operation identity. Explicit owned-only staging and `commit --only -- paths` retain
unrelated staging. Hooks/signing/identity remain enabled and unmodified. Git runs in its
own receipt-validated task-tool scope; nonempty descendants block. Actual parent, tree,
operation trailer, owned diff, residual files and index must all match before a receipt.
A failed or uncertain checkpoint is not replayed. No-change creates no empty commit.
`resume` never redispatches an uncertain partial task; unsupported recovery blocks precisely.

## Explicit recovery and projections

`resume` additionally requires `--resume-authority FILE`: a private, single-link owned
operator file outside the agent worktree, bound to action `reconcile`, run ID, the actual
recorded engine config hash, the sorted exact outstanding operation IDs, actor and truthful
external provenance. This input is not worker-accessible. It authorizes reconciliation,
not guessed completion, new scope or automatic implementation retry. Reentry scans every
unsettled worktree scope, task-tools first, retaining errors while recording known orphan
alarms. Live/unknown work blocks; a valid idle host remains distinct and still cannot be
silently replaced. Empty groups alone do not certify a task.

An exact already-created focused commit may be recovered using its immutable operation
intent, direct baseline parent, full expected tree/path set, current HEAD, file identities
and unrelated index. Only with still-current REQUIRED/gates does recovery record the
checkpoint and original graph result. It never reruns `git commit`. Interrupted SDK turns
or other unknown partial effects block for diagnosis/original-session recovery; no automatic
fresh replacement or reset is implemented. Old complete saver/app results remain audited.

Each CLI controller records real boot/PID/start/UID/parent identity and a stopped event.
Separate `status` uses a read-only SQLite snapshot and reports an absent/dead controller as
interrupted, not running in the background. It includes schema-validated state, config hash,
current task/gate/checkpoint, alarms, operations and projection lag. It never repairs files
or launches Node/models. Unsupported future DB versions produce a precise read-only blocker,
not checkpoint deserialization or downgrade.

The runner publishes `state.json`, `events.jsonl`, `metrics.jsonl` beneath the run's private
runtime directory. SQL remains sole decision authority. Events keep stable SQL ordering and
IDs; public event details are sanitized payload hashes (full restricted receipts stay in
SQL). Historical event timestamps absent from original SQL are explicitly labelled unknown,
not invented. SDK attempt readings preserve real profile/context/counter provenance and
null reasons; non-agent records have no invented Pi session/tokens. Checkpoint metric
revisions supersede, rather than add to, the original invocation's usage.

Publication compares actual complete records with SQL before appending. A torn final suffix
is archived and only that derived suffix truncated. Append-before-cursor crashes deduplicate
from actual complete bytes. A non-tail mismatch blocks for explicit owner-controlled rebuild;
there is no silent rewrite of valid history. State uses fsync plus atomic rename. Status
reports lag without repair. This is process-crash/single-host behavior, not physical power-loss
or hostile same-UID isolation certification.

The settled `Store.backup` API requires explicit scoped backup authorization, no outstanding
operations/alarms and a fresh canonical destination. It uses SQLite's backup API (including
committed WAL state) and integrity check, never a main-file-only copy. No automatic schema
migration or downgrade is provided. Changed runtime/config/registry/schema/resources/inputs/
approvals/host hashes block affected continuation; source/profile changes require the original
producing approval, not a resume flag.

## Bounded repair and independent acceptance

The graph explicitly routes REQUIRED failure to the configured repair node only after an
inspected registered implementation diagnosis. Missing/unrun/stale/unknown/environment/
permission/contract evidence blocks instead of retrying. File-byte mismatch and the contained
`workflow.PythonAnswer` integer-result mismatch are supported objective diagnoses; arbitrary
exception/command failure is not. Repair receives the unchanged original items, partial files,
source authority and original checkpoint baseline. Still-applicable evidence survives;
affected checks rerun. No model/profile escalation or complexity routing exists.

Repair budgets live in SQL under the original failing task or `review-final`, not under a
new correction ID. Zero blocks before host/model dispatch. Each actual repair prompt consumes
one count durably before dispatch, including an interrupted invocation. Capability checks may
stop before consumption; uncertain dispatched effects still block safe replacement. The
configured repair/review gate ceilings bind across restart; changing them changes run identity.

First final review is a fresh independent `review` session, with bounded `read_file` and,
only when explicitly configured and permission-admitted, nonmutating `request_owner_input`.
It receives the complete committed original base→current head patch, source/tasks/approval
content, item evidence, checkpoint refs and prior findings. No implementation history or write
capability is supplied. The shipped graph now uses role-default selection with SQL-derived
settled candidates; explicit fresh-only remains available for ordinary assignments. Exact
saved reopening bridges verified task-tool/checkpoint chains without altering old receipts.
A complete bundle over the supported protocol bound blocks rather than truncating the range.
Review judgment is distinct from mechanical green; malformed/stale-head review cannot accept.

A finding is not executable scope. Unapproved/scope-changing/unknown findings block for owner
contract renewal. A private operator catalog may explicitly supply `workflow_correction_rules`:
a list of records with `criterion_ref`, exact `path`, `original_task_id`, a full structured
correction task template in `task`, `scope_hash=digest(task)`, truthful external `actor` and
`provenance`. The existing authenticated local operator boundary supplies this catalog outside
the worktree; workers cannot author it. Templates must preserve original REQUIRED, optional,
gates and exact owned paths. Rules are pinned as owner input; model action prose never becomes
an executable command or invented approval. Dynamic correction IDs/order are runner-assigned;
each accepted finding becomes a separately authorized focused task/commit. Gate-bound corrections
that need renewed original authority remain blocked, not silently reapproved.

After corrections, affected real checks and the full original base→new-head independent review
run again. Every finding retains a visible unresolved/accepted-focused/resolved disposition;
a current passing rereview can resolve only checkpointed corrections. Acceptance reaudits current
required evidence, original permission/manual gates, full checkpoint chain and exact review head.
Optional green, worker confidence, implementation completion and an old review cannot replace
these conditions. An approved representative sample remains an unrun check until its real oracle
runs. Standalone interaction is delivered below; interactive parent transport remains gated
until its separately verified adapter is delivered.

`status` exposes SQL-derived reviews/findings/budgets, unsuperseded metric records, exact blocker,
current graph/attempt refs and null/unknown reasons without spawning agents or mutating projections.
A successful accepted run releases its durable mutation reservation only after graph/application
audit. A blocked/exhausted/uncertain run retains its evidence/reservation. Ordinary approved-profile
model requests remain unrelated to financial admission; repair counters are not token/spend caps.

### Serialized SDK tool batches and safe Git callbacks

Pi can issue sibling tool calls in parallel. The Python transport validates their original
session/operation/attempt/generation, role, registered version and arguments before placing
requests in a bounded FIFO. Only one task-tool process is active; strict Gateway admission is
not relaxed. Queued/launched/cancelled argument and call hashes are durable facts. Queued work
is unsettled: it prevents prompt success, telemetry, checks/commits and reuse. Abort cancels
never-launched requests and drains/reconciles actual active scopes. Missing cancellation
receipts block reuse even after physical drain. Overflow, duplicates, stale/wrong targets and
premature settlement block explicitly. T006 additionally enforces the separate exclusive
owner-question batch boundary described below; ordinary FIFO serialization alone is not its proof.

Before task dispatch and again before Git hashing/staging/commit launch, admission inspects
configuration, attributes and hook paths using builtins only. Applicable external clean/process
filters and executable (or ambiguous symlink) post-index-change hooks require a registered
contained adapter and currently block. They are never probed, disabled or configured around.
An unused filter declaration does not block a path to which it does not apply; uncertain
applicability fails closed. Built-in normalization remains supported, as do existing contained
commit/signing/hooks. Review patches explicitly use raw builtin diff with external diff and
textconv disabled as display mechanisms, not altered repository settings or waived checks.

SDK failures record allowlisted exception/cause classes, phase and operation refs—not provider
error bodies, tool arguments or credentials. Isolated integration failures retain a private
SQL backup, conversation/worktree copy, input/code/environment hashes and validated empty-scope/
partial-file receipts before fixture teardown. These copies are inspection evidence only;
their copied Git authority bindings must never be adopted as resumable worktrees. Tests retain
old failures as counterevidence rather than treating a later green as a diagnosis of lost data.

Before final review, later approved task changes refresh only stale producer checks, using
current correction proof when it already satisfies the unchanged original items. This creates
new evidence, not an empty commit or a rewritten original checkpoint. Failed/insufficient final
proof still blocks. The launcher disables Python bytecode writes process-locally so ordinary
read-only status does not depend on the caller already setting that environment flag.

## Standalone questions and anytime owner controls (T006)

The runner exposes `request_owner_input` only when BOTH the agent node's tool and permission
lists admit it. Registered tools/permission IDs must exactly fit the supported node manifest;
unsupported restrictive configurations block before SDK launch, never receive a widened tool
set. Preflight aggregates known node-tool/permission gaps. Workers cannot choose a recipient,
approve scope, access workflow storage or invoke `ask_user`. Inside-envelope implementation,
debugging and approved tests remain autonomous. Necessary manager product/priority or unexpected
material-impact questions require why/options/recommendation and scope/complexity/time/cost
impact. These structural checks assist bounded human judgment, not a semantic necessity oracle.

A question must be the ONLY tool in its observed finalized assistant batch. The host rejects
both sides of a mixed question batch before proxying effects; unknown question batches also
block. The runner records request intent, then returns a NORMAL completed `terminate:true`
result. Current tool end, `agent_settled`, prompt completion/idle, empty tool queues and actual
closed-host/task-scope reconciliation precede SQL pending/outbox. A separate sync LangGraph
interrupt records the original node/visit and checkpoint. Until that graph-park receipt exists,
an answer is blocked and the outbox is not eligible for delivery. A parked question is not a
successful task and cannot release verification, commit or dependents.

```sh
scripts/coordinate-implementation pending --project /canonical/project --run RUN_ID
scripts/coordinate-implementation answer --project /canonical/project --run RUN_ID \
  --input /owner/bound-answer.json --input-authority /owner/private-answer-authority.json
scripts/coordinate-implementation control --project /canonical/project --run RUN_ID \
  --input /owner/bound-control.json --input-authority /owner/private-control-authority.json
# Continuation still uses the original start inputs and explicit --resume-authority:
scripts/coordinate-implementation resume --project /canonical/project --run RUN_ID \
  --workflow /approved/workflow.yaml --tasks /approved/tasks.json \
  --owner-catalog /owner/catalog.json --manifest /approved/sdk-manifest.json \
  --containment /approved/delegated-parent --resume-authority /owner/recovery.json
```

Inputs use `interaction.schema.json`'s owner_answer/owner_control shapes. Answers enter with
`delivery: accepted` and `delivery_ref: null`; controls with `stage: received` and null evidence.
Copy the authoritative original/active/run binding, never invent session or source identities.
A CLI answer authority file contains `input_hash=digest(complete_input)`, `scope: within_envelope`
and the exact genuine `receipt` from that input. Its source must be `cli_owner`. A control authority
file instead binds the exact `owner_authority_ref` under `authority_ref`, plus the input hash and
scope. These private, owned, single-link operator files must be OUTSIDE worker tool reach/worktree.
They must represent genuine owner authority, not worker-authored approvals. They are a trusted
local operator channel, not authentication against malicious same-UID processes. The CLI rejects
parent_ask_user receipts until a registered parent adapter can verify their real provenance.
Do not submit secrets/private reasoning; bounded safe question/answer/control content is retained
in restricted SQL and the private original conversation, never exported as raw transcripts.

SQL UNIQUE/CAS acceptance and original delivery are separate. Identical duplicates return the
old receipt without redispatch; conflicting/stale/wrong binding or unverified/scope-changing
inputs reject. Scope changes require producing approval renewal, not a prose interpretation or
an answer flag. Acceptance preserves an original-only delivery obligation across process exit.
Resume revalidates exact source/task/approval/config and original role/resources, closed custody,
saved file/leaf/hash and ACTUAL new-host telemetry. Missing/unsafe/unknown or insufficient original
headroom blocks explicit recovery: no greedy/fresh substitute. Only after that admission does
the host persist a unique bound USER answer entry, reconstruct its context from SessionManager,
and acknowledge its entry ID before the next model request. Unknown delivery blocks blind resend;
accepted content is retained and never reasked. Post-request/result crash gaps without sufficient
settlement evidence remain explicit blockers. Completed app-result-before-saver recovery uses the
saved original visit and never redispatches the ask node.

Ordinary assignments use eligible SQL-retained candidates, exact manifest/role/affinity and
configured fresh telemetry (default maximum age 2000 ms, minimum headroom 150000). Stale/low/
unknown ordinary candidates yield fresh only after custody reconciliation. Repair prefers the
eligible original implementer; first final review is independent/fresh and later review stays
in its own range lineage. Original-question continuation takes priority, opens only that saved
conversation and measures current telemetry rather than renewing an old timestamp.

Controls are accepted while the execution lock is held through a narrow owner-input SQL channel;
SQLite serializes these short transactions with the execution controller. This channel cannot
run graph nodes, choose tasks/models, release process custody or change configuration. Received,
queued, SDK-enqueued (`sdk_delivered`) and actual public worker ACK are distinct immutable events.
Plain steer/followUp uses supported SDK boundaries and retains the generation's actually delivered
skill prompt; it does not re-expand the skill for each control. Public CONTROL_ACK receipts require
both actual persisted incoming-user and later assistant entry IDs. Public message_end precedes
SDK persistence, so receipts are resolved at a subsequent request/idle boundary. Missing ACK stays
visible; an ACK proves observable receipt, not understanding/compliance/private thoughts.

Run-scoped inquiry/pause/cancel uses null worker fields. Inquiry reports recorded facts only.
When no execution controller holds the lock, a short no-agent control consumer can report facts
or reconcile pause/cancel independently; while active, the current runner consumes queued inputs.
Pause/cancel uses supported abort/drain, validated owned `populated=0` scopes and partial files/
HEAD/index reconciliation before a stopped claim. Partial work/history stays intact and no
stopped-worker ACK is invented. Unknown custody remains blocked. No instant shell preemption,
universal absence-of-Pi-process claim or automatic retry of an interrupted task is promised.
Pending question pins cannot be bypassed by steering. Cancellation retains the run reservation;
new mutation requires explicit reconciliation, never automatic replacement.

The four closed v1 selectors are `workflow.QuestionParkTests`, `workflow.OriginalAnswerTests`,
`workflow.ControlDeliveryTests`, `workflow.AutonomyAdmissionTests`. Run their source-named classes
in test_interaction/test_controls with the same approved live/auth/catalog/cgroup environment
used above. Offline binding, crash/SQL and controlled headroom fixtures are distinct from actual
CLI/SDK/LangGraph/original-entry/control/cgroup traces. Parent wake/actual ask_user, transport busy/
outage/reconnect/authentication remain T007, not implied by standalone or historical PoC proof.
