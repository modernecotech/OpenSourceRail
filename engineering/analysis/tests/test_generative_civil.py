"""Independent equilibrium, section integration and bounded-search controls."""

import json
import math
from pathlib import Path

import numpy as np
import pytest
from engineering.generative_design import civil


def seed(**changes):
    values = dict(
        depth_m=1.155,
        stem_width_m=0.3,
        strand_count=48,
        lower_strand_fraction=2 / 3,
        lift_fraction=0.2,
    )
    values.update(changes)
    return values


def test_section_properties_against_independent_vertical_strip_quadrature():
    v = seed(depth_m=1.6, stem_width_m=0.36)
    result = civil.section(v)
    h = v["depth_m"] - 0.22
    # Integrate each constant-width zone with Gauss-Legendre quadrature.
    nodes, weights = np.polynomial.legendre.leggauss(4)
    integrals = []
    for a, b, width in [(0, h, 2 * v["stem_width_m"]), (h, v["depth_m"], 2.9)]:
        z = (nodes + 1) * (b - a) / 2 + a
        integrals.append([sum(weights * width * z**k) * (b - a) / 2 for k in range(3)])
    A, Q, J = np.sum(integrals, axis=0)
    assert result["area_m2"] == pytest.approx(A)
    assert result["centroid_z_m"] == pytest.approx(Q / A)
    assert result["inertia_x_m4"] == pytest.approx(J - Q**2 / A)


def test_retained_seed_matches_layout_and_negative_three_car_diagnostic():
    row = civil.assess(seed())
    assert len(row["strand_points"]) == 48
    assert sorted(set(round(p["z_m"], 8) for p in row["strand_points"])) == [
        0.1,
        0.16,
        0.22,
        0.28,
        0.99,
        1.05,
    ]
    assert row["checks"]["three_car_service_no_tension"]["status"] == "failed"
    assert row["metrics"]["minimum_service_compression_pa"] < 0
    assert row["metrics"]["minimum_geometric_cover_m"] == pytest.approx(0.0524)
    assert row["metrics"]["minimum_grip_surface_gap_m"] == pytest.approx(0.01)
    assert row["remaining_gates"]["six_car_loading"]["status"] == "unknown"
    assert not row["design_complete"] and not row["physical_release"]


def test_selfweight_mass_matches_independent_native_nonoverlapping_concrete_volume():
    row = civil.assess(seed(depth_m=1.4, strand_count=64))
    model = civil.native_model(row)
    concrete = sum(
        civil.volume(p) for p in model["parts"] if p["role"] == "design-solid"
    )
    known = concrete * 2500 + 64 * 0.00014 * 25 * (7850 - 2500)
    assert row["scenarios"][1]["known_concrete_plus_strand_mass_kg"] == pytest.approx(
        known
    )
    for s in row["scenarios"]:
        assert s["nominal_four_leg_tension_n"] * 4 == pytest.approx(
            s["known_concrete_plus_strand_mass_kg"] * civil.G * 1.25
        )
        assert s["two_effective_leg_tension_n"] == pytest.approx(
            2 * s["nominal_four_leg_tension_n"]
        )
        assert s["handling_station_x_m"] == pytest.approx(
            [0.2 * s["span_m"], 0.8 * s["span_m"]]
        )


def test_invalid_search_budgets_and_outside_space_are_rejected():
    for budget in (0, 2049, True, 1.5):
        with pytest.raises(ValueError):
            civil.search(budget=budget)
    with pytest.raises(ValueError, match="outside bounded"):
        civil.assess(seed(strand_count=49))


def test_search_preserves_failed_unknown_ancestry_and_budget(tmp_path):
    first = civil.search(budget=12)
    second = civil.search(budget=12)
    assert first == second
    assert first["candidate_count"] == 12
    assert first["termination"] == "candidate_budget_exhausted"
    assert len({r["id"] for r in first["candidates"]}) == 12
    prior = {}
    for row in first["candidates"]:
        if row["parent_id"]:
            assert row["parent_id"] in prior
            assert row["generation"] == prior[row["parent_id"]]["generation"] + 1
            assert (
                sum(
                    a != b
                    for a, b in zip(
                        row["variables"].values(),
                        prior[row["parent_id"]]["variables"].values(),
                    )
                )
                == 1
            )
        prior[row["id"]] = row
        assert any(c["status"] == "unknown" for c in row["remaining_gates"].values())
        assert not row["design_complete"] and not row["physical_release"]
    assert any(
        c["status"] == "failed"
        for r in first["candidates"]
        for c in r["checks"].values()
    )
    files = civil.write_artifacts(first, tmp_path)
    assert json.loads((tmp_path / "search.json").read_text()) == first
    assert len(files) <= 2
