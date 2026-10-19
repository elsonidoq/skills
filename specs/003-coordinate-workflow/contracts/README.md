# Proposed executable contracts (v1)

Design artifacts, not installed runtime/config or approved production task assignments.
[Spec](../spec.md) is truth; [data model](../data-model.md) owns proposed persistence and
custody. Schemas use JSON Schema draft 2020-12, closed objects and explicit versions.
JSON is a YAML-compatible structured subset. No LLM free-text parsing chooses transitions.
Examples are **synthetic**, absent owner approvals intentionally; validation never grants
execution authority. Future code packages reviewed schemas under runtime resources.

## Files and entry points

- [shared.schema.json](shared.schema.json): nonempty IDs, digests, paths, provenance,
  criterion/check/gate, profile/skill references and unknown-observation records.
- [task.schema.json](task.schema.json): direct/Standard/legacy normalized contract.
- [workflow.schema.json](workflow.schema.json): registered YAML graph and run policies.
- [agent-result.schema.json](agent-result.schema.json): implementation/repair and review
  results, fixed outcomes/findings and criterion-mapped evidence pointers.
- [execution-result.schema.json](execution-result.schema.json): runner-owned audited outcome,
  REQUIRED dispositions and mandatory survivor-alarm blocking; never model-supplied success.
- [host.schema.json](host.schema.json): one trusted local session host command/event
  envelope. Op-specific constraints in this contract are also mandatory.
- [projection.schema.json](projection.schema.json): state/event/attempt-metric projections.
- [interaction.schema.json](interaction.schema.json): original-session question pin, answer/control
  binding, required parent delivery and upfront authority preflight.
- [examples.json](examples.json): declarative schema-check examples only, not runnable work.

Schema validation is necessary, not sufficient. Runtime semantic/registry/current-approval
checks below always run before affected effects. Unknown fields/versions/handler outcomes
fail closed; do not weaken validation or coerce narrative/booleans into approval.

## Task intake and provenance

Both adapters produce the same structured task object, embedded as a fenced JSON block in
human tasks or as a linked adjacent JSON file covered by the approval digest. Exactly one
machine-readable representation is authoritative; human fields must agree. A complete old
structured subset may be normalized losslessly, retaining original IDs/order/source shape
and original approval evidence. Arbitrary legacy Markdown is not automatically parsed or
converted. Inadequate contracts return to producing review/renewal.

Task root authorization_envelope and each authorization_envelope_id retain the explicit
paid/profile/service/test/network/external/mutation scope and owner approval refs. Unresolved
authority may exist during preparation, but cannot pass paid preflight. No numeric production
budget is selected by an example.

Task `required` retains every item ID, objective criterion, registered check+version/arguments,
pass condition, evidence expectation, producer dependencies and gate IDs. `optional` uses
same item shape but cannot release REQUIRED failures. `context_group` initially story; no
complexity-based task model labels. Envelope allowed profiles constrain the approved YAML
node bindings, not runtime model selection. Paths are explicit ownership bounds, not a filesystem sandbox.
Check arguments are validated by the registered check's own schema; no shell/eval from YAML.

`origin`, `sources` and `approval_refs` carry source/input hashes and external approval provenance.
Each approval ref includes gate kind, scoped artifact digests, answer record digest/reference,
actor/authority provenance and exact affirmative action. A schema-valid reference is **not**
authentication: runner verifies the referenced external record, trusted actor/authority,
current content, review, scope, config and cancellation/renewal before dispatch. No trusted
`approved: true`. Draft adapters may emit empty approval_refs while preparing artifacts;
execution must block. Standard needs specification approval and independent overall/final
artifact review approval; TinySpec combined approval; legacy only its verified documented
original gates. Planning-only authorization never means implementation authorization.

Order is approved source order; all deps must exist earlier, unique item/task IDs and producer
refs resolve, no cycles, contiguous context where original format requires. A later-numbered
prerequisite returns to producing review, never silent reorder. All gates retain original
manual/permission requirements. No default invented sample STOP, no weakening existing STOP.

## Workflow/config validation beyond JSON Schema

YAML safe_load with duplicate-key rejection, no tags/aliases that evade bounded input limits;
reject unsafe paths, symlink escapes and secrets. All handlers/profiles/skills/checks/tool/
permission/containment entries resolve to registered usable versioned capabilities. Schema
shape does not prove exact model/effort support, auth, settings, skill delivery or tools.

