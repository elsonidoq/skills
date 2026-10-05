# Project coordination memory — TinySpec source

## Context, provenance and authorization

Project owners and the agents using this skill pack need validated repository-specific coordination experience available **before Planner → Choose**, without reading entire execution histories or changing global skills after each project run.

Source provenance: the owner's conversation request titled “Implementation Prompt: Project-Specific Coordination Memory for the Skill Pack.” Its required lifecycle is compact memory → planning/tasks → implementation/verification → factual evidence → reflection → candidate updates → explicit user approval → compact memory. This document captures the requirements because the request has no supplied durable repository path.

Recorded owner decisions through the parent's callable question tool:

- Planning depth: **“TinySpec → Tasks → Implement.”** Selection authorizes preparation only.
- Source/task preparation binding for `sonnet-class`: **“openai-codex/gpt-6.1-sol.”** This is this run's selected binding, not a global routing rule. The successful preparation child supplies observed launch evidence; implementation/reviewer capability and selections remain coordinator preflight concerns.
- Brainstorm gate: **`NO_BRAINSTORM_NEEDED`**. The detailed request settles behavior, safety boundaries and non-goals; storage naming and contract placement follow inspected conventions. No material owner choice blocks source production. No owner deferrals.

Status: prepared source, **not approved for implementation**. Separate tasks, planner-owned review and combined source/task/scope approval are still required. This preparation authorizes only this file; no implementation, commits, project initialization, task file or discovery-index edits.

## Inspected authorities and constraints

- [Repository policy](../../AGENTS.md), “Global Assets”: “Do not add project-specific workflow, data, or historical rationale to global assets.” Generic contracts and fictional fixtures stay in the pack; actual guidelines/evidence stay in each associated project. Advise `/reload` after future global skill changes.
- [Documentation routing](../index.md), “Documentation Routing Guide”: this configuration suite has **no declared project-memory adoption contract**. Do not initialize a store in this repository as an implicit side effect of implementing support.
- [Memory Handling](../../skills/memory-handling/SKILL.md), “Discovering The Store” and “Write Protocol”: association requires repository instructions/configuration; default adopted gotcha memory is `memory/MEMORY.md`; “Never write completed-work summaries, file inventories, task ledgers, or git-owned metadata.” Coordination evidence must be a separate category/store, not appended to that index or existing gotcha entries.
- [Planner](../../skills/planner/SKILL.md), “Discovery,” “Before selection,” and “Selected production”: memory is already retrieved before choice and passed to stages; choice remains the owner's, preselection is read-only, and current-content approvals govern continuation.
- [TinySpec](../../skills/tiny-spec/SKILL.md) and [Task Generation](../../skills/task-generation/SKILL.md): one compact source, mandatory separate tasks, shared contracts for direct and SpecKit adapters. `sonnet-class` is bounded work; `opus-class` is work that cannot safely be decomposed, with the existing class-share approval rule.
- [Coordinator](../../skills/coordinate-implementation/SKILL.md), “Execute and Integrate,” “Select Execution Capability,” and “Review and Acceptance”: verified task checkpoints, per-task commits, sequential batches, owner-selected mappings, inspected-cause retry rules and one fresh independent final review remain mandatory.
- [Approval/recovery](../../skills/planner/references/approval-and-recovery.md): executive brief before `ask_user`, bounded affirmative authority, current content comparison, denial/cancellation/ambiguity gives no writes.
- [Requirements](../../REQUIREMENTS.md): existing two-class abstraction and runtime requirements; model identifiers are configuration, not permanent skill policy.
- [Workflow checker](../../scripts/check-planner-workflow.py): `EXECUTION_SHA256` freezes coordinator text from “Execution Capability Preflight” onward. Authorized reflection/checkpoint additions need a deliberate baseline update and independent preservation checks, not removal of the freeze.

These are repository-derived design decisions, not external-library recommendations. The [dependency research contract](../../skills/planner/references/dependency-research.md) was read in full: no dependency is added or selected, local contracts suffice, and new internet research is unnecessary. The legacy port's package/lockfile is outside scope. No dependency documentation writes or external capability assumptions are needed.

