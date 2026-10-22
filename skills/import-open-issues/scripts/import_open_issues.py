"""Offline parser and renderer for historical open-issues Markdown.

This module deliberately has no subprocess or network dependency.  Later stages may
consume its ParsedRecord/Preview interfaces, but preview itself is read-only.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
import posixpath
import re
import subprocess
from typing import Callable, Collection, Mapping
from urllib.parse import quote

_HEADING = re.compile(r"^## (OI-\d+):\s+(.+?)\s*$")
_FIELD = re.compile(r"^- \*\*(.+?):\*\*\s*(.*)$")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_MARKDOWN_TOKEN = re.compile(r"(?P<ticks>`+).*?(?P=ticks)|\[[^\]]+\]\([^)]+\)", re.S)
# Code spans are skipped before diagnosing bracket nesting unsupported by _LINK.
_NESTED_LABEL = re.compile(r"(?P<ticks>`+).*?(?P=ticks)|(?P<nested>\[[^\]\n]*\[)", re.S)
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

    @property
    def pending_close_body(self) -> str:
        """The only recognized import-owned intermediate state for closed records."""
        if self.state != "closed":
            return self.body
        return self.body.replace("<!-- import-open-issues-closure: closed -->", "<!-- import-open-issues-closure: pending -->", 1)


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
    title: str
    state: str
    body: str
    is_pull_request: bool = False
    state_reason: str | None = None


@dataclass(frozen=True)
class Reconciliation:
    record: RenderedRecord
    outcome: str
    issue: RemoteIssue | None = None
    detail: str | None = None


@dataclass(frozen=True)
class ReconciliationPreview:
    preview: Preview
    host: str
    records: tuple[Reconciliation, ...]
    lookup_error: str | None = None
    uncertain_identities: frozenset[str] = frozenset()


class IncompleteLookup(RuntimeError):
    """The complete destination snapshot could not be established safely."""


@dataclass(frozen=True)
class ApplyAuthorization:
    """An operator's explicit confirmation of the named destination write scope."""

    host: str
    destination: str
    write_scope: str


@dataclass(frozen=True)
class ApplyResult:
    record: RenderedRecord
    outcome: str
    issue: RemoteIssue | None = None
    detail: str | None = None


