"""Build new end-to-end Baghdad trunks from mapped constraints and population."""

from collections import Counter
from copy import deepcopy
from itertools import combinations, product
from math import cos, radians

import numpy as np
from scipy.spatial import cKDTree
from shapely import LineString, Point, Polygon, distance, get_parts, intersects_xy, points

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
SUBURBAN_PARALLEL_SEPARATION_M = 5_000
SUBURBAN_GATE_OFFSET_M = 2_500
MIN_SUBURBAN_PARALLEL_RUN_M = 1_500
PARALLEL_DIRECTION_DEG = 15
MAX_PARALLEL_SHARE = .24
MAX_MINOR_WATER_SPAN_M = 150
MIN_OUTER_TERMINAL_REACH_M = SUBURBAN_GATE_OFFSET_M
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


def _approaches(landing, direction, terminals, demand, weights, airport, targets):
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
        options.append((not airport_site, not targets.get(int(i)), -score / (length[i] + 3_000), int(i), bearing))
    selected = []
    for other, ordinary, score, i, bearing in sorted(options):
        if ordinary and bins[bearing] >= 4:
            continue
        bins[bearing] += int(ordinary)
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


def spaced_platform_path(km, weights, target_gap_km):
    """Find the best accessible sequence under the minimum and maximum platform intervals."""
    reward = weights / max(float(weights.max()), 1.)
    parent = np.full(len(km), -1)
    merit = np.full(len(km), -np.inf)
    merit[0] = 0.
    for index in range(1, len(km)):
        gaps = km[index] - km[:index]
        parents = np.flatnonzero((gaps >= STATION_SPACING_M / 1000 - 1e-9)
                                 & (gaps <= MAX_STOP_GAP_M / 1000 + 1e-9)
                                 & np.isfinite(merit[:index]))
        if parents.size:
            scores = merit[parents] - .55 * (gaps[parents] - target_gap_km)**2
            best = int(scores.argmax())
            parent[index] = parents[best]
            merit[index] = scores[best] + reward[index] - .5
    if parent[-1] < 0:
        return None
    result = []
    index = len(km) - 1
    while index:
        result.append(index)
        index = parent[index]
    return result[::-1]


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
        segment = []
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
            segment.append(previous)
        if max(np.diff([low, *segment, high])) * 1000 > MAX_STOP_GAP_M:
            legal = np.flatnonzero(valid & (chain >= low + STATION_SPACING_M / 1000)
                                   & (chain <= high - STATION_SPACING_M / 1000))
            endpoints_and_sites = np.r_[low, chain[legal], high]
            support = np.array([0., *(weights[potential[i]].sum() for i in legal), 0.])
            path = spaced_platform_path(endpoints_and_sites, support, TARGET_STOP_GAP_M / 1000)
            if path is None:
                return None
            segment = endpoints_and_sites[path[:-1]].tolist()
        ordinary.extend(segment)
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


def _candidate(track, reach, bridge_id, bridge, tagged, water_rows, airport, names, proxy,
               graph, context, polygons, ring_tracks):
    shape = LineString(track.points)
    if not shape.is_simple or not all(shape.crosses(polygons[code]) for code in RINGS):
        return None, "does not cross every orbital"
    matches = _ring_sites(track, ring_tracks, polygons, graph, context)
    if matches is None:
        return None, "missing dry street-accessible orbital interchange"
    wet = []
    path_rows = [*water_rows[0], bridge, *water_rows[1]]
    for offset, rows in zip(track.chainage[:-1], path_rows, strict=True):
        wet.extend(row | {"chainage_km": round(offset / 1000 + row["chainage_km"], 3)} for row in rows)
    return {"track": track, "bridge": bridge_id, "reach": reach, "wet": wet, "airport": airport,
            "ring_sites": matches, "tagged_bridge": tagged, "proxy": proxy,
            "detour": third_ring_through._detour(track), "destinations": names}, None


