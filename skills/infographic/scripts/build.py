"""Render a standalone infographic page from a content JSON file.

    python scripts/build.py <kb-root> <content.json>

The agent writes CONTENT, never markup: a title, a lede, and a list of blocks
drawn from a fixed vocabulary. This script owns every layout decision, so two
pages built a month apart are identical in look and a weak-at-design model cannot
produce a page that reads badly. There is no escape hatch on purpose -- an
``html`` block would put the design back in the model's hands, which is the one
thing this script exists to prevent.

The page is written to ``<kb-root>/pages/<slug>.html`` and its path is appended to
``<kb-root>/.outbox/pending``. The bridge reads that file to know what to send;
nothing is parsed out of the model's reply, so a page either exists on disk or was
never built. The page's id (content "page_id", default: its slug) is recorded in
<kb-root>/pages/manifest.json, and rebuilding under the same id deletes the
previously built file.

Exit codes
    0  page written
    2  missing file, unreadable JSON
    3  content rejected -- unknown block, missing field, or fewer than two
       sources that exist on disk. NO page was written.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse

MINIMUM_SOURCES = 2
MAX_BLOCKS = 24
MAX_GLOSSARY = 8

# A bullet typed into prose. The body is one paragraph, so single newlines inside
# it collapse and the "list" renders as a run-on line of bullet characters.
MANUAL_BULLET = re.compile(r"^[ \t]*(?:[-*\u2022\u00b7\u2023\u25aa]|\d+[.)])\s+", re.MULTILINE)

# Non-greedy and DOTALL-free on purpose: a stray "**" earlier in the text must not
# swallow everything up to the next one several paragraphs later.
BOLD = re.compile(r"\*\*(.+?)\*\*")
CODE = re.compile(r"`([^`\n]+)`")
TAGS = re.compile(r"(<[^>]*>)")

# A link is markdown-shaped, never spans a line, and never swallows a following
# parenthesis. Its target is always a knowledge-base path: see Links.
LINK = re.compile(r"\[([^\]\n]+)\]\(([^)\s]+)\)")
SOURCE_FIELD = re.compile(r"^source:\s*(.+?)\s*$", re.MULTILINE)
URL_SCHEME = re.compile(r"^https?://", re.IGNORECASE)
# A file:// link opens a real local file -- e.g. another built page -- rather than
# web source material. It is verified by a disk read like everything else here.
FILE_SCHEME = re.compile(r"^file://", re.IGNORECASE)

ITEM_KEYS = ("term", "detail", "items")
MAX_TERM = 80
EMPHASIS_MIN_LEN = 120
EMPHASIS_MAX_SHARE = 0.25

PAGE_ID = re.compile(r"^[a-z0-9-]{1,60}$")
MANIFEST_NAME = "manifest.json"


def manual_bullets(text: str) -> str | None:
    """The first bullet line in a prose body, if it writes its own list."""
    match = MANUAL_BULLET.search(str(text))
    if match is None:
        return None
    line = str(text)[match.start():].splitlines()[0].strip()
    return line[:40]


def bullet_problem(where: str, bullet: str) -> str:
    return (f"{where}: writes its own list ({bullet!r}). A body is one paragraph, so those "
            "lines run together -- use a 'list' block, or 'steps' when the order matters")


def emphasis_problems(text: str, label: str) -> list[str]:
    """**bold** and `code` syntax errors in one field, checked on the raw text.

    Checked before escaping: the model typed these markers itself, so the count of
    literal ``**``/backtick characters is what tells us it forgot to close one.
    """
    text = str(text)
    problems = []
    if text.count("**") % 2 == 1:
        problems.append(f"{label}: odd number of ** markers, which would render as "
                        "a literal asterisk")
    if text.count("`") % 2 == 1:
        problems.append(f"{label}: an unclosed backtick")
    if len(text) >= EMPHASIS_MIN_LEN:
        bolded = sum(len(m.group(1)) for m in BOLD.finditer(text))
        if bolded > EMPHASIS_MAX_SHARE * len(text):
            problems.append(f"{label}: more than a quarter of the field is bolded -- "
                            "bolding everything is bolding nothing")
    return problems


def file_url_path(url: str) -> Path | None:
    """The local path a file:// URL names, or None when it is not a usable local URL."""
    parsed = urlparse(url)
    if parsed.scheme.lower() != "file":
        return None
    if parsed.netloc not in ("", "localhost"):
        return None
    path = unquote(parsed.path)
    return Path(path) if path else None


