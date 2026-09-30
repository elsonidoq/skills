---
name: finish-session
description: Use when closing a working session that may need documentation, unresolved-work, deployment, memory, or temporary current-execution state closeout.
---

# Finish Session

Preserve durable knowledge without turning closeout into a repository audit. A closeout is incomplete
when accepted information that matters to a future agent exists only in the conversation.

## Core invariants

1. Current-state documentation has one authoritative owner for each material fact.
2. Verified unresolved work has one canonical owner: `docs/open_issues.md`.
3. Memory contains only verified trigger-first gotchas.
4. A project's documented temporary execution state contains only temporary execution truth.
5. Every accepted, durable decision, constraint, rationale, user rule, or attributed assertion from
   the conversation has one persistent canonical owner. It is not left only in the transcript.
6. Documentation is discoverable: required directory indexes and the documentation-routing guide
   link future readers and writers to the same owner.

## Safety rules

- Start with `git status --short`, `git diff --name-status`, and
  `git diff --cached --name-status`. Inspect full diffs and relevant untracked paths only when they
  are attributable to this session. Preserve unrelated and pre-existing work.
- Before editing, record every target's initial dirty state and content. Do not edit an already-dirty
  target without explicit owner approval. Re-read it immediately before patching and stop on a
  concurrent change.
- Do not discard, stage, commit, or rewrite unrelated work. Do not modify product code, tests,
  generated application assets, or completed implementation artifacts.
- Verify claims about current code, configuration, schemas, generated output, or operational state
  against a primary artifact or configured external source. Do not record an unverified underlying
  claim as current-system truth.
- A direct, attributable user statement proves that the user made a decision, rule, constraint,
  rationale, or assertion; it does not prove an independently verifiable technical or external
  claim. Preserve the attributed statement with its provenance and verification status instead of
  promoting or discarding it.
- Never write credentials, tokens, personal data, or sensitive payloads. Do not execute deployment
  procedures or invent deployment commands.
- Git owns changelogs, completed-work summaries, file inventories, and plan/task completion
  metadata. Do not copy those into durable documentation or memory.

## Step 0: Documentation readiness and preservation gate

Read repository instructions and existing indexes only far enough to identify required documentation
owners, documentation directories, index conventions, the documentation-routing guide, and (when
applicable) the database-schema owner. This is an existence check, not a documentation audit.

If an owner, index, routing guide, or required schema owner is missing, report documentation
ownership as unavailable and name the missing element. Do not invent it and do not continue broad
documentation reconciliation. **Still run Steps 1–3 in preservation mode:** use existing owners and
obtain owner choices for accepted durable conversation candidates. Do not stop merely because an
owner is missing.

When missing infrastructure must be initialized, verify that `initialize-documentation` is available.
Use it after the required owner choices are made. If unavailable, report `documentation initialization:
UNAVAILABLE` and stop without creating the owner. Never report closeout complete while an accepted
durable candidate remains only in conversation.

## Step 1: Discover existing owners

Read applicable instructions and indexes. Preserve existing authoritative owners, runbooks, formats,
and identifiers. This suite uses `docs/open_issues.md` for unresolved issues through
`track-open-issue`; do not substitute another tracker.

Do not initialize fallback documents during discovery. Route ownerless candidates using Step 3's
owner-choice procedure. A missing issue register may be initialized only through `track-open-issue`
after the Step 0 readiness check passes.

## Step 2: Derive attributable candidates

Use attributable working-tree changes, commits, code, configuration, schemas, generated outputs, and
direct attributable user statements. Do not treat agent-authored summaries, inferred intent, or
session narrative as proof of current-system truth.

### Durable conversation-information pass

Run this pass even if Step 0 found missing infrastructure and even if no attributable file changed.
Inspect direct user statements for information that:

1. matters to a future agent's decision or action;
2. is not recoverable from code or authoritative documentation; and
3. remains useful beyond the current execution.

Consider decisions, constraints, rationale, user rules, and reported external context. Exclude
transient instructions, social conversation, secrets, personal data, file inventories,
completed-work summaries, and agent interpretations. Preserve concise meaning, not a transcript.

For every candidate, record in working memory: its concise statement; future trigger/use; direct
source; category; verification status of any underlying claim; proposed or existing owner; and
status (`pending confirmation`, `accepted`, `stored`, `superseded`, or `rejected`). An explicit,
clear user decision or constraint is accepted; ask the user when its authority, scope, or durability
is unclear.

