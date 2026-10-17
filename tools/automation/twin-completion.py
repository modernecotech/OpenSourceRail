#!/usr/bin/env python3
"""Plan, execute and resume bounded AI CAD/BIM design-proposal experiments."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.twin_workflow import core


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    for name in ("init", "run", "status", "verify", "submit", "request", "seed"):
        p = actions.add_parser(name)
        p.add_argument("--workspace", type=Path, required=True)
        if name == "submit":
            p.add_argument("--proposals", type=Path, required=True)
        elif name == "run":
            p.add_argument("--steps", type=int, default=8)
            p.add_argument("--wall-seconds", type=float, default=900)
            p.add_argument("--max-output-mib", type=float, default=512)
            p.add_argument("--reserve-gib", type=float, default=5)
            p.add_argument("--provider-argv", type=Path, help="JSON argv of explicitly configured provider; no shell, 60s/call")
        elif name == "verify":
            p.add_argument("--historical", action="store_true", help="Check retained integrity without claiming current-source evidence")
    p = actions.add_parser("evaluate", help=argparse.SUPPRESS)
    p.add_argument("--proposal", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "init":
        result = core.initialise(args.workspace)
    elif args.action == "run":
        result = core.run(args.workspace, steps=args.steps, wall_seconds=args.wall_seconds,
            max_output_mib=args.max_output_mib, reserve_gib=args.reserve_gib,
            provider_argv=core.read(args.provider_argv) if args.provider_argv else None)
    elif args.action == "status":
        result = core.status(args.workspace)
    elif args.action == "verify":
        result = core.verify(args.workspace, historical=args.historical)
    elif args.action == "submit":
        result = core.submit(args.workspace, core.read(args.proposals))
    elif args.action == "seed":
        from engineering.twin_workflow.examples import seeds
        baseline = core.status(args.workspace)["baseline_sha256"]
        result = core.submit(args.workspace, seeds(baseline))
    elif args.action == "request":
        core.status(args.workspace)
        result = core.provider_request(core.read(args.workspace / "state.json"), core.read(args.workspace / "work-orders.json", maximum=10_000_000))
    else:
        from engineering.twin_workflow.adapters import evaluate
        result = evaluate(core.read(args.proposal), args.output)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
