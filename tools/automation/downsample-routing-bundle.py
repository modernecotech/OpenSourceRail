#!/usr/bin/env python3
"""Create a compact deterministic OSR routing bundle from a raster bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_f32(path: Path, cells: int) -> tuple[float, ...]:
    data = path.read_bytes()
    if len(data) != cells * 4:
        raise ValueError(f"{path}: expected {cells * 4} bytes, found {len(data)}")
    return struct.unpack(f"<{cells}f", data)


def encode_f32(values: list[float]) -> bytes:
    return struct.pack(f"<{len(values)}f", *values)


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def build_outputs(sidecar_path: Path, slug: str, factor: int) -> dict[str, bytes]:
    source_dir = sidecar_path.parent
    sidecar = json.loads(sidecar_path.read_text())
    source_grid = sidecar["grid"]
    height = int(source_grid["height"])
    width = int(source_grid["width"])
    cells = height * width
    cost_path = source_dir / f"{slug}.cost.npy"
    demand_path = source_dir / f"{slug}.demand.npy"
    buildability_path = source_dir / f"{slug}.buildability.npy"
    anchors_path = source_dir / f"{slug}.anchors.json"
    water_path = source_dir / f"{slug}.water.npy"
    elevation_path = source_dir / f"{slug}.elevation.npy"
    terrain_slope_path = source_dir / f"{slug}.terrain-slope.npy"
    terrain_provenance_path = source_dir / f"{slug}.terrain-provenance.json"
    cost = read_f32(cost_path, cells)
    demand = read_f32(demand_path, cells)
    buildability = buildability_path.read_bytes()
    if len(buildability) != cells:
        raise ValueError(
            f"{buildability_path}: expected {cells} bytes, found {len(buildability)}"
        )
    water = water_path.read_bytes() if water_path.exists() else None
    if water is not None and len(water) != cells:
        raise ValueError(f"{water_path}: expected {cells} bytes, found {len(water)}")
    elevation = read_f32(elevation_path, cells) if elevation_path.exists() else None
    terrain_slope = read_f32(terrain_slope_path, cells) if terrain_slope_path.exists() else None
    if (elevation is None) != (terrain_slope is None):
        raise ValueError("elevation and terrain-slope rasters must be supplied together")

    out_height = math.ceil(height / factor)
    out_width = math.ceil(width / factor)
    out_cell_m = float(source_grid["cell_m"]) * factor
    out_cost: list[float] = []
    out_demand: list[float] = []
    out_buildability = bytearray()
    out_water = bytearray()
    out_elevation: list[float] = []
    out_terrain_slope: list[float] = []
    for out_row in range(out_height):
        row_start = out_row * factor
        row_end = min(row_start + factor, height)
        for out_col in range(out_width):
            col_start = out_col * factor
            col_end = min(col_start + factor, width)
            buildable_costs: list[float] = []
            maximum_demand = 0.0
            block_elevation: list[float] = []
            maximum_slope = 0.0
            water_total = 0
            water_samples = 0
            for row in range(row_start, row_end):
                offset = row * width
                for col in range(col_start, col_end):
                    index = offset + col
                    maximum_demand = max(maximum_demand, demand[index])
                    if water is not None:
                        water_total += water[index]
                        water_samples += 1
                    if elevation is not None and math.isfinite(elevation[index]):
                        block_elevation.append(elevation[index])
                    if terrain_slope is not None and math.isfinite(terrain_slope[index]):
                        maximum_slope = max(maximum_slope, terrain_slope[index])
                    if buildability[index] and math.isfinite(cost[index]):
                        buildable_costs.append(cost[index])
            if buildable_costs:
                out_buildability.append(1)
                out_cost.append(min(buildable_costs))
            else:
                out_buildability.append(0)
                out_cost.append(math.inf)
            out_demand.append(maximum_demand)
            if water is not None:
                out_water.append(round(water_total / max(1, water_samples)))
            if elevation is not None:
                out_elevation.append(
                    sum(block_elevation) / len(block_elevation) if block_elevation else math.nan
                )
                out_terrain_slope.append(maximum_slope)

    if elevation is not None:
        # Recalculate grade on the compact grid. Taking the maximum of source
        # slopes would preserve single-pixel DEM noise and overstate steep
        # terrain in otherwise flat cities.
        for row in range(out_height):
            for col in range(out_width):
                left = out_elevation[row * out_width + max(0, col - 1)]
                right = out_elevation[row * out_width + min(out_width - 1, col + 1)]
                north = out_elevation[max(0, row - 1) * out_width + col]
                south = out_elevation[min(out_height - 1, row + 1) * out_width + col]
                dx_cells = 1 if col in {0, out_width - 1} else 2
                dy_cells = 1 if row in {0, out_height - 1} else 2
                if all(math.isfinite(value) for value in [left, right, north, south]):
                    dx = (right - left) / (dx_cells * out_cell_m)
                    dy = (south - north) / (dy_cells * out_cell_m)
                    out_terrain_slope[row * out_width + col] = math.hypot(dx, dy) * 100.0
                else:
                    out_terrain_slope[row * out_width + col] = math.nan
    grid = dict(source_grid)
    grid.update(
        {
            "height": out_height,
            "width": out_width,
            "cell_m": out_cell_m,
            "bbox_south": source_grid["bbox_north"]
            - out_height * out_cell_m / source_grid["m_per_deg_lat"],
            "bbox_east": source_grid["bbox_west"]
            + out_width * out_cell_m / source_grid["m_per_deg_lon"],
        }
    )
    raster = lambda name, dtype: {
        "path": f"{slug}.{name}.npy",
        "dtype": dtype,
        "shape": [out_height, out_width],
        "byteorder": "little",
    }
    compact_sidecar = {
        "grid": grid,
        "rasters": {
            "buildability": raster("buildability", "u8"),
            "cost": raster("cost", "f32"),
            "demand": raster("demand", "f32"),
        },
    }
    if water is not None:
        compact_sidecar["rasters"]["water"] = raster("water", "u8")
    if elevation is not None:
        compact_sidecar["rasters"]["elevation"] = raster("elevation", "f32")
        compact_sidecar["rasters"]["terrain_slope"] = raster("terrain-slope", "f32")
    anchors = json.loads(anchors_path.read_text())
    for anchor in anchors:
        anchor["row"] = min(int(anchor["row"]) // factor, out_height - 1)
        anchor["col"] = min(int(anchor["col"]) // factor, out_width - 1)
    anchors.sort(key=lambda item: (item["id"], item["row"], item["col"]))
    upstream_paths = [sidecar_path, cost_path, demand_path, buildability_path, anchors_path]
    upstream_paths.extend(
        path
        for path in [water_path, elevation_path, terrain_slope_path, terrain_provenance_path]
        if path.exists()
    )
    upstream = {
        path.name: sha256(path.read_bytes())
        for path in upstream_paths
    }
    provenance = {
        "schema_version": 1,
        "generator": "tools/automation/downsample-routing-bundle.py",
        "factor": factor,
        "aggregation": {
            "buildability": "any-buildable-cell",
            "cost": "minimum-buildable-cost",
            "demand": "maximum-demand",
            **({"water": "mean-water-coverage-percent"} if water is not None else {}),
            **({
                "elevation": "mean-valid-elevation",
                "terrain_slope": "gradient-of-mean-elevation",
            } if elevation is not None else {}),
        },
        "upstream_sha256": upstream,
    }
    outputs = {
        f"{slug}.grid.json": json_bytes(compact_sidecar),
        f"{slug}.cost.npy": encode_f32(out_cost),
        f"{slug}.demand.npy": encode_f32(out_demand),
        f"{slug}.buildability.npy": bytes(out_buildability),
        f"{slug}.anchors.json": json_bytes(anchors),
        f"{slug}.routing-provenance.json": json_bytes(provenance),
    }
    if water is not None:
        outputs[f"{slug}.water.npy"] = bytes(out_water)
    if elevation is not None:
        outputs[f"{slug}.elevation.npy"] = encode_f32(out_elevation)
        outputs[f"{slug}.terrain-slope.npy"] = encode_f32(out_terrain_slope)
        if terrain_provenance_path.exists():
            outputs[f"{slug}.terrain-provenance.json"] = terrain_provenance_path.read_bytes()
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sidecar", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--factor", type=int, default=5)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.factor < 1:
        parser.error("--factor must be positive")
    outputs = build_outputs(args.sidecar, args.slug, args.factor)
    if args.check:
        mismatches = [
            name
            for name, data in outputs.items()
            if not (args.output / name).is_file()
            or (args.output / name).read_bytes() != data
        ]
        if mismatches:
            raise SystemExit("routing bundle differs: " + ", ".join(mismatches))
        print(f"verified {len(outputs)} deterministic routing artifacts")
        return 0
    args.output.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (args.output / name).write_bytes(data)
        print(f"{name} {sha256(data)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
