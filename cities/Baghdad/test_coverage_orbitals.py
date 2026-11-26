"""Check the population-fitted orbitals against the Baghdad geometry regressions."""

from itertools import product

import numpy as np
from shapely.geometry import Point, Polygon

from cities.Baghdad import central_access, coverage_orbitals as orbitals, holistic_access


def test_closed_fit_checks_the_transition_across_the_last_bearing():
    radii = np.array([5000, 6000, 7000])
    rewards = np.array([[8., 0., 0.], [3., 0., 0.], [0., 0., 7.], [0., 0., 8.]])
    path = orbitals._smooth_profile(rewards, radii)

    def score(cycle):
        changes = np.diff(np.r_[cycle, cycle[0]])
        if np.any(np.abs(changes) > 1500):
            return -np.inf
        return sum(reward[(radius - 5000) // 1000] for reward, radius in zip(rewards, cycle, strict=True)) - (
            .23 * np.sum((changes / 1000)**2))

    assert score(path) == max(map(score, product(radii, repeat=len(rewards))))


def test_nonlocal_clearance_detects_a_turnback_on_a_simple_closed_ring():
    foldback = Polygon([(0, 0), (4000, 0), (4000, 4000), (2200, 4000),
                        (2200, 800), (1800, 800), (1800, 4000), (0, 4000)])
    assert foldback.is_valid
    assert orbitals._arc_clearance(foldback)["close_sample_pairs"] > 0
    assert orbitals._arc_clearance(foldback.convex_hull)["close_sample_pairs"] == 0


def test_baghdad_fit_serves_distinct_catchments_without_central_turnback():
    context = central_access.read(central_access.INPUTS[-1])
    graph = central_access.walking_graph()
    population = holistic_access.load_population("worldpop-2026", graph)
    variants = orbitals.fit_orbitals(graph, context, population)
    assert len(variants) >= 2
    assert len({row["id"] for row in variants}) == len(variants)
    for row in variants:
        inner, middle, outer = (row["polygons"][code] for code in orbitals.RING_IDS)
        audit = row["audit"]
        assert all(ring.is_valid and ring.exterior.is_simple for ring in (inner, middle, outer))
        assert inner.convex_hull.area - inner.area < .01
        assert all(inner.contains(Point(np.asarray(point) * orbitals.LOCAL_METRES))
                   for point in orbitals.central_destinations(context).values())
        assert middle.contains(inner.buffer(orbitals.MIN_RING_SEPARATION_M))
        assert outer.contains(middle.buffer(orbitals.MIN_RING_SEPARATION_M))
        assert audit["inner_nonlocal_clearance"]["close_sample_pairs"] == 0
        assert audit["middle_outer_separation"]["p90_m"] > audit["middle_outer_separation"]["p10_m"]
        assert audit["unique_ring_walk_population"]["M09"] > 0
        assert audit["unique_ring_walk_population"]["M09"] <= audit["ring_walk_population"]["M09"]
        for ring, polygon in zip(orbitals.RING_IDS, (inner, middle, outer), strict=True):
            boundary = polygon.exterior
            coordinates = np.asarray(row["test_stations"][ring]) * orbitals.LOCAL_METRES
            stations = [Point(point) for point in coordinates]
            assert all(boundary.distance(station) < 1e-6 for station in stations)
            chainages = sorted(boundary.project(station) for station in stations)
            circular_spacing = np.diff([*chainages, chainages[0] + boundary.length])
            assert min(circular_spacing) >= orbitals.MIN_RING_STOP_SEPARATION_M - 1e-6
