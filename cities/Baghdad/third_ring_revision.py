"""Bounded redesign of Baghdad's three orbital traces and direct ring interchanges."""

from collections import Counter
from copy import deepcopy
from itertools import pairwise
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree
from shapely import distance, points as geometry_points
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import linemerge, nearest_points, substring

from . import holistic_network as network
from . import holistic_orbitals as orbital
from . import holistic_through as through
from . import residential_layouts
from . import ring_corridors as rings
from . import third_ring_geometry as geometry

MIDDLE = rings.OUTER
INNER = rings.INNER
OUTER = geometry.LINE_ID
INTERCHANGES = (("Karkh", INNER, MIDDLE), ("Rusafa", MIDDLE, OUTER))
OUTER_OFFSET_M = 2500
OUTER_ASSIST_WINDOW_M = 1500
MIDDLE_ASSIST_WINDOW_M = 1000
OUTER_ASSIST_SEAM_FRACTION = .25
MIDDLE_TARGET_GAP_M = 2500
INNER_FOLDBACK_SMOOTH_M = 400
SAMPLE_M = 50
NONLOCAL_ARC_M = 1500
INNER_SELF_CLEARANCE_M = 850


def _sample(line, step):
    chainages = np.arange(0., line.length, step)
    return chainages, np.asarray([line.interpolate(km).coords[0] for km in chainages])


def _bank(point, river):
    nearest = nearest_points(river, point)[0]
    part = min(river.geoms, key=lambda line: line.distance(nearest)) if river.geom_type == "MultiLineString" else river
    chainage = part.project(nearest)
    a = part.interpolate(max(0, chainage - 50))
    b = part.interpolate(min(part.length, chainage + 50))
    if a.y > b.y:
        a, b = b, a
    return "Karkh" if (b.x - a.x) * (point.y - a.y) - (b.y - a.y) * (point.x - a.x) > 0 else "Rusafa"


def _inner_polygon(retained, smooth_m, river):
    if not smooth_m:
        return retained
    closed = retained.buffer(smooth_m, quad_segs=8).buffer(-smooth_m, quad_segs=8).simplify(75)
    added = closed.difference(retained)
    pieces = added.geoms if hasattr(added, "geoms") else [added]
    revised = retained
    for part in pieces:
        if part.area > 2000 and river.distance(part) > 150:
            # Fill landward re-entrants. The overlap joins sub-metre GIS slivers.
            revised = revised.union(part.buffer(.1))
    return revised


def _self_adjacency(boundary):
    chainages, xy = _sample(boundary, SAMPLE_M)
    close = cKDTree(xy).query_pairs(INNER_SELF_CLEARANCE_M, output_type="ndarray")
    gaps = np.diff(chainages[close], axis=1).ravel()
    close = close[(gaps >= NONLOCAL_ARC_M) & (gaps <= boundary.length - NONLOCAL_ARC_M)]
    return {"sample_m": SAMPLE_M, "nonlocal_arc_minimum_m": NONLOCAL_ARC_M,
            "clearance_test_m": INNER_SELF_CLEARANCE_M, "close_sample_pairs": len(close),
            "near_reach_m": len(np.unique(close)) * SAMPLE_M}


def _local_approach(boundary, target, half_width, *, rounded=False):
    cut = boundary.project(target)
    if not half_width < cut < boundary.length - half_width:
        return None
    lo, hi = cut - half_width, cut + half_width
    below, above = substring(boundary, 0, lo), substring(boundary, hi, boundary.length)
    a, b = np.asarray(below.coords[-1]), np.asarray(above.coords[0])
    middle = np.asarray(target.coords[0])
    if rounded:
        # Two quadratic approaches share the contact with an approximate parallel tangent.
        tangent = (b - a) / np.linalg.norm(b - a)
        shoulders = (middle - tangent * half_width * .48, middle + tangent * half_width * .48)
        sample = np.arange(0., 1.01, .2)[:, None]
        lead = (1 - sample)**2 * a + 2 * sample * (1 - sample) * shoulders[0] + sample**2 * middle
        tail = (1 - sample)**2 * middle + 2 * sample * (1 - sample) * shoulders[1] + sample**2 * b
        vertices = [*below.coords, *lead[1:-1], middle, *tail[1:-1], *above.coords]
    else:
        vertices = [*below.coords, middle, *above.coords]
    return Polygon(vertices)


