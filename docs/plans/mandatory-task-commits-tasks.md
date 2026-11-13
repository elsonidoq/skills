# Mandatory task commits — implementation tasks

Producer: `planner`; selected depth: **TinySpec**. Authoritative source: [mandatory-task-commits-tinyspec.md](mandatory-task-commits-tinyspec.md), acceptance A1–A7. Original draft is historical input only; its runtime extension gate is superseded.

Status: prepared for combined planner review/owner approval, **not authorized for implementation**. Preparation binding was owner-selected Current Sol; implementation and independent-review bindings remain coordinator preflight gates. All seven bounded implementation tasks are `sonnet-class`; opus share is 0%. Do not infer provider/model assignments from that class.

## Shared execution and acceptance boundaries

Implement in numbered dependency order. Every task requires a focused verified commit before the next task; coherent sequential batches/session reuse remain valid. No commit waiver question. Preserve unrelated work and authorization gates. Coordinator preflight must establish task-owned baselines; a fresh implementer never adopts or commits unknown changes. A Git/commit/verification blocker stops execution. Final independent implementation review is coordinator-owned, not a self-review task below.

Required checks are specified per task. Optional broad regressions do not become acceptance blockers without a concrete changed-seam reason. No runtime extension, new mandatory checkpoint helper/adapter, new state schema, dependency installation, paid/live probe, push or deployment. Git fixture verification proves Git behavior/protocol examples, not actual agent obedience. Each task includes documentation for its changed boundary rather than deferring all accuracy to final closeout.

## Tasks

- [ ] T001 Define the shared non-waivable checkpoint contract and coverage inventory
  - **Depends**: none
  - **Outcome / source**: A1–A7 have one operational owner; every distributed skill and relevant package prompt is classified with its mutation/read-only/disposable/external-only boundary and current conflicts.
  - **Files / interfaces**: new `skills/memory-handling/references/task-commit-contract.md`; new `docs/plans/mandatory-task-commits-coverage.md`; narrowly scoped reference distribution/discovery wiring if existing lint/link conventions require it. Inspect existing shared-reference handling before choosing wiring; no duplicated policy owner.
  - **Required capabilities**: repository inspection/edit/Git, Python 3 and existing lint/reference checks.
  - **Model class / rationale**: sonnet-class — bounded contract synthesis from settled A1–A7 and a finite inventory.
  - **REQUIRED acceptance**: all 22 current skills plus relevant active prompts accounted for; task boundaries and no-change behavior explicit; no waiver path; coordinator versus implementer ownership, task-relative cleanliness, interruptions and evidence-only checkpoints documented; existing authority/guideline approvals retained. Focused reference/link check and skill lint pass; diff inspected. Inventory may not claim operational integration before later tasks implement it.
  - **Verification effort / integration checkpoint**: static bounded checks are sufficient for the policy/reference seam; Git behavior is tested in T005. Commit producer contract before T002 consumes it.

- [ ] T002 Enforce the pragmatic coordinator and implementer protocol
  - **Depends**: T001
  - **Outcome / source**: A2–A6 become actionable local/delegated/batch/resume instructions; no exceptions remain in Execute/Finish or delegate briefs.
  - **Files / interfaces**: `skills/coordinate-implementation/SKILL.md`; coordinator intake/batching tests; coverage rows; only the intentional `EXECUTION_SHA256` update in `scripts/check-planner-workflow.py` required to keep existing tests running against the reviewed new execution content.
  - **Required capabilities**: edit/Git, Python 3, existing coordinator/workflow checks; no live delegation necessary for contract changes.
  - **Model class / rationale**: sonnet-class — one existing execution seam with independently inspectable instructions/tests.
  - **REQUIRED acceptance**: pre-write Git/baseline gate; each internal batch task verifies/commits before next; fresh/resumed unknown-state guard; coordinator checks actual diff/checks/SHA/residual changes; contextual missing-commit recovery belongs to coordinator; failed recovery stops dispatch; no ask-to-skip/defer/no-Git fallback; compatible commit conventions and unrelated-change preservation intact; completion and final-review fixes carry verified commit evidence. Add a focused failing assertion before edits. Existing coordinator intake/batching and planner workflow checks pass after the reviewed hash update; record old/new hash rationale rather than removing the freeze.
  - **Verification effort / integration checkpoint**: focused operational-text assertions catch the changed seam; deeper mutations/fixtures follow in T005. Commit before other skill consumers are aligned.

