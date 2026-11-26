"""Compare a short-line-free suburban orbital with Baghdad's published service."""

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from math import isclose
from itertools import pairwise
from pathlib import Path
import tomllib

import numpy as np
from scipy.spatial import cKDTree
from shapely import contains_xy, distance, line_interpolate_point
from shapely.geometry import LineString, Point, Polygon

from . import (central_access, holistic_access, holistic_network, holistic_pathways, ring_corridors,
               residential_layouts, residential_planning, residential_systems, ring_grid_comparison, ring_grid_journeys,
               straight_network_study)
from .third_ring_revision import MIDDLE_TARGET_GAP_M


CITY = straight_network_study.CITY
REFERENCE = straight_network_study.RECORD
RINGS = ("M15", "M09", "M16")
SHORT_KM = 8.
WALK_M = 1300.
NEW_AXIS_MAX_DETOUR = 1.10


def _rings(network):
    polygons = {code: Polygon(holistic_network.Track(line["geometry"]).points)
                for code, line in network["lines"].items() if line["loop"]}
    return dict(sorted(polygons.items(), key=lambda entry: (entry[1].area, entry[0])))


def _ring_contacts(network, inner, outer, polygons):
    """Allow point contacts at a common station. Other contacts fail the layout."""
    boundary = polygons[inner].boundary.intersection(polygons[outer].boundary)
    if boundary.is_empty:
        return []
    if boundary.geom_type not in {"Point", "MultiPoint"}:
        raise ValueError(f"{inner} and {outer} share guideway at their contact")
    shared = set(network["lines"][inner]["station_ids"]) & set(network["lines"][outer]["station_ids"])
    sites = {site: Point(np.asarray(network["stations"][site]["coordinates"]) * holistic_network.LOCAL_METRES)
             for site in sorted(shared)}
    result = set()
    for point in boundary.geoms if boundary.geom_type == "MultiPoint" else (boundary,):
        matches = [site for site, location in sites.items() if location.distance(point) <= 1.]
        if len(matches) != 1:
            raise ValueError(f"{inner} and {outer} touch away from an exact shared station")
        result.update(matches)
    return sorted(result)


def _orbital_metrics(network, context):
    from .straight_through_layout import _tigris

    polygons = _rings(network)
    if RINGS[0] not in polygons:
        return {"inner_foldback_km": None}
    inner = polygons[RINGS[0]].boundary
    count = max(1, round(inner.length / 50))
    step = inner.length / count
    samples = line_interpolate_point(inner, np.arange(count) * step)
    positions = [(point.x, point.y) for point in samples]
    close_reaches = set()
    for first, second in cKDTree(positions).query_pairs(850):
        if min(second - first, count - second + first) * step >= 1500:
            close_reaches.update((first, second))
    metrics = {"inner_foldback_km": round(len(close_reaches) * step / 1000, 3)}
    if not set(RINGS) <= polygons.keys():
        return metrics
    middle, outer = (polygons[code].boundary for code in RINGS[1:])
    gaps = distance(line_interpolate_point(middle, np.arange(25., middle.length, 50.)), outer)
    metrics["middle_outer_gap_km"] = dict(zip(("p10", "median", "p90"), np.round(
        np.quantile(gaps, [.1, .5, .9]) / 1000, 3).tolist(), strict=True))
    contacts, river = [], _tigris(context)
    for first, second in pairwise(RINGS):
        for site in _ring_contacts(network, first, second, polygons):
            point = np.asarray(network["stations"][site]["coordinates"]) * holistic_network.LOCAL_METRES
            hits = {side: river.intersections(point, point + [side * 25_000, 0])[1] for side in (-1, 1)}
            offsets = [(float(fraction), side) for side, fractions in hits.items() for fraction in fractions]
            bank = {1: "Karkh", -1: "Rusafa"}[min(offsets)[1]] if offsets else "unresolved"
            contacts.append({"station_id": site, "bank": bank, "rings": [first, second]})
    metrics["inter_ring_contacts"] = contacts
    return metrics


