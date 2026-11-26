"""Search one urban interconnector against residual mapped pedestrian coverage."""

from collections import Counter
from itertools import pairwise

import numpy as np
from scipy.spatial import cKDTree
from shapely import LineString, Polygon, contains_xy

from . import central_access, coverage_trunks, holistic_network as rail, holistic_through as axes
from .straight_through_layout import _tigris

GAP_LINE_ID = "U01"
GAP_ROLE = "urban-gap"
MIN_URBAN_PLATFORM_SPACING_M = axes.STOP_SPACING_M
MAX_URBAN_PLATFORM_GAP_M = axes.MAX_STOP_GAP_M
MAX_SCREENED_AXES = 480
MAX_EXACT_AXES = 24
PLATFORM_SAMPLE_M = 125


def _outer(network):
    outer = network["lines"].get(coverage_trunks.RINGS[-1])
    return None if not outer or not outer["loop"] else Polygon(rail.Track(outer["geometry"]).points)


def _population_walk(walks, population):
    return np.where(population.offsets_m <= central_access.SNAP_M,
                    walks[population.nodes] + population.offsets_m, np.inf)


def _demand_tiles(population, residual):
    xy = population.coordinates[residual] * rail.LOCAL_METRES
    weights = population.counts[residual]
    if not len(xy):
        return np.empty((0, 2)), np.empty(0)
    _, groups = np.unique(np.floor(xy / 1000).astype(int), axis=0, return_inverse=True)
    people = np.bincount(groups, weights=weights)
    centers = np.column_stack([np.bincount(groups, weights=weights * xy[:, axis]) / people for axis in range(2)])
    order = np.argsort(-people, kind="stable")[:axes.DEMAND_CELL_LIMIT]
    return centers[order], people[order]


def _ranked_pairs(groups):
    ordered = sorted(groups.items(), key=lambda entry: (-entry[1][0][0], entry[0]))
    for depth in range(max((len(rows) for _, rows in ordered), default=0)):
        for _, rows in ordered:
            if depth < len(rows):
                yield rows[depth]


def _intermediate_crossings(track, tracks, network, graph, context, station_tree):
    crossings = []
    prior = np.array((), dtype=float)
    for km, code, point in axes._candidate_crossings(track, tracks, network, graph, context):
        near = rail._stations_at_crossing(network["stations"], point)
        if not near:
            near_distance, _ = station_tree.query(np.asarray(point) * rail.LOCAL_METRES)
            if near_distance < MIN_URBAN_PLATFORM_SPACING_M:
                continue
        if not np.any(np.abs(prior - km) * 1000 < MIN_URBAN_PLATFORM_SPACING_M):
            prior = np.append(prior, km)
            crossings.append((km, code, point))
    return crossings


def _new_platforms(track, crossings, station_tree, graph, context, demand, weights):
    """Choose connected sequences of street-linked station positions between fixed calls."""
    samples = np.arange(PLATFORM_SAMPLE_M / 1000, track.km, PLATFORM_SAMPLE_M / 1000)
    sites = [track.at(float(km)) for km in samples]
    if not sites:
        return []
    coordinates = np.asarray(sites) * rail.LOCAL_METRES
    access = graph[3].query(coordinates)[0]
    separated = station_tree.query(coordinates)[0] >= MIN_URBAN_PLATFORM_SPACING_M
    valid = (access <= central_access.SNAP_M) & separated & rail.dry_points(sites, context)
    heaps = cKDTree(demand).query_ball_point(coordinates[valid], coverage_trunks.WALK_M)
    gain = np.array([weights[cells].sum() for cells in heaps], dtype=float)
    gain /= max(float(gain.max(initial=0)), 1.)
    calls = [0., *(km for km, _, _ in crossings), track.km]
    stops = []
    for start, end in pairwise(calls):
        use = (samples[valid] > start) & (samples[valid] < end)
        path = np.r_[start, samples[valid][use], end]
        benefits = np.r_[0., gain[use], 0.]
        parents = np.full(len(path), -1)
        scores = np.full(len(path), -np.inf)
        scores[0] = 0.
        for i in range(1, len(path)):
            span = (path[i] - path[:i]) * 1000
            feasible = np.flatnonzero((span >= MIN_URBAN_PLATFORM_SPACING_M - 1e-6)
                                      & (span <= MAX_URBAN_PLATFORM_GAP_M + 1e-6) & np.isfinite(scores[:i]))
            if not len(feasible):
                continue
            # Penalise short redundant hops and excessive walking between calls.
            options = scores[feasible] - .35 * ((span[feasible] - 1_350) / 1000)**2
            winner = int(options.argmax())
            parents[i] = feasible[winner]
            scores[i] = options[winner] + benefits[i] * .4 - .35
        if parents[-1] < 0:
            return []
        interval = []
        index = int(parents[-1])
        while index:
            interval.append(float(path[index]))
            index = int(parents[index])
        stops.extend(reversed(interval))
    return stops


