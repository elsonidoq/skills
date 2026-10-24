# Owner-controlled review convergence — TinySpec

## Context and authority

**Outcome:** Coherence users can correct newly discovered material defects after a
successful review repair without abandoning completed delivery, weakening independent
acceptance, or authorizing an autonomous paid retry loop.

Source: the owner's review-convergence request and clarifications in the current planner
session. The owner selected **“Owner-authorized additional pair (recommended)”**:
“Ask after each later rejection; each approval permits exactly one scoped repair and fresh
full-range review. No automatic repeat.” The owner then selected **“TinySpec → Tasks →
Implement (recommended)”**. That selection authorizes source/task preparation and focused
planning checkpoints, **not implementation**. This source is preparation only: independent
specification review, separate tasks, parent review and combined current-content owner
approval remain outstanding. There is no standalone TinySpec approval gate.

The settled recommendation retains the first automatic repair. Every later blocking
rejection requires the actual owner to authorize exactly one further repair/review pair;
a further rejection returns to that owner again. Ordinary configured model usage is
already authorized by launch; this is a continuation-policy boundary, not a separate
paid application/test API consent request. No total round count guarantees acceptance.

### Evidence and bounded diagnosis

At source baseline `34a8c31edc774853ffa948451c155187bdd310df`:

- [`Engine._finish_reviews`](../../runtime/coherence_workflow/engine.py#L554) explicitly
  selects two reviews and one fixer; a second rejection raises `Blocked`.
  [`Store.review_dispatch`](../../runtime/coherence_workflow/store.py#L386) independently
  enforces ordinals 1–2 and rounds 0–1. Both must change together for new-policy runs.
- [`Engine.run_fix`](../../runtime/coherence_workflow/engine.py#L263), especially its
  prompt at lines 375–382, emphasizes the actionable list and original contracts, but
  does not explicitly ask for related failure-path/integrated-result examination.
  [`_review_value` / `_review`](../../runtime/coherence_workflow/engine.py#L460)
  accepts undifferentiated finding strings and rejects any nonempty findings list.
- [`test_review_chain.py`](../../runtime/tests/test_review_chain.py) deliberately checks
  the old stopping rule, saved reviewer repair, real scoped checks/checkpoints and fresh
  rereview. [`test_resume.py`](../../runtime/tests/test_resume.py) covers retained review
  heads and skipped completed checkpoints. These are existing offline fixture seams.
- [`parent_question`](../../runtime/coherence_workflow/pi_adapter.py#L22) sends ordinary
  question text; the [bridge question handler](../../.pi/extensions/coordinate-implementation-bridge.js#L113)
  tells the coordinator to triage and permits routine answers. Its
  [reply tool](../../.pi/extensions/coordinate-implementation-bridge.js#L260) correlates
  replies but does not distinguish owner-only continuation decisions. A generic
  yes/no question through this seam is insufficient to prevent coordinator self-consent.

The parent inspected one reported application history read-only: original task checkpoints,
a first rejection, one successful repair and a fresh second rejection. Source/diff inspection
showed the later missing database error-event handling and configuration-subprocess timeout
were already absent before repair, not introduced by it. Those support concrete crash/hang
risks, but no live reproduction was performed. This establishes a structural stopping cause
for that chain, not the cause of every reported failure; no other histories were inspected.
Private case paths, run IDs and raw evidence do not belong in reusable runtime prompts.

## Scope and governing constraints

Included: existing runtime review/fixer control, required history/recovery, review/repair
prompts and small result protocol, owner-only question routing, focused regression fixtures,
and synchronized operative documentation. Canonical delivery owners are
[`runtime/`](../../runtime/pyproject.toml), the
[execution skill](../../skills/coordinate-implementation/SKILL.md#review-and-acceptance),
[operating guide](../coordinate-implementation.md), and
[storage/interface owner](../coordinate-implementation-schema.md) wherever its described
interfaces change. Extend existing machinery, not a new engine or parallel ledger.

Excluded: application fixes, historical run restart/upgrade/backfill/migration, rewriting
old approvals/results or design artifacts, executor/model changes, new planning workflow,
universal test mandates, extra startup admission rules, deployment/push, credential changes,
automatic installs/reloads or an approve-until-green loop. No ADR or memory writing is
required by this source.

Carry these applicable accepted constraints into task-local REQUIRED verification and
worker/reviewer briefs, not merely a citation list:

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md): current
  launch authority supersedes historical planning-only wording for assigned execution,
  **not requirements, acceptance, real gates or permissions**. Task instructions remain
  authorization-neutral; launch does not grant automatic retries or unrelated work.
  Verify unchanged current-authority language reaches every repair/corrective brief.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md): retain shared
  ordinary scoped fixes and small isolated tests/databases/local setup, without repeated
  routine permission questions. Exclude global installs, credentials, deploy/push and
  unrelated deletion; authority never proves checks passed or permits blind expensive
  failure retries. Verify shared defaults/exclusions reach all affected roles.
- [Project memory](../../memory/MEMORY.md): routine transitions/completions and steering
  statuses must not wake the parent; questions and terminal success/error may. Test the
  new owner question wake-up without changing routine notification behavior.
- Preserve [task checkpoints](../../skills/memory-handling/references/task-commit-contract.md),
  actual REQUIRED/manual checks, explicit owned paths, unrelated staged/unstaged/untracked
  work, hooks/signing, original task checkpoints, historical rows and causal lineage.
  Unknown/live work, material scope/permission conflict or unsafe uncertainty stops the
  affected operation with the actual problem and concrete corrective action.

Selected future implementation executor: [`.pi/workflow-executor.json`](../../.pi/workflow-executor.json),
Terra/medium workers and fresh Sol 6.1/medium reviewers, unchanged. The saved TinySpec
source-producer assignment is not an implementation binding. New repair rounds continue
the rejecting reviewer using the configured reviewer model and existing scoped writer-tool
transition; the following acceptance reviewer must always be fresh and read-only.

## Approach and observable behavior

### 1. Classify findings without a taxonomy subsystem

Keep the existing small verdict object: `approved: boolean`, `findings: string[]`, adding
optional `suggestions: string[]` (absent means empty). `findings` remains the compatible
blocking list; old recorded verdicts retain their original meaning. Each blocker describes
location, concrete failure/impact and accepted requirement or material correctness,
security or data-safety basis. Suggestions cover optional hardening/style/improvements,
are reported honestly and do not block otherwise valid delivery. Do not reclassify real
crashes, hangs, target confusion, credential risk or false empty/unavailable observations
as optional merely because the application is small.

A valid positive verdict with no blockers completes, with or without suggestions. A positive
flag with blockers cannot approve; a negative flag with no actionable blockers is
nonactionable, not inferred approval or a reason to launch a fixer. Malformed types/results,
interruption or uncertainty stop without a fabricated verdict. Preserve safe deterministic
normalization of actual output only. Persist suggestions alongside existing outcome references
and expose them separately in safe owner history; do not reinterpret old finding strings or
put raw payloads/prompts/secrets into public/monitor records. This minimal protocol shape is
a design choice, not an owner-prescribed schema or a new severity catalogue.

### 2. Retain first repair; authorize every later pair

For new-policy runs the chain is:

- First independent review approves → complete directly.
- First actionable blocking rejection → existing automatic scoped repair, real required
  checks and focused checkpoint → fresh full-range independent review.
- Any subsequent actionable blocking rejection → report blockers and ask the actual owner
  whether to authorize **one** more scoped repair plus fresh full-range review, or stop.
  The question names the rejecting execution, original base/current reviewed head, original
  scope and effect of consent (one pair, ordinary configured model usage, no repeat grant).
- Affirmative actual-owner consent must be durably recorded **before** dispatch. Denial,
  cancellation, empty/unavailable/ambiguous answer stops honestly, preserves work/findings
  and launches no pair. A subsequent explicit resume may ask again for that still-current
  rejection if no grant exists; it must not treat the earlier denial as consent.
- Consume that single grant once for its assigned fixer and ensuing fresh reviewer.
  Approval completes; another actionable rejection asks again. Failed/nonactionable/
  malformed/uncertain stages are not new blocking verdicts and cannot acquire an automatic
  replacement pair. Never approve by exhaustion, skipped review or relabeling blockers.

Refactor existing chain selection around the last eligible persisted stage, not `reviews[1]`
or a raised numeric cap. Validate causal order and grant at the dispatch boundary as well as
in the engine; unsupported transitions report the affected stage and resolution. No
background model decides transitions. Correctable required-check/checkpoint errors may
retain existing **reasoned same-stage** correction behavior with actual failures and
rerun checks; this is not a new round, an unchanged expensive replay, or permission to
bypass hooks/signing. Unrecoverable errors stop.

Extend the existing question transport with a narrow owner-only continuation marker and
correlated decision context. Direct interactive terminal input remains owner input. For an
attached bridge, its notification must explicitly require the receiving parent to call its
actual owner-question capability (registered `ask_user`), relay only that actual answer, and
never apply routine coordinator triage/self-consent. Carry the owner-only marker through
pending request/reply handling so this decision cannot silently use a routine reply route;
missing actual-owner question capability/answer stops with a corrective diagnostic. Keep
routine technical questions autonomous. Do not add external identity/receipt services or
claim a model-mediated reply is cryptographic proof of human intent. Focused bridge fixtures
must observe owner-only routing, not merely matching question prose.

### 3. Broaden repair reasoning, not scope

Every repair prompt asks for a concise correction plan, examination of directly related
failure paths and the integrated result against original acceptance, then bounded fixes
and applicable checks. This includes handling adverse states adjacent to the finding,
not just editing listed lines; it is not speculative full rewrite or optional feature work.
Retain original contracts, owned paths, current launch/routine authority and paid-API
exclusions. Material trade-offs, substantial scope/complexity/verification expansion and
actions outside authority escalate rather than silently expanding the grant.

The runner owns check execution and focused commits. A successful fixer is only a repaired
checkpoint, never independent acceptance. Each subsequent reviewer uses a new context with
read/search-only tools and reviews **original base → actual final repaired head**, including
integrated regressions, not last-list compliance. Retain explicit rejecting-review → fixer →
fresh-review identities, real ordinals/rounds, checks, checkpoint/parent and exact ranges.
Optional monitoring/metrics extend existing positive ordinal support where needed and remain
nonblocking; they cannot authorize dispatch. Separate metrics-artifact SHAs never become
claims that unreviewed application code passed.

### 4. Durable policy and interruption recovery

Use the existing private `execution_run_inputs.authority` JSON to retain a named new review
policy at new-run start, before dependent execution; e.g. `review_policy: "owner-pair-v1"`.
Absence selects the original two-review/one-fixer lifecycle on resume, never today's default.
Preserve existing rows and historical outcomes in place; no historical upgrade is included.
An unknown policy stops affected continuation rather than guessing. New starts durably select
the new policy; ordinary resume uses that run's retained policy, inputs, executor and base.

Use existing append-only `execution_history` for single-pair authorization facts: stable grant
identity, actual-owner affirmative decision, rejecting execution, exact reviewed base/head,
original scope reference and assigned pair identities. Retain the decision fact, not a raw
question/answer transcript. Consume the grant and reserve its fixer atomically under the
existing writer lock/SQLite transaction; derive eligibility of its one reviewer from the same
grant and successful fixer. Do not introduce another state store. Preserve existing required
write reconciliation; persistence failure cannot launch a dependent call. Status/history must
show the selected policy, actionable rejection, authorization/consumption and next eligible or
blocked stage without exposing private sessions or owner conversation.

On explicit recovery, reconcile saved stage/invocation and actual check/commit facts first:

- Authorized but not dispatched: retain the exact grant, do not ask/pay twice; reserve only
  its original pair if the rejection/range/scope still matches. Target drift stops affected
  continuation for inspection/renewed authority, not a blanket dirty-tree admission gate.
- Reserved but provably not invoked: dispatch only that reserved stage once. Persist call
  start before provider invocation. A crash in the start/call gap is uncertain, not proof no
  call happened; invocation-started-without-terminal-outcome cannot be automatically replayed.
- Returned repair but incomplete checks/checkpoint/outcome recording: reconcile retained
  owned-path/check/commit facts; recover a matching actual SHA without recommit or rerunning
  the fixer. Missing/uncertain effects stop for inspection, not another paid call.
- Successful fixer with reviewer not yet dispatched: dispatch its one eligible fresh reviewer,
  not another fixer. Completed reviewer with missing run-finalization: reuse that verdict and
  exact reviewed head, never accept later incoming commits or call the provider again.
- Known failed fixer/reviewer/check/commit: inspect its actual cause and invocation before
  any specifically authorized targeted continuation. Consumed grants never reset on resume;
  unknown cause, live child, unclear scope or uncertain completion stops. Preserve partial
  work, all prior failures and completed task checkpoints.

Rollback is an explicit code revert for future launches, not rewriting retained policy or
history; runs with an unsupported retained policy stop with an actionable version limitation.
Changed bridge/global skill activation in Paseo requires a fresh-session handoff verifying
checkout/revision/current approvals/loaded capabilities, never an owner `/reload` instruction
or automatic restart. Installation/global activation and live workflow proof remain separately
gated, not authorized by source preparation.

## REQUIRED acceptance and verification for task generation

These are behavior/check needs, not implementation tasks. Carry each applicable criterion,
pass condition, smallest check and permission boundary into task-local REQUIRED briefs.
Use existing mocked adapters/fixtures, temporary Git repositories and real SQLite reopen tests;
**no live provider calls solely for regression** and no historical application replay.

| ID | Observable pass condition and smallest sufficient evidence |
| --- | --- |
| A1 | A findings-free first review completes directly; ordinary first rejection receives one repair/checkpoint and fresh accepted rereview. Extend actual engine fixtures, asserting provider-call counts, reviewer freshness/read-only tools and exact original-base→final-head range. |
| A2 | A new blocker after repair asks the actual owner. One yes permits exactly one pair; a further rejection asks again; no/empty/cancel/unavailable stops with retained blockers and zero unapproved calls. Engine plus SQLite reopen fixtures observe grant-before-dispatch, atomic single consumption, causal IDs and refusal of duplicate/wrong-rejection/range/scope grants. No blocker can become approval by exhausted rounds. |
| A3 | Suggestions-only positive review completes and reports suggestions; blockers remain blocking even with a contradictory positive flag; false-without-blockers and malformed verdicts stop without fixer/approval. Focused parser/outcome/status fixtures retain legacy finding semantics and safe output. |
| A4 | Repair briefs explicitly examine adjacent adverse paths/integrated original acceptance without scope expansion. Assert prompt delivery, selected reviewer model, current-authority and shared-permission/exclusion constraints from ADR-0003/0004 in initial and corrective repair prompts. Permanent lifecycle fixtures exercise an adjacent failure correction and an outside-authority stop; prompts/mocks are not live model-obedience proof. |
| A5 | Reopen at authorization-before-dispatch, reserved-not-started, uncertain invocation, repair-return/check/commit/result gaps, fixer-complete-before-review and review-complete-before-finalization preserves one grant/pair and exact verdict/range without duplicate provider calls/commits. Focused engine/store recovery fixtures plus real disposable-Git checkpoint reconciliation prove known effects retained and unknown effects blocked. Known failed calls never blind-retry; actual failed REQUIRED checks/hooks remain failures until reasoned scoped correction and real passes. |
| A6 | Historical/no-policy fixtures retain original lifecycle and cannot acquire later pairs or altered verdict meaning; old rows/task checkpoints remain readable and unchanged. New starts persist their policy and resume cannot silently switch it. Test existing store/CLI seams, including unknown-policy diagnostics. |
| A7 | Attached owner-only continuation is routed to actual owner questioning, never coordinator routine self-answer; direct terminal yes/no remains usable, unavailable owner input stops. Extend adapter/bridge offline tests for marker propagation/correlated pending reply and rejection of routine-route answers. Preserve routine question autonomy, notification wake-up boundaries, paid-API consent and safe text projection. No external receipt machinery. |
| A8 | Required project checks, owned-path limits, unrelated staged/unstaged/untracked work, hooks/signing, actual checkpoints and original lineage survive multiple authorized pairs. Reuse/extend focused Git/review fixtures, including safe history/status and optional-monitor/metric-gap nonblocking behavior. Synchronize operative skill/operating/schema docs so old limits describe historical policy only, with selected-config and Paseo fresh-session guidance intact. |

Repository-local dependencies are sufficient: Python >=3.10, pinned PyYAML 6.0.3,
standard SQLite/Git and the tested Pi SDK 0.87.1 host. Reuse the
[operating owner's setup/verification guidance](../coordinate-implementation.md#setup-and-verification),
[`runtime/pyproject.toml`](../../runtime/pyproject.toml) and
[`runtime/pi-host/package.json`](../../runtime/pi-host/package.json). No new dependency/API
selection or external internet research is needed for this known state-machine change;
local implementation and existing tests establish the affected interfaces. No separate
prototype is justified: permanent tests of actual helpers and composed lifecycle/reopen
boundaries directly address the consequential authorization/durability risk. Complete these
proofs before downstream reliance on the changed lifecycle; retain them as regression tests.
A failed/unrun REQUIRED proof blocks its dependent acceptance, not unrelated work.

Implementation verification should run focused `unittest` review/resume/authority/checkpoint
modules under `PYTHONPATH=runtime:runtime/tests` with the prepared Python, plus relevant
`node --test runtime/tests/test_bridge.mjs runtime/tests/test_host.mjs` fixtures where changed.
Use `git diff --check` and actual local link/content inspection for changed docs. Broader
existing regressions are appropriate for touched consumers but not a new universal startup
gate. Report actual commands and PASS/FAIL/NOT RUN; mocks do not establish provider behavior,
human participation in a live bridge, or defect-free application code.

## Risks, limits and next boundary

The new policy removes a structural dead end, not reviewer blind spots or legitimate rejection.
The owner may repeatedly elect to spend on another pair, but the runner never does so on its
own. Scope drift, missing authority and uncertain paid-call/commit outcomes intentionally
remain stops. Model-mediated actual-owner routing needs explicit transport/prompt tests and
honest live-evidence limits, not invented identity attestation.

Under the new policy a newly launched chain matching the inspected example would ask after
its second rejection; yes would permit one scoped repair of the remaining crash/hang defects
and a fresh review of the original base through repaired head. Another rejection asks again;
no answer stops. The historical failed chain and its commits remain unchanged and cannot use
this policy without separately approved future migration, which is excluded.

No material product decision remains unresolved for this source. Implementation details may
use the smallest equivalent compatible records/helpers; material discoveries return to the
existing owner/review gates rather than expanding acceptance by assumption. Next: planner's
fresh independent read-only intent review of this exact source, then separate executor-sized
tasks and combined approval. Source production is not implementation readiness or feature
acceptance.
