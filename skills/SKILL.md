---
name: infographic
description: Use whenever the user asks for something to be written out as a document rather than answered in chat — a page, infographic, report, routine, plan, guide, summary, cheat sheet, one-pager, visual explainer, or any standalone HTML file — built from a knowledge base. Also use before writing any .html file by hand: that is this skill's job, not yours. Never triggers on an ordinary question, only on an explicit request for a document.
---

# Infographic

## Overview

You write **content, never markup**. `scripts/build.py` owns every layout
decision: fonts, spacing, colour, dark mode, the lot. You describe what the page
says as JSON blocks; it renders a standalone HTML file that looks exactly like
every other page this skill has ever built.

That is deliberate. A page whose design varies per topic makes the reader relearn
the layout each time, and hand-written CSS is where a page stops being readable.
There is no raw-HTML block and asking for one is a red flag, not a feature.

**Scripts sit beside this SKILL.md.** Your working directory is the knowledge
base, not the skill's, so set `$SKILL` to the directory you loaded this file from
(`~/.claude/skills/infographic`, or `~/.config/opencode/skills/infographic`) and
invoke by absolute path.

```bash
python $SKILL/scripts/build.py <kb-root> content.json
```

## Never build unasked — and never build by hand

A page costs real tokens and takes a turn the user is waiting through. Build one
**only** when they explicitly ask for one. A hard question is not a request for a
page. An answer that would suit a diagram is not a request for a page. Offer in
one clause if you think it would help — then wait.

**They will not say "infographic".** They ask for a *report*, a *routine*, a
*plan*, a *guide*, a *summary*, a *cheat sheet*, a *one-pager*, "write this up",
"make me something I can read later". Every one of those is this skill.

**The build script writes the file. You never type HTML — anywhere.**
Not into a file, and above all not into your reply. If you are about to type
`<!DOCTYPE`, you have taken a wrong turn: go back, write `content.json`, run
`build.py`. Hand-written markup is the one thing you are worst at, and it arrives
with no design, no dark mode, no sources and none of the checks that stop a page
being wrong.

**Pasting a page into the chat instead is worse, not safer.** It reaches the
reader as a dozen messages of angle brackets they cannot open. When a page has
been built, it is delivered to them as a file automatically — you do not attach
it and you do not need to. Saying you cannot send files is false.

## Two phases. Always both.

### Phase 1 — pin the goal, then stop

Never open the JSON before the user has confirmed. Reply with four things, short,
and **nothing else**:

| | What you state |
|---|---|
| **Reader** | Who opens this, and what they already know |
| **The one question** | The single question the page answers. If you need "and", it is two pages — pick one |
| **The takeaway** | The sentence they should be able to repeat afterwards |
| **Outline** | The blocks in order, one line each, five to eight of them |
| **Page id** | A short stable id, lowercase letters, digits and hyphens. **Reuse the id of the page this one replaces** — look under `## Pages` in `index.md` (or `pages/manifest.json`) — so the old file is replaced rather than left beside the new one; a genuinely new page gets a new id |

Then stop and wait for approval. If the request is vague — "make me a page about
rerankers" — the missing piece is almost always the *reader* and the *one
question*; ask for those in the same message rather than guessing and building
the wrong page.

**A page is a shape for one argument, not a dump of a topic.** If the outline is
"everything I know about X", the goal is not pinned yet. Go back and ask what
decision the reader is trying to make.

If the user declines or changes the goal, do not build. If they approve with edits,
restate the corrected outline in one line and build from that.

**If you cannot see the outline you are meant to have agreed, you did not agree
it.** A conversation can be cleared or dropped between the two phases. When the
approval is not in front of you, propose the outline again rather than
reconstructing what you think was signed off — a reconstructed outline is a guess,
and the user pays a turn for the wrong page.

### Phase 2 — build it

1. **Save the reasoning as a conclusion first**, if it is not already one. The
   page is a rendering; the conclusion is the knowledge. A page built from
   reasoning that was never written down gets re-derived next month.
