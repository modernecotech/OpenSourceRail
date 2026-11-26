"""Evaluate Baghdad cross-city axes against three mapped orbital alignments."""

from collections import Counter
from copy import deepcopy
from itertools import combinations, pairwise, product
from math import atan2, degrees
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from shapely import Point, Polygon, intersects_xy

from engineering.outline.network_policy import MAXIMUM_DETOUR_RATIO, crossing_failures

from . import central_access, holistic_access, holistic_grid, holistic_network as rail
from . import holistic_through as through
from . import ring_corridors, straight_through_layout as precedent

OUTER_RING = "M16"
MIN_NEW_ROUTE_KM = 16
MAX_NEW_ROUTE_KM = 48
MIN_TERMINAL_REACH_M = 1_100
MAX_EXTENSION_M = 25_000
MAX_ENDPOINTS = 42
MAX_TRIALS_PER_BRIDGE = 96
MAX_ADMITTED_PER_BRIDGE = 3
MAX_NEW_AXES = 3
MIN_AXIS_ANGLE_DEG = 18
MIN_BRIDGE_SEPARATION_M = precedent.DISTINCT_BRIDGES_M
MAX_RING_STATION_SHIFT_M = 250


def _bearing(points):
    east, north = points[-1] - points[0]
    return degrees(atan2(east, north)) % 180


def _angle(first, second):
    angle = abs(first - second)
    return min(angle, 180 - angle)


def _detour(track):
    return track.km * 1000 / np.linalg.norm(track.points[-1] - track.points[0])


def _turn(first, second):
    return float(np.degrees(np.arccos(np.clip(
        np.dot(first, second) / np.linalg.norm(first) / np.linalg.norm(second), -1, 1,
    ))))


def _terminal_sites(network, graph, context, outer):
    ids = np.asarray(sorted(network["stations"]))
    coords = np.asarray([network["stations"][site]["coordinates"] for site in ids])
    points = coords * rail.LOCAL_METRES
    valid = (graph[3].query(points)[0] <= central_access.SNAP_M) & rail.dry_points(coords, context)
    ids, points = ids[valid], points[valid]
    outside = ~intersects_xy(outer, points[:, 0], points[:, 1])
    return ids, points, outside


def _movable_ring_station(network, ring_id, km):
    line = network["lines"][ring_id]
    ring_km = line["one_way_km"]
    distances = {site: min(abs(chainage - km), ring_km - abs(chainage - km)) * 1000
                 for site, chainage in line["station_chainage_km"].items()}
    close = [site for site, gap in distances.items() if gap < rail.INTERCHANGE_SPACING_M + .1]
    if len(close) != 1:
        return None
    site = close[0]
    if (distances[site] > MAX_RING_STATION_SHIFT_M or site == line["station_ids"][0]
            or network["stations"][site]["lines"] != [ring_id]
            or any(site in link["station_ids"] for link in network.get("station_site_links", []))):
        return None
    return site


def _ring_sites(track, ring_id, network, ring_track, graph, context, fixed, *, allow_move=False):
    spacing = through.STOP_SPACING_M / 1000
    line = network["lines"][ring_id]
    options = []
    for point, (km, ring_km) in rail._crossings(track, ring_track).items():
        if km < spacing or km > track.km - spacing or any(abs(hold - km) < spacing for hold in fixed):
            continue
        if rail._terminal_margin(line, ring_km) < rail.INTERCHANGE_SPACING_M + .1:
            if not any(np.linalg.norm((np.asarray(network["stations"][site]["coordinates"]) - point)
                                       * rail.LOCAL_METRES) <= rail.EXACT_CROSSING_M
                       for site in line["station_ids"]) and (
                           not allow_move or not _movable_ring_station(network, ring_id, ring_km)):
                continue
        offset = float(graph[3].query(np.asarray(point) * rail.LOCAL_METRES)[0])
        if offset <= central_access.SNAP_M:
            options.append((offset, km, ring_id, point))
    if options:
        options = [item for item, dry in zip(options, rail.dry_points([row[3] for row in options], context),
                                            strict=True) if dry]
    return sorted(options)


