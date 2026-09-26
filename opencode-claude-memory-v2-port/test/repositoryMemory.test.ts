import { afterEach, describe, expect, test } from "bun:test"
import {
  chmodSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readlinkSync,
  symlinkSync,
  writeFileSync,
} from "node:fs"
import { dirname, join } from "node:path"
import { MemoryOptionsSchema } from "../src/config.js"
import { sanitizePath } from "../src/store/paths.js"
import { reconcileRepositoryMemory, repositoryMemoryDir } from "../src/store/repositoryMemory.js"
import { cleanupTempDirs, makeHarness, runTool, tempDir, tempGitRepo } from "./helpers/index.js"

afterEach(cleanupTempDirs)

function write(dir: string, name: string, content = "x"): string {
  mkdirSync(dir, { recursive: true })
  const path = join(dir, name)
  writeFileSync(path, content)
  return path
}

describe("repositoryMemoryDir", () => {
  test("resolves a relative dir inside the canonical root", () => {
    expect(repositoryMemoryDir("/repo", ".claude/memory")).toBe("/repo/.claude/memory")
  })

  test("rejects absolute and escaping dirs", () => {
    expect(repositoryMemoryDir("/repo", "/etc")).toBeUndefined()
    expect(repositoryMemoryDir("/repo", "../outside")).toBeUndefined()
    expect(repositoryMemoryDir("/repo", "a/../../b")).toBeUndefined()
  })
})

describe("reconcileRepositoryMemory", () => {
  test("disabled is a no-op", () => {
    const central = join(tempDir(), "memory")
    const result = reconcileRepositoryMemory({
      enabled: false,
      dir: ".claude/memory",
      canonicalRoot: "/repo",
      centralDir: central,
    })
    expect(result.status).toBe("disabled")
    expect(existsSync(central)).toBe(false)
  })

  test("creates the repo dir and links the central path when neither exists", () => {
    const base = tempDir()
    const repo = join(base, "repo")
    const central = join(base, "claude", "memory")
    const result = reconcileRepositoryMemory({
      enabled: true,
      dir: ".claude/memory",
      canonicalRoot: repo,
      centralDir: central,
    })
    expect(result.status).toBe("linked")
    expect(lstatSync(central).isSymbolicLink()).toBe(true)
    expect(readlinkSync(central)).toBe(join(repo, ".claude/memory"))
    expect(existsSync(join(repo, ".claude/memory"))).toBe(true)
  })

  test("replaces an empty central dir with a symlink", () => {
    const base = tempDir()
    const central = join(base, "claude", "memory")
    mkdirSync(central, { recursive: true })
    const repo = join(base, "repo")
    expect(
      reconcileRepositoryMemory({ enabled: true, dir: ".claude/memory", canonicalRoot: repo, centralDir: central })
        .status,
    ).toBe("linked")
    expect(lstatSync(central).isSymbolicLink()).toBe(true)
  })

  test("is ok when central already links to the repo", () => {
    const base = tempDir()
    const repo = join(base, "repo")
    const central = join(base, "claude", "memory")
    reconcileRepositoryMemory({ enabled: true, dir: ".claude/memory", canonicalRoot: repo, centralDir: central })
    expect(
      reconcileRepositoryMemory({ enabled: true, dir: ".claude/memory", canonicalRoot: repo, centralDir: central })
        .status,
    ).toBe("ok")
  })

  test("conflicts when both sides hold memories and are not linked", () => {
    const base = tempDir()
    const repo = join(base, "repo")
    const repoDir = join(repo, ".claude/memory")
    const central = join(base, "claude", "memory")
    write(repoDir, "repo_memory.md", "repo")
    write(central, "central_memory.md", "central")
    const result = reconcileRepositoryMemory({
      enabled: true,
      dir: ".claude/memory",
      canonicalRoot: repo,
      centralDir: central,
    })
    expect(result.status).toBe("conflict")
    if (result.status === "conflict") {
      expect(result.message).toContain("conflict")
      expect(result.message).toContain(central)
      expect(result.message).toContain(repoDir)
    }
    // Nothing was mutated.
    expect(readFileSync(join(central, "central_memory.md"), "utf-8")).toBe("central")
    expect(readFileSync(join(repoDir, "repo_memory.md"), "utf-8")).toBe("repo")
  })

  test("notifies (without mutating) when only the central side has memories", () => {
    const base = tempDir()
    const repo = join(base, "repo")
    const central = join(base, "claude", "memory")
    write(central, "existing.md", "central")
    const result = reconcileRepositoryMemory({
      enabled: true,
      dir: ".claude/memory",
      canonicalRoot: repo,
      centralDir: central,
    })
    expect(result.status).toBe("notice")
    if (result.status === "notice") {
      expect(result.message).toContain("mv")
      expect(result.message).toContain("ln -s")
    }
    expect(lstatSync(central).isSymbolicLink()).toBe(false)
    expect(readFileSync(join(central, "existing.md"), "utf-8")).toBe("central")
    expect(existsSync(join(repo, ".claude/memory"))).toBe(false)
  })

  test("invalid dir is reported as unsupported", () => {
    const central = join(tempDir(), "memory")
    const result = reconcileRepositoryMemory({
      enabled: true,
      dir: "/absolute",
      canonicalRoot: "/repo",
      centralDir: central,
    })
    expect(result.status).toBe("unsupported")
  })

  test("a failed symlink falls back without crashing and keeps the central dir", () => {
    const base = tempDir()
    const readonlyParent = join(base, "ro")
    mkdirSync(readonlyParent, { recursive: true })
    chmodSync(readonlyParent, 0o500)
    try {
      const result = reconcileRepositoryMemory({
        enabled: true,
        dir: ".claude/memory",
        canonicalRoot: join(base, "repo"),
        centralDir: join(readonlyParent, "memory"),
      })
      expect(result.status).toBe("unsupported")
      if (result.status === "unsupported") expect(result.message).toContain("could not link")
    } finally {
      chmodSync(readonlyParent, 0o700)
    }
  })
})

