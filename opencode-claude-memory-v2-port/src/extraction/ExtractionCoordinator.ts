// Incremental post-session memory extraction driven by `session.idle`, with a persisted watermark
// per session.
//
// V2 cannot run the V1 tool-loop fork safely (plugin tools are Code Mode only), so extraction is a
// single `ctx.generate.text` call that returns a JSON plan which the plugin applies through the
// same MemoryStore the memory_* tools use.
import type { MemoryConfig } from "../config.js"
import { roleOf } from "../hooks/messages.js"
import type { ChatMessage, V2Event } from "../sdk.js"
import type { MemoryStore } from "../store/MemoryStore.js"
import { findLegacyShellHooks } from "../util/legacyShellHook.js"
import { getErrorMessage, type Logger } from "../util/log.js"
import { TimeoutError, withDeadline } from "../util/timeout.js"
import type { MemoryHost } from "../v2/host.js"
import { AutoDream } from "./autodream.js"
import { MaintenanceLock } from "./lock.js"
import { parseExtractionPlan } from "./plan.js"
import { buildExtractionPrompt } from "./prompts.js"
import { ExtractionStateStore, migrateLegacyAutodreamState, type SessionExtractionState } from "./state.js"

// Deadline for the plain reads and the extraction generation.
export const SDK_READ_TIMEOUT_MS = 30_000
export const MAX_EXTRACTION_FAILURES = 3
export const MIN_CONVERSATION_CHARS = 20

function messageTime(message: ChatMessage): { created?: number; completed?: number } {
  const time = (message.info as { time?: { created?: unknown; completed?: unknown } } | undefined)?.time
  return {
    created: typeof time?.created === "number" ? time.created : undefined,
    completed: typeof time?.completed === "number" ? time.completed : undefined,
  }
}

// Messages after the watermark. If the watermark message was removed (revert / compaction), fall
// back to everything created after the watermark message's own time (not the extraction's finish
// time: messages that arrived during the extraction must not be skipped).
export function sliceNewMessages(
  messages: readonly ChatMessage[],
  state: SessionExtractionState | undefined,
): ChatMessage[] {
  if (!state) return [...messages]
  if (state.lastExtractedMessageID) {
    const idx = messages.findIndex((m) => m.info.id === state.lastExtractedMessageID)
    if (idx >= 0) return messages.slice(idx + 1)
  }
  const boundary = state.lastMessageAt ?? state.updatedAt
  return messages.filter((m) => (messageTime(m).created ?? 0) > boundary)
}

// Drops assistant messages still being generated from the end of the slice: extracting them would
// record a watermark past content that is not final yet, and the final answer would never be seen.
export function trimIncompleteTail(messages: readonly ChatMessage[]): ChatMessage[] {
  let end = messages.length
  while (end > 0) {
    const message = messages[end - 1]
    if (!message || roleOf(message) !== "assistant" || messageTime(message).completed !== undefined) break
    end -= 1
  }
  return messages.slice(0, end)
}

export function hasExtractableUserMessage(messages: readonly ChatMessage[]): boolean {
  return messages.some((message) => {
    if (roleOf(message) !== "user" || !Array.isArray(message.parts)) return false
    return message.parts.some((part) => {
      const p = part as { type?: string; text?: string; synthetic?: boolean }
      return p.type === "text" && typeof p.text === "string" && p.text.trim().length > 0 && !p.synthetic
    })
  })
}

export function buildConversationForExtraction(messages: readonly ChatMessage[], maxChars: number): string {
  const lines: string[] = []
  for (const message of messages) {
    const role = roleOf(message)
    if (!role || !Array.isArray(message.parts)) continue
    for (const part of message.parts) {
      const p = part as {
        type?: string
        text?: string
        synthetic?: boolean
        tool?: string
        state?: { status?: string; output?: string }
      }
      if (p.type === "text" && typeof p.text === "string" && !p.synthetic) {
        lines.push(`### ${role === "user" ? "User" : "Assistant"}\n${p.text}`)
      } else if (p.type === "tool" && p.tool && p.state?.status === "completed" && typeof p.state.output === "string") {
        const out = p.state.output.length > 300 ? `${p.state.output.slice(0, 300)}…` : p.state.output
        lines.push(`_[tool ${p.tool}: ${out}]_`)
      }
    }
  }
  let text = lines.join("\n\n")
  // Keep the TAIL (newest turns carry the new facts worth extracting), drop the oldest head.
  if (text.length > maxChars) {
    text = `…[older turns truncated]\n\n${text.slice(-maxChars)}`
  }
  return text
}

export type ExtractionCoordinatorDeps = {
  store: MemoryStore
  config: MemoryConfig
  host: MemoryHost | undefined
  log: Logger
  now?: () => number
  state?: ExtractionStateStore
  lock?: MaintenanceLock
}

type Snapshot = {
  fresh: ChatMessage[]
  last: ChatMessage
  lastMessageAt: number | undefined
}

