"""Search compact surface-road rings inside the retained Baghdad M09 trace."""

from copy import deepcopy
from itertools import combinations, pairwise
from pathlib import Path

import numpy as np
from shapely import make_valid
from shapely.affinity import scale
from shapely.geometry import LineString, Point, Polygon, shape
from shapely.ops import nearest_points, polygonize, unary_union
from shapely.prepared import prep

from . import holistic_network as network
from . import holistic_orbitals as orbital
from .ring_corridors import (
    INNER, OUTER, _refresh_transfers, _restore_walk_links, _ring_polygon, _single_parts,
)

MIN_SEPARATION_M = 5_000
INSET_M = 5_050
MAIN_CHANNEL_MIN_M = 100
MIN_DIRECT_SPOKES = 2
MIN_TRANSFERS = 3
BRIDGE_NAMES = {
    "جسر باب المعظم": "Bab al-Mu’azzam Bridge",
    "جسر الشهداء": "Martyrs Bridge",
    "جسر الاحرار": "Al-Ahrar Bridge",
    "جسر السنك": "Al-Sinak Bridge",
    "جسر الجمهورية": "Al-Jumhuriya Bridge",
    "جسر 14 تموز": "14 July Bridge",
}


def _water(context):
    return unary_union([
        scale(make_valid(shape(row["geometry"])), *network.LOCAL_METRES, origin=(0, 0))
        for row in context["layers"]["water"]
    ])


def _graph(streets, inset, water):
    features = {row["id"]: row for row in streets["features"]}
    retained, _ = orbital._roads(streets, orbital.BRIDGES)
    window, wet = prep(inset), prep(water)
    points = {point: tuple(np.asarray(point) * network.LOCAL_METRES)
              for point in retained if window.covers(Point(np.asarray(point) * network.LOCAL_METRES))}
    roads = {a: {} for a in points}
    wet_ways = set()
    for a in sorted(points):
        for b, (_, way, bridge) in sorted(retained[a].items()):
            if b not in points or a >= b:
                continue
            segment = LineString([points[a], points[b]])
            if not window.covers(segment):
                continue
            if wet.intersects(segment):
                if not bridge:
                    continue
                wet_ways.add(way)
            roads[a][b] = roads[b][a] = (segment.length, way, bridge)
    bridge_paths = {}
    for way in sorted(wet_ways):
        feature = features[way]
        path = list(map(tuple, feature["geometry"]["coordinates"]))
        if not all(roads.get(a, {}).get(b, (None, None))[1] == way for a, b in pairwise(path)):
            continue
        track = LineString(np.asarray(path) * network.LOCAL_METRES)
        widths = [part.length for part in _single_parts(track.intersection(water))]
        name = feature["properties"].get("name")
        if max(widths, default=0.) < MAIN_CHANNEL_MIN_M or name not in BRIDGE_NAMES:
            continue
        bridge_paths[way] = (BRIDGE_NAMES[name], path if path[0][0] < path[-1][0] else path[::-1])
    bank_roads = {a: dict(b) for a, b in roads.items()}
    for _, path in bridge_paths.values():
        for a, b in pairwise(path):
            bank_roads[a].pop(b, None)
            bank_roads[b].pop(a, None)
    return roads, bank_roads, bridge_paths


def separation(outer_line, geometry):
    """Return continuous boundary distance and its controlling points in local metres."""
    outer = _ring_polygon(outer_line)
    inner = Polygon(network.Track(geometry).points)
    if geometry[0] != geometry[-1] or not inner.is_valid or not outer.contains(inner):
        raise ValueError("A compact inner ring must be simple, closed and wholly inside M09")
    outer_point, inner_point = nearest_points(outer.boundary, inner.boundary)
    return {
        "minimum_ring_separation_m": float(outer.boundary.distance(inner.boundary)),
        "nearest_outer_coordinates": (np.asarray(outer_point.coords[0]) / network.LOCAL_METRES).tolist(),
        "nearest_inner_coordinates": (np.asarray(inner_point.coords[0]) / network.LOCAL_METRES).tolist(),
    }


def _prospective_crossings(alignment, wet, rail):
    return sorted(
        code for code, line in rail.items()
        if any(part.geom_type == "Point" and not wet.intersects(part)
               for part in _single_parts(alignment.intersection(line)))
    )


def _actual_transfers(option, reference, walking_graph, context):
    trial = deepcopy(reference)
    track = network.Track(option["geometry"])
    trial["lines"][INNER] = {
        "loop": True, "one_way_km": track.km, "station_ids": ["reference"],
        "station_chainage_km": {"reference": 0.},
    }
    banks = option["bank_chainage_km"] or (0., track.km, track.km)
    return orbital._interchanges(trial, track, walking_graph, context, banks)


def _bridge_pair(first, second, paths, bank_roads):
    p, q = (paths[way][1] for way in (first, second))
    forbidden = frozenset(p + q)
    east = orbital._road_leg(bank_roads, [p[-1], q[-1]], forbidden)
    west = orbital._road_leg(bank_roads, [q[0], p[0]], forbidden)
    return network._concatenate(p, east, q[::-1], west)