def _bent_arms(bank, direction, target):
    """Offer a bounded set of tangents for a name missed by straight bank approaches."""
    vector = target - bank
    length = np.linalg.norm(vector)
    along = float(direction @ vector)
    lateral = direction[0] * vector[1] - direction[1] * vector[0]
    turn = float(np.degrees(np.arctan2(lateral, along)))
    if abs(turn) >= 2 * MAX_TURN_DEG or length < 2_000:
        return
    sign = 1 if turn >= 0 else -1
    angles = sorted({sign * angle for angle in (0, 10, 20, MAX_TURN_DEG)}
                    | {np.clip(turn, -MAX_TURN_DEG, MAX_TURN_DEG)})
    for angle in angles:
        radians_ = np.deg2rad(angle)
        tangent = direction * np.cos(radians_) + np.array([-direction[1], direction[0]]) * np.sin(radians_)
        for share in (.22, .40, .60):
            start_leg = tangent * (share * length)
            if third_ring_through._turn(start_leg, vector - start_leg) <= MAX_TURN_DEG + 1e-8:
                yield np.array([bank, bank + start_leg, target])


def _bent_named_candidates(bridges, terminals, targets, missing, graph, context, water,
                           river, polygons, ring_tracks):
    """Try one additional turn on the named bank, retaining the normal trunk checks."""
    result = []
    for bridge_id, reach, centre_rows, tagged, arms, bank_water in bridges:
        direction = reach[1] - reach[0]
        direction /= np.linalg.norm(direction)
        for side in (0, 1):
            outward = (2 * side - 1) * direction
            opposite = 1 - side
            for terminal, names in targets.items():
                if not names & missing:
                    continue
                endings = []
                for arm in _bent_arms(reach[side], outward, terminals[terminal]):
                    if not rail.dry_points(arm[1:2] / rail.LOCAL_METRES, context).all():
                        continue
                    oriented = arm[::-1] if side == 0 else arm
                    crossing = [_dry_bank_arm(a, b, context, water, river) for a, b in zip(oriented, oriented[1:])]
                    if any(rows is None for rows in crossing):
                        continue
                    for other, ordinary, score in arms[opposite][:14]:
                        if other == terminal or bank_water[opposite][other] is None:
                            continue
                        other_arm = np.array([reach[opposite], terminals[other]])
                        if opposite == 0:
                            other_arm = other_arm[::-1]
                        left, right = (oriented, other_arm) if side == 0 else (other_arm, oriented)
                        water_rows = (crossing, [bank_water[opposite][other]]) if side == 0 else (
                            [bank_water[opposite][other]], crossing)
                        path = np.vstack((left, right))
                        track = rail.Track(path / rail.LOCAL_METRES)
                        if MIN_LENGTH_KM <= track.km <= MAX_LENGTH_KM and third_ring_through._detour(track) <= MAX_DETOUR:
                            endings.append((track, water_rows, ordinary, score, other))
                endings.sort(key=lambda row: (row[2], row[3], third_ring_through._detour(row[0])))
                passed = 0
                for track, water_rows, ordinary, score, other in endings[:32]:
                    candidate, _ = _candidate(track, reach, bridge_id, centre_rows, tagged, water_rows,
                                              not ordinary, names | targets.get(other, frozenset()), -score,
                                              graph, context, polygons, ring_tracks)
                    if candidate:
                        result.append(candidate)
                        passed += 1
                    if passed == 4:
                        break
    return result


