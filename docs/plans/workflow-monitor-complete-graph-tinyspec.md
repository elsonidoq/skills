# Workflow monitor — complete planned graph TinySpec

**Status:** Retained planning draft for parent review. Owner authorized source preparation and focused commits; separate tasks, source/task review and combined owner approval remain pending. This is not an approved execution handoff, implementation authorization or feature-completion claim.

## Context and authority

The owner needs a monitor that shows the complete recorded plan from launch, preserves planned identities through execution, identifies the selected run unmistakably, and separates **plan progress**, **execution outcome/color**, and **acceptance**.

Source provenance: owner conversation selected TinySpec and requested persistent selected-run identity, the complete declared plan from launch, permanent planned nodes with distinct attached executions, factual status and a synthetic transition demonstration. The owner's subsequent correction explicitly requires successful execution returns (including workers) **GREEN**, execution failures **RED**, and acceptance separately in Details; later checks/review must not recolor a successful worker. The latest direction authorizes commits and continued planning, not implementation. These conversation requirements are preserved here without depending on temporary analysis files. Earlier neutral-worker/red-rejection presentation is superseded only where inconsistent with this execution-color contract; historical rejection evidence remains authoritative.

Preparation follows checkout-local [TinySpec](../../skills/tiny-spec/SKILL.md), [SDD guidance](../best_practices_spec_driven_development.md), [dependency research](../../skills/planner/references/dependency-research.md), [early risk reduction](../../skills/planner/references/early-risk-reduction.md) and [parsimony](../../skills/planner/references/parsimony.md). Applicable [repository instructions](../../AGENTS.md) and [constitution](../../.specify/memory/constitution.md) still govern. [Decision routing](../index.md) selects no general ADR store; this draft selects none and does not alter accepted ADR outcomes or the running ADR workflow.

Owner-selected preparation profile: **`openai-codex/gpt-6.1-sol`, medium**. This records selection, not verified runtime binding or an implementation assignment.

Verified memory: whole `memory/MEMORY.md` index contains no gotchas; `memory/coordination/GUIDELINES.md` contains no approved guidelines. Neither was changed.

## Scope

**Included:** read-only monitor normalization/public presentation, graph composition, selected-run UI, Details/legend, focused regression coverage and corresponding monitor README corrections.

**Excluded:** runtime recording redesign, scheduler/retry engine, database migration, history rewrite, reconstructed plans from current task files, extra reviewer invocations, polling changes/budgets, standalone prototype, new dependencies, installs, signals, reloads, or interaction with the running ADR workflow.

No tasks are generated here. This source and its minimal discovery entry are the only authorized repository changes, with a focused verified [planning checkpoint](../../skills/memory-handling/references/task-commit-contract.md). Separate task production, review and combined owner approval remain downstream gates; this checkpoint grants no execution authority.

## Evidence and bounded approach

The producer was inspected first:

Code spans below were checked at source-preparation baseline `1840c0c83db736c05ce912a485cf5f8819ed57af`:

- [Engine.invoke](../../runtime/coherence_workflow/engine.py#L37-L51) registers the descriptor **before** iterating tasks; [descriptor construction](../../runtime/coherence_workflow/monitoring.py#L92-L109) includes all task IDs and dependencies. Existing recording suffices (A1); no runtime recording redesign.
- [Phase declarations](../../runtime/coherence_workflow/monitoring.py#L19-L28) include Independent review. [Final-review execution](../../runtime/coherence_workflow/engine.py#L129-L164) occurs once after all tasks—not once per task (A1).
- [Normalization](../../workflow_monitor/mapping.py#L41-L106) and [public mapping](../../workflow_monitor/public.py#L61-L94) retain task topology. [Graph composition](../../workflow_monitor/web/src/graph.ts#L27-L51) currently renders actual occurrences instead of permanent plan topology; consume the declared topology to satisfy A1.
- [Worker/checkpoint recording](../../runtime/coherence_workflow/engine.py#L100-L123) separates worker `returned`, checks and successful checkpoint. [Review result recording](../../runtime/coherence_workflow/engine.py#L151-L164) distinguishes valid result facts from transport/malformed failures. These support separate execution/acceptance summaries (A2).
- [Pagination](../../workflow_monitor/app.py#L131-L171) retains occurrences while paging observations; [snapshot enrichment](../../workflow_monitor/app.py#L253-L260) already precedes paging. Summarize full evidence at that boundary (A3).
- [Run minimization](../../workflow_monitor/public.py#L53-L58) currently emits generic labels with opaque refs; [selector/header](../../workflow_monitor/web/src/main.tsx#L63-L68) omits explicit run identity. Add only the requested display identity, preserving routing refs (A4).

**Repository-derived implementation choice:** enrich the existing normalized/public snapshot, then consume it in existing graph/UI helpers. No producer/store change is justified. Public summary semantics must be established before graph/UI consumption, without inventing a task chain.

Minimal seams: `mapping.py`/`public.py`, existing pre-pagination enrichment in `app.py`, `web/src/graph.ts`, associated DTO types, `main.tsx` and existing Details components; update `workflow_monitor/README.md` in place. No migration; rollback is reverting presentation changes, not altering recorded rows.

Dependency declarations inspected: React `^19.1.1`, ReactFlow `^12.8.5`, ELK `^0.11.1`, Playwright `^1.55.0`, TypeScript `^5.9.2`, Vite `^7.1.3` ([package declarations](../../workflow_monitor/web/package.json)). These are declared ranges, not independently verified installed versions. Reuse existing composition/layout/test mechanisms; no new dependency API or external research is needed for this bounded presentation change. Before authorized checks, verify prepared versions/capabilities without installing. Canonical operating/dependency owner remains the [monitor README](../../workflow_monitor/README.md), discoverable from the [documentation index](../index.md).

## Deterministic presentation contract

### Plan identity and availability

- From the first valid snapshot, show every declared task and prerequisite edge, including unstarted work. Planned task identities are stable and run-scoped.
- Planned nodes remain visible throughout transitions. Attach distinct worker/fixing/reviewer occurrences; never replace plan nodes with execution history or collapse separate attempts.
- Show the declared final-review stage as **“Planned independent review — not an agent call.”** Attach actual reviewer executions separately. Generic possible-flow edges are neither task dependencies nor evidence of scheduled calls.
- Dependency, attachment, recorded-sequence and correction edges remain distinguishable.
- Missing, malformed, partially unusable or fallback-empty task descriptors show **“Complete graph unavailable”**, retaining valid available history. Do not present a partial graph as complete or repair it from progress rows/current files.
- Unsupported stores/read failures remain unavailable/error views, not empty completed workflows.

### Separate plan progress

These are proposed display derivations from existing evidence, not new scheduler states:

| Progress | Rule |
|---|---|
| Pending | Declared task, no started work and no demonstrated impediment. |
| Running | Started task work without established terminal result, qualified by recorded runner state. |
| Completed | Successful task checkpoint/completion evidence; worker return alone is insufficient. |
| Failed | Recorded task-scoped failure; identify the failing step without recoloring other successful executions. |
| Blocked | Unstarted task whose declared prerequisite is incomplete/failed, or explicit evidence prevents continuation; identify the prerequisite/reason. |

Waiting for input is a separate factual annotation, not an invented dependency failure. An otherwise independent unstarted task after termination says **“Not started; run stopped”** rather than dependency-blocked. Uncertain/incomplete evidence remains qualified rather than forced into a definitive progress state. A later final-review rejection does not erase completed task checkpoints.

`skipped` and `cancelled` are unsupported by the current recording vocabulary. Explain this in legend/Details/README; never infer either from absence, interruption, abandonment or run failure.

### Separate execution color

Derive each occurrence’s summary from **all normalized observations before pagination**:

- **GREEN:** explicit successful execution return, including worker/fixing-worker `returned`. This does not mean accepted work.
- **RED:** established failure of that execution. A different check, question, checkpoint or final review cannot recolor a successfully returned worker red.
- **Waiting:** outstanding recorded input/gate evidence, resolved using the full snapshot. Question delivery failure belongs to that question, not automatically its parent execution.
- **Running:** started without terminal evidence and compatible recorded runner state; label as *recorded running*, not proof of present process activity.
- **Unknown/incomplete:** insufficient/conflicting evidence, unfinished history with stopped/unknown runner, interruption or abandonment; retain the recorded qualification.

Established terminal execution outcome takes precedence over stale waiting/running observations. Preserve distinct attempts rather than merging their outcomes.

**Repository-derived reviewer interpretation proposed for review, not an additional owner requirement:** the producer records both valid rejection and transport/malformed failure as review `failed`. A valid typed `approved` plus `finding_count` result demonstrates a returned reviewer; the proposed execution summary is GREEN while acceptance remains rejected. Without that evidence, preserve failure/uncertainty; do not infer a successful reviewer return. No broader reviewer-color propagation or historical rewrite is proposed.

### Separate acceptance and identity

Details independently expose check results, checkpoint status, review approval/findings count, recorded ranges, and current full-range acceptance qualification. Preserve original rejection and correction-only/unresolved/cyclic limitations even when execution is GREEN.

Expose the requested run ID narrowly as text in every selector item and a persistent selected-run banner, including loading/error states. Selection remains unambiguous when labels match. Preserve opaque routing/reference IDs. Reuse stable task anchors; a narrow explicit task-ID display is an implementation recommendation for distinguishable generic task labels, not permission to expose private task prose.

## Compatibility and security

Keep legacy outcome/completeness evidence intact; add distinct execution summaries rather than redefining historical acceptance fields. Pagination must affect loaded evidence only, never already-established status.

Preserve existing stale-fetch/layout guards, status-only viewport/selection reuse, correction lineage and read-freshness distinctions. Preserve read-only SQLite access, closed GET API, loopback/same-origin/header restrictions and response protections. Add no raw errors, prompts, results, private task prose or unrelated identifiers; render requested identity as text, not markup.

## Observable acceptance and proof

**A1 — Complete plan through transitions.** A synthetic multi-task run includes T001, T002 and another pending task. Before completion, every declared task/dependency and the distinct planned final-review stage is visible. Across pending → running → returned/checkpoint and failure/review snapshots, planned node IDs persist, pending nodes remain, and attempts/reviews stay distinct.

**A2 — Focused T001/T002 outcome regression.** Successful returned workers are GREEN; failed workers RED; start-only/incomplete histories are appropriately running/unknown; outstanding input is waiting. A subsequent check failure or rejected final review leaves successfully returned T001/T002 workers GREEN while Details preserve failed acceptance evidence.

**A3 — Pagination-independent truth.** Place return/failure/question-answer evidence beyond the first observation page, including beyond the current default 50. First-page status equals fully loaded status; loading history neither changes established execution outcome nor creates a false outstanding question.

**A4 — Identity, history and compatibility.** Two identically labelled runs are selectable unambiguously; selected ID persists through loading/error and stale responses cannot replace the selected graph. Missing/partial plans show “Complete graph unavailable” with available history. Separate repair/review attempts, rejection evidence and review-range qualifications survive. Unsupported skipped/cancelled states are never synthesized.

**Proof selection:** permanent tests of actual normalization/presentation/graph helpers address the highest risk—mixing acceptance with execution and deriving status from partial evidence. Extend existing Python/public/history tests and composed Playwright execution/history/navigation/lineage fixtures. Exercise valid rejecting reviewer versus actual failure to validate the stated inference. Update obsolete color assertions without deleting rejection assertions. Build/type-check the existing web app. No separate prototype or new test framework is justified.

Synthetic browser checks must exercise production monitor helpers/UI with synthetic recorded facts, not a parallel mock implementation. They demonstrate composition and transitions, **not genuine live-workflow observation**.

**Execution limits:** application tests/build/browser checks are **NOT RUN**, not yet authorized by this source-preparation assignment. Current authority permits source/index preparation, bounded planning validation and a focused commit only. Link/span checks, source-coherence review and `git diff --check` validate this document, not the feature. Separate tasks, current-content review and combined owner approval remain pending before an execution handoff. Future failed or unrun product checks cannot establish acceptance; failures block reliance on the affected behavior until corrected and rechecked. Source/scope changes return through existing review/approval gates. No running ADR workflow interaction is required or authorized.

## Residual risks

Historical malformed reviewer results cannot always prove successful return. Invalid/fallback descriptors cannot establish complete topology. Recorded running is not a process-liveness guarantee. The proposed status derivations and reviewer inference require focused implementation evidence; no feature acceptance or readiness is claimed.
