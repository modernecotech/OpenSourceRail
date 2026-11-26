"""Evaluate a centre-serving Baghdad inner ring and simpler junctions at equal service."""

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import tomllib

import numpy as np

from . import (
    central_access, holistic_access, holistic_network, holistic_pathways,
    network_station_sites, residential_planning, residential_systems,
    ring_corridors, ring_grid_journeys, ring_network_study as previous,
    ring_service_assignment, spaced_ring_layouts,
)


CITY = previous.CITY
REPORT = CITY / "CENTRAL-RING-NETWORK.md"
RECORD = CITY / "central-ring-network.json"
FIGURE = CITY / "maps/baghdad-central-ring-network.png"
GEOJSON = CITY / "maps/baghdad-central-ring-network.geojson"
WALK_LIMITS = (1_200, 1_300)
WALK_NEW = WALK_LIMITS[-1]
RINGS = ("M09", "M15")
NAMES = {"current": "Published city network", "prior": "Previous reworked wider rings"}
SECTORS = ("Southwest", "South", "Southeast", "West", "Centre", "East", "Northwest", "North", "Northeast")


def _read_prior():
    """Recover all physical calls, lengths and measured street links from the public GIS."""
    source = central_access.read(previous.GEOJSON)
    lines, stations, walks = {}, {}, []
    for feature in source["features"]:
        meta = feature["properties"]
        kind = meta["kind"]
        coordinates = feature["geometry"]["coordinates"]
        if kind == "line":
            lines[meta["line_id"]] = {k: v for k, v in meta.items() if k not in {"kind", "line_id"}} | {
                "geometry": coordinates}
        elif kind in {"station", "interchange"}:
            stations[meta["station_id"]] = {k: v for k, v in meta.items() if k not in {"kind", "station_id"}} | {
                "coordinates": coordinates}
        elif kind == "walking-interchange":
            walks.append({k: v for k, v in meta.items() if k not in {"kind", "stroke"}} | {"geometry": coordinates})
    network = {"lines": lines, "stations": stations, "station_site_links": walks,
               "transfers": [], "physical_accepted": False, "operating_timetable_validated": False,
               "source_sha256": {previous.GEOJSON.relative_to(central_access.ROOT).as_posix():
                                     central_access.digest(previous.GEOJSON)},
               "imported_evaluation_id": source["evaluation_id"]}
    ring_corridors._refresh_transfers(network)
    network["topology"] = holistic_network.validate(network)
    network = holistic_network._identity(network)
    if network["candidate_id"] != source["candidate_id"]:
        raise ValueError("The public GIS no longer matches the previously compared physical configuration")
    return network


def _without_inner(prior):
    network = deepcopy(prior)
    del network["lines"]["M15"]
    spaced_ring_layouts._membership_and_links(network)
    network["topology"] = holistic_network.validate(network)
    network["previous_inner_ring_candidate"] = prior["candidate_id"]
    return holistic_network._identity(network)


def _data_zones(population):
    west, south, east, north = central_access.CORE
    x, y = population.coordinates.T
    inside = (x >= west) & (x <= east) & (y >= south) & (y <= north)
    columns = np.minimum(np.searchsorted(np.linspace(west, east, 4)[1:-1], x), 2)
    rows = np.minimum(np.searchsorted(np.linspace(south, north, 4)[1:-1], y), 2)
    return inside, {name: inside & (columns + rows * 3 == index) for index, name in enumerate(SECTORS)}


def _shares(counts, distances, where):
    total = counts[where].sum()
    served = {str(limit): float(counts[where & (distances <= limit)].sum()) for limit in WALK_LIMITS}
    return {"people": round(float(total)),
            **{threshold: {"people": round(value), "pct": round(100 * value / float(total), 4) if total else None}
               for threshold, value in served.items()}}


def _ring_street_access(network, graph):
    ids = network["lines"].get("M15", {}).get("station_ids", ())
    if not ids:
        return None
    return central_access.distances_from_stops({stop: network["stations"][stop]["coordinates"] for stop in ids}, graph)[0]


def _ring_connection_access(network, graph):
    """Reach lines that allow a direct change from an M15 service."""
    if "M15" not in network["lines"]:
        return None
    stations = network["stations"]
    ring_calls = set(network["lines"]["M15"]["station_ids"])
    transfer_sites = ring_calls | {
        other for link in network.get("station_site_links", ()) for first, other in
        (link["station_ids"], tuple(reversed(link["station_ids"]))) if first in ring_calls
    }
    routes = {route for stop in transfer_sites for route in stations[stop]["lines"]}
    points = {stop: data["coordinates"] for stop, data in stations.items() if routes.intersection(data["lines"])}
    return central_access.distances_from_stops(points, graph)[0]


