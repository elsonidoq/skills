# Coordinate Implementation — decisions and evidence

**Date:** 2026-10-18 UTC. **Stage:** Standard `spec_create` only, draft.
**Source:** [Full request and owner addendum](source-request.md).
**Specification:** [spec.md](spec.md). No specification approval is recorded or implied.

## D1 — Stack selection is completed, not hypothetical

**Repository-derived, empirically supported decision:** select candidate A, Python
LangGraph + SQLite checkpointer + Pi RPC/CLI + bounded declarative YAML adapter.
The parent supplied its independent acceptance of executed candidate A PASS at entry
to this stage, after source/tests/logs/diff inspection, independent verification of
22 manifest hashes and same-session real telemetry/deltas/headroom. Evidence commits:
`47bc57eac668af070facd9b973aa75bdc3f36e90` and
`b06ecd94209d33dd7ab91dae1c5e2fa7a5fbca8a` (settlement correction/current baseline).
The canonical report retains its historical “parent acceptance pending” wording;
that is the worker report's provenance, not a new unresolved stack-selection gate.

Canonical owners (reuse rather than duplicate library research):

- [Stack-validation report](../../stack-validation-report.md), “Acceptance matrix”,
  “Real result details”, “Authoritative remote verification”, and “Operational/glue cost and residual limits”.
- [Reproduction, state and telemetry semantics](../../docs/evidence/workflow-stack-validation/README.md).
- [Executed harness](../../docs/evidence/workflow-stack-validation/harness.py) and
  [five-test suite](../../docs/evidence/workflow-stack-validation/test_harness.py).
- [Current suite output](../../docs/evidence/workflow-stack-validation/logs/suite.log),
  [correction history](../../docs/evidence/workflow-stack-validation/logs/corrections.json),
  [real metrics](../../docs/evidence/workflow-stack-validation/logs/real-metrics.jsonl),
  [environment](../../docs/evidence/workflow-stack-validation/environment.json),
  [dated official remote responses](../../docs/evidence/workflow-stack-validation/remote-signals.json).

Tested compatible versions: **LangGraph 1.2.16**, **langgraph-checkpoint-sqlite 3.1.2**,
**Pi 0.87.1**, **PyYAML 6.0.3**, **jsonschema 4.26.0**, Python **3.12.3**, Git **2.43.0**.
The retained 2026-10-18 official GitHub/PyPI responses identify stable releases,
Python >=3.10, MIT licensing and active maintenance. GitHub's 43447 stars, 7407 forks
and 652 open issues are dated popularity/activity proxies, not users, installations,
quality guarantees or a benchmark. No new network research or dependency installation
was needed or performed for this specification: adequate version-specific local proof
was reused within its tested bounds.

**B — Temporal: NOT RUN. C — Prefect 3: NOT RUN.** A passed; neither fall-through nor a
fourth framework is authorized. The old shared-precondition failure and bounded harness
bugs are preserved in the report/corrections, not reclassified as framework failure.

## D2 — Tested limits become constraints, not production claims

The corrected full suite recorded **5 tests in 15.252 seconds, OK**. This stage read
that output and code; it did **not** rerun paid Pi calls or the stack-selection PoC.

