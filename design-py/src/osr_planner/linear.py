"""Linear-logic planner — **POI clusters → arterial corridors → stations**.

Algorithm (2026-04-24, user-specified):

1. **Cluster POIs.** Aggregate demand anchors within
   `cluster_radius_m` of each other into a single POI cluster whose
   position is the weight-averaged centroid and whose weight is the
   sum of its members. Prevents two stations from sitting 200 m
   apart because an OSM dataset has both a hospital node and a
   hospital way tag.

2. **Build the arterial graph.** Trunk/primary/secondary/tertiary
   only — residential grid streets are explicitly excluded so no
   line can zigzag through them.

3. **Hub.** Weight-averaged centroid of clusters → snap to nearest
   arterial node. Every line passes through the hub → 100% transfer
   reachability.

4. **Pick K corridor directions.** Grid-sweep orientations through
   the hub in 15° steps, score each by demand-weight within
   `walk_radius_m` perpendicular. Top K distinct (≥ `min_angle_sep_deg`
   apart) orientations become the line directions.

5. **For each corridor direction, build the line.** Find the
   arterial node farthest in +direction and -direction from the
   hub. Shortest-path between them through the arterial graph =
   the line's polyline — a real road running from one city edge
   to the other in the chosen direction. If the path doesn't
   already pass through the hub, splice via `neg → hub → pos`.

6. **Place stations along the line.** Walk the polyline; for each
   POI cluster whose closest point on the polyline is within
   `walk_radius_m` (500 m by default), place a station at that
   closest polyline vertex, naming it after the cluster's
   highest-weight anchor. Enforce `min_station_spacing_m` between
   consecutive stations on the same line.

7. **Share the hub station** across every line (interchange).

Result: each line **is** a real arterial polyline, stations sit at
cluster hits along that polyline with enforced spacing, and the
rendered track has no zigzag or dog-leg by construction — the line
IS a road.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .anchors import Anchor, haversine_m
from .lines import LinePlan
from .stations import StationCandidate, _archetype_for_seed, _slug


# --------------------------------------------------------------------------
# POI clusters
# --------------------------------------------------------------------------


@dataclass
class POICluster:
    """A spatially-aggregated group of demand anchors within
    `cluster_radius_m` of each other. Position is the weight-averaged
    centroid; weight is the sum of members."""

    lat: float
    lon: float
    weight: float
    primary_name: str
    primary_kind: str
    member_names: list[str] = field(default_factory=list)


def cluster_anchors(
    anchors: list[Anchor], cluster_radius_m: float = 400.0
) -> list[POICluster]:
    """Greedy single-pass clustering. Anchors are processed weight-
    descending so the highest-weight anchor in a cluster defines its
    primary name + archetype. Subsequent anchors in range merge into
    it and contribute to the weighted centre."""
    clusters: list[POICluster] = []
    for a in sorted(anchors, key=lambda x: -x.weight):
        merged = False
        for c in clusters:
            if haversine_m((a.lat, a.lon), (c.lat, c.lon)) <= cluster_radius_m:
                tw = c.weight + a.weight
                c.lat = (c.lat * c.weight + a.lat * a.weight) / tw
                c.lon = (c.lon * c.weight + a.lon * a.weight) / tw
                c.weight = tw
                c.member_names.append(a.name)
                merged = True
                break
        if not merged:
            clusters.append(POICluster(
                lat=a.lat, lon=a.lon, weight=a.weight,
                primary_name=a.name, primary_kind=a.kind,
                member_names=[a.name],
            ))
    return clusters


# --------------------------------------------------------------------------
# Planner
# --------------------------------------------------------------------------


def plan_arterial_network(
    anchors: list[Anchor],
    road_graph,
    road_nodes: dict,
    *,
    max_lines: int | None = None,
    population: int | None = None,
    cluster_radius_m: float = 500.0,
    walk_radius_m: float = 900.0,
    min_station_spacing_m: float = 900.0,
    corridor_score_width_m: float = 1_500.0,
    corridor_thread_width_m: float = 800.0,
    waypoint_thread_width_m: float = 500.0,
    waypoint_min_weight: float = 50.0,
    max_waypoints_per_line: int = 2,
    thread_min_weight: float = 15.0,
    must_cover_min_weight: float = 90.0,
    min_stations_per_line: int = 5,
    min_line_length_m: float = 4_000.0,
    suburban_extend_m: float = 2_500.0,
    ring_line: bool = False,
    ring_n_nodes: int = 8,
    ring_radius_fraction: float = 0.7,
    max_overlap_with_existing: float = 0.75,
    sweep_step_deg: float = 10.0,
    min_angle_sep_deg: float = 30.0,
    # Mega-city override: reduce min_angle_sep to 20° automatically
    # when population ≥ this threshold, so 8-10+ distinct radials
    # can survive the angular-separation filter. Metros the size of
    # Baghdad need finer-grained radial fanning than a 220 k town.
    megacity_pop_threshold: int = 3_000_000,
    megacity_min_angle_sep_deg: float = 20.0,
) -> tuple[list[StationCandidate], list[LinePlan]]:
    """Linear-logic planner. Returns `(stations, lines)`.

    Key parameters:
    - `cluster_radius_m`: anchors within this radius merge into one
      POI cluster (de-dupe overlapping OSM tags).
    - `walk_radius_m`: a cluster becomes a station if the line's
      polyline passes within this distance.
    - `min_station_spacing_m`: minimum gap between consecutive
      stations on the same line.
    - `corridor_score_width_m`: band around a candidate axis used to
      *score* that direction's demand during the grid-sweep (wide,
      so a slightly-off-axis neighbourhood still helps pick the
      right direction).
    - `corridor_thread_width_m`: band used to pick line endpoints —
      the farthest clusters in + and - axis direction. Generous
      (2 km) so intermediate-distance off-axis neighbourhoods still
      count as valid endpoints; the corridor direction is chosen by
      demand-along-axis scoring, so an off-axis endpoint just adds
      a small bend at the end of the line, not mid-line detours.
    - `thread_min_weight`: minimum cluster weight to qualify as an
      ordinary endpoint. Set low (~15) to include neighbourhoods
      (default weight 18).
    - `must_cover_min_weight`: any cluster with weight ≥ this value
      (railway station, major airport, university of record) is
      guaranteed to be on at least one line — the nearest-axis
      line picks it up as an endpoint even if that expands its
      perpendicular reach beyond `corridor_thread_width_m`. Prevents
      the embarrassing "intercity rail station 3 km from the
      metro" regression.
    - `suburban_extend_m`: after the core polyline (endpoint-cluster
      to endpoint-cluster via hub) is built, greedily extend each
      end outward along the axis by up to this distance along the
      arterial graph. Developing cities are growing — the rail
      system should reach the future-suburb edge, not just today's
      last anchor.
    - `min_stations_per_line`: lines shorter than this are dropped
      as spurious stubs.
    """
    import networkx as nx

    if not anchors or road_graph is None or road_nodes is None:
        return [], []

    clusters = cluster_anchors(anchors, cluster_radius_m)
    if not clusters:
        return [], []

    # Work inside the largest connected component of the arterial
    # graph — an isolated suburb's road loop can't host a line.
    cc = max(nx.connected_components(road_graph), key=len)
    cc_nodes = list(cc)
    cc_coords = np.array([road_nodes[n] for n in cc_nodes])

    # Snap every cluster to its nearest arterial node (brute-force;
    # clusters are few). This gives each POI a "POI-node" on the
    # graph that the line can thread through.
    cluster_nodes: list = []
    for c in clusters:
        dists = np.linalg.norm(
            cc_coords - np.array([c.lat, c.lon]), axis=1
        )
        cluster_nodes.append(cc_nodes[int(np.argmin(dists))])

    # Hub: weighted centroid of clusters, snapped to nearest arterial
    # node. Every line passes through the hub → 100% transfer
    # reachability.
    cl_coords = np.array([[c.lat, c.lon] for c in clusters])
    cl_weights = np.array([c.weight for c in clusters])
    centroid = np.average(cl_coords, weights=cl_weights, axis=0)
    hub_local = int(np.argmin(np.linalg.norm(cc_coords - centroid, axis=1)))
    hub_node = cc_nodes[hub_local]
    hub_pos = np.array(road_nodes[hub_node])

    # Pick K corridor directions by demand-along-axis.
    score_deg = corridor_score_width_m / 111_000.0
    thread_deg = corridor_thread_width_m / 111_000.0
    waypoint_deg = waypoint_thread_width_m / 111_000.0
    angles = np.arange(0.0, 180.0, sweep_step_deg)
    scores: list[tuple[float, float]] = []
    rel_clusters = cl_coords - hub_pos
    for ang in angles:
        ax = _unit_vec(ang)
        along = rel_clusters @ ax
        perp = rel_clusters - np.outer(along, ax)
        perp_d = np.linalg.norm(perp, axis=1)
        mask = perp_d <= score_deg
        scores.append((float(cl_weights[mask].sum()), float(ang)))
    scores.sort(reverse=True)

    n_lines = _pick_n_lines(len(clusters), max_lines, population)
    effective_angle_sep = (
        megacity_min_angle_sep_deg
        if population and population >= megacity_pop_threshold
        else min_angle_sep_deg
    )
    picked_angles: list[float] = []
    for _s, ang in scores:
        if len(picked_angles) >= n_lines:
            break
        if any(_angle_sep(ang, p) < effective_angle_sep for p in picked_angles):
            continue
        picked_angles.append(ang)

    # Identify must-cover clusters (weight ≥ must_cover_min_weight).
    # Each will be force-included as an endpoint on the line whose
    # axis best aligns with its direction from the hub.
    must_cover_ids: set[int] = set()
    must_cover_assignments: dict[int, int] = {}  # cluster_idx → best line idx
    for cidx, c in enumerate(clusters):
        if c.weight < must_cover_min_weight:
            continue
        rel = np.array([c.lat, c.lon]) - hub_pos
        if np.linalg.norm(rel) < 1e-9:
            continue  # it IS the hub
        # Best angle: the picked angle whose axis is closest to
        # this cluster's direction from hub (either polarity).
        rel_ang = math.degrees(math.atan2(rel[0], rel[1]))  # (dlat, dlon)
        rel_ang = rel_ang % 180.0
        best_line = -1
        best_sep = float("inf")
        for li, ang in enumerate(picked_angles):
            sep = _angle_sep(ang, rel_ang)
            if sep < best_sep:
                best_sep = sep
                best_line = li
        if best_line >= 0:
            must_cover_ids.add(cidx)
            must_cover_assignments[cidx] = best_line

    # Build each line: arterial corridor + stations along it.
    lines: list[LinePlan] = []
    all_stations: dict[str, StationCandidate] = {}

    # Hub is always a station (interchange).
    hub_cluster_idx = int(np.argmin(
        np.linalg.norm(cl_coords - hub_pos, axis=1)
    ))
    hub_cluster = clusters[hub_cluster_idx]
    hub_station = StationCandidate(
        id=_slug(hub_cluster.primary_name) or "hub",
        name=hub_cluster.primary_name or "Centre",
        lat=float(hub_pos[0]), lon=float(hub_pos[1]),
        archetype="interchange",
        score=hub_cluster.weight,
        serves=(_slug(hub_cluster.primary_name) or "hub",),
    )
    all_stations[hub_station.id] = hub_station

    for i, ang in enumerate(picked_angles):
        ax = _unit_vec(ang)
        must_cover_for_line = [
            cidx for cidx, li in must_cover_assignments.items() if li == i
        ]
        polyline = _corridor_via_clusters(
            road_graph=road_graph,
            road_nodes=road_nodes,
            clusters=clusters,
            cluster_nodes=cluster_nodes,
            hub_node=hub_node,
            hub_pos=hub_pos,
            axis=ax,
            thread_deg=thread_deg,
            thread_min_weight=thread_min_weight,
            must_cover_cluster_ids=must_cover_for_line,
            suburban_extend_m=suburban_extend_m,
            waypoint_deg=waypoint_deg,
            waypoint_min_weight=waypoint_min_weight,
            max_waypoints=max_waypoints_per_line,
        )
        if polyline is None or len(polyline) < 2:
            continue

        line_stations = _place_stations_on_polyline(
            polyline=polyline,
            clusters=clusters,
            walk_radius_m=walk_radius_m,
            min_spacing_m=min_station_spacing_m,
            hub_station=hub_station,
            existing=all_stations,
        )
        # Enforce monotonic along-axis order. The polyline can
        # traverse parallel arterials creating a near-loop that my
        # node-level cycle-collapse misses (it visits two different
        # graph nodes at geographically adjacent positions). Sorting
        # stations by their along-axis projection forces the
        # renderer to visit them in corridor order; any station that
        # breaks monotonicity is dropped so the line never doubles
        # back on itself.
        line_stations = _monotonise_stations(
            line_stations, hub_pos=hub_pos, axis=ax,
        )
        # Trim tails: if the first or last few stations are separated
        # from the main cluster by a big gap (> `max_tail_gap_m`) AND
        # the outlier isn't a must-cover, drop them. Otherwise a line
        # whose corridor reaches a distant OSM-tagged town can extend
        # 15-20 km through empty desert with no intermediate stops —
        # pointless rail. Must-cover clusters are preserved.
        must_cover_set = {
            clusters[cidx].primary_name for cidx in must_cover_ids
        }
        line_stations = _trim_isolated_tails(
            line_stations,
            max_gap_m=8_000.0,
            protected_names=must_cover_set | {hub_station.name},
        )
        if len(line_stations) < min_stations_per_line:
            continue  # too few stations — spurious stub
        line_length_m = _polyline_length_m(polyline)
        if line_length_m < min_line_length_m:
            continue  # polyline too short to be useful as a rail line
        # Redundancy: if most of this line's non-hub stations already
        # sit on an existing line, drop it — another direction will
        # eventually catch genuinely new demand.
        existing_line_ids = set()
        for prev in lines:
            existing_line_ids.update(prev.station_ids)
        my_ids = {s.id for s in line_stations if s.id != hub_station.id}
        if my_ids:
            overlap = len(my_ids & existing_line_ids) / len(my_ids)
            if overlap > max_overlap_with_existing:
                continue
        for s in line_stations:
            all_stations.setdefault(s.id, s)
        # Clip the polyline to the axis-projection range spanned by
        # the stations. The arterial shortest-path may bulge past a
        # terminus (e.g. via a ring road 2 km north, then back to
        # the terminus) — those bulge segments would render as "line
        # extends beyond terminus".
        clipped = _clip_polyline_to_axis_range(
            polyline, line_stations, hub_pos=hub_pos, axis=ax,
        )
        lines.append(LinePlan(
            id=f"line-{i + 1}", name=f"Line {i + 1}",
            station_ids=[s.id for s in line_stations],
            axis_dlat=float(ax[0]), axis_dlon=float(ax[1]),
            polyline=[(float(p[0]), float(p[1])) for p in clipped],
        ))

    # Optional ring line — a suburban loop connecting N outer
    # arterial nodes arranged around the hub at
    # `ring_radius_fraction` of the farthest endpoint distance.
    # Reduces traffic through the central interchange for trips
    # between outer districts (Baghdad-style metropolitan pattern).
    if ring_line and len(lines) >= 2:
        ring = _build_ring_line(
            road_graph=road_graph,
            road_nodes=road_nodes,
            cc_nodes=cc_nodes,
            cc_coords=cc_coords,
            hub_pos=hub_pos,
            lines=lines,
            all_stations=all_stations,
            clusters=clusters,
            cluster_nodes=cluster_nodes,
            walk_radius_m=walk_radius_m,
            min_spacing_m=min_station_spacing_m,
            n_nodes=ring_n_nodes,
            radius_fraction=ring_radius_fraction,
        )
        if ring is not None:
            r_line, r_stations = ring
            for s in r_stations:
                all_stations.setdefault(s.id, s)
            lines.append(r_line)

    # Merge any pair of stations across lines that ended up within
    # `merge_radius_m` of each other. Cluster-radius only applies
    # within the anchor set; two DIFFERENT clusters (e.g. a
    # university + a hospital that are 150 m apart on separate OSM
    # nodes) each produce their own station. For a rail network
    # there's no reason to have two platforms 150 m apart — merge
    # into the higher-weight one and update each affected line's
    # `station_ids` in place.
    _merge_nearby_stations(
        lines, all_stations, merge_radius_m=300.0,
    )

    # Sort lines longest → shortest, renumber. The ring line keeps
    # its dedicated "Ring Line" name instead of being swept into
    # the numbered radial sequence — it's topologically distinct
    # (closed loop around the perimeter, no radial through-hub run)
    # and should read that way on the map legend.
    radials = [L for L in lines if L.id != "line-ring"]
    ring = next((L for L in lines if L.id == "line-ring"), None)
    radials.sort(key=lambda L: -len(L.station_ids))
    for idx, L in enumerate(radials):
        L.id = f"line-{idx + 1}"
        L.name = f"Line {idx + 1}"
    lines[:] = radials + ([ring] if ring is not None else [])

    # Promote every line's first + last station to "terminal" so the
    # renderer draws them in terminal red, not the line colour — a
    # station with the same colour as the line it sits on looks
    # invisible and reads as "missing terminus".
    for L in lines:
        if not L.station_ids:
            continue
        for sid in (L.station_ids[0], L.station_ids[-1]):
            s = all_stations.get(sid)
            if s is None:
                continue
            if s.archetype == "interchange":
                continue  # hub shared by multiple lines — keep it as an interchange
            if s.archetype == "terminal":
                continue
            all_stations[sid] = StationCandidate(
                id=s.id, name=s.name,
                lat=s.lat, lon=s.lon,
                archetype="terminal",
                score=s.score, serves=s.serves,
            )

    used_ids = {hub_station.id}
    for L in lines:
        used_ids.update(L.station_ids)
    final_stations = [all_stations[sid] for sid in used_ids]
    return final_stations, lines


# --------------------------------------------------------------------------
# Corridor construction
# --------------------------------------------------------------------------


def _corridor_via_clusters(
    *,
    road_graph,
    road_nodes: dict,
    clusters: list[POICluster],
    cluster_nodes: list,
    hub_node,
    hub_pos: np.ndarray,
    axis: np.ndarray,
    thread_deg: float,
    thread_min_weight: float,
    must_cover_cluster_ids: list[int],
    suburban_extend_m: float = 0.0,
    waypoint_deg: float = 0.0,
    waypoint_min_weight: float = 0.0,
    max_waypoints: int = 0,
) -> list[tuple[float, float]] | None:
    """Return the arterial polyline running from the farthest
    endpoint cluster in the +axis direction to the farthest in
    the -axis direction, spliced through the hub.

    Endpoints are the clusters with `weight ≥ thread_min_weight` and
    perpendicular distance ≤ `thread_deg`. Any cluster in
    `must_cover_cluster_ids` is always admitted as an endpoint
    candidate regardless of perpendicular offset — this guarantees
    rail-station / airport-class anchors are on *some* line.
    """
    import networkx as nx

    candidates: list[tuple[float, int]] = []
    for idx, c in enumerate(clusters):
        rel = np.array([c.lat, c.lon]) - hub_pos
        along = rel @ axis
        perp = rel - along * axis
        perp_m = np.linalg.norm(perp)
        is_must = idx in must_cover_cluster_ids
        if is_must or (c.weight >= thread_min_weight and perp_m <= thread_deg):
            candidates.append((float(along), idx))
    if len(candidates) < 2:
        return None

    candidates.sort(key=lambda x: x[0])
    neg_along, neg_idx = candidates[0]
    pos_along, pos_idx = candidates[-1]

    # Must-cover clusters take precedence over "ordinary" endpoints
    # in their direction, even if another candidate is further out.
    for must_idx in must_cover_cluster_ids:
        for (a, cidx) in candidates:
            if cidx != must_idx:
                continue
            if a < 0 and a < neg_along:
                neg_along, neg_idx = a, cidx
            if a >= 0 and a > pos_along:
                pos_along, pos_idx = a, cidx
    # If a must-cover is on one side but no ordinary candidate is on
    # the other, still accept — the line becomes single-ended but
    # that's better than missing the rail station entirely.
    if neg_along >= 0 and pos_along <= 0:
        return None

    neg_node = cluster_nodes[neg_idx]
    pos_node = cluster_nodes[pos_idx]

    # Pick up to `max_waypoints` high-weight waypoints lying close to
    # the axis (`waypoint_deg` narrow band) — these anchor the
    # polyline to pass through dense pockets the endpoint-only path
    # would miss. Distinct from endpoints: waypoints are *mid-line*.
    # Narrow `waypoint_deg` keeps them close to the axis so threading
    # them in doesn't produce detours.
    waypoint_nodes: list = []
    waypoint_alongs: list[float] = []
    if max_waypoints > 0 and waypoint_min_weight > 0 and waypoint_deg > 0:
        wps: list[tuple[float, float, int, bool]] = []
        # (weight, along, cluster_idx, is_must_cover)
        must_ids = set(must_cover_cluster_ids)
        for idx, c in enumerate(clusters):
            is_must = idx in must_ids
            if not is_must and c.weight < waypoint_min_weight:
                continue
            if idx in (neg_idx, pos_idx):
                continue
            rel = np.array([c.lat, c.lon]) - hub_pos
            along = float(rel @ axis)
            perp = rel - along * axis
            if is_must or np.linalg.norm(perp) <= waypoint_deg:
                wps.append((c.weight, along, idx, is_must))
        # Must-cover clusters always kept (they bypass the cap).
        # Other waypoints are sorted heavy-first and capped.
        must_wps = [(a, ci) for _w, a, ci, m in wps if m]
        other_wps = sorted(
            [(w, a, ci) for w, a, ci, m in wps if not m],
            key=lambda x: -x[0],
        )
        chosen = list(must_wps) + [(a, ci) for _w, a, ci in other_wps[:max_waypoints]]
        chosen.sort(key=lambda x: x[0])
        for along, cidx in chosen:
            waypoint_nodes.append(cluster_nodes[cidx])
            waypoint_alongs.append(along)

    # Build node sequence: neg → (neg-side waypoints) → hub →
    # (pos-side waypoints) → pos.
    neg_waypoints = [n for n, a in zip(waypoint_nodes, waypoint_alongs) if a < 0]
    pos_waypoints = [n for n, a in zip(waypoint_nodes, waypoint_alongs) if a >= 0]
    seq: list = [neg_node] + neg_waypoints + [hub_node] + pos_waypoints + [pos_node]
    # Dedupe consecutive identical nodes.
    dedup: list = []
    for n in seq:
        if not dedup or dedup[-1] != n:
            dedup.append(n)

    # Concatenate shortest-paths between consecutive nodes.
    path: list = []
    for u, v in zip(dedup, dedup[1:]):
        try:
            seg = nx.shortest_path(road_graph, u, v, weight="weight")
        except nx.NetworkXNoPath:
            return None
        if path and path[-1] == seg[0]:
            path.extend(seg[1:])
        else:
            path.extend(seg)

    # Cycle removal: concatenated shortest-paths can visit the same
    # node twice if a waypoint forced an out-and-back — e.g., going
    # neg → A → waypoint → A → hub traverses A twice. That renders
    # as "a long segment to nothing then back". Collapse the loop:
    # if node N first appears at index i and again at index j > i,
    # drop path[i+1 : j+1]. Repeat until no cycles remain. The line
    # retains all anchors it actually reached; any waypoint whose
    # detour caused the cycle is dropped as a graceful fallback.
    path = _collapse_cycles(path)
    if len(path) < 2:
        return None

    # Generously extend each end along the axis toward the suburban
    # fringe. Developing-world cities grow outward; rail that stops
    # at today's last anchor is obsolete in a decade. The extension
    # walks the arterial graph greedily in the + / - axis direction,
    # up to `suburban_extend_m` metres of arterial from each end,
    # then is trimmed back so the tail doesn't dangle into empty
    # land with no demand.
    if suburban_extend_m > 0:
        path = _extend_along_axis(
            path, road_graph, road_nodes,
            axis=axis, direction=+1, max_extend_m=suburban_extend_m,
        )
        path = list(reversed(_extend_along_axis(
            list(reversed(path)), road_graph, road_nodes,
            axis=axis, direction=-1, max_extend_m=suburban_extend_m,
        )))
        path = _trim_dry_tails(
            path, road_nodes, clusters=clusters,
            walk_radius_deg=(800.0 / 111_000.0),
        )
    # Convert arterial-node path to a (lat, lon) polyline. For
    # must-cover clusters whose nearest arterial node is FAR from
    # the cluster's actual coord (e.g. a new suburb in the desert
    # with no existing arterials), splice in a "greenfield spur":
    # a straight segment from the arterial node out to the
    # cluster's actual position. Represents dedicated new RoW
    # through empty land — typical for reaching under-construction
    # suburbs.
    polyline = [road_nodes[n] for n in path]
    _insert_greenfield_spurs(
        polyline, path, road_nodes,
        clusters=clusters, cluster_nodes=cluster_nodes,
        must_cover_ids=must_cover_cluster_ids,
        min_spur_m=1_500.0,
    )
    return polyline


def _merge_nearby_stations(
    lines: list[LinePlan],
    all_stations: dict[str, StationCandidate],
    *,
    merge_radius_m: float,
) -> None:
    """If two stations are within `merge_radius_m` of each other,
    keep the higher-score one and rewrite every line's station_ids
    that referenced the dropped one. Mutates both `lines` and
    `all_stations` in place.

    Called after all lines are built to catch cross-line duplicates —
    two separate-OSM-cluster anchors that ended up geographically
    adjacent get consolidated into a single platform."""
    ids = sorted(all_stations.keys())
    # Build a dedup map: losing_id → winning_id.
    remap: dict[str, str] = {}
    for i, a in enumerate(ids):
        if a in remap:
            continue
        sa = all_stations[a]
        for b in ids[i + 1:]:
            if b in remap:
                continue
            sb = all_stations[b]
            if haversine_m((sa.lat, sa.lon), (sb.lat, sb.lon)) <= merge_radius_m:
                # Keep the higher-score one; if tied, keep the one
                # with more serves/member anchors (proxied by id
                # length for simplicity).
                keep, drop = (a, b) if sa.score >= sb.score else (b, a)
                remap[drop] = keep
    if not remap:
        return
    for L in lines:
        new_ids: list[str] = []
        seen: set[str] = set()
        for sid in L.station_ids:
            target = remap.get(sid, sid)
            if target in seen:
                continue
            seen.add(target)
            new_ids.append(target)
        L.station_ids = new_ids
    for drop in remap:
        all_stations.pop(drop, None)


def _trim_isolated_tails(
    stations: list[StationCandidate],
    *,
    max_gap_m: float,
    protected_names: set[str],
) -> list[StationCandidate]:
    """Drop tail stations at each end of a line whose gap to the
    previous station exceeds `max_gap_m` unless they're in
    `protected_names` (force-anchors + hub). Prevents a line from
    trailing off through empty desert to hit a single distant
    OSM-tagged town with nothing in between."""
    if len(stations) < 3:
        return stations
    # Trim from the end.
    trimmed = list(stations)
    while len(trimmed) >= 3:
        last = trimmed[-1]
        prev = trimmed[-2]
        gap = haversine_m((last.lat, last.lon), (prev.lat, prev.lon))
        if gap <= max_gap_m or last.name in protected_names:
            break
        trimmed.pop()
    # Trim from the start.
    while len(trimmed) >= 3:
        first = trimmed[0]
        nxt = trimmed[1]
        gap = haversine_m((first.lat, first.lon), (nxt.lat, nxt.lon))
        if gap <= max_gap_m or first.name in protected_names:
            break
        trimmed.pop(0)
    return trimmed


def _monotonise_stations(
    stations: list[StationCandidate],
    *,
    hub_pos: np.ndarray,
    axis: np.ndarray,
) -> list[StationCandidate]:
    """Sort stations by their projection onto the line's dominant
    direction.

    Uses the FIRST PRINCIPAL COMPONENT of the station coordinates as
    the sort axis — more reliable than the grid-sweep corridor axis
    (`axis` kwarg) when the line's actual station layout differs
    from the idealised corridor direction (e.g. must-cover endpoints
    pulled the line off-axis). Falls back to `axis` if PCA is
    degenerate. Guarantees the resulting line visits stations in
    strict corridor-direction order — no back-tracking."""
    if len(stations) < 3:
        return stations
    coords = np.array([[s.lat, s.lon] for s in stations])
    centred = coords - coords.mean(axis=0)
    try:
        _u, sigma, vt = np.linalg.svd(centred, full_matrices=False)
        # If the two singular values are comparable, the station set
        # is 2D (probably a ring) and no linear ordering is natural —
        # keep the input order. A ratio > 2× means a clear linear
        # dominant direction.
        if len(sigma) >= 2 and sigma[0] > 2.0 * sigma[1]:
            pc_axis = vt[0]
        else:
            pc_axis = axis  # falls back to the grid-sweep axis
    except Exception:
        pc_axis = axis
    # Ensure consistent orientation: positive projection in the
    # direction the caller's `axis` points, so the final sequence
    # matches the corridor's "positive" end.
    if float(pc_axis @ axis) < 0:
        pc_axis = -pc_axis
    proj: list[tuple[float, StationCandidate]] = [
        (float((np.array([s.lat, s.lon]) - hub_pos) @ pc_axis), s)
        for s in stations
    ]
    proj.sort(key=lambda x: x[0])
    return [s for _a, s in proj]


def _clip_polyline_to_axis_range(
    polyline: list[tuple[float, float]],
    stations: list[StationCandidate],
    *,
    hub_pos: np.ndarray,
    axis: np.ndarray,
) -> list[tuple[float, float]]:
    """Clip `polyline` to the along-axis range spanned by the
    stations. Any polyline vertex projecting outside
    `[min_station_along, max_station_along]` — e.g. a ring-road
    bulge past the terminus — is dropped. The result is guaranteed
    not to extend past either endpoint station in the corridor's
    axis direction."""
    if len(polyline) < 2 or len(stations) < 2:
        return polyline

    station_alongs = [
        float((np.array([s.lat, s.lon]) - hub_pos) @ axis) for s in stations
    ]
    along_min = min(station_alongs)
    along_max = max(station_alongs)

    clipped: list[tuple[float, float]] = []
    for plat, plon in polyline:
        rel = np.array([plat, plon]) - hub_pos
        along = float(rel @ axis)
        if along_min <= along <= along_max:
            clipped.append((plat, plon))

    # Ensure both endpoint stations are represented exactly —
    # prepend the first station's coords and append the last
    # station's coords if the filter removed them.
    first = (stations[0].lat, stations[0].lon)
    last = (stations[-1].lat, stations[-1].lon)
    if not clipped or clipped[0] != first:
        clipped.insert(0, first)
    if clipped[-1] != last:
        clipped.append(last)
    return clipped


def _build_ring_line(
    *,
    road_graph,
    road_nodes: dict,
    cc_nodes: list,
    cc_coords: np.ndarray,
    hub_pos: np.ndarray,
    lines: list[LinePlan],
    all_stations: dict[str, StationCandidate],
    clusters: list[POICluster],
    cluster_nodes: list,
    walk_radius_m: float,
    min_spacing_m: float,
    n_nodes: int,
    radius_fraction: float,
) -> tuple[LinePlan, list[StationCandidate]] | None:
    """Build a suburban ring line:

    1. Find the farthest endpoint across all existing radial lines —
       this gives the network's outer radius.
    2. Multiply by `radius_fraction` (default 0.7) to get the ring
       radius — outside the dense core but inside the outermost
       suburbs.
    3. Sample `n_nodes` angles evenly around the hub. For each, pick
       the arterial node closest to that (angle, radius) point.
    4. Connect consecutive ring nodes via arterial shortest-paths to
       form a closed polyline.
    5. Place stations along the polyline using the same cluster-hit
       + spacing logic as radial lines.

    Returns `(LinePlan, extra_stations)` or None if the graph can't
    form a valid ring."""
    import networkx as nx

    if not lines:
        return None

    # Max endpoint distance from hub across all lines.
    max_dist_deg = 0.0
    for L in lines:
        for sid in (L.station_ids[0], L.station_ids[-1]):
            s = all_stations.get(sid)
            if s is None:
                continue
            d = float(np.linalg.norm(
                np.array([s.lat, s.lon]) - hub_pos
            ))
            if d > max_dist_deg:
                max_dist_deg = d
    if max_dist_deg <= 0:
        return None
    ring_r_deg = max_dist_deg * radius_fraction

    # Sample N angles evenly around the hub.
    ring_node_ids: list = []
    for i in range(n_nodes):
        theta = 2 * math.pi * i / n_nodes
        # (dlat, dlon) offset from hub at angle theta, radius ring_r_deg.
        target_lat = hub_pos[0] + ring_r_deg * math.sin(theta)
        target_lon = hub_pos[1] + ring_r_deg * math.cos(theta)
        # Nearest arterial node in the connected component.
        best = int(np.argmin(
            (cc_coords[:, 0] - target_lat) ** 2
            + (cc_coords[:, 1] - target_lon) ** 2
        ))
        ring_node_ids.append(cc_nodes[best])

    # Deduplicate consecutive ring nodes (adjacent samples can land
    # on the same arterial node if the graph is sparse in that
    # direction).
    dedup: list = []
    for n in ring_node_ids:
        if not dedup or dedup[-1] != n:
            dedup.append(n)
    if len(dedup) < 4:
        return None  # too degenerate to be a ring

    # Close the ring: segment list wraps from last back to first.
    # For each segment, pick the shorter of (a) arterial shortest-
    # path, if within 1.8× the straight-line distance, or (b) a
    # straight-line **viaduct** segment that cuts across the desert /
    # edge-of-city without following any existing RoW. This is the
    # "ring can ignore existing RoW for efficiency" rule — the cost
    # estimator charges the full ring length at $20 M/km (viaduct
    # rate) to reflect the required elevated structure.
    viaduct_factor = 1.8  # arterial path ≤ this × straight-line before it's worth using
    polyline: list[tuple[float, float]] = []
    ring_segments = list(zip(dedup, dedup[1:])) + [(dedup[-1], dedup[0])]
    for u, v in ring_segments:
        u_pos = tuple(road_nodes[u])
        v_pos = tuple(road_nodes[v])
        straight_m = haversine_m(u_pos, v_pos)
        arterial_coords: list[tuple[float, float]] | None = None
        try:
            seg_nodes = nx.shortest_path(
                road_graph, u, v, weight="length_m"
            )
            arterial_m = sum(
                road_graph[a][b].get("length_m", 0.0)
                for a, b in zip(seg_nodes, seg_nodes[1:])
            )
            if arterial_m <= viaduct_factor * straight_m:
                arterial_coords = [tuple(road_nodes[n]) for n in seg_nodes]
        except nx.NetworkXNoPath:
            pass

        if arterial_coords is not None:
            if polyline and polyline[-1] == arterial_coords[0]:
                polyline.extend(arterial_coords[1:])
            else:
                polyline.extend(arterial_coords)
        else:
            # Viaduct shortcut — just u_pos → v_pos as a straight
            # line. No intermediate vertices.
            if not polyline or polyline[-1] != u_pos:
                polyline.append(u_pos)
            polyline.append(v_pos)

    if len(polyline) < 4:
        return None
    # Do NOT run `_collapse_cycles` on the ring — a ring is supposed
    # to close back to its start, and the cycle collapser would
    # destroy that. Intentional loop.

    # Place stations using the common logic. Use a synthetic hub
    # station that's just the last polyline vertex — the ring
    # doesn't need to intersect the hub (by design).
    synthetic_hub = StationCandidate(
        id="ring-anchor",
        name="Ring Anchor",
        lat=float(polyline[0][0]), lon=float(polyline[0][1]),
        archetype="interchange",
        score=0.0,
        serves=("ring-anchor",),
    )
    line_stations = _place_stations_on_polyline(
        polyline=polyline,
        clusters=clusters,
        walk_radius_m=walk_radius_m,
        min_spacing_m=min_spacing_m,
        hub_station=synthetic_hub,
        existing=all_stations,
    )
    # Drop the synthetic anchor from the output stations.
    line_stations = [s for s in line_stations if s.id != "ring-anchor"]
    if len(line_stations) < 4:
        return None

    # For a ring, don't monotonise along a single axis — the order
    # of polyline traversal is the visit order.
    ring_line = LinePlan(
        id="line-ring", name="Ring Line",
        station_ids=[s.id for s in line_stations],
        axis_dlat=0.0, axis_dlon=0.0,
        polyline=[(float(p[0]), float(p[1])) for p in polyline],
    )
    return ring_line, line_stations


def _insert_greenfield_spurs(
    polyline: list[tuple[float, float]],
    path: list,
    road_nodes: dict,
    *,
    clusters: list[POICluster],
    cluster_nodes: list,
    must_cover_ids: list[int],
    min_spur_m: float,
) -> None:
    """For each must-cover cluster whose nearest arterial node is
    ≥ `min_spur_m` from the cluster's actual position, insert the
    cluster position into `polyline` right after that arterial
    node. This produces a straight "greenfield" segment connecting
    the existing road network to the under-construction suburb.

    Mutates `polyline` in place. No-op for clusters that happen to
    sit on an arterial already."""
    for cidx in must_cover_ids:
        node = cluster_nodes[cidx]
        if node not in path:
            continue
        node_pos = tuple(road_nodes[node])
        cluster = clusters[cidx]
        cluster_pos = (float(cluster.lat), float(cluster.lon))
        dist = haversine_m(node_pos, cluster_pos)
        if dist < min_spur_m:
            continue
        # Find the node's position in the path (first occurrence).
        path_idx = path.index(node)
        # Insert cluster_pos right after that node in the polyline.
        # Avoid duplicate insertion if we've run this for the same
        # cluster already (subsequent calls will short-circuit via
        # the `< min_spur_m` guard since the polyline now contains
        # cluster_pos).
        # Check if cluster_pos already in polyline near that index.
        insert_at = path_idx + 1
        if insert_at < len(polyline) and polyline[insert_at] == cluster_pos:
            continue
        polyline.insert(insert_at, cluster_pos)


def _collapse_cycles(path: list) -> list:
    """If a node appears twice in `path`, remove the subpath between
    the two occurrences (which is the out-and-back loop). Repeats
    until every node occurs at most once."""
    while True:
        first_at: dict = {}
        loop_start = -1
        loop_end = -1
        for i, n in enumerate(path):
            if n in first_at:
                loop_start = first_at[n]
                loop_end = i
                break
            first_at[n] = i
        if loop_start < 0:
            return path
        path = path[: loop_start + 1] + path[loop_end + 1:]


def _trim_dry_tails(
    path: list,
    road_nodes: dict,
    *,
    clusters: list[POICluster],
    walk_radius_deg: float,
) -> list:
    """Pop nodes off each end of `path` that have no cluster within
    `walk_radius_deg` (rough-degrees). Prevents the suburban-extend
    step from leaving a dangling tail that runs into empty land
    beyond the last residential pocket."""
    if len(path) < 3:
        return path

    def _has_cluster(node) -> bool:
        pos = np.array(road_nodes[node])
        for c in clusters:
            if abs(pos[0] - c.lat) > walk_radius_deg:
                continue
            if abs(pos[1] - c.lon) > walk_radius_deg:
                continue
            dlat = pos[0] - c.lat
            dlon = pos[1] - c.lon
            if dlat * dlat + dlon * dlon <= walk_radius_deg * walk_radius_deg:
                return True
        return False

    # Trim end.
    while len(path) >= 3 and not _has_cluster(path[-1]):
        path.pop()
    # Trim start.
    while len(path) >= 3 and not _has_cluster(path[0]):
        path.pop(0)
    return path


def _extend_along_axis(
    path: list,
    road_graph,
    road_nodes: dict,
    *,
    axis: np.ndarray,
    direction: int,  # +1 extends the tail, -1 extends the head (call after reversing)
    max_extend_m: float,
) -> list:
    """Greedy walk outward from `path[-1]` along arterials, picking
    whichever unvisited neighbour maximises the axis-direction
    projection gain. Stops at `max_extend_m` or when no neighbour
    moves further in the axis direction (dead end / arterial
    runs out). Mutates and returns `path`."""
    if not path:
        return path
    visited = set(path)
    current = path[-1]
    extended_m = 0.0
    while extended_m < max_extend_m:
        best_next = None
        best_gain = 0.0
        cur_pos = np.array(road_nodes[current])
        for nb in road_graph.neighbors(current):
            if nb in visited:
                continue
            delta = np.array(road_nodes[nb]) - cur_pos
            gain = direction * float(delta @ axis)
            if gain > best_gain:
                best_gain = gain
                best_next = nb
        if best_next is None:
            break
        seg_m = haversine_m(road_nodes[current], road_nodes[best_next])
        if extended_m + seg_m > max_extend_m:
            break
        path.append(best_next)
        visited.add(best_next)
        extended_m += seg_m
        current = best_next
    return path


# --------------------------------------------------------------------------
# Station placement along a corridor polyline
# --------------------------------------------------------------------------


def _place_stations_on_polyline(
    *,
    polyline: list[tuple[float, float]],
    clusters: list[POICluster],
    walk_radius_m: float,
    min_spacing_m: float,
    hub_station: StationCandidate,
    existing: dict[str, StationCandidate],
) -> list[StationCandidate]:
    """Return the ordered list of stations for a line whose track
    follows `polyline`.

    For each cluster, find the polyline vertex closest to it. If that
    distance is ≤ `walk_radius_m`, the cluster is a candidate station
    anchored at that vertex. Candidates are ordered by along-polyline
    distance; pairs closer than `min_spacing_m` keep only the higher-
    weight cluster.

    The `hub_station` is always inserted at the polyline vertex
    nearest its position (which, by construction, is on the polyline)
    so every line shares the hub — delivering 100% transfer
    reachability."""
    if len(polyline) < 2:
        return []

    # Cumulative along-polyline distance for each vertex.
    cum = [0.0]
    for i in range(1, len(polyline)):
        cum.append(cum[-1] + haversine_m(polyline[i - 1], polyline[i]))

    def _closest_vertex(lat: float, lon: float) -> tuple[int, float]:
        """Return (polyline_index, distance_m) of the closest vertex."""
        best_i = 0
        best_d = float("inf")
        for i, pt in enumerate(polyline):
            d = haversine_m(pt, (lat, lon))
            if d < best_d:
                best_d, best_i = d, i
        return best_i, best_d

    # Candidate stations: one per cluster within walk_radius_m of the
    # polyline (measured to closest vertex).
    @dataclass
    class _Candidate:
        along_m: float
        cluster: POICluster
        vertex_idx: int

    cands: list[_Candidate] = []
    for c in clusters:
        vi, d = _closest_vertex(c.lat, c.lon)
        if d <= walk_radius_m:
            cands.append(_Candidate(
                along_m=cum[vi], cluster=c, vertex_idx=vi,
            ))

    # Insert the hub as a candidate (always included).
    hub_vi, _ = _closest_vertex(hub_station.lat, hub_station.lon)
    cands.append(_Candidate(
        along_m=cum[hub_vi],
        cluster=POICluster(
            lat=hub_station.lat, lon=hub_station.lon,
            weight=hub_station.score,
            primary_name=hub_station.name,
            primary_kind="interchange",
            member_names=[hub_station.name],
        ),
        vertex_idx=hub_vi,
    ))

    cands.sort(key=lambda x: x.along_m)

    # Enforce spacing: walk along, drop a candidate if too close to
    # the previously-kept one. The interchange/hub candidate is
    # **never** dropped — every line must share the hub for 100 %
    # transfer reachability. A higher-weight neighbour evicts a
    # lower-weight earlier pick; the hub is immune both ways.
    kept: list[_Candidate] = []
    for c in cands:
        is_hub = c.cluster.primary_kind == "interchange"
        if kept and c.along_m - kept[-1].along_m < min_spacing_m:
            prev_is_hub = kept[-1].cluster.primary_kind == "interchange"
            if is_hub and not prev_is_hub:
                kept[-1] = c  # hub evicts the squashed neighbour
                continue
            if prev_is_hub:
                continue  # skip this candidate, hub stays
            if c.cluster.weight > kept[-1].cluster.weight:
                kept[-1] = c
            continue
        kept.append(c)

    # Materialise into StationCandidate objects.
    out: list[StationCandidate] = []
    for k in kept:
        # Hub re-uses the existing hub_station exactly.
        if k.cluster.primary_kind == "interchange":
            out.append(hub_station)
            continue
        sid = _slug(k.cluster.primary_name) or f"sta-{k.vertex_idx}"
        # Avoid id collision with an earlier line's station.
        if sid in existing and existing[sid].name != k.cluster.primary_name:
            sid = f"{sid}-{k.vertex_idx}"
        if sid in existing:
            out.append(existing[sid])
            continue
        lat, lon = polyline[k.vertex_idx]
        out.append(StationCandidate(
            id=sid,
            name=k.cluster.primary_name,
            lat=float(lat), lon=float(lon),
            archetype=_archetype_for_seed(k.cluster.primary_kind),
            score=float(k.cluster.weight),
            serves=(sid,),
        ))
    return out


# --------------------------------------------------------------------------
# Small helpers (local copies to avoid circular imports)
# --------------------------------------------------------------------------


def _unit_vec(angle_deg: float) -> np.ndarray:
    r = math.radians(angle_deg)
    return np.array([math.sin(r), math.cos(r)])


def _angle_sep(a: float, b: float) -> float:
    d = abs(a - b) % 180.0
    return min(d, 180.0 - d)


def _polyline_length_m(polyline: list[tuple[float, float]]) -> float:
    total = 0.0
    for a, b in zip(polyline, polyline[1:]):
        total += haversine_m(a, b)
    return total


def _pick_n_lines(
    n_clusters: int,
    max_lines: int | None,
    population: int | None = None,
) -> int:
    """Scale line count with both cluster count and population. Small
    cities need ~3-5 lines, metros (Baghdad / Cairo / Tehran) need
    12-20. Tokyo-class cities cap at 25. Redundancy + min-length
    filters further trim so the *actual* output count is often
    lower than this ceiling."""
    cluster_term = round(n_clusters / 15)
    pop_term = 0 if not population else round(population / 500_000) + 2
    # Take the larger of the two heuristics so neither dense-data
    # small cities nor sparse-data big cities are under-planned.
    n = max(2, cluster_term, pop_term)
    if max_lines is not None:
        return max(2, min(n, max_lines))
    # Soft cap: 25 for mega-metros. Population > 12 M already hits
    # this and means the batch probably needs a bespoke config
    # rather than the default auto-planner.
    return min(n, 25)
