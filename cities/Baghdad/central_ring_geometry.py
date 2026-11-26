"""Search mapped Baghdad central loops and measure their station walks."""

from collections import Counter
from copy import deepcopy
from itertools import pairwise, product
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from shapely import box, make_valid
from shapely.affinity import scale
from shapely.geometry import LineString, Polygon, shape
from shapely.ops import unary_union
from shapely.prepared import prep

from . import central_access, holistic_network as network
from . import holistic_orbitals as orbital, network_station_sites as sites
from . import spaced_ring_geometry as spaced, wider_ring_geometry as wider
from .ring_corridors import INNER, OUTER, _refresh_transfers, _restore_walk_links, _ring_polygon, _single_parts


WALK_M = 1300
CANDIDATES_PER_BRIDGE_PAIR = 3
MAX_STATION_TRIALS = 12
ADDITIONAL_BRIDGES = {
    4295613: "Al-A’imma Bridge",
    4493480: "Al-Sarafiya Bridge",
    494461243: "Al-Jadriya Bridge",
    626727315: "Al-Jadriya Bridge",
}
PRIOR_MAP = central_access.CITY / "maps/baghdad-ring-network.geojson"


def _road_inputs(outer, destination_points, context):
    west, south, east, north = central_access.CORE
    anchors = np.vstack((destination_points, [[west, south], [east, north]])) * network.LOCAL_METRES
    target = box(*anchors.min(axis=0), *anchors.max(axis=0))
    water = spaced._water(context)
    # This is a search window around study points, not a separation constraint.
    streets = network.read(network.STREETS)
    roads, bank_roads, paths = spaced._graph(streets, outer.intersection(target.buffer(3 * WALK_M)), water)
    for feature in streets["features"]:
        way = feature["id"]
        if way not in ADDITIONAL_BRIDGES or feature["properties"].get("bridge") != "yes":
            continue
        path = list(map(tuple, feature["geometry"]["coordinates"]))
        if not all(roads.get(a, {}).get(b, (None, None))[1] == way for a, b in pairwise(path)):
            continue
        projected = LineString(np.asarray(path) * network.LOCAL_METRES)
        wet_length = max((part.length for part in _single_parts(projected.intersection(water))), default=0.)
        if wet_length < spaced.MAIN_CHANNEL_MIN_M:
            continue
        paths[way] = (ADDITIONAL_BRIDGES[way], path if path[0][0] < path[-1][0] else path[::-1])
        for a, b in pairwise(path):
            bank_roads[a].pop(b, None)
            bank_roads[b].pop(a, None)
    river = prep(unary_union([
        scale(make_valid(shape(row["geometry"])), *network.LOCAL_METRES, origin=(0, 0))
        for row in context["layers"]["water"] if row["properties"].get("kind_detail") == "river"
    ]))
    for a, neighbors in bank_roads.items():
        for b, (_, _, is_bridge) in list(neighbors.items()):
            if a < b and is_bridge and river.intersects(LineString(np.asarray([a, b]) * network.LOCAL_METRES)):
                bank_roads[a].pop(b)
                bank_roads[b].pop(a)
    return roads, bank_roads, paths, water


def _central_population(population):
    west, south, east, north = central_access.CORE
    points = population.coordinates
    return ((points >= (west, south)) & (points <= (east, north))).all(axis=1)


def _proxy_targets(population, central):
    points = population.coordinates[central] * network.LOCAL_METRES
    _, tiles = np.unique(np.floor(points / 400), axis=0, return_inverse=True)
    counts = population.counts[central]
    weights = np.bincount(tiles, weights=counts)
    xy = np.column_stack([np.bincount(tiles, weights=counts * p) / weights for p in points.T])
    return xy, weights


def _leg_access(leg, centres, population_xy):
    xy = np.asarray(leg) * network.LOCAL_METRES
    chain = np.r_[0., np.linalg.norm(np.diff(xy, axis=0), axis=1).cumsum()]
    along = np.r_[np.arange(0., chain[-1], 120.), chain[-1]]
    trace_tree = cKDTree(np.column_stack([np.interp(along, chain, axis) for axis in xy.T]))
    return trace_tree.query(centres)[0], trace_tree.query(population_xy)[0] <= WALK_M, chain[-1]


