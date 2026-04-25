"""Run the OSR design pipeline over a list of cities.

Pipeline per city:
    1. osr_osm.fetch_city          (cache-aware Overpass pull)
    2. osr_geo.rasterize_city      (numpy rasters + sidecar)
    3. osr_geo.save_grid           (write rasters + grid.json)
    4. osr-design (Rust CLI)       (solve + emit design.toml/geojson/quality.yaml)
    5. osr_scenario.render_map     (OSM-backed PNG of the network on a basemap)

Outputs land under `out_root/{continent}/{country}/{slug}/`. A batch-level
`summary.csv` is written with one row per city covering headline quality
metrics — the single file an operator scans to find failing designs.
"""

from __future__ import annotations

import csv
import logging
import os
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from osr_geo.buildings import fetch_building_density_layer
from osr_geo.overture import fetch_overture_anchors, merge_anchors
from osr_geo.population import (
    fetch_population_raster,
    population_demand_layer,
    sample_population_into_grid,
)
from osr_geo.rasterize import (
    DEFAULT_CELL_M,
    DEMAND_RADIUS_M,
    filter_anchors_by_population,
    rasterize_city,
    save_grid,
)
from osr_osm.fetcher import BBox, fetch_city

log = logging.getLogger(__name__)


_COUNTRY_NAME = {
    "IQ": "Iraq",
}


@dataclass
class CityInput:
    slug: str
    country: str
    region: str
    population: int
    bbox: BBox
    climate: str | None = None
    profile: str | None = None

    @property
    def country_name(self) -> str:
        return _COUNTRY_NAME.get(self.country.upper(), self.country.upper())

    @property
    def city_name(self) -> str:
        return self.slug.replace("-", " ").replace("_", " ").title()


def _radius_km_for_population(pop: int) -> float:
    """Half-bbox-width in km that should comfortably enclose a city of
    the given population.

    Population-band density model — small cities sprawl at low density,
    big-but-not-mega cities pack tighter, megacities sprawl back out
    again because of their ring of *satellite towns* (Baghdad's Abu Ghraib /
    Taji / Basmaya, Cairo's 6th of October / New Capital, Lagos's Ibeju,
    etc.). The metro is meant to *connect* those satellites — so the bbox
    has to capture them even though the contiguous urban core is much
    smaller.

        ≤ 500k:  3500 ppl/km² (mid-city, low-rise residential)
        ≤ 3M:    7500 ppl/km² (large city with mixed mid/high-rise)
        > 3M:    4000 ppl/km² (megacity urban core + satellite ring)

    20 % buffer beyond the implied square half-width so anchors can sit
    in transition zones rather than right on the urban edge.

    Population →  bbox half-width
        100k       5.0 km
        400k       8.5 km
        1M         8.7 km
        3M        15.1 km
        7.5M      32.7 km
       15M        46.2 km
    """
    import math as _m
    if pop <= 500_000:
        density = 3500.0
    elif pop <= 3_000_000:
        density = 7500.0
    else:
        density = 4000.0
    area_km2 = pop / density
    r = _m.sqrt(area_km2 / 4.0)
    return r * 1.2


def _expanded_bbox(bbox: BBox, pop: int) -> BBox:
    """Expand a hand-set bbox if it is smaller than the population
    would warrant. Never shrinks an already-large bbox."""
    centre_lat = (bbox.south + bbox.north) / 2
    centre_lon = (bbox.west + bbox.east) / 2
    needed_km = _radius_km_for_population(pop)
    needed_dlat = needed_km / 111.0
    import math as _m
    needed_dlon = needed_km / (111.0 * _m.cos(_m.radians(centre_lat)))
    cur_dlat = (bbox.north - bbox.south) / 2
    cur_dlon = (bbox.east - bbox.west) / 2
    new_dlat = max(cur_dlat, needed_dlat)
    new_dlon = max(cur_dlon, needed_dlon)
    return BBox(
        south=centre_lat - new_dlat,
        north=centre_lat + new_dlat,
        west=centre_lon - new_dlon,
        east=centre_lon + new_dlon,
    )


def load_cities(path: Path) -> list[CityInput]:
    raw = tomllib.loads(path.read_text())
    cities: list[CityInput] = []
    for c in raw.get("cities", []):
        b = c["bbox"]
        bbox = BBox(south=b["south"], west=b["west"], north=b["north"], east=b["east"])
        # Auto-expand small hand-set bboxes so they actually cover the
        # urban + suburban footprint of the city. Operators can always
        # override by supplying an already-large bbox.
        bbox = _expanded_bbox(bbox, int(c["population"]))
        cities.append(
            CityInput(
                slug=c["slug"],
                country=c["country"],
                region=c.get("region") or c.get("continent", "unknown"),
                population=c["population"],
                bbox=bbox,
                climate=c.get("climate"),
                profile=c.get("profile"),
            )
        )
    return cities


