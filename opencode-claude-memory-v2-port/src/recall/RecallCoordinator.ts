// Per-session recall state: which memories were already surfaced, whether the user asked to ignore
// memory, and the in-flight selector prefetch for the current turn. One instance per plugin instance.
//
// V2 folds the old messages/system transforms into one `session.hook("context")` call, so this
// coordinator both derives the turn and injects the memory system prompt in that single hook.
//
// Two kinds of state live here with different lifetimes: the turn cache (prefetch, turn id) is
// evicted after SESSION_STATE_TTL_MS so a long-running server does not leak; the user's
// "ignore memory" instruction is a session preference and lasts until `session.deleted` or an
// explicit resume. Eviction never clears it, and a session seen for the first time derives it
// from the conversation history so a restart does not silently bring memory back.
import type { MemoryConfig } from "../config.js"
import { deriveIgnoredFromContext, detectIgnoreMemory, detectResumeMemory } from "../hooks/ignore.js"
import { contextLastUser, contextRecentTools } from "../hooks/messages.js"
import { buildMemorySystemPrompt } from "../prompt/systemPrompt.js"
import type { ContextHookEvent, V2Event } from "../sdk.js"
import type { MemoryStore } from "../store/MemoryStore.js"
import { surfaceKey } from "../store/scan.js"
import type { Logger } from "../util/log.js"
import type { MemoryHost } from "../v2/host.js"
import { formatRecalledMemories, type RecalledMemory, recallSelectedMemories } from "./format.js"
import { selectRelevantMemoryFilenames } from "./selector.js"

export const SESSION_STATE_TTL_MS = 60 * 60 * 1000
export const SELECTOR_GRACE_MS = 60_000

type Prefetch = {
  turnID: string
  promise: Promise<RecalledMemory[]>
  consumed: boolean
}

type SessionState = {
  updatedAt: number
  ignored: boolean
  surfaced: Set<string>
  turnID?: string
  prefetch?: Prefetch
}

export type RecallCoordinatorDeps = {
  store: MemoryStore
  config: MemoryConfig
  host?: MemoryHost
  log: Logger
  now?: () => number
}

const TIMEOUT = Symbol("recall-timeout")

function isUsefulRecallQuery(query: string | undefined): query is string {
  const trimmed = query?.trim()
  if (!trimmed) return false
  if (/\s/.test(trimmed)) return true
  return /[㐀-鿿]/.test(trimmed) && trimmed.length >= 4
}

export class RecallCoordinator {
  private readonly sessions = new Map<string, SessionState>()
  private warnedMissingSessionID = false
  private readonly now: () => number

  constructor(private readonly deps: RecallCoordinatorDeps) {
    this.now = deps.now ?? Date.now
  }

  // `ctx.session.hook("context", ...)`: derive the turn state, await the selector prefetch (bounded)
  // and push the memory system prompt.
  async onContext(event: ContextHookEvent): Promise<void> {
    const sessionID = (event as { sessionID?: string }).sessionID
    if (!sessionID) {
      if (!this.warnedMissingSessionID) {
        this.warnedMissingSessionID = true
        this.deps.log("warn", "context hook received no sessionID; memory recall is disabled for this call")
      }
      this.inject(event, [], true)
      return
    }

    const now = this.now()
    this.evictStale(now)
    const state = this.sessions.get(sessionID) ?? {
      updatedAt: now,
      ignored: deriveIgnoredFromContext(event.messages),
      surfaced: new Set<string>(),
    }
    state.updatedAt = now

    const turn = contextLastUser(event.messages)
    const turnID = `${sessionID}:${turn.messageID ?? `${turn.messageIndex ?? -1}:${turn.query ?? ""}`}`
    if (state.turnID !== turnID) {
      if (detectIgnoreMemory(turn.query)) state.ignored = true
      else if (state.ignored && detectResumeMemory(turn.query)) state.ignored = false
      state.turnID = turnID
      state.prefetch = state.ignored ? undefined : this.startPrefetch(state, turnID, turn.query, event.messages)
    }
    this.sessions.set(sessionID, state)

    const recalled = state.ignored ? [] : await this.takeRecalled(state)
    for (const memory of recalled) state.surfaced.add(`${memory.name}|${memory.type}`)
    this.inject(event, recalled, !state.ignored)
  }

  isIgnored(sessionID: string | undefined): boolean {
    return sessionID !== undefined && this.sessions.get(sessionID)?.ignored === true
  }

  onEvent(event: V2Event): void {
    if (event.type === "session.deleted") {
      this.sessions.delete(event.data.sessionID)
      return
    }
    if (event.type === "session.compaction.ended") {
      // After a compaction the old recalled sections are gone from the conversation, so the next
      // turns may surface the same memories again.
      const state = this.sessions.get(event.data.sessionID)
      if (state) {
        state.surfaced.clear()
        state.turnID = undefined
        state.prefetch = undefined
      }
    }
  }

  dispose(): void {
    this.sessions.clear()
  }

  get trackedSessions(): number {
    return this.sessions.size
  }

  private inject(event: ContextHookEvent, recalled: RecalledMemory[], includeIndex: boolean): void {
    const text = buildMemorySystemPrompt(this.deps.store, formatRecalledMemories(recalled), { includeIndex })
    event.system.push({ type: "text", text })
  }

  private async takeRecalled(state: SessionState): Promise<RecalledMemory[]> {
    const prefetch = state.prefetch
    if (!prefetch || prefetch.consumed) return []
    const result = await this.race(prefetch.promise, this.deps.config.recall.waitMs)
    if (result === TIMEOUT) return []
    prefetch.consumed = true
    return result
  }

  private race(promise: Promise<RecalledMemory[]>, waitMs: number): Promise<RecalledMemory[] | typeof TIMEOUT> {
    let timer: ReturnType<typeof setTimeout> | undefined
    const timeout = new Promise<typeof TIMEOUT>((resolve) => {
      timer = setTimeout(() => resolve(TIMEOUT), waitMs)
    })
    return Promise.race([promise, timeout]).finally(() => {
      if (timer) clearTimeout(timer)
    })
  }

  // Drops the turn cache of sessions idle for longer than the TTL. An ignored session keeps its
  // entry (only the cache is cleared) so the instruction survives until the session is deleted.
  private evictStale(now: number): void {
    const cutoff = now - SESSION_STATE_TTL_MS
    for (const [id, state] of this.sessions) {
      if (state.updatedAt >= cutoff) continue
      if (state.ignored) {
        state.prefetch = undefined
        state.turnID = undefined
      } else {
        this.sessions.delete(id)
      }
    }
  }

  private startPrefetch(
    state: SessionState,
    turnID: string,
    query: string | undefined,
    messages: ContextHookEvent["messages"],
  ): Prefetch | undefined {
    const { config, store, host } = this.deps
    if (!config.recall.enabled || !host || !isUsefulRecallQuery(query)) return undefined

    const alreadySurfaced = state.surfaced
    const recentTools = contextRecentTools(messages)
    const headers = store.scan().filter((header) => !alreadySurfaced.has(surfaceKey(header)))
    if (headers.length === 0) return undefined

    const promise = selectRelevantMemoryFilenames({
      host,
      query,
      memories: headers,
      recentTools,
      timeoutMs: config.recall.timeoutMs,
      maxMemories: config.recall.maxMemories,
    })
      .then((selected) =>
        recallSelectedMemories(headers, selected, alreadySurfaced, { maxMemories: config.recall.maxMemories }),
      )
      .catch(() => [] as RecalledMemory[])

    return { turnID, promise, consumed: false }
  }
}
