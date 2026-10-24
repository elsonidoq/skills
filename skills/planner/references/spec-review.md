# Independent specification review — user-intent fidelity

## Purpose

Use this prompt core for one fresh independent skeptical review of a current TinySpec
or Standard specification. The primary focus is fidelity to the user's actual intent,
not technical polish or the producer's preferred solution. Product intent and relevant behavioral completeness are review
perspectives, not a checklist. Return explicit **zero findings** when no material
fidelity defect or unresolved decision remains. Otherwise return all material findings,
ranked by importance, with no numerical discovery cap. Group findings into meaningful
areas when useful; exclude duplicates and trivia rather than padding the report.
The coordinator controls presentation size, not reviewer discovery.

For each ranked finding, cite the relevant user-intent evidence (request or actual owner
answer), the affected specification section, the concrete consequence, and a correction or
owner question. Do not turn an evident omission/distortion into an unnecessary owner decision.
Check the actual problem, intended beneficiary, desired behavior, boundaries, explicit
exclusions, and observable completion. Detect omitted requirements, distorted meaning,
invented scope, unnecessary restrictions, and technical solutions that fail to deliver the
requested experience. Distinguish explicit user requirements from necessary derived choices
(with their basis) and revisitable assumptions; do not promote assumptions to requirements.

For a finding needing an owner decision, state a concrete scenario; reasonable divergent
assumptions or behaviors; their consequences; and a specific question, preferably with
meaningful alternatives. Ask only about unresolved decisions: exclude questions already answered
by supplied context, implementation questions, and generic questions.

## Definition of done and intent alignment

Check that the definition of done is clear and aligned with user intent: what must
be observably true for the user to consider the outcome complete? Use the request,
specification and relevant context, including acceptance criteria even when there is
no section named “Definition of Done”. Do not require a new heading or duplicate criteria.

Challenge missing, vague or misaligned completion conditions. Completing implementation
tasks, exposing technical metrics or passing tests alone is not enough if the user's
intended outcome is still unmet. Relevant failure or partial-success outcomes must also
have a clear completion boundary. Ask a concrete question about what evidence or outcome
would count as done when a material decision is unresolved; do not invent thresholds,
requirements or an additional approval gate.

Include definition-of-done gaps in the same ranked findings, not an extra questionnaire.
If existing criteria already establish observable completion aligned with user intent,
do not manufacture a question.

## Fresh-context input boundary

Give the fresh reviewer only:

- the original user request and actual owner clarifications/decisions;
- the exact current specification path and content identity, with readable current content;
- relevant context, constraints, accepted decisions, and memory; and
- this review contract and its runtime assignment.

Do not provide producer rationale, a producer transcript, or unrelated history.
Exclude producer conclusions and full unrelated transcripts; actual owner answers are evidence,
not the producer's paraphrased justification. The
reviewer is independent from the specification producer.

## Read-only review boundary

The reviewer returns findings only, not approval. The parent evaluates findings, routes
material decisions to the owner and substantive corrections to the source producer, then
inspects corrections. Neither path progresses with unresolved material intent gaps. Reuse
existing correction and approval gates; no separate TinySpec approval or automatic rereview loop.
The reviewer returns findings only. It must make no writes, implementation changes,
external actions, or further delegation. A read-only instruction/profile is an
operational boundary, not a security sandbox: available shell tools, including `bash`,
can still act outside it.

Bind the report output to the runtime invocation rather than persisting it as a
maintained artifact. This prompt does not authorize stage integration, corrections,
approvals, or implementation.
