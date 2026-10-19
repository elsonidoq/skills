"""Trusted isolated process-test tool; only writes its explicitly owned file."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def main():
    mode, output, code = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3])
    if mode == 'child':
        os.setsid()
        signal.signal(signal.SIGTERM,signal.SIG_IGN)
        while True:
            with output.open('a') as f: f.write('child\n'); f.flush()
            time.sleep(.03)
    if mode in ('survivor','survivor_hang'):
        subprocess.Popen([sys.executable,__file__,'child',str(output),'0'],
                         stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        deadline=time.monotonic()+5
        while 'child' not in output.read_text():
            if time.monotonic()>deadline: return 90
            time.sleep(.01)
        if mode=='survivor_hang':
            while True: time.sleep(1)
        return code
    output.write_text('partial\n')
    if mode=='hang':
        while True: time.sleep(1)
    return code


if __name__=='__main__': sys.exit(main())
