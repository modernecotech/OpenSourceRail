#!/usr/bin/env python3
"""Small dependency-free geometry helpers shared by city engineering generators."""

from __future__ import annotations

import json
import math
from pathlib import Path


EARTH_RADIUS_M = 6_371_008.8


def corridor_path(design_path: Path, slug: str) -> Path:
    path = design_path.parent / f"{slug}.corridor.geojson"
    if not path.is_file():
        raise RuntimeError(f"{design_path}: missing canonical corridor geometry {path.name}")
    return path


def load_line_coordinates(path: Path) -> dict[str, list[list[float]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    lines: dict[str, list[list[float]]] = {}
    for feature in data.get("features", []):
        geometry = feature.get("geometry") or {}
        properties = feature.get("properties") or {}
        if properties.get("kind") != "line" or geometry.get("type") != "LineString":
            continue
        name = str(properties.get("name", "")).strip()
        coordinates = geometry.get("coordinates") or []
        if name and len(coordinates) >= 2:
            lines[name] = [[float(point[0]), float(point[1])] for point in coordinates]
    return lines


def local_xy(coordinates: list[list[float]], lon0: float, lat0: float) -> list[tuple[float, float]]:
    scale_x = math.cos(math.radians(lat0)) * math.pi * EARTH_RADIUS_M / 180.0
    scale_y = math.pi * EARTH_RADIUS_M / 180.0
    return [((lon - lon0) * scale_x, (lat - lat0) * scale_y) for lon, lat in coordinates]


def local_lonlat(points: list[tuple[float, float]], lon0: float, lat0: float) -> list[list[float]]:
    scale_x = math.cos(math.radians(lat0)) * math.pi * EARTH_RADIUS_M / 180.0
    scale_y = math.pi * EARTH_RADIUS_M / 180.0
    return [[x / scale_x + lon0, y / scale_y + lat0] for x, y in points]


def polyline_length(points: list[tuple[float, float]]) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


def point_at(points: list[tuple[float, float]], distance: float) -> tuple[float, float]:
    total = polyline_length(points)
    target = min(max(distance, 0.0), total)
    walked = 0.0
    for a, b in zip(points, points[1:]):
        segment = math.hypot(b[0] - a[0], b[1] - a[1])
        if walked + segment >= target and segment:
            fraction = (target - walked) / segment
            return (a[0] + fraction * (b[0] - a[0]), a[1] + fraction * (b[1] - a[1]))
        walked += segment
    return points[-1]


def substring(
    points: list[tuple[float, float]], start_distance: float, end_distance: float
) -> list[tuple[float, float]]:
    """Return a distance-clipped polyline, preserving intermediate vertices."""
    total = polyline_length(points)
    start = min(max(start_distance, 0.0), total)
    end = min(max(end_distance, start), total)
    result = [point_at(points, start)]
    walked = 0.0
    for a, b in zip(points, points[1:]):
        segment = math.hypot(b[0] - a[0], b[1] - a[1])
        walked += segment
        if start < walked < end:
            result.append(b)
    result.append(point_at(points, end))
    deduplicated = [result[0]]
    for point in result[1:]:
        if point != deduplicated[-1]:
            deduplicated.append(point)
    return deduplicated


def orient_to_stations(
    points: list[tuple[float, float]], stations: list[dict[str, object]], lon0: float, lat0: float
) -> list[tuple[float, float]]:
    first = stations[0]
    station_xy = local_xy([[float(first["lon"]), float(first["lat"])]], lon0, lat0)[0]
    start_distance = math.hypot(points[0][0] - station_xy[0], points[0][1] - station_xy[1])
    end_distance = math.hypot(points[-1][0] - station_xy[0], points[-1][1] - station_xy[1])
    return list(reversed(points)) if end_distance < start_distance else points


def line_geometry(
    coordinates: list[list[float]],
    stations: list[dict[str, object]],
    declared_length_m: float,
    lon0: float,
    lat0: float,
) -> dict[str, object]:
    points = orient_to_stations(local_xy(coordinates, lon0, lat0), stations, lon0, lat0)
    geometry_length = polyline_length(points)
    if geometry_length <= 0 or declared_length_m <= 0:
        raise RuntimeError("corridor and declared line lengths must be positive")
    return {
        "points": points,
        "geometry_length_m": geometry_length,
        "declared_length_m": declared_length_m,
        "geometry_per_chainage": geometry_length / declared_length_m,
    }


def station_offset_m(
    station: dict[str, object], expected_xy: tuple[float, float], lon0: float, lat0: float
) -> float:
    actual = local_xy([[float(station["lon"]), float(station["lat"])]], lon0, lat0)[0]
    return math.hypot(expected_xy[0] - actual[0], expected_xy[1] - actual[1])
