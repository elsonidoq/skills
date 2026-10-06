---
name: infographic
description: Use when the user explicitly asks for a standalone visual HTML page or infographic built from a structured knowledge base.
---

# Infographic

Create structured content for the bundled renderer. Do not handwrite HTML or CSS.

## Detect The Contract

Before proposing a page, locate this canonical skill directory and confirm it contains:

- `scripts/build.py`
- `assets/page.css`
- `assets/page.js`

Identify the knowledge-base root. It must contain the source documents or conclusions the page will cite; existing `pages/manifest.json` establishes stable page IDs. Inspect `python3 <skill-dir>/scripts/build.py --help` rather than assuming invocation details.

If the renderer, assets, Python, or knowledge-base sources are unavailable, do not silently handcraft a replacement page. State the missing capability and offer either a structured Markdown document or instructions to make the canonical renderer and source corpus available.

Delivery bridges are optional. Detect one explicitly; do not assume a generated file is committed, uploaded, attached, or delivered automatically.

## Phase 1: Approve The Page

Before writing JSON or rendering, propose:

| Field | Requirement |
|---|---|
| Reader | Who will read it and what they know |
| Question | One question the page answers |
| Takeaway | One sentence the reader should retain |
| Outline | Five to eight blocks in order |
| Page ID | Stable lowercase letters, digits, and hyphens; reuse the prior ID when replacing a page |

Stop and wait for approval. If the prior approval is not visible in the current context, propose it again. Do not reconstruct approval from memory.

## Phase 2: Build

1. Read the cited source files. Preserve or create the underlying conclusion when the knowledge-base contract requires one.
2. Write a content JSON file containing the approved `page_id`, title, lede, structured blocks, and sources.
3. Run the renderer by absolute path:

```bash
python3 <skill-dir>/scripts/build.py <kb-root> <content.json>
```

4. Fix every validation error and rerun. Exit code `3` means no valid page was produced.
5. Inspect the resulting file for readable structure, escaped content, working source links, and mobile behavior.
6. Report the output path. If an actual delivery bridge exists, pass its outbox path with `--outbox <path>` and report the observed delivery state separately.

For authorized retained repository output, apply the shared task checkpoint after required validation; do not infer creation, upload, or external-delivery authority.

## Content Schema

```json
{
  "title": "A claim, not a topic",
  "page_id": "stable-page-id",
  "lede": "The page's argument in one sentence.",
  "blocks": [
    {"type": "stat", "value": "52%", "label": "answer accuracy"},
    {"type": "section", "heading": "The tension", "body": "Connected explanatory prose."},
    {"type": "compare", "columns": ["", "A", "B"], "rows": [["Cost", "Low", "High"]]},
    {"type": "list", "heading": "Evidence", "items": ["A traceable fact"]},
    {"type": "steps", "heading": "Action", "items": ["First step", "Second step"]},
    {"type": "callout", "tone": "warn", "body": "The one caveat worth interrupting for."},
    {"type": "sources", "items": ["documents/source-a.md", "conclusions/source-b.md"]}
  ],
  "glossary": {"term": "short definition"}
}
```

The renderer's validation is authoritative. Current block types are `section`, `stat`, `compare`, `steps`, `list`, `callout`, `quote`, and `sources`.

## Structure

| Content shape | Block |
|---|---|
| Important number | `stat` |
| Options on shared dimensions | `compare` |
| Ordered procedure | `steps` |
| Unordered facts or criteria | `list` |
| Verbatim sourced words | `quote` |
| One interrupting caveat | `callout` |
| Connected reasoning | `section` |

Use grouped list or step items when an item has a short `term`, optional `detail`, and flat `items`. Do not type bullets into prose bodies. Keep headings short, use emphasis sparingly, and write in the knowledge base's language.

## Traceability And Validation

- End with a `sources` block containing at least two files that exist under the knowledge-base root.
- Cite only files actually read. Source-document links resolve through their recorded `source:` metadata; never invent URLs.
- Reuse a stable `page_id` so a replacement does not orphan the old file.
- Keep content within renderer limits for blocks, glossary terms, nesting, emphasis, and links.
- Treat the generated HTML and `pages/manifest.json` as renderer outputs. The renderer prints the generated path; optional outbox delivery occurs only when explicitly configured.

## Stop Conditions

- No explicit request for a visual standalone page.
- No approved reader, question, takeaway, outline, and page ID.
- Missing renderer capability or knowledge-base sources.
- Sources were not opened or cannot be traced.
- The content is mostly prose sections when a list, comparison, steps, or stats express its structure better.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Authorized retained repository output checkpoints after its existing approval and validation; this neither grants creation/upload authority nor requires a commit for external-only output.
