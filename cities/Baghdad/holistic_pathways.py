"""Compare housing-to-centre rail journeys with a hard two-transfer limit."""

from dataclasses import asdict, dataclass
from hashlib import sha256

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

from . import central_access, holistic_journeys, holistic_network


MAX_TRANSFERS = 2
STREET_BATCH = 8


@dataclass(frozen=True)
class HousingOrigin:
    id: str
    coordinates: tuple[float, float]
    people: float
    name: str | None = None


@dataclass(frozen=True)
class CentreDestination:
    id: str
    coordinates: tuple[float, float]
    weight: float = 1.0
    name: str | None = None


def _within(coordinates, bounds):
    west, south, east, north = bounds
    if not np.isfinite(bounds).all() or not -180 <= west < east <= 180 or not -90 <= south < north <= 90:
        raise ValueError("Use ordered west, south, east and north coordinate bounds")
    return ((coordinates >= (west, south)) & (coordinates <= (east, north))).all(axis=1)


def sample_origins(population, *, tile_m=2_000, bounds=None, exclude_bounds=None):
    """Represent each populated housing tile by its retained pixel nearest the weighted centroid."""
    if not np.isfinite(tile_m) or tile_m <= 0:
        raise ValueError("Use a positive finite housing tile size")
    selected = np.ones(len(population.counts), dtype=bool)
    if bounds is not None:
        selected &= _within(population.coordinates, bounds)
    if exclude_bounds is not None:
        selected &= ~_within(population.coordinates, exclude_bounds)
    if not selected.any():
        raise ValueError("The housing study bounds contain no retained population")
    points = population.coordinates[selected]
    xy = population.xy[selected]
    counts = population.counts[selected]
    if not np.isfinite(counts).all() or (counts <= 0).any():
        raise ValueError("Housing sample needs positive finite retained pixel counts")
    tiles, membership = np.unique(np.floor(xy / tile_m).astype(int), axis=0, return_inverse=True)
    if len(tiles) > holistic_journeys.MAX_TILES:
        raise ValueError(f"Use at most {holistic_journeys.MAX_TILES} populated housing tiles")
    people = np.bincount(membership, weights=counts)
    centroid = np.column_stack([
        np.bincount(membership, weights=counts * axis) / people for axis in xy.T
    ])
    separation = ((xy - centroid[membership]) ** 2).sum(axis=1)
    order = np.lexsort((points[:, 1], points[:, 0], separation, membership))
    representatives = order[np.r_[True, np.diff(membership[order]) > 0]]
    return tuple(HousingOrigin(f"housing-{x}-{y}", tuple(map(float, points[index])), float(count))
                 for (x, y), index, count in zip(tiles, representatives, people, strict=True))


def _checked_points(rows, measure):
    rows = tuple(rows)
    if not rows or any(not isinstance(row.id, str) or not row.id.strip() for row in rows):
        raise ValueError("Provide at least one study point with a nonempty identifier")
    if len({row.id for row in rows}) != len(rows):
        raise ValueError("Study point identifiers must be unique within their group")
    rows = sorted(rows, key=lambda row: row.id)
    points = np.asarray([row.coordinates for row in rows], dtype=float)
    weights = np.asarray([getattr(row, measure) for row in rows], dtype=float)
    if (points.shape != (len(rows), 2) or not np.isfinite(points).all()
            or (np.abs(points) > (180, 90)).any()):
        raise ValueError("Study points need finite longitude and latitude")
    if (not np.isfinite(weights).all() or (weights <= 0).any()
            or not np.isfinite(weights.sum())):
        raise ValueError("Study points need positive finite weights and a finite total")
    return rows, points, weights


