#!/usr/bin/env python3
"""Reject drift between CAD-derived civil quantities and structures.toml."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mechanical-py/src"))

from osr_mech.civil.quantity_model import structure_quantities_per_km  # noqa: E402


def main() -> int:
    with (ROOT / "lib/templates/structures.toml").open("rb") as handle:
        actual = tomllib.load(handle)["classes"]
    expected = structure_quantities_per_km()
    mismatches: list[str] = []
    for class_id, fields in expected.items():
        for key, value in fields.items():
            if actual[class_id].get(key) != value:
                mismatches.append(
                    f"classes.{class_id}.{key}: template={actual[class_id].get(key)!r}, geometry={value!r}"
                )
    if mismatches:
        print("structure quantity drift:")
        for mismatch in mismatches:
            print(f"  - {mismatch}")
        return 1
    print("structures.toml matches CAD-derived civil quantities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