2. Write `content.json` — the schema below, with the agreed `page_id`. Every field is plain prose; the
   builder escapes everything, so write text, not tags.
3. Run `build.py`. It exits **3** and writes nothing if the content is rejected;
   read the problems it lists, fix them, rerun.
4. Reply in two or three sentences saying what the page argues. **Do not paste
   the HTML, do not paste the JSON, do not print the file path.** The bridge picks
   the page up and sends it on its own.

The page is written to `<kb-root>/pages/<slug>.html`, recorded in
`pages/manifest.json` under its `page_id`, and committed with the rest of the
knowledge base, so it can be re-sent or rebuilt later. Rebuilding under the same
`page_id` with a new title deletes the previous file — that is what the id is
for.

## The content file

```json
{
  "title": "Chunk size and reranking pull in opposite directions",
  "page_id": "chunk-size-vs-reranking",
  "lede": "Smaller chunks retrieve more precisely but push more candidates at the reranker than it can afford. Pick the chunk size from your reranking budget, not the other way round.",
  "blocks": [
    {"type": "stat", "value": "200–400", "label": "tokens per chunk", "note": "roughly 150–300 words"},
    {"type": "stat", "value": "52% → 62%", "label": "answer accuracy", "note": "reranking top 50, not top 10"},
    {"type": "stat", "value": "3×", "label": "reranker cost", "note": "for that same depth"},

    {"type": "section", "heading": "The tension",
     "body": "A chunk is the unit you retrieve. Cut it small and each one is about a single thing, so the search step rarely hands back a passage that merely mentions the right words.\n\nBut small chunks mean more of them, and **a reranker has a fixed budget** of passages it can score before the user notices the wait."},

    {"type": "compare", "columns": ["", "Small chunks", "Large chunks"],
     "rows": [["Retrieval precision", "High — one idea each", "Lower — matches can be incidental"],
              ["Candidates to rerank", "4× as many", "Fewer, cheaper"],
              ["Fails when", "The answer spans two", "The sentence is buried"]]},

    {"type": "list", "heading": "What you already have",
     "items": ["A cross-encoder reranker, 50-passage budget",
               "10k English documents, no code or tables",
               "Accuracy measured end to end, not by retrieval metrics"]},

    {"type": "steps", "heading": "What to do",
     "items": [
       {"term": "Measure the budget first",
        "detail": "How many passages the reranker scores inside your latency budget. Every other number here follows from that one.",
        "items": ["Time it at 10, 50 and 100 passages",
                  "Hold the generator constant while you do"]},
       "Start at **400 tokens** with 15% overlap, and rerank the top 50.",
       "Halve the chunk size only if **retrieval** is failing, not generation."]},

    {"type": "quote", "body": "We kept shrinking chunks to fix answers that were wrong for a different reason.",
     "attribution": "Postmortem, internal RAG rebuild, 2025"},

    {"type": "callout", "tone": "warn",
     "body": "If the model has the right passage and still answers badly, chunk size is not your problem and shrinking it costs retrieval for nothing."},

    {"type": "section", "heading": "What is uncertain",
     "body": "Both sources use English prose at ~10k documents, and [the position study](documents/lost-in-the-middle.md) measures retrieval depth rather than structure. Neither covers code or tables, where boundaries follow structure rather than length."},

    {"type": "sources", "items": ["conclusions/chunk-rerank.md", "documents/lost-in-the-middle.md",
                                  "documents/rerank-depth.md"]}
  ],
  "glossary": {"reranker": "a second pass that re-sorts search results by how well they answer the question",
               "chunk": "one slice of a document, and the unit the search step retrieves"}
}
```

**Copy the shape of that, not just its syntax.** Eleven blocks, eight types, one
argument: numbers up front, the tension in prose, the trade-off as a table, the
facts as a list, the plan as steps, the trap as a callout, the limits last.

## What the reader actually sees

You never see the page you are building, so here is what that example renders as.
The visual weight is the reason each block exists — read this before choosing one.

