// LLM memory selection, ported from Claude Code's findRelevantMemories.ts side query. Runs in a
// hidden child session so the main conversation never sees the selector exchange.
//
// V2 has no per-prompt structured-output option, so the selector agent is instructed to answer with
// JSON and the text is parsed; a malformed answer simply recalls nothing for this turn.
import { formatMemoryManifest, type MemoryHeader } from "../store/scan.js"
import { withDeadline } from "../util/timeout.js"
import type { MemoryHost } from "../v2/host.js"

export const SELECT_MEMORIES_SYSTEM_PROMPT = `You are selecting memories that will be useful to OpenCode as it processes a user's query. You will be given the user's query and a list of available memory files with their filenames and descriptions.

Return a list of filenames for the memories that will clearly be useful to OpenCode as it processes the user's query (up to 5). Only include memories that you are certain will be helpful based on their name and description.
- If you are unsure if a memory will be useful in processing the user's query, then do not include it in your list. Be selective and discerning.
- If there are no memories in the list that would clearly be useful, feel free to return an empty list.
- If a list of recently-used tools is provided, do not select memories that are usage reference or API documentation for those tools (OpenCode is already exercising them). DO still select memories containing warnings, gotchas, or known issues about those tools — active use is exactly when those matter.

Answer with a single JSON object and nothing else, in this exact shape: {"selected_memories": ["filename.md", ...]}. Use an empty array when nothing is clearly useful.
`

export const RECALL_SELECTOR_TITLE = "opencode-memory recall selector"

export type SelectRelevantMemoryFilenamesInput = {
  host: MemoryHost
  query: string
  memories: readonly MemoryHeader[]
  recentTools: readonly string[]
  timeoutMs: number
  maxMemories: number
}

function tryParseSelectedMemories(raw: string): string[] | undefined {
  const trimmed = raw.trim()
  const start = trimmed.indexOf("{")
  const end = trimmed.lastIndexOf("}")
  if (start === -1 || end === -1 || end <= start) return undefined
  try {
    const parsed = JSON.parse(trimmed.slice(start, end + 1)) as { selected_memories?: unknown }
    if (!Array.isArray(parsed.selected_memories)) return undefined
    return parsed.selected_memories.filter((item): item is string => typeof item === "string")
  } catch {
    return undefined
  }
}

export function extractSelectedMemories(text: string): string[] {
  return tryParseSelectedMemories(text) ?? []
}

export function buildSelectorQuery(
  query: string,
  memories: readonly MemoryHeader[],
  recentTools: readonly string[],
): string {
  const toolsSection = recentTools.length > 0 ? `\n\nRecently used tools: ${recentTools.join(", ")}` : ""
  return `Query: ${query}\n\nAvailable memories:\n${formatMemoryManifest(memories)}${toolsSection}`
}

// Never throws: a failed or timed-out selector simply recalls nothing for this turn.
export async function selectRelevantMemoryFilenames(input: SelectRelevantMemoryFilenamesInput): Promise<string[]> {
  if (input.memories.length === 0) return []

  try {
    const prompt = `${SELECT_MEMORIES_SYSTEM_PROMPT}\n\n${buildSelectorQuery(input.query, input.memories, input.recentTools)}`
    const text = await withDeadline(RECALL_SELECTOR_TITLE, input.timeoutMs, (signal) =>
      input.host.generateText(prompt, signal),
    )

    const validFilenames = new Set(input.memories.map((memory) => memory.filename))
    return extractSelectedMemories(text)
      .filter((filename) => validFilenames.has(filename))
      .slice(0, input.maxMemories)
  } catch {
    return []
  }
}
