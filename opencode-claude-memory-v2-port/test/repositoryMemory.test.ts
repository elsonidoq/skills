import { afterEach, describe, expect, test } from "bun:test"
import { chmodSync, existsSync, lstatSync, mkdirSync, readFileSync, readlinkSync, writeFileSync } from "node:fs"
import { join } from "node:path"
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

  test("a conflict makes setup fail with a user-visible error", async () => {
    const worktree = tempGitRepo()
    const claudeConfigDir = tempDir("ocm-claude-")
    write(join(claudeConfigDir, "projects", sanitizePath(worktree), "memory"), "central.md", "central")
    write(join(worktree, ".claude", "memory"), "repo.md", "repo")

    await expect(makeHarness({ worktree, projectCanonical: worktree, claudeConfigDir })).rejects.toThrow(/conflict/)
  })
})
