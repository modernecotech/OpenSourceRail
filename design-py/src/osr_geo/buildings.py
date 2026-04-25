"""Overture Buildings — building-density layer for catching new suburbs.

Overture Maps' *buildings* theme (CDLA-Permissive 2.0) is a unified
release of ML-extracted footprints (Microsoft Buildings, Google Open
Buildings) plus OSM. Coverage is markedly denser than OSM alone in the
developing world — recently-built suburbs in Baghdad, Lagos, Karachi
appear here months before they get hand-tagged in OSM.

We use it as a *demand* signal, not as buildable cost: building density
tells the planner "this is a populated place" even when OSM POIs and
WorldPop aren't quite caught up. Buildings are aggregated to a coarse
grid server-side via DuckDB to keep result sizes small (a Baghdad-sized
bbox returns ~1 M raw rows; 200 m server-side bins cut that to <2 k).
"""

from __future__ import annotations

import logging
import math
from pathlib import Path

import numpy as np

from osr_geo.overture import OVERTURE_RELEASE

log = logging.getLogger(__name__)


OVERTURE_BUILDINGS_S3 = (
    f"s3://overturemaps-us-west-2/release/{OVERTURE_RELEASE}/"
    "theme=buildings/type=building/*"
)


def fetch_building_density_layer(
    bbox_south: float, bbox_west: float, bbox_north: float, bbox_east: float,
    cell_m: float,
    *,
    server_bin_m: float = 200.0,
    sigma_cells: float | None = None,
) -> np.ndarray | None:
    """Return a building-density raster aligned to the same grid that
    `rasterize_city` will build for this bbox + `cell_m`.

    Returns None on failure (DuckDB missing, network error, empty bbox)
    so callers can fall back gracefully.
    """
    try:
        import duckdb
    except ImportError:
        log.warning("duckdb not installed — skipping Overture Buildings")
        return None

    lat0 = (bbox_south + bbox_north) / 2.0
    m_per_deg_lat = 111_132.0
    m_per_deg_lon = 111_320.0 * math.cos(math.radians(lat0))

    width_m = (bbox_east - bbox_west) * m_per_deg_lon
    height_m = (bbox_north - bbox_south) * m_per_deg_lat
    width_cells = max(1, int(math.ceil(width_m / cell_m)))
    height_cells = max(1, int(math.ceil(height_m / cell_m)))

    # Server-side bin edges in degrees so DuckDB can group cheaply.
    dlat = server_bin_m / m_per_deg_lat
    dlon = server_bin_m / m_per_deg_lon

    con = duckdb.connect()
    try:
        con.execute("INSTALL httpfs; LOAD httpfs;")
        con.execute("SET s3_region='us-west-2';")
        # FLOOR((bbox.ymin - south)/dlat) gives the bin index. Counting per
        # bin keeps the result set tiny regardless of city size.
        sql = f"""
            SELECT
                CAST(FLOOR((bbox.ymin - {bbox_south}) / {dlat}) AS INTEGER) AS bin_lat,
                CAST(FLOOR((bbox.xmin - {bbox_west}) / {dlon}) AS INTEGER) AS bin_lon,
                COUNT(*) AS n
            FROM read_parquet('{OVERTURE_BUILDINGS_S3}', filename=true,
                              hive_partitioning=1)
            WHERE bbox.xmin >= {bbox_west}
              AND bbox.xmax <= {bbox_east}
              AND bbox.ymin >= {bbox_south}
              AND bbox.ymax <= {bbox_north}
            GROUP BY bin_lat, bin_lon
        """
        rows = con.execute(sql).fetchall()
    except Exception as e:  # noqa: BLE001
        log.warning("Overture Buildings query failed: %s", e)
        return None
    finally:
        con.close()

    if not rows:
        log.info("Overture Buildings: 0 rows for bbox")
        return None

    # Coarse grid sized in server_bin_m units.
    coarse_h = max(1, int(math.ceil(height_m / server_bin_m)))
    coarse_w = max(1, int(math.ceil(width_m / server_bin_m)))
    coarse = np.zeros((coarse_h, coarse_w), dtype=np.float32)
    total = 0
    for bin_lat, bin_lon, n in rows:
        # bin_lat is south-up; numpy rows are north-down. Flip.
        if bin_lat is None or bin_lon is None:
            continue
        if not (0 <= bin_lat < coarse_h and 0 <= bin_lon < coarse_w):
            continue
        row = coarse_h - 1 - int(bin_lat)
        coarse[row, int(bin_lon)] = float(n)
        total += int(n)
    log.info(
        "Overture Buildings: %d buildings across %d bins (%dx%d @ %.0fm)",
        total, len(rows), coarse_h, coarse_w, server_bin_m,
    )

    # Upsample to the fine grid via nearest-neighbour (the layer is later
    # blurred so block artefacts vanish).
    upsample = max(1, int(round(server_bin_m / cell_m)))
    fine = np.kron(coarse, np.ones((upsample, upsample), dtype=np.float32))
    fine = fine[:height_cells, :width_cells]
    if fine.shape != (height_cells, width_cells):
        # Pad if rounding left a sliver short.
        pad_h = height_cells - fine.shape[0]
        pad_w = width_cells - fine.shape[1]
        fine = np.pad(fine, ((0, max(0, pad_h)), (0, max(0, pad_w))),
                      mode="edge")[:height_cells, :width_cells]

    # log1p compression + Gaussian blur + normalise. Same shape as the
    # WorldPop-derived layer so the demand blender treats them alike.
    fine = np.log1p(fine, dtype=np.float32)
    if sigma_cells is None:
        # Soften by one server-bin so adjacent populated bins merge.
        sigma_cells = server_bin_m / cell_m
    if sigma_cells > 0.5:
        fine = _gaussian_blur(fine, float(sigma_cells))
    peak = float(fine.max())
    if peak > 0:
        fine /= peak
    return fine.astype(np.float32)


def _gaussian_blur(arr: np.ndarray, sigma: float) -> np.ndarray:
    """Separable 1D Gaussian blur. No scipy dependency."""
    radius = max(1, int(math.ceil(3.0 * sigma)))
    xs = np.arange(-radius, radius + 1, dtype=np.float32)
    kernel = np.exp(-(xs * xs) / (2.0 * sigma * sigma))
    kernel /= kernel.sum()
    out = np.apply_along_axis(
        lambda v: np.convolve(v, kernel, mode="same"), 0, arr.astype(np.float32),
    )
    out = np.apply_along_axis(
        lambda v: np.convolve(v, kernel, mode="same"), 1, out,
    )
    return out
