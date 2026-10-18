# Fresh-context agent prompt — Validate orchestration stack, then plan the Coordinate Implementation migration

You are a **fresh-context coordinating agent working inside the actual Skills Git repository**. Your assignment has **two strictly sequential phases**:

1. **Pre-planning stack validation:** delegate a small, isolated, executable proof of concept (PoC) to a **fresh coding subagent** for candidate A. Review its recorded evidence. **Only if A definitively fails for a stack-specific reason**, delegate candidate B to a **different fresh coding subagent**; do the same for C only if B definitively fails. This phase happens **BEFORE invoking the `planner` skill or generating the migration plan**. It is technical uncertainty reduction, not planning the migration.
2. **Full migration planning:** **only after one candidate has empirically PASSED**, invoke the installed **`planner` skill** and use it to produce the end-to-end migration plan grounded in the validated stack. **Do not implement the actual migration.**

**Hard stop:** If A, B and C all definitively fail, or a shared prerequisite prevents meaningful validation, **do not invoke `planner`**. Stop, present the evidence and exact blockers to the user, and wait for the user to bring the findings back for a revised direction. Do not select an unvalidated stack, search for a fourth framework, or plan a migration against a hypothetical winner.

You are not being asked for a framework opinion, another theoretical survey, or an implementation of the new package. The critical output is a **reproducible, executed stack decision**, followed **conditionally** by an actionable, reviewed migration plan. Proceed autonomously on nonmaterial PoC details; preserve every required owner approval gate imposed by repository instructions and installed skills.

## Working repository and discovery

- You are already operating in the **Skills repository itself**. Locate its Git root and read its actual repository instructions and installed skills in place. **Do not search for or require an archive, attachment, or copied package.** Do not assume the checkout matches prior discussions.
- **Before delegating a PoC**, inspect just enough of the repository, environment, and Pi integration to establish genuine shared prerequisites and avoid touching real project work. Inspect the installed Pi version, permitted CLI/SDK/RPC capabilities, exact model bindings, subagent dispatch mechanism, Git state and isolated-test permissions. Do **not** invoke `planner` or generate the migration plan during this step.
- **After a PoC passes and immediately before using `planner`**, perform the complete repository inventory: read the installed `planner` skill, **every relevant `SKILL.md`**, supporting reference/test/helper files and approval/recovery/commit contracts, especially `coordinate-implementation`, `task-generation`, `memory-handling`, `requesting-code-review` and `scientific-method-debugging`. Use the repo as source of truth.
- Invoke/follow the **actual installed `planner`** only in Phase 2, rather than substituting improvised planning. Preserve the user's TinySpec/Standard selection, repository instructions and existing approval requirements. **Standard is a strong recommendation, not a user selection**: if `planner` requires owner choice or approval, request it using the prescribed mechanism. PoC authorization is not approval to migrate production code.
- This prompt is self-contained regarding the intended behavior and decisions; the **repository** is authoritative for integration contracts. If the checkout or required tools are unavailable, state the exact blocker rather than pretending to inspect or execute them.

## Why this migration is needed

Today, `coordinate-implementation` is a skill interpreted by a coordinating LLM. That agent manages batches, model routing by subjective task complexity, session/state bookkeeping, approvals, repair, and execution. The user has repeatedly observed fragile routing, unnecessary coordination overhead, and poor value from project-local coordinator memory and narrative STATE files. Implementation involves many more task iterations than planning, so **implementation coordination is the first migration target**.

The desired change is **not** another more detailed coordinator prompt. The existing **`Coordinate Implementation`** name must be retained, but as a **deterministic, executable workflow**, not a skill run by a long-lived coordinating agent. A conversational agent may start the workflow and read/explain its state; it has **no orchestration authority**. The same workflow must be usable from a CLI without that conversational agent.

Planning remains skill-based for this refactor. Adapt `planner`, `task-generation`, and other impacted skills to the new implementation handoff and **remove complexity-based model routing obligations wherever they conflict with the new design**. Do not undertake a wholesale planning-workflow rewrite just because the new runner could support it in the future.

