"""Scoped, append-only GitHub trace comments through the real gh subprocess seam.

No credentials are authority. Callers supply an actual grant, not inferred metadata:
{run_id, target: qualified HTTPS issue/PR URL, operations: ['trace_comment'],
 approval_ref: actual owner approval reference}. Missing grants defer only delivery.
PR selection additionally requires a caller-supplied known_linked_prs association.
confirm_delivery_links verifies known PR identities and reciprocal discovery without
creating PRs, editing bodies or republishing an already confirmed trace.

The observed GitHub IssueComment body-length validation is recognized automatically.
A complete marker/full-body reconciliation must prove no existing effect before
lossless partitioning. LengthProof remains a compatibility seam for other verified
consumer diagnostics. No built-in or guessed GitHub size limit is used.
"""
from dataclasses import dataclass
import hashlib
import json
import re
import subprocess
from urllib.parse import parse_qs, urlsplit

from .store import Blocked, canonical
from .trace_projection import project_trace, render_markdown


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class LengthProof:
    """Already verified diagnostic evidence supplied by the consuming integration.

    source names the inspected API/consumer contract, explanation states why this
    diagnostic proves length AND no effect. Hashes bind exact body and raw HTTP
    response. Tests use a source-backed fake API contract, not live GitHub proof.
    """
    body_sha256: str
    response_sha256: str
    source: str
    explanation: str
    no_effect: bool


class PublicationError(Blocked):
    def __init__(self, message, state='uncertain'):
        super().__init__(message)
        self.state = state


@dataclass(frozen=True)
class Target:
    host: str
    owner: str
    repo: str
    number: int
    kind: str

    @classmethod
    def parse(cls, url):
        if not isinstance(url, str):
            raise PublicationError('Trace target missing; supply a qualified HTTPS issue URL.', 'deferred')
        match = re.fullmatch(r'https://([A-Za-z0-9.-]+)/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/(issues|pull)/([1-9][0-9]*)', url)
        if not match:
            raise PublicationError('Trace target invalid; supply an exact qualified HTTPS issue or known PR URL.', 'deferred')
        host, owner, repo, kind, number = match.groups()
        return cls(host.lower(), owner, repo, int(number), kind)

    @property
    def url(self):
        return f'https://{self.host}/{self.owner}/{self.repo}/{self.kind}/{self.number}'

    @property
    def endpoint(self):
        return f'/repos/{self.owner}/{self.repo}/issues/{self.number}'

    @property
    def api_base(self):
        return 'https://api.github.com' if self.host == 'github.com' else f'https://{self.host}/api/v3'

    @property
    def issue_url(self):
        return self.api_base + self.endpoint


class Gh:
    """Argument arrays and JSON stdin only. No shell, auth dump or implicit repo."""
    def __init__(self, executable='gh'):
        self.executable = str(executable)

    def request(self, target, method, endpoint, body=None):
        argv = [self.executable, 'api', '--hostname', target.host, '--method', method,
                '--include', '-H', 'Accept: application/vnd.github+json',
                '-H', 'X-GitHub-Api-Version: 2022-11-28', endpoint]
        if body is not None:
            argv += ['--input', '-']
        try:
            result = subprocess.run(argv, input=json.dumps(body, ensure_ascii=False) if body is not None else None,
                                    text=True, encoding='utf-8', capture_output=True)
        except (OSError, UnicodeError) as exc:
            # Do not echo arbitrary CLI output, environment or possible credentials.
            raise PublicationError('gh transport unavailable; verify the installed executable and access, then reconcile before recovery.') from exc
        raw = result.stdout
        try:
            head, payload = re.split(r'\r?\n\r?\n', raw, maxsplit=1)
            lines = head.splitlines()
            status = int(re.fullmatch(r'HTTP/\S+ (\d{3})(?: .*)?', lines[0]).group(1))
            headers = {}
            for line in lines[1:]:
                key, value = line.split(':', 1)
                key = key.lower()
                if key in headers:
                    headers[key] += ', ' + value.strip()
                else:
                    headers[key] = value.strip()
            data = json.loads(payload)
        except (ValueError, AttributeError, IndexError):
            raise PublicationError('gh returned incomplete/unreadable HTTP data; restore read access and reconcile before any new comment.') from None
        return {'status': status, 'headers': headers, 'data': data, 'raw': raw,
                'ok': result.returncode == 0 and 200 <= status < 300}


