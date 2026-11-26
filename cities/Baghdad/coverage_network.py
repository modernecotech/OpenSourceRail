"""Assemble and rank density-fitted Baghdad networks on mapped walking access."""


from functools import lru_cache
from heapq import heapify, heappop, heappush

import numpy as np
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
from shapely import LineString, Point
from shapely.ops import substring

from . import central_access, coverage_orbitals, coverage_trunks, holistic_access, holistic_network as rail
from .coverage_orbitals import WALK_M

RINGS = coverage_trunks.RINGS
RING_NAMES = ("Central ring", "Residential middle ring", "Outer ring")
MIN_SITE_DISTANCE_M = coverage_trunks.STATION_SPACING_M
MAX_TRUNKS = 14
MAX_ORBITAL_LAYOUTS = 3
MAX_PUBLISHED_TRIALS = 2
INFILL_SAMPLE_M = 250
MAX_INFILL_SITES = 120


def _ring_seed(reference, layout):
    network = {
        "schema": "osr.baghdad.holistic-network.v1",
        "lines": {},
        "stations": {},
        "transfers": [],
        "source_sha256": reference.get("source_sha256", {}),
        "assumptions": reference.get("assumptions", {}),
        "physical_accepted": False,
        "operating_timetable_validated": False,
    }
    for code, name in zip(RINGS, RING_NAMES, strict=True):
        alignment = LineString(layout["polygons"][code].exterior.coords)
        locations = layout["test_stations"][code]
        origin_m = alignment.project(Point(np.asarray(locations[0]) * rail.LOCAL_METRES))
        if 1e-6 < origin_m < alignment.length - 1e-6:
            alignment = LineString(rail._concatenate(
                substring(alignment, origin_m, alignment.length).coords,
                substring(alignment, 0, origin_m).coords,
            ))
        track = rail.Track(np.asarray(alignment.coords) / rail.LOCAL_METRES)
        chainages = [track.locate(point)[0] for point in locations]
        second_km = min(chainages[1:], key=lambda km: (abs(km - track.km / 2), km))
        line = {
            "name": name,
            "loop": True,
            "source_sections": [],
            "basis": "Population-fitted closed planning alignment with mapped street-access checks",
            "geometry": track.coordinates.tolist(),
            "one_way_km": track.km,
            "station_ids": [],
            "station_chainage_km": {},
        }
        network["lines"][code] = line
        for index, km in enumerate((0., second_km), 1):
            stop = f"{code}-R{index:02d}"
            network["stations"][stop] = {"name": f"{name} · km {km:.1f}", "coordinates": track.at(km),
                                         "basis": "Mapped provisional orbital stop", "lines": [code]}
            rail._add(line, stop, km)
    return network


def _ring_calls(network, layout, minimum_m=MIN_SITE_DISTANCE_M):
    """Use shared stations first, then retain well-spaced single-route sites."""
    existing = np.asarray([row["coordinates"] for row in network["stations"].values()]) * rail.LOCAL_METRES
    tree = cKDTree(existing)
    chosen, additions = [], []
    for code in RINGS:
        track = rail.Track(network["lines"][code]["geometry"])
        for index, point in enumerate(layout["test_stations"][code], 3):
            position = np.asarray(point) * rail.LOCAL_METRES
            if tree.query(position)[0] < minimum_m:
                continue
            if any(np.linalg.norm(position - prior) < minimum_m for prior in chosen):
                continue
            km = track.locate(point)[0]
            if rail._terminal_margin(network["lines"][code], km) < minimum_m:
                continue
            chosen.append(position)
            additions.append({"id": f"{code}-R{index:02d}", "line_id": code, "chainage_km": km,
                              "name": f"{network['lines'][code]['name']} · km {km:.1f}",
                              "basis": "Population-fitted provisional stop with mapped street access"})
    return rail.insert_stations(network, additions)