describe("repository memory through the plugin", () => {
  test("is enabled by default: central becomes a symlink and writes land in the repo", async () => {
    const h = await makeHarness()
    expect(lstatSync(h.store.memoryDir).isSymbolicLink()).toBe(true)
    const repoDir = join(h.worktree, ".claude", "memory")
    expect(readlinkSync(h.store.memoryDir)).toBe(repoDir)

    await runTool(h.tools, "memory_save", {
      file_name: "repo_note",
      name: "Repo Note",
      description: "in the repo",
      type: "project",
      content: "stored in the repository",
    })
    expect(existsSync(join(repoDir, "repo_note.md"))).toBe(true)
    expect(existsSync(join(repoDir, "MEMORY.md"))).toBe(true)
  })

  test("can be disabled: central stays a real directory and no repo dir is created", async () => {
    const h = await makeHarness({ options: { repositoryMemory: { enabled: false } } })
    expect(lstatSync(h.store.memoryDir).isSymbolicLink()).toBe(false)
    expect(existsSync(join(h.worktree, ".claude", "memory"))).toBe(false)
  })

  test("existing central memories with no repo dir produce a synthetic notice with commands", async () => {
    const worktree = tempGitRepo()
    const claudeConfigDir = tempDir("ocm-claude-")
    const central = join(claudeConfigDir, "projects", sanitizePath(worktree), "memory")
    write(central, "existing.md", "central")

    const h = await makeHarness({ worktree, projectCanonical: worktree, claudeConfigDir })
    await h.emit({
      type: "session.execution.started",
      data: { sessionID: "ses_notice" },
      location: { directory: worktree },
    } as never)
    await new Promise((resolve) => setTimeout(resolve, 0))

    expect(h.syntheticCalls).toHaveLength(1)
    expect(h.syntheticCalls[0]?.sessionID).toBe("ses_notice")
    expect(h.syntheticCalls[0]?.text).toContain("not in this repository")
    expect(h.syntheticCalls[0]?.text).toContain("ln -s")

    // Only once per session.
    await h.emit({
      type: "session.execution.started",
      data: { sessionID: "ses_notice" },
      location: { directory: worktree },
    } as never)
    await new Promise((resolve) => setTimeout(resolve, 0))
    expect(h.syntheticCalls).toHaveLength(1)
  })

  test("the notice is scoped to this location and does not leak to other sessions", async () => {
    const worktree = tempGitRepo()
    const claudeConfigDir = tempDir("ocm-claude-")
    write(join(claudeConfigDir, "projects", sanitizePath(worktree), "memory"), "existing.md", "central")
    const h = await makeHarness({ worktree, projectCanonical: worktree, claudeConfigDir })

    // No event location: the plugin resolves the session's own location, which is elsewhere.
    h.setSessionLocation("ses_other", "/somewhere/else")
    await h.emit({ type: "session.execution.started", data: { sessionID: "ses_other" } } as never)
    await new Promise((resolve) => setTimeout(resolve, 0))
    expect(h.syntheticCalls).toHaveLength(0)

    // A session in this project is notified.
    await h.emit({ type: "session.execution.started", data: { sessionID: "ses_here" } } as never)
    await new Promise((resolve) => setTimeout(resolve, 0))
    expect(h.syntheticCalls.map((call) => call.sessionID)).toEqual(["ses_here"])
  })

  test("a conflict makes setup fail with a user-visible error", async () => {
    const worktree = tempGitRepo()
    const claudeConfigDir = tempDir("ocm-claude-")
    write(join(claudeConfigDir, "projects", sanitizePath(worktree), "memory"), "central.md", "central")
    write(join(worktree, ".claude", "memory"), "repo.md", "repo")

    await expect(makeHarness({ worktree, projectCanonical: worktree, claudeConfigDir })).rejects.toThrow(/conflict/)
  })
})

