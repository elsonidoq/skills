# Routing and recovery data / state model

This describes existing skill/Markdown carriers and checks; it does **not** require a new database, JSON schema, or global registry. See [approved spec](spec.md), [plan](plan.md) and [retained source evidence](research.md).

## Concepts and relationships

| Concept | Minimal fields / provenance | Invariants |
| --- | --- | --- |
| Family | owner-facing Luna, Terra, Sol or Astra | A family is neither an effort setting nor an automatically usable provider/model ID. |
| Concrete binding | provider/model version, permitted scope, callable status, observed tools/context and verification time | Configuration/catalog listing alone does not prove dispatchability. Recheck at assignment and before launch. |
| Effort capability | supported effort values for that binding, provider/Pi evidence and observed request behavior; explicit nonadjustable setting when applicable | Never enumerate efforts by analogy from another family or request an unverified level. |
| Qualifying benchmark | source URL/location/span, inspector/date, tested version **and reported effort**, workload/harness/conditions, measured result and limitations | Exact version + effort + task-relevant measured result are mandatory for initial routing eligibility. Estimated composite rankings, qualitative advice, uninspected links and older-version results alone do not qualify. Source facts persist after guidelines evolve. |
| Routing candidate | binding + one effort + qualifying benchmark(s) + task-applicability rationale + owner-selected authorization | Eligible only while both benchmark and usable capability evidence apply. Owner selection is distinct from a recommendation. Missing next-family candidate blocks escalation rather than skipping it. |
| Task contract | outcome/source, bounded file/operation scope, exclusions, prerequisites/producer checks, instructions, outputs, REQUIRED acceptance, selected family/effort | Every task is independently verifiable. Luna requires unusually explicit ordered steps and an executable failure-detecting oracle, not vague “looks right.” |
| Attempt | run/task id, ordinal, family/binding/effort, task baseline, owned files, failed invocation/diagnosis, checks, observed completion and cost, commit SHA or absence, evidence links | New execution after a failure consumes the next ordinal; resume/session rotation does not reset the count. Record unknown outcomes as unknown. Never claim a failed check is verified success. |
| Recovery pair | failed task implementation commit or newly made FAILED-ATTEMPT checkpoint; later distinct ordinary inverse commit; evidence before and after each, baseline/ownership/dependency checks | Only wholly task-owned changed content may be checkpointed; evidence first, then failed-attempt commit if needed, then ordinary inverse, restoration verification, separate evidence checkpoint. No empty commit, reset, unrelated loss or dependent rollback. |
| Project reflection | factual indexed run/task evidence, scoped proposal, exact guideline baseline/result and owner decision | Benchmark baseline remains separately discoverable. A failed Luna attempt does not become a permanent guideline or automatic model ban. |

## State transitions

```text
TASK_READY + verified binding + effort + matching benchmark + owner selection
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

**Separate transition guards:** Failure inspection and factual evidence remain required even when no attempts remain or the next family/effort/benchmark disappears. Before a failed-attempt commit or inverse, verify task-only ownership, baseline, approvals/permission, dependent impact, evidence checkpoints and ordinary inverse safety; if these fail, preserve evidence and stop *mutation*, not failure reporting. If the intermediate failure-SHA/check-status evidence checkpoint fails, do **not** create the inverse. Only the next-dispatch branch checks remaining attempt budget, task-relevant exact-version/effort benchmark, supported effort, owner-selected usable runtime binding and resolved environmental cause. These dispatch-only gaps never prevent safe recovery of the just-failed task. A task with no changed content has no failure/inverse commit pair and cannot automatically retry under this recovery policy; record the event without inventing a commit. A final Sol or third-attempt failure with safe task-owned changes still records/checkpoints and ordinarily inverts them, then stops without further dispatch. Astra can be selected initially or for an independent review under its own evidence and owner gates, but is never an automatic fourth attempt.

## Read and write boundaries

- The plan/task artifact references evidence; it does not copy full benchmark datasets into task prompts. `docs/index.md` points to durable source-backed `research.md`; routine project planning reads compact approved coordination guidelines, opening project execution history index selectively only when justified.
- Factual attempts belong in the project's run/task files and compact index, never in global skill text or a growing transcript. A guideline change needs separately approved exact content, even when task execution was authorized.
- Failure commits and their inverses are Git history entries, not a storage substitute for attributable attempt, diagnosis, benchmark citation, effort and review evidence. Never persist secrets or raw sensitive failure payloads.
