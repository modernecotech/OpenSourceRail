"""Compare Baghdad trunk networks, dense-gap corridors and station locations together."""

from collections import Counter
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from . import central_access, holistic_access, holistic_network, holistic_pathways, rail_duplication


def priority_areas(population, walking, *, area_m, count):
    """Hold the same high-population deficit areas fixed in every comparison."""
    cells, index = np.unique(np.floor(population.xy / area_m).astype(int), axis=0, return_inverse=True)
    missed = np.bincount(index, weights=population.counts * (walking > 1200), minlength=len(cells))
    order = np.argsort(-missed, kind="stable")[:count]
    rows = [{"id": f"G-{cells[i, 0]}-{cells[i, 1]}", "before_unserved": round(float(missed[i])),
             "bounds_wsen": [float((cells[i, axis] + shift) * area_m / holistic_network.LOCAL_METRES[axis])
                             for axis, shift in ((0, 0), (1, 0), (0, 1), (1, 1))]}
            for i in order if missed[i] > 0]
    return rows, [index == i for i in order if missed[i] > 0]


def _walk(network, graph, population):
    sites = {code: row["coordinates"] for code, row in network["stations"].items()}
    return holistic_access.walk_to_station(sites, graph, population)[0]


def _served(population, walking):
    return float(population.counts[walking <= 1200].sum())


def _dense_gain(population, original, walking, priority):
    return float(population.counts[priority & (walking <= 1200)].sum()
                 - population.counts[priority & (original <= 1200)].sum())


def _overlaps(network, screen):
    geometry = rail_duplication.screen(network["lines"], **screen)
    lengths = Counter()
    for row in geometry["runs"]:
        lengths[row["kind"]] += row["length_m"]
    return geometry, {"nearby_parallel_m": round(lengths["nearby_parallel"], 1),
                      "common_alignment_m": round(lengths["common_alignment"], 1),
                      "terminal_fans": len({tuple(row["lines"]) for row in geometry["runs"]
                                            if row["terminal_codeparture"]})}


def _close_site_pairs(network):
    points = central_access._points([row["coordinates"] for row in network["stations"].values()])
    return len(cKDTree(points).query_pairs(280, output_type="ndarray"))


def _infill(network, walking, priority, population, graph, context, policy):
    options = holistic_access.opportunities(network, population, walking, graph, policy["infill_sample_m"],
                                            policy["infill_spacing_m"], context, target_pixels=priority)
    selected = holistic_access.rank_stations(options, population.counts, walking, policy["infill_spacing_m"],
                                             policy["infill_limit"], primary_m=1200)
    # A second set of entrances beside an existing station would recreate the former clustering.
    prior_centres = central_access._points([row["coordinates"] for row in network["stations"].values()])
    tracks = {code: holistic_network.Track(row["geometry"]) for code, row in network["lines"].items()}
    accepted = []
    for row in selected:
        point = central_access._points([tracks[row["line_id"]].at(row["chainage_km"])])[0]
        if np.linalg.norm(prior_centres - point, axis=1).min() < 280:
            continue
        prior_centres = np.vstack((prior_centres, point))
        accepted.append(row)
    if accepted:
        network = holistic_network.insert_stations(network, accepted)
        walking = _walk(network, graph, population)
    return network, walking, accepted


