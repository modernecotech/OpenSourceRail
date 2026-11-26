"""Build new end-to-end Baghdad trunks from mapped constraints and population."""

from collections import Counter
from copy import deepcopy
from itertools import combinations, product
from math import cos, radians

import numpy as np
from scipy.spatial import cKDTree
from shapely import LineString, Point, Polygon, distance, intersects_xy, points

from . import holistic_grid, holistic_network as rail, holistic_through as through
from . import straight_through_layout, third_ring_through
from .coverage_orbitals import WALK_M

RINGS = ("M15", "M09", "M16")
MIN_LENGTH_KM = 16
MAX_LENGTH_KM = 56
MAX_DETOUR = 1.10
MAX_TURN_DEG = 30
STATION_SPACING_M = 750
TARGET_STOP_GAP_M = 1_650
MAX_STOP_GAP_M = 3_500
BRIDGE_SEPARATION_M = 700
DEDICATED_CROSSING_INTERVAL_M = 850
DEDICATED_REACH_HALF_M = 550
MAX_DEDICATED_LANDING_STREET_M = 330
PARALLEL_LIMIT_M = 1_100
PARALLEL_DIRECTION_DEG = 15
MAX_PARALLEL_SHARE = .24
MAX_MINOR_WATER_SPAN_M = 150
MIN_OUTER_TERMINAL_REACH_M = 350
MAX_OUTER_TERMINAL_REACH_M = 11_000
MAX_APPROACHES_PER_SIDE = 30
MAX_PAIRS_PER_BRIDGE = 220
MAX_POOL_PER_BRIDGE = 18


def _demand_tiles(population, size=1_000):
    points = population.coordinates * rail.LOCAL_METRES
    _, groups = np.unique(np.floor(points / size).astype(int), axis=0, return_inverse=True)
    counts = np.bincount(groups, weights=population.counts)
    weighted = [np.bincount(groups, weights=points[:, i] * population.counts) / counts for i in range(2)]
    return np.column_stack(weighted), counts


def _terminal_sites(demand, weights, graph, context, outer, airport):
    eligible = np.flatnonzero(~intersects_xy(outer, *demand.T)
                              & (weights >= 50))
    candidates = demand[eligible]
    nearest = graph[3].query(candidates)[1]
    coords = np.unique(graph[3].data[nearest], axis=0)
    outer_gap = distance(outer, points(coords))
    coords = coords[(outer_gap >= MIN_OUTER_TERMINAL_REACH_M) & (outer_gap <= MAX_OUTER_TERMINAL_REACH_M)]
    if airport is not None:
        coords = np.vstack((airport, coords[np.linalg.norm(coords - airport, axis=1) > 350]))
    clear = ~intersects_xy(outer, *coords.T)
    return coords[clear & rail.dry_points(coords / rail.LOCAL_METRES, context)]


def _approaches(landing, direction, terminals, demand, weights, airport):
    delta = terminals - landing
    length = np.linalg.norm(delta, axis=1)
    accepted = np.flatnonzero((length >= 1_200) & (length < 39_000)
                              & (delta @ direction >= length * cos(radians(MAX_TURN_DEG))))
    relative = demand - landing
    bins = Counter()
    options = []
    for i in accepted:
        unit = delta[i] / length[i]
        along = relative @ unit
        offset = np.abs(relative[:, 0] * unit[1] - relative[:, 1] * unit[0])
        support = (along >= 0) & (along <= length[i])
        score = float(np.dot(weights[support], np.maximum(0, 1 - offset[support] / WALK_M)))
        bearing = round(third_ring_through._bearing(np.asarray([landing, terminals[i]])) / 4)
        airport_site = airport is not None and np.linalg.norm(terminals[i] - airport) < 1
        options.append((not airport_site, -score / (length[i] + 3_000), int(i), bearing))
    selected = []
    for other, score, i, bearing in sorted(options):
        if bins[bearing] >= 4:
            continue
        bins[bearing] += 1
        selected.append((i, other, score))
        if len(selected) == MAX_APPROACHES_PER_SIDE:
            break
    return selected


def _exits_polygon(track, km, polygon):
    shift = min(.05, km / 2, (track.km - km) / 2)
    return (polygon.contains(Point(np.asarray(track.at(km - shift)) * rail.LOCAL_METRES))
            != polygon.contains(Point(np.asarray(track.at(km + shift)) * rail.LOCAL_METRES)))


