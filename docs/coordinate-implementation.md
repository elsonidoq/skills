# Coordinate Implementation runtime

## Current delivery: executable implementation entry

### Lean runtime amendment (T001)

The operative admission is five facts: valid dependency-ready work with REQUIRED checks,
usable selected configuration/resources, current scoped approval, one-writer safe ownership,
and runnable verification. Recheck a fact only when its input changes. Agents receive scoped
range reads (with continuation), bounded searches and owned edits/checks; a settled local tool
read error is returned with a correction so the same attempt can continue. Optional telemetry
is recorded but never vetoes a settled exact-compatible session. Required/manual gates, scoped
external authority, own-child custody and check-before-focused-runner-commit remain blocking.
This refactor is delivered by approved instruction-managed writer checkpoints; it does not
bootstrap itself through this CLI. T002 delivers revision-aware history below; T003 retains
review/input simplification work.

The suite skill is a thin executable interface; runtime installation remains optional/explicit.
No global installation or automatic reload is performed. The standalone
`scripts/coordinate-implementation` composes the foundation and pinned SDK with structured
intake, authority preflight, real registered checks and focused runner checkpoints.
The packaged task-progress graph uses bounded logical visits in the same LangGraph,
not a separate scheduler. Bounded diagnosed repairs and fresh independent read-only
full-range review now compose that graph. `implementation_complete` is not acceptance:
only current REQUIRED/gates, focused checkpoints, resolved findings and an exact current
full-range independent pass permit acceptance. Interaction commands require their delivered mode-specific authority/capability. `load_workflow(Registry())` still blocks
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
abstractions are instantiated. The wheel contains Python helpers, one YAML, eight schemas, the single pinned SDK host
and its npm manifest/lock; installed console entry is coordinate-implementation.
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
Host discovery uses the source suite or installed wheel data scheme, never the target
project layout. Installed start/resume additionally require --suite-root for approved skill/
settings resources; --project always names the separate execution worktree.

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

These are trusted runner interfaces, **not agent-exposed authority APIs**. Delivered intake,
authority and registered task/review handlers validate external requests and scope before effects.
Unregistered/unavailable capabilities still block before reliance. Fixture handlers used in engine tests are deliberately not Pi/approval certification.

Every successful graph route must traverse intake → authority → custody → verification →
checkpoint → independent review before a registered success terminal. Other terminals may
block early. Only registered bounded task-progress/repair/review/question cycles are admitted; arbitrary
cycles or blind effect retries are rejected. Definition order is not scheduling; configured
handlers/outcome edges/profile/skill bindings determine actual LangGraph routes. Reviewer
nodes are read-only and role isolated; actual fresh-first SDK session selection and current
full-range review are required, not a green synthetic handler. Configuration, declared registry
protocols, schemas and approved inputs remain compatibility boundaries; runtime source bytes
are not permanent run eligibility. See revision-aware attempts below.

## Read-only inventory before launch approval

Before requesting final launch approval, run the **source-local** entry with the already
prepared interpreter and unchanged task contract (installed callers use their approved entry):

```sh
COHERENCE_PYTHON=/absolute/path/to/existing/venv/bin/python \
  /approved/suite/scripts/coordinate-implementation preflight \
  --project /canonical/project --tasks /approved/tasks.json
```

`preflight` validates the task schema and uses the same Git prerequisites, owned-path
cleanliness, and actual full worktree snapshot as task selection. It needs no owner catalog,
model manifest, containment, run identity, approval receipt or database. It neither acquires
Authority nor creates/reserves a run, starts a controller/model, writes workflow storage,
or grants launch authority. Its hashes/counts are observations, not approval receipts or
proof of custody. Recheck after checkout/input changes; all original launch gates still apply.
Start repeats fresh-baseline validation **before** Authority/storage/controller startup.
Resume performs the same safe Git/path/type and actual inventory checks there, but preserves
owned partial bytes for the existing externally authorized recovery and original-baseline
reconciliation; structural inventory alone never approves those bytes or continuation.
The read-only `preflight` command and pending-task selection still require clean ownership;
task selection audits ownership; scoped tools validate their paths/permissions and process
release checks HEAD/index identity, not another whole-worktree inventory. No worker cleanliness-bypass
flag is exposed. A failing entry reports its
relative path and kind (for example `retained/toy/pipe (fifo)`), never its contents.

