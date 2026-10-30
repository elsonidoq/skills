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
{"provider":"openai-codex","model":"gpt-6.1-terra","effort":"medium","reviewer":{"provider":"openai-codex","model":"gpt-6.1-sol","effort":"medium"}}
```

Without `reviewer`, review retains the selected worker profile for compatibility.
An explicitly malformed reviewer profile fails with a corrective diagnostic, never a
silent fallback. These are selections, not proof of provider availability or actual usage.
For **this repository**, every launch (including continuations/corrections) supplies
`--executor .pi/workflow-executor.json`, or that file's absolute path through the parent
bridge: Terra/medium workers and Sol 6.1/medium reviewers. Other projects retain their own
configuration. Existing historical reviewer nodes are not changed retroactively.

The canonical project-local configuration is `<project-root>/.pi/workflow-executor.json`.
Resolve it once from the suite checkout, then pass the exact absolute path downstream:

```sh
executor=$(python3 scripts/resolve-workflow-executor.py --project /absolute/project) || exit
# Explicit override: add --executor config/custom.json (relative to the project, not cwd),
# or --executor /absolute/selected.json. See --help.
scripts/coordinate-implementation intake --tasks /tmp/tasks.json
scripts/coordinate-implementation start --project /absolute/project \
  --tasks /tmp/tasks.json --executor "$executor" --run fix-title
scripts/coordinate-implementation status --project /absolute/project --run fix-title
scripts/coordinate-implementation resume --project /absolute/project --run FAILED_OR_INTERRUPTED_RUN
# status/history include monitoring recording version, stable occurrence IDs, and safe review ranges when available
```

After an actual current owner grants routine repair/review continuation for one retained run, record that new bounded authority before resuming (the scope is the run's retained original task-scope hash):

```sh
scripts/coordinate-implementation authorize-routine-repairs --project /absolute/project \
  --run FAILED_OR_INTERRUPTED_RUN --scope RETAINED_ORIGINAL_SCOPE
```

If an unreserved pair grant was stopped by target drift, do not rebind it. Refresh the independent review of the current committed target over the retained original range first; a rejected refresh leaves the run stopped for normal explicit resume and a new exact pair, while an approval completes it:

```sh
scripts/coordinate-implementation refresh-review-target --project /absolute/project \
  --run FAILED_OR_INTERRUPTED_RUN
