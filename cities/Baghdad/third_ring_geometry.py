"""Screen a third Baghdad orbital against retained rail, streets and waterways."""

from collections import Counter
from copy import deepcopy
from itertools import pairwise
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from shapely import distance, points as geometry_points
from shapely.affinity import scale
from shapely.geometry import LineString, Point, Polygon, shape
from shapely.ops import nearest_points, substring, unary_union
from shapely.prepared import prep

from . import holistic_network as network
from . import holistic_orbitals as orbital
from . import holistic_through as through
from . import ring_corridors as rings
from . import spaced_ring_geometry as spaced

LINE_ID = "M16"
SETBACKS_M = (750, 1_250, 1_750, 2_500, 3_500, 5_000)
SIMPLIFICATIONS_M = (25, 75, 150)
MIN_SEPARATION_M = 500
MIN_TRANSFER_LINES = 3
ROAD_SUPPORT_M = 150
ROAD_GUIDE_TRIALS_M = (1_250, 1_750, 2_500)
ROAD_GUIDE_WINDOW_M = 1_200
ROAD_JOIN_M = 350


def _water_parts(geometry):
    if geometry.is_empty:
        return
    if geometry.geom_type in {"Point", "LineString"}:
        yield geometry
    elif hasattr(geometry, "geoms"):
        for part in geometry.geoms:
            yield from _water_parts(part)


def _tigris(context):
    return unary_union([
        scale(shape(row["geometry"]), *network.LOCAL_METRES, origin=(0, 0))
        for row in context["layers"]["water"]
        if row["properties"].get("name:en") == "Tigris River"
    ])


def _roads(streets, window):
    roads, bridges = [], []
    west, south, east, north = np.asarray(window.bounds) / np.tile(network.LOCAL_METRES, 2)
    for feature in streets["features"]:
        tags = feature["properties"]
        if ((tags.get("highway") or "").removesuffix("_link") not in network.MAJOR_ROADS
                or tags.get("tunnel") not in (None, "no")):
            continue
        if feature["geometry"]["type"] != "LineString":
            continue
        path = feature["geometry"]["coordinates"]
        if any(west < x < east and south < y < north for x, y in path):
            roads.append(path)
            if tags.get("bridge") == "yes":
                bridges.append(path)
    return roads, bridges


def _road_assisted(boundary, outer, road_paths):
    """Use retained road edges where they improve a split, buffered alignment."""
    clearance = prep(outer.buffer(MIN_SEPARATION_M))
    half = boundary.length / 2
    halves = (substring(boundary, 0., half), substring(boundary, half, boundary.length))
    routed = []
    metric_paths = [list(map(tuple, np.asarray(path) * network.LOCAL_METRES)) for path in road_paths]
    coords = np.asarray(sorted({node for path in metric_paths for node in path})).reshape(-1, 2)
    for guide in halves:
        stations = sorted(set(np.r_[np.arange(0., guide.length, 200.), guide.length,
                                    [guide.project(Point(xy)) for xy in guide.coords]]))
        scaffold = [tuple(guide.interpolate(km).coords[0]) for km in stations]
        corridor = prep(guide.buffer(ROAD_GUIDE_WINDOW_M))
        nearby = distance(geometry_points(coords), guide) <= ROAD_GUIDE_WINDOW_M
        nearby_coords = set(map(tuple, coords[nearby]))
        edges = {}

        def edge(a, b, factor, extra=0.):
            if a == b:
                return
            trace = LineString((a, b))
            if clearance.intersects(trace) or not corridor.covers(trace):
                return
            row = (trace.length * factor + extra, None, False)
            first, second = edges.setdefault(a, {}), edges.setdefault(b, {})
            if row[0] < first.get(b, (np.inf,))[0]:
                first[b] = second[a] = row

        for path in metric_paths:
            for a, b in pairwise(path):
                if a in nearby_coords and b in nearby_coords:
                    edge(a, b, 1.)
        road_nodes = sorted(edges)
        if road_nodes:
            tree = cKDTree(road_nodes)
            offsets, indexes = tree.query(scaffold, k=np.arange(1, 7), distance_upper_bound=ROAD_JOIN_M)
            for point, row, neighbors in zip(scaffold, offsets, indexes, strict=True):
                for dist, other in zip(row, neighbors, strict=True):
                    if np.isfinite(dist):
                        edge(point, road_nodes[other], 2., 100.)
        for a, b in pairwise(scaffold):
            edge(a, b, 2.2)
        try:
            routed.append(orbital._road_leg(edges, [scaffold[0], scaffold[-1]], frozenset()))
        except ValueError:
            return None
    return LineString(network._concatenate(*routed)).simplify(10)


