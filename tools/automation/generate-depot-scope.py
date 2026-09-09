#!/usr/bin/env python3
"""Reconcile city depot energy quantities, budget allowances and stabling needs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "design/component-catalogue/src"))
from osr_mech.depot.energy import depot_energy_scope  # noqa: E402

TEMPLATES = ROOT / "lib/templates"
MANIFEST = ROOT / "design/component-catalogue/catalog/buildable-stations/station-kit-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stabling_requirements(design: dict, scenario: dict, profiles: dict) -> list[dict]:
    """Reproduce initial dispatch queues, without crediting fictitious sidings."""
    families = {line.get("name", line.get("id")): line["rolling_stock"] for line in design["lines"]}
    rows = []
    for fleet in scenario["fleets"]:
        line = fleet["line"]
        count = int(fleet["trainset_count"])
        if count < 0 or count != fleet["trainset_count"]:
            raise ValueError(f"{line}: invalid trainset count")
        points = fleet.get("dispatch_points", [])
        if not points:
            raise ValueError(f"{line}: fleet has no dispatch points")
        length = float(profiles[families[line]]["length_m"])
        if not math.isfinite(length) or length <= 0:
            raise ValueError(f"{line}: invalid train length")
        allocations = {}
        for index, point in enumerate(points):
            assigned = count // len(points) + int(index < count % len(points))
            station = point["station"]
            allocations[station] = allocations.get(station, 0) + assigned
        for station, assigned in allocations.items():
            rows.append({
                "line": line, "station": station, "initial_trainset_count": assigned,
                "train_length_m": length,
                "train_body_length_m": assigned * length,
                "minimum_slot_length_with_clearance_m": assigned * (length + 10.0),
                "verified_stabling_slots": None,
                "status": "physical-allocation-missing",
            })
    return rows


def build_report(design_path: Path) -> dict:
    design_path = design_path.resolve()
    design = tomllib.loads(design_path.read_text())
    slug = design["city"]["slug"]
    scenario_path = design_path.with_name(f"{slug}.toml")
    scenario = tomllib.loads(scenario_path.read_text())
    costs = tomllib.loads((TEMPLATES / "capex-costs.toml").read_text())
    profiles = tomllib.loads((TEMPLATES / "rolling-stock.toml").read_text())["profiles"]
    station_manifest = json.loads(MANIFEST.read_text())
    reference = next(v for v in station_manifest["variants"] if v["archetype"] == "depot-terminal")["parameters"]
    sites = {}
    for site in scenario.get("sites", []):
        if site["station"] in sites:
            raise ValueError(f"duplicate physical energy site {site['station']}")
        sites[site["station"]] = site
    depots = []
    seen = set()
    for depot in design.get("depots", []):
        station = depot.get("station") or depot.get("station_id")
        if station in seen:
            raise ValueError(f"duplicate depot at {station}")
        seen.add(station)
        if station not in sites:
            raise ValueError(f"depot {station}: no operating energy site")
        archetype = depot["archetype"]
        scope = depot_energy_scope(archetype, site=sites[station])
        canonical = depot_energy_scope(archetype)
        reference_matches = archetype == "main-heavy" and all(
            reference[output] == scope[field] for output, field in (
                ("depot_pv_nameplate_kw", "pv_nameplate_kw"),
                ("depot_storage_capacity_kwh", "storage_capacity_kwh"),
                ("depot_storage_module_count", "storage_module_count"),
            )
        )
        # Existing repository planning rates provide an explicit sensitivity,
        # not a new supplier quote or an addition to the city budget.
        storage_rate = float(costs["station_800v_module_usd"]["stationary_lfp_500kwh"]) / 500.0
        pv_rate = float(costs["solar_power_plant"]["utility_pv_usd_per_kw"])
        depots.append({
            "station": station, "archetype": archetype, **scope,
            "catalogue_bom_quantities_reconciled": reference_matches,
            "site_override_from_catalogue": any(scope[k] != canonical[k] for k in ("pv_nameplate_kw", "storage_capacity_kwh", "storage_module_kwh")),
            "workshop_bays": int(depot.get("fleet_stalls", 0)),
            "cost_reconciliation": {
                "depot_base_allowance_usd": float(costs["depot_unit_usd"][archetype]),
                "additional_pv_reference_usd": scope["additional_pv_kw"] * pv_rate,
                "additional_storage_reference_usd": scope["additional_storage_kwh"] * storage_rate,
                "additional_equipment_reference_usd": scope["additional_pv_kw"] * pv_rate + scope["additional_storage_kwh"] * storage_rate,
                "pv_reference_usd_per_kw": pv_rate,
                "storage_reference_usd_per_kwh": storage_rate,
                "included_in_existing_allowance_verified": False,
                "applied_to_city_capex": False,
                "basis": "sensitivity using existing utility-PV and 500 kWh battery equipment rates; not an installed depot quotation",
                "unpriced_scope": ["canopy/racking and foundations", "power conversion and DC distribution", "utility/protection works", "battery compound and fire separation", "installation and renewal/disposal"],
            },
        })
    policy = tomllib.loads((TEMPLATES / "depots.toml").read_text())["operations"]["overnight_distributed_stabling"]
    allocations = stabling_requirements(design, scenario, profiles)
    quantities_reconciled = bool(depots) and all(d["catalogue_bom_quantities_reconciled"] for d in depots)
    sources = {
        "design_sha256": design_path,
        "scenario_sha256": scenario_path,
        "generator_sha256": Path(__file__),
        "scope_model_sha256": ROOT / "design/component-catalogue/src/osr_mech/depot/energy.py",
        "depot_template_sha256": TEMPLATES / "depots.toml",
        "energy_template_sha256": TEMPLATES / "energy-sites.toml",
        "cost_template_sha256": TEMPLATES / "capex-costs.toml",
        "rolling_stock_template_sha256": TEMPLATES / "rolling-stock.toml",
        "station_manifest_sha256": MANIFEST,
        "simulator_source_sha256": ROOT / "crates/osr-sim/src/sim.rs",
    }
    return {
        "schema_version": 1, "city": slug,
        **{key: sha256(path) for key, path in sources.items()},
        "source_paths": {key: str(path.relative_to(ROOT)) for key, path in sources.items()},
        "quantities_reconciled": quantities_reconciled,
        "overnight_stabling_policy": policy,
        "workshop_bays_are_fleet_parking": False,
        "depots": depots, "initial_dispatch_requirements": allocations,
        "fleet_trainsets": sum(r["initial_trainset_count"] for r in allocations),
        "passed": False, "deployment_release_ready": False,
        "open_gates": ["site PV and stationary-storage placement", "itemised depot energy budget and allowance reconciliation", "station-by-station healthy-fleet overnight allocation with usable tracks", "coordinated morning starts and conflict-aware evening run-in/morning run-out"],
        "limitations": [
            "Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.",
            "PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.",
            "Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.",
            "Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.",
            "Workshop bays and passenger platforms are not credited as verified overnight stabling slots.",
        ],
    }


def render_markdown(report: dict) -> str:
    lines = [f"# {report['city']} depot scope reconciliation", "",
             f"Depot energy quantities reconciled: **{'yes' if report['quantities_reconciled'] else 'no'}**. Physical/cost/stabling closure: **open**.", "",
             "The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.", "",
             "| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |",
             "|---|---:|---:|---:|---:|"]
    for d in report["depots"]:
        lines.append(f"| {d['station']} | {d['pv_nameplate_kw']:,.0f} | {d['storage_module_count']} / {d['storage_capacity_kwh']:,.0f} | {d['required_pv_module_area_m2']:,.1f} / {d['reference_pv_canopy_m2']:,.0f} | {d['cost_reconciliation']['additional_equipment_reference_usd']:,.0f} |")
    lines += ["", "The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.", "",
              "| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |",
              "|---|---|---:|---:|---:|---|"]
    for row in report["initial_dispatch_requirements"]:
        lines.append(f"| {row['station']} | {row['line']} | {row['initial_trainset_count']} | {row['train_body_length_m']:,.1f} | {row['minimum_slot_length_with_clearance_m']:,.1f} | unverified |")
    lines += ["", *[f"- {item}" for item in report["limitations"]], "", "Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.", ""]
    return "\n".join(lines)


def generate(design: Path) -> dict:
    report = build_report(design)
    output = design.resolve().parent / "engineering/depot-scope"
    output.mkdir(parents=True, exist_ok=True)
    for name, content in (("summary.json", json.dumps(report, indent=2, sort_keys=True) + "\n"), ("README.md", render_markdown(report))):
        with tempfile.NamedTemporaryFile("w", dir=output, delete=False) as handle:
            handle.write(content)
        os.replace(handle.name, output / name)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true")
    selection.add_argument("--design", type=Path)
    args = parser.parse_args()
    paths = sorted((ROOT / "cities/catalogue").glob("*/*/*/design.toml")) if args.all else [args.design]
    for path in paths:
        report = generate(path)
        print(f"{report['city']}: quantities={report['quantities_reconciled']}, placement/cost/stabling=open")
    # Successful evidence generation is distinct from the open design gates.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
