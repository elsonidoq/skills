import { join, resolve } from "node:path"
import type { Plugin } from "@opencode/plugin"
import { parseConfig } from "./config.js"
import { ExtractionCoordinator } from "./extraction/ExtractionCoordinator.js"
import { RecallCoordinator } from "./recall/RecallCoordinator.js"
import { MemoryStore } from "./store/MemoryStore.js"
import { findCanonicalGitRoot, resolveMemoryRoot, sanitizePath } from "./store/paths.js"
import { reconcileRepositoryMemory } from "./store/repositoryMemory.js"
import { buildMemoryToolDefinitions } from "./tools.js"
import { createLogger } from "./util/log.js"
import { createMemoryHost } from "./v2/host.js"

export const PLUGIN_ID = "opencode-claude-memory"

// Assembly only. Every piece of mutable state lives on the coordinators created here, so OpenCode's
// multi-directory server gets fully isolated instances. `env` and `homeDir` are injectable so tests
// never touch the real environment (CLAUDE_CONFIG_DIR is the only variable read, see config.ts).
//
// The returned object is exactly what `Plugin.define` produces; the literal form avoids a runtime
// import of `@opencode/plugin`, which OpenCode 2.0.16 does not resolve for local (path) plugins.
export function createMemoryPlugin(env: NodeJS.ProcessEnv = process.env, homeDir?: string): Plugin.Plugin {
  return {
    id: PLUGIN_ID,
    async setup(ctx) {
      const config = parseConfig(ctx.options, env, homeDir)
      const directory = ctx.location.directory
      const memoryRoot = resolveMemoryRoot(ctx.location.project.canonical ?? ctx.location.project.directory, directory)
      const log = createLogger(env)

      // Decide where memory physically lives before the store touches the filesystem. When
      // repositoryMemory is enabled this links the central Claude path to the project repo, or
      // reports a conflict/notice (see repositoryMemory.ts).
      const canonicalRoot = findCanonicalGitRoot(memoryRoot) ?? memoryRoot
      const centralDir = join(config.claudeConfigDir, "projects", sanitizePath(canonicalRoot), "memory")
      const reconcile = reconcileRepositoryMemory({
        enabled: config.repositoryMemory.enabled,
        dir: config.repositoryMemory.dir,
        canonicalRoot,
        centralDir,
      })
      if (reconcile.status === "conflict") {
        log("error", "repository memory conflict", { centralDir, canonicalRoot })
        throw new Error(reconcile.message)
      }
      const pendingNotice =
        reconcile.status === "notice" || reconcile.status === "unsupported" ? reconcile.message : undefined
      if (pendingNotice) log("warn", "repository memory notice", { centralDir, canonicalRoot })

      const store = new MemoryStore(memoryRoot, config)
      const host = createMemoryHost(ctx, directory, log)
      const deps = { store, config, host, log }
      const recall = new RecallCoordinator(deps)
      const extraction = new ExtractionCoordinator(deps)
      const notifiedSessions = new Set<string>()

      const toolRegistration = await ctx.tool.transform((editor) => {
        for (const definition of buildMemoryToolDefinitions(store, extraction)) editor.add(definition)
      })

      const contextRegistration = await ctx.session.hook("context", async (event) => {
        await recall.onContext(event)
      })

      // One-time start-up maintenance (legacy hook warning, auto-dream state migration).
      void extraction.initialize()

      const controller = new AbortController()
      void (async () => {
        try {
          for await (const event of ctx.event.subscribe({ signal: controller.signal })) {
            log("debug", "event", { type: event.type })
            // Surface the repository-memory notice once per session, in the transcript rather than
            // only the server log.
            if (event.type === "session.execution.started" && pendingNotice) {
              const sessionID = event.data.sessionID
              const location = (event as { location?: { directory?: string } }).location?.directory
              const sameLocation = !location || resolve(location) === resolve(directory)
              if (sameLocation && !notifiedSessions.has(sessionID)) {
                notifiedSessions.add(sessionID)
                void Promise.resolve(ctx.session.synthetic({ sessionID, text: pendingNotice })).catch(() => {})
              }
            }
            recall.onEvent(event)
            extraction.onEvent(event)
          }
        } catch {
          // subscription ended (shutdown)
        }
      })()

      return async () => {
        controller.abort()
        extraction.dispose()
        recall.dispose()
        await Promise.allSettled([toolRegistration.dispose(), contextRegistration.dispose()])
      }
    },
  }
}

export const MemoryPlugin: Plugin.Plugin = createMemoryPlugin()

export default createMemoryPlugin()

export { MEMORY_AGENTS, type MemoryConfig, type MemoryOptions, MemoryOptionsSchema } from "./config.js"
export { MemoryStore } from "./store/MemoryStore.js"
