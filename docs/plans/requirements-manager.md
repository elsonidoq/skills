# Requirements Manager implementation plan

## Status and scope

Design approved by the owner in this conversation. The owner subsequently authorized critique/fix followed by coordinated implementation and confirmed continuation. The reconciled task artifact records that authorization, reviewer dispositions, and model selections. This plan describes scope; execution evidence lives in the task/coverage artifacts.

This change is itself a candidate for the lightweight workflow: one detailed requirement, settled architecture, multiple bounded implementation tasks, and no need for a separate EPIC specification/planning pipeline. This plan exists because the owner explicitly requested it; Requirements Manager must not require an equivalent plan from its users.

## Intended outcome

Introduce `requirements-manager` as a plan-free entry point into shared brainstorming, task-generation standards, and existing coordinated implementation. Restore the original EPIC stage contract and protect it with regression tests. Preserve EPIC approval/provenance safeguards and keep batching independent of task origin.

## Evidence and settled decisions

- Historical source: `32e12feb382a6a0acb7e9d7f2e82559e3d397f2e:skills/epics-manager/SKILL.md`. It defines the brainstorming gate, optional brainstorm/fix stages, and stage-specific model assignments.
- `fdb91a5` removed that explicit pipeline during the skill rewrite. The current EPIC skill has readiness, SpecKit stages, approval gates, and review, but no explicit brainstorming stages.
- Current task standards are embedded in `skills/epics-manager/SKILL.md`; its dependency validator and tests live under `skills/epics-manager/scripts/`.
- `skills/coordinate-implementation/SKILL.md` currently requires specification, plan, and tasks and explicitly rejects task-only inputs. Its execution graph already depends primarily on task contracts.
- `scripts/install.sh` discovers suite skills dynamically; new skills should not require a hard-coded installer list.
- Owner-selected stage assignments use `sonnet-class` and `opus-class`, not provider/model IDs or historical agent names. Concrete callable bindings remain runtime capability checks and owner selections under `REQUIREMENTS.md`.
- Requirements Manager must reuse the historical EPIC brainstorming mechanism, not replace it with an independently written version or a generic brainstorming invocation.
- No separate plan, specification-generation stage, or SpecKit prerequisite is required for Requirements Manager.
- Latest owner-selected execution policy replaces the 15-task threshold and universal delegation: up to three bounded implementation tasks may run in the current agent when its selected model is appropriate; more than three implementation tasks require dependency-ordered delegation. Session reuse depends on observed context capacity, model-class match, and relevant retained context, not task count alone.
- Subsequent owner directive: commit each implementation task separately after its checks pass; do not review each task. Reuse class-specific agent sessions across task and commit checkpoints, and obtain one independent final implementation review.

## Architecture

```text
             Shared EPIC brainstorming
          gate → optional session → apply decisions
                    ↑                    ↑
              EPIC Manager      Requirements Manager
                    │                    │
             Spec + Plan          Resolved requirement
                    │                    │
             SpecKit tasks         Direct tasks
                    └──────────┬─────────┘
                      Shared task standards
                         and validation
                              │
                   Coordinate Implementation
                   origin-specific intake gates
                              │
                      Shared execution graph
                       ┌──────┴──────┐
                   ≤3 tasks        >3 tasks
                 Local if safe    Delegated batches
                  and class-fit   Context-aware reuse
                       └──────┬──────┘
                       Independent review
```

The diagram shows shared responsibilities and execution choices; the contracts below govern stage order, approvals, dependencies, model assignments, and capability fallbacks. The upward arrows indicate both managers reuse the same brainstorming primitive, not separate implementations.

### Shared brainstorming primitive

Add `skills/epic-brainstorming/SKILL.md`, discoverable by name from either manager. Extract the historical behavior rather than copying it into both managers:

1. Gate assessment returns `NO_BRAINSTORM_NEEDED` or `BRAINSTORM_NEEDED` with evidence.
2. Brainstorm only for open-ended design, owner product direction, or material technical trade-offs that block specification/tasking. Bias toward skipping when direction is settled or only mechanically answerable details remain.
3. If needed, present at most three agenda items, concrete alternatives, and a recommendation; the orchestrator owns user dialogue through `ask_user`, one material decision at a time.
4. Apply exactly the owner's decisions to the bounded source, retain settled decisions and deferrals, and carry concise handoff context forward.

