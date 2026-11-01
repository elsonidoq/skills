# Approval reconciliation and fresh final task review — tasks

Requirements truth: [TinySpec](approval-and-fresh-task-review-tinyspec.md), especially A1–A3.
[Executable tasks](approval-and-fresh-task-review-tasks.json) carry the same two outcomes,
owned paths, dependencies and REQUIRED checks. Deterministic commands occur once, in JSON
`checks`; semantic criteria are not shell commands. No SDD or old #39/#40 artifact is a
new requirements input. Historical #40 material is diagnostic input only.

## Shared worker/reviewer brief

Carry this context and each task's REQUIRED mappings into its worker/reviewer brief.
Use the selected executor path unchanged:
`/home/dev/.paseo/worktrees/0zfm1a0e/cold-turtle/.pi/workflow-executor.json`.
The producer read it before decomposition: Terra/medium worker, Sol/medium reviewer.
These runtime roles do not replace saved planning assignments. TinySpec task production
remains Sol/medium; fresh TinySpec final review inherits `planner-parent` (this parent:
Sol/medium); Standard retains its saved overall-review binding. No configuration change.

Re-establish accepted authority through the [decision index](../decisions/index.md):
[ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md) and
[ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md) are accepted with
no recorded supersession. Current launch authority supersedes historical phase wording;
task instructions stay neutral, without rewriting historical approvals. Shared routine
defaults remain in engine `_ROUTINE_AUTHORITY`, already delivered to initial/corrective
workers. No runtime engine edit or per-task copy of those defaults is needed. Map these
constraints to T001/A1/A3 and T002/A3: preserve actual requirements/manual gates and shared
defaults while removing invented consent gates and reviewing neutrality.

The verified [memory index](../../memory/MEMORY.md) was read whole; no technical gotchas
are recorded. Its routine technical/repair guidance requires autonomous bounded diagnosis
and already-authorized repairs, not repeated routine consent; actual run/scope authority
and material product/scope, manual, paid, security, data and external gates remain. Map
this to T001/A1 and T002/A2/A3. Preserve valid unaffected correction-review coverage; no
routine transition acknowledgment, memory write, STATE update or inferred lesson.

Preserve the source's exclusions: no permission framework/ledger/service, independent
prompt-delivery workstream, new harness, model setting, automatic review loop, finding
quota, output ceremony or prevention workstream. No application/index operations, unknown
or pre-existing deletion/cache cleanup, paid application APIs, deploy, push, install,
auth change or reload/restart. The owner's removed subagents version pin controls over
older wording: verify registered usable capability, never install/downgrade. Keep reusable
skills portable; private raw sessions and credentials never enter repository evidence.
After accepted global skill changes, provide a Paseo fresh-session activation handoff,
not an owner `/reload` instruction.

For both tasks, use [evaluations/README.md](../../evaluations/README.md): freeze relevant
inputs and independent expectations before examining output; record explicit previous
and candidate revisions, model/effort/environment, commands, actual results and material
differences. Select only the required seam exercises, not the whole collection. Use the
smallest actual interface exercise within each outcome before relying on success; no
separate prototype is justified. Static tests prove instruction delivery/sensitivity,
not model judgment. Retain failed evidence. Missing capability/evidence blocks only the
affected acceptance claim; fail, non-reproduction, regression, inconclusive and unavailable
are not success. Reuse proof only while revision, input and environment remain applicable;
disproof requires correction and affected review/approval renewal, not a weakened oracle
or retries until green. Ordinary runtime/issue evidence can hold concise sanitized results;
no new repository evidence file or raw transcript is required. A1–A3 require actual behavioral
and regression evidence, not an extra owner sign-off. For amended T002/A2, reuse the adequate
clear-case evidence identified in source A2 without further model tests. The parent evaluates
that evidence; the nondelegating worker uses the existing question path for bounded
coordinator assistance and consumes the returned observations and disposition.

## Tasks

