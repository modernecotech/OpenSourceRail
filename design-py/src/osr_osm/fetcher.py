"""Overpass API fetcher with SHA256-keyed disk cache.

Design notes
------------
* Overpass rate-limits aggressively (2 slots, ~60s cooldown). The cache is
  not an optimization — it is what makes 500-city batches feasible at all.
* Cache keys hash the *query text*, not the bbox, so changes to tag groups
  invalidate automatically. No "oops stale schema" silent drift.
* No pandas / geopandas — responses are unwrapped into plain Python dicts
  with a tiny shape contract (see CityOSM). This keeps the cross-language
  boundary with the Rust solver trivial (JSON in, polylines out).
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import requests

log = logging.getLogger(__name__)

OVERPASS_ENDPOINTS = [
    # Failover order; first responsive wins. Keeping >1 means a stalled
    # primary does not break the pipeline.
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

# User-Agent identifies the tool — Overpass operators ask for this.
UA = "OpenSourceRail-design/0.1 (+https://github.com/OpenSourceRail/OpenSourceRail)"

# Per-request timeout. Overpass can legitimately take 30-90s on a busy city.
HTTP_TIMEOUT_S = 180

# Default cache location. Overridable per-call.
DEFAULT_CACHE = Path.home() / ".cache" / "osr-design" / "osm"


class OverpassError(RuntimeError):
    """Raised when every Overpass endpoint has been tried and failed."""


@dataclass(frozen=True)
class BBox:
    """Geographic bounding box, south-west + north-east corners.

    Overpass wants [south, west, north, east], so we store in that order
    to avoid reshuffling at every query site.
    """

    south: float
    west: float
    north: float
    east: float

    def as_overpass(self) -> str:
        return f"({self.south},{self.west},{self.north},{self.east})"

    def area_km2_approx(self) -> float:
        # Cheap equirectangular approximation — accurate enough for
        # sanity checks at city scale; we are not plotting property lines.
        lat_mid = (self.south + self.north) / 2
        dy_km = (self.north - self.south) * 111.0
        dx_km = (self.east - self.west) * 111.0 * _cos_deg(lat_mid)
        return max(0.0, dy_km * dx_km)


@dataclass
class CityOSM:
    """Parsed Overpass payload for one city.

    `arterials` — highway=primary|secondary|tertiary|trunk as node sequences.
        Each entry is a dict: {"id": int, "class": str, "nodes": [(lat, lon)...]}
    `buildings` — building footprints as polygon node sequences.
    `water` — natural=water / waterway=river as polygons/lines.
    `protected` — boundary=protected_area / military / heritage polygons.
    `anchors` — POIs (university, hospital, intercity-rail, market, stadium)
        as point features with type + optional name + weight.
    `rail_existing` — existing rail lines in bbox (avoid duplicating routes).
    """

    bbox: BBox
    slug: str
    fetched_at: float
    arterials: list[dict[str, Any]] = field(default_factory=list)
    buildings: list[dict[str, Any]] = field(default_factory=list)
    water: list[dict[str, Any]] = field(default_factory=list)
    protected: list[dict[str, Any]] = field(default_factory=list)
    anchors: list[dict[str, Any]] = field(default_factory=list)
    rail_existing: list[dict[str, Any]] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        d = asdict(self)
        # BBox dataclass serializes as-is; nothing special needed.
        return d

    def summary(self) -> str:
        return (
            f"{self.slug}: {len(self.arterials)} arterials, "
            f"{len(self.buildings)} buildings, {len(self.water)} water, "
            f"{len(self.protected)} protected, {len(self.anchors)} anchors, "
            f"{len(self.rail_existing)} rail"
        )


# Overpass query blocks. Each returns out:geom so we get coordinates inline
# without a second "recurse down + out body" roundtrip.
ARTERIAL_TAGS = ["motorway", "trunk", "primary", "secondary", "tertiary", "residential"]

# Anchor POI weights match the recipe's topology logic: higher weight =
# stronger pull on line endpoints in osr-routing.
ANCHOR_RULES: list[tuple[str, str, float]] = [
    # (osm_key, osm_value, weight)
    ("amenity", "university", 1.0),
    ("amenity", "college", 0.8),
    ("amenity", "hospital", 0.9),
    ("amenity", "marketplace", 0.7),
    ("amenity", "bus_station", 0.6),
    ("public_transport", "station", 0.8),
    ("railway", "station", 0.9),
    ("leisure", "stadium", 0.5),
    ("shop", "mall", 0.6),
    ("tourism", "attraction", 0.3),
    # Airports — major commute generators, especially in capital cities.
    # Baghdad International (BIAP) was previously unreachable because no
    # POI tag in this list matched aeroway features.
    ("aeroway", "aerodrome", 1.0),
    ("aeroway", "terminal", 0.9),
    # Residential / suburban catchment — `place=neighbourhood` and
    # `place=suburb` are how OSM labels named residential districts.
    # Without these the demand surface relied on hospitals + universities
    # alone and missed populated suburbs (the "many urban areas not
    # connected" failure mode flagged 2026-04-26).
    ("place", "suburb", 0.7),
    ("place", "neighbourhood", 0.6),
    ("place", "town", 0.8),
]


def _build_query(bbox: BBox) -> str:
    """Single Overpass QL query returning every layer we need.

    We issue one big query rather than one-per-layer because:
    * Overpass amortizes bbox scan cost per query.
    * One cache entry per city > many tiny ones.
    * `out:json` streams all layers together so we parse once.
    """
    b = bbox.as_overpass()

    arterials = "\n".join(f'  way["highway"="{t}"]{b};' for t in ARTERIAL_TAGS)
    anchors_q = "\n".join(
        f'  node["{k}"="{v}"]{b};\n  way["{k}"="{v}"]{b};' for k, v, _ in ANCHOR_RULES
    )

    return f"""
