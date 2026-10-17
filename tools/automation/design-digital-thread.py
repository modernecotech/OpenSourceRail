#!/usr/bin/env python3
"""Run and inspect federated mechanical, civil, software and factory design twins."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.generative_design import digital_thread
from engineering.generative_design.digital_thread_telemetry import replay


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("plan")
    p = actions.add_parser("run")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--concurrency", type=int, default=3)
    p = actions.add_parser("verify")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--historical", action="store_true")
    p.add_argument("--replay", action="store_true")
    p = actions.add_parser("observe")
    p.add_argument("--packet", type=Path, required=True)
    p.add_argument("--observations", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "plan":
        graph = digital_thread.specification_graph()
        result = dict(work_packages=len(graph["packages"]), source_qualified_items=len(graph["items"]),
            source_attributes=sum(len(i["attributes"]) for i in graph["items"]),
            lanes=list(digital_thread.LANES), **digital_thread.FLAGS)
    elif args.action == "run":
        result = digital_thread.run(args.output, concurrency=args.concurrency)
    elif args.action == "verify":
        result = digital_thread.verify(args.output, current=not args.historical, replay=args.replay)
    else:
        if args.output.exists():
            raise ValueError("use a fresh observation result file")
        if args.observations.stat().st_size > 10_000_000:
            raise ValueError("observation batch exceeds 10 MB")
        digital_thread.verify(args.packet)
        contract = json.loads((args.packet / "telemetry-contract.json").read_text())
        result = replay(json.loads(args.observations.read_text()), contract)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation prevents accidental replacement after validation.
        with args.output.open("xb") as stream:
            stream.write(digital_thread.encoded(result))
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
