# Feature Specification: Coordinate Implementation executable workflow

> Historical stage/status/provenance statements below describe their original planning pass, not a permanent veto after the latest owner request. Current-content status: latest owner implementation/batching direction supersedes the original planning-only boundary for the bounded migration. The token-vs-separately-chargeable-service correction and FR-040 await targeted current-content independent review/coordinator audit; no renewal review is claimed. Original manual/safety/permission gates remain. See source-request.md (latest owner directions).


**Feature Branch**: `follow-attached-workflow-migration-instructions`

**Created**: 2026-10-18

**Status**: Revised draft — owner-directed SDK/lifecycle/interaction/autonomy changes during the originating plan pass; renewed specification approval REQUIRED before tasks. Historical approval covers the prior digest only; no migration authorized.

**Input**: [Full original request and conversation addendum](source-request.md). Standard selected by owner; `NO_BRAINSTORM_NEEDED` entry gate supplied by planner. [Decision record](decisions.md) preserves selection, evidence and limits.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Execute approved work without an LLM coordinator (Priority: P1)

As the owner of an adopted project, I start Coordinate Implementation with approved tasks and configuration. The executable workflow, not a conversational agent, selects ready work, dispatches configured agents, verifies results and checkpoints each task before releasing dependents.

**Why this priority**: Removes fragile subjective orchestration while retaining the existing approval and verification protections.

**Independent Test**: Run two dependency-linked toy tasks from the standalone interface with approved contracts; inspect dispatches, checks, commits and status without any coordinating conversation.

**Acceptance Scenarios**:

1. **Given** current approved source/tasks, usable configured profiles and permitted worktree ownership, **When** the owner starts the workflow, **Then** only dependency-ready tasks execute in approved order, one writer at a time, and every task has its own REQUIRED evidence and focused commit before its dependents proceed.
2. **Given** stale approval, a denied permission, an unavailable binding, or an inadequate REQUIRED contract, **When** start/preflight is requested, **Then** execution blocks at the affected gate with its exact missing condition and no unauthorized mutation or model substitution.
3. **Given** the same valid inputs, **When** started through a conversational interface or the CLI, **Then** the same executable transition rules govern; the conversational interface cannot choose tasks, models, sessions or outcomes.

---

### User Story 2 - Configure the graph and reuse eligible sessions (Priority: P1)

As an owner/operator, I configure nodes, skills, profiles and session policies without editing the orchestrator, and get deterministic reuse with measured headroom for every agent role.

**Why this priority**: Configurability and session continuity are required benefits, not a return to LLM-selected batches.

**Independent Test**: Use a supported YAML variation plus controlled telemetry fixtures to observe graph changes, session admission boundaries and role isolation, then verify compatible reuse through real Pi.

**Acceptance Scenarios**:

1. **Given** registered capabilities, **When** only a node's supported model, skill, handler, order or transition changes in valid YAML, **Then** the effective run follows that configuration without engine-source changes and records its provenance.
2. **Given** a ready same-group next task and a settled compatible implementer session, **When** measured free context to the effective compaction threshold is exactly 150000 tokens, **Then** reuse is eligible; at 149999 or with unknown inputs it is not. Cumulative usage alone never establishes eligibility.
3. **Given** a review node or repair node, **When** selecting a session, **Then** review starts independently from implementation, subsequent review rounds may reuse that reviewer's eligible session, and repair prefers the original eligible implementer. No reviewer session becomes an implementer session.
4. **Given** a fresh-only node or a different profile, skill, tool, permission or incompatible context requirement, **When** the node runs, **Then** it receives a fresh compatible session rather than silently changing or contaminating an existing one.

---

### User Story 3 - Recover interrupted work without duplicating side effects (Priority: P1)

As an operator, I inspect and safely resume an interrupted workflow without duplicate agents, repeated commits, lost changes or guessed completion.

**Why this priority**: Durable graph checkpoints alone cannot make external worktree and Git writes exactly once.

**Independent Test**: Interrupt execution after a file write and separately after a commit, restart the actual engine and reconcile the worktree, operation identity, worker lifecycle and commit receipts.

**Acceptance Scenarios**:

1. **Given** an interruption after file mutation but before success persistence, **When** restart occurs, **Then** the runner reconciles partial files and the original worker's live/stopped/unknown state before any writer can resume; uncertainty blocks rather than dispatching a duplicate.
2. **Given** a successful focused commit before its workflow checkpoint, **When** resumed, **Then** the existing matching commit is recovered against its baseline and owned diff, not recreated or blindly replayed.
3. **Given** mid-task context pressure, timeout, retry or compaction activity, **When** the worker is not yet settled, **Then** no completion, check, commit or session reuse is inferred from a low-level end event. Safe interruption/drain and reconciliation precede continuation.
4. **Given** host exit, **When** status is queried from a new process, **Then** durable progress is visible and execution is shown stopped/interrupted until an authorized resume; no promise of background progress is made.

---

### User Story 4 - Inspect evidence, repair failures and receive independent review (Priority: P2)

As the owner, I can see task/attempt progress, real metrics and blockers; failed checks or substantive review findings lead only to bounded authorized repairs and renewed review, never implicit scope expansion.

