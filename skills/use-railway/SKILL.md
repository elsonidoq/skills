---
name: use-railway
description: Use when a request explicitly concerns Railway, includes a railway.com resource URL, or operates a repository already configured for Railway through the Railway CLI, Railway MCP, or Railway configuration files.
---

# Use Railway

Operate Railway without assuming that a particular CLI version, MCP server, account, project link, or preview feature is available.

## Detect Capabilities

Before choosing commands:

1. Identify explicit scope from a Railway URL or the user's named project, environment, and service. URL IDs take precedence over local links.
2. Detect the available path: Remote Railway MCP tools, `command -v railway`, repository Railway configuration, and the relevant command's `--help`.
3. Run `railway status --json` only when local linked context is relevant. Do not substitute it for IDs supplied by the user.
4. Prefer the CLI for local deploys, linking, SSH, and exact command output; prefer available MCP tools for platform-scoped reads and supported mutations; use `railway api` only after inspecting the current schema or official documentation.

If no required Railway capability is available, do not invent commands or API fields. Explain what is missing and use the current official Railway documentation at `https://docs.railway.com/`; if the installed CLI exposes `railway docs`, use it. Ask the user to install, authenticate, configure, or enable the required capability before continuing.

## Route To References

Load only the references needed for the request.

| Intent | Reference |
|---|---|
| Create projects, services, databases, buckets, or workspace resources | [setup.md](references/setup.md) |
| Deploy, redeploy, restart, or configure builds | [deploy.md](references/deploy.md) |
| Variables, environments, domains, and networking | [configure.md](references/configure.md) |
| Health, bounded logs, metrics, SSH, and failure recovery | [operate.md](references/operate.md) |
| GraphQL, documentation, or community lookup | [request.md](references/request.md) |
| Infrastructure as code | [iac.md](references/iac.md) |
| Railway feature flags | [feature-flags.md](references/feature-flags.md) |
| Recovery, HA, failover, or pooling | [databases.md](references/databases.md) |
| Database performance analysis | [analyze-db.md](references/analyze-db.md) |
| Usage, costs, or spending limits | [usage.md](references/usage.md) |
| Railway cloud-agent VMs | [cloud-agents.md](references/cloud-agents.md) |
| Railway sandboxes and checkpoints | [sandbox.md](references/sandbox.md) |
| Railway tracing and OpenTelemetry | [tracing.md](references/tracing.md) |

Feature flags, tracing, MCP, deployments, databases, and infrastructure on other platforms do not trigger this skill unless Railway is explicit or already established by repository context.

## Operational Safety

- Resolve project, environment, and service before mutation. Pass explicit IDs or names when local context may be ambiguous.
- Inspect current `--help`, schema, or official docs before using unfamiliar or version-sensitive flags and fields.
- Prefer structured, bounded output such as `--json`, `--lines`, and time windows. Do not start an unbounded log stream in an agent workflow.
- Confirm destructive actions and explain impact before deleting resources, dropping data, restoring backups, failing over, or changing shared database configuration.
- Never expose tokens, credentials, secret variables, or bucket keys. Do not place secrets in command output or source control.
- After every mutation, perform a scoped read-back.
- Never report a deployment as successful until that exact deployment reaches `SUCCESS`. Exit code zero, upload completion, or a detached command is not deployment success.
- Do not commit repository changes unless the user explicitly asks.

Database configuration and extension changes listed as user-only in the analysis references must be shown to the user, not executed by the agent.

## Authentication

Use the authentication flow supported by the detected CLI. `railway up` is appropriate when the user asked to deploy the current directory; `railway login` is appropriate when authentication itself is the task. Do not turn a signup request into an unsolicited deployment.

If a command starts device-code authentication, relay the URL and code immediately while the process is still polling. If the harness cannot surface live output, stop and ask the user to run the login command in their terminal rather than letting an unseen code expire. For unattended automation, require an appropriately scoped token; never solicit a token in chat.

An authorization error for a specific resource is not proof that login expired. Check resource IDs, workspace membership, and granted scope before repeating authentication.

## Common Reads

Use these only after confirming they exist in the installed CLI:

```bash
railway status --json
railway whoami --json
railway project list --json
railway service list --json
railway deployment list --json
railway logs --service <service> --lines 200 --json
railway variable list --service <service> --json
```

For deploy-from-current-directory requests, use the current CLI's documented `railway up` flow, capture the submitted deployment identity, and verify it with a scoped deployment read. For operations without a dedicated CLI or MCP capability, follow [request.md](references/request.md), including its compatibility fallback.

## Response

Report the action and scope, observed result, and any required next step. Distinguish verified platform state from a recommendation or an unavailable capability.
