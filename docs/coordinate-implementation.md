# Coordinate Implementation operating guide

The existing entry runs ordinary requested tasks using Pi SDK tools. This operative contract
supersedes old graph/host/custody/session/evidence eligibility rules. Historical plans, schemas,
approvals and database rows are not rewritten or replayed.

## Run a minimal task

With the runtime dependencies already installed, create these ordinary inputs outside the
project's task-owned files:

```json
[{"id":"fix-title","description":"Correct the page title; run the existing relevant project test."}]
```

Executor JSON uses the actual owner selection, for example:

```json
{"provider":"openai-codex","model":"gpt-6.1-sol","effort":"medium"}
```

An optional `reviewer` object selects the fresh read-only review executor separately:

```json
{"provider":"openai-codex","model":"gpt-5.6-terra","effort":"medium","reviewer":{"provider":"openai-codex","model":"gpt-6.1-sol","effort":"medium"}}
```

Without `reviewer`, review retains the selected worker profile for compatibility.
An explicitly malformed reviewer profile fails with a corrective diagnostic, never a
silent fallback. These are selections, not proof of provider availability or actual usage.
For **this repository**, every launch (including continuations/corrections) supplies
`--executor .pi/workflow-executor.json`, or that file's absolute path through the parent
bridge: Terra/medium workers and Sol 6.1/medium reviewers. Other projects retain their own
configuration. Existing historical reviewer nodes are not changed retroactively.

```sh
scripts/coordinate-implementation intake --tasks /tmp/tasks.json
scripts/coordinate-implementation start --project /absolute/project \
  --tasks /tmp/tasks.json --executor /tmp/executor.json --run fix-title
scripts/coordinate-implementation status --project /absolute/project --run fix-title
scripts/coordinate-implementation resume --project /absolute/project --run FAILED_OR_INTERRUPTED_RUN
# status/history include monitoring recording version, stable occurrence IDs, and safe review ranges when available
```

Set `COHERENCE_PYTHON` only if the dependencies are in a selected environment. Source execution
uses the suite-relative SDK host; installed execution uses its packaged host. `COHERENCE_NODE`
can select an existing Node executable. Optional `COHERENCE_AUTH_PATH` and
`COHERENCE_CATALOG_PATH` select existing SDK credential/model storage; do not print or copy secrets.
No automatic installation, credential refresh, global reconfiguration or model substitution.

## Only six task-linter checks

1. File exists and is readable.
2. JSON/YAML parses into a list, or an object containing `tasks` list.
3. Every task has an ID and work description (`description` or `outcome`).
4. IDs are unique.
5. Declared `depends` references exist.
6. Dependencies have no cycle.

Dependencies determine sequential order; forward references are valid. Empty work reports
`no tasks` before storage, locks or SDK launch. No mandatory check, path list, approval envelope,
manifest, catalogue, graph, original session, cgroup or provenance record.

Implementation launch authorizes ordinary use of the selected worker/reviewer models; no separate
paid-consent question or `paid_scope` is needed for those calls. Paid application/test APIs still need
explicit approval. Declare them in `paid_apis` to request approval before storage or provider launch,
or supply an already approved top-level scope, for example:

```json
{"paid_scope":{"approved":true,"apis":["selected paid application/test API"]},"tasks":[{"id":"fix-title","description":"Correct the page title."}]}
```

Only application/test APIs are separately gated; changing selected model providers does not invalidate
API approval. Any declared paid APIs not covered by the approved scope trigger one current terminal or
attached-parent question. A denied or unavailable answer launches no provider. Credentials and historical
runs are not API approval. The unchanged grant and exclusions follow worker, fixing-worker and read-only
reviewer prompts. Additional paid APIs discovered during execution require approval before use. Existing
`agent_providers` fields remain compatible historical context, not a paid-consent requirement.

Optional `checks` accepts shell command strings, argv lists or objects with `command`/`argv`.
A singular `check` or `required[].check` uses the same command format. Old registered catalogue
IDs are no longer executable: supply the actual project command when requesting that check.
Commands run normally with no workflow deadline or output cap. A nonzero required command is retained with its exact command, exit and output as a failed attempt, then returned to the same-task worker for a reasoned safe scoped source/setup correction. The runner reruns the affected required command and only checkpoints after real passes; an unavailable safe correction or material decision reports its actual blocker. This is neither a skipped check nor cross-task reuse/post-review fixing, and it never spins an unchanged failed command. No universal test collection count, byte pin or evidence applicability receipt.
Optional `gates` contains question strings or objects with `question`/`description`; current owner
approval is needed before that task's worker starts. Other optional context is passed to the worker.

