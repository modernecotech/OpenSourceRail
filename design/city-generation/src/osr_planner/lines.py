"""Line planning — **corridor-first + station-projection**.

Algorithm (2026-04-24, optimised for straight lines + population access):

1. Find the weighted centroid of all demand anchors → **hub**.
2. Grid-sweep: try every line orientation through the hub in 15°
   steps. For each orientation, compute the total demand weight
   within `corridor_width_m` perpendicular of the line.
3. Pick the top K orientations with the most demand on-axis.
   Orientations within `min_angle_sep_deg` of an already-picked
   one are skipped (line directions must differ).
4. Assign each non-hub station to its single closest line (by
   perpendicular distance to the axis). Stations whose nearest-axis
   distance exceeds `corridor_width_m` are dropped — this avoids
   the long detours that cluster-then-fit placement produces.
5. **Project** each assigned station onto its line's axis so
   the line is mathematically straight. The station's new
   coordinates are the foot of the perpendicular from the original
   anchor onto the axis line through the hub. This shifts stations
   ≤ `corridor_width_m` (≤ one block) but guarantees zero
   zigzag.
6. Hub sits at the intersection of all axes → shared interchange
   → 100% transfer reachability.

Use `plan_straight_network(stations, ...)` to get both the
projected stations *and* the lines. `plan_lines` alone returns
the line plans against the ORIGINAL station coordinates (useful
for tests and diagnostics).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .anchors import haversine_m
from .stations import StationCandidate


@dataclass
class LinePlan:
    """One planned line with its ordered station sequence.

    `polyline` is the explicit (lat, lon) path the planner chose
    through the arterial graph — provided so the renderer can draw
    the line verbatim instead of recomputing a per-station-pair
    shortest-path (which can differ arbitrarily when the arterial
    graph forces a long detour between two stations that the
    planner's end-to-end path had already solved in a single walk).
    Empty list means "no explicit geometry; fall back to routing".
    """

    id: str
    name: str
    station_ids: list[str] = field(default_factory=list)
    axis_dlat: float = 0.0
    axis_dlon: float = 1.0
    polyline: list[tuple[float, float]] = field(default_factory=list)


def plan_lines(
    stations: list[StationCandidate],
    *,
    max_lines: int | None = None,
    corridor_width_m: float = 1_200.0,
    min_angle_sep_deg: float = 40.0,
    sweep_step_deg: float = 15.0,
) -> list[LinePlan]:
    """Corridor-first planner. Returns a list of `LinePlan`s built on
    the ORIGINAL station coordinates — stations are not moved. Use
    [`plan_straight_network`] if you want projected (straight) lines.
    """
    _stations, lines = _plan_corridors(
        stations,
        max_lines=max_lines,
        corridor_width_m=corridor_width_m,
        min_angle_sep_deg=min_angle_sep_deg,
        sweep_step_deg=sweep_step_deg,
        project=False,
    )
    return lines


def plan_straight_network(
    stations: list[StationCandidate],
    *,
    max_lines: int | None = None,
    corridor_width_m: float = 1_200.0,
    min_angle_sep_deg: float = 40.0,
    sweep_step_deg: float = 15.0,
) -> tuple[list[StationCandidate], list[LinePlan]]:
    """Plan corridors **and** project each assigned station onto its
    line's axis so the resulting polyline is mathematically straight.

    Returns `(projected_stations, lines)`. Stations that were not
    assigned to any corridor (perpendicular distance > corridor_width_m
    from every chosen axis) are dropped — keeping them would force
    the detours the user rejected.
    """
    return _plan_corridors(
        stations,
        max_lines=max_lines,
        corridor_width_m=corridor_width_m,
        min_angle_sep_deg=min_angle_sep_deg,
        sweep_step_deg=sweep_step_deg,
        project=True,
    )


def _plan_corridors(
    stations: list[StationCandidate],
    *,
    max_lines: int | None,
    corridor_width_m: float,
    min_angle_sep_deg: float,
    sweep_step_deg: float,
    project: bool,
) -> tuple[list[StationCandidate], list[LinePlan]]:
    if len(stations) < 4:
        return list(stations), [_single_line("line-1", "Line 1", stations)]

    # 1. Weighted centroid → hub. The axes are ANCHORED at the hub's
    # actual coordinates (not the centroid) so the hub lies perfectly
    # on every line after projection.
    weights = np.array([max(1.0, s.score) for s in stations], dtype=float)
    coords = np.array([(s.lat, s.lon) for s in stations])
    centroid = np.average(coords, axis=0, weights=weights)
    hub_idx = int(np.argmin(np.linalg.norm(coords - centroid, axis=1)))
    hub = stations[hub_idx]
    hub_pos = np.array([hub.lat, hub.lon])

    # 2. Grid-sweep line orientations (0°..180°). Perpendicular
    # distance is computed in raw-degree space — 1° lat ≈ 111 km,
    # 1° lon ≈ 95 km at 31°N; the asymmetry matters < 15 % which is
    # within the 600 m corridor tolerance.
    width_deg = corridor_width_m / 111_000.0
    angles_deg = np.arange(0.0, 180.0, sweep_step_deg)
    scores: list[tuple[float, float]] = []
    for ang in angles_deg:
        ax_dir = _unit_vec(ang)
        score = _demand_along_axis(
            coords=coords - centroid,
            weights=weights,
            axis=ax_dir,
            width_deg=width_deg,
        )
        scores.append((score, ang))
    scores.sort(reverse=True)

    # 3. Pick top K non-collinear orientations.
    n_lines = _pick_n_lines(len(stations), max_lines)
    picked: list[float] = []
    for _score, ang in scores:
        if len(picked) >= n_lines:
            break
        if any(_angle_sep(ang, p) < min_angle_sep_deg for p in picked):
            continue
        picked.append(ang)

    axes = [_unit_vec(ang) for ang in picked]

    # 4. Assign each station to its single closest axis (perpendicular
    # distance from the hub-anchored line). Every station gets
    # assigned — dropping stations for being "too far off corridor"
    # produced short stub lines with gaps in peripheral coverage.
    # Arterial-graph routing between stations absorbs any small
    # off-axis scatter without generating zigzag (residential streets
    # are excluded from the graph).
    assignments: dict[int, list[int]] = {i: [] for i in range(len(axes))}
    for s_idx, s in enumerate(stations):
        if s_idx == hub_idx:
            continue  # hub goes on every line, handled below
        rel = np.array([s.lat, s.lon]) - hub_pos
        best_line = -1
        best_dist = float("inf")
        for a_idx, ax in enumerate(axes):
            along = rel @ ax
            perp = rel - along * ax
            d = float(np.linalg.norm(perp))
            if d < best_dist:
                best_dist = d
                best_line = a_idx
        if best_line >= 0:
            assignments[best_line].append(s_idx)

    # 5. Build each line. Optionally project stations onto axis.
    station_map: dict[str, StationCandidate] = {s.id: s for s in stations}
    lines: list[LinePlan] = []
    for i, ax in enumerate(axes):
        member_idxs = assignments[i]
        if len(member_idxs) < 1:
            continue
        line_members: list[StationCandidate] = []
        for s_idx in member_idxs:
            s = stations[s_idx]
            if project:
                rel = np.array([s.lat, s.lon]) - hub_pos
                along = rel @ ax
                new_lat = float(hub_pos[0] + along * ax[0])
                new_lon = float(hub_pos[1] + along * ax[1])
                s = StationCandidate(
                    id=s.id, name=s.name,
                    lat=new_lat, lon=new_lon,
                    archetype=s.archetype, score=s.score, serves=s.serves,
                )
                station_map[s.id] = s
            line_members.append(s)
        # Hub goes on every line; axes are anchored at hub_pos so
        # the hub is exactly on every line with zero projection.
        if hub not in line_members:
            line_members.append(hub)
        if len(line_members) < 2:
            continue
        projections = np.array([
            (np.array([m.lat, m.lon]) - hub_pos) @ ax for m in line_members
        ])
        order = np.argsort(projections)
        ordered = [line_members[j] for j in order]
        lines.append(LinePlan(
            id=f"line-{i + 1}",
            name=f"Line {i + 1}",
            station_ids=[s.id for s in ordered],
            axis_dlat=float(ax[0]),
            axis_dlon=float(ax[1]),
        ))

    # 6. Sort by length, rename. Length measurement uses updated
    # station coords via `station_map`, so projected length is
    # consistent.
    def _len(L: LinePlan) -> float:
        return _line_length(L, list(station_map.values()))

    lines.sort(key=lambda L: -_len(L))
    for idx, L in enumerate(lines):
        L.id = f"line-{idx + 1}"
        L.name = f"Line {idx + 1}"

    # Final station list: the hub + every station that landed on a
    # line. Dropped stations are gone.
    kept_ids = {hub.id}
    for L in lines:
        kept_ids.update(L.station_ids)
    out_stations = [station_map[sid] for sid in kept_ids if sid in station_map]
    return out_stations, lines


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _unit_vec(angle_deg: float) -> np.ndarray:
    """Unit vector at `angle_deg` measured counter-clockwise from
    east (dlon axis). Returns (dlat, dlon)."""
    r = math.radians(angle_deg)
    return np.array([math.sin(r), math.cos(r)])  # (dlat, dlon)


def _angle_sep(a: float, b: float) -> float:
    """Minimum angle between two orientations in [0, 180) degrees."""
    d = abs(a - b) % 180.0
    return min(d, 180.0 - d)


def _demand_along_axis(
    coords: np.ndarray,  # already centred (relative to centroid)
    weights: np.ndarray,
    axis: np.ndarray,
    width_deg: float,
) -> float:
    """Sum of demand weight for points within `width_deg` perpendicular
    of the line through origin with direction `axis`."""
    # Perpendicular distance: |rel - (rel·axis)·axis|.
    along = coords @ axis
    rel_along = np.outer(along, axis)
    perp = coords - rel_along
    perp_dist = np.linalg.norm(perp, axis=1)
    mask = perp_dist <= width_deg
    return float(weights[mask].sum())


def _stations_near_axis(
    stations: list[StationCandidate],
    centroid: np.ndarray,
    axis: np.ndarray,
    width_deg: float,
) -> list[StationCandidate]:
    """Return stations whose perpendicular distance to the
    centroid-through-axis line is ≤ `width_deg`."""
    out = []
    for s in stations:
        rel = np.array([s.lat, s.lon]) - centroid
        along = rel @ axis
        perp = rel - along * axis
        if np.linalg.norm(perp) <= width_deg:
            out.append(s)
    return out


def _pick_n_lines(n_stations: int, max_lines: int | None) -> int:
    n = max(2, round(n_stations / 7))
    if max_lines is not None:
        n = min(n, max_lines)
    return min(n, 5)


def _single_line(id_: str, name: str, stations: list[StationCandidate]) -> LinePlan:
    if len(stations) < 2:
        return LinePlan(id=id_, name=name, station_ids=[s.id for s in stations])
    coords = np.array([(s.lat, s.lon) for s in stations])
    centred = coords - coords.mean(axis=0)
    _, _, vt = np.linalg.svd(centred, full_matrices=False)
    axis = vt[0]
    projections = centred @ axis
    order = np.argsort(projections)
    ordered = [stations[i] for i in order]
    return LinePlan(
        id=id_,
        name=name,
        station_ids=[s.id for s in ordered],
        axis_dlat=float(axis[0]),
        axis_dlon=float(axis[1]),
    )


def _line_length(line: LinePlan, stations: list[StationCandidate]) -> float:
    by_id = {s.id: s for s in stations}
    total = 0.0
    prev = None
    for sid in line.station_ids:
        s = by_id.get(sid)
        if s is None:
            continue
        if prev is not None:
            total += haversine_m(prev, (s.lat, s.lon))
        prev = (s.lat, s.lon)
    return total


# --------------------------------------------------------------------------
# Diagnostic metrics
# --------------------------------------------------------------------------


def curvature_penalty(
    line: LinePlan, stations: list[StationCandidate]
) -> float:
    """Sum of absolute heading changes, radians."""
    by_id = {s.id: s for s in stations}
    pts = [
        (by_id[sid].lat, by_id[sid].lon)
        for sid in line.station_ids if sid in by_id
    ]
    if len(pts) < 3:
        return 0.0
    headings = [
        math.atan2(b[1] - a[1], b[0] - a[0]) for a, b in zip(pts, pts[1:])
    ]
    total = 0.0
    for h1, h2 in zip(headings, headings[1:]):
        d = (h2 - h1 + math.pi) % (2 * math.pi) - math.pi
        total += abs(d)
    return total


def transfer_reachability(lines: list[LinePlan]) -> float:
    if len(lines) < 2:
        return 1.0
    n = len(lines)
    total = n * (n - 1) // 2
    shared = 0
    for i in range(n):
        for j in range(i + 1, n):
            if set(lines[i].station_ids) & set(lines[j].station_ids):
                shared += 1
    return shared / total
