# Workflow completion and recovery — implementation tasks (#30)

## Source and executable handoff

Requirements truth: [TinySpec](workflow-completion-recovery-tinyspec.md), A1–A5, read
entirely through the task-generation direct adapter. [Executable JSON](workflow-completion-recovery-tasks.json)
owns complete work instructions, explicit paths and task-local REQUIRED checks; this is
its concise presentation. No Standard plan or SDD requirements input is introduced.

### Preparation, review and approval record

Correction baseline: clean branch `planner-github-com-elsonidoq-skills-30`, HEAD
`f25fcc847bec1a332e4909464097b82e06c382c1`. Current source SHA256:
`aa89afc2f99755a0895368ff420a77dd1c0caed26895ca93099d6d3f7c6a7314`.
Parent inspected the actual upstream source/index correction and preservation boundaries.
Fresh independent affected-source review `c47d0154-bb4d-4e21-a481-d3164b6f62b0`
returned explicit **zero findings**; parent verified the source digest unchanged afterward.
That review covers the current source, not these task revisions or implementation acceptance.

Historical initial task checkpoint `b25969be7e29426f68e0b912ad5ff0e9fc7fe072`
used source digest `71e20f2bf47d9860d5de38408248c5ccc16fdfed6e700bcd6cce6bd4e84daab9`
and zero-finding source review `89c7c394-951b-410e-a36b-a6c68b899336`; those apply only
to that old identity. Git retains the original task/source history. Owner selected TinySpec
via `ask_user`, then explicitly authorized bounded corrections to confusion/overcomplication
and focused planning checkpoints. Saved `tinyspec-tasks` producer assignment remains
`openai-codex/gpt-6.1-sol`, medium, separate from runtime bindings.

Combined approval was **CANCELLED / not granted**. Affected task review/parent inspection
and renewed combined owner approval remain pending; implementation is **not approved**.
A planning checkpoint supplies none of those approvals. Final combined approval starts
coordinator preflight by default; no launch occurs here. No implementation proof, live
workflow/provider call or Cerca continuation ran during this task correction.

Revision disposition: A1 now distinguishes runner check execution/checkpoint/review dispatch
from worker semantic/manual evidence and independent judgment. Old T004/T005 are one bounded
A4 handling outcome, T004; no speculative facts producer or persistence inventory remains.
The supporting-guidance ID T006 is retained to avoid relabeling its history; T005 is removed
from this revised unlaunched list, not a runtime task mutation. A4 tests target the demonstrated
sequence and one uncertain-call control; unchanged grant/ownership safeguards reuse applicable
evidence. T006 is only a small example/text-contract fixture, not a generic validator.

## Shared worker and reviewer context

Producer itself re-read the exact selected executor JSON before decomposition:
`/home/dev/.paseo/worktrees/0zfm1a0e/unlucky-flamingo/.pi/workflow-executor.json`.
Pass that absolute path unchanged: worker `openai-codex/gpt-5.6-terra`, medium;
fresh reviewer `openai-codex/gpt-6.1-sol`, medium. Do not substitute producer settings
or historical executor files. These settings are not task eligibility metadata.

Binding source constraints below are carried **verbatim** from its governing section
(relative links share the same directory base). Apply each task's local REQUIRED mapping
at its changed seam; briefs include those observables, paths, dependencies and material
permission boundaries, not links alone:

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md): current owner-authorized launch governs assigned implementation over historical planning-only labels, including corrections/resumes; tasks stay authorization-neutral and temporary phase status stays in approval records. Preserve acceptance/manual/safety gates and escalate material authority conflicts. Returned execution is not acceptance. Validate unchanged authority delivery alongside the changed completion prompts; do not add a routine approval question or rewrite historical artifacts.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md): reuse shared `_ROUTINE_AUTHORITY` for ordinary scoped fixes, small isolated tests/databases/local servers, necessary local/in-project setup and task-artifact lifecycle without repeated approval. Preserve actual owner-imposed limits/manual gates, paid application/test API scope, credential/security/data/external boundaries, global-install exclusion, and prohibitions on deployment/push/unrelated deletion. Unknown bytes are not adopted or deleted. Authority is not proof; check results remain actual results. Validate these limits in affected initial/corrective/resumed prompts, not a new permission layer.
- [Project memory](../../memory/MEMORY.md), read in full, contains only inline owner guidance, no technical gotchas. Applicable guidance verbatim: “Handle routine technical decisions autonomously; ask the owner only for product decisions or material scope creep. Preserve mandatory explicit permission gates rather than treating this preference as consent. When the owner requests correction-only review, assess the correction and affected behavior instead of re-reviewing areas already confirmed correct.” Also: “Routine task transitions/completions and steering-status updates must not wake the parent agent or require acknowledgment. Only agent questions and terminal workflow completion, whether success or error, should trigger a parent turn.” Recovery diagnosis is routine coordinator work; owner-only additional-pair grants remain owner-only. No extra transition acknowledgments. Correction-only review guidance does not remove the executable runner's mandatory fresh full-original-range final review.
- [AGENTS](../../AGENTS.md) and [constitution](../../.specify/memory/constitution.md): preserve focused verified checkpoints, task-owned paths, unrelated staged/unstaged/untracked work, hooks/signing, independent final review and historical rows. AGENTS' explicit owner-controlled concurrency direction supersedes older blanket sole-writer text; coordinate overlapping ownership and respect real live-writer locks, rather than add a concurrency prohibition. Global assets remain portable. Changed global skills/tools in Paseo need a fresh-session handoff, not `/reload` or automatic restart.