def validate_layout(network, reference=None):
    """Check connected service and, for paired controls, unchanged parent alignments."""
    if holistic_network.validate(network) != network["topology"]:
        raise ValueError("Passenger topology does not reconcile")
    polygons = _rings(network)
    if reference is not None and tuple(polygons) != RINGS:
        raise ValueError("A three-ring control must supply all three alignments")
    for code, polygon in polygons.items():
        if not network["lines"][code]["loop"] or not polygon.is_valid or polygon.is_empty:
            raise ValueError(f"{code} is not a simple, closed orbital")
    ids = tuple(polygons)
    for inner, outer in zip(ids, ids[1:]):
        if not polygons[outer].covers(polygons[inner]):
            raise ValueError(f"{outer} must enclose {inner} without crossing it")
        _ring_contacts(network, inner, outer, polygons)
    if reference is not None:
        for code in (*RINGS[:2], "C1"):
            if network["lines"][code]["geometry"] != reference["lines"][code]["geometry"]:
                raise ValueError(f"{code} changed in a paired control that isolates the added orbital")
    return polygons


def _cross_ring_stations(network, code, polygons):
    track = holistic_network.Track(network["lines"][code]["geometry"])
    alignment = LineString(track.points)
    route_calls = set(network["lines"][code]["station_ids"])
    shares = {}
    for ring, polygon in polygons.items():
        hits = []
        for station in sorted(set(network["lines"][ring]["station_ids"]) & route_calls):
            lonlat = network["stations"][station]["coordinates"]
            location = Point(np.asarray(lonlat) * holistic_network.LOCAL_METRES)
            if alignment.distance(location) > 25 or polygon.boundary.distance(location) > 25:
                continue
            distance = alignment.project(location)
            before = alignment.interpolate(max(0., distance - 50.))
            after = alignment.interpolate(min(track.km * 1000, distance + 50.))
            if polygon.contains(before) != polygon.contains(after):
                hits.append(station)
        shares[ring] = hits
    return shares


def classify_through(network, context, *, middle_access_only=False):
    """Count straight cross-river trunks and verify their ring interchanges."""
    from .straight_through_layout import _tigris

    river = _tigris(context)
    polygons = _rings(network)
    beyond = polygons[next(reversed(polygons))] if polygons else None
    results = {}
    for code, line in network["lines"].items():
        if line["loop"] or code == "C1" or line["one_way_km"] <= SHORT_KM:
            continue
        track = holistic_network.Track(line["geometry"])
        chord = float(np.linalg.norm(track.points[-1] - track.points[0]))
        detour = track.km * 1000 / chord if chord else float("inf")
        if detour > NEW_AXIS_MAX_DETOUR or (not middle_access_only and beyond is not None and any(
                beyond.covers(Point(track.points[i])) for i in (0, -1))):
            continue
        shares = _cross_ring_stations(network, code, polygons)
        tigris = sum(bool(len(river.intersections(a, b)[1])) for a, b in zip(track.points, track.points[1:]))
        required = ("M15", "M09") if middle_access_only else shares
        if all(shares.get(code) for code in required) and tigris:
            results[code] = {"route_km": track.km, "detour_ratio": round(detour, 4), "ring_crossing_stations": shares,
                             "crosses_tigris_centreline": True}
    return results


def short_lines(network):
    return sorted(code for code, line in network["lines"].items()
                  if not line["loop"] and code != "C1" and line["one_way_km"] <= SHORT_KM)


