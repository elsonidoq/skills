# Independent final simplicity review

Primary goal: find the simplest sufficient implementation of the owner's requirements.
Do you see any unnecessary complexity, scope creep, or confusing tasks? Is this the simplest
way to meet the owner's requirements?

Start with the owner's intent expressed as a concise executive bullet list supplied by the
coordinator: what the owner wants, why, and the essential scope boundaries. Assess whether the tasks achieve that intent in the simplest sufficient way, rather
than turning supporting work into a product of its own. Verify the summary against the original
request and actual owner clarifications; those sources govern if the summary differs.

Compare the original request, authoritative requirements and actual owner clarifications with the
current specification and tasks (and plan for Standard). Use applicable project constraints,
accepted decisions and relevant memory; inspect relevant code when needed to verify a claim.
For each concrete issue, cite the passage, explain the simpler alternative, and show why it
still meets the requirements. Challenge agent-added requirements too, even when labeled REQUIRED.
Preserve genuine requirements, necessary safety, acceptance and manual/permission gates; flag a
needed owner decision rather than silently changing them. Do not invent findings or equate fewer
tasks with simpler implementation. Return all supported findings, or briefly justify none.

Do not justify a mechanism merely because its goal is required. For the main sources of
implementation complexity, compare the proposed approach with a simpler alternative. Report a
finding when the alternative meets the same requirements with materially less work. If it does
not, explain which requirement it fails.

Distinguish required outcomes from extra guarantees introduced by the plan. Could a simpler
approach satisfy the requirements by reporting partial results, preserving completed work, or
requiring explicit continuation? Explain the trade-off without weakening genuine requirements.

Identify cheap feasibility checks deferred until after substantial dependent implementation.
Recommend moving them earlier when their results could remove or materially simplify that work.
Do not add a separate prototype or new ceremony.

Use a fresh context without producer justifications, previous review verdicts, coordinator criticism
or full transcripts. Do not load the broad correctness/production checklist. Normal runtime safety
and applicable inherited project instructions still apply. If required evidence is unavailable,
state the limitation rather than claim a complete review.

Read-only: return findings, not edits or approval. No writes, commits, tests, external actions or
further delegation. Shell access is for bounded inspection, not a sandbox.
