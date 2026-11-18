# Skill simplification — sequential delegation plan

## Status and source

Plan preparation requested by the owner after the Astra/medium read-only critique of the
nine-skill simplification proposal. Execution has not been authorized by this plan-writing
request. This is an instruction-managed sequential delegation plan, not a workflow-runner
launch or a change to saved planner/executor assignments.

Starting implementation candidate: `0edff879a6368320df0506086daa70b954806d2f`.
Related delivery: https://github.com/elsonidoq/skills/issues/44.
This plan neither renews that delivery's acceptance nor authorizes tracker writes.

## Outcome and limits

Simplify only these nine skills: task-generation, planning-brainstorming, tiny-spec,
delegating-architectural-planning, planner, finish-session, track-open-issue, writing-skills
and handoff-prompt. Make each skill's job and input → action → output clear. Remove
repetition and delegate detailed procedures to existing authoritative owners. Do not
merely move paragraphs into reference files or add a new shared-policy subsystem.

Preserve behavior: planning depth choice, source authority, producer/reviewer separation,
independent reviews, current-content approvals, real permission gates, scoped routine
repair authority, recovery, and focused task commits. Preserve standalone entry where it
exists. Do not remove stages, reviews, approvals, required checks, or existing guarantees.

Accepted constraints:
- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md): task
  instructions remain authorization-neutral; historical preparation labels do not override
  current scoped launch authority.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md): routine scoped
  fixes and isolated checks do not require repeated approval; actual manual, paid, data,
  security and external-operation boundaries remain.
- [Task checkpoint owner](../../skills/memory-handling/references/task-commit-contract.md):
  each retained implementation/repair task is verified and committed on explicit owned
  paths before the next task. Preserve unrelated tracked and untracked work.

Do not change runtime code, model assignments, global links/configuration, Railway, Cerca,
main, historical plans/approvals, or the other 15 skills. No merge, push, installation,
service operation, tracker mutation, or live model/application trial is included.
Supporting test and direct caller/reference repairs are permitted only as specified below.
A genuine behavior conflict returns to the owner; do not call a behavior change compression.

## Execution method

- Delegate each numbered step to one fresh **Astra/medium** agent
  (`openai-codex/gpt-6-astra:medium`), as requested by the owner. No parallel workers.
  Step S10 uses a fresh read-only reviewer, independent of all authors.
- Use bounded asynchronous native subagent calls. Return control while a child runs;
  completion wakes the coordinator. Children do not delegate or launch the workflow CLI.
- Before each launch, supply the current baseline, owned paths, this plan, relevant
  accepted constraints, predecessor outputs, check results and unresolved issues. Verify
  the selected model and role are usable; do not silently substitute another model.
- Each author reads its complete skill and the existing canonical owners needed for its
  change. Keep anchors where practical. Existing references must specify when they apply
  and the result the caller consumes, not just say "follow related skills."
- One author owns its skill and directly coupled validation during that step. Shared
  check scripts can be edited by successive authors, never concurrently. No separate
  late test-repair phase: validate and checkpoint each skill before continuing.
- The coordinator inspects each returned diff, checks, commit and residual owned changes
  before releasing the next step. On failure inspect the existing invocation and retained
  work before targeted recovery; do not blindly relaunch an expensive failed call.
- Each return includes baseline/result SHA, changed paths, before/after skill line counts,
  rules removed or consolidated, checks and their limits, and unresolved matters. Keep
  these in the normal task/session return, not new repository ledgers.

### Supporting-path boundary

Each step may update `scripts/check-planner-workflow.py` and
`scripts/test-planner-workflow.py` only where its own simplification invalidates an
assertion or requires coverage. Preserve tested behavior; replace repeated-sentence
requirements with owner invocation, output consumption and stage-order checks.
Do not delete a failing test merely to obtain green results.

Other supporting files are listed per step. Inspect actual callers before changing an
anchor. If an unlisted file needs a substantive change, return its path, reason and exact
proposed scope for coordinator assessment before editing; ordinary scoped reference repair
is not permission to rewrite another skill. Do not rewrite canonical memory, ADR, research,
risk or checkpoint contracts, and do not enlarge review prompts with deleted planner text.

