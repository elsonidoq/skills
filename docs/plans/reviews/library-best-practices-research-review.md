# Library best-practices research — preparation review

Producer: planner. Selected depth: TinySpec. Status: reviewed preparation; owner combined approval GRANTED for the source/task hashes below and bounded implementation scope.

## Current content

- Source: `docs/plans/library-best-practices-research.md`, SHA-256 `508ff3de0678be03377b9c92328a8b00960465bf4e7c69d686f126a6b1e2a19f`.
- Tasks: `docs/plans/library-best-practices-research-tasks.md`, SHA-256 `6406544f2c2a44ac9aec602d4357e5e74c8c9cd0b1d7a6f012803d0c843ddcdd`.

Owner selected TinySpec preparation and GPT-6.1 Sol for bounded preparation. Explicit requirement: both TinySpec and Standard must incorporate dependency research. Original request is captured in the source's scope, research contract and R1–R6 acceptance.

## Planner assessment

Source-to-task review covers all R1–R6: shared research contract T001; planner early detection/direct Standard handoff and review T002; TinySpec including direct entry T003; Standard helper including standalone use and bounded canonical-document writes T004; deterministic positive/mutation/scenario checks T005; discoverability and accurate evidence limitations T006; integrated acceptance T007. All seven tasks are bounded sonnet-class (0% opus-class), have earlier prerequisites and contiguous stages. No implicit forward producer or unresolved material design gate identified.

Preserved constraints: read-only preselection, existing approvals and depth choice, repository-first reuse, proportional research, version/provenance, documented recommendation versus derived decision versus assumption, durable target-repository documentation, no fixed target-project paths, no new standalone research workflow, no arbitrary helper documentation permission. No execution/coordinator/brainstorm/task-generation skill rewrite is included. The helper's existing SpecKit-only write boundary is addressed explicitly, not silently bypassed.

Parent published producer outputs and corrected publication statements only. The task artifact's embedded acceptance report is historical producer-stage evidence, not final approval. Global skills, scripts and configuration remain unchanged.

## Validation performed by parent

- `PYTHONDONTWRITEBYTECODE=1 python3 skills/task-generation/scripts/check-task-order.py docs/plans/library-best-practices-research-tasks.md`: PASS.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-planner-workflow.py`: PASS (existing static instructions).
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-planner-workflow.py`: PASS (56 existing tests).
- `git diff --check`: PASS; newly published planning artifacts also inspected manually.
- Skill lint, new feature tests, live research/model/real-SpecKit behavior and independent implementation review: NOT RUN. This is planning review, not implementation verification or model-obedience proof.

## Approval boundary

Combined approval must name current source/tasks and bounded implementation scope before any skill edits. The owner initially requested a proposal and approval-before-modification; preparation selection did not grant implementation authority. If the owner approves implementation explicitly, the next phase is coordinator preflight, not planner execution. If the owner requests planning-only, preserve these artifacts and stop. Owner answer to the combined approval gate: “I approve the implementation. Make sure there are no regressions in the skill behavior.” This authorizes the bounded implementation against the source/task hashes above and starts coordinator preflight. Preserve existing behavior and explicitly report limits of regression evidence. Model/reviewer and commit prerequisites remain coordinator gates; approval does not grant push, deployment, or paid/live research operations.
