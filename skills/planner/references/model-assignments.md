# Owner planning assignments

`model-assignments.json` is the one owner-editable source for planning assignments. It is
located relative to the installed `planner` skill, so an installed planner symlink uses the
same file rather than a project's working directory or execution configuration.

Each operation resolves either a saved `assignment` or explicit
`"inherit": "launched-parent"`. Parent inheritance requires both the model and effort from
the owner-launched session; it never supplies a planning default. Saved assignment records
are shared by reference, so editing one changes every linked operation. The listed operations
cover planner-parent, both brainstorming calls, TinySpec source/tasks, Standard spec/tasks,
the direct and helper plan pass, and fresh overall review/rereview.

A correction calls `resolve_correction` with its producing operation and therefore keeps that
producer's assignment. There is no repair profile. If a retained producer context conflicts
with a later saved edit, the affected producing stage needs an owner resolution.

The resolver returns the **requested** model and effort only. Runtime code must separately
report an SDK-exposed model/effort when available; provider-internal actual execution remains
unknown unless the provider exposes it. This file has no implementation worker, fixer,
reviewer, or rereviewer assignment; those remain in the selected project's executor JSON.

A missing, malformed, ambiguous, or absent assignment raises an error naming the affected
operation, installed file, problem, and the smallest correction: ask the owner to correct that
operation's assignment. It makes no recommendation, inference, fallback, or substitute.
