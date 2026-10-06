# Mandatory task commits — coverage inventory

Canonical policy: [task-commit contract](../../skills/memory-handling/references/task-commit-contract.md).
This inventory records the approved T001–T007 integration plan. `planned` does not claim that
the consumer is already wired; later task evidence changes rows only after verification.

| Consumer | Boundary / role | Status | Task evidence |
| --- | --- | --- | --- |
| coordinate-implementation | Coordinator/implementer checkpoints, recovery and final review | integrated | T002 static checks |
| planner | Produces retained source/task artifacts and hands execution to coordinator | integrated | T003 link/read-through |
| planning-brainstorming | Read-only preselection; no empty commit | integrated | T003 link/read-through |
| tiny-spec | Retained source deliverable, separate from task-list deliverable | integrated | T003 link/read-through |
| task-generation | Retained task-list deliverable and dependency order | integrated | T003 link/read-through |
| delegating-architectural-planning | Approved planning artifacts only; no adaptation bypass | integrated | T003 link/read-through; RF001 operational checkpoint correction |
| memory-handling | Factual evidence/checkpoint persistence, not guideline authority | integrated | T003 link/read-through |
| compact-memory | Retained compact-memory output only after its approval boundary | integrated | T003 link/read-through |
| initialize-coherence | Focused/idempotent initialization; preserve approval boundary | integrated | T003 link/read-through |
| finish-session | Authorized retained closeout; read-only checks create no commit | integrated | T003 link/read-through |
| finish-session-jev | Same closeout boundary; external routing remains authorized separately | integrated | T003 link/read-through |
| track-open-issue | Bounded retained register update | integrated | T003 link/read-through |
| handoff-prompt | Retained handoff deliverable, not unknown inherited work | integrated | T003 link/read-through |
| brainstorming | Analysis/read-only unless an authorized retained deliverable exists | integrated | T004 link/read-through |
| using-git-worktrees | Workspace/ignore decisions stay gated; no commit waiver | integrated | T004 link/read-through |
| requesting-code-review | Review request artifacts when retained; review scope stays bounded | integrated | T004 link/read-through |
| receiving-code-review | Review fixes are separate verified tasks; review alone is read-only | integrated | T004 link/read-through |
| writing-skills | Bounded skill deliverable is a task | integrated | T004 link/read-through |
| incorporate-skill | Adaptation-plan approval precedes writes and checkpoints | integrated | T004 link/read-through |
| infographic | Authorized retained repository output checkpoints automatically | integrated | T004 link/read-through |
| scientific-method-debugging | Investigation-only work has no empty checkpoint; retained fix does | integrated | T004 link/read-through |
| supabase-server | External/secret safety and operation permissions remain independent | integrated | T004 link/read-through |

Relevant active prompt routes (`.pi/prompts/speckit.*.md`) are package entry points rather than
skills. T004 wires all active routes and classifies planning/analyze/checklist/clarify/
converge/plan/specify/tasks/taskstoissues routes as read-only or retained-artifact producers
under the same contract; no prompt may offer a commit waiver.

T005 supplies static omission mutations and temporary-Git protocol fixtures (implemented by
`scripts/check-task-commit-contract.py` and `scripts/test-task-commit-contract.py`). T006 aligns
governing/user documentation. T007 integration checks verified all rows and active prompt links
against the canonical owner; no row claims runtime model obedience. Static assertions and
Git fixtures remain instruction/protocol evidence only.