**Why this priority**: Observable evidence and independent judgment are needed to trust completion separately from acceptance.

**Independent Test**: Exercise a failing REQUIRED check, repair and review-correction loop, exhausted repair bound and manual approval stop; query status separately and compare metrics/projections with authoritative state.

**Acceptance Scenarios**:

1. **Given** a failed REQUIRED item, **When** a diagnosed in-scope repair is allowed, **Then** the configured repair node receives the unchanged original contract, preserves valid work and reruns invalidated checks; missing proof remains insufficient-evidence, not success.
2. **Given** all implementation commits, **When** final review starts, **Then** a fresh independent reviewer receives the full committed range and criterion-mapped proof. Authorized findings become individually verified and committed repair tasks; changed scope returns to owner approval.
3. **Given** a failed configured review gate, **When** correction is authorized and attempts remain, **Then** repair returns to review; exhaustion, unknown failure or unmet approval yields an explicit blocker/final failure rather than an unbounded loop.
4. **Given** a required representative sample/manual stop, **When** a model reports success, **Then** the workflow still waits for inspectable evidence and explicit scoped owner approval before downstream/full expensive work.
5. **Given** unavailable counters or a session restart, **When** metrics are recorded, **Then** unknown fields remain null with provenance and restart-aware accounting; reported current context is not cumulative billed tokens.

---

### User Story 5 - Migrate existing entry points without inventing approvals (Priority: P2)

As a suite adopter, I retain TinySpec, Standard and documented legacy artifacts and technical memory while the implementation entry point becomes executable.

**Why this priority**: A replacement that silently invalidates existing work or weakens gates is not acceptable.

**Independent Test**: Inspect representative TinySpec, Standard and legacy handoffs through compatibility intake; compare preserved source, approval and REQUIRED semantics and verify that inadequate contracts block rather than auto-convert.

**Acceptance Scenarios**:

1. **Given** an approved compatible existing handoff, **When** admitted to the runner, **Then** its provenance, source shape, task IDs and applicable approvals remain intact without a forced Epic or fabricated historical depth choice.
2. **Given** in-progress or insufficiently structured legacy work, **When** migration is attempted, **Then** prior Git/worker state is reconciled and any contract correction returns to producing review and renewed affected approval before dispatch.
3. **Given** existing STATE, technical gotchas, custom documentation and unrelated dirty files, **When** running or rolling back the new workflow, **Then** these remain preserved; no coordinator narrative memory, routing-feedback paperwork or agent-maintained STATE is generated.

### User Story 6 - Intervene through the launching interface without losing autonomy (Priority: P1)

As the owner, I authorize known capabilities and separately chargeable API/service actions before tasks start, then can inquire,
steer or pause. Only genuinely necessary manager-answerable questions wake my launching
interface and use its actual ask_user tool; the original worker conversation receives my
answer before continuing. The interface never selects tasks/models or owns persistence.

**Independent Test**: An actual structured question parks in LangGraph/SQLite, automatically
wakes the same launching parent, invokes actual ask_user and reopens the exact persisted
worker; submit live steering and observe receipt stages/worker acknowledgement. Separate
negative checks reject stale/duplicate/unapproved input and missing separately chargeable API/service authority.

**Acceptance Scenarios**:

1. **Given** known missing permissions/external-action authority, **When** start preflights, **Then** aggregate
   manager-readable choices before any task dispatch; inside the approved envelope, ordinary
   implementation/debugging and approved small isolated tests proceed without repeated questions.
2. **Given** a necessary product/priority or unexpected material-impact question, **When** the
   worker requests owner input, **Then** it uses no ask_user itself; the safely parked durable
   gate wakes the original launching interface, which actually calls ask_user and returns a
   bound receipt. CLI listing/answer works without UI; unavailable UI leaves pending, not success.
3. **Given** an accepted answer, **When** resuming, **Then** the pinned original conversation
   receives it before continuation even in a new host process. Missing/unsafe/insufficient or
   unknown headroom blocks for explicit recovery, never automatic fresh-session substitution.
4. **Given** active work, **When** the owner submits inquiry/steer/pause, **Then** received,
   queued, SDK-delivered and worker-acknowledged stages are distinct; pause drains/reconciles
   before replacement/checks/commits. No private-reasoning access or instant tool-preemption
   claim; changed scope still requires affected approval.

### Edge Cases

- A graph references an unknown handler/profile/skill, an invalid outcome/edge, an unsafe path or an unsupported schema version: reject before side effects (FR-003–005, FR-024).
- Multiple ready tasks or eligible sessions: use documented deterministic order, not an agent's preference (FR-009, FR-014).
- Unknown, stale or inconsistent telemetry; compaction disabled or threshold unresolvable; counters decrease or identity changes: no assumed reuse or invented deltas (FR-013, FR-021).
- Live/unknown orphan Pi worker, interrupted tool, unsettled retries, partial Git operation or HEAD drift: reconcile/block before replacement (FR-016, FR-025–027).
- Two runner processes target one worktree, including different run directories: second writer cannot acquire authority (FR-006).
- Owner denies/cancels a gate or artifacts/config change after approval: do not relabel success; invalidate only affected authority/evidence (FR-007–008, FR-023).
- Projection lags, duplicate replay or truncated append: authoritative store wins; recovery must not create divergent status or duplicate logical history (FR-018–019).
- Empty/already-completed task list: no empty implementation commit or duplicate work; applicable final acceptance gates remain (FR-009, FR-026, FR-030).
- Repair budget zero or exhausted, missing reviewer, out-of-scope finding or unavailable configured repair binding: explicit stop, no escalation (FR-028–031).