## Sequential tasks

### S01 — Simplify task-generation

**Depends on:** none. **Primary path:** `skills/task-generation/SKILL.md`.
**Coupled paths:** `skills/task-generation/scripts/test_contract.py`, plus the shared
check scripts above where affected. The task-order implementation stays unchanged.

- State common inputs, preparation authority, source authority and constraint propagation
  once; describe only real differences between direct and SpecKit adapters.
- Keep selected-executor reading here as the task-sizing owner. Preserve supplied paths
  and forbid silent assignment substitution.
- Merge repeated outcome sizing, supporting ownership, dependency and acceptance guidance.
  Condense examples while retaining the distinction between a milestone, an independent
  slice and ordinary established cross-system wiring.
- Keep prototype placement/markers but reference the existing early-risk owner for its
  detailed lifecycle. Keep authorization-neutral tasks and six-check executable intake.
- Outline: inputs/adapters → executor/outcome sizing → acceptance/dependencies → executable
  format → review/return.

**Verify:** run the task contract and task-order tests; run planner checks affected by the
edit. Inspect example independent-slice, wiring and prerequisite tasks. Confirm optional
fields remain optional and the `authorization-neutral-tasks` anchor still resolves.
**Return:** a shorter task-semantics owner with unchanged executable format and guarantees.

### S02 — Simplify planning-brainstorming

**Depends on:** S01. **Primary path:** `skills/planning-brainstorming/SKILL.md`.
**Coupled paths:** `skills/planning-brainstorming/scripts/test_contract.py` and affected
shared check scripts.

- Merge capability inputs and modes. Keep parent-led readiness assessment and dialogue.
- Keep the two gate outcomes, bias against unnecessary dialogue, existing agenda bounds,
  read-only preselection and explicit decisions/deferrals.
- Reference saved assignments and ADR/memory owners instead of copying their procedures.
- Combine decision application, return and resume; remove downstream task mechanics.
- Outline: inputs/modes → readiness → dialogue → bounded application/return → resume.

**Verify:** its contract tests and affected planner checks. Walk settled-request,
material-question, cancelled-answer and changed-source resume cases. No inferred answer
or automatic depth choice may appear.
**Return:** readiness and actual owner decisions for the calling planner, not artifacts
or implementation authority created during preselection.

### S03 — Simplify tiny-spec

**Depends on:** S02. **Primary path:** `skills/tiny-spec/SKILL.md`.
**Coupled paths:** affected shared check scripts only.

- Consolidate inputs and call canonical memory, decision, research and risk owners once
  at the relevant boundary, retaining the source-specific result each must provide.
- Keep the source contents: outcome, scope, constraints/decisions, approach, observable
  acceptance, risks/deferrals and provenance.
- Remove task-schema explanations; carry the selected executor path to task-generation.
- Keep the optional issue reference and one concise source-return contract.
- Outline: inputs/authority → evidence → source contents → return/review boundary.

**Verify:** affected planner checks and changed references. Inspect a bounded source and
one unresolved consequential dependency. Preserve separate tasks, independent source
review, standalone preparation authority, and no SpecKit prerequisite or extra TinySpec
source approval.
**Return:** a compact authoritative source producer, not a second task/planner manual.

### S04 — Simplify the architectural-planning adapter

**Depends on:** S03. **Primary path:**
`skills/delegating-architectural-planning/SKILL.md`.
**Coupled paths:** affected shared check scripts only.

- Combine common preflight with explicit managed/standalone entry differences.
- Name coordinating caller and delegated producer distinctly. Keep observed installed
  SpecKit capability and bounded artifact/research-document writes explicit.
- Replace copied research, memory, ADR and risk procedures with existing owner calls and
  the required plan-specific outputs. Leave task decomposition to task-generation.
- Keep one planning pass, source-change approval renewal and one correction/return block.
- Outline: entry modes → capability/write bounds → planning pass → decisions → return.

**Verify:** affected helper/planner checks. Walk managed, standalone and missing delegated
SpecKit cases. No generic Markdown fallback, duplicate plan creation or broader writes.
**Return:** checked plan and material decisions/risks to its caller.

