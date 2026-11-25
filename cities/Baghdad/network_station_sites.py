"""Consolidate candidate station calls on their source tracks and test street links."""

from copy import deepcopy
from functools import lru_cache
from hashlib import sha256

import numpy as np
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
from shapely import make_valid
from shapely.geometry import LineString, Point, shape
from shapely.strtree import STRtree

from . import central_access, holistic_network

NEARBY_M = 350
REDUNDANT_CALL_M = 450
WALK_LIMIT_M = 450
MAX_SNAP_M = 75
MAX_RELOCATION_M = 150
MIN_CALL_SPACING_M = holistic_network.INTERCHANGE_SPACING_M
EXACT_SITE_M = holistic_network.EXACT_CROSSING_M
PROVISIONAL_BASES = {
    "Population-ranked street-access infill on this alignment",
    "Dry alignment position near a retained pedestrian graph node",
}


def _metres(first, second):
    return float(np.linalg.norm((np.asarray(first) - second) * holistic_network.LOCAL_METRES))


def _nearby(stations, radius=NEARBY_M):
    ids = sorted(stations)
    points = np.asarray([stations[stop]["coordinates"] for stop in ids]) * holistic_network.LOCAL_METRES
    return sorted((float(np.linalg.norm(points[a] - points[b])), ids[a], ids[b])
                  for a, b in cKDTree(points).query_pairs(radius))


def _water_tree(context):
    return STRtree([make_valid(shape(feature["geometry"])) for feature in context["layers"]["water"]
                    if feature["geometry"]["type"] in {"Polygon", "MultiPolygon"}])


def _street_paths(graph, water):
    raw, matrix, active, tree, _ = graph

    @lru_cache(maxsize=None)
    def snap(point):
        if len(water.query(Point(point), predicate="intersects")):
            return None
        xy = central_access._points([point])[0]
        candidates = tree.query_ball_point(xy, MAX_SNAP_M)
        offsets = np.linalg.norm(tree.data[candidates] - xy, axis=1)
        for offset, index in sorted(zip(offsets, candidates, strict=True)):
            node = int(active[index])
            endpoint = (float(raw["lon"][node]), float(raw["lat"][node]))
            if point == endpoint or not len(water.query(LineString([point, endpoint]), predicate="intersects")):
                return node, float(offset)
        return None

    def path(first, second):
        source, target = snap(tuple(first)), snap(tuple(second))
        if source is None or target is None:
            return None
        start, start_offset = source
        end, end_offset = target
        limit = WALK_LIMIT_M - start_offset - end_offset
        distance, previous = dijkstra(matrix, directed=True, indices=start,
                                       limit=limit, return_predecessors=True)
        if not np.isfinite(distance[end]):
            return None
        nodes = [end]
        while nodes[-1] != start:
            nodes.append(int(previous[nodes[-1]]))
        coordinates = [[float(raw["lon"][node]), float(raw["lat"][node])] for node in reversed(nodes)]
        geometry = holistic_network._concatenate([first], coordinates, [second])
        return float(distance[end] + start_offset + end_offset), geometry

    return snap, path


def _separation(line, first, second):
    distance = abs(first - second)
    return 1000 * (min(distance, line["one_way_km"] - distance) if line["loop"] else distance)


def _endpoints(lines):
    return {station for line in lines.values() for station in (
        line["station_ids"][:1] if line["loop"] else (line["station_ids"][0], line["station_ids"][-1]))}


def _can_move(line, stop, chainage):
    current = line["station_chainage_km"][stop]
    if _separation(line, current, chainage) > MAX_RELOCATION_M:
        return False
    return all(_separation(line, chainage, other_km) >= MIN_CALL_SPACING_M - 1e-6
               for other, other_km in line["station_chainage_km"].items() if other != stop)


