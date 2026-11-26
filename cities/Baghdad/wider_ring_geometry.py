"""Bounded search for a wider, continuously spaced Baghdad inner orbital."""

from collections import Counter
from itertools import combinations, product

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from shapely.geometry import LineString, Polygon
from shapely.prepared import prep

from . import holistic_network as network
from . import holistic_orbitals as orbital
from . import spaced_ring_geometry as spaced
from .ring_corridors import INNER, OUTER, _ring_polygon

TARGET_KM = 22.66
LENGTH_BAND_KM = (18., 26.)
PREFERRED_BAND_KM = (22., 23.)
MIN_AREA_KM2 = 9.11
MIN_WIDTH_KM = 3.07
DIRECTION_COUNT = 12
DIRECTION_BIASES = (1.5, 4., 10.)
WAYPOINT_GRID_M = 1_000
MAX_TRANSFER_TRIALS = 36
MAX_TRIALS_PER_NAMED_PAIR = 5


def _routing_matrix(bank_roads):
    nodes = sorted(bank_roads)
    ids = {node: i for i, node in enumerate(nodes)}
    xy = np.asarray(nodes) * network.LOCAL_METRES
    matrix = csr_matrix((
        [row[0] for node in nodes for _, row in sorted(bank_roads[node].items())],
        [ids[neighbor] for node in nodes for neighbor in sorted(bank_roads[node])],
        np.cumsum([0, *(len(bank_roads[node]) for node in nodes)]),
    ), shape=(len(nodes), len(nodes)))
    return nodes, ids, xy, matrix


def _recover(previous, start, finish):
    path = [finish]
    while path[-1] != start:
        predecessor = int(previous[path[-1]])
        if predecessor < 0:
            return None
        path.append(predecessor)
    return tuple(reversed(path))


def _bank_legs(bank_roads, paths):
    """Route ordinary shortest legs and legs biased towards the outer footprint."""
    nodes, ids, xy, matrix = _routing_matrix(bank_roads)
    edge_start = np.repeat(np.arange(len(nodes)), np.diff(matrix.indptr))
    middle = (xy[edge_start] + xy[matrix.indices]) / 2 - xy.mean(axis=0)
    lengths = matrix.data.copy()
    approaches = sorted({ids[node] for _, path in paths.values() for node in (path[0], path[-1])})
    decks = {ids[node] for _, path in paths.values() for node in path[1:-1]}
    blocked = np.isin(edge_start, list(decks)) | np.isin(matrix.indices, list(decks))
    bridge_pairs = [(a, b) for a, b in combinations(paths, 2) if paths[a][0] != paths[b][0]]
    routes = {pair: ({}, {}) for pair in bridge_pairs}
    directions = np.linspace(0, 2 * np.pi, DIRECTION_COUNT, endpoint=False)
    weights = [np.ones(len(lengths))]
    for angle in directions:
        projection = middle @ [np.cos(angle), np.sin(angle)]
        inward = (projection.max() - projection) / np.ptp(projection)
        weights.extend(1 + bias * inward**2 for bias in DIRECTION_BIASES)
    cells = np.floor((xy - xy.min(axis=0)) / WAYPOINT_GRID_M).astype(int)
    centers = xy.min(axis=0) + (cells + .5) * WAYPOINT_GRID_M
    samples = {}
    for node in np.argsort(np.linalg.norm(xy - centers, axis=1), kind="stable"):
        if node not in decks and node not in approaches and matrix.indptr[node + 1] > matrix.indptr[node]:
            samples.setdefault(tuple(cells[node]), node)
    waypoints = sorted(samples.values())
    origin_rows = {node: row for row, node in enumerate(approaches)}
    for variant, weight in enumerate(weights):
        matrix.data[:] = lengths * weight
        matrix.data[blocked] = np.inf
        predecessors = dijkstra(matrix, indices=approaches, return_predecessors=True)[1]
        for pair, options in routes.items():
            first, second = (paths[way][1] for way in pair)
            for side, end in enumerate((-1, 0)):
                start, finish = ids[first[end]], ids[second[end]]
                path = _recover(predecessors[origin_rows[start]], start, finish)
                if path:
                    options[side].setdefault(tuple(nodes[i] for i in path), variant)
                if variant != 0:
                    continue
                for sample, waypoint in enumerate(waypoints, start=len(weights)):
                    first_leg = _recover(predecessors[origin_rows[start]], start, waypoint)
                    last_leg = _recover(predecessors[origin_rows[finish]], finish, waypoint)
                    if not first_leg or not last_leg or set(first_leg[:-1]).intersection(last_leg[:-1]):
                        continue
                    path = first_leg + last_leg[-2::-1]
                    options[side].setdefault(tuple(nodes[i] for i in path), sample)
    return routes


