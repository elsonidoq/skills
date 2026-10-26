---
description: "Sequential implementation task template"
---

# Tasks: [FEATURE NAME]

**Input**: [Relevant source or direct owner requirement]
**Executable task input**: [Adjacent JSON/YAML list or object containing tasks]

Apply the shared `task-generation` skill from the authorized suite installation.
Resolve `skills/planner/references/parsimony.md` through that installation, not a presumed
adopting-project layout. Use source-backed requirements and necessary choices; omit
inapplicable scaffolding rather than inventing constraints. Assumptions remain revisitable.
Discover actual project paths and installed stage instructions. Preserve the selected
executor and effort in runtime configuration without silent substitutions.

## [Coherent outcome]

- [ ] fix-title [Independently verifiable work description]
  - **Depends**: [Optional task IDs]
  - **Paths/context**: [Useful optional edit limits and interface pointers]
  - **Acceptance/context**: [Useful outcome-specific criteria or shared source pointers]
  - **Check**: [Relevant project command and expected behavior, when specified]

Keep routine tests and teardown inside the outcome. Separate only genuinely independent
work or prerequisites. Execution order comes from dependencies, not numbering/file order.

## Minimal executable intake

Emit JSON/YAML as a task list or `tasks` object. Each task needs a unique nonempty `id`
and `outcome` (or `description`). Optional `depends` references existing tasks without
cycles. Empty lists mean no work. No required order/context groups, source hashes,
approval refs, envelopes, gates, oracle mappings or execution-intent assessments.
Useful existing optional fields remain valid; no historical regeneration is needed.

## Verification and review

Acceptance/context and check commands are useful task detail, not universal startup fields.
Preserve owner/source-required checks, necessary security, persistence and integration
protections, and actual manual/permission gates. Additional hardening is optional and
nonblocking. Include justified interface checks within the delivery task; separate a
test/proof task only for an independently necessary prerequisite.
Optional `checks` accepts shell strings, argv lists or objects with `command`/`argv`;
`check` and `required[].check` use the same format. Put each authored deterministic required
command in one existing executable field once; semantic criteria remain prose and optional absent
checks remain absent. Run specified checks after the work and report their actual outcomes;
missing or failed checks are not passes.

Check readability, parsing into a list, ID/work description, uniqueness, dependency
references and cycles with the shared task linter. Relevant specified project commands
run later; no universal collection-count receipt. Preserve real required project checks,
actual action permission boundaries, unrelated work and the focused task-commit contract.
Task preparation does not itself start implementation or authorize external effects.
