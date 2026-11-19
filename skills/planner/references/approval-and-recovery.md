# Approval and Recovery Contract

## Interactive design agreement before detail

In TinySpec and Standard, including direct, standalone and resumed entry, produce a
project-owned self-contained interactive HTML high-level design and obtain explicit owner
design agreement before detailed architecture plan production or continuation. Discover the
page destination from the adopting project's routing and existing feature artifacts; use
an existing design page when present. No renderer, generator or framework is required.
Preparation authority permits the page, not agreement or implementation.

The report helps the owner judge how the architecture delivers the required properties
and whether the design is proportionate. In the producer brief, ask for a schematic
with named system components as boxes and labeled arrows showing what they exchange.
Distinguish reused components from changes and additions. Before presenting the page,
check that it shows how the components provide each important property and, for each
material addition, what the existing design lacks and what tradeoff the addition brings.

The page covers approach, interfaces, dependencies and material risks. Each clickable
component box opens popup executive bullets for purpose, inputs/outputs, boundaries and
significant choices. Executive bullets below the schematic explain the goal, relevant
supported properties, tradeoffs/limits and necessary context without unverified capability
or performance claims. Distinguish workflow approvals from data flow and proposed/unimplemented
behavior from implemented behavior. Require pointer and keyboard activation, readable mobile
layout, Close and Escape dismissal and focus return to the opener. Page controls never
simulate authorization.

Present the actual current page and its executive explanation to the owner before asking
for design agreement. Retain the shown page/content identity, actual answer, scope and ordering
in existing approval conventions. Page creation, opening/clicking, silence, no answer, denial
or cancellation is not consent: stop affected detailed planning. Significant design changes
update the page and renew agreement before affected planning resumes. Routine mechanics remain
autonomous; material unresolved choices need actual answers or explicit bounded deferral.

Keep requirements approval, design agreement and final implementation approval distinct.
One explicit settled grant can cover several outcomes only when it actually covers that
shown current content and scope; record each outcome without repeating the same question.
TinySpec needs no new standalone requirements-approval gate: draft its what/acceptance and
high-level page first, return for design agreement, then resume its detailed how. Standard
retains specification approval, then page/agreement before setup-plan or detailed artifacts.
Legacy/resumed planning preserves valid grants and stops only affected continuation at the
earliest invalid boundary; historical missing evidence is not invented or a new runtime
startup rule. Current authorized implementation and shared routine permissions remain valid.

Static/carrier and DOM tests are supplemental, not actual owner/model or real-browser proof.
Retain actual observations and NOT RUN limits in existing returns/evidence; changed global
carriers require a fresh session to verify checkout, revision, current approval and loaded
capabilities before relying on live examples. No automatic reload/restart.

## Executive brief before approval

At EVERY artifact-approval gate, including corrections/renewals and applicable
adoption/documentation-plan approvals, present an owner-visible executive brief as
concise content-first bullets in assistant text before calling `ask_user`. No universal
total-bullet cap applies. Do not
replace it with paragraphs, artifact links, a delegated report, or `ask_user.context`.
A brief only in tool arguments or after the question is insufficient. Cover all of:

- Intended outcome and concrete included scope.
- Every actual ordered plan stage separately with its identity and meaningful outcome,
  when a plan is part of this approval.
- Every actual task ID separately with its meaningful outcome in execution order,
  when tasks are part of this approval. Never truncate beyond six, merge IDs/stages,
  use catch-alls or empty headings. TinySpec has no plan; specification-only approval
  requires no nonexistent tasks. This adds no plan approval gate.
- Exclusions and implementation boundaries.
- Important settled decisions and material alternatives resolved.
- Risks, unresolved gates and intentional deferrals.
- Actual review/validation results, including failures and UNAVAILABLE/NOT RUN checks.
- Exact artifacts/current content and what approval authorizes: preparation,
  specification-to-planning, or implementation of the reviewed scope; name the next
  phase that starts automatically after approval and any explicit planning-only boundary.