After the final reviewer call has appended its terminal metric row and all child calls have drained, the
runner makes at most one runner-only `workflow: metrics` commit for this run's exact JSONL artifact.
It validates the closed typed rows and exact path/index bytes, preserves unrelated staged and dirty work,
and inspects the actual parent/diff if Git reports an error after a possible commit. The reviewed application
SHA remains separate from the metric artifact SHA; no artifact means no empty commit and no extra review.
A collision, malformed tail, drift, hook/signing failure, or abrupt process death retains bytes and reports
an artifact gap separately without changing the task/review result or automatically recovering/replaying it.
Optional `owned_paths` limits source file/directory scope. Explicit SDK edit/write selections identify
source checkpoint paths; the runner never derives ownership by scanning a clean baseline. Optional
`generated_outputs` names expected task artifacts for selective regeneration/cleanup guidance, not a
registration, allowlist, permission prerequisite, or automatic commit target.

## Real execution and safety

An exclusive Git-worktree writer lock prevents overlapping cooperating runners. The SDK host
inherits that lock while active. A CLI entry waits transparently for that existing lock and may be
cancelled while waiting without creating a failed task/run or replacing its live writer; a platform
that cannot wait returns concrete busy. This is lock entry only, not a queue, watchdog, polling
service, or cancellation-drain claim. At an actual SDK edit/write, the runner protects unsafe/symlink,
out-of-scope, and already-modified target paths. Commands remain ordinary SDK tools, not an
adversarial sandbox: new, modified, deleted, ignored, Git-visible, or undeclared output never
stops a later command or check. The runner stages only explicitly selected source/deliverable
paths; it does not inventory, adopt, or clean arbitrary output.

Task-worker prompts state that the owner-authorized launch approves implementation of the assigned
scope, superseding historical planning-only wording without changing requirements, acceptance, real
manual gates or safety/permission boundaries. Final planning review checks authorization-neutral task
instructions; temporary approval status stays in the approval record. See [ADR-0003](decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md).

The receiving coordinator investigates and answers routine technical diagnosis, implementation
choices, ordinary corrections and focused verification within approved authority. Missing technical
evidence calls for investigation or an actionable blocker, not asking the owner to debug. Escalate
only product decisions, consequential unresolved trade-offs, material scope/complexity/verification
expansion, separately scoped spending, or actions outside authority. Autonomous answers never
impersonate owner consent or bypass manual, paid or permission gates. Before continuing a failed
expensive worker, inspect its recorded cause and invocation; never blindly retry.

Each task runs in a fresh coding conversation. Ordinary scoped technical fixes, isolated tests/servers,
necessary local/in-project dependency setup, and current-task artifact lifecycle need no owner question.
Small isolated tests and local test databases are allowed for any task, using bounded data/execution
that do not risk exhausting the machine or affecting unrelated data/services. Shared defaults live in
`_ROUTINE_AUTHORITY` in [the runner](../runtime/coherence_workflow/engine.py), included in initial and
corrective task prompts; edit that block rather than individual tasks. See [ADR-0004](decisions/ADR-0004-shared-routine-worker-permissions.md).
This authority is not proof that checks passed. Product decisions, substantial complexity increases,
separately scoped paid usage, and actions outside authority still ask. No global install, credential change,
deployment, push, or unrelated-work deletion is implied. It runs requested project checks and yields a real
focused commit before dependents. Normal Git configuration, hooks and signing are honored. A correctable whitespace, source, hook, or Git checkpoint failure returns to the same task worker with its actual error; affected required checks rerun before the normal checkpoint retry. A reported-failed/interrupted commit is reconciled from that operation's selected paths, attempted parent, and actual result before any retry, retaining a matching SHA without recommit. Failures retain
partial work and report the actual operation error. No empty commit for no-change work. No intent settlement
or operation trailers, hook/filter admission, hidden repair quotas, arbitrary timers or process receipts.

