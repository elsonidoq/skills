import { resolve } from "node:path"
import type { Plugin } from "@opencode/plugin"
import { parseConfig } from "./config.js"
import { ExtractionCoordinator } from "./extraction/ExtractionCoordinator.js"
import { RecallCoordinator } from "./recall/RecallCoordinator.js"
import { MemoryStore } from "./store/MemoryStore.js"
import { resolveClaudeProjectPaths, resolveMemoryRoot } from "./store/paths.js"
import { reconcileRepositoryMemory } from "./store/repositoryMemory.js"
import { buildMemoryToolDefinitions } from "./tools.js"
import { createLogger, getErrorMessage } from "./util/log.js"
import { withDeadline } from "./util/timeout.js"
import { createMemoryHost } from "./v2/host.js"

export const PLUGIN_ID = "opencode-claude-memory"
// Bounds the session lookup used to scope repository-memory notices; a hung RPC must not stall the
// plugin's event pump.
export const SESSION_LOOKUP_TIMEOUT_MS = 30_000
const MAX_NOTIFIED_SESSIONS = 500

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
      const paths = resolveClaudeProjectPaths(config.claudeConfigDir, memoryRoot)
      const reconcile = reconcileRepositoryMemory({
        enabled: config.repositoryMemory.enabled,
        dir: config.repositoryMemory.dir,
        canonicalRoot: paths.canonicalRoot,
        centralDir: paths.memoryDir,
      })
      if (reconcile.status === "conflict") {
        log("error", "repository memory conflict", { centralDir: paths.memoryDir, canonicalRoot: paths.canonicalRoot })
        throw new Error(reconcile.message)
      }
      const pendingNotice =
        reconcile.status === "notice" || reconcile.status === "unsupported" ? reconcile.message : undefined
      if (pendingNotice)
        log("warn", "repository memory notice", { centralDir: paths.memoryDir, canonicalRoot: paths.canonicalRoot })

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
      const rememberNotified = (sessionID: string): void => {
        notifiedSessions.add(sessionID)
        // Bound the set on a long-lived server; insertion order makes this a cheap FIFO eviction.
        if (notifiedSessions.size > MAX_NOTIFIED_SESSIONS) {
          const oldest = notifiedSessions.values().next().value
          if (oldest !== undefined) notifiedSessions.delete(oldest)
        }
      }
      const pendingNotifications = new Set<string>()
      const notifyIfOwnLocation = async (sessionID: string, eventLocation: string | undefined): Promise<void> => {
        if (notifiedSessions.has(sessionID) || pendingNotifications.has(sessionID)) return
        pendingNotifications.add(sessionID)
        let belongs = false
        let resolved = false
        try {
          if (eventLocation) {
            belongs = resolve(eventLocation) === resolve(directory)
            resolved = true
          } else {
            // `session.execution.started` does not carry a location, and every plugin instance
            // subscribes to the same global stream — resolve the session's own location so only the
            // owning instance notifies (otherwise every open project would spam every session).
            const info = (await withDeadline("session.get", SESSION_LOOKUP_TIMEOUT_MS, (signal) =>
              ctx.session.get({ sessionID }, { signal }),
            )) as { location?: { directory?: string } }
            const loc = info.location?.directory
            belongs = loc !== undefined && resolve(loc) === resolve(directory)
            resolved = true
          }
        } catch {
          // Could not determine ownership (timeout or error): retry on the next event instead of
          // suppressing the notice for this session forever.
          resolved = false
        }
        pendingNotifications.delete(sessionID)
        if (!resolved) return
        rememberNotified(sessionID)
        if (belongs) {
          void Promise.resolve(ctx.session.synthetic({ sessionID, text: pendingNotice as string })).catch((error) =>
            log("warn", "repository memory notice could not be delivered", {
              sessionID,
              error: getErrorMessage(error),
            }),
          )
        }
      }

      void (async () => {
        try {
          for await (const event of ctx.event.subscribe({ signal: controller.signal })) {
            log("debug", "event", { type: event.type })
            // Surface the repository-memory notice once per session, in the transcript rather than
            // only the server log, and only for sessions in this plugin's location. Fire-and-forget:
            // the lookup can take up to SESSION_LOOKUP_TIMEOUT_MS and must not stall the shared event
            // pump that drives recall and extraction.
            if (event.type === "session.execution.started" && pendingNotice) {
              void notifyIfOwnLocation(
                event.data.sessionID,
                (event as { location?: { directory?: string } }).location?.directory,
              )
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