| Supporting observation | Derived specification constraint | Required observable production acceptance |
| --- | --- | --- |
| Actual Pi tasks t1/t2 used session `01a14fdf-b04b-7355-907e-064a63c6ce66`; requested/observed `openai-codex/gpt-6.1-sol`, medium; inline skill markers observed | FR-005, 011–014: exact binding and compatible measured reuse; production skill loading still needed | Real configured skill/profile delivery, role isolation and per-task evidence, SC-002/003 |
| Real context 0→950→1138 differs from cumulative total 4046; task input deltas 1762/2137, output 73/74, cache 0/0 | FR-013, 020–021: current occupancy separate; continuity-aware usage and honest unknowns | Attributable per-attempt metrics/restart accounting, SC-005 |
| Controlled effective reserve 16384 makes toy threshold 483616, not advertised 500000; cutoff fixture 150000/149999 synthetic | FR-013, 015: resolve effective per-version/model/settings threshold; no long-task guarantee | Real input provenance plus boundary fixtures and safe pressure recovery, SC-003/004 |
| Pi 0.87.1 lifecycle correction: subscribe before prompt, demultiplex response IDs, wait current `agent_settled`; retries/races exercised synthetically | FR-016: never treat `agent_end` or stale settlement as completion | Actual adapter lifecycle checks before telemetry/checks/commit, SC-004/005 |
| Actual LangGraph/SQLite/Git/process SIGKILL/restart with synthetic workers after file-write and post-commit; receipt/parent/path reconciliation | FR-017, 025–027: checkpoints do not make external effects exactly once; uncertain work blocks | Production real Pi orphan/in-flight reconciliation and no duplicate writer/commit, SC-004 |
| Synthetic YAML profile-alias/skill/edge change; both aliases use same concrete real model | FR-003–005, 024: registered configuration, no arbitrary execution, exact dispatch proof | Supported actual configured variation and fail-closed validation, SC-002 |
| One synthetic verification-failure/repair, standalone status and projections from SQLite | FR-018–019, 028–030: bound repairs, explicit authority/projections, substantive review separate | Production check/review/owner-gate loop, projection recovery and separate status, SC-005/006 |

Accepted **for entering planning**, not waived production risks: real orphan-Pi recovery,
durable session reattachment, mid-task pressure, full permission/approval and independent
review enforcement, production all-run state/projection handling and untrusted YAML
hardening remain unproven. Power-loss/fsync/multi-host hardening is not proven or promised.
The toy lock and instruction/tool restrictions are not comprehensive enforcement or a
filesystem sandbox. No daemon was required; host exit stops execution and needs restart.
The small explicit feasible adapter glue remains required production work; do not treat
this experiment as a migrated runner or repeat its stack-selection exercise as future work.
Proof must be retained through applicable downstream consumers, with permanent realistic
production tests before reliance; failed/unrun proof cannot release those consumers.

## D3 — Owner-selected depth/profile and preparation authority

The parent reports the exact `ask_user` selection **“Standard — Sol/medium (recommended)”**
in a question explicitly binding planning producers and a **separate independent review
session**. Exact selected dispatch profile: `openai-codex/gpt-6.1-sol:medium`.
This is owner preference, not a family ranking or evidence of medium's benefit over low.

Carried assessment: remaining inference is source-to-spec and cross-contract consistency;
tool depth is bounded inspection/writing; weakest adequate oracle is substantive
source-to-spec review, not syntax. Scope couples runner/Pi/Git/skills/contracts; retained
Markdown is reversible and has no production execution effect. Applicable memory/guidance:
`memory/MEMORY.md` read whole, no entries; `memory/coordination/GUIDELINES.md` exists
and states that no approved project coordination guidelines are recorded. No applicable
guidance or inferred guidance is introduced. Explicit non-reliance on benchmark rankings. Terra and
Luna are plausible alternatives with no established advantage; owner selected verified
Sol/medium. No empirically established effort gain is claimed and no automatic substitution
or escalation is permitted.

**Observed for this producer:** session `01a14ff5-c5ee-77f0-ab7f-cf2c7de676f7` records
`model_change` provider `openai-codex`, modelId `gpt-6.1-sol`, and
`thinking_level_change` `medium`; environment agrees on provider/model. These are actual
local runtime observations, not inferred from selected suffix. The parent supplied usable
pi-subagents 0.73.1 / pi-ask-user 0.15.1 verification and detached launch readiness;
this child did not invoke delegation or owner questions and has no ambient extension-tool
availability claim beyond that supplied evidence.

Depth selection authorizes only bounded planning preparation and required focused commits.
`NO_BRAINSTORM_NEEDED` is the parent-provided settled-direction gate, not permission to
skip specification approval. Parent owns dialogue, independent review orchestration,
current-content inspection and specification approval; `plan_create` remains stopped.
Original request is planning-only: even later artifact approvals must not silently start
migration. No architecture, tasks, overall review or implementation was performed here.

## D4 — Workflow-wide session selection and review correction

