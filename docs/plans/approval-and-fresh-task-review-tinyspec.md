# Approval reconciliation and fresh final task review — TinySpec

## Intent and authority

For owners and agents using the suite, remove duplicate routine consent questions (#39)
and isolate final task review from producer and parent planning history (#40).
Sources: current [#39](https://github.com/elsonidoq/skills/issues/39),
[#40](https://github.com/elsonidoq/skills/issues/40), and the owner's fresh-start
request (`/home/dev/skills-issues-39-40-fresh-start.md`, read in full). This source
records that request; old #39/#40 plans, tasks and approvals are not its contract.
Baseline: `23c5384bf5ba45a9dd66584e95bf1e6f6f8ff4fc`.

The owner selected TinySpec and authorized new source/task preparation, validation
and focused checkpoints. This source is not implementation approval. Fresh independent
source review, separate tasks, final task review and combined current-content approval
remain required. No material choice is deferred.

## Scope and smallest approach

- **Coordinator:** refine [Question triage](../../skills/coordinate-implementation/SKILL.md#question-triage).
  Before forwarding a worker permission question, compare its actual operation, target
  and effects with current owner approval. Answer covered work from that approval;
  do not invent an owner reply. Generic agent-authored demands for separate exact-operation
  approval do not create an owner gate. Investigate capacity and other technical
  prerequisites, apply bounded authorized corrections, or report the concrete blocker.
  Escalate only a concrete unapproved effect or material unresolved decision.
- **Task authoring:** refine [authorization-neutral tasks](../../skills/task-generation/SKILL.md#authorization-neutral-tasks)
  to avoid manufacturing routine reapproval gates. Preserve actual owner-imposed/manual
  gates. Current launch authority supersedes historical phase wording under
  [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md).
  Shared routine defaults stay in the existing engine `_ROUTINE_AUTHORITY` block,
  already delivered to initial/corrective workers; do not duplicate them in tasks or
  expand runtime permission machinery. This preserves
  [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md).
- **Planning:** change the existing final review in [planner](../../skills/planner/SKILL.md),
  for TinySpec and Standard, to always dispatch a fresh read-only independent reviewer,
  separate from the task producer **and** the parent's accumulated conversation.
  Never fork or resume either conversation for this independent review. Replace the
  TinySpec parent-only/no-additional-reviewer wording; do not add a second review stage.
  Keep existing review scope, correction routing and approval gates.
  Supply the original request, actual owner decisions, authoritative requirements,
  final human/executable tasks and necessary verified constraints/risks. Exclude producer
  self-assessments/conclusions, previous pass assurances and approval trajectory, without
  withholding substantive facts. The reviewer returns supported findings or justified
  zero findings, not owner approval. The parent evaluates the actual return, routes
  corrections and resolves material findings before requesting combined approval.
- **Existing checks:** make the minimal supported assertion alignment in
  `scripts/check-planner-workflow.py` and `scripts/test-planner-workflow.py` from obsolete
  same-head phrases to canonical evidence-only reassessment wording. Baseline checker
  has two obsolete expectations at line 912; 175 tests have 31 failures from those
  expectations. Preserve meaningful coverage, not obsolete policy. Align assertions
  affected by the requested final-review change; extend tests only for a demonstrated need.

## Constraints and dependencies

Preserve manual, paid, security, data, spending, destructive and external-operation
boundaries. Specifically requested snapshot/private transfer/owned loopback restore and
necessary approved local model/runtime setup must not acquire generic renewed-consent
requirements. A real disk shortage is not missing download consent. Do not infer authority
to delete unknown/pre-existing bytes, caches or arbitrary remote data.
[Project memory](../../memory/MEMORY.md), routine technical/repair guidance, applies
within these limits; it is not a blanket grant.

Reuse the installed subagents interface's fresh-context option and read-only reviewer
profile. Local capability guidance inspected during preparation supports this shape;
no novel dependency or web research is needed. The executing parent must verify a
registered, usable capability and exact dispatch at the applicable stage. The owner's
explicit removal of the pi-subagents version pin controls over older repository wording:
never install or downgrade to satisfy that pin. A profile/configuration alone does not
prove usable dispatch. Report an exact unavailable operation; do not silently substitute.

Preserve current [planning assignments](../../skills/planner/references/model-assignments.json).
TinySpec final review can reuse `planner-parent` inheritance in a fresh session (this
parent: Sol/medium); Standard retains its configured overall-review binding. Override
profile defaults only to preserve the resolved binding, not to select another model.
No new model setting. The task producer must read the selected executor before
breakdown: `/home/dev/.paseo/worktrees/0zfm1a0e/cold-turtle/.pi/workflow-executor.json`.
This source does not set runtime bindings.

## Acceptance and proportionate validation

**A1 — Approval seam:** exercise the actual conflicting task/worker-question/coordinator
seam from #39, retaining the current launch/routine authority and generic exact-approval
wording. Covered snapshot/local-seed work proceeds without renewed consent or fabricated
owner approval; necessary approved dependency setup and capacity investigation receive
ordinary technical treatment. Separately include a genuinely unapproved destructive,
external or spending effect: it is escalated with its concrete delta. A clean prompt
that supplies the desired interpretation is not this reproduction. No application effects
are needed or authorized for the exercise.

**A2 — Fresh final review and consumption:** observe a real fresh read-only dispatch,
using the exact configured model/effort, separate from the task producer and parent
conversation. Supply bounded factual requirements, decisions, final tasks and necessary
constraints/risks, without producer conclusions or prior pass assurances. Require
supported detection of clearly unsupported additions in a clear task case, with expected
findings frozen outside reviewer input. Inspect the actual returned report and the
parent's disposition before approval; unresolved material findings prevent approval.
A finding alone does not prove parent consumption; dispatch flags alone do not prove
review judgment. No mandatory rubric or expanded prompt/output ceremony is required.

The owner revised the historical-case requirement: the conditional source versus mandatory
T002/A2/A3 additions and T003 dependency at `6f68e823181ddee96db116a4e0fba3b58e477e72`
warrants uncertainty, but is not an unambiguous unnecessary-work oracle. Retain that
diagnostic as supplemental evidence and a limitation, not mandatory must-find acceptance.
Preserve its unsuccessful observations and T002 stop; do not relabel them as passes.

Reuse the adequate clear-case evidence in `/tmp/skills-39-40-fresh-eval/clear-results.md`
and its task, frozen-expectation and returned-report artifacts. Fresh Sol/medium reviewer
`623d5415-122e-4703-98e5-7788ca85a8ee` detected unsupported service/database/retention,
admin/accounts, speculative plugins and duplicate release reports; parent accepted the
findings and withheld synthetic task approval. Input was read-only with unchanged hash
and expectations outside intake. This is a new synthetic case, not a matched comparison
or proof that a rubric, prompt change or context isolation caused improvement. Reuse it
without further model tests; it establishes neither causal/statistical reliability nor
implementation approval.

**A3 — Regression and evidence:** run `python3 scripts/check-planner-workflow.py` and
`python3 scripts/test-planner-workflow.py` after affected changes; report real outcomes.
Inspect the owned diff for authorization-neutral instructions, preserved shared defaults,
real gates, unchanged source/implementation review freshness and configured bindings.
Use [evaluations/README.md](../../evaluations/README.md), including retained `bd6039e`
reproduction-validity guidance: explicit previous/candidate revisions, frozen inputs and
expectations, model/effort/environment identities, commands, outputs and interpretation.
Reuse valid private historical evidence where applicable; keep raw sessions/credentials
out of repository evidence. The retained tools-disabled continuation cannot test new
delegation: explain the intended context change and other material differences rather
than claim a matched comparison. Report fail, non-reproduction, regression, inconclusive
or unavailable honestly; failed required behavior remains unresolved despite green checks.

The consequential uncertainty is model judgment at these interaction boundaries. Use the
smallest actual interface exercise at the first usable changed seam before relying on
success; static assertions prove delivery/sensitivity only. No separate prototype or new
harness is justified. Reuse evidence only while its revision, inputs and environment
remain applicable; retain failed evidence. Missing capability/evidence blocks the affected
acceptance claim, not unrelated safe inspection. No reliability guarantee follows from
one observation.

## Exclusions and delivery

No runtime permission framework, approval ledger, new review service/stage/automatic loop,
prompt matrix, output ceremony, finding quota or prevention workstream. Existing source
and implementation final reviews are already fresh; do not redesign them. No forced test
extensions, old-plan adoption, historical evidence rewrite, broad reset or cleanup.
No application/index operations, cache deletion, paid application APIs, deployment, push,
install, auth change or automatic reload/restart. Keep reusable skills portable; incident
facts and evaluation policy stay project-local. Changes are bounded text/assertion edits;
no data migration is needed. Preserve unrelated bytes, hooks/signing and focused task
checkpoints. After accepted global skill changes, provide a Paseo fresh-session activation
handoff, never an owner `/reload` instruction.
