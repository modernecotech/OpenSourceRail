"""Export a generated OSR city network to planning-grade OSR-ALN.

The city planner emits WGS84 corridor geometry, line/station chainage, and
per-line civil-class spans. This module joins those artifacts and writes one
deterministic OSR-ALN document per line. It deliberately does not invent a
surveyed vertical profile, fitted curves, or cant: those fields are explicitly
marked as planning placeholders in the output metadata and comments.

Stdlib-only, matching the rest of ``osr-aln-convert``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import tomllib
from pathlib import Path
from typing import Iterable

from osr_aln.validate import validate

PLANNING_SIMPLIFICATION_TOLERANCE_M = 10.0


def _readme(city_slug: str, rendered: dict[str, str]) -> str:
    rows: list[str] = []
    for filename, content in sorted(rendered.items()):
        doc = tomllib.loads(content)
        line_id = str(doc["meta"]["line_id"])
        length_m = float(doc["horizontal"][-1]["station_m"])
        rows.append(
            f"| [`{filename}`]({filename}) | `{line_id}` | "
            f"{length_m:,.1f} m | {len(doc.get('station', []))} |"
        )
    return "\n".join(
        [
            f"# {city_slug.title()} Planning OSR-ALN Package",
            "",
            "Deterministic alignment exports for every line in the current generated network.",
            "",
            "| File | Design line | Length | Stations |",
            "|---|---:|---:|---:|",
            *rows,
            "",
            "## Status",
            "",
            "These files are **planning-only and not for construction**. Horizontal control",
            "comes from the current WGS84 corridor and is projected to the local UTM zone.",
            "Circular curves and transitions are not fitted, the vertical profile is a",
            "zero-datum placeholder, and cant has not been designed. Survey, curve-fit,",
            "vertical-profile, cant, geotechnical, utility, property, drainage, and",
            "structural release gates therefore remain open.",
            "",
            "Each OSR-ALN file records the SHA-256 hashes of `../../design.toml` and the",
            "city corridor GeoJSON used to generate it.",
            "",
        ]
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _toml_string(value: str) -> str:
    """Return a JSON/TOML-compatible quoted UTF-8 string."""

    return json.dumps(value, ensure_ascii=False)


def _utm_zone(longitude_deg: float) -> int:
    return max(1, min(60, int((longitude_deg + 180.0) / 6.0) + 1))


def _wgs84_to_utm(latitude_deg: float, longitude_deg: float, zone: int) -> tuple[float, float]:
    """Project WGS84 latitude/longitude into one UTM zone.

    Formula follows the standard transverse-Mercator series for WGS84. The
    generated city envelopes are much smaller than a UTM zone, so a single
    zone is enforced for every line in a network.
    """

    a = 6_378_137.0
    flattening = 1.0 / 298.257_223_563
    eccentricity_sq = flattening * (2.0 - flattening)
    second_eccentricity_sq = eccentricity_sq / (1.0 - eccentricity_sq)
    scale = 0.9996

    lat = math.radians(latitude_deg)
    lon = math.radians(longitude_deg)
    central_lon = math.radians((zone - 1) * 6 - 180 + 3)
    sin_lat = math.sin(lat)
    cos_lat = math.cos(lat)
    tan_lat = math.tan(lat)

    n = a / math.sqrt(1.0 - eccentricity_sq * sin_lat * sin_lat)
    t = tan_lat * tan_lat
    c = second_eccentricity_sq * cos_lat * cos_lat
    aa = cos_lat * (lon - central_lon)
    m = a * (
        (1.0 - eccentricity_sq / 4.0 - 3.0 * eccentricity_sq**2 / 64.0 - 5.0 * eccentricity_sq**3 / 256.0) * lat
        - (3.0 * eccentricity_sq / 8.0 + 3.0 * eccentricity_sq**2 / 32.0 + 45.0 * eccentricity_sq**3 / 1024.0) * math.sin(2.0 * lat)
        + (15.0 * eccentricity_sq**2 / 256.0 + 45.0 * eccentricity_sq**3 / 1024.0) * math.sin(4.0 * lat)
        - (35.0 * eccentricity_sq**3 / 3072.0) * math.sin(6.0 * lat)
    )

    easting = scale * n * (
        aa
        + (1.0 - t + c) * aa**3 / 6.0
        + (5.0 - 18.0 * t + t * t + 72.0 * c - 58.0 * second_eccentricity_sq) * aa**5 / 120.0
    ) + 500_000.0
    northing = scale * (
        m
        + n
        * tan_lat
        * (
            aa * aa / 2.0
            + (5.0 - t + 9.0 * c + 4.0 * c * c) * aa**4 / 24.0
            + (61.0 - 58.0 * t + t * t + 600.0 * c - 330.0 * second_eccentricity_sq) * aa**6 / 720.0
        )
    )
    if latitude_deg < 0.0:
        northing += 10_000_000.0
    return easting, northing


def _bearing(a: tuple[float, float], b: tuple[float, float]) -> float:
    easting_delta = b[0] - a[0]
    northing_delta = b[1] - a[1]
    return math.degrees(math.atan2(easting_delta, northing_delta)) % 360.0


def _point_to_segment_distance(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
) -> float:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    denominator = dx * dx + dy * dy
    if denominator == 0.0:
        return math.dist(point, start)
    fraction = max(
        0.0,
        min(
            1.0,
            ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy)
            / denominator,
        ),
    )
    closest = (start[0] + fraction * dx, start[1] + fraction * dy)
    return math.dist(point, closest)


def _simplify_polyline(
    points: list[tuple[float, float]], tolerance_m: float
) -> list[tuple[float, float]]:
    """Douglas-Peucker simplification with a metric maximum deviation."""

    if len(points) <= 2:
        return points
    maximum_distance = -1.0
    split_index = 0
    for index, point in enumerate(points[1:-1], start=1):
        distance = _point_to_segment_distance(point, points[0], points[-1])
        if distance > maximum_distance:
            maximum_distance = distance
            split_index = index
    if maximum_distance <= tolerance_m:
        return [points[0], points[-1]]
    before = _simplify_polyline(points[: split_index + 1], tolerance_m)
    after = _simplify_polyline(points[split_index:], tolerance_m)
    return before[:-1] + after


def _projected_points(
    coordinates: list[list[float]],
    zone: int,
    design_length_m: float,
) -> list[dict[str, float]]:
    if len(coordinates) < 2:
        raise ValueError("line geometry must contain at least two coordinates")
    source_xy = [_wgs84_to_utm(float(lat), float(lon), zone) for lon, lat in coordinates]
    xy = _simplify_polyline(source_xy, PLANNING_SIMPLIFICATION_TOLERANCE_M)
    cumulative = [0.0]
    for start, end in zip(xy, xy[1:]):
        cumulative.append(cumulative[-1] + math.dist(start, end))
    if cumulative[-1] <= 0.0:
        raise ValueError("line geometry has zero projected length")
    chainage_scale = design_length_m / cumulative[-1]

    rows: list[dict[str, float]] = []
    for index, point in enumerate(xy):
        bearing_in = _bearing(xy[index - 1], point) if index else _bearing(point, xy[1])
        bearing_out = _bearing(point, xy[index + 1]) if index + 1 < len(xy) else bearing_in
        rows.append(
            {
                "station_m": cumulative[index] * chainage_scale,
                "easting_m": point[0],
                "northing_m": point[1],
                "bearing_in_deg": bearing_in,
                "bearing_out_deg": bearing_out,
            }
        )
    rows[-1]["station_m"] = design_length_m
    return rows


def _render_line(
    *,
    city_slug: str,
    line: dict,
    coordinates: list[list[float]],
    stations: list[dict],
    civil_segments: list[dict],
    design_date: str,
    design_sha256: str,
    geojson_sha256: str,
    utm_zone: int,
    northern_hemisphere: bool,
) -> str:
    line_name = str(line["name"])
    length_m = float(line["length_m"])
    projected = _projected_points(coordinates, utm_zone, length_m)
    epsg = 32600 + utm_zone if northern_hemisphere else 32700 + utm_zone

    out = [
        "# OSR-ALN v1.0 — deterministic current-network planning export.",
        "# NOT FOR CONSTRUCTION: horizontal geometry is the generated GIS trace;",
        "# curve fitting, surveyed top-of-rail levels, and cant remain release gates.",
        f"# Source city: {city_slug}; source line: {line_name}; length: {length_m:.1f} m.",
        "",
        "[meta]",
        'schema_version = "1.0"',
        f"line_id        = {_toml_string(line_name)}",
        f"design_date    = {_toml_string(design_date)}",
        'surveyor       = "UNSURVEYED — OSR generated planning trace"',
        f"preset         = {_toml_string(str(line['geometry']))}",
        f"consist        = {_toml_string(str(line['rolling_stock']))}",
        f'crs            = "EPSG:{epsg}"',
        'units          = "metric"',
        f"is_ring        = {str(str(line.get('shape', '')).lower() == 'ring').lower()}",
        'source_status  = "planning-only; replace with signed survey/CAD export"',
        f"source_design_sha256 = {_toml_string(design_sha256)}",
        f"source_geojson_sha256 = {_toml_string(geojson_sha256)}",
        f'horizontal_status = "GIS control polyline simplified to ≤{PLANNING_SIMPLIFICATION_TOLERANCE_M:g} m; curves and transitions not fitted"',
        'vertical_status   = "zero-datum placeholder; surveyed top-of-rail profile required"',
        'cant_status       = "not designed; absent means zero only for planning validation"',
        'civil_status      = "generated planning classification; field verification required"',
        "",
        "# Horizontal control points projected from the checked-in WGS84 GeoJSON.",
        "# Radius/transition are zero because no survey-grade curve fit exists yet.",
    ]
    for row in projected:
        out.extend(
            [
                "",
                "[[horizontal]]",
                f"station_m           = {row['station_m']:.3f}",
                f"easting_m           = {row['easting_m']:.3f}",
                f"northing_m          = {row['northing_m']:.3f}",
                f"bearing_in_deg      = {row['bearing_in_deg']:.3f}",
                f"bearing_out_deg     = {row['bearing_out_deg']:.3f}",
                "curve_radius_m      = 0.000",
                "transition_length_m = 0.000",
            ]
        )

    out.extend(
        [
            "",
            "# Placeholder vertical profile. Replace both rows with surveyed",
            "# top-of-rail elevations and designed vertical curves before release.",
            "",
            "[[vertical]]",
            "station_m   = 0.000",
            "elevation_m = 0.000",
            "vc_radius_m = 0.000",
            "",
            "[[vertical]]",
            f"station_m   = {length_m:.3f}",
            "elevation_m = 0.000",
            "vc_radius_m = 0.000",
            "",
            "# Civil spans are the current planner classification, not a surveyed",
            "# constructability decision. They cover the complete line without gaps.",
        ]
    )
    for span in civil_segments:
        out.extend(
            [
                "",
                "[[civil]]",
                f"from_station_m = {float(span['from_station_m']):.3f}",
                f"to_station_m   = {float(span['to_station_m']):.3f}",
                f"class          = {_toml_string(str(span['class']))}",
            ]
        )

    out.extend(["", "# Station IDs and chainages resolve directly to design.toml."])
    for station in stations:
        out.extend(
            [
                "",
                "[[station]]",
                f"id                = {_toml_string(str(station['id']))}",
                f"station_m         = {float(station['s_m']):.3f}",
                f"platform_length_m = {float(station['platform_length_m']):.3f}",
            ]
        )
    out.extend(
        [
            "",
            "# No [[cant]] rows: cant has not been designed for this planning trace.",
            "",
        ]
    )
    return "\n".join(out)


def render_network(
    design_path: Path,
    geojson_path: Path,
    *,
    design_date: str,
) -> dict[str, str]:
    with design_path.open("rb") as handle:
        design = tomllib.load(handle)
    geojson = json.loads(geojson_path.read_text())

    lines = design.get("lines", [])
    civil = design.get("civil_segments", [])
    if not civil:
        raise ValueError("design.toml has no [[civil_segments]]; regenerate it with current osr-design")

    line_features = {
        str(feature.get("properties", {}).get("name")): feature
        for feature in geojson.get("features", [])
        if feature.get("properties", {}).get("kind") == "line"
    }
    known_line_names = {str(line["name"]) for line in lines}
    if set(line_features) != known_line_names:
        raise ValueError(
            f"GeoJSON/design line mismatch: design={sorted(known_line_names)}, "
            f"geojson={sorted(line_features)}"
        )

    all_coordinates = [
        coordinate
        for feature in line_features.values()
        for coordinate in feature["geometry"]["coordinates"]
    ]
    mean_lon = sum(float(point[0]) for point in all_coordinates) / len(all_coordinates)
    mean_lat = sum(float(point[1]) for point in all_coordinates) / len(all_coordinates)
    zone = _utm_zone(mean_lon)
    northern = mean_lat >= 0.0
    slug = str(design["city"]["slug"])
    design_hash = _sha256(design_path)
    geojson_hash = _sha256(geojson_path)
    known_station_ids = {
        str(station["id"]) for station in design.get("stations", []) if station.get("id")
    }

    rendered: dict[str, str] = {}
    for line in lines:
        line_name = str(line["name"])
        line_stations = [
            station for station in design.get("stations", []) if station.get("line") == line_name
        ]
        line_civil = [span for span in civil if span.get("line") == line_name]
        if not line_civil:
            raise ValueError(f"{line_name} has no civil segments")
        content = _render_line(
            city_slug=slug,
            line=line,
            coordinates=line_features[line_name]["geometry"]["coordinates"],
            stations=line_stations,
            civil_segments=line_civil,
            design_date=design_date,
            design_sha256=design_hash,
            geojson_sha256=geojson_hash,
            utm_zone=zone,
            northern_hemisphere=northern,
        )
        parsed = tomllib.loads(content)
        report = validate(
            parsed,
            known_station_ids=known_station_ids,
            known_line_ids=known_line_names,
        )
        if not report.ok:
            raise ValueError(f"generated {line_name} failed validation:\n{report.format_text()}")
        filename = f"{slug}-{line_name.replace('line-', 'line')}.aln.toml"
        rendered[filename] = content
    return rendered


def export_network(
    design_path: Path,
    geojson_path: Path,
    output_dir: Path,
    *,
    design_date: str,
    check: bool = False,
) -> list[Path]:
    rendered = render_network(design_path, geojson_path, design_date=design_date)
    package = {**rendered, "README.md": _readme(design_path.parent.name, rendered)}
    output_paths = [output_dir / filename for filename in sorted(package)]
    if check:
        drift = [path for path in output_paths if not path.exists() or path.read_text() != package[path.name]]
        unexpected = sorted(output_dir.iterdir()) if output_dir.exists() else []
        unexpected = [path for path in unexpected if path.is_file() and path.name not in package]
        if drift or unexpected:
            names = [str(path) for path in drift + unexpected]
            raise ValueError("current-network OSR-ALN drift: " + ", ".join(names))
        return output_paths

    output_dir.mkdir(parents=True, exist_ok=True)
    for path in output_paths:
        path.write_text(package[path.name])
    return output_paths


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="current-network-to-osr-aln",
        description="Export generated design.toml + corridor GeoJSON to planning OSR-ALN files.",
    )
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--geojson", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--design-date", required=True, help="Fixed ISO date for deterministic output.")
    parser.add_argument("--check", action="store_true", help="Fail if checked-in outputs differ.")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        paths = export_network(
            args.design,
            args.geojson,
            args.output_dir,
            design_date=args.design_date,
            check=args.check,
        )
    except (OSError, ValueError, KeyError, tomllib.TOMLDecodeError) as error:
        print(f"current-network-to-osr-aln: {error}", file=sys.stderr)
        return 1
    action = "checked" if args.check else "wrote"
    print(f"{action} {len(paths)} current-network OSR-ALN file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