## Non-negotiable target architecture

### Declarative workflow, explicit roles, code + agent nodes

- Define the workflow as **versioned YAML**, validated against a schema. The YAML declares its graph: node IDs, node types (`code` and `agent`, plus well-defined gates/terminals as needed), legal transitions/outcomes, agents' **skill bindings**, **provider/model IDs and effort**, retry limits, session policies, checkpoint/event locations, and permissions/allowed side effects.
- **The workflow graph, the model profile, and the skill for every agent node must be configurable.** Changing a node's model, skill, supported handler, order, or transition must not require changing orchestrator source. Code handlers themselves must be registered/implemented capabilities; YAML must not become an arbitrary-code-execution mechanism.
- The workflow runtime is a reusable engine/adaptor, not `if workflow_name == 'coordinate-implementation'` hard-coded throughout the control logic. Avoid inventing a generalized platform beyond the single required workflow.
- Sample initial profiles (illustrative aliases, **not verified provider IDs**): **Terra / medium** for implement and repair; **Sol / medium** for independent final review. Resolve concrete allowed bindings from the actual Pi installation. **No automatic model escalation or complexity-based routing.** A node's configured model/effort is verified at dispatch and recorded as requested versus observed.
- Allow `code` nodes for selecting the next ready task, preflight, checks, Git commits, checkpoints, approvals and deterministic error handling, and `agent` nodes for implementation, repair and substantive review. Output categories and transitions are schema-validated; never parse an LLM's free-form narrative to determine what happens next.
- Maintain **one writer per worktree**, preserving unrelated/uncommitted work, repository boundaries, permission gates, and owner approval authority.

### Dynamic/greedy session reuse (no batches precomputed by an LLM)

- Tasks are ordered according to real dependencies and approved source contracts. Planning or task generation may attach a simple **`context_group`** (initially the user story) identifying context affinity. Do **not** use another agent to optimize batch boundaries at runtime.
- After each completed, verified task, reuse the Pi implementer's session **only if** the next task is ready, has the required affinity, has a compatible model/profile/permissions, and has enough measured context headroom. Otherwise start a **fresh session**.
- Begin with configurable **`min_free_tokens_before_compaction: 150000`**. This means headroom to Pi's **effective automatic-compaction threshold**, not to a model's advertised maximum context window. The figure is an initial user preference, not a tested optimum. Missing/unreliable telemetry means **do not assume sufficient headroom**; start a fresh session or block with a precise capability issue, as justified.
- Context usage is not the same as cumulative token usage. Greedy admission **cannot guarantee that a single long task won't compact**. Define a safe interruption/recovery policy for mid-task context pressure without inventing such a guarantee.
- Individual tasks stay coherent, with their own acceptance and Git checkpoint. Reusing a session does **not** merge tasks into an unverifiable batch. There should be no routine extra LLM for bookkeeping.

### Durable status, event history, metrics and observability

- The **runner alone** owns persistence. Use an authoritative durable workflow checkpoint/store and expose **`state.json`** (current human/agent-readable status), **`events.jsonl`** (append-only event history), and **per-task/per-attempt metrics** (e.g. `metrics.jsonl`). Define exactly which store is authoritative and derive projections to prevent divergent truth. Document schemas and event ordering/versioning.
- Record per task and attempt: run/task IDs, node/profile/skill requested and observed, Pi session identity, context group, reused/fresh session, start/end timestamps, elapsed time, outcome, retry/repair count, checks/evidence, Git baseline/result SHA, **input, output, cache-read and cache-write tokens where available**, estimated current context at start/end, effective compaction headroom, and telemetry provenance. Record null/unknown honestly; never fabricate data. If Pi counters are session-cumulative, compute reliable deltas and account for session restarts.
- The conversational agent is merely an interface: `start`, `status`, perhaps `resume` after explicit authorized remediation, and human explanation of logged failures. **All decisions, transitions and side effects belong to the workflow.** No background LLM wakes up to decide what to do. Optional notifications on completion/blocking/final failure must not delay the workflow.
- Preserve recoverability after process interruptions and re-entry, without falsely promising that a workflow continues running after its host has exited. A permanently running daemon/service is **not a presumed requirement**; measure whether the chosen stack would force one.