## Requirements *(mandatory)*

### Functional Requirements

#### Executable authority and configuration

- **FR-001**: Retain the **Coordinate Implementation** name but replace long-lived LLM coordination with a deterministic executable workflow. A conversational agent MAY start, read status, request authorized resume and explain recorded failures; it MUST NOT own orchestration decisions, persistence or side effects. CLI operation MUST work without that agent, routine bookkeeping LLMs or a background decision-making LLM.
- **FR-002**: Use the empirically selected candidate A: Python LangGraph with SQLite checkpointer and a declarative YAML adapter; do not instantiate redundant LangChain agent abstractions. Owner-selected integration revision permits a thin pinned official Pi SDK subprocess/JSONL adapter for Pi lifecycle, resources, tools and telemetry only. Python LangGraph/SQLite remain sole orchestration and durable workflow authority, including task/session selection, approvals and commits. Pi session persistence is conversation data, not workflow authority. Native Pi RPC/CLI is an explicitly capability-checked compatible alternative only, never a silent fallback. The SDK host was not validated by the original stack-selection PoC. The subsequent owner-authorized [focused SDK probe](../../docs/evidence/workflow-sdk-validation/stack-integration-report.md) is parent-accepted within its tested bounds, not production certification: host death left detached tool descendants writing. Durable worktree-wide operation/process custody and actual restart/quiescence proof are required before production replacement; unknown ownership/quiescence blocks. Effective telemetry/outgoing-binding observations do not establish real high-pressure compaction, durable reattachment or arbitrary-tool containment. Focused permanent production validation remains required before reliance. Tested compatible baseline is LangGraph 1.2.16, SQLite checkpointer 3.1.2, Pi 0.87.1, PyYAML 6.0.3 and jsonschema 4.26.0. No required orchestration server/daemon is presumed; installation/runtime requirements and host-exit behavior MUST be documented. The completed stack-selection PoC is evidence, not future work or production certification.
- **FR-003**: Versioned, schema-validated YAML MUST declare graph node IDs/types, transitions/legal outcomes, agent skill bindings, provider/model IDs and effort, retry/repair limits, session policies, checkpoint/event locations and allowed side effects/permissions. Code and agent nodes plus explicitly defined gate/terminal semantics MUST be supported. Invalid references, illegal outcomes and unsafe/unavailable capabilities MUST fail closed before their effects.
- **FR-004**: The graph, every agent node's model profile and skill, and supported node handlers/order/transitions MUST be configurable without engine-source edits. Handlers, profiles and skills MUST resolve to registered usable capabilities, not arbitrary YAML evaluation or executable payloads. The engine/adapter MUST be reusable without workflow-name conditionals spread through its control logic, but V1 MUST NOT build an unrelated generalized platform.
- **FR-005**: Dispatch MUST verify exact configured provider/model/effort, skill loading, tools, permissions and runtime support and record requested versus observed separately; unknown observed values remain unknown. Unsupported or mismatched/clamped effort, unavailable capability or settings override MUST block, not silently substitute. Illustrative Terra/medium implement/repair and Sol/medium review aliases are not verified provider IDs or an approved production assignment. No runtime LLM model/session/batch selection, automatic escalation, benchmarking, optimizer or routing-feedback loop is allowed.
- **FR-006**: Enforce one writer per worktree across runs/processes, repository/path boundaries and allowed side effects. Preserve unrelated staged/unstaged/untracked work, custom content and user ownership. Ambiguous ownership, concurrent drift, symlink escape or unresolved in-flight writes MUST stop affected mutation; tool instructions MUST NOT be misrepresented as a filesystem sandbox.

#### Approved task intake and sequencing

- **FR-007**: Preserve explicit current-content approvals, security, manual/permission/capability gates and origin-specific evidence. TinySpec retains separate source/tasks and combined approval; Standard retains spec/plan/tasks, specification approval, independent overall review and final approval; documented legacy origins retain their applicable original gates. Denial, cancellation, ambiguity, stale approval or missing evidence MUST block the affected transition; an LLM success output cannot replace an owner answer.
- **FR-008**: Establish a versioned machine-readable task contract or backwards-compatible structured subset carrying IDs, dependencies, `context_group`, REQUIRED item IDs/criteria/checks/pass conditions/evidence/manual and permission gates, optional distinction, deliverable ownership, approved source provenance/content and approval status. Both task-generation adapters MUST preserve these semantics. Inadequate legacy/approved contracts MUST return to producing review/renewal, not executor-defined weaker criteria or unconditional conversion.
- **FR-009**: Code MUST select the next dependency-ready task in approved source order deterministically. Initially story affinity supplies `context_group`. Do not precompute LLM batches, reorder a later-numbered prerequisite silently or merge reused-session tasks. Verified producer acceptance and its focused checkpoint MUST precede dependent work; no ready task means report the actual completion/blocker, not guess or manufacture work.
- **FR-010**: Before mutation, establish task/attempt identity, baseline HEAD, allowed paths, index/worktree ownership, Git identity/signing/hooks/permissions and usable REQUIRED-check prerequisites. Reuse unchanged applicable readiness proof; concrete drift reopens affected checks only. Missing prerequisites block product reliance; setup authority is not proof of usability or permission for installations/external operations.

