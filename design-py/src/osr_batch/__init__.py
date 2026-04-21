"""Batch driver: auto-generate designs for many cities in one run.

City inputs come from `cities.toml` (a simple list of
{slug, country, population, bbox} records). The driver calls
`osr_osm.fetch_city`, `osr_geo.rasterize_city`, and then shells out to
`osr-design` (Rust) per city. Each run is idempotent and deterministic.

A summary CSV captures design-quality.yaml headline metrics across the
batch so failing cities (gates=false) surface quickly.
"""

from .runner import CityInput, run_batch

__all__ = ["CityInput", "run_batch"]