def _gap_routes(network, walking, population, graph, context, areas, priority, masks, policy, km_limit, demand, reference):
    from . import network_gap_routes

    options = network_gap_routes.generate(network, context, graph,
                                          coverage_cells=holistic_access.coverage_cells(population, walking),
                                          gap_ids={row["id"] for row in areas},
                                          max_candidates=policy["gap_candidate_limit"])
    chosen, trials, new_lines = [], {}, {}
    if not options:
        return network, walking, chosen, trials
    for _ in range(policy["gap_routes_per_layout"]):
        comparisons = []
        largest_gap = max(masks, key=lambda mask: float(population.counts[mask & (walking > 1200)].sum()))
        for option in options:
            code = option["id"]
            if code in trials and trials[code]["status"] != "compared":
                continue
            km = holistic_network.Track(option["geometry"]).km
            row = {"route_km": round(km, 3), "screening": option["screening"],
                   "geometry": option["geometry"], "terminal_ids": option["terminal_ids"]}
            if network["topology"]["route_km"] + km > km_limit + .01:
                trials[code] = row | {"status": "route length budget"}
                continue
            if new_lines and network_gap_routes.parallel_runs(option, new_lines):
                trials[code] = row | {"status": "parallel to a selected gap route"}
                continue
            try:
                extended = holistic_network.insert_through_lines(network, [option], graph=graph, context=context,
                                                                 connect_through_lines=True)
            except ValueError as error:
                trials[code] = row | {"status": str(error)}
                continue
            coverage = _walk(extended, graph, population)
            dense = _dense_gain(population, walking, coverage, priority)
            metro = _served(population, coverage) - _served(population, walking)
            largest_gain = _dense_gain(population, walking, coverage, largest_gap)
            trials[code] = row | {"status": "compared", "priority_people_gain": round(dense),
                                  "metro_people_gain": round(metro), "largest_gap_people_gain": round(largest_gain)}
            if dense >= 5000 and metro >= 5000:
                comparisons.append((-(dense + largest_gain + metro * .35) / km, -(dense + largest_gain),
                                    km, code, extended, coverage))
        if not comparisons:
            break
        best_walks = sorted(comparisons, key=lambda item: item[:4])[:12]
        results = holistic_pathways.compare({row[3]: row[4] for row in best_walks}, **demand)["variants"]
        for _, _, _, code, _, _ in best_walks:
            trials[code]["journey_effects"] = _effects(reference, results[code])
        # Exact journeys break the coverage shortlist. A route can restore a
        # journey without making a further home eligible for the walking test.
        def rank(item):
            _, dense_inverse, km, code, *_ = item
            impact = trials[code]["journey_effects"]
            weighted_loss = (max(impact["two_change_loss_pp"], 0) + .5 * max(impact["one_change_loss_pp"], 0)
                             + .25 * max(impact["destination_loss_pp"], 0))
            return (weighted_loss + (dense_inverse + 1500 * km) / 40_000, *item[:4])

        _, _, _, code, network, walking = min(best_walks, key=rank)
        trials[code]["status"] = "selected"
        chosen.append(code)
        new_lines[code] = network["lines"][code]
    return network, walking, chosen, trials


def _effects(baseline, candidate):
    before, after = baseline["journeys"], candidate["journeys"]
    before_transfers = before["reachable_with_at_most_share_of_all_pct"]
    after_transfers = after["reachable_with_at_most_share_of_all_pct"]
    return {"two_change_loss_pp": round(before_transfers["2"] - after_transfers["2"], 4),
            "one_change_loss_pp": round(before_transfers["1"] - after_transfers["1"], 4),
            "destination_loss_pp": round(max(row["served_share_pct"] - candidate["destinations"][key]["served_share_pct"]
                                             for key, row in baseline["destinations"].items()), 4),
            "p90_increase_min": round(after["elapsed_p90_min"] - before["elapsed_p90_min"], 4)
            if after["elapsed_p90_min"] is not None else None}


def _candidate_status(row, policy, reference):
    failures = [key for key, value in row["journey_effects"].items() if value is None or value > policy[f"max_{key}"]]
    if row["route_km"] > reference["route_km"]:
        failures.append("route_km")
    if row["overlaps"]["terminal_fans"] > reference["overlaps"]["terminal_fans"]:
        failures.append("terminal_fans")
    if row["overlaps"]["common_alignment_m"] > reference["overlaps"]["common_alignment_m"]:
        failures.append("common_alignment")
    if row["overlap_reduction_pct"] < policy["minimum_overlap_reduction_pct"]:
        failures.append("overlap_reduction")
    if row["gap_people_gain"] < policy["minimum_gap_population_gain"]:
        failures.append("dense_gap_access")
    if row["walking_gain_pp"] < policy["minimum_city_access_gain_pp"]:
        failures.append("metropolitan_walking_access")
    if not row["station_actions"] or row["close_site_pairs"] >= reference["close_site_pairs"]:
        failures.append("station_consolidation")
    return failures


