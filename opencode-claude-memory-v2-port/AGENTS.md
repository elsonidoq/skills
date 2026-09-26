# AGENTS.md

Port of Claude Code's persistent memory system to the **OpenCode 2.0.16 plugin API**
(`@opencode/plugin@2.0.16`). TypeScript on Bun. The default export is a V2 plugin definition
(`{ id, setup(ctx) }`); it is **type-only** imported from `@opencode/plugin` because 2.0.16 does not
resolve that package for local (path) plugins (see "Local loading").

This port is vendored inside the OpenCode config repo at
`~/.config/opencode/opencode-claude-memory-v2-port`. Source is tracked there; `node_modules/` and the
build output `dist/` are not, so run `bun install && bun run build` after a clone.

## Hard constraints of OpenCode 2.0.16

These shape the whole design — do not "fix" them without re-checking the runtime:

- **No `ctx.session.list` / `ctx.session.remove`.** No session listing (so no start-up catch-up) and
  no session deletion (so the plugin creates no child sessions at all).
- **Plugin tools are reachable by the model only through Code Mode (`execute`)**, which also allows
  arbitrary shell. There is no per-agent/per-prompt tool sandbox. Never run a tool-loop fork on
  untrusted transcript content; extraction and auto-dream are single tool-less `ctx.generate.text`
  calls whose JSON plan the plugin applies itself.
- **No server-log API** (`ctx.app` has name/version/channel only). Diagnostics go to the process
  console via `util/log.ts`.
- **`setup()` runs per location.** All mutable state lives on coordinator instances created there.
- **A `setup()` throw is a real, user-visible plugin load failure** (`failed to load plugin` with the
  exception). It disables the plugin for that location. Use it for hard errors (e.g. a repository
  memory conflict), not for notices.

## Structure

```
src/
├── index.ts                        # Assembly: parseConfig → reconcileRepositoryMemory → MemoryStore → coordinators → registrations. Default export { id, setup }.
├── config.ts                       # Strict zod MemoryOptionsSchema + CLAUDE_CONFIG_DIR → MemoryConfig; fixed MEMORY_AGENTS names (vestigial)
├── sdk.ts                          # V2 types from @opencode/plugin (type-only), internal ChatMessage model + toChatMessage/toChatMessages
├── tools.ts                        # memory_save / delete / list / search / read as V2 tool definitions (JSON Schema, { content } results)
├── v2/
│   └── host.ts                     # The one seam to the runtime: fetchMessages + generateText + log
├── store/
│   ├── frontmatter.ts              # THE memory file format: MEMORY_TYPES, parseFrontmatter (30-line limit), buildFrontmatter
│   ├── paths.ts                    # Pure: validateMemoryFileName (sub-paths), sanitizePath, findCanonicalGitRoot, resolveMemoryRoot
│   ├── scan.ts                     # THE scanner: MemoryHeader/MemoryEntry, manifest, surfaceKey; never follows symlinked entries
│   ├── indexFile.ts                # MEMORY.md minimal line-level upsert/remove + truncateEntrypoint
│   ├── MemoryStore.ts              # Resolves paths once; list/read/save/delete/search/scan/readIndex; stateDir
│   └── repositoryMemory.ts         # Reconciles ~/.claude/.../memory ↔ <repo>/<dir> (symlink or error/notice)
├── prompt/
│   ├── sections.ts                 # Claude Code prompt text ports (memoryTypes.ts / memdir.ts)
│   └── systemPrompt.ts             # buildMemorySystemPrompt(store, recalled, opts); AUTO_MEMORY_MARKER
├── recall/
│   ├── selector.ts                 # LLM selection via ctx.generate.text; JSON parsing
│   ├── format.ts                   # recallSelectedMemories / formatRecalledMemories / truncation / age warning
│   └── RecallCoordinator.ts        # ctx.session.hook("context"): turn state, bounded prefetch, session-scoped ignore, TTL
├── extraction/
│   ├── prompts.ts                  # EXTRACT_PROMPT / AUTODREAM_PROMPT (JSON-plan variants; only copies)
│   ├── plan.ts                     # Parse/validate extraction & auto-dream JSON plans into MemoryDraft[]
│   ├── state.ts                    # extraction-state.json (watermarks, autodream gate), atomic writes, v1 lock migration, posixCksum
│   ├── lock.ts                     # Cross-process maintenance lock: token ownership, heartbeat, reap-lock guarded stale recovery
│   ├── autodream.ts                # Gate + gate/lock + generate.text consolidation plan applied to the store
│   └── ExtractionCoordinator.ts    # session.execution.succeeded / session.idle debounce → serial queue → generate.text plan
├── hooks/
│   ├── messages.ts                 # internal-message helpers + V2 context-hook helpers (last user query, recent tools)
│   └── ignore.ts                   # ignore / resume detection
└── util/
    ├── log.ts                      # console logger (warn/error always; info/debug behind OPENCODE_MEMORY_DEBUG)
    ├── exclusiveFile.ts            # Atomic create-if-absent (tmp + hard link) and the short cross-process file lock
    ├── timeout.ts                  # withDeadline(): bounded V2 client/generate calls with an AbortSignal
    └── legacyShellHook.ts          # Read-only detection of v1's shell hook in rc files

test/
├── helpers/index.ts                # temp dirs, makeStore/makeConfig, fake V2 context + host, message builders, makeHarness
├── helpers/processWorker.ts        # real worker processes for the cross-process state/lock tests
├── plugin.test.ts, recall.test.ts, extraction.test.ts, repositoryMemory.test.ts   # plugin-level behaviour
└── store/, recall/, extraction/, config, prompt, hooks, util   # unit tests (bun test)
```