def _read(gh, target, endpoint):
    response = gh.request(target, 'GET', endpoint)
    if not response['ok']:
        status = response['status']
        raise PublicationError(f'GitHub GET failed (HTTP {status}); correct target/access or rate restriction, then reconcile. No new comment was sent.')
    return response


def _target_read(gh, target):
    data = _read(gh, target, target.endpoint)['data']
    if (not isinstance(data, dict) or data.get('number') != target.number or
            data.get('html_url') != target.url or data.get('url') != target.issue_url or
            ('pull_request' in data) != (target.kind == 'pull')):
        raise PublicationError('GitHub target identity drifted; verify the exact issue/known PR and renew changed target scope.', 'deferred')
    if target.kind == 'pull':
        pr = _read(gh, target, f'/repos/{target.owner}/{target.repo}/pulls/{target.number}')['data']
        if (not isinstance(pr, dict) or pr.get('number') != target.number or
                pr.get('html_url') != target.url or pr.get('issue_url') != target.issue_url):
            raise PublicationError('Known PR identity is not confirmed; correct the association before publication.', 'deferred')
    return data


def _comment(gh, target, identity, body):
    if type(identity) is not int or identity <= 0:
        raise PublicationError('Comment identity missing; perform a complete destination reconciliation before recovery.')
    data = _read(gh, target, f'/repos/{target.owner}/{target.repo}/issues/comments/{identity}')['data']
    url = target.url + '#issuecomment-' + str(identity)
    if (not isinstance(data, dict) or data.get('id') != identity or data.get('html_url') != url or
            data.get('issue_url') != target.issue_url or data.get('body') != body or
            data.get('url') != target.api_base + f'/repos/{target.owner}/{target.repo}/issues/comments/{identity}'):
        raise PublicationError('Independent comment readback differs in full body, identity or target; inspect the remote comment and reconcile, never overwrite it.')
    return {'id': identity, 'url': url}


def _comments(gh, target):
    """Read every page before consumers may infer that a link/comment is absent."""
    endpoint = target.endpoint + '/comments?per_page=100&page=1'
    visited, ids, items = set(), set(), []
    while endpoint:
        if endpoint in visited:
            raise PublicationError('Comment pagination repeats a page; correct read access/pagination before recovery.')
        visited.add(endpoint)
        response = _read(gh, target, endpoint)
        data = response['data']
        if not isinstance(data, list):
            raise PublicationError('Comment page is incomplete; obtain all destination comment pages before recovery.')
        for item in data:
            if (not isinstance(item, dict) or type(item.get('id')) is not int or
                    item['id'] in ids or not isinstance(item.get('body'), str)):
                raise PublicationError('Comment page has missing/duplicate identity or body; complete destination reads before recovery.')
            ids.add(item['id'])
            items.append(item)
        link = response['headers'].get('link', '')
        current_page = int(parse_qs(urlsplit(endpoint).query)['page'][0])
        endpoint = None
        if link:
            parsed_links = [re.fullmatch(r'\s*<([^>]+)>;\s*rel="([^"]+)"\s*', item)
                            for item in link.split(',')]
            if not all(parsed_links):
                raise PublicationError('Unusable pagination Link header; complete destination reads before recovery.')
            links = [item.groups() for item in parsed_links]
            if len([url for url, rel in links if rel == 'next']) > 1:
                raise PublicationError('Ambiguous pagination Link header; complete destination reads before recovery.')
            for url, rel in links:
                if rel != 'next':
                    continue
                parsed = urlsplit(url)
                expected = urlsplit(target.api_base + target.endpoint + '/comments')
                query = parse_qs(parsed.query)
                if (parsed.scheme != expected.scheme or parsed.netloc != expected.netloc or
                        parsed.path != expected.path or parsed.fragment or
                        set(query) != {'per_page', 'page'} or query['per_page'] != ['100'] or
                        len(query['page']) != 1 or not re.fullmatch('[1-9][0-9]*', query['page'][0]) or
                        int(query['page'][0]) != current_page + 1):
                    raise PublicationError('Pagination next target drifted; inspect destination pages before recovery.')
                endpoint = target.endpoint + '/comments?' + parsed.query
    return items