Parameterize the source and next-stage readiness target, not the behavior. An EPIC source is an existing selected brief section. A lightweight source may be the captured requirement within the task artifact. Do not modify unrelated source sections, invent scope, or create a plan.

Use `sonnet-class` for the bounded gate assessment and decision-application work; the original gate used a general agent without a class assignment. Keep interactive brainstorming orchestrator-owned. Verify required skills/tools and model mappings; stop with a capability report if unavailable rather than silently forking the mechanism.

### Shared task-generation contract

Add `skills/task-generation/SKILL.md`. It owns common task semantics and validation, not EPIC planning or execution:

- Outcome, prerequisites, likely files/interfaces, independently observable acceptance evidence, required capabilities, model class, and class rationale.
- Bounded work defaults to `sonnet-class`; reserve `opus-class` for work that cannot safely be decomposed. Preserve the existing 30% limit and recorded owner exception.
- Complete in-scope coverage, explicit exclusions, integration/acceptance checks, and documentation tasks whose evidence checks documentation against implemented behavior.
- Consecutive execution-order task numbers, earlier prerequisites, contiguous stories/setup segments, and manual checks of implicit dependencies and stage feasibility.
- Follow observed project formats. Use numbered Markdown with explicit dependency fields when there is no established format; do not impose a global project directory or state schema.

Move the validator and its tests to this skill as the single implementation. Update all references. If observed external callers require the old script entry point, use a forwarding wrapper rather than duplicate validation logic; otherwise remove the old location.

EPIC Manager runs its detected SpecKit task command under this shared contract. Requirements Manager derives tasks directly from its resolved requirement under the same contract. Capability checks are adapter-specific: direct task production does not inherit SpecKit's plan prerequisite.

### EPIC Manager

Restore this canonical stage sequence with executable stage descriptions, not just a diagram:

```text
brainstorm_gate
  → [epic_brainstorm → epic_brainstorm_fix (sonnet-class)]
  → spec_create (sonnet-class)
  → plan_create (opus-class)
  → tasks_create (sonnet-class)
  → overall_review
  → done
```

Both gate and optional stages reference the shared brainstorming primitive. `plan_create` combines review/correction of the spec with plan production; `tasks_create` is create-only, with task corrections owned by overall review. Overall review uses an observed permitted independent reviewer, not a hard-coded model.

Keep current constitution/capability preflight, sizing/provenance, documentation coverage, explicit specification approval, overall review approval, durable revision evidence, and fresh-session handoff. Treat approval checks as checkpoints within this sequence rather than additional create/critique/fix stages. Clarification is optional when requested or required by the detected project's workflow, not an unconditional extra stage. If planning/review changes approved specification content, renew its approval before handoff.

Do not restore historical fixed project paths, obsolete tools, rigid state JSON, provider IDs, or speculative defaults for material owner decisions. Stages must be resumable from verified artifacts and decision records using existing project conventions.

### Requirements Manager

Add `skills/requirements-manager/SKILL.md` with this orchestration:

1. Accept a detailed prompt or explicitly selected source; inspect repository instructions, evidence, applicable memory, and existing artifacts.
2. Check that the work fits the lightweight route. Reuse the existing sizing guidance; if scope justifies an EPIC, explain why and obtain the owner's route decision rather than silently rerouting.
3. Capture the requirement durably in an existing source/decision artifact, or within the task artifact. Include scope, acceptance criteria, exclusions, constraints, and source evidence. This is requirement preservation, not an intermediate design/plan phase.
4. Run the shared brainstorming gate; invoke the shared brainstorm and decision-application behavior only when needed.
5. Generate tasks directly using the shared task-generation contract. Record documentation scope directly from the requirement and inspected changes rather than from a missing plan.
6. Review requirement-to-task traceability, coverage, ordering, model share, integration, and exclusions. Obtain explicit approval of the current requirement/tasks and implementation scope. Record content/revision evidence and unresolved or deferred owner decisions.
7. Hand off explicit source, tasks, approval, and review locations to `coordinate-implementation`. Execute in the same session if the owner requested execution; otherwise provide a fresh-session handoff. The coordinator always performs its own preflight and agent/model selection.