```
+---------------------------------------+
|  Chunk size and reranking pull in     |  h1 - large. Two lines at most,
|  opposite directions                  |  so a title is a claim, not a topic
|                                       |
|  Smaller chunks retrieve more         |  lede - larger grey prose, set off
|  precisely but push more candidates   |  by a rule. Most readers read the
|  -------------------------------------|  title, the lede, the stats, and go
|                                       |
|  +---------+ +----------+ +---------+ |  stat - side by side in ONE row.
|  | 200-400 | | 52%>62%  | |   3x    | |  Two to four fit. Seven wrap into
|  | tokens  | | accuracy | |  cost   | |  a grid nobody reads. Every plate
|  +---------+ +----------+ +---------+ |  is drawn with a visible edge
|                                       |
|  THE TENSION                          |  h2 - SMALL, UPPERCASE, 2-4 words.
|  A chunk is the unit you retrieve.    |  A sentence here reads as shouting
|  Cut it small and each one is about   |
|  a single thing. But small chunks     |  section - the argument, prose only
|  mean more of them, and A RERANKER    |
|  HAS A FIXED BUDGET of passages.      |  **bold** lands the one clause the
|                                       |  reader must not skim past
|  +-----------------------------------+|  compare - boxed, and it scrolls
|  | precision | high     | lower      ||  sideways on a phone, so three
|  | cost      | 4x more  | cheaper    ||  columns is the practical limit
|  +-----------------------------------+|
|                                       |
|  +-----------------------------------+|  a GROUPED item: the term is an h3,
|  |(1) Measure the budget first       ||  the detail is prose beneath it, and
|  |    How many passages the reranker ||  its sub-items are indented bullets.
|  |    scores inside your latency...  ||  The plate is what shows they belong
|  |      - Time it at 10, 50 and 100  ||  to THIS step and not to the next
|  |      - Hold the generator constant||
|  +-----------------------------------+|
|  (2) Start at 400 TOKENS, top 50      |  a plain string item stays a plain
|                                       |  row. Mix the two freely in one list
|  | If the model has the right passage |  callout - tinted, heavy left bar,
|  | and still answers badly            |  boxed. It interrupts: one per page
|                                       |
|  -------------------------------------|
|  SOURCES                              |  small, grey, last. Always
|  conclusions/chunk-rerank.md          |
+---------------------------------------+
```

## Choosing a block

**`section` is not the default.** It is for argument — the connective tissue
between the things that carry the page. Before writing one, ask what shape the
content actually is:

| The content is | The block |
|---|---|
| A number that carries weight | `stat` — two to four in a row reads best |
| Two or three options along the same dimensions | `compare` |
| A procedure, in order | `steps` |
| Facts, items, criteria — unordered | `list` |
| Words worth reproducing verbatim | `quote` |
| The one caveat worth interrupting for | `callout` |
| Reasoning that only works as prose | `section` |

The three that get confused, in the order they get confused:

```json
"Three sources, 10k English documents, no code"  →  {"type": "list", "items": [...]}
"Small chunks are precise, large ones cheaper"   →  {"type": "compare", "columns": [...]}
"Accuracy went from 52% to 62%"                  →  {"type": "stat", "value": "52% → 62%"}
```

None of those three is a `section`. A `section` earns its place when the sentences
depend on each other — when removing one breaks the next.

**A page of five `section`s is a document, not an infographic.** If you have
written the same block type three times in a row, stop and look at what you are
actually saying: a run of facts is a `list`, a pair of options is a `compare`, a
number you keep repeating in prose is a `stat`. The layout is the work.

Three `steps` blocks in a row is that same failure wearing a different block. It
is one procedure with three phases, which is one `steps` block whose items are
grouped — the phases become the terms, and the reader can see they are phases of
one thing rather than three unrelated lists that happen to be adjacent.

**Never type a bullet into a body.** A body renders as one paragraph, so lines
starting with `•` or `-` run together into an unreadable strip. The builder
rejects them and names the block you wanted.

### The mistake this skill keeps having to correct

A real page came back with this block, and it is wrong in three ways at once:

```json
{"type": "section", "heading": "Your baseline",
 "body": "• MRI: labral signal change\n• Pain: mild pinch, only arm-behind\n• Strength: 12 pull-ups, 3×3 banded muscle-ups"}
```

The bullets collapse into one run-on strip, because single newlines are not
paragraph breaks. The content is a set of facts, not an argument, so `section` was
never the right block. And the two numbers that a reader would actually want —
the ones that say where this person is starting — are buried mid-sentence.

The same content, laid out:

```json
{"type": "stat", "value": "12–13", "label": "strict pull-ups"},
{"type": "stat", "value": "3×3", "label": "banded muscle-ups", "note": "bar, strict"},
{"type": "list", "heading": "Your baseline",
 "items": ["MRI: posterosuperior labral signal change, not a confirmed tear",
           "Pain: mild pinch, only in chest-open positions",
           "No trouble in daily life"]}
```

Same words, three blocks instead of one, and the page now opens with the two
numbers the reader came for.

### The second one: a paragraph doing a list's job

From the same real page, and the reason grouped items exist:

```json
{"type": "section", "heading": "Rehab, both days",
 "body": "Phase 1 (weeks 1-6), low biceps load, 3x12-15: internal and external rotation at 20-90 degrees, seated row, serratus punch, prone extension, shoulder-level scapular retraction. Phase 2 (weeks 7-16) adds the full can, forward flexion in supination, and elbow flexion in supination."}
```

Nothing in there is an argument. It is two named phases, each with a load and a
set of exercises, written as prose because no block could hold that shape. The
reader opens this mid-session on a phone and has to re-parse the colons and the
commas every single time.

The same content, grouped:

```json
{"type": "list", "heading": "Rehab, both days", "items": [
  {"term": "Phase 1, weeks 1-6",
   "detail": "Low biceps load, **3x12-15**.",
   "items": ["Internal and external rotation, 20-90 degrees", "Seated row",
             "Serratus punch", "Prone extension", "Shoulder-level scapular retraction"]},
  {"term": "Phase 2, weeks 7-16",
   "detail": "Everything above, plus the full can, forward flexion in supination, and elbow flexion in supination."}
]}
```

**If a body names two or three things and then describes each, it is a grouped
list.** The tell is a colon followed by a run of commas, or a sentence that opens
"Phase 2 adds". Both mean the structure is already in the content and only the
markup is missing.

## Emphasis and hierarchy

Three things, and only these three, may appear inside prose:

- `**bold**` for the clause that changes what the reader does — a stop rule, a
  threshold, the one number in a sentence they will otherwise skim past.
- `` `code` `` for a literal: a filename, a flag, a value typed exactly.
- `[text](documents/x.md)` for a link, which the next section explains.

Bold is a colour step, not just a weight, so it carries further than you expect.
**One or two per block.** The builder rejects a field that is more than a quarter
bold, because a paragraph in bold is a paragraph with no emphasis in it. Never
bold a heading, which is already styled, and never bold a phrase to fake a
heading — that is what a grouped item's `term` is for.

Three heading levels exist and each has exactly one job:

| Level | What it is | Where it comes from |
|---|---|---|
| `h1` | The page's claim | `title` |
| `h2` | A block's label, small and uppercase | a block's `heading` |
| `h3` | One item's name inside a list | an item's `term` |

There is no fourth level, and sub-items cannot have sub-items. If the content
needs that, it is a document: write a conclusion and build a page about one part
of it.

## Links, and the rule that keeps them honest

A link opens **the source material** — the article, the paper, the page a document
was fetched from. It never points at a file in the knowledge base, which the
reader has no way to open.

So you never type a URL. You link a *document*, and the builder substitutes the
address from that document's `source:` header:

```json
"body": "The ladder in [a coach's six-rung progression](documents/progression-muscleup-6step-ladder.md) treats the transition as the usual failure point."
```

The reader gets that phrase linked to `https://www.gymnasetips.com/muscle-up-progression/`,
because that is where the document says it came from. The link is verified by
reading the disk, not by trusting you: the file is there, and the address is there
because something actually fetched it.

