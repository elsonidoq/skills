# Feature Specification: Execution Tracing and Skill Assessment

Apply [Parsimony and Actionable Checks](../../skills/planner/references/parsimony.md).

**Feature Branch**: Not created; feature identity is `007-execution-tracing` (directory and branch are independent).

**Created**: 2026-11-17

**Status**: Current source and shown [interactive design review](design-review.html) approved by the owner's actual “ok I approve the plan. Start implementing” instruction; see [current approval and scope](checklists/requirements.md#current-actual-owner-approval--implementation-launch). Local implementation is authorized after bounded alignment and parent inspection. Historical pending/preparation-only statements below retain their original provenance, not current veto authority. Required live/manual proof and ungranted external effects remain separate.

**Current delivery scope**: The owner's latest direction is “make sure you finish correctly this implementation, demonstration is out of scope,” followed by explicit authorization to continue autonomously. This supersedes the earlier requirement to stage additional live/manual demonstrations for delivery acceptance. Retain the functional requirements, focused implementation tests, credential/permission protections and independent review. Planning examples, browser demonstrations, test issue lifecycles and issue/PR assessment exercises are not additional completion gates for this delivery; unperformed exercises are not reported as passed. Independent-test examples and success scenarios below describe intended behavior, not a mandate to stage those exercises now. Actual assessment-relevant facts remain required; full generic SDK tool arguments/results and transcript dumps remain excluded. See [current approval provenance](checklists/requirements.md#current-implementation-completion-scope--demonstrations-excluded).

