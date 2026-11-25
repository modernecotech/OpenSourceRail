"""Generate connected Baghdad rail trials through residual population gaps."""

from collections import defaultdict
from itertools import combinations
from math import cos, radians

import numpy as np
from scipy.spatial import cKDTree

from . import holistic_gaps, holistic_grid, holistic_network, holistic_through, rail_duplication
from .central_access import SNAP_M
from .holistic_network import LOCAL_METRES, MAX_TERMINAL_LINK_KM, Track, dry_points

GAP_TILE_M = 4000
MAX_GAPS = 12
MAX_WAYPOINTS = 5
MAX_NEAREST_ANCHORS = 60
MAX_TRIALS_PER_GAP = 96
MAX_CANDIDATES_PER_GAP = 8
MIN_CHORD_M = 3400
MAX_LENGTH_M = 18_000
MIN_LEG_M = 1300
MAX_TURN_DEGREES = 58
MAX_DIRECTNESS = 1.16
DUPLICATION_SETTINGS = dict(sample_m=100, nearby_m=1000, common_m=10, min_run_m=2000,
                            max_angle_deg=25, terminal_m=250)


def _parallel_runs(code, track, retained):
    return [run for other, existing in retained.items()
            for run in rail_duplication._pair_runs(code, other, track, existing, **DUPLICATION_SETTINGS)]


def parallel_runs(candidate, lines):
    """Apply the sustained-parallel screen to a trial and the specified comparison lines."""
    code = candidate["id"]
    retained = {key: rail_duplication._Alignment(line, DUPLICATION_SETTINGS["sample_m"])
                for key, line in lines.items() if key != code}
    probe = rail_duplication._Alignment(candidate, DUPLICATION_SETTINGS["sample_m"])
    return _parallel_runs(code, probe, retained)


def _waypoints(gap, cells, context, water):
    local = sorted(cells, key=lambda row: (-row["beyond_1200_m"], row["coordinates"]))
    west, south, east, north = gap["bounds_wsen"]
    sites = [gap["coordinates"], *(row["coordinates"] for row in local
                                  if west <= row["coordinates"][0] < east
                                  and south <= row["coordinates"][1] < north)]
    result = []
    for point, dry in zip(sites, dry_points(sites, context), strict=True):
        xy = np.asarray(point) * LOCAL_METRES
        # The leg intersection test excludes endpoints. Keep a bend off an
        # actual water edge so a crossing cannot disappear at the leg split.
        close = (np.all(xy >= np.minimum(water.starts, water.ends) - 1, axis=1)
                 & np.all(xy <= np.maximum(water.starts, water.ends) + 1, axis=1))
        vector = water.ends[close] - water.starts[close]
        shifts = xy - water.starts[close]
        fraction = np.clip((shifts * vector).sum(axis=1) / (vector * vector).sum(axis=1), 0, 1)
        on_water_edge = np.any(np.linalg.norm(shifts - fraction[:, None] * vector, axis=1) <= 1)
        if dry and not on_water_edge and all(np.linalg.norm(xy - old) >= 300 for old in result):
            result.append(xy)
        if len(result) == MAX_WAYPOINTS:
            break
    return result