#### Workflow-wide session selection and lifecycle

- **FR-011**: All **agent nodes** MUST use one workflow-wide deterministic session-selection facility with configurable per-node policies and sensible documented defaults. Code/gate nodes have no Pi session. Explicit fresh-only MUST be supported. Sessions MUST NOT be selected by an LLM.
- **FR-012**: Reuse requires a dependency-ready authorized node/task, compatible context affinity, exact profile/model/effort, skills, tools and permissions, reliable current telemetry and no unresolved live work. Implementation defaults to eligible same-group reuse; repair prefers the original eligible implementer. Review starts independently from implementation and may reuse its own eligible reviewer session for correction rounds; independent reviewers MUST never cross into implementer/repair roles or inherit their conversation. Final independent review's first session MUST be fresh. Different configured profile requires a new compatible session, not changing the old session silently.
- **FR-013**: Begin with configurable `min_free_tokens_before_compaction: 150000`, measured against Pi's **effective automatic-compaction threshold**, not advertised maximum context. At least 150000 free tokens is eligible; less is not. Reliable threshold/current-occupancy provenance MUST account for applicable Pi version/model/effective settings. Missing, unreliable or stale telemetry MUST cause fresh selection, or a precise blocker if fresh cannot safely resolve in-flight state. Current context and cumulative usage MUST remain distinct.
- **FR-014**: Selection precedence, compatibility, tie-breaking and fresh/reuse reasons MUST be documented and observable. Proposed deterministic tie-break: after role-specific preference, select the most recently settled eligible session, resolving equal settlement order by stable session identity. No eligible session means fresh, subject to safety gates. This is a mechanical default for specification approval, not an already-approved behavior.
- **FR-015**: Session admission MUST NOT promise that a single long task avoids compaction. Define safe mid-task pressure/interruption handling: stop new dispatch, interrupt/abort/drain as supported, establish worker/tool quiescence, reconcile partial files and durable operation identity, then continue safely or block. Do not spawn a fresh writer while the old one may still mutate.
- **FR-016**: Prompt dispatch MUST subscribe before sending, correlate command responses, retain lifecycle events and wait for current session-level settlement before after-task telemetry, verification, commits or reuse. For Pi 0.87.1 this is `agent_settled`, not `agent_end`; early/stale events, retries, overflow recovery, compaction, timeout/error and process death MUST not falsely complete a task. An uncertain session MUST be ineligible pending reconciliation.
- **FR-017**: Durable restart MUST reconcile Pi session/process identity and active/unknown work before resume/replacement. Logical worker/task completion (success or failure) with surviving task-tool processes MUST produce a durable `ORPHAN_PROCESS` alarm and blocked status/replacement until proven cleanup and partial-work reconciliation; optional notifications do not replace that authoritative alarm. Reusable idle Pi host lifetime is distinct from per-task tool lifetimes and is not itself an orphan. Safe continuation MAY reuse a verified eligible prior session or start fresh after reconciliation; durable reattachment MUST NOT be presumed from in-process reuse. Missing recovery capability MUST produce a precise blocker, never blind relaunch.

#### State, events, metrics and interface

- **FR-018**: The runner alone MUST own durable execution state. Define one authoritative checkpoint/store and derive human/agent-readable `state.json`, append-only `events.jsonl` and per-task/per-attempt `metrics.jsonl` from it, avoiding divergent decision inputs. Document schemas, versions, logical event identity/order and projection recovery/idempotency, including interrupted writes and stale projections. Minimal automated operational state is allowed; agent-written narrative STATE is not.
- **FR-019**: Provide standalone `start` and `status`, plus explicitly authorized `resume` after remediation. Status MUST expose run/task/node/attempt progress, effective configuration, gate/blocker/failure and checkpoint/evidence references from a separate process without launching an agent. Re-entry MUST recover durable progress without claiming host-exit continuity. Optional completion/block/final-failure notifications MUST NOT delay execution or become decision authority. Required interactive owner-question delivery and independent CLI input follow FR-035–039; they are not optional status notifications.
- **FR-020**: Each task/attempt MUST record run/task IDs; node/profile/skill requested and observed; Pi session identity; context group; fresh/reused and selection reason; start/end timestamps and elapsed time; outcome and retry/repair count; check/evidence mappings; Git baseline/result SHA; input/output/cache-read/cache-write tokens where available; estimated current context at start/end; effective headroom; and telemetry provenance. Unsupported data MUST be null/unknown with reason, never fabricated. Non-agent nodes MUST not be assigned fictitious Pi identities or tokens.
- **FR-021**: Session-cumulative counters MUST produce attributable before/after deltas only with valid identity/counter continuity; restarts, resets and missing observations MUST be accounted for explicitly rather than negative/invented usage or double counting. Real zero cache usage is valid data. Metrics MUST be retained for later user analysis without automatic guideline promotion.

