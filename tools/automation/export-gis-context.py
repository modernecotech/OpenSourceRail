#!/usr/bin/env python3
"""Convert a cached OSR city context snapshot into deterministic GeoJSON layers."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


def coordinates(nodes: list[list[float]]) -> list[list[float]]:
    return [[round(node[1], 7), round(node[0], 7)] for node in nodes]


def feature(item: dict, category: str) -> dict | None:
    if category == "water" and "outer_rings" in item:
        # Keep inner rings with the containing outer; distinct lake lobes
        # stay distinct polygons. Coordinates are lon/lat in GeoJSON.
        def contains(ring, point):
            x, y = point
            inside = False
            for a, b in zip(ring, ring[1:]):
                if (a[1] > y) != (b[1] > y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
                    inside = not inside
            return inside
        outers = [coordinates(r) for r in item["outer_rings"]]
        inners = [coordinates(r) for r in item.get("inner_rings", [])]
        polygons = [[outer, *[hole for hole in inners if contains(outer, hole[0])]] for outer in outers]
        return {"type": "Feature", "geometry": {"type": "MultiPolygon", "coordinates": polygons},
                "properties": {"osm_id": item.get("id"), "osm_type": "relation", "kind": item.get("kind", "water")}}
    points = coordinates(item.get("nodes", []))
    if len(points) < 2:
        return None
    closed = len(points) >= 4 and points[0] == points[-1]
    polygon_categories = {"buildings", "protected"}
    polygon = category in polygon_categories or (category == "water" and closed)
    geometry = {
        "type": "Polygon" if polygon else "LineString",
        "coordinates": [points] if polygon else points,
    }
    properties = {
        "osm_id": item.get("id"),
        "kind": item.get("class") or item.get("kind") or category.rstrip("s"),
    }
    if item.get("name"):
        properties["name"] = item["name"]
    return {"type": "Feature", "geometry": geometry, "properties": properties}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="processed osr_osm city JSON")
    parser.add_argument("output", type=Path, help="output directory")
    args = parser.parse_args()

    raw_bytes = args.input.read_bytes()
    source = json.loads(raw_bytes)
    fetched_at = datetime.fromtimestamp(source["fetched_at"], UTC).isoformat()
    mappings = {
        "roads": "arterials",
        "buildings": "buildings",
        "water": "water",
        "protected": "protected",
        "existing-rail": "rail_existing",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    digests: dict[str, str] = {}
    for layer, source_key in mappings.items():
        features = [
            converted
            for item in source.get(source_key, [])
            if (converted := feature(item, source_key)) is not None
        ]
        collection = {
            "type": "FeatureCollection",
            "metadata": {
                "schema_version": 1,
                "city": source["slug"],
                "coordinate_reference_system": "EPSG:4326",
                "source": "OpenStreetMap contributors",
                "license": "ODbL 1.0",
                "source_fetched_at": fetched_at,
                "source_sha256": hashlib.sha256(raw_bytes).hexdigest(),
                "generator": "tools/automation/export-gis-context.py",
            },
            "features": features,
        }
        path = args.output / f"context-{layer}.geojson"
        path.write_text(
            json.dumps(collection, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n",
            encoding="utf-8",
        )
        digests[layer] = hashlib.sha256(path.read_bytes()).hexdigest()
        print(f"{path}: {len(features)} features")

    lock_path = args.output.parent / "sources.lock.json"
    if lock_path.exists():
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        by_id = {entry["id"]: entry for entry in lock["sources"]}
        for layer, digest in digests.items():
            source_id = f"context-{layer}"
            entry = by_id.get(source_id)
            if entry is None:
                entry = {
                    "id": source_id,
                    "kind": "osm-context-geojson",
                    "path": f"gis/context-{layer}.geojson",
                    "sha256": digest,
                }
                lock["sources"].append(entry)
            else:
                entry["sha256"] = digest
        lock_path.write_text(
            json.dumps(lock, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"{lock_path}: refreshed {len(digests)} source locks")


if __name__ == "__main__":
    main()
