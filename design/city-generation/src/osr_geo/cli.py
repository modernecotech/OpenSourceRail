"""CLI: rasterize a previously cached city OSM dump.

Usage:
    osr-geo-rasterize --slug samawah \
                      --osm-json cache/samawah.osm.json \
                      --out-dir cache/rasters \
                      --cell-m 20 \
                      --country IQ
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from pathlib import Path

from osr_osm.fetcher import BBox, CityOSM

from .rasterize import DEMAND_RADIUS_M, rasterize_city, save_grid
from .terrain import sample_elevation_grid

log = logging.getLogger(__name__)


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
    ap.add_argument(
        "--country",
        default=None,
        help=(
            "ISO-2 country code for fetching the WorldPop population "
            "raster. When set, the demand surface includes a smoothed "
            "residential-population layer (RFC 0003 demand-blend) so "
            "lines reach population centres that have no mapped POI."
        ),
    )
    ap.add_argument(
        "--terrain-cache-dir",
        type=Path,
        default=Path.home() / ".cache" / "osr-pipeline" / "terrain",
        help="cache for source-locked open Skadi/SRTM elevation tiles",
    )
    ap.add_argument(
        "--no-terrain",
        action="store_true",
        help="omit the optional open elevation layer (water is still emitted)",
    )
    ap.add_argument(
        "--pop-cache-dir",
        type=Path,
        default=Path.home() / ".cache" / "osr-pipeline" / "population",
        help="WorldPop raster cache directory.",
    )
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    city = _load_city(args.osm_json)
    elevation_layer = None
    terrain_provenance = None
    if not args.no_terrain:
        # Build the same grid dimensions as rasterize_city so the DEM stays
        # byte-for-byte aligned with cost, demand and water.
        lat0 = (city.bbox.south + city.bbox.north) / 2
        width = max(
            1,
            math.ceil(
                (city.bbox.east - city.bbox.west)
                * 111_320.0
                * math.cos(math.radians(lat0))
                / args.cell_m
            ),
        )
        height = max(
            1,
            math.ceil(
                (city.bbox.north - city.bbox.south) * 111_132.0 / args.cell_m
            ),
        )
        terrain = sample_elevation_grid(
            city.bbox, height, width, args.terrain_cache_dir
        )
        elevation_layer = terrain.elevation_m
        terrain_provenance = terrain.provenance
    bundle = rasterize_city(
        city,
        cell_m=args.cell_m,
        country=args.country,
        pop_cache_dir=args.pop_cache_dir,
        elevation_layer=elevation_layer,
        terrain_provenance=terrain_provenance,
    )
    print(bundle.summary(), file=sys.stderr)
    paths = save_grid(bundle, args.out_dir, args.slug)
    for k, p in paths.items():
        print(f"{k:14s} {p}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
