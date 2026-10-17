#!/usr/bin/env python3
"""Plan, execute, verify and publish bounded hierarchical design experiments."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.generative_design import hierarchical_controller as controller
from engineering.generative_design.hierarchical_experiments import plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("plan")
    p = actions.add_parser("run")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--base-commit")
    p.add_argument("--concurrency", type=int, default=2)
    p = actions.add_parser("verify")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--historical", action="store_true")
    p = actions.add_parser("publish")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "plan":
        result = plan()
    elif args.action == "run":
        report = controller.run(
            args.output, base_commit=args.base_commit, concurrency=args.concurrency
        )
        result = dict(
            output=str(args.output),
            work_packages=report["plan"]["work_package_count"],
            promotions=report["promotions"],
        )
    elif args.action == "verify":
        result = controller.verify(args.output, current=not args.historical)
    else:
        result = controller.publish(args.output, args.destination)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