def import_layout(path, reference):
    """Read a complete edited GeoJSON route set. Omitted lines are withdrawn."""
    data = central_access.read(path)
    if data.get("type") != "FeatureCollection":
        raise ValueError("A complete GeoJSON FeatureCollection is required")
    source = reference["lines"]
    lines, stations, paths = {}, {}, {}
    for feature in data["features"]:
        props, geometry = feature["properties"], feature["geometry"]
        coords = geometry["coordinates"]
        if props["kind"] in {"station", "interchange"}:
            code = props["station_id"]
            if code in stations or geometry["type"] != "Point":
                raise ValueError(f"Provide one mapped Point for station {code}")
            stations[code] = {"name": props.get("name", code), "coordinates": coords, "lines": [],
                              "basis": "User-supplied planning station coordinate"}
        elif props["kind"] == "line":
            code = props["line_id"]
            if code in paths or geometry["type"] != "LineString" or type(props.get("loop")) is not bool:
                raise ValueError(f"Provide one mapped LineString with a loop flag for {code}")
            paths[code] = (coords, props["station_ids"], props["loop"], props.get("name", code))
    if not paths:
        raise ValueError("An edited network needs at least one route")
    for code, (coords, calls, loop, name) in sorted(paths.items()):
        if len(calls) < 2 or len(set(calls)) != len(calls) or set(calls) - stations.keys():
            raise ValueError(f"Provide at least two distinct mapped station calls on {code}")
        raw = np.asarray([*coords, *(stations[stop]["coordinates"] for stop in calls)], dtype=float)
        if raw.ndim != 2 or raw.shape[1] != 2 or not np.isfinite(raw).all() or (
                abs(raw[:, 0]) > 180).any() or (abs(raw[:, 1]) > 90).any():
            raise ValueError(f"{code} must use finite longitude/latitude coordinates")
        line = holistic_network._physical_line(coords, calls, stations, [], "Edited GeoJSON alignment", loop=loop)
        for stop in calls:
            stations[stop]["lines"].append(code)
        lines[code] = line | {"name": name}
    stations = {key: station for key, station in stations.items() if station["lines"]}
    record = {"lines": lines, "stations": stations, "transfers": [], "physical_accepted": False,
              "operating_timetable_validated": False, "parent_candidate_id": reference["candidate_id"],
              "edited_geojson_sha256": central_access.digest(path)}
    inherited = [link for link in reference.get("station_site_links", [])
                 if set(link["station_ids"]) <= stations.keys()]
    ring_corridors._restore_walk_links(record, reference, inherited)
    ring_corridors._refresh_transfers(record)
    record["topology"] = holistic_network.validate(record)
    revised = holistic_network._identity(record)
    changes = {"removed": sorted(source.keys() - lines.keys()), "added": sorted(lines.keys() - source.keys()),
               "compared_to_published": reference["candidate_id"], "geojson_sha256": revised["edited_geojson_sha256"]}
    changes["changed"] = [code for code in sorted(source.keys() & lines.keys()) if any(
        source[code][field] != paths[code][index]
        for index, field in enumerate(("geometry", "station_ids", "loop")))]
    return revised, changes


def _airport_walk(net, reference, graph):
    coordinates = reference["stations"]["Airport-00"]["coordinates"]
    sites = {code: row["coordinates"] for code, row in net["stations"].items()}
    distances, _ = central_access.distances_from_stops(sites, graph)
    offset, index = graph[3].query(central_access._points([coordinates])[0])
    distance = distances[graph[2][index]] + offset
    return round(float(distance), 1) if offset <= central_access.SNAP_M and np.isfinite(distance) else None


def _equal_scope_cost(network, context, policy):
    beam, civil, cost = straight_network_study._selected_resources(network, context, policy)
    quantities, programme, service = civil["quantities"], civil["programme"], cost["service"]
    return {"candidate_id": network["candidate_id"], "running_track_km": quantities["double_track_km"],
            "distinct_guideway_km": quantities["unique_guideway_km"], "fleet_trainsets": service["fleet_trainsets"],
            "standard_stock_paid_hours": civil["workforce"]["paid_deck_and_casting_hours"],
            "standard_stock_last_deck_day": programme["last_standard_deck_day"],
            "yard_sites": programme["concurrent_yard_sites"], "curved_pieces": sum(
                row["girders"] for family, row in beam["by_family"].items() if "curved_ugirder" in family),
            "beam_evaluation_id": beam["evaluation_id"], "civil_evaluation_id": civil["evaluation_id"],
            "cost_cases": cost["cost_cases"], "annual_grid_gwh": cost["power"]["annual_grid_gwh"],
            "held_service_route_km": beam["totals"]["held_route_length_m"] / 1000,
            "full_completion_day": beam["totals"]["integrated_completion_day"],
            "source_sha256": civil["source_sha256"]}