def _short_footprint_km(polygon):
    rectangle = np.asarray(polygon.minimum_rotated_rectangle.exterior.coords)
    return float(np.linalg.norm(np.diff(rectangle, axis=0), axis=1).min() / 1000)


def _turns(points):
    simplified = np.asarray(LineString(points).simplify(25).coords)
    delta = np.diff(simplified, axis=0)
    unit = delta / np.linalg.norm(delta, axis=1)[:, None]
    return np.rad2deg(np.arccos(np.clip(np.sum(unit * np.roll(unit, 1, axis=0), axis=1), -1, 1)))


def _candidate_trials(inset, bank_roads, paths):
    rejected = Counter()
    trials = []
    if not paths:
        return trials, rejected
    for ways, (east_legs, west_legs) in _bank_legs(bank_roads, paths).items():
        first, second = (paths[way][1] for way in ways)
        if not east_legs or not west_legs:
            rejected["disconnected bridge approaches"] += 1
        def road_km(trace):
            xy = np.asarray(trace) * network.LOCAL_METRES
            return float(np.linalg.norm(np.diff(xy, axis=0), axis=1).sum() / 1000)

        bridge_km = road_km(first) + road_km(second)
        east_cases = [(leg, variant, road_km(leg)) for leg, variant in east_legs.items()]
        west_cases = [(leg, variant, road_km(leg)) for leg, variant in west_legs.items()]
        for (east, east_variant, east_km), (west, west_variant, west_km) in product(east_cases, west_cases):
            length = bridge_km + east_km + west_km
            if not LENGTH_BAND_KM[0] <= length <= LENGTH_BAND_KM[1]:
                rejected["outside length band"] += 1
                continue
            trace = first + list(east[1:-1]) + second[::-1] + list(west[-2:0:-1]) + first[:1]
            points = np.asarray(trace) * network.LOCAL_METRES
            polygon = Polygon(points)
            if not polygon.is_valid or not inset.covers(polygon.boundary):
                rejected["non-simple or outside inset"] += 1
                continue
            area = polygon.area / 1e6
            width = _short_footprint_km(polygon)
            if area < MIN_AREA_KM2 or width < MIN_WIDTH_KM:
                rejected["insufficient area or width"] += 1
                continue
            turns = _turns(points)
            trials.append({
                "geometry": [list(node) for node in trace],
                "one_way_km": length,
                "enclosed_area_km2": area,
                "minimum_rotated_footprint_width_km": width,
                "enclosed_area_to_convex_hull_ratio": polygon.area / polygon.convex_hull.area,
                "bridge_ways": list(ways),
                "bridges": [paths[way][0] for way in ways],
                "routing_variants": [east_variant, west_variant],
                "simplified_turns_over_100_degrees": int(np.sum(turns > 100)),
            })
    return trials, rejected


def _rank(row):
    length = row["one_way_km"]
    return (
        not PREFERRED_BAND_KM[0] <= length <= PREFERRED_BAND_KM[1],
        length < 20.,
        row["simplified_turns_over_100_degrees"],
        -row["enclosed_area_km2"],
        abs(length - TARGET_KM),
        row["bridge_ways"],
        row["routing_variants"],
    )


def _connectivity_rank(row):
    return (-len(row["screened_spokes"]), -len(row["screened_transfer_sites"]), _rank(row))


def _screen(row, roads, outer_network, graph, context, shared, paths):
    track = network.Track(row["geometry"])
    gap = spaced.separation(outer_network["lines"][OUTER], row["geometry"])
    if gap["minimum_ring_separation_m"] < spaced.MIN_SEPARATION_M:
        return "continuous clearance below 5 km"
    contacts = orbital._water_crossings(track, roads, context)
    channel = {}
    for contact in contacts:
        way = contact["road_way_id"]
        if way in paths:
            contact["name"] = paths[way][0]
        if contact["mapped_wet_width_m"] >= spaced.MAIN_CHANNEL_MIN_M:
            channel[way] = contact
    if channel.keys() != set(row["bridge_ways"]):
        return "unexpected main-channel crossings"
    first, second = (channel[way] for way in row["bridge_ways"])
    row.update({
        **gap,
        "one_way_km": track.km,
        "topology": "Tigris-straddling",
        "bank_chainage_km": [first["exit_m"] / 1000, second["entry_m"] / 1000, second["exit_m"] / 1000],
        "mapped_water_crossings": contacts,
        "tunnels": 0,
        "road_trace_heading_changes_over_20_degrees": spaced._sharp_bends(track),
    })
    transfers = spaced._actual_transfers(row, outer_network, graph, context)
    row["screened_transfer_sites"] = transfers
    row["screened_spokes"] = sorted({transfer["line_id"] for transfer in transfers} & shared)
    if (len(transfers) < spaced.MIN_TRANSFERS or len(row["screened_spokes"]) < spaced.MIN_DIRECT_SPOKES
            or {transfer["bank"] for transfer in transfers} != {"east", "west"}):
        return "accessible interchange placement screen"
    return None


