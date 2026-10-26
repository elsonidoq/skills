# Workflow completion and recovery — implementation tasks (#30)

## Source and executable handoff

Requirements truth: [TinySpec](workflow-completion-recovery-tinyspec.md), A1–A5,
read entirely through the task-generation direct adapter. [Executable JSON](workflow-completion-recovery-tasks.json)
owns complete work instructions, explicit paths and task-local REQUIRED checks; this is its concise presentation.
No Standard plan or SDD input is introduced.

### Preparation, review and approval record

Preparation baseline: branch `planner-github-com-elsonidoq-skills-30`, clean HEAD
`9561175a2cee861fe5216951086c55846bd30087`. Source SHA256:
`71e20f2bf47d9860d5de38408248c5ccc16fdfed6e700bcd6cce6bd4e84daab9`.
Owner selected TinySpec via `ask_user` and authorized bounded planning preparation and
focused checkpoint after the clean approved fast-forward bringing completed #23–#28 safeguards.
Parent inspected the source/scope. Fresh independent read-only source-review invocation
`89c7c394-951b-410e-a36b-a6c68b899336` returned explicit **zero findings**; parent confirmed
source unchanged before/after. This is upstream source-review evidence, not task review or implementation acceptance.
Saved task-producer assignment: `openai-codex/gpt-6.1-sol`, medium (`tinyspec-tasks`),
not the implementation binding.

Current combined source/task review and owner approval are **pending**; implementation
is **not approved**. Task-list checkpoint is preparation, not that approval. Final combined
approval starts coordinator preflight by default; it has not been requested here. Temporary
phase status stays in this record, not executable instructions. No implementation proofs,
provider calls, live workflow or Cerca continuation ran during task preparation.

## Shared worker and reviewer context

Producer itself read the exact selected executor JSON before decomposition:
`/home/dev/.paseo/worktrees/0zfm1a0e/unlucky-flamingo/.pi/workflow-executor.json`.
Pass that absolute path unchanged: worker `openai-codex/gpt-5.6-terra`, medium;
fresh reviewer `openai-codex/gpt-6.1-sol`, medium. Do not substitute producer settings
or historical executor files. These runtime settings are not task eligibility metadata.

The following binding source constraints are carried **verbatim** from its governing section
(relative links retain the same directory base). Each task's REQUIRED mappings apply them
at its changed seam; worker/reviewer briefs include those mappings, exact owned paths,
consumed predecessor contracts and exclusions, not links alone:

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md): current owner-authorized launch governs assigned implementation over historical planning-only labels, including corrections/resumes; tasks stay authorization-neutral and temporary phase status stays in approval records. Preserve acceptance/manual/safety gates and escalate material authority conflicts. Returned execution is not acceptance. Validate unchanged authority delivery alongside the changed completion prompts; do not add a routine approval question or rewrite historical artifacts.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md): reuse shared `_ROUTINE_AUTHORITY` for ordinary scoped fixes, small isolated tests/databases/local servers, necessary local/in-project setup and task-artifact lifecycle without repeated approval. Preserve actual owner-imposed limits/manual gates, paid application/test API scope, credential/security/data/external boundaries, global-install exclusion, and prohibitions on deployment/push/unrelated deletion. Unknown bytes are not adopted or deleted. Authority is not proof; check results remain actual results. Validate these limits in affected initial/corrective/resumed prompts, not a new permission layer.
- [Project memory](../../memory/MEMORY.md), read in full, contains only inline owner guidance, no technical gotchas. Applicable guidance verbatim: “Handle routine technical decisions autonomously; ask the owner only for product decisions or material scope creep. Preserve mandatory explicit permission gates rather than treating this preference as consent. When the owner requests correction-only review, assess the correction and affected behavior instead of re-reviewing areas already confirmed correct.” Also: “Routine task transitions/completions and steering-status updates must not wake the parent agent or require acknowledgment. Only agent questions and terminal workflow completion, whether success or error, should trigger a parent turn.” Recovery diagnosis is routine coordinator work; owner-only additional-pair grants remain owner-only. No extra transition acknowledgments. Correction-only review guidance does not remove the executable runner's mandatory fresh full-original-range final review.
- [AGENTS](../../AGENTS.md) and [constitution](../../.specify/memory/constitution.md): preserve focused verified checkpoints, task-owned paths, unrelated staged/unstaged/untracked work, hooks/signing, independent final review and historical rows. AGENTS' explicit owner-controlled concurrency direction supersedes older blanket sole-writer text; coordinate overlapping ownership and respect real live-writer locks, rather than add a concurrency prohibition. Global assets remain portable. Changed global skills/tools in Paseo need a fresh-session handoff, not `/reload` or automatic restart.