def _spacing(boundary, outer):
    _, xy = _sample(boundary, SAMPLE_M)
    gaps = distance(geometry_points(xy), outer.exterior)
    return {f"p{percentile}_m": round(float(np.percentile(gaps, percentile)), 1)
            for percentile in (0, 10, 25, 50, 75, 90, 100)} | {
                "sample_m": SAMPLE_M,
                "midway_target_band_share": float((abs(gaps - MIDDLE_TARGET_GAP_M) <= 500).mean()),
            }


def _touch(middle, inner, outer, river, water, graph, *, bank, touch_inside, access_targets):
    fixed = inner if touch_inside else outer
    xy = np.asarray(fixed.exterior.coords[:-1])
    offsets, _ = graph[3].query(xy)
    candidates = []
    for x, offset in zip(xy, offsets, strict=True):
        site = Point(x)
        if offset > network.TRANSFER_SNAP_M or river.distance(site) < 700 or water.distance(site) < 120:
            continue
        if _bank(site, river) != bank:
            continue
        gap = middle.exterior.distance(site)
        if gap < 4800:
            candidates.append((gap + .8 * offset, site))
    rejected = Counter()
    accepted = []
    fixed_water_m = LineString(middle.exterior).intersection(water).length
    for score, site in sorted(candidates, key=lambda row: row[0])[:55]:
        for width in (450, 800, 1200, 1750, 2500, 3250):
            for rounded in (True, False):
                revised = _local_approach(middle.exterior, site, width, rounded=rounded)
                if revised is None or not revised.is_valid:
                    rejected["invalid local footprint"] += 1
                    continue
                if not outer.covers(revised) or not revised.covers(inner):
                    rejected["crossing a neighbouring ring"] += 1
                    continue
                if not revised.exterior.intersection(fixed.exterior).equals(site):
                    rejected["contact is not exactly one point"] += 1
                    continue
                if any(revised.exterior.distance(target) > .001 for target in access_targets):
                    rejected["former short-route access target moved"] += 1
                    continue
                added_water = LineString(revised.exterior).intersection(water).length - fixed_water_m
                if added_water > 50:
                    rejected["additional wet approach"] += 1
                    continue
                accepted.append((score + 0.3 * abs(revised.length - middle.length) + (0 if rounded else 500),
                                 revised, site, width, rounded))
    tested = sum(rejected.values()) + len(accepted)
    if not accepted:
        raise ValueError(f"No validated {bank} ring interchange in {tested} local approach trials: {dict(rejected)}")
    _, revised, site, width, rounded = min(accepted, key=lambda row: row[0])
    return revised, site, {"bank": bank, "approach_half_width_m": width, "rounded_approach": rounded,
                           "evaluated_approaches": tested, "eligible_approaches": len(accepted),
                           "rejected_approaches": dict(rejected), "base_gap_m": middle.exterior.distance(site)}


def _catchment_detours(middle, inner, outer, reference, graph, water, *, maximum_detours):
    stations = reference["stations"]
    short_stops = sorted({stop for code, line in reference["lines"].items()
                          if code != "C1" and not line["loop"] and line["one_way_km"] <= 8.
                          for stop in line["station_ids"]})
    targets = geometry_points(np.asarray([stations[stop]["coordinates"] for stop in short_stops])
                              * network.LOCAL_METRES)
    initial = distance(targets, middle.exterior)
    selected = []
    for _ in range(maximum_detours):
        current = distance(targets, middle.exterior)
        candidates = []
        for index in np.flatnonzero((current > 180) & (current < 1900)):
            site = targets[index]
            street_offset, _ = graph[3].query(site.coords[0])
            if (street_offset > network.TRANSFER_SNAP_M or water.distance(site) < 150
                    or outer.exterior.distance(site) < 950 or inner.exterior.distance(site) < 500
                    or not outer.contains(site) or inner.covers(site)):
                continue
            trial = _local_approach(middle.exterior, site, 1750, rounded=True)
            if (trial is None or not trial.is_valid or not outer.contains_properly(trial)
                    or not trial.contains_properly(inner)
                    or LineString(trial.exterior).intersection(water).length - LineString(middle.exterior).intersection(water).length > 50):
                continue
            residual = distance(targets, trial.exterior)
            score = (np.minimum(current, 1300) - np.minimum(residual, 1300)).sum()
            past_sites = [Point(np.asarray(row["coordinates"]) * network.LOCAL_METRES) for row in selected]
            if score > 250 and all(trial.exterior.distance(previous) < .001 for previous in past_sites):
                candidates.append((float(score), index, trial))
        if not candidates:
            break
        gain, index, middle = max(candidates, key=lambda row: (row[0], -row[1]))
        selected.append({"former_station_id": short_stops[index], "coordinates": list(stations[short_stops[index]]["coordinates"]),
                         "before_m": round(float(current[index]), 1),
                         "street_offset_m": round(float(graph[3].query(targets[index].coords[0])[0]), 1),
                         "aggregate_access_proxy_gain_m": round(gain, 1)})
    return middle, selected, short_stops, initial, targets