A well-specified requirement skips brainstorming, not review or owner authorization. A chat-only approval is insufficient for a fresh-session handoff. Missing capabilities or unverifiable approvals stop the workflow with a precise report.

### Origin-neutral execution boundary

Refactor coordinator intake, artifact references, and execution-strategy selection:

- Common contract: approved requirement/source, task list, applicable supporting artifacts, durable authorization/review evidence, and workspace context.
- For EPIC-origin work, specification, plan, both existing approvals, and required SpecKit stage evidence remain mandatory.
- For Requirements Manager, source/requirement plus tasks and current review/approval suffice; no placeholder specification or plan is created.
- For other producers, verify the documented origin, current owner authorization, and applicable project gates. Ambiguous origin is a blocker, never permission to downgrade safeguards.
- Run SpecKit implementation/prerequisite instructions only when applicable to the selected artifacts. Merely having SpecKit installed must not make a direct task list require a plan.

After intake, use one execution graph and select the execution strategy by the complete approved implementation task count (not plan presence, workflow origin, or the number remaining on resume). Preserve that selection on resume unless scope changes or an observed safety/context constraint requires revision. Change references to mandatory spec/plan in briefs, review, and defect routing to the applicable source/supporting artifacts. Sequencing defects return to the producing workflow's review gate.

### Execution strategy: local versus delegated

For up to three bounded implementation tasks, the current agent may execute locally only when its owner-selected model/class is appropriate, scope is clear, and observed context capacity is adequate. If a task needs another model class, broader isolation, or more context, delegate that task or segment. Do not silently switch the current model or downgrade task classes.

For more than three implementation tasks, delegation is mandatory. Batch consecutive same-class tasks to amortize agent startup and reuse relevant context. Plan/task producers must organize coherent work so this grouping is feasible without reordering approved prerequisites. Aim for 5–7 tasks when scope and context permit; this is guidance, not a quota. Internal dependencies and shared files are acceptable within one agent when tasks execute sequentially with producer verification before consumer work. Story/stage headings and shared write surfaces alone do not require new batches; preserve their internal task order and acceptance checkpoints. Split for model-class changes, owner gates, observed context limits, genuinely incompatible scope, or integration prerequisites that cannot be satisfied within the batch. A one-task batch remains valid when justified. Never pull distant tasks forward or reorder dependencies merely to fill a batch.

Both routes share one execution graph, applicable preflight, verification, integration, durable tracker, authorization gates, and independent final review. Record strategy from the complete approved implementation-task count (excluding standalone review tasks); completing tasks does not downgrade a delegated run to local execution on resume. Do not create origin-specific execution algorithms.

- Separate task/commit checkpoints, execution batches, and agent sessions. Checkpoints do not inherently require a new child or a per-task review.
- Resume only when supported, the selected model/class matches, retained context is relevant, and observed context headroom is adequate. Consider accumulated context, compaction, tool-output volume, and demonstrated task scope; do not treat cumulative billed tokens as identical to occupied context. A very expensive first task is a warning to inspect capacity, not a reason to force session reuse.
- Do not cap normal implementation sessions at one per class. When context is inadequate, record evidence and launch a fresh bounded child with durable artifact/evidence handoff. If context metrics are unavailable, state the limitation and conservatively narrow the next delegation.
- Inspect failed runs and invocations before retry or relaunch; context rotation is not permission for blind retries or unauthorized model changes.
- Commit each implementation task separately after its checks pass, before starting the next task, whether local or delegated. This supersedes the earlier single-small-run and per-batch commit policies. Preserve project policy, resolve conflicts with the owner, and commit verified review fixes separately.
- Obtain one fresh independent final review after implementation commits; no per-task reviews. The reviewer inspects the full committed revision range, not merely a clean working-tree diff.

This candidate has more than three implementation tasks and therefore uses delegated batches. Derive the actual schedule after correcting the reviewed task ordering, using the selected Terra/Sol mappings and observed context capacity; no forced one-session-per-class schedule applies.

## Implementation sequence