def _axis_record(network, code, ring_ids, outer, bridge, contacts, river_count):
    line = network["lines"][code]
    track = rail.Track(line["geometry"])
    interchanges = {ring_id: sorted(set(line["station_ids"]) & set(network["lines"][ring_id]["station_ids"]))
                    for ring_id in ring_ids}
    exact_interchanges = {}
    for ring_id, calls in interchanges.items():
        crossings = rail._crossings(track, rail.Track(network["lines"][ring_id]["geometry"]))
        exact_interchanges[ring_id] = [
            stop for stop in calls if any(
                np.linalg.norm((np.asarray(network["stations"][stop]["coordinates"]) - point) * rail.LOCAL_METRES) <= 50
                for point in crossings)
        ]
    failures = crossing_failures(detour_ratio=_detour(track), maximum_detour_ratio=MAXIMUM_DETOUR_RATIO,
                                 water_required=True, water_crossings=river_count,
                                 required_ring_ids=ring_ids, ring_interchanges=exact_interchanges)
    if failures:
        raise ValueError(f"{code}: {', '.join(failures)}")
    outside = [not bool(intersects_xy(outer, *point)) for point in track.points[[0, -1]]]
    return {"id": code, "route_km": track.km, "ring_interchanges": interchanges,
            "crossing_interchanges": exact_interchanges, "both_terminals_outside": all(outside),
            "detour_ratio": round(float(_detour(track)), 5), "bearing_deg": round(_bearing(track.points), 2),
            "terminal_ids": [line["station_ids"][0], line["station_ids"][-1]],
            "terminal_outside_third_ring": outside,
            "mapped_bridge_approaches": bridge, "water_crossings": contacts,
            "tigris_crossing_count": river_count}


def _wet_contacts(path, context, water, bridges, tigris):
    contacts = []
    chain_m = 0.
    river_count = 0
    for start, end in pairwise(path):
        length = np.linalg.norm(end - start)
        if any(len(hits) for hits in water.intersections(start, end)):
            rows = through._water_screen(start, end, context, water, bridges)
            if rows is None:
                return None
            contacts.extend(row | {"chainage_km": round(chain_m / 1000 + row["chainage_km"], 3)}
                            for row in rows)
            river_count += len(tigris.intersections(start, end)[1])
        chain_m += length
    return contacts, river_count


def _outward_options(landing, direction, points, outside):
    vectors = points - landing
    lengths = np.linalg.norm(vectors, axis=1)
    along = vectors @ direction
    eligible = np.flatnonzero(outside & (lengths >= MIN_TERMINAL_REACH_M) & (lengths <= MAX_EXTENSION_M)
                              & (along >= lengths * np.cos(np.deg2rad(precedent.MAX_TURN_DEG))))
    return sorted(eligible, key=lambda i: (lengths[i] + 2 * (lengths[i] - along[i]), int(i)))[:MAX_ENDPOINTS]


def _extension_sites(network, graph, context, outer, sites):
    """Screen additional outer terminal sites on existing non-orbital railway."""
    ids, points, outside = sites
    proposals = {}
    for code, line in network["lines"].items():
        if line["loop"] or line["one_way_km"] < MIN_NEW_ROUTE_KM:
            continue
        track = rail.Track(line["geometry"])
        chain = np.arange(.55, track.km - .55, .55)
        coords = np.asarray([track.at(km) for km in chain])
        projected = coords * rail.LOCAL_METRES
        eligible = ((graph[3].query(projected)[0] <= central_access.SNAP_M)
                    & ~intersects_xy(outer, projected[:, 0], projected[:, 1]))
        for i in np.flatnonzero(eligible):
            km = float(chain[i])
            if rail._terminal_margin(line, km) >= through.STOP_SPACING_M:
                proposals[f"X-RADIAL-{code}-{round(km * 1000):05d}"] = (code, km, coords[i])
    candidates = list(proposals)
    if candidates:
        dry = rail.dry_points([item[2] for item in proposals.values()], context)
        proposals = {key: proposals[key] for key, valid in zip(candidates, dry, strict=True) if valid}
    if not proposals:
        return sites, proposals
    points = np.vstack((points, np.asarray([item[2] for item in proposals.values()]) * rail.LOCAL_METRES))
    return (np.concatenate((ids, list(proposals))), points, np.r_[outside, np.ones(len(proposals), dtype=bool)]), proposals