## Scope and exclusions

Extend `memory-handling` with a linked shared reference, proposed `skills/memory-handling/references/project-coordination.md`, owning optional coordination discovery, formats, retrieval and write boundaries. Integrate only the affected planner, TinySpec, task-generation and coordinator instructions; Standard consumes the same planner handoff and shared task contract, without a second workflow. Update focused Python static/fixture checks and user-facing setup/discovery documentation (`README.md`, `REQUIREMENTS.md`, `docs/index.md`, applicable regression guide).

Preserve existing gotcha-memory rules, adoption prerequisites, task formats, source approvals, model classes, class-share rules, sequential batching, review, task commits, failure inspection and legacy recovery. Missing **optional coordination memory** must not introduce new blockers; missing **already-required gotcha memory** remains its existing blocker.

Exclude ML, bandits, embeddings, confidence scores, synthetic model benchmarks, automatic model optimization, a global cross-project store, concrete model rules, bulk evidence intake, mandatory migration, automatic guideline mutation, unrelated skill changes, deployment/push and legacy-port changes. Preserve pre-existing untracked `.pi/` and `.specify/` files. Do not seed the motivating heuristic rule into global guidance or initialize a real project store in this feature run; use it only as an explicitly fictional fixture demonstrating supported project guidance.

## Approach and persistence contract

### Association and the two knowledge layers

Association comes from project instructions or documented project configuration naming a **coordination root**, independently of the gotcha index. Follow an existing equivalent layout where declared. For projects requesting a new layout, propose `<approved-project-memory-root>/coordination/` when a project-memory root already exists; otherwise obtain a project-local root through the existing question/approval interaction. This is a proposal convention, never a discovery assumption. Explicit approved paths are authoritative. Association/skeleton creation requires bounded user approval and preserves existing content; no-memory reads never initialize anything.

The new-root convention is:

```text
<approved-coordination-root>/
  GUIDELINES.md
  evidence/
    INDEX.md
    <run-id>/
      SUMMARY.md
      T001.md
      T002.md
      REFLECTION.md
```

Markdown matches current human-readable index/entry and planning conventions, requires no parser dependency and permits selective reads. `GUIDELINES.md` is compact synthesized coordination guidance, **not** the existing `MEMORY.md` gotcha index. `REFLECTION.md` is a proposal/decision record, not planner-consumed guidance.

Guidelines contain only relevant reusable planning, decomposition, delegation, verification, manual checkpoints, subsystem risk and implementation traps. Each guideline has a scope/trigger, short actionable statement, qualitative status (tentative/repeated/stable or owner-supplied), and evidence pointers where available. Preserve uncertainty and contrary evidence. Owner-supplied guidelines identify their origin without fabricating a supporting run. Merge/refine/supersede rather than accumulating transcripts or duplicating observations.

Evidence is factual and append-oriented. Reuse an existing safe project execution/run identifier; if none exists, derive a unique filesystem-safe date/subject ID and retain it in the execution tracker. Reuse that ID on resume; never overwrite another run. Task records identify task/type, areas/tags, residual reasoning when assessed, approved class, selected capability role/model and reasoning effort when observed, attempt/check results, reviewer findings, failure cause, retries/escalation and their outcomes, surprises and manual/user validation. Unknowns are explicitly unknown, not inferred successes. Keep individual attempts and corrections distinguishable; update summaries/index metadata without erasing observations. Link bounded check/review evidence rather than copying raw logs, secrets or sensitive payloads.

`INDEX.md` has one short row per run: linked summary, date, areas/tags, relevant patterns and concise outcome. Create/update the run record **before** its index entry; every new evidence write must refresh that run's row without duplicate entries. An interrupted record/index operation is reconciled on resume before reporting successful persistence. Task files remain separate; no ever-growing execution-log file. Index rows omit task transcripts and full logs.

### Retrieval and planning integration

