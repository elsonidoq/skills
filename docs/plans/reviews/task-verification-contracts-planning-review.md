# Task verification contracts — TinySpec planning review

## Verdict and current content

**READY for planner's combined current-content approval; approval PENDING.** No material
planning blocker found. This is planner-owned source/task review, not independent
implementation/final review, implementation authorization or feature acceptance.
No source/task correction was necessary; unchanged artifacts create no empty commit.

- Preparation/review baseline: clean `main`, HEAD
  `692ea3e53671f3a92f46ae5a7b9e965d9d7dc87d`; Git identity was usable and inspected before writes.
- [Source](../task-verification-contracts-tinyspec.md) SHA-256:
  `266820b3b8aa8dfe8b2322f315659bf8b91fc4f6b5352c0d68a251316cc247ef`.
- [Tasks](../task-verification-contracts-tasks.md) SHA-256:
  `db1c467a93f89dede0e2d0501f4e4bb4fc499d6967fe4e6000b259822d1d0a2c`.
- Earlier source/task baselines and checkpoints remain original provenance, not assertions
  that the present HEAD is those revisions. STATE.md records an earlier completed run;
  it is not approval for this preparation and was not changed.
- Exact owner-selected delegated planner-review profile:
  `openai-codex/gpt-6.1-sol:medium`. THIS invocation observes `PI_MODEL=gpt-6.1-sol`;
  actual provider and effort are unknown here. Earlier parent/source observations do not
  establish this invocation's effort. No delegation, substitution or runtime probe performed.

Selection assessment: residual reasoning is medium (cross-owner causal/acceptance trace);
agentic/tool depth is bounded local reads, Python and Git; weakest verification blind spot is
future runtime obedience, which static instructions cannot prove; scope/coupling is the
existing producer→batch→audit→repair→evidence seam; failure cost is reversible preparation,
with scoped checkpoints; approved project guidance is **none**. Family rationale: retain
owner-selected Sol for coupled semantic review. Effort rationale: retain selected medium
for bounded traceability/proportionality analysis. These are planning rationales, not
implementation-task allocation or proof of observed effort/support.

## Inspected claims and dispositions

Read AGENTS.md, constitution I–VI, full empty gotcha index, empty approved-guidelines owner,
planner review/proportionate-validation and linked approval/recovery/research/SDD contracts,
task-generation semantics and shared checkpoint/coordination contracts. Ordinary history
was not loaded. The same run SUMMARY/index was read only to preserve/update its checkpoint
record, not to infer routing lessons. Local dependency owners and REQUIREMENTS.md Runtime
retain pi 0.87.x (tested 0.87.1), pi-subagents 0.73.1 and pi-ask-user 0.15.1. No new API,
version-sensitive design or external research need exists; local reuse is sufficient.