Renewals regenerate the complete brief from current artifacts, not the previous brief.
Be concise and accurate; headings alone are not evidence. Permit approve, withhold
approval/request changes, and cancellation. Do not treat “looks good except…” as full
approval. Missing question capability stops an artifact approval; do not substitute
inferred consent. Persist affirmative answers and their scope/content evidence in
existing artifact or decision conventions after authorized artifact production.

After affirmative approval, immediately continue to the next authorized phase. Do not
ask for a second routine continuation approval or end merely with “approved/ready.”
Final planning approval starts `coordinate-implementation` and its preflight in the
same session unless the owner explicitly requested planning-only or a separate-session
handoff. The brief and approval question must communicate that scope before consent;
older preparation-only approvals never imply execution authorization. Missing capability,
new material gate, denied/ambiguous answer or an explicit owner boundary still stops.
Ancillary adoption/documentation approvals authorize only their own stated bounded writes,
not unrelated implementation.

## Transition and invalidation table

| Event | Consequence |
| --- | --- |
| Owner chooses depth | Preparation authorization only; persist then immediately start selected source production |
| HTML high-level design ready | Show current page and obtain explicit design agreement before detailed how/plan production or continuation; no page interaction is consent |
| Significant design change | Update page and renew affected design agreement before affected detailed planning |
| TinySpec ready | Run fresh independent read-only specification review for user-intent fidelity before separate tasks; no intermediate approval gate |
| TinySpec specification review complete | Parent evaluates findings, owner resolves material decisions, source producer corrects and parent inspects; zero/resolved findings proceed to tasks, unresolved material intent gaps stop task generation |
| TinySpec/tasks reviewed | Bullet brief then combined source/task/scope approval; immediately start coordinator unless explicitly planning-only |
| Standard spec ready | Complete required ordinary clarification and parent inspection, then run distinct `spec_review`; do not approve or plan yet |
| Standard spec review returns zero | Skip question interaction; bullet brief then existing specification approval; immediately start planning |
| Standard spec review has findings | Ask one material question at a time; originating producer incorporates answered decisions and parent inspects before the existing specification approval |
| Standard plan/tasks reviewed | Bullet brief then overall approval; immediately start coordinator unless explicitly planning-only |
| Denied, cancelled, timed out or ambiguous answer | No downstream production requiring that approval or implementation; preserve pending correction |
| Request/source/decision changes | Recheck scope, traceability and affected downstream artifacts/review; material scope changes need owner decision. Source/spec/context drift invalidates only its affected review, correction, approval and downstream work, then resumes at the earliest affected boundary. |
| Approved specification content changes | Renew specification approval before proceeding beyond the affected Standard stage |
| Plan/tasks change after final approval | Re-review affected evidence and renew final approval |
| Any renewal | Present a new bullet-list executive brief before `ask_user`; old brief does not cover changed content; after approval immediately resume the affected stage |
| Fresh session/resume | Read artifacts AND linked external decisions/approvals; verify current content, scope and review; return earliest invalid gate |

Use exact revisions, external snapshots/digests, or clearly bounded approved sections
that permit actual comparison. Avoid recursive self-hashes. A completion checkbox or
`approved` label is not authorization. Expected task status/evidence updates during
execution do not by themselves change the approved task contracts; changed scope,
acceptance, dependencies or instructions do. Do not waive drift merely by calling it
cosmetic: verify the authorized content remains equivalent and record that comparison.

Unanswered `spec_review` questions retain their originating source/spec/context, alternatives,
scenario, consequences and owner rationale. Ask one at a time and remove later queued questions
that an earlier answer resolves. A cancelled or unanswered material answer stops only affected
planning; no recommendation, automatic deferral, clarification-taxonomy rerun, default, or
rereview releases it. Neither path progresses with unresolved material intent gaps. Zero
findings go directly to tasks for TinySpec or the existing specification approval gate for
Standard. Findings are not reviewer approval; necessary substantive corrections remain with
the source producer. No separate TinySpec approval or automatic rereview loop is added.
Delegate uncertain or substantive artifact corrections to that originating producer context
when supported and suitable; otherwise use a fresh bounded correction delegate.
No parent artifact authoring or substantive task-level or upstream repair, including legacy recovery.
Missing, unusable or unauthorized delegation stops substantive correction; no inline/local
fallback or full transcript handoff. Mechanical repairs follow the contract below.
Resume that correction context when supported; otherwise hand off durable answers and
constraints. Do not regenerate answers or silently apply recommended defaults.

