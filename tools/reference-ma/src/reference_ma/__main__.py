"""CLI: read a case JSON, compute MA, print MA JSON.

Input schema (stdin or `--input PATH`):
    {
      "network":  {...}                              # serde(Network)
      "entries":  [ {...}, {...}, ... ]              # serde([Entry])
      "train_id": <u64>,
      "now_ns":   <u64>
    }

Output schema (stdout):
    serde(MovementAuthority) — byte-for-byte matching the JSON
    `osr_interlocking::compute_self_ma` would produce on the same
    input. Divergence is a test failure in the differential harness.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import is_dataclass
from enum import Enum
from typing import Any, Dict, List

from .log import Entry
from .ma import MovementAuthority, compute_self_ma
from .types import Network


def _to_jsonable(obj: Any) -> Any:
    """Recursively lower our dataclasses / enums back to the serde JSON
    shape Rust produces."""
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj):
        out: Dict[str, Any] = {}
        for f in obj.__dataclass_fields__.values():
            out[f.name] = _to_jsonable(getattr(obj, f.name))
        return out
    if isinstance(obj, list):
        return [_to_jsonable(x) for x in obj]
    if isinstance(obj, tuple):
        return [_to_jsonable(x) for x in obj]  # Rust tuples → JSON arrays
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    return obj


def _ma_to_json(ma: MovementAuthority) -> Dict[str, Any]:
    return {
        "train_id": ma.train_id,
        "end": _to_jsonable(ma.end),
        "applicable_restrictions": [
            _to_jsonable(r) for r in ma.applicable_restrictions
        ],
        "valid_until_ns": ma.valid_until_ns,
        "derived_from_entry_id": ma.derived_from_entry_id,
        "has_known_position": ma.has_known_position,
    }


def _load_case(path: str) -> Dict[str, Any]:
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="reference-ma",
        description="Python reference interpreter for osr-interlocking (RFC 0004 M4).",
    )
    ap.add_argument(
        "--input",
        "-i",
        default="-",
        help="Path to case JSON (use '-' for stdin, the default).",
    )
    ap.add_argument(
        "--output",
        "-o",
        default="-",
        help="Path to write MA JSON to (use '-' for stdout, the default).",
    )
    args = ap.parse_args(argv)

    case = _load_case(args.input)
    network = Network.from_json(case["network"])
    entries = [Entry.from_json(e) for e in case["entries"]]
    train_id = int(case["train_id"])
    now_ns = int(case["now_ns"])

    ma = compute_self_ma(train_id, entries, network, now_ns)
    out = _ma_to_json(ma)

    text = json.dumps(out, separators=(",", ":"), sort_keys=False)
    if args.output == "-":
        sys.stdout.write(text + "\n")
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