These are planned work packages, not an execution-approved task artifact. Each package should become a task under the shared contract when implementation is authorized.

| Order | Work package | Depends on | Model class | Acceptance evidence |
|---|---|---|---|---|
| 1 | Establish baseline contract tests and shared brainstorming primitive | None | sonnet-class | Historical gate/decision behavior is covered; both skip and brainstorm paths have explicit contracts; missing capabilities stop safely. |
| 2 | Extract task-generation semantics and relocate the validator/tests | 1 | sonnet-class | Existing validator tests pass at the shared location; one standards definition remains; reference and format checks pass. |
| 3 | Restore EPIC stage orchestration using shared primitives | 1, 2 | sonnet-class | Exact ordered stage chain, class assignments, conditional branches, create/review ownership, approvals, and resume behavior pass contract checks. |
| 4 | Update shared batching criteria and upstream task organization for context continuity | 2, 3 | sonnet-class | Coordinator batches coherent consecutive same-class work to amortize startup; sequential internal dependencies/shared files are allowed; headings alone do not split batches. Task generation and EPIC planning preserve dependencies while preparing context-coherent work. Focused scenarios/mutations catch gratuitous stage/file splits and unsafe regrouping. |
| 5 | Generalize coordinator intake and add local/delegated execution selection | 2, 3, 4 | opus-class | Origin-specific gates remain intact; task-only input works without SpecKit/plan; up to three bounded tasks permit model-appropriate local execution; more than three require delegation using shared batching; context-aware session reuse, per-task commits, and one final review are explicit. |
| 6 | Add Requirements Manager orchestration and handoff | 1, 2, 5 | sonnet-class | Detailed prompt goes directly to tasks; optional brainstorming uses the shared primitive; no plan or SpecKit stage is required; approval and execution handoff are explicit. |
| 7 | Integrate documentation and direct-task entry points | 3–6 | sonnet-class | README examples, create-epic direct-task handoff, applicable adoption guidance, requirements, indexes, and discovery instructions match implemented behavior. |
| 8 | Complete regression, mutation, and scenario validation | 1–7 | sonnet-class | Static tests/lint pass; targeted mutations fail; EPIC and lightweight scenario matrix has recorded outcomes and limitations. |

Package 5 uses `opus-class` because preserving multiple authorization contracts while removing mandatory artifact assumptions is the principal judgment-heavy boundary. Other packages are bounded by this approved design. This planned split is one of eight packages, below the existing 30% threshold. These implementation assignments are separate from the fixed model classes of future manager stages and from complexity assignments on tasks those managers generate.

## Regression strategy

Add deterministic workflow-contract tests runnable without model calls, and wire them into routine suite validation so they are not an optional forgotten check. Keep skill prose authoritative; do not add a separate unused manifest that can pass while operational instructions drift.

Tests must verify:

- Canonical EPIC stage order and actual stage sections/instructions.
- Gate skip transition and conditional brainstorm → fix → spec transition.
- `sonnet-class` for specification/task creation and decision application; `opus-class` for plan creation.
- Both managers reference the same brainstorming and task-generation skills; dependency availability checks and stop behavior are present.
- Task creation is create-only and overall review owns correction.
- EPIC spec/plan and approval requirements remain enforced, including stale-approval handling.
- Lightweight intake explicitly permits requirement/tasks without a plan or SpecKit.
- One downstream execution graph remains with origin-neutral strategy selection; sequential and homogeneous segment/batch constraints are preserved.
- Batching prioritizes startup amortization and relevant context continuity. Sequential dependencies, shared files, and story/stage headings alone do not force a split; task producers prepare coherent consecutive work while preserving prerequisite order. Mutations reject reinstated automatic heading/file splits and unsafe dependency regrouping.
- Boundary cases of three and four implementation tasks select eligible local execution and mandatory delegation respectively; review-only tasks are excluded and resume does not switch strategy merely because fewer tasks remain.
- Local execution requires class/model suitability and context capacity; delegation preserves dependencies and resumes sessions only when class, retained context, and observed headroom are suitable.
- Task verification and per-task commits are independent of new agent launches; all implementation tasks receive separate commits, with one independent final review.
- Missing resumption/context capacity and inspected failures produce explicit, evidence-backed fallbacks, not blind retries or unauthorized model switches.
- New skills have valid frontmatter, discoverable names, and resolvable supporting files.

