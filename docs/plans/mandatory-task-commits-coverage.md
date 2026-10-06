# Mandatory task commits — coverage inventory

Canonical policy: [task-commit contract](../../skills/memory-handling/references/task-commit-contract.md).
This inventory records the approved T001–T007 integration plan. `planned` does not claim that
the consumer is already wired; later task evidence changes rows only after verification.

| Consumer | Boundary / role | Status | Task evidence |
| --- | --- | --- | --- |
| coordinate-implementation | Coordinator/implementer checkpoints, recovery and final review | planned | T002 |
| planner | Produces retained source/task artifacts and hands execution to coordinator | planned | T003 |
| planning-brainstorming | Read-only preselection; no empty commit | planned | T003 |
| tiny-spec | Retained source deliverable, separate from task-list deliverable | planned | T003 |
| task-generation | Retained task-list deliverable and dependency order | planned | T003 |
| delegating-architectural-planning | Approved planning artifacts only; no adaptation bypass | planned | T003 |
| memory-handling | Factual evidence/checkpoint persistence, not guideline authority | planned | T003 |
| compact-memory | Retained compact-memory output only after its approval boundary | planned | T003 |
| initialize-coherence | Focused/idempotent initialization; preserve approval boundary | planned | T003 |
| finish-session | Authorized retained closeout; read-only checks create no commit | planned | T003 |
| finish-session-jev | Same closeout boundary; external routing remains authorized separately | planned | T003 |
| track-open-issue | Bounded retained register update | planned | T003 |
| handoff-prompt | Retained handoff deliverable, not unknown inherited work | planned | T003 |
| brainstorming | Analysis/read-only unless an authorized retained deliverable exists | planned | T004 |
| using-git-worktrees | Workspace/ignore decisions stay gated; no commit waiver | planned | T004 |
| requesting-code-review | Review request artifacts when retained; review scope stays bounded | planned | T004 |
| receiving-code-review | Review fixes are separate verified tasks; review alone is read-only | planned | T004 |
| writing-skills | Bounded skill deliverable is a task | planned | T004 |
| incorporate-skill | Adaptation-plan approval precedes writes and checkpoints | planned | T004 |
| infographic | Authorized retained repository output checkpoints automatically | planned | T004 |
| scientific-method-debugging | Investigation-only work has no empty checkpoint; retained fix does | planned | T004 |
| supabase-server | External/secret safety and operation permissions remain independent | planned | T004 |

Relevant active prompt routes (`.pi/prompts/speckit.*.md`) are package entry points rather than
skills. T004 wires the implementation route and classifies planning/analyze/checklist/clarify/
converge/plan/specify/tasks/taskstoissues routes as read-only or retained-artifact producers
under the same contract; no prompt may offer a commit waiver.

T005 supplies static omission mutations and temporary-Git protocol fixtures. T006 aligns
governing/user documentation. T007 reconciles every row against actual evidence. Static and
fixture evidence does not prove runtime model obedience.
