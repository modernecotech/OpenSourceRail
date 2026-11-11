"""Command-line report for v0.6 software-release readiness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .release_gate import inspect, require_ready


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("readiness",), default="readiness")
    parser.add_argument("--require-ready", action="store_true",
                        help="return a failing status unless every software gate is ready")
    parser.add_argument("--source-commit", help="require this full commit to match the checked-out Git HEAD")
    parser.add_argument("--attestation-bundle", type=Path,
                        help="verify an external immutable proof bundle against a clean checkout")
    parser.add_argument("--expected-repository",
                        help="canonical repository identity obtained from trusted release configuration")
    parser.add_argument("--trusted-reviewer",
                        help="independent reviewer identity obtained through an authenticated channel")
    parser.add_argument("--trusted-reviewer-key-sha256",
                        help="out-of-band SHA-256 fingerprint of the independent reviewer's Ed25519 public key")
    args = parser.parse_args()
    try:
        report = (require_ready if args.require_ready else inspect)(
            ".", source_commit=args.source_commit,
            attestation_bundle=args.attestation_bundle,
            expected_repository=args.expected_repository,
            trusted_reviewer=args.trusted_reviewer,
            trusted_reviewer_key_sha256=args.trusted_reviewer_key_sha256)
    except ValueError as exc:
        print(json.dumps({"software_release_ready": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