Inventory enumerates the actual filesystem recursively, independently of Git's untracked/
ignored listing omissions (such as FIFOs and empty directories); Git still supplies tracked
deletions and current index/HEAD identity. Ignored nested repositories include their nested
Git data; no retained ignored user material is deleted, adopted or broadly excluded. Inventory reads
regular-file content and file identity through held directory descriptors, fingerprints
symlink text (including external/broken links) without following it, and records directory
identity plus descendants. Root Git administration and root private workflow storage remain
excluded; identically named nested user directories are not. Unsupported special kinds,
unsafe ancestors and observed read-time changes fail closed. New/removed directories needed
solely as owned-file ancestors are allowed, but unrelated children and replacement of an
existing ancestor still block. This is local cooperative custody, not a hostile-filesystem
atomic snapshot or a sandbox.

A compatible runtime bugfix can open a new revision-aware attempt at a settled boundary.
It does not rewrite old run identity or authorize replay of incomplete effects. The supported
`control cancel` path still retains the reservation; only acceptance releases it. Historical
runs without the new attempt protocol are read-only/unsupported for execution, not silently
adopted. Never clear reservations, manufacture approval or reinterpret old pins.

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
Runner Git checkpoints and exact existing-commit recovery are implemented below. REQUIRED
checks/original gates and actual owned/index/tree/operation receipts precede focused commits;
uncertain effects block instead of blind replay. Signing/hooks remain enabled and scoped;
recovery never invents success, replays commit blindly or discards partial/unrelated work.

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

Runtime installation remains optional/explicit; the skill entry is now executable. On failure
stop dispatch, preserve DB/evidence/partial work/commits,
reconcile only owned scopes and leave unknowns blocked. Do not reset Git, erase history,
auto-resume legacy, install services or infer acceptance. Historical T001/T002 did not amend
policy; the later owner-approved operative amendment and guarded entry cutover are delivered.

## SDK/session seam (internal trusted adapter, composed by the executable runner)

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
Pressure/headroom, including low/unknown values, are optional observations and do not
abort or veto settled continuation. Actual SDK compaction/lifecycle settlement still applies. No token-burn pressure guarantee or universal interrupt deadline is
claimed. The explicit `interrupt` callback is a trusted controlled-test/control seam, not
worker input. It is not evidence of naturally occurring high pressure.

`abort()` poisons reuse, drains registered task scopes using T001's kernel-empty/partial-work
oracle, and requests actual SDK abort/idle. Host death never proves tool quiescence. A live
survivor still records `ORPHAN_PROCESS` before release; resolving it does not resume the run.
`close(force=True)` drains only its validated own host scope, not guessed PIDs. Close/reopen
retains durable receipts; cleanup of fixture groups is separately validated test cleanup.
Concurrent tool effects are not supported: same-prompt requests use the bounded FIFO below;
an unregistered overlapping gateway operation blocks and
drains rather than opening a second writer. Process launch/release/settlement checks Git
HEAD/index identity and actual own-child custody. File ownership/unrelated retained material
are audited at task selection, attempt and checkpoint boundaries, not by per-tool or host
snapshot chains. SDK hosts own no worktree files and close before runner Git effects.

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
skill/tool/permission/trust/settings/worktree identities and actual settled sequence. Telemetry
is recorded separately, not session eligibility.
No code/gate Pi sessions are invented. Unsettled/poisoned custody blocks fresh replacement.
Low/null/stale/disabled/unknown optional headroom does not veto otherwise compatible settled reuse.
Role isolation is mandatory; implement/repair share a family, never reviewer history.
Fresh-only wins ordinary reuse. First independent review is fresh, later review requires its
own exact lineage. Repair prefers the eligible original implementer; remaining candidates
sort latest-settled then stable ID ascending. Reasons and rejected candidates are returned.
An original-question pin outranks greedy selection and **blocks**, never substitutes fresh,
if the original is missing/incompatible/unsettled. The delivered standalone protocol is below.

