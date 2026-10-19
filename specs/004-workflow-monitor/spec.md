# Feature Specification: Read-only Workflow Monitor

**Feature Branch**: `follow-attached-workflow-migration-instructions` (preserved; feature directory is independent)

**Created**: 2026-10-19

**Status**: Standard preparation only — compatibility-scope correction awaiting renewed specification approval

**Input**: Owner request for a local website to understand several workflow runs and exactly what happened, with selectable runs on the left, one unified execution graph on the right and node details including very brief executive task summaries.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Understand a selected run (Priority: P1)

As the local operator, I select a run created under the new monitoring contract in this worktree and understand its defined workflow, actual progress, task relationships and outcome in one graph, including stages that do not belong to a task. Pre-feature/runtime-migration runs are outside this iteration.

**Why this priority**: A faithful overview answers what ran and what remains without confusing plans with history.

**Independent Test**: Load a known recorded run and compare the graph and details with its pinned definition, task contract and execution records; no live controller is needed.

**Acceptance Scenarios**:

1. **Given** several runs, including two for the same specification and a historical failure, **When** I select each left-hand entry, **Then** its stable run identity, source/configuration provenance and observed outcome distinguish it without mixing records from other runs or worktrees.
2. **Given** a pinned definition and recorded visits, **When** I explore the right-hand graph, **Then** every defined node and recorded visit is discoverable in that same graph, including run-level intake, authority, custody, selection, review and terminal stages; unvisited alternatives are gray and not presented as executions.
3. **Given** a selected task-associated node, **When** I open details, **Then** I see an understandable node description and a very brief executive task summary, not a wall of specification text. A run-level node has a description without a fabricated task association.
4. **Given** declared task prerequisites and recorded transitions, **When** both are displayed, **Then** their edge types are visually distinct and the prerequisite relationship does not claim execution order.

---

### User Story 2 - Explain failure and continuation without losing history (Priority: P1)

As the operator, I trace failed visits, repairs, questions, interruptions, recovery and final review to see what actually changed and what is still unresolved.

**Why this priority**: A later success must not erase the counterevidence needed to diagnose the run.

**Independent Test**: Inspect deterministic histories and isolated real runtime records containing failure/repair/success and interruption/recovery, checking identities, relationships and evidence against their source.

**Acceptance Scenarios**:

1. **Given** a failed visit followed by repair and success, **When** I inspect the node and its history, **Then** the failed visit retains a unique stable identity, red failure indication and available evidence; the recovered current state does not overwrite it.
2. **Given** worker completion, successful verification, a checkpoint and later final acceptance, **When** I inspect progress, **Then** these are separate recorded milestones, not interchangeable meanings of green or “done.”
3. **Given** a pending owner question and an accepted answer not yet delivered to the original conversation, **When** I inspect the run, **Then** pending, accepted, delivered and continued states are distinguished using recorded evidence; no answer or continuation control is available.
4. **Given** reconciliation without a new model invocation, original-conversation continuation, a retry or code repair, **When** I inspect their relationships, **Then** the viewer labels each according to actual runtime semantics and never equates every resume with a new attempt or invocation.
5. **Given** full-range review, correction and rereview records, **When** I inspect the graph, **Then** the original range, subsequent checkpoint references, finding dispositions and exact current acceptance are understandable without exposing private approval artifacts or conversations.

---

### User Story 3 - Observe safely while work proceeds (Priority: P1)

As the local operator, I keep the viewer open during execution and see near-live changes without disturbing the controller, losing my place or mistaking stale data for progress.

**Why this priority**: Observation is useful only if it is safe and honest about freshness.

**Independent Test**: Open the viewer against an active isolated shipped-runtime execution; observe new records and failed updates while checking that viewer actions cannot change workflow execution or control state.

**Acceptance Scenarios**:

1. **Given** an open viewer and new authoritative records, **When** updates succeed, **Then** changes normally appear within about two seconds while the selected run/node and graph navigation remain stable. This is the owner's approximate near-live target, not a newly imposed hard latency percentile or benchmark.
2. **Given** failed reads, lagging projections, incompatible data or a stopped controller, **When** the viewer updates, **Then** it clearly warns of the actual condition, identifies the last successful observation and does not assert continuing background progress or final acceptance without evidence.
3. **Given** malicious stored labels or content and sensitive runtime records, **When** I explore all viewer surfaces, **Then** content cannot execute in the browser and no private transcripts, reasoning, credentials, raw tool payloads, approval artifacts, raw database or sensitive paths/payloads are exposed.
4. **Given** the application's own approved build run recorded before the viewer exists, **When** the viewer becomes usable, **Then** I can inspect that build retrospectively and observe subsequent supported work live, retaining failures and recovery rather than substituting a clean demonstration.