def _street_distances(matrix, point_nodes, point_offsets, stop_nodes, stop_offsets, limit_m,
                      snap_limit_m=central_access.SNAP_M):
    distance = np.full((len(point_nodes), len(stop_nodes)), np.inf)
    points = np.flatnonzero(point_offsets <= snap_limit_m)
    stops = np.flatnonzero(stop_offsets <= snap_limit_m)
    if not len(points) or not len(stops):
        return distance
    sources, source_index = np.unique(point_nodes[points], return_inverse=True)
    targets, target_index = np.unique(stop_nodes[stops], return_inverse=True)
    # Run from the smaller side of the point-to-stop matrix. Transposition
    # changes the search direction and preserves distances on asymmetric streets.
    reverse = len(targets) < len(sources)
    if reverse:
        matrix = matrix.T.tocsr()
        sources, targets = targets, sources
    walks = np.empty((len(sources), len(targets)))
    for start in range(0, len(sources), STREET_BATCH):
        batch = slice(start, start + STREET_BATCH)
        walks[batch] = dijkstra(matrix, directed=True, indices=sources[batch], limit=limit_m)[:, targets]
    routes = (walks.T if reverse else walks)[source_index[:, None], target_index]
    routes += point_offsets[points, None] + stop_offsets[stops]
    distance[np.ix_(points, stops)] = np.where(routes <= limit_m, routes, np.inf)
    return distance


def _street_access(networks, origins, destinations, graph, limit_m, project, snap_limit_m, cache=None):
    _, matrix, active, tree, _ = graph
    stops = sorted({tuple(station["coordinates"]) for network in networks.values()
                    for station in network["stations"].values()})
    if cache is None:
        cache = {}
    scope = (id(graph), id(project), limit_m, snap_limit_m, origins.tobytes(), destinations.tobytes())
    if cache.setdefault("scope", scope) != scope:
        raise ValueError("Walking access can be reused only with the same streets and demand points")
    columns = cache.setdefault("columns", {})
    new_stops = [point for point in stops if point not in columns]
    if new_stops:
        stop_offsets, stop_indices = tree.query(project(new_stops))

        def access(points, direction):
            offsets, indices = tree.query(project(points))
            return _street_distances(direction, active[indices], offsets, active[stop_indices], stop_offsets,
                                     limit_m, snap_limit_m)

        origin_walk = access(origins, matrix)
        # Egress is station-to-point travel. Search from destinations on reversed streets.
        destination_walk = access(destinations, matrix.T.tocsr())
        columns.update({point: (origin_walk[:, i].copy(), destination_walk[:, i].copy())
                        for i, point in enumerate(new_stops)})
    result = {}
    for name, network in networks.items():
        walks = [columns[tuple(station["coordinates"])] for _, station in sorted(network["stations"].items())]
        origin, destination = zip(*walks, strict=True)
        result[name] = np.column_stack(origin), np.column_stack(destination)
    return result


def _constrained_graph(route, origin_walk, destination_walk, assumptions):
    """Keep each rail state at the number of inter-line changes already made."""
    rail = route.matrix.tocoo()
    size = rail.shape[0]
    layers = MAX_TRANSFERS + 1
    station_count = origin_walk.shape[1]
    riding = np.flatnonzero((route.ride_segment[rail.row] >= 0) & (route.board_line[rail.col] >= 0))
    transfer = np.zeros(rail.nnz, dtype=bool)
    transfer[riding] = (route.segment_line[route.ride_segment[rail.row[riding]]]
                        != route.board_line[rail.col[riding]])

    origins = layers * size + np.arange(len(origin_walk))
    terminal_base = layers * size + len(origins)
    terminals = terminal_base + np.arange(layers * len(destination_walk)).reshape(layers, -1)
    origin, entry = np.nonzero(np.isfinite(origin_walk))
    destination, exit_station = np.nonzero(np.isfinite(destination_walk))
    rows, columns = [origins[origin]], [entry]
    costs = [origin_walk[origin, entry] / assumptions.walk_speed_m_s + assumptions.station_access_s]
    exit_cost = destination_walk[destination, exit_station] / assumptions.walk_speed_m_s + assumptions.station_access_s

    for layer in range(layers):
        allowed = np.ones(rail.nnz, dtype=bool) if layer < MAX_TRANSFERS else ~transfer
        rows.extend((rail.row[allowed] + layer * size, exit_station + station_count + layer * size))
        columns.extend((rail.col[allowed] + (layer + transfer[allowed]) * size, terminals[layer, destination]))
        costs.extend((rail.data[allowed], exit_cost))
    dimension = terminal_base + terminals.size
    # Reversed edges permit one rail search per destination and transfer count.
    matrix = csr_matrix((np.concatenate(costs), (np.concatenate(columns), np.concatenate(rows))),
                        shape=(dimension, dimension))
    return matrix, origins, terminals