- [ ] T003 Align planning, memory, adoption and closeout skill consumers
  - **Depends**: T002
  - **Outcome / source**: A1–A6 apply to workflow-managed retained artifacts without bypassing selection, adaptation, guideline or implementation approval.
  - **Files / interfaces**: `planner`, `planning-brainstorming`, `tiny-spec`, `task-generation`, `delegating-architectural-planning`, `memory-handling`, `compact-memory`, `initialize-coherence`, `finish-session`, `finish-session-jev`, `track-open-issue`, `handoff-prompt` skill instructions and directly affected references/tests; coverage rows. Keep shared owners canonical.
  - **Required capabilities**: edit/Git, Python 3, existing relevant skill tests/lint/link checks.
  - **Model class / rationale**: sonnet-class — mechanically consistent finite consumers with established approval boundaries.
  - **REQUIRED acceptance**: every listed consumer links the contract with appropriate role; retained source/task/evidence/closeout delivery committed without waiver; preselection read-only exceptions remain bounded; no fresh consumer commits unknown inherited work; guideline approval is not inferred from commit policy; initialization stays idempotent and focused. Add/run focused changed-consumer assertions, relevant existing contract tests and skill lint; update coverage truthfully.
  - **Verification effort / integration checkpoint**: inspect each operational boundary and shared-link resolution, not only global keyword presence. Do not add independent per-task reviews. Commit before T004 completes the inventory.

- [ ] T004 Align standalone capabilities, review skills and active prompt routes
  - **Depends**: T003
  - **Outcome / source**: remaining A1/A2/A4 consumers cannot introduce an opt-in/deferred commit path or accidentally acquire write authority.
  - **Files / interfaces**: remaining `brainstorming`, `using-git-worktrees`, `requesting-code-review`, `receiving-code-review`, `writing-skills`, `incorporate-skill`, `infographic`, `scientific-method-debugging` skill instructions/references; relevant `.pi/prompts/` operational routes, especially `speckit.implement.md`; coverage rows and focused tests.
  - **Required capabilities**: inspection/edit/Git, Python 3 and existing lint/tests; no external provider capabilities required to change instructions.
  - **Model class / rationale**: sonnet-class — bounded package alignment with explicit per-consumer acceptance.
  - **REQUIRED acceptance**: remove infographic's conflicting commit opt-in for authorized retained repository output; preserve adaptation approval, ignore/worktree decision gates, secret safety, review read-only scope and external operation permissions. Writing standalone routes define a deliverable/task checkpoint; analysis-only routes do not create empty commits or fabricate a coordinator. Fresh agent with unknown inherited work stops/returns the blocker, not commit blindly. Prompt routes carry the same contract and do not bypass coordinator gates; unrelated SpecKit semantics unchanged. All remaining inventory rows have actual integration evidence; relevant tests, lint and focused links pass.
  - **Verification effort / integration checkpoint**: use a small normal/read-only/blocked example per materially different boundary; no exhaustive provider tests. Commit before package-wide tests assess final consumer coverage.

