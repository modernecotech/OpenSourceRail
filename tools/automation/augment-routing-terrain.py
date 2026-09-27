#!/usr/bin/env python3
"""Add reproducible open-terrain and water evidence to an existing grid."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "design/city-generation/src"))

from osr_geo.cli import _load_city  # noqa: E402
from osr_geo.rasterize import GridRef, build_water_mask  # noqa: E402
from osr_geo.terrain import sample_elevation_grid, terrain_slope_percent  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osm-json", type=Path, required=True)
    parser.add_argument("--sidecar", type=Path, required=True)
    parser.add_argument("--terrain-cache", type=Path, required=True)
    args = parser.parse_args()

    city = _load_city(args.osm_json)
    sidecar = json.loads(args.sidecar.read_text())
    reference = GridRef(**sidecar["grid"])
    sample = sample_elevation_grid(
        city.bbox, reference.height, reference.width, args.terrain_cache
    )
    water = build_water_mask(city, reference)
    slope = terrain_slope_percent(sample.elevation_m, reference.cell_m)
    slug = city.slug
    directory = args.sidecar.parent
    outputs = {
        "water": (directory / f"{slug}.water.npy", water, "u8"),
        "elevation": (directory / f"{slug}.elevation.npy", sample.elevation_m, "f32"),
        "terrain_slope": (directory / f"{slug}.terrain-slope.npy", slope, "f32"),
    }
    for name, (path, values, dtype) in outputs.items():
        values.astype(np.uint8 if dtype == "u8" else np.float32).tofile(path)
        sidecar["rasters"][name] = {
            "path": path.name,
            "dtype": dtype,
            "shape": [reference.height, reference.width],
            "byteorder": "little",
        }
        print(f"{path}: {values.size} cells")
    provenance_path = directory / f"{slug}.terrain-provenance.json"
    provenance_path.write_text(
        json.dumps(sample.provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.sidecar.write_text(
        json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(provenance_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
