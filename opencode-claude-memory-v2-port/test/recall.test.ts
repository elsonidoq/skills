import { afterEach, describe, expect, test } from "bun:test"
import { AUTO_MEMORY_MARKER } from "../src/prompt/systemPrompt.js"
import { cleanupTempDirs, contextUser, makeHarness, runContextHook, runTool } from "./helpers/index.js"

afterEach(cleanupTempDirs)

const DB_MEMORY = {
  file_name: "database_rules",
  name: "Database Test Rules",
  description: "Rules for database integration tests",
  type: "feedback",
  content: "Run integration tests against a real database, not mocks.",
}

function selectOnly(fileName: string): string {
  return `{"selected_memories":["${fileName}"]}`
}

describe("automatic memory context injection", () => {
  test("a normal turn receives the memory system prompt and MEMORY.md index", async () => {
    const h = await makeHarness({ options: { recall: { waitMs: 50 } } })
    await runTool(h.tools, "memory_save", { ...DB_MEMORY, name: "Visible Memory" })

    const { system } = await runContextHook(h, [contextUser("What do you remember about visible context?", "m1")])
    expect(system.startsWith(AUTO_MEMORY_MARKER)).toBe(true)
    expect(system).toContain("## MEMORY.md")
    expect(system).toContain("Visible Memory")
  })

  test("a relevant memory is selected and injected without a manual memory_search", async () => {
    const h = await makeHarness({
      options: { recall: { waitMs: 200 } },
      generate: () => selectOnly("database_rules.md"),
    })
    await runTool(h.tools, "memory_save", DB_MEMORY)

    const { system } = await runContextHook(h, [contextUser("How should we test database changes?", "m1")])
    expect(system).toContain("## Recalled Memories")
    expect(system).toContain("Database Test Rules")
    expect(system).toContain("Run integration tests against a real database, not mocks.")
    expect(h.host.prompts[0]).toContain("Query: How should we test database changes?")
  })

  test("trivial queries do not call the selector", async () => {
    const h = await makeHarness({ options: { recall: { waitMs: 50 } }, generate: () => selectOnly("database_rules.md") })
    await runTool(h.tools, "memory_save", DB_MEMORY)
    const { system } = await runContextHook(h, [contextUser("hi", "m1")])
    expect(system).toContain("## MEMORY.md")
    expect(system).not.toContain("## Recalled Memories")
    expect(h.host.prompts).toHaveLength(0)
  })

  test("a slow selector is not awaited beyond recall.waitMs and is injected on the next call", async () => {
    let release!: () => void
    const gate = new Promise<void>((resolve) => {
      release = resolve
    })
    const h = await makeHarness({
      options: { recall: { waitMs: 0 } },
      generate: async () => {
        await gate
        return selectOnly("database_rules.md")
      },
    })
    await runTool(h.tools, "memory_save", DB_MEMORY)
    const messages = [contextUser("How should we test database changes?", "m1")]

    const first = await runContextHook(h, messages)
    expect(first.system).toContain("## MEMORY.md")
    expect(first.system).not.toContain("## Recalled Memories")

    release()
    await new Promise((resolve) => setTimeout(resolve, 5))
    const second = await runContextHook(h, messages)
    expect(second.system).toContain("## Recalled Memories")
    expect(second.system).toContain("Database Test Rules")
    // Once consumed, it is not injected again for the same turn.
    const third = await runContextHook(h, messages)
    expect(third.system).not.toContain("## Recalled Memories")
  })

  test("ignore memory suppresses the index for the rest of the session until resumed", async () => {
    const h = await makeHarness({ options: { recall: { waitMs: 50 } }, generate: () => selectOnly("database_rules.md") })
    await runTool(h.tools, "memory_save", { ...DB_MEMORY, name: "Hidden Memory" })

    const ignored = await runContextHook(h, [contextUser("Ignore memory and answer from fresh context only.", "m1")])
    expect(ignored.system).toContain("# Auto Memory")
    expect(ignored.system).not.toContain("## MEMORY.md")
    expect(ignored.system).not.toContain("Hidden Memory")

    const stillIgnored = await runContextHook(h, [contextUser("Now tell me about it", "m2")])
    expect(stillIgnored.system).not.toContain("## MEMORY.md")

    const resumed = await runContextHook(h, [contextUser("Use memory again please", "m3")])
    expect(resumed.system).toContain("## MEMORY.md")
  })

  test("already-surfaced memories are not recalled twice", async () => {
    const h = await makeHarness({ options: { recall: { waitMs: 200 } }, generate: () => selectOnly("database_rules.md") })
    await runTool(h.tools, "memory_save", DB_MEMORY)

    const first = await runContextHook(h, [contextUser("How should we test database changes?", "m1")])
    expect(first.system).toContain("## Recalled Memories")

    const second = await runContextHook(h, [contextUser("Tell me again about database tests", "m2")])
    expect(second.system).not.toContain("## Recalled Memories")
  })

  test("a compaction makes memories eligible for recall again", async () => {
    const h = await makeHarness({ options: { recall: { waitMs: 200 } }, generate: () => selectOnly("database_rules.md") })
    await runTool(h.tools, "memory_save", DB_MEMORY)

    const first = await runContextHook(h, [contextUser("How should we test database changes?", "m1")])
    expect(first.system).toContain("## Recalled Memories")

    await h.emit({ type: "session.compaction.ended", data: { sessionID: "ses_test" } } as never)

    const afterCompaction = await runContextHook(h, [contextUser("How should we test database changes?", "m3")])
    expect(afterCompaction.system).toContain("## Recalled Memories")
  })

  test("session.deleted drops recall state", async () => {
    const h = await makeHarness({ options: { recall: { waitMs: 50 } } })
    await runContextHook(h, [contextUser("Ignore memory.", "m1")], "ses_gone")
    await h.emit({ type: "session.deleted", data: { sessionID: "ses_gone" } } as never)
    const after = await runContextHook(h, [contextUser("hello there", "m2")], "ses_gone")
    expect(after.system).toContain("## MEMORY.md")
  })
})
