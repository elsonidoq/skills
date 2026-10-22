"""Offline parser and renderer for historical open-issues Markdown.

This module deliberately has no subprocess or network dependency.  Later stages may
consume its ParsedRecord/Preview interfaces, but preview itself is read-only.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import posixpath
import re
import subprocess
from typing import Callable, Mapping
from urllib.parse import quote

_HEADING = re.compile(r"^## (OI-\d+):\s+(.+?)\s*$")
_FIELD = re.compile(r"^- \*\*(.+?):\*\*\s*(.*)$")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_OI_REFERENCE = re.compile(r"(?<![\w-])(OI-\d+)(?![\w-])")
_REQUIRED_FIELDS = ("Status", "Problem", "Primary evidence", "Resumption condition")
_SENSITIVE = re.compile(r"(?:BEGIN [A-Z ]*PRIVATE KEY|(?:api[_-]?key|token|password|secret)\s*[:=])", re.I)
_UNSAFE = re.compile(r"<\s*(?:script|iframe|object)\b|javascript\s*:", re.I)


@dataclass(frozen=True)
class Source:
    host: str
    repository: str
    path: str
    revision: str

    def __post_init__(self) -> None:
        if not self.host or not re.fullmatch(r"[A-Za-z0-9.-]+", self.host):
            raise ValueError("source host must be a hostname")
        if not re.fullmatch(r"[^/\s]+/[^/\s]+", self.repository):
            raise ValueError("source repository must be OWNER/REPO")
        if not self.path or self.path.startswith("/") or ".." in self.path.split("/"):
            raise ValueError("source path must be normalized and repository-relative")
        if not self.revision or any(c.isspace() for c in self.revision):
            raise ValueError("source revision is required")

    @property
    def blob_url(self) -> str:
        return f"https://{self.host}/{self.repository}/blob/{quote(self.revision, safe='')}/{quote(self.path, safe='/')}"


@dataclass(frozen=True)
class ParsedRecord:
    oi_id: str
    title: str
    fields: tuple[tuple[str, str], ...]
    excerpt: str
    line: int

    @property
    def field_map(self) -> dict[str, str]:
        return dict(self.fields)


@dataclass(frozen=True)
class Diagnostic:
    line: int
    reason: str
    oi_id: str | None = None


@dataclass(frozen=True)
class RenderedRecord:
    identity: str
    marker: str
    title: str
    state: str
    body: str
    original_entry_url: str
    original_excerpt: str
    fields: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Preview:
    source: Source
    destination: str
    records: tuple[RenderedRecord, ...]
    diagnostics: tuple[Diagnostic, ...]

    @property
    def counts(self) -> dict[str, int]:
        return {"records": len(self.records), "open": sum(r.state == "open" for r in self.records), "closed": sum(r.state == "closed" for r in self.records), "unmappable": len(self.diagnostics)}


@dataclass(frozen=True)
class RemoteIssue:
    number: int
    state: str
    body: str
    is_pull_request: bool = False


@dataclass(frozen=True)
class Reconciliation:
    record: RenderedRecord
    outcome: str
    issue: RemoteIssue | None = None
    detail: str | None = None


@dataclass(frozen=True)
class ReconciliationPreview:
    preview: Preview
    records: tuple[Reconciliation, ...]
    lookup_error: str | None = None


class IncompleteLookup(RuntimeError):
    """The complete destination snapshot could not be established safely."""


class GhApiTransport:
    """Read-only, explicit-target `gh api` boundary used by reconciliation."""

    api_version = "2022-11-28"

    def __init__(self, execute: Callable[[tuple[str, ...], str | None], str] | None = None):
        self._execute = execute or self._subprocess_execute

    @staticmethod
    def _subprocess_execute(argv: tuple[str, ...], stdin: str | None) -> str:
        completed = subprocess.run(argv, input=stdin, text=True, capture_output=True, check=False)
        if completed.returncode:
            raise IncompleteLookup(completed.stderr.strip() or f"gh exited {completed.returncode}")
        return completed.stdout

    def list_issues(self, host: str, destination: str) -> tuple[RemoteIssue, ...]:
        if not re.fullmatch(r"[A-Za-z0-9.-]+", host):
            raise ValueError("destination host must be a hostname")
        if not re.fullmatch(r"[^/\s]+/[^/\s]+", destination):
            raise ValueError("destination must be OWNER/REPO")
        argv = (
            "gh", "api", "--method", "GET", "--hostname", host, "--paginate", "--slurp",
            "--header", f"X-GitHub-Api-Version: {self.api_version}",
            f"repos/{destination}/issues?state=all&per_page=100",
        )
        try:
            raw = self._execute(argv, None)
            pages = json.loads(raw)
        except (IncompleteLookup, OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            raise IncompleteLookup(f"complete destination lookup unavailable: {error}") from error
        if not isinstance(pages, list) or any(not isinstance(page, list) for page in pages):
            raise IncompleteLookup("complete destination lookup returned an unexpected paginated response")
        issues: list[RemoteIssue] = []
        for page in pages:
            for item in page:
                if not isinstance(item, dict) or not isinstance(item.get("number"), int):
                    raise IncompleteLookup("complete destination lookup returned an invalid issue")
                body = item.get("body")
                state = item.get("state")
                if not isinstance(body, str) or not isinstance(state, str):
                    raise IncompleteLookup("complete destination lookup omitted issue body or state")
                issues.append(RemoteIssue(item["number"], state, body, "pull_request" in item))
        return tuple(issues)


def reconcile(
    proposal: Preview,
    transport: GhApiTransport,
    host: str,
    confirmed_mappings: Mapping[str, int] | None = None,
) -> ReconciliationPreview:
    """Compare a local preview with one complete read-only remote issue snapshot.

    This performs no create, update, close, or other mutation.  A mapping is only a
    caller-supplied reviewed choice for an already-existing issue; it never adopts by title.
    """
    try:
        issues = transport.list_issues(host, proposal.destination)
    except IncompleteLookup as error:
        detail = str(error)
        return ReconciliationPreview(proposal, tuple(Reconciliation(record, "incomplete lookup", detail=detail) for record in proposal.records), detail)

    by_number = {issue.number: issue for issue in issues if not issue.is_pull_request}
    mappings = confirmed_mappings or {}
    results: list[Reconciliation] = []
    for record in proposal.records:
        matches = [issue for issue in by_number.values() if issue.body.count(record.marker)]
        if len(matches) > 1 or any(issue.body.count(record.marker) != 1 for issue in matches):
            results.append(Reconciliation(record, "conflict", detail="duplicate exact provenance marker; inspect affected issues"))
            continue
        if not matches and record.identity in mappings:
            issue = by_number.get(mappings[record.identity])
            if issue is None:
                results.append(Reconciliation(record, "conflict", detail="reviewed mapping does not name a visible non-PR issue"))
            else:
                results.append(Reconciliation(record, "existing-issue mapping", issue, "reviewed mapping; preserve remote body and state"))
            continue
        if not matches:
            results.append(Reconciliation(record, "planned create"))
            continue
        issue = matches[0]
        if issue.state not in {"open", "closed"}:
            results.append(Reconciliation(record, "conflict", issue, "unknown remote state; inspect close ownership"))
        elif issue.body == record.body and issue.state == record.state:
            results.append(Reconciliation(record, "no-op", issue))
        else:
            results.append(Reconciliation(record, "conflict", issue, "remote body or state diverges; inspect before any change"))
    return ReconciliationPreview(proposal, tuple(results))


def parse_markdown(markdown: str) -> tuple[tuple[ParsedRecord, ...], tuple[Diagnostic, ...]]:
    """Parse OI headings and bullet fields while retaining each exact source excerpt."""
    lines = markdown.splitlines(keepends=True)
    starts: list[tuple[int, re.Match[str]]] = [(i, match) for i, line in enumerate(lines) if (match := _HEADING.match(line.rstrip("\n")))]
    records: list[ParsedRecord] = []
    diagnostics: list[Diagnostic] = []
    for index, (start, heading) in enumerate(starts):
        end = starts[index + 1][0] if index + 1 < len(starts) else len(lines)
        excerpt = "".join(lines[start:end]).rstrip("\n")
        fields: list[tuple[str, str]] = []
        current: list[str] | None = None
        for line in lines[start + 1:end]:
            match = _FIELD.match(line.rstrip("\n"))
            if match:
                if current is not None:
                    fields.append((current[0], current[1].rstrip("\n")))
                current = [match.group(1), match.group(2)]
            elif current is not None:
                current[1] += line
        if current is not None:
            fields.append((current[0], current[1].rstrip("\n")))
        records.append(ParsedRecord(heading.group(1), heading.group(2), tuple(fields), excerpt, start + 1))
    if not starts:
        diagnostics.append(Diagnostic(1, "no OI headings found"))
    return tuple(records), tuple(diagnostics)


def _entry_url(source: Source, record: ParsedRecord) -> str:
    slug = re.sub(r"[^a-z0-9 -]", "", f"{record.oi_id} {record.title}".lower())
    slug = re.sub(r"[ -]+", "-", slug).strip("-")
    return f"{source.blob_url}#{slug}"


def _render_markdown(value: str, source: Source) -> str:
    def link(match: re.Match[str]) -> str:
        text, target = match.groups()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)
        target_path, separator, anchor = target.partition("#")
        if not target_path or target_path.startswith(("/", "//")):
            return match.group(0)
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source.path), target_path))
        if resolved == ".." or resolved.startswith("../"):
            return match.group(0)
        url = f"https://{source.host}/{source.repository}/blob/{quote(source.revision, safe='')}/{quote(resolved, safe='/')}"
        return f"[{text}]({url}{'#' + anchor if separator else ''})"

    linked = _LINK.sub(link, value)
    # Never alter code spans: paths there are evidence, not verified links.
    parts = re.split(r"(`[^`]*`)", linked)
    for i in range(0, len(parts), 2):
        # The referenced title may be unavailable, so link to the immutable file
        # instead of inventing an unreliable heading anchor.
        parts[i] = _OI_REFERENCE.sub(lambda m: f"[{m.group(1)}]({source.blob_url})", parts[i])
    return "".join(parts)


def render_record(record: ParsedRecord, source: Source) -> RenderedRecord | Diagnostic:
    fields = record.field_map
    missing = [name for name in _REQUIRED_FIELDS if name not in fields]
    if missing:
        return Diagnostic(record.line, f"missing required field(s): {', '.join(missing)}", record.oi_id)
    status = fields["Status"].strip().lower()
    if status not in {"open", "closed"}:
        return Diagnostic(record.line, f"unmappable status: {fields['Status']!r}", record.oi_id)
    if _UNSAFE.search(record.excerpt):
        return Diagnostic(record.line, "unsafe Markdown structure rejected", record.oi_id)
    if _SENSITIVE.search(record.excerpt):
        return Diagnostic(record.line, "sensitive candidate data rejected; fidelity is unavailable", record.oi_id)
    identity = f"{source.host}/{source.repository}:{source.path}:{record.oi_id}"
    marker = f"<!-- import-open-issues: {identity} -->"
    original_url = _entry_url(source, record)
    sections = [marker, f"Historical source revision: `{source.revision}`", f"Original entry: [{record.oi_id}]({original_url})", ""]
    for name, value in record.fields:
        sections.extend((f"## {name}", _render_markdown(value, source), ""))
    sections.extend(("## Original Markdown excerpt", "```markdown", record.excerpt, "```"))
    return RenderedRecord(identity, marker, f"{record.oi_id}: {record.title}", status, "\n".join(sections), original_url, record.excerpt, record.fields)


def preview(markdown: str, source: Source, destination: str) -> Preview:
    """Return exact offline proposals. This function has no external side effects."""
    if not re.fullmatch(r"[^/\s]+/[^/\s]+", destination):
        raise ValueError("destination must be OWNER/REPO")
    parsed, diagnostics = parse_markdown(markdown)
    output: list[RenderedRecord] = []
    all_diagnostics = list(diagnostics)
    seen: set[str] = set()
    for record in parsed:
        if record.oi_id in seen:
            all_diagnostics.append(Diagnostic(record.line, "duplicate OI identity in source", record.oi_id))
            continue
        seen.add(record.oi_id)
        rendered = render_record(record, source)
        if isinstance(rendered, Diagnostic):
            all_diagnostics.append(rendered)
        else:
            output.append(rendered)
    return Preview(source, destination, tuple(output), tuple(all_diagnostics))