def _reconcile(gh, target, marker, body):
    """Explicit Link traversal proves completion; no writes on incomplete scans."""
    candidates = [item['id'] for item in _comments(gh, target) if marker in item['body']]
    # Read every candidate independently even though the listing supplied a body.
    matches = [_comment(gh, target, identity, body) for identity in candidates]
    if len(matches) > 1:
        raise PublicationError('Multiple exact trace comments exist; resolve duplicate ambiguity before any further writes.')
    return matches[0] if matches else None


def _length_diagnostic(response):
    """Recognize only the actual IssueComment body-length validation, not any 422.

    Keep a safe useful cause, not arbitrary response text, headers or credentials.
    The diagnostic identifies length, while a complete reconciliation proves absence.
    """
    data = response.get('data')
    if response.get('status') != 422 or not isinstance(data, dict) or data.get('message') != 'Validation Failed':
        return None
    errors = data.get('errors')
    if not isinstance(errors, list) or len(errors) != 1 or not isinstance(errors[0], dict):
        return None
    error = errors[0]
    message = error.get('message')
    if (error.get('resource') != 'IssueComment' or error.get('code') != 'unprocessable' or
            error.get('field') != 'data' or not isinstance(message, str) or
            not re.fullmatch(r'Body is too long \(maximum is [1-9][0-9]* characters\)', message)):
        return None
    return {'message': message,
            'source': 'https://docs.github.com/rest/issues/comments#create-an-issue-comment'}


def _partition(text):
    """Progressively split at section/event/line boundaries, then Unicode text.

    This is not a guessed limit. Only a verified length rejection calls this;
    each rejected part is replaced by two smaller lossless continuations.
    """
    midpoint = len(text) // 2
    for pattern in (r'\n(?=# )', r'\n(?=    \{)', r'\n'):
        cuts = [m.end() for m in re.finditer(pattern, text) if 0 < m.end() < len(text)]
        if cuts:
            point = min(cuts, key=lambda value: abs(value - midpoint))
            return text[:point], text[point:]
    if not midpoint:
        raise PublicationError('Even a minimal continuation was rejected; inspect the verified endpoint diagnostic instead of retrying.', 'failed')
    return text[:midpoint], text[midpoint:]


