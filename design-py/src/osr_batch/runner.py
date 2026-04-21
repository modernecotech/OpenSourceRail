"""Run the OSR design pipeline over a list of cities.

Pipeline per city:
    1. osr_osm.fetch_city          (cache-aware Overpass pull)
    2. osr_geo.rasterize_city      (numpy rasters + sidecar)
    3. osr_geo.save_grid           (write rasters + grid.json)
    4. osr-design (Rust CLI)       (solve + emit design.toml/geojson/quality.yaml)

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

from osr_geo.rasterize import rasterize_city, save_grid
from osr_osm.fetcher import BBox, fetch_city

log = logging.getLogger(__name__)


@dataclass
class CityInput:
    slug: str
    country: str
    continent: str
    population: int
    bbox: BBox
    climate: str | None = None
    profile: str | None = None


def load_cities(path: Path) -> list[CityInput]:
    raw = tomllib.loads(path.read_text())
    cities: list[CityInput] = []
    for c in raw.get("cities", []):
        b = c["bbox"]
        cities.append(
            CityInput(
                slug=c["slug"],
                country=c["country"],
                continent=c.get("continent", "unknown"),
                population=c["population"],
                bbox=BBox(south=b["south"], west=b["west"], north=b["north"], east=b["east"]),
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
    raster_cache.mkdir(parents=True, exist_ok=True)

    # 1 + 2. OSM pull + rasterize.
    city_osm = fetch_city(city.bbox, city.slug, cache_dir=osm_cache)
    bundle = rasterize_city(city_osm, cell_m=cell_m)

    # 3. Save rasters. The sidecar file path is what Rust consumes.
    paths = save_grid(bundle, raster_cache, city.slug)

    # 4. Rust CLI.
    out_dir = out_root / city.continent / city.country.lower() / city.slug
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
