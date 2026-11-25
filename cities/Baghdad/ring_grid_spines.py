"""Construct comparable Baghdad ring and straight-through planning layouts."""

from collections import defaultdict
from copy import deepcopy
from itertools import combinations
from math import fsum
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from .central_access import SNAP_M
from .holistic_grid import _bridge_reaches, _screen_geometry
from .holistic_network import (
    LOCAL_METRES, ROOT, Track, _identity, digest, dry_points, insert_through_lines, validate,
)
from .holistic_through import WaterGeometry, _candidate_crossings, _demand_points, _platforms, _street_layers
from .residential_layouts import LineEdit, apply_edits

RINGS = frozenset({"M09", "M15"})
# Published direct routes that support the retained grid and airport operations.
DIRECT = frozenset({"G02", "G04", "G09", "G13", "M01", "M05", "M10", "M11", "M12", "M14"})
ANCHORS = frozenset({"C1", "C2", "T01", "T20"})
# Test the exchange of local or overlapping services for the two closed rings
# and new straight axes. Reserved branches and retained stop impacts stay visible.
FEEDER_EXCHANGE = frozenset({
    "G05", "G07", "G11", "G20", "M13", "T02", "T05", "T13",
    "T19", "T23", "T40", "D-1033-929-34", "D-1034-929-80", "D-1035-927-09",
    "D-1031-924-02", "D-1033-930-50",
})
RETAINED_GAP_FEEDERS = frozenset({"D-1033-930-50", "D-1034-929-80"})
FAMILIES = ("east–west", "southwest–northeast", "north–south", "northwest–southeast")
MIN_KM = 13
MAX_KM = 30
TARGET_KM = 18
MAX_TURN_DEGREES = 35
MAX_DIRECTNESS = 1.10
MAX_TRIALS_PER_FAMILY = 550
MAX_ADMITTED_PER_FAMILY = 5
CENTRE = np.array([44.390, 33.335]) * LOCAL_METRES


def _route_km(network):
    return fsum(row["one_way_km"] for row in network["lines"].values())


def _withdraw(network, withdrawals, protected_stations):
    source = deepcopy(network)
    removed_links = []
    for link in source.get("station_site_links", []):
        closed = [stop for stop in link["station_ids"]
                  if set(source["stations"][stop]["lines"]) <= withdrawals]
        if closed:
            removed_links.append({"id": link["id"], "station_ids": link["station_ids"],
                                  "closed_stations": closed,
                                  "reason": "Platform removed by route withdrawal"})
    obsolete = {row["id"] for row in removed_links}
    if obsolete:
        source["station_site_links"] = [row for row in source["station_site_links"] if row["id"] not in obsolete]
    revised, edits = apply_edits(source, (
        LineEdit(code, "Test exchange of retained guideway for the two rings and direct through services.")
        for code in sorted(withdrawals)
    ), protected_stations=protected_stations)
    revised["layout_revision"]["removed_walking_links"] = removed_links
    return _identity(revised), edits, removed_links


