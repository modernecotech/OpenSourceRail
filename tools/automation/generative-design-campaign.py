#!/usr/bin/env python3
"""Run a bounded multi-agent design scenario and audit whole-system closure."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.generative_design import (
    campaign,
    review,
    queue_campaign,
    architecture_campaign,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("plan")
    p = sub.add_parser("run")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--civil-budget", type=int, default=128)
    p.add_argument("--mechanical-budget", type=int, default=128)
    p.add_argument("--native", action="store_true")
    p.add_argument("--common", choices=["none", "screen", "native"], default="native")
    p.add_argument("--common-store", type=Path)
    p.add_argument("--import-job", action="append", default=[])
    p.add_argument("--revision", default="multi-agent-manufacturing-1")
    p = sub.add_parser("verify")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--historical", action="store_true")
    p = sub.add_parser("architecture")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--native", action="store_true")
    p = sub.add_parser("verify-architecture")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--historical", action="store_true")
    p = sub.add_parser("publish-architecture")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--destination", type=Path, required=True)
    p = sub.add_parser("verify-architecture-snapshot")
    p.add_argument("--destination", type=Path, required=True)
    p.add_argument("--historical", action="store_true")
    p = sub.add_parser("queue")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--native", action="store_true")
    p = sub.add_parser("verify-queue")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--historical", action="store_true")
    p = sub.add_parser("publish-queue")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--destination", type=Path, required=True)
    p = sub.add_parser("verify-queue-snapshot")
    p.add_argument("--destination", type=Path, required=True)
    p.add_argument("--historical", action="store_true")
    p = sub.add_parser("publish")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--destination", type=Path, required=True)
    p = sub.add_parser("verify-snapshot")
    p.add_argument("--destination", type=Path, required=True)
    p.add_argument("--historical", action="store_true")
    args = parser.parse_args()
    if args.action == "plan":
        result = campaign.plan()
    elif args.action == "run":
        result = campaign.run(
            args.output,
            civil_budget=args.civil_budget,
            mechanical_budget=args.mechanical_budget,
            native=args.native,
            common=args.common,
            common_store=args.common_store,
            import_jobs=args.import_job,
            revision=args.revision,
        )
    elif args.action == "verify":
        result = campaign.verify(args.output, current=not args.historical)
    elif args.action == "architecture":
        result = architecture_campaign.run(args.output, native=args.native)
    elif args.action == "verify-architecture":
        result = architecture_campaign.verify(args.output, current=not args.historical)
    elif args.action == "publish-architecture":
        result = architecture_campaign.publish(args.output, args.destination)
    elif args.action == "verify-architecture-snapshot":
        result = architecture_campaign.verify(
            args.destination, current=not args.historical, snapshot=True
        )
    elif args.action == "queue":
        result = queue_campaign.run(args.output, native=args.native)
    elif args.action == "verify-queue":
        result = queue_campaign.verify(args.output, current=not args.historical)
    elif args.action == "publish-queue":
        result = queue_campaign.publish(args.output, args.destination)
    elif args.action == "verify-queue-snapshot":
        result = queue_campaign.verify(
            args.destination, current=not args.historical, snapshot=True
        )
    elif args.action == "publish":
        result = review.publish(args.output, args.destination)
    else:
        result = review.verify_snapshot(args.destination, current=not args.historical)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