def publish_trace(store, run, *, target=None, authority=None, snapshot=None, snapshot_id=None,
                  known_linked_prs=(), gh=None, length_proofs=()):
    """Publish/confirm one stable snapshot; return delivery separately from execution.

    snapshot_id selects existing prepared content for publication-only recovery.
    Omitting it projects current history. All intent is durable before effects.
    A failed/uncertain send is never blindly repeated, including after process death.
    No blind request retry loop; verified no-effect length rejections split losslessly.
    Explicit recovery scans before a targeted send.
    Caller retains the existing worktree writer authority throughout this operation.
    """
    gh = gh or Gh()
    urls = []
    sid = snapshot_id
    def result(state, correction=None):
        return {'state': state, 'snapshot_id': sid, 'urls': urls[:], 'correction': correction}
    try:
        records = [dict(json.loads(row['details']), state=row['state'])
                   for row in store.trace_publication_history(run)]
        if snapshot_id is not None:
            prepared = next((r for r in records if r.get('snapshot_id') == snapshot_id and r.get('type') == 'snapshot'), None)
            if prepared is None:
                raise PublicationError('Retained snapshot unavailable; select an existing prepared snapshot or project retained facts.', 'deferred')
            if snapshot is not None:
                raise PublicationError('Conflicting snapshot inputs; select either retained snapshot ID or current source.', 'deferred')
            snapshot = prepared['snapshot']
        snapshot = project_trace(store, run) if snapshot is None else snapshot
        sid = snapshot.get('snapshot_id')
        unsigned = {key: value for key, value in snapshot.items() if key != 'snapshot_id'}
        if snapshot.get('run_id') != run or sid != digest(canonical(unsigned)):
            raise PublicationError('Snapshot identity differs from its fixed source; regenerate the factual projection.', 'deferred')
        issue = Target.parse(snapshot.get('delivery_issue'))
        destination = Target.parse(issue.url if target is None else target)
        if issue.kind != 'issues' or (destination != issue and
                (destination.kind != 'pull' or destination.url not in known_linked_prs or
                 (destination.host, destination.owner, destination.repo) != (issue.host, issue.owner, issue.repo))):
            raise PublicationError('Trace destination is not the delivery issue or explicitly selected known linked PR; correct the target/association.', 'deferred')
        if (not isinstance(authority, dict) or authority.get('run_id') != run or
                authority.get('target') != destination.url or
                not isinstance(authority.get('operations'), list) or
                'trace_comment' not in authority['operations'] or
                not isinstance(authority.get('approval_ref'), str) or not authority['approval_ref'].strip()):
            raise PublicationError('Trace comment authority missing/drifted; supply actual owner approval for this run, exact target and trace_comment operation.', 'deferred')
        relevant = [r for r in records if r.get('snapshot_id') == sid]
        intents = [r for r in relevant if r.get('type') == 'snapshot']
        text = render_markdown(snapshot)
        if intents and any(r['target'] != destination.url or r['text'] != text or r['snapshot'] != snapshot for r in intents):
            raise PublicationError('Prepared snapshot/target drifted; recover the exact retained target and content, not a replacement grant.', 'deferred')
        def record(state, **facts):
            value = {'version': 1, 'snapshot_id': sid, 'target': destination.url, **facts}
            store.history(run, None, 'trace_publication', state, value)
            relevant.append({**value, 'state': state})
        _target_read(gh, destination)  # Access and exact identity before any mutation.
        if not intents:
            record('prepared', type='snapshot', snapshot=snapshot, text=text,
                   authority_ref=authority['approval_ref'])
        def wire(part, chunk):
            marker = '<!-- coherence-trace:' + digest(run) + ':' + sid + ':' + part + ' -->'
            body = marker + '\n' + 'Trace continuation ' + part + '; concatenate leaf payloads in part order without added separators.\n' + chunk
            return marker, body
        def send(part, chunk):
            marker, body = wire(part, chunk)
            prior = [r for r in relevant if r.get('type') == 'part' and r.get('part') == part]
            last = prior[-1] if prior else None
            if last and (last['body'] != body or last['chunk'] != chunk):
                raise PublicationError('Retained part intent differs; restore exact prepared content before recovery.')
            def event(state, **extra):
                record(state, type='part', part=part, chunk=chunk, body=body,
                       body_sha256=digest(body), **extra)
            if last and last['state'] == 'split':
                children = last['children']
                if len(children) != 2 or ''.join(children) != chunk:
                    raise PublicationError('Retained continuations are incomplete; restore prepared content before recovery.')
                for index, child in enumerate(children, 1):
                    send(part + '.' + str(index), child)
                return
            def split(diagnostic=None, proof=None):
                try:
                    children = list(_partition(chunk))
                except PublicationError:
                    cause = diagnostic['message'] if diagnostic else 'Verified body-length rejection'
                    raise PublicationError(cause + '; even a minimal continuation cannot progress. '
                                           'Inspect endpoint validation and the continuation envelope before recovery.', 'failed') from None
                facts = {'length_diagnostic': diagnostic} if diagnostic else {'length_proof': proof.__dict__}
                event('split', children=children, **facts)
                for index, child in enumerate(children, 1):
                    send(part + '.' + str(index), child)
            if not last:
                event('prepared')
            elif last['state'] == 'confirmed':
                found = _comment(gh, destination, last['comment']['id'], body)
                urls.append(found['url'])
                return
            elif last['state'] != 'prepared':
                found = _reconcile(gh, destination, marker, body)
                if found:
                    event('confirmed', comment=found)
                    urls.append(found['url'])
                    return
                # Recover a retained known length rejection without resending it.
                if last['state'] == 'rejected' and last.get('length_diagnostic'):
                    split(diagnostic=last['length_diagnostic'])
                    return
                # A complete zero-match scan permits one targeted attempt, not a loop.
            event('sending')
            response = gh.request(destination, 'POST', destination.endpoint + '/comments', {'body': body})
            if not response['ok']:
                proof = next((p for p in length_proofs if isinstance(p, LengthProof) and
                              p.no_effect is True and p.source.strip() and p.explanation.strip() and
                              p.body_sha256 == digest(body) and p.response_sha256 == digest(response['raw']) and
                              response['status'] == 422), None)
                diagnostic = _length_diagnostic(response)
                event('rejected', status=response['status'],
                      **({'length_diagnostic': diagnostic} if diagnostic else {}))
                if diagnostic or proof:
                    found = _reconcile(gh, destination, marker, body)
                    if found:
                        event('confirmed', comment=found)
                        urls.append(found['url'])
                        return
                    split(diagnostic=diagnostic, proof=proof)
                    return
                raise PublicationError(f'GitHub comment POST failed (HTTP {response["status"]}); correct validation/access/rate restrictions and reconcile before recovery. No recognized IssueComment body-length diagnostic or matching verified no-effect proof; no partition or automatic retry.', 'failed')
            data = response['data']
            identity = data.get('id') if isinstance(data, dict) else None
            found = _comment(gh, destination, identity, body)
            event('confirmed', comment=found)
            urls.append(found['url'])
        send('1', text)
        record('confirmed', type='snapshot_result', urls=urls)
        return result('confirmed')
    except PublicationError as exc:
        return result('partial' if urls else exc.state, str(exc))