Exact reopen requires the original completed host operation, its private saved file/leaf/hash,
matching role/resource/worktree identity and durable last-settled lifecycle, followed by
new observational telemetry without a headroom gate. It never uses continueRecent. Reopen creates
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
content directly without a fake child; `search_file` searches the selected chunk with the same
continuation (including query overlap so a boundary-spanning match is not lost). Offsets are UTF-8 stream seek cookies (use the returned offset); limits bound
characters/output, not total file size. `write_file` creates/replaces bounded text;
`edit_file` replaces one unique nonempty old region in an arbitrarily large owned file.
Both reject hard-linked aliases and validate safe regular-file paths and exact task/node permission. Missing/ambiguous edits,
unavailable reads and invalid arguments return correctable errors in the same attempt.
No SDK built-in shell, Git or ask_user is exposed. One writer plus task/checkpoint audits
preserve unrelated ignored/nested material; no per-tool recursive proof chain remains.
This is cooperative scoped authority, not an OS filesystem sandbox.

Preflight aggregates known registered capability, permission, profile, REQUIRED-check and
gate gaps before any task. Ordinary approved-profile model traffic/retries/summaries have
no financial cap or approval/reservation. Separately chargeable service actions require
purpose/cost-impact/scoped authority and durable intent before sending; uncertain/attempted
external effects cannot blindly resend. They are not exposed as generic model tools.

`workflow.FileBytes` is a real exact-file oracle. Registered versioned unittest selectors
are closed code capabilities. `workflow.Command` accepts an explicitly approved REQUIRED
argv array (canonical absolute executable, project cwd, optional positive timeout); it runs
through existing Gateway custody, collecting actual exit/output and a command count. This
is trusted approved project code, not a shell/sandbox or an external-action permission.
`run_check` exposes only approved task item IDs, never worker-supplied argv; its persisted
Verification receipts are audited/reused by verify before checkpoint. Command stdout/stderr
are retained up to 32768 bytes; the worker sees an 8192-character receipt summary with
truncation indicated, not a duplicate full contract. Timeout drains the proven child and remains insufficient. Missing/unrun/empty/stale/
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
migration or downgrade is provided. Changed config/declared registry protocol/schema/resources/inputs/
approvals block affected continuation; compatible runtime revisions do not; source/profile changes require the original
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
It receives the complete committed original base→current head patch, whole authoritative task
contract, complete pinned source/approval `document_refs` (path/raw SHA/kind/section or role,
Git revision only when those exact committed bytes exist), item evidence, checkpoint refs and
prior findings. Source/approval bodies are obtained through existing authorized `read_file`,
not copied into the bundle. Equal canonical original task contracts in receipts use an exact
task-ID/hash reference; unequal and dynamic correction contracts remain complete. No
implementation history or write capability is supplied. The shipped graph now uses role-default selection with SQL-derived
settled candidates; explicit fresh-only remains available for ordinary assignments. Exact
saved reopening verifies the completed original host and empty custody without rewriting receipts.
A complete bundle over the supported protocol bound blocks rather than truncating the range.
Review judgment is distinct from mechanical green; malformed/stale-head review cannot accept.