| Finding | Actual supporting owner / disposition |
| --- | --- |
| Existing architecture is largely satisfied, not a redesign target | `skills/task-generation/SKILL.md:58–113` already defines stable criterion/check/evidence/gates, adapter continuity and producing-gate return. Planner Proportionate validation and Selected production/stage handoffs already preserve these contracts and approval boundaries. Coordinator graph/selection/union/integration/final-review sections already preserve coherent sequential batches, complete union, cheap audit, diagnosis-first repair and independent review. **Verified / retain.** |
| Real acceptance gap is semantic proof, not just vocabulary | `test_batching_contract.py:215–247` gives both tasks the generic criterion `shared check passes`; `simulated_audit:290–315` recognizes a hardcoded `both invariants satisfied` string and returns only accepted/blocked. It does not test task-specific criterion relevance or revision/environment attribution. Coordinator Execute and Integrate checks concrete outputs but does not yet articulate the proposed three per-item dispositions/relevance distinction. T001/V3 changes both carriers and practical sample proof. **Verified actual gap / adequately tasked.** |
| Routing extension belongs in the existing rubric | `batch-routing.md` Assess all six factors already covers weakest blind spots and closed design; its symbolic options allow moderate residual reasoning with strong oracles. Explicit implementation difficulty, oracle cost and combined practical verification are not fully demonstrated. T001/V2 supplies bounded contrasting cases and operational wording, not scoring or a second router. **Verified incremental gap / preserve existing strengths.** |
| Repair/evidence extension must preserve valid work | `simulated_repair_brief:405–417` already copies the complete contract and prior state; existing repair tests preserve producer evidence. They lack explicit current relevant SHA/environment and exceptional safe-clean-retry proof. `simulated_feedback:476–482` has selected/observed and first/final fields, but lacks item dispositions, proof/escalation/next-selection attribution. T001/V5–V6 adds those exact seams; original contracts/work/attempts remain. **Verified / adequately bounded.** |
| Checkers are causal consumers, not arbitrary assurance expansion | `check-planner-workflow.py:190–256, 407–435, 494–527` checks producer/adapters, coordinator approval/checkpoint/routing and coordination evidence; `test-planner-workflow.py:33–72, 225–252` already mutates affected clauses and inspects both adapter fixtures. Intake tests guard origin/current approval and final-review boundaries; coordination tests guard section-bound feedback, SUMMARY/index and exact guideline approval. **Verified / limited affected assertion updates justified.** |
| T001 size is coupled but viable | Actual Owned surfaces enumerates **11 paths** (five operational Markdown owners and six existing checker/test files), not 13. Seven REQUIRED items cover one coupled instruction/fixture increment. No independent runtime subsystem, parser or infrastructure is introduced. Producer checks precede consumers internally; task checkpoint precedes docs. Shared paths are not a reason for per-task dispatch. **No overpacking blocker; retain**, with moderate verification/context cost exposed to coordinator. The brief's 13-path characterization does not add two unlisted permissions. |
| Documentation is bounded to actual active consumers | REQUIREMENTS Implementation batch selection/Memory contract, README Planning and Implementation/Project coordination memory, and settings sample existing union/audit/repair prose already summarize this seam. T002 changes prose only and proves pins/JSON/defaults/unrelated bindings unchanged. `docs/index.md` already routes all canonical owners. **Verified / no new routing index or constitution changes.** |
| Evidence-only T003 is not circular review approval | T003 depends on verified/checkpointed T001/T002, owns only implementation-run SUMMARY/one index row, reuses still-valid item evidence and prepares the complete committed-range packet. V3 explicitly checkpoints packet before later coordinator-owned fresh independent review. Missing reviewer blocks feature acceptance, not this packet's checkpoint. **Verified / no circular dependency or new report.** |

No material uncovered product/permission/cost tradeoff was defaulted. The remaining cost is
moderate cross-owner instruction/fixture consistency, explicitly recorded in T001; implementation
preflight must assess context rather than use the three-task count as automatic local eligibility.

## Coverage, gates and stage feasibility

The task coverage table is complete and source-consistent; 15 criteria map to 12 unique REQUIRED
items. Manual inspection checked pass criteria, smallest checks, expected proof and gates:

| Source | Primary proof/check ownership |
| --- | --- |
| A1, A9 | T001/V1 practical ordinary-contract/adapter/legacy-producing-return checks; V7 preservation; T003/V1 trace |
| A2, A3, A13 | T001/V2 oracle-sensitive contrasting routing, union feasibility and ordered producers; V5 repair selection gates; T003/V1 |
| A4–A7 | T001/V3 shared distinct mappings, relevance/revision/environment/dispositions and producer release; V7 scope/checkpoints; T003/V1 |
| A8 | T001/V4 representative-sample STOP/approval versus ordinary path; T003/V1 |
| A10–A12 | T001/V5 original-contract exact-gap repair, invalidation, diagnosed/non-model stops and justified exceptional retry; V7; T003/V1 |
| A14 | T001/V6 factual first/final attempts, item evidence and escalation/selection; T003/V1 |
| A15 | T001 operational preservation, T002/V1–V2 lockstep prose, T003/V1–V3 integrated trace/checks/packet |

