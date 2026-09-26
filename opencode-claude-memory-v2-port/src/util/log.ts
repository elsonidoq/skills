// Best-effort logging. OpenCode 2.0.16's plugin context exposes no server-log API (ctx.app only
// carries name/version/channel), so the port writes to the process console instead. Warnings and
// errors are always emitted; info/debug only when OPENCODE_MEMORY_DEBUG is set to keep the UI quiet.
// Every call is synchronous and never throws.

export const LOG_SERVICE = "opencode-claude-memory"

export type LogLevel = "debug" | "info" | "warn" | "error"

export type Logger = (level: LogLevel, message: string, extra?: Record<string, unknown>) => void

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message
  if (error && typeof error === "object") {
    const message = (error as { message?: unknown }).message
    if (typeof message === "string") return message
  }
  return String(error)
}

function stringify(extra: Record<string, unknown> | undefined): string {
  if (!extra) return ""
  try {
    return ` ${JSON.stringify(extra)}`
  } catch {
    return ""
  }
}

export function createLogger(env: NodeJS.ProcessEnv = process.env): Logger {
  const verbose = typeof env.OPENCODE_MEMORY_DEBUG === "string" && env.OPENCODE_MEMORY_DEBUG !== ""
  return (level, message, extra) => {
    if (!verbose && (level === "debug" || level === "info")) return
    try {
      const line = `[${LOG_SERVICE}] ${level}: ${message}${stringify(extra)}`
      // OpenCode surfaces console output from plugins; stderr is the reliable channel.
      console.error(line)
    } catch {
      // best-effort
    }
  }
}