describe("repositoryMemory hardening (review follow-ups)", () => {
  test("repositoryMemoryDir handles the filesystem root", () => {
    expect(repositoryMemoryDir("/", ".claude/memory")).toBe("/.claude/memory")
  })

  test("repositoryMemoryDir refuses a parent symlink that escapes the repo", () => {
    const base = tempDir()
    const repo = join(base, "repo")
    const outside = join(base, "outside")
    mkdirSync(repo, { recursive: true })
    mkdirSync(outside, { recursive: true })
    symlinkSync(outside, join(repo, ".claude"), "dir")
    expect(repositoryMemoryDir(repo, ".claude/memory")).toBeUndefined()
  })

  test("conflicts when central is a symlink to a different non-empty directory", () => {
    const base = tempDir()
    const repo = join(base, "repo")
    write(join(repo, ".claude/memory"), "repo.md", "repo")
    const elsewhere = join(base, "elsewhere")
    write(elsewhere, "other.md", "other")
    const central = join(base, "claude/memory")
    mkdirSync(dirname(central), { recursive: true })
    symlinkSync(elsewhere, central, "dir")

    expect(
      reconcileRepositoryMemory({ enabled: true, dir: ".claude/memory", canonicalRoot: repo, centralDir: central })
        .status,
    ).toBe("conflict")
    expect(existsSync(join(elsewhere, "other.md"))).toBe(true)
  })

  test("relinks a dangling foreign symlink safely", () => {
    const base = tempDir()
    const repo = join(base, "repo")
    write(join(repo, ".claude/memory"), "repo.md", "repo")
    const central = join(base, "claude/memory")
    mkdirSync(dirname(central), { recursive: true })
    symlinkSync(join(base, "does-not-exist"), central, "dir")

    const result = reconcileRepositoryMemory({
      enabled: true,
      dir: ".claude/memory",
      canonicalRoot: repo,
      centralDir: central,
    })
    expect(result.status).toBe("linked")
    expect(lstatSync(central).isSymbolicLink()).toBe(true)
    expect(readlinkSync(central)).toBe(join(repo, ".claude/memory"))
  })

  test("conflicts when the repo dir exists (even empty) and central is non-empty", () => {
    const base = tempDir()
    const repo = join(base, "repo")
    mkdirSync(join(repo, ".claude/memory"), { recursive: true })
    const central = join(base, "claude/memory")
    write(central, "central.md", "central")
    expect(
      reconcileRepositoryMemory({ enabled: true, dir: ".claude/memory", canonicalRoot: repo, centralDir: central })
        .status,
    ).toBe("conflict")
  })

  test("a regular file at the central path is never deleted", () => {
    const base = tempDir()
    const repo = join(base, "repo")
    write(join(repo, ".claude/memory"), "repo.md", "repo")
    const central = join(base, "claude/memory")
    mkdirSync(dirname(central), { recursive: true })
    writeFileSync(central, "not a directory")

    const result = reconcileRepositoryMemory({
      enabled: true,
      dir: ".claude/memory",
      canonicalRoot: repo,
      centralDir: central,
    })
    expect(result.status).toBe("unsupported")
    expect(readFileSync(central, "utf-8")).toBe("not a directory")
  })

  test("reconciliation never touches plugin-private state", async () => {
    const h = await makeHarness()
    expect(existsSync(join(h.claudeConfigDir, "opencode-memory"))).toBe(false)
  })
})