## Where to look

| Task | File |
|---|---|
| Add or change a plugin option | `src/config.ts` (schema) → consumers via `MemoryConfig` |
| Add/modify a memory tool | `src/tools.ts` |
| Change the memory file format | `src/store/frontmatter.ts` |
| Path resolution / worktree sharing / file-name rules | `src/store/paths.ts`, `src/store/MemoryStore.ts` |
| In-repo memory + symlink reconciliation | `src/store/repositoryMemory.ts` |
| `MEMORY.md` editing rules | `src/store/indexFile.ts` |
| What the main agent sees about memory | `src/prompt/systemPrompt.ts`, `src/prompt/sections.ts` |
| Which memories are recalled and when | `src/recall/RecallCoordinator.ts`, `src/recall/selector.ts` |
| Extraction trigger, watermark, plan application | `src/extraction/ExtractionCoordinator.ts`, `src/extraction/plan.ts`, `src/extraction/state.ts` |
| Auto-dream gate / lock | `src/extraction/autodream.ts` |
| V2 client seam / timeouts | `src/v2/host.ts`, `src/util/timeout.ts` |

## Behaviour map

- **Recall** — one `ctx.session.hook("context")` per model request. It derives the turn from
  `event.messages`, starts a `generate.text` selector prefetch (max `recall.maxMemories`), waits up to
  `recall.waitMs`, then pushes the memory system prompt (index + `## Recalled Memories`) into
  `event.system`. Already-surfaced memories are tracked per session and reset on
  `session.compaction.ended`.
- **Extraction** — `session.execution.succeeded` (2.0.16 end-of-turn signal) and `session.idle` are
  debounced by `extract.debounceMs`; `session.execution.started` cancels the pending debounce. The
  coordinator reads `ctx.session.context`, slices after the per-session watermark, and if a new user
  message exists asks the model for a JSON plan (`ctx.generate.text`), then calls `MemoryStore.save`
  for each entry. A `memory_save` by the main agent marks the session so the round is skipped.
- **Auto-dream** — after an extracted session passes the gate (`autodream.minHours` and
  `autodream.minSessions`), a `generate.text` consolidation request returns `{ upserts, deletes }`,
  applied under the cross-process maintenance lock.
- **Repository memory** — see below.

## Repository memory (default on)

`repositoryMemory: { enabled: true, dir: ".claude/memory" }`. At `setup()` the plugin reconciles the
central Claude path with `<canonical repo root>/<dir>`:

- central symlink → repo, or central missing/empty and repo present → link.
- both sides non-empty and unlinked → **throw** (plugin load error; nothing mutated).
- repo missing but central non-empty → keep working centrally and post a **once-per-session synthetic
  notice** with migration commands (never auto-move).
- symlink unsupported → log and continue centrally.

Notices must be scoped to the owning location: `session.execution.started` carries no location, so
resolve the session via `ctx.session.get` before notifying, otherwise every plugin instance spams
every session. Do that resolution **off** the shared event pump (fire-and-forget, bounded by
`SESSION_LOOKUP_TIMEOUT_MS`); awaiting it inline stalls recall/extraction for every session in the
location. Plugin-private state (`~/.claude/opencode-memory/<key>`) is never linked.

## Conventions

- **ESM `.js` imports**, `node:` protocol for built-ins.
- **biome** for lint + format (`bun run lint`, `bun run format`); `tsconfig.json` covers `src` + `test`
  with `noUncheckedIndexedAccess`; `tsconfig.build.json` emits `dist/`.
- **No process-level state**: every `Map`/`Set` lives on a coordinator instance created per `setup`.
- **No environment variables except `CLAUDE_CONFIG_DIR`** (read in `config.ts` only). Tests inject
  `env` and the home directory via `createMemoryPlugin(env, homeDir)` / `parseConfig(options, env, homeDir)`.
- **Every V2 client/generate call has a deadline** (`util/timeout.ts` `withDeadline`): a hung call
  otherwise pins the extraction queue and the maintenance lock forever.
- **State is transactional**: `ExtractionStateStore.update()` runs under a file lock and the mutate
  callback must decide against the data it is given, never an earlier snapshot. The maintenance lock is
  held until the watermark is written.
- **Logging** goes through `util/log.ts` (console); warn/error always, info/debug behind
  `OPENCODE_MEMORY_DEBUG`.