Every referenced document must be delivered in the originating independent review turn,
including an original-question continuation. Reads recheck current admitted authority and
validate safe identity, raw SHA and UTF-8 on the same bytes returned, within the unchanged
32768-byte read bound. A read callback alone is not delivery: `review_documents` verifies the
existing settled SDK snapshot's private session-file hash and active branch, and joins successful
persisted `read_file` tool-result bytes/call IDs to that turn's actual Gateway process launches.
Only minimal path/hash/identity/process/entry/host/turn/bundle/range proof is retained in SQL;
no document bodies or transcript copy is added. Missing, undelivered or wrong-review coverage
blocks review recording (and finding resolution), and is reaudited with current authority before
acceptance. A prior host/turn's reads cannot substitute for the current review. This uses existing
SDK persistence/receipts, not new host protocol, tools, schema fields or read permissions.
The complete serialized bundle still blocks above120000 bytes; the SDK wire bound stays262144.

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
runs. Standalone and registered interactive-parent interaction are delivered below, each with
its own verified authority/capability boundary.

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
saved file/leaf/hash and actual new-host lifecycle settlement. Missing/unsafe/incompatible original
custody blocks explicit recovery: no greedy/fresh substitute. Only after that admission does
the host persist a unique bound USER answer entry, reconstruct its context from SessionManager,
and acknowledge its entry ID before the next model request. Unknown delivery blocks blind resend;
accepted content is retained and never reasked. Post-request/result crash gaps without sufficient
settlement evidence remain explicit blockers. Completed app-result-before-saver recovery uses the
saved original visit and never redispatches the ask node.

Ordinary assignments use eligible SQL-retained candidates, exact manifest/role/affinity and
actual settlement. Optional telemetry age/headroom does not force fresh substitution;
unsettled effects block replacement. Repair prefers the
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
CLI/SDK/LangGraph/original-entry/control/cgroup traces. The parent adapter below adds its separate
actual launch/wake/tool proof; neither standalone nor historical PoC proof alone establishes it.

## Registered same-parent interaction (T007, explicit mode)

Core standalone start/status/pending/answer/control remains independent of Paseo. Select
`interaction.mode: interactive_parent`, `question_transport: paseo-0.9.2`,
`question_tool: ask_user` and an explicit `parent_binding_ref`. Start/resume additionally
requires `--parent-binding FILE`, a private owned single-link operator descriptor OUTSIDE the
worker worktree. Its closed fields are:

- adapter=paseo-0.9.2, version=0.9.2, binding_id matching parent_binding_ref;
- actual recipient_id, runtime_session_id, canonical official Pi session_file, parent_cwd;
- observed parent_model/parent_effort, explicit generation (positive integer), fresh launch_nonce.

These are pinned observations, not model/task selection or authentication by opaque ID. The
runner verifies public Paseo inspect, exact recipient/provider/cwd/model/effort, current official
session header/active registered bash+ask_user tools and genuine registered launch provenance.
Launch through the actual parent's registered bash tool, asynchronously running the shipped
`coordinate-implementation start ... --parent-binding ...`, then returning the literal marker
`COHERENCE_LAUNCH_RECEIPT:<launch_nonce>`. The literal nonce, exact project/run and start command
must appear in that real tool's arguments/result, not only hidden ambient variables. The existing
single-writer lock still gates the actual runner. A shell background job/detached controller is
not a required daemon; use only an authorized launching interface and approved log/process scope.

Before any task dispatch, code sends a fresh run-bound readiness challenge through PUBLIC
`paseo inspect` / `send --no-wait --prompt-file`. The SAME parent receives the structured
COHERENCE_PARENT_FACADE_V1 event and executes its exact generated `command` (parent-ready).
The runner requires the completed genuine parent bash tool call/result before registering the
interactive capability with the graph. A descriptor, approved flag, registry name, queued send
or bare nonce is insufficient. Missing/unknown/failed readiness blocks interactive start; it
never silently substitutes manual polling or another transport/platform.

The facade is prescribed, not an orchestrator. For a question event:

1. Execute `received_command` verbatim through registered bash. This runner API durably claims
   the event and returns ask_allowed. If false, do NOT ask again: reconcile existing actual tool
   provenance/answer or leave a visible blocker.
2. If true, invoke the ACTUAL registered ask_user using the event's exact question, context,
   options and allowMultiple/allowFreeform/allowComment flags. No task/model/session/outcome choice.
3. After its genuine result, execute `answer_command` verbatim. That API derives the answer
   from the actual registered tool result, not parent prose or a supplied approval file.

The parent must not manufacture tool receipts, choose an option itself in production, approve
new scope or invoke private supervisor/file messaging. Original source/task/approval/config and
same-parent generation remain bound. Material-change answers conservatively block for producing
approval renewal; the genuine tool result remains available and the question is not reasked.
The facade never owns workflow persistence or dispatch: all transitions go through the runner's
narrow validated CLI APIs and SQL. Optional status delivery is not on the execution path and
cannot release a gate or change graph state.

Official Pi session JSONL is read-only provenance, NOT a transport or competing workflow store.
Only bounded active-branch registry/tool metadata, exact nonce-bound argument hashes, call/result
entry IDs and required safe answer facts are retained. No parent thoughts/unrelated text/raw
session is exported. Canonical path/file identity, same UID, regular single-link file and no
group/other writes are required; existing mode0644 parent files need not be modified. This does
NOT promise confidentiality, cryptographic authenticity or protection from malicious same-UID
actors. Missing/partial/rotated/ambiguous/stale evidence blocks or waits boundedly. Fresh challenge
ACK plus public inspection ties the observed conversation/tool generation to the actual launching
parent; process/OS-host continuity is not presumed.

Only SQL pending + actual sync graph-park receipt makes the outbox eligible. Its distinct stages
are recorded → transport_queued → parent_received → question_tool_invoked → answered. Code waits
for idle using a bounded retry (40 attempts, 0.5-second intervals; each public command also has a
10-second deadline), records busy/unavailable/queued facts, and revalidates the pinned recipient/
runtime generation on reconnect. A send receipt is NOT delivery or a worker answer. Actual parent
receipt can reconcile an uncertain send before its acknowledgement, preserving stage ordering.
Durable claim/dedup prevents blind repeated UI invocation; crash after an external ask before a
receipt requires actual tool reconciliation or stays blocked. No exactly-once UI guarantee.

After a bound genuine answer is accepted, the deterministic runner resumes the SAME LangGraph
interrupt and original worker conversation automatically; the facade does not choose a task.
Accepted input survives later transport/resume failure without reasking. UI loss leaves SQL
pending and parent_transport blocker/attempt data in status. CLI owner answers and reconciled
pause/cancel remain usable independently. Host exit promises no background retry; authorized
resume must retain the original inputs and parent binding, never silently rebind a new parent.

The three closed v1 checks are workflow.ParentRoundtripTests (test_interaction_live.py),
workflow.ParentTransportTests and workflow.FacadeAuthorityTests (test_parent_transport.py).
Controlled adapter subprocess/SQL/official-format fixture records are NOT genuine UI evidence.
The separately authorized live test uses actual parent launch/readiness/bash/ask_user provenance,
automatic public Paseo wake, original worker answer-before-request and a public SDK-root UI driver
that responds ONLY to the exact standing-authorized test question/request. That test-only driver
reconnects and revalidates the exact permission before responding; it is not shipped workflow
answer logic or a fabricated human click. It also injects a local command outage then uses the
actual public CLI again; this is controlled fault proof, not a natural daemon outage or hostile
same-UID security certification. Existing valid SDK/settings/custody/control proof is reused.

## Planning intent compatibility

