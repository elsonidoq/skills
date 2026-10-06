# Non-negotiable per-task commit checkpoints

## Status and owner direction

Status: **superseded historical proposal**, retained as original input, not current implementation authority. The [approved TinySpec](mandatory-task-commits-tinyspec.md) supersedes this draft's runtime extension gate and mandatory adapter availability; see its [planning review/approval](reviews/mandatory-task-commits-planning-review.md). The current operational owner is the [task-commit contract](../../skills/memory-handling/references/task-commit-contract.md). The proposal below is preserved for provenance and does not authorize delegation, installation, runtime changes, or work excluded by the approved source.

Owner direction: make all package skills consistent; committing after each task is mandatory, non-negotiable, and never presented to the user as an optional choice. Remove every execution path that asks whether to skip or defer a required task commit.

## Current-state evidence

- `skills/coordinate-implementation/SKILL.md` requires one verified commit per task before the next task, including local work and sequential tasks inside delegated batches. Its commit-conflict/no-Git and finish sections nevertheless permit explicit owner skip/defer decisions.
- The shared coordination contract already stops on initialization commit failures and preserves unrelated staged/worktree changes.
- Other entry points do not consistently carry a task-commit contract. `skills/infographic/SKILL.md` explicitly prohibits committing without a separate request; this conflicts with a package-wide automatic checkpoint policy for authorized retained repository changes.
- Coordinator tests and `scripts/check-planner-workflow.py` validate instruction text, not actual execution. The latter freezes the execution section through a hash; intentional policy changes must update this guard with reviewed evidence, not disable it.
- Project coordination store: `memory/coordination/`; `GUIDELINES.md` has no approved guidelines. This change belongs in package policy, not a learned project guideline.

## Required policy

1. Every authorized task that retains repository changes ends with a focused, verified Git commit before any subsequent task begins or the task is reported complete. This includes implementation, retained planning artifacts, documentation, skill edits, review fixes, closeout artifacts, and generated repository deliverables.
2. A read-only task or verified no-change task records that outcome and creates no empty commit. Scratch work explicitly designated disposable is not a retained deliverable; it cannot conceal retained changes.
3. Commit checkpoints are automatic within authorized task scope. Never ask whether to commit, skip, defer, batch several tasks into one commit, or proceed without Git. No owner-exception field or fallback path exists in this workflow.
4. Unavailable Git, commit permission, identity/signing capability, failed checks/hooks, ambiguous change ownership, or policy prohibiting the required checkpoint blocks the affected workflow. Report the exact blocker without offering a waiver. Do not bypass governing instructions, hooks, signing, or branch protections to enforce this policy.
5. Commit formatting, signing, and allowed-branch conventions remain supported when compatible with immediate per-task commits. Deferred/squash-only checkpoint policies are incompatible; later separately authorized history integration is outside task execution.
6. This contract grants no authority to make otherwise unapproved edits, push, deploy, incur costs, or perform destructive recovery. Existing product/model/guideline/permission approval gates remain. It must not commit secrets or unrelated work.
7. Delegation batches and agent sessions are independent of commit boundaries. Preserve sequential execution, coherent batches, approved task order, and one final independent implementation review rather than introducing per-task independent reviews.

## Design

### One authoritative contract

Add `skills/memory-handling/references/task-commit-contract.md` as the shared owner, following the package's existing distributed-reference pattern. Define scope, task boundaries, preflight, baseline, checkpoint verification, failure handling, and resume behavior there. Reference it from every skill's operational instructions; retain short action-specific obligations rather than copying diverging full policies.

Make global `AGENTS.md`, `REQUIREMENTS.md`, README, and applicable constitution guidance carry the same non-waivable rule. Explicitly distinguish automatic commits from unauthorized implementation or external operations.

### Preflight and recoverable baseline

Before a task's retained writes:

- Verify usable Git, permitted repository/branch, commit configuration and required checkpoint capability. Avoid side-effectful hook/signing probes and do not alter identity or security configuration automatically.
- Inspect HEAD, working-tree/index state, allowed files, and baseline check results. Preserve unrelated changes and ownership.
- Establish a recoverable task baseline. HEAD alone is insufficient when pre-existing changes overlap task paths: use an authorized isolated workspace or preserve an exact bounded baseline; otherwise stop before writes.
- Retain task ID, attempt ID, baseline revision, write scope, and check requirements in the established tracker/evidence convention. Do not invent a competing global execution-state format.

### Checked checkpoint

Implement a small reusable checkpoint helper owned by the shared contract. Provide preflight/baseline/checkpoint/resume validation using explicit repository and task inputs, with no provider or model assumptions.

At a checkpoint:

1. Verify required task checks and inspect the actual diff, including additions/deletions and task-related artifact changes.
2. Stage/commit only task-owned changes, preserving unrelated staged and unstaged content. Ambiguous same-file ownership blocks; never use blanket staging, stash/reset, or destructive cleanup as a shortcut.
3. Verify the resulting commit exists, belongs to the recorded baseline/attempt, and contains only authorized task changes. Confirm no task-owned deliverable remains uncommitted; do not require the entire repository to be clean.
4. Record baseline and resulting commit SHA, check evidence, attempt outcome, and checkpoint status before declaring completion or releasing dependents. Handle SHA metadata without recursive self-reference: record the task SHA after commit in execution evidence, then commit evidence at a defined evidence-only boundary before starting the next task or handing off.
5. If commit creation or verification fails, retain recoverable work, mark the task blocked, and stop. A successful tool return, checked box, or delegate report is not checkpoint proof.

For sequential delegated batches, require the delegate to run this boundary between internal tasks; the coordinator independently verifies returned commits. Coordinator-only commits are permissible only when the delegate pauses after each task and cannot start the next until the coordinator validates its checkpoint.

### Enforcement boundary

Package scripts can validate repository state and reject invalid checkpoints. They cannot, by themselves, prevent an unrestricted agent from issuing arbitrary write tools or ignoring instructions. Do not describe prompt checks or Git hooks as runtime enforcement.

For supported runtimes, introduce a verified task-transition/mutation gate that refuses next-task writes until the previous checkpoint is validated. Keep it independent of model and batch size. Inspect documented runtime extension APIs before implementation; avoid assuming an installed adapter exists. If no enforceable runtime capability is available, report `Task checkpoint enforcement: UNAVAILABLE` and stop package-managed mutation workflows rather than silently fall back to instruction-only enforcement. Read-only analysis remains available.

Keep runtime integration narrowly scoped to task/checkpoint admission, not a new general orchestration subsystem. Document unsupported runtimes explicitly. No extension installation or global configuration change is authorized by writing this plan.

### Failure, retry, and resume

- Failed attempts are not accepted task commits. Preserve bounded failure evidence and inspected cause before any restoration; do not commit failing code as successful work.
- Restore only the failed task's established baseline where existing authority permits. Preserve unrelated changes and previous successful task commits. Never equate a timeout or failure with evidence of insufficient model capability.
- Require verified clean task state and existing model/capability selection gates before retry/escalation.
- If final review finds a defect after dependents were committed, identify affected dependents and choose a bounded authorized corrective path. A single-task revert is not assumed safe. Verify and commit each correction task separately.
- Resume reconciles actual commits, tracker, task scope and interrupted evidence writes. A commit that succeeded before reporting failed is recovered, not duplicated. No subsequent task starts while checkpoint state is uncertain.

## Implementation sequence

