# Active planning routing — TinySpec planning review

Producer/reviewer: planner, local owner-selected Sol/medium preparation. This is the planner-owned TinySpec review, **not** an independent implementation review. Verdict: prepared for combined owner approval; implementation not authorized yet.

## Reviewed content identity

- Source: `docs/plans/active-planning-routing-tinyspec.md`, SHA-256 `1f44d5b3dfe4fdddcd4a0445ab85ec8700363b11465c13f19252a65c66423c5a` (source production commit `b1391477ed2d0d4d823847cb03e2e8cb5f1fe697`).
- Tasks: `docs/plans/active-planning-routing-tasks.md`, SHA-256 `0acca7d33e004631137a0ec744f9b065e832b4fb7b0bf066746e6acc42cd586e` (task production commit `8c2bed24f1b693cf6e96bb6b97611cdfdf0a1655`).
- Provenance: current owner request/decisions preserved in source; explicit TinySpec and current Sol/medium preparation choice. Active operational rules are inspected working-tree contracts, not the broader draft 001 routing design.

## Review findings and coverage

| Criterion / boundary | Tasks and observables | Disposition |
| --- | --- | --- |
| A1 active class authority removal | T001 consumer/checker mutations; T002 normative docs; T003 targeted inventory | Complete proposed coverage; historical snapshots and intentional rejection tests excluded from blind deletion |
| A2 exact Sol/medium Standard pass | T001 exact family/effort, adapter precedence and rejection checks; T002 docs; T003 direct/helper/unavailable scenarios | Explicit supported-binding/effort and no-substitution gates; full same-session pass retained |
| A3 routing elsewhere | T001 single shared six-factor reference and relevant consumer wiring; T002 normative routing owner; T003 non-plan/default-mismatch cases | No second router, old-class mapping or implementation-task assignments; implementation-only batching rules not imposed on planning |
| A4 preserved workflow boundaries | T001/V2–V3 baseline section comparison and causal retained checks; T002/V3 narrow constitution reference; T003 permission/approval stops | Depth/approvals/renewal, create-only tasks, writes/research, one helper pass, checkpoints and independent review retained |
| A5 honest evidence/docs | T002 doc/link truth checks; T003 bounded integration evidence and coordinator-owned fresh final review | Simulated/static versus live explicitly distinguished; NOT RUN live is not an obedience claim |

Manual review inspected traceability, exclusions, capabilities, independently observable REQUIRED items and their manual/permission gates, implicit prerequisites, contiguous sequence and smallest sufficient verification. T001 publishes operational instructions and their tests before T002 documents behavior; both produce inputs before T003 validates integration. Three tasks are not a local-execution authorization: coordinator must assess actual profile/context and independent reviewer availability. Source/profile selection is not implementation/reviewer selection.

No unresolved material design flag. Reference terminology cleanup in the constitution is explicitly bounded and leaves principles/governance unchanged. Other standalone helper selections remain distinct from a Standard manager-governed call; no helper fallback may bypass Standard Sol/medium. The source makes this scope visible rather than silently impose a new standalone workflow. A supported profile is not guaranteed by this document or a settings example.

## Actual preparation checks

- Python 3.12.3 available; `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-planner-workflow.py`: PASS on unchanged operational contracts.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-planner-workflow.py`: PASS, 80 tests, unchanged baseline.
- Source completeness, required item/path inspection and source-to-task digest binding: PASS.
- `PYTHONDONTWRITEBYTECODE=1 python3 skills/task-generation/scripts/check-task-order.py docs/plans/active-planning-routing-tasks.md`: initial FAIL for unsupported heading format; inspected validator, adapted new task list to checkbox/Depends format, reran PASS. No changed validator or waived requirement.
- Scoped introduced-link checks and `git diff --check`: PASS before review checkpoint.
- Actual implementation/mutations/integration lint/independent final review: NOT RUN, future approved work. Paid/live runtime probes and actual model obedience: NOT RUN, separately authorized and optional.

Unrelated untracked `.env` and `docs/plans/mandatory-task-commits.md` preserved; no operational skill/test changes made during preparation. Memory index empty; no approved coordination guidelines or guideline mutation. Dependency evidence reused from the existing routing owner; no version-sensitive runtime change requires new external research.

## Combined owner gate

Pending. Approval question must name these exact source/task identities and the implementation bounds, including Sol/medium Standard exception, shared routing elsewhere, preserved history and safeguards, static-proof limits and REQUIRED final independent review. An affirmative combined approval starts `coordinate-implementation` preflight in this session, not immediate permission to bypass profile/capability/ownership gates. Denial, cancellation or ambiguity leaves implementation unauthorized. Changes to source/task scope, acceptance or decisions require renewed review/approval. Persist the answer here with comparable current-content evidence; do not edit approved source/tasks solely to insert a status label.
