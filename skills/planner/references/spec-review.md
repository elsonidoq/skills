# Standard specification skeptical review

## Purpose

Use this prompt core for one independent skeptical review of a current Standard
specification. Product intent and relevant behavioral completeness are review
perspectives, not a checklist. Return explicit **zero findings** when no material
unresolved decision remains, or no more than **five** highest-impact unresolved
decisions, ranked by importance.

For each finding, state a concrete scenario; reasonable divergent assumptions or
behaviors; their consequences; and a specific question, preferably with meaningful
alternatives. Ask only about unresolved decisions: exclude questions already answered
by supplied context, implementation questions, and generic questions.

## Fresh-context input boundary

Give the fresh reviewer only:

- the request;
- the exact current specification path and content identity;
- relevant context, constraints, accepted decisions, and memory; and
- this review contract and its runtime assignment.

Do not provide producer rationale, a producer transcript, or unrelated history. The
reviewer is independent from the specification producer.

## Read-only review boundary

The reviewer returns findings only. It must make no writes, implementation changes,
external actions, or further delegation. A read-only instruction/profile is an
operational boundary, not a security sandbox: available shell tools, including `bash`,
can still act outside it.

Bind the report output to the runtime invocation rather than persisting it as a
maintained artifact. This prompt does not authorize stage integration, corrections,
approvals, or implementation.