- **`@opencode/plugin` is a type-only import.** The runtime value of the plugin is a plain
  `{ id, setup }` object. Never add a runtime import of `@opencode/plugin` (it breaks local loading).

## Local loading

Local plugins are referenced by **directory**, not file: `"file:///…/opencode-claude-memory-v2-port/dist"`
(the `plugins` array in `opencode.json(c)`). A bare `.js` path is rejected
(`configured plugin path must be a directory`). Rebuild `dist/` after changing `src/`.

## Anti-patterns

- **NEVER** touch memory files without `resolveMemoryFilePath()` / `MemoryStore` — path traversal and
  symlink-escape risk; `MEMORY` is reserved. The scanner walks directories itself and never follows
  symlinked entries (a symlinked memory *root* is fine; that is how repository memory works).
- **NEVER** extract a slice whose trailing assistant message has no `time.completed`, and never
  advance a watermark backwards (`ExtractionCoordinator.advance` is monotonic).
- **NEVER** rewrite `MEMORY.md` wholesale — use `upsertIndexLine` / `removeIndexLine`.
- **NEVER** run a tool-loop fork / Code Mode on transcript content — use `generate.text` + `plan.ts`.
- **NEVER** notify for a session that is not in this plugin's location.
- **NEVER** delete or merge a non-empty central memory directory automatically.

## Security

- `store/paths.ts`: `validateMemoryFileName()` rejects traversal, absolute paths, dotfiles, null bytes
  and the reserved name; `resolveMemoryFilePath()` re-checks containment after resolution.
  `resolveCanonicalRoot()` validates the worktree gitdir → commondir → backlink chain.
- `store/repositoryMemory.ts`: `repositoryMemoryDir()` keeps `dir` inside the canonical root;
  `repositoryMemory.dir` in `config.ts` rejects absolute and `..` segments.
- Extraction/auto-dream read untrusted transcript content but never expose tools to the model.

## Constants

| Constant | Value | Location |
|---|---|---|
| `PLUGIN_ID` | `opencode-claude-memory` | `index.ts` |
| `MAX_MEMORY_FILES` | 200 | `store/paths.ts` |
| `MAX_MEMORY_FILE_BYTES` | 40,000 | `store/paths.ts` |
| `MAX_ENTRYPOINT_LINES` / `MAX_ENTRYPOINT_BYTES` | 200 / 25,000 | `store/paths.ts` |
| `FRONTMATTER_MAX_LINES` | 30 | `store/frontmatter.ts` |
| recall `MAX_MEMORY_LINES` / `MAX_MEMORY_BYTES` | 200 / 4,096 | `recall/format.ts` |
| `SESSION_STATE_TTL_MS` (recall) | 1 h | `recall/RecallCoordinator.ts` |
| `MAX_EXTRACTED_MEMORIES` | 5 | `extraction/plan.ts` |
| `MAX_AUTODREAM_UPSERTS` / `MAX_AUTODREAM_DELETES` | 20 / 50 | `extraction/plan.ts` |
| `AUTODREAM_DUMP_MAX_CHARS` | 60,000 | `extraction/autodream.ts` |
| `MIN_CONVERSATION_CHARS` | 20 | `extraction/ExtractionCoordinator.ts` |
| `MAX_EXTRACTION_FAILURES` | 3 | `extraction/ExtractionCoordinator.ts` |
| `SDK_READ_TIMEOUT_MS` | 30 s | `extraction/ExtractionCoordinator.ts` |
| `SESSION_STATE_TTL_MS` (extraction state) | 30 d | `extraction/state.ts` |
| `MAINTENANCE_STALE_LOCK_MS` / `MAINTENANCE_HEARTBEAT_MS` | 10 min / 60 s | `extraction/lock.ts` |
| `FILE_LOCK_TIMEOUT_MS` / `FILE_LOCK_STALE_MS` | 5 s / 10 s | `util/exclusiveFile.ts` |

## Commands

```bash
bun install
bun test                 # unit + plugin-level tests
bun run typecheck
bun run build            # dist/ via tsconfig.build.json
bun run lint             # biome ci
bun run format           # biome check --write
```

## Notes

- Memory directory: `<CLAUDE_CONFIG_DIR>/projects/<sanitizePath(canonicalGitRoot)>/memory/`, shared
  with Claude Code. With repositoryMemory on (default) that path is a symlink to `<repo>/<dir>`.
  `sanitizePath` / `djb2Hash` are exact copies of Claude Code's.
- Plugin state: `<CLAUDE_CONFIG_DIR>/opencode-memory/<same key>/extraction-state.json` (+
  `extraction-state.lock` around every update, + `maintenance.lock` shared across processes). A v1
  `<cksum>.consolidate-lock` is migrated on first start-up; a v1 shell hook still present in an rc file
  is reported with a warn log.
- OpenCode dedupes `plugins` entries by package name across global/project config, last one wins.
- Design history lives in `docs/v2/`; the V1→V2 mapping is in `docs/v2-port-migration.md`.