def _centre_street_access(distances, destinations, graph):
    offsets, indexes = graph[3].query(central_access._points([site.coordinates for site in destinations]))
    values = np.full(len(offsets), np.inf) if distances is None else distances[graph[2][indexes]] + offsets
    return {site.id: {"name": site.name, "metres": round(float(value), 1)
                     if offset <= central_access.SNAP_M and np.isfinite(value) else None,
                     "within_1300_m": bool(offset <= central_access.SNAP_M and value <= WALK_NEW),
                     "coordinates": list(site.coordinates)}
            for site, offset, value in zip(destinations, offsets, values, strict=True)}


def _coverage(networks, graph, populations, destinations):
    ring_walk = {key: _ring_street_access(net, graph) for key, net in networks.items()}
    connection_walk = {key: _ring_connection_access(net, graph) for key, net in networks.items()}
    loaded = {}
    for dataset, population in populations.items():
        central, sectors = _data_zones(population)
        data = {}
        for key, network in networks.items():
            all_walk, _ = holistic_access.walk_to_station(
                {stop: row["coordinates"] for stop, row in network["stations"].items()}, graph, population)
            inner_walk = (np.full(len(population.counts), np.inf) if ring_walk[key] is None else
                          np.where(population.offsets_m <= central_access.SNAP_M,
                                   ring_walk[key][population.nodes] + population.offsets_m, np.inf))
            data[key] = {
                "metro": _shares(population.counts, all_walk, np.ones(len(all_walk), dtype=bool)),
                "central": _shares(population.counts, all_walk, central),
                "inner_ring": _shares(population.counts, inner_walk, central),
                "sectors": {label: {"network": _shares(population.counts, all_walk, mask),
                                    "ring": _shares(population.counts, inner_walk, mask)}
                            for label, mask in sectors.items()},
                "destinations_on_foot_to_ring": _centre_street_access(ring_walk[key], destinations, graph),
                "destinations_with_at_most_one_change_from_ring": _centre_street_access(
                    connection_walk[key], destinations, graph),
            }
        loaded[dataset] = data
    return loaded


def _check(inner_case, prior):
    if holistic_network.validate(inner_case) != inner_case["topology"]:
        raise ValueError("Passenger graph and network topology disagree")
    outer = inner_case["lines"]["M09"]
    if outer["geometry"] != prior["lines"]["M09"]["geometry"] or not outer["loop"]:
        raise ValueError("The outer ring alignment has changed")
    if not inner_case["lines"]["M15"]["loop"]:
        raise ValueError("The centre-serving inner route must be a complete loop")
    outer_region = ring_corridors._ring_polygon(outer)
    inner_region = ring_corridors._ring_polygon(inner_case["lines"]["M15"])
    if not outer_region.contains(inner_region) or not outer_region.boundary.disjoint(inner_region.boundary):
        raise ValueError("Inner and outer ring traces must be simple, nested and disjoint")
    if inner_case["lines"]["C1"]["geometry"] != prior["lines"]["C1"]["geometry"]:
        raise ValueError("The Airport through alignment changed")
    if set(previous.wider.grid.PROTECTED) - inner_case["stations"].keys():
        raise ValueError("A named central station was removed")
    if not previous._direct_routes(inner_case):
        raise ValueError("The two rings need a direct shared passenger route")
    if holistic_network._identity(dict(inner_case))["evaluation_id"] != inner_case["evaluation_id"]:
        raise ValueError("Network data differs from the sealed evaluation")
    return float(outer_region.boundary.distance(inner_region.boundary))


