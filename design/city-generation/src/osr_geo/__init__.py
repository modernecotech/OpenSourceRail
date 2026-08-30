"""Raster synthesis for OSR route solver.

Produces three aligned rasters per city, on a common bbox + resolution:

cost.npy          — per-cell cost to lay track (∞ inside buildings, low on
                    arterials, medium on side streets, high through parks,
                    very high over water, ∞ through protected areas)
demand.npy        — per-cell trip-generation potential from POI density
                    + distance-decay; serves as the demand surface the
                    route solver tries to cover.
buildability.npy  — boolean mask: True = we can physically lay track here.

Each raster ships with a sidecar grid.json describing geo-referencing, so
the Rust solver can consume them without a rasterio dependency.

Resolution defaults to 20 m per cell — small enough to resolve streets,
coarse enough that a mid-size city (~100 km²) fits in ~250k cells and
Dijkstra runs in well under a second.
"""

from .rasterize import (
    GridRef,
    build_buildability_mask,
    build_cost_surface,
    build_demand_surface,
    rasterize_city,
    save_grid,
)

__all__ = [
    "GridRef",
    "build_buildability_mask",
    "build_cost_surface",
    "build_demand_surface",
    "rasterize_city",
    "save_grid",
]