def _compare_access(networks, graph, population, baseline):
    stations = {key: {stop: row["coordinates"] for stop, row in net["stations"].items()}
                for key, net in networks.items()}
    walks = {key: holistic_access.walk_to_station(sites, graph, population)[0] for key, sites in stations.items()}
    inner, outer = (_rings(networks[baseline])[key] for key in RINGS[:2])
    x, y = (population.coordinates * holistic_network.LOCAL_METRES).T
    outside = ~contains_xy(outer, x, y)
    centre = contains_xy(inner, x, y)
    sectors = {"inside_inner_ring": centre, "between_existing_rings": ~(centre | outside), "outside_existing_outer_ring": outside}
    short = set(short_lines(networks[baseline]))
    regular_sites = {site: coords for site, coords in stations[baseline].items()
                     if set(networks[baseline]["stations"][site]["lines"]) - short}
    regular_walk = holistic_access.walk_to_station(regular_sites, graph, population)[0]
    total = population.counts.sum()
    result = {}
    for key, distances in walks.items():
        row = {}
        middle = networks[key]["lines"].get("M09")
        middle_only = (set(middle["station_ids"]) - {
            stop for stop, station in networks[key]["stations"].items() if len(station["lines"]) > 1
        }) if middle and "M16" in networks[key]["lines"] else set()
        remainder = {site: coords for site, coords in stations[key].items() if site not in middle_only}
        remainder_walk = (holistic_access.walk_to_station(remainder, graph, population)[0]
                          if middle_only else distances)
        for limit in (1200, 1300):
            present, old = distances <= limit, walks[baseline] <= limit
            served = population.counts[present].sum()
            gain = population.counts[present & ~old].sum()
            loss = population.counts[old & ~present].sum()
            row[str(limit)] = {"access_pct": round(float(served / total * 100), 4),
                               "access_people": round(float(served)),
                               "newly_served_people": round(float(gain)),
                               "formerly_served_people_losing_access": round(float(loss)),
                               "lost_pct": round(float(loss / total * 100), 4)}
            row[str(limit)]["district_access_pct"] = {name: round(float(population.counts[present & mask].sum()
                                                                        / population.counts[mask].sum() * 100), 4)
                                                       for name, mask in sectors.items() if mask.any()}
            short_only = old & (regular_walk > limit)
            row[str(limit)]["short_route_catchments"] = {
                "baseline_short_only_people": round(float(population.counts[short_only].sum())),
                "retained_access_people": round(float(population.counts[short_only & present].sum())),
                "served_by_middle_only_sites_people": round(float(
                    population.counts[short_only & present & (remainder_walk > limit)].sum())),
                "largest_unserved_cells": residential_layouts._loss_locations(
                    population, short_only & ~present & (population.counts > 0)),
            }
        result[key] = row
    return result