def _ring_sites(track, ring_tracks, polygons, graph, context):
    result = {}
    for code in RINGS:
        matches = [(km, ring_km, point) for point, (km, ring_km) in rail._crossings(track, ring_tracks[code]).items()
                   if STATION_SPACING_M / 1000 <= km <= track.km - STATION_SPACING_M / 1000
                   and _exits_polygon(track, km, polygons[code])]
        if not matches:
            return None
        points = np.asarray([row[2] for row in matches])
        offsets = graph[3].query(points * rail.LOCAL_METRES)[0]
        valid = rail.dry_points(points, context) & (offsets <= rail.TRANSFER_SNAP_M)
        sites = sorted((float(offset), km, ring_km, point)
                       for (km, ring_km, point), offset, keep in zip(matches, offsets, valid, strict=True) if keep)
        if not sites:
            return None
        result[code] = sites
    return result


def _platform_lattice(track, graph, context, demand_tree):
    chain = np.arange(.125, track.km, .125)
    coords = np.asarray([track.at(km) for km in chain]) * rail.LOCAL_METRES
    offset = graph[3].query(coords)[0]
    valid = (offset <= rail.TRANSFER_SNAP_M) & rail.dry_points(coords / rail.LOCAL_METRES, context)
    potential = {index: np.asarray(cells, dtype=np.intp)
                 for index, cells in zip(np.flatnonzero(valid),
                                         demand_tree.query_ball_point(coords[valid], WALK_M), strict=True)}
    return chain, coords, offset, valid, potential


def _calls(track, ring_sites, network, station_tree, weights, lattice):
    calls = []
    for code in sorted(RINGS, key=lambda code: (len(ring_sites[code]), code)):
        possible = [site for site in ring_sites[code]
                    if rail._terminal_margin(network["lines"][code], site[2]) >= STATION_SPACING_M
                    or rail._stations_at_crossing(network["stations"], site[3])]
        for _, km, ring_km, point in possible:
            location = np.asarray(point) * rail.LOCAL_METRES
            nearby = rail._stations_at_crossing(network["stations"], point)
            if not nearby and station_tree.query(location)[0] < STATION_SPACING_M:
                continue
            if all(abs(km - other_km) >= STATION_SPACING_M / 1000
                   or point == other_point for _, other_km, _, other_point in calls):
                calls.append((code, km, ring_km, point))
                break
        else:
            return None
    # An outbound crossing can serve the far bank as well when the sites
    # are genuinely distinct and leave enough room on both alignments.
    for code in reversed(RINGS):
        existing_km = next(km for ring, km, _, _ in calls if ring == code)
        for _, km, ring_km, point in ring_sites[code]:
            if all(abs(km - other_km) >= STATION_SPACING_M / 1000
                   for _, other_km, _, _ in calls) and (
                   abs(km - existing_km) >= 2.
                   and rail._terminal_margin(network["lines"][code], ring_km) >= STATION_SPACING_M
                   and station_tree.query(np.asarray(point) * rail.LOCAL_METRES)[0] >= STATION_SPACING_M):
                calls.append((code, km, ring_km, point))
                break
    mandatory = sorted({0., track.km, *(row[1] for row in calls)})
    chain, coords, offset, valid, potential = lattice
    valid = valid & (station_tree.query(coords)[0] >= STATION_SPACING_M)
    ordinary = []
    for low, high in zip(mandatory, mandatory[1:]):
        count = max(1, round((high - low) * 1000 / TARGET_STOP_GAP_M))
        previous = low
        for target in np.linspace(low, high, count + 1)[1:-1]:
            choices = np.flatnonzero(valid & (chain >= previous + STATION_SPACING_M / 1000)
                                      & (chain <= high - STATION_SPACING_M / 1000)
                                      & (abs(chain - target) <= .8))
            if not len(choices):
                continue
            index = min(choices, key=lambda i: (-float(weights[potential[i]].sum()),
                                                abs(chain[i] - target), offset[i], i))
            previous = float(chain[index])
            ordinary.append(previous)
    chainages = sorted([*mandatory, *ordinary])
    if max(np.diff(chainages)) * 1000 > MAX_STOP_GAP_M:
        return None
    return calls, ordinary