### Verification, Git, failures, review and permissions

- A worker proposes/produces task changes. The runner verifies **real REQUIRED checks**, applies mechanical gates, commits focused task results, and records the checkpoint. Review semantics remain distinct from mechanical checks.
- Keep bounded repairs with the configured repair profile, independently review completed work, and route substantive change requests through authorized tasks. An initial `max_repair_attempts: 2` is a **configurable proposal** to be confirmed in planning, not a silently imposed invariant.
- **Never replay Git side effects blindly.** Workflow checkpoint persistence alone does not make filesystem or Git writes exactly once. Persist operation identity, reconcile HEAD/worktree/commit receipts, and make rerunnable handlers idempotent where possible; an uncertain in-flight operation must block or reconcile rather than launch duplicate agents or overwrite work.
- Preserve all explicit approval, REQUIRED evidence, security, capability, dirty-tree and worktree constraints from the existing package. Do not bypass a human gate by reclassifying it as a `success` event.
- Remove coordinator-specific narrative memory/episodic guideline/routing paperwork from the execution path and eliminate agent-maintained STATE bookkeeping. **Preserve relevant technical gotchas and authoritative project documentation**. Retain only minimal, automated operational state needed for correctness and observability.
- For planning, establish a machine-readable task contract or backwards-compatible structured subset with IDs, dependencies, context group, REQUIRED checks, approval status, and deliverable ownership. Preserve TinySpec/Standard and existing artifact approvals.

## Framework decision: fixed Plan A -> Plan B -> Plan C

**Do not choose among these with model intuition. Execute the PoC sequentially. Do not implement PoCs B and C if A passes.** Language is not a primary criterion; these Python choices are practical candidates, **not a claim that Python is inherently superior to TypeScript**.

**A — LangGraph (Python) + SQLite checkpointer + Pi RPC/CLI + declarative YAML adapter.**
- **Reason for first position:** agent-and-code graph, conditional loops, local checkpointing, Python functions for host operations, no required orchestration server, large active community. Do not instantiate LangChain agent abstractions if Pi already fills that role.
- **Known concerns to test:** replay/side effects across crashes, persistence semantics, long-running Pi RPC process/session handling, YAML-to-graph expressiveness without hard-coding, and exact-model/skill configuration.

**B — Temporal (Python SDK) + local Temporal development server + Pi RPC/CLI + YAML adapter.**
- **Run only if A fails a mandatory acceptance criterion due to a genuine stack limitation.**
- **Reason for second position:** established durable workflow system with retry/history/queries and explicit activities. **Cost:** additional local service/worker infrastructure; measure setup, persistence and operations. The local dev server is acceptable for an *experimental PoC*, but do not misrepresent its properties as production guarantees.
- **Known concerns:** sandbox/determinism rules for workflow code, versioning, server lifecycle, suitability as a distributable locally installed skills suite. Put Pi/Git side effects in activities.

**C — Prefect 3 (Python) + local orchestration mode + Pi RPC/CLI + YAML adapter.**
- **Run only if A and B both fail their mandatory acceptance criteria.**
- **Reason for third position:** mature, widely adopted Python workflow orchestration with task states, retries and observability; comparatively different API shape from graph-first runtimes.
- **Known concerns:** whether the tested local mode actually resumes a partially completed dynamic flow after process termination (not just retries a failed task), and operational requirements to query status independently. Demonstrate, do not assume.

**Why these candidates:** all have comparatively substantial and visibly active open-source communities. As of the **18 Oct 2026** investigation, indicative GitHub signals were approximately **43.4k stars for LangGraph**, **23.8k for Temporal server**, and **24.0k for Prefect**, with recent releases in Oct 2026 (Temporal Python SDK in Sep 2026). Stars are **popularity proxies, not verified installation/user counts**. Recheck license, latest stable releases, maintenance, community activity and compatibility with the actual runtime at PoC time. Prefer pinned stable versions; avoid pre-releases by default.

