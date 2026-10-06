# Implementation Plan: Model Family and Reasoning-Effort Routing

**Branch**: `main` (SpecKit feature pointer: `001-model-family-routing`) | **Date**: 2026-10-06 | **Spec**: [approved specification](spec.md), digest and renewal in [spec-approval.md](spec-approval.md)

**Input**: the renewed Standard specification; [research and source provenance](research.md). This plan authorizes preparation, not implementation, model dispatch, live rollback, or benchmark-derived guideline mutation.

## Summary

Replace the two-class routing taxonomy with independent model-family and verified reasoning-effort selections throughout planner stages, shared task generation, delegated implementation, review and legacy recovery. Offer only provider-documented permitted usable runtime/effort choices for owner selection; record unverified proposals as non-dispatchable. Benchmark coverage is advisory under OD9, not an exact-pair hard gate. Use task risk/complexity, executable-oracle quality, context/tools, cost/latency, local outcomes and comparable signals with explicit uncertainty, justifying family separately from effort. Missing/conflicting evidence requires targeted research or an explicit bounded owner uncertainty decision; it cannot waive runtime support, owner authority or REQUIRED checks. Keep source facts, derived provisional recommendations, owner choices and project-learned outcomes distinct. An eligible Luna task must be unusually explicit and executable-oracle-backed. Failed task attempts are diagnosed and evidenced, checkpointed as NOT VERIFIED when task-owned changes exist, ordinarily reverted in a distinct commit, then—only if safe and authorized—escalated Luna → Terra → Sol within a maximum of three attempts.

## Technical Context

**Language/Version**: Markdown operational skills, Python 3 contract/fixture checks and POSIX/Git commands already used by this repository; installed Pi 0.87.1, SpecKit 1.0.12. No new runtime package is proposed.

**Primary Dependencies**: Existing Pi question/delegation and runtime model registry, SpecKit project commands for Standard, repository Git, existing coordination-memory contract, existing static test harness. Verify usable capabilities in the executing context rather than inferring them from the pins.

**Storage**: Existing approved SpecKit feature artifacts, indexed project-local coordination evidence and exact-content approved guidelines; durable compact feature [benchmark research](research.md) linked from `docs/index.md`, with byte-preserved source-identified [369-row archive](evidence/gpt_effort_benchmarks_2026-10-06.csv) and on-demand matching-row retrieval, never automatic whole-CSV intake or full-dataset prompts. No database, new global learned store or single growing log.

**Testing**: Focused Python static/mutation instruction checks plus temporary-Git fixtures for failed-attempt commit, inverse, evidence ordering and unrelated-work preservation; four narrowly authorized read-only binding/effort probes completed after this plan's first review (IDs and limits in [tasks](tasks.md) and project evidence). These were not task implementation, writer mutation tests or benchmarks; future live checks still require appropriate authority and truthful NOT RUN reporting otherwise. Test the single final-approval gate: a complete, evidence-backed task/reviewer assignment preview exists before the question; a changed or missing assignment blocks dispatch and returns for renewed approval. Existing lint, task-order, planner/coordinator/memory contracts and `git diff --check` remain relevant.

**Target Platform**: Pi skill-pack across unrelated Git projects; provider/catalog metadata vary at runtime.

**Project Type**: Portable configuration and process skills, not an application.

**Performance Goals**: Avoid blanket synthetic benchmarks or a required speed target. Reuse valid sourced evidence, selectively retrieve only relevant run history, and avoid combinatorial family × effort search. Task success and cost improvements are hypotheses to evaluate from real runs, not promises.

**Constraints**: No obsolete class routing or percentage quota in active instructions; preserve historical records as history. Provider documentation, permitted usable runtime/effort and owner authorization are hard gates. Benchmarks inform the task-sensitive advisory rubric, not eligibility, universal family rank or automatic maximum effort. Maximum three attempts; no automatic Astra fourth attempt; preserve approval/commit/review boundaries. No task-owned change means no empty failure/inverse pair and no automatic retry. Missing cause, ownership, commit safety or effort support stops affected execution. Insufficient benchmark applicability triggers research or a bounded owner uncertainty decision, not fabricated coverage or automatic rejection.