def document_source(path: Path) -> str | None:
    """The address a document was fetched from, read out of its frontmatter.

    Only the frontmatter is scanned. A document's body can legitimately contain a
    line beginning "source:", and that is prose, not provenance.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:4000]
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    match = SOURCE_FIELD.search(text[:end] if end != -1 else text)
    return match.group(1).strip() if match else None


def link_target_problem(target: str, kb_root: Path) -> str | None:
    """Why this link cannot be built, or None if it opens real source material."""
    if FILE_SCHEME.match(target):
        path = file_url_path(target)
        if path is None or not path.is_file():
            return (f"{target} does not name a local file that exists -- a file:// "
                    "link must open a real file on disk")
        return None
    if URL_SCHEME.match(target):
        return ("a page cannot link a URL directly -- cite the document that holds it, "
                "and if the knowledge base does not have that article yet, ingest it "
                "first and link the document you wrote")
    if not (kb_root / target).is_file():
        return (f"{target} is not a file in the knowledge base -- a page can only link "
                "a document it already holds")
    source = document_source(kb_root / target)
    if source is None:
        return (f"{target} has no source: header, which is what a conclusion looks like "
                "-- a conclusion is your own reasoning, not source material, so link one "
                "of the documents it cites")
    if not (URL_SCHEME.match(source) or FILE_SCHEME.match(source)):
        return (f"{target} records where it came from in words rather than as an address "
                f"({source[:40]!r}), so there is nothing for the reader to open")
    return None


def link_problems(text: object, label: str, kb_root: Path) -> list[str]:
    problems = []
    for match in LINK.finditer(str(text)):
        if not match.group(1).strip():
            problems.append(f"{label}: a link with no text")
        problem = link_target_problem(match.group(2), kb_root)
        if problem:
            problems.append(f"{label}: {problem}")
    return problems


def emphasize(text: str) -> str:
    """Turn **bold** and `code` into tags, in text that is already escaped.

    Split on tags first so the two regexes never have to reason about angle
    brackets: esc() has already turned every literal ``<`` into ``&lt;``, so the
    only real tags left are ones this builder inserted (a gloss button, say), and
    those must render exactly as built, not get re-parsed as prose.
    """
    parts = TAGS.split(text)
    for i in range(0, len(parts), 2):  # odd indices are the captured tags themselves
        parts[i] = CODE.sub(r"<code>\1</code>", parts[i])
        parts[i] = BOLD.sub(r"<strong>\1</strong>", parts[i])
    return "".join(parts)


def inline(text: object, gloss: "Glossary | None" = None,
           links: "Links | None" = None) -> str:
    """The one path every prose field takes.

    Escape, stash links, glossary-link, emphasize, restore links. The order
    matters: the glossary runs on plain escaped text (so a term can't match inside
    markup we just inserted), emphasis runs last so it only has to skip a gloss
    button's tags, and links are stashed around both so a resolved address is never
    exposed to a pass that might rewrite it.

    A consequence, and a deliberate one: a link's anchor text is neither glossed
    nor emphasized. Being a link is already emphasis; bolding inside one is noise.
    """
    escaped = esc(text)
    stashed = links.stash(escaped) if links else escaped
    linked = gloss.apply(stashed) if gloss else stashed
    emphasized = emphasize(linked)
    return links.restore(emphasized) if links else emphasized

BLOCK_FIELDS = {
    "section": ("heading", "body"),
    "stat": ("value", "label"),
    "compare": ("columns", "rows"),
    "steps": ("items",),
    "list": ("items",),
    "callout": ("body",),
    "quote": ("body",),
    "sources": ("items",),
}

PAGE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}</style>
</head>
<body>
<main>
{body}</main>
{script}</body>
</html>
"""


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug or "page")[:60]


def esc(value: object) -> str:
    return html.escape(str(value), quote=False)


def paragraphs(body: str, gloss: "Glossary | None" = None,
               links: "Links | None" = None) -> str:
    """Split a body string on blank lines. The model writes prose, not markup."""
    out = []
    for para in re.split(r"\n\s*\n", str(body)):
        if not para.strip():
            continue
        out.append(f"<p>{inline(para.strip(), gloss, links)}</p>\n")
    return "".join(out)