**DBOS Python, Dagu, XState, Restate and other packages were considered but are not in this fall-through sequence.** DBOS is actively maintained and lightweight, but its Python repository has a much smaller public community footprint (~1.6k GitHub stars) than the three selected; Dagu has ~4.4k and excellent YAML support but less direct evidence of this exact Pi-session/recovery use case. Their exclusion is not proof that they cannot work. Do not expand the search or silently substitute them unless all three selected candidates fail and the user authorizes a new decision.

### Shared dependency checks before the first PoC

Check first what is **framework-independent**: Pi installed and callable, Pi RPC or CLI protocol works, access to at least one authorized exact model, real (not mocked) telemetry interface, Git available, writable isolated test worktree, Python requirements and package installs permitted, and the ability to **delegate to fresh coding subagents**. If these are unavailable, report a **shared prerequisite blocker**; **do not falsely classify LangGraph as failed and burn through B/C**. If a normal version mismatch can be fixed safely in an isolated virtual environment, do so while recording the fix; never silently change production Pi or user credentials.

### Explicit delegation contract for Phase 1 — not a `planner` task

- **You are the coordinating agent for this ONE-TIME migration-planning request, not the future workflow's LLM coordinator.** Your work here is to dispatch an empirical test, inspect evidence, select a validated candidate, and (only then) invoke `planner`. You must **not** write or run the candidate PoC yourself under the guise of delegation.
- Delegate **A** as one bounded coding assignment to a **fresh-context coding subagent**, using the repository's available subagent mechanism. Provide that subagent the candidate stack, the **identical acceptance contract below**, safety constraints, a disposable test location and output/report requirements. Let the subagent write and **execute** the toy harness, inspect actual logs and return a clear PASS / FAIL / INCONCLUSIVE report with artifacts.
- Upon receiving the report, verify that test evidence supports its classification. If it reveals only a fixable mistake in the PoC, ask **that same subagent** to correct/re-run the bounded test before deciding; do not count ordinary coding bugs as framework failure. Record objective reasons rather than substituting your intuitions.
- If and **only if** A has an evidenced, stack-specific **FAIL**, delegate **B** to a **new fresh-context coding subagent** using the same acceptance contract. Include concise factual lessons from A (not its whole live context) to avoid repeated pitfalls. Repeat for **C**, with another **new coding subagent**, only if B fails for a confirmed stack-specific reason.
- **Never** launch multiple candidate PoCs in parallel, never pre-build B/C while A is being evaluated, and never spawn an agent to select models or frameworks by subjective complexity. Do not invoke or delegate the `planner` skill during Phase 1.
- If there is no permitted way to launch fresh subagents, report that exact capability blocker **instead of silently doing the PoC in the coordinator** or manufacturing results.

## Executable disposable PoC protocol (same contract for A/B/C)

Build the **smallest throwaway test harness** that establishes the stack, not a slice of the production migration. Work only in a temporary project/worktree and an isolated dependency environment; leave the original repository untouched. No destructive Git operation, no production secrets in logs, no live changes, no deployment. Prefer toy text files, trivial checks and short, inexpensive Pi invocations.

**Required demonstrations:**