- [ ] T001 Reconcile covered worker permission questions with current owner approval
  - **Depends**: none
  - **Own**: `skills/coordinate-implementation/SKILL.md`,
    `skills/task-generation/SKILL.md`, `scripts/check-planner-workflow.py`,
    `scripts/test-planner-workflow.py`.
  - **Outcome/interface**: refine Question triage and authorization-neutral task authoring.
    Compare the actual operation, target and effects with current approval before forwarding
    a worker question; answer covered work from real approval without impersonation.
    Treat setup/capacity as technical prerequisites, not renewed download consent. Escalate
    the concrete unapproved delta or unresolved material decision. Generic agent-authored
    exact-operation wording creates no owner gate. Keep genuine gates. Exclude final-review
    dispatch changes (T002) and runtime delivery changes. Minimally align the existing
    checker's two obsolete same-head triage expectations with canonical evidence-only
    wording; inspect coupled test assertions and change only demonstrated obsolete coverage.
  - **REQUIRED T001/A1**: reproduce the actual #39 conflicting task/worker-question/coordinator
    seam, retaining generic exact-approval language and current launch/routine authority.
    Observe covered snapshot/private-transfer/owned-loopback-seed work answered without
    renewed consent or fabricated owner reply, necessary approved local dependency setup
    and capacity investigation treated technically, and a separate genuinely unapproved
    destructive/external/spending effect escalated with its concrete delta. Exercise decisions,
    not application effects. A clean prompt that supplies the desired interpretation is not
    reproduction. Apply the shared ADR/memory constraints, including no unknown-byte deletion.
  - **REQUIRED T001/A3**: run both JSON-listed planner commands; preserve meaningful assertion
    coverage and report real outcomes against the known baseline. Inspect the exact diff
    for neutral task wording, intact real gates and unchanged shared engine delivery/defaults.
    Compare changed authoring/triage instructions with A1 observations; no new assertions
    without demonstrated need. A1 failure remains unresolved despite green static checks.

- [ ] T002 Make final planning-task review fresh and consume its returned findings
  - **Depends**: T001
  - **Own**: `skills/planner/SKILL.md`, `README.md`,
    `scripts/check-planner-workflow.py`, `scripts/test-planner-workflow.py`.
  - **Outcome/interface**: use the existing final-review stage in TinySpec and Standard to
    dispatch a fresh read-only independent reviewer separate from both producer and parent
    history; never fork/resume either conversation. Replace TinySpec parent-only/no-additional-
    reviewer wording, align the saved-role description in planner, and correct README's
    observed Parent review diagram/prose. Reuse `planner-parent` inheritance for TinySpec
    and saved Standard overall review, unchanged model/effort. Supply original request,
    owner decisions, authoritative requirements, final MD/JSON tasks and necessary verified
    risks/constraints, without producer conclusions/pass assurances/approval trajectory or
    omission of substantive facts. Parent evaluates the actual report, routes substantive
    corrections to producers and resolves material findings before combined approval.
    T001 supplies the canonical evidence-only checker baseline used by this task's focused
    regression check; it is not a new review/permission gate. Exclude source-review and
    implementation-review redesign, new assignments, SDK/runtime work and extra review stages.
  - **REQUIRED T002/A2**: verify actual fresh read-only dispatch at the exact configured
    model/effort, separate from producer and parent history, with bounded factual inputs
    excluding producer conclusions/prior pass assurances. Require supported detection of
    clearly unjustified additions in a clear case, with expectations frozen outside reviewer
    input, and the actual returned report reaching the parent's preapproval disposition;
    unresolved material findings prevent approval. Verify both route instructions and retain
    existing bindings/gates. Reuse the adequate clear-case evidence identified in amended
    source A2 (`/tmp/skills-39-40-fresh-eval/clear-results.md` and `clear-review-report.md`),
    including its read-only input/unchanged hash, external frozen expectations, supported
    findings and parent withholding of synthetic task approval. No further model tests,
    mandatory rubric, prompt/output schema or workflow are required. The parent supplies
    this evidence through existing bounded coordination; the worker consumes it before
    claiming acceptance. The historical conditional-versus-mandatory diagnostic is supplemental
    and uncertain, not required must-find acceptance; retain its unsuccessful observations
    and original T002 stop without relabeling them passed. The clear case is different
    synthetic input, not a matched historical comparison or causal/reliability proof of a
    rubric, prompt change or freshness. Missing/failed required evidence remains unmet;
    dispatch flags or a finding alone cannot prove judgment and parent consumption. The
    retained tools-disabled continuation cannot test delegation; disclose material differences.
  - **REQUIRED T002/A3**: run both JSON-listed planner commands after changes; minimally align
    affected final-review assertions and preserve meaningful coverage. Inspect exact owned
    diff and README against actual review behavior: neutral instructions, shared defaults,
    real gates, configured bindings, correction routing and unchanged source/implementation
    review freshness. Report A2 results and capability gaps without success wrappers; actual
    behavioral evidence and the parent's preapproval disposition remain necessary, not replaced
    by static green output or reviewer opinion. Preserve existing combined owner approval;
    add no separate owner-verification gate.

