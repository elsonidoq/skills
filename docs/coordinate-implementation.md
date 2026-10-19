# Coordinate Implementation runtime

## Current delivery: opt-in foundation only

The legacy skill remains the default. `runtime/` now provides an opt-in Python library,
not the production task runner or a replacement slash command. There is **no CLI, SDK
host, task execution, approval adapter, verification/commit handler or policy cutover**
in this delivery. The packaged `workflows/coordinate.yaml` declares future boundaries;
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
The package has no Paseo/Node dependency at this stage.

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

These are trusted runner interfaces, **not agent-exposed authority APIs**. T002/T003 must
validate external/agent requests and owner scope before exposing any gateway. Production
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
Host scopes may remain idle separately; the SDK host itself is not shipped yet.

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
skill or operative policy was changed by T001.
