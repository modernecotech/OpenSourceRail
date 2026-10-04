#!/usr/bin/env python3
"""Compatibility command: Baghdad now has one complete root publication."""
from pathlib import Path
import subprocess
import sys
if __name__ == '__main__':
    raise SystemExit(subprocess.call([sys.executable,str(Path(__file__).with_name('build-baghdad-proposal.py')),*sys.argv[1:]]))
