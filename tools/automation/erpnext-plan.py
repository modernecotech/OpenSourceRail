#!/usr/bin/env python3
"""Prepare a reviewable ERPNext planning import; never issue financial documents."""
import argparse
import gzip
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "deployment/erpnext/apps/osr_erpnext"))
from osr_erpnext.planning import KINDS, make_plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--kind", action="append", choices=list(KINDS))
    args = parser.parse_args()
    data = args.bundle.read_bytes()
    if args.bundle.suffix == ".gz":
        data = gzip.decompress(data)
    plan = make_plan(json.loads(data), args.kind)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    print(f'{plan["city"]}: {len(plan["records"])} planning tasks → {args.output}')


if __name__ == "__main__":
    main()
