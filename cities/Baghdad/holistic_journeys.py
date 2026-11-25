"""Compare passenger journeys on Baghdad planning alignments with a shared synthetic OD sample."""

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from hashlib import sha256
from itertools import pairwise

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

from . import central_access, holistic_access, holistic_network


COHORTS = ("inner-city", "centre–outer", "inter-district", "outer-local")
MAX_TILES = 2_000


@dataclass(frozen=True)
class JourneyAssumptions:
    tile_m: float = 2_000
    outer_district_grid_m: float = 8_000
    minimum_trip_m: float = 2_000
    distance_decay_m: float = 10_000
    walk_limit_m: float = 1_200
    walk_speed_m_s: float = 1.2
    station_access_s: float = 60
    speed_cap_km_h: float = 72
    acceleration_m_s2: float = 0.8
    dwell_s: float = 35
    headway_s: float = 360
    transfer_walk_s: float = 120
    transfer_penalty_s: float = 120
    operating_hours_day: float = 18

    def __post_init__(self):
        nonnegative = {"station_access_s", "dwell_s", "transfer_walk_s", "transfer_penalty_s"}
        for key, value in asdict(self).items():
            if not np.isfinite(value) or value < 0 or (value == 0 and key not in nonnegative):
                raise ValueError(f"Invalid journey assumption {key}={value}")
        if self.operating_hours_day > 24 or self.outer_district_grid_m < self.tile_m:
            raise ValueError("Invalid operating day or district grid")


@dataclass(frozen=True)
class DemandSample:
    coordinates: np.ndarray
    street_nodes: np.ndarray
    street_offsets: np.ndarray
    people: np.ndarray
    weights: np.ndarray
    cohorts: np.ndarray
    source: dict


def sample_demand(population, assumptions=JourneyAssumptions()):
    """Represent every populated tile using a retained pixel near its weighted centroid."""
    tiles = np.floor(population.xy / assumptions.tile_m).astype(int)
    _, membership = np.unique(tiles, axis=0, return_inverse=True)
    people = np.bincount(membership, weights=population.counts)
    if len(people) > MAX_TILES:
        raise ValueError(f"The all-pairs comparison supports at most {MAX_TILES} populated tiles")
    centroids = np.column_stack([
        np.bincount(membership, weights=population.counts * axis) / people for axis in population.xy.T
    ])
    centroid_distance = ((population.xy - centroids[membership]) ** 2).sum(axis=1)
    ranked = np.lexsort((population.coordinates[:, 1], population.coordinates[:, 0],
                         centroid_distance, membership))
    representatives = ranked[np.r_[True, np.diff(membership[ranked]) > 0]]
    coordinates = population.coordinates[representatives]
    xy = population.xy[representatives]
    distance = np.linalg.norm(xy[:, None, :] - xy[None, :, :], axis=2)
    # The distance decay represents decreasing trip propensity, separate from
    # the subsequent street and rail paths used for access and travel time.
    weights = people[:, None] * people[None, :] * np.exp(-distance / assumptions.distance_decay_m)
    weights[distance < assumptions.minimum_trip_m] = 0
    np.fill_diagonal(weights, 0)
    if not weights.any():
        raise ValueError("The common population sample has no OD pairs meeting the minimum distance")
    weights /= weights.sum()
    west, south, east, north = central_access.CORE
    longitude, latitude = coordinates.T
    core = (west <= longitude) & (longitude <= east) & (south <= latitude) & (latitude <= north)
    district = np.floor(xy / assumptions.outer_district_grid_m).astype(int)
    same_district = (district[:, None, :] == district[None, :, :]).all(axis=2)
    cohorts = np.where(core[:, None] & core[None, :], 0,
                       np.where(core[:, None] | core[None, :], 1, np.where(same_district, 3, 2)))
    return DemandSample(coordinates, population.nodes[representatives], population.offsets_m[representatives],
                        people, weights, cohorts, population.source)