**Scale/Scope**: Planner and helper, brainstorming gate, shared task-generation, coordinator, coordination-memory owner, setup/requirements examples, source checkers and fixtures. Historical plan/review artifacts are not retroactively rewritten.

## Constitution Check (pre-research and post-design)

| Principle | Decision and check |
| --- | --- |
| Portable assets | Use family/effort and evidence contracts in skills, not project-specific model IDs or learned facts. Concrete model bindings stay runtime owner selections; global examples are illustrative. PASS for this design; implementation must verify. |
| Evidence before guidance | Retain cited benchmark facts separately from provisional recommendations and project-local outcomes; no project guideline edit before exact-content approval. [Research](research.md) names measured, estimated and missing evidence. PASS for design; initial guideline candidate needs its own gate. |
| Explicit authority | Current renewed spec approval applies to current spec only; material corrections renew it. Owner chooses permitted usable models/efforts and approves project-guideline mutation separately. PASS for design. |
| Pragmatic verification | Use focused negative cases for unsupported effort, missing-row automatic rejection, unresolved uncertainty, noncomparable-score ranking, unclear Luna task, failed-check commit/inverse and index drift; no invented exhaustive score matrix or live success claim. PASS for design. |
| Safe execution/recovery | Inspect failed invocation first; write factual evidence before failure commit/inverse; task-only ownership, baseline, deps and Git preflight; ordinary inverse only; stop on uncertain state. PASS for design conditional on implementation fixtures and separate review. |
| Compatibility/ownership | Preserve TinySpec/Standard and legacy artifact approvals; migrate active routing contracts deliberately, not old evidence; one canonical benchmark owner and existing memory store. PASS for design. |

Post-design recheck: the data/transition model and validation guide below preserve these principles. The owner-approved change intentionally supersedes old class and verified-only task-commit instructions for the bounded failed-attempt case; implementation must update the canonical contract and affected tests together. No unrelated constitutional amendment is assumed.

## Phase 0: Research, classifications and decision boundaries

Canonical feature-local [research.md](research.md) contains source-specific rows, dates, conditions and limitations, and is linked by [documentation routing](../../docs/index.md). It remains available as guidelines evolve; do not overwrite source facts with a newer provisional guideline. Research was read from inspected Terminal-Bench 4.0, BenchLM model pages and authenticated MCP, Artificial Analysis model pages and provider model documentation; the linked provider launch articles could not be read directly in this context. BenchLM's aggregate BenchAlign rank is labelled **Estimated** and is not a directly measured model-task result. A BenchLM source-linked row may supply qualified task context with reported version/effort and unknown metadata explicit; it cannot supply an invented exact-effort measurement. An uninspected primary citation does not become a firsthand finding. Separate the supplied AA 66-task/three-repeat mini-swe-agent setup from the public 330-trial leaderboard; no cross-harness percentage ranking. The existing [dependency research contract](../../skills/planner/references/dependency-research.md) remains the evidence-quality boundary for further targeted refresh.

**Current advisory evidence, not an eligibility matrix:** [research compact signals](research.md) retain E-L/E-T/E-S/E-A reported efforts and logical rows in the supplied raw archive, unknown snapshots/modes/dates, secondary source labels and weak/nonmonotonic counterevidence. The older public leaderboard remains historical source evidence, not current-version substitution. BenchLM Sol DeepSWE max 71.9% / high 75.2% is source-linked qualified page provenance (high is an owner-supplied page observation, refresh HTTP 403; primary article previously HTTP 403); the family CSV has no per-row effort. Estimated composites do not establish task success or exact effort outcomes.