@dataclass(frozen=True)
class ApplyReport:
    preview: Preview
    records: tuple[ApplyResult, ...]


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
        return tuple(self._issue(item, "complete destination lookup") for page in pages for item in page)

    @staticmethod
    def _issue(item: object, operation: str) -> RemoteIssue:
        if not isinstance(item, dict) or not isinstance(item.get("number"), int):
            raise IncompleteLookup(f"{operation} returned an invalid issue")
        title = item.get("title")
        body = item.get("body")
        state = item.get("state")
        # GitHub represents an issue with no description as JSON null; it cannot
        # contain an import marker, so normalize it for exact marker comparison.
        if body is None:
            body = ""
        if not isinstance(title, str) or not isinstance(body, str) or not isinstance(state, str):
            raise IncompleteLookup(f"{operation} omitted issue title, body, or state")
        state_reason = item.get("state_reason")
        if state_reason is not None and not isinstance(state_reason, str):
            raise IncompleteLookup(f"{operation} returned an invalid state reason")
        return RemoteIssue(item["number"], title, state, body, "pull_request" in item, state_reason)

    def get_issue(self, host: str, destination: str, number: int) -> RemoteIssue:
        if not isinstance(number, int) or number < 1:
            raise ValueError("issue number must be positive")
        argv = (
            "gh", "api", "--method", "GET", "--hostname", host,
            "--header", f"X-GitHub-Api-Version: {self.api_version}",
            f"repos/{destination}/issues/{number}",
        )
        try:
            return self._issue(json.loads(self._execute(argv, None)), "issue readback")
        except (IncompleteLookup, OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            raise IncompleteLookup(f"issue readback unavailable: {error}") from error

    def create_issue(self, host: str, destination: str, record: RenderedRecord, body: str | None = None) -> RemoteIssue:
        argv = (
            "gh", "api", "--method", "POST", "--hostname", host, "--input", "-",
            "--header", f"X-GitHub-Api-Version: {self.api_version}",
            f"repos/{destination}/issues",
        )
        payload = json.dumps({"title": record.title, "body": record.body if body is None else body})
        try:
            return self._issue(json.loads(self._execute(argv, payload)), "issue create")
        except (IncompleteLookup, OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            raise IncompleteLookup(f"issue create outcome unknown: {error}") from error

    def close_issue(self, host: str, destination: str, number: int, record: RenderedRecord) -> RemoteIssue:
        argv = (
            "gh", "api", "--method", "PATCH", "--hostname", host, "--input", "-",
            "--header", f"X-GitHub-Api-Version: {self.api_version}",
            f"repos/{destination}/issues/{number}",
        )
        payload = json.dumps({"body": record.body, "state": "closed", "state_reason": None})
        try:
            return self._issue(json.loads(self._execute(argv, payload)), "issue close")
        except (IncompleteLookup, OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            raise IncompleteLookup(f"issue close outcome unknown: {error}") from error


def reconcile(
    proposal: Preview,
    transport: GhApiTransport,
    host: str,
    confirmed_mappings: Mapping[str, int] | None = None,
    uncertain_identities: Collection[str] = (),
) -> ReconciliationPreview:
    """Compare a local preview with one complete read-only remote issue snapshot.

    This performs no create, update, close, or other mutation.  A mapping is only a
    caller-supplied reviewed choice for an already-existing issue; it never adopts by title.
    """
    unresolved_uncertainties = frozenset(uncertain_identities)
    try:
        issues = transport.list_issues(host, proposal.destination)
    except IncompleteLookup as error:
        detail = str(error)
        return ReconciliationPreview(proposal, host, tuple(Reconciliation(record, "incomplete lookup", detail=detail) for record in proposal.records), detail, unresolved_uncertainties)

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
            if record.identity in unresolved_uncertainties:
                results.append(Reconciliation(record, "deferred", detail="previous create outcome remains uncertain; resolve the exact identity before another create"))
            else:
                results.append(Reconciliation(record, "planned create"))
            continue
        issue = matches[0]
        if issue.state not in {"open", "closed"}:
            results.append(Reconciliation(record, "conflict", issue, "unknown remote state; inspect close ownership"))
        elif issue.title != record.title:
            results.append(Reconciliation(record, "conflict", issue, "remote title diverges; inspect before any change"))
        elif record.state == "closed" and issue.state_reason is not None:
            results.append(Reconciliation(record, "conflict", issue, "remote state reason is not null; inspect closure mapping or human state changes before any write"))
        elif issue.body == record.body and issue.state == record.state:
            results.append(Reconciliation(record, "no-op", issue))
        elif record.state == "closed" and issue.body == record.pending_close_body and issue.state == "open":
            results.append(Reconciliation(record, "pending close", issue, "recognized import-owned closure is unfinished"))
        else:
            results.append(Reconciliation(record, "conflict", issue, "remote body or state diverges; inspect before any change"))
    return ReconciliationPreview(proposal, host, tuple(results), uncertain_identities=unresolved_uncertainties)


def _verified_open_readback(record: RenderedRecord, issue: RemoteIssue) -> ApplyResult:
    expected_body = record.pending_close_body if record.state == "closed" else record.body
    if issue.is_pull_request:
        return ApplyResult(record, "deferred", issue, "readback resolved to a pull request")
    if issue.body.count(record.marker) != 1:
        return ApplyResult(record, "deferred", issue, "readback marker is absent or duplicated")
    if record.state == "closed" and issue.state_reason is not None:
        return ApplyResult(record, "deferred", issue, "pending closure state reason diverges; preserve possible human state changes")
    if issue.title != record.title or issue.body != expected_body or issue.state != "open":
        return ApplyResult(record, "deferred", issue, "readback title, content, or open state diverges; preserve remote changes")
    return ApplyResult(record, "created", issue)


def _close_after_verified_pending(record: RenderedRecord, proposal: Preview, transport: GhApiTransport, host: str, number: int) -> ApplyResult:
    try:
        staged = _verified_open_readback(record, transport.get_issue(host, proposal.destination, number))
    except IncompleteLookup as error:
        return ApplyResult(record, "deferred", detail=f"pending close readback unavailable: {error}")
    if staged.outcome != "created" or staged.issue is None:
        return staged
    try:
        transport.close_issue(host, proposal.destination, number, record)
    except IncompleteLookup:
        pass
    try:
        final = transport.get_issue(host, proposal.destination, number)
    except IncompleteLookup as error:
        return ApplyResult(record, "deferred", staged.issue, f"closure readback unavailable: {error}")
    if final.is_pull_request or final.title != record.title or final.body.count(record.marker) != 1 or final.body != record.body or final.state != "closed" or final.state_reason is not None:
        return ApplyResult(record, "deferred", final, "closure readback did not prove exact title, closed content, and null state reason")
    return ApplyResult(record, "closed", final)


def _recover_uncertain_create(record: RenderedRecord, proposal: Preview, transport: GhApiTransport, host: str, cause: str) -> ApplyResult:
    snapshot = reconcile(proposal, transport, host)
    current = next(item for item in snapshot.records if item.record.identity == record.identity)
    expected = "no-op" if record.state == "open" else "pending close"
    if current.outcome != expected or current.issue is None:
        return ApplyResult(record, "deferred", detail=f"create outcome uncertain ({cause}); complete lookup did not prove one exact import-owned record")
    if record.state == "closed":
        return _close_after_verified_pending(record, proposal, transport, host, current.issue.number)
    try:
        return _verified_open_readback(record, transport.get_issue(host, proposal.destination, current.issue.number))
    except IncompleteLookup as error:
        return ApplyResult(record, "deferred", current.issue, f"create response was lost; candidate readback unavailable: {error}")


def apply(
    reviewed: ReconciliationPreview,
    transport: GhApiTransport,
    host: str,
    authorization: ApplyAuthorization,
) -> ApplyReport:
    """Create only reviewed, currently missing open records; never update or close issues.

    A successful POST is independently read back. A failed POST response is permanently
    uncertain: it is reconciled once and never retried by this helper.
    """
    proposal = reviewed.preview
    if authorization.host != host or reviewed.host != host or authorization.destination != proposal.destination or not authorization.write_scope.strip():
        raise ValueError("apply requires explicit matching host, destination, and non-empty write scope confirmation")
    immediate = reconcile(proposal, transport, host, uncertain_identities=reviewed.uncertain_identities)
    reviewed_by_id = {item.record.identity: item for item in reviewed.records}
    current_by_id = {item.record.identity: item for item in immediate.records}
    results: list[ApplyResult] = []
    for record in proposal.records:
        prior = reviewed_by_id.get(record.identity)
        current = current_by_id[record.identity]
        if prior is None:
            results.append(ApplyResult(record, "deferred", detail="record was not reviewed"))
        elif record.state == "closed" and prior.outcome == current.outcome == "pending close" and current.issue is not None:
            results.append(_close_after_verified_pending(record, proposal, transport, host, current.issue.number))
        elif prior.outcome != "planned create" or current.outcome != "planned create":
            results.append(ApplyResult(record, "deferred", current.issue, "immediate target reinspection changed; reconcile before any write"))
        else:
            try:
                created = transport.create_issue(host, proposal.destination, record, record.pending_close_body)
                staged = _verified_open_readback(record, transport.get_issue(host, proposal.destination, created.number))
                results.append(_close_after_verified_pending(record, proposal, transport, host, created.number) if record.state == "closed" and staged.outcome == "created" else staged)
            except IncompleteLookup as error:
                results.append(_recover_uncertain_create(record, proposal, transport, host, str(error)))
    return ApplyReport(proposal, tuple(results))


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
                current = [match.group(1), match.group(2) + ("\n" if line.endswith("\n") else "")]
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
        if target.startswith(("http://", "https://", "mailto:")):
            return match.group(0)
        if target.startswith("#"):
            return f"[{text}]({source.blob_url}{target})"
        target_path, separator, anchor = target.partition("#")
        if not target_path or target_path.startswith(("/", "//")):
            return match.group(0)
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source.path), target_path))
        if resolved == ".." or resolved.startswith("../"):
            return match.group(0)
        url = f"https://{source.host}/{source.repository}/blob/{quote(source.revision, safe='')}/{quote(resolved, safe='/')}"
        return f"[{text}]({url}{'#' + anchor if separator else ''})"

    # Transform only plain mentions between complete code/link tokens. Never run
    # OI substitution inside link labels/targets or link rewriting inside code.
    def mentions(text: str) -> str:
        return _OI_REFERENCE.sub(lambda m: f"[{m.group(1)}]({source.blob_url})", text)

    parts: list[str] = []
    end = 0
    for token in _MARKDOWN_TOKEN.finditer(value):
        parts.append(mentions(value[end:token.start()]))
        text = token.group(0)
        parts.append(text if text.startswith("`") else _LINK.sub(link, text))
        end = token.end()
    parts.append(mentions(value[end:]))
    return "".join(parts)


