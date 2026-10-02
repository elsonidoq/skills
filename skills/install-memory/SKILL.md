---
name: install-memory
description: Use when adopting this skill suite on a project so the agent reliably finds memory, state, and documentation — writes the project's instructions with the suite contract and initializes the memory store.
---

# Install Memory

One-time project adoption for this skill suite. Establish the durable contract that
makes retrieval deterministic: document **how memory, state, docs, and planning work** in
the project's instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent), and create the
project memory store skeleton. Proposal-first: do not write, edit, or overwrite any
target until the owner approves the adoption plan.

## Preflight

1. Read repository instructions and the existing instructions file. In a pi
   environment, `AGENTS.md` and `CLAUDE.md` are loaded automatically as context files;
   the suite also reads them to discover the memory store, documentation owners, and
   conventions.
2. Run `git status --short`. Record the initial dirty state and content of every
   prospective target (the instructions file and the memory directory). Do not edit a
   target that is already dirty without explicit owner approval; re-read it immediately
   before each patch and stop on a concurrent change.
3. Confirm the suite requirements exist (see the global configuration repository's
   `REQUIREMENTS.md`): pinned `pi-subagents` and `pi-ask-user` packages, an installed
   SpecKit toolkit when the project will use the pipeline, and `jev` only when Jev
   triage is wanted in `finish-session-jev`. Report any missing requirement rather than
   proceeding silently.

## Step 1: Propose The Adoption Plan

Present for approval:

1. The requirements block to record (pinned package versions, SpecKit, jev).
2. The instructions-file section to add, covering:
   - **How the suite works:** request → `planner` understanding/brainstorming/scope →
     explicit owner TinySpec/Standard choice → reviewed tasks → approved handoff →
     `coordinate-implementation` → `finish-session`. TinySpec uses `tiny-spec` plus
     separate tasks and combined approval; Standard uses installed SpecKit and its
     specification/final approval gates. Neither automatically creates an Epic.
   - **How memory is used:** the store location (default: `<project-root>/memory/`
     with `memory/MEMORY.md` index and entry files; owner may choose another path),
     the `memory-handling` retrieval contract, and the trigger-first rules.
   - **How state is used:** the temporary current-execution state document when the
     project uses one (common convention: root `STATE.md`), pi sessions as the
     conversation record, and `docs/open_issues.md` as the canonical unresolved-work
     register (`track-open-issue`).
   - **How docs are used:** the documentation owners and the documentation-routing
     guide established by `initialize-documentation`.
3. The memory store skeleton: a `memory/MEMORY.md` index containing only the header,
   this contract's rules, and a placeholder stating no gotchas are recorded yet — never
   fabricated facts.
4. The overwrite policy for an existing instructions file: append the suite contract as
   a clearly marked section rather than rewriting custom content.

Before calling `ask_user` for adoption approval, present an executive brief in 4–6 short
bullets covering
outcome, included/excluded edits, decisions, risks/deferrals, validation results and
exact target/authorization. Verify question capability; missing capability stops approval.
Follow the discoverable planner approval contract (including renewals); report a missing
contract rather than inventing it. Stop until explicit approval; denial/cancellation grants
no writes. If the project already documents a compatible contract, report that adoption
is unnecessary and validate the existing association instead.

### Refresh an existing adoption

For an old suite contract, propose an owner-approved bounded refresh of only its marked
suite-owned section, preserving custom memory paths, docs, policy and every unrelated byte.
Do not globally rename references or overwrite local modifications. If the section is
unmarked, customized ambiguously, dirty or changed concurrently, show the exact proposed
bounds/diff and ask before proceeding; re-read immediately before applying. Update planning
entry points without converting old artifacts or approvals. A refresh does not authorize
substantive documentation work or reset the memory store.

## Step 2: Apply The Approved Plan

1. Add the approved section to the instructions file, preserving all existing content
   verbatim. Keep the section self-contained and marked so `memory-handling`,
   `finish-session`, and `compact-memory` can cite it.
2. Create `memory/MEMORY.md` (or the approved location) with the approved skeleton.
   Do not create a documentation directory or planning artifacts. On refresh, preserve
   the existing memory store and index rather than replacing them with a skeleton.
3. Apply the dirty-target protections from Preflight to every write.

## Step 3: Validate And Report

Re-read the instructions file and the memory index. Verify:

- The suite contract section exists and names the memory store path.
- The memory index resolves and contains no fabricated gotchas.
- No unrelated content was changed.

Report the instructions file path, the memory store path, the requirements recorded,
anything intentionally left to `initialize-documentation`, and instruct the user to use
the `finish-session` skill for closeout workflows.