"""Fit named suburban connectors to shared stations on the Baghdad outer ring."""

from collections import Counter
from copy import deepcopy
from itertools import pairwise

import numpy as np
from scipy.spatial import cKDTree
from shapely import LineString, Point, Polygon, get_parts

from . import central_access as access, coverage_destinations, coverage_extensions as extensions
from . import coverage_trunks as trunks, holistic_access, holistic_network as rail, holistic_through as through
from . import ring_corridors, straight_network_study, straight_through_layout, third_ring_through

ROLE = "regional-connector"
RETAINED_APPROACHES = {"Basmaya": "M02", "Nahrawan": "M05", "Tajiyat": "M04"}
MAX_LENGTH_KM = 35.
MIN_LENGTH_KM = 1.5
MAX_DETOUR = 1.30
MAX_TURN_DEG = 45.
MAX_RING_ANCHORS = 12
MAX_EXACT_TRIALS = 12
MAX_REUSED_JOIN_M = 3_000.
ROAD_SEARCH_M = 400.
ENGINEERING_HOLDS = [
    "Verify accessible transfer and street entrances, land, vertical profile and swept path.",
    "Design and price all water crossings, curves, stations and turnbacks.",
    "Verify station dwell, fleet and recovery alongside the full network service.",
]


def departure(track, outer, contour):
    """Return one exterior departure, using the terminus for a short spoke."""
    path = LineString(track.points)
    if (not path.is_simple or outer.boundary.distance(Point(track.points[0])) > rail.EXACT_CROSSING_M
            or outer.covers(Point(track.points[-1])) or path.intersection(outer.buffer(-1.)).length > 1.):
        return None
    hits = [item for item in get_parts(path.intersection(contour.boundary)) if not item.is_empty]
    if len(hits) == 1 and hits[0].geom_type == "Point" and not contour.covers(Point(track.points[-1])):
        return np.array([hits[0].coords[0]]), "2.5 km suburban contour"
    if not hits and contour.covers(Point(track.points[-1])):
        return track.points[[-1]], "Suburban terminus before the contour"
    return None


def _water_evidence(track, context, water, river, bridges):
    entries = []
    for start, end, metres in zip(track.points[:-1], track.points[1:], track.chainage[:-1], strict=True):
        if len(river.intersections(start, end)[1]):
            return None
        segment = trunks._dry_bank_arm(start, end, context, water, river)
        if segment is None:
            segment = through._water_screen(start, end, context, water, bridges)
            if segment is None:
                return None
            segment = [row | {"basis": "Tagged surface bridge corridor. Rail crossing requires design."}
                       for row in segment]
        entries.extend(row | {"chainage_km": round(float(metres / 1000 + row["chainage_km"]), 3)}
                       for row in segment)
    return entries


def _road_support(track, roads):
    hits = total = 0
    for start, end, length in zip(track.points[:-1], track.points[1:], track.lengths, strict=True):
        points = np.linspace(start, end, int(np.ceil(length / 250)) + 2)[1:-1]
        hits += int(np.isfinite(roads.nearby(points, (end - start) / length, ROAD_SEARCH_M, 35)).sum())
        total += len(points)
    return round(hits / total, 4)


def _snap_walk(distances, coordinates, graph):
    offset, node = graph[3].query(np.asarray(coordinates) * rail.LOCAL_METRES)
    walk = float(distances[graph[2][node]] + offset)
    return round(walk, 1) if offset <= access.SNAP_M and np.isfinite(walk) else None


def _existing(network, outer, contour, exclude=()):
    arms, departures = {}, {}
    for code, line in sorted(network["lines"].items()):
        if code in exclude or line["loop"]:
            continue
        track = rail.Track(line["geometry"])
        arms[code] = trunks.suburban_arms(track, outer)
        if line.get("service_role") == ROLE:
            row = departure(track, outer, contour)
            if row is not None:
                departures[code] = row[0]
        elif (gates := trunks.suburban_departures(track, contour)) is not None:
            departures[code] = gates
    return arms, departures


def _geometry(track, outer, contour, other, context, water, river, roads, bridges):
    if (not MIN_LENGTH_KM <= track.km <= MAX_LENGTH_KM or third_ring_through._detour(track) > MAX_DETOUR
            or any(third_ring_through._turn(a, b) > MAX_TURN_DEG for a, b in pairwise(track.delta))):
        return None, "length or curvature"
    if not rail.dry_points(track.coordinates, context).all():
        return None, "bend or terminal on mapped water"
    row = departure(track, outer, contour)
    if row is None:
        return None, "outer ring or departure geometry"
    gates, basis = row
    arms, gate_points = other
    spacing = min((trunks.suburban_departure_distance(gates, points) for points in gate_points.values()),
                  default=None)
    if spacing is not None and spacing < trunks.SUBURBAN_PARALLEL_SEPARATION_M:
        return None, "suburban departure spacing"
    suburban = trunks.suburban_arms(track, outer)
    if any(trunks.suburban_parallel(suburban, other_arms) for other_arms in arms.values()):
        return None, "sustained suburban parallel running"
    water_rows = _water_evidence(track, context, water, river, bridges)
    if water_rows is None:
        return None, "unsupported water crossing"
    return {
        "departure": (gates[0] / rail.LOCAL_METRES).tolist(),
        "departure_basis": basis,
        "minimum_departure_spacing_m": round(spacing, 1) if spacing is not None else None,
        "mapped_water_contacts": water_rows,
        "major_road_support_share": _road_support(track, roads),
    }, None


