#!/usr/bin/env python3
"""Plan, execute, resume and verify feedback-directed civil/mechanical designs."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.generative_design import design_iteration, design_scenario


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--output", type=Path)
    p = sub.add_parser("run")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--budget", type=int, default=256)
    p.add_argument("--native", action="store_true")
    p.add_argument("--no-baseline", action="store_true")
    p.add_argument("--resume", type=Path)
    p.add_argument("--mode", choices=("repair", "optimization"), default="repair")
    p = sub.add_parser("verify")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--historical", action="store_true")
    p.add_argument("--require-native", action="store_true")
    p = sub.add_parser("publish")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "plan":
        result = design_scenario.plan()
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            result = dict(output=str(args.output), **result["counts"])
    elif args.action == "run":
        result = design_iteration.run(
            args.output,
            budget=args.budget,
            native=args.native,
            baseline=not args.no_baseline,
            resume=args.resume,
            mode=args.mode,
        )
    elif args.action == "verify":
        result = design_iteration.verify(
            args.output, current=not args.historical, require_native=args.require_native
        )
    else:
        result = design_iteration.publish(args.output, args.destination)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
