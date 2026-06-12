#!/usr/bin/env python3
"""Generate asset-level QA and maintenance data for the operations portal.

The input is a generated city `design.toml` plus its expanded
`scenario.toml`. The output is a deterministic JSON bundle and three CSV
tables that spreadsheet users can open directly.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import tomllib
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESIGN = REPO_ROOT / "designs/west-asia/Iraq/Samawah/design.toml"
DEFAULT_SCENARIO = REPO_ROOT / "designs/west-asia/Iraq/Samawah/samawah.toml"
DEFAULT_OUT_DIR = REPO_ROOT / "docs/operations-portal/data"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate asset-level QA and maintenance portal data."
    )
    parser.add_argument("--design", type=Path, default=DEFAULT_DESIGN)
    parser.add_argument("--scenario", type=Path, default=DEFAULT_SCENARIO)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    design = _load_toml(args.design)
    scenario = _load_toml(args.scenario)
    qa_template = _load_toml(REPO_ROOT / "lib/templates/construction-qa.toml")
    maint_template = _load_toml(REPO_ROOT / "lib/templates/maintenance-schedule.toml")

    bundle = build_bundle(
        design=design,
        scenario=scenario,
        qa_template=qa_template,
        maint_template=maint_template,
        design_path=args.design,
        scenario_path=args.scenario,
    )

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = bundle["meta"]["city_slug"]
    json_path = out_dir / f"{slug}-operations.json"
    assets_path = out_dir / f"{slug}-assets.csv"
    maintenance_path = out_dir / f"{slug}-maintenance-schedule.csv"
    qa_path = out_dir / f"{slug}-qa-register.csv"

    json_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n")
    _write_csv(assets_path, bundle["assets"])
    _write_csv(maintenance_path, bundle["maintenance_tasks"])
    _write_csv(qa_path, bundle["qa_actions"])

    print(f"wrote {json_path}")
    print(f"wrote {assets_path}")
    print(f"wrote {maintenance_path}")
    print(f"wrote {qa_path}")
    return 0


def build_bundle(
    *,
    design: dict[str, Any],
    scenario: dict[str, Any],
    qa_template: dict[str, Any],
    maint_template: dict[str, Any],
    design_path: Path,
    scenario_path: Path,
) -> dict[str, Any]:
    city = design.get("city", {})
    slug = str(city.get("slug", design_path.parent.name.lower()))
    prefix = _city_prefix(slug)
    stations = list(design.get("stations", []))
    lines = list(design.get("lines", []))
    fleets = list(design.get("fleets", []))
    depots = list(design.get("depots", []))
    switches = list(design.get("switches", []))
    for depot in depots:
        switches.extend(depot.get("switches", []))
    junctions = list(design.get("junctions", []))
    sites = list(scenario.get("sites", []))

    station_asset_by_source: dict[str, str] = {}
    assets: list[dict[str, Any]] = []
    counters: dict[str, int] = {}

    def next_id(kind: str) -> str:
        counters[kind] = counters.get(kind, 0) + 1
        return f"{prefix}-{kind}-{counters[kind]:03d}"

    project_asset_id = next_id("SYS")
    assets.append({
        "asset_id": project_asset_id,
        "source_id": slug,
        "asset_type": "system",
        "subtype": "whole railway",
        "name": f"{_title(slug)} railway system",
        "line": "",
        "parent_asset": "",
        "station": "",
        "km_start": "",
        "km_end": "",
        "location": _location_from_bbox(city.get("bbox", {})),
        "criticality": "system",
    })

    for fleet in fleets:
        line = str(fleet.get("line", "line"))
        line_code = _line_code(line)
        total = int(fleet.get("trainset_count", 0))
        peak = int(fleet.get("peak_count", 0))
        spare = int(fleet.get("spare_count", 0))
        for idx in range(1, total + 1):
            if idx <= peak:
                subtype = "revenue"
            elif idx <= peak + spare:
                subtype = "spare"
            else:
                subtype = "cold-reserve"
            assets.append({
                "asset_id": f"{prefix}-RS-{line_code}-{idx:03d}",
                "source_id": f"{line}-{idx:03d}",
                "asset_type": "rolling-stock",
                "subtype": subtype,
                "name": f"{line} trainset {idx:03d}",
                "line": line,
                "parent_asset": project_asset_id,
                "station": "",
                "km_start": "",
                "km_end": "",
                "location": "fleet",
                "criticality": "service",
            })

    for station in stations:
        asset_id = next_id("ST")
        station_asset_by_source[str(station.get("id"))] = asset_id
        station_name = station.get("anchor_name") or station.get("name") or station.get("id")
        assets.append({
            "asset_id": asset_id,
            "source_id": station.get("id", ""),
            "asset_type": "station",
            "subtype": station.get("archetype", "standard"),
            "name": station_name,
            "line": station.get("line", ""),
            "parent_asset": project_asset_id,
            "station": station.get("id", ""),
            "km_start": _km(station.get("s_m")),
            "km_end": _km(station.get("s_m")),
            "location": _lat_lon(station),
            "criticality": "public",
        })

    stations_by_line: dict[str, list[dict[str, Any]]] = {}
    for station in stations:
        stations_by_line.setdefault(str(station.get("line", "")), []).append(station)
    for line, line_stations in stations_by_line.items():
        ordered = sorted(line_stations, key=lambda s: float(s.get("s_m", 0.0)))
        line_code = _line_code(line)
        for idx, (a, b) in enumerate(zip(ordered, ordered[1:]), start=1):
            a_s = float(a.get("s_m", 0.0))
            b_s = float(b.get("s_m", a_s))
            assets.append({
                "asset_id": f"{prefix}-TRK-{line_code}-{idx:03d}",
                "source_id": f"{a.get('id')}--{b.get('id')}",
                "asset_type": "track-section",
                "subtype": "standard-urban",
                "name": f"{line} section {idx:03d}",
                "line": line,
                "parent_asset": project_asset_id,
                "station": f"{a.get('id')} to {b.get('id')}",
                "km_start": _km(a_s),
                "km_end": _km(b_s),
                "location": f"{_display_station(a)} to {_display_station(b)}",
                "criticality": "safety",
            })

    for switch in switches:
        station_id = str(switch.get("station", ""))
        assets.append({
            "asset_id": next_id("SW"),
            "source_id": switch.get("id", ""),
            "asset_type": "switch",
            "subtype": switch.get("kit", ""),
            "name": switch.get("id", ""),
            "line": _line_from_station_id(station_id),
            "parent_asset": station_asset_by_source.get(station_id, project_asset_id),
            "station": station_id,
            "km_start": "",
            "km_end": "",
            "location": f"{station_id} {switch.get('side', '')}".strip(),
            "criticality": "safety",
        })

    for depot in depots:
        station_id = str(depot.get("station", ""))
        assets.append({
            "asset_id": next_id("DEP"),
            "source_id": f"depot-{station_id}",
            "asset_type": "depot",
            "subtype": depot.get("archetype", ""),
            "name": f"{depot.get('archetype', 'depot')} at {station_id}",
            "line": _line_from_station_id(station_id),
            "parent_asset": station_asset_by_source.get(station_id, project_asset_id),
            "station": station_id,
            "km_start": "",
            "km_end": "",
            "location": f"{station_id}; {depot.get('fleet_stalls', '')} stalls",
            "criticality": "service",
        })

    for idx, depot in enumerate(depots, start=1):
        station_id = str(depot.get("station", ""))
        assets.append({
            "asset_id": f"{prefix}-PLANT-{idx:03d}",
            "source_id": f"plant-{station_id}",
            "asset_type": "depots-production",
            "subtype": "tooling-fixtures",
            "name": f"production/depot tooling at {station_id}",
            "line": _line_from_station_id(station_id),
            "parent_asset": station_asset_by_source.get(station_id, project_asset_id),
            "station": station_id,
            "km_start": "",
            "km_end": "",
            "location": station_id,
            "criticality": "production",
        })

    for site in sites:
        station_id = str(site.get("station", ""))
        assets.append({
            "asset_id": next_id("EN"),
            "source_id": f"energy-{station_id}",
            "asset_type": "energy",
            "subtype": "pv-bess-charger",
            "name": f"energy site at {station_id}",
            "line": _line_from_station_id(station_id),
            "parent_asset": station_asset_by_source.get(station_id, project_asset_id),
            "station": station_id,
            "km_start": "",
            "km_end": "",
            "location": (
                f"{float(site.get('pv_nameplate_kw', 0.0)):,.0f} kW PV; "
                f"{float(site.get('storage_capacity_kwh', 0.0)):,.0f} kWh storage"
            ),
            "criticality": "energy",
        })

    for junction in junctions:
        group = junction.get("group_id", len(assets))
        assets.append({
            "asset_id": next_id("STR"),
            "source_id": f"junction-{group}",
            "asset_type": "structure",
            "subtype": "elevated-interchange",
            "name": f"elevated interchange group {group}",
            "line": junction.get("elevated_line", ""),
            "parent_asset": project_asset_id,
            "station": "",
            "km_start": "",
            "km_end": "",
            "location": _lat_lon(junction),
            "criticality": "safety",
        })

    for station in stations:
        station_id = str(station.get("id", ""))
        assets.append({
            "asset_id": next_id("SIG"),
            "source_id": f"systems-{station_id}",
            "asset_type": "signalling-comms",
            "subtype": "station-node",
            "name": f"station systems node {station_id}",
            "line": station.get("line", ""),
            "parent_asset": station_asset_by_source.get(station_id, project_asset_id),
            "station": station_id,
            "km_start": _km(station.get("s_m")),
            "km_end": _km(station.get("s_m")),
            "location": _lat_lon(station),
            "criticality": "safety",
        })

    maintenance_tasks = _expand_maintenance_tasks(
        assets=assets,
        intervals=list(maint_template.get("maintenance_interval", [])),
        city_slug=slug,
    )
    qa_actions = _expand_qa_actions(
        assets=assets,
        gates=list(qa_template.get("construction_qa_gate", [])),
        city_slug=slug,
    )

    apps = _portal_apps(design_path, scenario_path)
    meta = {
        "city_slug": slug,
        "city_name": _title(slug),
        "country": city.get("country", ""),
        "population": city.get("population", ""),
        "source_design": _rel(design_path),
        "source_scenario": _rel(scenario_path),
        "opening_date_placeholder": "opening_date",
    }
    totals = {
        "assets": len(assets),
        "qa_gates": len(qa_template.get("construction_qa_gate", [])),
        "qa_actions": len(qa_actions),
        "maintenance_tasks": len(maintenance_tasks),
        "trainsets": sum(1 for a in assets if a["asset_type"] == "rolling-stock"),
        "stations": sum(1 for a in assets if a["asset_type"] == "station"),
        "track_sections": sum(1 for a in assets if a["asset_type"] == "track-section"),
        "switches": sum(1 for a in assets if a["asset_type"] == "switch"),
        "energy_sites": sum(1 for a in assets if a["asset_type"] == "energy"),
    }

    return {
        "meta": meta,
        "totals": totals,
        "applications": apps,
        "qa_gates": qa_template.get("construction_qa_gate", []),
        "maintenance_intervals": maint_template.get("maintenance_interval", []),
        "assets": assets,
        "maintenance_tasks": maintenance_tasks,
        "qa_actions": qa_actions,
        "policy": maint_template.get("policy", {}),
    }


def _expand_maintenance_tasks(
    *,
    assets: list[dict[str, Any]],
    intervals: list[dict[str, Any]],
    city_slug: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_type: dict[str, list[dict[str, Any]]] = {}
    for asset in assets:
        by_type.setdefault(str(asset["asset_type"]), []).append(asset)

    for interval in intervals:
        targets = _maintenance_targets(str(interval.get("id", "")))
        for target in targets:
            for asset in by_type.get(target, []):
                rows.append({
                    "task_uid": f"{city_slug}:{asset['asset_id']}:{interval.get('id')}",
                    "city": city_slug,
                    "asset_id": asset["asset_id"],
                    "asset_name": asset["name"],
                    "asset_type": asset["asset_type"],
                    "line": asset["line"],
                    "task_id": interval.get("id", ""),
                    "cadence": interval.get("cadence", ""),
                    "trigger": interval.get("trigger", ""),
                    "scope": interval.get("scope", ""),
                    "evidence_required": interval.get("evidence", ""),
                    "owner": interval.get("owner", ""),
                    "next_due_basis": _next_due_basis(str(interval.get("cadence", ""))),
                    "status": "scheduled",
                    "severity": _task_severity(str(interval.get("trigger", ""))),
                })
    return rows


def _expand_qa_actions(
    *,
    assets: list[dict[str, Any]],
    gates: list[dict[str, Any]],
    city_slug: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for gate in gates:
        for asset in assets:
            if not _qa_applies(gate, asset):
                continue
            rows.append({
                "qa_uid": f"{city_slug}:{asset['asset_id']}:{gate.get('id')}",
                "city": city_slug,
                "asset_id": asset["asset_id"],
                "asset_name": asset["name"],
                "asset_type": asset["asset_type"],
                "line": asset["line"],
                "gate_id": gate.get("id", ""),
                "domain": gate.get("domain", ""),
                "stage": gate.get("stage", ""),
                "hold_point": gate.get("hold_point", ""),
                "evidence_required": gate.get("evidence", ""),
                "release_authority": gate.get("release_authority", ""),
                "status": "planned",
            })
    return rows


def _maintenance_targets(task_id: str) -> list[str]:
    if task_id.startswith("rs-"):
        return ["rolling-stock"]
    if task_id.startswith("station-"):
        return ["station"]
    if task_id in {"track-weekly", "track-geometry"}:
        return ["track-section"]
    if task_id == "switch-monthly":
        return ["switch"]
    if task_id == "structures-annual":
        return ["structure"]
    if task_id.startswith("energy-"):
        return ["energy"]
    if task_id.startswith("systems-"):
        return ["signalling-comms"]
    if task_id == "depot-tooling":
        return ["depots-production"]
    return []


def _qa_applies(gate: dict[str, Any], asset: dict[str, Any]) -> bool:
    gate_id = str(gate.get("id", ""))
    asset_type = str(asset.get("asset_type", ""))
    if gate.get("domain") == "system":
        return asset_type == "system"
    if gate.get("domain") == "rolling-stock":
        return asset_type == "rolling-stock"
    if gate_id == "qa-20-survey-geotech":
        return asset_type in {"track-section", "station", "depot"}
    if gate_id == "qa-21-earthworks-drainage":
        return asset_type == "track-section"
    if gate_id == "qa-22-trackform-rail":
        return asset_type in {"track-section", "switch"}
    if gate_id == "qa-23-structures":
        return asset_type == "structure"
    if gate_id == "qa-24-stations-depots-plant":
        return asset_type in {"station", "depot", "depots-production"}
    if gate_id == "qa-25-power-energy":
        return asset_type == "energy"
    if gate_id == "qa-26-wayside-comms-safety":
        return asset_type in {"signalling-comms", "switch"}
    return False


def _portal_apps(design_path: Path, scenario_path: Path) -> list[dict[str, str]]:
    return [
        {
            "id": "occ",
            "name": "OCC Console",
            "category": "operator-gui",
            "status": "available",
            "summary": "Read-only operations-control console for dispatcher playback and action rehearsal.",
            "native_command": 'cargo run --release -p osr-occ-gui -- --operator "dispatcher-alpha"',
            "web_command": "cd crates/osr-occ-gui && trunk serve web/index.html --port 8081",
            "docs": "crates/osr-occ-gui/README.md",
        },
        {
            "id": "simulator",
            "name": "Simulation GUI",
            "category": "operator-gui",
            "status": "available",
            "summary": "Scenario playback and train/energy event timeline.",
            "native_command": f"cargo run --release -p osr-sim-gui -- --scenario {_rel(scenario_path)}",
            "web_command": "cd crates/osr-sim-gui && trunk serve web/index.html --port 8082",
            "docs": "crates/osr-sim-gui/README.md",
        },
        {
            "id": "cbm",
            "name": "CBM Backend",
            "category": "backend-library",
            "status": "library",
            "summary": "Depot-side condition-based maintenance analysis and work-order generation.",
            "native_command": "cargo test -p osr-cbm-backend",
            "web_command": "",
            "docs": "crates/osr-cbm-backend/Cargo.toml",
        },
        {
            "id": "afc",
            "name": "AFC Backoffice",
            "category": "backend-library",
            "status": "library",
            "summary": "Fare settlement, revenue reconciliation, and fraud detection library.",
            "native_command": "cargo test -p osr-afc-backoffice",
            "web_command": "",
            "docs": "crates/osr-afc-backoffice/Cargo.toml",
        },
        {
            "id": "historian",
            "name": "Historian",
            "category": "backend-library",
            "status": "library",
            "summary": "Time-series metric ring buffers and decimation for operations telemetry.",
            "native_command": "cargo test -p osr-historian",
            "web_command": "",
            "docs": "crates/osr-historian/Cargo.toml",
        },
        {
            "id": "qa-maintenance",
            "name": "QA + Maintenance Portal",
            "category": "embedded",
            "status": "active",
            "summary": "Asset register, construction QA gates, and maintenance schedule for the selected city.",
            "native_command": f"python3 scripts/generate-qa-maintenance-data.py --design {_rel(design_path)} --scenario {_rel(scenario_path)}",
            "web_command": "python3 scripts/ops-core-server.py --port 8008",
            "docs": "docs/operations-portal/README.md",
        },
    ]


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)


def _city_prefix(slug: str) -> str:
    letters = re.sub(r"[^a-zA-Z0-9]", "", slug).upper()
    return (letters[:3] or "OSR").ljust(3, "X")


def _line_code(line: str) -> str:
    match = re.search(r"(\d+)", line)
    if match:
        return f"L{int(match.group(1))}"
    return re.sub(r"[^A-Z0-9]", "", line.upper())[:4] or "LINE"


def _line_from_station_id(station_id: str) -> str:
    parts = station_id.split("-")
    if len(parts) >= 2 and parts[0] == "line":
        return "-".join(parts[:2])
    return ""


def _display_station(station: dict[str, Any]) -> str:
    return str(station.get("anchor_name") or station.get("name") or station.get("id"))


def _lat_lon(row: dict[str, Any]) -> str:
    lat = row.get("lat")
    lon = row.get("lon")
    if lat is None or lon is None:
        return ""
    return f"{float(lat):.6f}, {float(lon):.6f}"


def _location_from_bbox(bbox: dict[str, Any]) -> str:
    if not bbox:
        return ""
    return (
        f"{bbox.get('south', '')},{bbox.get('west', '')} to "
        f"{bbox.get('north', '')},{bbox.get('east', '')}"
    )


def _km(value: Any) -> str:
    if value in ("", None):
        return ""
    return f"{float(value) / 1000.0:.3f}"


def _title(slug: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[-_]+", slug) if part)


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _next_due_basis(cadence: str) -> str:
    c = cadence.lower()
    if "daily" in c:
        return "opening_date + 1 day"
    if "7 days" in c:
        return "opening_date + 7 days"
    if "30 days" in c:
        return "opening_date + 30 days"
    if "90 days" in c:
        return "opening_date + 90 days"
    if "12 months" in c:
        return "opening_date + 12 months"
    if "150,000 km" in c:
        return "asset_service_km >= 150,000 or wear limit"
    if "600,000 km" in c:
        return "asset_service_km >= 600,000"
    if "10 years" in c:
        return "opening_date + 10 years"
    if "30-180 days" in c:
        return "opening_date + 30-180 days by tool class"
    if "60-90 days" in c:
        return "opening_date + 60-90 days by geometry preset"
    return f"opening_date + {cadence}"


def _task_severity(trigger: str) -> str:
    if "condition" in trigger or "telemetry" in trigger:
        return "condition-sensitive"
    if "km" in trigger:
        return "usage-based"
    return "routine"


if __name__ == "__main__":
    raise SystemExit(main())