def _decision(summary, available, policy):
    reference = summary["published"]
    assessments = {}
    for code in available:
        option = summary[code]
        reasons = []
        if not all(ring in option["rings"] for ring in RINGS):
            reasons.append("This comparison retains two rings")
        else:
            geometry = option["orbital_metrics"]
            if sorted(row["bank"] for row in geometry["inter_ring_contacts"]) != ["Karkh", "Rusafa"]:
                reasons.append("The rings need exactly one shared contact on each bank")
            if abs(geometry["middle_outer_gap_km"]["median"] * 1000 - MIDDLE_TARGET_GAP_M) > 750:
                reasons.append("The median middle-to-outer gap is outside the planning band around 2.5 km")
            if geometry["inner_foldback_km"] > reference["orbital_metrics"]["inner_foldback_km"]:
                reasons.append("The inner ring adds close non-adjacent reaches")
        if option["short_count"]:
            reasons.append("A short standalone route remains")
        if option["airport_walk_m"] is None or option["airport_walk_m"] > WALK_M:
            reasons.append("The Airport terminal lacks a replacement station within the street catchment")
        if option["middle_ring_through_count"] < 2:
            reasons.append("Fewer than two near-straight cross-Tigris trunks connect the suburban and inner rings")
        if option["worldpop_1300_pct"] < reference["worldpop_1300_pct"] - policy["access"]["walking_loss_pp"]:
            reasons.append("WorldPop walk coverage falls below the existing planning tolerance")
        if option["ghsl_1300_pct"] < reference["ghsl_1300_pct"] - policy["access"]["walking_loss_pp"]:
            reasons.append("GHSL walk coverage falls below the existing planning tolerance")
        if option["housing_two_changes_pct"] < reference["housing_two_changes_pct"] - policy["network_redesign"]["max_two_change_loss_pp"]:
            reasons.append("Housing reach with up to two changes falls below the existing tolerance")
        if option["worst_centre_loss_pp"] > policy["network_redesign"]["max_destination_loss_pp"]:
            reasons.append("At least one named central destination loses too much access")
        if option["wide_two_changes_pct"] < reference["wide_two_changes_pct"] - policy["corridor_selection"]["served_loss_pp"]:
            reasons.append("Wide outer-district journeys with up to two changes fall below the service tolerance")
        if option["parallel_pair_km"] > reference["parallel_pair_km"]:
            reasons.append("The layout increases sustained close parallel running")
        assessments[code] = reasons
    eligible = [key for key, holds in assessments.items() if not holds]
    best = min(eligible, key=lambda key: (summary[key]["short_count"], -summary[key]["former_short_access_people"],
                                         -summary[key]["transfer_stations"],
                                         summary[key]["stations"], -summary[key]["through_count"], key), default=None)
    three_rings = [key for key in available if all(ring in summary[key]["rings"] for ring in RINGS)]
    strongest = min(three_rings, key=lambda key: (len(assessments[key]), summary[key]["short_count"],
                                               -summary[key]["former_short_access_people"],
                                               -summary[key]["transfer_stations"], summary[key]["stations"],
                                               -summary[key]["housing_two_changes_pct"], key), default=None)
    return {"eligible_replacement": best, "illustrated_trial": best or strongest, "holds": assessments}


def _summary(networks, cover, housing, metro, geometry, context):
    summary = {}
    for code, net in networks.items():
        trip = metro["variants"][code]
        wide = trip["cohorts"][ring_grid_journeys.WIDE_ANGLE_COHORT]
        direct = classify_through(net, context)
        suburban = classify_through(net, context, middle_access_only=True)
        short = short_lines(net)
        summary[code] = {key: geometry[code][key] for key in
                         ("route_km", "lines", "stations", "transfer_stations", "rings", "parallel_pair_km")}
        housing_case = housing["variants"][code]
        reach = {label: row["reachable_with_at_most_share_of_all_pct"]["2"]
                 for label, row in housing_case["destinations"].items()}
        control_reach = housing["variants"]["published"]["destinations"]
        loss = max(control_reach[label]["reachable_with_at_most_share_of_all_pct"]["2"] - value
                   for label, value in reach.items())
        summary[code].update(candidate_id=net["candidate_id"], short_count=len(short), short_lines=short,
                             orbital_metrics=_orbital_metrics(net, context),
                             through_count=len(direct), through_lines=direct,
                             middle_ring_through_count=len(suburban), middle_ring_through_lines=suburban,
                             housing_two_changes_pct=housing_case["journeys"][
                                 "reachable_with_at_most_share_of_all_pct"]["2"],
                             housing_by_destination_pct=reach, worst_centre_loss_pp=round(max(loss, 0.), 4),
                             wide_two_changes_pct=wide["at_most_two_transfers_share_of_all_pct"],
                             wide_served_pct=wide["served_share_pct"], headway_s=trip["service"]["directional_headway_s"],
                             peak_load_index=trip["concentration"]["peak_load_per_departure_index"],
                             worldpop_1300_pct=cover["worldpop-2026"][code]["1300"]["access_pct"],
                             former_short_access_people=cover["worldpop-2026"][code]["1300"][
                                 "short_route_catchments"]["retained_access_people"],
                             ghsl_1300_pct=cover["ghsl-2025"][code]["1300"]["access_pct"])
    return summary