Both task adapters retain whole REQUIRED maps, original source/approval shape and a separate
root executor class/effort intent with assumptions, resolution, provenance and decomposition
rationale. Resolve and approve exact compatible execution bindings before dispatch; unknown,
missing or incompatible intent returns to producing assessment/renewal while preserving the
original snapshot. Standard retains specification and overall/final approval; TinySpec retains
separate source/tasks and combined approval. Planning-only approval never launches execution.
Ordinary model tokens have no financial approval/cap/reservation; separately chargeable service
actions retain purpose/cost-impact and explicit scoped authority. Adopt changed skills/prompts
with `/reload` in pi; this does not automatically activate a global installation.

## Explicit portable setup and cutover

With scoped owner install/network authority, use `scripts/install-workflow.sh --prefix
NEW_ABSOLUTE_DIRECTORY --allow-network` (or install.sh --workflow-prefix with the same arguments).
It refuses existing/foreign prefixes and missing network opt-in before mutation. It creates
only the selected isolated environment, installs pinned dependencies/host lock and prints the
entry; ordinary entry/adoption never invokes it. No global settings/auth/service edits occur.
Source launcher uses suite-relative imports; wheel console/resources work from unrelated projects.
Core CLI has no Paseo dependency. Mode-specific capability blockers remain precise at use.

Default entry cutover requires actual composed multiple-task + fresh independent review +
scoped correction + owner answer + restart + unrelated dirty-index/custom/STATE preservation,
portable installation/resource proof and legacy-active denial. Separate earlier green seams
alone cannot establish composition. Reconcile existing active/unknown legacy workers before
origin reuse; never run both controllers or auto-convert old contracts. The CLI deliberately
blocks unresolved legacy writer state; approval booleans cannot bypass that boundary.

On failed acceptance/unsupported capability, stop dispatch, use bound pause/cancel and validated
own-child drain, reconcile partial files/Git and preserve authoritative DB/Pi evidence/commits/
unrelated work. Disable the new entry through a scoped reviewed focused change. Do not reset,
downgrade the DB, erase history or automatically restart legacy. Legacy requires explicit
compatible current authority and proven no live/unknown writer; otherwise remain blocked.
Implementation completion is not final acceptance; fresh full-range migration review is required.

### Pinned dependency security residual

The pinned SDK0.87.1 lock contains minimatch10.2.6 → nested brace-expansion5.0.9 at
`node_modules/@earendil-works/pi-coding-agent/node_modules/brace-expansion`. Current online
npm audit reports high severity: GHSA-6j4f-fj2g-mc7p (recursive comma parsing, fixed5.0.10),
GHSA-qhr7-859c-m2p7 (nested-brace recursion, fixed5.0.11), and GHSA-q2hr-2g5m-vwhr
(quadratic rewrite, fixed5.0.12). A patch is available; no lock/SDK upgrade or audit-fix was
performed. An empty OFFLINE audit lacks advisory data and is not clearance.

For this bounded host the explicit exact getModel/createAgentSession binding and verified
single-file skills/includeDefaults:false/custom empty-extension resource loader bypass the
SDK package-manager include/exclude-glob and model-scope wildcard expansion paths identified
by source inspection. No affected-input route is established in supported startup/prompt/
original-continuation settings. This is a parent-reviewed nonblocking residual for the current
restricted host, not blanket SDK immunity, zero vulnerabilities, or general CLI safety.
Exposing default/package resources, model-scope/cycle/glob APIs, or finding a supported-input
route immediately invalidates this rationale and blocks acceptance pending a narrow remedy.
The independent full-range migration reviewer must inspect this residual and its rationale.

## Final operating/rollback acceptance boundary

Current public commands are start/resume/intake/status/pending/answer/control and generated
parent-ready/parent-received/parent-answer callbacks. Status/pending print structured JSON
without a --json flag. Intake uses --config-hash; start/resume use the flags above and resume
requires --resume-authority. Generated parent callbacks bind --project/--run/--nonce and,
for received/answer, --event. Do not handcraft an ACK: actual registered launch/tool evidence
is still required. The callback binds its actual interpreter with Python -I and a fixed runpy
bootstrap inserting the actual imported package parent, so caller cwd/PYTHONPATH cannot
substitute another runtime. Source and wheel installations use the same CLI semantics.
Packaged host/manifest/lock live under share/coherence-workflow/pi-host; actual Python/YAML/
schema resources remain in coherence_workflow. No callback installs/provisions anything.