def run_one(
    city: CityInput,
    cache_root: Path,
    out_root: Path,
    osr_design_bin: Path,
    cell_m: float = 20.0,
) -> dict[str, Any]:
    """Process one city; return a summary row."""
    log.info("=== %s (%s, pop %d) ===", city.slug, city.country, city.population)

    osm_cache = cache_root / "osm"
    raster_cache = cache_root / "rasters"
    pop_cache = cache_root / "population"
    raster_cache.mkdir(parents=True, exist_ok=True)

    # 1 + 2. OSM pull + (optional) population raster + rasterize.
    city_osm = fetch_city(city.bbox, city.slug, cache_dir=osm_cache)

    # Overture Places booster — denser than OSM in much of the
    # developing world. Best-effort; on network/library failure the
    # batch continues with OSM-only anchors.
    try:
        overture_anchors = fetch_overture_anchors(
            city.bbox.south, city.bbox.west,
            city.bbox.north, city.bbox.east,
        )
        if overture_anchors:
            before = len(city_osm.anchors)
            city_osm.anchors = merge_anchors(city_osm.anchors, overture_anchors)
            log.info(
                "anchors: OSM=%d, +Overture=%d → merged=%d",
                before, len(overture_anchors), len(city_osm.anchors),
            )
    except Exception as e:  # noqa: BLE001
        log.warning("Overture step failed for %s: %s", city.slug, e)

    # Population layer: WorldPop constrained 2020. ~14 MB per country,
    # cached on disk so repeat city runs in the same country reuse it.
    # If the country has no mapping or the download fails, we fall
    # back gracefully to anchor-only demand.
    pop_layer = None
    pop_path = fetch_population_raster(city.country, pop_cache)
    if pop_path is not None:
        try:
            # Compute bbox dims that match what rasterize_city will use.
            # We pass the same bbox so the destination grid lines up.
            import math as _m
            lat0 = (city.bbox.south + city.bbox.north) / 2
            m_per_deg_lat = 111_132.0
            m_per_deg_lon = 111_320.0 * _m.cos(_m.radians(lat0))
            width_m = (city.bbox.east - city.bbox.west) * m_per_deg_lon
            height_m = (city.bbox.north - city.bbox.south) * m_per_deg_lat
            width = max(1, int(_m.ceil(width_m / cell_m)))
            height = max(1, int(_m.ceil(height_m / cell_m)))

            pop_raw = sample_population_into_grid(
                pop_path,
                city.bbox.south, city.bbox.west,
                city.bbox.north, city.bbox.east,
                height, width,
            )
            sigma_cells = DEMAND_RADIUS_M / cell_m
            pop_layer = population_demand_layer(pop_raw, sigma_cells)
            log.info(
                "population layer: %d×%d, peak=%.3f, mean=%.3f",
                pop_layer.shape[0], pop_layer.shape[1],
                float(pop_layer.max()), float(pop_layer.mean()),
            )
        except Exception as e:  # noqa: BLE001
            log.warning("pop layer build failed for %s: %s", city.slug, e)
            pop_layer = None

    # Building-density layer (Overture Buildings). ML-extracted footprints
    # are denser and more current than OSM in the developing world — they
    # pick up new suburbs that haven't been hand-tagged. Combined with the
    # population layer via element-wise max so either signal can flag a
    # populated block; the anchor filter then runs against the *combined*
    # layer so a new-construction anchor (low WorldPop, high buildings)
    # survives, while a rural farm (low pop, low buildings) gets dropped.
    try:
        building_layer = fetch_building_density_layer(
            city.bbox.south, city.bbox.west,
            city.bbox.north, city.bbox.east,
            cell_m=cell_m,
        )
        if building_layer is not None:
            if pop_layer is not None and pop_layer.shape == building_layer.shape:
                pop_layer = np.maximum(pop_layer, building_layer)
                log.info(
                    "demand layer: pop ⊕ buildings, peak=%.3f, mean=%.3f",
                    float(pop_layer.max()), float(pop_layer.mean()),
                )
            else:
                pop_layer = building_layer
                log.info(
                    "demand layer: buildings only, peak=%.3f, mean=%.3f",
                    float(pop_layer.max()), float(pop_layer.mean()),
                )
    except Exception as e:  # noqa: BLE001
        log.warning("building layer build failed for %s: %s", city.slug, e)

    # Drop anchors whose combined-layer neighbourhood is essentially empty
    # — these are farms / scattered rural POIs that the auto-expanded
    # bbox swept up. The threshold runs against the combined pop+buildings
    # layer so genuine new-suburb anchors (no WorldPop, fresh buildings)
    # survive.
    if pop_layer is not None:
        before = len(city_osm.anchors)
        city_osm.anchors = filter_anchors_by_population(
            city_osm.anchors, pop_layer, city.bbox, cell_m,
            threshold=0.10,
        )
        log.info(
            "anchor demand filter: %d → %d (dropped %d rural-noise)",
            before, len(city_osm.anchors), before - len(city_osm.anchors),
        )

    bundle = rasterize_city(city_osm, cell_m=cell_m, population_layer=pop_layer)

    # 3. Save rasters. The sidecar file path is what Rust consumes.
    paths = save_grid(bundle, raster_cache, city.slug)

    # 4. Rust CLI.
    out_dir = out_root / city.region / city.country_name / city.city_name
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(osr_design_bin),
        "--sidecar", str(paths["grid"]),
        "--slug", city.slug,
        "--population", str(city.population),
        "--country", city.country,
        "--out-dir", str(out_dir),
    ]
    if city.climate:
        cmd += ["--climate", city.climate]
    if city.profile:
        cmd += ["--profile", city.profile]

    res = subprocess.run(cmd, capture_output=True, text=True)
    log.info("osr-design stdout: %s", res.stdout.strip())
    if res.returncode != 0:
        log.error("osr-design failed for %s: %s", city.slug, res.stderr.strip())
        return _fail_row(city, res.stderr.strip() or res.stdout.strip())

    # 5. Render the OSM-backed network map PNG. Best-effort: a render
    # failure shouldn't fail the whole city — the design.toml is still
    # valid and downstream tools (diagnose, scenario, sim) keep working.
    try:
        from osr_scenario.render_map import render_city
        render_city(out_dir / "design.toml", out_dir)
    except Exception as e:  # noqa: BLE001
        log.warning("render_map failed for %s: %s", city.slug, e)

    # Parse quality file.
    quality_path = out_dir / f"{city.slug}.design-quality.yaml"
    row = _parse_quality(city, out_dir, quality_path, city_osm.summary(), bundle.summary())
    return row


