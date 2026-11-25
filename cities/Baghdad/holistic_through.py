"""Screen direct Baghdad route axes against retained rail, streets and water."""

from collections import defaultdict
from dataclasses import dataclass
from itertools import pairwise
from math import floor

import numpy as np
from scipy.spatial import cKDTree

from .central_access import SNAP_M, read
from .holistic_network import (
    EXACT_CROSSING_M, INTERCHANGE_SPACING_M, LOCAL_METRES, MAJOR_ROADS, MAX_TERMINAL_LINK_KM,
    STREETS, Track, _crossings,
    _terminal_margin, dry_points,
)

MIN_LENGTH_M = 4_000
MAX_LENGTH_M = 22_000
MIN_TERMINAL_ONLY_PROXY = 22_000
STOP_SPACING_M = 650
MAX_STOP_GAP_M = 2_400
MAX_AXES = 40
MAX_AXES_PER_TILE = 6
MAX_SCREENED_PER_TILE = 65
MAX_SEED_TILES = 26
DEMAND_CELL_LIMIT = 220
DEMAND_RADIUS_M = 1_200
SEED_TILE_M = 4_000
MIN_MAJOR_ROAD_SHARE = .12
ROAD_CORRIDOR_M = 150
BRIDGE_OFFSET_M = 90
MAX_WATER_SPAN_M = 550
MAX_LANDING_OFFSET_M = 150
RAIL_DUPLICATION_M = 350
MAX_DUPLICATION_SHARE = .45

# Independently screened local hypotheses retained alongside the wider search.
# The exact network and pedestrian calculations still rank every admitted axis.
AUDITED_TERMINAL_PAIRS = (
    ("C1-infill-31200", "M-172", "G-1033-928"),
    ("M09-infill-07800", "M11-infill-00900", "G-1033-928"),
    ("Karkh", "M-159", "G-1031-928"),
)


@dataclass(frozen=True)
class DirectionalRoads:
    tree: cKDTree | None
    directions: np.ndarray

    @classmethod
    def from_paths(cls, paths):
        segments = np.asarray([pair for path in paths for pair in pairwise(path)
                               if pair[0] != pair[1]], dtype=float).reshape(-1, 2, 2)
        if not len(segments):
            return cls(None, np.empty((0, 2)))
        segments *= LOCAL_METRES
        deltas = segments[:, 1] - segments[:, 0]
        lengths = np.linalg.norm(deltas, axis=1)
        intervals = np.ceil(lengths / 30).astype(int)
        direction = deltas / lengths[:, None]
        points = np.concatenate([np.linspace(first, last, count + 1)
                                 for (first, last), count in zip(segments, intervals, strict=True)])
        return cls(cKDTree(points), np.repeat(direction, intervals + 1, axis=0))

    def nearby(self, points, heading, radius, angle_degrees):
        if self.tree is None:
            return np.full(len(points), np.inf)
        distance, indexes = self.tree.query(points, k=np.arange(1, min(12, self.tree.n) + 1))
        parallel = np.abs(self.directions[indexes] @ heading) >= np.cos(np.deg2rad(angle_degrees))
        return np.min(np.where(parallel & (distance <= radius), distance, np.inf), axis=1)


@dataclass(frozen=True)
class WaterGeometry:
    starts: np.ndarray
    ends: np.ndarray
    polygon_edges: np.ndarray

    @classmethod
    def from_context(cls, context):
        segments, polygon_edges = [], []
        for feature in context["layers"]["water"]:
            geometry = feature["geometry"]
            kind, coordinates = geometry["type"], geometry["coordinates"]
            if kind == "Polygon":
                paths = coordinates
            elif kind == "MultiPolygon":
                paths = [ring for polygon in coordinates for ring in polygon]
            elif kind == "MultiLineString":
                paths = coordinates
            elif kind == "LineString":
                paths = [coordinates]
            else:
                continue
            for path in paths:
                edges = [(a, b) for a, b in pairwise(path) if a != b]
                segments.extend(edges)
                polygon_edges.extend([kind.endswith("Polygon")] * len(edges))
        points = np.asarray(segments, dtype=float).reshape(-1, 2, 2) * LOCAL_METRES
        return cls(points[:, 0], points[:, 1], np.asarray(polygon_edges, dtype=bool))

    def intersections(self, start, end):
        lower, upper = np.minimum(start, end), np.maximum(start, end)
        possible = (np.all(np.maximum(self.starts, self.ends) >= lower, axis=1)
                    & np.all(np.minimum(self.starts, self.ends) <= upper, axis=1))
        starts = self.starts[possible]
        delta, edge = end - start, self.ends[possible] - starts
        cross = lambda a, b: a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0]
        with np.errstate(divide="ignore", invalid="ignore"):
            t = cross(starts - start, edge) / cross(delta, edge)
            u = cross(starts - start, delta) / cross(delta, edge)
        hits = (t > 0) & (t < 1) & (u >= 0) & (u <= 1)
        polygon_edges = self.polygon_edges[possible]
        return np.unique(t[hits & polygon_edges]), np.unique(t[hits & ~polygon_edges])