def _water_crossings(line, water, tigris, bridges):
    """Identify mapped wet reaches and distinguish tagged and provisional bridge corridors."""
    # A polygon may return multiple adjacent pieces at vertices and tile seams.
    reaches = []
    for part in _water_parts(line.intersection(water)):
        first, last = (Point(part.coords[0]), Point(part.coords[-1]))
        lo, hi = sorted((line.project(first), line.project(last)))
        reaches.append((lo, hi))
    combined = []
    for lo, hi in sorted(reaches):
        if combined and lo - combined[-1][1] <= 5:
            combined[-1] = (combined[-1][0], max(hi, combined[-1][1]))
        else:
            combined.append((lo, hi))
    entries = []
    for lo, hi in combined:
        mid = (lo + hi) / 2
        sample = np.asarray([line.interpolate(x).coords[0] for x in np.linspace(lo, hi, 5)])
        delta = np.asarray(line.interpolate(mid + 1).coords[0]) - line.interpolate(mid - 1).coords[0]
        approach = np.asarray([line.interpolate(x).coords[0] for x in (lo - 60, hi + 60)])
        direction = delta / np.linalg.norm(delta)
        deck_offsets = bridges.nearby(sample, direction, through.BRIDGE_OFFSET_M, 25)
        landing_offsets = bridges.nearby(approach, direction, through.MAX_LANDING_OFFSET_M, 25)
        off_road = not (np.isfinite(deck_offsets).all() and np.isfinite(landing_offsets).all())
        entries.append({
            "entry_m": lo,
            "exit_m": hi,
            "mapped_wet_width_m": round(hi - lo, 1),
            "contact_kind": "wet polygon reach" if hi > lo else "watercourse centreline",
            "coordinates": (np.asarray(line.interpolate(mid).coords[0]) / network.LOCAL_METRES).tolist(),
            "tigris": hi - lo >= 100 and tigris.distance(line.interpolate(mid)) <= 150,
            "basis": "Provisional new elevated crossing" if off_road else "Mapped carriageway bridge corridor",
            "provisional_new_crossing": off_road,
        })
    return entries


def _interchanges(record, track, graph, context):
    lines, stations = record["lines"], record["stations"]
    candidates = []
    for code in sorted(lines.keys() - {LINE_ID, rings.INNER, rings.OUTER}):
        for point, (km, other_km) in network._crossings(track, network.Track(lines[code]["geometry"])).items():
            if 0 < km < track.km:
                candidates.append((code, point, km, other_km))
    points = np.asarray([row[1] for row in candidates]).reshape(-1, 2)
    offsets, _ = graph[3].query(points * network.LOCAL_METRES)
    dry = network.dry_points(points, context)
    selected = []
    for i in sorted(np.flatnonzero(dry & (offsets <= network.TRANSFER_SNAP_M)),
                    key=lambda i: (offsets[i], candidates[i])):
        code, point, km, other_km = candidates[i]
        try:
            stop = network._through_interchange(
                LINE_ID, {"line_id": code}, (point, (km, other_km)), lines, stations,
                require_intermediate=False,
            )
        except ValueError:
            continue
        selected.append({
            "station_id": stop, "line_id": code, "coordinates": list(point), "chainage_km": km,
            "street_offset_m": round(float(offsets[i]), 1),
        })
    lines[LINE_ID]["station_chainage_km"].pop("reference")
    if "reference" in lines[LINE_ID]["station_ids"]:
        lines[LINE_ID]["station_ids"].remove("reference")
    return sorted(selected, key=lambda row: (row["chainage_km"], row["line_id"]))


def _trial_record(reference, geometry, *, assisted=False):
    revised = deepcopy(reference)
    track = network.Track(geometry)
    revised["lines"][LINE_ID] = {
        "name": "Baghdad third orbital",
        "geometry": geometry,
        "loop": True,
        "one_way_km": track.km,
        "station_ids": [],
        "station_chainage_km": {"reference": 0.},
        "source_sections": [],
        "basis": ("GIS offset and mapped major-road concept outside M09" if assisted
                  else "GIS offset concept outside M09") + " with provisional elevated alignments and crossings",
    }
    return revised, track


def _road_support(line, roads):
    supported_m = 0.
    for a, b in pairwise(np.asarray(line.coords)):
        length = float(np.linalg.norm(b - a))
        count = int(np.ceil(length / 100))
        heading = (b - a) / length
        points = a + np.arange(.5, count)[:, None] / count * (b - a)
        supported_m += np.isfinite(roads.nearby(points, heading, ROAD_SUPPORT_M, 25)).sum() * length / count
    return supported_m / line.length


def _rank(row):
    return (-len(row["screened_spokes"]), -len(row["screened_transfer_lines"]),
            row["provisional_crossing_count"], row["one_way_km"],
            -row["major_road_support_share"], row["target_setback_m"], row["simplification_m"])


