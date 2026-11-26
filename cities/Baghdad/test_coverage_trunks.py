"""Check fresh trunk connectivity, station consolidation and water limits."""

from copy import deepcopy
from types import SimpleNamespace

import numpy as np
from scipy.spatial import cKDTree
from shapely import box

from cities.Baghdad import coverage_trunks as trunks, holistic_network as rail
from cities.Baghdad import holistic_through as through


def _coordinates(points):
    return np.asarray(points, dtype=float) / rail.LOCAL_METRES


def _track(points):
    return rail.Track(_coordinates(points))


def test_alternate_platforms_repair_a_gap_without_relaxing_spacing():
    km = np.array([0., 1.25, 3.375, 5.75, 7.])
    assert trunks.spaced_platform_path(km, np.ones_like(km), 1.65) == [1, 2, 3, 4]
    missing = km[[0, 1, 3, 4]]
    assert trunks.spaced_platform_path(missing, np.ones_like(missing), 1.65) is None


def test_named_bent_arm_preserves_turn_cap_and_fixed_terminal():
    bank, target = np.asarray([[0., 0.], [10_000, 7_000]])
    direction = np.array([1., 0.])
    arms = list(trunks._bent_arms(bank, direction, target))
    assert arms
    for arm in arms:
        assert np.array_equal(arm[[0, -1]], [bank, target])
        entry, exit_ = np.diff(arm, axis=0)
        assert trunks.third_ring_through._turn(direction, entry) <= trunks.MAX_TURN_DEG + 1e-8
        assert trunks.third_ring_through._turn(entry, exit_) <= trunks.MAX_TURN_DEG + 1e-8


def _rings():
    record = {"lines": {}, "stations": {}, "transfers": []}
    for code, radius in zip(trunks.RINGS, (2_000, 5_000, 8_000), strict=True):
        corner = [(-radius, -radius), (radius, -radius), (radius, radius), (-radius, radius)]
        track = _track([*corner, corner[0]])
        calls = [f"{code}-seed-0", f"{code}-seed-1"]
        line = {"geometry": track.coordinates.tolist(), "one_way_km": track.km, "loop": True,
                "station_ids": calls, "station_chainage_km": dict(zip(calls, (0., track.km / 2), strict=True))}
        record["lines"][code] = line
        for stop, km in line["station_chainage_km"].items():
            record["stations"][stop] = {"name": stop, "coordinates": track.at(km), "lines": [code], "basis": "Test"}
    return record


def test_airport_is_a_terminal_of_the_connected_through_trunk(monkeypatch):
    rings = _rings()
    original = deepcopy(rings)
    street = cKDTree(np.column_stack((np.arange(-12_000, 12_001, 125), np.zeros(193))))
    graph = (None, None, None, street)
    context = {"layers": {"water": []}}
    airport = _coordinates([(-12_000, 0)]).tolist()[0]
    reference = {"stations": {"Airport-00": {"coordinates": airport}}, "lines": {"legacy-stub": {}}}
    population = SimpleNamespace(coordinates=street.data[::4] / rail.LOCAL_METRES,
                                 counts=np.full(49, 100.), source={"dataset": "fixture"})

    def screen_candidates(terminals, demand, weights, airport, graph, context, polygons, ring_tracks):
        track = _track([(-12_000, 0), (-200, 0), (200, 0), (12_000, 0)])
        sites = trunks._ring_sites(track, ring_tracks, polygons, graph, context)
        candidate = {"track": track, "bridge": 1, "reach": track.points[1:3],
                     "wet": [{"mapped_wet_width_m": 300}], "airport": True,
                     "ring_sites": sites, "proxy": 1000, "detour": 1, "terminals": (0, 1)}
        return [candidate], [{"accepted": 1}]

    monkeypatch.setattr(trunks, "_pool", screen_candidates)
    result, audit = trunks.assemble(reference, rings, graph, context, population)
    assert rings == original
    assert set(result["lines"]) == {*trunks.RINGS, "T01"}
    assert result["lines"]["T01"]["station_ids"][0] == "Airport-00"
    assert result["topology"]["connected_components"] == 1
    assert audit["holds"] == []
    assert audit["trunks"][0]["both_terminals_outside"]
    assert audit["trunks"][0]["tigris_crossing_count"] == 1
    assert all(len(calls) == 2 for calls in audit["trunks"][0]["crossing_interchanges"].values())
    assert result["candidate_id"] == audit["candidate_id"]
    assert result["evaluation_id"] == audit["evaluation_id"]


