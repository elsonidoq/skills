// Auto-dream: periodic memory consolidation, gated on time since the last pass and on the number of
// sessions extracted since then, serialised by the same cross-process maintenance lock.
//
// V2 runs it as a single `ctx.generate.text` call returning a JSON plan (upserts + deletes) which the
// plugin applies through the MemoryStore.
import type { MemoryConfig } from "../config.js"
import type { MemoryStore } from "../store/MemoryStore.js"
import { getErrorMessage, type Logger } from "../util/log.js"
import { withDeadline } from "../util/timeout.js"
import type { MemoryHost } from "../v2/host.js"
import { MaintenanceLock } from "./lock.js"
import { parseAutodreamPlan } from "./plan.js"
import { buildAutodreamPrompt } from "./prompts.js"
import type { AutodreamState, ExtractionStateStore } from "./state.js"

export const AUTODREAM_DUMP_MAX_CHARS = 60_000

export type AutodreamGate = Pick<MemoryConfig["autodream"], "minHours" | "minSessions">

export function shouldRunAutodream(state: AutodreamState, gate: AutodreamGate, now: number): boolean {
  const hoursSince = (now - state.lastConsolidatedAt) / (60 * 60 * 1000)
  if (hoursSince < gate.minHours) return false
  return state.sessionsSince.length >= gate.minSessions
}

export function buildMemoryDump(
  store: Pick<MemoryStore, "list">,
  maxChars = AUTODREAM_DUMP_MAX_CHARS,
): string {
  const parts: string[] = []
  let total = 0
  for (const entry of store.list({ sort: "name" })) {
    const chunk = `### ${entry.filename}\n${entry.raw}`
    if (total + chunk.length > maxChars) break
    parts.push(chunk)
    total += chunk.length
  }
  return parts.join("\n\n")
}

export type AutoDreamDeps = {
  store: MemoryStore
  config: MemoryConfig
  host: MemoryHost
  state: ExtractionStateStore
  log: Logger
  now?: () => number
  lock?: MaintenanceLock
}

export class AutoDream {
  private readonly now: () => number
  private readonly lock: MaintenanceLock

  constructor(private readonly deps: AutoDreamDeps) {
    this.now = deps.now ?? Date.now
    this.lock = deps.lock ?? new MaintenanceLock(deps.state.lockPath, this.now)
  }

  // Called from the extraction coordinator's persisted update after a session was extracted.
  static noteSession(state: AutodreamState, sessionID: string): void {
    if (!state.sessionsSince.includes(sessionID)) state.sessionsSince.push(sessionID)
  }

  shouldRun(): boolean {
    const { config, state } = this.deps
    if (!config.autodream.enabled) return false
    return shouldRunAutodream(state.read().autodream, config.autodream, this.now())
  }

  // Runs a consolidation when the gate passes. Success resets the gate; failure leaves the gate
  // untouched so the next extracted session retries.
  async maybeRun(_parentSessionID: string): Promise<boolean> {
    if (!this.shouldRun()) return false
    if (!this.lock.tryAcquire()) {
      this.deps.log("info", "Auto-dream skipped: another process holds the maintenance lock")
      return false
    }

    const { host, config, store, state, log } = this.deps
    try {
      // Re-check under the lock: another process may have consolidated while we waited to acquire.
      if (!this.shouldRun()) return false
      const autodream = state.read().autodream
      log("info", "Auto-dream consolidation starting", {
        sessionsSince: autodream.sessionsSince.length,
        lastConsolidatedAt: autodream.lastConsolidatedAt,
      })

      const prompt = buildAutodreamPrompt(buildMemoryDump(store))
      const text = await withDeadline("auto-dream", config.autodream.timeoutMs, (signal) =>
        host.generateText(prompt, signal),
      )
      const plan = parseAutodreamPlan(text)

      let upserts = 0
      for (const draft of plan.upserts) {
        try {
          store.save({
            fileName: draft.file_name,
            name: draft.name,
            description: draft.description,
            type: draft.type,
            content: draft.content,
          })
          upserts += 1
        } catch (error) {
          log("warn", "Auto-dream memory could not be saved", { file: draft.file_name, error: getErrorMessage(error) })
        }
      }
      let deletes = 0
      for (const fileName of plan.deletes) {
        try {
          if (store.delete(fileName)) deletes += 1
        } catch (error) {
          log("warn", "Auto-dream memory could not be deleted", { file: fileName, error: getErrorMessage(error) })
        }
      }

      state.update((data) => {
        data.autodream.lastConsolidatedAt = this.now()
        data.autodream.sessionsSince = []
      })
      log("info", "Auto-dream consolidation completed", { upserts, deletes })
      return true
    } catch (error) {
      log("error", "Auto-dream consolidation failed", { error: getErrorMessage(error) })
      return false
    } finally {
      this.lock.release()
    }
  }
}
