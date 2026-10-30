# Worker-return review evidence and runner-metrics continuation — tasks

Requirements truth: [TinySpec](review-return-evidence-tinyspec.md), A1–A5 and its
verified approach. [Executable tasks](review-return-evidence-tasks.json) contain the same
outcomes, ownership, dependencies and task-local REQUIRED mappings. Commands occur only
in the JSON `checks` fields, which the existing runner executes; prose criteria remain
semantic. Issue [#38](https://github.com/elsonidoq/skills/issues/38) is provenance, not a
second requirements source. No SDD is used as direct requirements input.

## Shared contract and worker/reviewer brief

Read this section with each task and carry its applicable clauses, source links and local
REQUIRED mapping into worker and reviewer briefs. Re-establish current accepted authority
from the [whole decision index](../decisions/index.md); both records below are accepted,
with no recorded supersession. Source/task conflict or uncertain supersession stops only
the affected mapping; do not silently change requirements.

**C1 — Neutral instructions and real acceptance.**
[ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md):
“Executable task descriptions and check permissions are authorization-neutral. Temporary
phase/approval status belongs in the approval record.”
“Preserve task requirements, acceptance criteria, real manual gates and safety/permission
boundaries.”
Map A3/A5 to T001/A3, T001/A5, T002/A3 and T002/A5: current scoped launch authority
and existing real gates survive evidence delivery and continuation. A return, digest or
metrics commit is neither approval nor a check pass. Review tasks for neutrality, not
historical approval rewriting. Workers implement and verify their bounded outcome; the
runner owns configured checks/checkpoints and the fresh independent reviewer owns verdicts.

**C2 — Routine scope is autonomous, not waived acceptance.**
[ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md):
“Ordinary scoped technical fixes, isolated tests/local servers, necessary isolated or
in-project dependency setup, and current-task artifact regeneration/selective cleanup do
not need repeated owner approval.”
“Authorization does not waive required checks, turn failures into success, or justify
blind retries of expensive failed executions.”
Map A2–A5 to T001/A5 and T002/A2–A5: use bounded isolated fixtures and routine diagnosis,
not repeated owner-debugging questions. Actual manual, paid/external, security/data,
material-scope and uncertain-authority boundaries remain. Inspect an expensive failure's
cause before any supported continuation; no blind retry loop or fabricated owner answer.

**C3 — Owner guidance and correction scope.** The verified project association is
[memory/MEMORY.md](../../memory/MEMORY.md), read whole; it contains no technical gotchas.
Its Routine technical decisions and review scope guidance says:
“Handle routine technical decisions autonomously; ask the owner only for product decisions
or material scope creep. Preserve mandatory explicit permission gates rather than treating
this preference as consent.”
Its correction-only guidance preserves already-confirmed unaffected work, and Routine
repair authorization requires actual run-and-scope-bound authority, not blanket consent.
Map A3–A5 to T001/A3/A5 and T002/A3–A5: retain valid unaffected cumulative coverage,
revisit invalidated conclusions and outstanding gaps, and keep actual repairs under existing
causal grants/checks. No memory writes, inferred lessons, STATE maintenance or history intake.
Routine transitions require no parent acknowledgment (Parent-turn notifications guidance).

**Exclusions and evidence limits.**

> Do not remove target-drift protection, fabricate an approval, rewrite the old failure, reset HEAD, or replay completed implementation to make this pass.

> No new runner, judge, evidence schema, dashboard, replay framework, automatic retry loop or mandatory end-to-end run is requested.

Do not restart `minimal-evaluation`, change its records, revalidate its standalone approval,
or alter historical task/approval artifacts. No metrics append redesign (#4), generic
recovery redesign, application changes, dependency/API/SDK/schema changes, broad telemetry
filename/subject whitelist, raw-session reading/upload, credentials or unrelated payloads.
Missing/unusable historical return evidence is unavailable, not fabricated or a universal
startup blocker. Preserve hooks/signing, unrelated staged/working bytes and optional metric
failure semantics. Keep raw returns and diagnosis out of public projections.

Use [evaluation guidance](../../evaluations/README.md): freeze tiny inputs and independent
expectations before candidate output; compare an explicit previous/candidate revision once
where useful, disclose differences and honest non-reproduction/unavailable limits. Permanent
actual-helper tests suffice; no prototype/proof/report/cleanup chain is needed. Deterministic
tests prove plumbing/state transitions, not live model judgment or obedience. A live isolated
coordinator scenario is optional and separately authorized, never mandatory full-workflow
acceptance. If implementation disproves exact equivalence, stop affected reliance and renew
affected source/review/approval rather than broaden the exemption.

## Tasks

- [ ] T001 Deliver private completed-return evidence and reassessment identity
  - **Depends**: none
  - **Own**: `runtime/coherence_workflow/engine.py`, `runtime/tests/test_review_chain.py`,
    `runtime/tests/test_cumulative_review.py`, `docs/coordinate-implementation.md`,
    `docs/coordinate-implementation-schema.md`, `skills/coordinate-implementation/SKILL.md`.
  - **Outcome/interface**: use retained complete task summaries/result checkpoints from
    existing store data in actual initial/follow-up review prompts and evidence digest.
    Keep worker-reported prose separate from verified check attempts/Git facts. Update
    affected private-evidence descriptions with this outcome. Exclude metrics equivalence,
    new result formats and storage changes. Acceptance does not wait for T002.
  - **REQUIRED T001/A1**: capture harmless retained text, task identity and result checkpoint
    in initial and reassessment prompts; observe digest sensitivity to applicable returns,
    explicit unavailable historical text and exclusion of unsuccessful/incomplete diagnostic
    returns. Assert private sentinel absence from CLI status/history, monitor and exposed
    references; no raw-session input. Freeze tiny expectations first.
  - **REQUIRED T001/A3**: retain exact-HEAD success, substantive/changed-evidence basis,
    duplicate unchanged-basis rejection after reopen, uncertainty/historical-policy stops,
    failed/missing-check gaps, historical digest/reference compatibility and unchanged rows.
    Consume C1/C3 in worker/reviewer briefs: neutral authority, real gates, bounded repairs
    and unaffected coverage survive; digest change does not satisfy unmet acceptance.
  - **REQUIRED T001/A5**: compare changed docs with actual private prompt/digest behavior;
    apply C1–C3 and exclusions, preserve independent acceptance/privacy/check distinction.
    Execute the JSON review-chain and cumulative suites plus exact-owned-path whitespace
    check. Return real outcomes and evidence limits; fresh final review stays independent.
  - **Existing admitting support**: `intake.admit` validates task fixtures; `ProjectTest`
    creates disposable Git projects; `RequiredCheckEvidenceTests` and
    `EvidenceReassessmentRecoveryTests` capture actual prompts/check history. Existing
    `verification.commands/run_checks` consumes `checks` and `required[].check`, not prose.
    Store completion is `task/state=complete` with retained summary/result; inspect malformed
    historical data without treating failed worker history as acceptance. Safe CLI/monitor
    projections remain unchanged consumers, checked by sentinel assertions.

- [ ] T002 Complete exact same-run metrics-commit evidence reassessment honestly
  - **Depends**: T001
  - **Own**: `runtime/coherence_workflow/engine.py`, `runtime/coherence_workflow/git_effects.py`,
    `runtime/tests/test_review_chain.py`, `runtime/tests/test_metric_artifacts.py`,
    `runtime/tests/test_engine.py`, `docs/coordinate-implementation.md`,
    `docs/coordinate-implementation-schema.md`, `skills/coordinate-implementation/SKILL.md`.
  - **Outcome/interface**: retain ordinary exact HEAD; add only the source's retained
    successful same-run, non-no-change, directly-following exact metrics commit equivalence
    before reassessment dispatch. Consume T001 private evidence/identity and its tests.
    Reuse `git_effects._commit_result` verification shape and `artifact_relative(run)`;
    no finalizer recreation, new API or repair-authority expansion. Align affected review,
    metrics and coordinator-triage descriptions/diagnosis prompt in this same delivery.
  - **REQUIRED T002/A2**: at this earliest composed boundary run real tiny task/check/focused
    checkpoint → findings-free coverage rejection → normal failed-run metrics finalization
    → inspected explicit resume with substantive diagnosis → exactly one fresh independent
    read-only verdict → recorded completion at original application SHA. Current HEAD retains
    metrics SHA; initial/reassessment prompts contain T001 return evidence. Assert no task,
    check/checkpoint replay or recommit and retained failure/rejection/coverage/attempt/causal
    history. Use actual finalization, not fabricated finalizer success facts; freeze input
    and expectations first. This is plumbing proof, not live judgment.
  - **REQUIRED T002/A3**: test exact-HEAD control plus both successful statuses (`committed`,
    `committed_after_reported_error`) with actual Git verification. Reject absent/conflicting
    facts, failed/no-content/no-change status, wrong recorded SHA/parent/path, other-run
    artifact, actual parent/path mismatch, extra/merge commit and additional changed paths,
    regardless of subject/path appearance, before dispatch. Require recorded SHA=current
    HEAD, parent=rejected head, path=this run's exact artifact and actual single-parent/
    exact-path agreement. Preserve unrelated staged/working bytes and hooks/signing.
    Retain T001 identity/basis controls, uncertainty/historical stops, one reassessment per
    explicit resume, unchanged-basis rejection, real failed/missing-check gaps, remaining-gap
    stops and actual repair grants. Apply C1–C3 to briefs; original range is not refreshed.
  - **REQUIRED T002/A4**: inspect/assert actual diagnosis/reviewer prompts and operative
    contracts against implemented behavior: routine technical diagnosis stays with the
    coordinator; supported explicit continuation is not automatic retry. Apply C2/C3;
    changed files alone do not require new consent, real material/manual/paid/external/
    security/data/uncertain-authority gates do. Instruction assertions claim delivery only.
  - **REQUIRED T002/A5**: compare all affected docs against final implementation/composed
    evidence; preserve C1–C3, privacy, independent acceptance, launch authority, neutral
    instructions, historical rows, optional metric failure and original error. Execute all
    four source-required suites and scoped whitespace check from JSON. Return real results
    and limits for fresh independent final review; failed/unrun checks are not passes.
  - **Existing admitting/final configuration support**: inspect `ProjectTest.setUp` before
    reuse: `.coherence/` is ignored, so locally override the case's `.gitignore` to ignore
    workflow storage only, as existing metric-finalizer tests do, before the task baseline.
    Otherwise no real metrics commit is exercised. Keep this support local to the outcome;
    no shared fixture/harness redesign. Use normal `Engine.invoke` failure handling,
    `_finalize_metric_artifact`, retained `metric_artifact` history and CLI/engine explicit
    resume. Existing cumulative suite is unchanged support, rerun because engine changes
    can invalidate its evidence. `git_effects.py` ownership permits only necessary reuse of
    existing verification; unchanged support does not require an edit.

## Boundaries and execution prerequisites

Two outcomes fit the observed configured worker's medium-effort context: one private input/
identity contract, then one eligibility/continuation boundary against that completed contract.
Neither waits for unfinished downstream behavior to pass. T002 depends on T001 because the
composed resumed reviewer must consume the actual private returns/digest, not stubbed delivery.
Shared engine/docs ownership is sequential; tests/docs/evidence stay with their behavior.
There is no independent prerequisite warranting a separate experiment or cleanup task.

Producer read the selected executor JSON at the exact resolved path:
`/home/dev/.paseo/worktrees/0zfm1a0e/lethal-hippo/.pi/workflow-executor.json`.
Actual worker: `openai-codex/gpt-6.1-terra`, effort `medium`; reviewer:
`openai-codex/gpt-6.1-sol`, effort `medium`. Pass this absolute path unchanged; runtime
configuration, not task metadata, selects executors. The producer's saved Sol/medium binding
is not the implementation binding. No capability hierarchy is assumed.

Before worker reliance, the coordinator consumes these specific findings:

- **T001:** existing store completion and safe projection interfaces were inspected; no new
  schema is needed. Historical missing/malformed returns and old digest references require
  explicit compatibility controls. Implementation evidence is not yet observed: capture actual
  prompts/digest and sentinel absence before relying on the new private input.
- **T002:** `_commit_result` already verifies a single parent and exact changed path; engine
  finalization records success facts, but current reassessment requires exact HEAD. False
  drift exemption is the material risk. Verify retained run-specific facts against Git and
  adversarial cases before dispatch; keep original reviewed SHA separate at completion.
  The existing broad fixture ignore must be overridden locally so the composed check is real.
- **Both:** Python 3.12.3 is available; current `python3` imports PyYAML 6.0.1 while
  `runtime/pyproject.toml` declares 6.0.3. The previously referenced project validation venv
  is absent here. Task intake can run, but focused implementation suites have not run.
  Use the selected existing compatible Python environment if imports require it; report
  exact prerequisite errors, do not install or change dependencies during task production.
  No SDK/provider call is needed for these deterministic fixtures. Reuse source-local
  dependency evidence (Python >=3.10, declared PyYAML 6.0.3, standard-library SQLite/Git);
  no dependency/API change or research refresh is indicated.

## Approval record

Owner confirmed #38 and selected TinySpec → Tasks → Implement. This authorizes source/task
preparation and focused artifact commits, not implementation. Fresh independent source review
`143af97f-6c86-40df-9b22-8790855e4a15` reported zero material findings; the parent inspected
its source/report and unchanged source identity. No separate pre-task source approval is
required. Combined content/authority approval and task review remain pending. No implementation,
proof execution, live scenario, historical restart, acceptance or implementation-readiness claim
is made. This section is the existing owner for subsequent parent approval persistence.

Source identity: SHA256 `d963e6ab17094a78dc682d66f86614fdba43aaea5612b307ca4e05cf608d6ae8`.
Task-production baseline: `17a1077c09fa7686f886d4387e083d7d98c6d127`.
Task identities/result commit are returned by the producer; no self-referential content hash
or fabricated approval is embedded here.
