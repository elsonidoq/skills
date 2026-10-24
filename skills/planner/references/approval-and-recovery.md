# Approval and Recovery Contract

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
