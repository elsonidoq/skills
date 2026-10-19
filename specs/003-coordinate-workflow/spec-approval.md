# Coordinate Implementation specification approval

> Current-content status: latest owner implementation/batching direction supersedes the original planning-only boundary for the bounded migration. The token-vs-separately-chargeable-service correction and FR-040 await targeted current-content independent review/coordinator audit; no renewal review is claimed. Original manual/safety/permission gates remain. See source-request.md (latest owner directions).


Producer: planner; depth: Standard. Specification-to-planning approval only.

- On 2026-10-18 the owner selected **Standard — Sol/medium (recommended)** through `ask_user`, explicitly selecting `openai-codex/gpt-6.1-sol:medium` for planning producers and a separate independent review session.
- After the parent inspected the specification bundle and presented its executive brief, the owner answered **Approve specification** through `ask_user`. This includes its proposed configurable defaults: workflow-wide role-safe session reuse with >=150000 effective-compaction headroom, original eligible implementer preference for repair, fresh-first independent review followed by eligible reviewer-session reuse, deterministic latest-settled/stable-identity tie-breaking, fresh-only override, and `max_repair_attempts: 2`.
- Approved specification: `specs/003-coordinate-workflow/spec.md`, SHA-256 `1a849e288552a2d98d29c6e709b92675230ca3a53808c872d0ace6658d6d7f2c`. Source bundle commit: `adce2aade745e673f124ce09c5ba489dbe727444`; equivalent provenance-only correction: `810c7d5ab5536c65718ff65134acf8e50b396684` (existing empty coordination guidelines were incorrectly described as absent; requirements, decisions, scope, dependencies and acceptance remained unchanged).
- Parent checks: preserved original-source byte prefix, actual requirement/source coverage and links inspected; `check-planner-workflow.py`, `check-task-commit-contract.py` and committed whitespace checks PASS. Producer quality checklist passed with the documented settled-technical-constraint exception. No independent overall review or production implementation validation has occurred.
- Authorization: immediately begin the fresh delegated Standard architecture-planning stage using the selected Sol/medium profile, then separately create tasks and obtain independent overall review and final artifact approval. The original request remains **planning only**; this approval does not authorize migration implementation, production/global code changes, deployment or additional live probes.
- Approved specification changes require renewed owner specification approval before downstream release. Artifact status labels and commits do not substitute for this current-content evidence.

## Renewed specification approval — 2026-10-19

After the parent inspected the revised specification and architecture, independently validated eight design schemas and eighteen examples, and presented the executive approval brief, the owner answered **Approve revised specification** through `ask_user`.

- Current approved specification: `specs/003-coordinate-workflow/spec.md`, SHA-256 `766f46a18e60066d1597f5465678ab509efb5c22b178ed5659b6a7eb8c2f1f51`, content commit `9d33fbd2044e09f290c49d2f2d9e406e09bc5190`.
- Renewal includes the SDK integration, mandatory survivor alarms, original-session question pinning, automatic same-parent actual `ask_user`, active owner controls, upfront spending/capability authority and maximum inside-envelope autonomy. Original defaults remain >=150000 effective-compaction headroom and two configurable repair attempts.
- Accepted evidence remains bounded: original graph, SDK, local process-containment and interactive PoCs. Production crash/pressure/UI-reconnect/authentication/budget enforcement and implemented integration remain REQUIRED checks, not completed features.
- Authorization: immediately proceed to a separate fresh Standard task producer from this exact specification and its derived architecture, then independent overall review and final owner artifact approval. This is not final plan/task approval or production spend authorization.
- **Planning-only boundary remains explicit: no migration implementation is authorized, including after eventual final artifact approval.** Changed specification content requires affected renewal again; no historical approval is relabeled.
