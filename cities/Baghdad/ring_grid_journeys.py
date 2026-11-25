"""Evaluate concentric-ring and straight-line plans on the same Baghdad OD sample."""

from dataclasses import asdict
from hashlib import sha256

import numpy as np

from . import central_access, holistic_access, holistic_journeys as journeys, holistic_network


WIDE_ANGLE_DEG = 45
WIDE_ANGLE_COHORT = "wide-angle inter-district"


def _cohort_weights(sample):
    groups = {name: sample.cohorts == index for index, name in enumerate(journeys.COHORTS)}
    west, south, east, north = central_access.CORE
    centre = [(west + east) / 2, (south + north) / 2]
    offsets = central_access._points(sample.coordinates) - central_access._points([centre])[0]
    bearing = np.arctan2(offsets[:, 1], offsets[:, 0])
    separation = np.abs(bearing[:, None] - bearing[None, :])
    minor_angle = np.rad2deg(np.minimum(separation, 2 * np.pi - separation))
    groups[WIDE_ANGLE_COHORT] = groups["inter-district"] & (minor_angle >= WIDE_ANGLE_DEG)
    return {name: np.where(mask, sample.weights, 0.) for name, mask in groups.items()}


def _trip_metrics(weights, generalised, boards, penalty_s):
    report = journeys._journeys(weights, generalised, boards, penalty_s)
    total, served = weights.sum(), weights[boards > 0].sum()
    within_two = weights[(boards >= 1) & (boards <= 3)].sum()
    report["at_most_two_transfers_share_of_all_pct"] = journeys._percentage(within_two, total)
    report["at_most_two_transfers_share_of_served_pct"] = journeys._percentage(within_two, served)
    report["transfer_distribution_share_of_all_pct"] = {
        "0": journeys._percentage(weights[boards == 1].sum(), total),
        "1": journeys._percentage(weights[boards == 2].sum(), total),
        "2": journeys._percentage(weights[boards == 3].sum(), total),
        "3_or_more": journeys._percentage(weights[boards >= 4].sum(), total),
        "unserved": journeys._percentage(weights[boards == 0].sum(), total),
    }
    return report


def _paired_metrics(weights, elapsed, reference_elapsed):
    total = weights.sum()
    paired = journeys._paired_journeys(weights / total if total else weights, elapsed, reference_elapsed)
    if not total:
        for key in ("served_by_both_share_pct", "served_only_by_candidate_share_pct",
                    "served_only_by_reference_share_pct"):
            paired[key] = None
    return paired


def compare(networks, *, reference, graph=None, population=None, assumptions=journeys.JourneyAssumptions()):
    """Share OD and daily bidirectional running train-km across all alternatives."""
    if reference not in networks:
        raise ValueError("The reference must be among the evaluated networks")
    for network in networks.values():
        holistic_network.validate(network)
    if graph is None:
        graph = central_access.walking_graph()
    if population is None:
        population = holistic_access.load_population("worldpop-2026", graph)
    sample = journeys.sample_demand(population, assumptions)
    cohort_weights = _cohort_weights(sample)
    access = journeys._street_access(networks, sample, graph, assumptions.walk_limit_m)
    lengths = {name: sum(line["one_way_km"] for line in network["lines"].values())
               for name, network in networks.items()}
    train_km_day = 2 * lengths[reference] / assumptions.headway_s * assumptions.operating_hours_day * 3_600

    variants = {}
    for name in sorted(networks, key=lambda key: (key != reference, key)):
        headway = assumptions.headway_s * lengths[name] / lengths[reference]
        route = journeys._assignment_graph(networks[name], access[name], assumptions, headway)
        generalised, boards, boardings, rides = journeys._assign(route, sample)
        elapsed = np.where(boards > 0, generalised - (boards - 1) * assumptions.transfer_penalty_s, np.inf)
        if name == reference:
            reference_elapsed = elapsed
        served = sample.weights[boards > 0].sum()
        busiest = int(rides.argmax())
        reachable = np.isfinite(access[name]).any(axis=1)
        variants[name] = {
            "candidate_id": networks[name].get("candidate_id"),
            "service": {"route_km": round(lengths[name], 3),
                        "directional_headway_s": round(headway, 3),
                        "running_train_km_day": round(train_km_day, 2)},
            "sample_access": {"tiles_with_a_station": int(reachable.sum()),
                              "population_share_pct": journeys._percentage(
                                  sample.people[reachable].sum(), sample.people.sum())},
            "journeys": _trip_metrics(sample.weights, generalised, boards, assumptions.transfer_penalty_s),
            "cohorts": {cohort: _trip_metrics(weights, generalised, boards, assumptions.transfer_penalty_s)
                        for cohort, weights in cohort_weights.items()},
            "paired_journeys": _paired_metrics(sample.weights, elapsed, reference_elapsed),
            "paired_cohorts": {cohort: _paired_metrics(weights, elapsed, reference_elapsed)
                               for cohort, weights in cohort_weights.items()},
            "concentration": {
                "busiest_line": route.line_ids[int(boardings.argmax())] if served else None,
                "busiest_line_boarding_share_pct": journeys._percentage(boardings.max(), boardings.sum()),
                "busiest_directed_segment": route.segments[busiest] if served else None,
                "busiest_directed_segment_share_of_served_pct": journeys._percentage(rides[busiest], served),
                "peak_load_per_departure_index": round(float(rides[busiest] * headway * 100 /
                                                              assumptions.headway_s), 6),
            },
        }
    sample_record = {
        "source": sample.source,
        "tile_count": len(sample.people),
        "ordered_od_pairs": int(np.count_nonzero(sample.weights)),
        "modelled_population": round(float(sample.people.sum())),
        "core_bounds_wsen": central_access.CORE,
        "coordinates_lon_lat_and_tile_people": np.column_stack((sample.coordinates, sample.people)).tolist(),
        "cohort_definitions": {
            "inner-city": "Both endpoints inside the retained central box.",
            "centre–outer": "One endpoint inside the central box and one outside.",
            "inter-district": "Both endpoints outside the central box in different metric district grid cells.",
            "outer-local": "Both endpoints outside the central box in the same metric district grid cell.",
            WIDE_ANGLE_COHORT: f"Subset of inter-district pairs with at least {WIDE_ANGLE_DEG} degrees of bearing "
                               "separation around the midpoint of the central box.",
        },
    }
    sample_record["sample_id"] = sha256(central_access.encode(
        sample_record | {key: getattr(assumptions, key) for key in
                         ("tile_m", "minimum_trip_m", "outer_district_grid_m", "distance_decay_m")}
    )).hexdigest()
    return {
        "assumptions": asdict(assumptions) | {
            "street_source": graph[4],
            "street_snap_limit_m": central_access.SNAP_M,
            "matched_service_reference": reference,
            "paired_journey_reference": reference,
            "demand_basis": "Population-weighted tiles and exponential distance decay create synthetic OD weights.",
            "assignment_basis": "Continuous bidirectional all-stop service with half a headway at each boarding. "
                                "Transfer counts describe the path of least generalised cost without a transfer cap.",
            "paired_basis": "Elapsed P90 uses identical OD pairs served in both compared plans. Served shares "
                            "and transfer distribution use all OD weights in the displayed cohort.",
            "service_basis": "Equal scheduled running train-km exclude depot moves, terminal work and spare fleet.",
        },
        "demand_sample": sample_record,
        "variants": variants,
    }