### S05 — Simplify planner around the stable specialist interfaces

**Depends on:** S04. **Primary path:** `skills/planner/SKILL.md`.
**Coupled paths:** shared check scripts; conditional anchor-only repairs in
`skills/planner/references/model-assignments.md`, `approval-and-recovery.md`,
`spec-review.md` and `simplicity-review.md` when an actual caller requires them.

- Keep orchestration, not specialist authoring: understanding, depth choice, stage
  dispatch, inspection, independent review, current-content approval and handoff.
- Merge discovery/roles/assignments into compact preparation and dispatch guidance.
- Remove repeated memory, ADR, research, proof, task-sizing and recovery procedures;
  state the invocation boundary and output consumed from each existing owner.
- Replace long TinySpec/Standard paths with stage tables: input, producer, output, gate.
- Keep shared briefing rules once. Keep reviewer assessment instructions in existing
  review prompts, without transferring deleted prose into those prompts.
- Preserve source review, parent simplicity assessment, parallel independent final reviews,
  waiting for both reports before correction, saved bindings and exact approval sequence.
- Outline: purpose → understand/choose depth → dispatch → path tables → reviews/corrections
  → approval/recovery/handoff.

**Verify:** planner checker and regression script; changed anchors/callers. Walk settled
TinySpec and Standard with a changed approved specification. Verify authorized continuation
and planning-only handoff remain distinct. Check that ordinary planning loads less repeated
instruction text, not merely a shorter main file plus larger references.
**Return:** the compact stage coordinator with preserved behavior and clearer handoffs.

### S06 — Simplify finish-session and establish delivery-content ownership

**Depends on:** S05. **Primary path:** `skills/finish-session/SKILL.md`.
**Coupled paths:** affected shared check scripts. Preserve Jev's candidate-before-write
insertion point and existing published anchors so its consumer need not change.

- Consolidate discovery and safety without weakening the existing initialization gate.
- Keep one durable-information routing table; project routing supplies concrete owners.
- Replace copied memory/tracker procedures with calls and required return information.
- Keep deployment and worktree-removal branches conditional, with unknowns explicit.
- Own delivery meaning: result, exact reviewed revision, evidence/limits, corrections
  and acceptance status. Leave tracker mutation/reconciliation/readback to its owner.
- Combine final reporting instructions without requiring inapplicable bookkeeping.
- Outline: entry/authority → attributable findings → routing → conditional branches →
  delivery/report.

**Verify:** affected delivery/planner checks and references. Walk no-op closeout, missing
tracker authority, partial publication and requested worktree removal. Keep the existing
`issue-linked-delivery` and `worktree-removal-readiness-only-when-requested` anchors.
**Return:** canonical delivery-content contract ready for S07; no implementation reruns,
new acceptance gate, automatic archive or inferred owner acceptance.

### S07 — Simplify track-open-issue against the delivery contract

**Depends on:** S06. **Primary path:** `skills/track-open-issue/SKILL.md`.
**Coupled paths:** `skills/track-open-issue/scripts/test_contract.py` and affected shared
check scripts. Its assessment and closeout consumers remain otherwise unchanged.

- Separate candidate recording, scoped existing-issue changes and delivery operations.
  Delivery comments do not require a fresh problem-investigation cycle.
- Keep the declared-local-owner branch and explicit GitHub target/authority boundary.
- Consolidate candidate body requirements and mutation/readback/reconciliation guidance.
- Replace duplicated delivery prose with S06's content contract; keep the local closure
  guard requiring revision-specific acceptance and actual closure authority.
- Preserve full overlap discovery, autonomous-issue labeling, human-content protection,
  separate issue-body quality review and its bounded correction route.
- Outline: operation/input → owner/authority → candidate discovery → mutation/readback →
  applicable quality review → result.

**Verify:** tracker contract and affected planner/delivery checks. Walk uncertain create,
concurrent body edit, delivery comment and acceptance without closure authority. No live
GitHub write is included or needed for this prose-only refactor.
**Return:** one tracker-effects owner, with separate mutation/readback and review outcomes.

