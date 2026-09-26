# OpenCode 1 → OpenCode 2 (2.0.16) migration map

Target runtime: OpenCode **2.0.16** (`/usr/local/lib/opencode/2.0.16/opencode`).
Authoritative plugin package: **`@opencode/plugin@2.0.16`** (npm), which is what the
2.0.16 runtime decodes (`PluginModule.LoadError: ... an id and an effect or setup function`).

The old `@opencode-ai/plugin` (V1) package is not accepted by 2.0.16.

## Entrypoint

| V1 | V2 (2.0.16) |
| --- | --- |
| `export default { id, server: Plugin }` (`PluginModule`) | `export default { id, setup(ctx) }` (`Plugin.Plugin`) |
| `Plugin = async (input, options) => Hooks` | `setup(ctx, options)` registers handlers and returns a cleanup fn |
| `input.client` | domain methods on `ctx` (`ctx.session`, `ctx.tool`, ...) |
| `input.worktree` / `input.directory` | `ctx.location.project.canonical` / `ctx.location.directory` |
| `input.project` | `ctx.location.project` |
| plugin options argument | `ctx.options` |
| returned `dispose()` | cleanup function returned by `setup` |
| returned `event` hook | `ctx.event.subscribe({ signal })` |
| returned `config` hook | `ctx.agent.transform(...)` (and other domain transforms) |

## Tools

| V1 | V2 |
| --- | --- |
| `tool: { memory_save: tool({ args, execute }) }` | `ctx.tool.transform(editor => editor.add({ name, description, input, execute }))` |
| `args` via `tool.schema` (zod) | plain JSON Schema `input` |
| `execute(args, ctx)` returns `{ title, output }` | `execute(input, ctx)` returns `Tool.Result` (`{ content, output?, metadata? }`) |
| `ctx.sessionID` | `ctx.sessionID` (same) |

## Context / recall injection

| V1 | V2 |
| --- | --- |
| `experimental.chat.messages.transform` (derive turn, start prefetch, strip ignored segment) | `ctx.session.hook("context", ...)` — read `event.messages` |
| `experimental.chat.system.transform` (await prefetch, push prompt) | same `context` hook — push `{ type: "text", text }` into `event.system` |
| system parts appended to `output.system` array of strings | `event.system` array of `SystemPart` |
| `experimental.session.compacting` | `ctx.session.hook("compaction", ...)` |

## Session events

| V1 | V2 |
| --- | --- |
| `event: async ({ event }) =>` | `for await (const event of ctx.event.subscribe({ signal }))` |
| `event.properties.sessionID` | `event.data.sessionID` |
| `event.properties.info.id` (`session.deleted`) | `event.data.sessionID` |
| `session.idle`, `session.status`, `session.deleted` | same names, `event.data` payloads |
| — | `session.compaction.started/ended` used to reset recall state |

## Fork sub-sessions (extraction / recall selector / auto-dream)

V1 created a child session and passed `agent`, `system` and a `tools` sandbox on
`session.prompt`. V2's `session.prompt` accepts only the prompt text; agent, system and the
tool sandbox are agent/session level:

| V1 | V2 |
| --- | --- |
| `session.create({ body: { parentID, title }, query })` | `ctx.session.create({ title, agent, location: { directory } })` |
| `session.prompt({ body: { agent, system, tools, parts } })` | `ctx.session.prompt({ sessionID, text })` + `ctx.session.wait({ sessionID })` |
| agent `prompt` / `tools` config | `ctx.agent.transform` sets `system`; tool sandbox applied in the `context` hook per `event.agent` |
| `session.abort` / `session.delete` | `ctx.session.interrupt` / `ctx.session.remove` |
| `session.messages` | `ctx.session.context` |
| `session.list({ query: { directory } })` | `ctx.session.list({ directory })` |
| structured output (`format: json_schema`) on selector | selector agent prompt + JSON text parsing |
| `client.app.log` | console-based best-effort logger (`ctx.app` has no log API) |

## Cleanup

| V1 | V2 |
| --- | --- |
| `dispose()` hook | function returned from `setup()` |
| (registrations implicit) | registrations auto-dispose on unload; event subscription aborted via `AbortController` |

## Local loading note

For a local (path/file) plugin, the 2.0.16 runtime resolves bare imports from the plugin's
`node_modules`, **except** `@opencode/plugin` (the runtime does not provide it to local
plugins). The port therefore uses `@opencode/plugin` for **types only** and exports a plain
`{ id, setup }` object, which is exactly what `Plugin.define` returns at runtime. Package
plugins installed by OpenCode get `@opencode/plugin` resolved normally.