## Execution prerequisites and evidence limits

T001's runtime delivery prerequisite already exists in `runtime/coherence_workflow/engine.py`
and `runtime/tests/test_worker_authority.py`; inspected tests admit tasks using the existing
`ProjectTest` fixture and capture initial/corrective prompts. They prove delivery only and
need no implementation changes. T001 owns its actual coordinator-judgment exercise.

T002's runtime worker has no delegation tool: `runtime/pi-host/host.mjs` disables ambient
extensions and supplies the bounded worker tool set. The parent supplies the required fresh
read-only delegation capability and evaluates actual returned evidence using existing parent
tools. For amended A2, reuse the adequate clear-case observation specified by the source;
no further live model test is needed. The worker uses `ask_owner` to request bounded
coordinator assistance with that evidence and disposition, not renewed owner consent. The existing adapter/
attached-parent question path routes that routine request; the parent returns actual results
and evidence through `coordinate_implementation_reply` for the pending run/request. The
worker checks and includes that evidence against A2 before reporting acceptance. This uses
existing coordination, not worker delegation, a new service/runtime change, extra consent or
an automatic loop. See the [existing question interface](../coordinate-implementation.md#real-execution-and-safety).
Verify actual delegation and question-channel availability at execution; a profile alone is
not proof. Report the exact unavailable operation if needed; safe inspection can continue,
but missing/failed required evidence cannot pass A2. Historical observations remain
supplemental evidence with retained failure/uncertainty, not a must-find oracle. Optional `/tmp/skills-39-40-repro-v2/`,
`/tmp/issue40-candidate.wo1JbnGK/` and `/tmp/issue40-revised.Rc30BDcK/` exist on this host;
validate applicability before use, never treat them as portable dependencies. No prescribed
SDK-internal evidence recipe is needed.

## Approval record

Production baseline: `2f111cefe73e128975a0b556c7eccebcbc0b5fb8`.
Owner selected TinySpec and authorized new compact task preparation, validation and focused
explicit-path checkpoints, not implementation. Fresh independent specification review
returned zero findings; this permits task production without scope expansion. Saved
`tinyspec-tasks` Sol/medium is unchanged. Old #39/#40 approvals are not adopted.
Fresh independent final task review `ea5fdf20-204b-4790-ba3b-0b5e85c34e47` returned zero
findings and identified required parent participation for T002/A2. Parent inspection then
removed an unsupported owner-verification gate and clarified existing parent assistance;
the producer checkpointed that correction at `4ee89bac54ece7a02a90282646035e2d0ab6af2b`.
Parent inspected the actual correction and graph checks before presenting combined approval.

The owner explicitly replied “I approve” after the current-content executive brief and
requested short problem/solution summary. This approves the TinySpec and both tasks at
`4ee89bac54ece7a02a90282646035e2d0ab6af2b`, including T001/T002 implementation, bounded
behavioral verification, focused checkpoints and independent final review. The cancelled
question before that explicit reply granted no authority. Source SHA256:
`0b5f948b24eb52372f42c2c998228ebf69065e0e689276550595990643a1bd27`; pre-record human tasks:
`8062e03d30ae892b57491f6afeaa995ef8e5f579d67d0eea2ac109952daaa508`; executable tasks:
`f46f8d9f8d6705ffe8ec17876c9eb1add799f9dc75151eb5468104bf3e8963eb`.
Only this approval record changes after that identity; task contracts remain unchanged.
Next: new coordinator run with the selected executor, not an old-run restart. Existing
exclusions and real permission gates remain. Substantive corrections remain producer-routed.

Amendment: the owner explicitly agreed to simplify the disputed historical acceptance and
requested the minimal #40 change. Source A2 was amended at
`7fc8fd6af62f190cbe984c0e95f42e8029684a7a`; this task correction aligns A2 and its evidence
reuse only. The historical oracle is supplemental/uncertain; original unsuccessful T002
history remains unchanged. T001 checkpoint `86438716a7228b9b37d29998f6337e55cec86bdf`
and its prerequisite remain intact. Current amended content awaits parent-owned approval;
prior approval identities above describe prior content, not approval of this amendment.
Required final independent implementation review and focused checkpoints remain unchanged.