def _withdrawal_audit(trial, network, reference, graph, context, omitted):
    from . import network_station_sites, third_ring_pruning

    closed = {site for code in short_lines(reference) for site in reference["lines"][code]["station_ids"]
              if site not in trial["stations"]}
    before = {site: reference["stations"][site]["coordinates"] for site in closed}
    after = {site: row["coordinates"] for site, row in trial["stations"].items()}
    snap = network_station_sites._street_paths(graph, network_station_sites._water_tree(context))[0]
    paths, missing = third_ring_pruning._closure_paths(closed, after, before, graph, snap, WALK_M)
    return {
        "withdrawn_routes": omitted,
        "withdrawn_route_km": round(sum(network["lines"][code]["one_way_km"] for code in omitted), 3),
        "former_short_line_stations_closed": sorted(closed),
        "replacement_street_walks": paths,
        "stops_without_a_replacement_walk": missing,
    }


def _withdraw_short_services(network, reference, graph, context):
    """Remove the entire set of short routes before measuring the replacement."""
    omitted = short_lines(network)
    trial = deepcopy(network)
    trial.pop("through_lines", None)
    trial.pop("straight_through_layout", None)
    for code in omitted:
        del trial["lines"][code]
    memberships = {}
    for code, line in sorted(trial["lines"].items()):
        for site in line["station_ids"]:
            memberships.setdefault(site, []).append(code)
    trial["stations"] = {site: trial["stations"][site] | {"lines": calls}
                         for site, calls in sorted(memberships.items())}
    ring_corridors._restore_walk_links(trial, network, [
        row for row in network.get("station_site_links", []) if set(row["station_ids"]) <= memberships.keys()
    ])
    ring_corridors._refresh_transfers(trial)
    trial["topology"] = holistic_network.validate(trial)
    return holistic_network._identity(trial), _withdrawal_audit(trial, network, reference, graph, context, omitted)