def _extension_paths(landing, outward, endpoint, side, water, minor_bridges):
    paths = [np.asarray([landing, endpoint])]
    if any(len(hits) for hits in water.intersections(landing, endpoint)):
        axis = int(np.abs(endpoint - landing).argmax())
        forward = endpoint[axis] > landing[axis]
        first, last = (landing, endpoint) if forward else (endpoint, landing)
        for path in holistic_grid._bridge_paths(first, last, axis, minor_bridges):
            path = path if forward else path[::-1]
            if _turn(path[1] - path[0], outward) <= precedent.MAX_TURN_DEG:
                paths.append(path)
    yield from (path if side else path[::-1] for path in paths)


def _extension(network, axis, ring_id, graph, context, sites, outer, water, bridges, tigris, minor_bridges,
               *, allow_ring_station_move=False):
    # Retain the exact original alignment and every original platform chainage.
    code = axis["id"]
    line = network["lines"][code]
    track = rail.Track(line["geometry"])
    ring_track = rail.Track(network["lines"][ring_id]["geometry"])
    (ids, points, outside), possible_sites = _extension_sites(network, graph, context, outer, sites)
    choices = []
    rejections = Counter()
    old_calls = line["station_ids"]
    old_km = [line["station_chainage_km"][stop] for stop in old_calls]
    station_tree = cKDTree(np.asarray([row["coordinates"] for row in network["stations"].values()])
                          * rail.LOCAL_METRES)
    for side in (0, 1):
        landing, vector = ((track.points[0], -track.delta[0]), (track.points[-1], track.delta[-1]))[side]
        if not outer.covers(Point(landing)):
            choices.append([None])
            continue
        trials = []
        candidates = (
            (str(ids[i]), path)
            for i in _outward_options(landing, vector / np.linalg.norm(vector), points, outside)
            if str(ids[i]) not in old_calls
            and (str(ids[i]) not in possible_sites or possible_sites[str(ids[i])][0] != code)
            for path in _extension_paths(landing, vector, points[i], side, water, minor_bridges)
        )
        for terminal, path in candidates:
            wet = _wet_contacts(path, context, water, bridges, tigris)
            if wet is None or wet[1]:
                rejections["extension has an unsupported water crossing or adds another Tigris crossing"] += 1
                continue
            arm = rail.Track(path / rail.LOCAL_METRES)
            rings = _ring_sites(arm, ring_id, network, ring_track, graph, context, [],
                                allow_move=allow_ring_station_move)
            if not rings:
                rejections["no dry, spaced third-ring interchange"] += 1
                continue
            _, km, _, point = rings[0]
            # Sample an extension between its fixed original endpoint, ring and terminal.
            chain = np.arange(.125, arm.km, .125)
            coords = np.asarray([arm.at(value) for value in chain])
            street = graph[3].query(coords * rail.LOCAL_METRES)[0]
            valid = ((street <= central_access.SNAP_M) & rail.dry_points(coords, context)
                     & (station_tree.query(coords * rail.LOCAL_METRES)[0] >= 300))
            ordinary = []
            for low, high in pairwise((0., km, arm.km)):
                intervals = max(1, round((high - low) / 1.23))
                previous = low
                for target in np.linspace(low, high, intervals + 1)[1:-1]:
                    gap = through.STOP_SPACING_M / 1000
                    candidates = np.flatnonzero(valid & (chain >= previous + gap) & (chain <= high - gap)
                                                & (np.abs(chain - target) <= .6))
                    if len(candidates):
                        best = min(candidates, key=lambda n: abs(chain[n] - target) * 160 + street[n])
                        previous = float(chain[best])
                        ordinary.append(previous)
            if max(np.diff(sorted([0., km, arm.km, *ordinary]))) > through.MAX_STOP_GAP_M / 1000:
                rejections["extension platform gaps exceed the mapped stop-spacing screen"] += 1
                continue
            trials.append((terminal, arm, km, point, ordinary, wet[0]))
            if len(trials) == 4:
                break
        choices.append([*trials, None])
    for left, right in sorted(product(*choices), key=lambda pair: (-sum(item is not None for item in pair),
                                                                   sum(item[1].km for item in pair if item))):
        if left is None and right is None:
            continue
        path = (left[1].coordinates[:-1].tolist() if left else []) + line["geometry"] + (
            right[1].coordinates[1:].tolist() if right else [])
        combined = rail.Track(path)
        if _detour(combined) > MAXIMUM_DETOUR_RATIO:
            rejections["combined detour ratio exceeds the current planning screen"] += 1
            continue
        revised = deepcopy(network)
        target = revised["lines"][code]
        target["geometry"], target["one_way_km"] = path, combined.km
        shift = left[1].km if left else 0.
        target["station_chainage_km"] = dict(zip(old_calls, (km + shift for km in old_km), strict=True))
        transfer_ids = []
        try:
            for side, extension in enumerate((left, right)):
                if extension is None:
                    continue
                terminal, arm, km, point, ordinary, _ = extension
                start = 0. if side == 0 else shift + track.km
                rail._add(target, terminal, 0. if side == 0 else combined.km)
                if terminal in possible_sites and terminal not in revised["stations"]:
                    other, other_km, site = possible_sites[terminal]
                    existing = revised["lines"][other]
                    rail._through_station_spacing(other, terminal, other_km, revised["lines"])
                    revised["stations"][terminal] = {"name": f"{code} outer transfer to {other}",
                                                      "coordinates": site.tolist(), "lines": [other],
                                                      "basis": "Street-screened terminal on an existing approach"}
                    rail._add(existing, terminal, other_km)
                revised["stations"][terminal]["lines"].append(code)
                revised["stations"][terminal]["lines"].sort()
                for index, stop_km in enumerate(ordinary, 1):
                    station = f"{code}-E{side + 1}-{index:02d}"
                    revised["stations"][station] = {"name": f"{code} extension {side + 1} · km {stop_km:g}",
                                                    "coordinates": arm.at(stop_km), "lines": [code],
                                                    "basis": "Mapped street access on an outer through extension"}
                    rail._add(target, station, start + stop_km)
                ring_km = ring_track.locate(point)[0]
                request = {"line_id": ring_id}
                ring = revised["lines"][ring_id]
                if allow_ring_station_move and rail._terminal_margin(ring, ring_km) < rail.INTERCHANGE_SPACING_M:
                    moved = _movable_ring_station(revised, ring_id, ring_km)
                    if moved:
                        old = revised["stations"].pop(moved)
                        del ring["station_chainage_km"][moved]
                        ring["station_ids"].remove(moved)
                        request.update(id=moved, name=old["name"])
                transfer = rail._through_interchange(code, request, (point, (start + km, ring_km)),
                                                      revised["lines"], revised["stations"])
                transfer_ids.append(transfer)
            ring_corridors._refresh_transfers(revised)
            revised["topology"] = rail.validate(revised)
        except ValueError as error:
            rejections[str(error)] += 1
            continue
        if code in revised.get("through_lines", {}):
            summary = revised["through_lines"][code]
            summary["terminal_ids"] = [target["station_ids"][0], target["station_ids"][-1]]
            summary["required_intermediate_transfer_ids"].extend(transfer_ids)
            summary["transfer_ids"] = [stop for stop in target["station_ids"]
                                       if len(revised["stations"][stop]["lines"]) > 1]
            summary["transfer_count"] = len(summary["transfer_ids"])
        middle = [row | {"chainage_km": round(row["chainage_km"] + shift, 3)} for row in axis["water_crossings"]]
        downstream = [row | {"chainage_km": round(row["chainage_km"] + shift + track.km, 3)}
                      for row in right[5]] if right else []
        contacts = [*(left[5] if left else []), *middle, *downstream]
        try:
            proof = _axis_record(revised, code, (*sorted(precedent.RINGS), ring_id), outer,
                                 axis["mapped_bridge_approaches"], contacts, axis["tigris_crossing_count"])
        except ValueError as error:
            rejections[str(error)] += 1
            continue
        return revised, proof, dict(rejections)
    return None, None, dict(rejections)


