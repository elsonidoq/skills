# Planner job-first — tasks

Source: [TinySpec](planner-job-first-tinyspec.md), A1–A5.
Authorization/review: [run evidence](https://github.com/elsonidoq/skills/blob/5088b25877467887dd41c9547197c6da43b3c165/memory/coordination/evidence/2026-10-08-planner-job-first/SUMMARY.md).

- [ ] T001 — Job-first planner contract and focused regression

- **Depends**: none.
- Outcome: prominent job-first rules govern both paths and stage briefs; agents
  advance authorized stages rather than substituting administrative loops.
- Files: `skills/planner/SKILL.md`, `scripts/check-planner-workflow.py`,
  `scripts/test-planner-workflow.py`; add source/tasks discovery in `docs/plans/index.md`.
- REQUIRED T001/V1 (A1–A4): inspect the skill diff for job primacy, small-fraction
  bookkeeping, finite preparation, evidence reuse, terse records and preserved gates.
  Evidence: bounded diff and independent review disposition.
- REQUIRED T001/V2 (A5): `python3 scripts/check-planner-workflow.py` and
  `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-planner-workflow.py` pass, including
  targeted mutations removing the job-first obligations and deleting the whole section.
  Evidence: command output/count; establish new checks fail before skill changes.
- REQUIRED T001/V3: `git diff --check` passes; source/task discovery links resolve.
  Evidence: command output and inspected target paths.
- Capabilities/gates: local file tools, Python 3, Git; approved routing and combined
  artifact approval before implementation. Fresh independent final review after commit.
- Verification effort: existing focused static checks plus bounded manual contract review;
  no added test infrastructure or live model exercise. Runtime time allocation NOT RUN.
- Exclusions: numeric quotas, time tracking, shared contract changes, push/deployment.
- Checkpoint: focused task commit, separate indexed evidence commit; preserve unrelated work.
