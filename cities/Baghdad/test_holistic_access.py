"""Regressions for deterministic selection and explicit walking-coverage gaps."""

import numpy as np
import pytest

from cities.Baghdad import holistic_access as access
from cities.Baghdad.holistic_network import LOCAL_METRES


def candidate(line, km, close, longer=()):
    return access.Opportunity(line, km, np.asarray(close, dtype=int), np.asarray(longer, dtype=int))


def test_recalculate_marginal_population_and_enforce_station_spacing():
    sites = [candidate("M1", 1.0, [0, 1]), candidate("M1", 1.3, [2]),
             candidate("M2", 1.0, [0, 1, 3]), candidate("M3", 1.0, [4])]
    counts = np.array([100, 65, 23, 2, 10])
    existing = np.full(5, np.inf)
    result = access.rank_stations(sites, counts, existing, 650, None)
    assert [(r["line_id"], r["chainage_km"]) for r in result] == [("M2", 1.), ("M1", 1.3), ("M3", 1.)]


def test_tie_break_uses_longer_access_then_line_and_chainage():
    sites = [candidate("M2", 1., [0], [1]), candidate("M1", 2., [0], [1]),
             candidate("M1", 1., [0], [1]), candidate("M0", 1., [0])]
    for order in (sites, list(reversed(sites))):
        additions = access.rank_stations(order, np.array([10, 5]), np.array([np.inf, np.inf]), 650, 1)
        assert [(row["line_id"], row["chainage_km"]) for row in additions] == [("M1", 1.)]


def test_ring_infill_reserves_spacing_on_both_sides_of_first_stop():
    geometry = (np.array([[0, 0], [1000, 0], [1000, 1000], [0, 1000], [0, 0]]) / LOCAL_METRES).tolist()
    line = {"geometry": geometry, "station_chainage_km": {"first": 0, "opposite": 2}, "loop": True}
    assert [km for km, _ in access.sampled_positions(line, 250, 650)] == [.75, 1., 1.25, 2.75, 3., 3.25]


def test_access_denominator_includes_people_without_a_street_snap():
    population = access.Population({"dataset": "Test", "year": 2026, "bbox": {}, "documentation": "local"},
                                   np.array([[44.37, 33.30], [44.39, 33.33], [44.50, 33.48]]),
                                   np.array([100., 50., 50.]), np.array([5., 500., 5.]),
                                   np.array([0, 1, 2]), np.array([[0, 0], [0, 1], [0, 2]]))
    result = access.summarize(population, {"connected": np.array([777., np.inf, 1000.])})["metropolitan"]
    assert result["population"] == 200
    assert result["beyond_street_snap"] == 50
    assert result["cases"]["connected"]["800"]["share_pct"] == pytest.approx(50)
    assert result["cases"]["connected"]["1200"]["share_pct"] == pytest.approx(75)