Every agent node declares role, handler, profile, skill, session policy, legal outcomes and
limits, per-node tool/permission subsets and retry ceilings. Code/gate/terminal nodes have
no Pi profile/session. Final reviewer is fresh-first and
isolated; fresh-only is supported; no YAML can disable those invariants. All declared outcomes
must exactly match the handler output schema; transition targets exist or registered terminal.
Graph must be reachable and terminate/progress through bounded budget/task loops. Reject
routes bypassing intake, owner/permission gates, custody, verification, task checkpoint or
final independent review. This validation runs on compiled actual LangGraph routes, not
workflow-name conditionals. Node ordering/edges/handlers may change only within safe invariants.

Settings manifest is explicit and hashed; host merges only approved effective settings/trust
without persisting user defaults. Skill paths resolve relative to the registered approved
suite/resource root; task/input/checkpoint paths resolve relative to the selected project.
Neither grants traversal beyond its verified root. Session reuse preference can be configured
within role compatibility; independent-first reviewer isolation cannot be disabled. Monitor
interval/fact freshness are explicit configurable policy inputs, not guarantees against pressure.
Retries are bounded per node and restricted to diagnosed replay-safe/idempotent operations;
unknown external effects cannot retry simply because a budget remains.

Config identity is canonical JSON SHA256 plus versions/content hashes of registry, schemas,
handlers, host, exact profiles, skills/support resources, tools/permissions/settings/trust and
inputs/approval evidence. Checkpoint location is per-worktree authority binding, not a
way to evade locks with a different run dir. Supported schema/config migration needs an
explicit settled boundary and affected approval; active runs never adopt changed YAML.
`max_repair_attempts: 2` and threshold 150000 are configurable approved defaults, not measured
optima or routing ladders. Native RPC is not automatic SDK fallback.

## Agent results and review findings

Model supplies one schema-valid result object through an explicitly named completion tool
or bounded final JSON value. It cannot select a graph edge by prose. Host attaches observed
lifecycle/capability/telemetry; runner derives verification/commit/acceptance. Implementation
`produced` means proposed owned changes, **not** verified success. `read_only` permits no
empty commit after actual audit. Missing/invalid result blocks even if narrative claims green. A recognized completed
request_owner_input may yield owner_input_required and a safely parked execution result
instead of final implementation/review JSON; its question ref/normal completed tool receipt
and settled checkpoint are mandatory. ToolUse stop here is not task acceptance.

Worker evidence pointers are untrusted proposals until runner executes/revalidates checks
on actual bytes/environment. Preserve worker `pass|fail|not_verified` separately from runner
`satisfied|failed|insufficient-evidence`; demonstrated violation is failed, lack of proof is
insufficient. Evidence refs must resolve to bounded permitted files with content hashes,
not arbitrary URLs or traversal. Optional success cannot compensate.

Review `pass|correction|blocked` has findings with stable ID, severity, criterion reference,
location, observed evidence and proposed action/scope. Pass cannot carry unresolved blocking
findings; correction must identify at least one finding. Each finding receives a visible
runner/owner-authorized disposition: accepted focused correction task, declined with inspected
technical rationale, clarification/out-of-scope owner gate, or verified resolved. Reviewers
remain read-only; repairs are separate authorized task contracts/commits with affected checks
and review rerun. Final reviewed head must equal current committed head and cover complete
original base→head plus corrections. No mandatory per-task/per-batch review is added.

## Host protocol (facts only, no orchestration)

Local UTF-8 LF JSONL protocol v1, bounded byte decoder **before allocation of unbounded
lines**, unique string command ID, run/attempt/operation/session binding and per-host monotonic
sequence/nonce. Single controller; authenticated inherited pipes, not open network socket.
Reject malformed/duplicate/conflicting/out-of-order IDs and illegal op/phase combinations.
Continuously drain and demultiplex responses, lifecycle and tool requests independently;
do not discard unmatched early events. Never use low-level agent_end as completion.

