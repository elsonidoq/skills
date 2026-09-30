<!--
Sync Impact Report
Version change: scaffold → 1.0.0
Modified principles: scaffold placeholders → five initial project principles
Added sections: Operating Constraints; Delivery and Review Workflow
Removed sections: none
Follow-up TODOs: none
-->
# Pi Configuration Constitution

## Core Principles

### I. Portable Global Assets
Global skills, commands, and configuration MUST remain portable across unrelated projects. They
MUST NOT assume a project name, repository layout, branch, deployment state, configured model, or
agent. Project-specific policy belongs in the adopting project's instructions or local skills.

### II. Evidence and Capability Gates
A workflow MUST verify that each required command, asset, runtime tool, external service, and
prerequisite is available in the current project before relying on it. Missing capabilities MUST be
reported with a usable manual fallback or owner decision; agents MUST NOT simulate unavailable
stages, install tooling, or perform irreversible actions without authorization.

### III. Artifact-Led, Owner-Approved Delivery
Features MUST originate in an evidence-backed brief or owner-approved direct task list. Pipeline
work MUST preserve a traceable chain from brief through specification, clarification, plan, tasks,
analysis, and recorded approvals. Material changes to scope, architecture, privacy, permissions,
cost, or settled requirements require an explicit owner decision before progressing.

### IV. Durable Knowledge and Documentation Integrity
Documentation MUST describe the system as it exists. Project memory MUST contain only verified,
non-obvious, durable trigger-first guidance. Verified unresolved work MUST be recorded in the
canonical `docs/open_issues.md` register. Documentation ownership and routing MUST be established
before relying on new documentation governance.

### V. Verification Before Claims
Agents MUST base completion, readiness, and quality claims on inspected artifacts and applicable
checks. Plans and task lists MUST preserve dependency order, test or verify stated acceptance
criteria, and retain required final verification. Optional automation and model suggestions inform
engineering judgment but MUST NOT replace evidence, authorization, or final review.

## Operating Constraints

The suite requires the pinned Pi runtime and registered extensions documented in `REQUIREMENTS.md`.
SpecKit is a project-local dependency and is used only after its commands, templates, and
prerequisite checks are verified in that project. Jev is optional; unavailable or unauthenticated
Jev MUST leave the original manual workflow available. Agents MUST avoid transmitting secrets,
personal data, credentials, or raw sensitive payloads to optional tooling unless explicitly
authorized by the applicable project policy.

## Delivery and Review Workflow

The default delivery path is brief → `create-epic` → project-installed SpecKit pipeline via
`epics-manager` → `coordinate-implementation` → `finish-session`. The full SpecKit pipeline is
used only when its documented admission conditions are met and its project capabilities are
available. Specification and overall-review approvals MUST apply to the current artifacts before
implementation handoff. Independent evidence-based review is required when practical. A session
that changes global configuration, commands, or skills MUST instruct the user to run `/reload` in
Pi.

## Governance

This constitution governs the global Pi configuration repository and supersedes conflicting local
workflow guidance unless an owner explicitly amends it. Amendments require an owner decision,
written rationale, semantic-version update, and review of affected specifications, plans, tasks,
and documentation. Every planning, implementation, review, and closeout session MUST check
applicable principles and record evidence for any required exception.

**Version**: 1.0.0 | **Ratified**: 2026-09-29 | **Last Amended**: 2026-09-29