def _rotate(boundary, origin):
    at = boundary.project(origin)
    if at < 1e-6 or boundary.length - at < 1e-6:
        return boundary
    parts = substring(boundary, at, boundary.length), substring(boundary, 0, at)
    points = network._concatenate(*(part.coords for part in parts))
    return LineString(points)


def _add_platform(record, code, stop, km, point, name):
    stations = record["stations"]
    if stop not in stations:
        stations[stop] = {"name": name, "coordinates": list(point), "lines": [],
                          "basis": "Provisional orbital platform with dry mapped street access"}
    network._add(record["lines"][code], stop, km)
    stations[stop]["lines"] = sorted({*stations[stop]["lines"], code})


def _rebuild_record(reference, polygons, touch_sites, access_sites, graph, context):
    record = deepcopy(reference)
    lines, stations = record["lines"], record["stations"]
    old_ids = {INNER, MIDDLE, OUTER}
    retained = {
        stop for code, line in lines.items() if code not in old_ids for stop in line["station_ids"]
    }
    for stop in tuple(stations):
        if stop not in retained:
            del stations[stop]
        else:
            stations[stop]["lines"] = sorted(set(stations[stop]["lines"]) - old_ids)
    for code in old_ids:
        lines.pop(code, None)
    names = {INNER: "Baghdad central orbital", MIDDLE: "Baghdad suburban orbital",
             OUTER: "Baghdad outer orbital"}
    rotation = {}
    for code in (INNER, MIDDLE, OUTER):
        site = next(row for row in touch_sites if code in row["line_ids"])
        boundary = _rotate(polygons[code].exterior, site["point"])
        track = rotation[code] = network.Track(np.asarray(boundary.coords) / network.LOCAL_METRES)
        lines[code] = {"name": names[code], "geometry": track.coordinates.tolist(), "loop": True,
                       "one_way_km": track.km, "source_sections": [],
                       "basis": "Three orbital GIS redesign with explicit direct transfer approaches",
                       "station_ids": [], "station_chainage_km": {}}
    for site in touch_sites:
        codes = site["line_ids"]
        point = (np.asarray(site["point"].coords[0]) / network.LOCAL_METRES).tolist()
        for code in codes:
            track = rotation[code]
            km, offset, _ = track.locate(point)
            if min(km, track.km - km) < 1e-10:
                km = 0.
            if offset > 1e-6:
                raise ValueError(f"Exact {site['bank']} transfer misses {code} by {offset:.6f} m")
            _add_platform(record, code, site["station_id"], km, point, f"{site['bank']} orbital interchange")
    for code, track in rotation.items():
        if code == MIDDLE:
            for site in access_sites:
                point = site["coordinates"]
                km, offset, _ = track.locate(point)
                existing = network._stations_at_crossing(stations, point)
                if len(existing) == 1 and existing[0] in lines[code]["station_ids"]:
                    site["candidate_station_id"] = existing[0]
                elif offset <= .001 and network._terminal_margin(lines[code], km) >= network.INTERCHANGE_SPACING_M:
                    stop = existing[0] if len(existing) == 1 else f"{code}-catchment-{site['former_station_id']}"
                    _add_platform(record, code, stop, km, point, "Suburban orbital · former short-route catchment")
                    site["candidate_station_id"] = stop
        candidates = [(other, point, kms) for other in sorted(lines.keys() - old_ids)
                      for point, kms in network._crossings(track, network.Track(lines[other]["geometry"])).items()]
        points = np.asarray([row[1] for row in candidates]).reshape(-1, 2)
        offsets, _ = graph[3].query(points * network.LOCAL_METRES)
        dry = network.dry_points(points, context)
        for index in sorted(np.flatnonzero(dry & (offsets <= network.TRANSFER_SNAP_M)),
                            key=lambda i: (offsets[i], candidates[i])):
            other, point, kms = candidates[index]
            try:
                stop = network._through_interchange(code, {"line_id": other}, (point, kms), lines, stations,
                                                    require_intermediate=False)
            except ValueError:
                continue
            stations[stop]["street_offset_m"] = round(float(offsets[index]), 1)
        line = lines[code]
        fixed = [*sorted(line["station_chainage_km"].values()), track.km]
        available = np.arange(.1, track.km, .1)
        points = np.asarray([track.at(km) for km in available])
        offsets, _ = graph[3].query(points * network.LOCAL_METRES)
        available = available[network.dry_points(points, context) & (offsets <= network.TRANSFER_SNAP_M)]
        for low, high in pairwise(fixed):
            last = low
            for target in np.linspace(low, high, max(1, round((high - low) / 1.6)) + 1)[1:-1]:
                eligible = available[(available - last >= orbital.MIN_STOP_GAP_KM)
                                     & (high - available >= orbital.MIN_STOP_GAP_KM)]
                if not len(eligible):
                    continue
                km = float(eligible[np.argmin(abs(eligible - target))])
                if abs(km - target) <= .65:
                    _add_platform(record, code, f"{code}-revised-{round(km * 1000):05d}", km, track.at(km),
                                  f"{names[code]} · km {km:.1f}")
                    last = km
    links = [row for row in reference.get("station_site_links", []) if set(row["station_ids"]) <= stations.keys()]
    dropped = rings._restore_walk_links(record, reference, links)
    dropped.extend({"id": row["id"], "reason": "Orbital geometry retired a linked platform"}
                   for row in reference.get("station_site_links", []) if row not in links)
    rings._refresh_transfers(record)
    residential_layouts._rebuild_memberships(record)
    return record, dropped