def _assign(route, origin_walk, destination_walk, assumptions, weights):
    matrix, origins, terminals = _constrained_graph(route, origin_walk, destination_walk, assumptions)
    size = route.matrix.shape[0]
    generalised = np.full(weights.shape, np.inf)
    transfers = np.full(weights.shape, -1, dtype=int)
    reachable_by_limit = np.zeros((MAX_TRANSFERS + 1, *weights.shape), dtype=bool)
    rides = np.zeros(len(route.segments))
    witnesses = {}

    for start in range(0, weights.shape[1], 16):
        batch = slice(start, start + 16)
        batch_terminals = terminals[:, batch]
        distances, previous = dijkstra(matrix, indices=batch_terminals.ravel(), return_predecessors=True)
        costs = distances[:, origins].reshape(*batch_terminals.shape, len(origins))
        best = costs.argmin(axis=0)
        selected = np.take_along_axis(costs, best[None, ...], axis=0)[0]
        served = np.isfinite(selected)
        generalised[:, batch] = selected.T
        transfers[:, batch] = np.where(served, best, -1).T
        reachable_by_limit[:, :, batch] = np.logical_or.accumulate(np.isfinite(costs), axis=0).transpose(0, 2, 1)
        destination, origin = np.nonzero(served)
        rows = best[destination, origin] * batch_terminals.shape[1] + destination
        nodes = origins[origin]
        loads = weights[origin, start + destination]
        changes = best[destination, origin]
        for count in range(MAX_TRANSFERS + 1):
            candidates = np.flatnonzero(changes == count)
            if not len(candidates):
                continue
            pos = candidates[loads[candidates].argmax()]
            if count not in witnesses or loads[pos] > witnesses[count]["weight"]:
                node, segments = nodes[pos], []
                while node >= 0:
                    if node < len(terminals) * size and route.ride_segment[node % size] >= 0:
                        segments.append(route.segments[route.ride_segment[node % size]])
                    node = previous[rows[pos], node]
                witnesses[count] = {
                    "origin": int(origin[pos]), "destination": int(start + destination[pos]),
                    "weight": float(loads[pos]), "segments": segments,
                }
        # On the reversed graph predecessors are successors of the passenger path.
        while len(nodes):
            in_rail = nodes < len(terminals) * size
            segments = route.ride_segment[nodes[in_rail] % size]
            ridden = segments >= 0
            rides += np.bincount(segments[ridden], weights=loads[in_rail][ridden], minlength=len(rides))
            successor = previous[rows, nodes]
            active = successor >= 0
            nodes, rows, loads = successor[active], rows[active], loads[active]
    return generalised, transfers, reachable_by_limit, rides, witnesses


def _journeys(weights, generalised, transfers, reachable, walk_eligible, assumptions):
    served = transfers >= 0
    total = weights.sum()
    percent = holistic_journeys._percentage
    quantile = holistic_journeys._quantile
    elapsed = generalised[served] - transfers[served] * assumptions.transfer_penalty_s
    return {
        "od_pairs": int(weights.size),
        "walking_eligible_od_pairs": int(walk_eligible.sum()),
        "served_od_pairs": int(served.sum()),
        "walking_eligible_share_pct": percent(weights[walk_eligible].sum(), total),
        "outside_walking_limit_share_pct": percent(weights[~walk_eligible].sum(), total),
        "served_share_pct": percent(weights[served].sum(), total),
        "unserved_share_pct": percent(weights[~served].sum(), total),
        "eligible_but_unserved_share_pct": percent(weights[walk_eligible & ~served].sum(), total),
        "transfer_share_of_all_pct": {str(count): percent(weights[transfers == count].sum(), total)
                                      for count in range(MAX_TRANSFERS + 1)},
        "transfer_share_of_served_pct": {str(count): percent(weights[transfers == count].sum(), weights[served].sum())
                                         for count in range(MAX_TRANSFERS + 1)},
        "reachable_with_at_most_share_of_all_pct": {
            str(count): percent(weights[reachable[count]].sum(), total) for count in range(MAX_TRANSFERS + 1)
        },
        "elapsed_p50_min": quantile(elapsed, weights[served], .5),
        "elapsed_p90_min": quantile(elapsed, weights[served], .9),
        "generalised_p50_min": quantile(generalised[served], weights[served], .5),
        "generalised_p90_min": quantile(generalised[served], weights[served], .9),
    }


