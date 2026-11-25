"""Screen Baghdad inner orbital hypotheses on retained major-road geometry."""

from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
from heapq import heappop, heappush
from itertools import pairwise
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from .central_access import encode
from .holistic_network import (
    EXACT_CROSSING_M, INTERCHANGE_SPACING_M, LOCAL_METRES, MAJOR_ROADS, ROOT, STREETS,
    TRANSFER_SNAP_M, Track, _add,
    _concatenate, _crossings, _identity, _place_index, _through_interchange,
    digest, dry_points, read, validate,
)
from .holistic_through import WaterGeometry, _water_contacts

LINE_ID = "M15"
LENGTH_RANGE_KM = (25, 55)
MIN_STOP_GAP_KM = .65
MIN_BANK_TRANSFERS = 2
MAX_WET_WIDTH_M = 550
MAX_WAYPOINT_SNAP_M = 400

# Areas to pass through. The alignment stays on connected retained roads.
WEST_WAYPOINT = (44.3270, 33.3260)  # Al-Mansour
EAST_WAYPOINT = (44.4320, 33.3440)  # Palestine Street
NORTH_WAY = 4295613
SOUTH_WAYS = (4082481, 4082482, 494461243, 626727315)
# Retained ways stored east to west rather than west to east.
EAST_TO_WEST_WAYS = {4082482, 626727315}
BRIDGES = {
    NORTH_WAY: "Al-A'imma Bridge",
    4082481: "14 July Bridge",
    4082482: "14 July Bridge",
    494461243: "Al-Jadriya Bridge",
    626727315: "Al-Jadriya Bridge",
}


def _roads(streets, allowed_bridges):
    edges = defaultdict(dict)
    bridges = {}
    for feature in streets["features"]:
        tags = feature["properties"]
        kind = (tags.get("highway") or "").removesuffix("_link")
        if kind not in MAJOR_ROADS or tags.get("tunnel") not in (None, "no"):
            continue
        way = feature["id"]
        if way in BRIDGES and way not in allowed_bridges:
            continue
        path = list(map(tuple, feature["geometry"]["coordinates"]))
        tagged = tags.get("bridge") == "yes"
        if way in allowed_bridges and tagged:
            bridges[way] = path
        for a, b in pairwise(path):
            if a == b or not all(44.25 < x < 44.52 and 33.23 < y < 33.43 for x, y in (a, b)):
                continue
            length = np.linalg.norm((np.asarray(a) - b) * LOCAL_METRES)
            row = float(length * MAJOR_ROADS[kind]), way, tagged
            if row < edges[a].get(b, (np.inf,)):
                edges[a][b] = edges[b][a] = row
    return edges, bridges


def _road_leg(edges, anchors, forbidden):
    path = []
    for start, finish in pairwise(anchors):
        previous = {}
        costs = {start: 0.}
        pending = [(0., start)]
        while pending:
            distance, node = heappop(pending)
            if node == finish:
                break
            if distance != costs[node]:
                continue
            for other, (length, _, _) in edges[node].items():
                if other in forbidden and other != finish:
                    continue
                trial = distance + length
                if trial < costs.get(other, np.inf):
                    costs[other] = trial
                    previous[other] = node
                    heappush(pending, (trial, other))
        if finish not in costs:
            raise ValueError("No connected major surface-road path between nominated bridge approaches")
        leg = [finish]
        while leg[-1] != start:
            leg.append(previous[leg[-1]])
        path = _concatenate(path, reversed(leg))
    return path


def _water_crossings(track, edges, context):
    """Enforce mapped bridge support along the wet sections of the road trace."""
    water = WaterGeometry.from_context(context)
    contacts = []
    for i, (a, b) in enumerate(pairwise(track.points)):
        # Extend slightly to capture a linear canal at a retained road
        # vertex, then clip accepted contacts to the unextended edge.
        metres = track.lengths[i]
        extension = min(.01, metres / 100)
        offset = (b - a) * extension / metres
        hits = [(low * (metres + 2 * extension) - extension,
                 high * (metres + 2 * extension) - extension)
                for low, high in _water_contacts(a - offset, b + offset, context, water)]
        hits = [(max(0., low), min(metres, high)) for low, high in hits
                if low <= metres + 1e-7 and high >= -1e-7]
        if not hits:
            continue
        start, end = map(tuple, track.coordinates[i:i + 2])
        _, way, tagged = edges[start][end]
        if not tagged:
            raise ValueError(f"Water crossing on road way {way} lacks a retained carriageway bridge tag")
        for low, high in hits:
            entry, exit = track.chainage[i] + np.array([low, high])
            if contacts and way == contacts[-1]["road_way_id"] and entry - contacts[-1]["exit_m"] <= 5:
                contacts[-1]["exit_m"] = float(exit)
            else:
                contacts.append({"road_way_id": way, "entry_m": float(entry), "exit_m": float(exit)})
    for row in contacts:
        width = row["exit_m"] - row["entry_m"]
        if width > MAX_WET_WIDTH_M:
            raise ValueError(f"Road way {row['road_way_id']} exceeds the mapped water-width screen")
        row["mapped_wet_width_m"] = round(width, 1)
        if row["road_way_id"] in BRIDGES:
            row["name"] = BRIDGES[row["road_way_id"]]
    return contacts