**Capability boundary:** modelScope permits Terra 5.6, Sol 6.1 and Astra 6 and excludes Luna. The owner separately authorized four minimal read-only calls: Terra/medium, Terra/high, Sol/medium and Astra/high each completed a read on its exact requested model/effort; an earlier Sol/high planning writer completed source changes. [Task-specific proposals](tasks.md) replace the all-Astra snapshot with differentiated Terra/Sol/Astra options and a separately labelled non-dispatchable Luna alternative. Basic callability and requested effort labels are observed for the five distinct proposed pairs, not actual provider-internal effort, project-task success, writer mutation for every pair, price or future capacity. The installed worker declares mutation tools; before dispatch recheck current binding, role-specific tools/context/effort and permission. All assignments remain unselected pending final owner approval. Separate owner scope authority is required for any Luna option. No settings change or implementation probe is authorized. If current support is unavailable, mark the affected task blocked; do not silently substitute or skip an unavailable retry successor.

**Research decisions:** (1) Keep provider/version/effort and observed support separate from advisory benchmark metadata; (2) independently reason about family and effort using task profile/oracle/context/cost and qualified comparable signals, not a universal rank; (3) research applicability gaps or record an explicit bounded owner uncertainty decision before consequential selection; (4) preserve initial guidance and source-identified byte archive after guideline changes, while routine agents receive compact rubric/citations and inspect matching rows only on demand; (5) retain failed/blocked project outcomes without automatic guideline promotion. Alternatives rejected: universal class-to-provider map, all-Astra default, fabricated suitability scores, fixed effort ladder/automatic max, transferring old version results, naive cross-harness percentages, and benchmarking every combination ourselves. No current proposal is an owner preference or approved dispatch.

## Phase 1: Design and interfaces

[Data model and transitions](data-model.md) specify observed capability, advisory benchmark/uncertainty and archive retrieval, owner routing choice, task clarity, attempt budget, pre-recovery evidence and task-only commit/inverse state. [Quickstart validation](quickstart.md) describes runnable focused checks, negative fixtures, and separately gated live behavior. No external API is introduced by this process-skill repository, so SpecKit `contracts/` is not created; the operational interface contracts are in the existing skill owners and the data-model/quickstart artifacts.

### Operational seams in dependency order

1. **Evidence and capability vocabulary:** revise `REQUIREMENTS.md` and model configuration guidance so family/version/effort are separate, actual supported options are verified, not hard-coded or guessed; task-relevant benchmark signals, coverage gaps and uncertainty are advisory and separately attributed. Define how the coordinator records a concrete provider/model/effort and exact evidence; do not embed this repository's specific observed IDs in global skills.
2. **Shared routing/coordination authority:** update `skills/memory-handling/references/project-coordination.md` and task-generation for factual selected/observed effort, benchmark reference, independent family/effort rubric and research-or-owner uncertainty disposition. Retain a compact research → source-identified archive → matching-row retrieval contract without putting data into global assets or routine prompts. Keep source guidance distinct from per-project guideline updates; historical and current guidance remain selectively discoverable. Luna task briefs require objective, allowed surfaces, ordered explicit steps, producer dependencies, executable oracle and scope exclusions; incomplete briefs block dispatch.
3. **Planning producers:** migrate `skills/planner/SKILL.md`, `skills/planning-brainstorming/SKILL.md`, and `skills/delegating-architectural-planning/SKILL.md` from class-fixed stage tags to owner-selected eligible family/effort with current-content approval renewal and SpecKit stage evidence unchanged. Keep TinySpec/Standard routing separate from model choice; no stage may infer an unsupported runtime/effort or fabricate benchmark coverage. A supported pairing without a matching row can proceed only after research or an explicit owner uncertainty decision and normal routing authorization. **Before the single final implementation-approval question**, prepare and show a complete task-by-task assignment preview (family, concrete binding/version, effort, benchmark/capability evidence and task-specific rationale) plus independent reviewer; distinguish proposed assignments from approved selections. The owner may ask for changes before answering. The one affirmative current-content answer approves both task scope and listed assignments as distinct decisions; missing proposals or unresolved hard capability gates stop readiness; advisory gaps require research or an explicit bounded uncertainty disposition in the same final approval rather than a routine post-approval assignment gate. `skills/writing-skills/SKILL.md`, initialization and user-facing examples need accurate policy references.
4. **Coordinator and commit owner:** update `skills/coordinate-implementation/SKILL.md` and `skills/memory-handling/references/task-commit-contract.md` together. Recheck the approved assignment, task content, advisory applicability/uncertainty disposition and hard runtime capability immediately before each dispatch; stop and seek a renewed owner decision if any listed binding/effort/reviewer is changed or becomes unusable, never silently swap. Approval starts preflight, not an additional routine assignment-approval question. Preserve sequential producer-first batching, local/delegated eligibility, per-task verified commits and independent final review. Homogeneous batching should use actual selected model/effort compatibility and observed context rather than obsolete classes. The explicit failed-attempt exception checkpoints only safe task-owned changed content as NOT VERIFIED despite failed checks, then a separate ordinary history-preserving inverse; neither is success or a reason to release dependents. Pre-mutation evidence, focused Git ownership checks, safe stop and max-attempt sequence are invariant. Inspect failures before escalation. Avoid undocumented `reset`/history rewrite or blind cleanup.
5. **Compatibility and assurance:** revise normative docs and deterministic checkers/fixtures, including `scripts/check-planner-workflow.py` (its deliberate coordinator SHA freeze), `scripts/test-planner-workflow.py`, `skills/coordinate-implementation/scripts`, task-generation order fixtures, planning-brainstorming and coordination-memory checks. Existing historical docs remain provenance, not active defaults. Show named negative mutations for an unsupported effort, rejecting a supported no-row pairing solely for absence, fabricated exact-pair/owner-preference scores, ranking noncomparable harnesses, automatic whole-CSV loading, incomplete combined approval, Luna ambiguity, fourth attempt, bypassed failure evidence or unsafe inverse; temporary-Git tests verify distinct commits and index/working-tree preservation. Compare docs with implemented behavior.

