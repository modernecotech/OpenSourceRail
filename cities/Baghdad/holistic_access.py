"""Screen every proposed Baghdad corridor for station infill using retained pedestrian data."""

from dataclasses import dataclass
from functools import lru_cache
import gzip
import heapq
from io import BytesIO

import numpy as np
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

from .central_access import CORE, MAPPING, SNAP_M, WALK_M, _points, digest, distances_from_stops, read, walking_graph
from .holistic_network import INTERCHANGE_SPACING_M, Track, dry_points


@dataclass(frozen=True)
class Population:
    source: dict
    coordinates: np.ndarray
    counts: np.ndarray
    offsets_m: np.ndarray
    nodes: np.ndarray
    xy: np.ndarray


def load_population(name, graph):
    metadata = read(MAPPING / f"{name}-source.json")
    path = MAPPING / f"{name}-pixels.npz.gz"
    if digest(path) != metadata["retained_sha256"]:
        raise ValueError(f"The retained population file for {name} has changed")
    with np.load(BytesIO(gzip.decompress(path.read_bytes())), allow_pickle=False) as grid:
        valid = grid["valid"] & np.isfinite(grid["counts"]) & (grid["counts"] > 0)
        coordinates = np.column_stack((grid["lon"][valid], grid["lat"][valid]))
        counts = grid["counts"][valid].astype(float)
    xy = _points(coordinates)
    offsets, nearest = graph[3].query(xy)
    nodes = graph[2][nearest]
    return Population(metadata, coordinates, counts, offsets, nodes, xy)


def walk_to_station(stops, graph, population):
    distances, unmatched = distances_from_stops(stops, graph)
    return np.where(population.offsets_m <= SNAP_M,
                    distances[population.nodes] + population.offsets_m, np.inf), unmatched


@dataclass(frozen=True)
class Opportunity:
    line: str
    chainage_km: float
    within_800: np.ndarray
    within_1200: np.ndarray


def sampled_positions(line, step_m, spacing_m):
    track = Track(line["geometry"])
    samples = np.arange(step_m, track.km * 1000, step_m)
    existing = np.array(list(line["station_chainage_km"].values())) * 1000
    separation = np.abs(samples[:, None] - existing)
    if line["loop"]:
        separation = np.minimum(separation, track.km * 1000 - separation)
    return [(float(metres) / 1000, track.at(float(metres) / 1000))
            for metres in samples[separation.min(axis=1) >= spacing_m - 1e-7]]


def opportunities(network, population, existing, graph, step_m, spacing_m, context):
    """Build sparse sets of residents a station could newly reach via streets."""
    _, matrix, active, street_tree, _ = graph
    first, second = WALK_M
    residual = np.flatnonzero((existing > first) & (population.offsets_m <= SNAP_M))
    residual_tree = cKDTree(population.xy[residual])

    @lru_cache(maxsize=16)
    def street_walk(node):
        return dijkstra(matrix, directed=True, indices=node, limit=second)

    result = []
    for line_id, line in sorted(network["lines"].items()):
        rail_positions = sampled_positions(line, step_m, spacing_m)
        if not rail_positions:
            continue
        dry = dry_points([point for _, point in rail_positions], context)
        rail_positions = [row for row, keep in zip(rail_positions, dry, strict=True) if keep]
        if not rail_positions:
            continue
        coordinates = _points([point for _, point in rail_positions])
        snap, street_ids = street_tree.query(coordinates)
        for (chainage, _), xy, access, street_id in zip(rail_positions, coordinates, snap, street_ids, strict=True):
            if access > SNAP_M:
                continue
            # Limit computation to pixels near the candidate. The extra margin
            # covers the small planar projection error across the study area.
            nearby = residual[residual_tree.query_ball_point(xy, second * 1.03)]
            if not len(nearby):
                continue
            metres = street_walk(int(active[street_id]))[population.nodes[nearby]] + access + population.offsets_m[nearby]
            short = nearby[metres <= first]
            long = nearby[(metres <= second) & (existing[nearby] > second)]
            if len(short) or len(long):
                result.append(Opportunity(line_id, chainage, np.sort(short), np.sort(long)))
    return result