def _road_trials(outer, bank_roads, paths, centres, population_xy, weights):
    """Rank a finite set of connected mapped traces before station evaluation."""
    boundary = prep(outer)
    counts = Counter()
    by_pair = {}
    leg_access = {}
    for ways, (east, west) in wider._bank_legs(bank_roads, paths).items():
        first, second = (paths[way][1] for way in ways)
        name_pair = tuple(sorted(paths[way][0] for way in ways))
        for leg in (*east, *west):
            if leg not in leg_access:
                leg_access[leg] = _leg_access(leg, centres, population_xy)
        pair_trials = []
        for (right, right_variant), (left, left_variant) in product(east.items(), west.items()):
            east_offsets, east_cells, east_length = leg_access[right]
            west_offsets, west_cells, west_length = leg_access[left]
            centre_offsets = np.minimum(east_offsets, west_offsets)
            rank = (int((centre_offsets > WALK_M).sum()), -float(weights[east_cells | west_cells].sum()),
                    float(centre_offsets.max()), east_length + west_length, ways, right_variant, left_variant)
            pair_trials.append((rank, right, left))
        counts["bank leg combinations"] += len(pair_trials)
        distinct = {}
        for rank, right, left in sorted(pair_trials)[:24]:
            trace = first + list(right[1:-1]) + second[::-1] + list(left[-2:0:-1]) + first[:1]
            polygon = Polygon(np.asarray(trace) * network.LOCAL_METRES)
            if not polygon.is_valid or not boundary.contains_properly(polygon):
                counts["non-simple or not strictly inside M09"] += 1
                continue
            area = polygon.area / 1e6
            proxy_key = rank[:2]
            full_rank = (*rank[:3], -area, *rank[3:])
            trial = (full_rank, trace, area, rank[-2:])
            if proxy_key not in distinct or trial < distinct[proxy_key]:
                distinct[proxy_key] = trial
            counts["simple nested road traces"] += 1
        by_pair.setdefault(name_pair, []).extend(distinct.values())
    shortlist = [row for trials in by_pair.values() for row in sorted(trials)[:CANDIDATES_PER_BRIDGE_PAIR]]
    return sorted(shortlist)[:MAX_STATION_TRIALS], counts


def _walk_access(stops, graph, population, central, destinations):
    distances, unmatched = central_access.distances_from_stops(stops, graph)
    walk = distances[population.nodes[central]] + population.offsets_m[central]
    covered = (walk <= WALK_M) & (population.offsets_m[central] <= central_access.SNAP_M)
    counts = population.counts[central]
    street_offsets, indexes = graph[3].query(central_access._points([row.coordinates for row in destinations]))
    centre_walks = street_offsets + distances[graph[2][indexes]]
    centres = [
        {"id": row.id, "name": row.name, "walk_m": round(float(walk_m), 1) if np.isfinite(walk_m)
         and offset <= central_access.SNAP_M else None,
         "within_walk": bool(offset <= central_access.SNAP_M and walk_m <= WALK_M)}
        for row, offset, walk_m in zip(destinations, street_offsets, centre_walks, strict=True)]
    people = float(counts[covered].sum())
    return {"walk_limit_m": WALK_M, "central_bounds": list(central_access.CORE),
            "population": round(float(counts.sum())), "covered_people": round(people),
            "covered_share_pct": round(100 * people / float(counts.sum()), 3),
            "centres": centres, "centres_within_walk": sum(row["within_walk"] for row in centres),
            "unmatched_stations": unmatched}


