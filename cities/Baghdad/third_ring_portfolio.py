"""Assemble connected Baghdad rail portfolios from individually screened route options."""

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from heapq import heappop, heappush
from pathlib import Path

import numpy as np

from . import central_access, holistic_network, rail_consolidation, residential_layouts


@dataclass(frozen=True)
class RouteScreen:
    library_id: str
    walk_m: float
    neighbours: dict
    route_km: dict
    destinations: dict
    destination_walks: dict
    population_weights: dict
    masks: dict
    graph_source: dict
    graph_matrix: object


def _destinations(destinations):
    if not hasattr(destinations, "items"):
        destinations = {row.id: row.coordinates for row in destinations}
    return {code: tuple(getattr(point, "coordinates", point)) for code, point in sorted(destinations.items())}


def _neighbours(library):
    neighbours = {code: set() for code in library["lines"]}
    for station in library["stations"].values():
        for code in station["lines"]:
            neighbours[code].update(set(station["lines"]) - {code})
    for link in library.get("station_site_links", []):
        first, second = (library["stations"][code]["lines"] for code in link["station_ids"])
        for a in first:
            for b in second:
                neighbours[a].add(b)
                neighbours[b].add(a)
    return {code: tuple(sorted(routes)) for code, routes in neighbours.items()}


def screen(library, graph, *, populations, destinations, walk_m=1300):
    """Build reusable per-route street walking masks from the retained graph."""
    holistic_network.validate(library)
    destinations = _destinations(destinations)
    if (not np.isfinite(walk_m) or not 0 < walk_m <= max(central_access.WALK_M) + 3500
            or not destinations or not populations):
        raise ValueError("The portfolio needs a bounded walk, destinations and population data")
    points = np.asarray(list(destinations.values()))
    if points.shape != (len(destinations), 2) or not np.isfinite(points).all():
        raise ValueError("Use finite longitude and latitude for every destination")
    weights = {name: pop.counts for name, pop in sorted(populations.items())}
    if any(not np.isfinite(counts).all() or (counts < 0).any() or counts.sum() <= 0 for counts in weights.values()):
        raise ValueError("Portfolio population weights must be finite and represent positive population")
    _, matrix, active, tree, source = graph
    offsets, nearest = tree.query(central_access._points(points))
    nodes = active[nearest]
    destination_walks, masks = {}, {}
    for code, route in sorted(library["lines"].items()):
        stations = {stop: library["stations"][stop]["coordinates"] for stop in route["station_ids"]}
        distances, _ = central_access.distances_from_stops(stations, graph)
        walks = np.where(offsets <= central_access.SNAP_M, distances[nodes] + offsets, np.inf)
        destination_walks[code] = {
            name: float(length) for name, length in zip(destinations, walks, strict=True) if length <= walk_m
        }
        masks[code] = {name: (pop.offsets_m <= central_access.SNAP_M)
                            & (distances[pop.nodes] + pop.offsets_m <= walk_m)
                       for name, pop in sorted(populations.items())}
    return RouteScreen(
        library["evaluation_id"], walk_m, _neighbours(library),
        {code: row["one_way_km"] for code, row in library["lines"].items()},
        destinations, destination_walks, weights, masks, source, matrix,
    )


def _paths(data, chosen):
    """Minimum incremental route-km connector paths rooted at the current portfolio."""
    queue = [(0., (code,), code) for code in sorted(chosen)]
    best = {}
    while queue:
        distance, path, code = heappop(queue)
        if code in best:
            continue
        best[code] = tuple(route for route in path if route not in chosen)
        for neighbour in data.neighbours[code]:
            if neighbour not in best and neighbour not in chosen:
                extra = distance + data.route_km[neighbour]
                heappush(queue, (extra, (*path, neighbour), neighbour))
    return best


