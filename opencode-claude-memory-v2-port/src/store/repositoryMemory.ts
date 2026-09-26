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
import { lstatSync, mkdirSync, readdirSync, realpathSync, rmdirSync, statSync, symlinkSync, unlinkSync } from "node:fs"
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

function errorCode(error: unknown): string | undefined {
  return (error as { code?: string } | undefined)?.code
}

function canonical(path: string): string | undefined {
  try {
    return realpathSync.native(path)
  } catch {
    return undefined
  }
}

function existsNoFollow(path: string): boolean {
  try {
    lstatSync(path)
    return true
  } catch {
    return false
  }
}

function isInside(path: string, root: string): boolean {
  return path === root || path.startsWith(root + sep)
}

// Resolves `<canonicalRoot>/<dir>`, refusing anything that escapes the canonical root — lexically and
// through the filesystem. A symlinked parent inside the repo (`<repo>/.claude -> /elsewhere`) would
// otherwise let memory be created outside the project.
export function repositoryMemoryDir(canonicalRoot: string, dir: string): string | undefined {
  if (!dir || isAbsolute(dir)) return undefined
  const root = resolve(canonicalRoot)
  const prefix = root.endsWith(sep) ? root : root + sep
  const target = resolve(root, dir)
  if (target !== root && !target.startsWith(prefix)) return undefined

  const realRoot = canonical(root)
  if (realRoot !== undefined) {
    let probe = target
    while (probe !== root && !existsNoFollow(probe)) probe = dirname(probe)
    const realProbe = canonical(probe)
    if (realProbe === undefined || !isInside(realProbe, realRoot)) return undefined
  }
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

// Conservative: a missing path is empty, but an unreadable one counts as non-empty so it is never
// handed to a destructive operation.
function isNonEmptyDir(path: string): boolean {
  try {
    if (!statSync(path).isDirectory()) return false
    return readdirSync(path).length > 0
  } catch (error) {
    return errorCode(error) !== "ENOENT"
  }
}

function sameDir(a: string, b: string): boolean {
  return canonical(a) !== undefined && canonical(a) === canonical(b)
}

function quote(path: string): string {
  return JSON.stringify(path)
}

export function conflictMessage(centralDir: string, repoDir: string): string {
  return [
    "opencode-claude-memory: repository memory conflict.",
    `  Central memory (non-empty): ${quote(centralDir)}`,
    `  Repository directory (non-empty): ${quote(repoDir)}`,
    "Both hold memories but are not linked. Refusing to load so the two copies cannot silently diverge.",
    "Merge or withdraw one side by hand, then replace the central directory with a symlink:",
    `  rm -rf ${quote(centralDir)} && ln -s ${quote(repoDir)} ${quote(centralDir)}`,
  ].join("\n")
}

export function noticeMessage(centralDir: string, repoDir: string, centralIsSymlink = false): string {
  const lines = [
    "opencode-claude-memory: memories are stored centrally, not in this repository.",
    `  Central memory (non-empty): ${quote(centralDir)}`,
    `  Repository directory (missing): ${quote(repoDir)}`,
    "Existing memories keep working from the central path. To move them into the repository:",
    `  mkdir -p "$(dirname ${quote(repoDir)})"`,
    `  mv ${quote(centralDir)} ${quote(repoDir)}`,
    `  ln -s ${quote(repoDir)} ${quote(centralDir)}`,
    "Then restart OpenCode.",
  ]
  if (centralIsSymlink) {
    lines.splice(
      4,
      0,
      "The central path is itself a symlink: move its target directory, not the link, and remove the link before creating the new one.",
    )
  }
  return lines.join("\n")
}

function unsupportedMessage(centralDir: string, repoDir: string, error: unknown): string {
  return [
    "opencode-claude-memory: could not link the repository memory directory; continuing from the central path.",
    `  Central memory: ${quote(centralDir)}`,
    `  Repository directory: ${quote(repoDir)}`,
    `  Reason: ${getErrorMessage(error)}`,
    "Set repositoryMemory.enabled=false to silence this, or link the directories manually.",
  ].join("\n")
}

function ensureDir(path: string): void {
  try {
    mkdirSync(path, { recursive: true })
  } catch {
    // verified by the caller; the MemoryStore constructor surfaces a real failure
  }
}

// Points `centralDir` at `repoDir` after removing an empty directory or an existing symlink at the
// central path. Removal is atomic (`rmdirSync` only succeeds on an empty directory), so a memory
// written by another process in the meantime turns into a conflict instead of being deleted.
function linkCentral(centralDir: string, repoDir: string): ReconcileResult {
  const existing = lstatOrNull(centralDir)
  if (existing && !existing.isSymbolicLink() && !existing.isDirectory()) {
    return {
      status: "unsupported",
      message: unsupportedMessage(
        centralDir,
        repoDir,
        new Error("a non-directory entry occupies the central memory path"),
      ),
    }
  }
  // A symlink pointing at a regular file is an unexpected shape: never repoint it silently.
  if (existing?.isSymbolicLink() && !sameDir(centralDir, repoDir)) {
    try {
      if (!statSync(centralDir).isDirectory()) {
        return {
          status: "unsupported",
          message: unsupportedMessage(
            centralDir,
            repoDir,
            new Error("the central path is a symlink to a non-directory"),
          ),
        }
      }
    } catch {
      // dangling target: safe to relink
    }
  }
  if (!isDirectory(repoDir)) {
    return {
      status: "unsupported",
      message: unsupportedMessage(
        centralDir,
        repoDir,
        new Error("the repository memory directory could not be created"),
      ),
    }
  }

  try {
    ensureDir(dirname(centralDir))
    if (existing?.isSymbolicLink()) {
      unlinkSync(centralDir)
    } else if (existing?.isDirectory()) {
      try {
        rmdirSync(centralDir)
      } catch {
        return { status: "conflict", message: conflictMessage(centralDir, repoDir) }
      }
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

  // Repository directory does not exist yet. Only the central side holds memories: report and let the
  // user migrate, never move automatically.
  if (isNonEmptyDir(input.centralDir)) {
    return { status: "notice", message: noticeMessage(input.centralDir, repoDir, central?.isSymbolicLink() === true) }
  }
  ensureDir(repoDir)
  return linkCentral(input.centralDir, repoDir)
}
