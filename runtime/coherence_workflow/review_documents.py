"""Read-only references and continuation over the actual committed review range."""
from .store import Blocked, git, safe_path


def references(contract):
    return [dict(source) for source in contract['sources']] + [
        {'path': ref['record_ref'], 'sha256': ref['record_sha256'], 'kind': 'approval'}
        for ref in contract['approval_refs']]


def read_review(project, bundle, args):
    """No delivery attestation: judgment belongs to the independent reviewer."""
    name=args['path']
    allowed={ref['path'] for ref in bundle['document_refs']} | {
        path for task in bundle['source_tasks_approvals']['tasks'] for path in task['owned_paths']}
    if name not in allowed:
        raise Blocked('review read outside approved source/task paths; request scoped authority')
    path=safe_path(project,name)
    if git(project,'rev-parse','HEAD').decode().strip()!=bundle['range_head']:
        raise Blocked('stale review range; restart review at current HEAD')
    revision=args.get('revision','working')
    if revision=='working':
        if not path.is_file():raise Blocked('review file unavailable; read committed base/head instead')
        text=path.read_text(encoding='utf-8')
    elif revision=='diff':
        text=git(project,'diff','--no-ext-diff','--no-textconv',bundle['range_base']+'..'+bundle['range_head'],'--',name).decode('utf-8')
    elif revision in ('base','head'):
        text=git(project,'show',bundle['range_'+revision]+':'+name).decode('utf-8')
    else:raise Blocked('unknown review revision; select working, base, head or diff')
    offset=args.get('offset',0);limit=args.get('limit',8192)
    if offset<0 or not 1<=limit<=32768:raise Blocked('invalid review offset/limit; use a positive chunk up to 32768')
    chunk=text[offset:offset+limit];end=offset+len(chunk);eof=end>=len(text)
    return {'text':chunk,'offset':offset,'next_offset':end,'eof':eof,
            'continuation':None if eof else {'path':name,'revision':revision,'offset':end,'limit':limit}}
