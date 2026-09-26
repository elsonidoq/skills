<div align="center">

# 🧠 Claude Code-compatible memory for OpenCode

**Persistent, local-first shared memory for OpenCode and Claude Code — one plugin, zero migration.**

This OpenCode plugin lets OpenCode read and write Claude Code-compatible Markdown memory files, so both CLIs share the same project context.

Claude Code writes memory → OpenCode reads it. OpenCode writes memory → Claude Code reads it.

[![npm version](https://img.shields.io/npm/v/opencode-claude-memory.svg?style=flat-square)](https://www.npmjs.com/package/opencode-claude-memory)
[![npm downloads](https://img.shields.io/npm/dm/opencode-claude-memory.svg?style=flat-square)](https://www.npmjs.com/package/opencode-claude-memory)
[![License](https://img.shields.io/npm/l/opencode-claude-memory.svg?style=flat-square)](https://github.com/kuitos/opencode-claude-memory/blob/main/LICENSE)

[Quick Start](#-quick-start) • [How it works](#-how-it-works) • [Configuration](#-configuration) • [Compatibility](#-compatibility-with-claude-code) • [Migrating from v1](#-migrating-from-v1) • [FAQ](#-faq)

</div>

---

## 🆕 OpenCode 2.0.16 port

This branch ports the plugin to the **OpenCode 2 plugin API** as shipped in **OpenCode 2.0.16**
(`@opencode/plugin@2.0.16`). The V1 `PluginModule` (`{ id, server }`) is not accepted by 2.0.16; the
default export is now a V2 definition (`{ id, setup(ctx) }`).

```jsonc
// opencode.jsonc — load the built plugin from a local directory
{
  "plugins": [
    {
      "package": "file:///home/USER/prog/opencode-claude-memory-v2-port/dist",
      "options": {}
    }
  ]
}
```

Local (path) plugins must point at a **directory** containing `index.js`; a bare `.js` file is
rejected by 2.0.16 (`configured plugin path must be a directory`).

Everything that defines the product is unchanged: the same `~/.claude/projects/<project>/memory/`
paths, the same Markdown + YAML frontmatter, the same `MEMORY.md` index, the same `user` / `feedback`
/ `project` / `reference` taxonomy, the same worktree canonicalisation, and zero migration of
existing memories.

### Fresh clone / setup

`node_modules/` and the build output `dist/` are intentionally **not** tracked, so the plugin must be
built after a clone. This port usually lives inside the OpenCode config repo
(`~/.config/opencode/opencode-claude-memory-v2-port`), so cloning that repo already provides the
source. Requires [Bun](https://bun.sh) (see `.bun-version`; the reference build used Bun 1.3.11).

```bash
# point this at wherever the port was cloned/vendored
cd ~/.config/opencode/opencode-claude-memory-v2-port

bun install          # installs @opencode/plugin@2.0.16 + zod
bun run build        # emits dist/index.js, which the plugin entry points at

# optional sanity checks
bun run typecheck
bun test
```

Then reference the built **directory** in `opencode.json(c)` — the dynamic path is
`<port-dir>/dist`:

```jsonc
{
  "plugins": [
    {
      "package": "file:///home/USER/.config/opencode/opencode-claude-memory-v2-port/dist",
      "options": {}
    }
  ]
}
```

Restart OpenCode after adding or changing the plugin entry. Confirm it loaded with
`opencode plugin list` (expected: `opencode-claude-memory  local  .../dist/index.js`).

The integration layer was rewritten because the V2 API differs substantially:

| Concern | V2 implementation |
| --- | --- |
| Entrypoint | `export default { id, setup(ctx) }` |
| Tools | `ctx.tool.transform(editor => editor.add(...))`, JSON Schema inputs, `{ content }` results |
| Recall injection | one `ctx.session.hook("context", ...)` that reads `event.messages` and pushes into `event.system` |
| Events | `ctx.event.subscribe({ signal })` (`event.data`, not `event.properties`) |
| Extraction trigger | `session.execution.succeeded` / `session.idle`, debounced |
| Extraction work | `ctx.generate.text` returns a JSON plan; the plugin writes it through the same `MemoryStore` |
| Auto-dream work | `ctx.generate.text` returns `{ upserts, deletes }`; applied under the existing cross-process lock |
| Recall selection | `ctx.generate.text` (tool-less, session-less) |
| Compaction | `session.compaction.ended` clears the surfaced-memory set; memory is re-injected on every request |
| Cleanup | the function returned from `setup` aborts the event subscription and disposes registrations |

### Repository memory (on by default)

By default the plugin keeps the memories **inside the project repository** and exposes them to Claude
Code through a symlink at the central path:

```text
~/.claude/projects/<key>/memory  ──symlink──▶  <canonical repo root>/.claude/memory
```

So OpenCode and Claude Code both read/write the same Markdown files, but those files live with the
project (and can be committed or gitignored).

```jsonc
{
  "plugins": [
    {
      "package": "file:///home/USER/.config/opencode/opencode-claude-memory-v2-port/dist",
      "options": {
        "repositoryMemory": { "enabled": true, "dir": ".claude/memory" }
      }
    }
  ]
}
```

- `dir` is relative to the **canonical** repository root (worktrees share one directory) and is
  validated against traversal/symlink escape. Set `enabled: false` to keep the original central-only
  layout.
- Reconcile runs once per location, before memory is opened:

| Central (`~/.claude/projects/<key>/memory`) | Repo (`<repo>/<dir>`) | What happens |
| --- | --- | --- |
| symlink → repo | exists | nothing (already linked) |
| non-empty, not → repo | exists | **plugin load error** — both sides hold memories; nothing is mutated |
| missing or empty | exists | central is replaced with a symlink to the repo |
| non-empty | missing | memory keeps working centrally; the session shows a notice with migration commands |
| missing or empty | missing | repo dir is created and central is symlinked to it |

- A conflict is a real plugin load failure (OpenCode shows the exception) so the two copies can never
  silently diverge. Fix it by merging one side and running the printed `rm -rf … && ln -s …`.
- The notice case never moves anything automatically; it prints:

  ```bash
  mkdir -p "$(dirname "<repo>/<dir>")"
  mv "<central>" "<repo>/<dir>"
  ln -s "<repo>/<dir>" "<central>"
  ```

- If the platform refuses symlinks (e.g. Windows without developer mode), the plugin logs it and
  continues from the central path — it never crashes.
- Plugin-private state (`~/.claude/opencode-memory/<key>`) stays central and is never linked.
- If you commit memories, remove `<dir>` from the project's `.gitignore`; otherwise add it.

### 2.0.16 limitations (documented differences)

- **No per-prompt agent/tools, and plugin tools are Code Mode only.** 2.0.16 exposes plugin tools to
  the model through the Code Mode `execute` tool, which also permits arbitrary shell. Running the V1
  tool-loop forks on untrusted transcript content would therefore be unsafe and un-sandboxable, so
  extraction and auto-dream are single tool-less `generate.text` calls whose JSON plan the plugin
  applies itself. The model still decides what to remember; only the tool-loop transport changed.
- **No `session.list` / `session.remove`.** Start-up catch-up of sessions abandoned by a dead
  process cannot be reproduced, and a plugin cannot delete sessions. Extraction therefore relies on
  the live event stream; `extract.catchUpLimit` is accepted for config compatibility but unused.
- **No server-log API.** `ctx.app` exposes only name/version/channel, so diagnostics go to the
  process console (`OPENCODE_MEMORY_DEBUG=1` enables info/debug).
- **Model selection.** `generate.text` uses the default model; the old hidden-agent model overrides
  no longer apply.

See `docs/v2-port-migration.md` for the full V1 → V2 mapping.

---

## ✨ At a glance

- **Memory tools** — `memory_save` / `memory_delete` / `memory_list` / `memory_search` / `memory_read`, plus the Claude Code memory instructions injected into every system prompt.
- **LLM recall** — before each turn a hidden agent picks the memories relevant to the query; they appear in the *first* LLM call, including single-step questions.
- **Automatic extraction** — after a session goes idle, a sandboxed fork reviews only the *new* part of the conversation and saves what is worth keeping. Sessions closed before the fork ran are caught up at the next start.
- **Auto-dream** — periodic consolidation (merge / prune / rewrite) gated on time and session count, like Claude Code.
- **Claude Code-compatible** — same directory, same file format, same taxonomy, same worktree handling. `MEMORY.md` is edited line by line so hand-organised indexes stay intact.
- **Cross-platform, no shell hook** — everything runs inside the OpenCode process through the plugin SDK. No `python3`, no `jq`, no wrapper.

## 🚀 Quick Start

Requires OpenCode **≥ 1.18**.

```jsonc
// opencode.json (project) or ~/.config/opencode/opencode.json (global)
{
  "plugin": ["opencode-claude-memory"]
}
```

That's it. Start `opencode` and use it as usual. Memories live in `~/.claude/projects/<project>/memory/` (or under `$CLAUDE_CONFIG_DIR`), exactly where Claude Code keeps them.

## ⚙️ How it works

```mermaid
graph LR
    U[User turn] --> R[Hidden recall agent<br/>selects relevant memories]
    R --> S[System prompt: instructions + MEMORY.md + recalled memories]
    S --> A[Main agent answers<br/>memory_* tools available]
    A --> I[session.idle]
    I --> E[Extraction fork<br/>new messages only]
    E --> M[(~/.claude/projects/&lt;project&gt;/memory/)]
    E --> D{Auto-dream gate}
    D -->|24h & 5 sessions| C[Consolidation fork]
    C --> M
```

1. **Recall** — `experimental.chat.messages.transform` starts a selector prefetch for each new user turn (a hidden child session running `opencode-memory-recall`). `experimental.chat.system.transform` waits for it up to `recall.waitMs` (default 1.5 s) and injects the selected memories. Memories already in the conversation are not re-injected; after compaction they can surface again.
2. **Extraction** — every `session.idle` is debounced (`extract.debounceMs`). The plugin fetches the session's messages, slices them after the per-session watermark, and — only if there is a new user message — runs `opencode-memory-extract` in a child session restricted to `memory_save` / `memory_list` / `memory_read`. On success the watermark advances; if the main agent already saved memory in that stretch the fork is skipped.
3. **Catch-up** — on start-up the plugin lists the project's sessions and extracts the ones updated after their watermark (at most `extract.catchUpLimit`). This covers "answer, then quit immediately".
4. **Auto-dream** — after each extracted session the gate is evaluated (`autodream.minHours` since the last pass **and** `autodream.minSessions` extracted since). When it passes, `opencode-memory-dream` runs with all five memory tools. A lock file prevents two OpenCode processes from consolidating at once.
5. **Ignore memory** — "ignore memory" in a user message switches memory off for the rest of the session (no index, no recall); "use memory again" switches it back on.

State that is private to the plugin (watermarks, auto-dream gate, lock) lives in `<CLAUDE_CONFIG_DIR>/opencode-memory/<project>/`, never inside the Claude Code project directory.

## 🔧 Configuration

All behaviour is configured through OpenCode's own configuration. There are no `OPENCODE_MEMORY_*` environment variables.

```jsonc
// opencode.json
{
  "plugin": [
    ["opencode-claude-memory", {
      "extract":   { "enabled": true, "timeoutMs": 120000, "debounceMs": 10000, "maxConversationChars": 60000, "catchUpLimit": 5 },
      "autodream": { "enabled": true, "minHours": 24, "minSessions": 5, "timeoutMs": 300000 },
      "recall":    { "enabled": true, "waitMs": 1500, "timeoutMs": 30000, "maxMemories": 5 }
    }]
  ],
  "agent": {
    "opencode-memory-extract": { "model": "anthropic/claude-haiku-4-5", "steps": 20 },
    "opencode-memory-recall":  { "model": "anthropic/claude-haiku-4-5" },
    "opencode-memory-dream":   { "model": "anthropic/claude-sonnet-5" }
  }
}
```

- Every option above is optional; the values shown are the defaults. Unknown keys are rejected when the plugin loads.
- When the same plugin is listed in both the global and the project `opencode.json`, OpenCode keeps the **last** declaration (project wins); options are not merged across files.
- The three agents are registered hidden with a memory-only tool sandbox. Override any field (`model`, `steps`, `temperature`, …) under `agent.<name>`; the plugin fills in the rest.
- `CLAUDE_CONFIG_DIR` is honoured exactly like Claude Code does, and is the only environment variable the plugin reads.

Logs go to the OpenCode service log (`opencode` log directory, service `opencode-claude-memory`).

## 🤝 Compatibility with Claude Code

| Aspect | Claude Code | This plugin |
|---|---|---|
| Memory directory | `~/.claude/projects/<sanitized canonical git root>/memory/` | identical (`sanitizePath`, worktree → main repo resolution ported byte for byte) |
| File format | Markdown + `name` / `description` / `type` frontmatter | identical; frontmatter parsed only within the first 30 lines, as in Claude Code |
| Taxonomy | `user`, `feedback`, `project`, `reference` | identical |
| `MEMORY.md` | one-line pointers, hand-organisable | read with the same truncation rules; written with minimal line-level edits |
| Sub-directories | `team/x.md` etc. | scanned, recalled and addressable from every tool |
| System prompt | memory instructions + index + recalled memories | ported sections (`memoryTypes.ts`, `memdir.ts`) |
| Recall | LLM side query | LLM side query in a hidden child session (`findRelevantMemories.ts` port) |
| Extraction / auto-dream | after session, gated | after `session.idle` + start-up catch-up, gated the same way |

Memory files written by either tool need no conversion in either direction.

## 📝 Memory format

```markdown
---
name: User prefers terse responses
description: User wants concise answers without trailing summaries
type: feedback
---

Skip post-action summaries. User reads diffs directly.

**Why:** User explicitly requested terse output style.
**How to apply:** Don't summarize changes at the end of responses.
```

## 🔁 Migrating from v1

v2 removes the shell wrapper, the `opencode-memory` CLI and every `OPENCODE_MEMORY_*` environment variable. Memory files are untouched and need no conversion.

```bash
# 1. remove the v1 shell hook, then the v1 package (v2 no longer needs a global install)
opencode-memory uninstall     # or delete the ">>> opencode-memory auto-initialization >>>" block from your rc file
npm uninstall -g opencode-claude-memory

# 2. drop OPENCODE_MEMORY_* from your shell configuration
grep -n OPENCODE_MEMORY ~/.zshrc ~/.bashrc ~/.zshenv ~/.profile 2>/dev/null
```

```jsonc
// 3. pin the major in opencode.json — OpenCode caches npm plugins per specifier,
//    so a bare "opencode-claude-memory" keeps serving the v1 it installed earlier
{
  "plugin": ["opencode-claude-memory@2"]
}
```

Everything the environment variables used to control now lives under `extract`, `autodream`, `recall` and `agent.opencode-memory-*` in `opencode.json` — see [Configuration](#-configuration). The v1 documentation, including the full list of environment variables, stays available in the [v1 README](https://github.com/kuitos/opencode-claude-memory/blob/v1.7.7/README.md).

## ❓ FAQ

**Is this a new memory system?** No. It is a compatibility layer around Claude Code's memory layout and conventions.

**Do I need to migrate existing memory?** No. Existing Claude Code memory files are used as they are.

**Where is data stored?** `~/.claude/projects/<project>/memory/` (or `$CLAUDE_CONFIG_DIR/projects/...`). Plugin state lives in `$CLAUDE_CONFIG_DIR/opencode-memory/<project>/`.

**Can I disable extraction, auto-dream or recall?** Yes — `extract.enabled`, `autodream.enabled`, `recall.enabled` in the plugin options.

**Why did my first answer take a moment longer?** The system prompt waits up to `recall.waitMs` for the selector. Set it to `0` to never wait (recalled memories then appear from the second LLM call of a turn onwards).

**Does the extraction fork see my whole conversation?** Only the messages after the last extraction, capped at `extract.maxConversationChars` (newest first). The fork can only call memory tools.

## 🧪 Development

```bash
bun install
bun test            # unit, integration and eval tests
bun run evals       # readable task-eval report
bun run lint        # biome
bun run typecheck
bun run build       # emits dist/
```

Releases are cut by semantic-release on push to `main`.

## 📄 License

[MIT](LICENSE) © [kuitos](https://github.com/kuitos)
