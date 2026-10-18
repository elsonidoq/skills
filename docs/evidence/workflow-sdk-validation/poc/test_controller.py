"""No paid calls: fail-closed selectors/protocol/process identity tests."""
import os
from pathlib import Path
import tempfile
import unittest
from controller import Host, admit, live, proc

class Tests(unittest.TestCase):
    def test_cutoff_unknown_disabled_unsettled(self):
        for free, expected in [(150000, True), (149999, False), (None, False), (float('inf'), False), (float('nan'), False)]:
            with self.subTest(free=free):
                self.assertEqual(admit(dict(idle=True,effective={'enabled':True},headroom=free)),expected)
        self.assertFalse(admit({}))
        self.assertFalse(admit(dict(idle=False,effective={'enabled':True},headroom=200000)))
        self.assertFalse(admit(dict(idle=True,effective={'enabled':False},headroom=200000)))
    def test_process_identity_not_pid_only(self):
        identity=proc(os.getpid())
        self.assertTrue(live(identity))
        self.assertFalse(live({**identity,'start':'impossible'}))
    def test_protocol_version_poison_and_eof(self):
        with tempfile.TemporaryDirectory(dir=os.environ['TMPDIR']) as temp:
            base=Path(temp)
            h=Host(base/'toy',base/'protocol.jsonl')
            try:
                h.p.stdin.write('{"v":99,"id":"wrong","op":"prompt"}\n');h.p.stdin.flush()
                self.assertFalse(h.wait('response','wrong')['ok'])
                h.send('denied','prompt',text='never sent')
                self.assertFalse(h.wait('response','denied')['ok'])
                h.p.stdin.close();h.p.wait(timeout=10)
                with self.assertRaises(EOFError):h.wait('settled','denied',timeout=2)
                self.assertFalse((h.root/'sessions').exists())
            finally:h.close()

if __name__=='__main__':unittest.main(verbosity=2)
