"""Screen short Baghdad rail withdrawals against cumulative pedestrian access."""

from copy import deepcopy
from hashlib import sha256
from math import isfinite
from pathlib import Path

import numpy as np
from scipy.sparse.csgraph import dijkstra

from . import central_access, holistic_network, network_station_sites, residential_layouts
from .ring_grid_comparison import PROTECTED as REFERENCE_ANCHORS


PRIMARY_WALK_M = 1300
WALK_LIMITS_M = (PRIMARY_WALK_M, 1200, 800)


def _coordinates(network):
    return {stop: station["coordinates"] for stop, station in network["stations"].items()}


def _walks(stations, graph, populations):
    distances, unmatched = central_access.distances_from_stops(stations, graph)
    walks = [np.where(pop.offsets_m <= central_access.SNAP_M,
                      distances[pop.nodes] + pop.offsets_m, np.inf) for pop in populations]
    return walks, unmatched


def _population_change(population, baseline, revised):
    rows = {}
    for limit in WALK_LIMITS_M:
        before, after = baseline <= limit, revised <= limit
        people = population.counts
        lost, gained = before & ~after, after & ~before
        gross_loss, gross_gain = float(people[lost].sum()), float(people[gained].sum())
        rows[str(limit)] = {
            "baseline_estimated_residents": float(people[before].sum()),
            "retained_estimated_residents": float(people[after].sum()),
            "gross_estimated_residents_lost": gross_loss,
            "gross_estimated_residents_gained": gross_gain,
            "net_estimated_resident_change": gross_gain - gross_loss,
            "gross_loss_pct_of_study_population": 100 * gross_loss / float(people.sum()),
            "largest_loss_cells_approx_1_km": residential_layouts._loss_locations(population, lost),
        }
    return rows


def _coverage(populations, baseline, revised):
    return {
        name: _population_change(pop, before, after)
        for (name, pop), before, after in zip(populations, baseline, revised, strict=True)
    }


def _closure_paths(closed, current_stations, original_stations, graph, snap, max_walk_m):
    """Route each closed station to a still-open platform on the retained street graph."""
    raw, matrix, _, _, _ = graph
    terminals = [(station, result) for station, point in sorted(current_stations.items())
                 if (result := snap(tuple(point))) is not None]
    paths, missing = {}, []
    if terminals:
        terminal_nodes = np.array([node for _, (node, _) in terminals])
        terminal_offsets = np.array([offset for _, (_, offset) in terminals])
    for stop in sorted(closed):
        source = snap(tuple(original_stations[stop]))
        if source is None or not terminals or source[1] > max_walk_m:
            missing.append(stop)
            continue
        start, start_offset = source
        distances, previous = dijkstra(matrix, directed=True, indices=start,
                                       limit=max_walk_m - start_offset, return_predecessors=True)
        walks = distances[terminal_nodes] + start_offset + terminal_offsets
        best = int(np.argmin(walks))
        if walks[best] > max_walk_m:
            missing.append(stop)
            continue
        station, (end, _) = terminals[best]
        nodes = [end]
        while nodes[-1] != start:
            nodes.append(int(previous[nodes[-1]]))
        geometry = holistic_network._concatenate(
            [original_stations[stop]],
            [[float(raw["lon"][node]), float(raw["lat"][node])] for node in reversed(nodes)],
            [current_stations[station]],
        )
        paths[stop] = {"replacement_station_id": station, "walk_m": round(float(walks[best]), 2),
                       "geometry": geometry, "snap_connectors_surveyed": False}
    return paths, missing


def _drop(network, line_id):
    trial = deepcopy(network)
    del trial["lines"][line_id]
    if not trial["lines"]:
        raise ValueError("The trial would withdraw every service.")
    residential_layouts._rebuild_memberships(trial)
    missing_links = [link["id"] for link in network.get("station_site_links", [])
                     if set(link["station_ids"]) - trial["stations"].keys()]
    if missing_links:
        raise ValueError("The trial would remove a mapped walking interchange: " + ", ".join(missing_links))
    trial["topology"] = holistic_network.validate(trial)
    return trial