def evaluate(reference, graph, context, *, streets=None):
    """Compare bounded GIS corridors. Independent rail crossings are held for survey."""
    network.validate(reference)
    if LINE_ID in reference["lines"]:
        raise ValueError("Third orbital evaluation requires a reference without M16")
    outer = rings._ring_polygon(reference["lines"][rings.OUTER])
    inner = rings._ring_polygon(reference["lines"][rings.INNER])
    if not outer.contains(inner):
        raise ValueError("M15 needs to lie wholly inside M09 before testing a third orbital")
    streets = network.read(network.STREETS) if streets is None else streets
    road_paths, bridge_paths = _roads(streets, outer.buffer(max(SETBACKS_M) + ROAD_GUIDE_WINDOW_M))
    roads = through.DirectionalRoads.from_paths(road_paths)
    bridges = through.DirectionalRoads.from_paths(bridge_paths)
    tigris = _tigris(context)
    water = spaced._water(context)
    spokes = {code for stop in reference["lines"][rings.OUTER]["station_ids"]
              for code in reference["stations"][stop]["lines"]} - {rings.OUTER, rings.INNER}
    candidates, rejected = [], Counter()
    boundaries = [(setback, simplify, False,
                   LineString(outer.buffer(setback, quad_segs=8).exterior).simplify(simplify))
                  for setback in SETBACKS_M for simplify in SIMPLIFICATIONS_M]
    boundaries.extend(
        (setback, 75, True, _road_assisted(boundary, outer, road_paths))
        for setback, simplify, assisted, boundary in tuple(boundaries)
        if setback in ROAD_GUIDE_TRIALS_M and simplify == 75
    )
    for setback, simplify, assisted, boundary in boundaries:
        if boundary is None:
            rejected["road-assisted route unavailable"] += 1
            continue
        polygon = Polygon(boundary)
        separation = boundary.distance(outer)
        if not boundary.is_ring or not polygon.is_valid or not polygon.contains(outer) or separation < MIN_SEPARATION_M:
            rejected["invalid nesting or separation"] += 1
            continue
        # Keep the seam outside water so a single wet reach cannot be split across it.
        if water.distance(Point(boundary.coords[0])) < 100:
            vertices = list(boundary.coords)[:-1]
            dry_origin = next((index for index, xy in enumerate(vertices) if water.distance(Point(xy)) >= 100), None)
            if dry_origin is None:
                rejected["no dry chainage origin"] += 1
                continue
            boundary = LineString(vertices[dry_origin:] + vertices[:dry_origin + 1])
        geometry = (np.asarray(boundary.coords) / network.LOCAL_METRES).tolist()
        revised, track = _trial_record(reference, geometry, assisted=assisted)
        contacts = _water_crossings(boundary, water, tigris, bridges)
        main_channel = [item for item in contacts if item["tigris"]]
        if len(main_channel) != 2:
            rejected["expected two mapped Tigris crossings"] += 1
            continue
        transfers = _interchanges(revised, track, graph, context)
        connecting = sorted({site["line_id"] for site in transfers})
        controlling_outer, controlling_third = nearest_points(outer.boundary, boundary)
        candidates.append({
            "geometry": geometry,
            "road_assisted_trace": assisted,
            "one_way_km": track.km,
            "minimum_ring_separation_m": separation,
            "minimum_inner_separation_m": boundary.distance(inner),
            "nearest_m09_coordinates": (np.asarray(controlling_outer.coords[0]) / network.LOCAL_METRES).tolist(),
            "nearest_m16_coordinates": (np.asarray(controlling_third.coords[0]) / network.LOCAL_METRES).tolist(),
            "target_setback_m": setback,
            "simplification_m": simplify,
            "enclosed_area_km2": polygon.area / 1e6,
            "mapped_water_crossings": contacts,
            "new_tigris_crossings": [row for row in main_channel if row["provisional_new_crossing"]],
            "provisional_crossing_count": sum(row["provisional_new_crossing"] for row in contacts),
            "provisional_wet_reach_count": sum(row["provisional_new_crossing"] and row["contact_kind"] == "wet polygon reach"
                                               for row in contacts),
            "maximum_mapped_wet_reach_m": max(row["mapped_wet_width_m"] for row in contacts),
            "road_trace_heading_changes_over_20_degrees": spaced._sharp_bends(track),
            "screened_transfer_sites": transfers,
            "screened_transfer_lines": connecting,
            "screened_spokes": sorted(set(connecting) & spokes),
            "major_road_support_share": _road_support(boundary, roads),
            "passes_connectivity_screen": len(connecting) >= MIN_TRANSFER_LINES,
            "tunnels": 0,
        })
    candidates.sort(key=_rank)
    eligible = [row for row in candidates if row["passes_connectivity_screen"]]
    return {
        "selected": eligible[0] if eligible else None,
        "mapped_bridge_alternative": next((row for row in eligible if not row["provisional_crossing_count"]), None),
        "road_assisted_alternative": next((row for row in eligible if row["road_assisted_trace"]), None),
        "wider_alternative": next((row for row in eligible if row["target_setback_m"] >= 1_750
                                   and row is not eligible[0]), None),
        "checked_candidates": [{key: value for key, value in row.items() if key != "geometry"}
                               for row in candidates],
        "rejection_counts": dict(rejected),
        "trial_count": len(boundaries),
        "minimum_required_separation_m": MIN_SEPARATION_M,
        "ranking_basis": "Most direct M09 spokes, most distinct interchange lines, fewest provisional water "
                         "crossings, shortest loop and most parallel major-road support",
    }