```

The resolver requires only Python's standard library, prints only the absolute selected path on
success, and sends actionable failures to stderr with a nonzero exit. It reads existing JSON and
checks nonempty provider/model/effort strings, including an optional reviewer profile; it never
creates/copies configuration, searches outside the selected path, falls back after an explicit
override fails, authenticates providers or invokes a model. Downstream reads/validation still
apply; resolution does not prove runtime/provider availability. Resume uses retained executor
input rather than selecting new configuration.

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
IDs are no longer executable: supply the actual project command when requesting that check. Checks
run in the project cwd with the runner's inherited environment. Each consuming project owns its
prerequisite diagnostics: make the requested check self-contained (for example,
`env PROJECT_CHECK_MODE=ready python -m unittest`) or use its command-scoped CLI launch (for
example, `project-cli exec -- python -m unittest`). Coherence does not discover arbitrary missing
variables. An attached launch inherits its already-running parent's environment; an `export` in a
worker shell cannot configure that parent, so prefer self-contained check commands there.
Commands run normally with no workflow deadline or output cap. A nonzero required command is retained with its exact command, exit and output as a failed attempt, then returned to the same-task worker for a reasoned safe scoped source/setup correction. A transport return is not task acceptance: the host carries an explicit `completed`, `blocked`, `failed`, or `incomplete` outcome to the runner. A worker finishes its assigned implementation and worker-owned semantic/manual acceptance, reports actual outcomes and remaining blockers, then returns; the runner executes/reruns configured checks, creates the focused checkpoint, and dispatches fresh independent review, without taking over all semantic/manual acceptance or the reviewer verdict. Pending runner stages alone are not unsuccessful. The shared launch prompt requires every initial, corrective and resumed worker/repair invocation to work autonomously through its assigned implementation and worker-owned acceptance. Unfinished code, unrun checks, complexity and correctable or intermittent test failures call for continued scoped work and diagnosis, not an early incomplete return; workers must not assume an unprovided time limit. Real cancellation, execution limits and safety/permission boundaries still apply. If further authorized progress is genuinely blocked, the worker identifies the concrete blocker, actual failed operation/evidence and what is needed to continue. If it must return unsuccessfully, it uses the SDK `report_task_outcome` tool and honestly reports failed/unrun acceptance. This does not permit waived checks, retries-until-green, invented diagnoses or false completion; unmet acceptance never becomes success. Offline prompt checks establish instruction delivery, not model obedience. An unsuccessful outcome, or a missing completion, stops the task before its checkpoint, session settlement, dependent dispatch, final review, or automatic fixer. The runner preserves partial bytes and actual history; when the host returns text with an unsuccessful status, that explanation is retained in the terminal diagnostic and private failure history (with a useful fallback for status-only callers). It is diagnostic evidence only, never acceptance, retry consent, or permission expansion, and safe status/monitor projections do not expose it. The same boundary applies to initial and corrective review-repair returns: an unsuccessful fixer is not checkpointed or marked approved, and no following reviewer is dispatched. On explicit resume, a retained explicit unsuccessful fixer outcome may continue only its same assigned repair after inspecting the diagnostic and reconciling the retained HEAD, exact claimed source/artifact bytes and file modes, and operation-local Git index entries, without Git clean-filter normalization. The corrective brief carries the actual failed call and partial diff, requiring diagnosis and a targeted correction before editing, never an unchanged retry or routine human-debugging question. Missing effect facts or target/source/index drift stops that continuation with staged and working bytes preserved; no replacement pair or uncertain call is replayed. A later returned corrective call takes precedence over historical failures: resume reconciles its checks/checkpoint without another provider call. Before restoring uncommitted ownership after a returned call or passed checks, it verifies retained exact source/artifact working bytes, file modes, and selected-path Git index entries; missing historical facts or drift stops that continuation without adopting bytes or replaying the provider. The continued repair still needs real checks, a focused checkpoint (or genuine no-change), and a fresh cumulative repair-review verdict. It does not scan summary prose, require a universal result format, or replace semantic work with a judging call; ordinary returned text remains compatible. The runner reruns the affected required command and only checkpoints after real passes; an unavailable safe correction or material decision reports its actual blocker. This is neither a skipped check nor cross-task reuse/post-review fixing, and it never spins an unchanged failed command. No universal test collection count, byte pin or evidence applicability receipt.
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
source checkpoint paths; the runner never derives ownership by scanning a clean baseline. A task may
optionally provide `handoff_paths`, a list of exact explicitly authorized pre-existing dirty regular files.
At task preparation the runner records each named file's bytes; at the actual claim it requires those
same bytes, then permits the intended edit and focused checkpoint. A resumed task retains an already
claimed exact transfer, so it checkpoints that intended edit without resnapshotting it or requiring a second edit. This is a narrow transfer, not an
`owned_paths` extension: directory/glob/broad coverage never adopts dirty content. A changed, missing,
symlinked, or unapproved target is refused with its filename, operation, and the corrective action
(restoring its authorized bytes or supplying a current exact handoff entry). Optional `generated_outputs`
names expected task artifacts for selective regeneration/cleanup guidance, not a registration, allowlist,
permission prerequisite, or automatic commit target.

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

Before affected worker reliance, coordinator preparation consumes final-review/handoff material risk
findings: investigate or prepare routine prerequisites within authority, then brief workers with usable
interfaces/findings, evidence limits and remaining gates. Each finding identifies affected tasks,
observed evidence versus unknowns, and next investigation, mitigation or necessary permission; later
discoveries get the same treatment while unrelated safe work continues. An unavailable capability,
access, paid, data or external boundary names the exact affected operation and corrective action and
blocks only affected work. No risk schema, scoring, admission checklist or parent acknowledgment is
introduced.

The receiving coordinator investigates and answers routine technical diagnosis, implementation
choices, ordinary corrections and focused verification within approved authority. Missing technical
evidence calls for investigation or an actionable blocker, not asking the owner to debug. Escalate
only product decisions, consequential unresolved trade-offs, material scope/complexity/verification
expansion, separately scoped spending, or actions outside authority. Autonomous answers never
impersonate owner consent or bypass manual, paid or permission gates. Routine worker or reviewer early
returns are diagnosis events, not completion or owner debugging: inspect the invocation, unfinished
scope, actual checks and retained effects, prepare a targeted correction or evidence handoff, then use
supported history/resume or same-head reassessment paths. Before continuing a failed expensive worker or
reviewer, inspect its recorded cause and invocation; never repeat an unchanged expensive failure.
Respect the retained initial-plus-two same-task/session allowance and compact diagnosis context;
same-head review reassessment uses the existing retained evidence and only its supported eligibility,
never a task replay. Unknown cause or a real permission boundary stops the affected operation with its
exact capability/access/paid/data/external operation and corrective action.

Each task runs in a fresh coding conversation. Ordinary scoped technical fixes, isolated tests/servers,
necessary local/in-project dependency setup, and current-task artifact lifecycle need no owner question.
Small isolated tests and local test databases are allowed for any task, using bounded data/execution
that do not risk exhausting the machine or affecting unrelated data/services. Shared defaults live in
`_ROUTINE_AUTHORITY` in [the runner](../runtime/coherence_workflow/engine.py), included in initial,
corrective, and resumed task prompts; edit that block rather than individual tasks. See [ADR-0004](decisions/ADR-0004-shared-routine-worker-permissions.md).
Prompt delivery is text-contract evidence, not evidence of model obedience or a passed check. Worker continuations and coordinator failure diagnosis receive the actionable failure/diagnosis, targeted correction, unfinished scope, retained task/evidence/history references, and unchanged authority/acceptance constraints—not copied prior prompt bodies; original private history remains inspectable. An earlier agent-authored task, recovery, or handoff demand for
renewed exact-resource/setup/rerun consent does not override this current scoped authority; actual owner limits and
manual, paid, security, data, and external-operation gates still apply. Product decisions, substantial complexity increases,
separately scoped paid usage, and actions outside authority still ask. No global install, credential change,
deployment, push, or unrelated-work deletion is implied. It runs requested project checks and yields a real
focused commit before dependents. Normal Git configuration, hooks and signing are honored. A correctable whitespace, source, hook, or Git checkpoint failure returns to the same task worker with its actual error; affected required checks rerun before the normal checkpoint retry. A reported-failed/interrupted commit is reconciled from that operation's selected paths, attempted parent, and actual result before any retry, retaining a matching SHA without recommit. Failures retain
partial work and report the actual operation error. No empty commit for no-change work. No intent settlement
or operation trailers, hook/filter admission, hidden repair quotas, arbitrary timers or process receipts.
For an exact task-worker saved session, the initial dispatch plus at most two further calls is retained
in required history before adapter/provider dispatch. This narrow allowance includes required-check and
checkpoint corrections and survives process/storage reopen; terminal rows and duplicate observations do
not consume it again. Missing reservation history for retained invocations, or unsettled invocation history for reservations, stops continuation for inspection rather than resetting the allowance. A fourth call is refused before transport with the task/session identity and
inspect-recovery-or-authorized-fresh-context action. It does not create fresh-context authority or cap
reviewer/fixer lifecycle calls.

The final reviewer is a fresh, read-only SDK session, not the worker context. A routine reviewer early
return or evidence gap is a diagnosis/recovery event, not completion or an owner-debugging request:
inspect its invocation, retained task/check evidence, scope and effects; investigate within authority;
and use the supported targeted resume or evidence-only reassessment only when its requirements hold.
Do not repeat an unchanged expensive failed review. Unknown cause, target drift, or an actual
manual/paid/security/data/external gate stops only the affected continuation with the exact operation
and corrective action; unrelated safe work continues. It receives the
actual full committed range and diff on initial review, tasks, and the same routine-authority defaults/exclusions, with only
read/search tools for source continuation. It explicitly reports examined/passing areas and actionable defects.
Follow-up reviewers receive the prior outcome and actual delta from the prior reviewed head, checking repairs,
addressed findings, new defects and affected interactions. They carry forward unaffected passing coverage rather
than restarting the original review. Invalidated conclusions must be explained and re-examined; initial gaps
must be examined or remain explicit. A focused fix review never certifies unchecked original work. The brief separately identifies task/repair checkpoints verified from their actual Git commits, parents and changed paths; no-change means no commit changes, never that an unrelated HEAD is task work. It also gives each reviewer private retained required-command attempts (command, actual result and output) associated with completed task/repair checkpoints. Separately, initial and follow-up reviewers receive each available completed task's exact worker-reported return with its task ID and result checkpoint; missing or unusable historical returns are explicitly unavailable. These reports are not verified check passes or Git facts, and unsuccessful diagnostic returns are not completed acceptance. Reviewers evaluate that evidence semantically: retained passing execution remains valid when a read-only reviewer cannot rerun it; failed or missing required execution is an explicit gap; no live check is invented. On explicit resume, `owner-pair-v1` alone supports one same-head evidence reassessment when the latest settled review rejected for evidence/coverage only with no actionable finding: the coordinator privately retains a substantive targeted diagnosis or newly applicable retained evidence before one fresh read-only reassessment. It reviews outstanding gaps and affected conclusions only, retains the original rejection/range/checkpoints and unaffected coverage, and cannot use a fixer, task replay, empty commit, `refresh-review-target`, replacement verdict, or chain-limit reset. An unchanged handoff, uncertain stage, drift, failed/missing required check, or remaining gap stops the affected continuation. A remaining evidence gap stops that explicit resume after one reassessment; a later resume cannot repeat the preceding reassessment's diagnosis and unchanged evidence. Review ordinals advance independently of repair rounds, retaining causal grants for actual repairs before or after reassessment. Raw check output and worker returns stay out of CLI/monitor projections and review references. The existing evidence digest includes applicable completed returns as well as check evidence; when no usable return exists it retains the historical check-only digest. Historical references and rows are not backfilled. Intervening commits remain unrelated/unattributed integration context, and missing attribution stays explicit rather than guessed. Reviewers neither reject unrelated context solely for task-path scope nor certify it as delivery; causal cross-commit integration defects remain blockers, while independently unrelated defects report ownership/repair limits without expanding fixer authority. Authority does not prove checks or acceptance. The review protocol is `{approved:boolean,findings:string[],coverage:string[],coverage_gaps:string[],suggestions?:string[]}`. Coverage is the cumulative set of actual examined/passing areas, including retained valid prior coverage; gaps include unchecked or invalidated conclusions. These summaries and the prior review/delta base live in existing review-history references, with no schema migration or historical backfill. A historical outcome lacking explicit coverage is supplied as a gap to establish, not inferred passing areas; completed historical verdicts remain unchanged. Suggestions default empty, are nonblocking, and are shown separately from findings. A positive verdict with explicit passing coverage, no gaps and no blockers completes even with suggestions; blockers or gaps reject despite a positive flag. Every blocker uses `path:line - defect` and describes concrete impact and a requirement, correctness, security, or data-safety basis in ordinary prose; no literal basis suffix is required; crashes, hangs, target/credential risks, and false-unavailable observations remain blockers rather than suggestions. A well-formed actionable first rejection continues that same reviewer session for one correction round: the reviewer makes a concise plan and implements its fixes using the configured reviewer model, not the task-worker model. Malformed, interrupted, uncertain, negative-empty, or nonactionable review results stop without fixing; safe deterministic normalization may only recover the actual review result. The runner explicitly enables scoped writer tools only for the review→repair continuation, retaining the review transcript and SDK session identity. Every initial and same-stage corrective repair prompt receives the original task contracts,
unchanged authority, shared routine permissions/exclusions, paid-use boundary, explicit source/artifact
scope and the actual findings. It requires a concise correction plan, examination of directly related
adverse paths, and the integrated result against original acceptance without speculative scope expansion;
a fixer never independently accepts delivery. Its checks and focused checkpoint retain a distinct execution
identity and explicit predecessor. Correctable
check/checkpoint errors stay inside that assigned round and rerun affected checks before its
checkpoint. The existing `fixer` history role identifies this repair stage, not a separate executor-model agent. A process restart before repair reopens the privately retained reviewer session; historical outcomes without a saved session can only use a fresh reviewer-model repair session, without claiming warm-context reuse. Final chain control selects the last eligible persisted stage. New runs retain `owner-pair-v1`: the first repair is automatic, while each later actionable rejection needs an actual-owner durable one-pair grant before its assigned fixer and fresh read-only cumulative repair review. A further rejection asks again unless the current owner has explicitly recorded `authorize-routine-repairs` for that same retained run and unchanged original task scope; it then creates a new exact causal grant/reservation for each routine corrective pair without changing historical questions, rejections, or grants. This narrow authority never covers material scope, paid, security, data, external actions, uncertain stages, or target drift. Historical no-policy runs retain the old two-review/one-fixer limit. SDK compaction/retries follow SDK behavior; compaction/optional telemetry never creates a
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
Without an interactive terminal, or when terminal input reaches EOF, the run stops with a
non-sensitive operation/channel diagnostic and interactive or explicit inspected-resume guidance;
it does not fabricate an answer. Actual parent-channel connection loss or an empty reply likewise
identifies the question/readiness operation and directs reconnection through the parent-session
bridge followed by explicit inspected resume, never automatic retry. These errors preserve partial
work and do not establish recovery success. A loaded project parent-session bridge may instead
launch this same command with its private socket environment;
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

`resume --project ROOT --run ID` is explicit only for a retained failed or interrupted run. Under the ordinary writer lock it inspects retained invocation/cause and original inputs, preserves the original contract/order, executor, paid scope, review base and attempts, skips only checkpointed tasks with matching operation history, and continues unfinished work or the exact eligible review/fix stage. It never compares the worktree, HEAD, index or outputs as admission, repeats a completed checkpoint, replaces a known live writer, resets consumed review slots, or asks again for unchanged paid scope. Missing original/checkpoint history, uncertain completed effects, or uncertain review invocation reports that precise limit. An unfinished task may continue only with its retained task-local source paths and known generated artifacts; those facts permit a selective file cleanup, never adoption or deletion of unknown output. Its exact saved worker-session dispatch history also retains the initial-plus-two allowance across reopen; missing/uncertain identity or history stops that continuation for inspection rather than resetting the allowance.

“No automatic resume” means no blind retry, replay, daemon, or historical restart. When an inspected failure identifies an authorized repair outside the current worker's paths, the coordinator first settles that invocation and its lock, then delegates a separate repair with exact paths and the retained executor. The coordinator inspects the repair diff, runs relevant checks, and verifies its focused checkpoint before an explicit supported continuation of the retained unfinished run. The original worker never gains the repair path or launches a nested CLI. A failed or unknown repair cause is investigated rather than relaunched; a later routine technical question is coordinator-triaged without renewed routine consent. Manual, product, material-scope, spending, security and data boundaries still stop/escalate normally.

For evidence-only reassessment, explicit resume first requires the exact original reviewed HEAD and a retained `owner-pair-v1` findings-free coverage rejection. The coordinator's diagnosis/evidence basis remains private history; safe status reports only a coordinator/assigned evidence-reassessment stage, never the diagnosis. The fresh reviewer has no repair authority and approval still requires cumulative sufficient coverage with no blockers or gaps. For additional owner-authorized repair rounds, resume distinguishes a reserved/dispatched stage with no invocation start from an uncertain started call. Only the former may invoke once. A returned repair retains explicit owned paths and head; resume can continue local checks/checkpoint work without calling the fixer again. A passed checkpoint is retained at its exact SHA/parent. A commit completed before checkpoint-result recording is reconciled against its recorded parent, selected paths and content hashes before retaining it without recommit. Missing facts, uncertain check completion, failed calls, or mismatched target effects stop for inspection. This is scoped additional-round recovery, not historical repair or a general recovery overhaul.

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
runtime dependencies. The SDK dependency lock is install metadata, not exact SDK/Node equality
admission. The shared `runtime/pi-host/sdk.mjs` loader uses an available local package first
(including an explicit isolated installation), then Pi's `PI_PACKAGE_DIR`, then the installed
release named by `PI_CODING_AGENT_DIR/install/current-version` or the default `~/.pi/agent`.
A new Git/Paseo worktree does not need copied `node_modules`. An invalid explicitly selected
package reports its actual error rather than silently switching SDKs.

Package discovery uses Node's package lookup; entry and SDK-dependency loading use Node's ESM
resolver and public package exports, not constructed `dist/` paths or nested dependency paths.
The parent-aware resolver runs in a short-lived Node process with its required resolver flag;
Pi/Paseo need no extra launch flags. It executes no SDK code or workflow transport, and omits
`NODE_OPTIONS` in that resolver process so workflow preloads cannot start there. Caller
symlink-preservation and export-condition flags are forwarded separately; executable preloads
and loaders are not. Actual SDK imports retain the caller's environment and their original errors. Tests use the same loader.
Pi/Paseo updates therefore do not require a fixed installation layout; actual breaking SDK API
changes may still need adaptation. The offline compatibility checks below cover discovery,
public imports, sessions, tools and bridge discovery with the installed SDK, without paid
provider calls. Re-run them after updates; no automatic update, installation, restart or live
model probe is performed. No LangGraph, cgroup delegation, custom SDK tools or host manifests.
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
COHERENCE_PYTHON=python3 node --test runtime/tests/test_sdk_resolution.mjs \
  runtime/tests/test_host.mjs runtime/tests/test_bridge.mjs \
  runtime/tests/test_global_bridge.mjs runtime/tests/test_saved_sessions.mjs
```

These exercise real disposable Git/project/tool operations and clearly labelled offline SDK
transport/compaction fixtures; they do not manufacture live-provider success. Independent final
review remains separate from writer validation. An optional task input `review_base` must resolve to a
Git commit that is an ancestor of the run baseline; it changes that review's actual diff/prompt and every
recorded review outcome to base→current-head. Invalid or unrelated bases fail only the affected review.
A malformed, failed, or interrupted reviewer records that actual selected range before its original error
propagates. Without it, the default
run-baseline→head range is unchanged. In Paseo, adopting changed global skills requires a fresh-session handoff; do not reload or restart the current session automatically.