def _join_trunks_to_ring(network, graph, context, protected, orbit):
    """Create exact cross-river trunk interchanges and absorb nearby solo calls."""
    from . import network_station_sites, third_ring_stations
    from .straight_through_layout import _tigris

    trial = deepcopy(network)
    lines, stations = trial["lines"], trial["stations"]
    orbital = holistic_network.Track(lines[orbit]["geometry"])
    polygons = _rings(trial)
    river = _tigris(context)
    snap, walk = network_station_sites._street_paths(graph, network_station_sites._water_tree(context))
    fixed = set(protected) | network_station_sites._endpoints(lines) | {
        site for link in trial.get("station_site_links", []) for site in link["station_ids"]
    }
    joins = []
    for code, line in sorted(lines.items()):
        if line["loop"] or code == "C1":
            continue
        if orbit == "M16" and not (set(line["station_ids"]) & set(lines["M09"]["station_ids"])):
            continue
        track = holistic_network.Track(line["geometry"])
        chord = np.linalg.norm(track.points[-1] - track.points[0])
        if not chord or track.km * 1000 / chord > NEW_AXIS_MAX_DETOUR or not any(
                len(river.intersections(a, b)[1]) for a, b in pairwise(track.points)):
            continue
        if _cross_ring_stations(trial, code, polygons)[orbit]:
            continue
        options = []
        for point, kms in holistic_network._crossings(track, orbital).items():
            street = snap(point)
            if street is None or min(kms[0], track.km - kms[0]) < .35:
                continue
            absorbed = set()
            for route, km in zip((code, orbit), kms, strict=True):
                calls = lines[route]["station_chainage_km"]
                neighbours = {site for site, current in calls.items() if
                              abs(current - km) * 1000 < third_ring_stations.MIN_CALL_SPACING_M}
                if neighbours & fixed or any(stations[site]["lines"] != [route] for site in neighbours):
                    break
                if any(max((outward or (float("inf"),))[0], (returning or (float("inf"),))[0])
                       > network_station_sites.WALK_LIMIT_M for site in neighbours
                       for outward, returning in [(walk(stations[site]["coordinates"], point),
                                                   walk(point, stations[site]["coordinates"]))]):
                    break
                absorbed.update(neighbours)
            else:
                options.append((len(absorbed), street[1], point, kms, sorted(absorbed)))
        if not options:
            continue
        _, offset, point, kms, absorbed = min(options)
        station = f"X-{orbit}-{code}-" + sha256(central_access.encode(point)).hexdigest()[:8]
        for site in absorbed:
            route, = stations.pop(site)["lines"]
            lines[route]["station_ids"].remove(site)
            del lines[route]["station_chainage_km"][site]
        stations[station] = {"name": f"{orbit} to {code} interchange", "coordinates": list(point),
                             "lines": sorted((code, orbit)), "basis": "Dry mapped crossing of the two alignments"}
        for route, km in zip((code, orbit), kms, strict=True):
            holistic_network._add(lines[route], station, km)
        joins.append({"line": code, "ring": orbit, "station_id": station, "street_offset_m": round(offset, 1),
                      "former_single_service_sites": absorbed})
        fixed.add(station)
    ring_corridors._refresh_transfers(trial)
    trial["topology"] = holistic_network.validate(trial)
    return holistic_network._identity(trial), joins


def _refine_orbitals(revised, evidence, reference, graph, context):
    from . import third_ring_stations

    validate_layout(revised)
    clean, withdrawal = _withdraw_short_services(revised, reference, graph, context)
    protected = {row["station_id"] for row in evidence["ring_transfers"]}
    protected.update(set(ring_grid_comparison.PROTECTED) & clean["stations"].keys())
    connected, joins = clean, []
    for orbit in ("M09", "M16"):
        connected, transfers = _join_trunks_to_ring(connected, graph, context, protected, orbit)
        joins.extend(transfers)
        protected.update(row["station_id"] for row in transfers)
    joined, consolidation = third_ring_stations.consolidate(
        connected, graph=graph, context=context, protected_stations=protected)
    validate_layout(joined)
    joined_audit = _withdrawal_audit(joined, revised, reference, graph, context, withdrawal["withdrawn_routes"])
    return clean, joined, {"orbitals": evidence, "withdrawal": joined_audit, "unconsolidated_withdrawal": withdrawal,
                           "station_consolidation": consolidation,
                           "shared_sites_before_consolidation": connected["topology"]["transfer_stations"],
                           "trunk_joins": joins}


def _cases(reference, graph, context):
    from . import third_ring_revision

    revised, evidence = third_ring_revision.revise_orbitals(reference, graph, context)
    clean, joined, audit = _refine_orbitals(revised, evidence, reference, graph, context)
    networks = {"published": reference, "suburban-orbital": clean}
    metadata = {"suburban-orbital": {"orbitals": evidence, "withdrawal": audit["unconsolidated_withdrawal"]}}
    if joined["candidate_id"] != clean["candidate_id"]:
        networks["suburban-interchanges"] = joined
        metadata["suburban-interchanges"] = audit
    try:
        road, road_evidence = third_ring_revision.revise_orbitals(
            reference, graph, context, road_assisted=True, maximum_access_detours=7)
        _, road, road_audit = _refine_orbitals(road, road_evidence, reference, graph, context)
    except ValueError as error:
        road_audit = {"rejection_reason": str(error)}
    else:
        if road["candidate_id"] not in {case["candidate_id"] for case in networks.values()}:
            networks["suburban-road-corridors"] = road
    metadata["suburban-road-corridors"] = road_audit
    return networks, metadata, {"selected": evidence}