| Direction / op or record | Required payload and semantics |
| --- | --- |
| Controller→`create` | Explicit canonical project cwd, private agentDir, profile/skill/resource/tool/permission/settings manifest hashes; exact requested IDs/effort; runner-assigned host/session operation identity; read-only credential/catalog references not secrets |
| Controller→`open` | All create fields plus exact previously reconciled session reference/identity/branch; no continueRecent, no auto profile switch/fallback |
| Controller→`prompt` | Current attempt/operation/contract hash, full REQUIRED brief, task-owned paths, explicit skill invocation/instructions; only one active prompt |
| Controller→`steer`, `follow_up`, `owner_answer` | Runner-validated input ID/current target or original pin+hashes, authorized payload; SDK delivery receipt is not worker acknowledgement |
| Controller→`telemetry` | Current expected session/generation; source version/settings/model/branch and known/null values returned |
| Controller→`abort`, `drain`, `close` | Expected operation/session, cause; abort+waitForIdle/dispose only; does not prove controller tool descendants drained |
| Host→`response` | Same command ID, accepted/failed and sanitized structured error; prompt acceptance is not completion |
| Host→`lifecycle` | Session/prompt generation and sequence, current start/end/settled/tool/retry/compaction state; no narrative outcome parsing |
| Host→`tool_request` | Registered tool ID+version+validated arguments, bound attempt/operation; Python validates/gates/executes, no direct built-in bash escape |
| Controller→`tool_result` | Same tool operation ID, runner receipt/evidence ref and bounded sanitized result; not a host approval decision |
| Host→`request_observation` | Allowlisted provider/model/runtime effort/wire effort and mapping version, valid/blocked flag, request sequence; no raw body/auth |
| Host→`settled` | Prompt promise complete AND current agent_settled/idle, no queued work, final schema result or error; Python still independently drains registered tools before checks/commit |

Envelope `payload` is validated using a fixed op-specific registry schema, not arbitrary
code; the file gives closed envelope and discriminator. Payload validation must reject any
missing required fields described above. Retry, cache warmer and summaries must be observed
and attributable; unapproved background requests off. Guard wraps public streamFunction,
composes existing per-call/SDK hooks first, verifies final provider-specific payload before
send outside swallowed extension errors. Unsupported mapping/version blocks. Pi file/session
writes are permitted conversation storage only, never workflow authority.

Read-only credential/catalog views avoid refresh/global writes. Credential expiry or absent
exact cached model blocks; no auth refresh/install fallback. Effective settings assembled
from approved inputs and explicit trust use one actual SettingsManager passed to both loader
and session. Host reports its effective values/hashes. Mutation tools and process supervision
remain Python-owned. Unexpected EOF/deadline/error poisons session eligibility; no automatic
prompt replay or replacement before durable custody reconciliation.

## CLI and external owner answers

Proposed commands (not implemented): `coordinate-implementation start --project PATH
--workflow FILE --tasks FILE`, `status --project PATH --run ID [--json]`, `resume --project
PATH --run ID --authorization FILE`. No prompt-start convenience grants implementation
permission. Start/resume validate approved source/config/current content and worktree lock.
Resume authorization binds exact gate nonce, remediation/evidence, run/input/config hashes,
actor/authority and scoped action; denial/cancellation/ambiguous/stale records do not resume.
Changing scope/profile/graph requires affected producing review/approval, not a resume flag.

Standalone pending/status/answer/control commands remain independent of UI. Required question
transport is preflighted in interactive mode, not silently replaced by manual polling.

Status is read-only SQL, no Pi/LLM and no file projection mutation. JSON exit/result values
are enumerated: `accepted`, `implementation_complete`, `blocked`, `interrupted`, `cancelled`,
`final_failure`; running status may additionally show `running|reviewing|preflight|parking|waiting_owner_input|paused`. Invalid
input/command returns nonzero with structured error; blocked is not process success-as-
acceptance. Completion/block/failure notifications are optional non-authoritative and cannot delay
the workflow; required pending-owner-question transport is distinct.

## Published records

Projection schema distinguishes state/event/metric payloads. All carry schema_version,
run_id, event sequence and stable record ID. Metric revisions have unique identity and
optional supersedes pointer; consumers select latest revision per attempt and never sum
revisions as separate usage. Fields may be null **with unknown reason**. Request-observed
is not provider-acknowledged; observed skills mean verified loading/delivery, not obedience.
Public status omits sensitive payloads/raw paths to credentials and minimizes raw tool output.
The data model defines authoritative transaction/order and interrupted-tail repair protocol.

## Mandatory process alarm and separate lifetimes

Runner-owned execution-result is validated separately from untrusted agent-result. A logical
worker/task result cannot suppress `ORPHAN_PROCESS`: surviving task-tool group after completion
must persist active alarm + blocked status + replacement_allowed=false before any dependent
work, check/commit or session reuse. State/events/results carry stable alarm IDs and scoped
identity; cleanup records resolution without deleting history. Only actual validated group
empty plus partial file/Git reconciliation can resolve it; acceptance still needs original
REQUIRED/owner gates. Missing/unknown observations block, not success. Notifications optional.

