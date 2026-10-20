# Lean workflow runtime — TinySpec

**Status:** source preparation only; no tasks, design approval or execution authority.

## Outcome and bounds

The owner needs the implementation workflow to get real coding done with a few
principled checks, rather than becoming a defensive proof system: “This should end
up being deleting a lot of code and just implementing a couple of principal checks.”
The owner explicitly chose TinySpec over disproportionate Standard planning, then
authorized one Sol/medium source producer and this discovery link. This is a full
runtime simplification, not merely a fix for one file-read limit.

Retain the useful LangGraph/SQLite runner, thin Pi host and focused Git checkpoints;
prune redundant enforcement rather than build a replacement platform. The proposed
product path is **validate → execute task → configured checks → focused commit → next →
independent final review**. It covers runtime, host, workflow configuration, necessary
schemas and operative skills/docs. It does not overhaul planner routing or its fresh
producer/exact-profile requirements, implement the monitor app, install dependencies,
change global settings, or introduce a compatibility framework or new tracker.

Provenance: owner planning direction following `c395c01c60f8f91d2c3a7ef33980d54eb8f66a9d`
and its [parsimony policy](../../AGENTS.md#parsimony-and-actionable-checks);
original request was supplied in `/tmp/coherence-workflow-lean-planning-c395c01.md`
(the essential requirements are retained here because that file may expire).
The current monitor attempt `monitor-app-20261020-0ec48f3fe91b` was recorded running,
reserved and T001-active, with a stopped controller and incomplete SDK turn. Its
`local_guard_or_protocol_blocker` at `tool_poll` has **no proven exact cause**.
Clean Git or a stopped-controller record does not establish settled effects.
Preserve that attempt, the earlier intact archive, ignored nested-repository evidence,
original source/approval records and all unrelated material. This source grants no
start/resume/control/archive/reset, source renewal, process adoption or recovery.

## Proposed operating contract

Simplified-runtime readiness is five independent facts, checked at admission and again
only where a relevant change invalidates them—not the whole proof chain before every action:

1. **Executable work:** tasks have outcomes, owned paths, valid dependency order and
   task-local REQUIRED checks; reject the affected malformed contract with its repair.
2. **Usable configuration:** the selected workflow identifies an available exact
   executor/effort, skills, launcher and tools capable of the actual work. Report the
   missing capability and how to supply it; do not install or silently substitute.
3. **Approved authority:** current content and scope are approved; exceptional external
   actions have explicit permission. Identify the affected approval/action and renewal
   needed. Ordinary coding within that scope needs no repeated owner permission.
4. **Safe ownership:** one writer, known Git/task baseline and safe owned paths; preserve
   unrelated staged, unstaged and ignored material. Conflicting ownership or unknown/live
   effects stop the affected mutation and name what must be reconciled.
5. **Runnable verification:** required check commands and their dependencies are usable.
   Report an unavailable check and corrective setup, not a synthetic green substitute.

Five execution rules complete the contract:

- Execute dependency-ready work under the selected configuration; allow normal scoped
  source reads/searches/edits and test commands using existing SDK/tools where suitable.
  Keep cheap path/credential/external-action protections and own-child process custody;
  do not promise an adversarial same-user sandbox or permit workers to commit.
- Return ordinary safe tool errors to the executor with the failing operation and useful
  corrective action, so it can correct and continue. A known failed read/validation or
  nonzero check is not an uncertain SDK turn. Unknown side effects, lost host/process
  custody or ambiguous commits instead stop affected work: inspect before any replay
  or replacement, and never blindly retry an expensive failed invocation.
- The runner verifies actual REQUIRED results and original manual/permission gates,
  inspects the owned diff and makes one focused task commit before dependent mutation.
  Preserve hooks/signing and unrelated index state; no empty success or configure-around.
- Persist enough ordered history to explain work and reconcile interruptions. Optional
  usage/pressure metrics and projection publication are observations, not eligibility:
  missing values remain null/unknown; publication failure is reported without replacing
  the authoritative execution outcome. Actual SDK settlement still matters.
- Acceptance requires a fresh independent read-only review of the real full committed
  range, source and criterion evidence; resolve findings with verified focused repairs
  and current-range review. Implementation completion alone is not acceptance.

Each blocker must identify the problem, affected operation and concrete next action.
Any additional independent blocking rule needs an explicit requirement or demonstrated
serious risk, not a hypothetical completeness argument.

## Delete duplicate mechanisms; reuse real boundaries

These are repository-derived proposals, not claims that existing guarantees are already
optional. The cited seams explain what changes and what remains:

| Observed seam | Simplification and retained obligation |
| --- | --- |
| `cli.py` intake, `verify_action_origin`, `gates_satisfied`; `authority.py` action scopes | Admit approved tasks/config once; remove repeated whole-contract admission and redundant exact task/path/check encodings. Retain one scope owner and checks at actual permission/drift boundaries. |
| `engine.py:_assert_pins`, `store.py:reserve` | Remove whole-runtime hash identity as permanent run eligibility and per-node rehash/reload. Record runtime revision per attempt; at a settled boundary, a compatible bugfix may start a new attempt without rewriting old identity. Actual schema/config/authority incompatibility must be explicit; unresolved effects still block. This is not recovery permission for the current run. |
| `tools.py:snapshot/reconcile`, tool/Git call sites | Remove recursive whole-worktree fingerprint proofs around every tool. Use scoped mutation, safe path handling, one-writer custody and Git/task-boundary audits; preserve retained material, not a blanket ignored-file exemption. |
| `cli.py:_tools`, `pi_adapter.py:_poll_tools` | Replace no-op-process reads and whole-file replacement-only tools with usable existing read/search/edit/check facilities. Support ranged/chunked reads and useful output truncation/continuation at actual consumer limits. A 35,429-byte `tools.py` exceeds this reader's 32,768-byte cap; this proves incompatibility, not the latest failure cause. Do not impose a universal file-size rule. Catch safe tool-result errors locally rather than poisoning the prompt. |
| `host.mjs:observer/pressureReason`, session selection | Remove hardcoded Sol-only observation and optional-telemetry/headroom vetoes. Resolve binding/capabilities from selected configuration, record requested and observed separately, and use SDK lifecycle behavior without bespoke pressure proof. Unknown optional metrics do not erase known authority or create fresh-worker substitution. |
| `verification.py:ReviewRepair`, `review_documents.py`, interaction/parent delivery | Retire inline full-binary-diff bundles and process/SDK-byte/hash/turn/range document-delivery attestation. Let reviewers read actual revisions and files. Simplify owner-input delivery to genuine answers, original question/conversation association, deduplication and scoped authority; retain independent review, real gates and no uninspected retry. |

Use the existing check executor for authoritative results, but permit applicable normal
project commands instead of restricting every project to the narrow built-in unittest/
FileBytes/PythonAnswer registry. Reuse existing SQLite transactions, LangGraph transitions,
Git effects and process custody where they serve this contract; delete obsolete routes,
schemas and tests with their mechanisms rather than leave a second “lean mode.”

Dependency basis is the checked-in [runtime declarations](../../runtime/pyproject.toml)
and [runtime requirements](../../REQUIREMENTS.md#executable-implementation-runtime):
LangGraph 1.2.16, SQLite saver 3.1.2 and Pi SDK 0.87.1. No new dependency or upgrade is
proposed. Local call-site inspection suffices for pruning decisions; no external API
behavior or alternative SDK API is asserted proven. Actual host/tool integration must
be demonstrated under the acceptance gate below before downstream reliance.

## Minimal history, compatibility and policy boundary

Keep ordered task/attempt IDs, dependency/state changes, baseline/result SHAs, actual
check results and evidence references, approvals/decisions, runtime/config revisions,
review ranges/findings and unresolved process/tool/Git effects. Keep recorded run state
separate from observed liveness, and history separate from optional metrics/projections.
Do not store new transcript copies, secrets, narrative STATE or evidence-only ledgers.

Preserve old records and pinned inputs with read-only historical interpretation; do not
rewrite them into new semantics. The practical new reader interface is a documented,
versioned SQLite semantic surface for the history above, retained actual workflow
configuration/graph definition, and optional projection cursor—not preservation of
every obsolete internal proof table. Make additive changes where sufficient; otherwise
report unsupported versions explicitly, never silently reinterpret or migrate history.
The [monitor contract](../../specs/004-workflow-monitor/contracts/monitor-v1.md#sql-readnoninterference-contract)
currently consumes `wf_*` history, parent/proof tables, pins and actual YAML semantics.
Its unchanged-tools/runtime and exact-source constraints mean it is **not automatically
compatible**: affected reader/data-model/source/task approvals need explicit renewal
before that app consumes the lean runtime. Preserve its retrospective/live monitoring,
read-only/privacy and honest-unknown goals; app changes/recovery remain separate work.

Approval of later work must explicitly cover retirement of immutable runtime eligibility,
repeated full-tree and document-delivery proofs, telemetry-gated continuation and parent
provenance machinery in the [operating](../coordinate-implementation.md) and
[schema](../coordinate-implementation-schema.md) owners, workflow schemas/configuration
and affected [entry skill](../../skills/coordinate-implementation/SKILL.md) clauses.
Amend conflicting original runtime contracts explicitly, retaining historical approval
provenance. [REQUIREMENTS.md](../../REQUIREMENTS.md), the adoption contract and
[constitution](../../.specify/memory/constitution.md) must be checked/amended where their
exact original-conversation/continuation or compatibility mandates conflict; constitution
amendments require the owner's explicit decision and rationale. Do not silently waive
current policy. Retain current-content approval, one writer, configured exact bindings,
real REQUIRED/manual gates, the shared task-commit contract and independent final review.

## Acceptance and remaining gates

- **A1 — Lean behavior:** inspect the operative path and deletion diff: the five readiness
  facts and five execution rules above are understandable without hidden proof protocols.
  Obsolete duplicated blockers are removed, not renamed or bypassed. Diagnostics name
  the affected operation and correction; ordinary errors remain agent-correctable.
- **A2 — Real usable delivery:** under separate explicit live-test authority, the actual
  configuration-selected executor reads normal source, including usable continuation
  above the former read limit, makes an owned change, runs an applicable real check and
  receives a focused runner commit. Include a safe failed tool call corrected in the
  same attempt, with useful error reporting and no poisoned turn. Record actual binding,
  baseline/result SHA, check result and limits; a receipt or mocked metadata is insufficient.
- **A3 — Safety and durability:** focused existing tests of changed production seams prove
  owned-path/unrelated-work preservation, scoped authority, check-before-commit ordering,
  persisted attempt/result recovery and refusal to replay unresolved effects. Missing
  optional telemetry or failed projection publication must not turn valid work into failure.
  Use the smallest composed check where isolated helpers cannot observe the boundary.
- **A4 — Honest compatibility and acceptance:** schema/reader checks show retained old
  records are unmodified and interpreted historically or explicitly unsupported; new
  history explains the real A2 attempt. Operative docs/policy match approved behavior,
  and independent review covers the full actual refactor range and resolved findings.

The early high-leverage risk is whether the simplified host/tool boundary can perform
real work without either false uncertainty or lost custody. A2 is its smallest useful
composed milestone before broad reliance; it is not a separate prototype/report chain.
Known bounded safety/persistence behavior belongs in permanent actual-helper tests;
inspection handles names/types/deletion coverage. No giant fault-injection prerequisite
or live/provider call is authorized by source preparation. A failed/unrun REQUIRED
exercise cannot establish readiness, and changed assumptions renew affected approval.

For **delivery of this refactor**, the owner rejected using the runtime being simplified
and selected instruction-managed coordination: bounded workers, actual REQUIRED checks,
focused task commits and independent full-range final review. The actual owner answer
“Yes — gpt-5.6-terra / medium” selects **`openai-codex/gpt-5.6-terra`, effort `medium`**
for implementation tasks. Each Terra writer verifies and focused-commits its task under
the [shared checkpoint contract](../../skills/memory-handling/references/task-commit-contract.md);
the coordinator inspects actual diffs, SHAs and check evidence. Runner-owned commits above
remain proposed **product behavior**, not this refactor's delivery mechanism. No retired
skill is restored and no runtime-generated launch approval, custody proof or manifest is
a prerequisite. Before implementation in this worktree, reconcile real sole-writer/custody
safety; if necessary use a clean isolated workspace rather than repair the broken runtime
first. The uncertain monitor attempt stays untouched; no recovery programme is implied.

Tasks must carry this owner-selected binding explicitly, without fabricating a selected
workflow YAML or modifying existing app/base configuration. Future runtime/planning
consumers still derive executor intent from selected workflow configuration, not the
planner/session; this explicit owner selection governs this instruction-managed delivery.
The existing monitor build remains Sol/medium unchanged.

Parent review, separate tasks and combined current-content approval remain pending.
That approval must explicitly include this bounded execution-route exception to current
planner/adoption/constitution automatic-runner clauses and any affected policy amendments;
it is not an already-approved implementation or global process rewrite. Real tests, Git
checkpoints, ownership and independent review remain mandatory. Later live acceptance
needs separate explicit authority. No implementation, worktree creation, current-run
recovery or additional archive/reset is authorized by this planning correction.
