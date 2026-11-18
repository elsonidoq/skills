# Implementation Plan: Execution Tracing and Skill Assessment

Apply [Parsimony and Actionable Checks](../../skills/planner/references/parsimony.md).

**Feature**: `007-execution-tracing` (no feature branch created) | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)
**Actual branch**: `trial/permanent-paseo`, unchanged.
**Delivery issue**: https://github.com/elsonidoq/skills/issues/45 (`github.com/elsonidoq/skills#45`).
**Input identity**: approved requirements/design snapshot `bfc2121abef9c4e6e239e03eb1a81c5fa53d09bf`; current specification SHA256 `535d04500157b232473dac474011a807c100ce42d72e2abc29d7cbd6ab396697` (only status/provenance differs from the approved snapshot).
**Authority**: [current actual owner approval](checklists/requirements.md#current-actual-owner-approval--implementation-launch): “ok I approve the plan. Start implementing”. It covers the presented current source, shown [HTML design](design-review.html) and local implementation scope after faithful alignment and parent inspection; it is not implementation acceptance or blanket external-write consent. Historical pending/preparation-only labels do not override this grant.

This file follows the installed `.pi/prompts/speckit.plan.md` workflow and resolved plan template. Setup ran once after the separate approval checkpoint. Phase 0 research and Phase 1 design are planning activities, not delivered implementation phases. The later [task handoff](tasks.md) contains thirteen independently verifiable outcomes; this alignment does not rerun setup.

## Summary

Capture actual owner Q/A, worker/coordinator resolutions and execution evidence at existing tools and handoffs. Retain ordered facts in the current workflow store. At finish or practical failure, publish a compact, full-meaning trace to the qualified issue or a known linked PR, with independent readback and honest coverage. Extend the existing owner-triggered assessment to follow either entry without the original checkout. Make the interactive HTML design and actual owner agreement a gate before detailed planning in both paths, require planner issue association, and verify reciprocal issue/PR linkage for every delivery PR.

The smallest sufficient approach extends the current LangGraph controller, SDK host/bridge and existing skills. It adds no execution-time agent, DB, service, observability framework, startup gate, manual log or graph rewrite. [Research](research.md) classifies source-backed constraints, proposed mechanisms and remaining runtime proof.

## Technical Context

**Language/Version**: existing Python >=3.10 workflow, Node JavaScript bridge/host and Markdown skills. Inspected Node 22.23.3; actual SDK resolution 1.4.0, not the installation metadata's 0.87.1. No agent version requirement is introduced.

**Primary Dependencies**: existing LangGraph 1.2.21, SQLite saver 3.1.3, Python sqlite3, installed Pi SDK and ask_user tool, installed `gh` for authorized GitHub operations. No new dependency. Keep local Phoenix/OpenTelemetry separate and unchanged.

**Storage**: existing `.coherence/workflow/workflow.sqlite` history and review rows; existing graph saver for control. GitHub issue/PR comments hold all assessment-relevant content after worktree deletion. No new tables are needed for versioned facts in existing JSON details.

**Testing**: existing Python unittest and Node test suites with disposable Git projects and offline SDK fixtures; production-seam capture/publisher tests, followed by separately authorized genuine application/GitHub acceptance. Static skill checks are not model-obedience proof.

**Target Platform / Project Type**: current local CLI and attached Pi/Paseo session, with optional explicitly authorized GitHub publication. Global skills remain portable; no baked-in #45 or repository target in runtime assets.

**Constraints / Scope**: FR-001–015 and all source exclusions. No arbitrary output size, timeout, retry, retention or spending budget. Keep actual task/session dispatch allowance, manual gates, credentials, selected executor, independent review and focused commits. No live operation is authorized by this plan.

## Constitution Check

Before Phase 0: PASS for the proposed scope. Portable assets use declared project routing; evidence comes from actual consumers; exact source approval is recorded; no implementation or external writes occur; current graph/history and ordinary verification are reused.

After Phase 1: PASS for design within these bounds, not proof of implementation. Proposed new mechanisms each serve an explicit requirement: tool-result capture (FR-004), missing fixer evidence (FR-005), stable event/part identity (FR-006/008), scoped publisher/readback (FR-007/012), reciprocal links (FR-014). No new admission layer or approval protocol. Current source/design/local implementation authority is recorded separately; real external scope, live/page acceptance and independent implementation review remain unmet proof/effect gates. No constitution amendment is proposed.

## Project Structure

### Documentation (this feature)

```text
specs/007-execution-tracing/
├── spec.md                         # unchanged approved requirements
├── checklists/requirements.md      # exact current approval
├── plan.md                         # this derived architecture
├── research.md                     # canonical dependency/design evidence
├── data-model.md                   # factual entities and lifecycle
├── contracts/README.md             # capture, delivery and assessment interfaces
└── quickstart.md                   # future validation guide
```

`tasks.md` and an executable task handoff belong to the later task producer; neither exists from this pass. [Documentation index](../../docs/index.md) discovers the canonical research.

### Source code and existing owners

```text
runtime/coherence_workflow/
  graph.py             # worker/wait/check/checkpoint/review and terminal boundaries
  engine.py            # current authority, fixer/reviewer and evidence handoffs
  store.py             # operation-local history and retained run authority
  pi_adapter.py        # framed SDK callbacks and parent question transport
  verification.py      # actual checks and manual gates
  cli.py               # start/resume/status, terminal reporting
runtime/pi-host/host.mjs
runtime/pi-extensions/coordinate-implementation-bridge.js
runtime/tests/                         # existing Python/Node acceptance seams
scripts/coordinate-implementation     # existing executable entry
skills/{planner,planning-brainstorming,task-generation,
        assess-skill-improvements,track-open-issue,finish-session}/SKILL.md
```

**Structure decision**: keep capture/projection/publication helpers within `runtime/coherence_workflow/` as small focused functions/modules when they simplify testing. Do not build a generic event bus or provider framework. Existing operating and schema owners are [coordinate-implementation.md](../../docs/coordinate-implementation.md) and [coordinate-implementation-schema.md](../../docs/coordinate-implementation-schema.md); they are read-only in this stage and must be updated with eventual implemented interfaces.

## High-level architecture review

### Boundaries and durable data flow

1. **Planning boundary**: planner understands the request, brainstorms if needed and establishes a qualified issue through the existing tracker lifecycle. Both TinySpec and Standard produce a durable project-owned self-contained HTML high-level design before detailed architecture plan production or continuation. Clickable boxes open executive bullet briefs covering purpose, inputs/outputs, boundaries and significant choices; executive bullets below explain goal, relevant supported properties, tradeoffs/limits and necessary context. Review approach, interfaces, dependencies and material risks, distinguish workflow gates from factual data flow and label proposed behavior honestly. Require readable mobile layout and keyboard activation, Close/Escape and focus return. Obtain explicit actual owner agreement on this shown output before details; silence, denial, cancellation, page creation or interaction is not consent. Significant design changes renew agreement. Requirements approval, design agreement and final plan/tasks/implementation approval remain distinct outcomes; do not ask again for the same settled grant covering shown scope. Routine mechanics stay autonomous. Reuse [this feature’s delivered page](design-review.html); reusable instructions discover project-owned output without a renderer/framework or #45 dependency. The current owner grant permits this faithful alignment and local launch after parent inspection.
2. **Capture boundary**: existing host/adapter records worker questions and exact replies. Existing bridge observes parent `ask_user` call/result automatically for the active run, including actual selected/freeform/comment answer and cancellation/error. This matters because its normal metadata broadcast omits actual answers. No shared ask_user modification or global full-event opt-in. Terminal questions use a recording wrapper around the existing input function, not a new input tool.
3. **Persistence boundary**: append new factual question records and capture gaps to existing history; reuse invocation, check, checkpoint and all review-attempt facts. Include fixer submitted summaries at their current return boundary. Keep the original event and later resolution/failure distinct. Observe new recording failures without vetoing task execution or silently claiming complete coverage. Required operational history remains required for its existing safety purpose.
4. **Publication boundary**: runner drains bridge evidence and settles available facts before success/error publication. A deterministic projection reads a stable history snapshot, creates structured content and publishes through a small `gh api` adapter under retained target/operation scope. Verify each part independently. Finish-session consumes the outcome; it does not repeat publication blindly, rereview implementation or treat a trace comment as accepted delivery.
5. **Assessment boundary**: explicit issue or PR selection resolves qualified identity, reciprocal association, all relevant comment pages and supported post-completion code/commit/PR evidence. Analysis is read-only by default and works without local worktree identity. Inaccessible references produce partial conclusions; no automatic skill edits, implementation, labels or closure.

### Identity, ordering and pairing

Reuse run ID, task ID, graph invocation ID, SDK tool-call ID, bridge request ID and reviewer/fixer execution ID. Use history sequence for stored order, not timestamp inference. Parent question IDs include the actual session/tool-call identity internally but publish only necessary logical attribution, never private file paths or tokens. A run-level owner question without known task/worker identity explicitly says unavailable.

A worker question and coordinator resolution share an exact request ID. Parent owner question/result share actual tool-call ID. Link owner escalation to a worker request only when known from the active routing context; a contextual triage link is not proof that the owner approved the worker's exact question. Publish both actual texts and the final coordinator resolution. No text matching, nearest timestamp or shared author substitutes for identity. Retry/correction/review links retain explicit predecessor and cause/diagnosis actually supplied; do not perform RCA during execution.

The bridge buffers observed parent-tool facts until an existing question reply or terminal drain carries them to the runner, retaining batches until persistence acknowledgment. It must still drain unrelated in-flight owner questions when no worker is waiting. Existing private transport gains a read/drain operation, not a new service, public logging tool or competing DB writer. On loss of the bridge or abrupt termination, state the unconfirmed interval/gap. If the terminal process cannot run, publication cannot be promised. Recovery may consume retained facts and reconcile publication; it must not rerun providers to recover a log.

### Meaningful evidence, compactness and credentials

The trace includes actual Q/A and worker resolution, submitted completion report, rejection reasons and review coverage gaps, actual configured-check command/outcome and meaningful output, failed attempt/retry/escalation context, counts, relevant code/commit/PR references and coverage. It distinguishes worker-reported claims, runner-observed checks, focused commits, independent review and owner acceptance. It does not dump prompts, all transcripts, raw transport envelopes, environment or unrelated files.

Preserve assessment-relevant evidence content before temporary files disappear. Resolve explicitly submitted relevant evidence references within existing safe-path/ownership rules; include their meaningful content or report unavailable evidence. No broad filesystem harvest. Deterministic formatting may remove redundant representations, not silently omit a failed event or shorten an answer into metadata. Long content uses verified multi-part GitHub comments as needed. A local filename/hash alone does not satisfy durability.

Never copy auth headers, bridge tokens, credential files or provider configuration into the payload. Exclude known actual credentials in otherwise required content, identify the resulting gap, and preserve ordinary conversational content without routine approval/sanitization. No universal secret-detection claim. Existing Phoenix exporter and safe CLI/history projections retain their metadata-only/private-content boundaries; this is a separate explicitly authorized payload path.

### Automatic publication with actual scoped authority

The existing implementation launch does not authorize GitHub writes. The final approval/handoff must expressly cover the qualified target and operations: factual trace comments and necessary reciprocal issue/known-PR link comments for that run. Proposed optional delivery-authority context is carried in existing launch input and retained run authority, with target/operations and actual approval provenance; it is not a new mandatory task field or proof service. The attached start facade passes the approved context, direct CLI consumes the same context, and resume restores it without a new routine finish question. Field presence, issue context, credentials or successful reads alone never create consent.

At action time, verify declared target, exact resource identity, usable gh/auth and read capability. Missing/conflicting target, authority or access stops only publication/link mutation with a concrete correction. It does not block bare task startup or change implementation status. No runtime fallback issue. Target or scope drift requires renewed actual authority, not silent widening. An explicit recovery publication uses retained run facts and matching current scope without relaunching implementation. Provide one narrow publication-only CLI command invoking the existing publisher helper, callable by a terminal or attached agent through normal shell; no separate attached recovery tool or bridge route is needed. That command has no task mutation/provider path.

Default destination is the qualified issue; an explicitly selected already linked PR is also valid. Always make every delivery PR discoverable from the issue and link the issue from the PR, even with issue-hosted trace. Reuse confirmed existing links; add only scoped missing comments, never overwrite arbitrary bodies. PR creation and push remain outside publisher authority. If a PR appears after runner finish, finish-session establishes/verifies its links and refers to the existing trace; it does not duplicate it. No issue closure or acceptance is inferred.

### Failure, concurrency and restart

A finish/error adapter must preserve the original return or exception. It reports implementation outcome and trace outcome separately. Partial failure traces carry the known terminal failure and unavailable portions; incomplete capture can be published successfully as a **partial** trace, never as full coverage. Failed publication after successful implementation does not rewrite the implementation as failed. Failed implementation plus confirmed partial delivery is not implementation success.

Before mutation, retain a stable publication snapshot, part marker and intended content identity in existing history. Independently read back every part and discovery link. Lost response/readback means uncertain effect: inspect complete relevant destination pages and exact matching comments before retry; conflicting matches stop that operation. No blind append loop, no auto retry of rate/auth errors. Only an explicit no-effect length rejection justifies lossless partitioning; no guessed GitHub cap.

Sequential remains default. Owner-selected path-disjoint waves retain per-invocation IDs, current thread-local connections and short transactions. Join/quiesce writers for shared checks/Git and terminal publication. No DB transaction spans network or owner wait. One existing controller owns local publication; independently concurrent remote comments are preserved. Stable markers and readback detect duplicates/ambiguity but do not claim distributed exactly-once semantics.

Historical rows and prior approvals remain intact. Old runs without capture coverage say unavailable and do not gain invented zero-event counts. No backfill, migration, graph conversion or historic exporter replay. Rollback disables the new capture/publication wiring while leaving existing history and remote comments readable; no destructive database or comment cleanup. Resume of operational work still obeys existing graph/effect safety.

### Existing contracts and documentation impacts

- Planner/planning-brainstorming, TinySpec/Standard helper and plan prompt/template, approval/review carriers and coupled checks: require the HTML design and actual agreement before detailed planning in both paths; preserve distinct approval outcomes without routine duplicate consent. Issue association still precedes planned artifact production; no new planning depth or renderer framework. Keep exact overlap reuse, closed-state preservation, target/auth/scoped creation/readback and issue-body quality review.
- Task-generation and relevant TinySpec/Standard adapters: reuse task acceptance/evidence fields, dependency/manual gates and current-source approval. Do not make task JSON require publication metadata or a universal evidence schema. Downstream producers inspect coupled templates/checks before updating them.
- Finish-session/track-open-issue: separate factual finish/error trace from reviewed delivery/owner acceptance/closure; universal reciprocal PR links; do not add candidate RCA or body review to routine trace comments.
- Assess-skill-improvements: explicit PR selection as well as issue; navigate trace and supported later fixes, state evidence gaps and separate reusable weaknesses from issue-specific omissions. No post-run analysis agent.
- Runtime docs/schema and README/REQUIREMENTS: document implemented capture payloads, scope carrier, publication/recovery command, outcomes, no-checkout assessment and remaining live limits. Update only affected owners in implementation; no global repository-specific policy.
- Changed global skills/bridge require a fresh-session Paseo handoff with checkout/revision/approval/capability verification. No automatic reload/restart or owner slash-command instruction.

## Outcome sequencing and prerequisites

These are architecture dependencies, not a task list or implementation assignment.

Establish observable event identity/capture on actual SDK and question routes before the trace projector depends on it. Retain missing fixer reports and explicit links at existing boundaries alongside their focused checks. Develop the deterministic history projection against already persisted production facts before adding remote effects. Prove the publisher's content preservation/readback/uncertain-send behavior before integrating automatic success/error finish. Carry scoped authority and terminal drain through direct CLI and attached bridge together; publication-only recovery must not dispatch workers.

Planning issue/review behavior and read-only assessment can be developed against the agreed contracts without changing the execution graph, but their acceptance needs actual representative planning and durable evidence. Integrate reciprocal delivery linkage with finish after publication outcomes exist. Place genuine live application and GitHub readback proof at the first composed consumer boundary, then checkout-independent assessment and fresh independent final review. Failed or missing proof blocks affected acceptance, not safe unrelated development.

Task producer must read the exact selected `/home/paseo/projects/skills/.pi/workflow-executor.json` again: observed Terra/medium worker, Sol/medium fallback and reviewer. This plan selects neither executor nor concurrency. Split independently testable interfaces for that executor; keep ordinary tests/docs with their behavior. Explicitly brief consumers about current SDK hook applicability, bridge drain, capture gaps, credential rules, publication authority, remote availability and original manual/live gates. No task IDs/JSON or milestone-sized bundled tasks are supplied here.

## Observable acceptance mappings

| Source | Production seam and required observable | Evidence / release boundary |
| --- | --- | --- |
| FR-001–003, FR-015; SC-001, SC-008 | Both paths show the actual interactive HTML design and owner agreement before detailed planning, significant-choice agreement, autonomous routine choice and each task's proof/gates. Page interaction is not consent; significant changes renew agreement. | Actual bounded TinySpec/Standard examples, source/design/final approval-scope evidence and real browser pointer/keyboard/mobile/Close/Escape/focus checks of the project-owned page. Existing static/DOM checks supplement, not replace, actual page/model behavior. |
| FR-004, SC-002 | SDK owner tool result, terminal input and worker/coordinator handoff retain actual paired content, cancellation/failure and unavailable identities. | Focused hook/transport/graph reopen tests before projector reliance; representative live run before feature acceptance. |
| FR-005–006, SC-002 | Submission, rejection, checks, failed call, inspected retry/escalation, fixer and review attempts retain content and explicit causal identity through correction. | Fail-then-pass production helper tests; actual observed attempt/checkpoint/review evidence. Missing output is a gap, not pass. |
| FR-007, SC-003 | All meaningful trace parts and references are retrievable in GitHub without old worktree. Counts agree with retained facts; unavailable differs from zero. | Formatter/publisher body round trip, then authorized live publication and independent exact readback from a clean context. |
| FR-008, SC-004 | Success and error exits preserve implementation status while reporting confirmed/partial/failed/uncertain delivery; recovery does not duplicate or relaunch. | Known no-effect and uncertain-send tests at gh boundary, terminal integration and practical failure live evidence. Abrupt death limit is explicit. |
| FR-009–010, SC-005 | Owner-selected issue and PR independently reach trace/later fixes; findings cite facts and distinguish reusable, issue-specific and uncertain conclusions. | Two read-only assessment entries without original checkout; no edits or tracker state changes. |
| FR-011–012, SC-006 | No extra agent, manual log, startup gate, DB or graph rewrite; scoped external writes only; credentials excluded; Phoenix unchanged. | Capture/publication tests with credential sentinels, unchanged task intake, authority and Phoenix regressions; observed live workflow. |
| FR-013, SC-007 | No-issue planner actually creates under scoped authority or reuses exact overlap; missing prerequisite is actionable; closed issue not reopened. | Planner/tracker fixture cases plus authorized real no-issue entry demonstration, preserving body quality review. #45 is not recreated. |
| FR-014, SC-007 | Every delivered PR links issue; issue discovers PR regardless of trace location, with confirmed readback. | Known-link/no-link/partial-effect tests and live two-way traversal; absent/unconfirmed link remains incomplete. |

[ADR-0003](../../docs/decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md) maps to neutral task contracts, current-launch worker/corrective prompts and explicit return/check/review separation. [ADR-0004](../../docs/decisions/ADR-0004-shared-routine-worker-permissions.md) maps to shared ordinary test/repair permissions in initial/resumed/corrective briefs, retained manual/external gates and inspected failed-call recovery. Worker and reviewer acceptance must test these effects, not merely cite ADR links. Existing initial-plus-two worker-session allowance remains; add no trace-specific budget.

## Risk and proof rationale

Highest leverage: actual owner-tool data can be lost by using metadata events, and uncertain remote sends can duplicate evidence. Use early permanent tests of those production seams, not speculative prototypes. [Research R2/R4](research.md) records supporting spans and alternatives. No experiment was implemented or run in planning. No exhaustive historical replay or mandatory comparison collection is needed.

Actual installed hook operation, live agent behavior, authorized GitHub write/readback and original-worktree-independent assessment remain NOT RUN. Offline fixtures cannot release those source-required gates. Actual external-effect authority must name proof scope and destination before those operations; if unavailable, report the unmet gate rather than call feature acceptance complete, without blocking safe local implementation startup. Failure that changes mechanism only can be corrected within scope; changed requirements, material privacy/architecture or permission policy returns to owner and affected review.

## Self-review disposition

Aligned this design and supporting artifacts with all FR-001–015, SC-001–008 and exclusions in the owner-approved current source. Requirements text remains frozen; source/page status updates only reflect the recorded actual grant. The new early HTML gate is an explicit owner requirement, not an inferred mechanism. Corrected the initial assumption that existing question-state callbacks or ask_user broadcasts carry full owner answers; use actual tool results. Distinguished optional capture writes from existing required operational-history safety. Kept both question routes and all fixer/review attempts, terminal evidence drain, payload readback, no-issue planning and all-PR linkage explicit. Preserved local Phoenix privacy and live-proof gates. No new owner decision is introduced by this faithful alignment. Parent targeted review/inspection precedes the authorized launch; implementation proof and independent implementation review remain required. This producer does not approve its output.

## Approved persistence and publication timing

The owner explicitly chose “ok, maintain sqlite for now”. Keep the existing SQLite store for active execution, pause and recovery. Publish assessment-relevant actual Q/A/reports/rejections/check/failure/retry/reference content at successful execution before its completion report; on practical failure publish the available partial trace, and after abrupt death recover publication explicitly when retained facts permit. This is not continuous publication. Keep required facts until independent GitHub content confirmation; later assessment needs neither old worktree nor SQLite. Terminal execution and confirmed durable content permit owner-directed database disposal, not automatic deletion. Internal control rows and full transcripts are not promised as uploads. No new DB or text archive is added.