def _junction_calls(line, stations, track, graph, context, water, destinations):
    """Fill uncovered intervals using dry mapped walking junctions by the road trace."""
    raw, matrix, active, tree, _ = graph
    longitudes, latitudes = raw["lon"], raw["lat"]
    places, names = network._place_index(context)
    # Search pedestrian junctions within the same snap range as interchange siting.
    samples = np.arange(0., track.km, .06)
    sampled = central_access._points([track.at(site) for site in samples])
    indices = sorted({index for row in tree.query_ball_point(sampled, network.TRANSFER_SNAP_M + 30.)
                      for index in row})
    candidates = []
    wet = prep(water)
    for index in indices:
        node = active[index]
        if matrix.indptr[node + 1] - matrix.indptr[node] < 3:
            continue
        junction = (float(longitudes[node]), float(latitudes[node]))
        km, offset, _ = track.locate(junction)
        if offset > sites.MAX_SNAP_M:
            continue
        point = track.at(km)
        connector = LineString(np.asarray([point, junction]) * network.LOCAL_METRES)
        if not wet.intersects(connector):
            candidates.append((km, offset, junction, point))
    # Infill towards the middle of gaps, and prefer an actual street junction
    # close to that position. Shared rail calls take precedence throughout.
    fixed = sorted(line["station_chainage_km"].values())
    destination_points = np.asarray([row.coordinates for row in destinations]) * network.LOCAL_METRES
    held_gaps = []
    for low, high in pairwise([*fixed, track.km]):
        intervals = max(1, round((high - low) / (WALK_M / 1000)))
        last = low
        for target in np.linspace(low, high, intervals + 1)[1:-1]:
            choices = [row for row in candidates if row[0] - last >= orbital.MIN_STOP_GAP_KM
                       and high - row[0] >= orbital.MIN_STOP_GAP_KM
                       and abs(row[0] - target) <= .5]
            if not choices:
                held_gaps.append(round(float(target), 3))
                continue
            km, offset, junction, point = min(choices, key=lambda row: (
                abs(row[0] - target) * 1000 + row[1]
                + np.linalg.norm(destination_points - np.asarray(row[3]) * network.LOCAL_METRES, axis=1).min() / 5,
                row[0]))
            distance, place = places.query(np.asarray(point) * network.LOCAL_METRES)
            name = names[place][1] if distance <= 1100 else "Central orbital"
            code = f"{INNER}-{round(km * 1000):05d}"
            stations[code] = {"name": f"{name} · {code}", "coordinates": point, "lines": [INNER],
                              "basis": "Provisional orbital platform beside mapped pedestrian junction",
                              "street_junction_coordinates": list(junction), "street_offset_m": round(offset, 1)}
            network._add(line, code, km)
            last = km
    return held_gaps


