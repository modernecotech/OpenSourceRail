"""CLI: rasterize a previously cached city OSM dump.

Usage:
    osr-geo-rasterize --slug samawah \
                      --osm-json cache/samawah.osm.json \
                      --out-dir cache/rasters \
                      --cell-m 20
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from osr_osm.fetcher import BBox, CityOSM

from .rasterize import rasterize_city, save_grid


def _load_city(path: Path) -> CityOSM:
    """Deserialize a CityOSM dict (produced by osr_osm.cli) back to an object."""
    raw = json.loads(path.read_text())
    bbox = BBox(**raw["bbox"])
    return CityOSM(
        bbox=bbox,
        slug=raw["slug"],
        fetched_at=raw["fetched_at"],
        arterials=raw.get("arterials", []),
        buildings=raw.get("buildings", []),
        water=raw.get("water", []),
        protected=raw.get("protected", []),
        anchors=raw.get("anchors", []),
        rail_existing=raw.get("rail_existing", []),
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Rasterize an OSM city pull into cost/demand/buildability grids.")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--osm-json", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--cell-m", type=float, default=20.0, help="Cell size in metres.")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    city = _load_city(args.osm_json)
    bundle = rasterize_city(city, cell_m=args.cell_m)
    print(bundle.summary(), file=sys.stderr)
    paths = save_grid(bundle, args.out_dir, args.slug)
    for k, p in paths.items():
        print(f"{k:14s} {p}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
