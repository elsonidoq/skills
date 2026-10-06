# Active planning routing — preparation

Producer planner; owner-selected TinySpec. Status: combined source/tasks/implementation approval recorded in planning review at ebdc99b58e411377731cdec1cce85b606fc234ed; coordinator preflight complete, implementation dispatch next. Owner selected Sol/medium worker and fresh Sol/medium reviewer through ask_user. Exact approved source/task digests remain unchanged. Areas/tags: planning, routing, skill contracts, semantic validation.

Owner bounds: active contracts only; Sol/medium for the entire Standard plan_create pass, direct/helper; all other selections use existing routing criteria. Historical records, broad draft 001 retry/assignment changes, runtime/settings changes and live probes excluded. Owner selected current Sol/medium for local preparation; no implementation or reviewer selection inferred. Applicable approved coordination guidance: none; gotcha index empty.

Selected preparation profile: `openai-codex/gpt-6.1-sol`, medium. Observed: session model-change event and PI_MODEL report gpt-6.1-sol; latest thinking-level event medium. This is session-setting evidence, not independent provider execution attestation. Six-factor assessment: settled design with moderate cross-contract inference; shallow local tools; meaningful static checks with prose/obedience blind spots; three consumer contracts/shared checker coupling; reversible documentation changes but approval weakening risk; no approved local guidance. Family rationale: current Sol supports careful contract comparison. Effort rationale: medium for bounded remaining inference, separately selected. Runtime unavailable or failed checks stop, not automatic profile change.

| Item | Baseline | Result / evidence | Outcome |
| --- | --- | --- | --- |
| Source production | b2cf4d2890d0bdecd543737a3fc74c87c82e78af | b1391477ed2d0d4d823847cb03e2e8cb5f1fe697; docs/plans/active-planning-routing-tinyspec.md and plans index | PASS: source completeness/discovery, diff check; unchanged baseline checker PASS and 80 planner tests PASS |

| Task-list production | 94f99c4 | 8c2bed24f1b693cf6e96bb6b97611cdfdf0a1655; docs/plans/active-planning-routing-tasks.md and plans index | PASS: source digest binding, required-item/path inspection, task-order validator and diff check |

| Planner review | 495e6dd | 6f21f2c36614a3adae720ca81da2b83c14058df3; docs/plans/reviews/active-planning-routing-planning-review.md and review index | PASS: A1–A5/task traceability, exclusions, gates, producer order, scoped links/discovery, exact digests and diff check; combined approval pending |

Preparation exception: initial task-order check FAIL because heading-based task format was not supported by the bundled validator. Inspected its TASK/DEPENDS patterns, changed only this new task list to the repository checkbox/Depends format, then reran PASS. No delegated/model failure; no escalation or acceptance waiver.

| Combined owner approval | b71f0f8 | ebdc99b58e411377731cdec1cce85b606fc234ed; planning review exact-digest approval record | PASS: owner “I approve. start the coordination”; scope unchanged |

## Execution tracker

Complete task count: three (T001–T003). Strategy: one fresh async sequential worker, same checkout, no parallel writer; context-headroom metrics unavailable in parent, fresh bounded handoff preferred. Shared routing seam couples three skills to one checker; splitting writers would overlap ownership. T002 consumes T001; T003 consumes both. Parent does not mutate while worker runs. Independent final reviewer uses fresh context and read-only tools; reviewer receives full implementation range/patch, not a clean-tree diff.

- [ ] Batch 1 — T001–T003: in_progress (authorized; dispatch next).
- [ ] Final independent review — pending completed batch and parent checkpoint/evidence audit.

| Batch | Tasks | Scope | Dependencies | Integration | Verification | Selected profile | Mode | Initial status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | T001–T003 | Skills/checks → normative docs → acceptance scenarios | Internal T001 → T002 → T003 | Planner, brainstorming, helper/shared rubric, tests/docs | Whole approved REQUIRED item union; per-task and evidence commits; parent audit; final review | openai-codex/gpt-6.1-sol:medium | fresh async single writer | in_progress |

Assessment: moderate residual cross-contract reasoning; bounded local tool chain; weakest blind spot semantic contradictions/model obedience; tightly coupled producer/consumer prose/checker/docs; reversible owned changes with approval weakening risk; approved guidance none. Implementation Family rationale: Sol for cross-consumer inference and semantic blind spots, not fixed planning exception. Effort rationale: medium for settled design and bounded remaining inference. Reviewer Family rationale: same usable Sol with independent fresh context for adversarial semantic comparison. Reviewer Effort rationale: medium for bounded complete-diff review, no escalation to high. Conditional repair: inspect failed run/invocation/check/partial commit evidence; retain valid work; unknown cause stops; any profile change requires verified support and owner selection.

Capability evidence: subagent list reports executable native worker (read/bash/edit/write/contact_supervisor) and read-only reviewer; models registry/current session reports exact Sol binding; current parent session medium/model events observed. Doctor: async available, unlimited session spawn budget, fan-out limit 64, 0 active roots. Git identity/commits verified by preparation checkpoints; Python 3.12.3 and baseline checker/80 tests PASS. Runtime launch preflight is authoritative; registry/suffix evidence is not provider attestation. Missing support/authentication/tooling stops, not fallback. No live provider smoke probe authorized. Child receives edit/write, whose parent route succeeded during preparation; actual child tool results remain authoritative.

## Worker checkpoints

