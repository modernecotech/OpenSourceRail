"""Compare closed Baghdad planning rings against a retained passenger layout."""

from copy import deepcopy
from pathlib import Path

import numpy as np
from shapely import make_valid
from shapely.affinity import scale
from shapely.geometry import LineString, Point, Polygon, shape
from shapely.ops import unary_union

from . import holistic_network as network_model
from .holistic_orbitals import LINE_ID as INNER, add_inner_orbit
from .holistic_through import BRIDGE_OFFSET_M, MAX_WATER_SPAN_M, ROAD_CORRIDOR_M, _street_layers

OUTER = "M09"
SOUTHERN_WAY = 626727315  # Al-Jadriya road trace used in the earlier M15 study


def _close_outer(revised, retained):
    """Restore the omitted section of the retained M09 trace and its mapped stops."""
    lines, stations = revised["lines"], revised["stations"]
    line, source = lines[OUTER], retained["lines"][OUTER]
    if not source["loop"]:
        raise ValueError("The retained M09 source must contain a closed ring")
    if line["loop"]:
        return {"added_guideway_km": 0., "restored_station_ids": [], "restored_chainage_range_km": None,
                "retained_outer_candidate_id": retained["candidate_id"]}

    track = network_model.Track(source["geometry"])
    arc = network_model.Track(line["geometry"])
    start, end = [track.locate(point) for point in arc.coordinates[[0, -1]]]
    if max(start[1], end[1]) > network_model.SOURCE_STOP_SNAP_M:
        raise ValueError("The current M09 terminals differ from the retained outer ring")
    start_km, end_km = start[0], end[0]
    forward_km = (end_km - start_km) % track.km
    if abs(forward_km - arc.km) > abs(track.km - forward_km - arc.km):
        track = network_model.Track(track.coordinates[::-1])
        start_km, end_km = track.km - start_km, track.km - end_km
        forward_km = (end_km - start_km) % track.km
    if abs(forward_km - arc.km) > .1:
        raise ValueError("The current M09 arc distance differs from the corresponding retained trace")
    if any(track.locate(point)[1] > network_model.SOURCE_STOP_SNAP_M for point in arc.coordinates):
        raise ValueError("The current M09 alignment leaves the retained outer trace")

    if end_km < start_km:
        closure = track.between(end_km, start_km)
    else:
        tail = track.between(end_km, track.km) if end_km < track.km else []
        head = track.between(0., start_km) if start_km > 0. else []
        closure = network_model._concatenate(tail, head)
    geometry = network_model._concatenate(arc.coordinates.tolist(), closure, [arc.coordinates[0]])
    closed = network_model.Track(geometry)
    line.update({"geometry": geometry, "one_way_km": closed.km, "loop": True,
                 "source_sections": list(source["source_sections"]),
                 "basis": "Current outer arc plus the omitted section of the retained M09 mapped trace."})

    restored = []
    for stop in source["station_ids"]:
        station = stations.get(stop, retained["stations"][stop])
        chainage, offset, _ = closed.locate(station["coordinates"])
        if (stop in line["station_chainage_km"] or chainage <= arc.km or chainage >= closed.km
                or offset > network_model.SOURCE_STOP_SNAP_M
                or network_model._terminal_margin(line, chainage) < network_model.INTERCHANGE_SPACING_M):
            continue
        if stop not in stations:
            stations[stop] = deepcopy(station) | {
                "lines": [], "basis": "Mapped station on restored retained M09 section",
            }
        network_model._add(line, stop, chainage)
        stations[stop]["lines"] = sorted([*stations[stop]["lines"], OUTER])
        restored.append(stop)
    revised["source_sha256"] = retained.get("source_sha256", {}) | revised.get("source_sha256", {})
    return {
        "added_guideway_km": closed.km - arc.km,
        "restored_chainage_range_km": [arc.km, closed.km],
        "restored_station_ids": sorted(restored),
        "retained_outer_candidate_id": retained["candidate_id"],
    }


def _refresh_transfers(revised):
    previous = {row["id"]: row for row in revised["transfers"]}
    revised["transfers"] = [
        previous.get(stop, {"id": stop, "name": station["name"], "station_ids": [stop],
                            "walking_m": None, "basis": station["basis"]}) | {"lines": sorted(station["lines"])}
        for stop, station in sorted(revised["stations"].items()) if len(station["lines"]) > 1
    ]


def _restore_walk_links(revised, network, links):
    if links is None:
        return []
    accepted, dropped = [], []
    for link in links:
        first, second = link["station_ids"]
        stations = revised["stations"]
        if any(stations[stop]["coordinates"] != network["stations"][stop]["coordinates"]
               for stop in (first, second)):
            reason = "Orbital alignment relocated a linked platform"
        elif set(stations[first]["lines"]) & set(stations[second]["lines"]):
            reason = "Orbital alignment now serves both platforms on the same line"
        else:
            accepted.append(link)
            continue
        dropped.append({"id": link["id"], "reason": reason})
    revised["station_site_links"] = accepted
    return dropped