### Edge Cases

- No store, no eligible monitored runs or an unsupported/no-contract store: show a specific empty/not-eligible condition without importing, adapting or exposing older runs. For a new supported run with unavailable/corrupt pinned definition, unknown identity, missing task metadata or incomplete records, show explicit unavailable/unknown conditions, not invented nodes or success.
- Same-spec runs, repeated visits, loops and historical failures: retain distinct identities; represent unvisited branches finitely rather than unfolding loops forever.
- Collapsed sections: preserve failure/waiting indicators, disclose hidden history and allow access to every hidden visit.
- Missing evidence is not confirmed failure; unknown timestamps and metrics are not zero. Recorded zero remains zero.
- A later metric revision supersedes rather than adds to its earlier reading; continuation/reopen must not create false counter continuity.
- Controller loss, accepted-but-undelivered input, active orphan alarms, unresolved review findings and blocked terminal paths must remain distinguishable from running, generic failure and acceptance.
- Concurrent controller writes, stale projections, interrupted reads and unsupported record versions must fail safely without repair, publication, replay or controller interference.
- A record not explainable by the available pinned definition remains visible as unsupported/unresolved recorded evidence; never force it into an invented route or silently drop it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001 — Local scope**: The website MUST serve only a local operator on loopback and load eligible runs from the worktree being viewed, including this checkout for dogfooding. Only runs created under the new monitoring contract are eligible. Older pre-feature/runtime-migration runs are irrelevant and MUST NOT receive adapters, migration/import, archival extensions or incomplete-history fallback. No cross-project registry, broad scan, public/shared-network service or remote multiuser access is included.
- **FR-002 — Run selection**: A selectable run list MUST appear on the left and one unified execution graph on the right. Several runs in the worktree, including same-spec runs and historical failures, MUST be distinguishable by stable run identity and available safe source/status/time provenance; unavailable metadata MUST be identified as unknown.
- **FR-003 — Unified truth**: The graph MUST combine actual pinned workflow definitions/allowed transitions, specification task identities/dependencies and recorded execution visits/outcomes/history. The new monitoring contract MUST pin and retain a verifiable actual workflow definition before fully mapped graph reliance, proving agreement with actual runtime configuration rather than merely declaring an unrelated configuration source. It MUST NOT introduce competing primary task and workflow graphs. Tasks supply labels/grouping where justified, not universal containers; nodes may be run-level or span tasks.
- **FR-004 — Complete inventory**: The inventory MUST derive from each run's actual pinned definition and records, not an illustrative fixed route. Every defined node and recorded visit MUST be accessible, covering intake/validation/authority/capability/custody, selection/dispatch, implementation/verification/repair/checkpoints, question/wait/continuation/interruption/recovery, independent full-range review/correction and final acceptance/failure/blocked/terminal paths where defined or recorded. Semantic records that are not node definitions MUST remain distinguishable from workflow nodes.
- **FR-005 — Definitions versus visits**: Workflow node definitions MUST be distinguishable from visit instances. Repeated visits MUST have stable unique identities and preserve earlier failures after later success. Planned/unvisited branches MUST be gray with a finite representation of loops. No event, causal explanation, transition or execution order may be invented from task prerequisites alone.
- **FR-006 — Edges and navigation**: Actual execution transitions and declared prerequisite edges MUST be visually distinct if both shown. Zoom/navigation and optional collapsing MUST remain inside the one graph; collapsing MUST retain failure/waiting indicators and disclose, not silently omit, hidden history.
- **FR-007 — Status fidelity**: The viewer MUST distinguish worker-finished, mechanically verified, committed and finally accepted; failed historical visit versus recovered current state; insufficient evidence versus confirmed failure; stopped controller versus active progress; pending owner question versus generic failure; and accepted owner input versus actual original-conversation delivery and continuation. Chat prose MUST NOT establish authoritative status.
- **FR-008 — Status presentation**: Gray MUST mean not started, green successfully completed and red failed. Running MUST be blue; waiting and blocked MUST be amber with distinct labels. Unknown/stale data MUST have explicit warning labels/icons, never a confirmed-failure implication. Every status MUST use text/icons in addition to color. Historical failed visits MUST remain red after recovery; labels MUST identify which completion milestone succeeded rather than imply final acceptance.
- **FR-009 — Understandable details**: Every node MUST have an understandable description; task-associated nodes MUST also show a VERY BRIEF executive task summary rather than full source text. Where supported and safe, details MUST show sanitized node/visit/task identity and role, status/timestamps, verification results/evidence references, failure/interruption explanation, recovery/resumption relations, commit references and useful safe session identifiers. Missing explanations/evidence MUST remain unknown, not be generated as fact. No summary-generation policy or mandatory model summarization is selected.
- **FR-010 — Continuation semantics**: Original conversation continuation, recovery/reconciliation, attempts/retries and code repair MUST be separately represented when justified by the runtime. A resume MUST NOT automatically create a new invocation or attempt. Definitions and evidence MUST determine the relationships, including task-spanning and run-level stages.
- **FR-011 — Freshness**: While open, the viewer MUST provide near-live updates within about two seconds under normal local observation, preserve selection/navigation and clearly warn on failed/stale updates. It MUST show observed freshness, available actual timestamps, unknown timestamp reasons and data provenance, including projection lag where applicable. It MUST NOT silently strengthen the approximate target into an invented hard benchmark.
- **FR-012 — Metrics integrity**: Available metrics MUST preserve null/unknown values and provenance, preserve observed zero and avoid double-counting superseding revisions. Requested, runtime-observed, request-observed and provider-acknowledged bindings MUST not be conflated; non-agent stages MUST not gain fabricated sessions or token metrics.
- **FR-013 — Observer only**: Viewer opening, refresh, selection, navigation and detail access MUST NOT answer, pause, cancel, steer, resume, restart, schedule, launch workers/models or cause any execution/control effects. There MUST be no viewer controls for these actions, browser direct SQL writes, implicit repair, projection publication, saver deserialization or workflow restart. The application MUST NOT become a second scheduler or change authoritative runtime/controller/worker behavior or original REQUIRED gates.
- **FR-014 — Safe monitoring boundary**: Integration MUST use an explicit read-only VERSIONED monitoring seam grounded in real runtime semantics; no existing HTTP API is assumed. SQLite remains sole runtime authority; projections are derived and may lag. Active-database observation MUST not disturb the controller or depend on opening a writable saver. Missing/incompatible records MUST yield a safe explicit unavailable/unsupported condition rather than mutation, downgrade or fabricated state. Architecture MUST address appropriate web-origin/input defenses despite loopback scope; the scheme is not selected here.
- **FR-015 — Data minimization**: All stored labels, task summaries and other content MUST be treated as untrusted and rendered safely. All viewer-accessible outputs, including errors and detail links, MUST exclude private Pi transcripts/reasoning, credentials, raw tool payloads, approval artifacts, raw databases and sensitive paths/payloads. Safe identifiers and evidence references MUST not grant access to those materials. Sanitization MUST apply before exposure, not merely hide sensitive data visually.
- **FR-016 — Real validation**: Acceptance MUST include deterministic fixtures for definition/branch/repeated-visit/status/history completeness AND actual isolated shipped-runtime execution records for integration, not only invented UI fixtures. Mandatory isolated implementation tests and test-only approval scenarios were owner-preapproved, but MUST NOT fabricate human/tool receipts or production gates, or imply separately charged service authority.
- **FR-017 — Dogfooding without circularity**: Newly approved application tasks MUST be executed and recorded using the accepted source-local runtime without requiring the unfinished viewer. The usable viewer MUST then load its own build retrospectively and inspect subsequent supported work live. Failures and recovery counterevidence MUST be retained. Missing launch prerequisites MUST be reported exactly; no manual swarm fallback or reuse of historical runtime-migration approvals, run IDs, nonces or receipts is allowed.