def _water_contacts(start, end, context, water):
    """Find polygon wet reaches and intersections with mapped linear waterways."""
    delta = end - start
    length = np.linalg.norm(delta)
    edges, centreline = water.intersections(start, end)
    chain = np.r_[0, edges, 1]
    midpoint = (chain[:-1] + chain[1:]) * .5
    dry = dry_points((start + midpoint[:, None] * delta) / LOCAL_METRES, context)
    wet_intervals = []
    for low, high, is_dry in zip(chain[:-1], chain[1:], dry, strict=True):
        if is_dry:
            continue
        if wet_intervals and abs(wet_intervals[-1][1] - low) * length < 5:
            wet_intervals[-1] = (wet_intervals[-1][0], high)
        else:
            wet_intervals.append((low, high))
    return sorted([*wet_intervals, *((t, t) for t in centreline
                                    if not any(a <= t <= b for a, b in wet_intervals))])


def _water_screen(start, end, context, water, bridges):
    """Require directionally consistent mapped carriageway bridge corroboration."""
    delta = end - start
    length = np.linalg.norm(delta)
    contacts = _water_contacts(start, end, context, water)
    records = []
    for low, high in contacts:
        wet_m = (high - low) * length
        if wet_m > MAX_WATER_SPAN_M or low * length < 80 or (1 - high) * length < 80:
            return None
        reach = np.linspace(low, high, int(np.ceil(wet_m / 30)) + 1)
        bridge_m = bridges.nearby(start + reach[:, None] * delta, delta / length, BRIDGE_OFFSET_M, 25)
        landing = np.array([low - 60 / length, high + 60 / length])
        approach = start + landing[:, None] * delta
        landbridge_m = bridges.nearby(approach, delta / length, MAX_LANDING_OFFSET_M, 25)
        if not (np.isfinite(bridge_m).all() and np.isfinite(landbridge_m).all()
                and dry_points(approach / LOCAL_METRES, context).all()):
            return None
        records.append({"chainage_km": round(float((low + high) * length / 2_000), 3),
                        "mapped_wet_width_m": round(wet_m),
                        "maximum_tagged_bridge_offset_m": round(float(bridge_m.max()), 1)})
    return records


def _street_layers(context):
    roads, bridges = [], []
    # The pedestrian graph removes some highways. Use the companion retained
    # OSM geometry for carriageway and bridge corroboration instead.
    features = read(STREETS)["features"] if "roads" in context["layers"] else []
    for feature in features:
        tags = feature["properties"]
        kind = (tags.get("highway") or "").removesuffix("_link")
        if tags.get("tunnel") not in (None, "no"):
            continue
        path = feature["geometry"]["coordinates"]
        if kind in MAJOR_ROADS:
            roads.append(path)
        if kind in MAJOR_ROADS.keys() | {"residential", "unclassified", "service"} and tags.get("bridge") == "yes":
            bridges.append(path)
    return DirectionalRoads.from_paths(roads), DirectionalRoads.from_paths(bridges)