def insert(reference, option, graph, context):
    """Insert a screened M16 and exact shared platform sites in the network."""
    if LINE_ID in reference["lines"] or not option["passes_connectivity_screen"]:
        raise ValueError("Third orbital insertion requires an unused line ID and screened platform locations")
    revised, track = _trial_record(reference, option["geometry"], assisted=option["road_assisted_trace"])
    transfers = _interchanges(revised, track, graph, context)
    if transfers != option["screened_transfer_sites"]:
        raise ValueError("M16 interchange evidence differs from the screened network")
    line, stations = revised["lines"][LINE_ID], revised["stations"]
    origin = transfers[0]["chainage_km"]
    rotated = network.Track(network._concatenate(track.between(origin, track.km), track.between(0., origin)))
    line.update({"geometry": rotated.coordinates.tolist(), "one_way_km": rotated.km})
    line["station_chainage_km"] = {stop: km - origin for stop, km in line["station_chainage_km"].items()}
    for row in transfers:
        row["chainage_km"] -= origin
        stations[row["station_id"]].setdefault("street_offset_m", row["street_offset_m"])
    fixed = [*sorted(line["station_chainage_km"].values()), rotated.km]
    sites = np.arange(.1, rotated.km, .1)
    points = np.asarray([rotated.at(site) for site in sites])
    offsets, _ = graph[3].query(points * network.LOCAL_METRES)
    eligible = sites[network.dry_points(points, context) & (offsets <= network.TRANSFER_SNAP_M)]
    for low, high in pairwise(fixed):
        last = low
        intervals = max(1, round((high - low) / 1.6))
        for target in np.linspace(low, high, intervals + 1)[1:-1]:
            choices = eligible[(eligible - last >= orbital.MIN_STOP_GAP_KM)
                               & (high - eligible >= orbital.MIN_STOP_GAP_KM)]
            if not len(choices):
                continue
            km = float(choices[np.argmin(abs(choices - target))])
            if abs(km - target) > .5:
                continue
            code = f"{LINE_ID}-{round(km * 1000):05d}"
            stations[code] = {
                "name": f"Third orbital · {code}", "lines": [LINE_ID], "coordinates": rotated.at(km),
                "basis": "Provisional dry orbital platform with mapped street access",
            }
            network._add(line, code, km)
            last = km
    rings._refresh_transfers(revised)
    for source in (Path(__file__), network.STREETS, network.INPUTS[-1]):
        revised.setdefault("source_sha256", {})[source.relative_to(network.ROOT).as_posix()] = network.digest(source)
    revised["physical_accepted"] = revised["operating_timetable_validated"] = False
    revised["topology"] = network.validate(revised)
    evidence = {key: value for key, value in option.items()
                if key not in {"geometry", "screened_transfer_sites", "mapped_water_crossings", "new_tigris_crossings"}}
    evidence.update({
        "line_id": LINE_ID,
        "station_count": len(line["station_ids"]),
        "maximum_station_gap_km": float(max(np.diff([*sorted(line["station_chainage_km"].values()), rotated.km]))),
        "transfer_sites": transfers,
        "transfer_count": len({row["station_id"] for row in transfers}),
        "mapped_water_crossings": [
            {key: value for key, value in row.items() if key not in {"entry_m", "exit_m"}} | {
                "entry_km": (row["entry_m"] / 1000 - origin) % track.km,
                "exit_km": (row["exit_m"] / 1000 - origin) % track.km,
            } for row in option["mapped_water_crossings"]
        ],
        "open_engineering": [
            "Road-support share, alignment, land and structures outside matched road corridors",
            "Independent rail bridges, approaches, hydrology, navigation and flood clearance",
            "Surveyed grades, railway curves, platforms and accessible walking routes",
            "Service, depot access and recovery, fleet, lifecycle cost and construction",
        ],
    })
    evidence["new_tigris_crossings"] = [
        row for row in evidence["mapped_water_crossings"] if row["tigris"] and row["provisional_new_crossing"]
    ]
    revised["third_orbital"] = evidence
    return network._identity(revised), evidence
