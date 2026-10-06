# Implementation Plan: Model Family and Reasoning-Effort Routing

**Branch**: `main` (SpecKit feature pointer: `001-model-family-routing`) | **Date**: 2026-10-06 | **Spec**: [approved specification](spec.md), digest and renewal in [spec-approval.md](spec-approval.md)

**Input**: the renewed Standard specification; [research and source provenance](research.md). This plan authorizes preparation, not implementation, model dispatch, live rollback, or benchmark-derived guideline mutation.

## Summary

Replace the two-class routing taxonomy with independent model-family and verified reasoning-effort selections throughout planner stages, shared task generation, delegated implementation, review and legacy recovery. Do not offer a family/version/effort without both observed runtime support and an inspected task-relevant benchmark result for that exact version and reported effort. Keep source-backed provisional routing advice separate from mandatory eligibility, owner choices and project-learned guidance. An eligible Luna task must be unusually explicit and executable-oracle-backed. Failed task attempts are diagnosed and evidenced, checkpointed as NOT VERIFIED when task-owned changes exist, ordinarily reverted in a distinct commit, then—only if safe and authorized—escalated Luna → Terra → Sol within a maximum of three attempts.

## Technical Context

**Language/Version**: Markdown operational skills, Python 3 contract/fixture checks and POSIX/Git commands already used by this repository; installed Pi 0.87.1, SpecKit 1.0.12. No new runtime package is proposed.

**Primary Dependencies**: Existing Pi question/delegation and runtime model registry, SpecKit project commands for Standard, repository Git, existing coordination-memory contract, existing static test harness. Verify usable capabilities in the executing context rather than inferring them from the pins.

**Storage**: Existing approved SpecKit feature artifacts, indexed project-local coordination evidence and exact-content approved guidelines; durable, independently discoverable feature [benchmark research](research.md) linked from `docs/index.md`. No database, new global learned store or single growing log.

**Testing**: Focused Python static/mutation instruction checks plus temporary-Git fixtures for failed-attempt commit, inverse, evidence ordering and unrelated-work preservation; targeted live model/effort checks require separate owner permission and must be reported NOT RUN otherwise. Existing lint, task-order, planner/coordinator/memory contracts and `git diff --check` remain relevant.

**Target Platform**: Pi skill-pack across unrelated Git projects; provider/catalog metadata vary at runtime.

**Project Type**: Portable configuration and process skills, not an application.

**Performance Goals**: Avoid blanket synthetic benchmarks or a required speed target. Reuse valid sourced evidence, selectively retrieve only relevant run history, and avoid combinatorial family × effort search. Task success and cost improvements are hypotheses to evaluate from real runs, not promises.

**Constraints**: No obsolete class routing or percentage quota in active instructions; preserve historical records as history. Benchmark-backed eligibility is a hard gate, but benchmark scores are not universal success predictions. Maximum three attempts; no automatic Astra fourth attempt; preserve approval/commit/review boundaries. No task-owned change means no empty failure/inverse pair and no automatic retry. Missing cause, ownership, commit safety, source evidence, or effort support stops.

**Scale/Scope**: Planner and helper, brainstorming gate, shared task-generation, coordinator, coordination-memory owner, setup/requirements examples, source checkers and fixtures. Historical plan/review artifacts are not retroactively rewritten.

## Constitution Check (pre-research and post-design)

