"""Compare passenger use of the two Baghdad rings at a fixed train-km budget."""

from dataclasses import asdict
from hashlib import sha256

import numpy as np
from scipy.sparse.csgraph import dijkstra

from . import central_access, holistic_access, holistic_journeys as journeys, holistic_network, ring_grid_journeys


RING_BITS = {"M09": 1, "M15": 2}
BATCH_ORIGINS = 32


def _headways(network, train_km_day, hours, ring_multiplier):
    """Buy the ring frequency change with the other lines' train-km."""
    lengths = {code: line["one_way_km"] for code, line in network["lines"].items()}
    uniform_rate = train_km_day / (2 * hours * 3600 * sum(lengths.values()))
    ring_km = sum(km for code, km in lengths.items() if code in RING_BITS)
    other_km = sum(lengths.values()) - ring_km
    other_multiplier = (1 - (ring_multiplier - 1) * ring_km / other_km
                        if ring_km and other_km else 1.)
    if not np.isfinite(ring_multiplier) or ring_multiplier <= 0 or other_multiplier <= 0:
        raise ValueError("Ring priority must leave a positive frequency on every route")
    if ring_km and not other_km and ring_multiplier != 1:
        raise ValueError("Ring priority requires other routes to rebalance the operating budget")
    return {code: 1 / (uniform_rate * (ring_multiplier if code in RING_BITS else other_multiplier))
            for code in lengths}


def _trace(route, weights):
    """Record ridden rings and line changes along the least-cost path for each ordered pair."""
    costs = np.full(weights.shape, np.inf)
    boards = np.zeros(weights.shape, dtype=np.int16)
    ring_use = np.zeros(weights.shape, dtype=np.uint8)
    rides = np.zeros(len(route.segments))
    segment_bits = np.array([RING_BITS.get(segment["line"], 0) for segment in route.segments], dtype=np.uint8)
    for start in range(0, len(route.origins), BATCH_ORIGINS):
        batch = slice(start, start + BATCH_ORIGINS)
        distances, previous = dijkstra(route.matrix, indices=route.origins[batch], return_predecessors=True)
        costs[batch] = distances[:, route.destinations]
        row, destination = np.nonzero(np.isfinite(costs[batch]) & (weights[batch] > 0))
        trip = (start + row) * weights.shape[1] + destination
        nodes = route.destinations[destination]
        while len(nodes):
            segment = route.ride_segment[nodes]
            ridden = segment >= 0
            ring_use.flat[trip[ridden]] |= segment_bits[segment[ridden]]
            rides += np.bincount(segment[ridden], weights=weights.flat[trip[ridden]], minlength=len(rides))
            predecessor = previous[row, nodes]
            departing = np.flatnonzero(route.board_line[nodes] >= 0)
            arrival_segment = route.ride_segment[predecessor[departing]]
            incoming_line = np.full(len(departing), -1)
            incoming = arrival_segment >= 0
            incoming_line[incoming] = route.segment_line[arrival_segment[incoming]]
            changed = incoming_line != route.board_line[nodes[departing]]
            boards.flat[trip[departing[changed]]] += 1
            active = predecessor >= 0
            nodes, row, trip = predecessor[active], row[active], trip[active]
    return costs, boards, ring_use, rides


def _usage(weights, boards, ring_use):
    total = weights.sum()
    served = weights[boards > 0].sum()
    use = {"M09": (ring_use & RING_BITS["M09"]) > 0, "M15": (ring_use & RING_BITS["M15"]) > 0,
           "both": ring_use == sum(RING_BITS.values()), "either": ring_use > 0}
    return {code: {"share_of_all_pct": journeys._percentage(weights[mask].sum(), total),
                   "share_of_served_pct": journeys._percentage(weights[mask].sum(), served),
                   "at_most_two_changes_share_of_all_pct": journeys._percentage(
                       weights[mask & (boards > 0) & (boards <= 3)].sum(), total)}
            for code, mask in use.items()}


def _case(network, access, sample, cohorts, assumptions, headways):
    route = journeys._assignment_graph(network, access, assumptions, headways)
    costs, boards, ring_use, rides = _trace(route, sample.weights)
    penalty = assumptions.transfer_penalty_s
    elapsed = np.where(boards > 0, costs - (boards - 1) * penalty, np.inf)
    line_freq_km = {code: 2 * line["one_way_km"] / headways[code] * assumptions.operating_hours_day * 3600
                    for code, line in network["lines"].items()}
    pressure = rides * np.asarray([headways[segment["line"]] for segment in route.segments])
    busiest = {}
    for code in route.line_ids:
        segment = max((index for index, row in enumerate(route.segments) if row["line"] == code),
                      key=rides.__getitem__)
        busiest[code] = route.segments[segment] | {
            "share_of_all_od_pct": journeys._percentage(rides[segment], sample.weights.sum()),
            "relative_load_per_departure_index": round(float(pressure[segment] * 100 / assumptions.headway_s), 6),
        }
    return {
        "candidate_id": network.get("candidate_id"),
        "closed_ring_alignments": [code for code in RING_BITS
                                   if code in network["lines"] and network["lines"][code]["loop"]],
        "service": {"running_train_km_day": round(sum(line_freq_km.values()), 2),
                    "line_headways_s": {code: round(headway, 3) for code, headway in sorted(headways.items())},
                    "line_running_train_km_day": {code: round(km, 2) for code, km in sorted(line_freq_km.items())}},
        "journeys": ring_grid_journeys._trip_metrics(sample.weights, costs, boards, penalty),
        "ring_use": _usage(sample.weights, boards, ring_use),
        "cohorts": {name: {"journeys": ring_grid_journeys._trip_metrics(weights, costs, boards, penalty),
                          "ring_use": _usage(weights, boards, ring_use)} for name, weights in cohorts.items()},
        "peak_directed_segments": busiest,
        "network_peak_relative_load_per_departure_index": round(float(pressure.max() * 100 / assumptions.headway_s), 6),
    }, elapsed