def _insert(outer_network, trace, contacts, crossings, prospective, graph, context, water, destinations):
    revised = deepcopy(outer_network)
    links = revised.pop("station_site_links", None)
    lines, stations = revised["lines"], revised["stations"]
    track = network.Track(trace)
    line = lines[INNER] = {
        "name": "Baghdad central orbital",
        "geometry": track.coordinates.tolist(),
        "loop": True, "one_way_km": track.km, "station_ids": ["reference"],
        "station_chainage_km": {"reference": 0.},
        "source_sections": [row["name"] for row in crossings],
        "basis": "Mapped major roads and named bridge approaches for an independent elevated railway",
    }
    first, second = crossings
    banks = (first["exit_m"] / 1000, second["entry_m"] / 1000, second["exit_m"] / 1000)
    crossing_network = {"lines": {code: lines[code] for code in sorted(prospective | {INNER})}, "stations": stations}
    transfers = orbital._interchanges(crossing_network, track, graph, context, banks)
    direct = {code for stop in lines[OUTER]["station_ids"] for code in stations[stop]["lines"]}
    spokes = sorted(direct & {row["line_id"] for row in transfers})
    bank_counts = dict(Counter(row["bank"] for row in transfers))
    if len(transfers) < spaced.MIN_TRANSFERS or len(spokes) < spaced.MIN_DIRECT_SPOKES or len(bank_counts) < 2:
        raise ValueError("Too few dry interchanges, M09 spokes or banks represented")
    if lines[OUTER] != outer_network["lines"][OUTER]:
        raise ValueError("Central ring revised the retained M09")
    origin = transfers[0]["chainage_km"]
    rotated = network.Track(network._concatenate(track.between(origin, track.km), track.between(0., origin)))
    line.update({"geometry": rotated.coordinates.tolist(), "one_way_km": rotated.km})
    line["station_ids"].remove("reference")
    line["station_chainage_km"] = {stop: km - origin
                                  for stop, km in line["station_chainage_km"].items() if stop != "reference"}
    for row in transfers:
        row["chainage_km"] -= origin
    held = _junction_calls(line, stations, rotated, graph, context, water, destinations)
    _refresh_transfers(revised)
    removed = _restore_walk_links(revised, outer_network, links)
    sources = (Path(__file__), Path(orbital.__file__), Path(wider.__file__),
               Path(spaced.__file__), Path(sites.__file__), network.STREETS, PRIOR_MAP)
    revised.setdefault("source_sha256", {}).update({
        source.relative_to(network.ROOT).as_posix(): network.digest(source) for source in sources})
    revised["physical_accepted"] = revised["operating_timetable_validated"] = False
    revised["topology"] = network.validate(revised)
    evidence = {
        "line_id": INNER, "one_way_km": rotated.km, "tunnels": 0,
        "topology": "Tigris-straddling", "bridges": line["source_sections"],
        "bridge_ways": [row["road_way_id"] for row in crossings],
        "transfers_by_bank": bank_counts, "transfer_count": len(transfers),
        "transfer_sites": transfers, "direct_spokes_between_rings": spokes,
        "stations": len(line["station_ids"]), "unfilled_junction_targets_km": held,
        "maximum_station_gap_km": round(float(max(np.diff([
            *(line["station_chainage_km"][stop] for stop in line["station_ids"]), rotated.km]))), 3),
        "removed_walk_links": removed,
        "mapped_water_crossings": [
            {key: value for key, value in row.items() if key not in {"entry_m", "exit_m"}} | {
                "entry_km": round((row["entry_m"] / 1000 - origin) % track.km, 3),
                "exit_km": round((row["exit_m"] / 1000 - origin) % track.km, 3),
            } for row in contacts],
        **spaced.separation(lines[OUTER], line["geometry"]),
    }
    if evidence["minimum_ring_separation_m"] <= 0.:
        raise ValueError("Central ring touches or crosses M09")
    return network._identity(revised), evidence