def _pathway_witnesses(witnesses, origins, destinations, generalised, assumptions, access, stations):
    records = {}
    for count, witness in witnesses.items():
        origin, destination = witness["origin"], witness["destination"]
        legs = []
        for segment in witness["segments"]:
            if legs and legs[-1]["line"] == segment["line"]:
                legs[-1]["alight_station"] = segment["to_station"]
            else:
                legs.append({"line": segment["line"], "board_station": segment["from_station"],
                             "alight_station": segment["to_station"]})
        access_m = access[0][origin, stations[legs[0]["board_station"]]]
        egress_m = access[1][destination, stations[legs[-1]["alight_station"]]]
        records[str(count)] = {
            "origin_id": origins[origin].id,
            "destination_id": destinations[destination].id,
            "transfer_count": count,
            "transfer_stations": [leg["board_station"] for leg in legs[1:]],
            "rail_legs": legs,
            "origin_walk_m": round(float(access_m), 3),
            "destination_walk_m": round(float(egress_m), 3),
            "elapsed_min": round(float(generalised[origin, destination]
                                       - count * assumptions.transfer_penalty_s) / 60, 3),
            "generalised_min": round(float(generalised[origin, destination]) / 60, 3),
        }
    return records


def _evaluate(network, access, assumptions, headway, origins, people, destinations, weights):
    origin_walk, destination_walk = access
    route = holistic_journeys._assignment_graph(network, np.empty((0, origin_walk.shape[1])), assumptions, headway)
    generalised, transfers, reachable, rides, witnesses = _assign(
        route, origin_walk, destination_walk, assumptions, weights)
    origin_eligible = np.isfinite(origin_walk).any(axis=1)
    destination_eligible = np.isfinite(destination_walk).any(axis=1)
    walk_eligible = origin_eligible[:, None] & destination_eligible
    ordered_load = np.argsort(-rides, kind="stable")
    served_weight = weights[transfers >= 0].sum()
    busiest = [
        route.segments[index] | {
            "share_of_all_pct": holistic_journeys._percentage(rides[index], 1),
            "share_of_served_pct": holistic_journeys._percentage(rides[index], served_weight),
        }
        for index in ordered_load[:5] if rides[index] > 0
    ]
    route_km = sum(line["one_way_km"] for line in network["lines"].values())
    stations = {code: i for i, code in enumerate(sorted(network["stations"]))}
    return {
        "candidate_id": network.get("candidate_id"),
        "service": {
            "route_km": round(route_km, 3),
            "directional_headway_s": round(headway, 3),
            "nominal_directional_headway_s": assumptions.headway_s,
            "headway_to_nominal_ratio": round(headway / assumptions.headway_s, 6),
            "running_train_km_day": round(2 * route_km / headway * assumptions.operating_hours_day * 3_600, 2),
        },
        "sample_access": {
            "origin_population_with_station": round(float(people[origin_eligible].sum()), 3),
            "origin_population_with_station_share_pct": holistic_journeys._percentage(
                people[origin_eligible].sum(), people.sum()),
            "origin_points_with_station": int(origin_eligible.sum()),
            "destination_points_with_station": int(destination_eligible.sum()),
        },
        "journeys": _journeys(weights, generalised, transfers, reachable, walk_eligible, assumptions),
        "pathway_witnesses": _pathway_witnesses(witnesses, origins, destinations, generalised, assumptions,
                                               access, stations),
        "destinations": {
            point.id: {
                "destination_walk_eligible": bool(destination_eligible[i]),
                "nearest_station_walk_m": round(float(destination_walk[i].min()), 3) if destination_eligible[i] else None,
                **_journeys(weights[:, i], generalised[:, i], transfers[:, i], reachable[:, :, i],
                            walk_eligible[:, i], assumptions),
            }
            for i, point in enumerate(destinations)
        },
        "concentration": {
            "busiest_directed_segment": busiest[0] if busiest else None,
            "busiest_directed_segment_share_of_served_pct": busiest[0]["share_of_served_pct"] if busiest else None,
            "busiest_directed_segments": busiest,
        },
    }


