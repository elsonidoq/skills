# Requirements Manager implementation tasks

**Status: CRITIQUE-REVISED (revision 2) / INDEPENDENT REVIEW COMPLETE WITH MECHANICAL FIXES / PENDING TASK RECONCILIATION BEFORE DISPATCH.**

**Latest owner directives supersede older policy text below:** up to three bounded implementation tasks may execute locally when the current selected model/class and context are appropriate; more than three require delegated shared batching. Do not force one resumed implementation session per class; reuse depends on observed context capacity. Verify and commit each implementation task separately, with no per-task reviews and one fresh independent final review. Terra is selected for `sonnet-class` implementation; GPT-6.1 Sol for `opus-class` implementation and fresh independent reviews; T011's class flag is resolved as `opus-class`.

Independent task review: `/tmp/requirements-manager-task-overall-review.md`, verdict `READY_WITH_MECHANICAL_FIXES`. Before dispatch, reconcile the active task bodies and source hashes with these directives, move the source-derived coverage baseline before replacement-skill production, and explicitly require canonical operational-stage order plus reorder mutations. Bootstrap is the owner-authorized direct execution path, not a claim that the current coordinator already accepts direct tasks. The earlier critique findings remain historical evidence, not current policy. The plan has been updated; its earlier hash below is historical and no longer binds the current revision.

