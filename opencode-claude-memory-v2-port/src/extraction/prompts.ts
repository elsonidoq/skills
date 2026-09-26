// The only copies of the extraction and auto-dream prompts.
//
// V2 `ctx.generate.text` is a single tool-less generation, so both prompts ask for a JSON plan and
// the plugin applies it with the same MemoryStore used by the memory_* tools.

export const EXTRACT_PROMPT = `You are now acting as the memory extraction subagent. The conversation below is reviewed for anything worth remembering for future sessions.

Return ONLY a JSON object, with no prose and no markdown fences, in this exact shape:
{"memories":[{"file_name":"...","name":"...","description":"...","type":"user|feedback|project|reference","content":"..."}]}

## What to save
1. **user** — Who the user is: role, expertise, preferences, communication style.
2. **feedback** — Guidance on how to work: corrections ("don't do X"), confirmations ("yes, keep doing that"), approach preferences. Include *why* so edge cases can be judged.
3. **project** — Ongoing work context: goals, deadlines, initiatives, decisions, bugs. NOT derivable from code/git. Convert relative dates to absolute.
4. **reference** — Pointers to external resources: URLs, tool names, where to find information outside the codebase.

## What NOT to save
- Code patterns, architecture, file structure — derivable from the codebase
- Git history, recent changes — use git log / git blame
- Debugging solutions — the fix is in the code
- Anything already in AGENTS.md / project config files
- Ephemeral task details or current conversation context
- Information already covered by an existing memory (see below) unless you are updating it with something new

## Rules
- file_name: descriptive snake_case slug (e.g. user_role, feedback_testing_approach)
- description: one-line description used for relevance matching in future sessions — be specific
- content: the memory body. For feedback/project types, structure as: rule/fact, then **Why:** and **How to apply:** lines
- To update an existing memory, reuse its exact file_name and provide the merged content
- Save each distinct memory as a separate entry
- If the conversation was trivial, return {"memories":[]} — that is fine
- Be selective: 0-3 memories per session is typical. Quality over quantity.
- Do NOT save a memory about the extraction process itself.`

export const EXTRACT_EXISTING_MEMORIES_HEADING = "## Existing memories"

export function buildExtractionPrompt(manifest: string, conversation: string): string {
  const inventory = manifest.trim() ? manifest.trim() : "(none yet)"
  return `${EXTRACT_PROMPT}\n\n${EXTRACT_EXISTING_MEMORIES_HEADING}\n\n${inventory}\n\n## Conversation\n\n${conversation}`
}

export const AUTODREAM_PROMPT = `You are performing an auto-dream memory consolidation pass over a Claude Code memory directory.

Goal: tighten and de-duplicate memory files so future sessions can orient faster.

Return ONLY a JSON object, with no prose and no markdown fences, in this exact shape:
{"upserts":[{"file_name":"...","name":"...","description":"...","type":"user|feedback|project|reference","content":"..."}],"deletes":["obsolete_file.md"]}

## Available operations
- "upserts": memories to create or overwrite, identified by file_name. Use them to merge duplicates into a single stronger memory, sharpen vague descriptions, and restructure feedback/project bodies (rule/fact, then **Why:** and **How to apply:**).
- "deletes": file names to remove because they are clearly obsolete, contradictory, or low-value.

## Guardrails
- Do NOT invent facts. Only reorganise and prune what is present.
- If confidence is low, keep the existing memory instead of guessing.
- If memory quality is already strong, return {"upserts":[],"deletes":[]}.
- Use the existing file names when updating an entry.`

export function buildAutodreamPrompt(memoryDump: string): string {
  return `${AUTODREAM_PROMPT}\n\n## Current memories\n\n${memoryDump || "(none)"}`
}
