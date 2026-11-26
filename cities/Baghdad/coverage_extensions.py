"""Extend existing between-bank trunks to net new suburban catchments."""

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from itertools import pairwise

import numpy as np
from scipy.spatial import cKDTree
from shapely import LineString, Polygon

from . import central_access, coverage_trunks as trunks, holistic_access, holistic_network as rail
from . import holistic_through, straight_through_layout, third_ring_through

MIN_EXTENSION_KM = 1.5
MAX_EXTENSION_KM = 20.
MAX_TERMINAL_OPTIONS = 20
MIN_NEW_RESIDENTS_PER_KM = 250


@dataclass(eq=False)
class Extension:
    route: str
    end: int
    former_terminal: str
    track: rail.Track
    stops: list
    water: list
    reach: dict


def _full_track(core, tail, end):
    points = (rail._concatenate(tail.coordinates[::-1], core.coordinates) if end == 0
              else rail._concatenate(core.coordinates, tail.coordinates))
    return rail.Track(points)


def _terminals(start, heading, points, demand, people):
    """Bound the exact search across bearings and lengths on the outward bank."""
    delta = points - start
    distance = np.linalg.norm(delta, axis=1)
    eligible = np.flatnonzero((distance >= MIN_EXTENSION_KM * 1000)
                              & (distance <= MAX_EXTENSION_KM * 1000)
                              & (delta @ heading >= distance * np.cos(np.deg2rad(trunks.MAX_TURN_DEG))))
    relative = demand - start
    options = []
    for index in eligible:
        length = distance[index]
        direction = delta[index] / length
        along = relative @ direction
        offset = np.abs(relative[:, 0] * direction[1] - relative[:, 1] * direction[0])
        covered = (along >= trunks.WALK_M / 2) & (along <= length + trunks.WALK_M) & (offset <= trunks.WALK_M)
        score = float(people[covered] @ (1 - offset[covered] / trunks.WALK_M))
        sector = min(4, int(length / 4000))
        bearing = int(third_ring_through._bearing(np.asarray((start, points[index]))) // 10)
        if score:
            options.append((-score / np.sqrt(length), -score, int(index), sector, bearing))

    sectors, shortlist = Counter(), []
    for _, _, index, sector, bearing in sorted(options):
        if sectors[sector, bearing] == 2:
            continue
        shortlist.append(points[index])
        sectors[sector, bearing] += 1
        if len(shortlist) == MAX_TERMINAL_OPTIONS:
            break
    return shortlist


def _stops(track, stations, streets, context, demand_tree, people):
    """Find a spaced sequence of street-linked platforms from the last core stop."""
    km = np.r_[0., np.arange(.125, track.km, .125), track.km]
    coordinates = np.asarray([track.at(float(value)) for value in km])
    points = coordinates * rail.LOCAL_METRES
    offset = streets.query(points)[0]
    legal = ((offset <= central_access.SNAP_M) & rail.dry_points(coordinates, context)
             & (stations.query(points)[0] >= trunks.STATION_SPACING_M - 1e-6))
    legal[0] = True
    if not legal[-1]:
        return []
    legal_km = km[legal]
    coordinate_rows = coordinates[legal]
    weights = np.array([people[indices].sum()
                        for indices in demand_tree.query_ball_point(points[legal], trunks.WALK_M)])
    parents = np.full(len(legal_km), -1)
    merit = np.full(len(legal_km), -np.inf)
    merit[0] = 0
    scale = max(float(weights.max()), 1.)
    for index in range(1, len(legal_km)):
        gap = legal_km[index] - legal_km[:index]
        links = np.flatnonzero((gap >= trunks.STATION_SPACING_M / 1000 - 1e-9)
                               & (gap <= trunks.MAX_STOP_GAP_M / 1000 + 1e-9) & np.isfinite(merit[:index]))
        if not len(links):
            continue
        # Favour useful catchments while penalising excessive calls and empty reaches.
        rewards = merit[links] - .55 * (gap[links] - 1.9)**2
        upstream = int(rewards.argmax())
        parents[index] = links[upstream]
        merit[index] = rewards[upstream] + weights[index] / scale - .5

    if parents[-1] < 0:
        return []
    selected = []
    index = len(legal_km) - 1
    while index:
        selected.append((float(legal_km[index]), coordinate_rows[index].tolist()))
        index = int(parents[index])
    return selected[::-1]


def _install(network, extension):
    """Retain the old terminal as an intermediate stop, with explicit new chainages."""
    line = network["lines"][extension.route]
    before = rail.Track(line["geometry"])
    full = _full_track(before, extension.track, extension.end)
    rows = line["station_chainage_km"]
    offset = extension.track.km if extension.end == 0 else 0.
    for stop in rows:
        rows[stop] += offset
    for index, (km, point) in enumerate(extension.stops, 1):
        stop = f"{extension.route}-X{extension.end + 1}-{index:02d}"
        network["stations"][stop] = {
            "name": f"{line['name']} · suburban stop {extension.end + 1}.{index}",
            "coordinates": point, "lines": [extension.route],
            "basis": "Provisional suburban platform on the through service with mapped street access",
        }
        rows[stop] = offset - km if extension.end == 0 else before.km + km
    line.update(geometry=full.coordinates.tolist(), one_way_km=full.km,
                station_ids=sorted(rows, key=rows.__getitem__))
    rows[line["station_ids"][0]] = 0.
    rows[line["station_ids"][-1]] = full.km


def _proposal(core, route, end, target, outer, stations, graph, context, demand_tree, weights, walking, water, river):
    index = 0 if end == 0 else -1
    tail = rail.Track(np.asarray([core.points[index], target]) / rail.LOCAL_METRES)
    if not LineString(tail.points).disjoint(outer):
        return None, "re-enters the outer ring"
    full = _full_track(core, tail, end)
    if (not LineString(full.points).is_simple or third_ring_through._detour(full) > trunks.MAX_DETOUR
            or any(third_ring_through._turn(a, b) > trunks.MAX_TURN_DEG + 1e-8 for a, b in pairwise(full.delta))):
        return None, "excess bend, detour or self-intersection"
    crossings = trunks._dry_bank_arm(*tail.points, context, water, river)
    if crossings is None:
        return None, "second Tigris crossing or unsupported water crossing"
    new_stops = _stops(tail, stations, graph[3], context, demand_tree, weights)
    if not new_stops:
        return None, "no accessible spaced platform sequence"
    reach = {}
    sites = dict(new_stops)
    for name, (population, old) in walking.items():
        walk, _ = holistic_access.walk_to_station(sites, graph, population)
        reach[name] = np.flatnonzero((walk <= trunks.WALK_M) & ~old)
    crossings = list({(row["chainage_km"], row["mapped_wet_width_m"]): row for row in crossings}.values())
    return Extension(route, end, "", tail, new_stops, crossings, reach), None


def extend(core, graph, context, populations):
    """Compare a bounded set of outward tails and keep exact marginal walking gains."""
    tracks = {route: rail.Track(line["geometry"]) for route, line in sorted(core["lines"].items())
              if not line["loop"]}
    outer = Polygon(rail.Track(core["lines"][trunks.RINGS[-1]]["geometry"]).points)
    suburban_contour = outer.buffer(trunks.SUBURBAN_GATE_OFFSET_M)
    sites = {code: row["coordinates"] for code, row in core["stations"].items()}
    station_tree = cKDTree(central_access._points(sites.values()))
    water = holistic_through.WaterGeometry.from_context(context)
    river = straight_through_layout._tigris(context)
    primary = populations["worldpop-2026"]
    primary_sites, counts = trunks._demand_tiles(primary)
    demand_tree = cKDTree(primary_sites)
    terminal_candidates = primary_sites[(counts >= 100) & (station_tree.query(primary_sites)[0] > trunks.WALK_M)]
    street_index = graph[3].query(terminal_candidates)[1]
    targets = np.unique(graph[3].data[street_index], axis=0)
    targets = targets[rail.dry_points(targets / rail.LOCAL_METRES, context)]
    walking = {name: (population, holistic_access.walk_to_station(sites, graph, population)[0] <= trunks.WALK_M)
               for name, population in populations.items()}
    misses = station_tree.query(primary_sites)[0] > trunks.WALK_M
    weights = counts * misses
    options, rejected = [], Counter()

    for route, track in tracks.items():
        if core["lines"][route].get("service_role") == "regional-connector":
            continue
        for end, start, delta, terminal in zip(
                (0, 1), track.points[[0, -1]], (-track.delta[0], track.delta[-1]),
                (core["lines"][route]["station_ids"][0], core["lines"][route]["station_ids"][-1]), strict=True):
            if terminal == "Airport-00":
                continue
            heading = delta / np.linalg.norm(delta)
            for target in _terminals(start, heading, targets, primary_sites, weights):
                option, reason = _proposal(track, route, end, target, outer, station_tree, graph, context,
                                           demand_tree, weights, walking, water, river)
                if reason:
                    rejected[reason] += 1
                    continue
                option.former_terminal = terminal
                options.append(option)

    place_tree, places = rail._place_index(context)
    revised = deepcopy(core)
    reached = {name: mask.copy() for name, (_, mask) in walking.items()}
    totals = {name: population.counts.sum() for name, population in populations.items()}
    stops, accepted, ends = [], [], set()
    suburban = {route: trunks.suburban_arms(track, outer) for route, track in tracks.items()}

    def gain(option):
        return {name: float(populations[name].counts[pixels[~reached[name][pixels]]].sum())
                for name, pixels in option.reach.items()}

    def ranking(option, added):
        score = min(added[name] / totals[name] for name in totals)
        return (-score / np.sqrt(option.track.km), -score, option.route, option.end, option.track.km)

    while options:
        option, added = min(((row, gain(row)) for row in options), key=lambda item: ranking(*item))
        options.remove(option)
        if (option.route, option.end) in ends:
            continue
        if min(added.values()) / option.track.km < MIN_NEW_RESIDENTS_PER_KM:
            rejected["low incremental street-access gain"] += 1
            continue
        if LineString(option.track.points).intersects(suburban_contour):
            rejected["re-enters the suburban departure contour"] += 1
            continue
        other = [track for route, track in tracks.items() if route != option.route]
        if any(trunks._parallel_share(option.track, track) > trunks.MAX_PARALLEL_SHARE for track in other):
            rejected["duplicates an existing trunk corridor"] += 1
            continue
        xy = np.asarray([point for _, point in option.stops]) * rail.LOCAL_METRES
        if stops and (cKDTree(stops).query(xy)[0] < trunks.STATION_SPACING_M - 1e-6).any():
            rejected["duplicates a selected suburban station"] += 1
            continue
        line = rail.Track(revised["lines"][option.route]["geometry"])
        full = _full_track(line, option.track, option.end)
        if third_ring_through._detour(full) > trunks.MAX_DETOUR or not LineString(full.points).is_simple:
            rejected["combined ends exceed line directness or simplicity limits"] += 1
            continue
        arms = trunks.suburban_arms(full, outer)
        if any(trunks.suburban_parallel(arms, others) for route, others in suburban.items() if route != option.route):
            rejected["sustained parallel running outside the outer ring"] += 1
            continue
        _install(revised, option)
        tracks[option.route] = full
        suburban[option.route] = arms
        stops.extend(xy)
        ends.add((option.route, option.end))
        for name, pixels in option.reach.items():
            reached[name][pixels] = True
        place_distance, place_index = place_tree.query(option.track.points[-1])
        accepted.append({"route": option.route, "end": option.end, "former_terminal": option.former_terminal,
                         "nearby_place": places[place_index][1] if place_distance <= 1500 else None,
                         "new_terminal": revised["lines"][option.route]["station_ids"][0 if option.end == 0 else -1],
                         "route_km": option.track.km, "geometry": option.track.coordinates.tolist(),
                         "new_sites": len(option.stops), "additional_reach": {k: round(v) for k, v in added.items()},
                         "minor_water_crossings": option.water})
    revised["topology"] = rail.validate(revised)
    rail._identity(revised)
    return revised, {"base_candidate_id": core["candidate_id"], "base_evaluation_id": core["evaluation_id"],
                     "extensions": accepted, "rejections": dict(sorted(rejected.items())),
                     "maximum_km_per_end": MAX_EXTENSION_KM,
                     "minimum_residents_per_km_in_each_grid": MIN_NEW_RESIDENTS_PER_KM,
                     "route_km_added": round(sum(row["route_km"] for row in accepted), 2),
                     "new_station_sites": len(stops),
                     "newly_reached": {name: round(float(populations[name].counts[reached[name] & ~old].sum()))
                                       for name, (_, old) in walking.items()}}