def _trial_paths(waypoints, stations, station_lines, demand, weights):
    """Find modest bends through each demand waypoint, then score both legs."""
    ranked = []
    for waypoint in waypoints:
        station_distances = np.linalg.norm(stations - waypoint, axis=1)
        anchors = [i for i in np.argsort(station_distances, kind="stable")
                   if MIN_LEG_M <= station_distances[i] <= MAX_LENGTH_M - MIN_LEG_M][:MAX_NEAREST_ANCHORS]
        pairs = np.asarray([(a, b) for a, b in combinations(sorted(anchors), 2)
                            if station_lines[a].isdisjoint(station_lines[b])], dtype=int).reshape(-1, 2)
        first, last = stations[pairs[:, 0]], stations[pairs[:, 1]]
        legs = np.stack((waypoint - first, last - waypoint), axis=1)
        lengths = np.linalg.norm(legs, axis=2)
        direction = legs / lengths[:, :, None]
        chord = np.linalg.norm(last - first, axis=1)
        total = lengths.sum(axis=1)
        cosine = np.einsum("ij,ij->i", direction[:, 0], direction[:, 1])
        eligible = ((chord >= MIN_CHORD_M) & (total <= MAX_LENGTH_M) & (total <= chord * MAX_DIRECTNESS)
                    & (cosine >= cos(radians(MAX_TURN_DEGREES))) & (cosine <= cos(radians(4))))
        for rows in np.array_split(np.flatnonzero(eligible), max(1, (int(eligible.sum()) + 199) // 200)):
            starts = np.stack((first[rows], np.broadcast_to(waypoint, first[rows].shape)), axis=1)
            shifts = demand[None, None, :, :] - starts[:, :, None, :]
            heading = direction[rows, :, None, :]
            chain = np.clip((shifts * heading).sum(axis=3), 0, lengths[rows, :, None])
            lateral = np.linalg.norm(shifts - chain[:, :, :, None] * heading, axis=3)
            on_route = (chain[:, 0] >= 650) & (chain[:, 1] <= lengths[rows, 1, None] - 650)
            gain = np.where(on_route, np.maximum(1 - lateral.min(axis=1) / 1200, 0), 0) * weights
            gain = gain.sum(axis=1)
            for row, score in zip(rows, gain, strict=True):
                if score <= 0:
                    continue
                a, b = map(int, pairs[row])
                angle = np.degrees(np.arctan2(*(last[row] - first[row])[::-1])) % 180
                ranked.append((float(score / (total[row] / 1000)), a, b, float(angle), waypoint))
    families = defaultdict(list)
    for trial in sorted(ranked, key=lambda row: (-row[0], row[1], row[2])):
        families[int(trial[3] // 30)].append(trial)
    # Reserve trials in different directions before screening near variants.
    active = sorted(families.values(), key=lambda trials: -trials[0][0])
    for index in range(max(map(len, active), default=0)):
        yield from (trials[index] for trials in active if index < len(trials))


def _descriptor(code, gap, trial, geometry, network, ids, tracks, station_tree, context, graph, resources):
    road_share, near_share, water_contacts = resources
    score, a, b, bearing, _ = trial
    terminals = [ids[a], ids[b]]
    coordinates = (geometry / LOCAL_METRES).tolist()
    for index, stop in zip((0, -1), terminals, strict=True):
        coordinates[index] = network["stations"][stop]["coordinates"]
    track = Track(coordinates)
    crossings = holistic_through._candidate_crossings(track, tracks, network, graph, context)
    if not crossings and track.km > MAX_TERMINAL_LINK_KM:
        return None
    platforms = holistic_through._platforms(track, crossings, station_tree, graph, context)
    if not platforms:
        return None
    names = [network["stations"][stop].get("name") or stop for stop in terminals]
    return {
        "id": code, "key": code, "name": "–".join(names), "geometry": coordinates,
        "terminal_ids": terminals, "one_way_km": track.km,
        "directness": float(track.chainage[-1] / np.linalg.norm(track.points[-1] - track.points[0])),
        "basis": "Elevated corridor trial through a residual 1,200 m walking-access gap",
        "stops": [{"id": f"{code}-S{i:02d}", "name": f"New station · km {km:g}", "chainage_km": km,
                   "coordinates": track.at(km), "street_offset_m": round(offset, 1),
                   "basis": "Dry alignment position near a retained pedestrian graph node"}
                  for i, (km, offset) in enumerate(platforms, 1)],
        "terminal_link_only": not crossings,
        "required_interchanges": [{"line_id": line, "point": list(point), "chainage_km": km}
                                  for km, line, point in crossings],
        "screening": {
            "seed_gap_id": gap["id"], "seed_gap_population_beyond_1200_m": gap["beyond_1200_m"],
            "seed_waypoint": (geometry[1] / LOCAL_METRES).tolist(),
            "demand_proxy_basis": "Uncovered WorldPop residents in 1 km cells near the alignment",
            "proxy_residents_per_route_km": round(score, 2),
            "axis_bearing_degrees": round(bearing, 2),
            "major_surface_road_share": round(road_share, 3),
            "near_existing_rail_share": round(near_share, 3),
            "mapped_water_contacts": water_contacts,
            "sustained_parallel_screen": DUPLICATION_SETTINGS.copy(),
            "alignment_limits": "Survey, curves, bridge clearances, land take and accessible entrances require verification.",
        },
    }


def generate(network, context, graph, *, coverage_cells, max_candidates=48, gap_ids=None):
    """Screen fresh gap-led axes for exact walk-access and railway comparison.

    The caller supplies coverage measured against the same network that provides
    rail anchors. Optional gap IDs restrict the search to selected 4 km tiles.
    Candidate IDs are local to each returned pool.
    """
    if type(max_candidates) is not int or max_candidates < 0:
        raise ValueError("Candidate limit must be a nonnegative integer")
    if max_candidates == 0:
        return []
    gaps = holistic_gaps.prioritize(coverage_cells, network, tile_m=GAP_TILE_M)
    if gap_ids is not None:
        requested = set(gap_ids)
        gaps = [gap for gap in gaps if gap["id"] in requested]
    gaps = gaps[:MAX_GAPS]
    if not gaps:
        return []
    cells = sorted((cell for cell in coverage_cells if cell["beyond_1200_m"] > 0),
                   key=lambda row: (row["coordinates"], row["beyond_1200_m"]))
    demand = np.asarray([cell["coordinates"] for cell in cells]) * LOCAL_METRES
    weights = np.asarray([cell["beyond_1200_m"] for cell in cells])
    ids = sorted(network["stations"])
    stations = np.asarray([network["stations"][stop]["coordinates"] for stop in ids])
    station_tree = cKDTree(stations * LOCAL_METRES)
    eligible = (graph[3].query(stations * LOCAL_METRES)[0] <= SNAP_M) & dry_points(stations, context)
    stations = stations[eligible] * LOCAL_METRES
    ids = [stop for stop, keep in zip(ids, eligible, strict=True) if keep]
    station_lines = [set(network["stations"][key]["lines"]) for key in ids]
    tracks = {code: Track(line["geometry"]) for code, line in network["lines"].items()}
    retained = {code: rail_duplication._Alignment(line, DUPLICATION_SETTINGS["sample_m"])
                for code, line in network["lines"].items()}
    rail = cKDTree(np.concatenate([line.samples for line in retained.values()]))
    roads, bridges = holistic_through._street_layers(context)
    water = holistic_through.WaterGeometry.from_context(context)

    accepted = []
    for gap in gaps:
        waypoints = _waypoints(gap, cells, context, water)
        near_gap = np.linalg.norm(demand - np.asarray(gap["coordinates"]) * LOCAL_METRES, axis=1) <= MAX_LENGTH_M
        trials = _trial_paths(waypoints, stations, station_lines, demand[near_gap], weights[near_gap])
        accepted.append([])
        for index, trial in enumerate(trials):
            if index >= MAX_TRIALS_PER_GAP or len(accepted[-1]) == MAX_CANDIDATES_PER_GAP:
                break
            _, a, b, _, waypoint = trial
            geometry = np.asarray([stations[a], waypoint, stations[b]])
            if any(min(np.linalg.norm(geometry - prior, axis=1).max(),
                       np.linalg.norm(geometry - prior[::-1], axis=1).max()) < 850 for prior, _ in accepted[-1]):
                continue
            screen = holistic_grid._screen_geometry(geometry, context, roads, bridges, water, rail)
            if screen is None:
                continue
            code = f"D-{gap['id'][2:]}-{index + 1:02d}"
            if code in retained:
                continue
            candidate = _descriptor(code, gap, trial, geometry, network, ids, tracks,
                                    station_tree, context, graph, screen)
            if candidate is None:
                continue
            probe = rail_duplication._Alignment(candidate, DUPLICATION_SETTINGS["sample_m"])
            if _parallel_runs(code, probe, retained):
                continue
            try:
                holistic_network.insert_through_lines(network, [candidate], graph=graph, context=context)
            except ValueError:
                continue
            accepted[-1].append((geometry, candidate))
    return [row for index in range(MAX_CANDIDATES_PER_GAP) for options in accepted
            for _, row in options[index:index + 1]][:max_candidates]