Pi host is a tracked conversation process permitted to remain idle for reuse; its host scope
is distinct from each task-tool cgroup. Do not kill/reflag idle host after every prompt, and
do not leave background tools in its lifetime. Native SDK built-in process tools cannot
bypass the runner gateway. Supported first adapter uses approved Linux delegated cgroup-v2
own children for trusted local processes; no ancestor/service-root kills or PID-only fallback.
Accepted four-case evidence is feasibility, not malicious same-UID escape prevention or
production durable registry/atomic-spawn/remote effects proof. No service setup is automatic.

## Bound question, owner input and upfront authority

Interaction schema distinguishes worker request payload (`$defs/request`) from runner-owned
owner_question, owner_answer, owner_control, parent_delivery and preflight_authority records.
Worker gates/answers bind run/task/node/attempt/session/role and source/task/approval/config
hashes. Run-scoped startup delivery/inquire/pause/cancel uses null worker fields instead of
fabricating a session; steer/followUp requires an actual session target.
Worker cannot select recipient or approve its own envelope. SQL/registry semantic validation
must compare exact current expected identities and trusted owner evidence; schema equality
of strings/nonces is not authentication. Duplicate identical input returns prior receipt,
conflicting duplicate/stale/wrong target rejects; no second delivery/dispatch without actual
session/operation reconciliation. Positive fixtures are not real approval records.

Pending question requires original_only pin and settled park proof. `waiting_owner_input`
status/execution result requires question ref and blocks replacement. Pin takes precedence
over normal greedy reuse/fresh selection; unknown/insufficient headroom or missing/unsafe
original cannot select fresh automatically. A new process may open that original conversation,
receive accepted answer envelope before continuation, and record session-entry receipt.
Scope-changing answer needs producing approval first. Preserve accepted answer when transport
or resume fails; do not reask or replay blindly. Completed normal terminate:true question tool
needs exclusive/all-terminating batch semantics plus prompt/idle/tool drain; mixed batch is
not proven safe merely because this fixture terminated one question tool.

Interactive parent launch records a supported transport capability, exact actual launching
parent and verified readiness/permissions/ask_user receipt. Tested Paseo0.9.2 public fixed-argv
adapter is mode-specific, not a core dependency or authenticated identity solely from flags.
Parent receives committed outbox event, reads pending gate and actually calls ask_user; genuine
response travels through runner input API, never worker-approved files. No private supervisor
channels or universal native-Pi extension assumption. Busy/outage/reconnect/retry/dedup remain
permanent integration tests. A crash around the actual external dialog requires receipt/
invocation reconciliation before any reask; no exactly-once UI side effect is claimed.
Missing UI leaves pending transport blocker; CLI can answer.
No implicit manual polling substitute, required daemon or LLM orchestration in facade.

Owner controls inquire/steer/follow_up/pause/cancel are accepted anytime with active target and
authority binding. received/queued/sdk_delivered/worker_acknowledged are distinct. For steering,
sdk_delivered means the SDK enqueue command was accepted, not that the worker has consumed
or understood it; use actual entry/response/tool acknowledgement for observed receipt. Scope outside
envelope stays blocked for approval; a new approved binding/input is needed afterward. Acknowledged
requires evidence and is not semantic compliance. Inquiry cannot expose private reasoning.
SDK queue does not preempt shell; pause/cancel still needs abort/drain/cgroup/partial-files/Git.
Pause/cancel may finish as reconciled with quiescence evidence, without inventing a worker ACK.

Envelope has selected profiles, effect capabilities/action scopes, real owner approval refs,
paid authority and any owner-selected run limits/enforcement proof. Known gaps are aggregated
before tasks; unresolved/denied authority blocks paid dispatch. Scope-approved technical work,
debugging and small isolated tests do not reask routine cost/mechanics. Only product/priority
or unexpected material impact asks with rationale/options/recommendation. Enum categories
cannot decide semantic eligibility universally. Unexpected safety/auth remains fail-closed.
No universal cost/time threshold, model routing optimizer or production spend inferred from
PoC. Run-wide reservation semantics and supported hard-limit provenance are required; generic
maxTokens/per-host counts/catalog estimates are not hard token/dollar guarantees.
