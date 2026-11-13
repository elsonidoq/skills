# Feature Specification: Issue-linked delivery and manual skill assessment

Apply [Parsimony and Actionable Checks](../../skills/planner/references/parsimony.md).

**Feature Branch**: `plan-issue-44`

**Created**: 2026-11-13

**Status**: Draft — independent specification review and current-specification owner approval pending. No plan, tasks or implementation is authorized by this artifact.

**Input**: Full original request: [skills issue #44](https://github.com/elsonidoq/skills/issues/44), “Adopt issue-linked delivery, LangGraph orchestration, LangSmith monitoring and owner-triggered skill improvements.” Read through `gh issue view 44 --repo elsonidoq/skills --json body,title,state,comments`; OPEN with no comments at intake. This specification associates #44; it does not create another issue.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deliver against an issue and obtain acceptance (Priority: P1)

The owner starts with the planner, with or without an issue. After understanding and brainstorming, the planner associates an existing issue or creates one through the project's declared tracker and authorized access. The issue follows the selected planning path and approved execution. After implementation, checks and independent review, the owner receives the same meaningful delivery executive summary in the issue and current chat, reviews an exact commit, requests corrections if needed, then explicitly accepts the delivery.

**Why this priority**: Delivery must end in an informed owner decision, not an internal completion claim.

**Independent Test**: Demonstrate direct planner intake, association, a delivery summary, a correction and acceptance against one authorized issue. Inspect issue/chat content and linked commits; unrelated history must remain distinguishable. This is a later delivery check, not authority to write #44 now.

**Acceptance Scenarios**:

1. **Given** no issue at intake, **When** the planner understands the request, **Then** it can proceed to tracker association without making an issue an intake prerequisite; TinySpec/Standard choice, source/task reviews and existing approvals remain intact.
2. **Given** an existing issue, **When** planning and execution proceed, **Then** the same reference reaches artifacts and coordinator context without a duplicate issue or local register.
3. **Given** completed implementation, checks and independent review, **When** delivery is presented, **Then** issue and chat explain the result, verification, limits, what to review and the exact presented commit; the issue remains awaiting explicit acceptance.
4. **Given** owner feedback, **When** corrections produce more commits, **Then** feedback, purpose classification and corresponding commits stay linked to the issue, a current summary identifies the new review commit, and no previous acceptance is assumed for that revision.
5. **Given** explicit acceptance of the presented delivery, **When** closure is authorized and available, **Then** the acceptance trace is retained and the issue closes; acceptance does not start RCA, edit skills or create a PR.

### User Story 2 - Execute and recover through the selected framework (Priority: P1)

The coordinator uses Python LangGraph for execution control and the Pi SDK for agent calls. It keeps useful existing adapters, checks, focused Git checkpoints, judgment and parent/CLI integration. The framework replaces custom control rather than enclosing the old engine in one node.

**Why this priority**: A framework migration has value only if it reduces custom orchestration without losing safe delivery.

**Independent Test**: Through the actual CLI/Pi boundary, execute dependent tasks, pause for a genuine gate, reopen and resume, and inspect task checks/checkpoints and independent review. Separately demonstrate a fork/join under explicit concurrency direction. Use focused actual-boundary checks, not a replay of a historical feature.

**Acceptance Scenarios**:

1. **Given** approved dependent work, **When** the coordinator executes it, **Then** successors run only after prerequisite completion and focused checkpoints; framework transitions/persistence control execution and project acceptance still controls task success.
2. **Given** no concurrency direction, **When** independent work is available, **Then** workers remain sequential. **Given** explicit owner direction and distinct owned paths, **When** parallel steps execute, **Then** independent work can overlap and synchronize before dependent work; overlapping or uncertain ownership requires coordination.
3. **Given** a manual/material gate, **When** execution interrupts and later resumes with an actual answer, **Then** the answer reaches the affected operation without replaying completed provider, Git or external effects.
4. **Given** interruption around a successful Git commit or a provider call of uncertain outcome, **When** recovery runs, **Then** actual effects are reconciled before redispatch; uncertainty stops only the unsafe continuation, preserving partial work and history.
5. **Given** a routine scoped technical failure, **When** the coordinator diagnoses it, **Then** it can correct and verify within authority without repeated approval; material scope, paid, security, data and external-action decisions still escalate, and expensive failures are inspected before a targeted retry.

### User Story 3 - See safe invocation visibility before monitor retirement (Priority: P1)

The owner sees graph/task/agent relationships and invocation metadata in LangSmith instead of the custom monitor. Live use requires the later account, privacy, pricing and network gate.

**Why this priority**: Removing the old monitor before observing its replacement would remove visibility.

**Independent Test**: First inspect the actual adapter's outbound metadata and failure behavior locally. After explicit live authority, observe a real permitted invocation and its hierarchy in the selected LangSmith project. Only that visibility can release redundant monitor removal.

**Acceptance Scenarios**:

1. **Given** invocation-local observations, **When** tracing is enabled with authority, **Then** the owner can relate graph, task, role and invocation/session IDs, model, outcome and elapsed time, with usage/cost only when known for that invocation.
2. **Given** reused-session cumulative statistics or missing usage, **When** traces are produced, **Then** totals are not presented as invocation usage and absent values remain unknown, not zero.
3. **Given** private sentinel content in prompts, responses, tool payloads, paths and errors, **When** any outbound trace is assembled, **Then** none appears in inputs, outputs, exceptions, events or metadata. Only approved metadata leaves the boundary.
4. **Given** missing access, disabled upload or telemetry failure, **When** otherwise safe execution proceeds, **Then** it continues with a reported visibility gap; monitor removal remains unreleased until replacement visibility has actually been verified.

### User Story 4 - Assess issues manually for supported skill improvements (Priority: P2)

The owner invokes one reusable assessment entry point. It discovers unassessed issues in open and closed states, reads their evidence, groups supported causes, and proposes minimal changes to the responsible skills. It can conclude no change or uncertain attribution.

**Why this priority**: Learning should be evidence-based and owner-triggered, separate from delivery acceptance.

**Independent Test**: Use a bounded representative issue set with pagination, open/closed states, partial evidence, a changed requirement, a genuine omission and a previously assessed issue. Inspect discovery, classification, grouped proposal, source links and status transitions. This need not reconstruct any full historical feature execution.

**Acceptance Scenarios**:

1. **Given** a manual request and authorized tracker reads, **When** discovery runs, **Then** all matching issue pages across open/closed states are considered, PRs excluded, and acceptance status or its absence is recorded as evidence, not an eligibility filter.
2. **Given** original intent, approved artifacts, feedback and correction commits, **When** assessment runs, **Then** changed/new requirements, planning/task/implementation/review omissions and workflow-added complexity are distinguished by purpose; missing evidence and uncertain attribution are explicit.
3. **Given** unrelated or concurrent commits, **When** attribution is made, **Then** only supported issue-linked effects are classified; neither author identity, commit time nor a blind Git range establishes responsibility or a skill failure.
4. **Given** recurring supported causes across issues, **When** a proposal is presented, **Then** it groups causes and proposes the smallest justified changes to existing skill owners, with source links and existing approval routing; not every correction yields a rule, and project-specific experience does not become global policy by default.
5. **Given** analysis only, **When** status is recorded, **Then** it is proposed or no-change, not addressed. **Given** approved changes are delivered, **Then** addressed can be recorded with delivery evidence. No automatic scanner or self-editing loop runs.

### User Story 5 - Retire ineffective behavioral machinery without losing real checks (Priority: P2)

The maintainer removes the identified behavioral comparison/runner collection and mandatory behavioral-run requirements, while retaining meaningful source-contract, runtime, integration, application and security checks.

**Why this priority**: Verification must support the job, not require an expensive reconstruction program.

**Independent Test**: Inspect the bounded removal and its active callers against the classification below. Run relevant retained cheap checks for changed seams; show no active mandate or import points at removed machinery. Historical evidence is not rewritten as a pass or erased indiscriminately.

**Acceptance Scenarios**:

1. **Given** the identified behavioral collection, **When** removal is implemented, **Then** the listed obsolete tools/cases and their active invocation requirements are retired at their owners, with no mandatory synthetic replacement or replay prerequisite.
2. **Given** meaningful static/runtime/security checks beside that collection, **When** cleanup occurs, **Then** those checks remain usable and their limits remain honest; historical planner records are preserved rather than deleted merely for mentioning tests.

### Edge Cases

- Tracker capability or write authority is unavailable: report the affected association, summary, label or closure operation and corrective action; never invent success or create a local register. Other authorized safe work need not stop.
- Acceptance refers to an older commit, feedback adds scope, or current HEAD includes unrelated commits: identify the presented delivery and changed scope explicitly; renew affected existing approvals rather than treating acceptance as approval of unseen work.
- Interrupt resumption reruns node code: effect reconciliation must precede any repeated mutation or provider dispatch; a framework checkpoint is not exactly-once external-effect proof.
- One parallel branch fails while another finishes: retain completed results and actual failure, synchronize dependents correctly and reconcile before continuation. Parallel capability does not widen path authority.
- An issue has no approved artifact, acceptance record or accessible correction evidence: include it in discovery when otherwise unassessed, report gaps and permit uncertain/no-change conclusions.
- A proposal is approved but not implemented: it remains proposed; read or label failures cannot mark it addressed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 — Intake and association**: Permit direct planner entry without an issue. After understanding/brainstorming, associate an existing issue or create one through the project's declared tracker and authorized access. Carry the reference through source, plan/tasks where applicable, execution and delivery. Missing capability/authority is actionable and never creates a local fallback. For this work, reuse #44 with no issue writes during spec production.
- **FR-002 — Planning compatibility**: Preserve explicit TinySpec/Standard selection, separate source/task review and approval contracts, current-content renewal and independent review. Planning remains skill-owned, not a graph for consistency. A new issue association does not create another approval chain.
- **FR-003 — Executive delivery**: After implementation, specified checks and independent review, publish a meaningful executive summary to both the GitHub issue and current owner chat, including what changed, verification, limitations, review focus and exact presented commit. Track awaiting acceptance separately from internal workflow completion. A failure to publish to either destination is reported, not silently treated as delivery.
- **FR-004 — Feedback and closure**: Link owner feedback and corresponding correction commits to the delivery issue; distinguish approved implementation/internal-review fixes, owner-review corrections and new requirements by purpose. Keep unrelated/concurrent commits unattributed unless evidence supports attribution. Refresh the review commit/summary after corrections. Close only after explicit owner acceptance of the identified delivery and under actual tracker authority; retain the trace after closure. Do not automatically start RCA, skill edits or a PR.
- **FR-005 — Framework replacement**: Use selected Python LangGraph standard persistence, transitions, dependency execution, parallel fanout/join and interrupt/resume where they replace custom control, with the Pi SDK executing agents. Do not keep the custom engine as a single graph node, maintain two execution controllers, rewrite the language, add a scheduler service or combine Temporal and LangGraph. Application-specific dependency readiness may remain ordinary application logic.
- **FR-006 — Safe compatibility**: Preserve usable CLI/attached-parent interaction, selected executor configuration and effort, current launch authority, ordinary scoped repair, focused specified checks, owned-path commits with hooks/signing, fresh independent reviewer contexts, retained history and recovery judgment. Do not reinterpret a transport return, SQL progress row or graph checkpoint as task acceptance. Preserve historical CLI/history readability without automatic history conversion or replay; active legacy recovery needs an explicit compatible route, not silent reinterpretation.
- **FR-007 — Dependency and concurrency semantics**: Keep sequential default behavior. Support parallel execution only under explicit owner concurrency direction, including same-checkout concurrency with distinct task paths. Coordinate overlap/uncertainty; do not invent mandatory separate worktrees or sole-writer eligibility. Parallel steps may synchronize as supersteps; no continuous ready queue is required. Release dependent work only after prerequisite acceptance/checkpoints.
- **FR-008 — Recovery and permissions**: Reconcile actual Git/provider/external effects before retry/resume; do not replay uncertain calls or commits. Preserve known completed results and partial/unrelated work. Inspect expensive failures and target corrections to their cause. Escalate only material decisions or actual authority/capability limits; optional telemetry failure must not veto safe execution. Keep the task startup linter to readable file, parsed task list, ID/work description, unique IDs, existing dependency references and acyclic dependencies—no new admission/proof protocol.
- **FR-009 — Minimal observability**: Replace the custom workflow monitor with LangSmith, starting at the existing Pi invocation boundary and reusing SDK events/statistics. Show graph/task/agent hierarchy, opaque run/task/invocation/session IDs, role/model, outcome, elapsed time and known invocation-local usage/cost. Unknown values stay unknown; reused-session cumulative statistics require valid invocation-local derivation, not direct export as invocation totals. Initial per-token/per-tool tracing and Studio deployment are not required.
- **FR-010 — Privacy and live gate**: Outbound traces are metadata-only: no prompts, responses, tool payloads, private paths or raw errors. Apply this to all submission paths, including exceptions/events/metadata, not merely input/output hiding. Before affected live operations, obtain explicit account/project/region/access choice, pricing acceptance and upload/network authority. No account provisioning, credential changes or uploads are authorized now. Report safe outcome/error categories rather than raw exception content.
- **FR-011 — Monitor cutover**: Verify usable live replacement visibility before removing redundant custom monitor code or operational dependencies. Preserve required historical information and report existing acceptance limits honestly. No automatic history migration, service shutdown or data deletion. Missing live authority blocks that verification/removal, not unrelated local migration work.
- **FR-012 — Manual assessment entry**: Provide one portable reusable manually invoked entry point, separate from delivery acceptance. Discover unassessed issues across all open/closed issue pages using GitHub labels and excluding PRs. Reuse suitable labels if available; exact names are plan detail. Record acceptance status/evidence gaps without requiring recorded acceptance for eligibility.
- **FR-013 — Assessment reasoning**: Read original intent, approved artifacts, owner feedback and relevant commits where available; expose missing/inaccessible evidence. Classify by purpose, distinguish changed requirements from omissions and workflow complexity, and allow uncertainty. Group supported common causes across issues and propose minimal changes to responsible skill owners, without inferring that every correction needs a new rule.
- **FR-014 — Assessment state and authority**: Preserve source links and unassessed/proposed/addressed/no-change distinctions through labels and the issue trail, not a separate learning ledger or trace database. Addressed means delivered, with evidence. Route proposals through existing owner planning/implementation approvals; a PR needs its own applicable authority after improvement work, not feature acceptance. No automatic scanner or self-modifying loop.
- **FR-015 — Bounded retirement**: Retire the behavioral machinery identified below and its mandatory execution requirements at active owners. Preserve meaningful static contracts, runtime unit/integration/application acceptance, security and permission checks. Do not mandate synthetic replacement cases or historical feature replay. Use cheap relevant evidence where meaningful and report limits; future real issues provide recurrence evidence.
- **FR-016 — Policy reconciliation**: Make the explicit bounded operative amendments below through existing approval gates before affected implementation/cutover; do not silently waive them or edit historical approvals. Do not expand this migration into unrelated policy or recovery repairs.

### Bounded retirement classification

Inspection distinguishes behavioral-run machinery from static assertions and tests of actual production mechanisms. This is the deletion boundary to carry into the plan, not authority to delete during specification production:

| Surface | Disposition and basis |
| --- | --- |
| `evaluations/README.md`, `evaluations/review-necessity/packet.md`, `expectations.md`, `recipe.md` | Retire the current retained behavioral comparison convention and its single three-file case. README requires prior/candidate runs when an improvement claim matters; recipe drives reviewer comparisons. Preserve any necessary historical evidence through existing Git/issue links, not a new archive. Replace active verification guidance with proportionate checks/limits, not a new suite. |
| `scripts/planner-rpc-smoke.py` and `RpcDriverTests` in `scripts/test-planner-workflow.py` | Retire the opt-in behavioral scenario recorder and tests solely for this removed driver. Its fake-process tests establish driver mechanics, not planner behavior; removing the driver makes them obsolete. |
| `docs/plans/planner-regression.md` | Remove or explicitly supersede operative “Full behavioral scenarios,” live RPC smoke instructions and mandatory behavioral acceptance/resumption directions. Keep historical observations, NOT RUN limits and relevant static/runtime guidance. Do not delete the whole historical document. |
| `scripts/check-planner-workflow.py`, remaining `scripts/test-planner-workflow.py`, `scripts/planner-trace.py`, `scripts/fixtures/planner/*` | Not a blanket deletion set. Retain meaningful operational-carrier/approval/permission checks, parser/config/resolver/link/installer checks and bounded static/trace sensitivity where they still check maintained contracts. Synthetic traces are not model-obedience evidence and must not become mandatory live acceptance or a new startup gate. Remove only references/imports/driver-only assertions made obsolete by the named retirement; adapt changed contracts without weakening real approvals. |
| `scripts/check-skills-lint.sh` and its focused test callers; `runtime/tests/`; monitor tests until released cutover | Preserve meaningful frontmatter/static checks, task ordering, ownership/checkpoint/recovery tests, and application/privacy/integration checks. Update only obsolete invocation/reference requirements. Runtime tests exercise actual code and are not the ineffective skill behavioral collection. Monitor-only code/tests become redundant only after FR-011. |

Active reference owners include `AGENTS.md` (repository evaluation convention), `docs/index.md` (evaluation routing), `README.md` (validation), and relevant skill maintenance instructions. Reconcile references to retired paths there when authorized later. Historical plans under `docs/plans/`, including review-necessity source/task records and old approvals, are not a bulk cleanup target.

### Governing constraints and amendments to propose

- [ADR-0003](../../docs/decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md): current authorized launches supersede historical planning-only wording within assigned scope; executable tasks stay authorization-neutral and temporary phase status belongs in approval records. Acceptance must show these constraints survive initial, corrective and resumed prompts. This launch authorizes specification artifacts only, not implementation.
- [ADR-0004](../../docs/decisions/ADR-0004-shared-routine-worker-permissions.md): shared ordinary scoped fixes and small isolated local tests/databases need no repeated permission. Preserve hooks/signing, real manual/security/paid/data gates, unrelated work, global-install/credential/deploy/push restrictions and failure inspection before retry. Verify prompt/interaction preservation without a new permission service.
- [Constitution](../../.specify/memory/constitution.md), Project Constraints and Development Workflow: current sequential Python/SQLite implementation-only wording and one-writer clause conflict with selected framework/concurrency capability. Propose a bounded update for LangGraph control and owner-directed parallelism while retaining focused checkpoints, review and history. `AGENTS.md` already supersedes the older sole-writer rule; do not impose it during planning or infer permission to run parallel workers.
- [Coordinator contract](../../skills/coordinate-implementation/SKILL.md) and [operating/schema owners](../../docs/coordinate-implementation.md): sequential custom-control, “no graph saver” and exclusive-runner locking descriptions require explicit reconciliation with the replacement. Preserve useful effects/adapters and concrete safety; do not merely rename the existing engine.
- [Finish-session safety rule](../../skills/finish-session/SKILL.md): “Git owns … completed-work summaries … Do not add them to … issues” conflicts with FR-003. Replace this prohibition only as needed to permit the meaningful delivery executive summary and acceptance trace in the delivery issue and chat; do not authorize routine inventories in memory/docs or unrelated closeout bookkeeping. [Documentation routing](../../docs/index.md) has the same summary-ownership constraint to reconcile.
- The constitution's proportionate-check requirement is compatible with this request. Retire mandatory behavioral-run interpretations and the evaluation routing rule at their active owners, not security, permission, independent review or meaningful application checks. Amendments need existing explicit approval; this draft does not waive policy.

### Key Entities *(include if feature involves data)*

- **Delivery issue**: Declared tracker reference, original intent, planning links, feedback, presented commit, acceptance trace and closure status; durable evidence owner, not a second runtime ledger.
- **Delivery revision**: Exact commit presented, attributable implementation/internal-review/owner-review corrections, purpose and verification/limits; unrelated commits remain separate context.
- **Execution**: Retained run/task/invocation relationships, dependency completion, gates and actual checkpoints; framework persistence supports recovery but does not prove external effects.
- **Invocation observation**: Approved metadata, model/role/outcome/time and qualified usage/cost; no raw payloads or private paths.
- **Assessment**: Source issues, known intent/evidence/gaps, cause classification, grouped proposal and label status; addressed requires delivered improvement evidence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (FR-001–004)**: One authorized delivery can start without an issue, obtain or reuse an association, reach matching issue/chat summaries for an exact commit, link a correction and remain open until explicit acceptance; the accepted trace survives closure. No automatic RCA, skill edit or PR occurs.
- **SC-002 (FR-005–008)**: The actual execution entry completes dependent work with preserved checks/checkpoints and independent review, survives an interrupt/reopen without replaying settled effects, and safely stops an uncertain effect. Inspection shows one execution controller rather than a wrapper around a second engine; existing CLI/parent and executor selection remain usable.
- **SC-003 (FR-007)**: A permitted fork/join demonstrates overlap and correct synchronization with explicit path ownership; the same entry remains sequential without owner concurrency direction.
- **SC-004 (FR-009–011)**: After live authority, the owner can inspect a real graph/task/invocation relationship with approved metadata, qualified usage/cost and no private sentinels. Optional telemetry failure does not prevent safe completion. Redundant monitor removal cannot precede this observation; history and unresolved historical acceptance limits remain intact.
- **SC-005 (FR-012–014)**: A manual assessment includes eligible open and closed issues regardless of acceptance-record presence, exposes incomplete evidence/uncertain attribution, separates changed requirements from omissions/complexity and produces linked grouped minimal proposals. Proposed and no-change cases are distinguishable; addressed is shown only after delivery. Nothing runs automatically on feature acceptance.
- **SC-006 (FR-015–016)**: The named behavioral collection/recorder and active mandatory run directions are retired without deleting historical evidence or meaningful runtime/static/security checks. Changed active references resolve and retained relevant cheap checks pass or report exact limits. No synthetic suite, replay program or added startup protocol replaces them.
- **SC-007 (FR-006,008,016)**: Review of affected contracts and actual boundary checks demonstrates current launch authority, ordinary routine fixes, manual/material gates, safe owned-path commits, reviewer independence and history preservation. Required policy amendments are explicitly approved before affected behavior relies on them.

## Assumptions

### Actual owner decisions and provenance

These are current-session answers supplied by the planner, not inferred issue acceptance:

- **Q: Which orchestration framework? → A: “LangGraph — recommended.”** The parent first compared LangGraph, DBOS and Prefect using official sources. Python LangGraph is selected for planning; this does not authorize installation or implementation. Synchronizing parallel steps is acceptable; no continuous ready queue was requested.
- **Q: What trace privacy/live boundary? → A: “Metadata-only; gate live verification.”** Opaque run/task/invocation/session IDs, role/model, outcome, elapsed time and known invocation-local usage/cost are allowed. Prompts, responses, tool payloads, private paths and raw errors are excluded. Account/project/region/access, pricing acceptance and upload/network authority are not established. Live replacement visibility remains required before monitor removal.
- **Q: Which planning depth? → A: “Standard — recommended.”** This authorizes bounded planning-artifact writing, validation and commits. Independent spec review and explicit current-spec approval precede plan creation; later final approval/implementation gates remain.

### Necessary choices and bounded supporting facts

These facts constrain later design; they do not prescribe a new subsystem or establish implementation success.

- Baseline source inspection: `4e76e2b5624c84ae4492ea65bbdad99f191e0f2b`. `runtime/pyproject.toml` and `requirements.lock` declare PyYAML, not LangGraph or LangSmith. New dependency versions/ranges and compatible saver package selection remain plan-stage technical work; no install was performed and no agent capability version requirement is introduced.
- `Engine.invoke`, recovery and review helpers in `runtime/coherence_workflow/engine.py` currently control task sequencing, corrections and reviews. `store.py` owns private retained input/history and optional monitor tables; `git_effects.py` owns focused commits/reconciliation. Preserve useful interfaces and actual effect reconciliation, replace custom orchestration, and keep old rows readable. Historical graph proofs are not proof this migration works.
- `runtime/pi-host/host.mjs` subscribes to tool/compaction boundary events and `observation()` reads SDK session statistics. `pi_adapter.py` receives before/after observations; `metrics.py:interval_record` rejects invalid/nonexclusive/discontinuous deltas. This is a reusable seam, not a completed LangSmith adapter or permission to export the raw host request/result/session record.
- Reused official-source findings supplied by the parent: [checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers) describes saver persistence, stable thread identity, synchronous durability and pending writes; the SQLite saver is a separate package. [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) resumes with `Command` and reruns the interrupted node from its start. Therefore later actual-seam recovery checks must observe effect reconciliation, not assume exactly-once behavior.
- [Send/Command](https://docs.langchain.com/oss/python/langgraph/graph-api-send-command) provides fanout/reducers; arbitrary DAG readiness remains application logic. [Control flow](https://docs.langchain.com/oss/python/langgraph/graph-api-control-flow) synchronizes supersteps. Use those established mechanisms without inventing continuous scheduling semantics.
- [Custom instrumentation](https://docs.langchain.com/langsmith/annotate-code) supports invocation spans and parent hierarchy; explicit `RunTree` submission is not disabled solely by an environment tracing switch. [Usage metadata](https://docs.langchain.com/langsmith/log-llm-trace) accepts numeric usage; omit unknown fields. [Masking](https://docs.langchain.com/langsmith/mask-inputs-outputs) does not make exception/event/metadata content safe merely by hiding inputs/outputs. Thus local inspection must cover every outbound adapter path before the separately gated real visibility check. Findings are reused for specification constraints as of 2026-11-13; refresh compatibility details against chosen dependency versions during planning.
- Read-only label discovery found only standard GitHub labels (`accessibility`, `bug`, `documentation`, `duplicate`, `enhancement`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix`). None is a suitable assessment-state label. Plan exact minimal labels; any creation/application needs affected tracker write authority, not a new label subsystem.

### Revisitable assumptions, risks and exclusions

- Exact assessment label names and invocation naming are routine plan details, not unresolved product requirements. Use existing skill-entry conventions. Absence of historical acceptance evidence remains a reported gap, never an assessment gate.
- Consequential migration risks are the Git-success/history-write window, interrupted-node redispatch, Pi-to-trace privacy/usage mapping, synchronized parallel ownership and live replacement visibility. Plan proportionate checks of those actual seams before downstream reliance, preferably permanent production-helper/integration checks within their delivery outcomes. No forced prototype/consumer/cleanup chain, live proof during spec production or mandatory full historical replay is required. Failed or unrun required evidence does not release reliance.
- Actual LangSmith account, region/project/access, pricing and network authority remain later explicit gates for live use. They do not prevent local planning; they do prevent claiming replacement visibility or removing the monitor. Offline checks alone cannot satisfy SC-004.
- Related [#2](https://github.com/elsonidoq/skills/issues/2), [#10](https://github.com/elsonidoq/skills/issues/10) and [#13](https://github.com/elsonidoq/skills/issues/13) retain monitor usability/observation limits; replacement does not retroactively satisfy or close them. [#14](https://github.com/elsonidoq/skills/issues/14) identifies commit-before-history replay risk; [#16](https://github.com/elsonidoq/skills/issues/16) identifies lost-usage/false-zero risk. Use their concrete boundaries for migration checks without automatically resolving their tracker states.
- [#41](https://github.com/elsonidoq/skills/issues/41) and [#42](https://github.com/elsonidoq/skills/issues/42) preserve uncertainty about test expectations and review necessity, not proof every historical correction was a skill failure. Do not prescribe their historical experiments as prerequisites. [#28](https://github.com/elsonidoq/skills/issues/28) intended-edit handoff and [#43](https://github.com/elsonidoq/skills/issues/43) checkpoint-only transfer remain separately owned; preserve helpers without broad repair or migration prerequisites.
- Excluded: suite rewrite, planning-engine rewrite, extra permission/proof/retention/learning services, automatic STATE or ledgers, raw uploads, hosted setup, paid use without approval, service shutdown, deletion of retained data, history conversion, pushes, PR creation and changes to other issues. Retirement refers to later approved source-code/convention changes, not operational service/data deletion authority. No resource/spending caps or new admission chains are introduced.