def _approaches(reach, points, outside, demand, weights):
    vector = reach[1] - reach[0]
    heading = vector / np.linalg.norm(vector)
    result = []
    for landing, direction in zip(reach, (-heading, heading), strict=True):
        delta = points - landing
        length = np.linalg.norm(delta, axis=1)
        eligible = np.flatnonzero((length > 2500) & (length < 34_000)
                                  & (delta @ direction >= length * np.cos(np.deg2rad(precedent.MAX_TURN_DEG))))
        vectors = delta[eligible] / length[eligible, None]
        relative = demand - landing
        along = vectors @ relative.T
        offset = np.abs(vectors[:, 0, None] * relative[None, :, 1] - vectors[:, 1, None] * relative[None, :, 0])
        score = np.where((along > 0) & (along < length[eligible, None]),
                         np.maximum(0, 1 - offset / 1400) * weights, 0).sum(axis=1)
        ordered = sorted(zip(eligible, score, strict=True), key=lambda row: (
            -int(outside[row[0]]), -row[1], row[0]))
        # Reserve angular variety so an endpoint district with many stations cannot
        # consume the entire approach budget for a given bridge.
        bins = Counter()
        candidates = []
        for i, demand_score in ordered:
            angle = round((_bearing(np.asarray([landing, points[i]])) % 180) / 5)
            if bins[angle, bool(outside[i])] < 5:
                candidates.append((i, demand_score))
                bins[angle, bool(outside[i])] += 1
            if len(candidates) >= MAX_ENDPOINTS:
                break
        result.append(candidates)
    return result


