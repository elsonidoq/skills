import type { Plugin } from "@opencode/plugin"
import { parseConfig } from "./config.js"
import { ExtractionCoordinator } from "./extraction/ExtractionCoordinator.js"
import { RecallCoordinator } from "./recall/RecallCoordinator.js"
import { MemoryStore } from "./store/MemoryStore.js"
import { resolveMemoryRoot } from "./store/paths.js"
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
      const store = new MemoryStore(memoryRoot, config)
      const log = createLogger(env)
      const host = createMemoryHost(ctx, directory, log)
      const deps = { store, config, host, log }
      const recall = new RecallCoordinator(deps)
      const extraction = new ExtractionCoordinator(deps)

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