def _summary(networks, coverage, geometry, housing, assignment):
    summaries = {}
    for key, net in networks.items():
        a = coverage["worldpop-2026"][key]
        g = geometry[key]
        s = assignment["variants"][key]
        h = housing["variants"][key]
        summaries[key] = {
            "candidate_id": net["candidate_id"], "evaluation_id": net["evaluation_id"],
            "route_km": g["route_km"], "lines": g["lines"], "stations": g["stations"], "rings": g["rings"],
            "parallel_pair_km": g["parallel_pair_km"],
            "close_site_pairs": len(network_station_sites._nearby(net["stations"], spaced_ring_layouts.CLOSE_SITE_M)),
            "direct_routes": previous._direct_routes(net),
            "central_ring_named_centres": sum(row["within_1300_m"] for row in a["destinations_on_foot_to_ring"].values()),
            "central_centres_via_connection": sum(row["within_1300_m"] for row in
                                                  a["destinations_with_at_most_one_change_from_ring"].values()),
            "metro_walk_1200_pct": a["metro"]["1200"]["pct"],
            "metro_walk_1300_pct": a["metro"]["1300"]["pct"],
            "central_walk_1300_pct": a["central"]["1300"]["pct"],
            "inner_walk_1300_pct": a["inner_ring"]["1300"]["pct"],
            "worst_inner_sector_pct": min((row["ring"]["1300"]["pct"] for row in a["sectors"].values()
                                           if row["ring"]["1300"]["pct"] is not None), default=None),
            "worst_central_sector_pct": min((row["network"]["1300"]["pct"] for row in a["sectors"].values()
                                             if row["network"]["1300"]["pct"] is not None), default=None),
            "wide_trips_pct": s["cohorts"][ring_grid_journeys.WIDE_ANGLE_COHORT]["journeys"]["served_share_pct"],
            "all_trips_pct": s["journeys"]["served_share_pct"],
            "housing_two_changes_pct": h["journeys"]["reachable_with_at_most_share_of_all_pct"]["2"],
            "riding_inner_pct": s["ring_use"]["M15"]["share_of_all_pct"],
        }
    return summaries


def _pick(summary, variants, policy):
    old = summary["prior"]
    allowed_walk = policy["access"]["walking_loss_pp"]
    allowed_housing = policy["network_redesign"]["max_two_change_loss_pp"]
    allowed_trips = policy["corridor_selection"]["served_loss_pp"]
    available = [key for key in variants if key in summary]
    reach = [key for key in available
             if summary[key]["metro_walk_1300_pct"] >= old["metro_walk_1300_pct"] - allowed_walk
             and summary[key]["central_walk_1300_pct"] >= old["central_walk_1300_pct"] - allowed_walk
             and summary[key]["housing_two_changes_pct"] >= old["housing_two_changes_pct"] - allowed_housing
             and summary[key]["wide_trips_pct"] >= old["wide_trips_pct"] - allowed_trips]
    improved = [key for key in reach if summary[key]["central_ring_named_centres"] >= old["central_ring_named_centres"]
                and summary[key]["inner_walk_1300_pct"] > old["inner_walk_1300_pct"]
                and summary[key]["parallel_pair_km"] < old["parallel_pair_km"]
                and summary[key]["stations"] <= old["stations"]]
    balanced = [key for key in improved if summary[key]["worst_central_sector_pct"]
                >= old["worst_central_sector_pct"] - allowed_walk]
    ranked = balanced or improved or reach or available
    selected = max(ranked, key=lambda key: (summary[key]["central_ring_named_centres"],
                                           summary[key]["central_centres_via_connection"],
                                           summary[key]["worst_central_sector_pct"],
                                           -summary[key]["parallel_pair_km"], -summary[key]["close_site_pairs"],
                                           summary[key]["inner_walk_1300_pct"],
                                           summary[key]["worst_inner_sector_pct"] or 0.,
                                           summary[key]["housing_two_changes_pct"]))
    return selected, {"preserves_reach_and_improves_network": improved,
                       "preserves_weakest_sector": balanced,
                       "within_reach_limits": reach, "ranking_pool": ranked,
                       "allowed_walking_loss_pp": allowed_walk, "allowed_housing_loss_pp": allowed_housing,
                       "allowed_wide_trip_loss_pp": allowed_trips}


def _protected_ring_calls(network, destinations, graph):
    """Keep the ring call that gives each named destination its best short walk."""
    stations = network["stations"]
    ring = network["lines"]["M15"]["station_ids"]
    points = {stop: stations[stop]["coordinates"] for stop in ring}
    centre_points = np.asarray([site.coordinates for site in destinations])
    offsets, indexes = graph[3].query(central_access._points(centre_points))
    reached = {}
    for stop in ring:
        direct = np.linalg.norm((centre_points - points[stop]) * holistic_network.LOCAL_METRES, axis=1)
        if (direct > WALK_NEW * 1.03).all():
            continue
        street, _ = central_access.distances_from_stops({stop: points[stop]}, graph)
        walks = street[graph[2][indexes]] + offsets
        for i, distance in enumerate(walks):
            if offsets[i] <= central_access.SNAP_M and distance <= WALK_NEW:
                row = (float(distance), stop)
                key = destinations[i].id
                if key not in reached or row < reached[key]:
                    reached[key] = row
    return {key: stop for key, (_, stop) in sorted(reached.items())}


