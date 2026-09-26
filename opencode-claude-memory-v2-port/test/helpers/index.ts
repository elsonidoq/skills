import { mkdirSync, mkdtempSync, rmSync, symlinkSync, utimesSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import type { Info as ToolInfo } from "@opencode/plugin/promise/tool"
import { type MemoryConfig, parseConfig } from "../../src/config.js"
import { createMemoryPlugin } from "../../src/index.js"
import type {
  ChatMessage,
  ContextHookEvent,
  MessagePart,
  PluginContext,
  SessionMessage,
  V2Event,
} from "../../src/sdk.js"

export type { SessionMessage } from "../../src/sdk.js"

import { MemoryStore, type SaveMemoryInput } from "../../src/store/MemoryStore.js"
import type { Logger } from "../../src/util/log.js"
import type { MemoryHost } from "../../src/v2/host.js"

// ─── temp directories ────────────────────────────────────────────────────────

const tempDirs: string[] = []

export function tempDir(prefix = "ocm-"): string {
  const dir = mkdtempSync(join(tmpdir(), prefix))
  tempDirs.push(dir)
  return dir
}

export function tempGitRepo(prefix = "ocm-repo-"): string {
  const dir = tempDir(prefix)
  mkdirSync(join(dir, ".git"), { recursive: true })
  return dir
}

let symlinkSupport: boolean | undefined
export function canSymlink(): boolean {
  if (symlinkSupport === undefined) {
    const dir = mkdtempSync(join(tmpdir(), "ocm-symlink-probe-"))
    try {
      writeFileSync(join(dir, "target"), "")
      symlinkSync(join(dir, "target"), join(dir, "link"), "file")
      symlinkSupport = true
    } catch {
      symlinkSupport = false
    } finally {
      rmSync(dir, { recursive: true, force: true })
    }
  }
  return symlinkSupport
}

export function cleanupTempDirs(): void {
  while (tempDirs.length > 0) {
    const dir = tempDirs.pop()
    if (dir) rmSync(dir, { recursive: true, force: true })
  }
}

// ─── config / store ──────────────────────────────────────────────────────────

// A private home directory per config so the v1 shell-hook detection never reads the real one.
export function makeConfig(
  options: unknown = {},
  claudeConfigDir = tempDir("ocm-claude-"),
  homeDir = tempDir("ocm-home-"),
): MemoryConfig {
  return parseConfig(options, { CLAUDE_CONFIG_DIR: claudeConfigDir }, homeDir)
}

export function makeStore(root: string = tempGitRepo(), claudeConfigDir = tempDir("ocm-claude-")): MemoryStore {
  return new MemoryStore(root, { claudeConfigDir })
}

export function seedMemory(store: MemoryStore, input: Partial<SaveMemoryInput> & { fileName: string }): string {
  const result = store.save({
    name: input.name ?? input.fileName,
    description: input.description ?? `${input.fileName} description`,
    type: input.type ?? "user",
    content: input.content ?? `${input.fileName} content`,
    fileName: input.fileName,
  })
  return result.filePath
}

export function writeRawMemory(memoryDir: string, filename: string, content: string, mtime?: Date): string {
  const filePath = join(memoryDir, ...filename.split("/"))
  mkdirSync(join(filePath, ".."), { recursive: true })
  writeFileSync(filePath, content, "utf-8")
  if (mtime) utimesSync(filePath, mtime, mtime)
  return filePath
}

export const noopLog: Logger = () => {}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function collectingLog(): { log: Logger; entries: Array<{ level: string; message: string; extra?: unknown }> } {
  const entries: Array<{ level: string; message: string; extra?: unknown }> = []
  return { entries, log: (level, message, extra) => void entries.push({ level, message, extra }) }
}

// ─── internal messages ───────────────────────────────────────────────────────
// helpers/messages.ts (extraction/recall pure helpers) operate on this shape.

let messageSeq = 0

export function textPart(text: string, extra: Record<string, unknown> = {}): MessagePart {
  return { type: "text", text, ...extra } as unknown as MessagePart
}

export function toolPart(
  tool: string,
  status: "completed" | "error" | "running" = "completed",
  output?: string,
): MessagePart {
  return { type: "tool", tool, state: { status, output } } as unknown as MessagePart
}

export function message(
  role: "user" | "assistant" | "system",
  parts: MessagePart[],
  info: Record<string, unknown> = {},
): ChatMessage {
  messageSeq += 1
  const time = role === "assistant" ? { created: messageSeq, completed: messageSeq } : { created: messageSeq }
  return { info: { id: `msg_${messageSeq}`, role, time, ...info }, parts } as unknown as ChatMessage
}

export function userMessage(text: string, sessionID?: string, info: Record<string, unknown> = {}): ChatMessage {
  return message("user", [textPart(text)], { sessionID, ...info })
}

// ─── V2 `context` hook messages (@opencode/ai Message shape) ─────────────────

export function contextUser(text: string, id?: string): ContextHookEvent["messages"][number] {
  return { id, role: "user", content: [{ type: "text", text }] } as unknown as ContextHookEvent["messages"][number]
}

export function contextAssistant(toolNames: string[] = []): ContextHookEvent["messages"][number] {
  return {
    role: "assistant",
    content: toolNames.map((name) => ({
      type: "tool-result",
      id: `t_${name}`,
      name,
      result: { type: "text", value: "" },
    })),
  } as unknown as ContextHookEvent["messages"][number]
}

// ─── fake host ───────────────────────────────────────────────────────────────

export type GenerateResponder = (prompt: string, callIndex: number) => string | Promise<string>

export type FakeHost = MemoryHost & {
  readonly prompts: string[]
  setGenerate(responder: GenerateResponder): void
  setMessages(sessionID: string, messages: ChatMessage[]): void
}

export function makeFakeHost(
  directory: string,
  options: { generate?: GenerateResponder; log?: Logger } = {},
): FakeHost {
  const prompts: string[] = []
  const messagesBySession = new Map<string, ChatMessage[]>()
  let generate = options.generate ?? (() => "")
  return {
    directory,
    log: options.log ?? noopLog,
    prompts,
    setGenerate(responder) {
      generate = responder
    },
    setMessages(sessionID, messages) {
      messagesBySession.set(sessionID, messages)
    },
    async generateText(prompt) {
      prompts.push(prompt)
      return generate(prompt, prompts.length - 1)
    },
    async fetchMessages(id) {
      return messagesBySession.get(id) ?? []
    },
  }
}

// ─── fake V2 context ─────────────────────────────────────────────────────────

export type FakeContext = {
  ctx: PluginContext
  tools: Record<string, ToolInfo>
  contextHooks: Array<(event: ContextHookEvent) => Promise<void> | void>
  syntheticCalls: Array<{ sessionID: string; text: string }>
  setMessages(sessionID: string, messages: SessionMessage[]): void
  emit(event: V2Event): Promise<void>
  dispose(): Promise<void>
}

function makeEventStream() {
  const queue: V2Event[] = []
  let wake: (() => void) | undefined
  let closed = false
  return {
    iterable: {
      async *[Symbol.asyncIterator]() {
        for (;;) {
          if (queue.length > 0) {
            yield queue.shift() as V2Event
            continue
          }
          if (closed) return
          await new Promise<void>((resolve) => {
            wake = resolve
          })
        }
      },
    },
    push(event: V2Event) {
      queue.push(event)
      wake?.()
      wake = undefined
    },
    close() {
      closed = true
      wake?.()
    },
  }
}

export function makeFakeContext(input: {
  directory: string
  projectCanonical?: string
  options?: unknown
  host?: MemoryHost
}): FakeContext {
  const tools: Record<string, ToolInfo> = {}
  const contextHooks: Array<(event: ContextHookEvent) => Promise<void> | void> = []
  const stream = makeEventStream()
  const sessionMessages = new Map<string, SessionMessage[]>()
  const syntheticCalls: Array<{ sessionID: string; text: string }> = []

  const ctx = {
    app: { name: "opencode", version: "2.0.16", channel: "test" },
    location: {
      directory: input.directory,
      project: {
        id: "proj_test",
        directory: input.directory,
        canonical: input.projectCanonical ?? input.directory,
      },
    },
    options: input.options ?? {},
    tool: {
      async transform(callback: (editor: unknown) => void) {
        const editor = {
          list: () => Object.values(tools),
          get: (id: string) => tools[id],
          add: (tool: ToolInfo) => {
            tools[tool.name] = tool
          },
          update: () => {},
          remove: () => {},
          namespace: () => {},
        }
        callback(editor)
        return { dispose: async () => {} }
      },
    },
    session: {
      async hook(name: string, callback: (event: ContextHookEvent) => Promise<void> | void) {
        if (name === "context") contextHooks.push(callback)
        return { dispose: async () => {} }
      },
      async context({ sessionID }: { sessionID: string }) {
        return sessionMessages.get(sessionID) ?? []
      },
      async synthetic({ sessionID, text }: { sessionID: string; text: string }) {
        syntheticCalls.push({ sessionID, text })
        return {
          id: `synthetic_${syntheticCalls.length}`,
          sessionID,
          type: "synthetic",
          text,
          time: { created: Date.now() },
        }
      },
    },
    generate: {
      async text({ prompt }: { prompt: string }) {
        const host = input.host
        return { text: host ? await host.generateText(prompt) : "" }
      },
    },
    event: {
      subscribe() {
        return stream.iterable
      },
    },
    agent: {
      async transform() {
        return { dispose: async () => {} }
      },
      async list() {
        return { data: [] }
      },
    },
    storage: {
      async get() {},
      async set() {},
      async remove() {},
      async scan() {
        return { entries: [] }
      },
    },
  } as unknown as PluginContext

  return {
    ctx,
    tools,
    contextHooks,
    syntheticCalls,
    setMessages(sessionID, messages) {
      sessionMessages.set(sessionID, messages)
    },
    async emit(event) {
      stream.push(event)
      // Let the subscription loop consume it.
      await new Promise((resolve) => setTimeout(resolve, 0))
    },
    async dispose() {
      stream.close()
    },
  }
}

// ─── run a tool ──────────────────────────────────────────────────────────────

export function resultOutput(result: unknown): string {
  const value = result as { content?: unknown }
  return typeof value.content === "string" ? value.content : ""
}

export function resultTitle(result: unknown): string | undefined {
  const value = result as { metadata?: { title?: unknown } }
  return typeof value.metadata?.title === "string" ? value.metadata.title : undefined
}

export async function runTool(
  tools: Record<string, ToolInfo>,
  name: string,
  args: Record<string, unknown>,
  ctx: Record<string, unknown> = {},
): Promise<{ output: string; title?: string }> {
  const definition = tools[name]
  if (!definition) throw new Error(`tool ${name} not registered`)
  const result = await (definition.execute as (input: unknown, context: unknown) => Promise<unknown>)(args, {
    sessionID: "ses_test",
    agent: "build",
    messageID: "msg_test",
    id: "call_test",
    signal: new AbortController().signal,
    progress: async () => {},
    ...ctx,
  })
  return { output: resultOutput(result), title: resultTitle(result) }
}

// ─── plugin harness ──────────────────────────────────────────────────────────

export type Harness = {
  tools: Record<string, ToolInfo>
  contextHooks: Array<(event: ContextHookEvent) => Promise<void> | void>
  host: FakeHost
  store: MemoryStore
  claudeConfigDir: string
  worktree: string
  directory: string
  syntheticCalls: Array<{ sessionID: string; text: string }>
  setSessionMessages(sessionID: string, messages: SessionMessage[]): void
  emit(event: V2Event): Promise<void>
  dispose(): Promise<void>
}

export type HarnessInput = {
  worktree?: string
  directory?: string
  projectCanonical?: string
  claudeConfigDir?: string
  homeDir?: string
  options?: unknown
  generate?: GenerateResponder
  log?: Logger
}

export async function makeHarness(input: HarnessInput = {}): Promise<Harness> {
  const worktree = input.worktree ?? tempGitRepo()
  const directory = input.directory ?? worktree
  const claudeConfigDir = input.claudeConfigDir ?? tempDir("ocm-claude-")
  const homeDir = input.homeDir ?? tempDir("ocm-home-")
  const host = makeFakeHost(directory, { generate: input.generate, log: input.log })
  const fake = makeFakeContext({
    directory,
    projectCanonical: input.projectCanonical ?? worktree,
    options: input.options,
    host,
  })
  const plugin = createMemoryPlugin({ CLAUDE_CONFIG_DIR: claudeConfigDir }, homeDir)
  const cleanup = await plugin.setup(fake.ctx)
  const store = new MemoryStore(input.projectCanonical ?? worktree, { claudeConfigDir })
  return {
    tools: fake.tools,
    contextHooks: fake.contextHooks,
    host,
    store,
    claudeConfigDir,
    worktree,
    directory,
    syntheticCalls: fake.syntheticCalls,
    setSessionMessages: fake.setMessages,
    emit: fake.emit,
    async dispose() {
      await cleanup?.()
      await fake.dispose()
    },
  }
}

// Runs the registered context hook and returns the injected system text.
export async function runContextHook(
  harness: Harness,
  messages: ContextHookEvent["messages"],
  sessionID = "ses_test",
  agent = "build",
): Promise<{ system: string; event: ContextHookEvent }> {
  const event = { sessionID, agent, messages, system: [] as ContextHookEvent["system"] } as unknown as ContextHookEvent
  for (const hook of harness.contextHooks) await hook(event)
  return { system: event.system.map((part) => part.text).join("\n\n"), event }
}
