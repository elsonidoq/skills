# Coordinate Implementation runtime

## Current delivery: opt-in foundation and SDK adapter

The legacy skill remains the default. `runtime/` now provides an opt-in Python library,
not the production task runner or a replacement slash command. T002 adds a pinned SDK
host, deterministic session policy and telemetry segments. There is **no CLI, task
scheduler, approval adapter, verification/commit handler or policy cutover** in this delivery. The packaged `workflows/coordinate.yaml` declares future boundaries;
`load_workflow(Registry())` blocks on unavailable registered capabilities. Its selected
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
Only create/open/prompt/telemetry/abort/drain/close and correlated tool replies are supported;
owner-answer/steer/follow-up remain unavailable until their later task. Prompt acceptance and
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
if the original is missing/incompatible/low/unknown. The actual owner-input protocol is later.

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
