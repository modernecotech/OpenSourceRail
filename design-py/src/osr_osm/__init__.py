"""OSM data ingest for OpenSourceRail city designs.

Public API
----------
fetch_city(bbox, slug, cache_dir) -> CityOSM
    Pull arterials, buildings, water, protected areas and anchors (POIs) for
    a city bounding box. Every response is cached to disk keyed by
    SHA256(query); a second call with the same bbox + tag set hits the cache
    and never touches the network.

The result object is a plain dict-like structure designed for:
    - direct JSON serialization (feed the Rust solver as a sidecar file)
    - numpy-native raster synthesis in osr_geo
    - no pandas / geopandas dependency, keeping install surface tiny

Unified system principle: one fetcher, many cities. Overpass queries are
generated from a small rule table below; adding a new tag group is a
four-line change, not a new module.
"""

from .fetcher import (
    BBox,
    CityOSM,
    OverpassError,
    fetch_city,
)

__all__ = [
    "BBox",
    "CityOSM",
    "OverpassError",
    "fetch_city",
]