def _dry_bank_arm(start, end, context, water, river):
    """Check a complete bank approach and list its minor-water works."""
    if len(river.intersections(start, end)[1]):
        return None
    if not any(len(hits) for hits in water.intersections(start, end)):
        return []
    length = float(np.linalg.norm(end - start))
    result = []
    for low, high in through._water_contacts(start, end, context, water):
        wet_m = float((high - low) * length)
        if wet_m > MAX_MINOR_WATER_SPAN_M:
            return None
        result.append({"chainage_km": round((low + high) * length / 2000, 3),
                       "mapped_wet_width_m": round(wet_m) if high > low else None,
                       "basis": "Provisional dedicated minor-water crossing. Width is a mapped wet interval. "
                                "Unmapped banks, navigation, flood and structural envelopes remain open."})
    return result


def _dedicated_crossing(start, end, context, water, river):
    length = float(np.linalg.norm(end - start))
    hits = river.intersections(start, end)[1]
    if len(hits) != 1:
        return None
    for low, high in through._water_contacts(start, end, context, water):
        if not low <= hits[0] <= high:
            continue
        wet_m = (high - low) * length
        if 30 <= wet_m <= through.MAX_WATER_SPAN_M and min(low, 1 - high) * length >= 100:
            return [{"chainage_km": round(float((low + high) * length / 2_000), 3),
                     "mapped_wet_width_m": round(float(wet_m))}]
    return None


def _dedicated_reaches(context, water, river, graph, inner):
    bound = inner.buffer(4_000)
    reaches = []
    features = [row for row in context["layers"]["water"] if row["properties"].get("name:en") == "Tigris River"]
    for row in sorted(features, key=lambda row: str(row.get("id", row["geometry"]))):
        geometry = row["geometry"]
        paths = ([geometry["coordinates"]] if geometry["type"] == "LineString"
                 else geometry["coordinates"] if geometry["type"] == "MultiLineString" else [])
        for path in paths:
            riverline = LineString(np.asarray(path) * rail.LOCAL_METRES)
            for metres in np.arange(250, riverline.length - 250, DEDICATED_CROSSING_INTERVAL_M):
                centre = riverline.interpolate(metres)
                if not bound.covers(centre) or any(centre.distance(old[0]) < 350 for old in reaches):
                    continue
                delta = (np.asarray(riverline.interpolate(metres + 120).coords[0])
                         - np.asarray(riverline.interpolate(metres - 120).coords[0]))
                angle = np.arctan2(delta[1], delta[0]) + np.pi / 2
                directions = angle + np.deg2rad([0., -22., 22., -43., 43.])
                centre_xy = np.asarray(centre.coords[0])
                for heading in directions:
                    unit = np.array([np.cos(heading), np.sin(heading)])
                    reach = np.array([centre_xy - unit * DEDICATED_REACH_HALF_M,
                                      centre_xy + unit * DEDICATED_REACH_HALF_M])
                    land = graph[3].query(reach)[0] <= MAX_DEDICATED_LANDING_STREET_M
                    if (land.all() and rail.dry_points(reach / rail.LOCAL_METRES, context).all()
                            and _dedicated_crossing(*reach, context, water, river)):
                        reaches.append((centre, reach))
    return [reach for _, reach in reaches]