def recover_publication(store, run, *, snapshot_id=None, delivery_scope=None):
    """Recover only retained publication effects; never enter implementation control.

    Prefer the latest prepared snapshot, including its fixed source boundary. Only
    when none exists may retained run facts be projected. A supplied grant cannot
    silently replace an existing launch carrier. All sends/reconciliation remain
    owned by publish_trace and confirm_delivery_links.
    """
    row = store.db.execute('SELECT state FROM execution_runs WHERE run_id=?', (run,)).fetchone()
    report = {'implementation': {'state': row['state'] if row else 'unavailable',
                                 'replayed': False}}
    def deferred(message):
        report['publication'] = {'state': 'deferred', 'snapshot_id': snapshot_id,
                                 'urls': [], 'correction': message}
        return report
    if row is None:
        return deferred('Retained run unavailable; restore its original workflow database and select its exact run ID.')
    saved = store.input(run)
    if not saved:
        return deferred('Retained run input unavailable; restore original facts and delivery issue before publication recovery.')
    retained = saved.get('authority', {}).get('delivery_scope')
    if delivery_scope is not None and retained is not None and delivery_scope != retained:
        return deferred('Delivery scope drifted; restore the unchanged retained run/target/operation carrier. Changed effects need owner scope.')
    carrier = retained if delivery_scope is None else delivery_scope
    if (not isinstance(carrier, dict) or set(carrier) - {'target', 'authority', 'known_linked_prs'} or
            not isinstance(carrier.get('known_linked_prs', []), list) or
            any(not isinstance(url, str) for url in carrier.get('known_linked_prs', []))):
        return deferred('Publication authority unavailable/invalid; supply --delivery-scope with the actual run/target/operation grant carrier, not issue context.')
    records = [json.loads(item['details']) for item in store.trace_publication_history(run)]
    snapshots = [item for item in records if item.get('type') == 'snapshot']
    if snapshot_id is None and snapshots:
        snapshot_id = snapshots[-1]['snapshot_id']
    publication = publish_trace(store, run, snapshot_id=snapshot_id, **carrier)
    report['publication'] = publication
    if publication['state'] == 'confirmed':
        report['linkage'] = confirm_delivery_links(
            store, run, issue=saved['contract'].get('delivery_issue'),
            known_prs=carrier.get('known_linked_prs', []), snapshot_id=publication['snapshot_id'],
            authorities=[carrier.get('authority')])
    return report