This is a direct task-production artifact derived from the owner-approved design in
[`requirements-manager.md`](requirements-manager.md). Except for the authorization boundary stated in
[Scope of the exclusions in this artifact](#scope-of-the-exclusions-in-this-artifact), it does not itself
authorize implementation, delegation, commits, or an execution handoff; the parent session is handling the
owner's implementation authorization at a review barrier.

Three review stages are deliberately distinct and must not be conflated:

1. **This critique-stage record** (§Critique review record) — a task-artifact correctness review performed in the
   critique/fix stage. It is not an independent overall review, not the post-implementation semantic diff review
   (T011), and not owner implementation approval.
2. **Independent overall review of this task artifact** — still outstanding; it must verify the current artifacts
   and record owner implementation approval before `coordinate-implementation` can act.
3. **Post-implementation independent semantic diff review (T011)** — reviews the delivered diff against the
   original request, the historical EPIC contract, and current protections.

The owner's design approval of `docs/plans/requirements-manager.md` stands. No critique-stage change in this
revision is represented as owner-approved, and no item here is labelled implemented or complete.

**Evidence-honesty rule for the whole artifact:** deterministic checks in T008/T009/T010 assert prompt-contract
conformance in repository text. Passing them never demonstrates that a model or coordinator obeys those prompts at
runtime, and no report from T010 or T011 may claim otherwise.

## Provenance and settled approvals

- **Source design:** [`requirements-manager.md`](requirements-manager.md), owner-approved in the parent
  conversation; read as the authoritative scope, architecture diagram, execution-policy boundary, seven work
  packages, regression strategy, and exclusions.
  - sha256 `4393a641c34d5b3f2817b39c7eb0fa1b0581a9d7eb36ae3c1087c577bd7ee1e4`; git blob
    `11d7271ea944dc3b5e3c70e88ad7229522ffb257` (23137 bytes).
- **Reviewed task revision (pre-critique):** revision 1 of this file, sha256
  `35070a8b71ffb360a90d10d3c58e71fc276d40d9fd5b430ea4a2e456496cff69`; git blob
  `d8a7b549571ea7a6238f12cc8010efbbc0e7788f` (20640 bytes). Findings in §Critique review record cite this revision.
  Revision 2's own hash is intentionally not embedded (a recursive self-hash proves nothing); the parent may hash
  the delivered file once.
- **Historical source:** `32e12feb382a6a0acb7e9d7f2e82559e3d397f2e:skills/epics-manager/SKILL.md` (614 lines) —
  its create-only `tasks_create`, brainstorm gate/agenda/decision-application behavior, flagged-item protocol,
  reading and handoff contracts, resume recovery, and fixed future stage assignments. Confirmed removed in
  `fdb91a5`, which rewrote `skills/epics-manager/SKILL.md` (782 changed lines) and deleted
  `skills/epics-manager/scripts/resolve_epic.py`, `migrate_state.py`, and `tests/test_compatibility.py`.
- **Current evidence inspected:** `AGENTS.md`, `REQUIREMENTS.md`, `README.md`, `docs/index.md`,
  `docs/best_practices_spec_driven_development.md`, `docs/pi-settings-sample.md`,
  `skills/epics-manager/SKILL.md`, `skills/epics-manager/scripts/check-task-order.py` and
  `test_check_task_order.py`, `skills/coordinate-implementation/SKILL.md`, `skills/create-epic/SKILL.md`,
  `skills/install-memory/SKILL.md`, `skills/initialize-documentation/SKILL.md`,
  `skills/memory-handling/SKILL.md`, `skills/requesting-code-review/code-reviewer.md`,
  `skills/receiving-code-review/SKILL.md`, `scripts/check-skills-lint.sh`, `scripts/probe-pi-load.sh`,
  `scripts/install.sh`.
- **Settled constraints carried verbatim in effect:** Requirements Manager accepts a detailed requirement
  (optionally with a selected source), is plan-free, and does not require SpecKit; brainstorming is governed by the
  original EPIC `brainstorm_gate` → conditional `epic_brainstorm` → `epic_brainstorm_fix` behavior exposed as one
  shared primitive (reused, never forked); direct tasks carry the same standards as EPIC tasks; coordination and
  execution are common and independent of SpecKit; the EPIC pipeline is restored as
  `brainstorm_gate → [epic_brainstorm → epic_brainstorm_fix] → spec_create (sonnet-class) → plan_create
  (opus-class) → tasks_create (sonnet-class, create-only) → overall_review → done`; EPIC approval/provenance
  safeguards are preserved; SpecKit remains the EPIC stage provider; stage classes are owner assignments and are
  distinct from implementation-task complexity classes; fewer than 15 approved implementation tasks normally use at
  most one implementation session per class, resumed sequentially in dependency order, followed by independent
  review; 15 or more retain existing batching; no parallel implementation batches; documented capability checks and
  fallbacks are preserved; owner model/binding choices and the inspected-failure-before-retry rule are preserved;
  the owner approved one focused small implementation commit before review, subject to project policy.
- **Owner-critical coverage requirements added in revision 2:** a durable requirement-to-implementation/test matrix
  derived from the original request, the historical EPIC, and current protections; a preserved/changed/removed
  behavior inventory; an independent final semantic diff review rather than tests that merely match rewritten
  prompts; mutation checks that fail on missing operational stage instructions (not only missing diagram tokens);
  and no claim that static text tests prove model behavior.
- **Approval state:** design approval is recorded above. This task list has **not** received independent overall
  review or owner implementation approval. Any approval evidence must bind to the then-current requirement/source
  and task-list content.

## Critique review record (revision 2)

Reviewer contract used: `skills/requesting-code-review/code-reviewer.md` (findings first, severity, precise
location, impact, correction, verdict, verification gaps). Dispositions follow `skills/receiving-code-review/SKILL.md`
(valid / invalid / ambiguous / already addressed / outside scope, with action or evidence-based reason). This record
is durable so later sessions can inspect it.

| ID | Severity | Location (pre-critique revision) | Finding | Disposition |
|---|---|---|---|---|
| F1 | blocking | §Tasks — no task produced any source-derived coverage artifact; §Coverage checklist only mapped design work packages to tasks | Nothing bound the delivered work to the **original request + historical EPIC + current protections**, so the shortened redesign could pass while silently dropping behavior. | Fixed (valid): added T002 (matrix + behavior inventory + capability/fallback inventory) and made T004, T010, T011 consume it. |
| F2 | blocking | §Tasks T003–T005 acceptance lists only the canonical stage sequence | No **preserved/changed/removed behavior inventory**, so historical operational behavior (reading contract, flagged-item protocol, handoff context, resume recovery, `done` report, deferral recording) could be deleted with the diagram still "correct". | Fixed (valid): T002 requires the inventory; T004 requires each preserved row implemented and each change/removal recorded with rationale. |
| F3 | blocking | §Tasks T007–T008 acceptance ("removed/reordered required stages", "each mutation must make the relevant checker fail") | Checks could be satisfied by tokens in the architecture diagram or by any matching sentence, so **missing operational stage instructions would not fail mutation**. | Fixed (valid): T008 requires each stage check to resolve the stage's operational section and required operational elements; T009 lists mutations that delete instruction bodies, class assignments, gate transitions, create-only wording, capability stop text, and stale-approval wording while leaving the diagram intact. |
| F4 | important | §Tasks T009 acceptance ("independent overall review is requested … when available") | No defined reviewer, inputs, classification, or disposition requirement — a weak or self-review could satisfy it, and it could not detect stages deleted relative to the historical contract. | Fixed (valid): new T011 with reviewer-independence rule, required inputs (diff, original request, historical commit, current protections, matrix/inventory, reviewer contract), classification (preserved/changed/removed/absent per row), severity findings, verdict, and `UNAVAILABLE` honesty. |
| F5 | important | §Tasks T007–T009 acceptance | Tests asserted prompt text and could be reported as proof that EPIC behavior was restored. | Fixed (valid): T008/T009/T010/T011 must state the static prompt-contract limitation; the artifact states the same rule up front. |
| F6 | important | §Tasks T009 "…do not … commit, or authorize execution"; §Scope boundary | Read literally, these could be taken as forbidding the later owner-authorized implementation stage from delegating or committing. | Fixed (valid): added §Scope of the exclusions in this artifact; T010's exclusions are explicitly scoped to that task; the owner-approved single focused small-run commit before review, its review-fix commit, and 15+ per-batch commits are preserved. |
| F7 | important | §Tasks T003 acceptance | Restored-EPIC acceptance omitted design-mandated items: optional/conditional clarification, approvals as checkpoints rather than extra create/critique/fix stages, renewal of specification approval when `plan_create`/`overall_review` changes approved spec content, sizing/provenance admission verdict, documentation coverage, and observed (not hard-coded) reviewer selection. | Fixed (valid): added to T004 acceptance. |
| F8 | important | §Tasks T001/T003/T005 capability mentions | No inventory preserved the **documented capability checks and their unavailable-case behavior** (SpecKit stage detection, mandatory delegation, question tool plus prose fallback, model-class binding resolution, memory store, constitution preflight, reviewer selection). | Fixed (valid): T002 requires the capability/fallback inventory with current `file:line`; T008 asserts presence and stop wording; T010 must report unavailable capabilities as `UNAVAILABLE`, never `PASS`. |
| F9 | minor | §Tasks T005 acceptance | Omitted two design-mandated Requirements Manager behaviors: documentation scope derived from the requirement and inspected changes (not from a missing plan), and sequencing defects returning to the producing workflow's review gate. | Fixed (valid): added to T006 acceptance. |
| F10 | minor | §Tasks T006 acceptance | Omitted install/discovery explanation and the `/reload` reminder, the coverage-artifact index entry, and README routing that admits owner-authorized direct task lists into the coordinator. | Fixed (valid): added to T007 acceptance and dependencies. |
| F11 | minor | §Task contract "Count and split" | Count/share statements became stale after renumbering. | Fixed: revision 2 records 11 tasks, 9 `sonnet-class`, 2 `opus-class` (18.2%, below the 30% cap, no exception). |
| F12 | minor | §Coverage checklist, §Review concerns | Referenced only the old numbering and lacked matrix-completion and semantic-review rows. | Fixed: checklist and concerns updated. |
| F13 | minor | §Tasks T011 | The `opus-class` assignment for the independent semantic diff review is a critique-stage judgment, not an owner-settled assignment; reviewer binding is an owner selection at coordinator preflight. | Flagged for owner rather than silently settled; rationale and the `sonnet-class` alternative are recorded in T011. |
| F14 | important | §Tasks T003/T005 acceptance | No verification that obsolete historical elements stay excluded (OpenCode command files/paths, provider or agent IDs, `resolve_epic.py`-style resolution, rigid JSON state schema). | Fixed (valid): T008 adds negative assertions; T009 adds a mutation that reintroduces a legacy token; T011 reviews for reintroduction. |
| F15 | minor | `scripts/probe-pi-load.sh` `REQUIRED` list | The explicit discovery list still names `use-railway`, which no longer exists in `skills/` (removed by `6782415`), so the paid probe would fail on a stale entry rather than on a real regression. | Fixed (valid, in scope): T007 now also reconciles stale required entries; recorded in §Handoff context. |

Not changed (outside the critique stage): the architecture, stage sequence, class assignments of EPIC stages, the
15-task boundary, the small-list policy, and the seven-package shape are owner-settled and were left untouched. The
plan document `docs/plans/requirements-manager.md` and the existing `docs/index.md` edits were preserved.

**Verification executed in this revision:**

| Command | Result |
|---|---|
| `python3 skills/epics-manager/scripts/check-task-order.py docs/plans/requirements-manager-tasks.md` (pre-critique revision 1 and post-critique revision 2) | PASS both times |
| `python3 skills/epics-manager/scripts/test_check_task_order.py` | OK, 5 tests |
| `bash scripts/check-skills-lint.sh` | 21 skills checked, 0 failed |

**Residual risks after this revision:** (a) prose-contract checks still cannot prove runtime obedience; (b) T002's
matrix is only as complete as its derivation from the named sources, so the draft-before-reading-new-prompts rule
must be observed; (c) reviewer availability for T011 is unknown and may end as `UNAVAILABLE` with a recorded
blocker.

## Task contract and execution shape

All tasks use the shared task-generation contract being introduced: an explicit outcome, backward-only
prerequisites, narrow likely write scope, observable evidence, capability needs, exactly one implementation
complexity class, and a class rationale. `Model class` below is an implementation-task complexity assignment, not a
provider ID and not a replacement for the fixed classes of future EPIC workflow stages, which are owner
assignments.

**Count and split:** 11 tasks — 9 `sonnet-class`, 2 `opus-class` (18.2%; below the 30% limit; no exception needed).
T005 is the authorization/execution-contract task; T011 is the independent semantic diff review (see T011 for the
class rationale and the owner-flag).

**Contiguous stages:** shared primitives and coverage baseline (T001–T003) → restored EPIC contract (T004) →
coordinator authorization/execution boundary (T005) → Requirements Manager producer (T006) → documentation and
entry-point routing (T007) → deterministic contract and mutation coverage (T008–T009) → integration/acceptance
evidence (T010) → independent semantic diff review (T011). This is an eleven-task small list under the proposed
policy; the eventual coordinator must select the execution strategy from the approved implementation-task count and
revalidate actual scope, approvals, capabilities, and project policy rather than treating this description as
execution authorization.

## Tasks

### Shared primitives and coverage baseline

- [ ] T001 [Shared brainstorming] Extract the historical EPIC brainstorm gate, orchestrator-owned agenda/decision behavior, and decision-application contract into one discoverable `epic-brainstorming` skill that both managers invoke without duplicated behavior.
  - **Depends**: none.
  - **Likely files/interfaces / narrow write scope**: add `skills/epic-brainstorming/SKILL.md`; add focused deterministic contract tests only in the established skill-test location or a new adjacent test location; make only the minimum reference seam needed for test discovery. Preserve current manager behavior until T004/T006 consume the primitive.
  - **Acceptance evidence/checks**: contract tests cover `NO_BRAINSTORM_NEEDED`, the bounded `BRAINSTORM_NEEDED` agenda (maximum three items), orchestrator-owned material decisions, exact bounded decision application that leaves unrelated source content untouched, durable handoff/deferral recording, and capability-report stop behavior; the skill has valid discoverable frontmatter (`name` equal to its directory, `Use when…` description) and resolvable supporting files; tests assert the skill's own text and are labelled as prompt-contract checks with the explicit limitation that they prove no runtime model behavior; `scripts/check-skills-lint.sh` passes.
  - **Capability needs**: local file editing, Python/test runner, suite static lint; no model call, SpecKit installation, or runtime configuration change.
  - **Model class**: sonnet-class.
  - **Rationale**: bounded extraction from a named historical source with deterministic prose-contract checks.

- [ ] T002 [Coverage baseline] Produce the durable requirement-to-implementation/test matrix, the preserved/changed/removed behavior inventory, and the capability/fallback inventory that later tasks and the final independent review must satisfy.
  - **Depends**: none.
  - **Likely files/interfaces / narrow write scope**: add `docs/plans/requirements-manager-coverage.md`; add its one entry under the existing "Implementation Plans" section of `docs/index.md`. Do not modify `docs/plans/requirements-manager.md`, this task artifact, or any skill/script.
  - **Derivation rule (binding)**: every row is derived only from (a) the owner's authoritative scope and request as preserved in the design plan and the handoff, (b) the historical EPIC contract at `32e12feb382a6a0acb7e9d7f2e82559e3d397f2e:skills/epics-manager/SKILL.md`, and (c) current protections in `skills/epics-manager/SKILL.md`, `skills/coordinate-implementation/SKILL.md`, `skills/create-epic/SKILL.md`, `REQUIREMENTS.md`, `docs/best_practices_spec_driven_development.md`, and the current scripts/tests. Draft the matrix **before** reading any newly written `requirements-manager`, `epic-brainstorming`, or `task-generation` skill text, and record that ordering in the artifact so the matrix cannot be reverse-engineered from the rewritten prompts.
  - **Required content**: matrix columns `ID | source citation | required behavior | carrying stage or rule | status (preserved | changed-deliberate | removed-deliberate | removed-unaccounted) | rationale | expected task ID(s) | expected check/test ID | evidence status (planned | verified | missing)`; a historical behavior inventory covering the brainstorm gate, conditional brainstorm, decision application/fix, reading contract, spec creation, plan creation (review and create in one pass), create-only task creation, overall review, the flagged-item protocol (categories, never-flag list, single-option auto-accept rule, coordinator-side parsing, deferral scan), handoff context protocol, orchestrator-owned dialogue, resume/interruption recovery, the `done` readiness report, and the historical fixed stage classes — each marked preserved / changed / removed with historical line evidence and the current protection that retains or replaces it; a capability and fallback inventory (SpecKit stage detection and `UNAVAILABLE` stop, mandatory delegation, question tool with its prose fallback, model-class binding resolution with owner selection and no inference, memory store, constitution/principles preflight, independent reviewer selection) citing the current `file:line` for each and its required unavailable-case behavior; a deliberately-not-restored list (fixed project paths, OpenCode command files, `resolve_epic.py`-style resolution, rigid JSON state schema, provider/model IDs, named historical agents) with rationale; and an explicit statement that EPIC stage classes are owner assignments while this artifact's `Model class` values are implementation complexity classes.
  - **Acceptance evidence/checks**: every historical stage/behavior and every sentence of the owner's authoritative scope maps to at least one row; no row is left `removed-unaccounted` without an owner-facing flag; every row names its implementing task and expected check; no unsourced claim; `scripts/check-skills-lint.sh` still passes after the docs-only change.
  - **Owner-facing rule**: if the inventory shows a behavior removed by the redesign that the owner's scope does not authorize removing, or a capability fallback that would be lost, flag it to the owner instead of restoring or deleting it silently, and record the open question plus affected row IDs.
  - **Capability needs**: read-only inspection of repository files and git history (`git show <commit>:<path>`), local file writing.
  - **Model class**: sonnet-class.
  - **Rationale**: citation-driven extraction and comparison from named sources into deterministic evidence columns; the task records ambiguity for the owner rather than deciding architecture.

- [ ] T003 [Shared task generation] Create the single task-generation contract and relocate the dependency/story-order validator plus its unit tests so both producers use one validator implementation, retaining a compatibility wrapper only when an observed caller requires it.
  - **Depends**: T001.
  - **Likely files/interfaces / narrow write scope**: add `skills/task-generation/SKILL.md`; move or centralize `skills/epics-manager/scripts/check-task-order.py` and `test_check_task_order.py` under the shared skill; update only proven in-repository validator references (including the `skills/epics-manager/SKILL.md` pointer, which must not be left dangling) and add a forwarding wrapper only if such a caller exists. Do not create a project-global task format or state schema.
  - **Acceptance evidence/checks**: unit tests pass from the shared location; the validator still rejects missing/duplicate/gapped IDs, missing/forward/self dependencies, and resumed/noncontiguous story segments while accepting explicit `Depends: none` and prior ranges; search confirms exactly one validation implementation; the shared contract states outcome, prerequisites, files/interfaces, separately observable evidence, capability needs, class plus rationale, the 30% `opus-class` limit with recorded owner exception, consecutive execution numbering, contiguous story/setup segments, documentation tasks whose evidence checks documentation against implemented behavior, and manual checks of implicit dependencies and stage feasibility; tests are labelled as prompt-contract/validator checks.
  - **Capability needs**: local file editing, Python 3, repository search, suite static lint.
  - **Model class**: sonnet-class.
  - **Rationale**: a localized extraction with readily executable unit evidence and one narrow compatibility decision.

### Restored producer and execution contracts

- [ ] T004 [EPIC workflow] Restore executable EPIC Manager stages using the two shared primitives while preserving the current SpecKit preflight, provenance, approvals, revision evidence, and fresh-session safeguards.
  - **Depends**: T001, T002, T003.
  - **Likely files/interfaces / narrow write scope**: modify `skills/epics-manager/SKILL.md` and only its directly referenced validator path/test references; do not revive historical fixed paths, OpenCode command files, obsolete tools, JSON state schema, provider IDs, or named historical agents.
  - **Acceptance evidence/checks**: every stage in the exact sequence `brainstorm_gate → [epic_brainstorm → epic_brainstorm_fix (sonnet-class)] → spec_create (sonnet-class) → plan_create (opus-class) → tasks_create (sonnet-class) → overall_review → done` has its own operational instruction section with entry condition, inputs, class assignment, executable steps, outputs, gate/approval behavior, and resume behavior — a pipeline diagram and a stage name alone do not satisfy this; the gate skip transition and the conditional brainstorm path are explicit; clarification is conditional (only when requested or required by the detected project workflow) rather than an unconditional stage; approval checks remain checkpoints inside the sequence and no `epic_critique`/`spec_fix`/`plan_critique`/`tasks_fix` stage is reintroduced; `plan_create` performs spec review/correction plus plan creation in one pass and `tasks_create` is create-only with corrections owned by overall review; `overall_review` uses an observed permitted independent reviewer selected with the owner rather than a hard-coded model/provider; a specification approval that `plan_create` or `overall_review` invalidates by changing approved content is renewed before handoff; the sizing/provenance admission verdict, documentation coverage, durable revision evidence, constitution/capability preflight, and fresh-session handoff are preserved; capability `UNAVAILABLE` stops use the existing report format; resume derives state from verified artifacts and decision records, not a `done` label; each T002 inventory row is honoured (preserved rows implemented, changed rows implemented as recorded, no `removed-deliberate` row silently reinstated and no preserved row dropped).
  - **Capability needs**: local file editing, repository search, deterministic test runner, suite static lint; no simulated SpecKit command.
  - **Model class**: sonnet-class.
  - **Rationale**: the approved sequence, inventory rows, and preserved safeguards are explicit prose contracts with a bounded affected surface.

- [ ] T005 [Coordinator origin-neutral boundary] Refactor coordinator intake and execution-strategy instructions so it enforces origin-specific authorization evidence before one shared execution graph, including the small-list policy without changing large-list batching.
  - **Depends**: T003, T004.
  - **Likely files/interfaces / narrow write scope**: modify `skills/coordinate-implementation/SKILL.md` and directly coupled workflow-contract test fixtures only. Do not add a second implementation/batching algorithm, weaken EPIC gates, or alter runtime provider configuration.
  - **Acceptance evidence/checks**: EPIC origin still requires spec, plan, both current approvals, review evidence, and applicable SpecKit evidence; Requirements Manager origin accepts approved requirement/source plus tasks plus current review/authorization with no fabricated plan or SpecKit prerequisite, and the current "requires a spec, plan, and tasks" sentence is revised accordingly; other producers verify documented origin, current owner authorization, and applicable project gates, and ambiguous origin blocks; strategy selection uses the complete approved implementation-task count (not plan presence, origin, or tasks remaining on resume) and is recorded and retained on resume unless scope changes or an observed safety/context constraint requires a recorded revision; 14 selects small-list execution and 15 selects existing batching; one-class small lists use one implementation session followed by independent review; mixed small lists preserve consecutive dependency-ordered segments and resume class-matching sessions without regrouping across prerequisites or story/stage boundaries; **parallel implementation batches remain prohibited in both strategies**; mandatory delegation, task-level checks, producer-before-consumer integration, owner gates, allowed write scope, durable tracking, and owner selection of each class's agent/model binding with no inferred selection are preserved; checkpoints (verification, integration, progress, commits) do not require new agent launches; unavailable resumption/context pressure and inspected failures produce evidence-backed fallbacks with no blind retry or unauthorized model switch; default commits distinguish the focused small-run implementation commit before review (subject to project policy and explicit owner exceptions), the review-fix commit, and retained per-batch large-list commits; sequencing defects return to the producing workflow's review gate rather than being silently reordered.
  - **Capability needs**: local file editing, repository search, deterministic workflow-contract tests, suite static lint; owner/runtime question and delegation tools remain documented execution preconditions rather than invoked here.
  - **Model class**: opus-class.
  - **Rationale**: this is the indivisible judgment-heavy authorization and execution contract where a subtle relaxation could bypass approvals, reorder dependencies, or lose origin-specific gates.

- [ ] T006 [Requirements Manager] Add the plan-free Requirements Manager as a direct task-producing adapter that preserves the resolved requirement, reuses shared primitives, records review/approval evidence, and makes a coordinator handoff explicit.
  - **Depends**: T001, T003, T005.
  - **Likely files/interfaces / narrow write scope**: add `skills/requirements-manager/SKILL.md` and its directly coupled deterministic tests only; do not create a SpecKit replacement, an intermediate plan/specification stage, or a bespoke execution path.
  - **Acceptance evidence/checks**: contract tests show detailed prompt/selected source inspection and an explicit lightweight-route sizing decision that reuses existing guidance and asks the owner rather than silently rerouting EPIC-sized work; settled requirements, scope, criteria, exclusions, constraints, sources, deferrals, and revision evidence are durable in an existing artifact or the task artifact; only the shared brainstorming gate can trigger optional dialogue/application; direct tasks use the shared task contract, and **documentation scope is recorded directly from the requirement and inspected changes rather than from a missing plan**; traceability/coverage/order/model-share/integration/exclusions review and explicit current owner authorization are required, and chat-only approval is insufficient for a fresh-session handoff; the handoff names source, tasks, approval, and review locations; sequencing defects return to this workflow's review gate; missing capability, stale/unverifiable approval, ambiguous scope, or an EPIC-sized route stops or asks for the owner's route decision; the coordinator still performs its own preflight and agent/model selection.
  - **Capability needs**: local file editing, repository search, deterministic test runner, suite static lint; documented `ask_user`, memory, and coordinator capability checks.
  - **Model class**: sonnet-class.
  - **Rationale**: it adapts a settled design into one skill and explicit handoff contracts after its dependencies exist.

### Routing and validation

- [ ] T007 [Documentation and direct-task routing] Update suite-facing documentation, discovery probes, and direct-task entry-point guidance to describe the implemented Requirements Manager and its approved handoff route accurately.
  - **Depends**: T002, T004, T005, T006.
  - **Likely files/interfaces / narrow write scope**: modify only behaviorally affected documentation/routing surfaces among `README.md`, `REQUIREMENTS.md`, `docs/index.md`, `skills/create-epic/SKILL.md`, `skills/install-memory/SKILL.md`, `skills/initialize-documentation/SKILL.md`, and `scripts/probe-pi-load.sh`; add each new skill to discovery checks where the current script uses an explicit required list, and reconcile stale entries in that list (for example `use-railway`, which no longer exists in `skills/`) so the probe fails only on real regressions. Preserve unrelated instructions, prior `docs/index.md` entries (including the implementation-plans entry for `requirements-manager.md` and the T002 coverage entry), and dynamic installer discovery.
  - **Acceptance evidence/checks**: user-facing workflow distinguishes EPIC/SpecKit from Requirements Manager direct requirements and shows that an owner-authorized direct task list can enter `coordinate-implementation`; `create-epic` and documentation initialization route applicable direct work without falsely stopping coordinator access; requirements/model-class language remains provider-neutral and keeps stage classes distinct from implementation complexity classes; index and probe discovery include each new skill without running the paid probe unless separately authorized; documentation describes the delivered behavior (including the conditional clarification stage and the restored stage chain) rather than the pre-change workflow; the updated material explains skill installation/discovery and reminds the owner to run `/reload` inside pi; cross-links and sample fresh-session handoff fields match actual authorization requirements; static lint and no-model discovery validation pass.
  - **Capability needs**: local file editing, repository search, shell static checks; no installer run or paid probe unless separately authorized.
  - **Model class**: sonnet-class.
  - **Rationale**: documentation and discovery changes are bounded once final skill contracts are available.

- [ ] T008 [Workflow regression suite] Add deterministic normal-validation workflow-contract coverage for the shared skills, restored EPIC stages, Requirements Manager, and coordinator execution rules without model calls.
  - **Depends**: T004, T005, T006.
  - **Likely files/interfaces / narrow write scope**: add focused tests and a documented normal validation entry point adjacent to the existing skill scripts/tests; modify only test wiring required to run them with routine suite validation. Keep skill prose authoritative; do not introduce an independent manifest that can drift.
  - **Acceptance evidence/checks**: normal validation runs the new suite; valid frontmatter/discoverability/resolvable files are asserted; **each EPIC stage check resolves that stage's operational instruction section and its required operational elements (entry condition, inputs, outputs, class assignment, gate/approval behavior, resume behavior), so stages present only in the architecture diagram or as a bare name do not satisfy the check**; gate skip and conditional brainstorm transitions are asserted as transitions, not as words; fixed future stage classes are asserted where they appear in stage instructions; create-only task creation, overall-review ownership of corrections, EPIC spec/plan approvals, stale-approval handling, and specification-approval renewal are asserted; capability checks and their `UNAVAILABLE` stop/fallback wording are asserted, including delegation, question-with-prose-fallback, model-class binding resolution with owner selection, and SpecKit stage detection; lightweight intake permits requirement/tasks without a plan or SpecKit and no direct-input path requires a plan; one downstream execution graph, 14/15 threshold, resume strategy retention, single-class and mixed-class session behavior, checkpoint/agent-launch independence, independent review, and commit rules are asserted; negative assertions confirm no OpenCode paths/command files, provider or agent IDs, rigid JSON state schema, or second batching algorithm appear; EPIC stage classes and implementation complexity classes are asserted as distinct concepts; no test makes a live model call, and the suite reports that it proves prompt-contract conformance only, not runtime model obedience.
  - **Capability needs**: local file editing, Python 3/test runner, shell validation, suite static lint.
  - **Model class**: sonnet-class.
  - **Rationale**: deterministic text/contract assertions are mechanically bounded and directly enforce the settled policy.

- [ ] T009 [Mutation coverage] Add in-memory mutation tests that prove the workflow-contract checkers fail when each essential guardrail or operational instruction is removed or contradicted.
  - **Depends**: T008.
  - **Likely files/interfaces / narrow write scope**: modify only the workflow-contract test suite and its fixtures/helpers. Do not mutate repository source files during test execution or add runtime behavior.
  - **Acceptance evidence/checks**: each mutation operates on an in-memory copy and produces a **named checker failure** (not merely a changed exit code or an error count): deleting a stage's operational instruction body while leaving its name in the pipeline diagram; deleting a stage's model-class assignment while the diagram stays intact; deleting the gate skip transition or the conditional brainstorm→fix→spec transition text; deleting create-only wording so the tasks stage self-critiques; deleting capability `UNAVAILABLE` stop text; deleting stale-approval or specification-approval-renewal wording; reducing the shared-primitive invocation to an unrelated mention of the skill name; removing the small-list session policy; reinstating mandatory-plan wording for direct inputs; changing the 15-task boundary; permitting class-based dependency reordering; removing independent review; reintroducing a legacy token (provider ID, agent name, or OpenCode path); all run through the same normal validation entry point and report the limitation that prompt-contract tests cannot prove model obedience.
  - **Capability needs**: local file editing, Python 3/test runner, shell validation.
  - **Model class**: sonnet-class.
  - **Rationale**: isolated test-fixture work provides strong regression evidence without broad production changes.

- [ ] T010 [Integration and acceptance evidence] Run the approved static regression set and scenario walkthroughs, complete the T002 matrix's evidence column, repair only demonstrated integration/wiring defects within this approved scope, and record final verification plus independent-review availability for owner approval.
  - **Depends**: T002, T007, T009.
  - **Likely files/interfaces / narrow write scope**: amend only affected workflow tests, validation wiring, documentation introduced by T001–T009, and `docs/plans/requirements-manager-coverage.md`; record evidence in the project's established artifact convention or the task artifact if none exists. Within this task only: do not implement product features, install dependencies, run paid delegates or the paid probe, commit, or authorize execution. These limits do **not** constrain the later owner-authorized implementation stage (see §Scope of the exclusions in this artifact).
  - **Acceptance evidence/checks**: `scripts/check-skills-lint.sh`, the shared validator unit tests, the workflow-contract/mutation suite, `check-task-order.py` on this artifact, and `git diff --check` have recorded outcomes; every T002 matrix row has its evidence status set to verified/missing and any `removed-unaccounted` or mismatched row is reported as a blocker rather than silently reclassified; focused walkthroughs — recorded as **static prompt/contract walkthroughs** with that limitation stated, never as behaviour proof — cover each design scenario (well-specified direct work; 14 one-class and 14 mixed-class; 15 and resumed large list; context pressure or broad conflicting scope; unavailable resumption or implementation failure; commit-policy conflict; material product/technical uncertainty; EPIC-sized route decision; stale approval or ambiguous origin; no SpecKit and installed SpecKit with direct input; forward dependency; unavailable delegation/model/question capability; over-30% class share; handoff after requirement/task edits); documentation behavior is checked against implemented contracts; unavailable capabilities are reported as `UNAVAILABLE`, never `PASS`; independent overall review of the delivered work is requested through T011 or reported `UNAVAILABLE` with the missing capability named.
  - **Capability needs**: local shell/Python tests, repository diff inspection; no external service required for static evidence.
  - **Model class**: sonnet-class.
  - **Rationale**: final integration is bounded to observed wiring defects and produces the evidence needed for a separate approval gate.

- [ ] T011 [Independent semantic diff review] Obtain an independent semantic review of the delivered diff against the original owner request, the historical EPIC contract, current protections, and the T002 matrix/inventory.
  - **Depends**: T010.
  - **Likely files/interfaces / narrow write scope**: review is read-only unless the owner authorizes changes; record findings and dispositions durably in `docs/plans/requirements-manager-coverage.md` or the task artifact. Do not implement fixes here; confirmed defects return to the producing task's review gate under the owner's authorization.
  - **Reviewer independence**: the reviewer session must not have produced any T001–T010 change, and must not be a class-resumed implementation session; the class below governs the reviewer model binding, while the concrete agent/model remains an owner selection from observed permitted options at coordinator preflight. If no permitted reviewer is available, report `Independent review: UNAVAILABLE` with the missing capability and record the blocker instead of self-reviewing.
  - **Required inputs**: the implementation diff (not a summary); the original owner request and authoritative scope as preserved in the design plan and handoff; `32e12feb382a6a0acb7e9d7f2e82559e3d397f2e:skills/epics-manager/SKILL.md`; the current protections in `skills/epics-manager/SKILL.md`, `skills/coordinate-implementation/SKILL.md`, `skills/create-epic/SKILL.md`, `REQUIREMENTS.md`, and the current scripts/tests; the T002 matrix, behavior inventory, and capability inventory; and the review contract in `skills/requesting-code-review/code-reviewer.md`.
  - **Acceptance evidence/checks**: every matrix row and every restored EPIC stage is classified as preserved, changed, removed-deliberate, or absent, and each `absent`/`removed-unaccounted` item is reported as a finding with severity and `file:line`; the review states specifically whether EPIC stages or operational instructions were deleted, weakened, or left as diagram-only text relative to the historical contract and the owner's scope; capability checks/fallbacks, approval/provenance protections, the stage-class versus implementation-class distinction, single-strategy execution selection, the 15-task boundary, and the no-parallel-batches rule are each explicitly assessed; findings carry severity, precise location, impact, and suggested correction; the verdict is ready / ready with stated follow-up / not ready; verification gaps and open questions are listed; each finding receives a disposition per `skills/receiving-code-review/SKILL.md`; the review states that it assessed prompt and diff semantics only and does not prove runtime model behavior; any failure to obtain the review is reported honestly rather than replaced by re-running the checks.
  - **Capability needs**: an independent permitted reviewer binding, repository diff and file inspection, durable note-taking.
  - **Model class**: opus-class (critique-stage judgment, flagged for the owner: semantic diff review against a historical contract is judgment-heavy and cannot be safely decomposed; if the owner prefers the observed reviewer binding's own class instead, this becomes `sonnet-class` and the `opus-class` share drops to 1 of 11).
  - **Rationale**: catching silently deleted or weakened pipeline stages requires comparing intent across three artifact generations, which is exactly the judgment-heavy case where a wrong verdict is costly and hard to detect afterwards.

## Requirement coverage matrix requirement

T002 must produce `docs/plans/requirements-manager-coverage.md` with the columns and derivations listed in T002, and
T010 must complete its evidence column before this artifact can be presented to the owner as verification-complete.
The matrix is a durable repository artifact so a later session can re-verify coverage without re-deriving the
historical baseline.

## Coverage and verification checklist

- [x] Historical brainstorming extraction, shared task semantics, and one validator/test implementation: T001, T003.
- [x] Durable requirement-to-implementation/test matrix, preserved/changed/removed behavior inventory, and capability/fallback inventory derived from the original request, historical EPIC, and current protections: T002, verified in T010, reviewed in T011.
- [x] Restored executable EPIC stages with operational instruction sections and fixed **future workflow stage** classes: T004.
- [x] Origin-specific coordinator gates with one graph, 14/15 boundary, class-session reuse without dependency regrouping, no parallel batches, independent review, and commit policy: T005.
- [x] Plan-free Requirements Manager and durable direct-task authorization/handoff: T006.
- [x] Documentation, direct-task routing, discovery, reload guidance, and adoption-facing references: T007.
- [x] Routine deterministic contract regression and mutation coverage that fails on missing operational instructions: T008–T009.
- [x] Static integration evidence, scenario matrix, and matrix completion: T010.
- [x] Independent semantic diff review against the original request, historical EPIC, current protections, and the matrix: T011.
- [x] Honest capability/fallback reporting and no claim that static text tests prove model behavior: T008, T010, T011.

## Review concerns for the independent overall review (this task artifact)

1. Confirm direct-task routing language never accidentally permits task-only implementation without current durable review/owner authorization.
2. Compare the restored EPIC wording to the historical source for brainstorming, reading-contract, flagged-item, handoff, resume, and `done` behavior while ensuring no obsolete OpenCode paths, fixed project paths, rigid state file, agent names, or provider IDs return.
3. Inspect coordinator prose for a single strategy-selection and batching implementation; specifically reject plan-presence/origin/remaining-count selection and class regrouping across prerequisites.
4. Check that the 15-task boundary preserves existing large-list batching, that a context-pressure exception is evidence-recorded rather than a loophole, and that parallel batches remain prohibited.
5. Verify tests are actually wired into normal validation, that mutation tests mutate copies, that stage checks resolve operational sections rather than diagram tokens, and that docs describe the implementation rather than the pre-change workflow.
6. Confirm T002's matrix was drafted from the named sources before the rewritten prompts and that it maps every owner-scope sentence and historical behavior to a task and a check.

## Scope of the exclusions in this artifact

The exclusions below bind **this critique/task-production stage** and the execution of the listed tasks **before** the
owner grants implementation authorization. They do not forbid, and must not be read as forbidding, owner-authorized
implementation-stage actions: mandatory delegation to the selected agents, the owner-approved single focused
implementation commit before independent review (subject to project policy and explicit owner exceptions), the
review-fix commit, per-batch commits for lists of 15 or more tasks, or the T011 independent review delegation. Where
a task bullet says "do not delegate/commit/authorize execution" it constrains that task's own actions, not the
authorized implementation stage that follows owner approval.

These tasks implement only the approved suite-workflow design. They exclude product implementation, a duplicate
origin-specific batching algorithm, parallel-batch policy, SpecKit replacement, EPIC sizing redesign, global project
state schema, runtime package upgrades, obsolete platform commands, and retroactive conversion of unrelated task
artifacts.

## Handoff context: decisions/rationale, exclusions/deferrals, fragile areas for independent overall review, and non-obvious context

- **Decisions/rationale:** The approved seven-package dependency shape is preserved, with deterministic coverage
  (T002), validation (T008), mutation (T009), acceptance (T010), and the previously implicit independent review
  (T011) separated so each has narrow evidence. T005 is the sole producer-side `opus-class` task because it is the
  authorization/execution contract; T011's `opus-class` is a critique-stage judgment (F13) flagged for the owner.
  The `opus-class` share is 18.2% of 11 tasks. Future fixed EPIC stage assignments remain distinct from these
  implementation complexity classes.
- **Exclusions/deferrals:** No implementation, install, commit, delegation, provider/model binding, SpecKit
  emulation, global schema, or second batching path is included in the pre-approval scope; see §Scope of the
  exclusions in this artifact for what is deliberately *not* prohibited after owner authorization. Live
  model/runtime trials remain unavailable unless a later owner authorizes applicable capabilities.
- **Fragile areas:** Direct requirements must retain a durable review/authorization trail despite intentionally
  lacking spec/plan artifacts. Prose contracts, deterministic tests, and the T002 matrix must stay aligned; test
  success cannot prove a model's runtime obedience. T011's reviewer availability is unknown. The plan's
  seven-task small-list schedule is illustrative; the approved count is now 11 tasks across two classes, so the
  coordinator must derive the real schedule from the approved count. Existing dirty `docs/index.md` and
  `docs/plans/requirements-manager.md` must be preserved during implementation.
- **Non-obvious context:** The current validator recognizes only numbered Markdown checklist tasks plus an
  immediately following explicit `**Depends**` field, so this artifact keeps that syntax. The current installer
  discovers skills dynamically, but `scripts/probe-pi-load.sh` has an explicit `REQUIRED` list (and currently names
  `use-railway`, which no longer exists) that T007 must reconcile with the actual skills. `skills/epics-manager/SKILL.md`
  still points at `scripts/check-task-order.py` relative to its own directory, so T003's relocation must update that
  reference.
