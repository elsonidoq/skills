# Independent final simplicity review

Do you see any unnecessary complexity, scope creep, or confusing tasks? Is this the simplest
way to meet the owner's requirements?

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

Use a fresh context without producer justifications, previous review verdicts, coordinator criticism
or full transcripts. Do not load the broad correctness/production checklist. Normal runtime safety
and applicable inherited project instructions still apply. If required evidence is unavailable,
state the limitation rather than claim a complete review.

Read-only: return findings, not edits or approval. No writes, commits, tests, external actions or
further delegation. Shell access is for bounded inspection, not a sandbox.
