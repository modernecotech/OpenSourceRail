#!/usr/bin/env python3
"""Validate that every close ring/radial approach has a real interchange."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TRANSFER_ENVELOPE_M = 600.0
TERMINUS_EXTENSION_ENVELOPE_M = 1200.0
BACKTRACK_EXCURSION_M = 750.0


def distance_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    lon1, lat1 = a
    lon2, lat2 = b
    radians = math.pi / 180.0
    x = (lon2 - lon1) * radians * math.cos((lat1 + lat2) * radians / 2)
    y = (lat2 - lat1) * radians
    return 6_371_000.0 * math.hypot(x, y)


def _xy_m(
    point: tuple[float, float],
    *,
    origin_lon: float,
    origin_lat: float,
) -> tuple[float, float]:
    lon, lat = point
    radians = math.pi / 180.0
    x = (lon - origin_lon) * radians * math.cos(origin_lat * radians) * 6_371_000.0
    y = (lat - origin_lat) * radians * 6_371_000.0
    return x, y


def backtracking_finding(name: str, coords: list) -> dict | None:
    """Return a finding if a radial corridor materially doubles back.

    Small arterial wiggles are allowed. The check trips when the route falls
    more than 750 m behind its furthest progress along its start/end axis.
    This catches a real hairpin without adding unrelated street-grid wiggles.
    """
    if len(coords) < 3:
        return None
    origin_lon = float(coords[0][0])
    origin_lat = float(coords[0][1])
    points = [
        _xy_m((float(lon), float(lat)), origin_lon=origin_lon, origin_lat=origin_lat)
        for lon, lat in coords
    ]
    sx, sy = points[0]
    ex, ey = points[-1]
    dx = ex - sx
    dy = ey - sy
    length = math.hypot(dx, dy)
    if length < 2_000.0:
        return None
    ux = dx / length
    uy = dy / length
    projections = [(x - sx) * ux + (y - sy) * uy for x, y in points]
    furthest_progress = projections[0]
    maximum_excursion = 0.0
    for projection in projections[1:]:
        furthest_progress = max(furthest_progress, projection)
        maximum_excursion = max(maximum_excursion, furthest_progress - projection)
    if maximum_excursion < BACKTRACK_EXCURSION_M:
        return None
    return {
        "code": "radial-corridor-turns-back-on-itself",
        "radial": name,
        "severity": "fail",
        "maximum_reverse_excursion_m": round(maximum_excursion, 1),
    }


def validate(path: Path) -> dict:
    design = tomllib.loads(path.read_text(encoding="utf-8"))
    slug = str(design["city"]["slug"])
    corridor_path = path.parent / f"{slug}.corridor.geojson"
    geometries = json.loads(corridor_path.read_text(encoding="utf-8"))
    coords = {
        str(feature["properties"]["name"]): feature["geometry"]["coordinates"]
        for feature in geometries.get("features", [])
        if feature.get("properties", {}).get("kind") == "line"
    }
    shapes = {str(line["name"]): str(line.get("shape", "radial")) for line in design.get("lines", [])}
    stations: dict[str, list[dict]] = {}
    for station in design.get("stations", []):
        stations.setdefault(str(station["line"]), []).append(station)
    findings: list[dict] = []
    for radial in sorted(name for name, shape in shapes.items() if shape != "ring"):
        radial_coords = coords.get(radial, [])
        if radial_coords:
            finding = backtracking_finding(radial, radial_coords)
            if finding is not None:
                findings.append(finding)
    for ring in sorted(name for name, shape in shapes.items() if shape == "ring"):
        ring_groups = {
            station.get("junction_group")
            for station in stations.get(ring, [])
            if station.get("junction_group") is not None
        }
        for radial in sorted(name for name, shape in shapes.items() if shape != "ring"):
            radial_groups = {
                station.get("junction_group")
                for station in stations.get(radial, [])
                if station.get("junction_group") is not None
            }
            radial_coords = coords.get(radial, [])
            ring_coords = coords.get(ring, [])
            if not radial_coords or not ring_coords:
                findings.append({"code": "missing-corridor-geometry", "radial": radial, "ring": ring, "severity": "fail"})
                continue
            radial_line = next(line for line in design.get("lines", []) if str(line["name"]) == radial)
            line_length_m = float(radial_line.get("length_m", 0.0))
            radial_stations = stations.get(radial, [])
            terminal_stations = {
                "start": next(
                    (station for station in radial_stations if abs(float(station.get("s_m", 0.0))) <= 1.0),
                    None,
                ),
                "end": next(
                    (
                        station
                        for station in radial_stations
                        if abs(float(station.get("s_m", 0.0)) - line_length_m) <= 1.0
                    ),
                    None,
                ),
            }
            endpoint_distances = {
                "start": min(distance_m(radial_coords[0], point) for point in ring_coords),
                "end": min(distance_m(radial_coords[-1], point) for point in ring_coords),
            }
            for endpoint_name, endpoint_distance in endpoint_distances.items():
                if endpoint_distance > TERMINUS_EXTENSION_ENVELOPE_M:
                    continue
                terminal = terminal_stations[endpoint_name]
                junction_group = terminal.get("junction_group") if terminal else None
                if terminal is None or junction_group not in ring_groups:
                    severity = (
                        "fail"
                        if endpoint_distance <= TRANSFER_ENVELOPE_M
                        else "review"
                    )
                    findings.append({
                        "code": (
                            "terminus-near-ring-without-interchange"
                            if severity == "fail"
                            else "terminus-extension-omitted-to-avoid-poor-alignment"
                        ),
                        "endpoint": endpoint_name,
                        "radial": radial,
                        "ring": ring,
                        "severity": severity,
                        "terminal_station_present": terminal is not None,
                        "terminus_distance_m": round(endpoint_distance, 1),
                    })
            connected = bool(ring_groups & radial_groups)
            if connected:
                continue
            geometry_distance = min(distance_m(a, b) for a in radial_coords for b in ring_coords)
            terminus_distance = min(endpoint_distances.values())
            if geometry_distance <= TRANSFER_ENVELOPE_M:
                findings.append({
                    "code": "close-approach-without-interchange",
                    "geometry_distance_m": round(geometry_distance, 1),
                    "radial": radial,
                    "ring": ring,
                    "severity": "fail",
                    "terminus_distance_m": round(terminus_distance, 1),
                })
            elif terminus_distance <= TERMINUS_EXTENSION_ENVELOPE_M:
                # The endpoint-specific finding above carries the useful end
                # name and exact terminal-presence diagnosis.
                pass
            else:
                findings.append({
                    "code": "ring-radial-layout-disconnected",
                    "geometry_distance_m": round(geometry_distance, 1),
                    "radial": radial,
                    "ring": ring,
                    "severity": "review",
                    "terminus_distance_m": round(terminus_distance, 1),
                })
    failures = [finding for finding in findings if finding["severity"] == "fail"]
    reviews = [finding for finding in findings if finding["severity"] == "review"]
    return {
        "city": slug,
        "corridor_sha256": hashlib.sha256(corridor_path.read_bytes()).hexdigest(),
        "design_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "failures": failures,
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "passed": not failures,
        "review_findings": reviews,
        "ring_count": sum(shape == "ring" for shape in shapes.values()),
        "radial_count": sum(shape != "ring" for shape in shapes.values()),
        "backtrack_excursion_m": BACKTRACK_EXCURSION_M,
    }


def write_report(results: list[dict], output: Path) -> None:
    report = {
        "city_count": len(results),
        "failed_cities": [result["city"] for result in results if not result["passed"]],
        "passed": all(result["passed"] for result in results),
        "results": results,
        "review_finding_count": sum(len(result["review_findings"]) for result in results),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true")
    selection.add_argument("--design", type=Path, action="append")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    paths = sorted((REPO_ROOT / "designs").glob("*/*/*/design.toml")) if args.all else args.design
    results = [validate(path.resolve()) for path in paths]
    output = args.output
    if output is None:
        output = (
            REPO_ROOT / "designs/ring-interchange-validation.json"
            if args.all or len(paths) != 1
            else paths[0].resolve().parent / "engineering/ring-interchange-summary.json"
        )
    write_report(results, output)
    failed_cities = [result["city"] for result in results if not result["passed"]]
    review_count = sum(len(result["review_findings"]) for result in results)
    print(
        f"cities={len(results)} failed={len(failed_cities)} "
        f"review_findings={review_count}"
    )
    return 0 if not failed_cities else 1


if __name__ == "__main__":
    raise SystemExit(main())
