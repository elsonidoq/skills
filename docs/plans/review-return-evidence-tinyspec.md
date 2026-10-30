# Worker-return review evidence and runner-metrics continuation — TinySpec

## Outcome and authority

The coordinator must deliver retained worker-return acceptance evidence to independent
review and finish authorized work through the supported review chain without asking the
owner to debug routine evidence-delivery failures. Independent review, real acceptance,
completed checkpoints and target-drift protection remain mandatory.

Source: [elsonidoq/skills#38](https://github.com/elsonidoq/skills/issues/38), read with
`gh issue view 38 --repo elsonidoq/skills`. The owner selected **TinySpec → Tasks →
Implement** after confirming the issue. This source is the bounded preparation deliverable,
not implementation approval. Fresh independent read-only intent review precedes separate
task generation; planner review and combined current-content owner approval still apply.
The parent assessed `NO_BRAINSTORM_NEEDED`: intent is settled; mechanism questions use
source inspection. No owner deferrals are recorded.

## Scope and exclusions

Include private reviewer delivery of completed task-return summaries, evidence identity
for reassessment, and explicit evidence-only continuation across the exact metrics commit
made by that same run. Align the existing operating/skill instructions with the supported
boundary and retain autonomous coordinator diagnosis of ordinary failures.

Do not remove target-drift protection, fabricate an approval, rewrite the old failure,
reset HEAD, or replay completed implementation to make this pass. No new runner, judge,
evidence schema, dashboard, replay framework, automatic retry loop or mandatory end-to-end
run is requested. Do not restart `minimal-evaluation`, change its stored records, revalidate
its standalone approval as part of this work, or modify historical task/approval artifacts.
The later standalone approval remains unknown, not a retained engine verdict. Resumed
metrics append (#4), generic recovery redesign and application issues are outside scope.
Do not upload raw sessions, credentials or unrelated payloads.

## Verified evidence and approach

Inspection baseline: `8c55acb6fffd9e02f536d89c3cccc75823390b6d`. Line spans below refer
to that revision. These are repository-derived mechanism decisions, not new product policy.

### Retained return → private review input

- [Engine](../../runtime/coherence_workflow/engine.py), `_review_check_evidence`
  (787–855), selects only check/checkpoint and repair equivalents. `_review`
  (970–985) supplies that evidence, not task-complete summaries. Task completion
  (1518–1528) already retains the final worker text as `summary`.
- [Store](../../runtime/coherence_workflow/store.py), `task` (727–744), retains
  baseline/result and details in `execution_tasks` plus append-only `kind=task`,
  `state=complete` history. Reuse this private data; do not read raw session files,
  parse prose for completion, require a new return format, or add storage/schema fields.
- Supply retained completed-task summaries to initial and follow-up independent review,
  clearly labeled as worker-reported evidence with task identity and retained result
  checkpoint. Keep runner-verified check attempts and Git checkpoint facts distinct.
  A return is evidence to assess, not proof a command passed or an approval.
  Missing/empty/unusable historical returns remain explicit unavailable evidence, never
  invented acceptance or a new universal startup blocker. Do not include failed or
  incomplete worker diagnostic text as completed-task acceptance.
- `_review_evidence_digest` (857–859) currently identifies only check evidence. The
  private evidence supplied to reassessment and its identity must include the retained
  returns too, using existing references/authorization machinery. Preserve existing
  historical digest/reference compatibility; no historical rewrite or backfill. A changed
  digest is not permission to accept unmet requirements.

### Exact runner commit → unchanged reviewed application target

- [Engine](../../runtime/coherence_workflow/engine.py), `_finish_reviews`
  (1067–1097), already supports explicit findings-free coverage reassessment under
  `owner-pair-v1`, but requires current HEAD to equal the rejected review head.
  `_finalize_metric_artifact` (210–243) appends a private `metric_artifact` history
  result with status, SHA, parent, exact path and `no_change`. The failure handler
  (1536–1544) calls it after retaining failure.
- [Git effects](../../runtime/coherence_workflow/git_effects.py), `_commit_result`
  and `MetricArtifactFinalizer` (7–66), already verify a single parent and exactly one
  changed artifact path. Commit success and reconciled success after a reported error
  return those same facts. [Artifact owner](../../runtime/coherence_workflow/metric_artifacts.py),
  `artifact_relative`, derives this run's exact JSONL path.
- Keep exact-HEAD reassessment as the ordinary path. Add only a narrow equivalence:
  current HEAD may instead be the **one directly following metrics commit** retained as
  successfully committed by this run's finalizer (`committed` or
  `committed_after_reported_error`, non-no-change). Its recorded SHA must equal current
  HEAD, its recorded parent must equal the rejected review head, its recorded path must
  equal `artifact_relative(run)`, and actual Git parent/changed-path facts must agree.
  Reuse the existing Git verification shape rather than introduce a commit catalogue.
  This is mechanically supported by existing recorded facts; no new continuation API,
  approval protocol or telemetry-name whitelist is needed.
- The reassessment still reviews the original base/head and an unchanged application
  delta. Do not reset HEAD, treat the metrics commit as task delivery, approve its parent
  by inference, or substitute `refresh-review-target`. Completion records the actually
  reviewed application SHA; metrics/current HEAD stays separate, as it does on ordinary
  success. Preserve metrics finalization, its optional failure reporting and normal
  hooks/signing. Do not solve drift by deleting telemetry or suppressing failure history.
- Missing or conflicting finalizer facts, another run's artifact, any additional commit,
  merge, or a commit with another changed path is real/unproven target drift and stops
  reassessment before reviewer dispatch. A commit subject or `.coherence/metrics/` path
  pattern alone grants nothing. Report the affected operation, mismatched fact and need
  to inspect/reconcile the retained target through a supported path; never suggest reset
  or fabricate missing history. This rule does not broaden actual repair grants.

### Coordinator follow-through and authority

The existing [Question triage](../../skills/coordinate-implementation/SKILL.md#question-triage)
and [operating guide](../coordinate-implementation.md#history-explicit-resume-and-abandon)
already require coordinator diagnosis and supported explicit continuation, not routine
owner-debugging. Supply retained evidence in the existing private handoff; do not add a
new automatic resume or question channel. Update only affected review/evidence/metrics
boundary text in these owners; the [schema owner](../coordinate-implementation-schema.md)
needs change only if its description is affected, not a schema migration.

Applicable accepted constraints must pass into task-local REQUIRED checks and worker/reviewer
briefs, not just remain citations:

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md):
  “Executable task descriptions and check permissions are authorization-neutral. Temporary
  phase/approval status belongs in the approval record.” “Preserve task requirements,
  acceptance criteria, real manual gates and safety/permission boundaries.” Thus current
  scoped launch authority and real acceptance stay intact (A3–A5); task review checks
  authorization neutrality, not historical approval rewrites.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md): “Ordinary
  scoped technical fixes, isolated tests/local servers, necessary isolated or in-project
  dependency setup, and current-task artifact regeneration/selective cleanup do not need
  repeated owner approval.” “Authorization does not waive required checks, turn failures
  into success, or justify blind retries of expensive failed executions.” Thus routine
  coordinator evidence diagnosis uses existing authority (A4), with actual gates and
  failures retained (A2–A5); no permission service or retry loop.
- [Project memory](../../memory/MEMORY.md), Routine technical decisions and review scope:
  “Handle routine technical decisions autonomously; ask the owner only for product
  decisions or material scope creep. Preserve mandatory explicit permission gates rather
  than treating this preference as consent.” Its routine repair guidance also requires
  run/scope-bound authority. Apply to A4/A5 and correction-only review: preserve valid
  unaffected coverage; escalate actual material decisions only.

## Acceptance and smallest sufficient validation

These criteria are behavioral outcomes, not an implementation task list. Task generation
must attach stable task-local REQUIRED evidence for the relevant criterion, with the pass
conditions below. No implementation proof was executed during source production.

**A1 — Return evidence reaches its consumer.** A tiny completed task returns a harmless
handoff required by its acceptance. The actual initial and reassessment reviewer prompts
contain that retained text, task identity and result checkpoint, separately from real
check evidence. The evidence identity changes when applicable return evidence changes.
Missing/empty historical text remains explicitly unavailable; an unsuccessful return is
not completed acceptance. Private return text does not appear in CLI status/history or
monitor projections. Use actual engine helpers and existing disposable-project utilities.

**A2 — Supported telemetry continuation completes honestly.** In a disposable Git project
that tracks metrics (ignore workflow storage only), run a tiny task with a real passing
check and focused checkpoint. A scripted independent reviewer returns passing coverage,
zero findings and a return-evidence gap. Normal failed-run finalization commits the metric
JSONL. After inspection, explicit resume with substantive coordinator diagnosis dispatches
one fresh read-only reassessment of the original range. A genuine gap-free approval
records `complete` at the original reviewed application SHA, while current HEAD retains
the metrics commit. Completed tasks/checkpoints are not replayed or recommitted; original
failure, rejection, coverage, check attempts and causal review history remain inspectable.
This proves plumbing and state transitions, not live reviewer judgment.

**A3 — Drift and invalid acceptance remain blocked.** Preserve the existing exact-HEAD
success path. Reject the metrics exception before dispatch when recorded SHA/parent/path
or actual commit facts mismatch, facts are absent, the artifact belongs to another run,
an extra/merge commit intervenes, or other files change even under a metrics-looking
subject/path. Preserve staged/working unrelated bytes. Retain uncertainty/historical-policy
stops, failed/missing required-check gaps, substantive/changed-evidence basis requirements,
one reassessment per explicit resume and duplicate unchanged-basis rejection. Remaining
gaps or actionable findings are not completion; actual repairs retain existing grants and
checks. Reuse unaffected cumulative-coverage and repair-chain regression tests.

**A4 — Routine diagnosis stays with the coordinator.** Inspect affected prompt/operational
contracts for retained-return handoff, targeted diagnosis and the exact supported metrics
boundary. The coordinator investigates ordinary technical evidence gaps and uses supported
explicit continuation within current authority, rather than asking the owner to debug or
asking again solely because files changed. Material scope, paid/external, security/data,
real manual and uncertain authority gates still stop/escalate. Prompt/contract assertions
prove instruction delivery only, not autonomous model obedience.

**A5 — Preservation and regression evidence.** Keep genuine independent acceptance,
current launch authority, neutral tasks, valid unaffected coverage, privacy, hooks/signing
and optional metric failure semantics. Align affected operative documentation without
new requirements or historical edits. Run focused existing suites plus added cases:
`PYTHONPATH=runtime python3 -B -m unittest discover -s runtime/tests -p test_review_chain.py`,
and the same command with `test_cumulative_review.py`, `test_engine.py` and
`test_metric_artifacts.py`; run scoped `git diff --check`. Use the selected existing Python
environment if imports require it; report actual unavailable prerequisites and obey current
setup authority. Required checks and fresh independent final review remain necessary after
implementation; no failed/unrun check can be reported passed.

## Research, proof rationale and remaining risk

[Runtime declarations](../../runtime/pyproject.toml) specify Python >=3.10 and
PyYAML==6.0.3; [REQUIREMENTS](../../REQUIREMENTS.md#executable-implementation-runtime)
owns existing Git, standard-library SQLite and Pi SDK requirements. This approach changes
no dependency/API version and does not touch YAML or SDK integration. The inspected local
engine/store/Git/artifact code and existing focused tests supply sufficient dependency
research for these internal seams. No dependency-wide audit, internet refresh, installation
or new reusable dependency guidance is needed. Existing technical owners remain canonical.

[Review-chain tests](../../runtime/tests/test_review_chain.py),
`RequiredCheckEvidenceTests` and `EvidenceReassessmentRecoveryTests`, already exercise
private check delivery, CLI resume, duplicate basis, drift and post-repair reassessment.
[Cumulative tests](../../runtime/tests/test_cumulative_review.py) cover preserved coverage;
[engine tests](../../runtime/tests/test_engine.py) cover real check/checkpoint ordering.
[Metric tests](../../runtime/tests/test_metric_artifacts.py), finalizer/terminal-call cases,
already exercise real metrics commits, separate reviewed SHA and original-error preservation.
Extend these permanent actual-helper/integration tests; do not create a prototype chain or
new harness. No independent producer/consumer prerequisite is needed beyond retaining
completion evidence before review and verifying the exact metrics exception before dispatch.
Tests remain permanent regression evidence; there is no disposable proof cleanup phase.

The main risk is a false drift exemption. Exact retained run-specific commit facts plus
actual Git verification and adversarial A3 controls bound it. A1 guards false equivalence
between return prose and a check pass. Both risks have cheap deterministic oracles in
existing utilities; no separate experiment or mandatory full workflow earns its cost.
Freeze tiny input and expected A1–A3 behavior before candidate output; demonstrate the
relevant previous failure and candidate correction once where useful. Follow
[evaluations/README.md](../../evaluations/README.md) for any model comparison. A small
isolated coordinator scenario is optional only if proportionate and separately authorized;
use equivalent previous/candidate inputs and report non-reproduction or unavailable checks
honestly. Deterministic results cannot establish live coordinator/reviewer obedience.

No unresolved product choice or owner deferral remains in this source. The exact-commit
mechanism is derived from inspected existing APIs, not proven implementation. If actual
implementation evidence disproves its bounds, stop affected reliance, report the mismatch
and renew affected source/review/approval rather than generalize the exemption. Historical
standalone approval and historical-run completion remain outside its claims.

For downstream task production, the selected executor path is
`.pi/workflow-executor.json`; read it before decomposition. It is separate from this source
producer's unchanged saved Sol/medium assignment. No binding is selected or copied into
executable tasks by this source. This deliverable is ready for source review only.