Named semantic cases target concrete failures rather than status-label presence. Limited
section-bound removals check actual operational carriers even when a summary mention remains.
Missing/irrelevant/stale/conflicting/unrun proof is insufficient evidence; objectively demonstrated
criterion violation is failed, including retained evidence limitations when both coexist. Only
satisfied REQUIRED items and fulfilled original gates release dependents. Optional green output
cannot compensate. These instructions and focused fixtures are actionable improvements to
assignment→proof→acceptance→repair; a generalized policy parser/formal verifier is not required.

Sequence is T001 → T002 → T003, with T003 also depending explicitly on T001. All implicit
producers exist before consumption; shared checks may run once with every item mapping.
Task/evidence checkpoints remain before later task work. No task profile allocation, imposed
batch split, task quota, exhaustive matrix or mandatory strong reviewer per accepted batch.
T003's existing lint integration is proportionate once at the cross-owner packaging boundary:
inspection of `scripts/check-skills-lint.sh` confirms planner/commit/producer/order/coordinator/state
integrations; coordination checks are separate there. It is not required for this read-only
baseline review and was NOT RUN here.

Both adapters, Standard create-only, original producing/legacy/current-content approval gates,
exact supported profile/permission/owner selection, final review and manual STOP are preserved.
Unknown/environment/manual/permission/spec/contract gaps cannot blind escalate. Stronger repair
is authorized implementation continuation under the SAME contracts, never generic review or
acceptance weakening. Exceptional clean retry is symbolic only; no reset executed.

## Validation actually executed

PASS: four Python invocations — task-order checker, producer fixture **4 tests**, coordinator
batching fixture **28 tests**, planner workflow checker (static instructions only). PASS: one
inline local Python inspection verified **25 local links/anchors**, exact source/task digests,
A1–A15 coverage and **12 REQUIRED references**. PASS: `git diff --check`; baseline/status,
identity and explicit path inventory inspected. These baseline successes establish that existing
local execution/check infrastructure is feasible, **not** that future feature checks already pass.
Post-write link/scope/digest/whitespace validation and focused review/evidence checkpoint SHAs
are recorded in the [same run evidence](../../../memory/coordination/evidence/2026-10-07-task-verification-contracts/SUMMARY.md).

NOT RUN: future named implementation cases, expanded/mutated fixtures, full lint, live provider
support/callability/obedience/performance, manual runtime user approval, stronger implementation
repair and fresh independent final review. This review has no ask_user capability and was not
assigned the owner gate; parent planner alone verifies/uses that gate and handles continuation.
No implementation/model-performance claim, install, push, external probe, operational/configuration/
STATE/guideline/history edit or guideline proposal. No new `/reload` obligation from preparation;
implementation closeout must request it after actual global skill changes.

## Combined approval — PENDING

No answer or owner approval is invented here. Planner must present 4–6 bullets before its
ask_user combined current-source/task/scope gate and bind the answer to the digests above.
With affirmative implementation-scope approval, planner immediately starts coordinator preflight;
that preflight still owns routing approval, usable exact profiles, Git/context and fresh independent
reviewer checks. This review does not launch it or reinterpret earlier preparation-only authority.

Proposed gate brief:

- Improve practical per-task observables, coherent batch assignment, cheap proof audit and exact-gap same-contract repair across existing instructions/fixtures, active prose and reviewer packet.
- Preserve both adapters/Standard/legacy approvals, per-task/evidence commits, one profile per coherent sequential batch and one fresh independent final review; no per-task allocation or mandatory strong batch review.
- No runtime/settings/pin changes, new framework/store/router/scoring, automatic learning, external probes, reset/discard, historical rewrites or guideline edits.
- Planner-owned review found no material blocker; order/static baseline checks PASS (4 producer + 28 batching tests), 25 links and A1–A15/12-item trace PASS; future feature/live/manual/final-review proof NOT RUN.
- Approve the exact source/tasks digests above and reviewed implementation scope, or withhold/request changes; this authorizes coordinator preflight next, not automatic routing selection, manual gates or feature acceptance.