def _concentrated_sites(key, label, seed, edits, graph, context, *, destinations=()):
    from . import central_junction_sites

    # Compare deeper station consolidation against actual network access.
    sources = {code: row for code, row in edits.items() if row["network"] is not None}
    most_trimmed = min(sources, key=lambda code: sources[code]["network"]["topology"]["route_km"], default=None)
    basis = sources[most_trimmed] if most_trimmed else {"network": seed, "actions": []}
    named_calls = _protected_ring_calls(basis["network"], destinations, graph) if destinations else {}
    suffix = "central stops protected" if named_calls else "more concentrated junctions"
    result = {"name": f"{label} · {suffix}", "ring_source": key, "actions": basis["actions"],
              "named_centre_ring_calls": named_calls}
    protected = set(previous.wider.grid.PROTECTED) | set(named_calls.values())
    try:
        revised, audit = central_junction_sites.consolidate(
            basis["network"], graph, context, protected_stations=protected,
            replacement_m=800, relocation_m=550, link_m=650)
        return result | {"network": revised, "junction_audit": audit}
    except ValueError as error:
        return result | {"network": None, "rejection_reason": str(error)}


def _proposals(seeds, graph, context, population, screen, destinations):
    from . import central_junction_sites, central_parallel_routes

    proposals = {}
    protected = previous.wider.grid.PROTECTED
    for index, (key, seed) in enumerate(seeds.items()):
        label = "Central-coverage ring" if key == "central-coverage" else "Central interchange ring"
        proposals[key] = {"network": seed, "name": label, "ring_source": key}
        # Compare the tighter and wider site search on the same alignment once.
        for suffix, bounds in (("junctions", {}),
                               ("500m", {"replacement_m": 500, "relocation_m": 350, "link_m": 500})):
            if suffix == "500m" and index:
                continue
            try:
                rebuilt, audit = central_junction_sites.consolidate(
                    seed, graph, context, protected_stations=protected, population=population, **bounds)
                proposals[f"{key}/{suffix}"] = {"network": rebuilt, "name": f"{label} · junctions {audit['bounds']['replacement_m']:g} m",
                                                 "ring_source": key, "junction_audit": audit}
            except ValueError as error:
                proposals[f"{key}/{suffix}"] = {"network": None, "name": f"{label} · junction consolidation",
                                                 "ring_source": key, "rejection_reason": str(error)}
        edits = central_parallel_routes.alternatives(seed, graph, context, screen=screen, protected_stations=protected)
        for code, variant in edits.items():
            adjusted = {"name": f"{label} · {variant['name']}", "ring_source": key, "actions": variant["actions"]}
            if variant["network"] is not None:
                try:
                    revised, audit = central_junction_sites.consolidate(
                        variant["network"], graph, context, protected_stations=protected, population=population)
                    adjusted.update(network=revised, junction_audit=audit)
                except ValueError as error:
                    adjusted.update(network=None, rejection_reason=str(error))
            else:
                adjusted.update(network=None, rejection_reason=variant["rejection_reason"])
            proposals[f"{key}/{code}"] = adjusted
        proposals[f"{key}/strong"] = _concentrated_sites(key, label, seed, edits, graph, context)
        proposals[f"{key}/strong-centres"] = _concentrated_sites(
            key, label, seed, edits, graph, context, destinations=destinations)
    return proposals


def _passenger_layout_key(network):
    links = sorted(network.get("station_site_links", []), key=lambda row: row["id"])
    return network["candidate_id"], sha256(central_access.encode(links)).hexdigest()


