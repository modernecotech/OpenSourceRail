"""Compare population-fitted rings and cross-city trunks with Baghdad’s reference."""

from dataclasses import replace
from hashlib import sha256
from math import isclose
from itertools import combinations, pairwise
from pathlib import Path
import tomllib

from engineering.outline import metro_network

import numpy as np
from scipy.spatial import cKDTree
from shapely import contains_xy, distance, line_interpolate_point
from shapely.geometry import LineString, Point, Polygon

from . import (central_access, coverage_destinations, coverage_gap, coverage_network, coverage_regional,
               coverage_through_journeys, coverage_trunks, holistic_access, holistic_network, holistic_pathways, ring_corridors,
               residential_layouts, residential_planning, residential_systems, ring_grid_comparison, ring_grid_journeys,
               straight_network_study)
from .coverage_orbitals import WALK_M


CITY = straight_network_study.CITY
REFERENCE = straight_network_study.RECORD
RINGS = coverage_network.RINGS
SHORT_KM = 8.
NEW_AXIS_MAX_DETOUR = coverage_trunks.MAX_DETOUR


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
    for name, (first, second) in zip(("inner_middle", "middle_outer"), pairwise(RINGS), strict=True):
        boundary, outer = (polygons[code].boundary for code in (first, second))
        gaps = distance(line_interpolate_point(boundary, np.arange(25., boundary.length, 50.)), outer)
        metrics[name + "_gap_km"] = dict(zip(("p10", "median", "p90"), np.round(
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


def _local_service(line):
    return line.get("service_role") in {"urban-gap", "regional-connector"}


def classify_through(network, context, *, middle_access_only=False):
    """Count straight cross-river trunks and verify their ring interchanges."""
    from .straight_through_layout import _tigris

    river = _tigris(context)
    polygons = _rings(network)
    beyond = polygons[next(reversed(polygons))] if polygons else None
    results = {}
    for code, line in network["lines"].items():
        if line["loop"] or _local_service(line) or line["one_way_km"] < coverage_trunks.MIN_LENGTH_KM:
            continue
        track = holistic_network.Track(line["geometry"])
        chord = float(np.linalg.norm(track.points[-1] - track.points[0]))
        detour = track.km * 1000 / chord if chord else float("inf")
        if detour > NEW_AXIS_MAX_DETOUR or (not middle_access_only and beyond is not None and any(
                beyond.covers(Point(track.points[i])) for i in (0, -1))):
            continue
        shares = _cross_ring_stations(network, code, polygons)
        crossings = sorted(track.chainage[i] + fraction * track.lengths[i]
                           for i, (a, b) in enumerate(pairwise(track.points))
                           for fraction in river.intersections(a, b)[1])
        tigris_count = len(crossings[:1]) + sum(end - start > 1. for start, end in pairwise(crossings))
        required = ("M15", "M09") if middle_access_only else shares
        if all(shares.get(code) for code in required) and tigris_count == 1:
            results[code] = {"route_km": track.km, "detour_ratio": round(detour, 4), "ring_crossing_stations": shares,
                             "crosses_tigris_centreline": True}
    return results


def short_lines(network):
    return sorted(code for code, line in network["lines"].items()
                  if not line["loop"] and not _local_service(line) and code != "C1" and line["one_way_km"] <= SHORT_KM)


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
            role = props.get("service_role")
            if role not in {None, "urban-gap", "regional-connector"}:
                raise ValueError(f"{code} has an unsupported service role")
            paths[code] = (coords, props["station_ids"], props["loop"], props.get("name", code), role,
                           props.get("destination"))
    if not paths:
        raise ValueError("An edited network needs at least one route")
    for code, (coords, calls, loop, name, role, destination) in sorted(paths.items()):
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
        if role:
            lines[code]["service_role"] = role
        if destination is not None:
            if not isinstance(destination, str) or role != "regional-connector":
                raise ValueError(f"{code} has an unsupported named terminal")
            lines[code]["destination"] = destination
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


def _compare_access(networks, graph, population, baseline, suburban_boundary=None):
    stations = {key: {stop: row["coordinates"] for stop, row in net["stations"].items()}
                for key, net in networks.items()}
    walks = {key: holistic_access.walk_to_station(sites, graph, population)[0] for key, sites in stations.items()}
    inner, outer = (_rings(networks[baseline])[key] for key in RINGS[:2])
    x, y = (population.coordinates * holistic_network.LOCAL_METRES).T
    outside = ~contains_xy(outer, x, y)
    centre = contains_xy(inner, x, y)
    suburban = ~contains_xy(suburban_boundary, x, y) if suburban_boundary is not None else None
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
                               "lost_pct": round(float(loss / total * 100), 4),
                               "middle_only_people": round(float(population.counts[
                                   present & (remainder_walk > limit)].sum()))}
            row[str(limit)]["largest_formerly_served_cells"] = residential_layouts._loss_locations(
                population, old & ~present & (population.counts > 0))
            row[str(limit)]["district_access_pct"] = {name: round(float(population.counts[present & mask].sum()
                                                                        / population.counts[mask].sum() * 100), 4)
                                                       for name, mask in sectors.items() if mask.any()}
            if suburban is not None:
                total_fringe = float(population.counts[suburban].sum())
                fringe_people = float(population.counts[suburban & present].sum())
                row[str(limit)]["outside_trial_outer_ring"] = {
                    "population": round(total_fringe), "served": round(fringe_people),
                    "access_pct": round(100 * fringe_people / total_fringe, 4) if total_fringe else None,
                }
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


def _suburban_metrics(network):
    polygons = _rings(network)
    if set(polygons) != set(RINGS):
        return {}
    outer = polygons[RINGS[-1]]
    contour = outer.buffer(coverage_trunks.SUBURBAN_GATE_OFFSET_M)
    tracks = {code: holistic_network.Track(line["geometry"]) for code, line in sorted(network["lines"].items())
              if not line["loop"] and line.get("service_role") != "urban-gap"}
    gates = {}
    for code, track in tracks.items():
        if network["lines"][code].get("service_role") == "regional-connector":
            result = coverage_regional.departure(track, outer, contour)
            gates[code] = result[0] if result else None
        else:
            gates[code] = coverage_trunks.suburban_departures(track, contour)
    arms = {code: coverage_trunks.suburban_arms(track, outer) for code, track in tracks.items()}
    distances = [(first, second, coverage_trunks.suburban_departure_distance(gates[first], gates[second]))
                 for first, second in combinations(tracks, 2) if gates[first] is not None and gates[second] is not None]
    return {
        "departures": {code: (points / holistic_network.LOCAL_METRES).tolist()
                       for code, points in gates.items() if points is not None},
        "missing_contour_crossings": [code for code, points in gates.items() if points is None],
        "minimum_departure_spacing_m": round(min(row[2] for row in distances), 2) if distances else None,
        "close_departures": [[a, b] for a, b, distance in distances
                             if distance < coverage_trunks.SUBURBAN_PARALLEL_SEPARATION_M],
        "parallel_suburban_corridors": [[a, b] for a, b in combinations(tracks, 2)
                                       if coverage_trunks.suburban_parallel(arms[a], arms[b])],
    }


def _decision_holds(summary, available, policy, metadata):
    reference = summary["published"]
    assessments = {}
    for code in available:
        option = summary[code]
        reasons = list(metadata.get(code, {}).get("trunk_search", {}).get("holds", []))
        if set(option["rings"]) != set(RINGS):
            reasons.append("The layout needs exactly three rings")
        if option["orbital_metrics"]["inner_foldback_km"] != 0:
            reasons.append("The central ring retains close non-adjacent reaches")
        if option["short_count"]:
            reasons.append("A short standalone route remains")
        if option["airport_walk_m"] is None or option["airport_walk_m"] > WALK_M:
            reasons.append("The Airport terminal lacks a replacement station within the street catchment")
        if option["through_count"] < 2 or option["through_count"] != (
                option["lines"] - len(option["rings"]) - len(option["local_services"])):
            reasons.append("Every cross-city trunk must cross the Tigris once and share a station with each ring")
        missing = [name for name, walk in option["destination_walk_m"].items() if walk is None or walk > WALK_M]
        if missing:
            reasons.append("Named suburban destinations outside street walking catchment: " + ", ".join(missing))
        if any(option["suburban"].get(key) for key in (
                "missing_contour_crossings", "close_departures", "parallel_suburban_corridors")):
            reasons.append("The suburban departures or parallel corridors fail the outside-ring screen")
        if option["lines"] >= reference["lines"] or option["stations"] >= reference["stations"]:
            reasons.append("The layout must use fewer routes and station sites")
        if option["station_screen"]["pairs_closer_than_750_m"] >= reference["station_screen"]["pairs_closer_than_750_m"]:
            reasons.append("The layout must reduce clusters of distinct station sites within 750 m")
        if option["worldpop_1300_pct"] < reference["worldpop_1300_pct"]:
            reasons.append("WorldPop walk coverage is below the two-ring reference")
        if option["ghsl_1300_pct"] < reference["ghsl_1300_pct"]:
            reasons.append("GHSL walk coverage is below the two-ring reference")
        if option["housing_two_changes_pct"] < reference["housing_two_changes_pct"] - policy["network_redesign"]["max_two_change_loss_pp"]:
            reasons.append("Housing reach with up to two changes falls below the existing tolerance")
        if option["worst_centre_loss_pp"] > policy["network_redesign"]["max_destination_loss_pp"]:
            reasons.append("At least one named central destination loses too much access")
        if option["wide_two_changes_pct"] < reference["wide_two_changes_pct"] - policy["corridor_selection"]["served_loss_pp"]:
            reasons.append("Wide outer-district journeys with up to two changes fall below the service tolerance")
        if option["parallel_pair_km"] > reference["parallel_pair_km"]:
            reasons.append("The layout increases sustained close parallel running")
        assessments[code] = reasons

    return assessments


def _through_research_lead(summary, journeys, available):
    """Prefer one-seat reach across all named suburbs before trading off coverage."""
    candidates = []
    for code in available:
        row = summary[code]
        if any(walk is None or walk > WALK_M for walk in row["destination_walk_m"].values()):
            continue
        if row["airport_walk_m"] is None or row["airport_walk_m"] > WALK_M:
            continue
        if any(row["suburban"].get(key) for key in (
                "missing_contour_crossings", "close_departures", "parallel_suburban_corridors")):
            continue
        origins = journeys["variants"][code]["origins"].values()
        direct = [origin["direct_through_destination_count"] for origin in origins]
        if not any(direct):
            continue
        candidates.append((-sum(count > 0 for count in direct), -min(direct), -sum(direct),
                           -min(row["worldpop_1300_pct"], row["ghsl_1300_pct"]), row["route_km"], code))
    return min(candidates)[-1] if candidates else None


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
        summary[code].update(station_screen=coverage_network.station_audit(net), candidate_id=net["candidate_id"], short_count=len(short), short_lines=short,
                             orbital_metrics=_orbital_metrics(net, context),
                             suburban=_suburban_metrics(net),
                             local_services={line_id: line["service_role"] for line_id, line in net["lines"].items()
                                             if _local_service(line)},
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
        networks, metadata, examined = coverage_network.designs(reference, graph, context, populations)
        for network in networks.values():
            validate_layout(network)
    else:
        custom, changes = import_layout(layout, reference)
        validate_layout(custom)
        networks, metadata, examined = {"published": reference, "custom-layout": custom}, {"custom-layout": changes}, {"selected": None}
    for network in networks.values():
        urban = [line_id for line_id, line in network["lines"].items() if line.get("service_role") == "urban-gap"]
        if urban and urban != [coverage_gap.GAP_LINE_ID]:
            raise ValueError("Only one independently verified urban gap service can be exempt from the trunk screen")
        if urban:
            coverage_gap.validate_gap_line(network, graph, context)
        for code, regional in coverage_regional.validate(network, context, graph).items():
            if regional["failures"]:
                raise ValueError(f"{code}: " + ", ".join(regional["failures"]))
    assumptions = replace(residential_systems.service_assumptions(policy["planning_service"]), walk_limit_m=WALK_M)
    core = next((details["core_layout"] for details in metadata.values() if "core_layout" in details), None)
    suburban_boundary = _rings(networks[core])[RINGS[-1]] if core else None
    coverage = {key: _compare_access(networks, graph, population, "published", suburban_boundary)
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
        summary[key]["destination_walk_m"] = coverage_destinations.walking(net, graph)
    journeys = coverage_through_journeys.compare(
        networks, graph=graph, destinations=destinations, assumptions=assumptions,
        through_routes={code: row["through_lines"] for code, row in summary.items()},
    )
    for key, case in journeys["variants"].items():
        if not isclose(case["running_train_km_day"], housing["variants"][key]["service"]["running_train_km_day"],
                       abs_tol=.01):
            raise ValueError("Suburban journeys must carry the same scheduled train-km")
    holds = _decision_holds(summary, [key for key in networks if key != "published"], policy, metadata)
    costs = {key: _equal_scope_cost(net, context, policy) for key, net in networks.items()}
    scope = {"walking": f"Baghdad retained streets and population grids, {WALK_M} m",
             "service": "Matched train-km passenger test and six-minute cost offer",
             "cost": "Baghdad common 2026 scope and 30-year present cost"}
    metro_cases = {key: {
        "destination_walk_m": row["destination_walk_m"] | {"Airport": row["airport_walk_m"]},
        "population_access_pct": {"worldpop-2026": row["worldpop_1300_pct"], "ghsl-2025": row["ghsl_1300_pct"]},
        "installed_cost": costs[key]["cost_cases"]["base"]["installed_planning_usd_m"],
        "whole_life_cost": costs[key]["cost_cases"]["base"]["whole_life_present_usd_m"],
        "route_count": row["lines"], "station_count": row["stations"],
        "holds": holds.get(key, []), "scope": scope,
    } for key, row in summary.items()}
    comparison = metro_network.compare(metro_cases, required_destinations=[*coverage_destinations.ANCHORS, "Airport"],
                                       population_grids=populations, walk_limit_m=WALK_M, reference_id="published")
    through_lead = _through_research_lead(summary, journeys, metadata)
    selection = {"holds": holds, "eligible_replacement": comparison["eligible_economic_lead"],
                 "through_research_lead": through_lead,
                 "illustrated_trial": comparison["eligible_economic_lead"] or through_lead or comparison["research_lead"]}
    if layout is not None:
        selection["illustrated_trial"] = "custom-layout"
    sources = dict(published["source_sha256"])
    for key, value in costs.items():
        sources.update(value.pop("source_sha256"))
    for key, net in networks.items():
        if not key.startswith("retained-"):
            sources.update(net.get("source_sha256", {}))
    sources.update(metro_network.SOURCE_SHA256)
    for path in (REFERENCE, coverage_destinations.REFERENCE_GIS, coverage_network.RETAINED_SEED,
                 residential_planning.POLICY, Path(__file__), *(CITY / f"{name}.py" for name in
                   ("coverage_network", "coverage_orbitals", "coverage_trunks", "coverage_extensions", "third_ring_through",
                    "third_ring_publication", "coverage_destinations", "coverage_gap", "coverage_regional",
                    "coverage_through_journeys"))):
        sources[path.relative_to(central_access.ROOT).as_posix()] = central_access.digest(path)
    record = {"schema": "osr-baghdad-three-ring-comparison/1", "reference": published["publication_id"],
              "study_status": "planning-comparison", "physical_acceptance": False, "selection": selection,
              "rings": examined, "layouts": networks, "layout_trials": metadata, "summary": summary,
              "geometry": geometry, "coverage": coverage, "housing": housing, "metropolitan": metro,
              "named_suburban_journeys": journeys,
              "costs": costs, "source_sha256": sources,
              "destinations": coverage_destinations.locations(),
              "metropolitan_comparison": comparison,
              "metropolitan_patterns": metro_network.pattern_options(
                  pedestrian_network=True, population_grids=populations, mapped_destinations=coverage_destinations.ANCHORS)}
    record["publication_id"] = sha256(central_access.encode(record)).hexdigest()
    return record, context
