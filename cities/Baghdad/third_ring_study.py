"""Compare Baghdad's connected network with an outer ring and longer through services."""

from dataclasses import replace
from hashlib import sha256
from math import isclose
from pathlib import Path
import tomllib

import numpy as np
from shapely import contains_xy
from shapely.geometry import LineString, Point, Polygon

from . import (central_access, holistic_access, holistic_network, holistic_pathways, ring_corridors,
               residential_planning, residential_systems, ring_grid_comparison, ring_grid_journeys,
               straight_network_study)


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
        if not polygons[outer].contains_properly(polygons[inner]):
            raise ValueError(f"{outer} must fully enclose {inner} without touching it")
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


def classify_through(network, context):
    """Count only through lines with actual ring-crossing platforms and a Tigris crossing."""
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
        if detour > NEW_AXIS_MAX_DETOUR or (beyond is not None and any(
                beyond.covers(Point(track.points[i])) for i in (0, -1))):
            continue
        shares = _cross_ring_stations(network, code, polygons)
        tigris = sum(bool(len(river.intersections(a, b)[1])) for a, b in zip(track.points, track.points[1:]))
        if all(shares.values()) and tigris:
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
    total = population.counts.sum()
    result = {}
    for key, distances in walks.items():
        row = {}
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
        if option["short_count"] >= reference["short_count"]:
            reasons.append("Short-line count did not fall")
        if option["airport_walk_m"] is None or option["airport_walk_m"] > WALK_M:
            reasons.append("The Airport terminal lacks a replacement station within the street catchment")
        if option["through_count"] <= reference["through_count"]:
            reasons.append("Too few near-straight Tigris through lines with shared stations on all three rings")
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
    best = min(eligible, key=lambda key: (summary[key]["short_count"], -summary[key]["through_count"],
                                         summary[key]["route_km"], key), default=None)
    three_rings = [key for key in available if all(ring in summary[key]["rings"] for ring in RINGS)]
    strongest = min(three_rings, key=lambda key: (len(assessments[key]), -summary[key]["through_count"],
                                               summary[key]["short_count"], -summary[key]["housing_two_changes_pct"],
                                               summary[key]["route_km"], key), default=None)
    return {"eligible_replacement": best, "illustrated_trial": best or strongest, "holds": assessments}


def _summary(networks, cover, housing, metro, geometry, context):
    summary = {}
    for code, net in networks.items():
        trip = metro["variants"][code]
        wide = trip["cohorts"][ring_grid_journeys.WIDE_ANGLE_COHORT]
        direct = classify_through(net, context)
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
                             through_count=len(direct), through_lines=direct,
                             housing_two_changes_pct=housing_case["journeys"][
                                 "reachable_with_at_most_share_of_all_pct"]["2"],
                             housing_by_destination_pct=reach, worst_centre_loss_pp=round(max(loss, 0.), 4),
                             wide_two_changes_pct=wide["at_most_two_transfers_share_of_all_pct"],
                             wide_served_pct=wide["served_share_pct"], headway_s=trip["service"]["directional_headway_s"],
                             peak_load_index=trip["concentration"]["peak_load_per_departure_index"],
                             worldpop_1300_pct=cover["worldpop-2026"][code]["1300"]["access_pct"],
                             ghsl_1300_pct=cover["ghsl-2025"][code]["1300"]["access_pct"])
    return summary