| Principle | Decision and check |
| --- | --- |
| Portable assets | Use family/effort and evidence contracts in skills, not project-specific model IDs or learned facts. Concrete model bindings stay runtime owner selections; global examples are illustrative. PASS for this design; implementation must verify. |
| Evidence before guidance | Retain cited benchmark facts separately from provisional recommendations and project-local outcomes; no project guideline edit before exact-content approval. [Research](research.md) names measured, estimated and missing evidence. PASS for design; initial guideline candidate needs its own gate. |
| Explicit authority | Current renewed spec approval applies to current spec only; material corrections renew it. Owner chooses permitted usable models/efforts and approves project-guideline mutation separately. PASS for design. |
| Pragmatic verification | Use focused negative cases for unsupported effort, missing benchmark, unclear Luna task, failed-check commit/inverse and index drift; no invented exhaustive score matrix or live success claim. PASS for design. |
| Safe execution/recovery | Inspect failed invocation first; write factual evidence before failure commit/inverse; task-only ownership, baseline, deps and Git preflight; ordinary inverse only; stop on uncertain state. PASS for design conditional on implementation fixtures and separate review. |
| Compatibility/ownership | Preserve TinySpec/Standard and legacy artifact approvals; migrate active routing contracts deliberately, not old evidence; one canonical benchmark owner and existing memory store. PASS for design. |

Post-design recheck: the data/transition model and validation guide below preserve these principles. The owner-approved change intentionally supersedes old class and verified-only task-commit instructions for the bounded failed-attempt case; implementation must update the canonical contract and affected tests together. No unrelated constitutional amendment is assumed.

## Phase 0: Research, classifications and decision boundaries

Canonical feature-local [research.md](research.md) contains source-specific rows, dates, conditions and limitations, and is linked by [documentation routing](../../docs/index.md). It remains available as guidelines evolve; do not overwrite source facts with a newer provisional guideline. Research was read from inspected Terminal-Bench 4.0, BenchLM model pages and authenticated MCP, Artificial Analysis model pages and provider model documentation; the linked provider launch articles could not be read directly in this context. BenchLM's aggregate BenchAlign rank is labelled **Estimated** and is not a directly measured model-task result. A BenchLM source-linked row may inform a cautious candidate only when its specific version, effort and task relevance are established; an uninspected primary citation does not become a firsthand finding. The existing [dependency research contract](../../skills/planner/references/dependency-research.md) remains the evidence-quality boundary for further targeted refresh.

**Initial eligibility matrix, not an automatic assignment:** Terminal-Bench 4.0 directly reports GPT-5.6 Luna/max, GPT-5.6 Terra/max, GPT-5.6 Sol/max, and GPT-6 Astra/low, medium, high, xhigh and max (all 330 trials; different generation/date/harness confounds). These are narrowly relevant to terminal-agent implementation tasks, not all specification work. BenchLM source-linked DeepSWE coding and Sol agentic rows concern GPT-6 Luna and GPT-6.1 Sol, but the primary launch-chart effort/task protocol is not yet independently confirmed; no other effort is eligible from those rows. Artificial Analysis displays max-effort model evaluations, but an aggregate index is not a task-specific result. This plan **does not claim a complete initial candidate matrix** or authorize GPT-6 Luna/6.1 Sol at a guessed effort. Runtime modelScope observed during research excludes available Luna bindings despite the catalog listing them; changing scope or creating a model binding is future separately authorized implementation work. Research, runtime capability and scope checks must all succeed at each assignment and escalation; if the next family has no qualifying usable pair, stop and report the gap rather than skip it or use a proxy. Initial benchmark-based guideline candidates remain proposed, not active project memory.

**Research decisions:** (1) Keep exact model/version/effort as separate eligibility fields and provenance; (2) select among eligible pairs using task complexity, oracle strength, context, cost and observed project evidence, without treating a cross-version leaderboard ordering as causal; (3) refresh missing effort/workload metadata before that pair is offered; (4) retain all failed/blocked attempts as project-local evidence without treating one outcome as policy. Alternatives rejected: universal class-to-provider map, fixed effort ladder, transferring old version scores to new versions, treating aggregate Estimated ranks as measured rows, or benchmarking every combination ourselves. Remaining research gaps are explicit; they block only affected model choices, not the shared routing contract design.

## Phase 1: Design and interfaces