**Owner-confirmed direction**, preserved verbatim in the source addendum: configurable
session reuse across the whole workflow with sensible defaults, eligible repair reuse of
the implementer and eligible review-session reuse. Applies to all agent nodes, not code
or gates; final review starts fresh and independent. Eligibility requires reliable current
headroom >=150000 to the effective automatic-compaction threshold, exact compatible
profile/model/effort/skills/tools/permissions/context affinity and no unresolved live work.
Reviewer and implementer roles never mix. Unknown telemetry means fresh or precise safety
blocker, not guessed headroom. No admission rule guarantees a long task avoids compaction.

**Mechanical defaults proposed for specification approval**, not fabricated prior approvals:
user-story context group; eligible same-group implementer reuse; repair original eligible
implementer first; independent-first reviewer then own eligible reviewer session for
correction rounds; explicit fresh-only; most-recently-settled eligible session then stable
identity tie-break; fresh/block if none eligible. `max_repair_attempts: 2` remains a
configurable proposal. The PoC's one-repair setting is not a production cap. Exact
production implement/repair/review profiles remain configuration choices requiring usable
permitted bindings and applicable approval; original Terra/Sol aliases are illustrative.

Worker/repair mutations require individual focused checkpoints. Schema-valid review
findings route only authorized focused repair tasks; changed scope returns to owner
approval. A shared session selector does not give a reviewer mutation authority.

## D5 — Contract impact and retained boundaries

Read installed contracts and mapped impact: `coordinate-implementation` presently owns
LLM batch/profile approvals, direct/delegated thresholds, recovery and final review;
`batch-routing.md` also serves planning/advisory consumers. Its three scripts enforce
textual/symbolic intake/batching/recovery and Git fixtures, not actual runtime orchestration.
`task-generation`'s two adapters and three scripts preserve REQUIRED item/dependency
semantics; a machine-readable intake will need deliberate compatibility, not a second
weaker contract. Planner and all three references preserve Standard source approval,
producer independence and renewal; architectural helper, TinySpec and brainstorming retain
planning roles. Review requester/reviewer/receiver, empirical debugger, handoff, finish,
adoption, memory and shared checkpoint/coordination contracts preserve their safety owners.

Suite impact includes `scripts/check-skills-lint.sh`, planner checker/trace/RPC smoke and
regression tests, task-checkpoint checks/Git fixtures, adoption/source fixtures, README,
REQUIREMENTS, AGENTS, constitution and docs routing. Static guards currently encode old
execution routing and will require bounded operative adaptation; safety guards must not
be deleted merely to make the migration pass. File-by-file designs and changes belong
to later planning, not this inventory. Existing generic bounded-extension preference does
not reopen the owner-selected validated engine; needed operative exceptions/amendments
must be identified under constitution governance before implementation approval.

This bundle changes no production contracts/configuration/code and preserves STATE,
memory and authoritative current-behavior documentation. Only the authorized feature
bundle and one discovery link are retained; the installed ignored feature pointer is
persisted without branch creation/switching. No global asset changed, so `/reload` is not
needed for this draft. Later global contract changes must tell the owner to run `/reload`.

## D6 — Installed specification capability and next gate

Observed SpecKit **1.0.12**, integration **pi**, scripts **sh**, sequential feature
numbering from metadata; existing features 001/002, selected directory
`specs/003-coordinate-workflow` independent of existing branch name. The actual readable
`.pi/prompts/speckit.specify.md` was followed; resolver/common and active spec/checklist
templates were read, resolver executed, resolved spec template copied before filling.
No `.specify/extensions.yml`: before/after specification hooks absent and skipped;
no branch script run. Ignored `.specify/feature.json` points to this feature. No tool
installation, generic substitute spec, shell-simulated slash or downstream stage invocation.

[Requirements checklist](checklists/requirements.md) records stage-local quality review,
not independent review or owner approval. Traceability is in spec.md; no extra research,
plan, schema, task or Epic file is produced. **Next gate: parent inspection and explicit
current-content owner specification approval before a fresh bounded `plan_create`.**

## D7 — Owner-selected SDK integration revision