class Glossary:
    """Turns the first mention of each term into a term with a tooltip.

    The model supplies plain prose and a flat ``term: definition`` map; it never
    marks a word up. That is the whole point -- an inline syntax is one more thing
    to get subtly wrong, and a half-written marker would show up as literal
    punctuation in the middle of a sentence.

    Only the *first* mention is linked. A page that underlines every occurrence of
    its own subject is harder to read than one that never defines it.
    """

    def __init__(self, terms: dict | None):
        self.terms = terms or {}
        self.pending = {t: str(d) for t, d in self.terms.items()}
        self.count = 0

    @property
    def unused(self) -> list[str]:
        return list(self.pending)

    def apply(self, escaped: str) -> str:
        """Link terms inside ALREADY-ESCAPED text, so no markup can come in with it.

        Text already turned into markup is held aside rather than rescanned: one
        term's definition routinely contains another term, and substituting there
        would nest a tooltip inside a tooltip.
        """
        segments: list[tuple[str, bool]] = [(escaped, True)]  # (text, still substitutable)
        for term in list(self.pending):
            pattern = re.compile(rf"(?<![\w-]){re.escape(esc(term))}(?![\w-])", re.IGNORECASE)
            out: list[tuple[str, bool]] = []
            hit = False
            for text, free in segments:
                match = pattern.search(text) if free and not hit else None
                if match is None:
                    out.append((text, free))
                    continue
                out.append((text[:match.start()], True))
                out.append((self._markup(match.group(0), self.pending[term]), False))
                out.append((text[match.end():], True))
                hit = True
            if hit:
                segments = out
                del self.pending[term]
                self.count += 1
        return "".join(text for text, _ in segments)

    @staticmethod
    def _markup(term: str, definition: str) -> str:
        return ("<button class=\"gloss\" type=\"button\" aria-expanded=\"false\">"
                f"{term}<span class=\"gloss-text\">{emphasize(esc(definition))}</span></button>")


def prose_fields(block: dict, where: str) -> list[tuple[str, str]]:
    """(label, text) pairs for every field of this block that carries emphasis.

    Headings, sources items, and a stat's value/label are labels, not sentences --
    they never take **bold** or `code`, so they are not in this list.
    """
    kind = block.get("type")
    fields: list[tuple[str, str]] = []
    if kind in ("section", "callout", "quote") and block.get("body"):
        fields.append((f"{where} ({kind}): body", block["body"]))
    if kind == "stat" and block.get("note"):
        fields.append((f"{where} (stat): note", block["note"]))
    if kind == "compare":
        for c, col in enumerate(block.get("columns") or []):
            fields.append((f"{where} (compare): column {c}", col))
        for r, row in enumerate(block.get("rows") or []):
            if isinstance(row, list):
                for c, cell in enumerate(row):
                    fields.append((f"{where} (compare): row {r} cell {c}", cell))
    if kind in ("list", "steps"):
        for j, item in enumerate(block.get("items") or []):
            if isinstance(item, str):
                fields.append((f"{where} ({kind}): item {j}", item))
            elif isinstance(item, dict):
                if item.get("term"):
                    fields.append((f"{where} ({kind}): item {j} term", item["term"]))
                if item.get("detail"):
                    fields.append((f"{where} ({kind}): item {j} detail", item["detail"]))
                for s, sub in enumerate(item.get("items") or []):
                    if isinstance(sub, str):
                        fields.append((f"{where} ({kind}): item {j} sub-item {s}", sub))
    return fields


def check_grouped_item(item: dict, where: str) -> list[str]:
    """A list/steps item that groups a term with a detail and sub-items.

    Structural checks only -- the term/detail/sub-item text itself is validated
    like any other prose field by ``prose_fields`` and ``emphasis_problems``.
    """
    problems = []
    term = item.get("term")
    if not str(term or "").strip():
        problems.append(f"{where}: has no term")
    elif len(str(term)) > MAX_TERM:
        problems.append(f"{where}: term is longer than {MAX_TERM} characters -- "
                        "it is a label, not a sentence")
    unknown = sorted(set(item) - set(ITEM_KEYS))
    if unknown:
        problems.append(f"{where}: unknown key {unknown[0]!r}, allowed keys are "
                        f"{', '.join(ITEM_KEYS)}")
    detail = item.get("detail")
    if detail:
        bullet = manual_bullets(detail)
        if bullet:
            problems.append(bullet_problem(f"{where} detail", bullet))
    subitems = item.get("items")
    if subitems is not None:
        if not isinstance(subitems, list):
            problems.append(f"{where}: items must be a list -- only one level of nesting")
        else:
            for s, sub in enumerate(subitems):
                if not isinstance(sub, str):
                    problems.append(f"{where}: sub-item {s} is not a string -- "
                                    "only one level of nesting")
                else:
                    bullet = manual_bullets(sub)
                    if bullet:
                        problems.append(bullet_problem(f"{where} sub-item {s}", bullet))
    return problems