1. **YAML-driven graph:** load and validate a tiny YAML with at least two `code` nodes and two `agent` roles or representative agent definitions, declared profile/skill and explicit transitions; prove that changing a supported model/skill or rewiring a transition in YAML changes execution without changing engine source. Capture validated configuration and runtime/versions.
2. **Real Pi integration:** launch a real authorized Pi implementer against an isolated toy Git repository; perform **two minimal tasks in the same context group**, e.g. create and then update a test text file. Verify session identity **really stays the same** when reused, exact requested/observed model+effort where observable, and that the assigned skill/instructions reach the node. Do not claim real integration from mocks only. Use a synthetic Pi stub separately when deliberately injecting crashes or token thresholds.
3. **Per-task telemetry:** query the actual Pi interface before and after tasks, persist context occupancy and token/caching counters with provenance and reliable deltas. A zero cache hit is a valid measurement; unsupported fields are explicitly `unknown`, not invented. Show example JSONL records and the human-readable status readout from a separate process.
4. **Greedy cutoff:** demonstrate, with an explicitly marked **synthetic threshold/test fixture**, that a next task uses a new session when effective free headroom would be below **150k**, otherwise reuses the session. Confirm the Pi API provides the real inputs needed for that calculation; do not waste hundreds of thousands of tokens attempting to reach compaction in a toy test.
5. **Git/verification:** run a toy REQUIRED check and create a focused commit on successful completion; record the commit SHA, task identity and baseline. Check that the workflow does not commit unrelated modifications.
6. **Crash/recovery:** inject a process failure (in the disposable harness) at least (a) after writing a file but before recording success, and (b) after a Git commit but before its checkpoint. Restart/reconcile. Show that no second agent runs into uncontrolled partial state and no duplicate commit or destructive cleanup occurs. Be explicit about which state was actually exercised through the real engine versus mocked components.
7. **Failure handling:** exercise one bounded verification failure / repair or a `blocked` transition, and show its status/evidence. Demonstrate the controller is runnable and its status queryable without a conversational coordinator.
8. **No hidden orchestration LLM:** the workflow transitions must follow machine-readable results and code logic. Pi is used only for work requiring an agent, never to decide the next node or model.

**Acceptance rule:** Candidate passes only if the relevant mandatory behaviors are **demonstrated in executed code** and the remaining glue is small, explicit and technically feasible. An impressive demo that skips real Pi telemetry, session reuse, or crash reconciliation is **inconclusive**, not PASS. Conversely, a bug in the PoC's first draft is not proof against the framework: fix bounded PoC mistakes before deciding it fails. A serious framework incompatibility, mandatory operational dependency that violates the stated design, unavailable required checkpoint functionality, or disproportionate custom orchestration code constitutes evidence for FAIL. Document both technical and operational cost.

**Sequential procedure and exit conditions (enforced by you as the parent agent):**

1. **Check shared prerequisites** without invoking `planner`. If blocked, record **BLOCKED/UNVERIFIED**, explain what is missing and **STOP**; a shared environment failure is not an A/B/C stack failure.
2. **Delegate A to a fresh coding subagent.** Require the agent to execute the toy PoC and return exact commands, versions, assertions, real-versus-synthetic distinctions, logs, results, and a minimal reproduction of any failure. Inspect the report. If **PASS**, record A as selected and move **directly to Phase 2**. **Do not run B or C.**
3. If and **only if A has an evidenced framework-specific FAIL**, record why and **delegate B to another fresh coding subagent**. Give it the same acceptance matrix. If **PASS**, select B and proceed directly to Phase 2. **Do not run C.**
4. If and **only if B also has an evidenced framework-specific FAIL**, record why and **delegate C to another fresh coding subagent**. If **PASS**, select C and proceed to Phase 2.
5. If **C also FAILS**, the result is **NO VALIDATED STACK**. Preserve all three failure reports, explain the concrete obstacles and **STOP without using `planner` or drafting the migration plan**. Report to the user so they can return with the findings and change the technical direction. **Do not explore a fourth stack or build a custom engine.**
6. If any candidate remains **INCONCLUSIVE** (e.g., permissions missing, telemetry unavailable across all frameworks), do not promote it to PASS or framework-specific FAIL or automatically proceed to B/C. Attempt only safe, bounded clarification or remediation, then **STOP** with evidence of the blocker if it cannot be resolved.

Keep PoCs **tiny and disposable**, but retain durable reports, logs, minimal reproduced code or instructions, exact environment metadata and acceptance matrix as project decision evidence. Remove temporary infrastructure safely, keeping enough to reproduce the test. **Never perform the real migration during this phase.**

## Phase 2 — ONLY after PASS: invoke `planner` and plan the migration end-to-end

