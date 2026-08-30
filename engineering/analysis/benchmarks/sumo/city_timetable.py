#!/usr/bin/env python3
"""Generate and optionally run a SUMO screening timetable for one OSR city."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
ROLLING_STOCK = REPO_ROOT / "lib/templates/rolling-stock.toml"
sys.path.insert(0, str(REPO_ROOT))

from engineering.analysis.city_geometry import (  # noqa: E402
    corridor_path,
    line_geometry,
    load_line_coordinates,
    point_at,
    station_offset_m,
    substring,
)


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        handle.write(value)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def portable_output_text(value: str, output: Path) -> str:
    """Remove the generator workstation path from retained SUMO evidence."""
    prefix = str(output.resolve()) + os.sep
    return value.replace(prefix, "")


def xml_text(root: ET.Element) -> str:
    ET.indent(root)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-") or "unnamed"


def sumo_command(
    node_file: Path,
    edge_file: Path,
    net_file: Path,
    route_file: Path,
    tripinfo_file: Path,
    end_time_s: int,
    version_file: Path,
) -> list[str]:
    script = """
set -eu
netconvert --node-files "$1" --edge-files "$2" --output-file "$3" --no-turnarounds true
sumo --net-file "$3" --route-files "$4" --tripinfo-output "$5" --end "$6" --no-step-log true --duration-log.statistics true
sumo --version | head -n 1 > "$7"
""".strip()
    return [
        "flatpak",
        "run",
        "--command=sh",
        "org.eclipse.sumo",
        "-c",
        script,
        "osr-sumo",
        str(node_file),
        str(edge_file),
        str(net_file),
        str(route_file),
        str(tripinfo_file),
        str(end_time_s),
        str(version_file),
    ]


def generate_city(
    design_path: Path,
    output: Path,
    *,
    selected_lines: set[str] | None = None,
    generate_only: bool = False,
    services_per_direction: int = 2,
    headway_s: int = 600,
    opposing_offset_s: int = 300,
    dwell_s: int = 60,
) -> dict[str, object]:
    design_path = design_path.resolve()
    output = output.resolve()
    design = tomllib.loads(design_path.read_text(encoding="utf-8"))
    rolling_stock = tomllib.loads(ROLLING_STOCK.read_text(encoding="utf-8"))["profiles"]
    city = design.get("city", {})
    city_slug = str(city.get("slug", "")).strip()
    if not city_slug:
        raise RuntimeError(f"{design_path}: missing city.slug")
    geometry_path = corridor_path(design_path, city_slug)
    corridor_lines = load_line_coordinates(geometry_path)

    declared_lines = list(design.get("lines", []))
    if selected_lines is not None:
        missing_names = sorted(selected_lines - {str(line.get("name")) for line in declared_lines})
        if missing_names:
            raise RuntimeError(f"{city_slug}: unknown line selection: {', '.join(missing_names)}")
        declared_lines = [line for line in declared_lines if line.get("name") in selected_lines]
    if not declared_lines:
        raise RuntimeError(f"{city_slug}: no lines selected")

    all_stations = list(design.get("stations", []))
    lon0 = sum(float(station["lon"]) for station in all_stations) / len(all_stations)
    lat0 = sum(float(station["lat"]) for station in all_stations) / len(all_stations)
    nodes = ET.Element("nodes")
    edges = ET.Element("edges")
    routes = ET.Element("routes")
    line_reports: list[dict[str, object]] = []
    input_issues: list[dict[str, object]] = []
    expected_service_ids: set[str] = set()
    service_line_by_id: dict[str, str] = {}
    maximum_departure = 0
    maximum_route_allowance = 0.0

    for line_index, line in enumerate(declared_lines):
        line_name = str(line["name"])
        line_key = safe_id(line_name)
        stations = sorted(
            (station for station in all_stations if station.get("line") == line_name),
            key=lambda station: float(station.get("s_m", 0.0)),
        )
        if len(stations) < 2:
            raise RuntimeError(f"{city_slug}/{line_name}: fewer than two stations")

        chainages = [float(station["s_m"]) for station in stations]
        for station_index, (before, after) in enumerate(zip(chainages, chainages[1:])):
            if after <= before:
                raise RuntimeError(
                    f"{city_slug}/{line_name}: non-increasing chainage at station index {station_index + 1}"
                )
        declared_length = float(line["length_m"])
        is_ring = str(line.get("shape", "radial")) == "ring"
        rolling_stock_id = str(line.get("rolling_stock", ""))
        profile = rolling_stock.get(rolling_stock_id)
        if profile is None:
            raise RuntimeError(f"{city_slug}/{line_name}: unknown rolling-stock profile {rolling_stock_id!r}")
        train_length = float(profile["length_m"])
        maximum_speed = float(profile["max_speed_mps"])
        start_gap = round(chainages[0], 3)
        # A ring has one physical station at chainage zero and a final track
        # segment returning to that same node. It must not duplicate the
        # station record at declared_length merely to satisfy a linear-line
        # endpoint check.
        end_gap = 0.0 if is_ring else round(declared_length - chainages[-1], 3)
        if not is_ring and abs(start_gap) > 1.0:
            input_issues.append(
                {"code": "line-start-station-gap", "line": line_name, "gap_m": start_gap}
            )
        if abs(end_gap) > 1.0:
            input_issues.append(
                {"code": "line-end-station-gap", "line": line_name, "gap_m": end_gap}
            )

        coordinates = corridor_lines.get(line_name)
        if not coordinates:
            raise RuntimeError(f"{city_slug}/{line_name}: no LineString in {geometry_path.name}")
        geometry = line_geometry(coordinates, stations, declared_length, lon0, lat0)
        geometry_points = geometry["points"]
        geometry_factor = float(geometry["geometry_per_chainage"])
        station_points = [point_at(geometry_points, chainage * geometry_factor) for chainage in chainages]
        station_offsets = [
            station_offset_m(station, point, lon0, lat0)
            for station, point in zip(stations, station_points)
        ]
        prefix = f"l{line_index:02d}_{line_key}"
        for station_index, station in enumerate(stations):
            node_type = "rail_signal" if 0 < station_index < len(stations) - 1 else "priority"
            x, y = station_points[station_index]
            ET.SubElement(
                nodes,
                "node",
                id=f"{prefix}_n{station_index:03d}",
                x=f"{x:.3f}",
                y=f"{y:.3f}",
                type=node_type,
            )

        forward_edges: list[str] = []
        reverse_edges: list[str] = []
        segment_lengths: list[float] = []
        segment_count = len(stations) if is_ring else len(stations) - 1
        for segment_index in range(segment_count):
            next_station_index = (segment_index + 1) % len(stations)
            segment_end_chainage = (
                chainages[next_station_index]
                if next_station_index > 0
                else declared_length + chainages[0]
            )
            segment_length = segment_end_chainage - chainages[segment_index]
            if segment_length <= 60.0:
                raise RuntimeError(
                    f"{city_slug}/{line_name}: segment {segment_index} is only {segment_length:.3f} m"
                )
            segment_lengths.append(segment_length)
            forward = f"{prefix}_f{segment_index:03d}"
            reverse = f"{prefix}_r{segment_index:03d}"
            forward_edges.append(forward)
            reverse_edges.insert(0, reverse)
            shape_points = substring(
                geometry_points,
                chainages[segment_index] * geometry_factor,
                min(segment_end_chainage, declared_length) * geometry_factor,
            )
            forward_shape = " ".join(f"{x:.3f},{y:.3f}" for x, y in shape_points)
            reverse_shape = " ".join(f"{x:.3f},{y:.3f}" for x, y in reversed(shape_points))
            ET.SubElement(
                edges,
                "edge",
                id=forward,
                **{
                    "from": f"{prefix}_n{segment_index:03d}",
                    "to": f"{prefix}_n{next_station_index:03d}",
                },
                priority="1",
                numLanes="1",
                speed=f"{maximum_speed:.3f}",
                length=f"{segment_length:.3f}",
                shape=forward_shape,
                allow="rail",
            )
            ET.SubElement(
                edges,
                "edge",
                id=reverse,
                **{
                    "from": f"{prefix}_n{next_station_index:03d}",
                    "to": f"{prefix}_n{segment_index:03d}",
                },
                priority="1",
                numLanes="1",
                speed=f"{maximum_speed:.3f}",
                length=f"{segment_length:.3f}",
                shape=reverse_shape,
                allow="rail",
            )

        platform_lengths = [float(station.get("platform_length_m", 0.0)) for station in stations]
        if not platform_lengths or min(platform_lengths) < train_length:
            raise RuntimeError(
                f"{city_slug}/{line_name}: a platform does not fit the canonical "
                f"{rolling_stock_id} consist length of {train_length:.3f} m"
            )
        vehicle_type = f"{prefix}_vehicle"
        outbound_route = f"{prefix}_outbound"
        inbound_route = f"{prefix}_inbound"
        ET.SubElement(
            routes,
            "vType",
            id=vehicle_type,
            vClass="rail",
            length=f"{train_length:.3f}",
            maxSpeed=f"{maximum_speed:.3f}",
            accel="0.8",
            decel="1.1",
        )
        ET.SubElement(routes, "route", id=outbound_route, edges=" ".join(forward_edges))
        ET.SubElement(routes, "route", id=inbound_route, edges=" ".join(reverse_edges))

        for service_index in range(services_per_direction):
            departures = (
                ("outbound", outbound_route, service_index * headway_s),
                ("inbound", inbound_route, service_index * headway_s + opposing_offset_s),
            )
            for direction, route_id, departure in departures:
                service_id = f"{prefix}_{direction}_{service_index:03d}"
                expected_service_ids.add(service_id)
                service_line_by_id[service_id] = line_name
                maximum_departure = max(maximum_departure, departure)
                vehicle = ET.SubElement(
                    routes,
                    "vehicle",
                    id=service_id,
                    type=vehicle_type,
                    route=route_id,
                    line=f"{city_slug}:{line_name}",
                    depart=str(departure),
                    departSpeed="0",
                )
                if direction == "outbound":
                    ordered_segments = list(zip(forward_edges, segment_lengths))
                else:
                    ordered_segments = list(zip(reverse_edges, reversed(segment_lengths)))
                for edge_id, segment_length in ordered_segments[:-1]:
                    ET.SubElement(
                        vehicle,
                        "stop",
                        lane=f"{edge_id}_0",
                        endPos=f"{segment_length - 5.0:.3f}",
                        duration=str(dwell_s),
                    )

        modeled_length = (
            round(declared_length, 3)
            if is_ring
            else round(chainages[-1] - chainages[0], 3)
        )
        allowance = modeled_length / 5.0 + len(stations) * dwell_s * 2 + 600.0
        maximum_route_allowance = max(maximum_route_allowance, allowance)
        line_reports.append(
            {
                "declared_length_m": declared_length,
                "end_station_gap_m": end_gap,
                "corridor_geometry_length_m": round(float(geometry["geometry_length_m"]), 3),
                "corridor_geometry_to_declared_ratio": round(geometry_factor, 6),
                "line": line_name,
                "maximum_station_corridor_offset_m": round(max(station_offsets), 3),
                "modeled_length_m": modeled_length,
                "maximum_speed_mps": maximum_speed,
                "rolling_stock": rolling_stock_id,
                "scheduled_services": services_per_direction * 2,
                "start_station_gap_m": start_gap,
                "station_count": len(stations),
                "station_ids": [station["id"] for station in stations],
                "train_length_m": train_length,
            }
        )

    output.mkdir(parents=True, exist_ok=True)
    node_file = output / "city.nod.xml"
    edge_file = output / "city.edg.xml"
    net_file = output / "city.net.xml"
    route_file = output / "city.rou.xml"
    tripinfo_file = output / "tripinfo.xml"
    version_file = output / "sumo-version.txt"
    atomic_text(node_file, xml_text(nodes))
    atomic_text(edge_file, xml_text(edges))
    atomic_text(route_file, xml_text(routes))

    report: dict[str, object] = {
        "analysis_family": "OSR-AN-OPS-SUMO-CITY",
        "analysis_id": f"OSR-AN-OPS-SUMO-CITY:{city_slug}",
        "city": city_slug,
        "country": city.get("country"),
        "design_input": str(design_path.relative_to(REPO_ROOT)),
        "design_sha256": hashlib.sha256(design_path.read_bytes()).hexdigest(),
        "corridor_input": str(geometry_path.relative_to(REPO_ROOT)),
        "corridor_sha256": hashlib.sha256(geometry_path.read_bytes()).hexdigest(),
        "geometry_mode": "canonical-corridor",
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "local_coordinate_origin": {"latitude": lat0, "longitude": lon0},
        "input_issues": input_issues,
        "input_quality_passed": not input_issues,
        "line_count": len(line_reports),
        "lines": line_reports,
        "scheduled_services": len(expected_service_ids),
        "station_count": sum(int(line["station_count"]) for line in line_reports),
        "rolling_stock_input": str(ROLLING_STOCK.relative_to(REPO_ROOT)),
        "rolling_stock_sha256": hashlib.sha256(ROLLING_STOCK.read_bytes()).hexdigest(),
        "tool": {"name": "SUMO", "version_output": None},
    }

    if generate_only:
        report.update({"arrived_services": None, "passed": None, "simulation_status": "generated-not-run"})
    else:
        end_time_s = int(maximum_departure + maximum_route_allowance)
        completed = subprocess.run(
            sumo_command(node_file, edge_file, net_file, route_file, tripinfo_file, end_time_s, version_file),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        atomic_text(output / "sumo.log", portable_output_text(completed.stdout, output))
        if completed.returncode:
            raise RuntimeError(f"SUMO failed for {city_slug}; see {output / 'sumo.log'}")
        trips = ET.parse(tripinfo_file).getroot().findall("tripinfo")
        arrived_ids = {trip.attrib["id"] for trip in trips}
        durations_by_line: dict[str, list[float]] = {str(line["line"]): [] for line in line_reports}
        for trip in trips:
            line_name = service_line_by_id.get(trip.attrib["id"], "")
            if line_name in durations_by_line:
                durations_by_line[line_name].append(float(trip.attrib["duration"]))
        for line_report in line_reports:
            durations = durations_by_line[str(line_report["line"])]
            line_report["arrived_services"] = len(durations)
            line_report["mean_trip_duration_s"] = sum(durations) / len(durations) if durations else None
        simulation_passed = arrived_ids == expected_service_ids
        report.update(
            {
                "arrived_services": len(arrived_ids),
                "missing_service_ids": sorted(expected_service_ids - arrived_ids),
                "passed": simulation_passed and not input_issues,
                "simulation_passed": simulation_passed,
                "simulation_status": "completed",
            }
        )
        report["tool"] = {
            "name": "SUMO",
            "version_output": version_file.read_text(encoding="utf-8").strip(),
        }
        for retained_xml in (net_file, tripinfo_file):
            atomic_text(
                retained_xml,
                portable_output_text(retained_xml.read_text(encoding="utf-8"), output),
            )

    atomic_text(output / "summary.json", json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main(default_design: Path | None = None, default_lines: set[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, default=default_design)
    parser.add_argument("--line", action="append", dest="lines")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--generate-only", action="store_true")
    parser.add_argument("--allow-input-gaps", action="store_true")
    parser.add_argument("--services-per-direction", type=int, default=2)
    args = parser.parse_args()
    if args.design is None:
        parser.error("--design is required")
    design_path = args.design.resolve()
    metadata = tomllib.loads(design_path.read_text(encoding="utf-8"))
    slug = str(metadata.get("city", {}).get("slug", "unknown"))
    output = args.output_dir or design_path.parent / "engineering/sumo"
    selected = set(args.lines) if args.lines else default_lines
    report = generate_city(
        design_path,
        output,
        selected_lines=selected,
        generate_only=args.generate_only,
        services_per_direction=args.services_per_direction,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["simulation_status"] == "generated-not-run":
        return 0 if report["input_quality_passed"] or args.allow_input_gaps else 1
    return 0 if report["passed"] or (report.get("simulation_passed") and args.allow_input_gaps) else 1


if __name__ == "__main__":
    raise SystemExit(main())