#### Verification, side effects and repairs

- **FR-022**: Workers propose/produce owned task changes; the runner MUST perform real REQUIRED checks, mechanical gates, actual diff/ownership audit and focused task commits/checkpoints. Preserve each item ID, criterion relevance, current revision/environment, concrete output and original gates. Shared checks may run once with every item mapping. Optional green or worker confidence MUST NOT compensate for missing REQUIRED proof; review judgment remains distinct from mechanical verification.
- **FR-023**: Audit REQUIRED items as satisfied, failed or insufficient-evidence. Failed needs demonstrated criterion violation; missing/stale/irrelevant/conflicting/unrun proof is insufficient unless independent observations prove a defect. Preserve defects and limitations together. Only satisfied REQUIRED items and fulfilled gates release dependents; representative-sample STOP requires inspectable sample plus explicit scoped owner approval. Reuse only confirmed-valid proof; later changes invalidate affected items, not all evidence automatically.
- **FR-024**: Persist effective configuration identity/hash/version and approved input provenance. Active runs MUST NOT silently adopt changed graphs, bindings, contracts or approvals. Safe configuration/schema evolution and affected approval renewal MUST be defined; unsupported/unsafe changes block. Logs and stores MUST exclude secrets/credentials, sensitive payloads and unnecessary raw transcripts; checkpoint/event locations and input paths MUST respect project boundaries and permissions.
- **FR-025**: Persist side-effect operation identity/intent and reconcile filesystem, HEAD/worktree/index and commit receipts across restart. Rerunnable handlers MUST be idempotent where possible; uncertain effects MUST block or reconcile before action. Checkpoint replay MUST NOT blindly replay Git, dispatch duplicate workers, overwrite partial work or claim exactly-once external effects. Address other external effects explicitly and require their original authorization.
- **FR-026**: Each authorized retained implementation/repair mutation MUST receive an individually verified focused owned-path Git checkpoint before subsequent task mutation or handoff. Recover a matching existing commit by its baseline, actual diff and receipt rather than duplicate it. Read-only/no-change work makes no empty commit. Missing Git/identity/signing/permissions, failed hooks/checks or ownership conflict MUST stop; do not disable safeguards, configure around failure, stage broadly, push/reset/rewrite or discard unrelated work.
- **FR-027**: Failure handling MUST inspect the failed run/invocation, lifecycle, partial commits and proof before targeted retry/repair/resume. Preserve valid work and attempts, distinguish capability/tool/environment/dependency/contract/permission/unknown failures and retain original acceptance. Unknown causes MUST block blind retry; contract/scope gaps return to producing approval. Clean retry requires diagnosed necessity, safe ownership/mechanics and applicable owner gates, never automatic rollback.
- **FR-028**: Bounded retries/repairs MUST follow configured node limits and the configured repair profile, never automatic model escalation. Proposed initial `max_repair_attempts: 2` remains configurable and subject to specification approval; the PoC's one repair is not a production limit. Exhaustion MUST end in an explicit blocked/final-failure outcome with evidence and remediation, not success or an unbounded loop.
- **FR-029**: Configured substantive review nodes MUST use schema-validated findings/outcomes and explicit pass/correction/block transitions, not narrative parsing. A failed review routes authorized focused repair tasks and reruns affected verification/review; scope-changing findings require owner approval first. Reviewers remain read-only unless separately authorized, and do not become repair producers. Each finding MUST have a visible disposition.
- **FR-030**: All completed task commits MUST receive a fresh independent final review of the complete committed revision range against source/tasks/approval and criterion-mapped evidence. Missing reviewer blocks final acceptance. After authorized focused repairs, eligible reuse of the same independent reviewer for correction rounds is allowed; invalidated review/checks and affected approvals MUST be renewed. Implementation completion and final acceptance MUST be reported separately. No mandatory per-task/per-batch review is added by this feature; configured review nodes remain supported.

#### Migration and preservation

- **FR-031**: Keep planning skill-based; adapt planner, task-generation and affected review/debugging/approval/handoff/checkpoint consumers to executable intake. Replace/remove conflicting subjective implementation batching/model-routing/escalation obligations and execution-path coordinator narrative memory/episodic guidelines paperwork. Preserve technical gotchas, authoritative docs, existing STATE/custom content and historical evidence. Unrelated planning profile-selection policy is not automatically removed.
- **FR-032**: Define versioned compatibility for in-progress/legacy tasks and approved TinySpec/Standard artifacts. No invented approvals, unconditional mass conversion, forced new Epic or silent weakening of REQUIRED contracts. Reconcile in-flight work first; unavailable/inadequate contracts return to the earliest affected producing review/approval gate.
- **FR-033**: The later migration design MUST specify file-by-file adaptation/removal, risk-reduction proof before reliance, bounded coexistence only while necessary, replacement of the implementation entry point, updated references/tests, removal of dead routing/memory execution code, operating docs and explicit rollout/rollback criteria. Rollback MUST preserve durable evidence, prior commits, unrelated work and approval validity and MUST reconcile live writers first. This specification does not itself prescribe task decomposition or authorize that migration.
- **FR-034**: Production acceptance MUST include automated graph/config/handler/result validation, role/profile/skill bindings, affinity/headroom/session selection, restart-aware telemetry, sequential multiple tasks, one-writer/permission/approval enforcement, mid-task interruption/real Pi lifecycle and orphan recovery, post-write/post-commit reconciliation, separate status and review/repair loops. Use the smallest sufficient unit plus realistic integration evidence for each seam; synthetic fixtures alone MUST NOT be called real Pi/security/durability proof. Required live/paid/external checks retain separate permission gates; NOT RUN/UNAVAILABLE is not PASS. Full power-loss/fsync/multi-host guarantees are not established by the PoC and MUST not be advertised without corresponding production proof.

