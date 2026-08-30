"""Overture Places — supplemental POI anchors for sparse-OSM regions.

Overture Maps is a Linux-Foundation-hosted release of harmonised
basemap data backed by Meta, Microsoft, Amazon and TomTom. The
*places* theme (CDLA-Permissive 2.0) is denser than OSM in much of
the developing world — Iraq, Pakistan, Bangladesh, sub-Saharan Africa
in particular — because it merges Meta's social-graph-derived POIs
with the operator partners' commercial datasets.

We use DuckDB's `httpfs` extension to query the public S3 release
per bounding box, returning rows that look enough like our existing
OSM anchor schema to be merged in directly. No Overture-specific data
is cached on disk; the bbox queries hit the live release each run.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any


def _stable_i64(s: str) -> int:
    """Deterministic i64 derived from a string. Used to fit Overture's
    UUID-style IDs into the integer-id schema the Rust loader expects.
    Negative values are reserved for non-OSM origins so they never
    collide with positive OSM ids."""
    h = hashlib.blake2b(s.encode("utf-8"), digest_size=8).digest()
    n = int.from_bytes(h, "big", signed=True)
    return -abs(n) if n != 0 else -1

log = logging.getLogger(__name__)


# Pinned release path. Update when bumping; old releases stay available
# for ~6 months after a new one is cut so a stale value still works.
OVERTURE_RELEASE = "2026-04-15.0"
OVERTURE_PLACES_S3 = (
    f"s3://overturemaps-us-west-2/release/{OVERTURE_RELEASE}/theme=places/type=place/*"
)


# Map Overture's place categories onto the same kind/weight scheme our
# OSM anchors use. Anything not matched here is dropped — Overture has
# >2000 fine-grained categories and most are noise (gas-station-brand
# subtypes, individual restaurants) that would oversaturate the demand
# grid if all wired in.
_CAT_TO_KIND_WEIGHT: dict[str, tuple[str, float]] = {
    "education":               ("amenity:university", 0.9),
    "school":                  ("amenity:school", 0.6),
    "university":              ("amenity:university", 1.0),
    "college":                 ("amenity:university", 0.85),
    "hospital":                ("amenity:hospital", 1.0),
    "medical_clinic":          ("amenity:clinic", 0.5),
    "shopping_mall":           ("shop:mall", 0.9),
    "market":                  ("shop:market", 0.7),
    "supermarket":             ("shop:supermarket", 0.5),
    "park":                    ("leisure:park", 0.4),
    "stadium":                 ("leisure:stadium", 0.7),
    "transportation":          ("public_transport:hub", 0.8),
    "airport":                 ("aeroway:aerodrome", 1.0),
    "train_station":           ("railway:station", 1.0),
    "bus_station":             ("amenity:bus_station", 0.7),
    "government":              ("amenity:government", 0.6),
    "place_of_worship":        ("amenity:place_of_worship", 0.4),
    "mosque":                  ("amenity:place_of_worship", 0.4),
    "church":                  ("amenity:place_of_worship", 0.4),
    "library":                 ("amenity:library", 0.5),
}


def fetch_overture_anchors(
    bbox_south: float, bbox_west: float, bbox_north: float, bbox_east: float,
    *, cache_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Query Overture Places for the bbox; return OSM-shaped anchor dicts.

    Best-effort: a network failure or DuckDB error returns an empty
    list and logs a warning. Callers should treat it as a *booster*
    on top of OSM, not a replacement.
    """
    try:
        import duckdb
    except ImportError:
        log.warning("duckdb not installed — skipping Overture")
        return []

    con = duckdb.connect()
    try:
        con.execute("INSTALL httpfs; LOAD httpfs;")
        # us-west-2 is the public Overture region; no creds needed.
        con.execute("SET s3_region='us-west-2';")
        # The places parquet has a struct column `categories` with
        # `primary` (string) and `alternate` (string[]). bbox is also
        # a struct; we filter on its xmin/ymin/xmax/ymax components.
        sql = f"""
            SELECT
                id,
                names.primary AS name,
                categories.primary AS category,
                ST_X(geometry) AS lon,
                ST_Y(geometry) AS lat
            FROM read_parquet('{OVERTURE_PLACES_S3}', filename=true,
                              hive_partitioning=1)
            WHERE bbox.xmin >= {bbox_west}
              AND bbox.xmax <= {bbox_east}
              AND bbox.ymin >= {bbox_south}
              AND bbox.ymax <= {bbox_north}
              AND categories.primary IS NOT NULL
        """
        # Spatial functions need the spatial extension.
        try:
            con.execute("INSTALL spatial; LOAD spatial;")
        except Exception:  # noqa: BLE001
            # If spatial isn't available, fall back to the bbox struct only.
            sql = sql.replace("ST_X(geometry) AS lon,", "")
            sql = sql.replace("ST_Y(geometry) AS lat", "")
            sql = sql.replace("SELECT\n",
                              "SELECT\n                bbox.xmin AS lon,\n                bbox.ymin AS lat,\n")
        rows = con.execute(sql).fetchall()
    except Exception as e:  # noqa: BLE001
        log.warning("Overture query failed: %s", e)
        return []
    finally:
        con.close()

    anchors: list[dict[str, Any]] = []
    for row in rows:
        oid, name, category, lon, lat = row
        if category is None:
            continue
        mapped = _CAT_TO_KIND_WEIGHT.get(category)
        if mapped is None:
            continue
        kind, weight = mapped
        anchors.append({
            "id": _stable_i64(f"overture:{oid}"),
            "kind": kind,
            "weight": weight,
            "name": name,
            "lat": float(lat),
            "lon": float(lon),
        })
    log.info("Overture: %d anchors after filtering", len(anchors))
    return anchors


def merge_anchors(
    osm_anchors: list[dict[str, Any]],
    overture_anchors: list[dict[str, Any]],
    *,
    dedup_radius_m: float = 80.0,
) -> list[dict[str, Any]]:
    """Merge Overture anchors into OSM anchors, dropping Overture rows
    that sit within `dedup_radius_m` of an existing OSM anchor of the
    same kind. The OSM entry wins (it has the OSM id and tags).
    """
    if not overture_anchors:
        return osm_anchors
    import math
    R = 6371000.0
    PI = math.pi / 180.0

    def hav(la1: float, lo1: float, la2: float, lo2: float) -> float:
        dlat = (la2 - la1) * PI
        dlon = (lo2 - lo1) * PI
        midlat = ((la1 + la2) * 0.5) * PI
        return math.hypot(R * dlat, R * math.cos(midlat) * dlon)

    # Bucket existing anchors by 0.01° (~1 km) cell so the dedup pass is O(n).
    buckets: dict[tuple[int, int, str], list[dict[str, Any]]] = {}
    for a in osm_anchors:
        key = (int(a["lat"] * 100), int(a["lon"] * 100), a["kind"])
        buckets.setdefault(key, []).append(a)

    merged = list(osm_anchors)
    for o in overture_anchors:
        key = (int(o["lat"] * 100), int(o["lon"] * 100), o["kind"])
        # Check a 3×3 neighbourhood of buckets for duplicates.
        is_dup = False
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                k2 = (key[0] + dr, key[1] + dc, key[2])
                for cand in buckets.get(k2, ()):
                    if hav(o["lat"], o["lon"], cand["lat"], cand["lon"]) <= dedup_radius_m:
                        is_dup = True
                        break
                if is_dup:
                    break
            if is_dup:
                break
        if not is_dup:
            merged.append(o)
    return merged