Planner discovers and reads associated `GUIDELINES.md` during initial understanding, before brainstorming, scope assessment and depth choice. Report applicable guidance and carry its exact constraints/evidence references into both selected routes, downstream tasking and coordinator briefs. Guidance can affect the owner's informed depth choice, source observables, producer/consumer boundaries, checkpoints, acceptance and delegation; it cannot replace owner authority or source requirements. Missing undeclared coordination memory means existing behavior with no invented knowledge or writes. An explicitly declared missing/unreadable store is reported accurately; do not fabricate guidance or bypass an existing required-memory policy.

Do **not** automatically read `evidence/INDEX.md` or history on each request. Historical clarification is justified only by matching ambiguous/tentative/conflicting guidance, pattern synthesis, user requests for justification, or new contradictory observations. Then read the compact evidence index first, select relevant summaries/task records by tags and pointers, and open only those. No relevant evidence means proceed while retaining uncertainty. Never recursively load the directory or promote raw outcomes directly into instructions.

### Coordination evidence and conservative reflection

At existing task/attempt checkpoints, coordinator records observed outcomes in the associated evidence store and refreshes the index. Include failures, blocked/partial work and manual validation, not just successful completion. Evidence-write authority is bounded to the associated store; if association/write authority is absent, report observations in the existing execution handoff and offer future bounded setup rather than silently initializing a store. Evidence recording is not permission to mutate synthesized memory.

After implementation/verification and independent review (or when pausing a run with a blocker), lightweight reflection asks whether an observation is useful to future planning; project-specific versus general; reusable versus incidental; reinforcing versus contradicting existing guidance; supported enough for a guideline or evidence-only; informative about delegation; or something manual validation found that automated checks missed. Append attributable observations to run/task records, refresh the index, and separately record concise candidate changes in `REFLECTION.md`.

Distinguish direct observation, tentative pattern, repeated pattern, stable guideline, insufficient evidence and conflicting evidence without numerical confidence thresholds. A single failure may justify a narrowly scoped tentative caution, never a universal tier/subsystem ban. Review selected prior evidence only when needed to justify synthesis. Propose add/refine/supersede/remove changes with scope, status, supporting and contradicting evidence, plus evidence-only items. General lessons stay out of project guidance unless explicitly scoped; improving a global skill is separate approved work. If no reusable lesson exists, say no update proposed.

Before guideline mutation, coordinator shows an executive brief and exact candidate diff and uses the existing `ask_user` mechanism to allow **accept, edit, reject, or add a guideline**. Approval of implementation is not approval of future guidance. Edits/additions must have explicit approved resulting content; ambiguous/cancelled/unavailable interaction leaves the proposal pending and guidelines unchanged. Persist the answer, approved bounds and comparable baseline/proposed content evidence in the run reflection record. Re-read guidelines immediately before applying only approved changes; concurrent/baseline drift stops application and requires renewed review/approval. Reject leaves guidelines byte-identical; evidence and rejection record remain. Re-check relevant guidance after approved writes. Report feature acceptance separately from pending optional memory approval.

### Lightweight routing experiment

Use future real implementation outcomes, not benchmarks. Optional `residual_reasoning: low|medium|high` plus a brief rationale fits existing task notes/briefs; its absence preserves existing class selection. Favor a cheaper usable **owner-selected option compatible with the approved class** for low residual reasoning; medium only with a strong executable acceptance oracle and stronger verification/review; high favors a stronger compatible reasoning option. These are experiment proposals subject to capability/selection gates, not permission to silently replace selected models, relabel classes or waive acceptance. Existing `sonnet-class`/`opus-class` semantics remain authoritative; high residual reasoning alone does not force `opus-class` or bypass its share gate.

Record actual class, capability role, selected model/effort and observable outcome, while guidelines refer to capability/class and task/oracle conditions rather than provider names. On cheap-option failure, first inspect the child run and failed invocation. Preserve valid completed evidence and unrelated workspace changes; isolate/restore only the failed task's clean state where the existing workspace architecture and authority permit. Escalate through verified stronger capability and owner-selection gates; if no permitted option/cause/clean state can be established, stop with the precise blocker. Record both attempts; no automatic permanent guideline follows one outcome.

