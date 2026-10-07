# Early isolated technical risk reduction — implementation tasks

## Source, status and shared context

Authoritative source: [TinySpec](early-risk-reduction-tinyspec.md), R1–R5 and AC1–AC8.
Origin: planner / owner-selected TinySpec, task-generation direct adapter. Preparation
only; combined current-content source/task/scope approval **pending**. No task is authorized
for execution by this file. Planner-owned review/content digests and planning checkpoints
are recorded in [run SUMMARY](../../memory/coordination/evidence/2026-10-07-early-risk-reduction/SUMMARY.md).
No implementation profile assigned; coordinator owns later selection and routing approval.

This instruction change plans selective executable risk-reduction work in future projects;
it is not itself a library spike. Established checker, mutation tests and Markdown fixtures
are the lowest sufficient oracle for the changed contracts. Synthetic A–E cases must be
labelled illustrative, not real library/runtime experiments or model-obedience evidence.
Owner instructions, constitution and existing approval/recovery, dependency research,
task-generation and task-commit contracts remain authoritative. Memory has no gotchas or
approved coordination guidance; no history intake required. Existing templates/examples
were inspected; do not edit SpecKit assets or impose Standard prerequisites on TinySpec.

Excluded: runtime/settings/production edits, policy/guideline updates, new dependencies,
compulsory prototypes, trivial name/type scripts, forced non-isolatable prototypes, new
schemas/infrastructure, live/provider tests, implementation during planning and extra gates.
Only future separately authorized execution may perform scheduled implementation proofs.

## Sequential work

- [ ] T001 Implement the shared selective-risk contract and atomic offline regressions.
  - **Depends**: none
  - **Outcome**: one canonical portable contract actually applied by all four skills;
    scheduled executable producer/consumer work, retention and disproof handling are
    operationally explicit and regressions expose their loss. Covers R1–R5 / AC1–AC7.
  - **Files/interfaces**: new `skills/planner/references/early-risk-reduction.md`;
    `skills/planner/SKILL.md` (proportionate validation, production/handoff, TinySpec and
    Standard reviews); `skills/tiny-spec/SKILL.md` (approach/acceptance and boundary/return);
    `skills/delegating-architectural-planning/SKILL.md` (preflight, plan boundary and return,
    managed adapter and standalone applicability); `skills/task-generation/SKILL.md`
    (task semantics and review/handoff); `scripts/check-planner-workflow.py`,
    `scripts/test-planner-workflow.py`; bounded Markdown fixtures under
    `scripts/fixtures/planner/` (prefer existing tiny/standard fixtures plus concise new
    risk examples only when needed). Update `skills/task-generation/scripts/test_contract.py`
    only for affected shared-task carrier coverage; no parser/schema change.
  - **Shared context**: source inspection basis and AC table; same R1–R5 contract for both
    paths/direct/standalone, existing task fields/numbering, explicit dependencies,
    permission/evidence gates, renewal rules and static assurance limits. Link the shared
    owner from actual executing sections; missing packaging stops, not silent omission.
  - **Acceptance**:
    - REQUIRED T001/V1 (AC1, AC7): pass when resolved shared links and applied obligations
      exist in all four operational consumers, their handoffs/reviews and managed/direct/
      standalone paths without changing preparation/execution or approval boundaries.
      Smallest check: named carrier-removal and summary-only replacement mutations plus
      missing/wrong-reference and distributed-link tests in the existing checker suite.
      Evidence: test names, failing-mutant diagnostics and passing candidate output from
      `python3 scripts/check-planner-workflow.py` and `python3 scripts/test-planner-workflow.py`,
      with quoted bounded skill/reference spans from manual semantic review.
      Gates: local edits/offline Python only after owner implementation approval; no live gate.
    - REQUIRED T001/V2 (AC2–AC6): pass when labelled A–E walkthroughs distinguish easy-name
      inspection from a leverage-bearing executable core, select a real-dependency/runtime
      proof for B, representative/adversarial transformation proof before plumbing for C,
      appropriate whole-environment validation with actual prerequisites/gates for D, and
      retained disproof/corrected downstream plan with affected approval renewal for E.
      Smallest check: bounded fixtures/walkthrough assertions plus mutations of the
      corresponding operational selection, execution-boundary and failure clauses.
      Evidence: case-to-test/span mapping and exact expected task/check/evidence/gate fields;
      candidate PASS and mutation diagnostics. No mock/trivial script can stand in for B/C;
      no real library experiment is claimed by fixtures. Gates: local offline checks only.
    - REQUIRED T001/V3 (AC3, AC4, AC7): pass when both adapter examples retain the existing
      schema and demonstrate an earlier executable proof producer, a production consumer
      with explicit `Depends` and acceptance requiring inspect/run/use of proof with preserved
      behavior, then production tests and cleanup only after applicable consumption.
      Commands/artifact/findings and version/runtime applicability survive until that point;
      early deletion, report-link-only consumption, omitted dependency and failed-technique-
      as-proven variants fail the relevant semantic/sensitivity checks. Smallest check:
      bounded producer/consumer fixture tests and manual semantic inspection, plus existing
      task-order validator on tiny/standard and any new numbered task fixtures.
      Evidence: producer-to-consumer item mapping, retained proof/cleanup conditions,
      parser output and named negative results. Gates: local checks; a future real-system
      REQUIRED check unavailable/unrun is NOT VERIFIED and cannot release its dependents.
    - REQUIRED T001/V4 (AC1, AC7): pass when all relevant existing safety checks remain
      green, with no new schema/routing/policy/runtime changes. Smallest check:
      `python3 skills/task-generation/scripts/test_contract.py`,
      `python3 skills/task-generation/scripts/test_check_task_order.py`,
      `bash scripts/check-skills-lint.sh` and `git diff --check`.
      Evidence: commands/counts/results and scoped diff review; do not weaken unrelated
      mutations or update unrelated freezes. Gates: local tools; missing required capability
      means NOT VERIFIED and blocks acceptance, not automatic waiver.
  - **Capabilities**: repository edits, Python 3, bash and Git; no provider, SpecKit stage,
    network, installed runtime mutation or new testing framework required.
  - **Verification effort**: bounded clause/link sensitivity and illustrative adapter
    fixtures; suite lint justified by four coupled consumers and approval safety, not an
    exhaustive risk matrix. Add tests with contract changes in this same task, not later.
  - **Integration checkpoint**: verify and commit T001 and distinct evidence-only checkpoint
    before T002. T002 must inspect this actual implementation and mapped test evidence;
    unresolved contract gaps/disproof block acceptance and return to affected review/renewal.
  - **Notes**: residual_reasoning: medium — closed semantics but cross-consumer lifecycle
    and semantic-oracle blind spot. Static PASS cannot establish live runtime obedience.