Shared exclusions: no Cerca execution/recovery/application fixes, reopening completed #23–#27,
redoing #26, #5 unchanged-check loops or duplicating delivered #28. No framework/state machine,
outcome schema, migration/history rewrite, retry/permission service, runtime task/path mutation,
automatic ownership adoption, extra startup rules, quotas/limits, blanket concurrency ban,
automatic install/auth/reload, push/deploy or mandatory paid/live proof. Current operating/schema
docs change in lockstep with behavior; historical source/tasks/rows and memory/STATE remain intact.

Read baseline production owners and actual-helper fixtures named by each task; reuse
`runtime/tests/fixtures/support.py` disposable Git, actual adapter subprocess fixtures in
`test_engine.py`, and recovery/grant fixtures in `test_resume.py`/`test_review_chain.py`.
Ordinary tests/docs/teardown stay with outcomes. Workers do not stage/commit; runner runs
configured actual commands, inspects owned diffs and checkpoints, then fresh independent
full-range review. Explicit manual/external/paid/security/data gates remain at the real action;
local isolated fixture work has no new permission ceremony. Routine technical decisions
are autonomous. Overlapping shared-file edits require scheduling/coordination, not invented dependencies.

## Bounded outcomes

- [ ] T001 Separate worker-owned completion from runner-owned acceptance stages (A1).
  - **Depends**: none
  - Shared completion/task/fixer prompts and registered host description, captured authority,
    real Engine stage order/positive controls and preserved unsuccessful stops; current docs.
- [ ] T002 Retain unsuccessful task/fixer status and actionable returned explanation (A2).
  - **Depends**: none
  - Actual host → adapter → Engine terminal/history diagnostics, fallback/invalid controls,
    safe existing projections; no new reporting schema or success inference.
- [ ] T003 Attribute task/repair checkpoints within full integration review (A3).
  - **Depends**: none
  - Actual Git parents/paths and retained checkpoints distinguish unrelated/unknown context;
    composed initial/repair rereview keeps full original diff and cross-commit defects visible.
- [ ] T004 Retain restart-usable settled-unsuccessful-fixer facts (A4 producer).
  - **Depends**: T002
  - Persist actual failure identity/cause/session/claims/effects; reopening can inspect facts
    while the existing unsuccessful stop remains. Acceptance needs no unfinished consumer.
- [ ] T005 Continue inspected settled-unsuccessful fixer in its exact assignment (A4 consumer).
  - **Depends**: T004
  - Consume restart facts and diagnosis before same-assignment continuation; compose real
    checks/checkpoint/fresh review for first repair and exact consumed additional pair;
    preserve uncertain no-replay, negative controls, existing reconciliation and real owner grants.
- [ ] T006 Prepare coupled supporting-test/harness ownership within bounded outcomes (A5).
  - **Depends**: none
  - Canonical authoring reminder/example and focused fixture; unchanged real ownership,
    command-field, neutral wording and exact-file handoff/resume controls.

Only causal graph: `T002 → T004 → T005`; other outcomes need no new producer.
T004 produces failure facts independently inspectable after restart; T005 consumes those
facts before reliance. T003's new attribution brief is independently useful and not required
to enable the already-existing original-range recovery contract. Shared `engine.py`, docs
and test files require coordinated nonoverlapping writes; runner sequencing already provides
that scheduling. Each outcome includes its own tests/current docs and excludes other seams.

## Proof and handoff limits

No disposable prototype is warranted: bounded existing helpers and permanent regression
fixtures observe these seams. T001 composes completion→real check→checkpoint→review;
T002 composes actual framed transport→terminal/history; T003 composes actual Git attribution
through repair rereview; T004 verifies retained facts before T005 composes restart/grant recovery.
T006's example tests preparation quality, not live planner behavior. Scripted host/model and
reviewer answers are labelled: they prove mechanics/instruction delivery, not live autonomous
judgment, consent or obedience. No new test platform or mandatory provider proof.

Executable REQUIRED argv commands occur once per task in existing `required[].check` fields;
semantic pass criteria remain prose. Selected pre-existing classes/modules were inspected,
not guessed. Run commands after relevant implementation and report actual outcomes; failed,
unrun or unavailable proof cannot release affected acceptance. Reuse still-applicable evidence
once; rerun when code/environment/scope changes invalidate it. Missing historical attribution
or safe recovery facts stays an actionable limit, not guessed ownership/migration. Disproof
blocks affected reliance and returns through existing correction/review; scope/acceptance or
authority changes renew affected approval. Keep disposable proof until consumers/production
validation complete; routine teardown remains inside the task.

Final review checks A1–A5, actual required results, scoped paths, unchanged completed
safeguards and applicable ADR/memory mappings, not green syntax alone. Changed global
contracts/tools require a fresh Paseo session handoff after delivery, with checkout/revision,
current approval and loaded capabilities verified; no automatic restart or `/reload` instruction.