export class ExtractionCoordinator {
  readonly state: ExtractionStateStore
  readonly autodream: AutoDream | undefined
  private readonly lock: MaintenanceLock
  private readonly now: () => number
  private readonly timers = new Map<string, ReturnType<typeof setTimeout>>()
  private readonly busy = new Set<string>()
  private readonly inFlight = new Set<string>()
  private readonly savedByMainAgent = new Set<string>()
  private queue: Promise<void> = Promise.resolve()
  private initialized = false
  private disposed = false

  constructor(private readonly deps: ExtractionCoordinatorDeps) {
    this.now = deps.now ?? Date.now
    this.state = deps.state ?? new ExtractionStateStore(deps.store.stateDir, this.now)
    this.lock = deps.lock ?? new MaintenanceLock(this.state.lockPath, this.now)
    this.autodream = deps.host
      ? new AutoDream({ store: deps.store, config: deps.config, host: deps.host, state: this.state, log: deps.log, now: this.now, lock: this.lock })
      : undefined
  }

  get enabled(): boolean {
    return this.deps.config.extract.enabled && this.deps.host !== undefined
  }

  onEvent(event: V2Event): void {
    switch (event.type) {
      case "session.idle":
        this.onSessionIdle(event.data.sessionID)
        break
      // 2.0.16 marks the end of a turn with `session.execution.*`; `session.idle` fires later (or
      // not at all for short-lived clients), so both schedule the debounced extraction.
      case "session.execution.succeeded":
      case "session.execution.failed":
      case "session.execution.interrupted":
        this.onSessionIdle(event.data.sessionID)
        break
      case "session.execution.started":
        this.onSessionStatus(event.data.sessionID, "busy")
        break
      case "session.deleted":
        this.onSessionDeleted(event.data.sessionID)
        break
      case "session.status":
        this.onSessionStatus(event.data.sessionID, event.data.status.type)
        break
      default:
        break
    }
  }

  onSessionIdle(sessionID: string): void {
    if (!this.enabled || this.disposed || !sessionID) return
    this.busy.delete(sessionID)
    this.clearTimer(sessionID)
    const timer = setTimeout(() => {
      this.timers.delete(sessionID)
      void this.enqueue(sessionID)
    }, this.deps.config.extract.debounceMs)
    timer.unref?.()
    this.timers.set(sessionID, timer)
  }

  // A session that starts a new turn (busy / retry) cancels its pending debounce: the previous
  // turn is extracted together with the new one once the session is idle again.
  onSessionStatus(sessionID: string, status: string): void {
    if (!sessionID) return
    if (status === "idle") {
      this.busy.delete(sessionID)
      return
    }
    this.busy.add(sessionID)
    this.clearTimer(sessionID)
  }

  onSessionDeleted(sessionID: string): void {
    this.clearTimer(sessionID)
    this.busy.delete(sessionID)
    this.savedByMainAgent.delete(sessionID)
  }

  // A memory_save by the main agent marks the session so the next extraction round is skipped (the
  // agent already curated its memory).
  recordSave(sessionID: string | undefined, _fileName: string): string[] | undefined {
    if (!sessionID) return undefined
    this.savedByMainAgent.add(sessionID)
    return undefined
  }

  // Resolves once every queued extraction has finished (tests, dispose).
  idle(): Promise<void> {
    return this.queue
  }

  // One-time start-up maintenance. OpenCode 2.0.16 does not expose `session.list` to plugins, so
  // the V1 catch-up of sessions abandoned by a dead process cannot be reproduced; extraction now
  // relies on the live `session.idle` event (see README limitations).
  async initialize(): Promise<void> {
    if (this.initialized || !this.enabled) return
    this.initialized = true
    const { store } = this.deps

    this.warnLegacyShellHook()
    migrateLegacyAutodreamState(this.state, `${store.claudeConfigDir}/opencode-memory`, [
      store.gitRoot ?? store.memoryRoot,
      store.memoryRoot,
      store.canonicalRoot,
    ])
  }

  dispose(): void {
    this.disposed = true
    for (const timer of this.timers.values()) clearTimeout(timer)
    this.timers.clear()
    this.busy.clear()
  }

  private clearTimer(sessionID: string): void {
    const existing = this.timers.get(sessionID)
    if (existing) clearTimeout(existing)
    this.timers.delete(sessionID)
  }

  private warnLegacyShellHook(): void {
    let hooks: string[]
    try {
      hooks = findLegacyShellHooks(this.deps.config.homeDir)
    } catch {
      return
    }
    if (hooks.length === 0) return
    this.deps.log(
      "warn",
      "v1 opencode-memory shell hook is still installed; v2 extracts in-process, so run `opencode-memory uninstall` (or delete the marked block) to avoid a second, competing extraction",
      {
        files: hooks,
      },
    )
  }

  private enqueue(sessionID: string): Promise<void> {
    const run = this.queue.then(() => this.runIncremental(sessionID)).catch(() => {})
    this.queue = run
    return run
  }