def evaluate(outer_network, graph, context, *, streets=None):
    """Generate finite road trials, then check bridge and actual transfer placement."""
    outer_line = outer_network["lines"][OUTER]
    inset = _ring_polygon(outer_line).buffer(-spaced.INSET_M, quad_segs=32)
    if inset.is_empty:
        raise ValueError("M09 has no interior after the 5.05 km road search inset")
    water = spaced._water(context)
    streets = network.read(network.STREETS) if streets is None else streets
    roads, bank_roads, paths = spaced._graph(streets, inset, water)
    shared = {code for stop in outer_line["station_ids"]
              for code in outer_network["stations"][stop]["lines"]} - {OUTER, INNER}
    rail = {code: LineString(network.Track(line["geometry"]).points)
            for code, line in outer_network["lines"].items() if code not in {OUTER, INNER}}
    trials, rejected = _candidate_trials(prep(inset), bank_roads, paths)
    wet = prep(water)
    checked = []
    checked_by_pair = Counter()
    selected = None
    connectivity_alternative = None
    for row in sorted(trials, key=_rank):
        if len(checked) == MAX_TRANSFER_TRIALS:
            break
        pair = tuple(sorted(row["bridges"]))
        if checked_by_pair[pair] >= MAX_TRIALS_PER_NAMED_PAIR:
            rejected["named bridge-pair transfer-screen budget"] += 1
            continue
        polygon = Polygon(network.Track(row["geometry"]).points)
        crossings = spaced._prospective_crossings(polygon.boundary, wet, rail)
        spokes = sorted(set(crossings) & shared)
        if len(crossings) < spaced.MIN_TRANSFERS or len(spokes) < spaced.MIN_DIRECT_SPOKES:
            rejected["insufficient mapped dry rail crossings"] += 1
            continue
        checked_by_pair[pair] += 1
        row["prospective_interchange_lines"], row["prospective_spokes"] = crossings, spokes
        try:
            failure = _screen(row, roads, outer_network, graph, context, shared, paths)
        except ValueError as error:
            failure = str(error)
        row["passes_connectivity_screen"] = failure is None
        if failure:
            row["rejection_reason"] = failure
        else:
            if selected is None:
                selected = row
            if (PREFERRED_BAND_KM[0] <= row["one_way_km"] <= PREFERRED_BAND_KM[1]
                    and len(row["screened_spokes"]) >= 3 and len(row["screened_transfer_sites"]) >= 7
                    and (connectivity_alternative is None
                         or _connectivity_rank(row) < _connectivity_rank(connectivity_alternative))):
                connectivity_alternative = row
        checked.append({key: value for key, value in row.items()
                        if key not in {"geometry", "mapped_water_crossings", "screened_transfer_sites"}}
                       | {"screened_transfer_count": len(row.get("screened_transfer_sites", []))})
    return {
        "selected": selected,
        "connectivity_alternative": connectivity_alternative if connectivity_alternative is not selected else None,
        "checked_candidates": checked,
        "cheap_screen_counts": dict(rejected),
        "footprint_screen_passes": len(trials),
        "target_route_km": TARGET_KM,
        "length_band_km": list(LENGTH_BAND_KM),
        "preferred_length_band_km": list(PREFERRED_BAND_KM),
        "minimum_required_separation_m": spaced.MIN_SEPARATION_M,
        "road_search_inset_m": spaced.INSET_M,
        "minimum_enclosed_area_km2": MIN_AREA_KM2,
        "minimum_footprint_width_km": MIN_WIDTH_KM,
        "direction_count": DIRECTION_COUNT,
        "bank_waypoint_grid_m": WAYPOINT_GRID_M,
        "direction_biases": list(DIRECTION_BIASES),
        "maximum_transfer_trials": MAX_TRANSFER_TRIALS,
        "maximum_trials_per_named_bridge_pair": MAX_TRIALS_PER_NAMED_PAIR,
        "inset_area_km2": inset.area / 1e6,
        "ranking_basis": "22–23 km band, at least 20 km, fewer >100° turns after 25 m simplification, then area and distance to target",
        "connectivity_alternative_ranking_basis": "22–23 km with at least three direct spokes and seven screened interchanges, "
                                                    "then most direct spokes, most interchanges and the area-led rank",
        "connectivity_basis": "At least three dry interchanges, two direct M09 spokes and one interchange on each bank",
    }