def _demand_points(coverage_cells, graph):
    if coverage_cells is None:
        # A source-free proxy for exploratory callers. Count distinct active
        # 100 m street tiles per kilometre, rather than OSM node density.
        tiles = np.unique(np.floor(graph[3].data / 100).astype(int), axis=0)
        kilometre, count = np.unique(tiles // 10, axis=0, return_counts=True)
        order = np.argsort(-count, kind="stable")[:DEMAND_CELL_LIMIT]
        return kilometre[order] * 1000 + 500, count[order]
    rows = sorted(((row["beyond_1200_m"], *row["coordinates"])
                   for row in coverage_cells if row["beyond_1200_m"] > 0), reverse=True)
    if not rows:
        return np.empty((0, 2)), np.empty(0)
    weights, lon, lat = np.asarray(rows[:DEMAND_CELL_LIMIT]).T
    return np.column_stack((lon, lat)) * LOCAL_METRES, weights


def _pair_options(points, station_lines, demand, weights):
    pairs = cKDTree(points).query_pairs(MAX_LENGTH_M, output_type="ndarray")
    pairs = sorted((int(a), int(b)) for a, b in pairs if station_lines[a].isdisjoint(station_lines[b]))
    groups = defaultdict(list)
    for offset in range(0, len(pairs), 800):
        indexes = np.asarray(pairs[offset:offset + 800])
        start, end = points[indexes[:, 0]], points[indexes[:, 1]]
        delta = end - start
        length = np.linalg.norm(delta, axis=1)
        valid = length >= MIN_LENGTH_M
        start, end, delta, length, indexes = (item[valid] for item in (start, end, delta, length, indexes))
        dx = demand[None, :, 0] - start[:, None, 0]
        dy = demand[None, :, 1] - start[:, None, 1]
        heading = delta / length[:, None]
        along = dx * heading[:, 0, None] + dy * heading[:, 1, None]
        lateral = np.abs(dx * heading[:, 1, None] - dy * heading[:, 0, None])
        gain = np.where((along >= STOP_SPACING_M) & (along <= length[:, None] - STOP_SPACING_M),
                        np.maximum(1 - lateral / DEMAND_RADIUS_M, 0) * weights, 0)
        score = gain.sum(axis=1)
        for row in np.flatnonzero((gain > 0).sum(axis=1) >= 2):
            anchor = demand[int(gain[row].argmax())]
            tile = tuple(int(floor(value / SEED_TILE_M)) for value in anchor)
            bearing = float(np.degrees(np.arctan2(heading[row, 1], heading[row, 0])) % 180)
            length_bin = int(np.searchsorted([9_500, 14_000], length[row]))
            groups[(tile, int(bearing // 30), length_bin)].append(
                (float(score[row]), *indexes[row], bearing, float(length[row])))
    return {key: sorted(rows, key=lambda row: (-row[0], row[1], row[2])) for key, rows in groups.items()}


def _candidate_crossings(track, tracks, network, graph, context):
    options = []
    for line, base in tracks.items():
        record = network["lines"][line]
        for point, (our, other) in _crossings(track, base).items():
            if not STOP_SPACING_M <= our * 1000 <= track.km * 1000 - STOP_SPACING_M:
                continue
            margin = _terminal_margin(record, other)
            if margin >= INTERCHANGE_SPACING_M + .1:
                options.append((our, line, point))
            else:
                if any(np.linalg.norm((np.asarray(network["stations"][stop]["coordinates"]) - point)
                                      * LOCAL_METRES) <= EXACT_CROSSING_M for stop in record["station_ids"]):
                    options.append((our, line, point))
    if not options:
        return []
    coords = np.asarray([position for _, _, position in options])
    offsets, _ = graph[3].query(coords * LOCAL_METRES)
    dry = dry_points(coords, context)
    result = []
    for i in sorted(np.flatnonzero((offsets <= SNAP_M) & dry), key=lambda i: (offsets[i], options[i])):
        chain, line, point = options[i]
        if any(code == line or abs(chain - existing) * 1000 < STOP_SPACING_M
               for existing, code, _ in result):
            continue
        result.append((chain, line, point))
    return sorted(result)


def _platforms(track, crossings, other_stations, graph, context):
    # A sampled axis still gives an exact track position. Streets are used
    # to locate passenger entrances and never to move the platform off track.
    chain = np.arange(.125, track.km, .125)
    points = np.asarray([track.at(metres) for metres in chain])
    street, _ = graph[3].query(points * LOCAL_METRES)
    distance, _ = other_stations.query(points * LOCAL_METRES)
    dry = dry_points(points, context)
    valid = (street <= SNAP_M) & dry & (distance >= 300)
    fixed = [0., *(position for position, _, _ in crossings), track.km]
    stops = []
    for low, high in pairwise(fixed):
        span = high - low
        count = max(1, int(round(span / 1.23)))
        targets = np.linspace(low, high, count + 1)[1:-1]
        previous = low
        for target in targets:
            candidates = np.flatnonzero(valid & (chain >= previous + STOP_SPACING_M / 1000)
                                        & (chain <= high - STOP_SPACING_M / 1000)
                                        & (np.abs(chain - target) <= .6))
            if len(candidates):
                index = min(candidates, key=lambda i: (abs(chain[i] - target) * 160 + street[i], i))
                stops.append((float(chain[index]), float(street[index])))
                previous = chain[index]
    if len(stops) < 2 or max(np.diff(sorted([*fixed, *(km for km, _ in stops)]))) > MAX_STOP_GAP_M / 1000:
        return []
    return stops


def _screen_axis(pair, ids, points, tracks, context, network, graph, roads, bridges, water, rail,
                 station_tree, allow_short_connector=False):
    proxy, first, second, bearing, length = pair
    start, end = points[first], points[second]
    samples = np.linspace(start, end, int(np.ceil(length / 125)) + 1)[1:-1]
    road_offsets = roads.nearby(samples, (end - start) / length, ROAD_CORRIDOR_M, 35)
    road_share = float(np.isfinite(road_offsets).mean())
    duplicate_share = float((rail.query(samples)[0] <= RAIL_DUPLICATION_M).mean())
    if road_share < MIN_MAJOR_ROAD_SHARE or duplicate_share > MAX_DUPLICATION_SHARE:
        return None
    water_contacts = _water_screen(start, end, context, water, bridges)
    if water_contacts is None:
        return None
    # Maintain the retained coordinates verbatim for interchange identity.
    terminals = [ids[first], ids[second]]
    geometry = [network["stations"][stop]["coordinates"] for stop in terminals]
    track = Track(geometry)
    crossings = _candidate_crossings(track, tracks, network, graph, context)
    terminal_link_only = not crossings
    if terminal_link_only and not (allow_short_connector and track.km <= MAX_TERMINAL_LINK_KM
                                   and proxy >= MIN_TERMINAL_ONLY_PROXY):
        return None
    platforms = _platforms(track, crossings, station_tree, graph, context)
    if not platforms:
        return None
    code = f"T-{terminals[0]}--{terminals[1]}"
    names = [network["stations"][stop].get("name") or stop for stop in terminals]
    return {
        "key": code,
        "id": code,
        "name": "–".join(names),
        "geometry": geometry,
        "terminal_ids": terminals,
        "one_way_km": track.km,
        "directness": 1.0,
        "basis": "Direct elevated search axis between existing passenger stations",

        "stops": [
            {"id": f"{code}-S{i:02d}", "name": f"New station · km {km:g}", "chainage_km": km,
             "coordinates": track.at(km), "street_offset_m": round(snap, 1),
             "basis": "Dry alignment position near a retained pedestrian graph node"}
            for i, (km, snap) in enumerate(platforms, 1)
        ],
        "terminal_link_only": terminal_link_only,
        "required_interchanges": [
            {"line_id": line, "point": list(point), "chainage_km": km}
            for km, line, point in crossings
        ],
        "screening": {
            "axis_bearing_degrees": round(bearing, 2),
            "distance_proxy_score": round(proxy, 2),
            "major_surface_road_share": round(road_share, 3),
            "major_surface_road_test": "125 m axis samples within 150 m and 35° of a mapped major road",
            "near_existing_rail_share": round(duplicate_share, 3),
            "mapped_water_contacts": water_contacts,
            "alignment_limits": "Survey, curvature, guideway and bridge clearance, "
                                "land take, entrances and pedestrian accessibility require verification.",
        },
    }


def generate(network, context, graph, coverage_cells=None):
    """Return geometrically viable search axes for exact street-walk comparison."""
    demand, weights = _demand_points(coverage_cells, graph)
    if len(demand) < 2 or len(network["stations"]) < 2:
        return []
    ids = sorted(network["stations"])
    all_coords = np.asarray([network["stations"][key]["coordinates"] for key in ids])
    points = all_coords * LOCAL_METRES
    station_tree = cKDTree(points)
    nearby_demand = cKDTree(demand).query(points)[0]
    eligible = ((graph[3].query(points)[0] <= SNAP_M) & (nearby_demand <= MAX_LENGTH_M)
                & dry_points(all_coords, context))
    ids = [key for key, keep in zip(ids, eligible, strict=True) if keep]
    points = points[eligible]
    line_sets = [set(network["stations"][key]["lines"]) for key in ids]
    groups = _pair_options(points, line_sets, demand, weights)
    if not groups:
        return []

    tracks = {code: Track(line["geometry"]) for code, line in sorted(network["lines"].items())}
    rail = cKDTree(np.concatenate([
        np.asarray([track.at(x) for x in np.linspace(0, track.km, int(np.ceil(track.km * 12)) + 1)])
        * LOCAL_METRES for track in tracks.values()
    ]))
    roads, bridges = _street_layers(context)
    water = WaterGeometry.from_context(context)
    groups = sorted(groups.items(), key=lambda item: (-item[1][0][0], item[0]))
    tile_demand = defaultdict(float)
    for point, weight in zip(demand, weights, strict=True):
        tile_demand[tuple(int(value // SEED_TILE_M) for value in point)] += weight
    # Round-robin over gaps, then headings and lengths, so the populous east
    # does not fill the geometry budget before Karkh, central and south axes.
    tiles = defaultdict(list)
    for group, pairs in groups:
        tiles[group[0]].append((group, pairs))
    accepted_axes = []
    accepted_by_tile = {}
    audited = []
    pair_lookup = {(ids[row[1]], ids[row[2]]): row for _, pairs in groups for row in pairs}
    for first, second, gap in AUDITED_TERMINAL_PAIRS if coverage_cells is not None else ():
        pair = pair_lookup.get(tuple(sorted((first, second))))
        if pair is None:
            continue
        row = _screen_axis(pair, ids, points, tracks, context, network, graph,
                           roads, bridges, water, rail, station_tree)
        if row is None:
            continue
        row["screening"]["seed_gap_id"] = gap
        row["screening"]["demand_proxy_basis"] = "Uncovered people in 1 km cells"
        row["screening"]["seed_basis"] = "Independently screened pair of existing terminals"
        audited.append(row)
        _, a, b, angle, length = pair
        accepted_axes.append(((points[a] + points[b]) / 2, angle, length))
    ordered_tiles = sorted(tiles, key=lambda tile: (-tile_demand[tile], tile))[:MAX_SEED_TILES]
    for tile in ordered_tiles:
        accepted = []
        screened = 0
        for depth in range(12):
            for group, pairs in tiles[tile]:
                if depth >= len(pairs):
                    continue
                pair = pairs[depth]
                _, a, b, angle, length = pair
                midpoint = (points[a] + points[b]) / 2
                if any(np.linalg.norm(midpoint - centre) < 950 and abs(length - prior_length) < 2_000
                       and min(abs(angle - prior_angle), 180 - abs(angle - prior_angle)) < 9
                       for centre, prior_angle, prior_length in accepted_axes):
                    continue
                screened += 1
                row = _screen_axis(pair, ids, points, tracks, context, network, graph,
                                   roads, bridges, water, rail, station_tree,
                                   allow_short_connector=coverage_cells is not None and tile in ordered_tiles[:5])
                if row is not None:
                    row["screening"]["seed_gap_id"] = f"G-{tile[0]}-{tile[1]}"
                    row["screening"]["demand_proxy_basis"] = (
                        "Uncovered people in 1 km cells" if coverage_cells is not None
                        else "Density of mapped pedestrian street tiles")
                    accepted.append(row)
                    accepted_axes.append((midpoint, angle, length))
                if len(accepted) >= MAX_AXES_PER_TILE or screened >= MAX_SCREENED_PER_TILE:
                    break
            if len(accepted) >= MAX_AXES_PER_TILE or screened >= MAX_SCREENED_PER_TILE:
                break
        if accepted:
            accepted_by_tile[tile] = accepted
    pool = [*audited, *(tile_candidates[index]
                        for index in range(MAX_AXES_PER_TILE)
                        for tile_candidates in accepted_by_tile.values() if index < len(tile_candidates))]
    candidates = pool[:MAX_AXES]
    for i, candidate in enumerate(candidates, 1):
        code = f"T{i:02d}"
        candidate["id"] = code
        for j, stop in enumerate(candidate["stops"], 1):
            stop["id"] = f"{code}-S{j:02d}"
    return candidates