A completed read/tool in an earlier settled batch does not prevent a new observed exclusive
owner-question batch. Current pending/FIFO work, unknown registered process custody, stale/
duplicate identity, mixed batches and post-question effects still block. Lifetime replay IDs
are retained; kernel-empty/Git reconciliation and current SDK settlement precede durable park.

For failed acceptance or unsupported capability: stop new dispatch, submit the bound pause/
cancel, abort/drain actual owned scopes and reconcile partial files/Git before claiming stopped.
An input receipt alone is not pause. If live tools remain, the CLI/runner keeps a blocker until
explicit validated cleanup; unknown scopes/writers are never adopted or killed. Retain SQLite
state/backups, real Pi conversations, immutable event/operation/check evidence, prior task SHAs,
unrelated index/STATE/custom/history and partial owned work. A paused partial task is not accepted.
No DB downgrade, Git reset/rewrite, evidence deletion or inferred task completion is permitted.

Disable only the owner-reviewed selected entry/config through a scoped focused change after
safe drain/reconciliation; do not modify an unowned/foreign link or global installation. This
is a routing/adoption disable, not a new core security switch or permission to bypass paused
state by invoking the CLI directly. Preserve the old runtime read-only for evidence/status.
Never automatically restart legacy. Legacy requires explicit compatible current contract/
authority and proven reconciliation of active/unknown writers; otherwise remain blocked.
Re-enable only after remediation, affected verification and renewed current-range review.
Fresh independent full-range migration review and all current REQUIRED/gates distinguish final
acceptance from implementation completion. Changed skills/prompts need /reload when adopted,
not an automatic global activation or reload of this bootstrap session.

### Concrete builtin action authority and private process payloads

Executable preflight derives the actually exposed node tools and whole REQUIRED check stream,
not merely declared/available registry names. Each applicable action needs a unique explicit
owner envelope declaration, compatible concrete scope/effects, workflow permission and applicable
node restriction. Required oracles are not authorized by registry existence. Potentially mutating
streams additionally declare runner-git-commit as a scoped mutation and workflow permission;
Git remains runner-only, never an agent tool. No-change/read-only effects create no empty commit.

Builtin action_scope is the version=1/action declaration produced by authority.action_requirement.
The approved task contract owns path/check scope; capabilities no longer duplicate task/path/
argument encodings. Exact node permissions/effects and actual task/check membership still
restrict effects. Local read/question is external; write/edit/Git is mutation; checks/run_check
are test. Local external grants no network/paid authority. Command/PythonAnswer execute trusted
project code, not a shell or filesystem/network sandbox; mutation/service authority is not
inferred from a broad test label. Approved models remain exact-profile-bound without financial
ceremony. Exceptional paid/external actions retain their existing scoped original semantics.

At actual checks, registered tools, question admission and Git dispatch the runner rechecks
current admitted original contract/approvals, concrete scope and exact node/workflow policy.
Missing production authorizer fails closed; preflight is not a cached grant. Unknown/omitted/
duplicate/wrong task/path/check/effect declarations return producing renewal, not silent legacy
conversion. Standalone trusted ledger/process protocol fixtures are not executable-workflow
permission substitutes. Source launcher and internal Python helper/write imports bind isolated
actual package roots with -I/-B; cwd/caller PYTHONPATH cannot shadow privileged runtime code.
A separately authorized project-code test retains its own intended project import semantics.