  private snapshot(
    messages: readonly ChatMessage[],
    previous: SessionExtractionState | undefined,
  ): Snapshot | undefined {
    const fresh = trimIncompleteTail(sliceNewMessages(messages, previous))
    const last = fresh[fresh.length - 1]
    if (!last || !hasExtractableUserMessage(fresh)) return undefined
    return { fresh, last, lastMessageAt: messageTime(last).created }
  }

  // Persists the watermark unless another process already moved it past this snapshot. Runs inside
  // the state lock, so the decision is made against the current on-disk state.
  private advance(sessionID: string, snapshot: Snapshot, extra: Partial<SessionExtractionState> = {}): boolean {
    let advanced = false
    this.state.update((data) => {
      const current = data.sessions[sessionID]
      if (
        current?.lastMessageAt !== undefined &&
        snapshot.lastMessageAt !== undefined &&
        current.lastMessageAt > snapshot.lastMessageAt
      ) {
        return
      }
      advanced = true
      data.sessions[sessionID] = {
        lastExtractedMessageID: snapshot.last.info.id,
        ...(snapshot.lastMessageAt !== undefined ? { lastMessageAt: snapshot.lastMessageAt } : {}),
        updatedAt: this.now(),
        failures: 0,
        ...extra,
      }
      AutoDream.noteSession(data.autodream, sessionID)
    })
    return advanced
  }

  private async runIncremental(sessionID: string): Promise<void> {
    const { host, config, store, log } = this.deps
    if (!host || this.disposed || this.inFlight.has(sessionID)) return
    // Re-check at dequeue time: the debounce may have fired just before the session went busy, or
    // the session may have started a new turn while this job waited in the queue.
    if (this.busy.has(sessionID)) return
    this.inFlight.add(sessionID)

    try {
      const messages = await withDeadline("session.context", SDK_READ_TIMEOUT_MS, (signal) =>
        host.fetchMessages(sessionID, signal),
      )
      if (this.busy.has(sessionID)) return
      let snapshot = this.snapshot(messages, this.state.getSession(sessionID))
      if (!snapshot) return

      if (this.savedByMainAgent.delete(sessionID)) {
        if (this.advance(sessionID, snapshot)) await this.autodream?.maybeRun(sessionID)
        return
      }

      if (
        buildConversationForExtraction(snapshot.fresh, config.extract.maxConversationChars).trim().length <
        MIN_CONVERSATION_CHARS
      ) {
        this.advance(sessionID, snapshot)
        return
      }

      // Cross-process serialisation (#30): another OpenCode process on this project is extracting or
      // consolidating right now. Skip without touching the watermark; the next idle retries.
      if (!this.lock.tryAcquire()) {
        log("info", "Memory extraction skipped: another process holds the maintenance lock", { sessionID })
        return
      }

      let extracted = false
      try {
        // Recompute against the state as it is *now*: while we waited for the lock another process
        // may have extracted part (or all) of this slice.
        const previous = this.state.getSession(sessionID)
        snapshot = this.snapshot(messages, previous)
        if (!snapshot) return
        const conversation = buildConversationForExtraction(snapshot.fresh, config.extract.maxConversationChars)
        if (conversation.trim().length < MIN_CONVERSATION_CHARS) {
          this.advance(sessionID, snapshot)
          return
        }

        try {
          const prompt = buildExtractionPrompt(store.manifest(), conversation)
          const text = await withDeadline("memory extraction", config.extract.timeoutMs, (signal) =>
            host.generateText(prompt, signal),
          )
          const plan = parseExtractionPlan(text)
          let saved = 0
          for (const draft of plan.memories) {
            try {
              store.save({
                fileName: draft.file_name,
                name: draft.name,
                description: draft.description,
                type: draft.type,
                content: draft.content,
              })
              saved += 1
            } catch (error) {
              log("warn", "Extracted memory could not be saved", { file: draft.file_name, error: getErrorMessage(error) })
            }
          }
          log("info", "Memory extraction completed", { sessionID, saved })
        } catch (error) {
          const failures = (previous?.failures ?? 0) + 1
          log("error", "Memory extraction failed", { error: getErrorMessage(error), sessionID, failures })
          if (failures >= MAX_EXTRACTION_FAILURES) {
            // Do not stay stuck on a message that keeps failing: move on and reset the counter.
            this.advance(sessionID, snapshot)
          } else {
            this.state.update((data) => {
              data.sessions[sessionID] = {
                ...(data.sessions[sessionID] ?? previous ?? { updatedAt: 0 }),
                failures,
                attemptedAt: this.now(),
              }
            })
          }
          return
        }
        // The watermark is committed while the lock is still held, so no other process can extract
        // between this write and the watermark that records it.
        extracted = this.advance(sessionID, snapshot)
      } finally {
        this.lock.release()
      }

      if (extracted) await this.autodream?.maybeRun(sessionID)
    } catch (error) {
      const detail = error instanceof TimeoutError ? error.message : getErrorMessage(error)
      log("error", "Memory extraction failed", { error: detail, sessionID })
    } finally {
      this.inFlight.delete(sessionID)
    }
  }
}