def _water_evidence(track, context, water, river, bridges):
    if sum(len(river.intersections(a, b)[1]) for a, b in pairwise(track.points)) > 1:
        return None
    contacts = []
    for a, b in pairwise(track.points):
        evidence = axes._water_screen(a, b, context, water, bridges)
        if evidence is None:
            return None
        contacts.extend(evidence)
    return contacts


def _parallel_duplicate(track, tracks):
    return any(coverage_trunks._parallel_share(track, existing) > coverage_trunks.MAX_PARALLEL_SHARE
               for code, existing in tracks.items() if code != GAP_LINE_ID)


def _new_sites(candidate, network):
    line = candidate["lines"][GAP_LINE_ID]
    return {site: candidate["stations"][site]["coordinates"]
            for site in line["station_ids"] if site not in network["stations"]}


def validate_gap_line(network, graph, context):
    """Independently check the geometry, exact transfers and station spacing of U01."""
    line = network["lines"].get(GAP_LINE_ID)
    if line is None or line.get("service_role") != GAP_ROLE or line["loop"]:
        raise ValueError("The urban gap service requires one open line with the urban-gap role")
    rail.validate(network)
    track = rail.Track(line["geometry"])
    outer = _outer(network)
    geometry = LineString(track.points)
    chord = LineString(track.points[[0, -1]])
    if (outer is None or not outer.covers(geometry) or not geometry.is_simple
            or geometry.hausdorff_distance(chord) > .01
            or not axes.MIN_LENGTH_M <= track.km * 1000 <= axes.MAX_LENGTH_M):
        raise ValueError("The urban gap service needs one direct bounded alignment inside the outer ring")
    stations = network["stations"]
    memberships = {site: set(stations[site]["lines"]) - {GAP_LINE_ID} for site in line["station_ids"]}
    exact = {}
    for site, routes in memberships.items():
        point = np.asarray(stations[site]["coordinates"])
        if routes and track.locate(point)[1] <= rail.EXACT_CROSSING_M:
            connected = [code for code in sorted(routes)
                         if rail.Track(network["lines"][code]["geometry"]).locate(point)[1] <= rail.EXACT_CROSSING_M]
            if connected:
                exact[site] = connected
    connections = sorted({code for routes in exact.values() for code in routes})
    if len(exact) < 2 or len(connections) < 2:
        raise ValueError("The urban gap service needs two exact shared station sites and two onward routes")
    chainage = np.array([line["station_chainage_km"][site] for site in line["station_ids"]]) * 1000
    gaps = np.diff(chainage)
    coordinates = np.asarray([stations[site]["coordinates"] for site in line["station_ids"]])
    if (np.any(gaps < MIN_URBAN_PLATFORM_SPACING_M - 1e-5)
            or np.any(gaps > MAX_URBAN_PLATFORM_GAP_M + 1e-5)
            or not rail.dry_points(coordinates, context).all()
            or (graph[3].query(coordinates * rail.LOCAL_METRES)[0] > central_access.SNAP_M).any()):
        raise ValueError("The urban gap service has an inaccessible, wet or poorly spaced station")
    all_points = np.asarray([row["coordinates"] for row in stations.values()]) * rail.LOCAL_METRES
    new_points = coordinates[[not memberships[site] for site in line["station_ids"]]] * rail.LOCAL_METRES
    if len(new_points) and (cKDTree(all_points).query(new_points, k=2)[0][:, 1] < MIN_URBAN_PLATFORM_SPACING_M - 1e-5).any():
        raise ValueError("An urban gap station duplicates a nearby existing site")
    tracks = {code: rail.Track(row["geometry"]) for code, row in network["lines"].items()}
    if _parallel_duplicate(track, tracks):
        raise ValueError("The urban gap service duplicates a close parallel railway")
    _, bridges = axes._street_layers(context)
    chord_track = rail.Track(track.coordinates[[0, -1]])
    water = _water_evidence(chord_track, context, axes.WaterGeometry.from_context(context), _tigris(context), bridges)
    if water is None:
        raise ValueError("The urban gap service lacks mapped water-crossing evidence")
    return {"shared_station_ids": list(exact), "connected_route_ids": connections, "mapped_water_contacts": water}


