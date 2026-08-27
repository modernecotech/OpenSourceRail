#!/usr/bin/env python3
"""Reject drift across CAD-derived civil quantities and cost contracts."""

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

    with (ROOT / "lib/templates/civil-cost-model.toml").open("rb") as handle:
        cost_contract = tomllib.load(handle)
    with (ROOT / "docs/civil/viaduct-quantity-cost-model.toml").open("rb") as handle:
        viaduct_estimate = tomllib.load(handle)["estimate"]
    elevated = cost_contract["classes"]["elevated"]
    expected_estimate = {
        "active_cost_contract": "lib/templates/civil-cost-model.toml",
        "benchmark_usd_per_km": elevated["benchmark_usd_per_km"],
        "design_target_usd_per_km": elevated["design_target_usd_per_km"],
        "design_to_benchmark_ratio": elevated["design_to_benchmark_ratio"],
    }
    for key, value in expected_estimate.items():
        if viaduct_estimate.get(key) != value:
            mismatches.append(
                f"viaduct estimate.{key}: narrative={viaduct_estimate.get(key)!r}, "
                f"contract={value!r}"
            )
    if mismatches:
        print("structure quantity drift:")
        for mismatch in mismatches:
            print(f"  - {mismatch}")
        return 1
    print("civil structures and viaduct estimate match CAD-derived contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