Shared exclusions: no Cerca execution/recovery/application fixes, reopening completed #23–#27,
redoing #26, #5 unchanged-check loops or duplicating delivered #28. No framework/state machine,
outcome schema, migration/history rewrite, retry/permission service, runtime task/path mutation,
automatic ownership adoption, extra startup rules, quotas/invented limits, blanket concurrency
ban, automatic install/auth/reload, push/deploy or mandatory paid/live proof. Preserve current
requirements and actual safeguards; historical records and memory/STATE remain intact.

Use existing `runtime/tests/fixtures/support.py` disposable Git projects, actual adapter
subprocess fixtures in `test_engine.py`, and existing resume/review/grant fixtures. Ordinary
tests, relevant current operating/schema docs and routine teardown stay with the outcome.
Workers never stage/commit. Runner executes/reruns configured commands, inspects owned diffs,
checkpoints and dispatches fresh independent review; this does not transfer all semantic/manual
acceptance or verdict judgment to the runner. Worker-owned failed/unrun requirements remain
blockers. Routine technical correction and small isolated fixture work require no new consent;
real manual/external/paid/security/data gates remain at their actual actions. Coordinate
shared-file overlaps and respect actual live-writer locks, without invented dependencies.

## Bounded outcomes

- [ ] T001 Clarify worker completion versus runner check execution, checkpoint and review dispatch (A1).
  - **Depends**: none
  - Shared prompts/tool description, captured existing authority, actual stage order and
    completed/no-change/correction controls; explicit unsuccessful truth stays intact.
- [ ] T002 Preserve actionable unsuccessful task/fixer explanations (A2).
  - **Depends**: none
  - Actual host → adapter → terminal/history, fallback/success/invalid controls and safe
    projection; no new reason schema, acceptance inference or retry permission.
- [ ] T003 Attribute checkpoints within full original integration review (A3).
  - **Depends**: none
  - Actual checkpoint/Git parent/path attribution separates unrelated/unknown context;
    composed task/repair rereview keeps full original diff and causal interactions visible.
- [ ] T004 Deliver inspected actionable handling of the demonstrated settled unsuccessful fixer (A4).
  - **Depends**: T002
  - Consume the returned explanation, inspect cause/call/effects and correct the technical
    gap through the smallest supported path. An alternative authority limitation must cite
    an actual binding rule and supported next action, not a missing branch or routine handoff.
    Preserve failed truth, grants/ownership, uncertain no-replay and independent acceptance.
- [ ] T006 Add a small supporting-test/harness ownership reminder and example (A5).
  - **Depends**: none
  - Canonical recipe plus existing text-contract fixture; preserve executable command/neutral
    wording and unchanged claim/handoff controls, without generalized closure validation.

Only causal edge: `T002 → T004`, supplying the unsuccessful explanation consumed during
diagnosis. A4's diagnosis, any missing fact actually consumed and its supported handling are
one checkpointable outcome for the selected worker, not a persistence subsystem plus consumer.
No independent facts deliverable is evidenced. T003 attribution and T006 authoring remain
independently useful and unnecessary as recovery prerequisites. Shared engine/docs/test paths
need coordinated scheduling; the sequential runner provides it without extra graph edges.

## Verification and handoff limits

No prototype is warranted: existing production-helper seams support permanent focused tests.
T001 observes worker return → real check → checkpoint → fresh review; T002 observes framed
transport → terminal/history; T003 observes actual Git attribution across repair rereview;
T004 observes settled failure → diagnosis → supported handling and one uncertain no-replay
control, including retained-resume/restart where relevant. T006 observes small-example guidance
delivery only. Scripted host/model/reviewer responses prove mechanics and instruction delivery,
not autonomous judgment, owner consent or live obedience. No paid/provider proof is required.

REQUIRED argv commands occur only in existing `required[].check` fields. Named selectors
already exist; extend those focused seams rather than invent infrastructure. Semantic criteria
remain prose. After work, run specified commands and report actual results; missing/failed/unrun
proof is not a pass. Reuse unchanged applicable evidence, not an assumed result; rerun only
invalidated/changed-seam checks or necessary exposed safety coverage. No new first/additional-pair
matrix or repeated proof of unaffected safeguards. Source constraints and actual exposed
security/durability/grant protections remain binding. Report unrelated baseline failures separately;
do not weaken assertions or fix unrelated code. In particular the reported unchanged full-planner
text assertion failure is not this delivery's target or a reason for full-suite retry loops.

Changed scope/acceptance/authority returns through existing review/approval boundaries; disproof
blocks affected reliance, not unrelated outcomes. Historical missing facts stay specific gaps,
not migration or guessed ownership. Retain disposable evidence through its consumers/validation;
teardown belongs inside the outcome. Final review checks A1–A5 and actual results, precise task
ownership, neutral instructions, applicable ADR/memory constraints and retained #23–#28 safeguards.
Changed global contracts/tools in Paseo need a fresh-session handoff verifying checkout/revision,
current approval and loaded capabilities, not `/reload` or automatic restart.