Mutation tests edit in-memory copies to remove each required stage, reorder stages, bypass the gate, change a required model class, remove a shared reference, reinstate mandatory-plan wording for direct inputs, remove the local/delegated strategy, change the three-task boundary, permit class-based dependency reordering, or remove independent review. Each mutation must make the relevant checker fail. These tests enforce explicit prompt contracts, not proof that a model will obey them; retain scenario review for behavioral coverage.

Scenario matrix:

| Scenario | Expected result |
|---|---|
| Well-specified localized multi-task requirement | Skip brainstorming; generate/review tasks directly; coordinator uses shared execution. |
| Three bounded tasks, current model appropriate | Local execution permitted; verify and commit each task, then independent final review. |
| Three tasks requiring a different model class or excessive context | Delegate affected work; no silent model switch or class downgrade. |
| Four tasks, or a delegated list resumed with three remaining | Mandatory delegation remains selected; use sequential shared batches and per-task commits. |
| Delegated task consumes substantial context | Inspect actual capacity and handoff evidence; narrow batches or rotate sessions rather than forcing reuse. |
| Small list with observed context pressure or broad conflicting scope | Record evidence and use smaller segments or existing batching; retain verification and approval gates. |
| Resumption unavailable or implementation agent fails | Report resumption limits; inspect any failure before targeted continuation/relaunch; no blind retry. |
| Small run under conflicting project commit policy | Resolve the policy conflict with the owner before execution; record the approved commit boundaries. |
| Multiple tasks in one reused session | Verify and commit each task separately without launching a new agent or conducting a per-task review. |
| Consecutive same-class producer/consumer tasks touching shared files across phase headings | Keep coherent work in one batch where context and scope permit; execute sequentially with producer checks and separate task commits. |
| Class change, material owner gate, incompatible scope, or context limit inside coherent work | Split at the evidenced boundary; never reorder prerequisites or pad batches with distant tasks. |
| Material product or technical uncertainty | Shared gate emits agenda; owner decides; fix applies only decisions before tasking. |
| Large initiative or substantive scope expansion | Explain sizing; obtain route decision; preserve EPIC path. |
| Existing EPIC from an earlier session | Validate stage artifacts and current approvals; do not assume done from a label. |
| Missing/stale approval or ambiguous origin | Stop before implementation at the applicable producing gate. |
| No SpecKit installed | Requirements path works; EPIC reports unavailable required capability. |
| SpecKit installed but direct task input selected | Do not require or fabricate a plan. |
| Forward dependency or resumed story | Validator/review rejects it; coordinator does not silently reorder. |
| Missing delegation/model binding/question capability | Report blocker; do not switch to unauthorized local implementation. |
| Opus task share above 30% | Require recorded exception before finalizing tasks. |
| Handoff or resume after requirement/task edits | Compare current content with approval evidence and renew affected approval. |

## Verification and delivery

- Run `scripts/check-skills-lint.sh` and the shared validator unit tests.
- Run the new workflow-contract and mutation test suite through its documented validation entry point.
- Review references and all coordinator artifact assumptions; inspect the diff to ensure no second batching algorithm was introduced.
- Run the scenario matrix as focused prompt/contract walkthroughs; use bounded runtime trials only if permitted capabilities are available and the owner authorizes them. Report static coverage separately from live behavior.
- Obtain independent assessment through the existing review workflow when an authorized reviewer is available; report unavailable review honestly.
- Do not execute the installer, make provider/configuration changes, commit, or launch paid delegates merely to publish this plan.
- After implementation, explain installation/discovery of new skills and remind the owner to run `/reload` inside pi.

## Exclusions

No product implementation, duplicate origin-specific batching algorithm, parallel-batch policy, SpecKit replacement, EPIC sizing redesign, global project state schema, runtime package upgrade, or restoration of obsolete platform-specific commands. The local/delegated threshold, context-continuity batching criteria, context-aware reuse, and per-task commits are the intended downstream policy changes; batch selection/dependency machinery remains shared rather than duplicated by origin. No retroactive conversion of unrelated historical task artifacts.