### S08 — Amend writing-skills without adding process machinery

**Depends on:** S07. **Primary path:** `skills/writing-skills/SKILL.md`.
**Coupled paths:** affected existing shared checks only if necessary.

- Amend the existing authoring recipe to state trigger, responsibility, inputs, actions,
  output/consumer and authority boundary clearly; do not mandate identical headings.
- Require removing duplicated instructions rather than relocating them into references.
- Reconcile universal prior/candidate pressure-run wording with current proportionate
  validation policy; retain actual required behavior/safety checks.
- Keep portability, reusable-dependency availability/fallback, useful examples and the
  existing checkpoint owner. No new linter, score, size cap or reference library.

**Verify:** focused read-through against the revised planner and its specialist interfaces;
check references and the unchanged incorporate-skill consumer's authoring expectations.
**Return:** a small authoring-rule improvement, not a full redesign.

### S09 — Correct handoff-prompt's obsolete executable-continuation instructions

**Depends on:** S08. **Primary path:** `skills/handoff-prompt/SKILL.md`.
**Coupled paths:** affected existing shared checks only if necessary.

- Keep ground-truth discovery and the copyable prompt's optional sections.
- Replace only the obsolete executable-continuation protocol with observed run/status,
  unfinished work, authority, uncertain effects and the next supported action.
- Route recovery to the current coordinator and operating guide; preserve explicit
  compatible-runtime handling for historical runs.
- Remove universal receipt/envelope/nonce/resource-identity demands; retain identities
  genuinely needed for the selected operation and never fabricate template fields.

**Verify:** changed links/callers and relevant active-consumer checks. Inspect ordinary
fresh-session and interrupted-run handoffs. Preserve no blind restart, no invented consent,
no implicit delegation and no assumption that temporary artifacts survive another checkout.
**Return:** a usable continuation prompt contract aligned with existing execution owners.

### S10 — Fresh independent review of the nine-skill simplification

**Depends on:** S09. **Agent:** fresh read-only Astra/medium reviewer.
**Owned mutation paths:** none. Report through the native subagent output artifact.

- Review the actual cumulative diff and task commits against this plan, applicable accepted
  decisions, existing source contracts and original owner intent.
- Confirm only nine skills and necessary coupled support changed. Verify responsibility,
  input/output and authority remained complete; check standalone and resumed entry.
- Inspect duplication removed and normal loaded instructions, not just line counts. Flag
  reference-file inflation, lost guarantees, new ceremony and stale anchors/callers.
- Reuse valid per-step evidence. Run the cumulative planner checks, three affected skill
  contract suites and task-order tests as applicable to changed seams. No full runtime,
  live-provider, Railway or historical workflow replay is required by this editorial plan.
- Return examined coverage, actionable findings and remaining evidence limits. Any repair
  is a separate scoped Astra/medium correction with its own verified checkpoint, followed
  by independent review of the affected delta/interactions; do not launch repairs now.

**Completion:** resolved material findings, intact applicable checks and a concise owner
summary of changes, before/after sizes and behavioral limits. Static/fixture/manual
walkthrough evidence is not live model-obedience proof. Prepare a Paseo fresh-session
handoff for changed global assets; do not switch global links, reload/restart, activate the
Railway trial, merge or push. Owner acceptance remains separate from technical completion.

## Verification commands

Use an already available compatible Python environment; missing dependencies are an
observed setup issue, not permission to install globally. Run from the suite checkout:

```sh
python3 scripts/check-planner-workflow.py
python3 scripts/test-planner-workflow.py
python3 skills/task-generation/scripts/test_contract.py
python3 skills/task-generation/scripts/test_check_task_order.py
python3 skills/planning-brainstorming/scripts/test_contract.py
python3 skills/track-open-issue/scripts/test_contract.py
git diff --check
```

Each step runs the applicable commands, not every unrelated suite. Record exact failures
and distinguish pre-existing failures from introduced ones. Preserve tests for real behavior;
change obsolete copied-text assertions together with their skill. No arbitrary reduction
quota: success is a smaller, clearer contract with less repeated context, not fewer lines
achieved through omission or relocation.