def _new_axes(network, ring_id, graph, context, population, outer, water, roads, bridges, tigris, sites):
    ring_ids = (*sorted(precedent.RINGS), ring_id)
    inner = precedent._core_polygon(network)
    ids, points, outside = sites
    station_tree = cKDTree(np.asarray([s["coordinates"] for s in network["stations"].values()]) * rail.LOCAL_METRES)
    tracks = {code: rail.Track(row["geometry"]) for code, row in network["lines"].items()}
    rail_tree = cKDTree(np.concatenate([
        np.asarray([track.at(km) for km in np.linspace(0, track.km, int(np.ceil(track.km * 10)) + 1)])
        * rail.LOCAL_METRES for track in tracks.values()
    ]))
    cells = None
    if population is not None:
        existing = {code: row["coordinates"] for code, row in network["stations"].items()}
        cells = holistic_access.coverage_cells(population, holistic_access.walk_to_station(existing, graph, population)[0])
    demand, weights = through._demand_points(cells, graph)
    pool, audit = [], []
    for bridge_id, reach in enumerate(precedent._bridge_sites(context, water, bridges, inner), 1):
        candidates = []
        approaches = (reach / rail.LOCAL_METRES).tolist()
        accepted_approaches = []
        for side, proposals in enumerate(_approaches(reach, points, outside, demand, weights)):
            accepted = []
            for i, score in proposals:
                arm = [points[i], reach[0]] if side == 0 else [reach[1], points[i]]
                wet = _wet_contacts(arm, context, water, bridges, tigris)
                if wet is not None and not wet[1]:
                    accepted.append((i, score))
            accepted_approaches.append(accepted)
        for (a, a_score), (b, b_score) in product(*accepted_approaches):
            first, last = str(ids[a]), str(ids[b])
            if not (outside[a] or outside[b]) or set(network["stations"][first]["lines"]).intersection(
                    network["stations"][last]["lines"]):
                continue
            path = np.array([points[a], *reach, points[b]])
            length = np.linalg.norm(np.diff(path, axis=0), axis=1).sum() / 1000
            detour = length * 1000 / np.linalg.norm(path[-1] - path[0])
            if MIN_NEW_ROUTE_KM <= length <= MAX_NEW_ROUTE_KM and detour <= MAXIMUM_DETOUR_RATIO:
                candidates.append((-(int(outside[a]) + int(outside[b])), -float(a_score + b_score), detour, a, b, path))
        failures = Counter()
        count = screened = 0
        for ends, score, detour, a, b, path in sorted(candidates, key=lambda row: row[:5])[:MAX_TRIALS_PER_BRIDGE]:
            screened += 1
            screen = precedent._corridor(path, context, roads, bridges, water, rail_tree)
            if screen is None:
                failures["mapped water or parallel railway screen"] += 1
                continue
            road_share, rail_share, _ = screen
            if road_share < through.MIN_MAJOR_ROAD_SHARE:
                failures["insufficient parallel mapped major-road coverage"] += 1
                continue
            contacts, river_count = _wet_contacts(path, context, water, bridges, tigris)
            if river_count != 1:
                failures["requires exactly one mapped Tigris crossing"] += 1
                continue
            track = rail.Track(path / rail.LOCAL_METRES)
            crossings = []
            for code in reversed(ring_ids):
                matches = _ring_sites(track, code, network, tracks[code], graph, context,
                                      [km for km, _, _ in crossings])
                if not matches:
                    failures[f"no dry, spaced exact interchange with {code}"] += 1
                    break
                _, km, code, point = matches[0]
                crossings.append((km, code, point))
                if code == ring_id:
                    opposite = [row for row in matches[1:] if abs(row[1] - km) >= through.STOP_SPACING_M / 1000
                                and abs(row[1] - km) > .3 * track.km]
                    if opposite:
                        crossings.append(opposite[0][1:])
            else:
                for km, code, point in through._candidate_crossings(
                        track, {code: row for code, row in tracks.items() if code not in ring_ids},
                        network, graph, context):
                    if all(abs(km - existing) >= through.STOP_SPACING_M / 1000 for existing, _, _ in crossings):
                        crossings.append((km, code, point))
                crossings.sort()
                platforms = through._platforms(track, crossings, station_tree, graph, context)
                if not platforms:
                    failures["invalid station spacing or mapped pedestrian access"] += 1
                    continue
                count += 1
                code = f"M16-AX{bridge_id:02d}-{count:02d}"
                pool.append({"id": code, "name": f"Cross-Tigris through service {code}",
                             "geometry": track.coordinates.tolist(),
                             "basis": "Elevated planning centreline via mapped approaches. Dedicated rail spans, "
                                      "curves, land and clearance require design.",
                             "terminal_ids": [str(ids[a]), str(ids[b])],
                             "required_interchanges": [{"line_id": ring, "point": list(point)}
                                                       for _, ring, point in crossings],
                             "stops": [{"id": f"{code}-S{i:02d}", "name": f"{code} · km {km:g}", "chainage_km": km}
                                       for i, (km, _) in enumerate(platforms, 1)],
                             "mapped_bridge_approaches": approaches, "water_crossings": contacts,
                             "tigris_crossing_count": river_count, "bearing_deg": _bearing(path),
                             "major_road_share": round(road_share, 4), "near_existing_rail_share": round(rail_share, 4),
                             "one_way_km": track.km, "demand_proxy_score": -score,
                             "terminals_outside_third_ring": -ends, "detour_ratio": detour})
                if count >= MAX_ADMITTED_PER_BRIDGE:
                    break
        audit.append({"bridge_id": bridge_id, "mapped_bridge_approaches": approaches,
                      "mapped_water_approach_passes": [len(options) for options in accepted_approaches],
                      "rankable_terminal_pairs": len(candidates), "screened_pairs": screened,
                      "passed_initial_screen": count, "failures": dict(failures)})
    return pool, audit