def _street_access(networks, sample, graph, limit_m):
    """Reuse one bounded street search per sampled street node across all variants."""
    _, street_matrix, active_nodes, tree, _ = graph
    coordinates = sorted({tuple(station["coordinates"]) for network in networks.values()
                          for station in network["stations"].values()})
    station_offsets, nearest = tree.query(central_access._points(coordinates))
    station_nodes, node_columns = np.unique(active_nodes[nearest], return_inverse=True)
    access = np.full((len(sample.people), len(coordinates)), np.inf)
    usable_origins = np.flatnonzero(sample.street_offsets <= central_access.SNAP_M)
    source_nodes, source_index = np.unique(sample.street_nodes[usable_origins], return_inverse=True)
    street_distances = np.empty((len(source_nodes), len(station_nodes)))
    for start in range(0, len(source_nodes), 8):
        batch = slice(start, start + 8)
        street_distances[batch] = dijkstra(street_matrix, directed=True, indices=source_nodes[batch],
                                         limit=limit_m)[:, station_nodes]
    access[usable_origins] = (street_distances[source_index[:, None], node_columns]
                              + station_offsets + sample.street_offsets[usable_origins, None])
    access[(access > limit_m) | (station_offsets > central_access.SNAP_M)] = np.inf
    column = {point: index for index, point in enumerate(coordinates)}
    return {candidate: access[:, [column[tuple(station["coordinates"])]
                                  for _, station in sorted(network["stations"].items())]]
            for candidate, network in networks.items()}


def _running_time(distance_m, assumptions):
    """Triangular or capped trapezoidal speed profile between consecutive calls."""
    speed = assumptions.speed_cap_km_h / 3.6
    acceleration = assumptions.acceleration_m_s2
    if distance_m <= speed ** 2 / acceleration:
        return float(2 * np.sqrt(distance_m / acceleration))
    return distance_m / speed + speed / acceleration


@dataclass(frozen=True)
class AssignmentGraph:
    matrix: csr_matrix
    origins: np.ndarray
    destinations: np.ndarray
    board_line: np.ndarray
    ride_segment: np.ndarray
    segment_line: np.ndarray
    line_ids: list
    segments: list


def _assignment_graph(network, access, assumptions, headway_s):
    station_index = {code: index for index, code in enumerate(sorted(network["stations"]))}
    station_count = len(station_index)
    tile_count = len(access)
    origins = np.arange(2 * station_count, 2 * station_count + tile_count)
    destinations = origins + tile_count
    dimension = 2 * (station_count + tile_count)
    rows, columns, costs = [], [], []
    boarded, ridden = {}, {}
    arrivals, departures = {}, {}
    line_ids = sorted(network["lines"])
    waits = [headway_s[code] / 2 for code in line_ids] if isinstance(headway_s, Mapping) else [headway_s / 2] * len(line_ids)
    segments, segment_lines = [], []

    def edge(source, target, cost):
        rows.append(source)
        columns.append(target)
        costs.append(cost)

    for tile, station in zip(*np.nonzero(np.isfinite(access)), strict=True):
        cost = access[tile, station] / assumptions.walk_speed_m_s + assumptions.station_access_s
        edge(origins[tile], station, cost)
        edge(station + station_count, destinations[tile], cost)

    transfer_stations = [transfer["id"] for transfer in sorted(network["transfers"], key=lambda row: row["id"])]
    for line_index, line_id in enumerate(line_ids):
        line = network["lines"][line_id]
        stops = line["station_ids"]
        chainage = line["station_chainage_km"]
        legs = [(a, b, chainage[b] - chainage[a]) for a, b in pairwise(stops)]
        if line["loop"]:
            legs.append((stops[-1], stops[0], line["one_way_km"] - chainage[stops[-1]]))
        for direction in (1, -1):
            depart, arrive = {}, {}
            directed_legs = legs if direction == 1 else [(b, a, km) for a, b, km in reversed(legs)]
            for start, end, km in directed_legs:
                depart[start], arrive[end] = dimension, dimension + 1
                dimension += 2
                boarded[depart[start]] = line_index
                ridden[arrive[end]] = len(segments)
                departures.setdefault(start, []).append((line_index, depart[start]))
                arrivals.setdefault(end, []).append((line_index, arrive[end]))
                segments.append(dict(line=line_id, from_station=start, to_station=end,
                                     direction=direction, distance_km=round(km, 6)))
                segment_lines.append(line_index)
                edge(depart[start], arrive[end], _running_time(km * 1_000, assumptions))
                edge(station_index[start], depart[start], waits[line_index])
                edge(arrive[end], station_index[end] + station_count, 0)
            for stop in sorted(depart.keys() & arrive.keys()):
                edge(arrive[stop], depart[stop], assumptions.dwell_s)

    transfer_cost = assumptions.transfer_walk_s + assumptions.transfer_penalty_s
    for stop in transfer_stations:
        for previous_line, arrival in arrivals[stop]:
            for next_line, departure in departures[stop]:
                if previous_line != next_line:
                    edge(arrival, departure, transfer_cost + waits[next_line])

    matrix = csr_matrix((costs, (rows, columns)), shape=(dimension, dimension))
    if matrix.nnz != len(costs):
        raise ValueError("Passenger graph edges must remain distinct")
    board_line = np.full(dimension, -1)
    ride_segment = np.full(dimension, -1)
    for node, index in boarded.items():
        board_line[node] = index
    for node, index in ridden.items():
        ride_segment[node] = index
    return AssignmentGraph(matrix, origins, destinations, board_line, ride_segment,
                           np.array(segment_lines), line_ids, segments)