### Key Entities *(include if feature involves data)*

- **Worktree**: The canonical viewed execution workspace and its local run store; not a project-wide or cross-project registry.
- **Run**: Stable run identity, pinned source/configuration provenance, observed controller/current state, historical outcome and freshness; several runs may reference the same specification.
- **Workflow definition**: Pinned node definitions, roles, allowed outcomes and transitions. Its inventory does not assert that every branch executed.
- **Task**: Specification task identity, declared prerequisites and brief executive summary; optional associations with nodes/visits do not determine actual execution order.
- **Visit / execution record**: Stable repeated-node visit identity and actual outcome/order/evidence; linked but distinct from task, model invocation, retry, repair, continuation and recovery records.
- **Evidence / observation**: Safe reference to verification, checkpoint, review, failure, question/input-delivery, metrics or freshness facts, with provenance and explicit unknowns. A revision may supersede another observation without erasing history.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 — Coverage and identity**: For the tested pinned definitions and recorded histories, every defined node and every recorded visit is accessible in the single graph with correct identity, justified edges and grouping, including non-task stages, unvisited alternatives, repeats and terminal outcomes; zero fabricated execution visits/edges or silently omitted visits. Validate against a source-derived inventory, not a manually selected happy path (FR-002–006).
- **SC-002 — History and acceptance**: In failure→repair→success, interruption→recovery, question→accepted→delivered→continued and review→correction→rereview examples, operators can identify each distinct recorded milestone and earlier failure; no worker completion, reconciliation or old review is presented as current final acceptance. Include stopped-controller, missing-evidence, blocked and terminal examples (FR-007–010).
- **SC-003 — Near-live honesty**: During representative active local execution, record source observation and displayed-update times to demonstrate the about-two-second near-live behavior; retain measured deviations for review without inventing a hard percentile. Selection/navigation survive updates, and forced failed/stale reads and controller loss visibly warn instead of claiming progress (FR-011).
- **SC-004 — Evidence fidelity**: All tested unknown/missing timestamps, null metrics, observed zeros, superseding revisions, non-agent observations and accepted-but-undelivered input retain their correct meaning and provenance, with no invented values or duplicated revision totals (FR-007, FR-009, FR-012).
- **SC-005 — Safe observation**: Across viewer actions against active and historical records, there are zero viewer-triggered execution/control effects or authoritative data mutations. Adversarial stored content cannot execute; sensitive-data sentinel records do not appear in any viewer-accessible output. Missing/incompatible data fails safely, with controller activity unaffected (FR-001, FR-013–015).
- **SC-006 — Actual integration and self-history**: Retain evidence from actual isolated shipped-runtime executions in addition to deterministic coverage fixtures; the viewer successfully displays its own recorded build under the new monitoring contract, including retained failures/recovery, and subsequent supported live work. Verify that the retained definition agrees with actual runtime configuration. Multiple new eligible runs, including same-spec and completed/failed/recovered runs, retain their full histories. Older pre-feature/runtime-migration runs require no inclusion or conversion and are not substitute evidence. This is application acceptance evidence, not proof that a static fixture or historical PoC certifies runtime behavior (FR-001, FR-003, FR-016–017).

