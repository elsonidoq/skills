# Unified project memory — implementation tasks

## Source and executable contract

Requirements truth: [TinySpec](unified-project-memory-tinyspec.md) at preparation baseline
`f8a81f2417c038251836dd67b5e919c203ecbfcf`, SHA256
`f4643cfee2a3ee7451ac99357476507903344e4fcb512b592eba268a805de8b1`.
The separate [executable JSON](unified-project-memory-tasks.json) is canonical for whole work,
explicit exact `owned_paths`, scope/exclusions, commands and task-local REQUIRED pass/evidence
items. This document is its concise presentation, not additional executable restrictions.
Workers must read the JSON context: the current runner injects each task, not top-level context;
each task explicitly carries that instruction.

Producer read the actual [selected executor](../../.pi/workflow-executor.json):
`openai-codex/gpt-5.6-terra`, medium workers; fresh `openai-codex/gpt-6.1-sol`, medium reviewers.
This configuration remains unchanged. Installed planner `tinyspec-tasks` resolves to
`openai-codex/gpt-6.1-sol`, medium; it is not an implementation assignment.

## Ordered outcomes

- [ ] T001 Make Memory Handling the unified retrieval and authorized-write owner.
  - **Depends**: none
  - Own canonical memory skill and existing memory regression module. Deliver both evidence kinds,
    custom association/index retrieval, feedback authority and safety/non-bookkeeping mutations.
- [ ] T002 Route planning adapters, coordinator and checkpoint feedback seams to unified authority.
  - **Depends**: T001
  - Own the four planning skills, coordinator, checkpoint reference and corresponding planner
    checker/tests; only the SDD document's retired link destination changes. Preserve actual
    source → dependency/gate → REQUIRED → brief propagation and accepted ADR outcomes.
- [ ] T003 Preserve legitimate guidance through closeout, compaction and optional Jev triage.
  - **Depends**: T001
  - Own the three closeout skills and existing memory regression module. Retain conditional
    discovery, explicit write authority, compaction target/backup/approval and manual triage.
- [ ] T004 Produce unified new-adoption and bounded-refresh outputs with custom-path fixtures.
  - **Depends**: T001
  - Own initializer skill, tests and current output fixture. No implicit cleanup in other projects;
    inert legacy custom bytes remain preserved. Frozen historical inputs remain unchanged.
- [ ] T005 Align repository policy/governance and save the exact current owner guidance.
  - **Depends**: T002, T003, T004
  - Own memory-related AGENTS/README/REQUIREMENTS/constitution/routing/index/regression spans and
    relevant existing assertions. Preserve the verbatim parent-turn quote with current-feedback
    provenance in `memory/MEMORY.md`, without runtime investigation/testing/change.
- [ ] T006 Repair historical reference destinations before releasing destructive retirement.
  - **Depends**: T005
  - Own only the JSON-enumerated inbound Markdown records, including affected scope references and
    specs. Pin historical targets to exact revision/path; preserve approvals, answers, digests,
    failed/withdrawn attempts and historical schemas. No deletion or new archive/report.
- [ ] T007 Retire the exact legacy subsystem with composed reintroduction regressions.
  - **Depends**: T006
  - Own exactly the source-listed 41 legacy records, retired reference and existing regression
    owners. Consume T006's verified preservation first; delete no extra history. Verify all active
    consumers/new adoption/refresh together and reject positive second-store reintroduction.

The existing sequential runner selects T001 → T002 → T003 → T004 → T005 → T006 → T007.
The graph permits T002/T003/T004 after T001, but does not authorize parallel launches; shared
regression paths require explicit ownership coordination if the owner chooses concurrency.

## Why these boundaries

Seven independently verifiable outcomes fit Terra/medium by separating canonical authority,
planning propagation, closeout classification, adoption outputs and repository policy. Each keeps
its own relevant regressions and checkpoint. Reference repair is a real deletion prerequisite:
T006 verifies exact provenance before T007 removes bytes. T007 combines retirement with composed
acceptance rather than adding a report/cleanup/review chain. Existing local fixtures are sufficient
for this known instruction seam; no dependency unknown warrants a prototype or live probe.

Focused tests finish with predecessors plus their own result. New focused classes live in existing
modules; obsolete positive separate-owner assertions migrate with their corresponding delivery,
not via safety weakening. Full initialization runs at T005; full planner/checkpoint checks and
skills lint converge at T007. Failed/unavailable checks are not passes. Any unrelated baseline
failure is reported precisely, not repaired outside scope or silently waived.

## Traceability and limits

| Source | Task-local REQUIRED items |
| --- | --- |
| A1 — one association/index and retrieval | T001/V1; T002/V1; T003/V1; T004/V1; T005/V1; T007/V1 |
| A2 — authority, safety, no bookkeeping | T001/V1–V2; T002/V2; T003/V1–V2; T004/V2; T005/V2; T006/V2; T007/V1 |
| A3 — consumers and closeout | T002/V1–V2; T003/V1; T005/V1; T007/V1 |
| A4 — new adoption/refresh | T004/V1–V2; T005/V1; T007/V1 |
| A5 — exact guidance and historical disposition | T005/V1; T006/V1–V2; T007/V2 |
| A6 — delivery bounds and activation | T002/V2; T003/V2; T004/V2; T005/V2; T006/V2; T007/V3 |

[ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md#decision)
constrains neutral instructions/current authority and preserved historical approval at T002/V2,
T005/V2 and T007/V3. [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md#decision)
constrains ordinary scoped permissions and safety at T001/V2, T002/V2, T003/V2, T005/V2 and T007/V3.
Both remain constraints, not runtime-modification permission.

Historical retrieval is `git show 5088b25877467887dd41c9547197c6da43b3c165:<exact-path>`;
T006/T007 check each pinned target with `git cat-file -e` and relevant sections. Git availability
is authoritative, not remote publication/access. Uncertain extra substantive guidance/provenance
stops only its mapping/disposition for owner resolution, not a blanket archive or deletion.

All actual verification stays static/local fixture/manual contract inspection: it does **not**
prove model obedience, live workflow behavior or parent-wakeup delivery. No runtime work, issue
management change, installs/push, schema/stage/approval/model/executor changes, routine memory,
STATE/progress/summaries/evidence commits or wholesale historical archive/move. Source test
results remain baseline preservation, not implementation acceptance. The runner already owns a
fresh independent full-range implementation review; there is no duplicate review task.

Global skill activation requires a fresh-session Paseo handoff. The fresh agent verifies the
checkout/revision, current approvals, loaded skills and usable required capabilities before
approved workflow launch; no automatic reload/restart or owner slash-command instruction.

## Planning review and owner approval

Task preparation and its focused commit are authorized under the chosen TinySpec path. Parent
planner review completed after task checkpoint `bdfaf8503c11bed7f73903fa1b16a96af0a1f599`:
**READY for combined planning-only approval; no blocking findings**. This is the prescribed
TinySpec parent review, not an independent implementation review or implementation acceptance.

Reviewed content: source SHA256
`f4643cfee2a3ee7451ac99357476507903344e4fcb512b592eba268a805de8b1`;
canonical JSON SHA256 `188115ae9c25be6a81a0e106c77f21dca5bc262cd4281b1b2437032f1de847fd`;
human task presentation at the task checkpoint above (this review section adds no task semantics).
The parent inspected actual source/tasks, producer commits and owned diffs, relevant current
consumer/test/loader seams and source-to-task A1–A6/ADR traceability. Seven outcome boundaries
are proportionate to the selected executor: no milestone bundle, gratuitous prototype, duplicate
review task or report/cleanup chain. Real reference/provenance preservation precedes removal.
Explicit paths, dependencies, fifteen REQUIRED mappings, source/context delivery, exclusions,
authorization-neutral executable instructions and unchanged runtime/configuration are covered.

Actual planning validation:

- Both `check-task-order.py` invocations (JSON and Markdown): **PASS**, independently rerun by parent.
- Actual `coherence_workflow.intake.load_contract` and `verification.commands`: **PASS**;
  seven ordered tasks, command arrays, nonempty REQUIRED pass/evidence fields, existing/unique
  within-task ownership, explicit source/context instructions. No runner launch occurred.
- Inventory/reference checks: **PASS**; all 41 tracked legacy files plus retired reference match
  deletion ownership and exist at baseline via `git cat-file -e`; introduced local Markdown
  destinations resolve; source/JSON digests match; parent owned-range `git diff --check` passes.
- Source producer's baseline checks: workflow checker **PASS**, planner **155**, memory **9** and
  initialization **190** tests **PASS**. Unchanged suites were not rerun for bookkeeping.
- Implementation checks/new regressions, live model obedience, notification runtime and remote
  historical URL accessibility: **NOT RUN**. Runtime work is excluded; exact local Git retrieval,
  not remote publication, is the historical-provenance acceptance boundary.

### Combined owner approval — planning-only handoff

Owner approved the reviewed source, tasks and proposed scope with **“OK. I approve”**, after
confirming that Coherence is reusable across many projects and must use only each project's own
associated memory, never a suite/global memory or second guidance store. This clarification is
already covered by T001–T004; this approval record changes no task requirement.

Approved content is the source and canonical JSON at the SHA256 identities above, and the human
task/review presentation at commit `72829f6d879a0786b9dcbfde58d2a289cc02cc5f` (SHA256 before
this approval addition: `095d75f8de64aa2b95179b9b48b1a66efa5da624fc1c7c9ac88c117dcd6ef723`).
Approval covers the proposed seven-task scope, including removal of the 41 obsolete coordination
records and retired reference without relocation, precise Git historical references, unified quote
preservation and memory-only constitutional alignment. It does not authorize performing those
changes in this planning session.

The request remains **planning only**. Return this approved handoff without launching the
coordinator or deleting/relocating records. Later implementation needs explicit launch authority
and the existing applicable gates. Use `docs/plans/unified-project-memory-tasks.json` and the
unchanged `.pi/workflow-executor.json`; preserve exact owned paths, fifteen REQUIRED items,
current-content approval, checkpoint safety and the runner's fresh independent full-range review.
Global skill activation in Paseo remains a fresh-session handoff with checkout/current-approval/
loaded-capability verification, never automatic reload/restart. No implementation acceptance is
claimed by this approval.
