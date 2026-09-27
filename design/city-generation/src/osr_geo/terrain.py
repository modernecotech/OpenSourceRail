"""Open elevation data for planning-level terrain screening.

The source is the public ``elevation-tiles-prod`` Terrain Tiles bucket in
Skadi/HGT form.  Skadi tiles are one-degree EPSG:4326 grids of signed,
big-endian 16-bit elevations.  The files are cached verbatim and their
SHA-256 digests are carried into the routing-bundle provenance.

This is deliberately a planning input, not a surveyed ground model.  It is
good enough to steer a city-scale route away from steep ground and to flag
likely elevated works; detailed vertical alignment still needs controlled
survey evidence.
"""

from __future__ import annotations

import gzip
import hashlib
import math
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from osr_osm.fetcher import BBox

TERRAIN_DATASET = "AWS Open Data Terrain Tiles (Skadi/SRTM)"
TERRAIN_BASE_URL = "https://elevation-tiles-prod.s3.amazonaws.com/skadi"
HGT_SAMPLES = 3601
HGT_VOID = -32768
MAX_TILE_BYTES = HGT_SAMPLES * HGT_SAMPLES * 2


@dataclass(frozen=True)
class TerrainSample:
    elevation_m: np.ndarray
    provenance: dict[str, Any]


def _tile_name(lat: int, lon: int) -> str:
    return f"{'N' if lat >= 0 else 'S'}{abs(lat):02d}{'E' if lon >= 0 else 'W'}{abs(lon):03d}"


def _download_tile(lat: int, lon: int, cache_dir: Path) -> tuple[np.ndarray, dict[str, str]]:
    name = _tile_name(lat, lon)
    directory = cache_dir / name[:3]
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.hgt.gz"
    url = f"{TERRAIN_BASE_URL}/{name[:3]}/{name}.hgt.gz"
    if not path.exists():
        request = urllib.request.Request(url, headers={"User-Agent": "OpenSourceRail/terrain-planner"})
        with urllib.request.urlopen(request, timeout=120) as response:
            compressed = response.read(MAX_TILE_BYTES)
        temporary = path.with_suffix(".tmp")
        temporary.write_bytes(compressed)
        temporary.replace(path)
    compressed = path.read_bytes()
    raw = gzip.decompress(compressed)
    if len(raw) != MAX_TILE_BYTES:
        raise ValueError(
            f"{path}: expected {MAX_TILE_BYTES} decompressed HGT bytes, found {len(raw)}"
        )
    tile = np.frombuffer(raw, dtype=">i2").reshape((HGT_SAMPLES, HGT_SAMPLES))
    return tile, {
        "tile": name,
        "url": url,
        "sha256": hashlib.sha256(compressed).hexdigest(),
    }


def sample_elevation_grid(
    bbox: BBox,
    height: int,
    width: int,
    cache_dir: Path,
) -> TerrainSample:
    """Sample open terrain at the centre of every OSR planning cell."""
    if height < 1 or width < 1:
        raise ValueError("terrain output dimensions must be positive")
    latitudes = bbox.north - (np.arange(height, dtype=np.float64) + 0.5) * (
        (bbox.north - bbox.south) / height
    )
    longitudes = bbox.west + (np.arange(width, dtype=np.float64) + 0.5) * (
        (bbox.east - bbox.west) / width
    )
    output = np.full((height, width), np.nan, dtype=np.float32)
    sources: list[dict[str, str]] = []
    north_tile = math.floor(np.nextafter(bbox.north, -math.inf))
    south_tile = math.floor(bbox.south)
    west_tile = math.floor(bbox.west)
    east_tile = math.floor(np.nextafter(bbox.east, -math.inf))
    for tile_lat in range(south_tile, north_tile + 1):
        row_indices = np.flatnonzero(
            (latitudes >= tile_lat) & (latitudes <= tile_lat + 1)
        )
        if row_indices.size == 0:
            continue
        for tile_lon in range(west_tile, east_tile + 1):
            col_indices = np.flatnonzero(
                (longitudes >= tile_lon) & (longitudes <= tile_lon + 1)
            )
            if col_indices.size == 0:
                continue
            tile, source = _download_tile(tile_lat, tile_lon, cache_dir)
            sources.append(source)
            # HGT row zero is north and column zero is west. Nearest-neighbour
            # sampling avoids inventing precision beyond the source DEM.
            rows = np.rint((tile_lat + 1 - latitudes[row_indices]) * (HGT_SAMPLES - 1))
            cols = np.rint((longitudes[col_indices] - tile_lon) * (HGT_SAMPLES - 1))
            values = tile[np.ix_(rows.astype(int), cols.astype(int))].astype(np.float32)
            values[values == HGT_VOID] = np.nan
            output[np.ix_(row_indices, col_indices)] = values
    if not np.isfinite(output).any():
        raise ValueError("open terrain tiles contain no usable elevations for the city grid")
    # Keep a missing sample explicit rather than silently treating it as sea
    # level. Slope generation below ignores these cells.
    sources.sort(key=lambda item: item["tile"])
    return TerrainSample(
        elevation_m=output,
        provenance={
            "dataset": TERRAIN_DATASET,
            "source": "NASA/NGA Shuttle Radar Topography Mission via AWS Open Data",
            "access": "https://registry.opendata.aws/terrain-tiles/",
            "format": "Skadi HGT, EPSG:4326, 1 arc-second",
            "planning_use_only": True,
            "tiles": sources,
        },
    )


def terrain_slope_percent(elevation_m: np.ndarray, cell_m: float) -> np.ndarray:
    """Return the maximum local ground slope as rise/run percent."""
    if elevation_m.ndim != 2 or cell_m <= 0:
        raise ValueError("terrain slope requires a 2D elevation grid and positive cell size")
    valid = np.isfinite(elevation_m)
    if not valid.any():
        return np.full(elevation_m.shape, np.nan, dtype=np.float32)
    # Fill isolated voids only for the derivative. They remain NaN in the
    # published elevation raster so source gaps stay visible to reviewers.
    fill = float(np.nanmedian(elevation_m))
    working = np.where(valid, elevation_m, fill).astype(np.float32)
    # SRTM's native sample spacing is about 30 m. Use at least a 60 m
    # baseline so a resampled 20 m routing grid does not interpret one-metre
    # DEM quantisation steps as repeated 5% cliffs.
    window = max(1, math.ceil(60.0 / cell_m))
    padded = np.pad(working, window, mode="edge")
    dy = (
        padded[2 * window :, window:-window]
        - padded[: -2 * window, window:-window]
    ) / (2.0 * window * cell_m)
    dx = (
        padded[window:-window, 2 * window :]
        - padded[window:-window, : -2 * window]
    ) / (2.0 * window * cell_m)
    slope = np.hypot(dx, dy) * 100.0
    slope[~valid] = np.nan
    return slope.astype(np.float32)