| Step | Work | Dependencies | Completion evidence |
| --- | --- | --- | --- |
| 1 | Inventory every skill, supporting reference, prompt entry point and policy document. Classify read-only, retained-writing, approval-gated, disposable and external-only workflows; record conflicting commit instructions and reference consumers. | None | Coverage table accounts for every distributed skill and executable entry point; historical documents identified separately. |
| 2 | Add the shared non-negotiable task-commit contract and align package instructions/runtime prerequisites. | 1 | No skip/defer/proceed-without-Git option; compatible repository conventions and higher-priority-policy blockers are explicit. |
| 3 | Implement and fixture-test baseline/checkpoint/resume helper with unrelated-change preservation. | 2 | Real temporary-Git tests verify scoped commits, interrupted recovery and failure stops. |
| 4 | Implement the supported-runtime checkpoint gate against verified APIs and expose enforceable capability detection. | 2, 3 | Next-task writes are rejected without checkpoint proof; missing capability blocks mutation rather than weakening enforcement. |
| 5 | Integrate coordinator local/delegated execution, briefs, internal batch transitions, tracker, completion report, retries and final-review fixes. | 3, 4 | Each successful mutating task has independently checked baseline/commit evidence; no next-task execution after a blocked checkpoint. |
| 6 | Integrate every other skill and prompt entry point. Reconcile infographic delivery, retained planning, adaptation approvals, worktree setup, debugging, memory and closeout without expanding write authority. | 1–5 | Every inventory row links its operational contract and focused acceptance test; read-only/disposable/external-only boundaries remain accurate. |
| 7 | Extend package lint, workflow/mutation tests and documentation; deliberately update execution hash guards with evidence. | 5, 6 | Routine validation rejects omitted contract links, reintroduced waivers and unenforced transitions; docs match actual supported capability. |
| 8 | Obtain independent review of policy coverage, helper safety and runtime gate; verify and separately commit correction tasks, then publish bounded installation/reload guidance. | 7 | Full committed-range review; all material findings resolved or acceptance blocked; no unsupported enforcement claim. |

Each mutating implementation step must itself use a separate verified task commit. If an implementation step needs decomposition, assign independently verifiable task boundaries first; do not hide several tasks behind a single milestone commit. During bootstrap, follow the requested commit policy directly and record the limitation until the new gate exists; do not claim that bootstrap is mechanically enforced by the not-yet-built gate.

## Required verification

Use static tests for policy consistency and actual temporary-repository/runtime tests for behavior. Cover:

- Local and delegated tasks; two tasks inside one reused batch/session; last-task and closeout commits.
- No-change/read-only tasks without empty commits; authorized retained planning and generated artifacts with commits.
- Missing Git, forbidden commit policy, absent enforcement adapter, failed checks, failed hook/signing and failed commit: blocked, no waiver question, no subsequent task writes.
- Unrelated staged/unstaged work, deletions/untracked task files, same-file ownership ambiguity and baseline drift.
- Commit succeeds but reporting/evidence fails; resume recovers the exact SHA without duplicate commits.
- Failed attempt restoration and escalation preserve previous task commits and unrelated changes.
- Later reviewer findings affecting dependent tasks do not trigger unsafe automatic rollback.
- Mutation tests remove the checkpoint rule/reference or introduce skip/defer/ask-to-waive behavior; routine validation must fail with a specific diagnostic.
- Runtime tests attempt a next-task mutation without a verified checkpoint and verify rejection, not merely the presence of policy prose.

Required package validation includes skill lint, coordinator intake/batching tests, planner workflow checks and mutation tests, new checkpoint-helper/runtime tests, and `git diff --check`. Report unavailable runtime testing as unavailable and leave mechanical-enforcement acceptance blocked.

## Non-goals and safety boundaries

No model-routing rubric changes, provider hard-coding, new class taxonomy, unrelated history rewriting, automatic pushes, paid probes, broad deployment changes, or promotion of a single failure into a model-capability conclusion. Do not rewrite historical review records as current policy; label/link superseded records where they could mislead a current entry point.

## Acceptance

The package is ready only when every skill is accounted for, authorized retained-writing workflows share the non-waivable checkpoint rule, no workflow asks whether to omit/defer it, and supported execution gates actually prevent next-task mutation without verified commit evidence. Missing prerequisites stop execution; they never create an exception. All preserved authorization, unrelated-work, sequencing and independent-review protections remain intact.

After implementation changes global skills/configuration, tell the user to run `/reload` inside pi. No reload is needed for this plan-only document.