def _orbital_geometry(streets, context, southern_way):
    edges, bridges = _roads(streets, {NORTH_WAY, southern_way})
    if not {NORTH_WAY, southern_way} <= bridges.keys():
        raise ValueError("A nominated carriageway bridge is missing from retained streets")
    north, south = bridges[NORTH_WAY], bridges[southern_way]
    if southern_way in EAST_TO_WEST_WAYS:
        south = south[::-1]
    # Both bridges are oriented from the western bank to the eastern bank.
    if not dry_points([north[0], north[-1], south[0], south[-1]], context).all():
        raise ValueError("A named bridge lacks two mapped dry approaches")
    nodes = sorted(edges)
    offsets, indexes = cKDTree(np.asarray(nodes) * LOCAL_METRES).query(
        np.asarray([WEST_WAYPOINT, EAST_WAYPOINT]) * LOCAL_METRES)
    if max(offsets) > MAX_WAYPOINT_SNAP_M:
        raise ValueError("An orbital waypoint is outside the major-road snap allowance")
    west, east = [nodes[i] for i in indexes]
    forbidden = frozenset(north + south)
    east_leg = _road_leg(edges, [north[-1], east, south[-1]], forbidden)
    west_leg = _road_leg(edges, [south[0], west, north[0]], forbidden)
    geometry = _concatenate(north, east_leg, south[::-1], west_leg)
    if geometry[0] != geometry[-1] or len(set(map(tuple, geometry[:-1]))) != len(geometry) - 1:
        raise ValueError("The road trace does not form a closed simple loop")
    track = Track(geometry)
    if not LENGTH_RANGE_KM[0] <= track.km <= LENGTH_RANGE_KM[1]:
        raise ValueError(f"The road loop is {track.km:.2f} km, outside the orbital comparison range")
    if any(.00001 < abs(a - b) < track.km - .00001 for a, b in _crossings(track, track).values()):
        raise ValueError("The road loop crosses its own alignment")
    crossings = _water_crossings(track, edges, context)
    main_channel_ways = {row["road_way_id"] for row in crossings if row["mapped_wet_width_m"] >= 100}
    if main_channel_ways != {NORTH_WAY, southern_way}:
        raise ValueError("The route must cross mapped water on both named bridges")
    north_end = max(row["exit_m"] for row in crossings if row["road_way_id"] == NORTH_WAY) / 1000
    # The main channel defines the bank on the Al-Jadriya alternative,
    # where the same mapped bridge way crosses a minor canal.
    river = max((row for row in crossings if row["road_way_id"] == southern_way),
                key=lambda row: row["mapped_wet_width_m"])
    return track, crossings, (north_end, river["entry_m"] / 1000, river["exit_m"] / 1000)


def _cycle_distance(a, b, length):
    return min(abs(a - b), length - abs(a - b))


def _relocatable_infill(line, stations, code, chainage, point):
    distance = abs
    if line["loop"]:
        distance = lambda first: _cycle_distance(first, 0., line["one_way_km"])
    allowance = INTERCHANGE_SPACING_M / 1000
    conflicts = [stop for stop, km in line["station_chainage_km"].items()
                 if distance(chainage - km) < allowance]
    if len(conflicts) != 1:
        return None
    stop = conflicts[0]
    station = stations[stop]
    if (station["lines"] != [code] or not stop.startswith(f"{code}-infill-")
            or not station["basis"].startswith("Population-ranked street-access infill")
            or np.linalg.norm((np.asarray(station["coordinates"]) - point) * LOCAL_METRES) <= EXACT_CROSSING_M):
        return None
    return stop