- [ ] T002 Document the implemented assurance and complete bounded acceptance review.
  - **Depends**: T001
  - **Outcome**: regression guide explains actual implemented selection, proof consumption,
    failure routing, named A–E coverage and honest assurance limits. Covers AC8 and verifies
    completed AC1–AC7 traceability without duplicating operational contract ownership.
  - **Files/interfaces**: `docs/plans/planner-regression.md`; only its necessary existing
    discovery entry in `docs/plans/index.md` if changed. Authoritative reference/skill/test
    files from T001 are read-only inputs; defects require a separately verified correction,
    not a documentation claim masking incomplete implementation.
  - **Shared context**: T001 committed reference, consumer spans, named mutation and fixture
    outputs; source AC1–AC8; existing regression guide's offline/live separation.
  - **Acceptance**:
    - REQUIRED T002/V1 (AC8): pass when guide matches actual T001 contract and named tests
      for A–E, producer→consumer→production-tests→cleanup lifetime, non-isolatable validation,
      disproof/renewal, direct/standalone coverage and planning-not-execution boundary.
      Smallest check: manual comparison of documentation to committed reference, operational
      consumers and test definitions, with existing local link checks and `git diff --check`.
      Evidence: concise AC-to-span/test mapping and resolved-link output. Gates: local docs
      only; no new workflow or approval stage, no policy edits.
    - REQUIRED T002/V2 (AC1–AC8): pass when T001 evidence is inspected and still applicable,
      each REQUIRED item has satisfied criterion-relevant proof, and guide states precisely
      that offline fixtures/static checks are not live-agent or real-library proof.
      Smallest check: inspect T001 SHA/diff/check outputs and manual A–E semantic mapping;
      reuse unchanged checks, rerun `python3 scripts/check-planner-workflow.py` and
      `python3 scripts/test-planner-workflow.py` only if guide changes invalidate their
      documentation-dependent coverage. Evidence: current revision applicability, item
      dispositions, refreshed results if needed, remaining NOT RUN live checks.
      Gates: independently reviewed final implementation acceptance under existing workflow
      after these tasks; no live/provider check authorized or required by this scope.
  - **Capabilities**: repository reading/documentation edits, Git and existing local tools.
  - **Verification effort**: small lockstep documentation comparison; no duplicate full suite
    without concrete invalidation. Independent final review remains unchanged, not a third
    padded implementation task or task-local profile assignment.
  - **Integration checkpoint**: verified T002 focused commit, distinct evidence-only checkpoint;
    coordinator performs existing whole-range independent review and acceptance. Report
    `/reload` after global skill edits, not after planning alone.
  - **Notes**: residual_reasoning: low — implemented contract/test evidence is the producer.

## Producer review and authorization boundary

Validate with the existing `check-task-order.py`, then manually inspect source traceability,
implicit prerequisites, item criteria/checks/evidence/gates, exclusions and stage feasibility.
T001 contract and tests are intentionally atomic; T002 consumes their verified evidence and
owns lockstep assurance documentation, with no filler setup/spike task. Checkpoint planning
source and this separate list before the combined owner approval; no implementation-readiness
claim or execution follows this planning-only request without current-content owner approval.