def compare(networks, *, origins, destinations, graph=None, assumptions=holistic_journeys.JourneyAssumptions(),
            match_service_to=None, origin_source=None, project=central_access._points,
            validate_network=holistic_network.validate, snap_limit_m=central_access.SNAP_M, street_access_cache=None):
    """Compare weighted housing and centre points on candidate rail networks.

    Other cities can supply their directed walking graph, its longitude/latitude
    projection into metres and their own geometry validator.
    A batch of layout trials can reuse street distances with an initially empty cache.
    """
    if not networks or match_service_to is not None and match_service_to not in networks:
        raise ValueError("Provide networks and include any matched-service reference")
    if not np.isfinite(snap_limit_m) or snap_limit_m < 0:
        raise ValueError("Street snap needs a finite nonnegative distance")
    for network in networks.values():
        validate_network(network)
    origins, origin_coordinates, people = _checked_points(origins, "people")
    destinations, destination_coordinates, destination_weights = _checked_points(destinations, "weight")
    if graph is None:
        graph = central_access.walking_graph()
    access = _street_access(networks, origin_coordinates, destination_coordinates, graph, assumptions.walk_limit_m,
                            project, snap_limit_m, street_access_cache)
    weights = np.outer(people / people.sum(), destination_weights / destination_weights.sum())
    sample = {
        "status": "Illustrative housing-to-centre demand",
        "origin_source": origin_source,
        "origin_count": len(origins),
        "destination_count": len(destinations),
        "modelled_population": round(float(people.sum()), 3),
        "ordered_od_pairs": int(weights.size),
        "origins": [{**asdict(row), "name": row.name or row.id,
                     "coordinates": list(map(float, row.coordinates)), "people": float(row.people)}
                    for row in origins],
        "destinations": [{**asdict(row), "name": row.name or row.id,
                          "coordinates": list(map(float, row.coordinates)), "weight": float(row.weight)}
                         for row in destinations],
    }
    sample["sample_id"] = sha256(central_access.encode(sample)).hexdigest()
    route_km = {key: sum(line["one_way_km"] for line in network["lines"].values())
                for key, network in networks.items()}
    return {
        "assumptions": {
            "maximum_transfers": MAX_TRANSFERS,
            **{key: getattr(assumptions, key) for key in (
                "walk_limit_m", "walk_speed_m_s", "station_access_s", "speed_cap_km_h", "acceleration_m_s2",
                "dwell_s", "headway_s", "transfer_walk_s", "transfer_penalty_s", "operating_hours_day")},
            "street_snap_limit_m": snap_limit_m,
            "street_source": graph[4],
            "matched_service_reference": match_service_to,
            "assignment_basis": "Shortest generalised cost among paths with zero to two inter-line changes, "
                                "including street access and egress. Equal costs prefer fewer changes.",
            "waiting_basis": "Each boarding waits half its directional headway. Transfer walk counts as elapsed time "
                             "and the transfer penalty contributes to generalised cost.",
            "weight_basis": "Origin population share multiplied by the assigned centre destination share. All networks "
                            "use these same ordered pairs and weights.",
            "walking_eligibility_basis": "Each endpoint has a feasible directed street walk to or from at least one "
                                         "station within the walking and snap limits.",
            "witness_basis": "For each observed transfer count, use the assigned path for the highest-weight pair.",
            "service_basis": "Simulated bidirectional all-stops rail with continuous headways. Running train-km "
                             "exclude depot and turnback movements.",
            "scope": "Rail trips with walking access. Relative demand and segment shares require local trip data "
                     "and timetable evidence to establish passenger counts and capacity.",
        },
        "demand_sample": sample,
        "variants": {
            name: _evaluate(networks[name], access[name], assumptions,
                            assumptions.headway_s if match_service_to is None else
                            assumptions.headway_s * route_km[name] / route_km[match_service_to],
                            origins, people, destinations, weights)
            for name in sorted(networks)
        },
    }
