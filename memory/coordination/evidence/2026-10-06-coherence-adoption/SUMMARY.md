# Coherence adoption and documentation indexes — run evidence

Date: 2026-10-06. Tags: adoption, memory association, documentation indexes.
**Status:** adoption and directory indexes committed; structural checks PASS. Owner chose full adoption plus indexes and approved `AGENTS.md`, `memory/MEMORY.md`, `docs/index.md`, `docs/plans/index.md`, `docs/plans/reviews/index.md` and this factual run/index checkpoint; a later explicit approval added only `skills/initialize-coherence/scripts/test_contract.py` to correct a stale pre-adoption assertion. Initial checkout clean at `22adfc6`; no prior gotcha-memory association, no `STATE.md`, no persistent database documented for this configuration suite. Existing coordination history/guidelines untouched.

| Task | Baseline → result | Checks / outcome |
| --- | --- | --- |
| Marked adoption and empty gotcha index | `22adfc6` → `e09903a`; evidence `2dbcbfe` | pi 0.87.1, subagents 0.73.1, ask-user 0.15.1 present; initializer static fixtures 135 OK; scoped diff whitespace PASS; index has no fabricated entries. Requirements and owner approval checked before writes. |
| Directory indexes, association routing and fixture correction | `2dbcbfe` → `c8ae7d2` | New indexes list all 20 direct plans and 18 direct reviews; all introduced links resolve. First initializer run 134/135 passed: one pre-adoption assertion contradicted approved association, **not** an adoption/behavior failure. Owner separately approved its causal test correction; rerun 135 OK, lint 12 OK, direct-file maps/links and diff whitespace PASS. No test protections removed. |

No guideline update proposed. No installation, deployment, paid/live probe or unrelated-project adoption. `planner` is discoverable; no substantive planner handoff is needed for this structural-only request. Static fixtures and file/link checks do not demonstrate runtime agent behavior or substantive documentation accuracy. Structural owner/index readiness only; no application implementation or database schema claimed.