def _route_options(anchor, terminal, former_track):
    yield [anchor, terminal], "Fresh direct connection between the outer ring and the destination"
    near, far = former_track.locate(anchor), former_track.locate(terminal)
    if max(near[1], far[1]) <= MAX_REUSED_JOIN_M and abs(near[0] - far[0]) > 1e-3:
        coordinates = former_track.between(*sorted((near[0], far[0])))
        if near[0] > far[0]:
            coordinates.reverse()
        route = rail._concatenate([anchor], coordinates, [terminal])
        path = LineString(np.asarray(route) * rail.LOCAL_METRES).simplify(150.)
        yield (np.asarray(path.coords) / rail.LOCAL_METRES).tolist(), "Reconnected segment of the retained alignment"
    # Prefer reused alignments and direct named spokes. One waypoint can provide
    # a street-accessible station where a straight segment crosses empty fields.
    target = np.asarray([anchor, terminal]) * rail.LOCAL_METRES
    along = target[1] - target[0]
    norm = np.linalg.norm(along)
    perpendicular = np.array([-along[1], along[0]]) / norm
    for fraction in (.35, .6):
        for offset in (-600., 600.):
            point = target[0] + fraction * along + perpendicular * offset
            yield [anchor, (point / rail.LOCAL_METRES).tolist(), terminal], "Single-bend named-district option"


def _install(network, name, anchor, track, calls, basis):
    code = f"RGN-{name}"
    stations = network["stations"]
    stations[anchor]["lines"] = sorted([*stations[anchor]["lines"], code])
    ids = [anchor]
    chainages = {anchor: 0.}
    for index, (km, coordinates) in enumerate(calls, 1):
        last = index == len(calls)
        station = f"{code}-S{index:02d}"
        ids.append(station)
        chainages[station] = km
        stations[station] = {"coordinates": coordinates, "lines": [code],
                             "name": name if last else f"{name} corridor · stop {index}",
                             "basis": "Provisional mapped street-access location"}
    network["lines"][code] = {
        "geometry": track.coordinates.tolist(), "station_ids": ids, "station_chainage_km": chainages,
        "one_way_km": track.km, "loop": False, "service_role": ROLE, "destination": name,
        "name": f"Outer ring – {name}", "source_sections": [], "basis": basis,
    }
    ring_corridors._refresh_transfers(network)
    network["topology"] = rail.validate(network)
    network["physical_accepted"] = network["operating_timetable_validated"] = False
    rail._identity(network)
    return code


