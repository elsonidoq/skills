"""Gated exec helper. EOF or wrong release nonce means no tool execution."""
import json
import os
from pathlib import Path
import sys

from .containment import Cgroup, process_identity


MAX_MANIFEST_BYTES=1024*1024


def control_line(fd, limit):
    data=bytearray()
    while len(data)<=limit:
        chunk=os.read(fd,min(4096,limit+1-len(data)))
        if not chunk:raise EOFError('controller pipe closed before release')
        data.extend(chunk)
        if b'\n' in chunk:
            if not data.endswith(b'\n') or data.count(b'\n')!=1:raise ValueError('invalid control frame')
            return bytes(data[:-1])
    raise ValueError('control frame byte limit')


def main():
    gate, ready = int(sys.argv[1]), int(sys.argv[2])
    try:
        manifest = json.loads(control_line(gate,MAX_MANIFEST_BYTES))
        capability = Cgroup(manifest['containment']['parent'])
        path = capability.validate(manifest['containment'])
        (path / 'cgroup.procs').write_text(str(os.getpid()))
        identity = process_identity(os.getpid(), manifest['nonce'])
        capability.member(manifest['containment'], identity, manifest['nonce'])
        os.write(ready, (json.dumps(identity) + '\n').encode())
        os.close(ready)
        # The private launch payload and later release nonce are separate bounded frames.
        data=control_line(gate,128)
        os.close(gate)
        if data != manifest['nonce'].encode():return 125
        capability.member(manifest['containment'], identity, manifest['nonce'])
        os.chdir(manifest['cwd'])
        os.execve(manifest['argv'][0], manifest['argv'], manifest['environment'])
    except EOFError:
        return 125
    except BaseException:
        return 126


if __name__ == '__main__':
    sys.exit(main())
