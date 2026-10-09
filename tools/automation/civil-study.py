#!/usr/bin/env python3
"""Run and verify bounded complete civil-system exploration campaigns."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'design/component-catalogue/src'))

from engineering.civil_exploration.contracts import HERE
from engineering.civil_exploration.workflow import run_campaign, verify, compare, derive, worker


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    run = commands.add_parser('run')
    run.add_argument('--config', type=Path, default=HERE/'config/reference.json')
    run.add_argument('--output', type=Path, default=ROOT/'build/engineering/civil-studies/first-campaign')
    run.add_argument('--resume', action='store_true')
    run.add_argument('--retry-failed', action='store_true')
    check = commands.add_parser('verify')
    check.add_argument('bundle', type=Path); check.add_argument('--historical', action='store_true')
    report = commands.add_parser('compare'); report.add_argument('bundle', type=Path)
    child = commands.add_parser('derive')
    child.add_argument('--parent', type=Path, required=True); child.add_argument('--definition', type=Path, required=True)
    child.add_argument('--output', type=Path, required=True)
    child.add_argument('--reason', required=True, help='Reason for the recorded geometry modification')
    native = commands.add_parser('_worker', help=argparse.SUPPRESS)
    native.add_argument('job', type=Path); native.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        if args.command == '_worker':
            worker(args.job, args.output)
            return 0
        if args.command == 'run':
            result = run_campaign(args.config, args.output, resume=args.resume, retry_failed=args.retry_failed)
            rows = json.loads((args.output/'comparison.json').read_text())['rows']
            print(f"Retained {len(rows)} comparisons at {args.output/'comparison.md'}")
            return int(any(r['execution'] != 'completed' or r['numerical_screen'] != 'passed' for r in rows))
        if args.command == 'verify':
            result = verify(args.bundle, current=not args.historical)
            print(f"Verified {len(result['evaluations'])} evaluation attempts; physical release remains false")
        elif args.command == 'compare':
            compare(args.bundle); print(args.bundle/'comparison.md')
        else:
            result = derive(args.parent, args.definition, args.output, reason=args.reason)
            print(result['id'])
        return 0
    except (ValueError, RuntimeError, OSError) as error:
        print(f'Civil study: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
