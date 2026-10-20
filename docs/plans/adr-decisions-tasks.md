# ADR decisions — Terra-sized implementation tasks (planning only)

**PLANNING ONLY. Implementation STOP.** Parent review and combined source/task approval
remain pending; even approval does not release the owner's separate implementation go-ahead.

Requirements truth: [TinySpec](adr-decisions-tinyspec.md), revised source checkpoint
`4207aba5461c8c400b99f1c85516a3e0ac3db2c3`. The source-stage “no tasks” restriction is
historical; the owner subsequently authorized task production and this targeted correction.
No SDD is direct task input. **Sol/medium is the planning profile. Terra/medium is the owner's
intended implementation family/effort and task-sizing constraint.** Exact provider/model and
usable runtime configuration remain for later explicit selection/preflight; no version,
launch authority or silent binding substitution is inferred.

[Executable handoff](adr-decisions-tasks.json) carries the same eleven outcomes/dependencies,
explicit owned paths, consumed interfaces, local completion oracles and permission boundaries.
`acceptance` contains REQUIRED check/pass/evidence context; `checks` contains only executable
argv arrays, not prose shell commands. These optional fields add no task-startup eligibility
rules. Relevant source constraints must reach each actual worker brief, not only the wrapper.

## Ordered outcomes

- [ ] T001 Deliver the canonical portable save-adr authority/history contract.
  - **Depends**: none
  - Own `skills/save-adr/SKILL.md`; consume existing project decision/routing conventions
    and writing-skills. One coherent skill owns save/consult/propagate once.
  - **REQUIRED A1/A2**: frontmatter, portability and links plus bounded custom/absent/
    ambiguous owner, repeat-save and authority/history scenarios. Evidence shows equivalent
    format reuse, honest status/provenance, retained rationale and navigable supersession,
    distinct acceptance/implementation, affected-only stops and no implementation permission.
    Local completion needs no downstream consumer or actual project store creation.

- [ ] T002 Route approved consequential decisions at closeout without replacing duties.
  - **Depends**: T001
  - Own finish-session and its Jev adapter only if needed; consume T001's save trigger.
  - **REQUIRED A3**: approved-decision versus ordinary-session/inferred-lesson routing
    observations and introduced links. Existing primary-artifact, current-doc/schema/runbook,
    issue, memory, explicit-feedback and validation duties survive; Jev stays optional/manual.
    No backfill/fabricated acceptance; locally complete without other consumers.

- [ ] T003 Deliver approval-bound adoption/refresh owner discovery and managed consultation.
  - **Depends**: T001
  - Own initialize-coherence's contract, existing contract test and scenarios fixture;
    consume T001 and existing approval/managed-diff interfaces.
  - **REQUIRED A4**: extend/run existing initialization fixtures and inspect managed-diff
    expectations for adoption, approved refresh/custom owner, unchanged repeat, denial,
    dirty overlap and drift. Whole-index/relevant-accepted consultation reaches managed
    instructions only through approved adoption/refresh. Preserve customization; no incidental
    refresh, unapproved/global store or absent-store-only legacy startup veto. No actual
    project adoption is needed for local completion.

- [ ] T004 Preserve accepted constraints in planner orchestration and stage briefs.
  - **Depends**: T001
  - Own planner plus focused existing planner check/test assertions; consume T001 and
    Discovery, Selected production/stage handoffs and Handoff interfaces.
  - **REQUIRED A5 orchestration**: supplied accepted constraints reach direct/delegated
    TinySpec/Standard producer/review briefs and handoff in fresh/resumed contexts.
    Read-only preselection and existing gates remain. Existing fixtures/checks expose a
    missing carrier; completion checks planner's output contract, not downstream obedience.

- [ ] T005 Preserve accepted constraints through the source-to-task acceptance adapter.
  - **Depends**: T001
  - Own tiny-spec, task-generation and focused existing planner check/test assertions;
    consume T001, source acceptance and both direct/SpecKit task adapters.
  - **REQUIRED A5 adapter**: a fixture's relevant accepted outcome affects source acceptance
    then task dependency/REQUIRED check/brief; exercise both adapters and direct/fresh/resumed
    entry. Check a concrete observable-to-task mapping, not only a link. Complete with supplied
    source fixtures and T001, without waiting for orchestration, helpers or runtime.

- [ ] T006 Preserve accepted constraints in standalone brainstorming gate/handoff/resume.
  - **Depends**: T001
  - Own planning-brainstorming and focused assertions in existing planner tests; consume
    T001 and brainstorming's preselection versus selected-production modes.
  - **REQUIRED A5 brainstorming**: accepted constraints inform direct/helper gate assessment
    and survive dialogue handoff/resume; mode-specific observations and fixture assertions
    detect omission. Preselection remains read-only, with no new stage or durable artifact.
    Completion does not require the architectural helper or live dialogue.

- [ ] T007 Preserve accepted constraints in standalone architectural planning briefs.
  - **Depends**: T001
  - Own delegating-architectural-planning and focused existing planner test assertions;
    consume T001 and approved-spec/plan-request preflight/delegation interfaces.
  - **REQUIRED A5 architecture**: direct/manager and fresh/resumed brief expectations retain
    exact accepted constraints/links and existing SpecKit, research, binding and approval
    renewal stops. Verify the local contract with supplied records; do not invoke SpecKit,
    rewrite a specification or wait for downstream task/runtime implementation.