def evaluate(network, walking, baseline_assignment, population, graph, context, demand, config, *, protected_stations=()):
    from . import network_station_sites, network_trunks

    policy = config["network_redesign"]
    screen = config["corridor_screen"]
    demand = dict(demand, street_access_cache={})
    areas, masks = priority_areas(population, walking, area_m=policy["area_m"], count=policy["priority_areas"])
    priority = np.logical_or.reduce(masks) if masks else np.zeros(len(walking), dtype=bool)
    before_geometry, overlaps = _overlaps(network, screen)
    reference = {"candidate_id": network["candidate_id"], **network["topology"], "overlaps": overlaps,
                 "close_site_pairs": _close_site_pairs(network),
                 "walking_share_pct": _served(population, walking) / population.counts.sum() * 100}
    alternatives = network_trunks.alternatives(network, protected_stations=protected_stations)
    layouts, sketches, outcomes = {}, {}, {}
    for key, option in alternatives.items():
        candidate = option.get("network")
        if candidate is None:
            outcomes[key] = {"name": option["name"], "failed": [option.get("rejection_reason", "invalid trunk graph")]}
            continue
        if candidate["candidate_id"] == network["candidate_id"]:
            continue
        candidate_walk = _walk(candidate, graph, population)
        _, counters = _overlaps(candidate, screen)
        sketches[key] = (candidate, candidate_walk, counters)
        outcomes[key] = {"name": option["name"], **candidate["topology"], "overlaps": counters,
                         "trunk_metro_walk_pct": round(_served(population, candidate_walk) / population.counts.sum() * 100, 5),
                         "trunk_actions": option.get("actions", []), "failed": ["outside the bounded corridor trial"]}
    # Carry the best access-first skeletons and a lower-overlap option into design refinement.
    suitable = [key for key in sketches if outcomes[key]["overlaps"]["nearby_parallel_m"] <=
                overlaps["nearby_parallel_m"] * (1 - policy["minimum_overlap_reduction_pct"] / 100) + .1]
    best_access = sorted(suitable, key=lambda key: (-outcomes[key]["trunk_metro_walk_pct"], key))
    best_balance = sorted(suitable, key=lambda key: (-outcomes[key]["trunk_metro_walk_pct"]
                          + outcomes[key]["overlaps"]["nearby_parallel_m"] / 10_000, key))
    shortlist = list(dict.fromkeys([*best_access[:3], *best_balance[:2]]))
    for key in shortlist:
        candidate, candidate_walk, _ = sketches[key]
        candidate, candidate_walk, infill = _infill(candidate, candidate_walk, priority, population, graph, context, policy)
        candidate, _, added, gap_trials = _gap_routes(candidate, candidate_walk, population, graph, context, areas,
                                                      priority, masks, policy, reference["route_km"], demand, baseline_assignment)
        candidate, station_audit = network_station_sites.consolidate(candidate, graph=graph, context=context,
                                                                     protected_stations=protected_stations)
        candidate_walk = _walk(candidate, graph, population)
        geometry, counters = _overlaps(candidate, screen)
        walk_gain = _served(population, candidate_walk) / population.counts.sum() * 100 - reference["walking_share_pct"]
        outcomes[key].update({**candidate["topology"], "candidate_id": candidate["candidate_id"], "overlaps": counters,
                              "overlap_reduction_pct": round(100 * (1 - counters["nearby_parallel_m"] /
                                                                     max(overlaps["nearby_parallel_m"], 1)), 5),
                              "walking_gain_pp": round(walk_gain, 5), "gap_people_gain": round(
                                  _dense_gain(population, walking, candidate_walk, priority)), "gap_route_ids": added,
                              "gap_trials": gap_trials, "infill": infill, "station_actions": station_audit["actions"],
                              "close_site_pairs": _close_site_pairs(candidate),
                              "station_audit": station_audit})
        layouts[key] = (candidate, candidate_walk, geometry)
    trial_statistics = holistic_pathways.compare({key: row[0] for key, row in layouts.items()}, **demand)["variants"] if layouts else {}
    for key, stats in trial_statistics.items():
        outcomes[key]["journeys"] = stats["journeys"]
        outcomes[key]["journey_effects"] = _effects(baseline_assignment, stats)
        outcomes[key]["failed"] = _candidate_status(outcomes[key], policy, reference)
    eligible = [key for key in layouts if not outcomes[key]["failed"]]
    selected = min(eligible, key=lambda key: (-outcomes[key]["gap_people_gain"], -outcomes[key]["walking_gain_pp"],
                   outcomes[key]["overlaps"]["nearby_parallel_m"], outcomes[key]["route_km"], key)) if eligible else None
    selected_network, selected_walk, final_geometry = layouts[selected] if selected else (network, walking, before_geometry)
    for row, mask in zip(areas, masks, strict=True):
        row["revised_unserved"] = round(float(population.counts[mask & (selected_walk > 1200)].sum()))
    if selected:
        source = Path(__file__)
        selected_network["source_sha256"][source.relative_to(central_access.ROOT).as_posix()] = central_access.digest(source)
        selected_network = holistic_network._identity(selected_network)
    return selected_network, selected_walk, trial_statistics.get(selected, baseline_assignment), {
        "selected": selected, "reference": reference, "priority_areas": areas, "options": outcomes,
        "before_geometry": before_geometry, "final_geometry": final_geometry,
    }