def _pool(terminals, demand, weights, airport, graph, context, polygons, ring_tracks):
    _, bridges = through._street_layers(context)
    water = through.WaterGeometry.from_context(context)
    river = straight_through_layout._tigris(context)
    reaches = sorted(holistic_grid._bridge_reaches(context, water, bridges), key=lambda row: tuple(row.mean(axis=0)))
    sites = []
    for reach in reaches:
        if len(river.intersections(*reach)[1]) != 1:
            continue
        if all(np.linalg.norm(reach.mean(axis=0) - prior.mean(axis=0)) >= 150 for prior in sites):
            sites.append(reach)
    mapped_count = len(sites)
    sites.extend(_dedicated_reaches(context, water, river, graph, polygons[RINGS[0]]))
    candidates, audit = [], []
    for bridge_id, reach in enumerate(sites, 1):
        tagged_bridge = bridge_id <= mapped_count
        if tagged_bridge:
            bridge = through._water_screen(*reach, context, water, bridges)
            basis = "Tagged road bridge corridor. New rail crossing requires design."
        else:
            bridge = _dedicated_crossing(*reach, context, water, river)
            basis = "Dedicated rail crossing at mapped Tigris banks. Navigation, flood and structure remain open."
        if not bridge:
            continue
        bridge = [row | {"basis": basis} for row in bridge]
        delta = reach[1] - reach[0]
        direction = delta / np.linalg.norm(delta)
        arms = [_approaches(landing, sign * direction, terminals, demand, weights, airport)
                for landing, sign in zip(reach, (-1, 1), strict=True)]
        west = {i: _dry_bank_arm(terminals[i], reach[0], context, water, river) for i, _, _ in arms[0]}
        east = {i: _dry_bank_arm(reach[1], terminals[i], context, water, river) for i, _, _ in arms[1]}
        pairs = []
        for (a, other_a, score_a), (b, other_b, score_b) in product(*arms):
            if a == b:
                continue
            path = np.asarray([terminals[a], *reach, terminals[b]])
            distance = np.linalg.norm(np.diff(path, axis=0), axis=1).sum()
            detour = distance / np.linalg.norm(path[-1] - path[0])
            if MIN_LENGTH_KM * 1000 <= distance <= MAX_LENGTH_KM * 1000 and detour <= MAX_DETOUR:
                start_angle = round(third_ring_through._bearing(path[:2]) / 6)
                end_angle = round(third_ring_through._bearing(path[-2:]) / 6)
                pairs.append((other_a and other_b, score_a + score_b, detour, a, b, path, (start_angle, end_angle)))
        failures = Counter()
        tried_sector, accepted_sector = Counter(), Counter()
        accepted = 0
        screened = 0
        airport_pairs_passed = 0
        for other, score, detour, a, b, path, sector in sorted(pairs, key=lambda row: row[:5]):
            if (screened == (MAX_PAIRS_PER_BRIDGE if tagged_bridge else 50)
                    or accepted == (MAX_POOL_PER_BRIDGE if tagged_bridge else 6)):
                break
            if other and (tried_sector[sector] >= 12 or accepted_sector[sector] >= 2):
                continue
            tried_sector[sector] += 1
            screened += 1
            if west[a] is None or east[b] is None:
                failures["unsupported water crossing or repeated Tigris crossing"] += 1
                continue
            track = rail.Track(path / rail.LOCAL_METRES)
            shape = LineString(path)
            if not all(shape.crosses(polygons[code]) for code in RINGS):
                failures["does not cross every orbital"] += 1
                continue
            matches = _ring_sites(track, ring_tracks, polygons, graph, context)
            if matches is None:
                failures["missing dry street-accessible orbital interchange"] += 1
                continue
            wet = [*west[a]]
            for offset, rows in ((track.chainage[1], bridge), (track.chainage[2], east[b])):
                wet.extend(row | {"chainage_km": round(offset / 1000 + row["chainage_km"], 3)} for row in rows)
            candidates.append({"track": track, "bridge": bridge_id, "reach": reach,
                               "wet": wet, "airport": not other, "ring_sites": matches, "tagged_bridge": tagged_bridge,
                               "proxy": -score, "detour": detour, "terminals": (a, b)})
            accepted_sector[sector] += 1
            accepted += 1
            airport_pairs_passed += int(not other)
        audit.append({"bridge": bridge_id, "mapped_bridge_approaches": (reach / rail.LOCAL_METRES).tolist(),
                      "uses_tagged_bridge_corridor": tagged_bridge,
                      "rankable_pairs": len(pairs), "screened_pairs": screened, "accepted": accepted,
                      "rankable_airport_pairs": sum(not row[0] for row in pairs),
                      "airport_pairs_passed": airport_pairs_passed,
                      "reasons": dict(sorted(failures.items()))})
    return candidates, audit


def _parallel_share(first, second):
    def directional(source, comparison):
        samples = np.linspace(0, source.km, round(source.km * 5) + 1)
        positions = np.asarray([source.at(float(km)) for km in samples])
        positions *= rail.LOCAL_METRES
        segments = np.clip(np.searchsorted(source.chainage, samples * 1000, side="right") - 1,
                           0, len(source.delta) - 1)
        directions = source.delta[segments] / source.lengths[segments, None]
        vectors = comparison.delta
        relative = positions[:, None, :] - comparison.points[:-1]
        projections = np.clip(np.sum(relative * vectors, axis=2) / comparison.lengths**2, 0, 1)
        offset = np.linalg.norm(relative - projections[:, :, None] * vectors, axis=2)
        alignment = abs(directions @ (vectors / comparison.lengths[:, None]).T)
        close = (offset < PARALLEL_LIMIT_M) & (alignment >= cos(radians(PARALLEL_DIRECTION_DEG)))
        return float(np.mean(close.any(axis=1)))

    return max(directional(first, second), directional(second, first))


