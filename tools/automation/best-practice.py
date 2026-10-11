#!/usr/bin/env python3
"""Generate/check reviewed component guidance without network or release actions."""
import argparse
from datetime import date
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engineering.best_practice.register import OUTPUTS, build, check


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "check", "review-sources"))
    parser.add_argument("--as-of", type=date.fromisoformat, required=True,
                        help="Explicit ISO assessment date; source age is never inferred from a frozen report.")
    args = parser.parse_args()
    try:
        if args.command == "review-sources":
            result = json.loads(build(ROOT, args.as_of)["coverage.json"])
            if result["source_refresh_required"]:
                raise ValueError("source refresh required: " + ", ".join(
                    row["source_id"] for row in result["source_refresh_required"]))
        if args.command == "generate":
            results = build(ROOT, args.as_of)
            for name, path in OUTPUTS.items():
                destination = ROOT / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(results[name].encode())
        if args.command != "review-sources":
            result = check(ROOT, args.as_of)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"Best-practice check failed: {error}\n")
    print(json.dumps({k: result[k] for k in ("assessed_on", "inventory_count", "mapped_count",
        "practice_count", "source_count", "documentation_coverage_complete", "physical_validation")}))


if __name__ == "__main__":
    main()