Historical D1–D6 describe their original specification-stage state; do not read their
pending labels as current authority. [spec-approval.md](spec-approval.md) records owner
approval of the original SHA-256 and configurable defaults, including two repairs. During
this same fresh Sol/medium `plan_create` pass the owner answered **“Allow the thin SDK host
(recommended)”** through the parent's `ask_user`. [Source addendum](source-request.md#sdk-integration-owner-direction)
preserves the scope: update FR-002 and continue design, **not implementation**. Renew
specification approval for the revised digest before tasks. Do not alter the historical
approval record or claim this transport was PoC-tested.

Repository-derived architecture: a thin version-pinned official Pi SDK subprocess with
JSONL protocol permits direct effective SettingsManager telemetry and sanitized outgoing
request observations without recreating Pi trust/settings resolution in Python. Python
LangGraph and one SQLite database remain sole workflow/operation authority. Pi's own
session files persist conversation only. [Canonical research](research.md) identifies
inspected SDK/provider spans, alternative native-RPC limitations and remaining proof.
The host has no task selection, routing, approval, repair-policy or Git authority.

[Draft plan](plan.md), [data model](data-model.md), [contracts](contracts/README.md) and
[quickstart validation](quickstart.md) are design only. No tasks, overall independent
review, implementation authorization or production PASS is implied. Source review found
no other specification defect; all previously approved constraints/defaults remain.

## D8 — Focused SDK evidence consumed, no repeat experiment

Owner chose **“Run the focused PoC (recommended)”**; parent paused this plan producer and
accepted separate evidence commit `6939f113c199c557f8b6c2b3afacc5cfb81a78a0` within tested
bounds after independent source/log and no-paid-check inspection. [Canonical SDK research
interpretation](research.md#r10--accepted-sdk-experiment-changes-production-constraints)
links exact sources/results. Six real outgoing requests, two real same-session tasks,
actual skill expansion and effective threshold are distinct from synthetic cutoff/summary-
route guard tests. Real retry/compaction and durable session reopening were not induced.

Critical correction: wrap public `agent.streamFunction`, composing per-call/SDK payload
hooks first; onPayload alone misses summaries. Real host death left detached tool writing,
so production lock + durable operation/process registry + gated launch/controlled tool
gateway must precede mutation. Unknown ownership/quiescence blocks. A PID, quiet file window
or exited host is not sufficient evidence. No new supervision platform/daemon, arbitrary
sandbox promise or workflow authority in Node is introduced. Killed usage/cost stays unknown.

The same originating plan resumes from known six partial paths at baseline `6939f11`.
Only FR-002's authorized integration seam and associated status/provenance/assumption text
change in the spec; original approval file stays historical. **RENEW_SPEC_APPROVAL** before
separate task production. No code implementation, task generation or overall review here.

## D9 — Local lifecycle feasibility accepted; mandatory orphan alarm

Owner requested simple sleep60-survivor tracking/cleanup and an alarm after logical worker
completion. Parent accepted `00b7a4d908a9ab2a6bb650deb6803b7ebe6947de` after full source/event
inspection and independent same-four-case rerun. Earlier unavailable cgroup discovery is
historical: owner enabled delegation, parent verified own-child controls, and the real
fixture proved exit0/exit1/SIGKILL+setsid/TERM resistance plus distinct-controller reentry.
No agent service modification, provider call or new platform survey occurred.

Choose the smallest supported production seam: Linux delegated cgroup-v2 adapter for trusted
local tools, project-configured parent and validated own-child identity, populated oracle;
no daemon, generic container/service platform or PID-only fallback. Preserve tested limits:
not adversarial same-UID migration prevention, remote effects or production durable-registry/
spawn/reboot proof. Current capability is proven only in its inspected environment; production
preflight and actual helper crash-phase tests remain REQUIRED before reliance, not another
stack/lifecycle selection experiment. Canonical research R12 links spans→constraints→checks.

FR-017 gains the owner-required durable ORPHAN_PROCESS alarm/status with blocked replacement
until cleanup+partial-work reconciliation. Reusable idle session host is separate from task
tool lifetimes. Optional notifications do not replace the authoritative alarm. Original
approval remains immutable; revised spec (FR-002/017 and provenance/status/assumption text)
needs **RENEW_SPEC_APPROVAL** before tasks. All other defaults and planning-only gates remain.