def _has_url(body, url):
    # Trace JSON/evidence can mention arbitrary URLs inside code: those are not
    # navigable association links. Exclude code and hidden comments before reuse.
    if not isinstance(body, str) or body.startswith('<!-- coherence-trace:'):
        return False
    body = re.sub(r'(?ms)^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*?^[ \t]{0,3}\1[ \t]*(?:\n|$)', '', body)
    body = re.sub(r'(`+)[^\n]*?\1|<!--.*?-->', '', body, flags=re.S)
    # Do not accept a different issue number, comment fragment or URL suffix.
    return re.search(
        r'(?<![\w/])' + re.escape(url) + r'''(?=$|[\s<>"'`)\]},]|[;.!](?=\s|$))''', body) is not None


def confirm_delivery_links(store, run, *, issue, known_prs, snapshot_id,
                           authorities=(), gh=None):
    """Confirm reciprocal links for supplied known PRs, including late discovery.

    authorities contains actual per-target grants with operation link_comment,
    run_id and approval_ref (same shape as publish_trace). Reads/reuse need no
    write grant. Only missing links are appended. The retained confirmed snapshot
    is independently read again, never projected or resent. This helper does not
    execute finish, review, Git or any implementation work.
    """
    gh = gh or Gh()
    associations, trace_urls = [], []
    try:
        delivery = Target.parse(issue)
        prs = list(dict.fromkeys(known_prs))
        targets = [Target.parse(url) for url in prs]
        if delivery.kind != 'issues' or any(t.kind != 'pull' for t in targets):
            raise PublicationError('Delivery linkage needs an exact issue and qualified known PR URLs; correct the supplied association.', 'deferred')
        records = [dict(json.loads(row['details']), state=row['state'])
                   for row in store.trace_publication_history(run)]
        snapshots = [r for r in records if r.get('snapshot_id') == snapshot_id and r.get('type') == 'snapshot']
        confirmed = [r for r in records if r.get('snapshot_id') == snapshot_id and r.get('type') == 'snapshot_result' and r['state'] == 'confirmed']
        if not snapshots or not confirmed or snapshots[0]['snapshot'].get('delivery_issue') != delivery.url:
            raise PublicationError('Confirmed trace for this delivery issue is unavailable; confirm the retained publication before linking it.', 'deferred')
        destination = Target.parse(snapshots[0]['target'])
        _target_read(gh, destination)
        for url in confirmed[-1]['urls']:
            part = next((r for r in reversed(records) if r.get('type') == 'part' and
                         r.get('snapshot_id') == snapshot_id and r['state'] == 'confirmed' and
                         r.get('comment', {}).get('url') == url), None)
            if part is None:
                raise PublicationError('Confirmed trace part intent is missing; restore retained publication facts before linkage.', 'deferred')
            trace_urls.append(_comment(gh, destination, part['comment']['id'], part['body'])['url'])
        if not trace_urls:
            raise PublicationError('Confirmed trace has no parts; confirm retained publication before linkage.', 'deferred')
        # Confirm all supplied target identities before any link mutation.
        bodies = {t.url: _target_read(gh, t).get('body') for t in [delivery, *targets]}
        if destination != delivery and destination.url not in prs:
            raise PublicationError('PR-hosted trace is outside the known delivery PRs; supply its qualified association.', 'deferred')

        def ensure(target, required):
            # Resume exact uncertain intents before deriving a new missing-link body.
            prior = [r for r in records if r.get('type') == 'link' and r.get('target') == target.url]
            pending = {}
            for row in prior:
                pending[row['link_id']] = row
            for row in pending.values():
                if row['state'] not in ('prepared', 'sending', 'rejected'):
                    continue
                if row.get('issue') != delivery.url:
                    continue
                found = _reconcile(gh, target, row['marker'], row['body'])
                if found:
                    record_link(target, row, 'confirmed', comment=found)
            pages = _comments(gh, target)
            missing = []
            for url in required:
                # A direct confirmed trace-part link also discovers its host PR.
                equivalents = [url] + [part for part in trace_urls if url in prs and part.startswith(url + '#')]
                def linked(body):
                    return any(_has_url(body, reference) for reference in equivalents)
                if linked(bodies[target.url]):
                    continue
                candidates = [item for item in pages if linked(item['body'])]
                for item in candidates:
                    _comment(gh, target, item['id'], item['body'])
                if not candidates:
                    missing.append(url)
            if not missing:
                return
            grant = next((a for a in authorities if isinstance(a, dict) and
                          a.get('run_id') == run and a.get('target') == target.url and
                          isinstance(a.get('operations'), list) and 'link_comment' in a['operations'] and
                          isinstance(a.get('approval_ref'), str) and a['approval_ref'].strip()), None)
            if grant is None:
                raise PublicationError('Missing link_comment authority for ' + target.url +
                                       '; supply actual run/target/operation approval to establish missing links.', 'deferred')
            key = digest(canonical([run, delivery.url, target.url, missing]))
            marker = '<!-- coherence-link:' + key + ' -->'
            body = marker + '\nDelivery evidence links:\n' + '\n'.join('- ' + url for url in missing)
            row = {'type': 'link', 'link_id': key, 'issue': delivery.url,
                   'marker': marker, 'body': body, 'body_sha256': digest(body),
                   'authority_ref': grant['approval_ref']}
            record_link(target, row, 'prepared')
            found = _reconcile(gh, target, marker, body)
            if not found:
                record_link(target, row, 'sending')
                response = gh.request(target, 'POST', target.endpoint + '/comments', {'body': body})
                if not response['ok']:
                    record_link(target, row, 'rejected', status=response['status'])
                    raise PublicationError(f'Link comment POST failed (HTTP {response["status"]}); correct access/validation and reconcile before recovery.', 'failed')
                data = response['data']
                found = _comment(gh, target, data.get('id') if isinstance(data, dict) else None, body)
            record_link(target, row, 'confirmed', comment=found)

        def record_link(target, row, state, **extra):
            store.history(run, None, 'trace_publication', state,
                          {**row, 'version': 1, 'target': target.url, **extra})

        # Issue discovery is necessary even for issue-hosted traces. PR-hosted
        # traces additionally require direct discovery of every confirmed part.
        ensure(delivery, prs + (trace_urls if destination != delivery else []))
        for pr in targets:
            ensure(pr, [delivery.url])
            associations.append({'issue': delivery.url, 'pr': pr.url})
        return {'state': 'confirmed', 'associations': associations, 'trace_urls': trace_urls, 'correction': None}
    except PublicationError as exc:
        return {'state': 'incomplete', 'associations': associations,
                'trace_urls': trace_urls, 'correction': str(exc)}
