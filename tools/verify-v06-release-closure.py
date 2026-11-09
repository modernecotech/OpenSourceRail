#!/usr/bin/env python3
"""Check whether the declared v0.6 digital design-closure gates permit release."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engineering.v06_design_closure.release_gate import inspect


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        report = inspect(args.root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({'release_ready': False, 'error': str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0 if report['release_ready'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
