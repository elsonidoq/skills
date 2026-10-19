---
name: handoff-prompt
description: Use when preparing a continuation prompt for a fresh session or delegated agent that cannot access the current conversation.
---

# Handoff Prompt

Produce one copyable Markdown prompt that lets a fresh agent continue without
guessing. Reference durable context by verified path; carry conversation-only
context directly.

## Establish Ground Truth

1. Identify the requested outcome and whether the next agent will plan,
   implement, research, or review.
2. Detect the workspace root and read the repository instructions advertised by
   the runtime or present in the workspace.
3. Inspect current changes and verify every path cited in the handoff.
4. Locate the relevant brief, spec, plan, tasks, contracts, decisions, and
   progress records from their own metadata and links. Do not infer provenance
   from numbering or a familiar directory layout.
5. Follow links only as far as needed for the next action. Label missing,
   proposed, and optional artifacts accurately.

For SpecKit work, first inspect the project's available commands and assets.
Record which stage command, template, prerequisite checker, or implementation
instruction was actually found. Do not assume conventional names or locations.
If SpecKit is absent, cite the existing artifact paths and describe the next
operation in generic terms; do not tell the next agent to invoke an unavailable
command.

## Prompt Contract

Lead with the exact outcome, then include only applicable sections:

```markdown
# Outcome
[One observable result]

## Workspace
- Root: [verified path]
- Revision or branch: [observed value, if available]
- Existing changes: [relevant summary]

## Read First
- [verified path]: [why it is authoritative]

## Provenance
- Request/source: [where scope originated]
- Artifact chain: [brief -> spec -> plan -> tasks, using actual links]
- Approvals: [decision, approver, and evidence]

## Constraints and Decisions
- [settled decisions, scope fences, rejected alternatives, deferrals]

## Current State
- Completed: [work plus verification]
- Incomplete: [work and blockers]
- Next dependency-ready action: [task or deliverable]

## Verification
- [check]: PASS | FAIL | NOT RUN | UNAVAILABLE - [evidence or reason]

## Operating Limits
- [write scope, authorization limits, owner gates]

## Return
- [changed artifacts, evidence, unresolved decisions, continuation context]
```

Use acceptance criteria and dependency evidence to choose the next action; the
first unchecked item is not necessarily ready. Distinguish verified facts from
agent reports and proposals from owner-approved decisions. Include non-obvious
runtime findings and conversation-only rationale that files do not preserve.

## Executable continuation

Carry the actual run ID, effective config/input/schema/environment/host/resource identities,
source/task/approval provenance, exact selected versus observed profiles, executor intent and
authorization envelope/action limits. Cite authoritative SQLite/status and baseline/result
commits/evidence, not a new narrative ledger. Pending questions carry original session/role/
branch pin, gate/input/nonce and accepted-versus-delivered state. Interactive mode carries
verified actual launching-parent/transport/question-tool generation; never replay historical
recipients or invent tool receipts. Low/unknown/unsafe original or live/unknown writers block;
no automatic fresh replacement or legacy restart. Next action is an authorized CLI status/
input/resume operation, never LLM work/model/session selection. Host exit means stopped, not
background progress. Preserve STATE/custom/history/unrelated work and original gates.

## Delegation Capability

Before recommending delegation, check that the runtime exposes an allowed
delegation mechanism (the `subagent` tool from the suite's pinned `pi-subagents`
package) and an appropriate configured agent. If available, name the
observed mechanism and agent class without inventing a model identifier. If
unavailable, make the prompt suitable for a fresh local session and state
`Delegation: UNAVAILABLE`; do not imply that a subagent was launched.

Close with the verified workspace, exact next action, and the checks already run.
Never claim that chat history, a session record, an agent task ID, or an uncommitted
file will be available in another checkout. If you record the current session, state
only observable facts: the current pi session ID (`PI_SESSION_ID`) and session file
(`PI_SESSION_FILE`) are available to commands run in this session and are not
portable to another checkout.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). A retained handoff prompt is a bounded deliverable; a fresh agent returns unknown inherited state rather than committing it.