def _bank_faces(bank_roads, wet):
    """Enumerate bounded road faces whose boundary and interior stay dry."""
    edges = [LineString([a, b]) for a, neighbors in sorted(bank_roads.items())
             for b in sorted(neighbors) if a < b]
    for face in polygonize(edges):
        points = [list(row) for row in face.exterior.coords]
        polygon = Polygon(np.asarray(points) * network.LOCAL_METRES)
        if polygon.area < 100_000 or polygon.length < 2_600 or wet.intersects(polygon):
            continue
        yield points


def evaluate_geometry(outer_line, reference_network, context, *, streets=None, walking_graph=None):
    """Return compact GIS candidates ranked by shortest screened corridor."""
    outer = _ring_polygon(outer_line)
    inset = outer.buffer(-INSET_M, quad_segs=32)
    if inset.is_empty:
        raise ValueError("The retained M09 has no interior at the specified search inset")
    water = _water(context)
    wet = prep(water)
    streets = network.read(network.STREETS) if streets is None else streets
    roads, bank_roads, paths = _graph(streets, inset, water)
    shared = {code for stop in outer_line["station_ids"]
              for code in reference_network["stations"][stop]["lines"]} - {OUTER, INNER}
    rail = {code: LineString(network.Track(line["geometry"]).points)
            for code, line in reference_network["lines"].items() if code not in {OUTER, INNER}}

    def assess(geometry, ways=()):
        track = network.Track(geometry)
        polygon = Polygon(track.points)
        if not polygon.is_valid or not inset.covers(polygon.boundary):
            raise ValueError("Road path failed the simple closed-loop inset screen")
        gap = separation(outer_line, geometry)
        if gap["minimum_ring_separation_m"] < MIN_SEPARATION_M:
            raise ValueError("Road path failed continuous minimum ring separation")
        contacts = orbital._water_crossings(track, roads, context) if ways else []
        for row in contacts:
            if row["road_way_id"] in paths:
                row["name"] = paths[row["road_way_id"]][0]
        channel = {row["road_way_id"]: row for row in contacts if row["mapped_wet_width_m"] >= MAIN_CHANNEL_MIN_M}
        if channel.keys() != set(ways):
            raise ValueError("Road path failed its expected main-channel bridge crossings")
        banks = None
        if ways:
            first, second = (channel[way] for way in ways)
            banks = [first["exit_m"] / 1000, second["entry_m"] / 1000, second["exit_m"] / 1000]
        prospective = _prospective_crossings(polygon.boundary, wet, rail)
        option = {
            "geometry": geometry, "one_way_km": track.km, **gap,
            "topology": "Tigris-straddling" if ways else "one-bank",
            "enclosed_area_km2": polygon.area / 1e6,
            "bridge_ways": list(ways), "bridges": [paths[way][0] for way in ways],
            "mapped_water_crossings": contacts, "bank_chainage_km": banks,
            "prospective_spokes": sorted(set(prospective) & shared),
            "prospective_interchange_lines": prospective,
            "tunnels": 0,
            "road_trace_heading_changes_over_20_degrees": _sharp_bends(track),
        }
        connected = len(option["prospective_spokes"]) >= MIN_DIRECT_SPOKES and len(prospective) >= MIN_TRANSFERS
        if connected and walking_graph is not None:
            transfers = _actual_transfers(option, reference_network, walking_graph, context)
            option["screened_transfer_sites"] = transfers
            option["screened_spokes"] = sorted({row["line_id"] for row in transfers} & shared)
            connected = len(option["screened_spokes"]) >= MIN_DIRECT_SPOKES and len(transfers) >= MIN_TRANSFERS
            if ways:
                connected &= {row["bank"] for row in transfers} == {"east", "west"}
        option["passes_connectivity_screen"] = connected
        return option

    trials, rejected = [], []
    for first, second in combinations(paths, 2):
        if paths[first][0] == paths[second][0]:
            continue
        ways = (first, second)
        try:
            trials.append(assess(_bridge_pair(*ways, paths, bank_roads), ways))
        except ValueError as error:
            rejected.append({"bridge_ways": list(ways), "reason": str(error)})
    bank_trials = []
    for face in _bank_faces(bank_roads, wet):
        try:
            bank_trials.append(assess(face))
        except ValueError:
            continue
    ordered = sorted(trials, key=lambda row: (row["one_way_km"], row["bridge_ways"]))
    bank_trials.sort(key=lambda row: (-len(row["prospective_spokes"]),
                                      -len(row["prospective_interchange_lines"]), row["one_way_km"]))
    eligible = [row for row in [*ordered, *bank_trials] if row["passes_connectivity_screen"]]
    selected = min(eligible, key=lambda row: row["one_way_km"], default=None)
    return {
        "selected": selected, "one_bank": bank_trials[0] if bank_trials else None,
        "bridge_pairs": ordered, "rejected_bridge_pairs": rejected, "one_bank_faces_screened": len(bank_trials),
        "minimum_required_separation_m": MIN_SEPARATION_M, "road_search_inset_m": INSET_M,
        "distance_basis": "Continuous segment separation in the retained Baghdad local metric projection",
        "ranking_basis": "Shortest eligible route among shortest mapped road-leg trials for each bridge-way pair and single dry road faces",
        "connectivity_basis": f"At least {MIN_TRANSFERS} distinct connecting lines and {MIN_DIRECT_SPOKES} direct M09 spokes"
                              + (", with screened interchange placement and one transfer on each bank for river loops"
                                 if walking_graph is not None else ", using dry alignment crossings"),
    }