- [ ] T005 Protect policy omissions and demonstrate Git checkpoint safety
  - **Depends**: T004
  - **Outcome / source**: A3–A7 have routine, diagnostic regression checks plus concrete temporary-Git evidence.
  - **Files / interfaces**: existing `scripts/check-planner-workflow.py`, `scripts/test-planner-workflow.py`, coordinator/consumer tests and lint wiring as needed; focused new commit-contract fixture test under `scripts/` if existing tests cannot express temporary-Git cases; coverage evidence.
  - **Required capabilities**: Python 3, Git and temporary directories; local fixtures only, no actual provider/agent launches.
  - **Model class / rationale**: sonnet-class — bounded deterministic oracle construction, separable from runtime orchestration.
  - **REQUIRED acceptance**: mutations diagnose missing contract links/operational guards, reintroduced waiver questions, omitted coordinator recovery/failed-commit stops, per-batch replacement and fresh-agent blind commit. Real temporary Git cases show focused task commits and unrelated staged/unstaged preservation; residual/absent/incorrect/combined checkpoint failures; failing hooks block; successful commit with interrupted metadata is recovered by SHA without duplicate commit. Same-file ambiguity is a stop case, not blanket staging. Fixtures never alter current repo/config or bypass hooks. Fail-before/pass-after evidence for at least the changed checkpoint rule; routine existing workflow/mutation checks invoke new required assertions. Clearly label instruction assertions versus Git examples, never model-obedience proof.
  - **Verification effort / integration checkpoint**: only the failure seams named above; no runtime extension matrix, abstract new framework or universal clean-tree rule. Commit validated tests before documentation claims their capabilities.

- [ ] T006 Align governing instructions, requirements and user-facing documentation
  - **Depends**: T005
  - **Outcome / source**: A1/A2/A7 and rollout are accurately documented throughout the package.
  - **Files / interfaces**: `AGENTS.md`, `REQUIREMENTS.md`, `README.md`, `docs/index.md`, `docs/best_practices_spec_driven_development.md`, `.specify/memory/constitution.md` and directly affected current templates/guides; final coverage rows.
  - **Required capabilities**: edit/Git, Python 3 and existing documentation/reference/lint checks.
  - **Model class / rationale**: sonnet-class — deterministic documentation alignment with implemented contracts and tests.
  - **REQUIRED acceptance**: governing policy says no commit waiver; no new runtime adapter requirement; scope and authorization boundaries explicit; read-only/no-change and unrelated-dirty-work behavior documented; compatible Git conventions versus blocking conflicts distinguished; constitution amendment/version rationale recorded under explicit approved policy scope. Links resolve; historical source/review records remain historical rather than silently rewritten. Document `/reload` after skill changes and limits of instruction-managed enforcement. Focused link/policy assertions and diff check pass.
  - **Verification effort / integration checkpoint**: verify claims against actual T001–T005 changes/results rather than repeat broad tests. Commit before final integration packet.

- [ ] T007 Reconcile coverage and validate the integrated package
  - **Depends**: T006
  - **Outcome / source**: all A1–A7 mapped to current evidence and a complete committed-range packet is ready for the coordinator's fresh independent final review.
  - **Files / interfaces**: coverage/review/execution evidence in existing project conventions; only demonstrated in-scope integration defects in preceding touched files/tests. New unrelated compatibility work requires separate scope rather than silent expansion.
  - **Required capabilities**: Git, Python 3, local skill/workflow/checkpoint fixtures; independent reviewer is a coordinator acceptance prerequisite, not delegated to this implementer.
  - **Model class / rationale**: sonnet-class — finite integration verification and evidence reconciliation, not self-certification.
  - **REQUIRED acceptance**: skill lint; coordinator intake/batching tests; planner checker/mutation suite; affected task-generation checks; new commit-contract/Git fixtures; task-order checker on this artifact; diff check. Record actual commands/results and inspect all coverage rows for omission, no false PASS. Export baseline/final revisions and complete committed changes for independent final review; note original draft as pre-existing untracked content excluded from implementation commits. No live/runtime obedience claim. Successful implementation agent return alone does not establish final acceptance.
  - **Verification effort / integration checkpoint**: reuse valid focused prior results where content/environment unchanged; run routine integration checks needed for changed wiring. Commit this task's evidence before coordinator review. Confirmed review fixes receive separate verified task commits; unresolved findings block acceptance.

## Planning review and approval

Planner reviews source-to-task traceability, inventory coverage, dependencies, class share, exclusions, acceptance, documentation and retained authorization boundaries. Record exact source/task content evidence in a separate review record so task execution status updates do not invalidate self-hashes. Combined owner approval remains pending; approval starts coordinator preflight, not automatic assumption of implementation models, reviewer or workspace cleanliness.