def _assign(route, demand):
    """Solve each origin in SciPy and walk predecessor batches to tally directed loads."""
    boardings = np.zeros(len(route.line_ids))
    rides = np.zeros(len(route.segments))
    journey_boards = np.zeros(demand.weights.shape, dtype=np.int16)
    generalised = np.full(demand.weights.shape, np.inf)
    for start in range(0, len(route.origins), 32):
        batch = slice(start, start + 32)
        distances, previous = dijkstra(route.matrix, indices=route.origins[batch], return_predecessors=True)
        generalised[batch] = distances[:, route.destinations]
        origin, destination = np.nonzero(np.isfinite(generalised[batch]) & (demand.weights[batch] > 0))
        weights = demand.weights[start + origin, destination]
        nodes = route.destinations[destination]
        trip_boardings = np.zeros(len(nodes), dtype=np.int16)
        while len(nodes):
            predecessors = previous[origin, nodes]
            lines = route.board_line[nodes]
            boarding = lines >= 0
            board_positions = np.flatnonzero(boarding)
            previous_segments = route.ride_segment[predecessors[board_positions]]
            after_ride = previous_segments >= 0
            # The single in-train dwell edge retains the same line. Every other
            # predecessor of a departure is a first boarding or inter-line change.
            boarding[board_positions[after_ride]] = (
                route.segment_line[previous_segments[after_ride]] != lines[board_positions[after_ride]]
            )
            trip_boardings[boarding] += 1
            boardings += np.bincount(lines[boarding], weights=weights[boarding], minlength=len(boardings))
            segments = route.ride_segment[nodes]
            aboard = segments >= 0
            rides += np.bincount(segments[aboard], weights=weights[aboard], minlength=len(rides))
            # The predecessor sentinel marks the source of a complete journey.
            complete = predecessors < 0
            journey_boards[start + origin[complete], destination[complete]] = trip_boardings[complete]
            active = ~complete
            nodes, origin, destination, weights, trip_boardings = (
                array[active] for array in (predecessors, origin, destination, weights, trip_boardings)
            )
    return generalised, journey_boards, boardings, rides


def _percentage(numerator, denominator):
    return round(float(100 * numerator / denominator), 4) if denominator > 0 else None


def _quantile(values, weights, fraction):
    if not len(values):
        return None
    order = np.argsort(values, kind="stable")
    cumulative = np.cumsum(weights[order])
    index = np.searchsorted(cumulative, cumulative[-1] * fraction)
    return round(float(values[order[index]]) / 60, 3)


def _journeys(weights, generalised, boards, penalty_s):
    active = weights > 0
    served = active & np.isfinite(generalised)
    direct = weights[served & (boards == 1)].sum()
    at_most_one = weights[served & (boards >= 1) & (boards <= 2)].sum()
    total, served_weight = weights.sum(), weights[served].sum()
    elapsed = generalised[served] - (boards[served] - 1) * penalty_s
    return {
        "od_pairs": int(active.sum()),
        "served_od_pairs": int(served.sum()),
        "synthetic_demand_share_pct": _percentage(total, 1),
        "served_share_pct": _percentage(served_weight, total),
        "direct_share_of_all_pct": _percentage(direct, total),
        "direct_share_of_served_pct": _percentage(direct, served_weight),
        "at_most_one_transfer_share_of_all_pct": _percentage(at_most_one, total),
        "at_most_one_transfer_share_of_served_pct": _percentage(at_most_one, served_weight),
        "mean_transfers_of_served": round(float(np.average(boards[served] - 1, weights=weights[served])), 4)
        if served_weight else None,
        "elapsed_mean_min": round(float(np.average(elapsed, weights=weights[served])) / 60, 3)
        if served_weight else None,
        "generalised_mean_min": round(float(np.average(generalised[served], weights=weights[served])) / 60, 3)
        if served_weight else None,
        "elapsed_p50_min": _quantile(elapsed, weights[served], .5),
        "elapsed_p90_min": _quantile(elapsed, weights[served], .9),
        "generalised_p50_min": _quantile(generalised[served], weights[served], .5),
        "generalised_p90_min": _quantile(generalised[served], weights[served], .9),
    }


