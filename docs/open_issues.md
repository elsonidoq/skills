# Open Issues

## OI-1

- Status: open
- Problem: The global `/track-open-issue` command hard-codes `docs/open_issues.md`, so it assumes a repository layout despite the global portability policy.
- Primary evidence: `AGENTS.md` requires global commands not to assume a repository layout; `command/track-open-issue.md` records every issue in `docs/open_issues.md`.
- Resumption condition: Generalize issue-register discovery and its safe fallback, or move the fixed-path command to project-local configuration.