def _cases(reference, graph, context, populations, destinations):
    from . import third_ring_geometry, third_ring_portfolio, third_ring_pruning, third_ring_realign, third_ring_through

    examined = third_ring_geometry.evaluate(reference, graph, context)
    networks, metadata = {"published": reference}, {}
    if examined["selected"] is None:
        return networks, metadata, examined
    ring, evidence = third_ring_geometry.insert(reference, examined["selected"], graph, context)
    validate_layout(ring, reference)
    networks["ring-only"] = ring
    metadata["ring-only"] = evidence
    for key, field in (("wider-ring", "wider_alternative"), ("road-assisted-ring", "road_assisted_alternative")):
        if (option := examined.get(field)) is not None:
            alternative, evidence = third_ring_geometry.insert(reference, option, graph, context)
            validate_layout(alternative, reference)
            metadata[key] = evidence
            if alternative["candidate_id"] not in {row["candidate_id"] for row in networks.values()}:
                networks[key] = alternative
    people = populations["worldpop-2026"]
    axes = third_ring_through.alternatives(ring, graph, context, population=people, ring_id=RINGS[-1])
    for code, option in sorted(axes.items()):
        net = option.get("network")
        metadata[code] = {k: value for k, value in option.items() if k != "network"}
        if net is not None and net["candidate_id"] not in {row["candidate_id"] for row in networks.values()}:
            validate_layout(net, reference)
            networks[code] = net
    protected = set(ring_grid_comparison.PROTECTED) & set(reference["stations"])
    for code, net in tuple(networks.items()):
        if code in {"wider-ring", "road-assisted-ring"}:
            continue
        filtered, audit = third_ring_pruning.prune(
            net, graph, protected_stations=protected,
            protected_lines={ring for ring in RINGS if ring in net["lines"]} | {"C1", *classify_through(net, context)},
            populations=populations,
            reference=reference, context=context, max_route_km=SHORT_KM, max_closed_station_walk_m=WALK_M,
            max_population_loss_pct=.50, max_trials=20)
        key = "two-rings-trimmed" if code == "published" else f"{code}-trimmed"
        metadata[key] = audit
        if filtered["candidate_id"] != net["candidate_id"]:
            if code == "published":
                holistic_network.validate(filtered)
            else:
                validate_layout(filtered, reference)
            networks[key] = filtered
    library = networks.get("shifted-ring-through", networks.get("retained-through", ring))
    try:
        realigned = third_ring_realign.replace(library, graph, context)
        validate_layout(realigned)
        networks["realigned-inner-ring"] = realigned
        metadata["realigned-inner-ring"] = realigned["inner_ring_revision"]
    except ValueError as error:
        metadata["realigned-inner-ring"] = {"rejection_reason": str(error)}
    points = {point.id: point.coordinates for point in destinations} | {
        "airport-terminal": reference["stations"]["Airport-00"]["coordinates"]}
    prepared = third_ring_portfolio.screen(library, graph, populations=populations, destinations=points, walk_m=WALK_M)
    for key, required in (("from-empty-three", RINGS), ("from-empty-optional", ())):
        candidate, audit = third_ring_portfolio.assemble(
            library, graph, populations=populations, destinations=points, walk_m=WALK_M,
            required_ring_ids=required, max_lines=29, prepared=prepared)
        metadata[key] = audit
        if candidate is not None:
            validate_layout(candidate)
            networks[key] = candidate
    return networks, metadata, examined


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
        networks, metadata, examined = _cases(reference, graph, context, populations, destinations)
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
    price_keys = ("published", "two-rings-trimmed", "ring-only", "wider-ring", "road-assisted-ring",
                  "realigned-inner-ring", "from-empty-three", "from-empty-optional", selection["illustrated_trial"])
    priced = list(dict.fromkeys(key for key in price_keys if key in networks))
    costs = {key: _equal_scope_cost(networks[key], context, policy) for key in priced}
    sources = dict(published["source_sha256"])
    for key, value in costs.items():
        sources.update(value.pop("source_sha256"))
    for path in (REFERENCE, residential_planning.POLICY, Path(__file__), *(CITY / f"{name}.py" for name in
                  ("third_ring_geometry", "third_ring_portfolio", "third_ring_pruning", "third_ring_realign",
                   "third_ring_through", "third_ring_publication"))):
        sources[path.relative_to(central_access.ROOT).as_posix()] = central_access.digest(path)
    record = {"schema": "osr-baghdad-three-ring-comparison/1", "reference": published["publication_id"],
              "study_status": "planning-comparison", "physical_acceptance": False, "selection": selection,
              "rings": examined, "layouts": networks, "layout_trials": metadata, "summary": summary,
              "geometry": geometry, "coverage": coverage, "housing": housing, "metropolitan": metro,
              "costs": costs, "source_sha256": sources}
    record["publication_id"] = sha256(central_access.encode(record)).hexdigest()
    return record, context
