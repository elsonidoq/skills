# Routing and recovery data / state model

This describes existing skill/Markdown carriers and checks; it does **not** require a new database, JSON schema, or global registry. See [approved spec](spec.md), [plan](plan.md) and [retained source evidence](research.md).

## Concepts and relationships

| Concept | Minimal fields / provenance | Invariants |
| --- | --- | --- |
| Family | owner-facing Luna, Terra, Sol or Astra | A family is neither an effort setting nor an automatically usable provider/model ID. |
| Concrete binding | provider/model version, permitted scope, callable status, observed tools/context and verification time | Configuration/catalog listing alone does not prove dispatchability. Recheck at assignment and before launch. |
| Effort capability | supported effort values for that binding, provider/Pi evidence and observed request behavior; explicit nonadjustable setting when applicable | Never enumerate efforts by analogy from another family or request an unverified level. |
| Advisory benchmark signal / retained initial guidance | source URL/archive logical row or span, inspector/date, reported provider/version and effort if present, metric/unit/direction, dataset/split/harness/setup, result, source label, verification limits, applicability and uncertainty | Coverage is advisory, not a runtime eligibility gate. Unknown snapshot, reasoning mode, date or effort stays unknown. Missing/conflicting task-relevant evidence triggers targeted research or an explicit bounded owner uncertainty decision, not automatic exclusion. Do not rank noncomparable scores or invent an exact-pair result from composites/other versions. Source facts and original guidance persist after guidelines evolve. |
| Project-owned raw archive | supplied source identity, byte-preserving path and SHA-256; compact research/index discovery and selective row keys | Retain the supplied 369 rows without automatic whole-CSV agent intake or full-dataset prompts. Routine agents read rubric/citations; matching-row retrieval is on demand. Archive is reference evidence, separate from execution history and mutable guidelines. |
| Routing proposal / selection / approval snapshot | task or reviewer identity; family and exact proposed binding; independent effort rationale; provider-documentation and runtime/tool/context evidence or explicit unresolved status; task risk/complexity/oracle/context/cost profile; local outcomes, comparable benchmark signals, gaps/uncertainty and research or owner uncertainty disposition; proposed versus owner-selected state and artifact revision | A complete reviewed proposal for every task and independent reviewer precedes the *single* final scope-and-assignments approval. Provider-documented permitted usable runtime/effort and owner routing authorization are hard gates; unresolved candidates are visibly non-dispatchable, never offered as usable. Benchmark absence alone does not block a supported pairing. No fabricated suitability score, permanent family rank or automatic max effort. One answer may approve distinct scope and listed selections; no routine post-approval assignment question. Changed/unavailable approved assignment stops dispatch for renewed choice, never silent substitution or skipping a missing retry family. |
| Task contract | outcome/source, bounded file/operation scope, exclusions, prerequisites/producer checks, instructions, outputs, REQUIRED acceptance, selected family/effort | Every task is independently verifiable. Luna requires unusually explicit ordered steps and an executable failure-detecting oracle, not vague “looks right.” |
| Attempt | run/task id, ordinal, family/binding/effort, task baseline, owned files, failed invocation/diagnosis, checks, observed completion and cost, commit SHA or absence, evidence links | New execution after a failure consumes the next ordinal; resume/session rotation does not reset the count. Record unknown outcomes as unknown. Never claim a failed check is verified success. |
| Recovery pair | failed task implementation commit or newly made FAILED-ATTEMPT checkpoint; later distinct ordinary inverse commit; evidence before and after each, baseline/ownership/dependency checks | Only wholly task-owned changed content may be checkpointed; evidence first, then failed-attempt commit if needed, then ordinary inverse, restoration verification, separate evidence checkpoint. No empty commit, reset, unrelated loss or dependent rollback. |
| Project reflection | factual indexed run/task evidence, scoped proposal, exact guideline baseline/result and owner decision | Benchmark baseline remains separately discoverable. A failed Luna attempt does not become a permanent guideline or automatic model ban. |

## State transitions

```text
TASK_READY + provider-documented permitted usable binding/effort + owner selection
  + advisory rubric/evidence and resolved research-or-owner uncertainty disposition
  -> ATTEMPT_1_RUNNING

ATTEMPT_N_RUNNING
  -> VERIFIED_TASK_COMMIT -> integration / independent review / evidence checkpoint
  -> FAILED_INSPECTION (required check, reviewer finding or later defect)
  -> BLOCKED_UNKNOWN (failed invocation/cause or execution status unavailable)

FAILED_INSPECTION (even on final Sol / exhausted attempt or unavailable successor)
  -> EVIDENCE_CHECKPOINTED_BEFORE_MUTATION (cause, baseline, ownership,
     intended task commit/inverse, dependencies, permission and remaining budget)
  -> FAILED_ATTEMPT_COMMIT (only if task-owned changed content not already committed;
     label NOT VERIFIED; failed checks explicitly recorded)
  -> FAILURE_SHA_AND_CHECK_STATUS_EVIDENCE_CHECKPOINTED (existing or new task
     commit SHA, failed-check status and exact intended inverse; REQUIRED before inverse)
  -> ORDINARY_INVERSE_COMMIT (exact failed task commit only)
  -> RESTORED_BASELINE_VERIFIED + RECOVERY_EVIDENCE_CHECKPOINTED
  -> STOP_FINAL (budget exhausted, no qualified next family, or environment still blocked)
     OR NEXT_ELIGIBLE_FAMILY_SELECTED (Luna -> Terra -> Sol, or Terra -> Sol)
  -> ATTEMPT_(N+1)_RUNNING (only on the selected-next-family branch)
```

**Separate transition guards:** Failure inspection and factual evidence remain required even when no attempts remain or the next family/effort/benchmark disappears. Before a failed-attempt commit or inverse, verify task-only ownership, baseline, approvals/permission, dependent impact, evidence checkpoints and ordinary inverse safety; if these fail, preserve evidence and stop *mutation*, not failure reporting. If the intermediate failure-SHA/check-status evidence checkpoint fails, do **not** create the inverse. Only the next-dispatch branch checks remaining attempt budget, independently justified supported effort, owner-selected permitted usable runtime binding, advisory evidence/uncertainty disposition and resolved environmental cause. A missing benchmark row alone never fails that guard. These dispatch-only gaps never prevent safe recovery of the just-failed task. A task with no changed content has no failure/inverse commit pair and cannot automatically retry under this recovery policy; record the event without inventing a commit. A final Sol or third-attempt failure with safe task-owned changes still records/checkpoints and ordinarily inverts them, then stops without further dispatch. Astra can be selected initially or for an independent review under its own evidence and owner gates, but is never an automatic fourth attempt.

## Read and write boundaries

- The plan/task artifact references compact evidence; it does not load whole CSVs automatically or copy full datasets into prompts. `docs/index.md` → durable `research.md` → project-owned raw archive → matching rows only is the benchmark discovery path, independent of guideline supersession. Routine planning reads compact approved coordination guidelines first; project execution history remains index-first, justified and relevant-only.
- Factual attempts belong in the project's run/task files and compact index, never in global skill text or a growing transcript. A guideline change needs separately approved exact content, even when task execution was authorized.
- Failure commits and their inverses are Git history entries, not a storage substitute for attributable attempt, diagnosis, benchmark citation, effort and review evidence. Never persist secrets or raw sensitive failure payloads.