def _evaluate(network, access, sample, assumptions, headway):
    route = _assignment_graph(network, access, assumptions, headway)
    generalised, boards, boardings, rides = _assign(route, sample)
    served_weight = sample.weights[boards > 0].sum()
    total_boardings = boardings.sum()
    busiest_line = int(boardings.argmax())
    busiest_segment = int(rides.argmax())
    total_km = sum(line["one_way_km"] for line in network["lines"].values())
    headways = headway if isinstance(headway, Mapping) else dict.fromkeys(route.line_ids, headway)
    service_km_per_s = sum(network["lines"][code]["one_way_km"] / headways[code] for code in route.line_ids)
    segment_waits = np.asarray([headways[code] for code in route.line_ids])[route.segment_line]
    pressures = rides * segment_waits * (100 / assumptions.headway_s)
    peak_pressure = int(pressures.argmax())
    accessible = np.isfinite(access).any(axis=1)
    by_line = {}
    for index, code in enumerate(route.line_ids):
        segments = np.flatnonzero(route.segment_line == index)
        peak = max(segments, key=rides.__getitem__)
        by_line[code] = dict(boarding_share_pct=_percentage(boardings[index], total_boardings),
                             peak_segment_share_of_all_od_pct=round(100 * float(rides[peak]), 7),
                             boardings_per_100_synthetic_od=round(float(100 * boardings[index]), 4),
                             busiest_directed_segment=(route.segments[peak] | {
                                 "share_of_served_pct": _percentage(rides[peak], served_weight)
                             }) if rides[peak] > 0 else None)
    report = {
        "candidate_id": network.get("candidate_id"),
        "service": {"route_km": round(total_km, 3), "directional_headway_s": round(total_km / service_km_per_s, 3),
                    "line_headways_s": {code: round(value, 3) for code, value in headways.items()},
                    "running_train_km_day": round(2 * service_km_per_s * assumptions.operating_hours_day * 3_600, 2)},
        "sample_access": {"tiles_with_a_station": int(accessible.sum()),
                          "population_share_pct": _percentage(sample.people[accessible].sum(), sample.people.sum())},
        "journeys": _journeys(sample.weights, generalised, boards, assumptions.transfer_penalty_s),
        "cohorts": {cohort: _journeys(np.where(sample.cohorts == index, sample.weights, 0),
                                    generalised, boards, assumptions.transfer_penalty_s)
                    for index, cohort in enumerate(COHORTS)},
        "line_loads": by_line,
        "concentration": {
            "busiest_line": route.line_ids[busiest_line] if total_boardings else None,
            "busiest_line_boarding_share_pct": _percentage(boardings[busiest_line], total_boardings),
            "line_boarding_hhi": round(float(((boardings / total_boardings) ** 2).sum()), 6)
            if total_boardings else None,
            "busiest_directed_segment": route.segments[busiest_segment] if served_weight else None,
            "busiest_directed_segment_share_of_served_pct": _percentage(rides[busiest_segment], served_weight),
            "peak_load_per_departure_index": round(float(pressures[peak_pressure]), 6),
            "peak_load_per_departure_segment": route.segments[peak_pressure] if served_weight else None,
        },
    }
    elapsed = np.where(boards > 0, generalised - (boards - 1) * assumptions.transfer_penalty_s, np.inf)
    return report, elapsed


def _balanced_frequencies(network, access, sample, assumptions, headway):
    """Redistribute the same running train-km toward busy segments and reroute trips."""
    codes = sorted(network["lines"])
    lengths = np.array([network["lines"][code]["one_way_km"] for code in codes])
    current = np.full(len(codes), 1. / headway)
    target = float(lengths @ current)
    lower, upper = .5 / headway, 2. / headway
    result, elapsed = _evaluate(network, access, sample, assumptions, headway)
    best = result, elapsed
    for _ in range(4):
        loads = np.array([result["line_loads"][code]["peak_segment_share_of_all_od_pct"] for code in codes])
        active = loads > 0
        if lengths @ np.where(active, upper, lower) <= target:
            break
        lo, hi = 0., upper / loads[active].min()
        for _ in range(48):
            midpoint = (lo + hi) / 2
            if lengths @ np.clip(loads * midpoint, lower, upper) < target:
                lo = midpoint
            else:
                hi = midpoint
        current = .5 * current + .5 * np.clip(loads * ((lo + hi) / 2), lower, upper)
        result, elapsed = _evaluate(network, access, sample, assumptions, dict(zip(codes, 1. / current, strict=True)))
        best = min((best, (result, elapsed)), key=lambda row: (
            row[0]["concentration"]["peak_load_per_departure_index"],
            -row[0]["journeys"]["at_most_one_transfer_share_of_all_pct"]))
    return best