def _existing_axes(network, context, water, bridges, tigris):
    """Include older direct axes when current mapping can corroborate their bridge."""
    published = network.get("straight_through_layout", {}).get("certified_through", [])
    records = {row["id"]: row for row in published}
    rings = [set(network["lines"][code]["station_ids"]) for code in sorted(precedent.RINGS)]
    for code, line in sorted(network["lines"].items()):
        if code in records or line["loop"] or not all(sites.intersection(line["station_ids"]) for sites in rings):
            continue
        track = rail.Track(line["geometry"])
        if _detour(track) > MAXIMUM_DETOUR_RATIO:
            continue
        hits = [(i, float(fraction)) for i, (a, b) in enumerate(pairwise(track.points))
                for fraction in tigris.intersections(a, b)[1]]
        if len(hits) != 1:
            continue
        wet = _wet_contacts(track.points, context, water, bridges, tigris)
        if wet is None or wet[1] != 1:
            continue
        i, fraction = hits[0]
        centre_m = track.chainage[i] + fraction * track.lengths[i]
        contacts = [row for row in wet[0] if abs(row["chainage_km"] * 1000 - centre_m) <= 300]
        if not contacts:
            continue
        reach = max(row["mapped_wet_width_m"] for row in contacts) / 2 + 60
        records[code] = {"id": code, "mapped_bridge_approaches": [
            track.at((centre_m - reach) / 1000), track.at((centre_m + reach) / 1000)],
            "water_crossings": wet[0], "tigris_crossing_count": wet[1]}
    return list(records.values())