def _sharp_bends(track):
    directions = track.delta / track.lengths[:, None]
    return int((np.sum(directions * np.roll(directions, 1, axis=0), axis=1)
                < np.cos(np.deg2rad(20))).sum())


def insert(outer_network, option, graph, context):
    """Add a screened compact M15 and bind it to retained passenger lines."""
    network.validate(outer_network)
    if INNER in outer_network["lines"] or not option["passes_connectivity_screen"]:
        raise ValueError("Compact M15 requires a cleared ring geometry and an unused route ID")
    revised = deepcopy(outer_network)
    links = revised.pop("station_site_links", None)
    lines, stations = revised["lines"], revised["stations"]
    track = network.Track(option["geometry"])
    line = lines[INNER] = {
        "name": "Baghdad compact inner orbital",
        "geometry": option["geometry"],
        "loop": True,
        "one_way_km": track.km,
        "station_ids": ["reference"],
        "station_chainage_km": {"reference": 0.},
        "source_sections": list(option["bridges"]),
        "basis": "Retained major surface roads and mapped carriageway bridge corridors. Elevated rail planning hypothesis.",
    }
    banks = option["bank_chainage_km"] or (0., track.km, track.km)
    transfers = orbital._interchanges(revised, track, graph, context, banks)
    bank_counts = {bank: sum(row["bank"] == bank for row in transfers) for bank in ("east", "west")}
    outer_lines = {code for stop in lines[OUTER]["station_ids"] for code in stations[stop]["lines"]}
    spokes = sorted(outer_lines & {row["line_id"] for row in transfers})
    if (len(transfers) < MIN_TRANSFERS or len(spokes) < MIN_DIRECT_SPOKES
            or (option["bridge_ways"] and not min(bank_counts.values()))):
        raise ValueError("Compact M15 requires screened connections to three lines, including two M09 spokes and both river banks")

    origin = transfers[0]["chainage_km"]
    rotated = network.Track(network._concatenate(track.between(origin, track.km), track.between(0., origin)))
    line.update({"geometry": rotated.coordinates.tolist(), "one_way_km": rotated.km})
    line["station_chainage_km"].pop("reference")
    line["station_chainage_km"] = {stop: km - origin for stop, km in line["station_chainage_km"].items()}
    line["station_ids"].remove("reference")
    for row in transfers:
        row["chainage_km"] -= origin
        if not option["bridge_ways"]:
            row["bank"] = "same bank"
    orbital._ordinary_stations(line, stations, rotated, graph, context)
    _refresh_transfers(revised)
    removed = _restore_walk_links(revised, outer_network, links)
    for source in (Path(__file__), Path(orbital.__file__), network.STREETS):
        revised.setdefault("source_sha256", {})[source.relative_to(network.ROOT).as_posix()] = network.digest(source)
    revised["physical_accepted"] = False
    revised["operating_timetable_validated"] = False
    evidence = {
        "line_id": INNER,
        "status": "compact GIS corridor and access screen passed",
        "one_way_km": rotated.km,
        **separation(lines[OUTER], line["geometry"]),
        "transfers_by_bank": bank_counts if option["bridge_ways"] else {"same bank": len(transfers)},
        "transfer_sites": transfers,
        "transfer_count": len(transfers),
        "direct_spokes_between_rings": spokes,
        "stations": len(line["station_ids"]),
        "maximum_station_gap_km": round(float(max(np.diff([
            *(line["station_chainage_km"][stop] for stop in line["station_ids"]), rotated.km,
        ]))), 3),
        "mapped_water_crossings": [
            {key: value for key, value in row.items() if key not in {"entry_m", "exit_m"}} | {
                "entry_km": round((row["entry_m"] / 1000 - origin) % track.km, 3),
                "exit_km": round((row["exit_m"] / 1000 - origin) % track.km, 3),
            }
            for row in option["mapped_water_crossings"]
        ],
        "tunnels": 0,
        "removed_walk_links": removed,
        "road_trace_heading_changes_over_20_degrees": _sharp_bends(track),
        "open_engineering": [
            "Surveyed rail curves, transition lengths, grades and resulting closure clearance",
            "Independent rail river crossings, navigation and flood clearance",
            "Accessible platform layout and walking transfers",
            "Land, utilities, piers, foundations and construction staging",
            "Train working, depot moves, capacity and lifecycle cost",
        ],
    }
    if evidence["minimum_ring_separation_m"] < MIN_SEPARATION_M:
        raise ValueError("The final compact M15 failed continuous minimum ring separation")
    revised["spaced_inner_ring"] = evidence
    revised["topology"] = network.validate(revised)
    return network._identity(revised), evidence