## Acceptance and proportional validation

Required implementation acceptance cases, using focused contract checks, instruction-removal mutations and explicitly simulated temporary-project fixtures where applicable:

| ID | Observable required behavior/check |
| --- | --- |
| A1 | A declared project-local guideline is discovered and carried into planner assessment **before** depth choice and downstream source/task constraints; no global-store fallback. |
| A2 | A project without optional coordination association/guidelines follows existing planning behavior, without initialization, fabricated facts or a new mandatory adoption gate. Existing required gotcha-memory failures remain distinct. |
| A3 | A coordinator checkpoint produces attributable task/run evidence, including failed/partial and manual-validation outcomes, within associated write bounds. |
| A4 | Two runs and multiple tasks persist as separate linked summary/task files; no monolithic history or synthesized transcript. |
| A5 | New and resumed evidence refresh the correct compact index row after record creation, retain existing runs, avoid duplicate rows, and reconcile an interrupted record/index update. |
| A6 | End reflection separates observation from synthesis, proposes scoped reusable guidance or evidence-only, and preserves tentative/contradicting/insufficient evidence. |
| A7 | A pending proposal, unavailable gate, cancellation or ambiguous answer leaves guideline bytes unchanged; implementation approval alone grants no memory mutation. |
| A8 | Explicit approval persists only accepted/edited/added guideline content and its decision/baseline evidence; re-reading detects concurrent drift and prevents unapproved overwrite. |
| A9 | Explicit rejection leaves synthesized memory byte-identical while keeping evidence and rejection disposition. |
| A10 | Evidence retrieval opens the index then only selected relevant run/task records; unrelated records stay unread and no match produces no invented project knowledge. |
| A11 | Routing records residual reasoning, actual class/model/effort, failures and stronger-tier outcomes without hard-coded global model policy or a permanent rule after one outcome; owner selections, approved classes and inspected-failure rules survive. |
| A12 | Existing TinySpec/direct and Standard/SpecKit contracts, approvals, legacy recovery, task order, class share, sequential batching, per-task commits and independent final review remain valid. |

The concrete failure seam is instruction wiring and filesystem/approval lifecycle, so focused Python static/mutation/fixture tests are the lowest sufficient automated layer; no new external test infrastructure or broad application suite. Lifecycle fixtures must identify themselves as simulated and not claim to execute models, production approvals or genuine SpecKit. Review actual links, stage placement, formats and candidate-diff authority manually. If a persistence helper is introduced during implementation, test the helper directly rather than a duplicate fixture implementation; do not invent an engine merely to make a fixture executable.

Required existing regression checks: `python3 scripts/check-planner-workflow.py`, `python3 scripts/test-planner-workflow.py`, coordinator intake/batching checks, task-generation contract/order checks, `bash scripts/check-skills-lint.sh`, and `git diff --check`. Extend existing tests or add a focused memory-handling contract/fixture test with documented invocation. Preserve the coordinator freeze with an explicitly reviewed updated digest for authorized additions; retain mutation assertions detecting lost safety clauses. New acceptance checks must demonstrably reject omitted approval/selective-read/class/failure boundaries, not merely match incidental keywords.

Real model compliance and end-to-end SpecKit behavior require separately authorized live runs and captured read/write/approval evidence; offline success is not proof of them. No live/provider/deployment tests are authorized by preparation. Required acceptance and actual PASS/FAIL/NOT RUN reporting cannot be weakened silently.

## Risks, recovery and next authorized stage

Natural-language adherence, evidence quality and index scale remain residual risks; small rows and selective reads reduce context cost but do not eliminate growth. No arbitrary scoring/retention framework is introduced. Failed writes, stale proposals and unavailable approval must be reported without calling persistence or acceptance passed. Existing stores and artifacts need no migration; proposed generic contract changes are reversible independently of project evidence.

No material source-production blocker remains. Implementation tests, independent implementation review and combined owner approval are **not performed**. Parent should inspect this source, generate separate tasks through the direct adapter, review both and seek the existing combined approval before coordinator preflight. This is source production, not feature completion.