def prune(network, graph, *, protected_stations, protected_lines, populations=(), reference=None, context=None,
          max_route_km=8, max_closed_station_walk_m=800, max_population_loss_pct=0.0, max_trials=20):
    """Try whole-route withdrawal in increasing length order under declared access bounds.

    Population may be a mapping from source ID to retained Population, or a
    sequence of Population objects. The percentage bound applies independently
    to gross residential loss at 1,300 m in each dataset, against this layout
    before withdrawal. The 1,200 m and 800 m diagnostics and comparison with
    the published reference report their own gross loss.
    """
    if (not all(isfinite(v) and v >= 0 for v in (
            max_route_km, max_closed_station_walk_m, max_population_loss_pct))
            or max_population_loss_pct > 100 or not isinstance(max_trials, int) or max_trials < 0):
        raise ValueError("Invalid withdrawal trial bounds")
    starting_topology = holistic_network.validate(network)
    anchor_source = network if reference is None else reference
    protected_stations = set(protected_stations) | (set(REFERENCE_ANCHORS) & anchor_source["stations"].keys())
    protected_lines = set(protected_lines) | ({"C1"} & network["lines"].keys())
    if protected_stations - network["stations"].keys() or protected_lines - network["lines"].keys():
        raise ValueError("The input layout is missing requested protected stations or railway lines")
    if reference is not None and "C1" in reference["lines"]:
        original_airport_calls = reference["lines"]["C1"]["station_ids"]
        airport_calls = network["lines"].get("C1", {}).get("station_ids", [])
        original_airport_sites = set(original_airport_calls)
        if [stop for stop in airport_calls if stop in original_airport_sites] != original_airport_calls:
            raise ValueError("The input layout changes published Airport-route calls")
    if hasattr(populations, "items"):
        populations = tuple(sorted(populations.items()))
    else:
        populations = tuple((pop.source["dataset"], pop) for pop in populations)
    if any(not np.isfinite(pop.counts).all() or (pop.counts < 0).any() or pop.counts.sum() <= 0
           for _, pop in populations) or len({name for name, _ in populations}) != len(populations):
        raise ValueError("Each retained population dataset needs a unique identity and positive valid weights")
    datasets = [pop for _, pop in populations]
    original_stations = _coordinates(network)
    original_walks, unmatched = _walks(original_stations, graph, datasets) if datasets else ([], None)
    final_walks = original_walks
    snap = network_station_sites._street_paths(graph, network_station_sites._water_tree(context))[0] if context else None

    trials = sorted((line["one_way_km"], code) for code, line in network["lines"].items()
                    if code not in protected_lines and not line["loop"] and line["one_way_km"] <= max_route_km)
    actions, rejected, closure_paths = [], [], {}
    revised = network
    for route_km, code in trials[:max_trials]:
        row = {"line_id": code, "one_way_km": round(route_km, 3)}
        try:
            trial = _drop(revised, code)
        except ValueError as error:
            rejected.append(row | {"reason": str(error)})
            continue
        stations = _coordinates(trial)
        closed = original_stations.keys() - stations.keys()
        if missing := protected_stations & closed:
            rejected.append(row | {"reason": "Protected calls would close.", "station_ids": sorted(missing)})
            continue
        paths, walks, walk_unmatched = {}, original_walks, unmatched
        if closed:
            if snap is None or not datasets:
                rejected.append(row | {"reason": "Station closure requires street geometry and retained populations.",
                                       "station_ids": sorted(closed)})
                continue
            paths, missing = _closure_paths(closed, stations, original_stations, graph, snap, max_closed_station_walk_m)
            if missing:
                rejected.append(row | {"reason": "No remaining station within the street walking bound.",
                                       "station_ids": missing})
                continue
            walks, walk_unmatched = _walks(stations, graph, datasets)
        coverage = _coverage(populations, original_walks, walks)
        if any(data[str(PRIMARY_WALK_M)]["gross_loss_pct_of_study_population"] > max_population_loss_pct
               for data in coverage.values()):
            rejected.append(row | {"reason": "Cumulative gross residential loss exceeds the 1,300 m bound.",
                                   "coverage_vs_unpruned": coverage})
            continue
        actions.append(row | {"action": "withdraw_line", "removed_route_km": row["one_way_km"],
                              "closed_stations": sorted(revised["stations"].keys() - stations.keys()),
                              "retained_station_calls_on_other_lines": [
                                  stop for stop in revised["lines"][code]["station_ids"] if stop in stations]})
        revised, final_walks, unmatched, closure_paths = trial, walks, walk_unmatched, paths

    audit = {
        "parent_candidate_id": network["candidate_id"],
        "reference_candidate_id": reference["candidate_id"] if reference is not None else None,
        "bounds": {"max_route_km": max_route_km, "max_closed_station_walk_m": max_closed_station_walk_m,
                   "max_population_loss_pct_at_1300_m": max_population_loss_pct, "max_trials": max_trials,
                   "protected_stations": sorted(protected_stations), "protected_lines": sorted(protected_lines)},
        "actions": actions, "rejected": rejected, "unexamined_line_ids": [code for _, code in trials[max_trials:]],
        "before": starting_topology,
        "after": revised["topology"] if actions else starting_topology,
        "cumulative_station_replacement_paths": closure_paths,
        "coverage_vs_unpruned": _coverage(populations, original_walks, final_walks),
        "unmatched_retained_stations": unmatched,
        "station_path_snap_limit_m": network_station_sites.MAX_SNAP_M,
        "street_graph": graph[4],
        "journey_times_transfers_capacity_validated": False,
        "physical_access_validated": False,
    }
    if reference is not None and datasets:
        reference_walks, _ = _walks(_coordinates(reference), graph, datasets)
        audit["coverage_vs_published"] = _coverage(populations, reference_walks, final_walks)
    if actions:
        revised["short_route_withdrawal"] = audit
        revised["physical_accepted"] = revised["operating_timetable_validated"] = False
        source = Path(__file__).resolve()
        revised.setdefault("source_sha256", {})[source.relative_to(central_access.ROOT).as_posix()] = (
            sha256(source.read_bytes()).hexdigest())
        holistic_network._identity(revised)
    return revised, audit
