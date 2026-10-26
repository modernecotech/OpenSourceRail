#!/usr/bin/env python3
"""Render current-design user units; installation is an explicit separate action.

Run this file to inspect the proposed service/timer text. The service invokes the
same cached current-selection build as ``./osr cycle``. This helper never writes
user configuration, enables a timer or starts work by itself.
"""
import argparse
import json
from pathlib import Path


def units(root, python=None):
    root = Path(root).resolve()
    interpreter = Path(python) if python else root / '.venv/bin/python'
    if any(c in str(root) for c in ('\n','\r','\0')):
        raise ValueError('Ordinary single-line working directory required')
    directory = str(root).replace('%', '%%')
    def arg(value):
        return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%') + '"'
    return {
        'osr-development-baseline.service':
            '[Unit]\nDescription=OpenSourceRail selected development design refresh\n'
            '[Service]\nType=oneshot\nWorkingDirectory=' + directory + '\n'
            'ExecStart=' + arg(interpreter) + ' ' + arg(root / 'tools/automation/default-design.py') + ' cycle\n'
            'TimeoutStartSec=14400\nUMask=0077\n',
        'osr-development-baseline.timer':
            '[Unit]\nDescription=OpenSourceRail selected design source-change refresh\n'
            '[Timer]\nOnBootSec=2min\nOnUnitActiveSec=15min\nPersistent=true\n'
            'Unit=osr-development-baseline.service\n[Install]\nWantedBy=timers.target\n',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--python', type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(units(args.root, args.python), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