Non-Git process intents/events retain executable, argv_hash, environment_hash and required
custody/Git reconciliation metadata, never the incoming write body or arbitrary argv/env
values. Complete executable data travels only through process memory and the existing private
inherited controller pipe: bounded1MiB initial JSON frame, membership/identity registration,
then a separate matching release nonce before any task effect. The spawned test-hook boundary
means manifest input available but identity not yet observed; spawned_before_payload proves
independent pre-payload EOF cancellation. Malformed/oversize/truncated/EOF/mismatched release
fails closed without payload echo. There is no persistent payload cache or automatic replay.
Exact checkpoint-bound non-content Git argv is the sole retained argv exception, validated
against original operation/task/path/message identity for focused receipt recovery.

Old private/test SQL/event rows remain historical and are NOT scrubbed or relabeled as redacted.
Historical pinned runs remain read-only; new attempts use declared protocol/input compatibility, not whole-code identity. Lost private
payload after interruption cannot be reconstructed/replayed from SQL; unknown effects still
block for explicit reconciliation, preserving partial work and prior receipts. Check evidence
is separately bounded registered-oracle output and must be non-sensitive/sanitized; this is
process-payload minimization, not a general secret classifier or blanket transcript redaction.


## T002 revision-aware attempts and semantic history

This approved amendment retires immutable whole-runtime/module/callable hash eligibility
and per-node code/schema rehash and workflow reload. Admission still validates the actual
workflow/resources, declared handler versions/schemas, configured authority and task bounds.
`Engine.invoke` checks current configuration/authority compatibility once, not before each
node. Runtime changes that alter a handler protocol must change its declared version; this
is not a promise that arbitrary unversioned incompatible code is safe.

`wf_attempts` records ordered runtime-revision attempts, compatibility, exact supplied workflow
YAML and effective graph. Programmatic callers without source bytes retain the serialized
effective configuration. Revision is checkout Git HEAD (null without Git), an observation,
not an attestation of clean/identical source bytes. Unchanged revisions reuse the same attempt;
a changed revision appends one only if original operations are completed, alarms resolved and
original questions settled. The same LangGraph thread/sync SQLite saver and ordered application
receipts are reused: completed effects are reconciled, not dispatched again. Pending SDK/tool/
Git effects stop even same-revision reliance; no automatic migration or new recovery apparatus.
Config/schema/authority incompatibility stops affected execution and requires explicit renewal.

Use `store.read_history(db, run, version=1)` on a private `mode=ro` SQLite connection in a
`BEGIN` snapshot; see the schema owner for the semantic fields. It never opens a writer,
deserializes saver checkpoints or publishes files. Actual checks/decisions/task states, baseline/
result SHAs, dependency order and effect refs stay ordered in SQLite. History is distinct from
optional metrics and files: absent counters stay null; publication errors report an exception
class only and cannot replace success or mask the original execution error in CLI `finally`.
State projections now distinguish `recorded_state` from observed `controller_live`; recorded
running is not evidence of a live controller. Raw private history/configuration is not a public
HTTP DTO; public projection details remain an explicit allowlist/hashes, never raw receipts.

Old application-v1 records/pins are not rewritten. The reader labels records with no attempts
`historical-read-only`; missing retained definitions stay missing rather than borrowing current
YAML. Engine refuses executable adoption. Unknown application/reader versions are unsupported,
with no downgrade or auto-migration. Internal obsolete proof tables are not a frozen reader API.

The monitor's [v1 contract](../specs/004-workflow-monitor/contracts/monitor-v1.md), especially
Eligible runs and pin proof, SQL read/noninterference, and Public DTO field allowlist, needs
separate reader/data-model/source/task approval renewal before consuming this runtime. Its
full Engine-pin/unchanged-runtime assumptions no longer hold; parent/proof-table consumers
also need renewal when T003 retires those protocols. Retain read-only/privacy/honest-unknown
goals, not an unchanged-app compatibility promise. This task does not implement the app,
renew its approvals, or touch/recover the existing incomplete monitor attempt.