def _terminal_trials(network, graph, context, demand, weights):
    eligible_lines = RINGS | DIRECT | ANCHORS | {"M02", "M03", "M04", "M06", "M07", "M08"}
    station_ids = sorted(stop for stop, row in network["stations"].items() if eligible_lines.intersection(row["lines"]))
    coords = np.asarray([network["stations"][stop]["coordinates"] for stop in station_ids])
    points = coords * LOCAL_METRES
    usable = (graph[3].query(points)[0] <= SNAP_M) & dry_points(coords, context)
    ids = [stop for stop, keep in zip(station_ids, usable, strict=True) if keep]
    points = points[usable]
    pair_ids = cKDTree(points).query_pairs(MAX_KM * 1000, output_type="ndarray")
    groups = {code: defaultdict(list) for code in range(4)}
    route_sets = [set(network["stations"][stop]["lines"]) for stop in ids]
    for block in np.array_split(pair_ids, max(1, len(pair_ids) // 1000)):
        start, end = points[block[:, 0]], points[block[:, 1]]
        delta = end - start
        km = np.linalg.norm(delta, axis=1) / 1000
        heading = delta / (km[:, None] * 1000)
        mid = (start + end) / 2
        near_centre = np.linalg.norm(mid - CENTRE, axis=1)
        valid = (km >= MIN_KM) & (near_centre <= 11_000)
        valid &= np.array([route_sets[a].isdisjoint(route_sets[b]) for a, b in block], dtype=bool)
        start, heading, km, near_centre, block, mid = (
            column[valid] for column in (start, heading, km, near_centre, block, mid)
        )
        if not len(block):
            continue
        displacement = demand[None, :, :] - start[:, None, :]
        along = np.sum(displacement * heading[:, None, :], axis=2)
        lateral = np.linalg.norm(displacement - along[:, :, None] * heading[:, None, :], axis=2)
        score = np.where((along >= 650) & (along <= km[:, None] * 1000 - 650),
                         np.maximum(0, 1 - lateral / 1400) * weights, 0).sum(axis=1)
        score = score * np.minimum(km / TARGET_KM, 1) / (1 + near_centre / 10_000)
        family = np.floor((np.degrees(np.arctan2(heading[:, 1], heading[:, 0])) + 22.5) / 45).astype(int) % 4
        tiles = np.floor((mid - CENTRE) / 2900).astype(int)
        for (a, b), group, value, tile in zip(block, family, score, tiles, strict=True):
            if value > 0:
                groups[group][tuple(tile)].append((float(value), ids[a], ids[b]))
    ordered = {}
    for family, strips in groups.items():
        rows = [sorted(trials, key=lambda row: (-row[0], row[1:])) for trials in strips.values()]
        rows.sort(key=lambda trials: (-trials[0][0], trials[0][1:]))
        ordered[family] = [trials[i] for i in range(max(map(len, rows), default=0))
                           for trials in rows if i < len(trials)]
    return ordered


def _bridge_paths(start, end, bridge_reaches):
    heading = end - start
    chord = np.linalg.norm(heading)
    heading /= chord
    choices = []
    for reach in bridge_reaches:
        displacement = reach.mean(axis=0) - start
        along = displacement @ heading
        if not 1400 <= along <= chord - 1400:
            continue
        lateral = np.linalg.norm(displacement - along * heading)
        if lateral > 3000:
            continue
        ordered = reach if (reach[1] - reach[0]) @ heading > 0 else reach[::-1]
        route = np.asarray([start, *ordered, end])
        delta = np.diff(route, axis=0)
        lengths = np.linalg.norm(delta, axis=1)
        if np.any(lengths < 250) or lengths.sum() > min(MAX_KM * 1000, chord * MAX_DIRECTNESS):
            continue
        directions = delta / lengths[:, None]
        if (directions @ heading > 0).all() and (np.sum(directions[:-1] * directions[1:], axis=1)
                                                  >= np.cos(np.deg2rad(MAX_TURN_DEGREES))).all():
            choices.append((float(lengths.sum()), lateral, route))
    return [route for _, _, route in sorted(choices, key=lambda row: row[:2])[:3]]


def _screen(network, graph, context, coverage_cells, *, withdrawn=()):
    demand, weights = _demand_points(coverage_cells, graph)
    if not len(demand):
        return []
    trials = _terminal_trials(network, graph, context, demand, weights)
    roads, bridges = _street_layers(context)
    water = WaterGeometry.from_context(context)
    reaches = _bridge_reaches(context, water, bridges)
    tracks = [Track(row["geometry"]) for code, row in network["lines"].items() if code not in withdrawn]
    rail = cKDTree(np.concatenate([
        np.array([track.at(km) for km in np.linspace(0, track.km, int(np.ceil(track.km * 12)) + 1)])
        * LOCAL_METRES for track in tracks
    ]))
    accepted = []
    for family, rows in trials.items():
        endpoints = []
        screened = 0
        for score, first, last in rows:
            codes = [first, last]
            coordinates = [network["stations"][stop]["coordinates"] for stop in codes]
            start, end = np.asarray(coordinates) * LOCAL_METRES
            if any(min(max(np.linalg.norm(start - a), np.linalg.norm(end - b)),
                       max(np.linalg.norm(start - b), np.linalg.norm(end - a))) < 680 for a, b in endpoints):
                continue
            if screened == MAX_TRIALS_PER_FAMILY:
                break
            endpoints.append((start, end))
            screened += 1
            for path in [np.asarray([start, end]), *_bridge_paths(start, end, reaches)]:
                result = _screen_geometry(path, context, roads, bridges, water, rail)
                if result is None:
                    continue
                route = (path / LOCAL_METRES).tolist()
                route[0], route[-1] = coordinates
                chord = np.linalg.norm(end - start) / 1000
                road_share, duplicate_share, water_contacts = result
                accepted.append({
                    "id": f"RG{family + 1}-{screened:02d}", "family": FAMILIES[family], "geometry": route,
                    "terminal_ids": codes, "one_way_km": Track(route).km,
                    "screening": {"directness": round(Track(route).km / chord, 4),
                                  "distance_proxy_score": round(score, 2),
                                  "major_surface_road_share": round(road_share, 3),
                                  "near_existing_rail_share": round(duplicate_share, 3),
                                  "mapped_water_contacts": water_contacts,
                                  "geometry_type": "straight" if len(route) == 2 else "mapped bridge approaches"},
                })
                break
    return accepted


def _describe(network, option, graph, context):
    terminals = option["terminal_ids"]
    if set(terminals) - network["stations"].keys():
        return None
    track = Track(option["geometry"])
    tracks = {code: Track(row["geometry"]) for code, row in network["lines"].items()}
    crossings = _candidate_crossings(track, tracks, network, graph, context)
    if len(crossings) < 2 or crossings[-1][0] - crossings[0][0] < .20 * track.km:
        return None
    connections = {line for _, line, _ in crossings}
    connections.update(line for stop in terminals for line in network["stations"][stop]["lines"])
    if not RINGS.intersection(connections):
        return None
    station_tree = cKDTree(np.asarray([row["coordinates"] for row in network["stations"].values()]) * LOCAL_METRES)
    platforms = _platforms(track, crossings, station_tree, graph, context)
    if not platforms:
        return None
    code = option["id"]
    return option | {
        "name": f"{option['family'].capitalize()} through line {code}",
        "basis": "Continuous elevated planning axis. Vertical clearance, curve geometry, land and station access open.",
        "required_interchanges": [{"line_id": line, "point": list(point)} for _, line, point in crossings],
        "stops": [{"id": f"{code}-S{i:02d}", "name": f"{code} · km {km:g}", "chainage_km": km}
                  for i, (km, _) in enumerate(platforms, 1)],
    }


def _bearing_delta(first, second):
    headings = []
    for row in (first, second):
        vector = (np.asarray(row["geometry"][-1]) - row["geometry"][0]) * LOCAL_METRES
        headings.append(float(np.degrees(np.arctan2(vector[1], vector[0])) % 180))
    delta = abs(headings[0] - headings[1])
    return min(delta, 180 - delta)


def _cross(network, first, second):
    return bool(set(network["lines"][first]["station_ids"][1:-1])
                & set(network["lines"][second]["station_ids"][1:-1]))


def _select(skeleton, pool, graph, context, budget, *, family_pair=None):
    admitted = []
    families = set(family_pair or FAMILIES)
    for family in FAMILIES:
        if family not in families:
            continue
        count = 0
        for option in pool:
            if option["family"] != family or _route_km(skeleton) + option["one_way_km"] > budget + 1e-7:
                continue
            row = _describe(skeleton, option, graph, context)
            if row is not None:
                admitted.append(row)
                count += 1
                if count == MAX_ADMITTED_PER_FAMILY:
                    break
    rejected = []
    pairs = [pair for pair in combinations(admitted, 2)
             if pair[0]["family"] != pair[1]["family"] and _bearing_delta(*pair) >= 45
             and _route_km(skeleton) + sum(row["one_way_km"] for row in pair) <= budget + 1e-7]
    pairs.sort(key=lambda pair: (-sum(row["screening"]["distance_proxy_score"] for row in pair),
                                 tuple(row["id"] for row in pair)))
    for pair in pairs:
        try:
            revised = insert_through_lines(skeleton, pair, graph=graph, context=context, connect_through_lines=True)
        except ValueError as error:
            rejected.append({"routes": [row["id"] for row in pair], "reason": str(error)})
            continue
        codes = [row["id"] for row in pair]
        if not _cross(revised, *codes):
            rejected.append({"routes": codes, "reason": "No dry street-linked common crossing"})
            continue
        served_rings = {ring for ring in RINGS if any(
            set(revised["lines"][ring]["station_ids"]) & set(revised["lines"][code]["station_ids"])
            for code in codes
        )}
        if served_rings != RINGS:
            rejected.append({"routes": codes, "reason": "The pair lacks a direct transfer to each ring"})
            continue
        return revised, pair, rejected
    return None, (), rejected


def alternatives(network, graph, context, *, route_km_limit=740.29, protected_stations=(),
                 coverage_cells=None):
    """Return rings-only and paired-axis layouts with retained geometry and evidence.

    Each entry carries a network or a reason the bounded trial did not produce
    one. Walking, cohort access and equal-service ranking belong to the caller.
    """
    validate(network)
    if not all(network["lines"].get(code, {}).get("loop") for code in RINGS):
        raise ValueError("The ring and through layout requires two closed Baghdad rings")
    pool = _screen(network, graph, context, coverage_cells, withdrawn=FEEDER_EXCHANGE)
    recipes = {
        "ring-grid": FEEDER_EXCHANGE,
        # Preserve the two northern access links in the tighter budget trial.
        "ring-grid-feeder-retention": FEEDER_EXCHANGE - RETAINED_GAP_FEEDERS,
        "pure-ring-grid": network["lines"].keys() - (RINGS | DIRECT | ANCHORS),
    }
    candidates = {}
    for name, withdrawals in recipes.items():
        try:
            skeleton, edits, removed_links = _withdraw(network, set(network["lines"]) & withdrawals, protected_stations)
        except ValueError as error:
            candidates[name] = {"network": None, "failure": str(error)}
            continue
        basis = {"actions": edits, "removed_walking_links": removed_links,
                 "retained_direct_line_ids": sorted(DIRECT.intersection(skeleton["lines"])),
                 "route_km_limit": route_km_limit,
                 "axes_screened": pool if name == "ring-grid" else [row["id"] for row in pool]}
        skeleton.setdefault("source_sha256", {})[Path(__file__).relative_to(ROOT).as_posix()] = digest(Path(__file__))
        _identity(skeleton)
        candidates[f"{name}-skeleton"] = basis | {"network": skeleton, "added_axes": []}
        trials = {"": None}
        if name == "pure-ring-grid":
            trials = {"": None, "-orthogonal": (FAMILIES[0], FAMILIES[2]),
                      "-diagonal": (FAMILIES[1], FAMILIES[3])}
        for suffix, families in trials.items():
            revised, axes, rejected = _select(skeleton, pool, graph, context, route_km_limit, family_pair=families)
            result = basis | {"network": revised, "added_axes": list(axes), "failed_pairs": rejected}
            if revised is None:
                result["failure"] = "No pair met route length, crossing and station screens within the bounded search"
            else:
                revised["ring_grid_layout"] = {
                    "variant": name + suffix, "axes": list(axes),
                    "parent_candidate_id": network["candidate_id"], "route_km_limit": route_km_limit,
                }
                revised.setdefault("source_sha256", {})[Path(__file__).relative_to(ROOT).as_posix()] = digest(Path(__file__))
                _identity(revised)
            candidates[name + suffix] = result
    return candidates
