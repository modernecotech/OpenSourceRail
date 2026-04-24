"""Top-level planner orchestrator.

`plan_city(CityInputs)` runs the full anchors → stations → lines →
design pipeline and returns a [`NetworkPlan`] that:

- Can emit a `design.toml` ready for `osr_scenario`.
- Carries diagnostic metrics (coverage %, per-line curvature,
  transfer reachability) so a batch runner can triage 500
  auto-designed cities and surface the weakest.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .anchors import Anchor, fetch_anchors
from .emit import design_toml
from .lines import LinePlan, curvature_penalty, transfer_reachability
from .linear import plan_arterial_network
from .stations import StationCandidate, coverage_score, place_stations


@dataclass(frozen=True)
class CityInputs:
    """Everything needed to auto-plan one city."""

    slug: str
    country_iso: str
    city_name: str
    center_lat: float
    center_lon: float
    bbox: tuple[float, float, float, float]
    population: int
    climate_preset: str = "temperate"
    peak_sun_hours: float = 5.0
    anchor_weight_overrides: dict[str, float] | None = None
    max_lines: int | None = None
    walk_radius_m: float = 800.0
    min_station_spacing_m: float = 600.0
    snap_to_roads: bool = True
    # Extra "forced" anchors beyond what Overpass returns. Use for
    # under-construction suburbs / new developments / future growth
    # areas where OSM tagging is sparse. Each tuple is
    # (name, lat, lon, weight) — weight ≥ 90 makes it must-cover.
    force_anchors: tuple[tuple[str, float, float, float], ...] = ()
    # Add a suburban ring line that loops around the city at
    # ~70 % of the farthest radial endpoint distance. Intersects
    # every radial so outer-to-outer trips don't congest the centre.
    ring_line: bool = False


@dataclass
class NetworkPlan:
    """Result of `plan_city` — stations + lines + diagnostic metrics."""

    inputs: CityInputs
    anchors: list[Anchor]
    stations: list[StationCandidate]
    lines: list[LinePlan]

    # Diagnostics.
    coverage: float = 0.0
    transfer_reachability: float = 0.0
    curvatures: dict[str, float] = field(default_factory=dict)

    def to_design_toml(self) -> str:
        return design_toml(
            slug=self.inputs.slug,
            country_iso=self.inputs.country_iso,
            city_name=self.inputs.city_name,
            center_lat=self.inputs.center_lat,
            center_lon=self.inputs.center_lon,
            bbox=self.inputs.bbox,
            population=self.inputs.population,
            climate_preset=self.inputs.climate_preset,
            peak_sun_hours=self.inputs.peak_sun_hours,
            stations=self.stations,
            lines=self.lines,
        )

    def metrics_summary(self) -> str:
        lines_section = "\n".join(
            f"  {lid}: {pen:.2f} rad  (sum of turns)"
            for lid, pen in self.curvatures.items()
        )
        return (
            f"City: {self.inputs.city_name}\n"
            f"Anchors:                {len(self.anchors)}\n"
            f"Stations:               {len(self.stations)}\n"
            f"Lines:                  {len(self.lines)}\n"
            f"Anchor-weighted coverage: {self.coverage:.1%}\n"
            f"Transfer reachability:  {self.transfer_reachability:.1%}  (pairs of lines sharing ≥1 station)\n"
            f"Per-line curvature:\n{lines_section}\n"
        )


def plan_city(
    inputs: CityInputs,
    *,
    cache_dir: Path | None = None,
    road_graph=None,
    road_nodes: dict | None = None,
) -> NetworkPlan:
    """Full planner run — **linear-logic** algorithm.

    Steps (see `osr_planner.linear.plan_arterial_network` for detail):
    1. Fetch demand anchors from OSM (cached).
    2. Fetch the arterial graph (trunk / primary / secondary / tertiary
       only — residential is excluded so no line can zigzag through
       a residential grid).
    3. Cluster anchors within 400 m of each other → POI clusters
       with summed weight.
    4. Grid-sweep axes through the weighted-centroid hub for the
       dominant demand directions. Pick K distinct orientations.
    5. For each direction, build the corridor polyline as the
       shortest arterial path between the two farthest-in-direction
       nodes, spliced through the hub.
    6. Walk each polyline; drop a station at each POI cluster within
       500 m, respecting an 800 m minimum inter-station spacing.
    """
    cache_dir = cache_dir or Path(".cache/osm")
    anchors = fetch_anchors(inputs.bbox, cache_dir)

    # Inject user-specified force-anchors (for under-construction
    # suburbs / new developments with sparse OSM tagging). Each one
    # is added to the anchor set with a `city`-class kind and a
    # configurable weight; weight ≥ 90 also marks it as must-cover
    # for line-endpoint selection.
    if inputs.force_anchors:
        for name, flat, flon, fweight in inputs.force_anchors:
            anchors.append(Anchor(
                kind="city",
                name=name,
                lat=float(flat),
                lon=float(flon),
                weight=float(fweight),
            ))

    if road_graph is None or road_nodes is None:
        road_graph, road_nodes = _fetch_arterial_graph(
            inputs.bbox, cache_dir
        )

    if road_graph is None or road_nodes is None:
        # Offline / fetch failed: fall back to the legacy greedy
        # placement so the pipeline still produces a valid
        # design.toml rather than crashing the 500-city batch run.
        stations = place_stations(
            anchors=anchors,
            population=inputs.population,
            walk_radius_m=inputs.walk_radius_m,
            min_spacing_m=inputs.min_station_spacing_m,
        )
        lines = []
    else:
        # Auto-enable the suburban ring for mid-to-large metros
        # (≥ 3 M population). Smaller cities rarely need it — the
        # radials already cross-cover. Caller can override via
        # `inputs.ring_line`.
        auto_ring = inputs.ring_line or inputs.population >= 3_000_000
        stations, lines = plan_arterial_network(
            anchors=anchors,
            road_graph=road_graph,
            road_nodes=road_nodes,
            max_lines=inputs.max_lines,
            population=inputs.population,
            walk_radius_m=500.0,
            min_station_spacing_m=800.0,
            ring_line=auto_ring,
        )

    plan = NetworkPlan(inputs=inputs, anchors=anchors, stations=stations, lines=lines)
    plan.coverage = coverage_score(stations, anchors, inputs.walk_radius_m)
    plan.transfer_reachability = transfer_reachability(lines)
    plan.curvatures = {
        L.id: curvature_penalty(L, stations) for L in lines
    }
    return plan


def _reorder_lines_along_axes(
    lines: list[LinePlan], stations: list[StationCandidate]
) -> None:
    """Re-sort each line's `station_ids` by projection of the
    station's (post-snap) coords onto the line's stored axis. Mutates
    `lines` in place."""
    import numpy as np

    by_id = {s.id: s for s in stations}
    for L in lines:
        ax = np.array([L.axis_dlat, L.axis_dlon])
        members = [by_id[sid] for sid in L.station_ids if sid in by_id]
        if len(members) < 2:
            continue
        coords = np.array([[m.lat, m.lon] for m in members])
        rel = coords - coords.mean(axis=0)
        proj = rel @ ax
        order = np.argsort(proj)
        L.station_ids = [members[j].id for j in order]


def _fetch_arterial_graph(
    bbox: tuple[float, float, float, float], cache_dir: Path
):
    """Fetch the arterial-only OSM road graph and build a networkx
    graph. Returns `(None, None)` if the fetch fails (offline run
    without a cached result), in which case the planner falls back
    to keeping stations at their OSM anchor coordinates."""
    try:
        from osr_scenario.routing import BBox, build_road_graph, fetch_roads
    except Exception:
        return None, None
    try:
        osm = fetch_roads(
            BBox(bbox[0], bbox[1], bbox[2], bbox[3]), cache_dir
        )
        G, nodes = build_road_graph(osm)
    except Exception:
        return None, None
    return G, nodes