Separately inspect only documentation plausibly affected by verified changed behavior or data. Update
facts only when primary evidence supports them. Treat unverifiable but actionable uncertainty as an
investigation candidate, not as current truth.

## Step 3: Route each candidate

Use one canonical owner. A secondary link is allowed only for a distinct warning or discovery aid.
Apply the documentation-routing guide first.

| Candidate | Canonical owner |
| --- | --- |
| Current contract, invariant, interface, behavior, procedure, or schema | Most specific established authoritative document |
| Attributed decision, constraint, rationale, or user rule | Established decision, policy, convention, or subject-specific owner |
| Verified trigger-first non-obvious trap | Project memory store |
| Unfixed bug, risk, missing capability, or unresolved investigation | `docs/open_issues.md` via `track-open-issue` |
| Verified deployment prerequisite | Established deployment/runbook owner |

### Owner-choice procedure

When no existing owner or reusable schema can hold an accepted durable candidate, propose one
sensible, reusable design and ask the user to choose it or provide an alternative. Never silently
select a new location or create a file before approval.

The proposal must specify:

- a project-relative, stable, subject-based filename and location;
- whether an existing document can be extended instead;
- purpose, scope, intended readers, and reusable entry/document shape;
- required fields: scope or trigger, decision/rule/fact, rationale, provenance and date,
  verification status, and supersession status when relevant;
- directory-index and parent-index entries needed for discovery;
- the routing-guide category and link that sends future readers **and writers** to the owner; and
- why the filename and shape accumulate related information over time.

Prefer extending the most specific compatible owner. Never propose a session-, task-, or date-named
file merely because closeout discovered the fact. This prevents documentation sprawl across sessions.

After explicit approval, initialize missing ownership through `initialize-documentation` when it owns
the infrastructure, then write the accepted content. Update required indexes and routing links in the
same closeout, subject to dirty-target protection. Re-read all links to confirm future discovery and
update routing work.

Record attributed external or technical assertions only as assertions, with their verification status;
never present them as established current truth without evidence. Track every durable conversation
candidate to a disposition. If an accepted candidate is blocked by a dirty target, unavailable
capability, or unresolved owner choice, report closeout incomplete and the exact next action.

For verified issue candidates, load and follow `track-open-issue` with primary evidence and a
resumption condition. Do not track documentation facts, memories, deployment prerequisites, or
non-actionable uncertainty as issues.

## Step 4: Deployment, only when relevant

Enter only when attributable changes have deployment implications or verified deployment evidence can
change an existing entry. Determine state as `deployed`, `not deployed`, or `unknown`; a direct user
report is attributed, not independently verified. Record only verified prerequisites with timing,
applicable environment, provenance, verification, rollback/irreversibility where known, and explicit
unknowns. Do not create hypothetical deployment work.

## Step 5: Memory and compaction

Enter when a verified finding satisfies the project's memory contract or project instructions require
an index check. Follow `memory-handling` for discovery, retrieval, writing, and re-checking. Do not
use memory for ordinary documentation facts or decisions. If a suitable memory owner is absent, use
the owner-choice procedure; do not leave an accepted qualifying candidate only in conversation.

## Step 6: Temporary execution state

Only when instructions name a temporary state document, replace its current-execution block with the
active work, exact next action, commands actually run and results, blockers, and durable-owner map.
Do not append history or place durable facts there.

## Metrics closeout

When the `jev_metrics` tool is available, invoke it exactly once with `action=closeout`. This metrics
closeout is independent of documentation readiness: run it even when documentation ownership,
indexes, or routing are unavailable. Treat only `appended` or `already_exported` as complete. Report
`store_error` explicitly and do not claim metrics closeout succeeded. Never maintain aggregate
counters in the model or write the metrics CSV directly.

## Step 7: Validate and report

Validate only changed links, index entries, routing links, issue references, and memory-index or
supersession pointers. Confirm every accepted durable conversation candidate has a discoverable,
persistent canonical owner.

Report separately whether work is implemented, verified, deployable, and fully closed out. Include:
existing and initialized owners; changed documents; conversation candidates with attribution,
disposition, and owners; owner/schema decisions; index and routing updates; issue/deployment/memory
results; metrics closeout result; deliberately skipped or unverifiable items; and every blocker
preventing complete closeout.
