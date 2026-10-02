## Review

**No issues found.**

**Verdict: READY with separately authorized validation follow-up.**  
**Merge verdict: OK with notes.**

This targeted recheck closes F1, F2, and F3. No related regression found in the corrective code or test predicates.

### Finding dispositions

| Finding | Disposition | Verified evidence |
|---|---|---|
| **F1 — Orphaned choice result accepted** | **Fixed** | `scripts/planner-trace.py:40–52,79–103,110–112` validates tracked starts, rejects wrong-tool/orphaned/reversed/duplicate lifecycles, prevents invalid choice gates from authorizing selection, and requires an observed completed lifecycle. |
| **F2 — Disconnected shared invocation escaped checks** | **Fixed** | `scripts/check-planner-workflow.py:63–69` checks operational preselection invocation, mode/readiness target, owner dialogue, and bounded selected-production application. `:78–80` requires actual TinySpec/direct-task adapter calls. |
| **F3 — Undocumented title-prefix constraint** | **Fixed** | `scripts/planner-trace.py:66–69,93–103` validates the supervisor’s exact `expected_title` against offered options and the returned selection, independently of normalized depth. No first-word convention remains. |

### Regression evidence

- `scripts/test-planner-workflow.py:225–238` covers orphaned freeform results, wrong-tool starts, reversed events, and duplicate starts/results.
- `:251–256` covers duplicate and orphaned approval lifecycles.
- `:87–100` changes only caller operational instructions while retaining prerequisite mentions and primitive files; each mutation requires its relevant diagnostic.
- `:240–249` accepts punctuated/prefixed titles through explicit supervisor mapping and rejects a mismatched mapping.
- `:40` now accurately names the ledger test `test_preservation_ledger_maps_retired_carriers`, without implying chronological proof.
- `docs/plans/planner-regression.md:39–59` documents lifecycle requirements, exact title mapping, trusted inputs, and the oracle’s remaining limits consistently with the implementation.

The original F1 counterexample now produces an orphaned-result error and cannot set `selected`. Later arrival of the missing start cannot repair the invalid lifecycle. The original F2 deletions now fail caller-local predicates rather than relying on the shared primitive’s continued existence.

### Verification inspected

The supervisor’s `/tmp/planner-review-reproduction.log` records **11 failing subcases before correction**.

The command-labelled `/tmp/planner-final-verification.log` records:
- Suite lint: **23 skills, zero failures**.
- **56 passing offline tests across six suites**.
- Both fixture dependency parsers: **PASS**.
- Shell syntax, Python compilation, and diff whitespace: **PASS**.

These are inspected supervisor results—not reviewer-executed commands.

### Scope and remaining limits

This was a read-only recheck of the five named corrective files, prior findings, and supplied verification evidence—not a new full implementation review. No edits, commands, agents, installations, or live probes were performed.

Real-agent behavior, installed SpecKit integration, differential scenarios, and global installation remain **NOT RUN** and require separate authorization. Their absence does not block this correction’s acceptance. Static predicates and synthetic traces still do not establish semantic brief completeness, model obedience, or full mutation-path isolation; the documentation states those limits accurately.