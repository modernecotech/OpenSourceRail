#!/usr/bin/env python3
"""Generate asset-level operations data for the operations portal.

The input is a generated city `design.toml` plus its expanded
`scenario.toml`. The output is a deterministic JSON bundle and CSV tables
that spreadsheet users can open directly.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import re
import tempfile
import tomllib
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESIGN = REPO_ROOT / "designs/west-asia/Iraq/Samawah/design.toml"
DEFAULT_SCENARIO = REPO_ROOT / "designs/west-asia/Iraq/Samawah/samawah.toml"
DEFAULT_BOM_DIR = REPO_ROOT / "build/bom"
DEFAULT_OUT_DIR = REPO_ROOT / "build/generated-operations/samawah"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate asset-level operations portal data."
    )
    parser.add_argument("--design", type=Path, default=DEFAULT_DESIGN)
    parser.add_argument("--scenario", type=Path, default=DEFAULT_SCENARIO)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="output folder (default: build/generated-operations/samawah)",
    )
    args = parser.parse_args()

    design = _load_toml(args.design)
    scenario = _load_toml(args.scenario)
    qa_template = _load_toml(REPO_ROOT / "lib/templates/construction-qa.toml")
    maint_template = _load_toml(REPO_ROOT / "lib/templates/maintenance-schedule.toml")
    manufacturing_template = _load_toml(REPO_ROOT / "lib/templates/manufacturing-schedule.toml")
    bom_catalog = _load_bom_catalog(DEFAULT_BOM_DIR)

    bundle = build_bundle(
        design=design,
        scenario=scenario,
        qa_template=qa_template,
        maint_template=maint_template,
        manufacturing_template=manufacturing_template,
        bom_catalog=bom_catalog,
        design_path=args.design,
        scenario_path=args.scenario,
    )

    out_dir = args.out_dir or DEFAULT_OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = bundle["meta"]["city_slug"]
    json_path = out_dir / f"{slug}-operations.json.gz"
    manifest_path = out_dir / f"{slug}-operations-manifest.json"
    assets_path = out_dir / f"{slug}-assets.csv"
    manufacturing_path = out_dir / f"{slug}-manufacturing-schedule.csv"
    manufacturing_materials_path = out_dir / f"{slug}-manufacturing-materials.csv"
    manufacturing_verification_path = out_dir / f"{slug}-manufacturing-verification.csv"
    maintenance_path = out_dir / f"{slug}-maintenance-schedule.csv"
    qa_path = out_dir / f"{slug}-qa-register.csv"

    payload = (json.dumps(bundle, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile("wb", dir=out_dir, delete=False) as handle:
        temporary = Path(handle.name)
        with gzip.GzipFile(filename="", mode="wb", fileobj=handle, mtime=0) as compressed:
            compressed.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, json_path)
    compressed_bytes = json_path.read_bytes()
    manifest_path.write_text(
        json.dumps(
            {
                "city": slug,
                "compression": "gzip",
                "content_type": "application/json",
                "file": json_path.name,
                "compressed_bytes": len(compressed_bytes),
                "compressed_sha256": hashlib.sha256(compressed_bytes).hexdigest(),
                "uncompressed_bytes": len(payload),
                "uncompressed_sha256": hashlib.sha256(payload).hexdigest(),
                "totals": bundle.get("totals", {}),
            },
            indent=2,
            sort_keys=True,
        ) + "\n"
    )
    _write_csv(assets_path, bundle["assets"])
    _write_csv(manufacturing_path, bundle["manufacturing_tasks"])
    _write_csv(manufacturing_materials_path, bundle["manufacturing_materials"])
    _write_csv(manufacturing_verification_path, bundle["manufacturing_verifications"])
    _write_csv(maintenance_path, bundle["maintenance_tasks"])
    _write_csv(qa_path, bundle["qa_actions"])

    print(f"wrote {json_path}")
    print(f"wrote {manifest_path}")
    print(f"wrote {assets_path}")
    print(f"wrote {manufacturing_path}")
    print(f"wrote {manufacturing_materials_path}")
    print(f"wrote {manufacturing_verification_path}")
    print(f"wrote {maintenance_path}")
    print(f"wrote {qa_path}")
    return 0


def build_bundle(
    *,
    design: dict[str, Any],
    scenario: dict[str, Any],
    qa_template: dict[str, Any],
    maint_template: dict[str, Any],
    manufacturing_template: dict[str, Any],
    bom_catalog: dict[str, dict[str, dict[str, str]]],
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
            track_asset_id = f"{prefix}-TRK-{line_code}-{idx:03d}"
            assets.append({
                "asset_id": track_asset_id,
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
            mid_s = (a_s + b_s) / 2.0
            assets.append({
                "asset_id": f"{prefix}-WPT-{line_code}-{idx:03d}",
                "source_id": f"w-node-{a.get('id')}--{b.get('id')}",
                "asset_type": "waypoint",
                "subtype": "wayside-node",
                "name": f"{line} waypoint {idx:03d}",
                "line": line,
                "parent_asset": track_asset_id,
                "station": f"{a.get('id')} to {b.get('id')}",
                "km_start": _km(mid_s),
                "km_end": _km(mid_s),
                "location": f"{_display_station(a)} to {_display_station(b)} midpoint W-Node",
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
    manufacturing_tasks = _expand_manufacturing_tasks(
        assets=assets,
        packages=list(manufacturing_template.get("manufacturing_package", [])),
        city_slug=slug,
    )
    _resolve_manufacturing_predecessors(manufacturing_tasks, assets)
    manufacturing_materials = _expand_manufacturing_materials(
        manufacturing_tasks=manufacturing_tasks,
        bom_catalog=bom_catalog,
    )
    manufacturing_verifications = _expand_manufacturing_verifications(
        manufacturing_tasks=manufacturing_tasks,
        qa_actions=qa_actions,
    )
    _apply_manufacturing_control_summaries(
        manufacturing_tasks=manufacturing_tasks,
        manufacturing_materials=manufacturing_materials,
        manufacturing_verifications=manufacturing_verifications,
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
        "manufacturing_packages": len(manufacturing_template.get("manufacturing_package", [])),
        "manufacturing_tasks": len(manufacturing_tasks),
        "manufacturing_materials": len(manufacturing_materials),
        "manufacturing_verifications": len(manufacturing_verifications),
        "maintenance_tasks": len(maintenance_tasks),
        "trainsets": sum(1 for a in assets if a["asset_type"] == "rolling-stock"),
        "stations": sum(1 for a in assets if a["asset_type"] == "station"),
        "track_sections": sum(1 for a in assets if a["asset_type"] == "track-section"),
        "waypoints": sum(1 for a in assets if a["asset_type"] == "waypoint"),
        "switches": sum(1 for a in assets if a["asset_type"] == "switch"),
        "energy_sites": sum(1 for a in assets if a["asset_type"] == "energy"),
    }

    return {
        "meta": meta,
        "totals": totals,
        "applications": apps,
        "qa_gates": qa_template.get("construction_qa_gate", []),
        "maintenance_intervals": maint_template.get("maintenance_interval", []),
        "manufacturing_packages": manufacturing_template.get("manufacturing_package", []),
        "assets": assets,
        "manufacturing_tasks": manufacturing_tasks,
        "manufacturing_materials": manufacturing_materials,
        "manufacturing_verifications": manufacturing_verifications,
        "maintenance_tasks": maintenance_tasks,
        "qa_actions": qa_actions,
        "policy": {
            "maintenance": maint_template.get("policy", {}),
            "manufacturing": manufacturing_template.get("policy", {}),
        },
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


def _expand_manufacturing_tasks(
    *,
    assets: list[dict[str, Any]],
    packages: list[dict[str, Any]],
    city_slug: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    indexed_assets = sorted(assets, key=lambda a: (str(a.get("asset_type", "")), str(a.get("asset_id", ""))))
    sequence_by_type: dict[str, int] = {}
    order_by_asset: dict[str, int] = {}
    for asset in indexed_assets:
        asset_type = str(asset.get("asset_type", ""))
        sequence_by_type[asset_type] = sequence_by_type.get(asset_type, 0) + 1
        order_by_asset[str(asset.get("asset_id", ""))] = sequence_by_type[asset_type]

    for package in packages:
        target_types = {str(t) for t in package.get("asset_types", [])}
        sequence = int(package.get("sequence", 0) or 0)
        duration_days = int(package.get("duration_days", 1) or 1)
        for asset in indexed_assets:
            asset_type = str(asset.get("asset_type", ""))
            if asset_type not in target_types:
                continue
            asset_order = order_by_asset.get(str(asset.get("asset_id", "")), 1)
            start_day = _manufacturing_start_day(asset_type, sequence, asset_order)
            finish_day = start_day + max(duration_days, 1) - 1
            rows.append({
                "manufacturing_uid": f"{city_slug}:{asset['asset_id']}:{package.get('id')}",
                "city": city_slug,
                "asset_id": asset["asset_id"],
                "asset_name": asset["name"],
                "asset_type": asset["asset_type"],
                "line": asset["line"],
                "package_id": package.get("id", ""),
                "phase": package.get("phase", ""),
                "sequence": sequence,
                "work_center": package.get("work_center", ""),
                "duration_days": duration_days,
                "planned_start_day": start_day,
                "planned_finish_day": finish_day,
                "planned_start_basis": f"project_day_{start_day}",
                "planned_finish_basis": f"project_day_{finish_day}",
                "predecessors": package.get("predecessors", ""),
                "predecessor_uids": "",
                "external_predecessors": "",
                "work_order_title": package.get("work_order_title", ""),
                "work_order_detail": package.get("work_order_detail", ""),
                "staff_roles": "; ".join(str(role) for role in package.get("staff_roles", [])),
                "staff_tasks": package.get("staff_tasks", ""),
                "materials_or_inputs": package.get("materials_or_inputs", ""),
                "bom_refs": "; ".join(str(ref) for ref in package.get("bom_refs", [])),
                "material_count": 0,
                "material_status": "not generated",
                "deliverables": package.get("deliverables", ""),
                "evidence_required": package.get("evidence_required", ""),
                "release_authority": package.get("release_authority", ""),
                "qa_gate_hint": package.get("qa_gate_hint", ""),
                "qa_uid": "",
                "verification_uid": "",
                "verification_status": "not generated",
                "blocks_successors": "yes",
                "status": "planned",
                "priority": package.get("priority", "routine"),
            })
    return sorted(rows, key=lambda row: (
        int(row["planned_start_day"]),
        str(row["asset_type"]),
        str(row["asset_id"]),
        int(row["sequence"]),
    ))


def _resolve_manufacturing_predecessors(
    manufacturing_tasks: list[dict[str, Any]],
    assets: list[dict[str, Any]],
) -> None:
    asset_by_id = {str(asset["asset_id"]): asset for asset in assets}
    tasks_by_asset_package = {
        (str(task["asset_id"]), str(task["package_id"])): str(task["manufacturing_uid"])
        for task in manufacturing_tasks
    }
    system_by_package = {
        str(task["package_id"]): str(task["manufacturing_uid"])
        for task in manufacturing_tasks
        if task.get("asset_type") == "system"
    }
    track_assets = [asset for asset in assets if asset.get("asset_type") == "track-section"]

    for task in manufacturing_tasks:
        resolved: list[str] = []
        external: list[str] = []
        asset = asset_by_id.get(str(task["asset_id"]), {})
        for predecessor in _split_refs(str(task.get("predecessors", ""))):
            uid = _resolve_manufacturing_predecessor(
                predecessor=predecessor,
                task=task,
                asset=asset,
                tasks_by_asset_package=tasks_by_asset_package,
                system_by_package=system_by_package,
                track_assets=track_assets,
            )
            if uid:
                resolved.append(uid)
            else:
                external.append(predecessor)
        task["predecessor_uids"] = "; ".join(resolved)
        task["external_predecessors"] = "; ".join(external)


def _resolve_manufacturing_predecessor(
    *,
    predecessor: str,
    task: dict[str, Any],
    asset: dict[str, Any],
    tasks_by_asset_package: dict[tuple[str, str], str],
    system_by_package: dict[str, str],
    track_assets: list[dict[str, Any]],
) -> str:
    asset_id = str(task["asset_id"])
    same_asset = tasks_by_asset_package.get((asset_id, predecessor))
    if same_asset:
        return same_asset
    if predecessor in system_by_package:
        return system_by_package[predecessor]
    parent_asset_id = str(asset.get("parent_asset", ""))
    parent = tasks_by_asset_package.get((parent_asset_id, predecessor))
    if parent:
        return parent
    if predecessor.startswith("trk-"):
        track_asset = _nearest_track_asset(asset, track_assets)
        if track_asset:
            return tasks_by_asset_package.get((str(track_asset["asset_id"]), predecessor), "")
    return ""


def _nearest_track_asset(
    asset: dict[str, Any],
    track_assets: list[dict[str, Any]],
) -> dict[str, Any] | None:
    parent_asset = str(asset.get("parent_asset", ""))
    for track in track_assets:
        if str(track.get("asset_id")) == parent_asset:
            return track
    station = str(asset.get("station", ""))
    line = str(asset.get("line", ""))
    candidates = [
        track for track in track_assets
        if (not line or track.get("line") == line)
        and (not station or station in str(track.get("station", "")))
    ]
    if candidates:
        return sorted(candidates, key=lambda row: str(row.get("asset_id", "")))[0]
    line_candidates = [track for track in track_assets if not line or track.get("line") == line]
    return sorted(line_candidates, key=lambda row: str(row.get("asset_id", "")))[0] if line_candidates else None


def _expand_manufacturing_materials(
    *,
    manufacturing_tasks: list[dict[str, Any]],
    bom_catalog: dict[str, dict[str, dict[str, str]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task in manufacturing_tasks:
        for position, ref in enumerate(_split_refs(str(task.get("bom_refs", ""))), start=1):
            source, key = _split_bom_ref(ref)
            bom_row = bom_catalog.get(source, {}).get(key, {})
            material = _material_from_bom_ref(
                task=task,
                source=source,
                key=key,
                bom_row=bom_row,
                position=position,
            )
            rows.append(material)
    return rows


def _material_from_bom_ref(
    *,
    task: dict[str, Any],
    source: str,
    key: str,
    bom_row: dict[str, str],
    position: int,
) -> dict[str, Any]:
    if source == "rolling_stock_bom" and bom_row:
        description = bom_row.get("description", key)
        quantity = bom_row.get("quantity", "")
        make_buy_source = bom_row.get("source", "")
        base_usd = bom_row.get("base_usd", "")
        cost_basis = bom_row.get("cost_basis", "")
        evidence = "supplier certificate, serial/lot traceability, receiving inspection"
    elif source == "rolling_stock_cots_fitout" and bom_row:
        description = bom_row.get("name", key)
        quantity = bom_row.get("qty_per_consist", "")
        make_buy_source = "COTS"
        base_usd = bom_row.get("consist_cost_base_usd", "")
        cost_basis = bom_row.get("cost_basis", "")
        evidence = "supplier datasheet, fit check, fire/safety evidence where applicable"
    else:
        description = key.replace("-", " ")
        quantity = "per asset package"
        make_buy_source = "PROJECT_KIT"
        base_usd = ""
        cost_basis = "Controlled project-kit placeholder; replace with detailed BOM row when available."
        evidence = "kit issue note, receiving inspection, lot/serial traceability where applicable"

    material_uid = f"{task['manufacturing_uid']}:MAT-{position:03d}"
    return {
        "material_uid": material_uid,
        "manufacturing_uid": task["manufacturing_uid"],
        "city": task["city"],
        "asset_id": task["asset_id"],
        "asset_name": task["asset_name"],
        "asset_type": task["asset_type"],
        "package_id": task["package_id"],
        "phase": task["phase"],
        "bom_source": source,
        "bom_ref": key,
        "description": description,
        "quantity_basis": quantity,
        "make_buy_source": make_buy_source,
        "base_usd": base_usd,
        "cost_basis": cost_basis,
        "traceability_required": "yes",
        "evidence_required": evidence,
        "material_status": "required",
    }


def _expand_manufacturing_verifications(
    *,
    manufacturing_tasks: list[dict[str, Any]],
    qa_actions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    qa_by_asset_gate = {
        (str(row["asset_id"]), str(row["gate_id"])): row
        for row in qa_actions
    }
    rows: list[dict[str, Any]] = []
    for task in manufacturing_tasks:
        gate_id = str(task.get("qa_gate_hint", ""))
        qa = qa_by_asset_gate.get((str(task["asset_id"]), gate_id), {})
        verification_uid = f"{task['manufacturing_uid']}:VERIFY"
        rows.append({
            "verification_uid": verification_uid,
            "manufacturing_uid": task["manufacturing_uid"],
            "qa_uid": qa.get("qa_uid", ""),
            "city": task["city"],
            "asset_id": task["asset_id"],
            "asset_name": task["asset_name"],
            "asset_type": task["asset_type"],
            "package_id": task["package_id"],
            "phase": task["phase"],
            "qa_gate_id": gate_id,
            "qa_stage": qa.get("stage", task.get("phase", "")),
            "hold_point": qa.get("hold_point", task.get("work_order_title", "")),
            "evidence_required": qa.get("evidence_required", task.get("evidence_required", "")),
            "release_authority": qa.get("release_authority", task.get("release_authority", "")),
            "required_result": "pass",
            "blocks_successors": "yes",
            "verification_source": "qa_action" if qa else "template",
            "status": "required",
        })
    return rows


def _apply_manufacturing_control_summaries(
    *,
    manufacturing_tasks: list[dict[str, Any]],
    manufacturing_materials: list[dict[str, Any]],
    manufacturing_verifications: list[dict[str, Any]],
) -> None:
    material_counts: dict[str, int] = {}
    for row in manufacturing_materials:
        uid = str(row["manufacturing_uid"])
        material_counts[uid] = material_counts.get(uid, 0) + 1
    verifications = {
        str(row["manufacturing_uid"]): row
        for row in manufacturing_verifications
    }
    for task in manufacturing_tasks:
        uid = str(task["manufacturing_uid"])
        verification = verifications.get(uid, {})
        material_count = material_counts.get(uid, 0)
        task["material_count"] = material_count
        task["material_status"] = "required" if material_count else "missing"
        task["qa_uid"] = verification.get("qa_uid", "")
        task["verification_uid"] = verification.get("verification_uid", "")
        task["verification_status"] = verification.get("status", "missing")
        task["qa_hold_point"] = verification.get("hold_point", "")


def _manufacturing_start_day(asset_type: str, sequence: int, asset_order: int) -> int:
    base_by_type = {
        "system": 0,
        "depots-production": 8,
        "depot": 12,
        "energy": 28,
        "station": 36,
        "track-section": 42,
        "switch": 52,
        "waypoint": 62,
        "signalling-comms": 66,
        "rolling-stock": 72,
        "structure": 44,
    }
    spacing_by_type = {
        "system": 0,
        "depots-production": 4,
        "depot": 5,
        "energy": 4,
        "station": 4,
        "track-section": 3,
        "switch": 2,
        "waypoint": 2,
        "signalling-comms": 2,
        "rolling-stock": 4,
        "structure": 6,
    }
    sequence_offset = max(sequence // 10, 0) * 5
    return (
        base_by_type.get(asset_type, 40)
        + (max(asset_order, 1) - 1) * spacing_by_type.get(asset_type, 3)
        + sequence_offset
    )


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
        return ["signalling-comms", "waypoint"]
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
        return asset_type in {"energy", "depot"}
    if gate_id == "qa-26-wayside-comms-safety":
        return asset_type in {"signalling-comms", "switch", "waypoint"}
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
            "name": "Ops Core Portal",
            "category": "embedded",
            "status": "active",
            "summary": "Asset register, manufacturing schedule, construction QA gates, maintenance schedule, work orders, evidence, defects, and audit.",
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
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _load_bom_catalog(path: Path) -> dict[str, dict[str, dict[str, str]]]:
    return {
        "rolling_stock_bom": _load_csv_index(path / "rolling_stock_bom.csv", "line_id"),
        "rolling_stock_cots_fitout": _load_csv_index(
            path / "rolling_stock_cots_fitout_bom.csv",
            "category",
        ),
    }


def _load_csv_index(path: Path, key: str) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as f:
        return {
            str(row.get(key, "")): row
            for row in csv.DictReader(f)
            if row.get(key)
        }


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


def _split_refs(value: str) -> list[str]:
    return [
        item.strip()
        for item in re.split(r"[;,]", value)
        if item.strip()
    ]


def _split_bom_ref(ref: str) -> tuple[str, str]:
    if ":" not in ref:
        return "project_kit", ref
    parts = ref.split(":")
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], ":".join(parts[1:])


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