def _assisted_polygon(guide, exclusion, roads, *, window, seam_fraction=0.):
    line = LineString(guide.exterior)
    if seam_fraction:
        line = _rotate(line, line.interpolate(seam_fraction, normalized=True))
    trace = geometry._road_assisted(line, exclusion, roads, guide_window_m=window)
    if trace is None or not trace.is_ring:
        raise ValueError("Mapped-road alignment did not yield one simple closed orbital")
    return Polygon(trace)


def revise_orbitals(reference, graph, context, *, outer_offset_m=OUTER_OFFSET_M,
                    inner_smooth_m=INNER_FOLDBACK_SMOOTH_M, maximum_access_detours=3,
                    road_assisted=False, streets=None):
    """Return a GIS trial, using separately registered ring/contact and access screens."""
    network.validate(reference)
    base_outer = rings._ring_polygon(reference["lines"][MIDDLE])
    base_inner = rings._ring_polygon(reference["lines"][INNER])
    if not (outer_offset_m > 0 and inner_smooth_m >= 0 and maximum_access_detours >= 0):
        raise ValueError("Orbital offsets, re-entrant smoothing and detour count must be in their geometric domains")
    streets = network.read(network.STREETS) if streets is None else streets
    outer = base_outer.buffer(outer_offset_m, quad_segs=8).simplify(25)
    if road_assisted:
        road_paths, _ = geometry._roads(streets, base_outer.buffer(outer_offset_m + OUTER_ASSIST_WINDOW_M + 800))
        outer = _assisted_polygon(outer, base_outer, road_paths, window=OUTER_ASSIST_WINDOW_M,
                                  seam_fraction=OUTER_ASSIST_SEAM_FRACTION)
    middle = outer.buffer(-MIDDLE_TARGET_GAP_M, quad_segs=8).simplify(65)
    tigris = geometry._tigris(context)
    river = linemerge(tigris) if tigris.geom_type == "MultiLineString" else tigris
    water = geometry.spaced._water(context)
    inner = _inner_polygon(base_inner, inner_smooth_m, river).segmentize(75)
    if middle.geom_type != "Polygon":
        raise ValueError("The target middle offset did not yield one suburban orbital")
    if road_assisted:
        middle = _assisted_polygon(middle, inner, road_paths, window=MIDDLE_ASSIST_WINDOW_M)
    outer = outer.segmentize(75)
    if not (inner.is_valid and middle.contains_properly(inner) and outer.contains_properly(middle)):
        raise ValueError("The revised central, suburban and outer traces require valid nested polygons")
    middle, detours, short_stops, initial, targets = _catchment_detours(
        middle, inner, outer, reference, graph, water, maximum_detours=maximum_access_detours)
    touch_sites = []
    access_targets = [Point(np.asarray(row["coordinates"]) * network.LOCAL_METRES) for row in detours]
    for bank, first, second in INTERCHANGES:
        middle, point, approach = _touch(middle, inner, outer, river, water, graph,
                                          bank=bank, touch_inside=first == INNER, access_targets=access_targets)
        touch_sites.append(approach | {"point": point, "station_id": f"X-RING-{bank.upper()}",
                                       "line_ids": [first, second],
                                       "street_offset_m": round(float(graph[3].query(point.coords[0])[0]), 1)})
    if any(not middle.exterior.intersection(fixed.exterior).equals(site["point"])
           for site, fixed in zip(touch_sites, (inner, outer), strict=True)):
        raise ValueError("A local approach changed a previously screened exact ring contact")
    polygons = {INNER: inner, MIDDLE: middle, OUTER: outer}
    revised, dropped = _rebuild_record(reference, polygons, touch_sites, detours, graph, context)
    revised["topology"] = network.validate(revised)
    road_paths, bridge_paths = geometry._roads(streets, outer)
    roads = through.DirectionalRoads.from_paths(road_paths)
    bridges = through.DirectionalRoads.from_paths(bridge_paths)
    current = distance(targets, middle.exterior)
    screens = {code: {"one_way_km": polygon.length / 1000,
                      "major_road_support_share": geometry._road_support(polygon.exterior, roads),
                      "mapped_water_crossings": geometry._water_crossings(LineString(polygon.exterior), water, tigris, bridges)}
               for code, polygon in polygons.items()}
    for row in touch_sites:
        row["coordinates"] = (np.asarray(row.pop("point").coords[0]) / network.LOCAL_METRES).tolist()
    evidence = {
        "reference_candidate_id": reference["candidate_id"], "reference_evaluation_id": reference["evaluation_id"],
        "outer_offset_m": outer_offset_m, "middle_target_gap_m": MIDDLE_TARGET_GAP_M,
        "road_guide": {"outer_window_m": OUTER_ASSIST_WINDOW_M, "middle_window_m": MIDDLE_ASSIST_WINDOW_M,
                       "outer_seam_fraction": OUTER_ASSIST_SEAM_FRACTION} if road_assisted else None,
        "middle_outer_gap": _spacing(middle.exterior, outer), "ring_transfers": touch_sites,
        "inner_foldback_smoothing_m": inner_smooth_m, "inner_self_adjacency": _self_adjacency(inner.exterior),
        "retained_inner_self_adjacency": _self_adjacency(base_inner.exterior), "alignments": screens,
        "former_short_stop_proximity": {"sample_count": len(short_stops),
                                        "median_before_m": round(float(np.median(initial)), 1),
                                        "median_after_m": round(float(np.median(current)), 1),
                                        "within_400m_before": int((initial <= 400).sum()),
                                        "within_400m_after": int((current <= 400).sum()),
                                        "detours": detours},
        "dropped_walking_links": dropped, "tunnels": 0,
        "limits": ["Local plan geometry and Euclidean former-stop proxy",
                   "Independent platform structure, vertical geometry, accessible links and walks require survey",
                   "Check railway curve radii, continuous elevated construction and bridge hydraulics",
                   "Provisional wet contacts and off-street segments require separate quantities and costs"],
    }
    revised["orbital_revision"] = evidence
    revised["parent_candidate_id"] = reference["candidate_id"]
    revised["physical_accepted"] = revised["operating_timetable_validated"] = False
    for source in (Path(__file__), Path(geometry.__file__), network.STREETS, network.INPUTS[-1]):
        revised.setdefault("source_sha256", {})[source.relative_to(network.ROOT).as_posix()] = network.digest(source)
    return network._identity(revised), evidence
