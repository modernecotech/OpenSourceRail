#!/usr/bin/env python3
"""Generate a QGIS-ready GeoPackage and review layers for one OSR city."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
import tomllib
from pathlib import Path

import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from engineering.city_geometry import (  # noqa: E402
    corridor_path,
    line_geometry,
    load_line_coordinates,
    local_lonlat,
    point_at,
    station_offset_m,
    substring,
)


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def collection(features: list[dict[str, object]]) -> dict[str, object]:
    return {"type": "FeatureCollection", "features": features}


def feature(geometry: dict[str, object], **properties: object) -> dict[str, object]:
    return {"type": "Feature", "geometry": geometry, "properties": properties}


def qgis_convert(layer_files: list[tuple[str, Path]], output: Path) -> str:
    script_lines = [
        'set -eu',
        'ogr2ogr -f GPKG "$1" "$2" -nln "$3" -a_srs EPSG:4326 -overwrite',
    ]
    arguments = [str(output), str(layer_files[0][1]), layer_files[0][0]]
    parameter = 4
    for name, path in layer_files[1:]:
        script_lines.append(
            f'ogr2ogr -f GPKG -update "$1" "${{{parameter}}}" -nln "${{{parameter + 1}}}" -a_srs EPSG:4326'
        )
        arguments.extend([str(path), name])
        parameter += 2
    script_lines.extend(['ogrinfo -ro -so "$1"', 'qgis_process --version'])
    completed = subprocess.run(
        [
            "flatpak",
            "run",
            "--command=sh",
            "org.qgis.qgis",
            "-c",
            "\n".join(script_lines),
            "osr-gis",
            *arguments,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if completed.returncode:
        raise RuntimeError(f"QGIS/GDAL GeoPackage conversion failed:\n{completed.stdout}")
    return completed.stdout


def generate(design_path: Path, output: Path) -> dict[str, object]:
    design_path = design_path.resolve()
    output = output.resolve()
    design = tomllib.loads(design_path.read_text(encoding="utf-8"))
    city = design.get("city", {})
    slug = str(city.get("slug", "")).strip()
    if not slug:
        raise RuntimeError(f"{design_path}: missing city.slug")
    scenario_path = design_path.parent / f"{slug}.toml"
    if not scenario_path.is_file():
        raise RuntimeError(f"{design_path}: missing city scenario {scenario_path.name}")
    scenario = tomllib.loads(scenario_path.read_text(encoding="utf-8"))
    source_path = corridor_path(design_path, slug)
    source_data = json.loads(source_path.read_text(encoding="utf-8"))
    line_coordinates = load_line_coordinates(source_path)
    lines = {str(line["name"]): line for line in design.get("lines", [])}
    stations = list(design.get("stations", []))
    lon0 = sum(float(station["lon"]) for station in stations) / len(stations)
    lat0 = sum(float(station["lat"]) for station in stations) / len(stations)
    geometry_by_line: dict[str, dict[str, object]] = {}
    issues: list[dict[str, object]] = []

    corridor_features = [
        item for item in source_data.get("features", []) if (item.get("properties") or {}).get("kind") == "line"
    ]
    station_features: list[dict[str, object]] = []
    endpoint_features: list[dict[str, object]] = []
    for line_name, line in lines.items():
        is_ring = str(line.get("shape", "radial")) == "ring"
        line_stations = sorted(
            (station for station in stations if station.get("line") == line_name),
            key=lambda station: float(station["s_m"]),
        )
        coordinates = line_coordinates.get(line_name)
        if not coordinates:
            raise RuntimeError(f"{slug}/{line_name}: no LineString in {source_path.name}")
        geometry = line_geometry(
            coordinates, line_stations, float(line["length_m"]), lon0, lat0
        )
        geometry_by_line[line_name] = geometry
        for station in line_stations:
            expected = point_at(
                geometry["points"], float(station["s_m"]) * float(geometry["geometry_per_chainage"])
            )
            offset = station_offset_m(station, expected, lon0, lat0)
            station_features.append(
                feature(
                    {"type": "Point", "coordinates": [float(station["lon"]), float(station["lat"])]},
                    id=station["id"],
                    line=line_name,
                    chainage_m=float(station["s_m"]),
                    archetype=station.get("archetype"),
                    platform_length_m=station.get("platform_length_m"),
                    junction_group=station.get("junction_group"),
                    anchor_kind=station.get("anchor_kind"),
                    anchor_name=station.get("anchor_name"),
                    corridor_offset_m=round(offset, 3),
                )
            )
        start_gap = float(line_stations[0]["s_m"])
        end_gap = (
            0.0
            if is_ring
            else float(line["length_m"]) - float(line_stations[-1]["s_m"])
        )
        for code, gap, chainage in (
            ("line-start-station-gap", start_gap, 0.0),
            ("line-end-station-gap", end_gap, float(line["length_m"])),
        ):
            if is_ring and code == "line-start-station-gap":
                continue
            if abs(gap) > 1.0:
                location = point_at(
                    geometry["points"], chainage * float(geometry["geometry_per_chainage"])
                )
                lonlat = local_lonlat([location], lon0, lat0)[0]
                issue = {"code": code, "line": line_name, "gap_m": round(gap, 3)}
                issues.append(issue)
                endpoint_features.append(
                    feature({"type": "Point", "coordinates": lonlat}, **issue)
                )

    interchange_features: list[dict[str, object]] = []
    for interchange in design.get("interchanges", []):
        interchange_features.append(
            feature(
                {
                    "type": "Point",
                    "coordinates": [float(interchange["lon"]), float(interchange["lat"])],
                },
                id=interchange["id"],
                junction_group=interchange["junction_group"],
                line_count=len(interchange.get("lines", [])),
                lines=",".join(str(value) for value in interchange.get("lines", [])),
                platform_count=len(interchange.get("platforms", [])),
                platforms=",".join(
                    str(value) for value in interchange.get("platforms", [])
                ),
            )
        )

    civil_features: list[dict[str, object]] = []
    for index, segment in enumerate(design.get("civil_segments", [])):
        line_name = str(segment["line"])
        geometry = geometry_by_line[line_name]
        factor = float(geometry["geometry_per_chainage"])
        clipped = substring(
            geometry["points"],
            float(segment["from_station_m"]) * factor,
            float(segment["to_station_m"]) * factor,
        )
        civil_features.append(
            feature(
                {"type": "LineString", "coordinates": local_lonlat(clipped, lon0, lat0)},
                id=f"{line_name}-civil-{index + 1:03d}",
                line=line_name,
                from_chainage_m=float(segment["from_station_m"]),
                to_chainage_m=float(segment["to_station_m"]),
                civil_class=segment.get("class"),
            )
        )

    station_by_id = {str(station["id"]): station for station in stations}
    site_features: list[dict[str, object]] = []
    for site in scenario.get("sites", []):
        station = station_by_id.get(str(site["station"]))
        if station is None:
            issues.append({"code": "energy-site-station-missing", "station": site["station"]})
            continue
        properties = {key: value for key, value in site.items() if key != "station"}
        site_features.append(
            feature(
                {"type": "Point", "coordinates": [float(station["lon"]), float(station["lat"])]},
                station=site["station"],
                line=station["line"],
                **properties,
            )
        )

    depot_features: list[dict[str, object]] = []
    for depot in design.get("depots", []):
        station = station_by_id.get(str(depot["station"]))
        if station is None:
            issues.append({"code": "depot-station-missing", "station": depot["station"]})
            continue
        depot_features.append(
            feature(
                {"type": "Point", "coordinates": [float(station["lon"]), float(station["lat"])]},
                station=depot["station"],
                line=station["line"],
                archetype=depot.get("archetype"),
                fleet_stalls=depot.get("fleet_stalls"),
            )
        )

    layers = {
        "corridors": collection(corridor_features),
        "stations": collection(station_features),
        "interchanges": collection(interchange_features),
        "civil_segments": collection(civil_features),
        "energy_sites": collection(site_features),
        "depots": collection(depot_features),
        "input_issues": collection(endpoint_features),
    }
    layer_files: list[tuple[str, Path]] = []
    for name, data in layers.items():
        path = output / "layers" / f"{name}.geojson"
        atomic_json(path, data)
        if data["features"]:
            layer_files.append((name, path))
    output.mkdir(parents=True, exist_ok=True)
    gpkg_path = output / f"{slug}.gpkg"
    with tempfile.NamedTemporaryFile(dir=output, suffix=".gpkg", delete=False) as handle:
        temporary_gpkg = Path(handle.name)
    temporary_gpkg.unlink()
    try:
        log = qgis_convert(layer_files, temporary_gpkg)
        os.replace(temporary_gpkg, gpkg_path)
    finally:
        temporary_gpkg.unlink(missing_ok=True)
    log = log.replace(str(temporary_gpkg), gpkg_path.name)
    log = log.replace(str(output) + os.sep, "")
    (output / "qgis-gdal.log").write_text(log, encoding="utf-8")
    report = {
        "analysis_family": "OSR-AN-GIS-CITY",
        "analysis_id": f"OSR-AN-GIS-CITY:{slug}",
        "city": slug,
        "design_input": str(design_path.relative_to(REPO_ROOT)),
        "design_sha256": hashlib.sha256(design_path.read_bytes()).hexdigest(),
        "corridor_input": str(source_path.relative_to(REPO_ROOT)),
        "corridor_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "scenario_input": str(scenario_path.relative_to(REPO_ROOT)),
        "scenario_sha256": hashlib.sha256(scenario_path.read_bytes()).hexdigest(),
        "coordinate_reference_system": "EPSG:4326",
        "geopackage": str(gpkg_path.relative_to(REPO_ROOT)),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "layers": {name: len(data["features"]) for name, data in layers.items()},
        "input_issues": issues,
        "input_quality_passed": not issues,
        "generation_passed": gpkg_path.is_file() and gpkg_path.stat().st_size > 0,
        "passed": gpkg_path.is_file() and gpkg_path.stat().st_size > 0 and not issues,
        "tool": {
            "name": "QGIS/GDAL",
            "version_output": next(
                (line for line in log.splitlines() if line.startswith("QGIS ")), "unknown"
            ),
        },
    }
    atomic_json(output / "summary.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--allow-input-gaps", action="store_true")
    args = parser.parse_args()
    design = tomllib.loads(args.design.read_text(encoding="utf-8"))
    slug = str(design.get("city", {}).get("slug", "unknown"))
    output = args.output_dir or args.design.resolve().parent / "engineering/gis"
    report = generate(args.design, output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["passed"] or (report["generation_passed"] and args.allow_input_gaps) else 1


if __name__ == "__main__":
    raise SystemExit(main())
