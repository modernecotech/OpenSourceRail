#!/usr/bin/env python3
"""Prepare, qualify and verify reusable city design options."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'engineering/design-options'))
from workflow import prepare, qualify, verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('prepare')
    create.add_argument('--profile', type=Path, required=True)
    create.add_argument('--output', type=Path, required=True)
    run = commands.add_parser('qualify')
    run.add_argument('bundle', type=Path)
    check = commands.add_parser('verify')
    check.add_argument('bundle', type=Path)
    check.add_argument('--historical', action='store_true', help='Verify sealed evidence without requiring unchanged current source')
    args = parser.parse_args()
    if args.command == 'prepare':
        result = prepare(args.profile, args.output)
    elif args.command == 'qualify':
        result = qualify(args.bundle)
    else:
        result = verify(args.bundle, current=not args.historical)
    print(json.dumps({k: result[k] for k in ('city', 'id', 'passed', 'operating_release') if k in result}, indent=2))
    return 1 if result.get('passed') is False else 0


if __name__ == '__main__':
    raise SystemExit(main())
