#!/usr/bin/env python3
"""Refresh planning CAPEX from controlled rates, preserving historical evidence."""

from __future__ import annotations

import hashlib
import argparse
import json
import re
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CAPEX = tomllib.loads((REPO_ROOT / "lib/templates/capex-costs.toml").read_text())
CIVIL_COST_MODEL = tomllib.loads(
    (REPO_ROOT / "lib/templates/civil-cost-model.toml").read_text()
)
CIVIL_RATES = CIVIL_COST_MODEL["civil_usd_per_km"]
USD_TO_EUR = float(CAPEX["schema"]["usd_to_eur"])
EPC_FRACTION = float(CAPEX["overhead"]["epc_fraction"])
CHARGING_UNIT_USD = CAPEX["charging_microgrid_unit_usd"]


def replace_number(text: str, key: str, value: float) -> str:
    pattern = re.compile(rf"^(?P<prefix>{re.escape(key)}\s*=\s*)[^\s#]+(?P<suffix>.*)$", re.MULTILINE)
    updated, count = pattern.subn(
        lambda match: f"{match.group('prefix')}{value:.0f}{match.group('suffix')}",
        text,
        count=1,
    )
    if count != 1:
        raise ValueError(f"expected exactly one {key}, found {count}")
    return updated


def recalculate(path: Path) -> bool:
    text = path.read_text()
    design = tomllib.loads(text)
    costs = design["costs"]
    families = {
        str(line["rolling_stock"])
        for line in design.get("lines", [])
        if line.get("rolling_stock")
    }
    if len(families) != 1:
        raise ValueError(f"{path}: expected one rolling-stock family, found {sorted(families)}")
    family = next(iter(families))
    scenario_path = path.parent / f"{design['city']['slug']}.toml"
    scenario = tomllib.loads(scenario_path.read_text(encoding="utf-8"))
    charging_powers = {
        int(station.get("charging_power_kw", 0))
        for station in scenario.get("stations", [])
        if int(station.get("charging_power_kw", 0)) > 0
    }
    if len(charging_powers) != 1 or next(iter(charging_powers)) % 500:
        raise ValueError(
            f"{scenario_path}: expected one repeated 500 kW charging-module power"
        )
    cabinet_count = next(iter(charging_powers)) // 500
    civil_totals = {"at-grade": 0.0, "elevated": 0.0, "bridge": 0.0}
    for segment in design.get("civil_segments", []):
        civil_class = str(segment["class"])
        length_m = float(segment["to_station_m"]) - float(segment["from_station_m"])
        multiplier = (
            float(segment.get("elevated_cost_multiplier", 1.0))
            if civil_class == "elevated"
            else 1.0
        )
        civil_totals[civil_class] += length_m * multiplier
    at_grade_usd = round(civil_totals["at-grade"] / 1000.0 * CIVIL_RATES["at_grade"])
    elevated_usd = round(civil_totals["elevated"] / 1000.0 * CIVIL_RATES["elevated"])
    bridge_usd = round(civil_totals["bridge"] / 1000.0 * CIVIL_RATES["bridge"])
    junction_premium_usd = float(costs["junction_premium_usd"])
    civil_subtotal_usd = round(
        at_grade_usd + elevated_usd + bridge_usd + junction_premium_usd
    )
    charging_microgrid_usd = round(
        sum(
            float(CHARGING_UNIT_USD.get(station.get("archetype"), CHARGING_UNIT_USD["standard"]))
            for station in design.get("stations", [])
        )
        * cabinet_count
    )
    stations_usd = sum(float(CAPEX["station_unit_usd"][s["archetype"]]) for s in design.get("stations", []))
    depots_usd = sum(float(CAPEX["depot_unit_usd"][d["archetype"]]) for d in design.get("depots", []))
    rolling_stock_usd = sum(int(f["trainset_count"]) for f in design.get("fleets", [])) * float(CAPEX["trainset_unit_usd"][family])
    pre_epc_usd = stations_usd + depots_usd + rolling_stock_usd + float(costs["signalling_usd"]) + charging_microgrid_usd + civil_subtotal_usd
    epc_usd = round(pre_epc_usd * EPC_FRACTION)
    total_usd = round(pre_epc_usd + epc_usd)
    values = {
        "at_grade_usd": at_grade_usd,
        "at_grade_eur": round(at_grade_usd * USD_TO_EUR),
        "elevated_usd": elevated_usd,
        "elevated_eur": round(elevated_usd * USD_TO_EUR),
        "bridge_usd": bridge_usd,
        "bridge_eur": round(bridge_usd * USD_TO_EUR),
        "civil_subtotal_usd": civil_subtotal_usd,
        "civil_subtotal_eur": round(civil_subtotal_usd * USD_TO_EUR),
        "production_plant_usd": 0.0,
        "production_plant_eur": 0.0,
        "charging_microgrid_usd": charging_microgrid_usd,
        "charging_microgrid_eur": round(charging_microgrid_usd * USD_TO_EUR),
        "station_charging_cabinet_count": cabinet_count,
        "stations_usd": stations_usd,
        "stations_eur": round(stations_usd * USD_TO_EUR),
        "depots_usd": depots_usd,
        "depots_eur": round(depots_usd * USD_TO_EUR),
        "rolling_stock_usd": rolling_stock_usd,
        "rolling_stock_eur": round(rolling_stock_usd * USD_TO_EUR),
        "epc_overhead_usd": epc_usd,
        "epc_overhead_eur": round(epc_usd * USD_TO_EUR),
        "total_usd": total_usd,
        "total_eur": round(total_usd * USD_TO_EUR),
    }
    updated = text
    for key, value in values.items():
        updated = replace_number(updated, key, value)
    if updated == text:
        return False
    with tempfile.NamedTemporaryFile(
        "w", dir=path.parent, delete=False, encoding="utf-8"
    ) as handle:
        handle.write(updated)
        temporary = Path(handle.name)
    temporary.replace(path)
    return True


def without_costs(raw: bytes) -> dict:
    data = tomllib.loads(raw.decode("utf-8"))
    data.pop("costs", None)
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--city", help="comma-separated slugs; default all catalogue cities")
    parser.add_argument("--skip", default="", help="comma-separated already regenerated cities")
    args = parser.parse_args()
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools/automation/generate-civil-cost-model.py"), "--check"],
        cwd=REPO_ROOT,
        check=True,
    )
    changed = 0
    migrations = []
    design_paths = sorted((REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml"))
    for path in design_paths:
        previous_bytes = path.read_bytes()
        slug = tomllib.loads(previous_bytes.decode())["city"]["slug"]
        if args.city and slug not in args.city.split(","):
            continue
        if slug in args.skip.split(","):
            continue
        previous_current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if recalculate(path):
            changed += 1
            if without_costs(previous_bytes) != without_costs(path.read_bytes()):
                raise ValueError(f"{path}: unexpected non-cost change")
            migrations.append({"city": slug, "design": path.relative_to(REPO_ROOT).as_posix(),
                               "previous_sha256": previous_current_hash,
                               "current_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                               "change_scope": "costs-only", "retained_solver_evidence": "historical-refresh-required"})
    # Never rewrite old run hashes, approved reviews, or workspace source locks.
    receipt = REPO_ROOT / "build/capex-migration.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({"migrations": migrations}, indent=2) + "\n")
    print(f"recalculated {changed} city CAPEX blocks; historical evidence and source locks preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