def _summary(data, chosen, covered):
    connections = defaultdict(set)
    for code in chosen:
        for dest in data.destination_walks[code]:
            connections[dest].add(code)
    populations, journey_proxy = {}, {}
    for name, counts in data.population_weights.items():
        total = float(counts.sum())
        people = float(counts[covered[name]].sum())
        populations[name] = {"estimated_residents": people, "share_pct": 100 * people / total}
        destination_reach = []
        for targets in connections.values():
            reachable = targets
            for _ in range(2):
                reachable = reachable | {other for code in reachable for other in data.neighbours[code] if other in chosen}
            walk = np.logical_or.reduce([data.masks[code][name] for code in sorted(reachable)])
            destination_reach.append(float(counts[walk].sum()) / total)
        journey_proxy[name] = (100 * sum(destination_reach) / len(data.destinations))
    return {
        "route_ids": sorted(chosen), "route_km": sum(data.route_km[code] for code in sorted(chosen)),
        "population_access": populations, "two_change_topological_proxy_pct": journey_proxy,
        "destination_walk_m": {dest: min(data.destination_walks[code][dest] for code in targets)
                               for dest, targets in sorted(connections.items())},
    }


def _trial(data, seed, rings, max_lines, cost_power):
    chosen = {seed}
    covered = {name: mask.copy() for name, mask in data.masks[seed].items()}
    totals = {name: weights.sum() for name, weights in data.population_weights.items()}
    pending_rings, pending_destinations = set(rings), set(data.destinations)
    pending_rings.discard(seed)
    pending_destinations.difference_update(data.destination_walks[seed])
    steps = [[seed]]
    while len(chosen) < max_lines:
        mandatory = bool(pending_rings or pending_destinations)
        options = _paths(data, chosen).values()
        ranked = []
        for path in sorted(set(options)):
            if not path or len(path) + len(chosen) > max_lines or (not mandatory and len(path) > 2):
                continue
            rings_hit = pending_rings.intersection(path)
            destinations_hit = pending_destinations.intersection(
                dest for code in path for dest in data.destination_walks[code])
            obligations = len(rings_hit) + len(destinations_hit)
            if mandatory and not obligations:
                continue
            lengths = sum(data.route_km[code] for code in path)
            gains = 0.
            for name, weights in data.population_weights.items():
                reach = (data.masks[path[0]][name] if len(path) == 1
                         else np.logical_or.reduce([data.masks[code][name] for code in path]))
                new = reach & ~covered[name]
                gains += weights[new].sum() / totals[name]
            if mandatory or gains:
                score = (-obligations / lengths, -gains / lengths ** cost_power, len(path), lengths, path)
                ranked.append((score, path, rings_hit, destinations_hit))
        if not ranked:
            break
        _, path, rings_hit, destinations_hit = min(ranked)
        for code in path:
            for name in covered:
                covered[name] |= data.masks[code][name]
        chosen.update(path)
        pending_rings.difference_update(rings_hit)
        pending_destinations.difference_update(destinations_hit)
        steps.append(list(path))
    return _summary(data, chosen, covered) | {"assembly_steps": steps, "unserved_destinations": sorted(pending_destinations),
                                             "omitted_requested_rings": sorted(pending_rings), "seed_id": seed}


def _load_portfolio(library, route_ids, audit):
    network = deepcopy(library)
    retained = set(route_ids)
    network["lines"] = {code: line for code, line in network["lines"].items() if code in retained}
    residential_layouts._rebuild_memberships(network)
    network["station_site_links"] = [link for link in network.get("station_site_links", [])
                                     if all(code in network["stations"] for code in link["station_ids"])]
    for field in ("straight_through_layout", "short_route_withdrawal", "third_ring_through", "third_orbital"):
        network.pop(field, None)
    network["topology"] = holistic_network.validate(network)
    network["physical_accepted"] = network["operating_timetable_validated"] = False
    network["portfolio_assembly"] = {
        "source_library_candidate_id": library["candidate_id"], "source_library_evaluation_id": library["evaluation_id"],
        "assembled_line_ids": list(route_ids), "omitted_library_line_ids": sorted(library["lines"].keys() - retained),
        "required_ring_ids": audit["required_ring_ids"], "walk_m": audit["walk_m"],
    }
    source = Path(__file__).resolve()
    network.setdefault("source_sha256", {})[source.relative_to(central_access.ROOT).as_posix()] = central_access.digest(source)
    return rail_consolidation.refresh_interchange_names(network)