**ENTRY GATE: an executed, evidence-backed PASS from one of the delegated PoC subagents.** No PASS means **no `planner` invocation and no migration plan**. A validated winner lets you record the stack decision, identify tested compatible dependency versions, inspect the full Skills repository, and **now** invoke the actual installed `planner` skill to produce authorized specification, architecture, ordered tasks, review and handoff for the migration.

The stack-selection PoC has **already happened**; do not make `planner` recreate it as an unexecuted future task or reopen A/B/C without contrary evidence. It may plan additional focused risk-reduction tests for unvalidated integration details, but must not treat the chosen framework as merely hypothetical.

This substantial migration merits recommending **Standard: Specify -> Plan -> Tasks**, while following `planner`'s required owner depth choice, review and approvals exactly. **Explicit authorization from this request covers isolated, disposable pre-planning PoCs, not implementation of the real migration.** If repository-wide governance rules impose any approval before even disposable experiments, obey that gate and report precisely; do not circumvent it. This does **not** change the required ordering: validate first, then invoke `planner` once authorized.

Ensure the eventual migration plan covers at least:

- Scope and file-by-file adaptation/removal of `coordinate-implementation`, associated batching/routing/memory contracts/tests, and affected references in `planner`, `task-generation`, review, debugging, approval, handoff and commit contracts.
- Versioned YAML schema, static graph validation, node/handler registry, model/skill/profile registry, result schema, configuration provenance/hash, safe evolution of active runs, safe defaults and fail-closed behavior for unknown handlers/capabilities.
- A real workflow runner using **the chosen tested engine**, Pi session adapter and reliable measurement of current context versus cumulative usage; greedy session reuse and cutoff; single worktree writer; config of skills and models by node.
- Git effects and idempotent recovery protocol with checkpoint boundaries and crash tests. Address external effects explicitly rather than claiming SQLite/Temporal/Prefect gives exactly-once Git operations automatically.
- Authoritative durable execution state plus documented, derived `state.json`, `events.jsonl`, `metrics.jsonl` and a minimal `status`/`start` CLI callable by a conversational agent. No coordinator narrative memory and no LLM-written state.
- Genuine REQUIRED checks, per-task evidence, commits, repairs, final independent reviewer, owner approval gates, reviewer corrections, blockers and status reporting. Preserve technical project memory and user/unrelated changes.
- Versioned migration/compatibility strategy for in-progress/legacy tasks and previously approved TinySpec/Standard artifacts; no invented approvals or unconditional mass conversion.
- Automated tests covering graph configurations, role bindings, session affinity and cutoff, telemetry accounting, multiple tasks, mid-task interruption, post-commit interruption, status queries and review/repair loops. Use the smallest sufficient realistic integration tests in addition to unit mocks.
- A migration sequence that begins with risk-reduction validation, introduces the new runner alongside legacy behavior only while necessary, replaces the old implementation entry point, updates skill references/tests, removes dead routing/coordinator-memory code, documents how to operate it, and includes rollback criteria.
- No automatic model benchmarking or routing feedback loop in V1. **Record** task-level metrics for later user analysis; do not add optimizers, heuristics or automated guideline promotion.

**Important current versus prior design:** Older analysis of this project suggested one fresh session per task and no dedicated events log. Those points were superseded in discussion: the user now wants **greedy session reuse with >=150k headroom**, **per-task telemetry**, **an event log and state projection**, and an **agent serving only as start/status interface**. Do not treat the older design as equally authoritative.

## Required outputs

**Always provide Phase 1 evidence**, under the repository's appropriate evidence location (without changing production Skills code):