- [ ] T008 Preserve direct/fresh/resumed implementation handoff constraints in the skill.
  - **Depends**: T001
  - Own coordinate-implementation and focused existing planner test assertions; consume
    T001 and Load/Verify, Recover Context, Execute/Integrate and Review brief interfaces.
  - **REQUIRED A5 execution skill**: local worker/review brief observations and assertions
    carry known accepted constraints/links without prior-read claims. Keep six intake checks,
    ordinary errors, ownership, context-first recovery and independent review unchanged.
    Completion is skill-local; executable prompts are explicitly excluded and owned by T010.

- [ ] T009 Preserve accepted constraints in the paired review-request/reviewer contract.
  - **Depends**: T001
  - Own requesting-code-review, its code-reviewer contract and focused existing planner
    test assertions; consume T001 and review Inputs/Review Focus interfaces.
  - **REQUIRED A5 review skill**: trace a request constraint into direct/fresh/resumed
    reviewer scope and compare representative actual simplification/deletion diffs using
    supplied records. Detect either missing carrier; preserve fresh independent read-only
    review. Locally complete without engine changes or a live review invocation.

- [ ] T010 Wire the existing engine worker and final-review prompt discovery instructions.
  - **Depends**: T001
  - Own only engine.py prompt text and test_engine.py captures; consume T001 and existing
    Engine.invoke task/range/diff prompt interfaces. Reviewer skills remain disabled.
  - **REQUIRED A5 runtime**: actual captured worker and read-only reviewer prompts contain
    usable canonical-contract discovery/accepted-constraint instructions, including file
    reads despite disabled reviewer skills. Extend/run existing offline engine tests with
    `PYTHONPATH=runtime:runtime/tests`; retain independence/read-only assertions. Skill
    consumer changes are not prerequisites for this local emitted-prompt oracle.
  - **Real boundary**: implementation waits for current running work to finish and a fresh
    sole-writer/path ownership inspection. Never recursively execute through the runtime
    being edited. No host, intake, sessions/recovery, SQL/state or configuration changes.

- [ ] T011 Publish bounded discovery/managed instructions with composed continuity evidence.
  - **Depends**: T002, T003, T004, T005, T006, T007, T008, T009, T010
  - Own only marked local AGENTS consultation instructions, docs/index routing, necessary
    README discovery/workflow text, plans index source/task entries and reviews index links
    to actual authorized review artifacts. Consume delivered consumers and their evidence.
  - **REQUIRED A6**: introduced links/sections and actual owned/full-range diffs agree with
    delivered behavior. Compose a representative source/task/brief → emitted worker prompt
    → review-scope trace once all consumers exist, reusing applicable A1–A5 evidence.
    This acceptance stays with substantive docs delivery, not a verification-only task.
    Focus-checkpoint docs before the existing final fresh independent read-only full-range
    implementation review; completion never substitutes a generic green suite for evidence.

## Sizing rationale and shared authority

The old planning milestone is now orchestration (brief output), source-to-task acceptance
adapter, brainstorming (read-only gate/dialogue) and architecture (approved-spec delegated
plan) consumer contracts. The latter two have distinct authority/mode boundaries and can be
finished independently. TinySpec/task-generation remain together only for their bounded
source-acceptance → task-check mapping; they do not own orchestration or helper contracts.
The old execution milestone is now implementation-skill handoff, paired review-request/
reviewer interface, and actual runtime prompt wiring/captures. Reviewer files remain paired
because request scope must agree with reviewer inputs. Both engine prompts remain together
because one existing capturing adapter observes this bounded runtime instruction interface.
Canonical skill, closeout and adoption remain coherent separate outcomes. No split is merely
a file quota; each Terra/medium assignment has its own usable predecessor and local oracle.

Only genuine producer reliance is encoded. All thin consumers depend on T001, not each other;
shared test-file ownership requires sequential fresh inspection, not invented dependencies.
T011 needs all consumer contracts to publish accurate discovery and compose their evidence.
Every task keeps its tests, relevant local docs, actual evidence and focused explicit-owned-path
checkpoint together. Preserve unrelated dirty/staged/concurrent work, hooks/signing and history;
stop on same-path ownership drift. No parallel implementation writers are authorized.

The canonical authority cases apply at relevant A5 consumer checks without repeating a full
scenario matrix per consumer: accepted capability removal needs explicit approved supersession
through existing gates; compatible helper deletion needs no new gate; an explicitly accepted
mechanism stays binding. Proposed/superseded records are not current policy; contradictory
accepted authority needs a material owner decision before affected conflicting continuation.
Saving a decision never grants implementation authority. Re-establish fresh/resumed applicability
by the whole index, relevant accepted ADRs in full and needed supersession links, not read
receipts. Known accepted constraints survive packaging gaps. Missing/unreadable/conflicting
ownership blocks only affected writes/decision-dependent operations with a concrete remedy;
missing storage alone must not veto unrelated legacy work.

General repository ADR ownership/path remains **unselected and unauthorized**: propose/confirm
it at an actual future save/adoption boundary. No store creation/backfill is tasked. Preserve
specs/reference/operational owners; any actual constitutional conflict returns through Governance,
not an incidental amendment. T011's bounded existing-file changes await approved implementation
scope; no shared index, source, AGENTS, skill or runtime is edited by this task correction.

No prototype, new framework/dependency/install, mandatory live/provider evaluation, metadata
registry/read attestation/receipt, unrelated permission/cache/resume repair, settings/memory/STATE
write, fleet migration, running-workflow edit or host redesign. Static/scenario/fixture PASS is
instruction/prompt-wiring evidence, **not model obedience**. Future feature checks are NOT RUN
in planning. Paseo activation later uses a fresh-session checkout/capability-verification handoff,
not /reload or automatic restart. Parent review, combined approval and the separate implementation
STOP remain after this focused planning checkpoint.
