"""Gated exec helper. EOF or wrong release nonce means no tool execution."""
import json
import os
from pathlib import Path
import sys

from .containment import Cgroup, process_identity


def main():
    gate, ready = int(sys.argv[1]), int(sys.argv[2])
    manifest = json.loads(sys.argv[3])
    try:
        capability = Cgroup(manifest['containment']['parent'])
        path = capability.validate(manifest['containment'])
        (path / 'cgroup.procs').write_text(str(os.getpid()))
        identity = process_identity(os.getpid(), manifest['nonce'])
        capability.member(manifest['containment'], identity, manifest['nonce'])
        os.write(ready, (json.dumps(identity) + '\n').encode())
        os.close(ready)
        # Strictly bounded control protocol, no stdout parsing or executable YAML.
        data = b''
        while len(data) < 128:
            chunk = os.read(gate, 1)
            if not chunk:
                return 125
            data += chunk
            if chunk == b'\n':
                break
        os.close(gate)
        if data != (manifest['nonce'] + '\n').encode():
            return 125
        capability.member(manifest['containment'], identity, manifest['nonce'])
        os.chdir(manifest['cwd'])
        os.execve(manifest['argv'][0], manifest['argv'], manifest['environment'])
    except BaseException:
        return 126


if __name__ == '__main__':
    sys.exit(main())