**If the knowledge base does not hold the article, you cannot link it yet.**
Ingest it first — propose the search, wait for approval exactly as always, write
the document, then link it. A URL written from memory is the one kind of link that
is confidently wrong, so the builder will not take one.

| You wrote | Why it is rejected | What to do |
|---|---|---|
| `[text](https://…)` | A URL you typed cannot be checked against anything | Cite the document that holds it, or ingest the article and link that |
| `[text](conclusions/x.md)` | A conclusion is your reasoning, not source material | Link one of the documents it cites |
| A document whose `source:` is a sentence rather than an address | There is nothing to open | Leave it unlinked and name it in the prose |

Two things follow that are worth knowing. A link's text is never bolded and never
glossed, because being a link is already emphasis. And the `sources` block links
itself — every cited document becomes a link to its own source — so you do not
need to repeat those links in the prose.

**`blocks` is a list of any length, in any order, repeating types freely** — five
blocks or twenty, four `stat`s in a row, three `section`s between two `compare`s.
The order you write is the order the reader gets. The only fixed rule is that
`sources` comes last.

| Block | Use it for | Required |
|---|---|---|
| `section` | A paragraph or three under a short heading | `heading`, `body` |
| `stat` | One number that carries weight. Consecutive stats become one row — two to four reads best | `value`, `label` |
| `compare` | Two or three options along the same dimensions | `columns`, `rows` (every row as wide as `columns`) |
| `steps` | An ordered procedure. `heading` optional | `items` |
| `list` | Facts, items, criteria — no order implied. `heading` optional | `items` |
| `callout` | The one caveat worth interrupting for. `tone`: `note` or `warn` | `body` |
| `quote` | Words worth reproducing verbatim, from a source. `attribution` optional | `body` |
| `sources` | What the page was built from. **Mandatory, last block** | `items` |

An item of a `list` or `steps` is either a plain string or a group, and one block
may hold both:

```json
{"term": "Phase 1, weeks 1-6", "detail": "Low biceps load, 3x12-15.",
 "items": ["Seated row", "Serratus punch"]}
```

`term` is required and is a label of a few words, not a sentence. `detail` and
`items` are both optional, and sub-items are plain strings only. Reach for a group
when an item has a name *and* something to say under it; a bare fact stays a
string.

Optional top level: `page_id` (defaults to the slug; see Phase 1), `slug`
(defaults to a slug of the title), `lang` (defaults to `en`), `glossary` (below).

## The glossary — jargon without the interruption

An answer has to gloss its terms inline — *a reranker (a second pass that re-sorts
search results by relevance)* — and three of those in a paragraph is a paragraph
nobody finishes. On a page, the gloss moves out of the sentence: the term gets a
dotted underline, and tapping it shows the definition.

```json
"glossary": {"reranker": "a second pass that re-sorts search results by relevance"}
```

**You write plain prose and a flat map. You never mark a word up.** The builder
finds each term's **first** mention anywhere on the page — lede, sections, steps,
callouts, quotes — and links that one. Later mentions are left alone, because a
page that underlines every occurrence of its own subject is harder to read than
one that never defines it.

- **Match the prose, not the dictionary.** The term is matched whole-word and
  case-insensitively, so `reranker` catches `Reranker` but not `reranking`. A term
  the page never says is rejected — write it the way the prose writes it.
- **Eight terms maximum**, and fewer reads better. If a page needs more than a
  handful, its reader is not the outsider you said they were.
- **Gloss the vocabulary, not the argument.** A definition is a phrase that lets
  someone keep reading, not the point the section is making. If it takes two
  sentences, it is a `section`.
- Write the definition in the knowledge base's language, like everything else.

## The rules the builder enforces

- **At least two sources, each a file that exists** under the knowledge base root
  — same rule as a conclusion, for the same reason: a page nobody can trace is a
  poster, not knowledge.
- **Unknown block type, missing field, or a `compare` row of the wrong width**
  rejects the whole page. Nothing half-rendered ever ships.