def _merge(stations, lines, tracks, keep, absorbed, location, chainages, kind):
    originals = [keep, absorbed]
    before = {stop: {"name": stations[stop]["name"], "coordinates": stations[stop]["coordinates"],
                     "lines": {line: lines[line]["station_chainage_km"][stop]
                               for line in stations[stop]["lines"]}} for stop in originals}
    stations[keep]["source_stations"] = sorted({*originals, *stations[keep].get("source_stations", []),
                                               *stations[absorbed].get("source_stations", [])})
    stations[keep]["coordinates"] = list(location)
    stations[keep]["lines"] = sorted(chainages)
    stations[keep]["site_kind"] = kind
    del stations[absorbed]
    for code, chainage in chainages.items():
        line = lines[code]
        line["station_chainage_km"].pop(absorbed, None)
        holistic_network._add(line, keep, chainage)
    return {"kind": "shared_site", "basis": kind, "kept_station_id": keep, "source_station_ids": originals,
            "source_stations": before, "coordinates": list(location),
            "platforms": {code: {"chainage_km": km, "coordinates": tracks[code].at(km)}
                          for code, km in sorted(chainages.items())}}


def consolidate(network, *, graph, context, protected_stations=()):
    """Return a new network and audit, retaining every line's source geometry."""
    revised = deepcopy(network)
    stations, lines = revised["stations"], revised["lines"]
    tracks = {code: holistic_network.Track(line["geometry"]) for code, line in lines.items()}
    terminals = _endpoints(lines)
    protected = set(protected_stations) | terminals
    prior_transfers = {row["id"]: row for row in revised["transfers"]}
    snap, street_path = _street_paths(graph, _water_tree(context))
    pairs = _nearby(stations, REDUNDANT_CALL_M)
    actions, held, changed = [], [], set()

    def movable(stop):
        row = stations[stop]
        return (stop not in protected and len(row["lines"]) == 1
                and row["basis"] in PROVISIONAL_BASES)

    def priority(stop):
        return stop not in prior_transfers, stop not in protected, movable(stop), stop

    @lru_cache(maxsize=None)
    def crossings(first, second):
        return holistic_network._crossings(tracks[first], tracks[second])

    for distance, first, second in pairs:
        if {first, second} & changed:
            continue
        keep, absorbed = sorted((first, second), key=priority)
        left, right = stations[keep], stations[absorbed]
        shared = set(left["lines"]) & set(right["lines"])
        if shared:
            if movable(absorbed):
                code, = right["lines"]
                line = lines[code]
                a, b = (line["station_chainage_km"][stop] for stop in (keep, absorbed))
                stops = line["station_ids"]
                neighbors = abs(stops.index(keep) - stops.index(absorbed))
                if (_separation(line, a, b) <= REDUNDANT_CALL_M + 1e-6
                        and (neighbors == 1 or (line["loop"] and neighbors == len(stops) - 1))):
                    outbound = street_path(left["coordinates"], right["coordinates"])
                    inbound = street_path(right["coordinates"], left["coordinates"])
                    if outbound is not None and inbound is not None:
                        stops.remove(absorbed)
                        del line["station_chainage_km"][absorbed]
                        del stations[absorbed]
                        actions.append({"kind": "retired_close_call", "kept_station_id": keep,
                                        "source_station_ids": [keep, absorbed], "line_id": code,
                                        "retired_chainage_km": b, "retired_station": right,
                                        "replacement_walks_m": [round(outbound[0], 2), round(inbound[0], 2)]})
                        changed.update((first, second))
                        continue
            held.append({"station_ids": [first, second], "reason": "shared line with distinct retained calls"})
            continue

        if distance > NEARBY_M:
            continue

        chainages = {code: lines[code]["station_chainage_km"][stop]
                     for stop, row in ((keep, left), (absorbed, right)) for code in row["lines"]}
        location = left["coordinates"]
        kind = "co-located mapped platforms"
        if (distance > EXACT_SITE_M or any(
                _metres(location, tracks[code].at(km)) > holistic_network.SOURCE_STOP_SNAP_M
                for code, km in chainages.items())):
            options = []
            if distance <= 2 * MAX_RELOCATION_M and (movable(keep) or movable(absorbed)):
                for a in left["lines"]:
                    for b in right["lines"]:
                        for point, (a_km, b_km) in crossings(a, b).items():
                            offsets = [_metres(point, row["coordinates"]) for row in (left, right)]
                            if max(offsets) > MAX_RELOCATION_M or snap(point) is None:
                                continue
                            trial = dict(chainages)
                            for stop, code, km, offset in (
                                    (keep, a, a_km, offsets[0]), (absorbed, b, b_km, offsets[1])):
                                if movable(stop) and _can_move(lines[code], stop, km):
                                    trial[code] = km
                                elif offset > EXACT_SITE_M:
                                    break
                            else:
                                if all(_metres(point, tracks[code].at(km)) <= holistic_network.SOURCE_STOP_SNAP_M
                                       for code, km in trial.items()):
                                    options.append((sum(offsets), point, a, b, trial))
            if not options:
                continue
            _, point, _, _, chainages = min(options, key=lambda item: item[:4])
            location = point
            kind = "eligible call moved to mapped track crossing"

        if snap(tuple(location)) is None or any(
                snap(tuple(tracks[code].at(km))) is None for code, km in chainages.items()):
            held.append({"station_ids": [first, second], "reason": "shared platform street snap or water screen"})
            continue
        rename = movable(keep)
        actions.append(_merge(stations, lines, tracks, keep, absorbed, location, chainages, kind))
        if rename:
            stations[keep]["name"] = "–".join(sorted(chainages)) + " interchange"
        changed.update((first, second))

    proposals = []
    for distance, first, second in _nearby(stations):
        a, b = stations[first], stations[second]
        if set(a["lines"]) & set(b["lines"]):
            continue
        outbound = street_path(a["coordinates"], b["coordinates"])
        inbound = street_path(b["coordinates"], a["coordinates"])
        if outbound is None or inbound is None or min(outbound[0], inbound[0]) <= EXACT_SITE_M:
            held.append({"station_ids": [first, second], "reason": "no credible two-way street path within the limit"})
            continue
        proposals.append((max(outbound[0], inbound[0]), first, second, distance, outbound, inbound))

    links, linked = [], set()
    for _, first, second, distance, outbound, inbound in sorted(proposals):
        if linked & {first, second}:
            held.append({"station_ids": [first, second], "reason": "another shorter link uses this station"})
            continue
        linked.update((first, second))
        key = sha256(central_access.encode([first, second])).hexdigest()[:12]
        links.append({"id": f"W-{key}", "station_ids": [first, second],
                      "walks_m": [round(outbound[0], 2), round(inbound[0], 2)],
                      "geometry": [outbound[1], inbound[1]], "straight_m": round(distance, 2),
                      "status": "separate complexes linked by public street",
                      "basis": "Retained pedestrian graph with provisional dry station-to-street connectors"})

    revised["transfers"] = [
        prior_transfers.get(stop, {"id": stop, "station_ids": [stop], "walking_m": None,
                                   "basis": row.get("site_kind", row["basis"])})
        | {"name": row["name"], "lines": sorted(row["lines"])}
        for stop, row in sorted(stations.items()) if len(row["lines"]) > 1
    ]
    revised["station_site_links"] = links
    revised["topology"] = holistic_network.validate(revised)
    report = {"source_candidate_id": network.get("candidate_id"),
              "station_sites_before": len(network["stations"]), "station_sites_after": len(stations),
              "links": links, "actions": actions, "held": held,
              "bounds": {"nearby_m": NEARBY_M, "redundant_call_m": REDUNDANT_CALL_M,
                         "walk_limit_m": WALK_LIMIT_M, "max_snap_m": MAX_SNAP_M,
                         "max_relocation_m": MAX_RELOCATION_M, "min_call_spacing_m": MIN_CALL_SPACING_M,
                         "co_location_m": EXACT_SITE_M},
              "access_status": "Planning screen from mapped water and street topology. Confirm step-free access, "
                               "grade, crossing rights, platform structures and connectors by survey."}
    return holistic_network._identity(revised), report