def _ring_polygon(line):
    track = network_model.Track(line["geometry"])
    polygon = Polygon(track.points)
    if not line["loop"] or polygon.is_empty or not polygon.is_valid or not polygon.exterior.is_simple:
        raise ValueError("A planning ring must close without intersecting itself")
    return polygon


def _nesting(revised, include_inner):
    outer = _ring_polygon(revised["lines"][OUTER])
    polygon = outer
    separation = None
    center_offset = None
    if include_inner:
        inner = _ring_polygon(revised["lines"][INNER])
        separation = outer.boundary.distance(inner.boundary)
        if not outer.contains(inner) or separation <= 0.:
            raise ValueError("The outer ring must enclose the inner ring without touching it")
        polygon = inner
        center_offset = outer.centroid.distance(inner.centroid)
    center = polygon.representative_point()
    basis = "Interior GIS point"
    if "Mansour" in revised["stations"]:
        preferred = Point(np.asarray(revised["stations"]["Mansour"]["coordinates"]) * network_model.LOCAL_METRES)
        if polygon.contains(preferred):
            center, basis = preferred, "Mansour mapped station"
    return {
        "common_enclosed_anchor": (np.asarray(center.coords[0]) / network_model.LOCAL_METRES).tolist(),
        "common_enclosed_anchor_basis": basis,
        "minimum_ring_separation_m": separation,
        "ring_polygon_centroid_separation_m": center_offset,
    }


def _single_parts(geometry):
    if geometry.is_empty:
        return
    if hasattr(geometry, "geoms"):
        for item in geometry.geoms:
            yield from _single_parts(item)
    else:
        yield geometry


def _outer_context(line, context):
    """Measure legacy trace overlap with retained roads and mapped water."""
    track = network_model.Track(line["geometry"])
    roads, bridges = _street_layers(context)
    x_scale, y_scale = network_model.LOCAL_METRES
    alignment = LineString(track.points)
    features = [scale(make_valid(shape(row["geometry"])), x_scale, y_scale, origin=(0, 0))
                for row in context["layers"]["water"]]
    contacts = alignment.intersection(unary_union(features))
    intervals = []
    for part in _single_parts(contacts):
        start, finish = sorted(alignment.project(Point(point)) for point in (part.coords[0], part.coords[-1]))
        intervals.append((start, finish))
    merged = []
    for start, finish in sorted(intervals):
        if merged and start <= merged[-1][1] + .05:
            merged[-1] = (merged[-1][0], max(merged[-1][1], finish))
        else:
            merged.append((start, finish))
    crossings = []
    for start, finish in merged:
        width = finish - start
        reach = np.linspace(start, finish, max(1, int(np.ceil(width / 30)) + 1))
        points = np.asarray([alignment.interpolate(distance).coords[0] for distance in reach])
        delta = (np.asarray(alignment.interpolate(min(track.km * 1000, finish + 10)).coords[0])
                 - np.asarray(alignment.interpolate(max(0., start - 10)).coords[0]))
        distances = bridges.nearby(points, delta / np.linalg.norm(delta), BRIDGE_OFFSET_M, 25)
        corroborated = bool(np.isfinite(distances).all())
        crossings.append({"entry_km": round(start / 1000, 3), "exit_km": round(finish / 1000, 3),
                          "mapped_wet_width_m": round(width, 1),
                          "tagged_road_bridge_aligned": corroborated,
                          "within_provisional_span_screen": width <= MAX_WATER_SPAN_M})
    samples = np.arange(25., track.km * 1000, 50.)
    road_share = None
    if roads.tree is not None and samples.size:
        points = [alignment.interpolate(distance).coords[0] for distance in samples]
        offsets, _ = roads.tree.query(points)
        road_share = float(np.mean(offsets <= ROAD_CORRIDOR_M))
    return {"mapped_water_crossings": crossings,
            "crossings_without_tagged_road_bridge_alignment": sum(
                not row["tagged_road_bridge_aligned"] for row in crossings),
            "crossings_above_provisional_span_limit": sum(
                not row["within_provisional_span_screen"] for row in crossings),
            "provisional_wet_width_limit_m": MAX_WATER_SPAN_M,
            "major_road_proximity_radius_m": ROAD_CORRIDOR_M,
            "length_share_near_mapped_major_roads": road_share}


