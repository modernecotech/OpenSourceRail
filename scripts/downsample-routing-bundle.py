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
    cost = read_f32(cost_path, cells)
    demand = read_f32(demand_path, cells)
    buildability = buildability_path.read_bytes()
    if len(buildability) != cells:
        raise ValueError(
            f"{buildability_path}: expected {cells} bytes, found {len(buildability)}"
        )

    out_height = math.ceil(height / factor)
    out_width = math.ceil(width / factor)
    out_cost: list[float] = []
    out_demand: list[float] = []
    out_buildability = bytearray()
    for out_row in range(out_height):
        row_start = out_row * factor
        row_end = min(row_start + factor, height)
        for out_col in range(out_width):
            col_start = out_col * factor
            col_end = min(col_start + factor, width)
            buildable_costs: list[float] = []
            maximum_demand = 0.0
            for row in range(row_start, row_end):
                offset = row * width
                for col in range(col_start, col_end):
                    index = offset + col
                    maximum_demand = max(maximum_demand, demand[index])
                    if buildability[index] and math.isfinite(cost[index]):
                        buildable_costs.append(cost[index])
            if buildable_costs:
                out_buildability.append(1)
                out_cost.append(min(buildable_costs))
            else:
                out_buildability.append(0)
                out_cost.append(math.inf)
            out_demand.append(maximum_demand)

    out_cell_m = float(source_grid["cell_m"]) * factor
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
    anchors = json.loads(anchors_path.read_text())
    for anchor in anchors:
        anchor["row"] = min(int(anchor["row"]) // factor, out_height - 1)
        anchor["col"] = min(int(anchor["col"]) // factor, out_width - 1)
    anchors.sort(key=lambda item: (item["id"], item["row"], item["col"]))
    upstream = {
        path.name: sha256(path.read_bytes())
        for path in [sidecar_path, cost_path, demand_path, buildability_path, anchors_path]
    }
    provenance = {
        "schema_version": 1,
        "generator": "scripts/downsample-routing-bundle.py",
        "factor": factor,
        "aggregation": {
            "buildability": "any-buildable-cell",
            "cost": "minimum-buildable-cost",
            "demand": "maximum-demand",
        },
        "upstream_sha256": upstream,
    }
    return {
        f"{slug}.grid.json": json_bytes(compact_sidecar),
        f"{slug}.cost.npy": encode_f32(out_cost),
        f"{slug}.demand.npy": encode_f32(out_demand),
        f"{slug}.buildability.npy": bytes(out_buildability),
        f"{slug}.anchors.json": json_bytes(anchors),
        f"{slug}.routing-provenance.json": json_bytes(provenance),
    }


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