class Links:
    """Resolves [text](documents/x.md) to the address that document was fetched from.

    A link on a page opens the **source material** -- the article, the paper -- and
    never a file in the knowledge base, which the reader has no way to open. So the
    model never types a URL: it names a document it already holds, and the address
    comes off that document's own header, where it sits because something actually
    fetched it. Verification is therefore a disk read rather than a network call:
    it cannot hang, cannot fail offline, cannot be refused by a publisher that
    answers a bot with 403, and cannot be fooled by a URL the model invented.

    When the knowledge base does not hold the article, the answer is to ingest it
    and link the document that produces -- not to relax this.

    A ``file://`` target is the deliberate exception: it opens a real local file
    (for example another built page) and is verified by the same disk read.
    """

    def __init__(self, kb_root: Path):
        self.kb_root = kb_root
        self._stash: list[str] = []
        self._source: dict[str, str | None] = {}

    def source_of(self, target: str) -> str | None:
        if target not in self._source:
            self._source[target] = document_source(self.kb_root / target)
        return self._source[target]

    def url_for(self, target: str) -> str | None:
        if FILE_SCHEME.match(target):
            path = file_url_path(target)
            return target if path and path.is_file() else None
        source = self.source_of(target)
        return source if source and (URL_SCHEME.match(source) or FILE_SCHEME.match(source)) else None

    def anchor(self, url: str, text: str) -> str:
        """``text`` is already escaped; the href is escaped for an attribute."""
        return f"<a href=\"{html.escape(url, quote=True)}\">{text}</a>"

    def stash(self, escaped: str) -> str:
        """Links out, placeholders in.

        The placeholder holds nothing but control characters and digits, so no
        glossary term can match inside it and no address is ever visible to a later
        pass. That is the whole trick, and it is why neither Glossary nor emphasize
        needs to know that links exist.
        """
        def take(match: re.Match) -> str:
            url = self.url_for(match.group(2))
            # validate() has already rejected a target with no address, so this only
            # falls back when render is driven directly, as the tests do.
            self._stash.append(self.anchor(url, match.group(1)) if url else match.group(0))
            return f"\x00{len(self._stash) - 1}\x00"
        return LINK.sub(take, escaped)

    def restore(self, text: str) -> str:
        return re.sub(r"\x00(\d+)\x00", lambda m: self._stash[int(m.group(1))], text)