def test_close_parallel_trunks_are_distinguished_from_crossing_trunks():
    first = _track([(0, 0), (20_000, 0)])
    parallel = _track([(0, 250), (20_000, 250)])
    crossing = _track([(10_000, -10_000), (10_000, 10_000)])
    assert trunks._parallel_share(first, parallel) > trunks.MAX_PARALLEL_SHARE
    assert trunks._parallel_share(first, crossing) < trunks.MAX_PARALLEL_SHARE


def test_dedicated_tigris_reach_requires_two_actual_banks_and_bounded_wet_width():
    centreline = {"type": "LineString", "coordinates": _coordinates([(0, -2_000), (0, 2_000)]).tolist()}
    river = through.WaterGeometry.from_context({"layers": {"water": [{"geometry": centreline}]}})
    start, end = np.asarray([(-700, 0), (700, 0)], dtype=float)

    def crossing(width):
        edges = [(-width / 2, -1_000), (width / 2, -1_000),
                 (width / 2, 1_000), (-width / 2, 1_000), (-width / 2, -1_000)]
        geometry = {"type": "Polygon", "coordinates": [_coordinates(edges).tolist()]}
        context = {"layers": {"water": [{"geometry": centreline}, {"geometry": geometry}]}}
        return trunks._dedicated_crossing(start, end, context, through.WaterGeometry.from_context(context), river)

    assert crossing(300) == [{"chainage_km": .7, "mapped_wet_width_m": 300}]
    assert crossing(900) is None

def test_suburban_parallel_is_a_continuous_run_with_a_five_kilometre_width():
    first = _track([(0, 0), (10_000, 0)])
    overlapping = _track([(8_401, 1_000), (18_401, 1_000)])
    separated = _track([(0, 5_000), (10_000, 5_000)])
    short_overlap = _track([(8_501, 1_000), (18_501, 1_000)])
    near_width = _track([(0, 4_999), (10_000, 4_999)])
    crossing = _track([(5_000, -5_000), (5_000, 5_000)])
    assert trunks.suburban_parallel((first,), (overlapping,))
    assert trunks.suburban_parallel((first,), (near_width,))
    assert not trunks.suburban_parallel((first,), (separated,))
    assert not trunks.suburban_parallel((first,), (short_overlap,))
    assert not trunks.suburban_parallel((first,), (crossing,))


def test_suburban_parallel_clips_off_inner_sections_and_ignores_disjoint_end_caps():
    boundary = box(0, 0, 10_000, 10_000)
    inside = _track([(1_000, 1_000), (9_000, 1_000)])
    first = _track([(-5_000, 0), (-1_000, 0)])
    second = _track([(0, 1_000), (4_000, 1_000)])
    assert trunks.suburban_arms(inside, boundary) == ()
    assert not trunks.suburban_parallel((first,), (second,))


def test_suburban_contour_checks_departure_spacing_and_ignores_tangent_touch():
    contour = box(0, 0, 10_000, 10_000)
    touches_then_enters = _track([(-3_000, 2_000), (0, 0), (-600, 600), (600, 3_000), (11_000, 3_500)])
    other = _track([(-4_000, 2_500), (14_000, 6_500)])
    ends_short = _track([(-5_000, 5_000), (1_000, 5_000)])
    first = trunks.suburban_departures(touches_then_enters, contour)
    second = trunks.suburban_departures(other, contour)
    assert np.allclose(first[0], [0, 1_800])
    assert trunks.suburban_departure_distance(first, second) < 5_000
    assert trunks.suburban_departures(ends_short, contour) is None