The final reviewer is a fresh, read-only SDK session, not the worker context. It receives the
actual full committed range, tasks, and the same routine-authority defaults/exclusions, with only
read/search tools for source continuation. Authority does not prove checks or acceptance. The review protocol is `{approved:boolean,findings:string[],suggestions?:string[]}`. Suggestions default empty, are nonblocking, and are shown separately from findings. A positive verdict with no blockers completes even with suggestions; blockers reject despite a positive flag. Every blocker uses `path:line - defect` and describes concrete impact and a requirement, correctness, security, or data-safety basis in ordinary prose; no literal basis suffix is required; crashes, hangs, target/credential risks, and false-unavailable observations remain blockers rather than suggestions. A well-formed actionable first rejection continues that same reviewer session for one correction round: the reviewer makes a concise plan and implements its fixes using the configured reviewer model, not the task-worker model. Malformed, interrupted, uncertain, negative-empty, or nonactionable review results stop without fixing; safe deterministic normalization may only recover the actual review result. The runner explicitly enables scoped writer tools only for the review→repair continuation, retaining the review transcript and SDK session identity. Every initial and same-stage corrective repair prompt receives the original task contracts,
unchanged authority, shared routine permissions/exclusions, paid-use boundary, explicit source/artifact
scope and the actual findings. It requires a concise correction plan, examination of directly related
adverse paths, and the integrated result against original acceptance without speculative scope expansion;
a fixer never independently accepts delivery. Its checks and focused checkpoint retain a distinct execution
identity and explicit predecessor. Correctable
check/checkpoint errors stay inside that assigned round and rerun affected checks before its
checkpoint. The existing `fixer` history role identifies this repair stage, not a separate executor-model agent. A process restart before repair reopens the privately retained reviewer session; historical outcomes without a saved session can only use a fresh reviewer-model repair session, without claiming warm-context reuse. Final chain control selects the last eligible persisted stage. New runs retain `owner-pair-v1`: the first repair is automatic, while each later actionable rejection needs an actual-owner durable one-pair grant before its assigned fixer and fresh read-only original-range rereview. A further rejection asks again; historical no-policy runs retain the old two-review/one-fixer limit. SDK compaction/retries follow SDK behavior; compaction/optional telemetry never creates a
workflow fatal condition. SDK tools truncate long output with their normal continuation
instructions; the transport has no size cap. A runner may reuse only a returned private saved session identity from the same run after a
successful idle settlement and preceding verified checkpoint. Reuse also requires an explicit
nonempty matching `context_group` and unchanged role, worktree, executor, resources,
instructions, settings and authority; task text or callback identity alone are not mismatches.
`fresh_only` and each independent review select fresh. Review→repair is a continuation of the selected review, not cross-task candidate reuse; it keeps all effective resources except the explicitly enabled writer tools unchanged, including disabled skill discovery through subsequent corrective prompts. Every repair prompt carries the current-launch implementation authority and shared routine permissions/exclusions.
The repair primitive accepts and forwards its caller's explicit rejecting-review, predecessor, fixer identity and
positive assigned round, subject to retained dispatch policy; legacy chain selection still supplies the first repair
assignment, so this does not itself select or authorize an additional lifecycle round. Candidates sort by latest successful settlement then
stable ID. Reuse needs measured effective headroom (context window minus effective reserve minus
occupancy) at least `min_free_tokens_before_compaction`, whose configurable default is 150000.
Unknown, invalid, disabled or inapplicable compaction/headroom facts select fresh rather than
inventing capacity or blocking safe fresh execution. There is no age expiry or file-change routing
rule. Each reopen rebuilds the current task's callbacks, tools and mutation scope. An adapter that understands the
standalone pre-invocation `session` transport record explicitly requests it with
`sessionObservations: true`; absent opt-in keeps the legacy record kinds. The host returns fresh
boundary observations and waits for SDK idle before disposal. Missing optional observations select a fresh
session at the routing layer; they do not stop ordinary SDK/tool correction. The engine keeps a
small private same-run candidate registry and records each selection/rejection reason in private
operation history. It promotes a saved identity only after that task is idle, all required checks
actually pass, and its focused checkpoint succeeds; same-task corrective prompts keep their live
context, while failed or unsettled sessions never route another task.