def _pool(terminals, demand, weights, airport, graph, context, polygons, ring_tracks, *, targets=None):
    targets = targets or {}
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
    candidates, audit, approaches = [], [], []
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
        arms = [_approaches(landing, sign * direction, terminals, demand, weights, airport, targets)
                for landing, sign in zip(reach, (-1, 1), strict=True)]
        west = {i: _dry_bank_arm(terminals[i], reach[0], context, water, river) for i, _, _ in arms[0]}
        east = {i: _dry_bank_arm(reach[1], terminals[i], context, water, river) for i, _, _ in arms[1]}
        approaches.append((bridge_id, reach, bridge, tagged_bridge, arms, (west, east)))
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
                destinations = targets.get(a, frozenset()) | targets.get(b, frozenset())
                pairs.append((other_a and other_b, -len(destinations), score_a + score_b, detour, a, b, path,
                              (start_angle, end_angle), destinations))
        failures = Counter()
        tried_sector, accepted_sector = Counter(), Counter()
        accepted = 0
        screened = 0
        airport_pairs_passed = 0
        group_counts = Counter()
        group_screened = Counter()
        for other, _, score, detour, a, b, path, sector, destinations in sorted(pairs, key=lambda row: row[:6]):
            group = (other, tuple(sorted(destinations)))
            if (group_screened[group] >= (MAX_PAIRS_PER_BRIDGE if tagged_bridge else 50)
                    or group_counts[group] >= (MAX_POOL_PER_BRIDGE if tagged_bridge else 6)):
                continue
            if other and not destinations and (tried_sector[sector] >= 12 or accepted_sector[sector] >= 2):
                continue
            tried_sector[sector] += 1
            screened += 1
            group_screened[group] += 1
            if west[a] is None or east[b] is None:
                failures["unsupported water crossing or repeated Tigris crossing"] += 1
                continue
            track = rail.Track(path / rail.LOCAL_METRES)
            candidate, failure = _candidate(
                track, reach, bridge_id, bridge, tagged_bridge, ([west[a]], [east[b]]),
                not other, destinations, -score, graph, context, polygons, ring_tracks)
            if failure:
                failures[failure] += 1
                continue
            candidates.append(candidate)
            accepted_sector[sector] += 1
            accepted += 1
            group_counts[group] += 1
            airport_pairs_passed += int(not other)
        audit.append({"bridge": bridge_id, "mapped_bridge_approaches": (reach / rail.LOCAL_METRES).tolist(),
                      "uses_tagged_bridge_corridor": tagged_bridge,
                      "rankable_pairs": len(pairs), "screened_pairs": screened, "accepted": accepted,
                      "rankable_airport_pairs": sum(not row[0] for row in pairs),
                      "airport_pairs_passed": airport_pairs_passed,
                      "reasons": dict(sorted(failures.items()))})
    missing = set().union(*targets.values()) - set().union(*(row["destinations"] for row in candidates))
    if missing:
        bent = _bent_named_candidates(approaches, terminals, targets, missing, graph, context,
                                     water, river, polygons, ring_tracks)
        candidates.extend(bent)
        additions = Counter(row["bridge"] for row in bent)
        for row in audit:
            row["accepted_bent_named"] = additions[row["bridge"]]
            row["accepted"] += row["accepted_bent_named"]
    return candidates, audit


def _parallel_samples(source, comparison, distance_m):
    samples = np.linspace(0, source.km, max(2, round(source.km * 5) + 1))
    positions = np.asarray([source.at(float(km)) for km in samples]) * rail.LOCAL_METRES
    segments = np.clip(np.searchsorted(source.chainage, samples * 1000, side="right") - 1,
                       0, len(source.delta) - 1)
    directions = source.delta[segments] / source.lengths[segments, None]
    vectors = comparison.delta
    relative = positions[:, None, :] - comparison.points[:-1]
    fraction = np.sum(relative * vectors, axis=2) / comparison.lengths**2
    projection = np.clip(fraction, 0, 1)
    offset = np.linalg.norm(relative - projection[:, :, None] * vectors, axis=2)
    alignment = abs(directions @ (vectors / comparison.lengths[:, None]).T)
    close = (offset < distance_m) & (alignment >= cos(radians(PARALLEL_DIRECTION_DEG)))
    return close.any(axis=1)


def _parallel_share(first, second):
    return max(float(_parallel_samples(a, b, PARALLEL_LIMIT_M).mean())
               for a, b in ((first, second), (second, first)))