[Data model and transitions](data-model.md) specify observed capability, benchmark eligibility, owner routing choice, task clarity, attempt budget, pre-recovery evidence and task-only commit/inverse state. [Quickstart validation](quickstart.md) describes runnable focused checks, negative fixtures, and separately gated live behavior. No external API is introduced by this process-skill repository, so SpecKit `contracts/` is not created; the operational interface contracts are in the existing skill owners and the data-model/quickstart artifacts.

### Operational seams in dependency order

1. **Evidence and capability vocabulary:** revise `REQUIREMENTS.md` and model configuration guidance so family/version/effort are separate, actual supported options and qualifying benchmark rows are verified, not hard-coded or guessed. Define how the coordinator records a concrete provider/model/effort and exact evidence; do not embed this repository's specific observed IDs in global skills.
2. **Shared routing/coordination authority:** update `skills/memory-handling/references/project-coordination.md` and task-generation for factual selected/observed effort, benchmark reference, and benchmark-only eligibility. Keep source guidance distinct from per-project guideline updates; historical and current guidance remain selectively discoverable. Luna task briefs require objective, allowed surfaces, ordered explicit steps, producer dependencies, executable oracle and scope exclusions; incomplete briefs block dispatch.
3. **Planning producers:** migrate `skills/planner/SKILL.md`, `skills/planning-brainstorming/SKILL.md`, and `skills/delegating-architectural-planning/SKILL.md` from class-fixed stage tags to owner-selected eligible family/effort with current-content approval renewal and SpecKit stage evidence unchanged. Keep TinySpec/Standard routing separate from model choice; no stage may infer an unbenchmarked pairing. `skills/writing-skills/SKILL.md`, initialization and user-facing examples need accurate policy references.
4. **Coordinator and commit owner:** update `skills/coordinate-implementation/SKILL.md` and `skills/memory-handling/references/task-commit-contract.md` together. Preserve sequential producer-first batching, local/delegated eligibility, per-task verified commits and independent final review. Homogeneous batching should use actual selected model/effort compatibility and observed context rather than obsolete classes. The explicit failed-attempt exception checkpoints only safe task-owned changed content as NOT VERIFIED despite failed checks, then a separate ordinary history-preserving inverse; neither is success or a reason to release dependents. Pre-mutation evidence, focused Git ownership checks, safe stop and max-attempt sequence are invariant. Inspect failures before escalation. Avoid undocumented `reset`/history rewrite or blind cleanup.
5. **Compatibility and assurance:** revise normative docs and deterministic checkers/fixtures, including `scripts/check-planner-workflow.py` (its deliberate coordinator SHA freeze), `scripts/test-planner-workflow.py`, `skills/coordinate-implementation/scripts`, task-generation order fixtures, planning-brainstorming and coordination-memory checks. Existing historical docs remain provenance, not active defaults. Show named negative mutations for an unsupported effort, missing benchmark, Luna ambiguity, fourth attempt, bypassed failure evidence or unsafe inverse; temporary-Git tests verify distinct commits and index/working-tree preservation. Compare docs with implemented behavior.

### Recovery / rollout

Retain previous instruction commits for traceability; never rewrite historical source approvals or existing tasks to guess new routing. During deployment of this skill revision, each new or resumed task needing an unavailable exact binding/effort/benchmark stops at selection and returns to its applicable producing owner gate. Preserve valid pre-change tasks and approvals when their scope remains equivalent; changed acceptance/routing or approval drift renews only affected gates. No bulk project-memory migration, package install, push, deployment, provider call or automatic guideline seed is authorized by this plan. After any future global skill change tell the user to run `/reload` in pi.

## Project Structure

### Feature planning artifacts

```text
specs/001-model-family-routing/
├── spec.md                # renewed owner-approved WHAT
├── spec-approval.md       # external exact-content decision
├── checklists/requirements.md
├── research.md            # durable benchmark provenance, linked from docs/index.md
├── plan.md                # this HOW; not yet approved
├── data-model.md          # routing/attempt states and invariants
├── quickstart.md          # validation guide
└── tasks.md              # future SpecKit tasks stage, not created here
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