def _append(network, candidate, code, calls, ordinary, airport):
    track = candidate["track"]
    line = {"name": f"Cross-city trunk {code[1:]}", "geometry": track.coordinates.tolist(), "loop": False,
            "source_sections": [], "basis": "Planning centreline with a dedicated rail crossing at mapped riverbanks. "
                                              "Swept path, grades and structures require design.",
            "station_ids": [], "station_chainage_km": {}, "one_way_km": track.km}
    network["lines"][code] = line
    for index, km in enumerate([0., *ordinary, track.km]):
        point = track.at(km)
        is_airport = airport is not None and np.linalg.norm(np.asarray(point) * rail.LOCAL_METRES - airport) < 1
        stop = "Airport-00" if is_airport else f"{code}-S{index + 1:02d}"
        network["stations"][stop] = {"name": "Baghdad International Airport" if is_airport else f"{code} · km {km:g}",
                                     "coordinates": point, "lines": [code],
                                     "basis": "Proposed platform on elevated cross-city alignment"}
        rail._add(line, stop, km)
    for ring, km, ring_km, point in calls:
        rail._through_interchange(code, {"line_id": ring}, (point, (km, ring_km)),
                                  network["lines"], network["stations"], require_intermediate=False)


def _connect_trunks(network, selected, graph, context):
    for (first, previous), (second, following) in combinations(selected, 2):
        lines, stations = network["lines"], network["stations"]
        for point, chainages in sorted(rail._crossings(previous["track"], following["track"]).items()):
            if not rail.dry_points([point], context)[0]:
                continue
            nearby = rail._stations_at_crossing(stations, point)
            offset = graph[3].query(np.asarray(point) * rail.LOCAL_METRES)[0]
            if offset > rail.TRANSFER_SNAP_M:
                continue
            closest = min(np.linalg.norm((np.asarray(row["coordinates"]) - point) * rail.LOCAL_METRES)
                          for stop, row in stations.items() if stop not in nearby)
            if closest < STATION_SPACING_M:
                continue
            try:
                rail._through_interchange(first, {"line_id": second}, (point, chainages),
                                          lines, stations, require_intermediate=False)
            except ValueError:
                continue
            break