def _interchanges(revised, track, graph, context, banks):
    lines, stations = revised["lines"], revised["stations"]
    candidates = []
    for code in sorted(lines.keys() - {LINE_ID}):
        for point, (chain, other_chain) in _crossings(track, Track(lines[code]["geometry"])).items():
            if 0 < chain < track.km:
                candidates.append((code, point, chain, other_chain))
    points = [row[1] for row in candidates]
    offsets, _ = graph[3].query(np.asarray(points).reshape(-1, 2) * LOCAL_METRES)
    dry = dry_points(points, context)
    place_tree, places = _place_index(context)
    selected, occupied = [], set()
    north_end, east_end, west_start = banks
    for i in sorted(np.flatnonzero(dry & (offsets <= TRANSFER_SNAP_M)), key=lambda i: (offsets[i], candidates[i])):
        code, point, chain, other_chain = candidates[i]
        if code in occupied or any(_cycle_distance(chain, row["chainage_km"], track.km) < MIN_STOP_GAP_KM
                                    for row in selected):
            continue
        if north_end < chain < east_end:
            bank = "east"
        elif west_start < chain < track.km:
            bank = "west"
        else:
            continue
        distance, place = place_tree.query(np.asarray(point) * LOCAL_METRES)
        name = places[place][1] if distance <= 1100 else f"{LINE_ID}–{code}"
        movable = _relocatable_infill(lines[code], stations, code, other_chain, point)
        previous = {}
        if movable is not None:
            previous = {"prior_chainage_km": lines[code]["station_chainage_km"][movable],
                        "prior_coordinates": stations[movable]["coordinates"]}
            stations[movable]["coordinates"] = list(point)
            _add(lines[code], movable, other_chain)
        try:
            stop = _through_interchange(
                LINE_ID, {"line_id": code, "name": f"{name} interchange"},
                (point, (chain, other_chain)), lines, stations,
            )
        except ValueError:
            if movable is not None:
                stations[movable]["coordinates"] = previous["prior_coordinates"]
                _add(lines[code], movable, previous["prior_chainage_km"])
            continue
        detail = {"station_id": stop, "line_id": code, "bank": bank, "coordinates": list(point),
                  "chainage_km": chain, "street_offset_m": round(float(offsets[i]), 1)}
        stations[stop]["street_offset_m"] = detail["street_offset_m"]
        if movable is not None:
            previous["shift_on_retained_line_m"] = round(
                _cycle_distance(other_chain, previous["prior_chainage_km"], lines[code]["one_way_km"]) * 1000
                if lines[code]["loop"] else abs(other_chain - previous["prior_chainage_km"]) * 1000, 1)
            detail["relocated_infill"] = previous
            stations[stop]["name"] = f"{name} interchange"
            stations[stop]["basis"] = "Population-ranked infill relocated to an exact orbital crossing"
        selected.append(detail)
        occupied.add(code)
    return sorted(selected, key=lambda row: row["chainage_km"])


def _ordinary_stations(line, stations, track, graph, context):
    fixed = sorted(line["station_chainage_km"].values())
    sites = np.arange(.1, track.km, .1)
    points = np.asarray([track.at(site) for site in sites])
    offsets, _ = graph[3].query(points * LOCAL_METRES)
    dry = dry_points(points, context)
    eligible = sites[dry & (offsets <= TRANSFER_SNAP_M)]
    place_tree, places = _place_index(context)
    for low, high in pairwise([*fixed, track.km]):
        intervals = max(1, round((high - low) / 1.4))
        last = low
        for target in np.linspace(low, high, intervals + 1)[1:-1]:
            choices = eligible[(eligible - last >= MIN_STOP_GAP_KM) & (high - eligible >= MIN_STOP_GAP_KM)]
            if not len(choices):
                continue
            chainage = float(choices[np.abs(choices - target).argmin()])
            if abs(chainage - target) > .5:
                continue
            point = track.at(chainage)
            distance, place = place_tree.query(np.asarray(point) * LOCAL_METRES)
            name = places[place][1] if distance <= 1100 else "Inner orbital"
            code = f"{LINE_ID}-{round(chainage * 1000):05d}"
            stations[code] = {"name": f"{name} · {code}", "coordinates": point, "lines": [LINE_ID],
                              "basis": "Provisional orbital platform on retained major-road corridor"}
            _add(line, code, chainage)
            last = chainage