def _link_outer(network, code, ring_id, graph, context):
    """Connect existing crossing alignments where a shared platform can fit."""
    line = network["lines"][code]
    ring = network["lines"][ring_id]
    if set(line["station_ids"]).intersection(ring["station_ids"]):
        return network, []
    track, orbital = (rail.Track(row["geometry"]) for row in (line, ring))
    choices = _ring_sites(track, ring_id, network, orbital, graph, context,
                          list(line["station_chainage_km"].values()))
    revised = deepcopy(network)
    added = []
    for _, km, _, point in choices:
        try:
            station = rail._through_interchange(code, {"line_id": ring_id},
                                                (point, (km, orbital.locate(point)[0])),
                                                revised["lines"], revised["stations"])
            added.append(station)
        except ValueError:
            continue
    if not added:
        return network, []
    if code in revised.get("through_lines", {}):
        summary = revised["through_lines"][code]
        summary["required_intermediate_transfer_ids"].extend(added)
        summary["transfer_ids"] = [stop for stop in revised["lines"][code]["station_ids"]
                                   if len(revised["stations"][stop]["lines"]) > 1]
        summary["transfer_count"] = len(summary["transfer_ids"])
    ring_corridors._refresh_transfers(revised)
    revised["topology"] = rail.validate(revised)
    return revised, added


def _bridge_separation(first, second):
    a = np.asarray(first["mapped_bridge_approaches"]).mean(axis=0)
    b = np.asarray(second["mapped_bridge_approaches"]).mean(axis=0)
    return float(np.linalg.norm((a - b) * rail.LOCAL_METRES))


def _summarise(network, axes, actions, audit, holds):
    comparisons = [{"lines": [a["id"], b["id"]], "bearing_separation_deg": round(_angle(a["bearing_deg"], b["bearing_deg"]), 2),
                    "bridge_separation_m": round(_bridge_separation(a, b)),
                    "both_full_axes": a["both_terminals_outside"] and b["both_terminals_outside"]}
                   for a, b in combinations(axes, 2)]
    network.setdefault("source_sha256", {})[Path(__file__).relative_to(central_access.ROOT).as_posix()] = central_access.digest(Path(__file__))
    network["third_ring_through"] = {"axes": axes, "actions": actions, "axis_comparisons": comparisons}
    return {"network": rail._identity(network), "axes": axes, "actions": actions,
            "audit": audit, "holds": dict(holds), "axis_comparisons": comparisons}


