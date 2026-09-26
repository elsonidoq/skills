// Type aliases derived from the OpenCode 2.0.16 plugin package so the rest of the code base never
// spells out hand-written subsets of the plugin context, session client or message shapes.
//
// `@opencode/plugin` is imported for TYPES ONLY: OpenCode 2.0.16 does not resolve the package for
// local (path) plugins, and `Plugin.define` is a runtime identity helper. The plugin object is
// assembled literally in index.ts. The subpath type imports below are erased at build time.
import type { Plugin } from "@opencode/plugin"
import type { SessionContext as SessionContextHookEvent } from "@opencode/plugin/promise/session"
import type { ToolContext as ToolExecuteContext, Result as ToolResult } from "@opencode/plugin/promise/tool"

export type { SessionContextHookEvent, ToolExecuteContext, ToolResult }

// The context handed to `setup`.
export type PluginContext = Parameters<Plugin.Plugin["setup"]>[0]

// Event passed to `ctx.session.hook("context", ...)`.
export type ContextHookEvent = SessionContextHookEvent
export type ContextMessage = ContextHookEvent["messages"][number]
export type ContextSystemPart = ContextHookEvent["system"][number]

// Element yielded by `ctx.event.subscribe(...)`.
export type V2Event = ReturnType<PluginContext["event"]["subscribe"]> extends AsyncIterable<infer E> ? E : never

// A session row as returned by the 2.0.16 session client.
export type SessionInfo = Awaited<ReturnType<PluginContext["session"]["create"]>>

// A message row as returned by `ctx.session.context(...)`.
export type SessionMessage = Awaited<ReturnType<PluginContext["session"]["context"]>>[number]

// ─── internal message model ─────────────────────────────────────────────────
// The memory core (extraction slicing, conversation building, recall helpers) works on one
// tolerant shape. V2 session messages are converted into it exactly once, in toChatMessage().

export type MessagePart = {
  type?: string
  text?: string
  synthetic?: boolean
  tool?: string
  state?: { status?: string; output?: string }
  [key: string]: unknown
}

export type ChatMessage = {
  info: {
    id?: string
    role?: string
    sessionID?: string
    time?: { created?: number; completed?: number }
    error?: unknown
    [key: string]: unknown
  }
  parts: MessagePart[]
}

function toolOutput(state: {
  status: string
  content?: ReadonlyArray<{ type: string; text?: string }>
  error?: { message?: string }
}): string | undefined {
  if (state.status === "completed" && Array.isArray(state.content)) {
    const text = state.content
      .filter((part) => part.type === "text" && typeof part.text === "string")
      .map((part) => part.text as string)
      .join("\n")
    return text || undefined
  }
  if (state.status === "error" && state.error?.message) return state.error.message
  return undefined
}

// Converts one V2 session message into the internal shape. Synthetic user messages keep
// `synthetic: true` so they are excluded from extraction, matching the V1 behaviour.
export function toChatMessage(message: SessionMessage): ChatMessage {
  const base = message as {
    id?: string
    type?: string
    time?: { created?: number; completed?: number }
    text?: string
    content?: ReadonlyArray<Record<string, unknown>>
    error?: unknown
  }
  const id = typeof base.id === "string" ? base.id : undefined
  const time = base.time
  switch (base.type) {
    case "user":
      return {
        info: { id, role: "user", time: time ? { created: time.created } : undefined },
        parts: [{ type: "text", text: base.text ?? "" }],
      }
    case "synthetic":
      return {
        info: { id, role: "user", time: time ? { created: time.created } : undefined },
        parts: [{ type: "text", text: base.text ?? "", synthetic: true }],
      }
    case "system":
      return {
        info: { id, role: "system", time: time ? { created: time.created } : undefined },
        parts: [{ type: "text", text: base.text ?? "" }],
      }
    case "assistant": {
      const parts: MessagePart[] = []
      for (const part of base.content ?? []) {
        const type = part.type
        if (type === "text" && typeof part.text === "string") {
          parts.push({ type: "text", text: part.text })
        } else if (type === "reasoning" && typeof part.text === "string") {
          parts.push({ type: "reasoning", text: part.text })
        } else if (type === "tool" && typeof part.name === "string") {
          const state = (part.state ?? {}) as {
            status?: string
            content?: ReadonlyArray<{ type: string; text?: string }>
            error?: { message?: string }
          }
          parts.push({
            type: "tool",
            tool: part.name,
            state: {
              status: state.status,
              output: toolOutput({ status: state.status ?? "", content: state.content, error: state.error }),
            },
          })
        }
      }
      return {
        info: {
          id,
          role: "assistant",
          time: time ? { created: time.created, completed: time.completed } : undefined,
          error: base.error,
        },
        parts,
      }
    }
    default:
      return { info: { id, role: base.type, time: time ? { created: time.created } : undefined }, parts: [] }
  }
}

export function toChatMessages(messages: readonly SessionMessage[]): ChatMessage[] {
  return messages.map(toChatMessage)
}

// The last assistant message's text, used to read the recall selector's JSON answer.
export function assistantText(messages: readonly ChatMessage[]): string {
  for (let i = messages.length - 1; i >= 0; i--) {
    const message = messages[i]
    if (!message || message.info.role !== "assistant" || !Array.isArray(message.parts)) continue
    const text = message.parts
      .filter((part) => part.type === "text" && typeof part.text === "string")
      .map((part) => part.text as string)
      .join("\n")
      .trim()
    if (text) return text
  }
  return ""
}