def alternatives(outer_network, graph, context, *, population, destinations):
    """Screen two distinct central loops with real pedestrian-network catchments."""
    network.validate(outer_network)
    if INNER in outer_network["lines"]:
        raise ValueError("Central ring alternatives require an unused M15 route ID")
    destinations = tuple(destinations)
    centres = np.asarray([row.coordinates for row in destinations])
    outer = _ring_polygon(outer_network["lines"][OUTER])
    roads, bank_roads, paths, water = _road_inputs(outer, centres, context)
    central = _central_population(population)
    population_xy, weights = _proxy_targets(population, central)
    short, counts = _road_trials(outer, bank_roads, paths, centres * network.LOCAL_METRES, population_xy, weights)
    old = network.read(PRIOR_MAP)["features"]
    previous_outer = next(row["geometry"]["coordinates"] for row in old
                          if row["properties"].get("kind") == "line" and row["properties"]["line_id"] == OUTER)
    if outer_network["lines"][OUTER]["geometry"] != previous_outer:
        raise ValueError("Central ring comparison must preserve the published M09 trace")
    previous_inner = next(row["geometry"]["coordinates"] for row in old
                          if row["properties"].get("kind") == "line" and row["properties"]["line_id"] == INNER)
    core = box(*(np.asarray(central_access.CORE) * np.tile(network.LOCAL_METRES, 2))).difference(water)

    def footprint(coordinates):
        polygon = Polygon(np.asarray(coordinates) * network.LOCAL_METRES)
        enclosed = polygon.intersection(core).area
        return {"enclosed_area_km2": polygon.area / 1e6,
                "enclosed_central_dry_land_km2": enclosed / 1e6,
                "enclosed_central_dry_land_pct": 100 * enclosed / core.area}

    old_stops = {row["properties"]["station_id"]: row["geometry"]["coordinates"] for row in old
                 if row["properties"].get("kind") in {"station", "interchange"}
                 and INNER in row["properties"]["lines"]}
    prior = _walk_access(old_stops, graph, population, central, destinations)
    prior.update(footprint(previous_inner))
    prior["one_way_km"] = network.Track(previous_inner).km
    rail = {code: LineString(network.Track(line["geometry"]).points)
            for code, line in outer_network["lines"].items() if code != OUTER}
    shared = {code for stop in outer_network["lines"][OUTER]["station_ids"]
              for code in outer_network["stations"][stop]["lines"]} - {OUTER}
    wet = prep(water)
    checked = []
    eligible = []
    for rank, trace, area, variants in short:
        ways = rank[-3]
        option = {"bridge_ways": list(ways), "routing_variants": list(variants),
                  "bridges": [paths[way][0] for way in ways], "enclosed_area_km2": area}
        checked.append(option)
        try:
            track = network.Track(trace)
            prospective = set(spaced._prospective_crossings(LineString(track.points), wet, rail))
            if len(prospective) < spaced.MIN_TRANSFERS or len(prospective & shared) < spaced.MIN_DIRECT_SPOKES:
                raise ValueError("Too few dry rail crossings or prospective M09 spokes")
            contacts = orbital._water_crossings(track, roads, context)
            main = {row["road_way_id"]: row for row in contacts
                    if row["mapped_wet_width_m"] >= spaced.MAIN_CHANNEL_MIN_M}
            if main.keys() != set(ways):
                raise ValueError(f"Main-channel crossing ways {sorted(main)} differ from the named bridge ways {sorted(ways)}")
            crossings = [main[way] | {"name": paths[way][0]} for way in ways]
            by_way = {row["road_way_id"]: row for row in crossings}
            contacts = [by_way.get(row["road_way_id"], row) for row in contacts]
            revised, evidence = _insert(outer_network, trace, contacts, crossings, prospective, graph, context, water, destinations)
            line = revised["lines"][INNER]
            stops = {stop: revised["stations"][stop]["coordinates"] for stop in line["station_ids"]}
            access = _walk_access(stops, graph, population, central, destinations)
            option.update(evidence | footprint(line["geometry"]) | {"ring_only_access": access})
            if access["covered_people"] <= prior["covered_people"]:
                raise ValueError("Central population access does not improve on the previous published ring")
            eligible.append((revised, option))
        except ValueError as error:
            option["rejection_reason"] = str(error)

    def access_rank(row):
        _, option = row
        access = option["ring_only_access"]
        return (access["centres_within_walk"], access["covered_people"],
                len(option["direct_spokes_between_rings"]), option["transfer_count"],
                option["enclosed_area_km2"], -option["one_way_km"])

    networks, evidence = {}, {}
    if eligible:
        primary = max(eligible, key=access_rank)
        networks["central-coverage"], evidence["central-coverage"] = primary
        competitors = [row for row in eligible if set(row[1]["bridges"]) != set(primary[1]["bridges"])]
        if competitors:
            networks["central-connections"], evidence["central-connections"] = max(
                competitors, key=lambda row: (row[1]["ring_only_access"]["centres_within_walk"],
                                               len(row[1]["direct_spokes_between_rings"]),
                                               row[1]["transfer_count"], access_rank(row)))
    return {"selected": evidence.get("central-coverage"), "connectivity_alternative": evidence.get("central-connections"),
            "networks": networks, "evidence": evidence, "prior_ring_access": prior,
            "checked_candidates": checked, "cheap_screen_counts": dict(counts),
            "maximum_station_trials": MAX_STATION_TRIALS,
            "ranking_basis": "Named centres and central residents within 1,300 m by mapped pedestrian walks, "
                             "then M09 spokes, transfers, enclosed area and route length."}