def _insert(network, track, crossings, banks, graph, context):
    revised = deepcopy(network)
    lines, stations = revised["lines"], revised["stations"]
    # A temporary chainage reference lets the shared interchange routine
    # check orbital wrap spacing before the first passenger station is known.
    line = lines[LINE_ID] = {
        "name": "Baghdad inner orbital", "geometry": track.coordinates.tolist(),
        "station_ids": ["reference"], "station_chainage_km": {"reference": 0.},
        "loop": True, "one_way_km": track.km, "source_sections": [
            BRIDGES[way] for way in dict.fromkeys(row["road_way_id"] for row in crossings) if way in BRIDGES],
        "basis": "Retained OSM major-road and named carriageway bridge corridor. Elevated rail planning hypothesis.",
    }
    selected = _interchanges(revised, track, graph, context, banks)
    bank_counts = {bank: sum(row["bank"] == bank for row in selected) for bank in ("east", "west")}
    if min(bank_counts.values()) < MIN_BANK_TRANSFERS:
        raise ValueError(f"Insufficient accessible retained-line interchanges on both banks ({bank_counts})")
    origin = selected[0]["chainage_km"]
    line["geometry"] = _concatenate(track.between(origin, track.km), track.between(0., origin))
    rotated = Track(line["geometry"])
    line["one_way_km"] = rotated.km
    line["station_chainage_km"].pop("reference")
    line["station_chainage_km"] = {code: km - origin for code, km in line["station_chainage_km"].items()}
    line["station_ids"].remove("reference")
    for row in selected:
        row["chainage_km"] -= origin
    _ordinary_stations(line, stations, rotated, graph, context)
    prior = {row["id"]: row for row in revised["transfers"]}
    revised["transfers"] = [
        prior.get(stop, {"id": stop, "name": row["name"], "station_ids": [stop],
                         "walking_m": None, "basis": row["basis"]}) | {"lines": sorted(row["lines"])}
        for stop, row in sorted(stations.items()) if len(row["lines"]) > 1
    ]
    source_hashes = revised.setdefault("source_sha256", {})
    for source in (Path(__file__), Path(__file__).with_name("holistic_through.py"), STREETS):
        source_hashes[source.relative_to(ROOT).as_posix()] = digest(source)
    revised["topology"] = validate(revised)
    revised["physical_accepted"] = False
    revised["operating_timetable_validated"] = False
    bends = np.arccos(np.clip(np.sum(track.delta * np.roll(track.delta, 1, axis=0), axis=1)
                             / (track.lengths * np.roll(track.lengths, 1)), -1, 1))
    evidence = {
        "status": "gis corridor and access screen passed",
        "line_id": LINE_ID,
        "one_way_km": rotated.km,
        "road_geometry_sha256": sha256(encode(track.coordinates.tolist())).hexdigest(),
        "tunnels": 0,
        "transfer_count": len(selected),
        "relocated_infill_stations": sum("relocated_infill" in row for row in selected),
        "transfers_by_bank": bank_counts,
        "transfer_sites": selected,
        "stations": len(line["station_ids"]),
        "maximum_station_gap_km": round(max(np.diff([*(line["station_chainage_km"][stop]
                                                       for stop in line["station_ids"]), rotated.km])), 3),
        "mapped_water_crossings": [
            {key: value for key, value in row.items() if key not in {"entry_m", "exit_m"}} | {
                "entry_km": round((row["entry_m"] / 1000 - origin) % track.km, 3),
                "exit_km": round((row["exit_m"] / 1000 - origin) % track.km, 3)}
            for row in crossings
        ],
        "road_trace_heading_changes_over_20_degrees": int((bends > np.deg2rad(20)).sum()),
        "open_engineering": ["Surveyed horizontal rail curves and vertical grades",
                             "Independent rail bridge structures, navigation and flood clearance",
                             "Platform fit, vertical transfer routes, street entrances and accessibility",
                             "Road clearances, land, utilities, foundations and construction staging",
                             "Fleet, timetable, traction, junctions, operating cost and service comparison"],
    }
    if "M09" in lines:
        outer = Track(lines["M09"]["geometry"])
        inner_samples = [track.at(km) for km in np.arange(0., track.km, .05)]
        outer_samples = [outer.at(km) for km in np.arange(0., outer.km, .05)]
        offsets, _ = cKDTree(np.asarray(outer_samples) * LOCAL_METRES).query(
            np.asarray(inner_samples) * LOCAL_METRES)
        evidence["outer_orbit_km"] = outer.km
        evidence["inner_length_share_within_350_m_of_outer"] = round(float((offsets <= 350).mean()), 3)
    return revised, evidence


def add_inner_orbit(network, graph, context, *, southern_way=None):
    """Return a revised passenger network and the exact geometry/access screen.

    Pass the southern_way from evidence to trace the same roads for another
    network. A failed screen returns the input with its failure evidence.
    """
    if LINE_ID in network["lines"]:
        raise ValueError(f"{LINE_ID} already exists")
    validate(network)
    streets = read(STREETS)
    attempts = []
    for way in (southern_way,) if southern_way is not None else SOUTH_WAYS:
        if way not in SOUTH_WAYS:
            raise ValueError(f"Unknown southern orbital bridge way {way}")
        try:
            track, crossings, banks = _orbital_geometry(streets, context, way)
            revised, evidence = _insert(network, track, crossings, banks, graph, context)
        except ValueError as error:
            attempts.append({"southern_way": way, "reason": str(error)})
            continue
        evidence.update({"southern_way": way, "earlier_failed_hypotheses": attempts})
        revised["inner_orbit"] = evidence
        return _identity(revised), evidence
    return network, {"status": "gis corridor or access screen failed", "failed_hypotheses": attempts}