def evaluate(layout=None):
    published = central_access.read(REFERENCE)
    reference = published["network"]
    if holistic_network._identity(dict(reference))["evaluation_id"] != reference["evaluation_id"]:
        raise ValueError("The active reference network differs from its evaluation")
    graph = central_access.walking_graph()
    context = central_access.original_cases()[3]
    policy = tomllib.loads(residential_planning.POLICY.read_text())
    populations = {key: holistic_access.load_population(key, graph) for key in ("worldpop-2026", "ghsl-2025")}
    people = populations["worldpop-2026"]
    origins, destinations, _ = residential_planning.study_points(policy, people)
    if layout is None:
        networks, metadata, examined = _cases(reference, graph, context)
    else:
        custom, changes = import_layout(layout, reference)
        validate_layout(custom)
        networks, metadata, examined = {"published": reference, "custom-layout": custom}, {"custom-layout": changes}, {"selected": None}
    assumptions = replace(residential_systems.service_assumptions(policy["planning_service"]), walk_limit_m=WALK_M)
    coverage = {key: _compare_access(networks, graph, population, "published")
                for key, population in populations.items()}
    print(f"Evaluating {len(networks)} distinct passenger layouts", flush=True)
    housing = holistic_pathways.compare(networks, graph=graph, assumptions=assumptions, origins=origins,
                                       destinations=destinations, origin_source=people.source, match_service_to="published")
    metro = ring_grid_journeys.compare(networks, reference="published", graph=graph, population=people,
                                      assumptions=assumptions)
    for code in networks:
        if not isclose(housing["variants"][code]["service"]["running_train_km_day"],
                       metro["variants"][code]["service"]["running_train_km_day"], abs_tol=.01):
            raise ValueError("Housing and wider assignment must carry the same scheduled train-km")
    geometry = {key: ring_grid_comparison._geometry(net, policy["corridor_screen"]) for key, net in networks.items()}
    summary = _summary(networks, coverage, housing, metro, geometry, context)
    for key, net in networks.items():
        summary[key]["airport_walk_m"] = _airport_walk(net, reference, graph)
    selection = _decision(summary, [key for key in networks if key != "published"], policy)
    if layout is not None:
        selection["illustrated_trial"] = "custom-layout"
    priced = list(networks)
    costs = {key: _equal_scope_cost(networks[key], context, policy) for key in priced}
    sources = dict(published["source_sha256"])
    for key, value in costs.items():
        sources.update(value.pop("source_sha256"))
    for net in networks.values():
        sources.update(net.get("source_sha256", {}))
    for path in (REFERENCE, residential_planning.POLICY, Path(__file__), *(CITY / f"{name}.py" for name in
                  ("third_ring_geometry", "third_ring_revision", "third_ring_stations", "third_ring_pruning",
                   "third_ring_publication"))):
        sources[path.relative_to(central_access.ROOT).as_posix()] = central_access.digest(path)
    record = {"schema": "osr-baghdad-three-ring-comparison/1", "reference": published["publication_id"],
              "study_status": "planning-comparison", "physical_acceptance": False, "selection": selection,
              "rings": examined, "layouts": networks, "layout_trials": metadata, "summary": summary,
              "geometry": geometry, "coverage": coverage, "housing": housing, "metropolitan": metro,
              "costs": costs, "source_sha256": sources}
    record["publication_id"] = sha256(central_access.encode(record)).hexdigest()
    return record, context
