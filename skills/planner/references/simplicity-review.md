# Independent final simplicity review

Primary goal: find the simplest sufficient implementation of the owner's requirements.
Summarize the planned task specifications in one sentence, then explicitly answer:
“Does the current plan induce scope creep or over complexities?”
Do you see any unnecessary complexity or confusing tasks? Is this the simplest
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
tasks with simpler implementation. Return all supported findings within the per-task review below;
when none qualify, justify keeping the tasks rather than substituting a blanket pass.

Do not justify a mechanism merely because its goal is required. For the main sources of
implementation complexity, compare the proposed approach with a simpler alternative. Distinguish
necessary diagnostic evidence from a permanent diagnostic interface: consider calling the actual helper
through a bounded probe when that satisfies the same need. Do not claim duplicate interfaces or rigid
architecture when the tasks explicitly share an interface or permit alternatives. Report a
finding when the alternative meets the same requirements with materially less work. If it does
not, explain which requirement it fails.

Distinguish required outcomes from extra guarantees introduced by the plan. Could a simpler
approach satisfy the requirements by reporting partial results, preserving completed work, or
requiring explicit continuation? Explain the trade-off without weakening genuine requirements.

## Required report: review every task

Provide a concise entry for each task ID, not just a general review:

- **Contribution:** How does this task support the executive goal or a genuine requirement?
- **Simplicity:** Start from the owner's intent and binding requirements, not the proposed
  mechanism. Describe the smallest credible implementation and verification approach that would
  satisfy them, using existing capabilities where sufficient. Compare the proposed task against
  that baseline. Flag additional machinery when the simpler approach meets the same requirements
  with materially less work; otherwise explain the necessary benefit the extra machinery provides.
  Compare against a sufficient alternative, not an obviously inadequate one. Preserve evidence
  fidelity, safety, isolation and practical repeatability. State concrete trade-offs and unresolved
  assumptions; another possible approach alone is not a defect.
- **Proportionality:** Are tests, setup, recovery and workflow mechanisms justified by the
  required outcome and concrete risks? Assess the verification method separately from the
  implementation. Do not treat “this behavior needs testing” as justification for the proposed
  test setup. Identify what the test must prove, then compare the proposed setup with the smallest
  credible alternative using existing capabilities. Justify any additional environment, service,
  fixture lifecycle or workflow by evidence the simpler alternative cannot provide. If equivalence
  is uncertain, report that uncertainty. Prefer smaller sufficient checks, not weaker evidence.
- **Verdict:** Keep, simplify, or unresolved, with a brief evidence-based reason. Distinguish
  supported findings from hypotheses; name missing evidence for unresolved judgments.

Require an entry for every task, not a finding for every task. Assess shared machinery once and
reference that assessment from affected tasks. Do not stop after the first findings or claim
coverage of a task you could not assess.

End with a short cross-task check for duplication, unnecessary dependencies and cheap feasibility
checks deferred until after substantial dependent implementation. Recommend moving checks earlier
when their results could remove or materially simplify that work. Do not add a separate prototype
or new ceremony.

Use a fresh context without producer justifications, previous review verdicts, coordinator criticism
or full transcripts. Do not load the broad correctness/production checklist. Normal runtime safety
and applicable inherited project instructions still apply. If required evidence is unavailable,
state the limitation rather than claim a complete review.

Read-only: return findings, not edits or approval. No writes, commits, tests, external actions or
further delegation. Shell access is for bounded inspection, not a sandbox.