def compare(networks, *, reference, paired_reference=None, graph=None, population=None,
            assumptions=journeys.JourneyAssumptions(), ring_frequency_multipliers=(1., 1.25), housing=None):
    """Use common OD weights and daily running train-km for layout and frequency trials."""
    if reference not in networks:
        raise ValueError("Include the matched-service reference in the assignment")
    if paired_reference is None:
        paired_reference = reference
    if paired_reference not in networks:
        raise ValueError("Include the paired journey-time reference in the assignment")
    if tuple(ring_frequency_multipliers[:1]) != (1.,) or len(ring_frequency_multipliers) != 2:
        raise ValueError("Provide a uniform and a single ring-priority frequency multiplier")
    for network in networks.values():
        holistic_network.validate(network)
    if graph is None:
        graph = central_access.walking_graph()
    if population is None:
        population = holistic_access.load_population("worldpop-2026", graph)
    sample = journeys.sample_demand(population, assumptions)
    cohorts = ring_grid_journeys._cohort_weights(sample)
    access = journeys._street_access(networks, sample, graph, assumptions.walk_limit_m)
    hours = assumptions.operating_hours_day
    train_km_day = (2 * sum(line["one_way_km"] for line in networks[reference]["lines"].values())
                    / assumptions.headway_s * hours * 3600)
    variants, priority_variants = {}, {}
    wide_angle_weights = cohorts[ring_grid_journeys.WIDE_ANGLE_COHORT]
    for name in sorted(networks, key=lambda key: (key != paired_reference, key)):
        network = networks[name]
        for multiplier, results in zip(ring_frequency_multipliers, (variants, priority_variants), strict=True):
            if results is priority_variants and not all(
                network["lines"].get(code, {}).get("loop") for code in RING_BITS
            ):
                continue
            headways = _headways(network, train_km_day, hours, multiplier)
            row, elapsed = _case(network, access[name], sample, cohorts, assumptions, headways)
            if row["service"]["running_train_km_day"] != round(train_km_day, 2):
                raise ValueError(f"{name} moved away from the common train-km budget")
            if results is variants:
                uniform_elapsed = elapsed
                if name == paired_reference:
                    reference_elapsed = elapsed
            row["paired_vs_reference"] = ring_grid_journeys._paired_metrics(
                sample.weights, elapsed, reference_elapsed)
            row["paired_wide_angle_vs_reference"] = ring_grid_journeys._paired_metrics(
                wide_angle_weights, elapsed, reference_elapsed)
            if results is priority_variants:
                row["paired_vs_same_layout_uniform"] = ring_grid_journeys._paired_metrics(
                    sample.weights, elapsed, uniform_elapsed)
                row["paired_wide_angle_vs_same_layout_uniform"] = ring_grid_journeys._paired_metrics(
                    wide_angle_weights, elapsed, uniform_elapsed)
            results[name] = row
    demand = {"source": sample.source, "tile_count": len(sample.people),
              "ordered_od_pairs": int(np.count_nonzero(sample.weights)),
              "modelled_population": round(float(sample.people.sum())),
              "weights_sha256": sha256(sample.weights.astype("<f8", copy=False).tobytes()).hexdigest(),
              "coordinates_lon_lat_and_tile_people": np.column_stack((sample.coordinates, sample.people)).tolist()}
    demand["sample_id"] = sha256(central_access.encode(demand)).hexdigest()
    result = {"assumptions": asdict(assumptions) | {
        "matched_service_reference": reference,
        "paired_journey_reference": paired_reference,
        "ring_priority_frequency_multiplier": ring_frequency_multipliers[1],
        "street_source": graph[4], "street_snap_limit_m": central_access.SNAP_M,
        "demand_basis": "Common synthetic population-weighted OD pairs and exponential distance decay.",
        "ring_usage_basis": "A journey uses M09 or M15 if its least-generalised-cost path traverses at least one "
                            "directed segment of that route. Both-ring journeys traverse a segment of each route. "
                            "Alignment closure is recorded for each variant.",
        "service_basis": "Continuous bidirectional all-stop service, half-headway waits and equal running train-km. "
                         "The ring frequency increase is paid for by a uniform proportional frequency reduction "
                         "on the other routes. Depot moves and turnaround work are excluded.",
        "load_basis": "Synthetic OD share multiplied by the ratio of a route's headway to the reference headway.",
    }, "demand_sample": demand, "variants": variants, "ring_priority_variants": priority_variants}
    if housing is not None:
        result["housing_max_two_changes"] = {"sample_id": housing["demand_sample"]["sample_id"], "variants": {}}
        for name, row in variants.items():
            housing_row = housing["variants"][name]
            if (housing_row["candidate_id"] != row["candidate_id"]
                    or housing_row["service"]["running_train_km_day"] != row["service"]["running_train_km_day"]):
                raise ValueError(f"Housing result for {name} needs matching geometry and train-km")
            result["housing_max_two_changes"]["variants"][name] = {
                "reachable_share_of_all_pct": housing_row["journeys"]["reachable_with_at_most_share_of_all_pct"]["2"],
                "uniform_elapsed_p90_min": housing_row["journeys"]["elapsed_p90_min"],
            }
    return result
