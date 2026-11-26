"""Suburban continuations keep the parent railway aligned and connected."""

from copy import deepcopy

import numpy as np
import pytest
from scipy.spatial import cKDTree
from shapely import Point

from . import coverage_extensions as extensions, holistic_network as rail


def _coordinates(values):
    return (np.asarray(values) / rail.LOCAL_METRES).tolist()


def _core():
    sites = {"start": [0, 0], "shared": [3_000, 0], "end": [4_000, 0], "branch-end": [3_000, 2_000]}
    stations = {key: {"coordinates": _coordinates(point), "name": key, "basis": "Fixture", "lines": []}
                for key, point in sites.items()}
    lines = {}
    for route, ids in (("trunk", ["start", "shared", "end"]), ("connecting", ["shared", "branch-end"])):
        lines[route] = rail._physical_line([stations[key]["coordinates"] for key in ids],
                                           ids, stations, [], "Fixture")
        lines[route]["name"] = route
        for key in ids:
            stations[key]["lines"].append(route)
    return {"lines": lines, "stations": stations, "transfers": [
        {"id": "shared", "station_ids": ["shared"], "lines": ["trunk", "connecting"]}]}


@pytest.mark.parametrize("end, points, terminal", [(0, [(0, 0), (-2_000, 0)], "start"),
                                                  (1, [(4_000, 0), (6_000, 0)], "end")])
def test_extend_each_end_reconciles_chainage_and_keeps_shared_stop(end, points, terminal):
    network = _core()
    parent = deepcopy(network)
    track = rail.Track(_coordinates(points))
    extension = extensions.Extension("trunk", end, terminal, track,
                                     [(1., track.at(1.)), (2., track.at(2.))], [], {})
    extensions._install(network, extension)
    assert rail.validate(network)["connected_components"] == 1
    before, after = parent["lines"]["trunk"], network["lines"]["trunk"]
    assert after["one_way_km"] == pytest.approx(before["one_way_km"] + 2)
    retained = after["geometry"][1:] if end == 0 else after["geometry"][:-1]
    assert retained == before["geometry"]
    assert network["lines"]["connecting"] == parent["lines"]["connecting"]
    assert network["transfers"] == parent["transfers"]
    assert all(network["stations"][site] == row for site, row in parent["stations"].items())
    for site, km in before["station_chainage_km"].items():
        assert after["station_chainage_km"][site] == pytest.approx(km + (2 if end == 0 else 0))


def test_legal_platform_sequence_bridges_gaps_with_available_streets():
    tail = rail.Track(_coordinates([(0, 0), (6_000, 0)]))
    streets = cKDTree([[0, 0], [2_000, 0], [4_000, 0], [6_000, 0]])
    stations = cKDTree([[0, 0]])
    demand = cKDTree([[2_000, 0], [4_000, 0], [6_000, 0]])
    context = {"layers": {"water": []}}
    stops = extensions._stops(tail, stations, streets, context, demand, np.ones(3))
    assert [km for km, _ in stops] == pytest.approx([2., 4., 6.])
    sparse = cKDTree([[0, 0], [2_000, 0], [6_000, 0]])
    assert extensions._stops(tail, stations, sparse, context, demand, np.ones(3)) == []


def test_rejects_tail_entering_outer_ring_before_station_search():
    core = rail.Track(_coordinates([(0, 0), (2_000, 0)]))
    outer = Point(3_000, 0).buffer(200)
    option, reason = extensions._proposal(core, "trunk", 1, [4_000, 0], outer,
                                          None, None, None, None, None, None, None, None)
    assert option is None and reason == "re-enters the outer ring"
