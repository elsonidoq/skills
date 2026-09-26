import type { Info as ToolInfo } from "@opencode/plugin/promise/tool"
import type { ExtractionCoordinator } from "./extraction/ExtractionCoordinator.js"
import type { ToolExecuteContext } from "./sdk.js"
import { MEMORY_TYPES } from "./store/frontmatter.js"
import type { MemoryStore, SaveMemoryResult } from "./store/MemoryStore.js"

// Tool result for memory_save. Inside an extraction fork, `savedThisRun` (file names already saved
// by this fork, in order) is appended as an explicit done-signal so the model does not lose track on
// long transcripts and re-save the same memories until the timeout kills it (#35).
export function formatMemorySaveResult(outcome: SaveMemoryResult, savedThisRun?: readonly string[]): string {
  const inExtractionRun = savedThisRun !== undefined
  // The current file is recorded before formatting, so "earlier" means it appeared before this call.
  const savedEarlierThisRun = inExtractionRun && savedThisRun.indexOf(outcome.fileName) < savedThisRun.length - 1

  let head: string
  if (outcome.unchanged) {
    head = savedEarlierThisRun
      ? `Skipped: "${outcome.fileName}" was already saved earlier in this extraction run with identical content — nothing written.`
      : `Skipped: "${outcome.fileName}" already exists with identical content — nothing written (${outcome.filePath}).`
  } else if (savedEarlierThisRun) {
    head = `Updated "${outcome.fileName}" (first saved earlier in this extraction run) at ${outcome.filePath}`
  } else {
    head = `Memory saved to ${outcome.filePath}`
  }
  if (!inExtractionRun) return head

  const unique = Array.from(new Set(savedThisRun))
  return (
    `${head}\n\n` +
    `Saved so far in this extraction run (${unique.length}): ${unique.join(", ")}\n` +
    "These memories are already persisted — do not call memory_save for them again. " +
    "Once every distinct memory worth keeping is saved, stop calling tools and reply with a one-line summary."
  )
}

function plural(count: number, singular: string, pluralForm: string): string {
  return `${count} ${count === 1 ? singular : pluralForm}`
}

export function memorySaveTitle(type: string, name: string): string | undefined {
  if (type && name) return `${type}: ${name}`
  return name || undefined
}

export function memoryListTitle(count: number): string {
  return plural(count, "memory", "memories")
}

export function memorySearchTitle(query: string, count: number): string {
  return `"${query}" · ${plural(count, "match", "matches")}`
}

const FILE_NAME_HINT = 'with or without the .md extension; sub-directories are allowed, e.g. "team/conventions"'

const OBJECT_SCHEMA = (properties: Record<string, unknown>, required: string[]): Record<string, unknown> => ({
  type: "object",
  properties,
  required,
  additionalProperties: false,
})

