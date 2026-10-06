---
name: supabase-server
description: Use when planning, reviewing, or modifying server-side code that imports `@supabase/server`, calls its auth or client primitives, or migrates an authenticated Supabase handler to that package.
---

# Supabase Server

Use the installed `@supabase/server` package as the authority for API shape and auth behavior. Do not transfer assumptions from unrelated Supabase clients or neighboring handlers.

## Detect The Package Contract

Before planning or editing:

1. Find the importing workspace and resolve its installed or locked `@supabase/server` version.
2. Inspect that version's exports, types, package docs, and source. Relevant locations commonly include `node_modules/@supabase/server/docs/`, package export maps, and `src/adapters/README.md`.
3. Confirm the runtime and adapter: Supabase Edge Functions/Deno, Node, Bun, Cloudflare, Hono, or a custom integration.
4. Confirm how credentials reach the request and which identity the handler must establish.

If the package or its matching docs/source are unavailable, do not guess imports, auth values, context fields, environment variables, or error shapes. Ask to install the locked dependency or consult the official repository source and documentation for the exact version. If version-matched material cannot be found, state the limitation and avoid emitting package-specific code.

## Choose Auth From Intent

Verify the names below against the installed version before use.

| Intent | Typical mode |
|---|---|
| End user identified by bearer JWT and RLS | `user` |
| Caller proves possession of a publishable key | `publishable` or a named variant |
| Trusted service proves possession of a secret key | `secret` or a named variant |
| No Supabase credential check | `none` |

Auth selection protects the inbound endpoint; admin-client availability governs elevated downstream access. These are separate decisions. Never infer endpoint auth merely because business logic needs an admin client.

Before using `none`, confirm that the endpoint is intentionally public or implements another complete verification mechanism, such as a webhook signature. Never use unauthenticated access for user data or sensitive side effects. For multiple accepted modes, verify ordering and invalid-credential behavior in the installed package docs instead of assuming fallback semantics.

Prefer publishable and secret keys supported by the installed package. Do not introduce legacy anon or service-role keys into new code. During migration, determine whether a legacy key authenticated the caller, created an elevated client, or both before choosing a replacement.

## Implement

Use the highest-level adapter that fits the runtime:

- Handler wrapper for standard fetch-style endpoints.
- Framework adapter for Hono or another adapter exported by the installed version.
- Core primitives only when cookie handling, custom responses, or another framework requires explicit composition.

For Deno or Edge Functions, follow the repository's import map and the package's documented specifier. For cookie-based frameworks, preserve the framework's session refresh and cookie lifecycle; `@supabase/server` credential verification does not replace it.

Minimal shape, only after confirming the installed API:

```ts
import { withSupabase } from '@supabase/server'

export default {
  fetch: withSupabase({ auth: 'user' }, async (_request, context) => {
    const { data, error } = await context.supabase.from('todos').select()
    if (error) return Response.json({ error: error.message }, { status: 500 })
    return Response.json(data)
  }),
}
```

Do not copy this specifier into Deno code without checking the installed package guidance.

## Edge Function Gate

Supabase platform JWT verification can reject a request before the handler runs. Compare the selected package auth mode with the function's current `verify_jwt` configuration. Change the platform gate only when required by the intended inbound credential flow, and explain the security effect. Never disable it merely to make a request pass.

For webhooks using `none`, verify the provider signature over the exact raw body before parsing or causing side effects. Keep webhook secrets in platform secret storage.

## Migration

When replacing manual `Deno.serve`, CDN imports, direct `createClient`, or legacy key handling:

1. Record the existing caller identity, credential transport, CORS behavior, admin access, and error responses.
2. Select the package auth mode from that behavior.
3. Preserve provider signature checks and framework cookie refresh.
4. Replace manual clients only where the package provides an equivalent client with the required identity.
5. Update function configuration consistently with the new request gate.
6. Test missing, valid, malformed, expired, and wrong-kind credentials plus CORS preflight where applicable.

Do not mechanically translate auth names or fields from old examples. Use the installed version's types and migration notes.

## Verify

- Typecheck against the locked dependency.
- Run package and application tests.
- Exercise each accepted and rejected credential path.
- Confirm user-scoped queries retain RLS and elevated operations occur only where intended.
- Confirm secrets are not logged, returned, or committed.

For detailed APIs, use the matching package's `docs/getting-started.md`, `docs/auth-modes.md`, adapter docs, core-primitives docs, error-handling docs, API reference, security docs, and source exports. Treat those files as versioned references, not timeless claims.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Secret safety and explicit external-operation permissions remain independent; only authorized retained repository changes checkpoint.