def evaluate(baseline_path):
    from . import central_junction_sites, central_parallel_routes, central_ring_geometry

    baseline_record = central_access.read(baseline_path)
    current = baseline_record["network"]
    historic = central_access.read(previous.RECORD)
    if central_access.digest(baseline_path) != historic["reference_packet_sha256"]:
        raise ValueError("The previous rings study used a different published city baseline")
    prior = _read_prior()
    if prior["candidate_id"] != historic["summary"][historic["display_trial"]]["candidate_id"]:
        raise ValueError("Previous cost and GIS packets describe different network candidates")
    graph = central_access.walking_graph()
    context = central_access.original_cases()[3]
    policy = tomllib.loads(residential_planning.POLICY.read_text())
    screen = policy["corridor_screen"]
    populations = {name: holistic_access.load_population(name, graph) for name in ("worldpop-2026", "ghsl-2025")}
    population = populations["worldpop-2026"]
    origins, destinations, centre_sources = residential_planning.study_points(policy, population)
    outer = _without_inner(prior)
    search = central_ring_geometry.alternatives(outer, graph, context, population=population, destinations=destinations)
    if not search["networks"]:
        raise ValueError("No centre-serving ring passed the mapped alignment and interchange screen")
    proposals = _proposals(search["networks"], graph, context, population, screen, destinations)
    networks = {"current": current, "prior": prior}
    held = {}
    gaps = {"prior": _check(prior, prior)}
    retained = set()
    admitted = {_passenger_layout_key(net) for net in networks.values()}
    for key, entry in proposals.items():
        net = entry.get("network")
        if net is None:
            held[key] = entry.get("rejection_reason", "Geometry not admitted")
            continue
        try:
            gap = _check(net, prior)
        except ValueError as error:
            held[key] = str(error)
            continue
        identity = _passenger_layout_key(net)
        if identity not in admitted:
            networks[key] = net
            gaps[key] = gap
            retained.add(key)
            admitted.add(identity)
    if not retained:
        raise ValueError(f"No central ring case admitted for assignment: {held}")
    coverage = _coverage(networks, graph, populations, destinations)
    if abs(coverage["worldpop-2026"]["prior"]["metro"]["1200"]["pct"]
           - historic["summary"][historic["display_trial"]]["walk_1200_pct"]) > .011:
        raise ValueError("The reconstructed comparison does not reproduce prior walk access")
    physical = {key: previous.wider.grid._geometry(network, screen) for key, network in networks.items()}
    assumptions = replace(residential_systems.service_assumptions(policy["planning_service"]), walk_limit_m=WALK_NEW)
    housing = holistic_pathways.compare(networks, graph=graph, origins=origins, destinations=destinations,
                                       assumptions=assumptions, origin_source=population.source,
                                       match_service_to="current")
    use = ring_service_assignment.compare(
        networks, reference="current", paired_reference="prior", graph=graph, population=population,
        assumptions=assumptions, housing=housing)
    if (housing["demand_sample"]["sample_id"] != historic["household_journeys"]["demand_sample"]["sample_id"]
            or use["demand_sample"]["sample_id"] != historic["ring_service"]["demand_sample"]["sample_id"]):
        raise ValueError("The walk catchment trial changed the previous trip sample")
    summary = _summary(networks, coverage, physical, housing, use)
    for key, gap in gaps.items():
        summary[key]["minimum_ring_separation_m"] = gap
    chosen, selection = _pick(summary, proposals, policy)
    most_parallel_reduction = min(retained, key=lambda key: (summary[key]["parallel_pair_km"],
                                                             -summary[key]["central_ring_named_centres"],
                                                             summary[key]["close_site_pairs"], key))
    price_cases = {key: networks[key] for key in dict.fromkeys((chosen, most_parallel_reduction))}
    previous_cost = historic["six_minute_delivery_and_cost"]
    costs = {"current": previous_cost["current"], "prior": previous_cost[historic["display_trial"]]}
    costs.update(previous.wider.grid._price(price_cases, policy["planning_service"]))
    if any(row["candidate_id"] != summary[key]["candidate_id"] for key, row in costs.items()):
        raise ValueError("An installed allowance was calculated on a different route configuration")

    sources = historic["assumption_sources"] | baseline_record["sources"] | networks[chosen]["source_sha256"]
    required = (Path(__file__), Path(central_ring_geometry.__file__), Path(central_parallel_routes.__file__),
                Path(central_junction_sites.__file__), Path(holistic_access.__file__), previous.RECORD, previous.GEOJSON,
                residential_planning.POLICY,
                Path(central_access.__file__), Path(residential_planning.__file__))
    sources.update({previous.compact._file_id(path): central_access.digest(path) for path in required})
    record = {
        "schema": "osr-baghdad-central-ring-network/1", "display_trial": chosen, "selection": selection,
        "prior_comparison_id": historic["comparison_id"], "reference_packet_sha256": central_access.digest(baseline_path),
        "assumption_sources": sources, "central_area_wsen": list(central_access.CORE), "centre_sources": centre_sources,
        "walk_thresholds_m": list(WALK_LIMITS), "minimum_ring_separation_required_m": None,
        "geometry": physical, "summary": summary, "coverage": coverage, "household_journeys": housing, "ring_service": use,
        "geometry_search": {key: value for key, value in search.items() if key != "networks"},
        "layout_actions": {key: {field: value for field, value in item.items() if field != "network"}
                           for key, item in proposals.items()},
        "held_trials": held, "six_minute_delivery_and_cost": costs,
    }
    record["comparison_id"] = sha256(central_access.encode(record)).hexdigest()
    return record, networks, context