### Recovery / rollout

Retain previous instruction commits for traceability; never rewrite historical source approvals or existing tasks to guess new routing. During deployment of this skill revision, each new or resumed task needing an unavailable permitted usable exact binding/effort stops at selection and returns to its applicable producing owner gate. Preserve valid pre-change tasks and approvals when their scope remains equivalent; changed acceptance/routing or approval drift renews only affected gates. No bulk project-memory migration, package install, push, deployment, provider call or automatic guideline seed is authorized by this plan. After any future global skill change tell the user to run `/reload` in pi.

## Project Structure

### Feature planning artifacts

```text
specs/001-model-family-routing/
├── spec.md                # renewed owner-approved WHAT
├── spec-approval.md       # external exact-content decision
├── checklists/requirements.md
├── research.md            # compact rubric/provenance, linked from docs/index.md
├── evidence/gpt_effort_benchmarks_2026-10-06.csv # raw bytes; matching rows on demand
├── plan.md                # this HOW; not yet approved
├── data-model.md          # routing/attempt states and invariants
├── quickstart.md          # validation guide
└── tasks.md              # reviewed tasks and pre-approval assignment proposal
```

### Existing implementation owners (future work only)

```text
REQUIREMENTS.md
README.md
docs/index.md
docs/pi-settings-sample.md
skills/planner/SKILL.md
skills/delegating-architectural-planning/SKILL.md
skills/planning-brainstorming/SKILL.md
skills/task-generation/SKILL.md
skills/coordinate-implementation/SKILL.md
skills/memory-handling/references/project-coordination.md
skills/memory-handling/references/task-commit-contract.md
scripts/check-planner-workflow.py
scripts/test-planner-workflow.py
skills/*/scripts/*                       # only affected contract and fixture checks
```

**Structure decision:** no new runtime service or external API; keep portable process rules in existing shared owners, feature-local researched evidence in SpecKit artifacts, and actual project outcomes/guidelines in their own project-local stores. Documentation discovery link is already bounded and committed; later updates must preserve unrelated content.

## Complexity Tracking

No constitutional violation is accepted by this plan. The failed-attempt commit exception and removal of fixed classes are expressly approved source changes, not a covert relaxation of safety gates. A too-large benchmark matrix or automatic learned policy would add speculative complexity and is excluded.