**Input**: Address [issue #45](https://github.com/elsonidoq/skills/issues/45), “Improvements in the planning -> implementing -> improving cycle,” with the owner's selected Standard Specify → Plan → Tasks → Implement path and subsequent durable-content clarification.

**Delivery issue**: https://github.com/elsonidoq/skills/issues/45 (qualified OPEN in `github.com/elsonidoq/skills`; complete body and empty comments read on 2026-11-17).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retain useful execution facts after worktree removal (Priority: P1)

As the owner, I need actual questions, answers, execution outcomes and supporting evidence in the delivery issue or linked pull request (PR), so that I can understand a finished or failed execution after I delete its worktree.

**Why this priority**: Private local references cannot support the requested later assessment.

**Independent Test**: Exercise an execution with user and worker questions, a rejected completion, a failed attempt, an inspected retry or escalation, and a successful completion. Read the published record without the execution checkout and compare it with the observed facts.

**Acceptance Scenarios**:

1. **Given** an execution asks the owner a question and a worker asks the coordinator another question, **When** answers or resolutions arrive through existing tools, **Then** each actual question and corresponding answer/resolution is captured automatically, attributed where identities are available, and retained in the issue or linked PR at finish.
2. **Given** a worker submits completion evidence but a check or review rejects the completion, **When** the execution later succeeds, **Then** the trace preserves the submitted meaningful evidence, rejection reason, failed validation, subsequent attempts and final validation, without replacing failure with success.
3. **Given** execution finishes and publication succeeds, **When** a reader follows the delivery issue and any linked PR without the original worktree, **Then** the reader can find factual event details, basic counts, available code/commit/PR references and trace completeness status; counts and local file paths alone do not pass.
4. **Given** execution fails after facts were captured, **When** a finish/error boundary can still publish, **Then** a partial trace identifies the known events, failure and unavailable portions, rather than claiming complete delivery.
5. **Given** publication is unauthorized, fails or cannot be confirmed, **When** the result is reported, **Then** implementation outcome and trace-delivery outcome are reported separately, with the affected operation and corrective action; no complete trace-delivery claim or disposable-local-only success is made.
6. **Given** a delivery produces a PR, even when its trace is hosted in the issue, **When** delivery is presented, **Then** the PR links to its qualified delivery issue and the issue makes the PR discoverable; readers can navigate from either entry to the associated evidence.

---

### User Story 2 - Resolve consequential planning gaps before workers start (Priority: P1)

As the owner, I need a mandatory high-level architecture review during planning, foreseeable ambiguity resolution and task-level acceptance evidence, without being asked routine technical questions.

**Why this priority**: Better planning prevents avoidable interruption and incomplete handoffs instead of only documenting them afterward.

**Independent Test**: Inspect a bounded planning example with a significant architecture trade-off and a routine technical choice, then inspect the resulting worker task contracts before execution.

**Acceptance Scenarios**:

1. **Given** planned work on either supported planning path, **When** planning is prepared for implementation, **Then** a high-level architecture review has addressed the proposed approach, relevant boundaries, dependencies and material risks through the existing planning flow.
2. **Given** the review exposes a significant decision or foreseeable material ambiguity, **When** it affects planned work, **Then** the owner agrees to the consequential choice before affected execution; routine in-scope mechanics are resolved autonomously. Any explicit deferral states its consequences and permitted bounds and does not release reliance on unresolved work.
3. **Given** tasks are ready for implementation, **When** their contracts are inspected, **Then** each task defines observable acceptance and the completion evidence needed to verify it, including actual checks and any applicable manual or permission gates.
4. **Given** a planner session starts without an issue, **When** the planner understands the request, brainstorms with the owner if needed and finds no exact overlap through the declared tracker, **Then** it creates the requested issue under actual target- and operation-scoped authority, independently reads it back and carries its qualified URL before continuing planned artifact production. With usable capability and authority, merely suggesting creation does not pass.
5. **Given** no issue was supplied but an exact overlap exists, **When** tracker discovery completes, **Then** the planner reuses the qualified match without creating a duplicate or automatically reopening a closed issue. If target, capability or necessary authority is missing or conflicting, it reports the concrete issue-association blocker and corrective action rather than inventing an issue or local fallback; it does not claim the no-issue flow is complete.
6. **Given** high-level design review is ready, **When** the owner reviews its actual HTML schematic, clicks component boxes and reads the executive bullets below, **Then** the owner can inspect each component brief and give explicit design agreement before detailed plan production or continuation. This is separate from requirements/specification approval and final plan/tasks/implementation approval.
7. **Given** design agreement is absent, denied or cancelled, **When** planning would continue, **Then** the gate remains closed; producing or opening the page is not consent. A significant change to the agreed design requires renewed agreement on the updated page before affected detailed planning continues.

---

### User Story 3 - Assess selected durable evidence after completion (Priority: P2)

As the owner, I can explicitly select an issue or PR for the existing skill-improvement assessment, so that it can examine execution facts and later fixes and propose small, evidence-backed improvements days after the worktree is gone.

**Why this priority**: This closes the improvement cycle without adding agents or analysis to execution.

**Independent Test**: Supply an explicit issue URL and, separately, a PR URL with linked traces and post-completion fixes. Perform assessment using accessible GitHub evidence and supported code/commit references, without the original checkout.

**Acceptance Scenarios**:

1. **Given** an explicit owner-selected issue or PR URL, **When** assessment runs, **Then** it follows the issue/PR association from either entry to the linked evidence and relevant post-completion fixes, inspects supported code/commits/PRs, and cites the evidence used, without requiring worktree identity or access.
2. **Given** evidence of a reusable handoff weakness and a separate requirement omitted by the user, **When** conclusions are presented, **Then** reusable process improvements are distinguished from issue-specific omissions, with supported causes separated from hypotheses and missing evidence.
3. **Given** the assessment finds an improvement, **When** it proposes a targeted planning, skill, tool or worker-instruction change, **Then** it does not autonomously edit skills, launch implementation, open a PR or change tracker state; existing scoped approvals still apply.

### Edge Cases

- A cancelled or denied design approval keeps detailed planning closed; significant changes invalidate affected design agreement, not historical records.
- An unanswered, denied, cancelled or delivery-failed question remains unresolved with its actual outcome; no synthetic answer is recorded.
- Missing issue/task/worker/attempt identity or unavailable code/commit/PR references are reported as unavailable, not inferred or invented. A runtime execution without a qualified delivery target cannot claim GitHub trace delivery and MUST NOT invent a fallback issue. This does not prohibit the owner-directed planner no-issue entry flow in FR-013.
- A resumed execution keeps earlier failures and their relation to later attempts. Uncertain publication is inspected before retry to avoid blindly duplicating published evidence.
- Abrupt termination can prevent a finish action. Partial publication is practical only when retained facts and the authorized publication boundary are available; otherwise report the gap on recovery, not a fabricated partial trace.
- Linked evidence may be missing, inaccessible or incomplete. Assessment states which conclusions are partial and what evidence is absent; inaccessible does not mean no failures occurred.
- Ordinary conversational content is included without a routine per-question review gate. Existing protections still exclude actual credentials from evidence; there is no claim of complete free-text secret detection.
- A post-completion correction is evidence, not proof of a reusable process failure. Unrelated commits must not be attributed merely by author, date or position in a range.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 — Planning review**: Planning MUST include a mandatory high-level architecture review of the approach, relevant boundaries/dependencies and material risks before detailed architecture plan production or continuation, with the HTML output and owner gate in FR-015. It MUST fit the existing TinySpec and Standard flows, not introduce a separate planning system.
- **FR-002 — Decisions and ambiguity**: Planning MUST obtain owner agreement for significant architectural/product/scope decisions and resolve foreseeable material ambiguities before affected execution. Routine scoped technical decisions MUST remain autonomous. Unresolved consequential choices MUST be answered or explicitly deferred with consequences and permitted bounds; affected work cannot rely on an unanswered choice.
- **FR-003 — Task proof**: Plans and derived task contracts MUST identify task acceptance and meaningful submitted completion evidence, required validation and applicable manual/permission gates. A worker's completion claim or tool return alone MUST NOT mean accepted completion. Reuse existing task-evidence requirements rather than create a competing contract.
- **FR-004 — Automatic question capture**: Existing execution tools and worker handoffs MUST automatically capture each in-flight user question with its actual answer and each worker question to the coordinator with its resolution. Unresolved or failed deliveries MUST retain their factual status. No manual coordinator logging or extra execution-time analysis agent is permitted.
- **FR-005 — Automatic outcome capture**: Existing boundaries MUST automatically capture submitted completion evidence, validation results, rejected completion and its reason, failed attempts, retries and escalations to coordinator or owner. Record observed failure/retry/escalation context, not execution-time root-cause analysis. Capture does not grant retry authority.
- **FR-006 — Attribution and references**: Events MUST associate available delivery issue, task, worker and execution-attempt identities and retain order and causal links sufficient to pair questions/resolutions and relate failures to retries or rejection to correction. Include available relevant code, commit and PR references; explicitly distinguish absent evidence from observed zero events.
- **FR-007 — Durable factual delivery**: At execution finish, publish a compact structured trace in the qualified delivery issue or its linked PR under scoped external-write authority. The delivery issue MUST make a PR-hosted trace discoverable. Retain actual question/answer content, worker resolutions, meaningful submitted completion evidence, rejection reasons, validation outcomes, failure/retry/escalation details, basic counts and available references needed for later assessment. Essential evidence MUST be in GitHub, not solely in disposable files or session references. Compact does not mean metadata-only.
- **FR-008 — Partial and failed publication**: Preserve and publish partial factual traces on execution failure where practical. Report known coverage/gaps. Report implementation outcome separately from publication failure, missing authority or uncertain readback. Complete trace delivery MUST NOT be claimed until all assessment-relevant content is durably available and confirmed. Preserve available evidence for an authorized recovery; do not silently substitute local-only evidence, a local issue register, blind retries or invented success.
- **FR-009 — Explicit assessment selection**: Extend the existing owner-triggered assessment skill to accept explicit issue OR PR URL selection and resolve linked evidence without the original worktree. No automatic post-delivery investigation is introduced.
- **FR-010 — Evidence-led assessment**: Assessment MUST analyze trace facts alongside supported post-completion fixes and inspect relevant accessible code, commits and PRs. It MUST identify avoidable interruptions, incomplete work and supported process weaknesses, distinguish reusable workflow improvements from issue-specific omissions, cite supporting evidence, and separate observed facts/supported causes from hypotheses and gaps. Proposals MUST target existing planning, skill, tool or worker-instruction owners; no automatic edits or statistical evaluation.
- **FR-011 — Lean compatible operation**: Reuse existing tools, handoffs, planning reviews and execution persistence. Capture facts during execution; analyze causes afterward. Instrumentation MUST NOT require manual bookkeeping, extra execution-time agent calls, a new database/dashboard/general observability framework, new startup admission gates, or a graph rewrite. Keep existing acceptance, focused task checkpoints and independent review intact.
- **FR-012 — Authority and credential boundaries**: Existing actual-credential protections and scoped external-action gates MUST remain. Ordinary question/answer text MUST NOT be omitted by default, reduced to metadata, or made subject to mandatory sanitization agents or per-conversation approval. Keep the separate opt-in local metadata-only Phoenix exporter boundary unchanged; the requested GitHub factual trace is not that exporter.
- **FR-013 — Planner issue association**: If a planner session starts without an issue, the planner MUST understand the request and brainstorm with the owner if needed, then establish its issue through the existing [track-open-issue](../../skills/track-open-issue/SKILL.md) lifecycle before continuing planned artifact production. Resolve and verify the declared tracker target, usable capability/authentication and, for creation or another required mutation, actual target- and operation-scoped write authority; inspect complete open/closed overlap evidence and reuse an exact match rather than duplicate it or automatically reopen it. If no exact match exists, the planner MUST create the user-requested issue, independently read back its qualified identity/content/state and carry its URL into subsequent artifacts and handoff. With these prerequisites satisfied, proceed without another routine creation-approval question; suggesting creation alone is insufficient. Missing/conflicting target, capability or authority MUST be surfaced with the concrete corrective action, not bypassed. Preserve existing issue-body quality review and uncertain-effect reconciliation rules. This is planner behavior, not runtime permission to fabricate issues or a change to planning-depth/current-content approval gates.
- **FR-014 — Every delivery PR links its issue**: Every delivery PR MUST link to its qualified delivery issue, regardless of whether trace content is in the issue or PR. The issue MUST make its delivery PR discoverable so issue-led assessment can reach it; PR-led assessment MUST be able to follow the issue link and resolve linked evidence. Verify the association under existing scoped write/readback rules; a missing or unconfirmed link MUST be reported as incomplete linkage, not claimed complete.

- **FR-015 — Interactive design review and owner gate**: The high-level design-review phase MUST produce a durable, self-contained HTML schematic before detailed architecture plan production or continuation. Each component box MUST be clickable and show a popup executive brief in bullets covering purpose, inputs/outputs, boundaries and significant design choices. Executive bullets below the schematic MUST explain the overall goal, relevant supported properties, tradeoffs/limits and other necessary context, without claiming unverified capability or performance. The review MUST distinguish workflow approvals from factual data flow and identify proposed/unimplemented behavior. The owner MUST explicitly agree based on this actual output before detailed planning continues; requirements/specification approval and final plan/tasks/implementation approval remain distinct. Cancellation, denial, silence, page creation or interaction MUST NOT count as agreement. Significant design changes MUST renew design agreement. The page MUST be keyboard accessible with readable mobile layout and popup close/Escape/focus behavior; it MUST NOT simulate an authorization control.

### Key Entities *(include if feature involves data)*

- **Execution trace**: Ordered factual events for a delivery, with outcome, coverage/gaps, event counts and durable GitHub location.
- **Trace event**: Question/answer or resolution, completion submission, validation, rejection, failure, retry or escalation; carries actual meaningful content, available attribution and relevant references.
- **Execution attempt**: An attributable worker invocation/continuation associated with a task and outcome; later attempts do not erase earlier ones.
- **Completion evidence**: Worker-submitted proof and observed validation used to accept or reject the task, distinct from a completion claim.
- **Assessment proposal**: An owner-requested evidence-backed finding, classified as reusable process improvement, issue-specific omission or uncertain, with a targeted change suggestion and supporting links.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewed planning example shows a high-level architecture review, explicit owner agreement for its significant choice, autonomous resolution of its routine choice and acceptance/evidence for every worker task (FR-001–003).
- **SC-002**: In a representative observed execution containing both question types, rejected completion, failed attempt, retry/escalation and eventual completion, each occurrence is represented with its actual content/outcome and available attribution; the coordinator writes no manual log and no extra analysis agent is invoked (FR-004–006, FR-011).
- **SC-003**: With the original worktree unavailable, a reader starting at the delivery issue can retrieve the paired questions/answers, submitted evidence, rejection reasons, validation, execution details, counts and available code/commit/PR references from the issue or linked PR (FR-006–007, FR-012).
- **SC-004**: Failure cases show an honest practical partial trace when publication remains possible; unavailable/failed/uncertain publication never appears as successful trace delivery and never changes the actual implementation outcome (FR-008).
- **SC-005**: Explicit issue selection and explicit PR selection each support a later assessment of linked trace evidence and post-completion fixes without the original checkout. Findings distinguish reusable weaknesses, issue-specific omissions and unsupported attribution and do not initiate changes (FR-009–010).
- **SC-006**: Capture and assessment preserve actual credential protection, scoped write authority, task verification and independent review, without per-question publication approval, a new execution-time agent or a changed local-monitoring privacy boundary (FR-011–012).
- **SC-007**: A planner entry without an issue demonstrates needed owner brainstorming followed by confirmed creation when no exact overlap exists, or qualified overlap reuse without duplicate/reopen. Missing prerequisite cases report the blocker without fabricated association. Every delivery PR links its issue, and readers starting at either the issue or PR can reach the associated evidence regardless of trace location (FR-013–014; Story 2 scenarios 4–5, Story 1 scenario 6, Story 3 scenario 1).

- **SC-008**: Before detailed plan production or continuation, the owner can open the HTML review, activate every component box by pointer or keyboard, read its bulleted popup, close it with Close or Escape and return focus to the opener. The below-schematic executive bullets explain goal, supported properties and limits. Actual explicit design agreement is recorded separately from requirements and final approval; cancellation/denial leaves the gate closed, and a significant design change requires renewed agreement (FR-001, FR-015; Story 2 scenarios 6–7).

## Assumptions

### Owner decisions and source precedence

- The original issue supplies planning, factual capture, finish publication and post-execution assessment requirements. The subsequent owner clarification explicitly supersedes the earlier metadata-only proposal: “I want the questions and answers be in the repository ... everything should be in the GitHub issue or in ... the PR.” The owner intends to delete worktrees and assess days later. Therefore GitHub must hold actual assessment-relevant content, not references to private local detail.
- Q: Must later assessment depend on knowing the old worktree? → A: No. Actual Q/A and necessary execution evidence belong in the issue or linked PR. Assessment accepts explicit issue or PR selection. “Everything” means facts needed for that assessment, not every full transcript or tool-output byte.
- Q: Should ordinary Q/A publication require another content-review agent or owner approval? → A: No. Do not revive metadata-only publication or routine text-approval gates. Actual credential protections remain; complete secret detection is not promised.
- At the current-specification approval checkpoint the owner requested a change, not approval: “important: the PR must always be linked to the issue. If a planner session starts with no issue, the planner agent must brainstorm with the user if needed and create the issue”. FR-013–014 make this owner requirement binding, using existing tracker ownership, overlap reuse, scoped authority, readback and review protections rather than an agent-selected new issue system. This feature already has qualified issue #45; no new issue is needed for this correction.
- Latest owner direction adds a distinct design gate: “I require a pixel art schematic and a quick explanation of the overall design before continuing. I want to gate that”, then requests an HTML schematic with clickable boxes, popup executive bullets and an overall executive-bullet explanation below. The actual [design-review.html](design-review.html) is the required output, not the earlier text-only schematic. This is an owner requirement, not optional hardening. A small block-style document is a local presentation choice, not a new renderer/framework requirement.
- The two preceding approval questions were cancelled, not consent. Historical specification approval remains in the checklist for its exact accepted bytes; this changed source requires renewed approval. Prior plan/contracts/tasks are preserved as historical proposed context pending revised propagation, not current approval. Page creation grants neither design agreement nor implementation authority.
- The owner selected Standard and authorized bounded planning preparation/commits only. This specification does not authorize live GitHub writes, implementation or downstream planning. Later stage approvals remain separate.

### Verified constraints and evidence reuse

- [ADR-0003](../../docs/decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md): Carry current approved execution authority instead of historical phase wording; task contracts stay authorization-neutral. Acceptance evidence and real gates remain, and a returned execution is not acceptance (FR-003, FR-011–012).
- [ADR-0004](../../docs/decisions/ADR-0004-shared-routine-worker-permissions.md): Shared routine scoped permissions prevent repeated ordinary approval questions; material product/scope, paid, credential/data and external-action boundaries remain. No blind expensive retries or invented budgets (FR-002, FR-005, FR-012).
- Repository evidence at baseline `9b05443adf3e738747d4330205a7acfd03ab25ca`: [store.py](../../runtime/coherence_workflow/store.py), `execution_history` and `Store.history`, already retain ordered run/task/kind/state/details/time facts. [graph.py](../../runtime/coherence_workflow/graph.py), worker/wait/checks/checkpoint flow, retains invocation summaries/sessions/effects, check outcomes, escalation facts and invocation-bound question resume. These are reuse evidence, NOT proof of complete paired capture or GitHub publication.
- [pi_adapter.py](../../runtime/coherence_workflow/pi_adapter.py), `PiAdapter.prompt` question handling, and [host.mjs](../../runtime/pi-host/host.mjs), question tool, expose relevant existing boundaries. [engine.py](../../runtime/coherence_workflow/engine.py), `_delivery_issue_context`, carries delivery issue context but is NOT evidence of automatic publishing. Current consuming implementation is graph-based; stale target wording is not a rewrite prerequisite.
- [Local monitoring contract](../../docs/coordinate-implementation.md#local-phoenix-configuration) and [tracing.py](../../runtime/coherence_workflow/tracing.py) describe a distinct local metadata-only exporter. Preserve its boundary (FR-012). Existing [task generation](../../skills/task-generation/SKILL.md) owns task proof, and [assessment skill](../../skills/assess-skill-improvements/SKILL.md) already owns explicit analysis/no-auto-edit behavior (FR-003, FR-009–010).
- The [worktree-retention contract](../../AGENTS.md) requires durable necessary facts outside disposable worktrees. GitHub trace content satisfies this requested use case without a new local archive.

### Dependencies, uncertainties and later proof

- Reuse inspected repository source and current operating/assessment contracts for this behavioral specification. No new dependency or version selection is needed now; new internet library research would not establish missing end-to-end capture/publication behavior. No specific installed-agent version requirement is introduced.
- Complete automatic capture, GitHub delivery/readback and checkout-independent assessment remain UNVERIFIED as delivered capabilities. Architectural planning must inspect the exact consuming boundaries and applicable dependency guidance before selecting mechanisms; inspection here establishes reuse opportunities only.
- Later authorized implementation must demonstrate real boundary pairing and factual capture, confirmed durable delivery plus partial/uncertain-publication behavior, and assessment from GitHub without the execution worktree. Ordinary production-focused checks should prove these seams; no speculative standalone prototype is required now. Static instruction checks alone cannot prove agent obedience or live application delivery. Live provider/GitHub proof retains its actual authority gates.
- Planner issue association is required by FR-013, not assumed optional. Runtime loss of the qualified target or authorized GitHub access at finish is a reported publication gap, not permission to create a fallback issue or replacement tracker. No retention period, numeric size cap, retry budget or service setup is assumed.

### Explicit exclusions

No historical backfill; no real-time RCA; no extra execution-time agents or autonomous investigations; no autonomous skill edits or implementation of proposals; no statistical evaluation; no separate telemetry database/dashboard/general framework; no manual coordinator bookkeeping, routine STATE/memory/ledger maintenance, full transcript dump, graph rewrite, service installation or weakening of Phoenix privacy. This specification-correction stage grants no push, PR creation, GitHub mutation or implementation authority. The required future planner issue-creation flow remains subject to its actual target- and operation-scoped external authority; runtime publication failures do not authorize fallback issue creation.
