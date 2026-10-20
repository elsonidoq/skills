---
name: finish-session-jev
description: Use when closing a session and optional Jev triage may help route multiple evidence-backed closeout findings.
---

Before any closeout action, resolve this skill's directory and read the installed sibling
`../finish-session/SKILL.md` in full. If the sibling cannot be read, stop and report that the base workflow is
unavailable; do not reconstruct it from memory. Follow that complete workflow exactly.

Insert the optional triage below after the base workflow derives candidate findings and before it writes any artifact. All base safety, lightweight-execution, ownership, deployment, memory, validation, and reporting rules remain binding.

## Jev Triage

An explicitly approved consequential decision that warrants durable rationale routes manually to `save-adr` under the base workflow; it is outside Jev triage. Jev cannot establish that approval or provenance.

Load the `jev` skill before using Jev and follow its authentication and data-safety rules. If the skill or CLI is unavailable or authentication is unavailable, route every candidate manually and continue the base workflow.

Use Jev only when each candidate's routing is a narrow, self-contained typed semantic judgment with explicit alternatives, and the candidate is already grounded in the attributable diff and primary artifacts. Do not use it merely because there are multiple candidates. Exclude and manually route any candidate involving security, deployment, credentials, personal data, sensitive payloads, or uncertain evidence. Submit every eligible candidate together; do not select a subset based on count. Make at most one bulk Jev call.

Give every eligible candidate a stable ID and a compact evidence-backed description containing no sensitive data. Send the descriptions as JSONL through stdin or non-repository scratch data; do not persist the batch in the repository. Use one typed `choice` decision per input line with JSON output, order preserved, and a minimum confidence of `0.80` (for example, `jev pick ... -l --field description --json --min-confidence 0.80`). Define these choices in the prompt:

- `documentation`: a verified current-state fact that needs an authoritative document update
- `open_issue`: unresolved work with a concrete problem and evidence
- `memory`: a trigger-first, non-obvious gotcha
- `skip`: duplicate, git-owned metadata, or ephemeral observation; uncertainty is not permission to discard a candidate

Treat a nonzero exit, malformed output, missing candidate result, unknown label, or confidence below `0.80` as an unavailable result requiring manual routing. Do not retry repeatedly or lower the threshold during closeout.

Jev is not an authority. It must not:

- decide whether a claim is true
- create, edit, or delete any artifact
- authorize deployment work or commands
- see credentials, tokens, personal data, or sensitive payloads
- replace duplicate checks, primary-artifact verification, or the final routing decision

Before writing, manually review every candidate against its primary artifact and the base workflow's routing table, including every `skip`, excluded candidate, and low-confidence or unavailable result. Jev may prioritize attention but cannot suppress a candidate or make the final routing decision.

Report whether Jev was used, the eligible and submitted counts, the confidence threshold, how many classifications were manually overridden, how many `skip` results were retained or rerouted after review, and all excluded, unavailable, malformed, or low-confidence cases.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Jev triage is read-only unless an authorized retained repository deliverable exists; external routing permissions remain separate.