#### Interaction and maximum autonomy

- **FR-035**: Plan/tasks and machine-readable intake MUST declare permitted exact profiles, test/network/external/mutation capabilities/action scope and actual owner approval references. Ordinary approved-profile model requests/retries/summaries MUST NOT require token spending approval, numeric caps or spend reservations; efficient use, metrics/cache telemetry and compaction headroom remain required, not financial gates. Separately chargeable API/service actions MUST have purpose and likely-cost/cost-impact explanation and explicit scoped owner approval before effects; persist relevant action authority and any owner-selected limits without mandatory amounts/limits or a generic billing platform. Preflight MUST aggregate all known capability/permission gaps before tasks with manager-readable options. Missing/denied/unknown external paid authority blocks those actions only, not ordinary approved-profile model traffic. Inside-envelope technical/debug/approved-test work MUST NOT reask routine costs/mechanics. Unexpected out-of-envelope auth/safety/material impact still blocks; no unsupported hard-cap claim.
- **FR-036**: Workers MUST use schema-validated `request_owner_input`, never direct `ask_user`. Ask only manager-answerable product/priority decisions or genuinely unexpected material scope/complexity/time/cost impact, with why progress needs an owner, options, recommendation and impact. Ordinary technical implementation/debugging and inside-envelope tests remain autonomous. Category enums alone MUST NOT be represented as universal semantic eligibility proof. Question admission MUST freeze new conflicting work, complete the question tool normally and safely settle/drain the current batch before persisting a pending gate/checkpoint; do not leave an unfinished tool call awaiting human input or treat an arbitrary mixed batch as proven safe.
- **FR-037**: Interactive-parent launch MUST pin the actual launching/status interface identity and permissions and preflight a supported required notification/question capability. The deterministic runner MUST automatically wake that same interface for an eligible pending question; the interface MUST actually invoke its registered `ask_user` and return truthful bound response provenance through the runner. It MUST NOT decide orchestration or fabricate approvals from worker-written files/opaque IDs. Required owner-question transport is separate from optional notifications; no silent manual-polling fallback in interactive mode. CLI-only mode remains portable and can list pending questions/answer independently. UI loss leaves durable pending state; busy/reconnect/outbox retries and acknowledgements MUST be bounded, idempotent and observable, never an always-on decision-making LLM requirement.
- **FR-038**: A pending owner question MUST pin the ORIGINAL worker persisted conversation, role and source/task/approval/config identity, not its OS process. Accepted answer MUST be durably bound by unique input/gate IDs, nonce and verified owner/parent provenance and delivered to that conversation before continuation. No greedy-headroom/fresh-session substitution is allowed for this continuation. Missing/unsafe/insufficient-headroom or unknown-telemetry original session MUST block for explicit owner recovery; do not promise impossible continuation. Stale, duplicate, wrong-session/source/role/config or unauthorized inputs MUST not dispatch a duplicate worker or consume an answer twice. Durable accepted input is distinct from transport delivery and retry; recovery preserves it without reasking. Source/scope-changing answers require original producing approval renewal.
- **FR-039**: Owners MUST be able to submit inquiry, steering/follow-up, pause or cancellation at any time through the runner's bound control interface. Code MUST bind active run/task/attempt/session/role and authority, persist received/queued/SDK-delivered/worker-acknowledged stages separately and apply supported SDK execution-boundary delivery, not instant shell interruption. Inquiry reports facts or requests an observable worker response, never reads private reasoning or guarantees semantic compliance. Pause/cancel MUST use supported abort/drain and existing cgroup/partial-work reconciliation before verification, commit, reuse or replacement. Out-of-envelope/scope-changing control requires owner/producing gates; absence of acknowledgement MUST remain visible, not success.

- **FR-040**: Planning MUST capture the intended coding model class and effort separately from planning-producer profiles before architecture/task decomposition, adapt task specificity and boundaries to explicit capability assumptions, and preserve that intent/rationale in human and machine handoffs. Apply the normative [execution-profile-aware planning amendment](execution-profile-planning.md), including its qualitative rubric, unchanged quality/safety obligations, compatibility assessment on profile change and T008/V1 verification. This is not current execution/spend authorization or automatic model routing.

### Key Entities *(include if feature involves data)*

