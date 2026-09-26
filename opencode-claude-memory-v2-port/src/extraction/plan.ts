// Parsing and validation of the model's JSON memory plans. V2 `ctx.generate.text` is tool-less, so
// extraction and auto-dream ask the model for a JSON plan and the plugin performs the file writes
// itself (see docs/v2-port-migration.md for why the V1 tool-loop forks are not reproduced).
import { MEMORY_TYPES, parseMemoryType, type MemoryType } from "../store/frontmatter.js"

export type MemoryDraft = {
  file_name: string
  name: string
  description: string
  type: MemoryType
  content: string
}

export type ExtractionPlan = {
  memories: MemoryDraft[]
}

export type AutodreamPlan = {
  upserts: MemoryDraft[]
  deletes: string[]
}

export const MAX_EXTRACTED_MEMORIES = 5
export const MAX_AUTODREAM_UPSERTS = 20
export const MAX_AUTODREAM_DELETES = 50

function sliceJsonObject(text: string): unknown {
  const trimmed = text.trim()
  const start = trimmed.indexOf("{")
  const end = trimmed.lastIndexOf("}")
  if (start === -1 || end === -1 || end <= start) return undefined
  try {
    return JSON.parse(trimmed.slice(start, end + 1))
  } catch {
    return undefined
  }
}

function normaliseDraft(raw: unknown): MemoryDraft | undefined {
  if (!raw || typeof raw !== "object") return undefined
  const value = raw as Record<string, unknown>
  const file_name = typeof value.file_name === "string" ? value.file_name.trim() : ""
  const name = typeof value.name === "string" ? value.name.trim() : ""
  const content = typeof value.content === "string" ? value.content.trim() : ""
  if (!file_name || !name || !content) return undefined
  const description = typeof value.description === "string" ? value.description.trim() : ""
  const type = parseMemoryType(typeof value.type === "string" ? value.type : undefined) ?? "user"
  return { file_name, name, description, type, content }
}

function normaliseDrafts(raw: unknown, max: number): MemoryDraft[] {
  if (!Array.isArray(raw)) return []
  const drafts: MemoryDraft[] = []
  const seen = new Set<string>()
  for (const item of raw) {
    const draft = normaliseDraft(item)
    if (!draft) continue
    if (seen.has(draft.file_name)) continue
    seen.add(draft.file_name)
    drafts.push(draft)
    if (drafts.length >= max) break
  }
  return drafts
}

export function parseExtractionPlan(text: string, max = MAX_EXTRACTED_MEMORIES): ExtractionPlan {
  const parsed = sliceJsonObject(text) as { memories?: unknown } | undefined
  return { memories: normaliseDrafts(parsed?.memories, max) }
}

export function parseAutodreamPlan(text: string): AutodreamPlan {
  const parsed = sliceJsonObject(text) as { upserts?: unknown; deletes?: unknown } | undefined
  const deletes: string[] = []
  if (Array.isArray(parsed?.deletes)) {
    for (const item of parsed.deletes) {
      if (typeof item === "string" && item.trim()) deletes.push(item.trim())
      if (deletes.length >= MAX_AUTODREAM_DELETES) break
    }
  }
  return { upserts: normaliseDrafts(parsed?.upserts, MAX_AUTODREAM_UPSERTS), deletes }
}

export { MEMORY_TYPES }