def assemble(library, graph, *, populations, destinations, required_ring_ids=(), excluded_route_ids=(),
             max_lines=24, walk_m=1300, max_trials=6, prepared=None):
    """Construct a connected planning option without requiring any inherited line.

    Named destinations are mandatory street walks at the specified bound.
    Rings are mandatory only in scenarios requesting them. The two-change
    proxy counts route interchanges and is followed by the timetable assignment.
    """
    rings, excluded = set(required_ring_ids), set(excluded_route_ids)
    if (not isinstance(max_lines, int) or not isinstance(max_trials, int) or max_trials < 1 or max_lines < 1
            or not excluded <= library["lines"].keys() or not rings <= library["lines"].keys() - excluded
            or any(not library["lines"][ring]["loop"] for ring in rings)):
        raise ValueError("Invalid line, ring or bounded trial request")
    data = prepared if prepared is not None else screen(
        library, graph, populations=populations, destinations=destinations, walk_m=walk_m)
    if (data.library_id != library["evaluation_id"] or data.walk_m != walk_m or data.graph_matrix is not graph[1]
            or data.destinations != _destinations(destinations) or data.population_weights.keys() != populations.keys()
            or any(data.population_weights[key] is not pop.counts for key, pop in populations.items())):
        raise ValueError("Prepared route masks belong to a different portfolio evaluation")
    available = sorted(data.route_km.keys() - excluded)
    if excluded:
        data = RouteScreen(data.library_id, data.walk_m, {
            code: tuple(other for other in data.neighbours[code] if other not in excluded) for code in available},
            {code: data.route_km[code] for code in available}, data.destinations, data.destination_walks,
            data.population_weights, data.masks, data.graph_source, data.graph_matrix)
    destination_routes = {dest: [code for code in available if dest in data.destination_walks[code]]
                          for dest in data.destinations}
    unreachable = [dest for dest, codes in destination_routes.items() if not codes]
    coverage = {code: sum(float(weights[data.masks[code][name]].sum()) / float(weights.sum())
                          for name, weights in data.population_weights.items()) for code in available}
    ranked = [
        sorted(available, key=lambda code: (-len(data.destination_walks[code]), -coverage[code], code)),
        sorted(available, key=lambda code: (-coverage[code], code)),
        sorted(available, key=lambda code: (-coverage[code] / data.route_km[code], code)),
    ]
    trials = []
    option_count = 0 if unreachable else min(max_trials, len(available) * len(ranked))
    for index in range(option_count):
        variant, offset = index % len(ranked), index // len(ranked)
        seed = ranked[variant][offset]
        power = (.7, 0., 1.)[variant]
        trials.append(_trial(data, seed, rings, max_lines, power) | {"route_km_exponent": power})
    eligible = [row for row in trials if not row["unserved_destinations"] and not row["omitted_requested_rings"]]
    best = min(eligible, key=lambda row: (
        -sum(value["share_pct"] for value in row["population_access"].values()),
        -sum(row["two_change_topological_proxy_pct"].values()), row["route_km"], row["route_ids"]), default=None)
    audit = {
        "source_library_candidate_id": library["candidate_id"], "source_library_evaluation_id": library["evaluation_id"],
        "required_ring_ids": sorted(rings), "excluded_route_ids": sorted(excluded),
        "walk_m": walk_m, "max_lines": max_lines, "max_trials": max_trials,
        "street_graph": data.graph_source, "required_destination_coordinates": data.destinations,
        "library_destination_route_options": destination_routes, "destinations_outside_all_route_catchments": unreachable,
        "trials": trials, "chosen": best,
        "rejection_reason": None if best else (
            "No eligible route reaches " + ", ".join(unreachable) + "." if unreachable
            else "No bounded connected portfolio reaches every requested destination and ring."),
    }
    if best is None:
        return None, audit
    return _load_portfolio(library, best["route_ids"], audit), audit