- **Workflow definition/configuration**: Versioned graph, node capabilities, exact profiles/skills, policies, locations, permissions and immutable run-effective identity.
- **Approved task contract**: Source and current approval provenance, ownership, order/dependencies, affinity, REQUIRED items and gates; remains independently verifiable even when sessions are reused.
- **Workflow run/checkpoint**: Durable run identity and graph/task/attempt position, effective inputs, gate outcomes, side-effect reconciliation and completion versus acceptance status.
- **Agent session**: Pi session/process identity, role isolation, compatibility, lifecycle/quiescence, current telemetry and eligibility; shared selection does not merge role contexts.
- **Attempt/evidence record**: Requested/observed binding, skill/session, counters/context provenance, checks, result, baseline/result SHA and retries/repairs.
- **Operation receipt**: Durable identity and observed result of an external effect used with actual Git/worktree/process evidence to reconcile uncertain completion.
- **Review finding/approval gate**: Criterion-bound judgment and disposition, authorized repair scope or owner decision tied to current artifacts; neither is implied by a mechanical pass.
- **Owner interaction/authority**: upfront approved profile/capability/external-action authority envelope, original-conversation question pin, bound answer/control IDs, actual launching-parent dialog provenance and durable delivery outbox; no workflow authority in the facade.
- **Status/event/metric projections**: Versioned derived views of authoritative state with documented logical ordering/recovery, not competing persistence authorities.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An approved two-task dependency sequence completes from the standalone interface with no orchestration LLM decisions, exactly one focused checkpoint per changed task and zero dependent releases before all original REQUIRED items/gates are satisfied (US1; FR-001, 006–010, 022–026).
- **SC-002**: Supported configuration-only variations change the selected graph route and requested profile/skill without controller edits; every invalid configuration/capability case in the acceptance checks blocks before its prohibited effect (US2; FR-003–005, 024).
- **SC-003**: Session admission checks distinguish exactly 150000 from 149999 free tokens and unknown telemetry; all agent roles follow their configured policy, reviewer independence and recorded selection reasons. Real sequential work demonstrates eligible reuse without combining task evidence (US2; FR-011–017, 020–021).
- **SC-004**: After the required post-write, mid-task and post-commit interruption cases, safe restart produces zero duplicate active writers, zero duplicate task commits and no lost unrelated changes; unresolved state is visibly blocked rather than reported complete (US3; FR-006, 015–019, 025–027).
- **SC-005**: For every exercised task/attempt, an operator can inspect all required evidence/metrics fields and explicit unknown reasons, reconcile attributable usage across session reuse/restart and obtain consistent current status from a separate process without a conversational coordinator (US4; FR-018–024).
- **SC-006**: Failing checks/reviews exercise correction and exhaustion paths under the configured bound; zero unmet owner gates are bypassed, every accepted mutation is individually checkpointed and final acceptance requires independent full-range review (US4; FR-007, 023, 026–030).
- **SC-007**: Representative TinySpec, Standard and documented legacy intake checks preserve their source and approval semantics or stop precisely for producing review/renewal. Migration documentation covers operation, coexistence, cutover and safe rollback, with no new narrative STATE or coordinator-memory execution paperwork and no production-readiness claims based only on the toy proof (US5; FR-031–034).

- **SC-008**: An actual interactive launch demonstrates automatic same-parent wake, actual ask_user, safely checkpointed pending question, bound original-conversation reopen/answer-before-continuation and live steering with separately observed acknowledgement; wrong/duplicate/stale inputs produce zero duplicate dispatch. Unsafe original/session/transport conditions are visibly pending/blocked, not fresh substituted (US6; FR-036–039).
- **SC-009**: Preflight fixtures identify known capability/permission/external-action authority gaps before any dispatch; zero separately chargeable API/service dispatch occurs with absent/denied/unknown authority and zero routine owner questions are required for exercised approved technical/test actions. Scope-changing input cannot bypass approval, and submitted pause/control remains honest about delivery/quiescence/acknowledgement limits (US6; FR-035–039).

## Assumptions