All criteria above are REQUIRED for later decomposition, not implementation results claimed by this draft. Choose the smallest sufficient validation layer for each concrete failure: deterministic inventory/history checks for representation, real composed runtime checks for safe active observation and integration, and targeted browser/output checks for navigation, rendering and exclusion. Keep ordinary tests/evidence with coherent delivery; no mandatory separate prototype chain, exhaustive unrelated matrix or duplicate proof reports. A missing/unrun required proof blocks reliance; preserve applicable evidence, counterevidence and original gates.

## Assumptions

### Settled source decisions and provenance

- Requirements originate in the self-contained owner monitoring request supplied to this fresh producer by parent session `01a155ad-f798-745f-b6ce-032eca08f263`; no previous monitoring-feature approval was supplied or discovered in the inspected documentation routing index. `specs/003-coordinate-workflow/tasks.json` is historical runtime-migration work, NOT this feature's task contract or authority.
- Genuine parent `ask_user` decisions selected Standard preparation, read-only iteration one (“Read only, yes”), local loopback operator access, runs from the viewed worktree (“It should load from the worktree”), approximate two-second updates and the conceptual left-list/right-unified-graph/details UI. These are settled constraints, not implementation approval.
- During this production, the parent relayed a genuine `ask_user` answer “Confirm these treatments”: blue running, amber waiting/blocked with distinct labels and explicit warning labels/icons for unknown/stale. This supplements gray unstarted, green successfully completed and red failed; no tool receipt IDs are invented.
- Exact responsive behavior, frontend/backend frameworks, HTTP/API/transport/hosting architecture and summary-generation policy are design choices, not inferred requirements. During architecture preparation, the owner delegated graph and backend technical selection against community-use and adequate-documentation criteria; final reviewed plan approval remains pending. No deployment or separately chargeable action is authorized.
- During architecture preparation, genuine parent `ask_user` returned “older runs are irrelevant. Do nothing to include them”. This narrows compatibility to new monitored-contract runs, including the application's own build; completed, failed and recovered runs created under that contract remain fully in scope. No older-run adapters, migration/import, archival extension or incomplete-history fallback is authorized. New supported inputs still require safe missing/corrupt/incompatible-data behavior.

### Imposed runtime constraints and inspected evidence

