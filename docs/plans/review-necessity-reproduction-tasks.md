# Review necessity reproduction — tasks

## Approval record

Owner approved **Approve and start** through `ask_user` on 2026-11-03 for the four source/task
artifacts at `88d88e8b3366657b8a91c2044d830724a17ccaea`. Approval covers T001 through the existing
coordinator, one parent baseline call, T002 only after a valid reproduced miss, one conditional
candidate call and independent acceptance. Both launches use `.pi/workflow-executor.json`.
Source and final task reviews returned zero material findings after simplification; dependency
validation and actual workflow intake passed. Live capability, recipe execution and behavioral
outcomes remain unverified. The earlier cancelled question is superseded only for this scope.
This approval-record update does not change task instructions, source acceptance or exclusions.

## Shared context

Requirements truth: [TinySpec](review-necessity-reproduction-tinyspec.md), SHA256
`ba5868c2a85d0e2e93b8feb6fbbbd8fe4e4799f183d6820a239cc6dda0391637`.
Workers and future review briefs must reference its **Required review direction**. Apply it to
this delivery as well as resulting reviewer guidance. Source A1 owns comparison evidence;
its minimal case and independent expectations own the fixed input/oracle. Use the existing
[evaluation convention](../../evaluations/README.md) and [regression guide](planner-regression.md).

The only changing behavior seam is the body of `roles/coherence-reviewer.md` from each explicit
revision. The planner's [Shared final task-review contract](../../skills/planner/SKILL.md#shared-final-task-review-contract)
sets fresh read-only review/input boundaries; it is not a dynamic input transformation or resource
graph to reconstruct. Keep oracle/answers and other-revision guidance out of supplied reviewer
prompts/resources; inspect actual reads for contamination per A1. Read tools are not a sandbox,
and theoretical access alone does not invalidate a run.

Preserve source exclusions and safety boundaries. [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md)
keeps executable work neutral under current launch authority; [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md)
permits routine scoped isolated checks without repeated consent. Preserve unrelated work and
runner-owned focused checkpoints/reviews. Workers do not stage, commit, delegate or invoke models.
No new harness, runtime behavior, protocol or issue prerequisite is needed.

## Two-list execution and parent schedule

Use the existing coordinator for [T001](review-necessity-reproduction-tasks.json) first and
[T002](review-necessity-reproduction-correction-tasks.json) only conditionally. The actual CLI
runs the whole list and cannot pause before conditional correction. Both launches use the same
retained project checkout and `/home/dev/projects/skills/.pi/workflow-executor.json`.

1. After T001's checkpoint and independent run review, parent uses its recipe for one baseline
   call at unchanged `bad3ccc49ce491db3de990d2a4e638191176269a`, with source A1's Sol/medium
   test binding and fresh equivalent context. This is a structural reproduction attempt, not a
   historical replay. Parent assesses public output/reads against the frozen expectations.
2. Parent writes source A1's evidence to the plain project-root-relative file
   `.local/review-necessity/baseline-observation.md` before any correction launch. Keep any linked
   public output/read files under the same retained `.local/review-necessity/` directory with
   resolvable relative links; do not rely only on temporary or child-session storage. Retain this
   sanitized evidence outside Git and reviewer input through comparison and independent acceptance.
   No raw private reasoning or credentials. This file is read-only input for T002, not a receipt.
3. A valid miss releases T002. Baseline pass means **not reproduced**, not refutation of the old
   incident: correction list NOT LAUNCHED, candidate NOT RUN. Error, incomplete inspection or actual
   contamination means **inconclusive**, with the same no-correction disposition. No retries or
   padding to force red. Changed facts/oracle return through affected planning approval.
4. After T002's checkpoint and independent run review, parent runs one candidate comparison at
   the explicit candidate SHA using the same frozen case/expectations/recipe and A1 equivalence.
   Record A1's candidate evidence with reference to the baseline observation, not copied receipts.
   Interpret per A4: fail/pass is improvement on this case only; fail/fail remains unresolved;
   errors/incomplete observations are inconclusive. No justified candidate means NOT RUN.

Overall behavioral acceptance requires this comparison and fresh independent acceptance review;
local/static success is not behavioral green. Global role activation uses a Paseo fresh-session
handoff, never automatic restart or `/reload`.

## Work units

- [ ] T001 Retain the frozen case and concrete invocation recipe.
  - **Depends**: none
  - Own `evaluations/review-necessity/{packet,expectations,recipe}.md` and the necessary discovery/
    empty-collection correction in `evaluations/README.md`.
  - Deliver the source's neutral packet, independent expectations and a shell recipe using each
    revision's reviewer instruction body. Check installed Pi semantics, extraction of that body,
    clean equivalent context and supported capability readiness without a model call or install/auth.
    Recipe names the parent-written baseline observation route above and A1 evidence requirements;
    T001 does not create the observation. Keep the useful sanitized case permanent.
  - **REQUIRED T001/A1:** inspect fidelity to the source's fixed facts/oracle, distinct input/output
    locations, usable command and revision-owned body selection. Record frozen identities before
    baseline. Report exact capability gaps as UNAVAILABLE, not a behavioral result. Run
    `git diff --check`; parent performs the live call, not the worker.

- [ ] T002 Correct the selected reviewer instruction body only after a valid miss.
  - **Depends**: T001
  - Before edits, resolve/read `.local/review-necessity/baseline-observation.md` from the retained
    project root and follow its linked public evidence. This explicit cross-run prerequisite
    replaces inherited parent context; the standalone JSON has no dangling dependency.
  - **REQUIRED T002/A2:** verify source A1 identities against retained inputs and selected baseline
    resource, actual completion/reads and the principal miss against frozen expectations. A parent
    verdict alone is insufficient. Missing/mismatched evidence or an invalid run blocks correction,
    not a reason to retry or fabricate evidence.
  - **REQUIRED T002/A3:** make the smallest justified project-neutral change to
    `roles/coherence-reviewer.md`'s body. Do not repair the packet or preselect stronger prompting.
    No justified bounded remedy means unresolved; a different seam returns to affected planning
    review. Own `scripts/test-install-capabilities.py` and `docs/plans/planner-regression.md`
    only as necessary support. Add/update a static check only for a concrete delivery defect per
    A3, not mere prose changes. Preserve role metadata; run that existing isolated installation-link
    test and `git diff --check`. These check delivery, not reviewer decisions. No planner-suite
    change or broad suite is needed.
  - **REQUIRED T002/A4 handoff:** return the explicit candidate checkpoint and applicable local
    results for the parent comparison above. Do not claim improvement before that comparison.

## Remaining execution risks

T001's recipe and live selected-model access are not yet demonstrated; supported local interface
checks precede the parent baseline, and a capability gap stops only that call. T002 depends on a
real miss and may have no justified fix. The parent candidate may remain unresolved/inconclusive.
The single baseline is the earliest useful proof, so no separate disposable prototype is needed.