## Bounded mechanical corrections

Ordinary drafting is not submitted-artifact correction: an assigned producer may revise,
shorten and mechanically validate its own unsubmitted output within authorized scope without
a supervisor decision. This does not permit upstream requirement changes, self-certification
as independent review, or bypassing review/approval. Once submitted, defects follow the
producing workflow's review/correction route below.

A coordinating parent may directly repair typos, formatting or broken links only after
comparing the actual before/after diff and proving unchanged requirements, decisions, scope,
dependencies, acceptance and approval validity. Record the equivalence comparison in the
existing return/approval convention and retain comparable current-content evidence for the
corrected bytes; never silently reuse a stale digest. A cosmetic label alone is insufficient.
If equivalence or approval validity cannot be established, direct repair is not permitted.
Uncertain or substantive changes return to suitable originating producer context or a fresh
bounded correction delegate, affected review and renewed approval. This applies to task-level,
upstream and legacy corrections alike, not fresh creation: every new artifact still uses a
separate fresh bounded-context producer. Missing, unusable or unauthorized delegation stops
substantive work; no inline/local fallback. The independent reviewer never becomes the producer.
Authorized retained repairs follow the shared
[task-commit contract](../../memory-handling/references/task-commit-contract.md).

## Legacy checkpoint mapping

Compatibility repairs are owned by planner, not retired skills. Original evidence is
still required; do not fabricate history or use a convenient origin to bypass gates.

| Origin/state | Planner checkpoint and preserved requirements |
| --- | --- |
| `requirements-manager`, approved | Validate durable original requirement/source (possibly inside tasks), tasks, review and explicit current scope approval; no separate TinySpec/plan/SpecKit imposed |
| `requirements-manager`, partial/stale | Preserve existing source shape; resolve missing decisions, produce/review affected tasks via direct adapter, brief and renew combined requirement/task/scope approval |
| `epics-manager`, approved | Validate original source, spec, plan, tasks, SpecKit stage evidence, independent review and both current approvals |
| `epics-manager`, approved spec awaiting plan | Continue mapped Standard plan stage without forcing a new path choice; retain valid spec approval and full adapter safeguards |
| `epics-manager`, missing/stale spec approval | Return Standard specification/clarification checkpoint, brief and approve current spec before plan |
| `epics-manager`, missing/stale plan/tasks/review | Return earliest affected Standard stage and renew affected approvals; never downgrade origin to direct tasking |
| Other documented producer | Follow that producer's documented source/task/authorization gates; no imposed Standard placeholders |
| Ambiguous/conflicting origin | Resolve provenance with owner before production or implementation |

Old source documents labelled Epic are legacy inputs, not a new required planning
concept. New planning uses the explicit depth choice; legacy repair does not invent
historical route-selection records. Missing runtime capabilities still block affected
stages even with otherwise valid approvals. No installing/simulating missing SpecKit.

Existing approved tasks with inadequate REQUIRED contracts block dispatch and return to the
producing review/approval gate for correction and renewed affected approval. Preserve original
source provenance, valid approvals and task-embedded legacy requirements; do not fabricate
historical contracts or add requirements retroactively under old approval.

## Executable intake handoff

Preserve original source/approval origin and whole REQUIRED maps in both human/machine
handoffs. Planner producer assignments remain separate from the owner-launched parent binding
and the selected project's execution configuration; do not add planning intent or compatibility
assessment intake. Known separately chargeable action gaps stop that action; ordinary model
tokens have no financial gate. Current-content scope/approval remains mandatory. Reconcile
active/unknown legacy writers first; preserve STATE/custom/history/gotchas without automatic
conversion. Planning-only final approval never launches implementation; later explicit
implementation scope and all original gates remain required for that origin.