def add_missing(network, graph, context, populations):
    """Add one independently screened connector for every still-unreached named suburb."""
    revised = deepcopy(network)
    outer_line = network["lines"][trunks.RINGS[-1]]
    outer = Polygon(rail.Track(outer_line["geometry"]).points)
    contour = outer.buffer(trunks.SUBURBAN_GATE_OFFSET_M)
    old = access.read(straight_network_study.RECORD)["network"]
    locations = coverage_destinations.locations()
    targets = coverage_destinations.terminal_candidates(graph, context)
    roads, bridges = through._street_layers(context)
    water = through.WaterGeometry.from_context(context)
    river = straight_through_layout._tigris(context)
    primary = populations["worldpop-2026"]
    demand, weights = trunks._demand_tiles(primary)
    demand_tree = cKDTree(demand)
    baseline = coverage_destinations.walking(network, graph)
    selected, rejected = {}, {}
    for name in locations:
        access_m = coverage_destinations.walking(revised, graph)[name]
        if access_m is not None and access_m <= trunks.WALK_M:
            continue
        stations = revised["stations"]
        sites = {stop: row["coordinates"] for stop, row in stations.items()}
        street_tree = graph[3]
        station_tree = cKDTree(access._points(sites.values()))
        prior_population, _ = holistic_access.walk_to_station(sites, graph, primary)
        other = _existing(revised, outer, contour)
        former = rail.Track(old["lines"][RETAINED_APPROACHES[name]]["geometry"])
        location_metric = np.asarray(locations[name]) * rail.LOCAL_METRES
        anchor_ids = sorted(outer_line["station_ids"], key=lambda stop: (
            float(np.linalg.norm(np.asarray(sites[stop]) * rail.LOCAL_METRES - location_metric)), stop))
        shortlist = []
        trials = []
        missing = station_tree.query(demand)[0] > trunks.WALK_M
        failures = Counter()
        for anchor in anchor_ids[:MAX_RING_ANCHORS]:
            if (street_tree.query(np.asarray(sites[anchor]) * rail.LOCAL_METRES)[0] > access.SNAP_M
                    or not rail.dry_points([sites[anchor]], context)[0]):
                failures["outer ring station lacks a dry, mapped street entrance"] += 1
                continue
            for metric in targets[name]:
                for coordinates, basis in _route_options(sites[anchor], (metric / rail.LOCAL_METRES).tolist(), former):
                    track = rail.Track(coordinates)
                    evidence, reason = _geometry(track, outer, contour, other, context, water, river, roads, bridges)
                    if reason:
                        failures[reason] += 1
                        continue
                    calls = extensions._stops(track, station_tree, street_tree, context, demand_tree, weights)
                    if not calls:
                        failures["no accessible spaced platform sequence"] += 1
                        continue
                    near = cKDTree(access._points(dict(calls).values())).query(demand)[0] <= trunks.WALK_M
                    proxy = float(weights[near & missing].sum()) / (track.km + len(calls))
                    shortlist.append(((-proxy, track.km, len(calls), anchor),
                                      (name, anchor, track, calls, basis), evidence))
        for _, design, evidence in sorted(shortlist, key=lambda row: row[0])[:MAX_EXACT_TRIALS]:
            _, anchor, track, calls, _ = design
            distances, _ = access.distances_from_stops(dict(calls), graph)
            walk_m = _snap_walk(distances, locations[name], graph)
            if walk_m is None or walk_m > trunks.WALK_M:
                failures["target lacks a 1.3 km street walk"] += 1
                continue
            access_m = distances[primary.nodes] + primary.offsets_m
            added = int(round(primary.counts[(prior_population > trunks.WALK_M)
                          & (primary.offsets_m <= access.SNAP_M) & (access_m <= trunks.WALK_M)].sum()))
            # Length and platforms are provisional cost drivers. Native
            # costing compares the resulting complete network separately.
            metric = (-added / (track.km + len(calls)), track.km, len(calls), walk_m, anchor)
            trials.append((metric, design, evidence, added, walk_m))
        rejected[name] = dict(sorted(failures.items()))
        if not trials:
            continue
        _, design, evidence, population, walk_m = min(trials, key=lambda row: row[0])
        code = _install(revised, *design)
        selected[name] = evidence | {
            "route": code, "ring_station": design[1], "destination_walk_m": walk_m,
            "route_km": design[2].km, "new_station_sites": len(design[3]),
            "added_worldpop_residents": population, "basis": design[4],
            "engineering_holds": ENGINEERING_HOLDS,
        }
    after = coverage_destinations.walking(revised, graph)
    return revised, {
        "base_candidate_id": network["candidate_id"], "selected": selected, "rejections": rejected,
        "before_walk_m": baseline, "after_walk_m": after,
        "holds": [f"No screened outer-ring connection supplied the named {name} walking catchment."
                  for name, metres in after.items() if metres is None or metres > trunks.WALK_M],
    }


def validate(network, context, graph):
    """Re-evaluate each named connector, including the geometry of edited GIS inputs."""
    regional = {code: line for code, line in network["lines"].items() if line.get("service_role") == ROLE}
    if not regional:
        return {}
    outer_id = trunks.RINGS[-1]
    if outer_id not in network["lines"]:
        return {code: {"failures": ["Missing outer ring"]} for code in regional}
    outer_line = network["lines"][outer_id]
    outer = Polygon(rail.Track(outer_line["geometry"]).points)
    contour = outer.buffer(trunks.SUBURBAN_GATE_OFFSET_M)
    destinations = coverage_destinations.locations()
    roads, bridges = through._street_layers(context)
    water = through.WaterGeometry.from_context(context)
    river = straight_through_layout._tigris(context)
    rows = {}
    for code, line in regional.items():
        name = line.get("destination")
        ids = line["station_ids"]
        sites = {stop: network["stations"][stop]["coordinates"] for stop in ids}
        track = rail.Track(line["geometry"])
        other = _existing(network, outer, contour, (code,))
        geometry, reason = _geometry(track, outer, contour, other, context, water, river, roads, bridges)
        failures = [reason] if reason else []
        if (line["loop"] or ids[0] not in outer_line["station_ids"]
                or outer_id not in network["stations"][ids[0]]["lines"]
                or np.linalg.norm((track.coordinates[0] - sites[ids[0]]) * rail.LOCAL_METRES) > rail.EXACT_CROSSING_M):
            failures.append("missing exact shared outer-ring terminal")
        chainages = np.array([line["station_chainage_km"][stop] for stop in ids])
        gaps = np.diff(chainages) * 1_000
        if np.any(gaps < trunks.STATION_SPACING_M - 1e-6) or np.any(gaps > trunks.MAX_STOP_GAP_M + 1e-6):
            failures.append("station calls fail spacing")
        if not rail.dry_points(list(sites.values()), context).all() or np.any(
                graph[3].query(access._points(sites.values()))[0] > access.SNAP_M):
            failures.append("station lacks a dry, mapped street entrance")
        distances, _ = access.distances_from_stops(sites, graph)
        walk_m = _snap_walk(distances, destinations[name], graph) if name in destinations else None
        if walk_m is None or walk_m > trunks.WALK_M:
            failures.append("named destination walking access is unproven")
        rows[code] = (geometry or {}) | {"destination": name, "destination_walk_m": walk_m, "failures": failures}
    return rows
