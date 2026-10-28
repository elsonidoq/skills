# Issue #33 — execution interruption tasks

Requirements: [unchanged TinySpec](issue33-execution-interruptions-tinyspec.md), AC1–AC5 and
Binding constraints. [Executable tasks](issue33-execution-interruptions-tasks.json) contain the
bounded outcomes, mutation paths and task-local REQUIRED pass/check/evidence/gate mappings.
Source SHA256: `0e8bc6494de5fd018797d8818c5d9b30248e06132aec04b59dee3c70e77fbe80`.
Correction baseline: `e06d744a7ee11e97880e8e38970877850db79a2b`.

## Outcomes

| Task | Outcome / source evidence |
| --- | --- |
| T001 | AC1: actual `run_checks` prerequisite mismatch failure and same-check scoped/self-contained success, not worker-only setup. |
| T002 | AC2: exact local/live wording reaches the worker; existing success/required-failure dispatch mechanics only, not agent semantic judgment. |
| T003 | AC3 integration: inspect final configuration/integration ownership; only a demonstrated guidance correction requires a representative override/ordinary-success example. |
| T004 | AC3 producer: inspect admitting-check coverage before reliance; only a demonstrated guidance correction requires a representative producer-type/admitting-check/ordinary-success example. |
| T005 | AC4: inspect existing socket/terminal coverage, establish answerability after a completed wait with living parent versus actionable actual loss; add only missing focused coverage. |

AC5 applies to every outcome through its REQUIRED reference to the shared contract below.
Five independently finishable Terra/medium outcomes remain: integration ownership and producer
readiness are separately inspectable, not a combined milestone or mandatory demonstration chain.
No producer dependencies exist between investigations. The executor is sequential (lowest ready ID);
empty `depends` does not authorize concurrency, and shared paths preserve preceding checkpoints.

## Shared worker and reviewer contract

**Read this section and the source's relevant AC/Binding constraints before acting or reviewing.**
Every executable outcome explicitly instructs that read. The inspected `engine.py` worker prompt
includes the complete individual task (`canonical(task)`); initial/corrective reviewer contexts carry
the task contracts. Thus this path and read instruction reach fresh contexts without a new carrier,
schema or repeated per-task ADR block. Follow the references; their presence alone is not compliance.

The producer re-read `/home/dev/projects/skills/.pi/workflow-executor.json` before correction.
Pass that path unchanged: worker `openai-codex/gpt-5.6-terra`, medium; fresh reviewer
`openai-codex/gpt-6.1-sol`, medium. Producing assignment remains
`tinyspec-tasks: openai-codex/gpt-6.1-sol`, medium.

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md):
  **“Preserve task requirements, acceptance criteria, real manual gates and safety/permission boundaries. Material unresolved authority conflicts still ask the owner.”**
  Current scoped launch supersedes historical phase wording, not real acceptance or unrelated scope.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md):
  **“Unknown/pre-existing bytes must not be adopted or deleted.”**
  Small isolated tests/databases, scoped routine repairs and selective current-task artifacts need
  no renewed routine consent; retain resource/data/security/paid/external boundaries and no global install.
- [Verified memory](../../memory/MEMORY.md): ordinary technical choices are autonomous; ask only
  material product/scope/real-permission questions. Retain completed checkpoints and still-valid
  unaffected checks/cumulative review coverage. Routine transitions/steering do not wake parent;
  questions and terminal success/error may. Preserve closed #30/#32 support rather than redo it.
- Inspection comes first. An unchanged conclusion needs exact carrier/fixture evidence, findings,
  remaining claims and tested/inspection limits, not blanket no-op success. AC1/AC2/AC4 retain their
  actual boundary checks. AC3 examples are conditional on guidance correction, not a demand for
  toy applications, typecheckers or new infrastructure. Run only affected existing fixture selections
  and necessary regressions; report exact commands/results. No blanket generated-output/review reruns.
- Required failed, inconclusive, unavailable or unrun evidence cannot release its affected claim or
  consumer. Live/manual/paid/external checks retain actual capability/permission gates; local success
  never claims live readiness/deployment. No extra ceremony for ordinary isolated local verification.
  Material scope/acceptance/dependency drift returns through existing affected review/owner gates.
- Prefer permanent actual-boundary fixtures. A genuinely necessary T005 informational [PROTOTYPE]
  remains one bounded question inside that outcome, with script/actual output/conclusion/limits,
  consumed before reliance and retained through production validation before routine teardown.
  No prototype/report/cleanup chain or SDK lifecycle redesign by recollection; insufficient matching
  version evidence stops the affected design. Reuse [canonical dependency guidance](../coordinate-implementation.md#setup-and-verification)
  and declared Python >=3.10/PyYAML 6.0.3 and Node >=22/Pi SDK 0.87.1.
- Mutation paths are narrow maximum boundaries, not dirty-byte adoption or whole-owner rewrite
  permission. Necessary support outside them uses existing scoped coordination, not automatic scope
  expansion. Honor the [checkpoint contract](../../skills/memory-handling/references/task-commit-contract.md):
  runner owns executable staging/commits; no-change makes no empty commit. Return findings, actual
  changed paths/checks/checkpoint identities and gaps in the existing task return, no new ledger.
- Preserve all source exclusions: no application/Cerca replay, #28 dirty-file takeover, #5 loops,
  #14 replay, extra intake rules, env schema/admission/framework/amendment API/recovery service,
  ledgers/STATE/reflection/retry budgets, production/deployment/push/auth/global settings or automatic
  install/reload/restart. Global skill/extension changes require fresh-session Paseo handoff, not `/reload`.

## Approval and validation limits

Owner-requested simplification corrects the stronger task embellishments, not source acceptance.
The previous combined approval was cancelled; no implementation launched. Parent inspection and
renewed combined current-content approval remain later gates. Executable instructions stay neutral.

Only mechanical planning validation is run here. Product checks remain scheduled, not PASS claims.
The known bridge fixture assumes absent `runtime/.venv/bin/python`; T005 may repair that coupled
launcher only if selected coverage needs it, using the existing scoped interpreter. It is not a new
prerequisite or separate deliverable. Parent-reported unchanged broad-suite failure in
`CoordinateAcceptedDecisionBriefTests.test_skill_requires_consultation_and_worker_review_propagation`
(literal missing from coordinate-implementation skill) is outside #33; do not fix/weaken it or rerun
that broad suite simply to rediscover it. Retain its disclosed baseline limit.
