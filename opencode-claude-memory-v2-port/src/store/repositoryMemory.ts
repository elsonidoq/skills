// Optional "memories live in the project repository" mode.
//
// When enabled (default), the plugin keeps the Claude Code-compatible central directory
// (<CLAUDE_CONFIG_DIR>/projects/<key>/memory) as a symlink to <canonical repo root>/<dir>, so the
// same Markdown files are versioned with the project while Claude Code still finds them at the
// central path. The reconcile runs once per location, before the MemoryStore is constructed.
//
// It never deletes or merges a non-empty central directory: either the two places are already linked,
// or the situation is reported to the user (a hard plugin-load error when both sides hold memories,
// or a notice with migration commands when only the central side does).
import { lstatSync, mkdirSync, readdirSync, realpathSync, rmSync, statSync, symlinkSync, unlinkSync } from "node:fs"
import { dirname, isAbsolute, resolve, sep } from "node:path"
import { getErrorMessage } from "../util/log.js"

export type RepositoryMemoryOptions = {
  enabled: boolean
  dir: string
}

export type ReconcileInput = RepositoryMemoryOptions & {
  canonicalRoot: string
  centralDir: string
}

export type ReconcileResult =
  | { status: "disabled" }
  | { status: "ok" }
  | { status: "linked" }
  | { status: "unsupported"; message: string }
  | { status: "notice"; message: string }
  | { status: "conflict"; message: string }

// Resolves `<canonicalRoot>/<dir>`, refusing anything that escapes the canonical root.
export function repositoryMemoryDir(canonicalRoot: string, dir: string): string | undefined {
  if (!dir || isAbsolute(dir)) return undefined
  const root = resolve(canonicalRoot)
  const target = resolve(root, dir)
  if (target !== root && !target.startsWith(root + sep)) return undefined
  return target
}

function lstatOrNull(path: string): ReturnType<typeof lstatSync> | null {
  try {
    return lstatSync(path)
  } catch {
    return null
  }
}

function isDirectory(path: string): boolean {
  try {
    return statSync(path).isDirectory()
  } catch {
    return false
  }
}

function isNonEmptyDir(path: string): boolean {
  try {
    if (!statSync(path).isDirectory()) return false
    return readdirSync(path).length > 0
  } catch {
    return false
  }
}

function sameDir(a: string, b: string): boolean {
  try {
    return realpathSync(a) === realpathSync(b)
  } catch {
    return false
  }
}

function quote(path: string): string {
  return JSON.stringify(path)
}

export function conflictMessage(centralDir: string, repoDir: string): string {
  return [
    "opencode-claude-memory: repository memory conflict.",
    `  Central memory (non-empty): ${centralDir}`,
    `  Repository directory (non-empty): ${repoDir}`,
    "Both hold memories but are not linked. Refusing to load so the two copies cannot silently diverge.",
    "Resolve it by hand — merge or delete one side, then link them:",
    `  rm -rf ${quote(centralDir)} && ln -s ${quote(repoDir)} ${quote(centralDir)}`,
  ].join("\n")
}

export function noticeMessage(centralDir: string, repoDir: string): string {
  return [
    "opencode-claude-memory: memories are stored centrally, not in this repository.",
    `  Central memory (non-empty): ${centralDir}`,
    `  Repository directory (missing): ${repoDir}`,
    "Existing memories keep working from the central path. To move them into the repository:",
    `  mkdir -p "$(dirname ${quote(repoDir)})"`,
    `  mv ${quote(centralDir)} ${quote(repoDir)}`,
    `  ln -s ${quote(repoDir)} ${quote(centralDir)}`,
    "Then restart OpenCode.",
  ].join("\n")
}

function unsupportedMessage(centralDir: string, repoDir: string, error: unknown): string {
  return [
    "opencode-claude-memory: could not link the repository memory directory; continuing from the central path.",
    `  Central memory: ${centralDir}`,
    `  Repository directory: ${repoDir}`,
    `  Reason: ${getErrorMessage(error)}`,
    "Set repositoryMemory.enabled=false to silence this, or link the directories manually.",
  ].join("\n")
}

function ensureDir(path: string): void {
  try {
    mkdirSync(path, { recursive: true })
  } catch {
    // best-effort; the MemoryStore constructor will surface a real failure
  }
}

// Removes an empty directory or a symlink at `centralDir` and points it at `repoDir`.
function linkCentral(centralDir: string, repoDir: string): ReconcileResult {
  try {
    ensureDir(dirname(centralDir))
    const existing = lstatOrNull(centralDir)
    if (existing) {
      if (existing.isSymbolicLink() || existing.isFile()) unlinkSync(centralDir)
      else rmSync(centralDir, { recursive: true, force: true })
    }
    symlinkSync(repoDir, centralDir, "dir")
    return { status: "linked" }
  } catch (error) {
    // Keep the central directory usable so memory is never lost.
    ensureDir(centralDir)
    return { status: "unsupported", message: unsupportedMessage(centralDir, repoDir, error) }
  }
}

export function reconcileRepositoryMemory(input: ReconcileInput): ReconcileResult {
  if (!input.enabled) return { status: "disabled" }

  const repoDir = repositoryMemoryDir(input.canonicalRoot, input.dir)
  if (!repoDir) {
    return {
      status: "unsupported",
      message: `opencode-claude-memory: invalid repositoryMemory.dir ${quote(input.dir)}; continuing from the central path.`,
    }
  }

  const central = lstatOrNull(input.centralDir)
  const repoExists = isDirectory(repoDir)

  if (repoExists) {
    if (central?.isSymbolicLink() && sameDir(input.centralDir, repoDir)) return { status: "ok" }
    if (isNonEmptyDir(input.centralDir)) {
      return { status: "conflict", message: conflictMessage(input.centralDir, repoDir) }
    }
    return linkCentral(input.centralDir, repoDir)
  }

  // Repository directory does not exist yet.
  if (isNonEmptyDir(input.centralDir)) {
    return { status: "notice", message: noticeMessage(input.centralDir, repoDir) }
  }
  ensureDir(repoDir)
  return linkCentral(input.centralDir, repoDir)
}