Worker requested/selected profile (parent evidence): `openai-codex/gpt-6.1-sol:medium`.
Worker observed actual binding/effort: unknown; this child has no independent execution attestation.
Approved guidance: none. Single writer, native read/edit/write/bash; no delegation or live probes.
Initial main HEAD and empty index verified at `91d560de5d00d7f22a57b49f4a0e0c67a83eea97`;
approved source/task digests matched before writes. Approved contracts remain byte-unchanged;
use this tracker, not digest-sensitive task checkboxes.

| Task/item | Baseline → result / evidence | Outcome |
| --- | --- | --- |
| T001/V1 | 91d560de5d00d7f22a57b49f4a0e0c67a83eea97 → f9330400adaf668b0ead6089deaf6affefc915b5; checker and `ActivePlanningRoutingTests` | PASS: pre-change exact Sol/medium assertion expected FAIL, same assertion post-change PASS; 7 new tests, 46 consumer-scoped mutation/link cases reject restored classes (both labels), changed family/effort, partial pass, fallback/default substitution, adapter bypass, lost selection/observed gates and summary-only carriers |
| T001/V2 | f933040; all commands with `PYTHONDONTWRITEBYTECODE=1 python3` | PASS: `scripts/check-planner-workflow.py`; `scripts/test-planner-workflow.py` 87 (baseline 80); brainstorming `scripts/test_contract.py` 4; task-generation `scripts/test_contract.py` 4; memory-handling `scripts/test_coordination_contract.py` 21 |
| T001/V3 | Manual baseline-to-patch inspection; bounded table below | PASS instruction inspection only; no live model-obedience inference |
| T001/V4 | `git diff --check`; explicit eight-path commit/show/status/index audit; historical fixture compared byte-for-byte with HEAD | PASS: only assigned T001 paths; historical initialization fixture unchanged; no staged files or task-owned residual changes; excluded untracked files untouched (metadata unchanged) |

T001 diagnosed check iterations: initial checker FAIL on two wrapped literal phrases (36 cascade
assertion failures); aligned wrapping. Next suite FAIL on two non-unique mutation targets; narrowed
actual carrier targets. Next suite FAIL on one whole-pass mutation because another ENTIRE mention
masked it; strengthened exact direct/helper entire-pass assertion. Final required union PASS.
These are inspected instruction/test-contract causes, not model-capability evidence or blind retries.

### T001 protected-boundary inspection (D4)

| Boundary | Retained operational carrier / rationale |
| --- | --- |
| Depth/owner dialogue | Planner Before selection; both options and `ask_user` STOP; brainstorming Owner dialogue stays orchestrator-owned; preselection read-only remains |
| Approval/current content/renewal | Planner Approval-driven continuation, TinySpec Combined approval, Standard spec_create/plan_create/overall_review and Approval, resume and legacy recovery; denied/stale answers never authorize work |
| Standard order/create-only tasks | Standard spec → complete same-session spec review/fix → one plan → plan review/fix → create-only tasks → independent overall review; unchanged causal stage/removal/order assertions |
| Helper ownership | Planner plan_create and helper Planner Standard adapter contract propagate exact selected Sol/medium, one entire pass and no duplicate creation; standalone policies explicitly cannot override manager |
| Writes/research | Planner Selected production/research paragraphs and helper Preflight/Planner Boundary retain separate bounded documentation permission, no arbitrary edits/code, research/approval stops |
| Task checkpoints/retries/final review | Shared task-commit link unchanged; coordinator contract unchanged and causal mutation coverage retained for checkpoints, inspected failure and fresh final review |
| Six factors/profile evidence | Shared seed's original table unchanged: residual reasoning; agentic/tool depth; verification blind spots (weakest unobservable failure); scope/coupling; failure cost/reversibility; approved guidance or none. All three consumers link this owner and require independent family/effort rationale, exact owner selection, runtime support, unchanged dispatch and unknown observed values. Planning never inherits implementation quotas/REQUIRED rules |

### T002 documentation checkpoint

T001 evidence-only checkpoint: `eae54d671f09f52304b8f1092b710f11b1a43207` (SUMMARY/index).
T002 baseline: that SHA; result: `0fd2c67499e94827173bf672e3d3d98f52519163`.

| Item | Evidence / bounded document-to-contract comparison | Outcome |
| --- | --- | --- |
| T002/V1 | REQUIREMENTS Planning/advisory selection ↔ planner Shared routing selection/Standard plan_create and helper adapter (A1–A3/A5); settings prose ↔ exact selection/observed gates; docs routing owner/link ↔ existing shared seed; constitution Project Constraints ↔ REQUIREMENTS owner terminology | PASS manual: entire same-session Sol/medium direct/helper pass, unavailable stop/no substitution, other six-factor selections, examples not selections/support proof. README inspected for contradictions: none requiring change |
| T002/V2 | Python local Markdown resolution across four owned docs: 66 links PASS; scoped active contract/docs obsolete-label search: zero; shared reference table/options unchanged | PASS: no replacement router; preserved Claude example ID and configuration decision attribution; intentional negative mutations and historical source-contract snapshot remain attributable, not normative authority |
| T002/V3 | `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-planner-workflow.py` and `scripts/test-planner-workflow.py`: PASS, 87; `git diff --check`, four-path diff/show/status/index audit; exact constitution substitution comparison | PASS: only owner-reference phrase changed in constitution, no principle/version amendment; no settings/runtime/history writes; no staged/task-owned residual files |

Limits: baseline checks do not accept the proposed implementation; static/simulated checks cannot prove model obedience; no paid/live probes. Untracked .env and docs/plans/mandatory-task-commits.md untouched. No delegated attempt or failed child. Reflection: no guideline update proposed; semantic validation limits are explicit source constraints, not newly learned project policy.