describe("repositoryMemory option schema", () => {
  test("defaults to enabled with .claude/memory", () => {
    expect(MemoryOptionsSchema.parse({}).repositoryMemory).toEqual({ enabled: true, dir: ".claude/memory" })
  })

  test("rejects absolute, escaping or empty dir values", () => {
    for (const dir of ["/abs", "a/../b", "", ".", "a//b"]) {
      expect(MemoryOptionsSchema.safeParse({ repositoryMemory: { dir } }).success).toBe(false)
    }
  })
})

describe("repositoryMemory round-2 follow-ups", () => {
  test("a central symlink to a regular file is left untouched", () => {
    const base = tempDir()
    const repo = join(base, "repo")
    write(join(repo, ".claude/memory"), "repo.md", "repo")
    const target = join(base, "some-file")
    writeFileSync(target, "file content")
    const central = join(base, "claude/memory")
    mkdirSync(dirname(central), { recursive: true })
    symlinkSync(target, central, "file")

    const result = reconcileRepositoryMemory({
      enabled: true,
      dir: ".claude/memory",
      canonicalRoot: repo,
      centralDir: central,
    })
    expect(result.status).toBe("unsupported")
    expect(lstatSync(central).isSymbolicLink()).toBe(true)
    expect(readFileSync(target, "utf-8")).toBe("file content")
  })

  test("a failed session lookup does not suppress a later notice", async () => {
    const worktree = tempGitRepo()
    const claudeConfigDir = tempDir("ocm-claude-")
    write(join(claudeConfigDir, "projects", sanitizePath(worktree), "memory"), "existing.md", "central")
    const h = await makeHarness({ worktree, projectCanonical: worktree, claudeConfigDir })

    h.setSessionGetFailure("ses_retry", true)
    await h.emit({ type: "session.execution.started", data: { sessionID: "ses_retry" } } as never)
    await new Promise((resolve) => setTimeout(resolve, 0))
    await new Promise((resolve) => setTimeout(resolve, 0))
    expect(h.syntheticCalls).toHaveLength(0)

    h.setSessionGetFailure("ses_retry", false)
    await h.emit({ type: "session.execution.started", data: { sessionID: "ses_retry" } } as never)
    await new Promise((resolve) => setTimeout(resolve, 0))
    await new Promise((resolve) => setTimeout(resolve, 0))
    expect(h.syntheticCalls.map((call) => call.sessionID)).toEqual(["ses_retry"])
  })
})