def suburban_arms(track, outer_ring):
    """Return only the alignment outside the outer orbital."""
    clipped = LineString(track.points).difference(outer_ring)
    return tuple(rail.Track(np.asarray(part.coords) / rail.LOCAL_METRES) for part in get_parts(clipped)
                 if part.geom_type == "LineString" and part.length >= MIN_SUBURBAN_PARALLEL_RUN_M)


def suburban_departures(track, suburban_contour):
    """Find the outermost crossing of the suburban contour at each end."""
    if any(suburban_contour.covers(Point(point)) for point in track.points[[0, -1]]):
        return None
    line = LineString(track.points)
    contacts = get_parts(line.intersection(suburban_contour.boundary))
    crossings = [p for p in contacts if p.geom_type == "Point"]
    if len(crossings) < 2 or len(crossings) != len(contacts):
        return None
    chainages = sorted({line.project(point) for point in crossings})
    bounds = [0., *chainages, line.length]
    intervals = [suburban_contour.contains(line.interpolate((a + b) / 2)) for a, b in zip(bounds, bounds[1:])]
    exits = [km for km, before, after in zip(chainages, intervals[:-1], intervals[1:], strict=True)
             if before != after]
    if len(exits) < 2:
        return None
    return np.array([line.interpolate(km).coords[0] for km in (exits[0], exits[-1])])


def suburban_departure_distance(first, second):
    return float(np.linalg.norm(first[:, None, :] - second[None, :, :], axis=2).min())


def _affine_interval(value, slope, lower, upper, *, open_bounds=False):
    if abs(slope) < 1e-12:
        inside = lower + 1e-7 < value < upper - 1e-7 if open_bounds else lower <= value <= upper
        return (-np.inf, np.inf) if inside else (1., 0.)
    return sorted(((lower - value) / slope, (upper - value) / slope))


def _continuous_parallel_m(source, comparison):
    """Union exact qualifying intervals on the source chainage."""
    intervals = []
    cosine = cos(radians(PARALLEL_DIRECTION_DEG))
    for a, direction_a, length_a, at in zip(
            source.points[:-1], source.delta / source.lengths[:, None], source.lengths, source.chainage[:-1], strict=True):
        for b, direction_b, length_b in zip(
                comparison.points[:-1], comparison.delta / comparison.lengths[:, None], comparison.lengths, strict=True):
            if abs(direction_a @ direction_b) < cosine:
                continue
            offset = a - b
            normal = np.array([-direction_b[1], direction_b[0]])
            along = _affine_interval(offset @ direction_b, direction_a @ direction_b, 0., length_b)
            width = _affine_interval(offset @ normal, direction_a @ normal, -SUBURBAN_PARALLEL_SEPARATION_M,
                                     SUBURBAN_PARALLEL_SEPARATION_M, open_bounds=True)
            start, end = max(0., along[0], width[0]), min(length_a, along[1], width[1])
            if end > start:
                intervals.append((start + at, end + at))
    longest = 0.
    first, last = 0., -np.inf
    for start, end in sorted(intervals):
        if start > last + 1e-7:
            first, last = start, end
        else:
            last = max(last, end)
        longest = max(longest, last - first)
    return longest


def suburban_parallel(first_arms, second_arms):
    """Detect a sustained side-by-side run on either suburban alignment."""
    for first, second in product(first_arms, second_arms):
        gap = np.maximum(first.points.min(axis=0) - second.points.max(axis=0),
                         second.points.min(axis=0) - first.points.max(axis=0))
        if np.linalg.norm(np.maximum(gap, 0)) >= SUBURBAN_PARALLEL_SEPARATION_M:
            continue
        if max(_continuous_parallel_m(first, second), _continuous_parallel_m(second, first)) >= (
                MIN_SUBURBAN_PARALLEL_RUN_M - 1e-7):
            return True
    return False


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