Material questions, including unapproved paid application/test APIs, use actual current terminal input.
Without an interactive terminal the run stops with the question and does not fabricate an answer. A loaded project
parent-session bridge may instead launch this same command with its private socket environment;
it wakes that parent with the exact pending question (including the paid-scope decision when needed) and returns only its correlated reply to the
waiting worker. A marked owner-only continuation decision instead carries the rejecting execution, original reviewed base/head, original scope, and one-repair/fresh-review/no-repeat effect. The bridge requires registered `ask_user`, tells the parent to call it, and accepts the actual nonempty owner answer only through `coordinate_implementation_owner_reply`; routine `coordinate_implementation_reply` cannot answer it. This is transport routing, not cryptographic proof of human identity, and neither question nor answer is retained in SQLite or public projections. Missing `ask_user`, cancellation, an empty answer, or an unavailable/uncorrelated reply stops with the concrete bridge diagnostic. A callback that cannot accept the owner-only marker/context also stops; it is never retried through routine triage. Routine technical questions remain coordinator-triaged and autonomous. Before attached execution, the runner checks the existing socket's authenticated
readiness response and active parent reply tool; incomplete/mismatched configuration stops before
storage or SDK launch, without terminal fallback. Each worker's actual SDK tool set must contain
`ask_owner` before its prompt starts. This proves current readiness, not future delivery; later
connection failures retain partial work and report the error. No model probe or heartbeat is used.
It retains neither questions nor answers in SQLite. Parent-session shutdown or the
launch tool's cancellation signal terminates only its owned runner through that runner's normal
SIGTERM path and waits for it before bridge cleanup. The bridge is optional: direct terminal
invocation remains unchanged. The project entry is
`.pi/extensions/coordinate-implementation-bridge.js`; Pi auto-discovers `.js`/`.ts`, not `.mjs`.
Noninteractive Pi (including RPC) skips project extensions without project trust. Use explicit
one-run `pi --approve` or an owner-approved saved decision for the exact checkout; never change
global trust defaults or trust parent directories just to load this bridge. A prompt cannot load
tools that startup skipped. In Paseo, use a fresh session and verify checkout, revision, current approval, loaded capabilities, and all four bridge tools
(`coordinate_implementation_start`, `coordinate_implementation_reply`, `coordinate_implementation_owner_reply`, and `coordinate_implementation_steer`) are available before launch;
do not reload or restart the current session automatically. After merging, start in the main
checkout and verify its own trust decision and tool availability: trust is path-specific, not
branch-specific. The bridge uses an executable `scripts/coordinate-implementation` in that session's checkout when present; otherwise it launches the shared `coordinate-implementation` on PATH. Permission errors on an existing local launcher are not silently bypassed. Both paths keep that session's cwd as `--project`, never an old worktree or the suite checkout.
Runner diagnostics go to stderr so they cannot corrupt the parent's RPC stdout. During an attached run, the active worker/fixer privately advertises its exact task and invocation target. The parent may call `coordinate_implementation_steer` only with that exact advertised run/task/invocation and a new direction ID; it returns `accepted` immediately, then parent notifications report `queued`, `consumed`, `failed-unavailable`, or `unknown`. Active-target and steering-status notifications remain visible but do not trigger a parent agent turn; only questions and terminal workflow success/error notifications wake the parent. `consumed` is matching SDK user-message observation, not compliance. No target exists for a reviewer, a completed invocation, or a task-ID-only successor; connection loss stays unknown and is never automatically resent or retargeted. Direction text remains in the authorized parent/worker conversation, not runner history or monitor data. After a bridge change, use a fresh Paseo session, verify checkout, revision, current approval, loaded capabilities, checkout trust, and all four bridge tools (`coordinate_implementation_start`, `coordinate_implementation_reply`, `coordinate_implementation_owner_reply`, `coordinate_implementation_steer`), and obtain separate authorization before any live-provider proof. The bridge starts an explicit same-run continuation with `{run, resume: true}`; it supplies no replacement task or executor input. There is no Paseo
version/transcript/binding/receipt gate. No automatic resume/control mailbox or daemon.
Cancellation aborts the owned SDK session and waits for its host; it never signals parent/sibling
processes or provisions/signals cgroups.

## History, explicit resume and abandon

`resume --project ROOT --run ID` is explicit only for a retained failed or interrupted run. Under the ordinary writer lock it inspects retained invocation/cause and original inputs, preserves the original contract/order, executor, paid scope, review base and attempts, skips only checkpointed tasks with matching operation history, and continues unfinished work or the exact eligible review/fix stage. It never compares the worktree, HEAD, index or outputs as admission, repeats a completed checkpoint, replaces a known live writer, resets consumed review slots, or asks again for unchanged paid scope. Missing original/checkpoint history, uncertain completed effects, or uncertain review invocation reports that precise limit. An unfinished task may continue only with its retained task-local source paths and known generated artifacts; those facts permit a selective file cleanup, never adoption or deletion of unknown output.