def render_record(record: ParsedRecord, source: Source) -> RenderedRecord | Diagnostic:
    fields = record.field_map
    missing = [name for name in _REQUIRED_FIELDS if name not in fields]
    if missing:
        return Diagnostic(record.line, f"missing required field(s): {', '.join(missing)}", record.oi_id)
    if _UNSAFE.search(record.excerpt):
        return Diagnostic(record.line, "unsafe Markdown structure rejected", record.oi_id)
    if _SENSITIVE.search(record.excerpt):
        return Diagnostic(record.line, "sensitive candidate data rejected; fidelity is unavailable", record.oi_id)
    if any(match.group("nested") for _, value in record.fields for match in _NESTED_LABEL.finditer(value)):
        return Diagnostic(record.line, "unsupported nested link label; flatten the label in a reviewed source copy and preview again before importing this record", record.oi_id)
    status = fields["Status"].strip().lower()
    if status not in {"open", "closed"}:
        return Diagnostic(record.line, "unmappable status", record.oi_id)
    identity = f"{source.host}/{source.repository}:{source.path}:{record.oi_id}"
    marker = f"<!-- import-open-issues: {identity} -->"
    original_url = _entry_url(source, record)
    sections = [marker]
    if status == "closed":
        sections.append("<!-- import-open-issues-closure: closed -->")
    sections.extend((f"Historical source revision: `{source.revision}`", f"Original entry: [{record.oi_id}]({original_url})", ""))
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
    counts = Counter(record.oi_id for record in parsed)
    for record in parsed:
        if counts[record.oi_id] > 1:
            all_diagnostics.append(Diagnostic(record.line, "duplicate OI identity in source; reconcile all occurrences before importing this identity", record.oi_id))
            continue
        rendered = render_record(record, source)
        if isinstance(rendered, Diagnostic):
            all_diagnostics.append(rendered)
        else:
            output.append(rendered)
    return Preview(source, destination, tuple(output), tuple(all_diagnostics))
