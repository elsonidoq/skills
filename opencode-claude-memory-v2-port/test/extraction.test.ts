import { afterEach, describe, expect, test } from "bun:test"
import { existsSync, readFileSync } from "node:fs"
import { join } from "node:path"
import { AutoDream, buildMemoryDump, shouldRunAutodream } from "../src/extraction/autodream.js"
import { MaintenanceLock } from "../src/extraction/lock.js"
import { parseAutodreamPlan, parseExtractionPlan } from "../src/extraction/plan.js"
import { ExtractionStateStore } from "../src/extraction/state.js"
import { MemoryStore } from "../src/store/MemoryStore.js"
import {
  cleanupTempDirs,
  makeConfig,
  makeFakeHost,
  makeHarness,
  makeStore,
  noopLog,
  runTool,
  type SessionMessage,
} from "./helpers/index.js"

afterEach(cleanupTempDirs)

function v2User(text: string, id: string, created: number): SessionMessage {
  return { id, type: "user", time: { created }, text } as unknown as SessionMessage
}

function waitFor(check: () => boolean, timeoutMs = 2000): Promise<void> {
  const deadline = Date.now() + timeoutMs
  return new Promise((resolve, reject) => {
    const tick = () => {
      if (check()) return resolve()
      if (Date.now() > deadline) return reject(new Error("timed out waiting for condition"))
      setTimeout(tick, 10)
    }
    tick()
  })
}

const FACT_SESSION = "ses_parent"

describe("automatic extraction", () => {
  test("session.idle extracts a memorable fact through a generated JSON plan", async () => {
    const h = await makeHarness({
      options: { extract: { debounceMs: 0 }, autodream: { enabled: false } },
      generate: () =>
        JSON.stringify({
          memories: [
            {
              file_name: "reports_output_dir",
              name: "Reports Output",
              description: "Reports go to ./artifacts/final/",
              type: "project",
              content: "All generated reports must be written to ./artifacts/final/.",
            },
          ],
        }),
    })
    h.setSessionMessages(FACT_SESSION, [
      v2User("For this test project all generated reports must be written to ./artifacts/final/.", "u1", 1),
    ])

    await h.emit({ type: "session.idle", data: { sessionID: FACT_SESSION } } as never)

    const filePath = join(h.store.memoryDir, "reports_output_dir.md")
    await waitFor(() => existsSync(filePath))
    expect(readFileSync(filePath, "utf-8")).toContain("All generated reports must be written to ./artifacts/final/.")
    expect(h.store.readIndex()).toContain("reports_output_dir.md")
    expect(h.host.prompts[0]).toContain("## Existing memories")
    expect(h.host.prompts[0]).toContain("## Conversation")
  })

  test("session.execution.succeeded also triggers extraction (2.0.16 end-of-turn signal)", async () => {
    const h = await makeHarness({
      options: { extract: { debounceMs: 0 }, autodream: { enabled: false } },
      generate: () =>
        JSON.stringify({
          memories: [
            {
              file_name: "exec_fact",
              name: "Exec Fact",
              description: "from execution.succeeded",
              type: "project",
              content: "Extraction is triggered by session.execution.succeeded.",
            },
          ],
        }),
    })
    h.setSessionMessages(FACT_SESSION, [v2User("A durable fact from a completed execution.", "u1", 1)])
    await h.emit({ type: "session.execution.succeeded", data: { sessionID: FACT_SESSION } } as never)
    const filePath = join(h.store.memoryDir, "exec_fact.md")
    await waitFor(() => existsSync(filePath))
    expect(readFileSync(filePath, "utf-8")).toContain("session.execution.succeeded")
  })

  test("the watermark prevents re-extracting the same turn", async () => {
    const h = await makeHarness({
      options: { extract: { debounceMs: 0 }, autodream: { enabled: false } },
      generate: () => JSON.stringify({ memories: [] }),
    })
    h.setSessionMessages(FACT_SESSION, [v2User("A stable fact", "u1", 1)])

    await h.emit({ type: "session.idle", data: { sessionID: FACT_SESSION } } as never)
    await waitFor(() => h.host.prompts.length === 1)

    await h.emit({ type: "session.idle", data: { sessionID: FACT_SESSION } } as never)
    await new Promise((resolve) => setTimeout(resolve, 50))
    expect(h.host.prompts).toHaveLength(1)
  })

  test("a memory_save by the main agent skips the extraction round", async () => {
    const h = await makeHarness({
      options: { extract: { debounceMs: 0 }, autodream: { enabled: false } },
      generate: () => JSON.stringify({ memories: [{ file_name: "x", name: "X", description: "d", type: "user", content: "c" }] }),
    })
    h.setSessionMessages(FACT_SESSION, [v2User("A fact worth remembering for later use.", "u1", 1)])

    await runTool(
      h.tools,
      "memory_save",
      { file_name: "manual", name: "Manual", description: "d", type: "user", content: "c" },
      { sessionID: FACT_SESSION },
    )
    await h.emit({ type: "session.idle", data: { sessionID: FACT_SESSION } } as never)
    await new Promise((resolve) => setTimeout(resolve, 60))
    expect(h.host.prompts).toHaveLength(0)
  })

  test("a failed generation leaves the watermark and retries", async () => {
    let calls = 0
    const h = await makeHarness({
      options: { extract: { debounceMs: 0 }, autodream: { enabled: false } },
      generate: () => {
        calls += 1
        throw new Error("model down")
      },
    })
    h.setSessionMessages(FACT_SESSION, [v2User("A fact worth remembering for later use.", "u1", 1)])
    await h.emit({ type: "session.idle", data: { sessionID: FACT_SESSION } } as never)
    await waitFor(() => calls === 1)
    const state = h.store.stateDir
    // nothing written, and the watermark was not advanced (no lastExtractedMessageID recorded)
    const stateFile = join(state, "extraction-state.json")
    if (existsSync(stateFile)) {
      const data = JSON.parse(readFileSync(stateFile, "utf-8"))
      expect(data.sessions[FACT_SESSION]?.lastExtractedMessageID).toBeUndefined()
      expect(data.sessions[FACT_SESSION]?.failures).toBe(1)
    }
  })
})