For additional owner-authorized repair rounds, resume distinguishes a reserved/dispatched stage with no invocation start from an uncertain started call. Only the former may invoke once. A returned repair retains explicit owned paths and head; resume can continue local checks/checkpoint work without calling the fixer again. A passed checkpoint is retained at its exact SHA/parent. A commit completed before checkpoint-result recording is reconciled against its recorded parent, selected paths and content hashes before retaining it without recommit. Missing facts, uncertain check completion, failed calls, or mismatched target effects stop for inspection. This is scoped additional-round recovery, not historical repair or a general recovery overhaul.

`status` and `history` are read-only, execution-format-only SQLite readers; there is no
legacy-reader fallback. A missing run reports its ID; an unsupported database format reports
incompatibility without changing storage. Only a new `start` quarantines an unsupported database,
under the worktree writer lock and before execution tables are created. It checkpoints committed
WAL data first (busy storage stops recovery), preserves the database and remaining sidecars in a
unique `.coherence/workflow/quarantine-*` directory, reports that path on stderr, and creates clean
execution storage. It never migrates or deletes archived history. `resume` and `abandon` do not
quarantine storage; an archived run cannot resume against the clean database.

New runs privately retain their original parsed contract/order, selected executor, settled authority, resolved initial review base, and `authority.review_policy: "owner-pair-v1"` before dependent mutation. Resume uses those retained inputs; historical absent policy remains the old two-review/one-fixer lifecycle, while an unknown retained name blocks the affected continuation with a compatible-version action. The new policy selects the owner-controlled lifecycle in production. For that named policy, an affirmative actual-owner authorization is an append-only safe fact (grant ID, rejecting execution, exact base/head, original scope reference, assigned fixer/fresh reviewer), never raw question/answer or session data. The grant must be retained before dispatch and is atomically consumed to reserve exactly its fixer; its reviewer becomes eligible only after that fixer succeeds. The store rejects a second grant for the same rejection and validates causal order, exact range, original-scope reference and assigned reservation at dispatch, not just in the engine. Duplicate or mismatched rejection/range/scope/order, failed fixer, and uncertain stages stop actionably without a replacement call. CLI status/history separately projects policy and grant/reservation facts with the next retained stage, without private conversations or sessions. That stage follows actual execution outcomes: completed pairs show completion, failed/uncertain invocations show blocked, and another actionable rejection requires another owner decision. Append-only operation history preserves actual invocation, check and checkpoint outcomes; a corrected check does not replace its failed command/exit/output, and checkpoint facts retain only task-local paths/artifacts and available SHA/parent. CLI output is a safe projection (task IDs, review base and operation facts), never original task text, prompts, answers or check output. This is not a resume policy or a filesystem/Git snapshot.

Ordinary task/run progress is useful history, not dispatch or completion proof. New optional usage reporting appends one JSONL row per actual terminal worker, correction, fixer, or reviewer call, keyed by its exact invocation identity; it never allocates reviewer usage to tasks or mirrors metrics in SQLite. Status derives qualified token subtotals and coverage from those rows plus ordinary exact dispatch identities. Selected session mode/reason is intent, while actual mode/identity requires the current call's opened-session observation. Missing/failed optional appends remain partial or unknown, never zero or an invoice claim, and do not replace task, check, Git, provider, or required-history outcomes. Required original-input, operation-history, progress, and review/fixer dispatch writes are made before their dependent mutation. Review-chain history retains actual execution IDs, attempts/outcomes/uncertainty, consumed review ordinal/fixing round, explicit causal IDs, private parsed findings and commit/range references. It preserves an initial rejection and completed task checkpoint identity across reopen; an uncertain invocation is never a success or replay permission. Status safely exposes parsed findings, nonblocking suggestions, and references separately, not raw reviewer JSON, prompts, saved sessions, or answers. Optional monitor observations remain non-authoritative gaps.  If one reports a SQLite failure, the runner re-reads that specific operation: a known completed write is retained without replay, otherwise it makes one safe local correction; an unreadable or unrecoverable result stops only that affected action with its actual persistence limit. It never reruns task tools or commits to repair progress or invents missing history. Optional monitoring, metrics, and telemetry persistence remains a reported gap and does not block task/check/Git/provider work. Once terminal calls have drained, the runner may make one separately reported metrics-only artifact commit; its SHA/current HEAD is not reviewed application code and does not alter the recorded review range or task checkpoints. Its failure retains the exact artifact bytes and original execution outcome. Old tables/rows in supported mixed-format databases remain in place, including incomplete intents;
unsupported databases are preserved in startup quarantine. New tasks neither reconcile nor replay old rows. Malformed optional history cannot veto new coding.
There is no automatic schema migration, drop, mass conversion or invented successful effect.

