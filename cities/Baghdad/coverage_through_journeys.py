"""Compare rail access from mapped Baghdad suburbs to fixed central destinations."""

import numpy as np

from . import central_access, coverage_destinations, holistic_journeys, holistic_network, holistic_pathways


def _through_access(origin, destinations, route_columns):
    walks, served = {}, np.zeros(len(destinations), dtype=bool)
    for code, columns in route_columns.items():
        board = columns[np.isfinite(origin[columns])]
        if not len(board):
            continue
        walks[code] = round(float(origin[board].min()), 1)
        # The all-stops service runs in both directions. Exclude paths that
        # board and alight at the same station without taking a train.
        alight = columns[columns != board[0]] if len(board) == 1 else columns
        served |= np.isfinite(destinations[:, alight]).any(axis=1)
    return walks, int(served.sum())


def compare(networks, *, graph, destinations, assumptions, reference="published", through_routes=None):
    """Use the housing pathway model at equal scheduled running train-km."""
    if reference not in networks:
        raise ValueError("Include the matched-service reference in the suburban journey comparison")
    through_routes = {} if through_routes is None else through_routes
    if through_routes.keys() - networks.keys():
        raise ValueError("Through service lists must refer to compared layouts")
    origins = tuple(holistic_pathways.HousingOrigin(name, tuple(point), 1)
                    for name, point in coverage_destinations.locations().items())
    origins, origin_coordinates, _ = holistic_pathways._checked_points(origins, "people")
    destinations, destination_coordinates, _ = holistic_pathways._checked_points(destinations, "weight")
    for network in networks.values():
        holistic_network.validate(network)
    walks = holistic_pathways._street_access(
        networks, origin_coordinates, destination_coordinates, graph, assumptions.walk_limit_m,
        central_access._points, central_access.SNAP_M)
    weights = np.ones((len(origins), len(destinations)))
    transfers = range(holistic_pathways.MAX_TRANSFERS + 1)
    # Use unrounded route lengths, as in the housing and metropolitan assignments.
    route_km = {key: sum(line["one_way_km"] for line in network["lines"].values())
                for key, network in networks.items()}
    variants = {}
    for key, network in sorted(networks.items()):
        headway = assumptions.headway_s * route_km[key] / route_km[reference]
        origin_walk, destination_walk = walks[key]
        route = holistic_journeys._assignment_graph(
            network, np.empty((0, origin_walk.shape[1])), assumptions, headway)
        generalised, assigned, reachable, _, _ = holistic_pathways._assign(
            route, origin_walk, destination_walk, assumptions, weights)
        stations = {code: i for i, code in enumerate(sorted(network["stations"]))}
        route_columns = {
            code: np.array([stations[stop] for stop in network["lines"][code]["station_ids"]])
            for code in sorted(through_routes.get(key, ()))
        }
        elapsed = (generalised - assigned * assumptions.transfer_penalty_s) / 60
        suburb_results = {}
        for j, origin in enumerate(origins):
            walk = origin_walk[j].min()
            eligible = bool(np.isfinite(walk))
            pairs = {}
            for i, destination in enumerate(destinations):
                served = assigned[j, i] >= 0
                pairs[destination.id] = {
                    "minimum_transfers": next((k for k in transfers if reachable[k, j, i]), None),
                    "assigned_transfers": int(assigned[j, i]) if served else None,
                    "elapsed_min": round(float(elapsed[j, i]), 3) if served else None,
                }
            through_walks, through_count = _through_access(origin_walk[j], destination_walk, route_columns)
            suburb_results[origin.id] = {
                "walk_m": round(float(walk), 1) if eligible else None,
                "walk_eligible": eligible,
                "walkable_through_routes": through_walks,
                "direct_through_destination_count": through_count,
                "destination_count_by_max_transfers": {
                    str(k): int(reachable[k, j].sum()) for k in transfers
                },
                "destinations": pairs,
            }
        variants[key] = {
            "candidate_id": network.get("candidate_id"),
            "directional_headway_s": round(headway, 3),
            "running_train_km_day": round(
                2 * route_km[key] / headway * assumptions.operating_hours_day * 3_600, 2),
            "origins": suburb_results,
        }
    for result in variants.values():
        for name, row in result["origins"].items():
            baseline = variants[reference]["origins"][name]["destinations"]
            for code, pair in row["destinations"].items():
                minutes, before = pair["elapsed_min"], baseline[code]["elapsed_min"]
                pair["elapsed_delta_vs_reference_min"] = (
                    round(minutes - before, 3) if minutes is not None and before is not None else None)
    return {
        "matched_service_reference": reference,
        "walk_limit_m": assumptions.walk_limit_m,
        "street_source": graph[4],
        "origin_coordinates": {row.id: list(row.coordinates) for row in origins},
        "destinations": {row.id: {"name": row.name or row.id, "coordinates": list(row.coordinates)}
                         for row in destinations},
        "basis": (
            "Mapped suburban anchors and the same central destinations as the housing comparison. Both endpoints "
            "use directed walks on the retained streets. Counts are cumulative by maximum changes and give one "
            "vote to each destination. Walk distance is reported for origins with an eligible station within the cap. "
            "Where identified through services are supplied, their one-seat count requires distinct board and "
            "alight stations and counts each destination once across those services. "
            "Elapsed minutes follow the least-generalised-cost path with up to two changes, with half a headway "
            "per boarding. Time differences use only pairs served in both layouts. This is simulated all-stop access "
            "at equal scheduled running train-km. Actual timetables, ridership and capacity require separate evidence."
        ),
        "variants": variants,
    }