- This remains **planning-only**. Parent inspection and owner approval of the original digest released `plan_create`; the owner subsequently selected the thin SDK host and authorized this originating integration correction/design continuation. Renewed approval of these changed specification bytes is required before downstream tasks; separate overall review/final approval gates still apply. Committing a draft records preparation, not content approval or migration authority.
- Settled technical constraints in FR-002–005 and FR-016 intentionally remain in the spec: the SDD reference permits already-settled choices. Actual architecture, task-contract/result schemas, module layout, registry/CLI design and file-by-file task sequence belong to the later plan, not this stage.
- Proposed mechanical defaults for approval: user-story `context_group`, implementer same-group eligible reuse, repair original-eligible-implementer preference, reviewer independent-first then own-session eligible reuse, explicit fresh-only override, latest-settled/stable-identity tie-break and fresh/block on unknown telemetry. The 150000 preference comes from the owner, not a measured optimum. `max_repair_attempts: 2` is proposed, not already confirmed.
- Scope includes the new runner/Pi/Git/state/config/task-contract seams and affected existing contracts/tests: `coordinate-implementation` and its batch-routing reference/three test scripts; both `task-generation` adapters/three scripts; planner/references; planning-brainstorming, tiny-spec and architectural helper; review requester/reviewer/receiver; empirical debugging; handoff/finish/adoption; task-commit/project-coordination/memory consumers; suite lint/planner/checkpoint/install checks; README, REQUIREMENTS, AGENTS, constitution and documentation routing where operative text conflicts. Inventory identifies adaptation candidates, not permission to rewrite every file or wholesale planning policy. Preserve existing contract owners and update tests with their operative guards, not by deleting safety expectations.
- Existing constitution 3.0.0 remains authoritative. The settled validated executable-runtime direction is not reopened by its generic preference for bounded extensions. Later planning must identify and justify necessary operative adaptations (LLM routing, wrapper restrictions, coordinator recovery/commit responsibilities and no narrative memory) while preserving explicit authority, portability, checkpoints and independent review; any needed amendment follows owner governance, not silent change.
- Dependency guidance is reused from the canonical [stack-validation report](../../stack-validation-report.md) and [reproduction/semantics owner](../../docs/evidence/workflow-stack-validation/README.md), not a new framework survey. The report's historical “parent acceptance pending” label is superseded only by the parent-accepted entry decision recorded in [decisions.md](decisions.md). B/C remain NOT RUN. Production integration proof remains required; no production outcomes have occurred here.
- Out of scope: actual migration now; planning-workflow rewrite; fourth-framework selection or repeated stack-selection PoC; model benchmarking/automatic routing learning; automatic escalation; parallel writers; unsolicited installations/global configuration/auth changes; deployment/push/history rewrite; deleting STATE/history/gotchas; a required always-on daemon or unrelated generalized platform.

## Integration revision provenance

During the same bounded Standard plan pass, the parent obtained the owner's exact `ask_user` answer **“Allow the thin SDK host (recommended)”**. This permits revising FR-002 and continuing design, not implementation. The historical [specification approval](spec-approval.md) remains unchanged and does not approve these revised bytes. See the appended [source direction](source-request.md#sdk-integration-owner-direction) and [decision D7](decisions.md#d7--owner-selected-sdk-integration-revision). **RENEW_SPEC_APPROVAL** before tasks release. The owner subsequently required survivor alarms and accepted the focused local containment probe; FR-017 records that bounded lifecycle clarification. New owner interaction/autonomy directions are recorded in [source addendum](source-request.md#owner-interaction-and-maximum-autonomy-additions-after-d6acc13) and FR-035–039/US6/SC-008–009; they also require renewed approval. Other approved defaults and requirements are retained.

## Source-to-requirement traceability

Each row maps a specific original-request heading or addendum to normative requirements and observable acceptance. The original Phase 1 procedure is a completed entry condition, not migration work to repeat.

| Source request span | Requirements | Acceptance / outcome |
| --- | --- | --- |
| Working repository/discovery; Phase 2 installed planner and approvals | FR-007–010, 031–034; assumptions | US1/US5, SC-001/007; draft approval boundary |
| Why migration is needed; no conversational orchestration | FR-001, 009, 018–019, 031 | US1, SC-001/005 |
| Declarative workflow, explicit roles, code + agent nodes (all bullets) | FR-002–006, 022, 024, 029 | US1/US2/US4, SC-001/002/006 |
| Dynamic/greedy session reuse (all bullets) | FR-008–017, 026 | US2/US3, SC-003/004 |
| Durable status, events, metrics and observability (all bullets) | FR-018–021, 024–025 | US3/US4, SC-004/005 |
| Verification, Git, failures, review and permissions (all bullets) | FR-006–010, 022–032 | US1/US3/US4/US5, SC-001/004/006/007 |
| Framework decision A→B→C; shared prerequisites; delegation and PoC protocol; required outputs 1–3 | FR-002, 034; decisions/evidence links | Completed parent-accepted A PASS; B/C NOT RUN; no rerun scheduled |
| Phase 2 coverage: file adaptation, YAML/registries/results/config evolution | FR-003–005, 008, 024, 031, 033 | US2/US5, SC-002/007 |
| Phase 2 coverage: runner, telemetry, greedy cutoff, one writer | FR-001–002, 006, 009–021 | US1/US2/US3, SC-001/003/004/005 |
| Phase 2 coverage: Git replay, authoritative projections, CLI | FR-018–026 | US3/US4, SC-004/005 |
| Phase 2 coverage: REQUIRED, repairs/final review, approvals | FR-007, 022–030 | US1/US4, SC-001/006 |
| Phase 2 coverage: legacy compatibility, production tests, rollout/rollback, no optimizers | FR-005, 021, 031–034 | US5, SC-007 |
| Required output 4: decisions; output 5: installed planning artifacts | FR-002, 033; decisions and current draft stage | Decision record delivered; architecture/tasks deliberately gated |
| Current versus prior design supersession | FR-001, 011–021 | US1/US2/US4, SC-001/003/005 |
| 2026-10-18 owner review/fix/session-rotor addendum and confirmation | FR-011–017, 028–030 | US2/US4, SC-003/006; two repairs still a proposal |
| Post-d6acc13 owner interaction/autonomy excerpts and accepted integrated fixture | FR-035–039; FR-019 required question vs optional notification distinction | US6, SC-008/009; renewed specification approval before tasks |