def add_gap_line(network, graph, context, populations):
    """Select one inside-ring line by its actual pedestrian reach in both population grids."""
    audit = {"base_candidate_id": network["candidate_id"], "selected": None, "screened": 0,
             "exactly_evaluated": 0, "rejections": {}}
    outer = _outer(network)
    if outer is None or GAP_LINE_ID in network["lines"]:
        return network, audit | {"held": "Need a closed outer ring and an unused urban line ID."}
    rail.validate(network)
    sites = {code: row["coordinates"] for code, row in network["stations"].items()}
    old, _ = central_access.distances_from_stops(sites, graph)
    residuals = {key: _population_walk(old, population) > coverage_trunks.WALK_M
                 for key, population in populations.items()}
    inside = {key: contains_xy(outer, *(population.coordinates * rail.LOCAL_METRES).T)
              for key, population in populations.items()}
    primary = "worldpop-2026"
    snapped = populations[primary].offsets_m <= central_access.SNAP_M
    demand, weights = _demand_tiles(populations[primary], residuals[primary] & inside[primary] & snapped)
    if len(demand) < 2:
        return network, audit | {"held": "No two populated residual cells inside the outer ring."}
    station_ids = sorted(sites)
    locations = np.asarray([sites[site] for site in station_ids])
    points = locations * rail.LOCAL_METRES
    station_tree = cKDTree(points)
    allowed = (contains_xy(outer.buffer(1e-6), *points.T) & rail.dry_points(locations, context)
               & (graph[3].query(points)[0] <= central_access.SNAP_M))
    ids = [station_ids[i] for i in np.flatnonzero(allowed)]
    groups = axes._pair_options(points[allowed], [set(network["stations"][key]["lines"]) for key in ids],
                                demand, weights)
    tracks = {code: rail.Track(row["geometry"]) for code, row in network["lines"].items()}
    _, bridges = axes._street_layers(context)
    water, river = axes.WaterGeometry.from_context(context), _tigris(context)
    rejected = Counter()
    finalists = []
    for _score, first, second, _bearing, _length in _ranked_pairs(groups):
        if audit["screened"] >= MAX_SCREENED_AXES or len(finalists) >= MAX_EXACT_AXES:
            break
        audit["screened"] += 1
        terminals = [ids[first], ids[second]]
        geometry = [sites[stop] for stop in terminals]
        track = rail.Track(geometry)
        if not outer.covers(LineString(track.points)):
            rejected["leaves_outer_ring"] += 1
            continue
        if _parallel_duplicate(track, tracks):
            rejected["parallel_duplication"] += 1
            continue
        wet = _water_evidence(track, context, water, river, bridges)
        if wet is None:
            rejected["water_crossing_unproved"] += 1
            continue
        crossings = _intermediate_crossings(track, tracks, network, graph, context, station_tree)
        terminal_link_only = not crossings
        if terminal_link_only and track.km > rail.MAX_TERMINAL_LINK_KM:
            rejected["no_intermediate_transfer"] += 1
            continue
        calls = _new_platforms(track, crossings, station_tree, graph, context, demand, weights)
        if not calls:
            rejected["no_spaced_street_linked_platforms"] += 1
            continue
        addition = {
            "id": GAP_LINE_ID, "name": "Baghdad urban gap line", "geometry": geometry,
            "terminal_ids": terminals, "terminal_link_only": terminal_link_only,
            "required_interchanges": [{"line_id": code, "point": list(point)} for _, code, point in crossings],
            "stops": [{"id": f"{GAP_LINE_ID}-S{index:02d}", "name": f"Urban access · km {km:g}", "chainage_km": km}
                      for index, km in enumerate(calls, 1)],
            "basis": "Bounded direct elevated search within the outer ring, ranked by mapped residual walking access",
        }
        try:
            revised = rail.insert_through_lines(network, [addition], graph=graph, context=context)
        except ValueError:
            rejected["inconsistent_interchange"] += 1
            continue
        revised["lines"][GAP_LINE_ID]["service_role"] = GAP_ROLE
        rail._identity(revised)
        distances, _ = central_access.distances_from_stops(_new_sites(revised, network), graph)
        gained, urban_gain = {}, {}
        for key, population in populations.items():
            reached = (_population_walk(distances, population) <= coverage_trunks.WALK_M) & residuals[key]
            gained[key] = float(population.counts[reached].sum())
            urban_gain[key] = float(population.counts[reached & inside[key]].sum())
        if not min(urban_gain.values()):
            rejected["no_joint_population_gain"] += 1
            continue
        shares = [urban_gain[key] / float(population.counts[inside[key]].sum())
                  for key, population in populations.items()]
        key = (-min(shares), -sum(shares), track.km, len(calls), terminals)
        finalists.append((key, revised, gained, urban_gain))
    audit.update(exactly_evaluated=len(finalists), rejections=dict(sorted(rejected.items())))
    if not finalists:
        return network, audit | {"held": "No candidate jointly clears geometry, transfer and walking-access screens."}
    _, revised, gains, urban = min(finalists, key=lambda row: row[0])
    proof = validate_gap_line(revised, graph, context)
    return revised, audit | {
        "selected": proof | {
            "line_id": GAP_LINE_ID, "route_km": round(revised["lines"][GAP_LINE_ID]["one_way_km"], 2),
            "new_station_sites": len(_new_sites(revised, network)),
            "newly_reached": {key: round(value) for key, value in gains.items()},
            "newly_reached_inside_outer_ring": {key: round(value) for key, value in urban.items()},
        },
        "planning_limits": {
            "min_station_spacing_m": MIN_URBAN_PLATFORM_SPACING_M, "max_station_gap_m": MAX_URBAN_PLATFORM_GAP_M,
            "screen_budget": MAX_SCREENED_AXES, "exact_walk_budget": MAX_EXACT_AXES,
        },
        "survey_holds": ["Confirm alignment, level and rail curve at interchange, rights of way, navigation clearances, "
                         "walk entrances, turnback and operating capacity before engineering acceptance."],
    }
