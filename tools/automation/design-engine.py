#!/usr/bin/env python3
"""Common local design entry point; legacy domain tools retain their own formats."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "design/component-catalogue/src")]
from engineering.design_engine.contracts import load, identity
from engineering.design_engine.registry import problems, get, dependencies
from engineering.design_engine.runtime import (
    request,
    Manager,
    worker,
    comparison,
    compare,
    TERMINAL,
    toolchain,
)
from engineering.design_engine.store import Store


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, default=ROOT / "var/design-engine")
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("problems")
    p.add_argument("id", nargs="?")
    for action in ("run", "refine", "search", "iterate"):
        p = sub.add_parser(action)
        p.add_argument("--problem", required=True)
        p.add_argument("--city", required=True)
        p.add_argument("--project")
        p.add_argument(
            "--environment",
            choices=["simulation", "physical", "training"],
            default="simulation",
        )
        p.add_argument("--revision", default="research-1")
        p.add_argument("--baseline-sha256")
        p.add_argument("--run-id")
        p.add_argument("--asset-id")
        p.add_argument("--part-id")
        p.add_argument("--candidates", type=Path)
        p.add_argument(
            "--interactions",
            type=Path,
            help="JSON containing bounded two-level factors and an evaluation budget",
        )
        p.add_argument("--shortlist", type=int, default=3)
        p.add_argument("--refine", action="store_true")
        p.add_argument("--evaluations", type=int)
        p.add_argument("--wall-seconds", type=int)
        p.add_argument("--proposals", type=int)
        p.add_argument("--seeds", type=int, nargs="+", default=[11, 29, 47])
        if action == "iterate":
            p.add_argument("--rounds", type=int, help="Maximum deterministic recursive rounds")
            p.add_argument("--confirmations", type=int, help="Maximum actual native confirmation attempts")
            p.add_argument("--finite-exhaustive", action="store_true", default=None,
                           help="Enumerate the bounded all-choice domain; physical acceptance stays open")
            p.add_argument("--recursive-policy", type=Path,
                           help="JSON bounded recursive tuning; verification checks remain controlled")
    p = sub.add_parser("jobs")
    p.add_argument("--city", required=True)
    p.add_argument("--environment", default="simulation")
    for action in ("verify", "cancel", "resume", "show", "export"):
        p = sub.add_parser(action)
        p.add_argument("job")
        if action == "verify":
            p.add_argument(
                "--historical",
                action="store_true",
                help="Verify retained bytes without claiming current-source applicability",
            )
        if action == "export":
            p.add_argument("--output", type=Path, required=True)
            p.add_argument(
                "--native",
                action="store_true",
                help="Generate and reopen native CAD/STEP/inspection drawings and available IFC",
            )
    p = sub.add_parser("compare")
    p.add_argument("jobs", nargs="+")
    for action in ("_worker", "_driver"):
        p = sub.add_parser(action)
        p.add_argument("--store", type=Path, required=True)
        p.add_argument("--job", required=True)
    for action, command in sub.choices.items():
        if action not in {"_worker", "_driver"}:
            command.add_argument("--store", type=Path, default=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.action == "_worker":
        return worker(args.store, args.job)
    if args.action == "_driver":
        Manager(args.store, recover_pending=False)._launch(args.job)
        return 0
    if args.action == "problems":
        print(
            json.dumps(get(args.id) if args.id else list(problems().values()), indent=2)
        )
        return 0
    if args.action in ("run", "refine", "search", "iterate"):
        scope = identity(
            dict(
                schema="osr-design-identity/1",
                city=args.city,
                project=args.project or args.city,
                environment=args.environment,
                configuration_revision=args.revision,
                baseline_sha256=args.baseline_sha256,
                run_id=args.run_id,
                asset_id=args.asset_id,
                part_id=args.part_id,
            )
        )
        budget = {}
        if args.evaluations is not None:
            budget["evaluations"] = args.evaluations
        if args.wall_seconds is not None:
            budget["wall_seconds"] = args.wall_seconds
        recursive = None
        if args.action == "iterate":
            recursive = load(args.recursive_policy) if args.recursive_policy else {}
            if not isinstance(recursive, dict):
                raise ValueError("recursive policy must be a structured tuning object")
            recursive = dict(recursive)
            if args.proposals is not None:
                recursive["evaluations"] = args.proposals
            elif "evaluations" not in recursive:
                recursive["evaluations"] = 32
            if args.rounds is not None:
                recursive["iterations"] = args.rounds
            if args.confirmations is not None:
                recursive["confirmations"] = args.confirmations
            if args.finite_exhaustive is not None:
                recursive["finite_exhaustive"] = args.finite_exhaustive
        req = request(
            args.problem,
            scope,
            load(args.candidates) if args.candidates else None,
            refine=args.refine or args.action == "refine",
            shortlist=args.shortlist,
            budget=budget,
            search=(
                dict(seeds=args.seeds, evaluations=args.proposals if args.proposals is not None else 32)
                if args.action == "search"
                else None
            ),
            interactions=load(args.interactions) if args.interactions else None,
            recursive=recursive,
        )
        manager = Manager(args.store)
        job = manager.start(req)
        print("Local design job:", job["id"], flush=True)
        while True:
            current = manager.store.get(job["id"])
            if current["status"] in TERMINAL:
                break
            time.sleep(0.2)
        result = {
            k: current[k]
            for k in ("id", "status", "phase", "error", "physical_release")
        }
        if args.action == "iterate" and current["status"] == "completed":
            recursive_result = comparison(manager.store, job["id"])["recursive_search"]
            result["recursive_search"] = {
                key: recursive_result[key]
                for key in (
                    "incumbent_id", "termination_reason", "finite_domain_complete",
                    "native_domain_complete", "best_verified_in_tested_domain_claimed",
                    "best_verified_claim_scope", "decision_trace_sha256",
                )
            }
            result["recursive_search"]["report_path"] = str(
                manager.store.root / "runs" / job["id"]
                / f"attempt-{current['active_attempt']:04d}" / "recursive-search.json"
            )
        print(json.dumps(result, indent=2))
        return 0 if current["status"] == "completed" else 1
    store = Store(args.store)
    if args.action == "jobs":
        result = store.list(args.city, args.environment)
    elif args.action == "show":
        result = store.get(args.job)
    elif args.action == "cancel":
        result = store.cancel(args.job)
    elif args.action == "resume":
        manager = Manager(args.store)
        result = manager.resume(args.job)
        while manager.store.get(args.job)["status"] not in TERMINAL:
            time.sleep(0.2)
        result = manager.store.get(args.job)
    elif args.action == "compare":
        result = compare(store, args.jobs)
    elif args.action == "verify":
        job = store.verify_request(args.job)
        adapter = job["request"]["problem"]["adapter"]
        if not args.historical and (
            job["request"]["dependencies"] != dependencies(adapter)
            or job["request"]["toolchain"] != toolchain(adapter)
        ):
            raise ValueError(
                "stale design evidence; original attempts remain inspectable"
            )
        result = [
            store.verify_attempt(args.job, a["number"])
            for a in job["attempts"]
            if a["manifest"]
        ]
        if not result:
            raise ValueError("no sealed execution to verify")
    elif args.action == "export":
        from engineering.design_engine.export import export

        result = export(store, args.job, args.output, native=args.native)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, RuntimeError) as error:
        print("Design engine:", error, file=sys.stderr)
        raise SystemExit(1)