// V2 tools use plain JSON Schema and return `{ content }` (plus optional metadata). The old V1
// `{ title, output }` titles are carried in metadata so the intent is not lost.
export function buildMemoryToolDefinitions(
  store: MemoryStore,
  extraction: Pick<ExtractionCoordinator, "recordSave">,
): ToolInfo[] {
  return [
    {
      name: "memory_save",
      description:
        "Save or update a memory for future conversations. " +
        "Each memory is stored as a markdown file with frontmatter. " +
        "Use this when the user explicitly asks you to remember something, " +
        "or when you observe important information worth preserving across sessions " +
        "(user preferences, feedback, project context, external references). " +
        "Check existing memories first with memory_list or memory_search to avoid duplicates.",
      input: OBJECT_SCHEMA(
        {
          file_name: {
            type: "string",
            description:
              'File name for the memory (without .md extension). Use snake_case, e.g. "user_role", "feedback_testing_style", "project_auth_rewrite"; a sub-directory prefix such as "team/conventions" is allowed',
          },
          name: { type: "string", description: "Human-readable name for this memory" },
          description: {
            type: "string",
            description: "One-line description — used to decide relevance in future conversations, so be specific",
          },
          type: {
            type: "string",
            enum: [...MEMORY_TYPES],
            description:
              "Memory type: user (about the person), feedback (guidance on approach), project (ongoing work context), reference (pointers to external systems)",
          },
          content: {
            type: "string",
            description:
              "Memory content. For feedback/project types, structure as: rule/fact, then **Why:** and **How to apply:** lines",
          },
        },
        ["file_name", "name", "description", "type", "content"],
      ),
      async execute(input, context: ToolExecuteContext) {
        const args = input as {
          file_name: string
          name: string
          description: string
          type: (typeof MEMORY_TYPES)[number]
          content: string
        }
        const outcome = store.save({
          fileName: args.file_name,
          name: args.name,
          description: args.description,
          type: args.type,
          content: args.content,
        })
        const savedThisRun = extraction.recordSave(context?.sessionID, outcome.fileName)
        return {
          content: formatMemorySaveResult(outcome, savedThisRun),
          metadata: {
            title: memorySaveTitle(args.type, args.name) ?? args.file_name,
            fileName: outcome.fileName,
            unchanged: outcome.unchanged,
          },
        }
      },
    },

    {
      name: "memory_delete",
      description: "Delete a memory that is outdated, wrong, or no longer relevant. Also removes it from the index.",
      input: OBJECT_SCHEMA(
        { file_name: { type: "string", description: `File name of the memory to delete (${FILE_NAME_HINT})` } },
        ["file_name"],
      ),
      async execute(input) {
        const args = input as { file_name: string }
        const deleted = store.delete(args.file_name)
        return {
          content: deleted ? `Memory "${args.file_name}" deleted.` : `Memory "${args.file_name}" not found.`,
          metadata: { title: args.file_name },
        }
      },
    },

    {
      name: "memory_list",
      description:
        "List all saved memories with their names, types, and descriptions. " +
        "Use this to check what memories exist before saving a new one (to avoid duplicates) " +
        "or when you need to recall what's been stored.",
      input: OBJECT_SCHEMA({}, []),
      async execute() {
        const entries = store.list()
        const title = memoryListTitle(entries.length)
        if (entries.length === 0) return { content: "No memories saved yet.", metadata: { title } }
        const lines = entries.map((e) => `- **${e.name}** (${e.type}) [${e.filename}]: ${e.description}`)
        return { content: `${entries.length} memories found:\n${lines.join("\n")}`, metadata: { title } }
      },
    },

    {
      name: "memory_search",
      description:
        "Search memories by keyword. Searches across names, descriptions, and content. " +
        "Use this to find relevant memories before answering questions or when the user references past conversations.",
      input: OBJECT_SCHEMA(
        { query: { type: "string", description: "Search query — searches across name, description, and content" } },
        ["query"],
      ),
      async execute(input) {
        const args = input as { query: string }
        const results = store.search(args.query)
        const title = memorySearchTitle(args.query, results.length)
        if (results.length === 0) return { content: `No memories matching "${args.query}".`, metadata: { title } }
        const lines = results.map(
          (e) =>
            `- **${e.name}** (${e.type}) [${e.filename}]: ${e.description}\n  Content: ${e.body.slice(0, 200)}${e.body.length > 200 ? "..." : ""}`,
        )
        return { content: `${results.length} matches for "${args.query}":\n${lines.join("\n")}`, metadata: { title } }
      },
    },

    {
      name: "memory_read",
      description: "Read the full content of a specific memory file.",
      input: OBJECT_SCHEMA(
        { file_name: { type: "string", description: `File name of the memory to read (${FILE_NAME_HINT})` } },
        ["file_name"],
      ),
      async execute(input) {
        const args = input as { file_name: string }
        const entry = store.read(args.file_name)
        if (!entry) return { content: `Memory "${args.file_name}" not found.`, metadata: { title: args.file_name } }
        return {
          content: `# ${entry.name}\n**Type:** ${entry.type}\n**Description:** ${entry.description}\n\n${entry.body}`,
          metadata: { title: args.file_name },
        }
      },
    },
  ]
}
