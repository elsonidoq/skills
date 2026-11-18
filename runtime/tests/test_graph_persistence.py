"""Exercise the selected SQLite saver with actual graph interrupt and reopen."""
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from coherence_workflow.graph import graph_saver


class State(TypedDict, total=False):
    run_id: str
    answer: str
    phase: str


def build(saver):
    def prepare(state):
        return {'phase': 'waiting'}

    def ask(state):
        answer = interrupt('continue?')
        return {'answer': answer, 'phase': 'answered'}

    builder = StateGraph(State)
    builder.add_node('prepare', prepare)
    builder.add_node('ask', ask)
    builder.add_edge(START, 'prepare')
    builder.add_edge('prepare', 'ask')
    builder.add_edge('ask', END)
    return builder.compile(checkpointer=saver)


class AuthorityStub:
    def __init__(self, root):
        self.database = root / 'workflow.sqlite'

    def assert_held(self):
        pass


class PersistenceTests(unittest.TestCase):
    def test_reopen_latest_interrupt_and_preserve_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            authority = AuthorityStub(root)
            with sqlite3.connect(authority.database) as db:
                db.execute('CREATE TABLE wf_history (payload BLOB)')
                db.execute('INSERT INTO wf_history VALUES (?)', (b'old\x00history',))
            original = authority.database.read_bytes()
            config = {'configurable': {'thread_id': 'stable-run'}}
            with graph_saver(authority) as saver:
                graph = build(saver)
                result = graph.invoke({'run_id': 'stable-run'}, config, durability='sync')
                self.assertEqual(result['__interrupt__'][0].value, 'continue?')
                self.assertEqual(graph.get_state(config).values['phase'], 'waiting')
            with graph_saver(authority) as saver:
                graph = build(saver)
                self.assertEqual(graph.get_state(config).values['phase'], 'waiting')
                result = graph.invoke(Command(resume='yes'), config, durability='sync')
                self.assertEqual((result['phase'], result['answer']), ('answered', 'yes'))
            with graph_saver(authority) as saver:
                self.assertEqual(build(saver).get_state(config).values['answer'], 'yes')
            self.assertEqual(authority.database.read_bytes(), original)
            self.assertEqual(os.stat(root / 'graph.sqlite').st_mode & 0o777, 0o600)

    def test_existing_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'target'
            target.write_bytes(b'untouched')
            (root / 'graph.sqlite').symlink_to(target)
            with self.assertRaisesRegex(Exception, 'symlink'):
                with graph_saver(AuthorityStub(root)):
                    pass
            self.assertEqual(target.read_bytes(), b'untouched')