- The existing runtime's [operating guide](../../docs/coordinate-implementation.md) and [schema owner](../../docs/coordinate-implementation-schema.md), read completely for this draft, own current semantics; [pinned YAML](../../runtime/coherence_workflow/workflows/coordinate.yaml) and [packaged schemas](../../runtime/coherence_workflow/schemas/) supply definition/contract evidence. Later integration design or launch preparation MUST reread these complete authorities, `cli.py`, `projections.py` and [open issues](../../docs/open_issues.md), then inspect relevant actual interfaces/tests proportionally. Do not replace source verification with this summary.
- The current shipped YAML defines 19 nodes, including run-level gates/selection and question/continuation/repair/review cycles; this is baseline evidence, not a fixed future inventory. `cli.py:774–821` registers their actual stage meanings. Definitions, logical graph visits, SDK turns and task records have different identities; `cli.py:459–488` and `679–736` distinguish original continuation from recovery/reconciliation. This motivates FR-003–005 and FR-010 and their source-derived acceptance inventory.
- `cli.py:854–900` implements read-only SQLite status snapshots (`mode=ro`), schema checks and SQL-derived status/operations/metrics; `pending` delegates to status without launching/resuming. These are CLI interfaces, not an existing monitoring HTTP API or a ready browser-safe response. A new versioned safe seam remains design work (FR-014–015).
- `projections.py:23–86` derives state from controller, alarm, acceptance, question and gate facts. `projections.py:131–173` publishes event payload hashes except defined special cases and selects unsuperseded metrics. Projections alone do NOT establish a complete explanatory graph contract. `Publisher` can mutate projections and MUST NOT be invoked by observation. Existing `runtime/tests/test_projections.py` checks separate-process status nonmutation, revision handling and non-agent nulls; inspection is reused, tests were NOT run for this specification.
- Dependency evidence is reused from the canonical operating/schema owners and `runtime/pyproject.toml`: LangGraph 1.2.16, checkpoint-sqlite 3.1.2, PyYAML 6.0.3, jsonschema 4.26.0; official SDK host pin 0.87.1. No new dependency or version is selected. Research into new web/graph libraries and active-database/read-seam choices belongs before consequential architecture decisions; no new internet research, install or PoC was needed to state these requirements.
- OI-3 retains high-severity brace-expansion advisories in the pinned SDK tree. Existing bounded-host review found no supported affected-input route, NOT blanket SDK safety. Exposing SDK resource/default/package/glob/model-scope paths requires renewed reachability assessment; no silent SDK upgrade is allowed. Historical scratch SQL reservations/PoCs are not runnable approval or certification.
- `memory/MEMORY.md` is the verified local gotcha index and has no entries; `memory/coordination/GUIDELINES.md` has no approved guidance. No applicable guidance or memory writes were invented.

### Intended executor and remaining gates

- Implementation intent is separately owner-selected **Sol / medium**, exact compatible target **`openai-codex/gpt-6.1-sol:medium`** (owner clarified “use 6.1 sol medium”). Preserve `model_class: Sol`, `effort: medium`, owner provenance, assumptions, compatibility assessment and decomposition rationale into architecture/task production and the later root execution-intent contract. This is not permission to dispatch.
- Assumptions/rationale: outcome-oriented delivery may leave routine choices open for this intended executor, but explicitly scaffold pinned node/visit/task distinctions, authoritative status/evidence mapping, sanitization, active-read safety, original REQUIRED acceptance and dependency/gate boundaries. No universal model-family superiority or effort benefit is claimed. The current host documents only this observed compatible binding; fresh execution preflight must verify it and its local skill/SDK resources rather than infer availability from this specification or the planning profile.
- Planning/review independently selected the same exact Sol/medium target; it does not establish implementation compatibility or authority by itself. Unknown/provider-unacknowledged observations must remain unknown.
- The highest downstream risk is safely exposing enough real pinned-runtime semantics for complete graph history without leaking private data or interfering with an active controller. Schedule a small real composed read/seam validation before dependent UI reliance; permanent focused helper tests may supply the proof, not necessarily a disposable prototype. Existing PoC findings may inform bounds but cannot replace production acceptance.
- The original specification bytes were approved as recorded in `specification-approval.md`; the explicit newer-run-only correction above changes those bytes and requires renewed current-content specification approval before architecture production proceeds. Parent must inspect the correction and present a new concise executive brief before actual `ask_user` renewal. Task contracts and implementation approval remain absent.
- Later runtime admission requires newly approved app tasks/configuration, truthful external owner catalog, verified manifest/local skill bindings, containment capability and fresh run identity. Owner-preapproved isolated tests/test-only approval scenarios do not fabricate production receipts or waive missing prerequisites. No model escalation, quotas, batching heuristics, new Epic or narrative STATE is requested.
