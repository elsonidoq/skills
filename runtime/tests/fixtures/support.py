"""Owned disposable Git projects; never a fake provider-success oracle."""
from pathlib import Path
import tempfile
import unittest
from coherence_workflow.store import git


class ProjectTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='coherence-simplification-03-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / 'project'
        self.project.mkdir()
        git(self.project, 'init', '-q')
        git(self.project, 'config', 'user.name', 'Fixture')
        git(self.project, 'config', 'user.email', 'fixture@invalid')
        for name, text in {'.gitignore': '.coherence/\n', 'owned.txt': 'base\n',
                           'other.txt': 'other\n', 'STATE.md': 'custom\n'}.items():
            (self.project / name).write_text(text)
        git(self.project, 'add', '--', '.gitignore', 'owned.txt', 'other.txt', 'STATE.md')
        git(self.project, 'commit', '-qm', 'baseline')
        self.base = git(self.project, 'rev-parse', 'HEAD').decode().strip()

    def write(self, name, text):
        (self.project / name).write_text(text)
