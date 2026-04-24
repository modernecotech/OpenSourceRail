"""Convert OSM vector data to cost / demand / buildability rasters.

Coordinate system
-----------------
Lat/lon are converted to a local metric grid via an equirectangular
projection anchored at the bbox centroid. This is accurate to a few
percent at city scale — we are not surveying parcels, we are picking
tracks. The grid origin (0, 0) is the NW corner; x increases east,
y increases south (matching numpy row-major ordering).

No GDAL, no rasterio (optional extra). A ~1500x1500 numpy array is
enough for a 30 x 30 km city at 20 m resolution; that fits in RAM
with room to spare even on laptops.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from osr_osm.fetcher import BBox, CityOSM

# ---- Cost weights (per-cell base cost) --------------------------------
#
# Small number = cheap to build on. 0 is reserved for "already have ROW"
# (existing rail corridors we can share). ∞ (np.inf) = forbidden.
#
# Tuned so that a 1 km straight arterial run costs ~30 cost-units while
# a 1 km tunnel under buildings costs ~300 — i.e., elevated/tunnel civil
# work is ~10x more expensive than street-running, which matches the
# spread in lib/templates/structures.toml.

BASE_COST_OPEN = 20.0       # open ground, no constraints
COST_ARTERIAL = 8.0         # wide road, easy ROW (light metro street-running)
COST_SIDE_STREET = 25.0     # narrow road, possible but slower build
COST_PARK = 45.0            # green space — expropriation + optics
COST_WATER = 300.0          # bridges only, very expensive
COST_EXISTING_RAIL = 3.0    # reuse corridor if we can
# Buildings get a very high but *finite* cost. Physical interpretation:
# the solver can always get through a built-up block, but at tunnel cost.
# Civil classification tags these segments as BoredTunnel downstream.
# Without this (when buildings = inf), dense cities like Lyon and Nairobi
# fragment into disconnected buildable islands and solve failures result.
COST_BUILDING = 600.0
COST_PROTECTED = math.inf   # legally forbidden (protected area, military)

# Demand kernel: how far a POI's gravity extends.
DEMAND_RADIUS_M = 600.0
DEMAND_CENTRE_BIAS = 0.3    # pull toward bbox centroid (urban density proxy)

# Default cell size. 20m is a good compromise: resolves one-street spacing
# in dense urban tissue, keeps the grid tractable.
DEFAULT_CELL_M = 20.0


# ---- Geo-reference book-keeping ---------------------------------------

@dataclass
class GridRef:
    """Maps between (row, col) cells and geographic coordinates.

    The grid uses an equirectangular projection anchored at lat0 (bbox
    centre). Rust reads this JSON via serde and performs the same
    transform in reverse when emitting corridor.geojson.
    """

    # Rows × columns.
    height: int
    width: int

    # Cell size in metres (isotropic).
    cell_m: float

    # Anchor for the projection — bbox centre latitude.
    lat0: float

    # Geographic corners (for sanity and for GeoJSON writers).
    bbox_south: float
    bbox_west: float
    bbox_north: float
    bbox_east: float

    # Cached transform constants: metres per degree at lat0.
    m_per_deg_lat: float
    m_per_deg_lon: float

    def latlon_to_rc(self, lat: float, lon: float) -> tuple[int, int]:
        dx_m = (lon - self.bbox_west) * self.m_per_deg_lon
        dy_m = (self.bbox_north - lat) * self.m_per_deg_lat
        col = int(dx_m / self.cell_m)
        row = int(dy_m / self.cell_m)
        return (row, col)

    def rc_to_latlon(self, row: int, col: int) -> tuple[float, float]:
        dx_m = (col + 0.5) * self.cell_m
        dy_m = (row + 0.5) * self.cell_m
        lon = self.bbox_west + dx_m / self.m_per_deg_lon
        lat = self.bbox_north - dy_m / self.m_per_deg_lat
        return (lat, lon)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


def _grid_ref(bbox: BBox, cell_m: float) -> GridRef:
    lat0 = (bbox.south + bbox.north) / 2
    m_per_deg_lat = 111_132.0  # mean across latitudes, good enough
    m_per_deg_lon = 111_320.0 * math.cos(math.radians(lat0))

    width_m = (bbox.east - bbox.west) * m_per_deg_lon
    height_m = (bbox.north - bbox.south) * m_per_deg_lat

    width = max(1, int(math.ceil(width_m / cell_m)))
    height = max(1, int(math.ceil(height_m / cell_m)))
    return GridRef(
        height=height,
        width=width,
        cell_m=cell_m,
        lat0=lat0,
        bbox_south=bbox.south,
        bbox_west=bbox.west,
        bbox_north=bbox.north,
        bbox_east=bbox.east,
        m_per_deg_lat=m_per_deg_lat,
        m_per_deg_lon=m_per_deg_lon,
    )


# ---- Polyline / polygon rasterizers -----------------------------------

def _iter_line_cells(
    grid: GridRef, nodes: Iterable[tuple[float, float]]
) -> Iterable[tuple[int, int]]:
    """Bresenham-like rasterization of a sequence of lat/lon nodes."""
    prev_rc: tuple[int, int] | None = None
    for lat, lon in nodes:
        rc = grid.latlon_to_rc(lat, lon)
        if prev_rc is not None:
            yield from _line(prev_rc, rc)
        prev_rc = rc


def _line(a: tuple[int, int], b: tuple[int, int]) -> Iterable[tuple[int, int]]:
    """Integer-grid line from a to b, inclusive."""
    r0, c0 = a
    r1, c1 = b
    dr = abs(r1 - r0)
    dc = abs(c1 - c0)
    sr = 1 if r0 < r1 else -1
    sc = 1 if c0 < c1 else -1
    err = dr - dc
    r, c = r0, c0
    while True:
        yield (r, c)
        if r == r1 and c == c1:
            return
        e2 = err * 2
        if e2 > -dc:
            err -= dc
            r += sr
        if e2 < dr:
            err += dr
            c += sc


def _fill_polygon(
    grid: GridRef, nodes: list[tuple[float, float]]
) -> Iterable[tuple[int, int]]:
    """Simple scanline fill of a closed polygon (lat/lon nodes).

    Handles convex and non-convex shapes. For our purposes (buildings,
    water, protected areas) this is fine — and we do not need topologically
    perfect fills, just approximate coverage.
    """
    if len(nodes) < 3:
        # Degenerate; treat as a polyline.
        yield from _iter_line_cells(grid, nodes)
        return

    rc = [grid.latlon_to_rc(lat, lon) for lat, lon in nodes]
    # Ensure closed ring.
    if rc[0] != rc[-1]:
        rc.append(rc[0])

    rows = [p[0] for p in rc]
    cols = [p[1] for p in rc]
    r_min, r_max = max(0, min(rows)), min(grid.height - 1, max(rows))
    c_min = max(0, min(cols))
    c_max = min(grid.width - 1, max(cols))

    for r in range(r_min, r_max + 1):
        xs: list[int] = []
        for i in range(len(rc) - 1):
            r0, c0 = rc[i]
            r1, c1 = rc[i + 1]
            if r0 == r1:
                continue
            if min(r0, r1) <= r < max(r0, r1):
                t = (r - r0) / (r1 - r0)
                xs.append(int(c0 + t * (c1 - c0)))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            a = max(c_min, xs[i])
            b = min(c_max, xs[i + 1])
            for c in range(a, b + 1):
                yield (r, c)


# ---- Raster builders --------------------------------------------------

def build_cost_surface(city: CityOSM, grid: GridRef) -> np.ndarray:
    """Base cost raster for route-finding.

    Layer order is deliberate: we lay *additive friendly* features first
    (open ground), then overwrite with *subtractive/expensive* features
    (water, buildings). Buildings and protected areas always win.
    """
    h, w = grid.height, grid.width
    cost = np.full((h, w), BASE_COST_OPEN, dtype=np.float32)

    # Arterials lower the cost — street-running rail integrates well.
    for way in city.arterials:
        cls = way["class"]
        if cls in {"motorway", "trunk", "primary", "secondary", "tertiary"}:
            weight = COST_ARTERIAL
        else:
            weight = COST_SIDE_STREET
        for rc in _iter_line_cells(grid, way["nodes"]):
            r, c = rc
            if 0 <= r < h and 0 <= c < w:
                # Take the minimum so a junction keeps the cheaper value.
                if cost[r, c] > weight:
                    cost[r, c] = weight

    # Existing rail — reuse if the route happens to align.
    for line in city.rail_existing:
        for rc in _iter_line_cells(grid, line["nodes"]):
            r, c = rc
            if 0 <= r < h and 0 <= c < w:
                cost[r, c] = min(cost[r, c], COST_EXISTING_RAIL)

    # Water — expensive but possible (bridges).
    for feat in city.water:
        for rc in _fill_polygon(grid, feat["nodes"]):
            r, c = rc
            cost[r, c] = max(cost[r, c], COST_WATER)

    # Buildings — forbidden.
    for b in city.buildings:
        for rc in _fill_polygon(grid, b["nodes"]):
            r, c = rc
            cost[r, c] = COST_BUILDING

    # Protected — forbidden.
    for p in city.protected:
        for rc in _fill_polygon(grid, p["nodes"]):
            r, c = rc
            cost[r, c] = COST_PROTECTED

    return cost


def build_demand_surface(city: CityOSM, grid: GridRef) -> np.ndarray:
    """Demand potential raster.

    Each anchor paints a Gaussian blob scaled by its weight. A mild
    centre-of-city bias represents density that OSM POIs under-represent
    in many target cities.
    """
    h, w = grid.height, grid.width
    demand = np.zeros((h, w), dtype=np.float32)

    sigma_cells = DEMAND_RADIUS_M / grid.cell_m
    two_sigma2 = 2.0 * sigma_cells * sigma_cells

    # Pre-compute coordinate grids once.
    rr, cc = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")

    for a in city.anchors:
        r0, c0 = grid.latlon_to_rc(a["lat"], a["lon"])
        d2 = (rr - r0) ** 2 + (cc - c0) ** 2
        blob = a["weight"] * np.exp(-d2 / two_sigma2, dtype=np.float32)
        demand += blob

    if DEMAND_CENTRE_BIAS > 0:
        cr, cc_ = h // 2, w // 2
        max_d = math.hypot(h / 2, w / 2)
        d = np.sqrt((rr - cr) ** 2 + (cc - cc_) ** 2) / max_d
        demand += DEMAND_CENTRE_BIAS * (1.0 - d).astype(np.float32)

    # Normalize to [0, 1] so Rust can compose with other surfaces.
    vmax = demand.max()
    if vmax > 0:
        demand /= vmax
    return demand


def build_buildability_mask(cost: np.ndarray) -> np.ndarray:
    """Boolean mask: True where track *can* physically be laid."""
    return np.isfinite(cost)


def _nudge_to_buildable(
    buildability: np.ndarray, r: int, c: int, max_radius: int
) -> tuple[int, int] | None:
    """Return the nearest (row, col) that is buildable, or None.

    Searches concentric rings outward from (r, c). Used to snap anchor
    points off building footprints (OSM POIs often sit on the centroid
    of the building that owns them).
    """
    h, w = buildability.shape
    if 0 <= r < h and 0 <= c < w and buildability[r, c]:
        return (r, c)
    for radius in range(1, max_radius + 1):
        best: tuple[int, int] | None = None
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if max(abs(dr), abs(dc)) != radius:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w and buildability[nr, nc]:
                    best = (nr, nc)
                    break
            if best is not None:
                break
        if best is not None:
            return best
    return None


# ---- Public pipeline --------------------------------------------------

@dataclass
class RasterBundle:
    grid: GridRef
    cost: np.ndarray
    demand: np.ndarray
    buildability: np.ndarray
    anchors_rc: list[dict[str, Any]]

    def summary(self) -> str:
        build_pct = 100.0 * self.buildability.mean()
        # Cost stats on buildable cells only — infs skew everything otherwise.
        buildable_cost = self.cost[self.buildability]
        return (
            f"grid {self.grid.height}x{self.grid.width} @ {self.grid.cell_m} m "
            f"({self.grid.height * self.grid.width / 1000:.0f}k cells); "
            f"buildable {build_pct:.1f}%; "
            f"cost mean={buildable_cost.mean():.1f} p95={np.percentile(buildable_cost, 95):.1f}; "
            f"demand peak={self.demand.max():.3f}; "
            f"anchors {len(self.anchors_rc)}"
        )


def rasterize_city(
    city: CityOSM,
    cell_m: float = DEFAULT_CELL_M,
) -> RasterBundle:
    grid = _grid_ref(city.bbox, cell_m)
    cost = build_cost_surface(city, grid)
    demand = build_demand_surface(city, grid)
    buildability = build_buildability_mask(cost)

    # Pre-compute anchor (row, col) for Rust. OSM POIs are often the
    # centroid of a building polygon, which lands on an infinite-cost
    # cell — snap each anchor to the nearest buildable neighbour so the
    # solver can always start / end there.
    anchors_rc = []
    for a in city.anchors:
        r, c = grid.latlon_to_rc(a["lat"], a["lon"])
        if not (0 <= r < grid.height and 0 <= c < grid.width):
            continue
        nudged = _nudge_to_buildable(buildability, r, c, max_radius=8)
        if nudged is None:
            continue
        r, c = nudged
        anchors_rc.append(
            {
                "id": a["id"],
                "kind": a["kind"],
                "weight": a["weight"],
                "name": a.get("name"),
                "row": r,
                "col": c,
                "lat": a["lat"],
                "lon": a["lon"],
            }
        )

    return RasterBundle(
        grid=grid,
        cost=cost,
        demand=demand,
        buildability=buildability,
        anchors_rc=anchors_rc,
    )


def save_grid(bundle: RasterBundle, out_dir: Path | str, slug: str) -> dict[str, Path]:
    """Write rasters + grid.json + anchors.json to disk.

    File layout:
        out_dir/
            {slug}.cost.npy
            {slug}.demand.npy
            {slug}.buildability.npy
            {slug}.grid.json
            {slug}.anchors.json
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "cost": out_dir / f"{slug}.cost.npy",
        "demand": out_dir / f"{slug}.demand.npy",
        "buildability": out_dir / f"{slug}.buildability.npy",
        "grid": out_dir / f"{slug}.grid.json",
        "anchors": out_dir / f"{slug}.anchors.json",
    }

    # np.save would add a magic header that complicates Rust reading.
    # Use raw little-endian bytes + sidecar JSON describing dtype/shape.
    # cost + demand are f32, buildability is u8. Rust reads via bytemuck.
    bundle.cost.astype(np.float32).tofile(paths["cost"])
    bundle.demand.astype(np.float32).tofile(paths["demand"])
    bundle.buildability.astype(np.uint8).tofile(paths["buildability"])

    paths["grid"].write_text(
        json.dumps(
            {
                "grid": bundle.grid.to_json(),
                "rasters": {
                    "cost": {
                        "path": paths["cost"].name,
                        "dtype": "f32",
                        "shape": list(bundle.cost.shape),
                        "byteorder": "little",
                    },
                    "demand": {
                        "path": paths["demand"].name,
                        "dtype": "f32",
                        "shape": list(bundle.demand.shape),
                        "byteorder": "little",
                    },
                    "buildability": {
                        "path": paths["buildability"].name,
                        "dtype": "u8",
                        "shape": list(bundle.buildability.shape),
                        "byteorder": "little",
                    },
                },
            },
            indent=2,
        )
    )

    paths["anchors"].write_text(json.dumps(bundle.anchors_rc, indent=2))
    return paths
