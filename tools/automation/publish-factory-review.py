#!/usr/bin/env python3
"""Project one common factory job export into a compact, immutable review snapshot."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]

from engineering.design_engine.factory_review import publish_snapshot, verify_snapshot

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--export", dest="source", type=Path)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--check", action="store_true")
parser.add_argument("--current", action="store_true")
args = parser.parse_args()
if args.check:
    result = verify_snapshot(args.output, current=args.current)
elif args.source:
    result = publish_snapshot(args.source, args.output)
else:
    parser.error("--export or --check required")
print(json.dumps(result, indent=2))