1. **`stack-validation-report.md`** — dated A/B/C selection order; community/maintenance/license signals; shared prerequisite result; **which distinct coding subagent tested each candidate**; executed acceptance matrix; commands, environment, versions, real versus synthetic evidence; reproducible reason for each FAIL or INCONCLUSIVE outcome. Mark unrun fallbacks **`NOT RUN`**, never `PASSED`.
2. **`poc/`** or reproducible disposable harness plus logs, small enough to inspect and safe to re-run; no secrets and no non-disposable modifications. For all tested candidates, keep their individual findings so negative results are not lost.
3. **A concise Phase 1 result:** selected stack, with evidence, **or** shared BLOCKER, INCONCLUSIVE candidate, or **NO VALIDATED STACK after A/B/C**. For any non-PASS result, **STOP here**, explain why, and ask the user to return with the results to revise the direction. **Do not produce items 4–5.**

**Only if a candidate PASSES and Phase 2 legitimately runs**, also provide:

4. **`decisions.md`** (or the repository's standard decision record) with the single empirically validated stack, exact PoC evidence and accepted residual risks.
5. **Migration design and structured planning artifacts** authored/reviewed through the installed **`planner`** and its owner-approved path, with task dependencies, follow-on proof tasks, checks, integration, rollout/rollback, and a concise final summary. The deliverable is a **plan**, not a migrated implementation.

## Research starting points (reverify current applicability)

- LangGraph: https://github.com/langchain-ai/langgraph ; https://docs.langchain.com/oss/python/langgraph/persistence ; https://reference.langchain.com/python/langgraph.checkpoint.sqlite ; https://github.com/langchain-ai/langgraph/releases
- Temporal: https://github.com/temporalio/temporal ; https://github.com/temporalio/sdk-python ; https://docs.temporal.io/develop/python ; https://docs.temporal.io/production-deployment
- Prefect: https://github.com/PrefectHQ/prefect ; https://github.com/PrefectHQ/prefect/releases ; https://docs.prefect.io/v3/
- Pi RPC: https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent/docs (follow the actual installed package/version's RPC docs; repository URLs/ownership may move).
- DBOS as an explicitly nonfinalist reference: https://github.com/dbos-inc/dbos-transact-py ; https://docs.dbos.dev/python/tutorials/database-connection

**Execution order is mandatory: prerequisite checks → delegate and execute A → (only on evidenced framework-specific FAIL, delegate B) → (only on evidenced framework-specific FAIL, delegate C) → if PASS, invoke `planner` → plan the migration. If all three FAIL, or validation is blocked/inconclusive, STOP and report; do not invoke `planner`. Do not make a stack choice on documentation alone, do not test unused fallbacks, and do not implement the actual migration. The future runtime must not use an LLM coordinator; the one-time parent agent in this prompt only manages PoC delegation and the subsequent planner invocation.**

---

## Conversation addendum — 2026-10-18 UTC

Provenance: parent-supplied owner conversation, retained verbatim below. The original
request above is preserved in full; illustrative profiles and proposals there are not
independent provider verification or additional approvals.

User: 'There will probably be reviewing nodes in the graph ... if that review does not pass, then A fixing round should be run. ... we can reuse existing sessions, both for reviewing ... with the same rules of only reusing if there is a at least a hundred and fifty thousand tokens ... before reaching the autocompactation limit. ... for the repairing agent ... reuse the [agent] that already ... implemented the task. ... a session [rotor] ... across the whole workflow. So every node can be instantiated with a previous session or ... from scratch.'

Parent explained deterministic workflow-wide session selection, configurable per-node
policies, reviewer reuses its own independent session for review rounds, repair reuses
original implementer if eligible, never reviewer-to-implementer mixing,
unknown/insufficient headroom fresh, explicit fresh-only possible.

User then confirmed: 'Okay, it makes sense, but I think we should have sensible defaults. But yeah, it makes sense to be configurable. Okay, with this, I'm okay to proceed with the next step.'

### Planning-path selection and limits

Parent reports that the owner selected through `ask_user`:
**“Standard — Sol/medium (recommended)”**, in a planning-path question explicitly binding
planning producers and a separate independent review session to
`openai-codex/gpt-6.1-sol` with `medium` effort. This authorizes bounded planning
artifacts and their focused commits, not migration implementation. Specification approval
is still pending. This feature contains only the Standard specification-stage bundle;
architecture, tasks, overall review and implementation have not been released.