def alternatives(network, graph, context, *, population=None, ring_id=OUTER_RING):
    """Return retained-extension and added-axis trials on one fixed outer alignment."""
    rail.validate(network)
    ring_ids = (*sorted(precedent.RINGS), ring_id)
    if any(not network["lines"].get(code, {}).get("loop") for code in ring_ids):
        raise ValueError("The through-axis trial requires three closed orbital routes")
    outer = Polygon(np.asarray(network["lines"][ring_id]["geometry"]) * rail.LOCAL_METRES)
    if not outer.is_valid:
        raise ValueError("The third ring must define a simple planning boundary")
    roads, bridges = through._street_layers(context)
    water = through.WaterGeometry.from_context(context)
    tigris = precedent._tigris(context)
    retained = _existing_axes(network, context, water, bridges, tigris)
    minor_bridges = [reach for reach in holistic_grid._bridge_reaches(context, water, bridges)
                     if not any(len(hits) for hits in tigris.intersections(*reach))]
    revised, axes, actions, holds = deepcopy(network), [], [], {}
    extension_audit = {}
    for previous in retained:
        code = previous["id"]
        if code not in revised["lines"]:
            holds[code] = "Previous through service is absent."
            continue
        sites = _terminal_sites(revised, graph, context, outer)
        trial, proof, rejected = _extension(revised, previous, ring_id, graph, context, sites, outer,
                                             water, bridges, tigris, minor_bridges)
        extension_audit[code] = rejected
        if trial is not None:
            revised = trial
            axes.append(proof)
            actions.append({"action": "extend_through", "line_id": code, "added_route_km": round(
                proof["route_km"] - network["lines"][code]["one_way_km"], 3)})
            continue
        try:
            trial, added = _link_outer(revised, code, ring_id, graph, context)
            proof = _axis_record(trial, code, ring_ids, outer, previous["mapped_bridge_approaches"],
                                 previous["water_crossings"], previous["tigris_crossing_count"])
        except ValueError:
            holds[code] = "Existing service retained. No bounded extension passed the approach, water and station checks."
            continue
        revised = trial
        axes.append(proof)
        if added:
            actions.append({"action": "connect_through", "line_id": code, "added_route_km": 0.,
                            "shared_station_ids": added})
    variants = {"retained-through": _summarise(deepcopy(revised), axes.copy(), actions.copy(),
                                                {"extensions": extension_audit}, holds)}
    sites = _terminal_sites(revised, graph, context, outer)
    pool, bridge_audit = _new_axes(revised, ring_id, graph, context, population, outer, water, roads, bridges, tigris, sites)
    unresolved = {item["id"]: item for item in retained if item["id"] in holds and item["id"] in revised["lines"]}
    counted = [{"id": code, "mapped_bridge_approaches": row["mapped_bridge_approaches"],
                "bearing_deg": _bearing(rail.Track(revised["lines"][code]["geometry"]).points)}
               for code, row in unresolved.items()]
    integration_holds = {}
    for _ in range(MAX_NEW_AXES):
        references = [*axes, *counted]
        eligible = [item for item in pool if all(_bridge_separation(item, old) >= MIN_BRIDGE_SEPARATION_M
                                                  for old in references)]
        if not eligible:
            break
        eligible.sort(key=lambda row: (
            -row["terminals_outside_third_ring"],
            -min((_angle(row["bearing_deg"], item["bearing_deg"]) for item in references), default=90),
            row["near_existing_rail_share"], row["detour_ratio"], -row["demand_proxy_score"], row["id"]))
        found = False
        for option in eligible:
            pool.remove(option)
            if references and min(_angle(option["bearing_deg"], old["bearing_deg"]) for old in references) < MIN_AXIS_ANGLE_DEG:
                integration_holds[option["id"]] = "Heading is too close to a retained or selected through service."
                continue
            try:
                trial = rail.insert_through_lines(revised, [option], graph=graph, context=context,
                                                  connect_through_lines=True)
                proof = _axis_record(trial, option["id"], ring_ids, outer, option["mapped_bridge_approaches"],
                                     option["water_crossings"], option["tigris_crossing_count"])
            except ValueError as error:
                integration_holds[option["id"]] = str(error)
                continue
            revised = trial
            axes.append(proof | {"major_road_share": option["major_road_share"],
                                 "near_existing_rail_share": option["near_existing_rail_share"]})
            actions.append({"action": "add_through", "line_id": option["id"], "added_route_km": proof["route_km"]})
            found = True
            break
        if not found:
            break
    variants["added-through"] = _summarise(revised, axes, actions,
                                         {"extensions": extension_audit, "bridges": bridge_audit,
                                          "integration_holds": integration_holds,
                                          "remaining_axes": [item["id"] for item in pool]}, holds)
    shifted_from = variants["retained-through"]
    shifted = shifted_from["network"]
    shifted_axes, shifted_actions = shifted_from["axes"].copy(), shifted_from["actions"].copy()
    shift_audit = {}
    for index, axis in enumerate(shifted_axes.copy()):
        if axis["both_terminals_outside"]:
            continue
        sites = _terminal_sites(shifted, graph, context, outer)
        trial, proof, rejected = _extension(shifted, axis, ring_id, graph, context, sites, outer,
                                             water, bridges, tigris, minor_bridges, allow_ring_station_move=True)
        shift_audit[axis["id"]] = rejected
        if trial is None or not proof["both_terminals_outside"]:
            continue
        moved = []
        for stop in set(shifted["lines"][ring_id]["station_ids"]).intersection(trial["lines"][ring_id]["station_ids"]):
            before, after = (row["stations"][stop]["coordinates"] for row in (shifted, trial))
            distance = np.linalg.norm((np.asarray(before) - after) * rail.LOCAL_METRES)
            if distance > 1e-3:
                moved.append({"station_id": stop, "from": before, "to": after, "offset_m": round(float(distance), 1)})
        shifted = trial
        shifted_axes[index] = proof
        shifted_actions.append({"action": "extend_through_with_ring_station_shift", "line_id": proof["id"],
                                "added_route_km": round(proof["route_km"] - axis["route_km"], 3),
                                "ring_station_moves": sorted(moved, key=lambda row: row["station_id"])})
    if shifted is not shifted_from["network"]:
        variants["shifted-ring-through"] = _summarise(shifted, shifted_axes, shifted_actions,
                                                     {"extensions": shift_audit}, holds)
    else:
        variants["retained-through"]["audit"]["ring_station_shift_attempts"] = shift_audit
    return variants