def _paired_journeys(weights, elapsed, reference):
    served, baseline = np.isfinite(elapsed), np.isfinite(reference)
    common = served & baseline & (weights > 0)
    shared_weight = weights[common].sum()
    difference = elapsed[common] - reference[common]
    return {
        "served_by_both_share_pct": _percentage(shared_weight, 1),
        "served_only_by_candidate_share_pct": _percentage(weights[served & ~baseline].sum(), 1),
        "served_only_by_reference_share_pct": _percentage(weights[baseline & ~served].sum(), 1),
        "reference_elapsed_p90_min": _quantile(reference[common], weights[common], .9),
        "candidate_elapsed_p90_min": _quantile(elapsed[common], weights[common], .9),
        "candidate_minus_reference_elapsed_mean_min": round(float(np.average(
            difference, weights=weights[common])) / 60, 3) if shared_weight else None,
    }


def compare(networks, *, graph=None, population=None, assumptions=JourneyAssumptions(),
            match_service_to=None, reference=None, balance_frequencies=False):
    """Assign the same synthetic passenger demand to each validated planning network."""
    reference = match_service_to if reference is None else reference
    if not networks or any(key is not None and key not in networks for key in (match_service_to, reference)):
        raise ValueError("Provide networks and include any matched service or paired journey reference")
    for network in networks.values():
        holistic_network.validate(network)
    if graph is None:
        graph = central_access.walking_graph()
    if population is None:
        population = holistic_access.load_population("worldpop-2026", graph)
    sample = sample_demand(population, assumptions)
    access = _street_access(networks, sample, graph, assumptions.walk_limit_m)
    lengths = {key: sum(row["one_way_km"] for row in network["lines"].values())
               for key, network in networks.items()}
    sample_record = {
        "status": "Illustrative synthetic origin–destination demand",
        "source": sample.source,
        "method": "Population-weighted centroids represented by a retained pixel in each metric tile. "
                  "Ordered OD weights use origin population × destination population × exponential distance decay.",
        "district_basis": "Outer grid cells are spatial proxies for districts. The central cohort uses the retained "
                          "central walking-study box.",
        "tile_count": len(sample.people),
        "modelled_population": round(float(sample.people.sum())),
        "ordered_od_pairs": int(np.count_nonzero(sample.weights)),
        "core_bounds_wsen": central_access.CORE,
        "coordinates_lon_lat_and_tile_people": np.column_stack((sample.coordinates, sample.people)).tolist(),
    }
    sample_record["sample_id"] = sha256(central_access.encode({
        **sample_record, "tile_m": assumptions.tile_m, "minimum_trip_m": assumptions.minimum_trip_m,
        "outer_district_grid_m": assumptions.outer_district_grid_m,
        "distance_decay_m": assumptions.distance_decay_m,
    })).hexdigest()
    variants = {}
    baseline_elapsed = None
    order = sorted(networks, key=lambda name: (name != reference, name))
    for name in order:
        headway = assumptions.headway_s
        if match_service_to is not None:
            headway *= lengths[name] / lengths[match_service_to]
        evaluate = _balanced_frequencies if balance_frequencies else _evaluate
        report, elapsed = evaluate(networks[name], access[name], sample, assumptions, headway)
        if name == reference:
            baseline_elapsed = elapsed
        if baseline_elapsed is not None:
            report["paired_journeys"] = _paired_journeys(sample.weights, elapsed, baseline_elapsed)
        variants[name] = report
    return {
        "assumptions": asdict(assumptions) | {
            "street_snap_limit_m": central_access.SNAP_M,
            "street_source": graph[4],
            "matched_service_reference": match_service_to,
            "paired_journey_reference": reference,
            "frequency_balance": balance_frequencies,
            "boarding_wait_basis": "Half the applicable directional headway at each boarding.",
            "assignment_basis": "Lowest generalised cost across eligible street-walk station pairs and both rail "
                                "directions, including orbital closure. Equal-cost paths use a deterministic sparse "
                                "graph order. Transfer shares describe the assigned paths. Transfer walking time "
                                "is elapsed time. The transfer penalty adds disutility.",
            "service_basis": "Continuous bidirectional service with all stations called. Daily running train-km "
                             "exclude depot moves, terminal work and spare fleet.",
            "demand_limits": "Population at both ends approximates travel opportunities. Actual trip rates, "
                             "jobs, schools, fare, feeder travel, queueing and displacement require local evidence.",
            "load_limits": "One path per OD. Reported shares are comparative concentration measures; "
                           "passenger counts, train loads and operational capacity require demand and timetable data.",
        },
        "demand_sample": sample_record,
        "variants": variants,
    }