describe("plan parsing", () => {
  test("extraction plan tolerates prose and drops invalid entries", () => {
    const plan = parseExtractionPlan(
      `Here you go:\n{"memories":[{"file_name":"a","name":"A","description":"d","type":"user","content":"c"},{"file_name":"","name":"bad"}]}\nthanks`,
    )
    expect(plan.memories).toHaveLength(1)
    expect(plan.memories[0]?.file_name).toBe("a")
  })

  test("autodream plan reads upserts and deletes", () => {
    const plan = parseAutodreamPlan(`{"upserts":[{"file_name":"a","name":"A","type":"feedback","content":"c"}],"deletes":["old.md",""]}`)
    expect(plan.upserts).toHaveLength(1)
    expect(plan.upserts[0]?.type).toBe("feedback")
    expect(plan.deletes).toEqual(["old.md"])
  })
})

describe("auto-dream consolidation", () => {
  function makeDream(store: MemoryStore, generate: (prompt: string) => string, overrides: Record<string, unknown> = {}) {
    const config = makeConfig(
      { autodream: { enabled: true, minHours: 24, minSessions: 1, ...overrides }, extract: { enabled: true } },
      store.claudeConfigDir,
    )
    const state = new ExtractionStateStore(store.stateDir)
    const host = makeFakeHost(store.memoryRoot, { generate, log: noopLog })
    const dream = new AutoDream({ store, config, host, state, log: noopLog })
    return { dream, state, host, config }
  }

  test("gate requires minHours and minSessions", () => {
    expect(shouldRunAutodream({ lastConsolidatedAt: 0, sessionsSince: [] }, { minHours: 24, minSessions: 5 }, Date.now())).toBe(false)
    expect(
      shouldRunAutodream(
        { lastConsolidatedAt: Date.now() - 25 * 60 * 60 * 1000, sessionsSince: ["a", "b", "c", "d", "e"] },
        { minHours: 24, minSessions: 5 },
        Date.now(),
      ),
    ).toBe(true)
  })

  test("merges duplicates and prunes obsolete memories without corrupting the rest", async () => {
    const store = makeStore()
    store.save({ fileName: "db_rules", name: "DB Rules", description: "old", type: "feedback", content: "Use a real DB." })
    store.save({ fileName: "db_tests", name: "DB Tests", description: "old", type: "feedback", content: "Never mock the DB." })
    store.save({ fileName: "keep", name: "Keep Me", description: "stable", type: "reference", content: "Important long-term info." })

    const { dream, state } = makeDream(store, () =>
      JSON.stringify({
        upserts: [
          {
            file_name: "db_testing",
            name: "DB Testing",
            description: "Integration tests use a real database",
            type: "feedback",
            content: "Rule: integration tests hit a real database.\n\n**Why:** mocked tests hid a broken migration.",
          },
        ],
        deletes: ["db_rules.md", "db_tests.md"],
      }),
    )
    state.update((data) => {
      data.autodream.sessionsSince = ["s1"]
      data.autodream.lastConsolidatedAt = 0
    })
    expect(dream.shouldRun()).toBe(true)
    expect(await dream.maybeRun("s1")).toBe(true)

    expect(store.read("db_testing")?.description).toContain("Integration tests use a real database")
    expect(store.read("db_testing")?.body).toContain("real database")
    expect(store.read("db_rules")).toBeNull()
    expect(store.read("db_tests")).toBeNull()
    // Manual/other memories are preserved and the index is valid.
    expect(store.read("keep")?.body).toContain("Important long-term info.")
    expect(store.readIndex()).toContain("db_testing.md")
    expect(store.readIndex()).not.toContain("db_rules.md")
    expect(store.readIndex()).toContain("keep.md")
    // Gate reset.
    expect(state.read().autodream.sessionsSince).toEqual([])
    expect(state.read().autodream.lastConsolidatedAt).toBeGreaterThan(0)
  })

  test("buildMemoryDump includes file content and caps size", () => {
    const store = makeStore()
    store.save({ fileName: "a", name: "A", description: "d", type: "user", content: "body-a" })
    expect(buildMemoryDump(store, 1)).toBe("")
    const full = buildMemoryDump(store, 10_000)
    expect(full).toContain("body-a")
    expect(full).toContain("### a.md")
  })

  test("a live maintenance lock prevents a concurrent consolidation", async () => {
    const store = makeStore()
    const state = new ExtractionStateStore(store.stateDir)
    const lock = new MaintenanceLock(state.lockPath)
    expect(lock.tryAcquire()).toBe(true)
    try {
      const { dream } = makeDream(store, () => JSON.stringify({ upserts: [], deletes: [] }))
      state.update((data) => {
        data.autodream.sessionsSince = ["s1"]
      })
      expect(await dream.maybeRun("s1")).toBe(false)
    } finally {
      lock.release()
    }
  })
})
