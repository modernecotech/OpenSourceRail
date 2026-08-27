#!/usr/bin/env python3
"""Generate the civil planning-cost contract from canonical CAD quantities."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MECHANICAL_SRC = REPO_ROOT / "mechanical-py/src"
CALIBRATION_PATH = REPO_ROOT / "lib/templates/civil-cost-calibration.toml"
OUTPUT_PATH = REPO_ROOT / "lib/templates/civil-cost-model.toml"
if str(MECHANICAL_SRC) not in sys.path:
    sys.path.insert(0, str(MECHANICAL_SRC))

from osr_mech.civil.quantity_model import structure_quantities_per_km  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_tree_sha256() -> str:
    paths = sorted((MECHANICAL_SRC / "osr_mech/civil").glob("*.py"))
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(REPO_ROOT).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_model() -> dict[str, object]:
    calibration = tomllib.loads(CALIBRATION_PATH.read_text(encoding="utf-8"))
    quantities = structure_quantities_per_km()
    classes: dict[str, object] = {}
    for name in ("at-grade", "elevated", "bridge"):
        configured = calibration["classes"][name]
        drivers = configured.get("drivers", [])
        costed_share = sum(float(driver["cost_share"]) for driver in drivers)
        if costed_share > 1.0 + 1e-9:
            raise ValueError(f"{name}: driver cost shares exceed 1.0")
        quantity_table = quantities.get(name, {})
        index = 1.0 - costed_share
        rows = []
        for driver in drivers:
            key = str(driver["quantity"])
            if key not in quantity_table:
                raise KeyError(f"{name}: CAD quantity {key!r} is missing")
            current = float(quantity_table[key])
            benchmark = float(driver["benchmark_quantity"])
            ratio = current / benchmark
            share = float(driver["cost_share"])
            index += share * ratio
            rows.append(
                {
                    "quantity": key,
                    "current_quantity": current,
                    "benchmark_quantity": benchmark,
                    "cost_share": share,
                    "quantity_ratio": ratio,
                    "reason": str(driver["reason"]),
                }
            )
        benchmark_rate = float(configured["benchmark_usd_per_km"])
        target_rate = round(benchmark_rate * index / 1000.0) * 1000
        classes[name] = {
            "benchmark_usd_per_km": int(benchmark_rate),
            "design_target_usd_per_km": int(target_rate),
            "design_to_benchmark_ratio": index,
            "unscaled_cost_share": 1.0 - costed_share,
            "drivers": rows,
        }
    return {
        "schema": calibration["schema"],
        "provenance": {
            "generator": "scripts/generate-civil-cost-model.py",
            "calibration_sha256": sha256(CALIBRATION_PATH),
            "civil_source_tree_sha256": source_tree_sha256(),
        },
        "classes": classes,
    }


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render(model: dict[str, object]) -> str:
    schema = model["schema"]
    provenance = model["provenance"]
    classes = model["classes"]
    lines = [
        "# GENERATED FILE — edit civil-cost-calibration.toml or the CAD quantity model.",
        "# Regenerate with: python3 scripts/generate-civil-cost-model.py",
        "",
        "[schema]",
        f"version = {int(schema['version'])}",
        f"currency = {_toml_string(str(schema['currency']))}",
        f"basis = {_toml_string(str(schema['basis']))}",
        'maturity = "planning-target-not-a-quotation"',
        "",
        "[provenance]",
        f"generator = {_toml_string(str(provenance['generator']))}",
        f"calibration_sha256 = {_toml_string(str(provenance['calibration_sha256']))}",
        f"civil_source_tree_sha256 = {_toml_string(str(provenance['civil_source_tree_sha256']))}",
        "",
        "[civil_usd_per_km]",
    ]
    for name in ("at-grade", "elevated", "bridge"):
        key = name.replace("-", "_")
        lines.append(f'{key} = {classes[name]["design_target_usd_per_km"]}')
    lines.extend(["", "[benchmark_civil_usd_per_km]"])
    for name in ("at-grade", "elevated", "bridge"):
        key = name.replace("-", "_")
        lines.append(f'{key} = {classes[name]["benchmark_usd_per_km"]}')
    for name in ("at-grade", "elevated", "bridge"):
        item = classes[name]
        lines.extend(
            [
                "",
                f'[classes.{_toml_string(name)}]',
                f'benchmark_usd_per_km = {item["benchmark_usd_per_km"]}',
                f'design_target_usd_per_km = {item["design_target_usd_per_km"]}',
                f'design_to_benchmark_ratio = {item["design_to_benchmark_ratio"]:.6f}',
                f'unscaled_cost_share = {item["unscaled_cost_share"]:.6f}',
            ]
        )
        for driver in item["drivers"]:
            lines.extend(
                [
                    "",
                    f'[[classes.{_toml_string(name)}.drivers]]',
                    f'quantity = {_toml_string(driver["quantity"])}',
                    f'current_quantity = {driver["current_quantity"]:g}',
                    f'benchmark_quantity = {driver["benchmark_quantity"]:g}',
                    f'cost_share = {driver["cost_share"]:.6f}',
                    f'quantity_ratio = {driver["quantity_ratio"]:.6f}',
                    f'reason = {_toml_string(driver["reason"])}',
                ]
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build_model())
    if args.check:
        if not OUTPUT_PATH.is_file() or OUTPUT_PATH.read_text(encoding="utf-8") != expected:
            print(f"stale: {OUTPUT_PATH.relative_to(REPO_ROOT)}", file=sys.stderr)
            return 1
        print(f"current: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
        return 0
    OUTPUT_PATH.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