def _add_missing_access(network, graph, context, population):
    """Place extra calls only where the exact street network exposes a catchment gap."""
    stations = {site: row["coordinates"] for site, row in network["stations"].items()}
    walking, _ = holistic_access.walk_to_station(stations, graph, population)
    eligible = (walking > WALK_M) & (population.offsets_m <= central_access.SNAP_M)
    residents = np.flatnonzero(eligible)
    population_tree = cKDTree(population.xy[residents])
    station_tree = cKDTree(central_access._points(stations.values()))
    _, matrix, active, streets, _ = graph
    covered = ~eligible
    options = []

    @lru_cache(maxsize=12)
    def street_distance(node):
        return dijkstra(matrix, directed=True, indices=node, limit=WALK_M)

    for code, line in sorted(network["lines"].items()):
        samples = holistic_access.sampled_positions(line, INFILL_SAMPLE_M, MIN_SITE_DISTANCE_M)
        if not samples:
            continue
        xy = central_access._points([point for _, point in samples])
        offsets, nearest = streets.query(xy)
        valid = ((offsets <= central_access.SNAP_M) & (station_tree.query(xy)[0] >= MIN_SITE_DISTANCE_M)
                 & rail.dry_points([point for _, point in samples], context))
        for slot in np.flatnonzero(valid):
            in_range = population_tree.query_ball_point(xy[slot], WALK_M * 1.02)
            candidates = residents[in_range]
            if not len(candidates):
                continue
            metres = (street_distance(int(active[nearest[slot]]))[population.nodes[candidates]]
                      + offsets[slot] + population.offsets_m[candidates])
            pixels = np.sort(candidates[metres <= WALK_M])
            if len(pixels):
                options.append((code, samples[slot][0], xy[slot], pixels))

    def gain(pixels):
        return round(float(population.counts[pixels[~covered[pixels]]].sum()), 6)

    queue = [(-gain(row[3]), index) for index, row in enumerate(options)]
    heapify(queue)
    accepted, positions, additions = {}, [], []
    while queue and len(additions) < MAX_INFILL_SITES:
        previous, index = heappop(queue)
        code, km, xy, pixels = options[index]
        length = network["lines"][code]["one_way_km"]
        old_calls = accepted.get(code, [])
        gaps = np.abs(np.asarray(old_calls) - km)
        if network["lines"][code]["loop"]:
            gaps = np.minimum(gaps, length - gaps)
        if np.any(gaps < MIN_SITE_DISTANCE_M / 1000) or any(
                np.linalg.norm(xy - prior) < MIN_SITE_DISTANCE_M for prior in positions):
            continue
        value = -gain(pixels)
        if value == 0:
            continue
        if value != previous:
            heappush(queue, (value, index))
            continue
        covered[pixels] = True
        accepted.setdefault(code, []).append(km)
        positions.append(xy)
        additions.append({"id": f"{code}-A{round(km * 1000):05d}", "line_id": code, "chainage_km": km,
                          "name": f"{network['lines'][code]['name']} · km {km:.1f}",
                          "basis": "Marginal residential catchment over mapped walking streets"})
    return rail.insert_stations(network, additions), len(additions)


def _coverage(network, graph, populations):
    sites = {site: row["coordinates"] for site, row in network["stations"].items()}
    return {key: round(100 * float(population.counts[
                holistic_access.walk_to_station(sites, graph, population)[0] <= WALK_M].sum())
                       / float(population.counts.sum()), 4) for key, population in populations.items()}


def station_audit(network):
    stations = network["stations"]
    points = np.asarray([row["coordinates"] for row in stations.values()]) * rail.LOCAL_METRES
    tree = cKDTree(points)
    return {"physical_sites": len(points), "shared_sites": len(network["transfers"]),
            "pairs_closer_than_750_m": len(tree.query_pairs(MIN_SITE_DISTANCE_M)),
            "scheduled_calls": sum(len(row["station_ids"]) for row in network["lines"].values())}


def _portfolio_rank(trial):
    return (-min(trial["walking"].values()), -sum(trial["walking"].values()),
            trial["station_screen"]["physical_sites"], trial["route_km"], trial["id"])


def designs(reference, graph, context, populations):
    """Fit shapes independently, then rank complete networks on both population grids."""
    primary = populations["worldpop-2026"]
    fitted = coverage_orbitals.fit_orbitals(graph, context, primary)
    layouts, examined = [], {}
    best = fitted[0]
    alternate_outer = next((row for row in fitted if
                            row["audit"]["outer_profile_km"] != best["audit"]["outer_profile_km"]), None)
    shortlist = fitted[:MAX_ORBITAL_LAYOUTS] if alternate_outer is None else [
        *fitted[:MAX_ORBITAL_LAYOUTS - 1], alternate_outer,
    ]
    for orbital in shortlist:
        trial_id = orbital["id"]
        print(f"Building {trial_id} with up to {MAX_TRUNKS} cross-Tigris trunks", flush=True)
        seeds = _ring_seed(reference, orbital)
        likely_stops = (site for stops in orbital["test_stations"].values() for site in stops)
        assembly, trunks = coverage_trunks.assemble(reference, seeds, graph, context, primary,
                                                     max_trunks=MAX_TRUNKS, coverage_sites=likely_stops)
        audit = {"id": trial_id, "orbitals": orbital["audit"], "trunk_search": trunks}
        examined[trial_id] = audit
        if not trunks["trunks"]:
            continue
        assembly = _ring_calls(assembly, orbital)
        assembly, added = _add_missing_access(assembly, graph, context, primary)
        audit.update(sites_added_for_walk_access=added, walking=_coverage(assembly, graph, populations),
                     station_screen=station_audit(assembly), route_km=assembly["topology"]["route_km"],
                     lines=len(assembly["lines"]), candidate_id=assembly["candidate_id"],
                     evaluation_id=assembly["evaluation_id"])
        print(f"{trial_id}: {audit['lines']} lines, {audit['walking']} reachable", flush=True)
        layouts.append((assembly, audit))

    ranked = sorted(layouts, key=lambda item: _portfolio_rank(item[1]))
    networks, trials = {"published": reference}, {}
    for assembly, audit in ranked[:MAX_PUBLISHED_TRIALS]:
        code = "coverage-" + audit["id"].removeprefix("population-orbitals-")
        networks[code] = assembly
        trials[code] = audit
    return networks, trials, {
        "walk_limit_m": WALK_M, "trunk_limit": MAX_TRUNKS,
        "generated_orbital_shapes": [{"id": row["id"], "audit": row["audit"]} for row in fitted],
        "examined_layouts": examined,
    }
