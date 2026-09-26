// The single narrow seam between the memory core and OpenCode 2.0.16.
//
// The V1 tool-loop forks cannot be reproduced safely: 2.0.16 exposes plugin tools only through Code
// Mode (`execute`), which also permits arbitrary shell, and gives plugins no way to delete or list
// sessions. Extraction and auto-dream therefore use `ctx.generate.text` (a transient, tool-less
// model call) and the plugin applies the resulting JSON plan itself. Recall selection uses the same
// call. Everything stays cancellable.
import type { ChatMessage, PluginContext } from "../sdk.js"
import { toChatMessages } from "../sdk.js"
import type { Logger } from "../util/log.js"

export interface MemoryHost {
  readonly directory: string
  // Persisted messages of a session, converted to the internal shape (used by extraction).
  fetchMessages(id: string, signal?: AbortSignal): Promise<ChatMessage[]>
  // `ctx.generate.text`: a transient, tool-less model call with no session.
  generateText(prompt: string, signal?: AbortSignal): Promise<string>
  log: Logger
}

export function createMemoryHost(ctx: PluginContext, directory: string, log: Logger): MemoryHost {
  return {
    directory,
    log,

    async fetchMessages(id, signal) {
      const messages = await ctx.session.context({ sessionID: id }, { signal })
      return toChatMessages(messages)
    },

    async generateText(prompt, signal) {
      const result = await ctx.generate.text({ prompt }, { signal })
      return result.text
    },
  }
}
