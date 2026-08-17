#!/usr/bin/env python3
"""Remove duplicated city factories and recalculate city CAPEX in place."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CAPEX = tomllib.loads((REPO_ROOT / "lib/templates/capex-costs.toml").read_text())
USD_TO_EUR = float(CAPEX["schema"]["usd_to_eur"])
EPC_FRACTION = float(CAPEX["overhead"]["epc_fraction"])
CHARGING_UNIT_USD = CAPEX["charging_microgrid_unit_usd"]
PROVENANCE_SUFFIXES = {".json", ".md", ".toml", ".txt", ".xml"}


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
    charging_microgrid_usd = round(
        sum(
            float(CHARGING_UNIT_USD.get(station.get("archetype"), CHARGING_UNIT_USD["standard"]))
            for station in design.get("stations", [])
        )
        * cabinet_count
    )
    pre_epc_usd = sum(
        float(costs[key])
        for key in (
            "civil_subtotal_usd",
            "stations_usd",
            "depots_usd",
            "rolling_stock_usd",
            "signalling_usd",
        )
    ) + charging_microgrid_usd
    epc_usd = round(pre_epc_usd * EPC_FRACTION)
    total_usd = round(pre_epc_usd + epc_usd)
    values = {
        "production_plant_usd": 0.0,
        "production_plant_eur": 0.0,
        "charging_microgrid_usd": charging_microgrid_usd,
        "charging_microgrid_eur": round(charging_microgrid_usd * USD_TO_EUR),
        "station_charging_cabinet_count": cabinet_count,
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


def head_version(path: Path) -> bytes:
    relative = path.relative_to(REPO_ROOT).as_posix()
    completed = subprocess.run(
        ["git", "show", f"HEAD:{relative}"],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return completed.stdout


def without_costs(raw: bytes) -> dict:
    data = tomllib.loads(raw.decode("utf-8"))
    data.pop("costs", None)
    return data


def replace_hash(path: Path, old_hash: str, new_hash: str) -> bool:
    if not path.is_file() or path.suffix.lower() not in PROVENANCE_SUFFIXES:
        return False
    text = path.read_text(encoding="utf-8", errors="strict")
    if old_hash not in text:
        return False
    updated = text.replace(old_hash, new_hash)
    with tempfile.NamedTemporaryFile(
        "w", dir=path.parent, delete=False, encoding="utf-8"
    ) as handle:
        handle.write(updated)
        temporary = Path(handle.name)
    temporary.replace(path)
    return True


def refresh_cost_only_provenance(path: Path) -> tuple[str, str]:
    """Re-attest evidence only when the committed/current delta is cost-only.

    Engineering geometry, simulation, GIS, energy and product outputs do not
    consume the [costs] block. This guarded migration avoids rerunning those
    unchanged models while keeping their whole-design provenance pointers
    current. Any non-cost design delta aborts instead of re-attesting evidence.
    """

    previous = head_version(path)
    current = path.read_bytes()
    if without_costs(previous) != without_costs(current):
        raise ValueError(f"{path}: refusing provenance refresh for a non-cost design change")
    old_hash = hashlib.sha256(previous).hexdigest()
    new_hash = hashlib.sha256(current).hexdigest()
    return old_hash, new_hash


def refresh_visual_source_hashes(city_dir: Path) -> bool:
    manifest_path = city_dir / "engineering/screenshots/manifest.json"
    if not manifest_path.is_file():
        return False
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sources = manifest.get("sources", {})
    for key, relative in (
        ("sumo_summary_sha256", "engineering/sumo/summary.json"),
        ("gis_summary_sha256", "engineering/gis/summary.json"),
        ("energy_summary_sha256", "engineering/energy/summary.json"),
    ):
        source_path = city_dir / relative
        sources[key] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    updated = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    if updated == manifest_path.read_text(encoding="utf-8"):
        return False
    with tempfile.NamedTemporaryFile(
        "w", dir=manifest_path.parent, delete=False, encoding="utf-8"
    ) as handle:
        handle.write(updated)
        temporary = Path(handle.name)
    temporary.replace(manifest_path)
    return True


def main() -> int:
    changed = 0
    provenance_files = 0
    hash_updates: list[tuple[str, str]] = []
    design_paths = sorted((REPO_ROOT / "designs").glob("*/*/*/design.toml"))
    for path in design_paths:
        previous_current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if recalculate(path):
            changed += 1
        old_hash, new_hash = refresh_cost_only_provenance(path)
        replacements = {(old_hash, new_hash), (previous_current_hash, new_hash)}
        hash_updates.extend(replacements)
        for artifact in path.parent.rglob("*"):
            for source_hash, target_hash in replacements:
                provenance_files += int(replace_hash(artifact, source_hash, target_hash))
        provenance_files += int(refresh_visual_source_hashes(path.parent))

    # The repository-level validation reports also retain each city design hash.
    for report in (
        REPO_ROOT / "designs/ring-interchange-validation.json",
        REPO_ROOT / "designs/station-cluster-validation.json",
    ):
        for old_hash, new_hash in hash_updates:
            provenance_files += int(replace_hash(report, old_hash, new_hash))

    print(
        f"recalculated {changed} city CAPEX blocks; "
        f"refreshed {provenance_files} cost-only provenance files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
