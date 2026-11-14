"""Standard, private file-backed checkpoint storage for graph control state.

Callers compile their graph with the yielded saver and use a stable thread_id and
sync durability. State should contain control facts and references, not payloads.
"""
from contextlib import contextmanager
import os

from langgraph.checkpoint.sqlite import SqliteSaver

from .store import safe_path


@contextmanager
def graph_saver(authority):
    """Open a saver beside, never inside, the existing workflow history database."""
    authority.assert_held()
    root = authority.database.parent
    for suffix in ('', '-wal', '-shm', '-journal'):
        safe_path(root, 'graph.sqlite' + suffix)
    path = safe_path(root, 'graph.sqlite')
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    os.close(fd)
    with SqliteSaver.from_conn_string(str(path)) as saver:
        yield saver