def rank_stations(candidates, population_counts, existing, spacing_m, max_infill):
    """Greedy marginal population gain with deterministic tie breaks and spacing."""
    included = {}
    covered = [existing <= limit for limit in WALK_M]

    def value(candidate):
        return tuple(round(float(population_counts[pixels[~current[pixels]]].sum()), 6)
                     for pixels, current in zip((candidate.within_800, candidate.within_1200), covered, strict=True))

    queue = []
    for i, candidate in enumerate(candidates):
        gain = value(candidate)
        queue.append((-gain[0], -gain[1], candidate.line, candidate.chainage_km, i))
    heapq.heapify(queue)
    added = []
    while queue and (max_infill is None or len(added) < max_infill):
        a, b, line, chainage, index = heapq.heappop(queue)
        if any(abs(chainage - prior) * 1000 < spacing_m - 1e-7 for prior in included.get(line, [])):
            continue
        candidate = candidates[index]
        gain = value(candidate)
        if gain == (0., 0.):
            continue
        priority = (-gain[0], -gain[1], line, chainage, index)
        if priority[:2] != (a, b):
            heapq.heappush(queue, priority)
            continue
        for pixels, current in zip((candidate.within_800, candidate.within_1200), covered, strict=True):
            current[pixels] = True
        included.setdefault(line, []).append(chainage)
        added.append(dict(line_id=line, chainage_km=chainage, id=f"{line}-infill-{round(chainage*1000):05d}",
                          name=f"{line} infill · km {chainage:g}",
                          basis="Population-ranked street-access infill on this alignment",
                          newly_covered_worldpop_800=round(gain[0], 2), newly_covered_worldpop_1200=round(gain[1], 2)))
    return added


def summarize(population, walks):
    lon, lat = population.coordinates.T
    core = (lon >= CORE[0]) & (lat >= CORE[1]) & (lon <= CORE[2]) & (lat <= CORE[3])
    scopes = {"metropolitan": np.ones(len(lon), dtype=bool), "central": core}
    return {
        "dataset": population.source["dataset"], "year": population.source["year"],
        "bbox": population.source["bbox"], "url": population.source["documentation"],
        **{label: {"population": round(float(population.counts[mask].sum())),
                   "beyond_street_snap": round(float(population.counts[mask & (population.offsets_m > SNAP_M)].sum())),
                   "cases": {case: {str(limit): {
                       "population": round(float(population.counts[mask & (distance <= limit)].sum())),
                       "share_pct": round(float(population.counts[mask & (distance <= limit)].sum() /
                                                population.counts[mask].sum() * 100), 2)}
                       for limit in WALK_M} for case, distance in walks.items()}}
           for label, mask in scopes.items()},
    }


def coverage_cells(population, distances, cell_m=1000):
    """Aggregate map dots on a metric grid for a readable coverage layer."""
    locations, group = np.unique(np.floor(population.xy / cell_m).astype(int), axis=0, return_inverse=True)
    count = np.bincount(group, weights=population.counts)
    within = np.bincount(group, weights=population.counts * (distances <= WALK_M[1]))
    lon = np.bincount(group, weights=population.counts * population.coordinates[:, 0]) / count
    lat = np.bincount(group, weights=population.counts * population.coordinates[:, 1]) / count
    return [dict(coordinates=[round(float(x), 6), round(float(y), 6)],
                 people=round(float(total)), beyond_1200_m=round(float(total - served)))
            for x, y, total, served in zip(lon, lat, count, within, strict=True) if round(total) > 0]


def evaluate(network, insert_stations, historic_stops, *, graph=None, context=None, step_m=300, spacing_m=650, max_infill=None):
    if not 0 < step_m <= spacing_m or spacing_m < INTERCHANGE_SPACING_M or max_infill is not None and max_infill < 0:
        raise ValueError(f"Use at least {INTERCHANGE_SPACING_M} m spacing, a positive step no larger than that spacing, "
                         "and an optional nonnegative cap")
    if graph is None:
        graph = walking_graph()
    datasets = {name: load_population(name, graph) for name in ("worldpop-2026", "ghsl-2025")}
    original = {label: location["coordinates"] for label, location in network["stations"].items()}
    worldpop = datasets["worldpop-2026"]
    existing, _ = walk_to_station(original, graph, worldpop)
    options = opportunities(network, worldpop, existing, graph, step_m, spacing_m, context) if max_infill != 0 else []
    additions = rank_stations(options, worldpop.counts, existing, spacing_m, max_infill)
    revised = insert_stations(network, additions)
    stops = {label: location["coordinates"] for label, location in revised["stations"].items()}
    offsets, _ = graph[3].query(_points(list(stops.values())))
    unmatched = sorted(label for label, offset in zip(stops, offsets, strict=True) if offset > SNAP_M)
    scopes = {}
    for name, population in datasets.items():
        without = existing if population is worldpop else walk_to_station(original, graph, population)[0]
        historical, _ = walk_to_station(historic_stops, graph, population)
        final, _ = walk_to_station(stops, graph, population)
        scopes[name] = summarize(population, {"earlier_clockface": historical,
                                              "connected_before_infill": without, "connected_network": final})
        if name == "worldpop-2026":
            cells = coverage_cells(population, final)
    return revised, {"walk_m": WALK_M, "station_and_population_snap_m": SNAP_M, "walk_graph": graph[4],
                     "candidate_step_m": step_m, "minimum_infill_spacing_m": spacing_m,
                     "max_infill": max_infill, "candidate_opportunities": len(options), "infill": additions,
                     "proposed_stops_without_a_street_snap": unmatched,
                     "population": scopes}, cells