def run_batch(
    cities_toml: Path,
    cache_root: Path,
    out_root: Path,
    osr_design_bin: Path,
    cell_m: float = 20.0,
    summary_csv: Path | None = None,
    only: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    cities = load_cities(cities_toml)
    if only:
        only_set = set(only)
        cities = [c for c in cities if c.slug in only_set]
    if not cities:
        log.warning("no cities selected")
        return []

    rows: list[dict[str, Any]] = []
    for c in cities:
        try:
            rows.append(run_one(c, cache_root, out_root, osr_design_bin, cell_m))
        except Exception as e:  # noqa: BLE001 — batch must continue
            log.exception("unhandled error on %s", c.slug)
            rows.append(_fail_row(c, f"exception: {e}"))

    if summary_csv:
        _write_summary(summary_csv, rows)
        log.info("wrote summary: %s", summary_csv)
    return rows


# ---- Helpers ---------------------------------------------------------

_QUALITY_FLOAT = re.compile(r"^\s*(\w+):\s*([0-9]+(?:\.[0-9]+)?)\s*$")
_QUALITY_BOOL = re.compile(r"^\s*(\w+):\s*(true|false)\s*$")


def _parse_quality(
    city: CityInput, out_dir: Path, quality_path: Path, osm_summary: str, raster_summary: str
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "slug": city.slug,
        "country": city.country,
        "population": city.population,
        "out_dir": str(out_dir),
        "osm_summary": osm_summary,
        "raster_summary": raster_summary,
    }
    if not quality_path.exists():
        row["pass"] = False
        row["error"] = "no quality file"
        return row

    text = quality_path.read_text()
    # Cheap line-by-line extraction (avoids a yaml dependency).
    for line in text.splitlines():
        mf = _QUALITY_FLOAT.match(line)
        if mf and mf.group(1) in {
            "total_route_m",
            "n_lines",
            "n_stations",
            "anchor_hit_rate",
            "high_demand_coverage",
        }:
            row[mf.group(1)] = float(mf.group(2))
            continue
        mb = _QUALITY_BOOL.match(line)
        if mb and mb.group(1) == "pass":
            row["pass"] = mb.group(2) == "true"
    row.setdefault("pass", False)
    return row


def _fail_row(city: CityInput, err: str) -> dict[str, Any]:
    return {
        "slug": city.slug,
        "country": city.country,
        "population": city.population,
        "pass": False,
        "error": err,
    }


_SUMMARY_FIELDS = [
    "slug",
    "country",
    "population",
    "pass",
    "n_lines",
    "n_stations",
    "total_route_m",
    "anchor_hit_rate",
    "high_demand_coverage",
    "out_dir",
    "error",
]


def _write_summary(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_SUMMARY_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
