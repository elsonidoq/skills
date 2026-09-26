import { afterEach, describe, expect, test } from "bun:test"
import { existsSync, readdirSync, readFileSync } from "node:fs"
import { join } from "node:path"
import { MemoryOptionsSchema } from "../src/config.js"
import plugin, { createMemoryPlugin, MemoryStore, PLUGIN_ID } from "../src/index.js"
import { ENTRYPOINT_NAME, sanitizePath } from "../src/store/paths.js"
import { cleanupTempDirs, makeHarness, runTool, tempDir, tempGitRepo, writeRawMemory } from "./helpers/index.js"

afterEach(cleanupTempDirs)

const DB_MEMORY = {
  file_name: "database_rules",
  name: "Database Test Rules",
  description: "Rules for database integration tests",
  type: "feedback",
  content: "Run integration tests against a real database, not mocks.",
}

describe("plugin module shape (OpenCode 2.0.16)", () => {
  test("default export is a V2 plugin definition with an id and setup", () => {
    expect(plugin.id).toBe(PLUGIN_ID)
    expect(typeof plugin.setup).toBe("function")
    expect("effect" in plugin).toBe(false)
    expect(typeof createMemoryPlugin).toBe("function")
    expect(MemoryOptionsSchema.safeParse({}).success).toBe(true)
    expect(typeof MemoryStore).toBe("function")
  })

  test("invalid plugin options fail during setup with the offending path", async () => {
    await expect(makeHarness({ options: { extract: { enabled: "yes" } } })).rejects.toThrow(/extract\.enabled/)
  })
})

describe("memory tools", () => {
  test("all five tools are registered", async () => {
    const h = await makeHarness()
    expect(Object.keys(h.tools).sort()).toEqual([
      "memory_delete",
      "memory_list",
      "memory_read",
      "memory_save",
      "memory_search",
    ])
  })

  test("save → list → search → read → delete with filesystem effects", async () => {
    const h = await makeHarness()
    const saved = await runTool(h.tools, "memory_save", DB_MEMORY)
    expect(saved.output).toContain("Memory saved to")
    expect(saved.title).toBe("feedback: Database Test Rules")

    const filePath = join(h.store.memoryDir, "database_rules.md")
    expect(existsSync(filePath)).toBe(true)
    const raw = readFileSync(filePath, "utf-8")
    expect(raw).toContain("name: Database Test Rules")
    expect(raw).toContain("type: feedback")
    expect(h.store.readIndex()).toContain("- [Database Test Rules](database_rules.md)")

    const listed = await runTool(h.tools, "memory_list", {})
    expect(listed.title).toBe("1 memory")
    expect(listed.output).toContain("Database Test Rules")

    const found = await runTool(h.tools, "memory_search", { query: "mocks" })
    expect(found.output).toContain("Database Test Rules")
    const missing = await runTool(h.tools, "memory_search", { query: "zzz-none" })
    expect(missing.output).toContain("No memories matching")

    const read = await runTool(h.tools, "memory_read", { file_name: "database_rules" })
    expect(read.output).toContain("Run integration tests against a real database")

    const deleted = await runTool(h.tools, "memory_delete", { file_name: "database_rules" })
    expect(deleted.output).toContain("deleted")
    expect(existsSync(filePath)).toBe(false)
    expect(h.store.readIndex()).not.toContain("database_rules.md")
  })

  test("memory_list is empty for a fresh project", async () => {
    const h = await makeHarness()
    expect((await runTool(h.tools, "memory_list", {})).output).toBe("No memories saved yet.")
  })
})

describe("Claude Code path compatibility", () => {
  test("memory lives under <CLAUDE_CONFIG_DIR>/projects/<sanitizePath(canonical)>/memory", async () => {
    const harness = await makeHarness()
    const expected = join(harness.claudeConfigDir, "projects", sanitizePath(harness.worktree), "memory")
    expect(harness.store.memoryDir).toBe(expected)
  })

  test("reads a hand-written Claude memory and writes back without migration", async () => {
    const harness = await makeHarness()
    const sentinel = "CLAUDE_MEMORY_COMPAT_TEST_84721"
    writeRawMemory(
      harness.store.memoryDir,
      "handwritten.md",
      `---\nname: Handwritten\ndescription: ${sentinel}\ntype: reference\n---\n\nBody ${sentinel}\n`,
    )

    const read = await runTool(harness.tools, "memory_read", { file_name: "handwritten" })
    expect(read.output).toContain(sentinel)
    expect(read.output).toContain("**Type:** reference")

    await runTool(harness.tools, "memory_save", {
      file_name: "written_by_opencode",
      name: "Written By OpenCode",
      description: "saved from the plugin",
      type: "project",
      content: "value",
    })

    const written = readFileSync(join(harness.store.memoryDir, "written_by_opencode.md"), "utf-8")
    expect(
      written.startsWith("---\nname: Written By OpenCode\ndescription: saved from the plugin\ntype: project\n---"),
    ).toBe(true)
    const index = readFileSync(join(harness.store.memoryDir, ENTRYPOINT_NAME), "utf-8")
    expect(index).toContain("- [Written By OpenCode](written_by_opencode.md)")
    // Only the two markdown files + the index exist: no database, embeddings or migration artifacts.
    expect(readdirSync(harness.store.memoryDir).sort()).toEqual([
      "MEMORY.md",
      "handwritten.md",
      "written_by_opencode.md",
    ])
  })
})

describe("worktree compatibility", () => {
  test("a worktree sharing the project canonical root uses the same memory directory", async () => {
    const main = tempGitRepo("ocm-main-")
    const worktree = tempDir("ocm-wt-")
    const claudeConfigDir = tempDir("ocm-claude-")

    const mainHarness = await makeHarness({ worktree: main, directory: main, projectCanonical: main, claudeConfigDir })
    const wtHarness = await makeHarness({
      worktree,
      directory: worktree,
      projectCanonical: main,
      claudeConfigDir,
    })

    // resolveMemoryRoot uses the canonical project root provided by OpenCode, and MemoryStore's
    // git-root resolution then produces the same sanitized key for both.
    expect(wtHarness.store.memoryDir).toBe(mainHarness.store.memoryDir)

    await runTool(mainHarness.tools, "memory_save", DB_MEMORY)
    const seenFromWorktree = await runTool(wtHarness.tools, "memory_list", {})
    expect(seenFromWorktree.output).toContain("Database Test Rules")
  })
})

describe("instance isolation", () => {
  test("two plugin instances in one process do not share recall or store state", async () => {
    const claudeConfigDir = tempDir("ocm-claude-")
    const a = await makeHarness({ claudeConfigDir })
    const b = await makeHarness({ claudeConfigDir })

    await runTool(a.tools, "memory_save", DB_MEMORY)
    expect((await runTool(b.tools, "memory_list", {})).output).toBe("No memories saved yet.")
    expect((await runTool(a.tools, "memory_list", {})).title).toBe("1 memory")
  })
})