[out:json][timeout:120];
(
{arterials}
  way["building"]{b};
  way["natural"="water"]{b};
  relation["natural"="water"]{b};
  way["waterway"="river"]{b};
  way["boundary"="protected_area"]{b};
  relation["boundary"="protected_area"]{b};
  way["landuse"="military"]{b};
  way["railway"~"^(rail|light_rail|subway|tram)$"]{b};
{anchors_q}
);
out geom tags;
""".strip()


def _cache_path(cache_dir: Path, query: str, slug: str) -> Path:
    digest = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{slug}__{digest}.json"


def _fetch_overpass(query: str) -> dict[str, Any]:
    """Try each Overpass endpoint in order; first one that answers wins."""
    last_exc: Exception | None = None
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            log.info("overpass: %s (%d chars)", endpoint, len(query))
            r = requests.post(
                endpoint,
                data={"data": query},
                headers={"User-Agent": UA},
                timeout=HTTP_TIMEOUT_S,
            )
            if r.status_code == 429:
                # Rate limited. Short sleep + next endpoint.
                log.warning("overpass 429 from %s; trying next endpoint", endpoint)
                time.sleep(2)
                continue
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as e:
            last_exc = e
            log.warning("overpass fail at %s: %s", endpoint, e)
            time.sleep(1)
    raise OverpassError(f"all endpoints failed; last error: {last_exc}")


# ---- Parsing helpers ---------------------------------------------------

def _centroid_of_geom(geom: list[dict[str, float]]) -> tuple[float, float] | None:
    if not geom:
        return None
    lat = sum(g["lat"] for g in geom) / len(geom)
    lon = sum(g["lon"] for g in geom) / len(geom)
    return (lat, lon)


def _anchor_weight(tags: dict[str, str]) -> tuple[str, float] | None:
    for k, v, w in ANCHOR_RULES:
        if tags.get(k) == v:
            # Compose a stable type key like "amenity:hospital".
            return (f"{k}:{v}", w)
    return None


def _parse_overpass(raw: dict[str, Any], bbox: BBox, slug: str) -> CityOSM:
    city = CityOSM(bbox=bbox, slug=slug, fetched_at=time.time())
    for el in raw.get("elements", []):
        tags = el.get("tags", {}) or {}
        etype = el.get("type")
        eid = el.get("id")

        # Pull the geometry as a list of (lat, lon). Nodes have a single
        # point; ways have a `geometry` array; relations sometimes also.
        if etype == "node":
            geom = [{"lat": el["lat"], "lon": el["lon"]}]
        else:
            geom = el.get("geometry") or []

        nodes = [(g["lat"], g["lon"]) for g in geom]

        if "highway" in tags and tags["highway"] in ARTERIAL_TAGS:
            city.arterials.append(
                {"id": eid, "class": tags["highway"], "nodes": nodes, "name": tags.get("name")}
            )
            continue

        if "building" in tags:
            city.buildings.append({"id": eid, "nodes": nodes})
            continue

        if tags.get("natural") == "water" or tags.get("waterway") == "river":
            city.water.append({"id": eid, "kind": tags.get("waterway", "water"), "nodes": nodes})
            continue

        if tags.get("boundary") == "protected_area" or tags.get("landuse") == "military":
            city.protected.append(
                {"id": eid, "kind": tags.get("boundary", tags.get("landuse")), "nodes": nodes}
            )
            continue

        if tags.get("railway") in {"rail", "light_rail", "subway", "tram"}:
            city.rail_existing.append(
                {"id": eid, "kind": tags["railway"], "nodes": nodes}
            )
            continue

        anchor = _anchor_weight(tags)
        if anchor:
            kind, weight = anchor
            centroid = _centroid_of_geom(geom)
            if centroid is None:
                continue
            city.anchors.append(
                {
                    "id": eid,
                    "kind": kind,
                    "weight": weight,
                    "name": tags.get("name"),
                    "lat": centroid[0],
                    "lon": centroid[1],
                }
            )

    return city


# ---- Public API --------------------------------------------------------

def fetch_city(
    bbox: BBox,
    slug: str,
    cache_dir: Path | str | None = None,
    force_refresh: bool = False,
) -> CityOSM:
    """Pull (or load from cache) all OSM layers for a city.

    Parameters
    ----------
    bbox : BBox
        Geographic bounding box.
    slug : str
        Short identifier used in cache filenames and logging (e.g. "samawah").
    cache_dir : Path | str | None
        Cache root. Defaults to ~/.cache/osr-design/osm/.
    force_refresh : bool
        If True, ignore cached response and refetch.
    """
    cache_root = Path(cache_dir) if cache_dir else DEFAULT_CACHE
    query = _build_query(bbox)
    cpath = _cache_path(cache_root, query, slug)

    if cpath.exists() and not force_refresh:
        # Validate cache contents before trusting them — earlier
        # versions cached partial / truncated downloads when an
        # Overpass endpoint returned a 200 but the response body was
        # cut short, and on the next run JSON parsing exploded. Treat
        # parse errors + 0-byte files as cache misses and refetch.
        try:
            text = cpath.read_text()
            if text.strip():
                raw = json.loads(text)
                log.info("cache hit: %s", cpath.name)
                return _parse_overpass(raw, bbox, slug)
            log.warning("cache empty for %s; refetching", cpath.name)
        except (OSError, json.JSONDecodeError) as e:
            log.warning("cache invalid for %s (%s); refetching", cpath.name, e)
        try:
            cpath.unlink()
        except OSError:
            pass

    log.info("cache miss: fetching %s (area %.1f km²)", slug, bbox.area_km2_approx())
    raw = _fetch_overpass(query)
    # Atomic-ish write: stage to a sibling tmp then rename, so a
    # mid-write SIGKILL leaves the previous good cache intact.
    tmp = cpath.with_suffix(cpath.suffix + ".part")
    tmp.write_text(json.dumps(raw))
    tmp.replace(cpath)
    return _parse_overpass(raw, bbox, slug)


def _cos_deg(deg: float) -> float:
    import math

    return math.cos(math.radians(deg))