After inspecting actual writers and partial work, an operator may explicitly abandon an old run:

```sh
scripts/coordinate-implementation abandon --project /absolute/project --run OLD_RUN
```

This acquires the writer lock, checks current recorded controller/child identities and recorded
scope membership without signalling anything, labels only the run abandoned and releases its old
reservation. It never completes old effects. New failed runs can also be labelled abandoned.
A stale reservation alone is not a live writer. Do not infer safe ownership from SQL, a stale PID
or an old empty-scope observation. A live overlapping writer must not be killed or overwritten.
Inspect/reconcile actual commits before starting fresh work; never blindly replay uncertain
external operations or a possibly completed Git commit. Start a fresh run ID, not the old attempt.

## Setup and verification

Python >=3.10 with PyYAML, local Git/SQLite, and a usable Node/Pi SDK installation are actual
runtime dependencies. SDK 0.87.1 is tested; the dependency lock is install metadata, not exact
SDK/Node equality admission. No LangGraph, cgroup delegation, custom SDK tools or host manifests.
Explicit optional setup remains `scripts/install-workflow.sh --prefix NEW_DIRECTORY --allow-network`
only with separate install/network authority. Ordinary entry never calls it.

For explicitly authorized global activation, add `--global`:

```sh
scripts/install-workflow.sh --prefix "$HOME/.local/share/coherence-workflow" --allow-network --global
```

Choose a new absolute prefix. This installs an isolated Python/SDK runtime and links its command
at `~/.local/bin/coordinate-implementation` and the suite bridge at
`${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}/extensions/coordinate-implementation-bridge.js`.
Existing foreign prefixes or link destinations are preserved and reported. Keep this suite checkout:
the bridge and globally linked skills refer to its current files, while the installed runner is a
snapshot and needs an explicit new-prefix installation to update. Ensure `~/.local/bin` is on PATH.
Pi canonicalizes matching global/project symlink resources, so the same bridge loads once in the
suite checkout as well as unrelated repos. New repos need no copied launcher or bridge, but still
supply their own task file and explicit executor JSON; no model, permissions, adoption policy,
authentication or old run data is copied. Use a fresh Pi/Paseo session and verify checkout, revision, current approval, loaded capabilities, and all four bridge tools;
never automatically reload/restart the current session. Attached runs need a long-lived parent:
use interactive Pi, Paseo, or RPC with stdin kept open until the terminal workflow notification.
A one-shot print/JSON parent can settle after an intermediate notification and exit, which normally
cancels its owned runner; it is not a reliable harness for a nonempty asynchronous run. An empty-task
smoke verifies discovery/launch without creating a workflow store; use a disposable repository for
actual worker/reviewer smoke checks rather than adding runtime artifacts to an unrelated project.
To roll back global activation, remove
only the two proven installer-owned symlinks, leaving the isolated runtime and project data intact.

Focused checks in the prepared environment:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests \
  .pi/workflow-validation/venv/bin/python -B -m unittest discover -v -s runtime/tests
node --test runtime/tests/test_host.mjs
```

These exercise real disposable Git/project/tool operations and clearly labelled offline SDK
transport/compaction fixtures; they do not manufacture live-provider success. Independent final
review remains separate from writer validation. An optional task input `review_base` must resolve to a
Git commit that is an ancestor of the run baseline; it changes that review's actual diff/prompt and every
recorded review outcome to base→current-head. Invalid or unrelated bases fail only the affected review.
A malformed, failed, or interrupted reviewer records that actual selected range before its original error
propagates. Without it, the default
run-baseline→head range is unchanged. In Paseo, adopting changed global skills requires a fresh-session handoff; do not reload or restart the current session automatically.