def _interchanges(revised, code):
    line = revised["lines"][code]
    return [
        {"station_id": row["id"], "lines": sorted(row["lines"]),
         "chainage_km": line["station_chainage_km"][row["id"]],
         "coordinates": list(revised["stations"][row["id"]]["coordinates"])}
        for row in sorted((row for row in revised["transfers"] if code in row["lines"]),
                          key=lambda row: line["station_chainage_km"][row["id"]])
    ]


def _add_inner(network, graph, context):
    revised, evidence = add_inner_orbit(network, graph, context, southern_way=SOUTHERN_WAY)
    if INNER not in revised["lines"]:
        raise ValueError(f"M15 corridor screen failed: {evidence}")
    return revised, evidence


def inner_only(network, graph, context):
    """Add the mapped inner ring while retaining the current outer arc."""
    network_model.validate(network)
    alternative = deepcopy(network)
    links = alternative.pop("station_site_links", None)
    revised, inner = _add_inner(alternative, graph, context)
    evidence = {
        "status": "closed GIS planning corridor",
        "baseline_candidate_id": network["candidate_id"],
        "ring_ids": [INNER],
        "inner_road_screen": inner,
        "removed_walk_links": _restore_walk_links(revised, network, links),
        "route_km_added": revised["lines"][INNER]["one_way_km"],
        "rings": {INNER: {"one_way_km": revised["lines"][INNER]["one_way_km"],
                          "stations": len(revised["lines"][INNER]["station_ids"]),
                          "interchanges": _interchanges(revised, INNER)}},
    }
    source = Path(__file__)
    revised["source_sha256"][source.relative_to(network_model.ROOT).as_posix()] = network_model.digest(source)
    revised["ring_corridors"] = evidence
    revised["topology"] = network_model.validate(revised)
    return network_model._identity(revised), evidence


def evaluate_rings(network=None, graph=None, context=None, *, include_inner=True, retained=None):
    """Return a separate one- or two-ring planning layout and corridor evidence."""
    graph = network_model.walking_graph() if graph is None else graph
    context = network_model.read(network_model.INPUTS[-1]) if context is None else context
    if network is None:
        network = retained if retained is not None else network_model.evaluate(graph)
    network_model.validate(network)
    revised = deepcopy(network)
    if OUTER not in revised["lines"]:
        raise ValueError("The base layout needs a retained M09 corridor to compare restoring a ring")
    if include_inner is False and INNER in revised["lines"]:
        raise ValueError("The one-ring comparison requires a baseline without M15")
    if retained is None:
        retained = network if network["lines"][OUTER]["loop"] else network_model.evaluate(graph)
    links = revised.pop("station_site_links", None)
    outer = _close_outer(revised, retained)
    _refresh_transfers(revised)
    revised["topology"] = network_model.validate(revised)

    inner = None
    if include_inner and INNER not in revised["lines"]:
        # The M15 generator can relocate nearby single-line infill stations.
        # Retain every mapped pedestrian path whose endpoint still agrees.
        revised, inner = _add_inner(revised, graph, context)
    elif include_inner:
        inner = revised.get("inner_orbit")
    dropped_links = _restore_walk_links(revised, network, links)

    codes = [OUTER, INNER] if include_inner else [OUTER]
    for code in codes:
        if not _interchanges(revised, code):
            raise ValueError(f"{code} requires mapped passenger interchanges")
    evidence = {
        "status": "closed GIS planning corridors",
        "baseline_candidate_id": network["candidate_id"],
        "ring_ids": codes,
        "nesting": _nesting(revised, include_inner),
        "outer_restoration": outer,
        "outer_gis_context": _outer_context(revised["lines"][OUTER], context),
        "inner_road_screen": inner,
        "removed_walk_links": dropped_links,
        "route_km_added": sum(row["one_way_km"] for row in revised["lines"].values())
        - sum(row["one_way_km"] for row in network["lines"].values()),
        "rings": {code: {"one_way_km": revised["lines"][code]["one_way_km"],
                         "stations": len(revised["lines"][code]["station_ids"]),
                         "interchanges": _interchanges(revised, code)} for code in codes},
        "open_engineering": ["Outer ring water and bridge alignment survey",
                             "Horizontal curves, vertical grades and land take",
                             "Platform fit and accessible transfer paths",
                             "Train working, capacity, depot, civil and whole-life cost"],
    }
    if include_inner:
        served = [{line for row in evidence["rings"][code]["interchanges"] for line in row["lines"]}
                  for code in codes]
        evidence["direct_spokes_between_rings"] = sorted((served[0] & served[1]) - set(codes))
    source = Path(__file__)
    revised.setdefault("source_sha256", {})[source.relative_to(network_model.ROOT).as_posix()] = network_model.digest(source)
    revised["ring_corridors"] = evidence
    revised["physical_accepted"] = False
    revised["operating_timetable_validated"] = False
    revised["topology"] = network_model.validate(revised)
    return network_model._identity(revised), evidence
