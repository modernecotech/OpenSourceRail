"""Urban gap service geometry, topology and reproducible pedestrian access."""

from copy import deepcopy

import numpy as np
import pytest
from scipy.sparse import csr_matrix
from scipy.spatial import cKDTree

from . import coverage_gap as gap, holistic_access, holistic_network as rail, ring_corridors

CONTEXT = {"layers": {"water": []}}


def _coordinates(xy):
    return (np.asarray(xy, dtype=float) / rail.LOCAL_METRES).tolist()


def _fixture():
    physical = {
        "nw": (-6_000, 5_000), "ne": (6_000, 5_000),
        "sw": (-6_000, -5_000), "se": (6_000, -5_000),
        "left": (-4_000, 0), "right": (4_000, 0),
        "left-ring": (-4_000, 5_000), "right-ring": (4_000, 5_000),
        "link-end": (0, -3_000), "link-ring": (0, 5_000),
    }
    stations = {code: {"coordinates": _coordinates(point), "name": code, "lines": [], "basis": "Fixture"}
                for code, point in physical.items()}
    calls = {"M16": ["nw", "left-ring", "link-ring", "right-ring", "ne", "se", "sw"],
             "L": ["left", "left-ring"], "R": ["right", "right-ring"], "A": ["link-end", "link-ring"]}
    lines = {}
    for code, ids in calls.items():
        vertices = [stations[stop]["coordinates"] for stop in ids]
        is_ring = code == "M16"
        line = rail._physical_line(vertices + vertices[:1] if is_ring else vertices,
                                   ids, stations, [], "Fixture", loop=is_ring)
        lines[code] = line | {"name": code}
        for stop in ids:
            stations[stop]["lines"].append(code)
    record = {"lines": lines, "stations": stations, "transfers": [],
              "physical_accepted": False, "operating_timetable_validated": False}
    ring_corridors._refresh_transfers(record)
    record["topology"] = rail.validate(record)
    rail._identity(record)

    grid = np.arange(-7_000, 7_001, 500)
    points = np.array([(x, y) for x in grid for y in grid])
    indices = {tuple(point): i for i, point in enumerate(points)}
    pairs = [(i, indices[neighbor]) for i, (x, y) in enumerate(points)
             for neighbor in ((x - 500, y), (x + 500, y), (x, y - 500), (x, y + 500)) if neighbor in indices]
    matrix = csr_matrix((np.full(len(pairs), 500.), tuple(zip(*pairs, strict=True))), shape=(len(points), len(points)))
    graph = (None, matrix, np.arange(len(points)), cKDTree(points), None)
    residents = np.asarray([(-2_000, y) for y in (-500, 0, 500)] + [(2_000, y) for y in (-500, 0, 500)])
    coords = residents / rail.LOCAL_METRES
    pop = holistic_access.Population({}, coords, np.full(len(residents), 1_000.), np.zeros(len(residents)),
                                      np.array([indices[tuple(point)] for point in residents]), residents)
    return record, graph, {"worldpop-2026": pop, "ghsl-2025": pop}


def test_urban_gap_adds_one_deterministic_interconnected_service_with_measured_benefit():
    source, graph, populations = _fixture()
    frozen = deepcopy(source)
    result, audit = gap.add_gap_line(source, graph, CONTEXT, populations)
    replay, proof = gap.add_gap_line(source, graph, CONTEXT, populations)
    assert source == frozen
    assert result == replay and audit == proof
    assert set(result["lines"]) == {*source["lines"], gap.GAP_LINE_ID}
    assert result["lines"][gap.GAP_LINE_ID]["service_role"] == gap.GAP_ROLE
    assert rail.validate(result)["connected_components"] == 1
    screened = gap.validate_gap_line(result, graph, CONTEXT)
    assert set(screened["connected_route_ids"]) == {"L", "R", "A"}
    assert audit["selected"]["newly_reached"] == {"worldpop-2026": 6_000, "ghsl-2025": 6_000}


def test_urban_gap_rejects_undeclared_role():
    source, graph, populations = _fixture()
    result, _ = gap.add_gap_line(source, graph, CONTEXT, populations)
    del result["lines"][gap.GAP_LINE_ID]["service_role"]
    with pytest.raises(ValueError, match="urban-gap role"):
        gap.validate_gap_line(result, graph, CONTEXT)


def test_urban_gap_held_without_a_closed_outer_ring():
    source, graph, populations = _fixture()
    source["lines"]["M16"]["loop"] = False
    revised, audit = gap.add_gap_line(source, graph, CONTEXT, populations)
    assert revised is source and audit["selected"] is None
    assert "closed outer ring" in audit["held"]


def test_urban_gap_rejects_an_unverified_river_crossing():
    source, graph, populations = _fixture()
    result, _ = gap.add_gap_line(source, graph, CONTEXT, populations)
    wet_context = {"layers": {"water": [{
        "properties": {"name:en": "Tigris River"},
        "geometry": {"type": "LineString", "coordinates": _coordinates([(500, -7_000), (500, 7_000)])},
    }]}}
    with pytest.raises(ValueError, match="lacks mapped water-crossing evidence"):
        gap.validate_gap_line(result, graph, wet_context)