def assemble(reference, ring_network, graph, context, population, *, max_trunks=8, coverage_sites=()):
    """Generate and select a bounded fresh pool. Preserve airport access as a gate."""
    if set(ring_network["lines"]) != set(RINGS):
        raise ValueError("Trunk search requires a ring-only starting network")
    network = deepcopy(ring_network)
    ring_tracks = {code: rail.Track(network["lines"][code]["geometry"]) for code in RINGS}
    polygons = {code: Polygon(track.points) for code, track in ring_tracks.items()}
    airport_row = reference["stations"].get("Airport-00")
    airport = np.asarray(airport_row["coordinates"]) * rail.LOCAL_METRES if airport_row is not None else None
    demand, counts = _demand_tiles(population)
    demand_tree = cKDTree(demand)
    terminals = _terminal_sites(demand, counts, graph, context, polygons[RINGS[-1]], airport)
    pool, bridge_audit = _pool(terminals, demand, counts, airport, graph, context, polygons, ring_tracks)
    positions = [row["coordinates"] for row in network["stations"].values()]
    positions.extend(coverage_sites)
    fixed = np.asarray(positions) * rail.LOCAL_METRES
    served = cKDTree(fixed).query(demand)[0] <= WALK_M
    selected = []
    failures = Counter()
    parallel = {}
    for _ in range(max_trunks):
        options = []
        stations = np.asarray([row["coordinates"] for row in network["stations"].values()]) * rail.LOCAL_METRES
        station_tree = cKDTree(stations)
        for index, candidate in enumerate(pool):
            track = candidate["track"]
            close = False
            for old_code, old in selected:
                if old["airport"] and candidate["airport"]:
                    failures["duplicate airport route"] += 1
                    close = True
                    break
                if np.linalg.norm(candidate["reach"].mean(axis=0) - old["reach"].mean(axis=0)) < BRIDGE_SEPARATION_M:
                    failures["closely spaced Tigris crossings"] += 1
                    close = True
                    break
                pair = (id(candidate), old_code)
                if pair not in parallel:
                    parallel[pair] = _parallel_share(track, old["track"])
                if parallel[pair] > MAX_PARALLEL_SHARE:
                    failures["too much close parallel alignment"] += 1
                    close = True
                    break
            if close:
                continue
            if np.any(station_tree.query(track.points[[0, -1]])[0] < STATION_SPACING_M):
                failures["endpoint duplicates an existing station"] += 1
                continue
            if "lattice" not in candidate:
                candidate["lattice"] = _platform_lattice(track, graph, context, demand_tree)
            calls = _calls(track, candidate["ring_sites"], network, station_tree, counts * ~served,
                           candidate["lattice"])
            if calls is None:
                failures["station spacing or inaccessible platform gap"] += 1
                continue
            chain = [0., track.km, *(km for _, km, _, _ in calls[0]), *calls[1]]
            proxy = cKDTree(np.asarray([track.at(km) for km in chain]) * rail.LOCAL_METRES).query(demand)[0] <= WALK_M
            gained = float(counts[proxy & ~served].sum())
            prioritize_airport = airport is not None and not any(old["airport"] for _, old in selected)
            options.append((prioritize_airport and not candidate["airport"], -gained, -gained / track.km,
                            candidate["detour"], index, proxy, calls))
        if not options:
            break
        _, neg_gained, _, _, index, proxy, (calls, ordinary) = min(options, key=lambda item: item[:5])
        if selected and neg_gained >= 0:
            break
        candidate = pool.pop(index)
        code = f"T{len(selected) + 1:02d}"
        _append(network, candidate, code, calls, ordinary, airport)
        candidate["incremental_proxy"] = round(-neg_gained)
        served |= proxy
        selected.append((code, candidate))
    if selected:
        _connect_trunks(network, selected, graph, context)
        network["transfers"] = [
            {"id": stop, "name": row["name"], "station_ids": [stop], "lines": sorted(row["lines"]),
             "walking_m": None, "basis": row["basis"]}
            for stop, row in sorted(network["stations"].items()) if len(row["lines"]) > 1
        ]
        network["topology"] = rail.validate(network)
        network["physical_accepted"] = False
        network["operating_timetable_validated"] = False
        rail._identity(network)
    holds = []
    if not selected:
        holds.append("No candidate satisfied the cross-city trunk and orbital interchange screens")
    if airport is not None and "Airport-00" not in network["stations"]:
        holds.append("No selected end-to-end cross-Tigris route called at the mandatory airport destination")
    rows = []
    for code, candidate in selected:
        track = candidate["track"]
        row = third_ring_through._axis_record(network, code, RINGS, polygons[RINGS[-1]],
                                                (candidate["reach"] / rail.LOCAL_METRES).tolist(), candidate["wet"], 1)
        rows.append(row | {"incremental_population_proxy": candidate["incremental_proxy"],
                           "maximum_bend_deg": round(max(third_ring_through._turn(a, b)
                                                        for a, b in zip(track.delta, track.delta[1:])), 2),
                           "serves_airport": candidate["airport"],
                           "terminal_distance_beyond_outer_ring_m": [
                               round(float(polygons[RINGS[-1]].distance(Point(point))), 1)
                               for point in track.points[[0, -1]]],
                           "uses_tagged_bridge_corridor": candidate.get("tagged_bridge", False)})
    return network, {"trunks": rows, "holds": holds, "mapped_bridge_search": bridge_audit,
                     "physical_evidence_holds": [
                         "Verify site geometry, land access, vertical grades and swept train paths.",
                         "Size and price all dedicated river and minor-water structures against flood, "
                         "navigation, riverbed and construction evidence.",
                         "Design platforms, turnbacks and degraded operation for the proposed service.",
                     ],
                     "pool_candidates": sum(row["accepted"] for row in bridge_audit),
                     "selection_rejections": dict(sorted(failures.items())),
                     "population_source": population.source, "candidate_id": network.get("candidate_id"),
                     "evaluation_id": network.get("evaluation_id"),
                     "screen": {"walk_proxy_m": WALK_M, "maximum_detour": MAX_DETOUR,
                                "maximum_bend_deg": MAX_TURN_DEG, "minimum_station_spacing_m": STATION_SPACING_M,
                                "parallel_limit_m": PARALLEL_LIMIT_M, "maximum_parallel_share": MAX_PARALLEL_SHARE,
                                "parallel_direction_tolerance_deg": PARALLEL_DIRECTION_DEG,
                                "ordinary_terminal_reach_beyond_outer_ring_m": [
                                    MIN_OUTER_TERMINAL_REACH_M, MAX_OUTER_TERMINAL_REACH_M],
                                "bridge_separation_m": BRIDGE_SEPARATION_M,
                                "maximum_dedicated_landing_street_m": MAX_DEDICATED_LANDING_STREET_M,
                                "maximum_mapped_minor_wet_width_m": MAX_MINOR_WATER_SPAN_M}}