def assemble(reference, ring_network, graph, context, population, *, max_trunks=8, coverage_sites=(),
             destination_sites=None):
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
    target_rows = {}
    if destination_sites:
        names = {}
        for name, sites in destination_sites.items():
            for row in sites:
                names.setdefault(tuple(row), set()).add(name)
        existing = set(map(tuple, terminals))
        extra = sorted(names.keys() - existing)
        if extra:
            terminals = np.vstack((terminals, extra))
        target_rows = {i: frozenset(names[tuple(row)]) for i, row in enumerate(terminals) if tuple(row) in names}
    options = {"targets": target_rows} if target_rows else {}
    pool, bridge_audit = _pool(terminals, demand, counts, airport, graph, context, polygons, ring_tracks, **options)
    outer = polygons[RINGS[-1]]
    suburban_contour = outer.buffer(SUBURBAN_GATE_OFFSET_M)
    failures = Counter()
    admitted = []
    for candidate in pool:
        gates = suburban_departures(candidate["track"], suburban_contour)
        if gates is None:
            failures["trunk ends before the suburban contour"] += 1
            continue
        candidate["suburban_gates"] = gates
        candidate["suburban"] = suburban_arms(candidate["track"], outer)
        admitted.append(candidate)
    pool = admitted
    positions = [row["coordinates"] for row in network["stations"].values()]
    positions.extend(coverage_sites)
    fixed = np.asarray(positions) * rail.LOCAL_METRES
    served = cKDTree(fixed).query(demand)[0] <= WALK_M
    selected = []
    reached_destinations = set()
    parallel = {}
    suburban_overlap = {}
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
                if suburban_departure_distance(candidate["suburban_gates"], old["suburban_gates"]) < SUBURBAN_PARALLEL_SEPARATION_M:
                    failures["suburban departure corridors too close"] += 1
                    close = True
                    break
                if pair not in suburban_overlap:
                    suburban_overlap[pair] = suburban_parallel(candidate["suburban"], old["suburban"])
                if suburban_overlap[pair]:
                    failures["sustained parallel running outside the outer ring"] += 1
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
            destinations = candidate.get("destinations", frozenset()) - reached_destinations
            options.append((prioritize_airport and not candidate["airport"], -len(destinations), -gained,
                            -gained / track.km, candidate["detour"], index, proxy, calls))
        if not options:
            break
        _, neg_destinations, neg_gained, _, _, index, proxy, (calls, ordinary) = min(options, key=lambda item: item[:6])
        if selected and neg_gained >= 0 and neg_destinations == 0:
            break
        candidate = pool.pop(index)
        reached_destinations.update(candidate.get("destinations", ()))
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
                           "named_terminal_anchors": sorted(candidate.get("destinations", ())),
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
                     "named_terminal_anchors": sorted(reached_destinations),
                     "selection_rejections": dict(sorted(failures.items())),
                     "population_source": population.source, "candidate_id": network.get("candidate_id"),
                     "evaluation_id": network.get("evaluation_id"),
                     "screen": {"walk_proxy_m": WALK_M, "maximum_detour": MAX_DETOUR,
                                "maximum_bend_deg": MAX_TURN_DEG, "minimum_station_spacing_m": STATION_SPACING_M,
                                "parallel_limit_m": PARALLEL_LIMIT_M,
                                "suburban_parallel_separation_m": SUBURBAN_PARALLEL_SEPARATION_M,
                                "minimum_suburban_parallel_run_m": MIN_SUBURBAN_PARALLEL_RUN_M,
                                "suburban_gate_offset_m": SUBURBAN_GATE_OFFSET_M, "maximum_parallel_share": MAX_PARALLEL_SHARE,
                                "parallel_direction_tolerance_deg": PARALLEL_DIRECTION_DEG,
                                "ordinary_terminal_reach_beyond_outer_ring_m": [
                                    MIN_OUTER_TERMINAL_REACH_M, MAX_OUTER_TERMINAL_REACH_M],
                                "bridge_separation_m": BRIDGE_SEPARATION_M,
                                "maximum_dedicated_landing_street_m": MAX_DEDICATED_LANDING_STREET_M,
                                "maximum_mapped_minor_wet_width_m": MAX_MINOR_WATER_SPAN_M}}
