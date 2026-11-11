"""Command-line report for v0.6 software-release readiness."""

from __future__ import annotations

import argparse
import json

from .release_gate import inspect, require_ready


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("readiness",), default="readiness")
    parser.add_argument("--require-ready", action="store_true",
                        help="return a failing status unless every software gate is ready")
    parser.add_argument("--source-commit", help="inspect this full Git commit identity")
    args = parser.parse_args()
    try:
        report = (require_ready if args.require_ready else inspect)(
            ".", source_commit=args.source_commit)
    except ValueError as exc:
        print(json.dumps({"software_release_ready": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
