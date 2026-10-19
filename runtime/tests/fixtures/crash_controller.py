"""Subprocess fault driver exercising the shipped gateway, not a substitute launcher."""
import json
import os
from pathlib import Path
import signal
import sys
import time

from coherence_workflow.store import Authority
from coherence_workflow.tools import Gateway
from fixtures.custody_support import process_tool


def main():
    project,parent,phase,log,mode=sys.argv[1:]
    project=Path(project)
    with Authority(project) as authority:
        authority.store.reserve('run','fixture')
        gateway=Gateway(authority,'run',parent,{'fixture':process_tool(project)})
        def hook(observed,op):
            row=authority.store.db.execute('SELECT * FROM wf_processes WHERE op_id=?',(op,)).fetchone()
            # Independent test-owned receipt permits teardown, never runtime adoption.
            receipt=None
            if observed!='intent': receipt=gateway.containment.receipt(row['name'])
            with open(log,'a') as f:
                f.write(json.dumps({'phase':observed,'op':op,'test_receipt':receipt})+'\n'); f.flush(); os.fsync(f.fileno())
            if observed==phase:
                if observed=='released':
                    deadline=time.monotonic()+5
                    while project.joinpath('owned.txt').read_text()=='base' and time.monotonic()<deadline: time.sleep(.01)
                os.kill(os.getpid(),signal.SIGKILL)
        op,proc=gateway.launch('tool','fixture','1',{'mode':mode,'exit':0},phase_hook=hook)
        gateway.settle(op,proc.wait(timeout=10))


if __name__=='__main__': main()