class Rejected(Exception):
    """Content the page cannot be built from. Carries every problem at once."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


def read_manifest(pages: Path) -> dict:
    """``pages/manifest.json``: page id -> {file, title, built}. Missing means empty.

    A manifest that exists but cannot be read is rejected rather than replaced:
    silently overwriting it would orphan every page it named.
    """
    path = pages / MANIFEST_NAME
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise Rejected([f"pages/{MANIFEST_NAME} is not valid JSON ({e}) -- fix or delete it"])
    if not isinstance(data, dict):
        raise Rejected([f"pages/{MANIFEST_NAME} is not a JSON object -- fix or delete it"])
    # Every `file` names a page inside pages/ and nothing else. Entries are
    # read back to delete the old file on a retitle, so a path with a
    # separator or a `..` component would reach outside pages/ entirely.
    for pid, entry in data.items():
        if not isinstance(entry, dict) or "file" not in entry:
            continue
        name = entry["file"]
        if (not isinstance(name, str) or not name.endswith(".html")
                or "/" in name or "\\" in name or name in ("", ".", "..")
                or Path(name).name != name):
            raise Rejected([f"pages/{MANIFEST_NAME}: entry {pid!r} has file {name!r} -- "
                            "must be a bare *.html filename inside pages/, "
                            "fix or delete it"])
    return data


def write_manifest(pages: Path, manifest: dict) -> None:
    tmp = pages / (MANIFEST_NAME + ".tmp")
    tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    os.replace(tmp, pages / MANIFEST_NAME)


def validate(content: dict, kb_root: Path) -> list[str]:
    problems: list[str] = []
    for field in ("title", "lede", "blocks"):
        if not content.get(field):
            problems.append(f"missing required field: {field}")
    page_id = content.get("page_id")
    if page_id is not None and not PAGE_ID.match(str(page_id)):
        problems.append(f"page_id {page_id!r} must be 1-60 lowercase letters, digits or hyphens")
    blocks = content.get("blocks") or []
    if not isinstance(blocks, list):
        return problems + ["blocks must be a list"]
    if len(blocks) > MAX_BLOCKS:
        problems.append(f"{len(blocks)} blocks, maximum is {MAX_BLOCKS} -- "
                        "an infographic that long is a document, write a conclusion instead")

    sourced = False
    for i, block in enumerate(blocks):
        where = f"block {i}"
        if not isinstance(block, dict):
            problems.append(f"{where}: not an object")
            continue
        kind = block.get("type")
        if kind not in BLOCK_FIELDS:
            problems.append(f"{where}: unknown type {kind!r}, "
                            f"pick one of {', '.join(sorted(BLOCK_FIELDS))}")
            continue
        for field in BLOCK_FIELDS[kind]:
            if not block.get(field):
                problems.append(f"{where} ({kind}): missing field {field!r}")
        if kind == "compare" and isinstance(block.get("rows"), list):
            width = len(block.get("columns") or [])
            for r, row in enumerate(block["rows"]):
                if not isinstance(row, list) or len(row) != width:
                    problems.append(f"{where} (compare): row {r} has "
                                    f"{len(row) if isinstance(row, list) else '?'} cells, "
                                    f"columns declares {width}")
        if kind == "sources":
            sourced = True
            items = block.get("items") or []
            if len(items) < MINIMUM_SOURCES:
                problems.append(f"{where} (sources): cites {len(items)} file(s), "
                                f"needs at least {MINIMUM_SOURCES}")
            for item in items:
                if not (kb_root / str(item)).exists():
                    problems.append(f"{where} (sources): {item} is not on disk")
    if not sourced:
        problems.append("no sources block -- every page cites the knowledge base "
                        f"it was built from, at least {MINIMUM_SOURCES} files")

    for i, block in enumerate(blocks):
        if not isinstance(block, dict):
            continue
        where = f"block {i}"
        kind = block.get("type")
        if block.get("body"):
            bullet = manual_bullets(block["body"])
            if bullet:
                problems.append(bullet_problem(f"{where} ({kind})", bullet))
        if kind in ("list", "steps"):
            for j, item in enumerate(block.get("items") or []):
                if isinstance(item, dict):
                    problems.extend(check_grouped_item(item, f"{where} ({kind}): item {j}"))
        for label, text in prose_fields(block, where):
            problems.extend(emphasis_problems(text, label))
            problems.extend(link_problems(text, label, kb_root))
        # A heading renders escaped and unprocessed, so link syntax there would reach
        # the reader as literal brackets rather than as nothing.
        if block.get("heading") and LINK.search(str(block["heading"])):
            problems.append(f"{where} ({kind}): a heading cannot hold a link -- it is a "
                            "label, so put the link in the prose beneath it")
    if content.get("lede"):
        bullet = manual_bullets(content["lede"])
        if bullet:
            problems.append("the lede writes its own list; it is one sentence, not a summary")
        problems.extend(emphasis_problems(content["lede"], "lede"))
        problems.extend(link_problems(content["lede"], "lede", kb_root))

    glossary = content.get("glossary") or {}
    if not isinstance(glossary, dict):
        problems.append("glossary must be an object of term: definition")
    else:
        if len(glossary) > MAX_GLOSSARY:
            problems.append(f"{len(glossary)} glossary terms, maximum is {MAX_GLOSSARY} -- "
                            "a page of dotted words is harder to read than one that "
                            "explains its terms in the prose")
        for term, definition in glossary.items():
            if len(str(term).strip()) < 2:
                problems.append(f"glossary term {term!r} is too short to underline")
            if not str(definition).strip():
                problems.append(f"glossary term {term!r} has no definition")
            else:
                label = f"glossary term {term!r}"
                problems.extend(emphasis_problems(str(definition), label))
                problems.extend(link_problems(str(definition), label, kb_root))
    return problems


def render_stat(block: dict, gloss: "Glossary | None" = None,
                links: "Links | None" = None) -> str:
    # value and label are numbers/short labels, never prose -- no emphasis, no glossary.
    note = block.get("note")
    return ("<div class=\"stat\">"
            f"<span class=\"value\">{esc(block['value'])}</span>"
            f"<span class=\"label\">{esc(block['label'])}</span>"
            + (f"<span class=\"note\">{inline(note, gloss, links)}</span>" if note else "")
            + "</div>\n")


def render_item(item: object, gloss: Glossary, links: "Links | None" = None) -> str:
    """A plain string renders as it always has; an object groups a term with an
    optional detail paragraph and an optional flat run of sub-items."""
    if not isinstance(item, dict):
        return f"<li>{inline(item, gloss, links)}</li>\n"
    detail = item.get("detail")
    subitems = item.get("items") or []
    out = [f"<li class=\"grouped\">\n<h3>{inline(item['term'], gloss, links)}</h3>\n"]
    if detail:
        out.append(f"<p>{inline(detail, gloss, links)}</p>\n")
    if subitems:
        subs = "".join(f"<li>{inline(s, gloss, links)}</li>\n" for s in subitems)
        out.append(f"<ul class=\"sub\">\n{subs}</ul>\n")
    out.append("</li>\n")
    return "".join(out)


def wrap(kind: str, inner: str) -> str:
    """Every top-level block is one <section>, so a heading can never orphan from
    the content it titles and every block gets a section's spacing. ``sources`` is
    the one exception: it already is a section, styled by its own class."""
    return f"<section class=\"block block-{kind}\">\n{inner}</section>\n"


def render_block(block: dict, gloss: Glossary, links: "Links | None" = None) -> str:
    kind = block["type"]
    if kind == "section":
        return wrap(kind, f"<h2>{esc(block['heading'])}</h2>\n"
                    f"{paragraphs(block['body'], gloss, links)}")
    if kind == "compare":
        head = "".join(f"<th>{inline(c, gloss, links)}</th>" for c in block["columns"])
        rows = "".join("<tr>" + "".join(f"<td>{inline(c, gloss, links)}</td>" for c in row) + "</tr>\n"
                       for row in block["rows"])
        table = ("<div class=\"table-wrap\">\n<table>\n"
                f"<thead><tr>{head}</tr></thead>\n<tbody>\n{rows}</tbody>\n</table>\n</div>\n")
        return wrap(kind, table)
    if kind in ("steps", "list"):
        tag, css = ("ol", "steps") if kind == "steps" else ("ul", "facts")
        items = "".join(render_item(i, gloss, links) for i in block["items"])
        head = f"<h2>{esc(block['heading'])}</h2>\n" if block.get("heading") else ""
        return wrap(kind, f"{head}<{tag} class=\"{css}\">\n{items}</{tag}>\n")
    if kind == "callout":
        tone = "warn" if block.get("tone") == "warn" else "note"
        return wrap(kind, f"<div class=\"callout {tone}\">\n{paragraphs(block['body'], gloss, links)}</div>\n")
    if kind == "quote":
        who = block.get("attribution")
        quote = ("<blockquote>\n"
                f"{paragraphs(block['body'], gloss, links)}"
                + (f"<span class=\"attribution\">{esc(who)}</span>\n" if who else "")
                + "</blockquote>\n")
        return wrap(kind, quote)
    if kind == "sources":
        # The visible text stays the knowledge-base path, because that is what makes
        # the page traceable; the link is what makes it openable. A conclusion, or a
        # document whose origin is a sentence, simply stays unlinked.
        cells = []
        for item in block["items"]:
            code = f"<code>{esc(item)}</code>"
            url = links.url_for(str(item)) if links else None
            cells.append(f"<li>{links.anchor(url, code) if url else code}</li>\n")
        items = "".join(cells)
        return ("<section class=\"sources\">\n<h2>Sources</h2>\n"
                f"<ul>\n{items}</ul>\n</section>\n")
    raise AssertionError(f"unrendered block type {kind!r}")  # validate() gates this


def render_body(blocks: list[dict], gloss: "Glossary | None" = None,
                links: "Links | None" = None) -> str:
    """Render blocks, grouping runs of stats into one row."""
    gloss = gloss or Glossary({})
    out: list[str] = []
    run: list[dict] = []

    def flush() -> None:
        if run:
            stats = "<div class=\"stats\">\n" + "".join(render_stat(s, gloss, links) for s in run) + "</div>\n"
            out.append(wrap("stats", stats))
            run.clear()

    for block in blocks:
        if block["type"] == "stat":
            run.append(block)
            continue
        flush()
        out.append(render_block(block, gloss, links))
    flush()
    return "".join(out)


def render(content: dict, css: str, gloss: Glossary, js: str = "",
           links: "Links | None" = None) -> str:
    # The lede goes through inline() like every other prose field. It used to be
    # glossed and escaped by hand here, which quietly meant a bolded lede rendered
    # its asterisks literally.
    body = (f"<h1>{esc(content['title'])}</h1>\n"
            f"<p class=\"lede\">{inline(content['lede'], gloss, links)}</p>\n"
            + render_body(content["blocks"], gloss, links))
    # A page with no glossed term gets no script at all, so most pages stay pure
    # markup that opens correctly anywhere.
    script = f"<script>\n{js}</script>\n" if gloss.count and js else ""
    return PAGE.format(lang=esc(content.get("lang", "en")), title=esc(content["title"]),
                       css=css, body=body, script=script)


def build(kb_root: Path, content: dict, css: str, js: str = "") -> Path:
    problems = validate(content, kb_root)
    if problems:
        raise Rejected(problems)

    # Rendered before anything is written, because a term the prose never mentions
    # is only discoverable by trying to link it.
    gloss = Glossary(content.get("glossary"))
    page_html = render(content, css, gloss, js, Links(kb_root))
    if gloss.unused:
        raise Rejected([f"glossary term {t!r} never appears in the page's prose -- "
                        "the page says it differently, or the term is dead weight"
                        for t in gloss.unused])

    slug = slugify(content.get("slug") or content["title"])
    page_id = str(content.get("page_id") or slug)
    pages = kb_root / "pages"
    pages.mkdir(parents=True, exist_ok=True)
    manifest = read_manifest(pages)
    filename = f"{slug}.html"
    owner = next((pid for pid, entry in manifest.items()
                  if isinstance(entry, dict) and entry.get("file") == filename and pid != page_id),
                 None)
    if owner is not None:
        raise Rejected([f"pages/{filename} already belongs to page id {owner!r} -- "
                        "reuse that page_id, or change the title"])
    previous = manifest.get(page_id)
    previous_file = previous.get("file") if isinstance(previous, dict) else None

    page = pages / filename
    page.write_text(page_html, encoding="utf-8")
    # Same id, new title: the old file is deleted in the same step, so a retitle
    # can no longer orphan a page by construction rather than by someone noticing.
    if previous_file and previous_file != filename:
        (pages / previous_file).unlink(missing_ok=True)
    manifest[page_id] = {"file": filename, "title": str(content["title"]),
                         "built": date.today().isoformat()}
    write_manifest(pages, manifest)

    # The outbox is the bridge's only channel. It is dot-prefixed and deleted
    # after delivery, so it never reaches a commit.
    outbox = kb_root / ".outbox"
    outbox.mkdir(exist_ok=True)
    with (outbox / "pending").open("a", encoding="utf-8") as fh:
        fh.write(f"{page.relative_to(kb_root)}\n")
    return page


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kb_root", type=Path)
    ap.add_argument("content", type=Path, help="JSON file: title, lede, blocks")
    args = ap.parse_args(argv)

    if not args.kb_root.is_dir():
        print(f"not a directory: {args.kb_root}", file=sys.stderr)
        return 2
    try:
        content = json.loads(args.content.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"no such file: {args.content}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"{args.content} is not valid JSON: {e}", file=sys.stderr)
        return 2
    if not isinstance(content, dict):
        print(f"{args.content} must hold a JSON object", file=sys.stderr)
        return 2

    assets = Path(__file__).resolve().parent.parent / "assets"
    css = (assets / "page.css").read_text(encoding="utf-8")
    js = (assets / "page.js").read_text(encoding="utf-8")
    try:
        page = build(args.kb_root, content, css, js)
    except Rejected as e:
        print("no page written:", file=sys.stderr)
        for problem in e.problems:
            print(f"  - {problem}", file=sys.stderr)
        return 3
    print(page)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