- **Twenty-four blocks maximum.** Longer than that is a document; write a
  conclusion and build a page about one part of it.
- **A glossary term the page never says** rejects it too, as does a term shorter
  than two characters, a definition that is blank, or more than eight of them.
- **A bullet or a number starting a line inside a `body`** — that is a `list` or
  `steps` block written in the wrong place, and it renders as a run-on line.
- **An unpaired `**` or backtick**, which would otherwise reach the reader as a
  literal asterisk in the middle of a sentence.
- **More than a quarter of a field in bold**, once the field is long enough to
  have a shape at all.
- **A group with no `term`**, a `term` longer than eighty characters, an unknown
  key beside `term`, `detail` and `items`, or a sub-item that is not a plain
  string.
- **A link to anything but a document that carries a URL** — a URL you typed, a
  conclusion, a file that is not there, or a document whose origin is recorded in
  words rather than as an address.
- **A `page_id` that is not 1–60 lowercase letters, digits or hyphens**, a title
  whose file already belongs to a different id, or a `pages/manifest.json` that
  is not a JSON object — all rejected, nothing written. Two ids never share one
  file.

## Writing for the page

Follow the expert skill's answer rules — a capable outsider reads it once and
acts on it — with three additions the format demands:

- **The lede is the whole page in one sentence.** Most readers read the title, the
  lede, the stats, and leave. Make those four survive alone.
- **Headings are labels, not sentences.** Two to four words. They are rendered
  small and uppercase; a full sentence there reads as shouting.
- **A number needs its unit and its meaning**, exactly as in an answer: `52% → 62%
  accuracy`, never a bare metric name. A `stat` block with a number nobody can
  interpret is the most expensive kind of noise.

**Write the page in the knowledge base's language.** If `SCOPE.md` and the
conclusions are in Spanish, the title, lede and every block are in Spanish too.

## Red flags — stop

- Building without an explicit request → offer, then wait.
- Typing HTML anywhere — a file, a code fence, the reply → `content.json` and
  `build.py`. There is no case where hand-written markup is the right answer.
- "I can't attach files, so here is the page as text" → you can, and it is not
  text. Build it; it is delivered on its own.
- "Save this as report.html" → the user is on a phone. Build it.
- "They said report, not page, so this skill does not apply" → it applies.
- Building before the user confirmed the outline → phase 1 exists to make a wrong
  page cost one message instead of one page.
- Writing HTML or CSS anywhere → you write JSON; the design is not yours.
- A page with no conclusion behind it → save the reasoning first.
- `sources` citing a file you did not open, or that is not on disk → the builder
  rejects it, and it would have been a lie.
- Pasting the page, its JSON or its path into the reply → the bridge sends it.
- An outline with "and" in the one question → two pages. Pick one.
- Every block a `section` → you described the topic instead of laying it out.
  Re-read the outline and pick the block that matches each piece's shape.
- Bullets typed into a `body` → `list`, or `steps` if the order matters.
- Typing a URL anywhere → link the document that holds it. If the knowledge base
  does not have the article, ingest it first and link what you wrote.
- Linking a `conclusions/` file → that is your own reasoning, not something the
  reader can open. Link a document it cites.
- A `body` that names two or three phases and then describes each → one `list` of
  grouped items, with the phases as the terms.
- Bolding a whole sentence, a heading, or every other phrase → emphasis that marks
  everything marks nothing. One or two per block.
- Bold used to stand in for a heading → that is a grouped item's `term`.
- Wanting sub-items inside sub-items → two levels is the limit; the content is a
  document, so write the conclusion and build a page about one part of it.
- Rebuilding the whole page for a small fix → edit `content.json` and rerun with
  the same `page_id`; the id is stable, so the old file is replaced, never left
  beside the new one.
- A glossary term that repeats what the sentence already explains → drop one of
  them. Glossing a word you also defined in the prose wastes both.
- A new `page_id` for a page that updates an existing one → reuse the old id, or
  the knowledge base keeps two near-identical pages forever.
