"""Provisional six-car equilibrium and explicit architecture conflicts."""

import math

import pytest

from engineering.generative_design import integration


@pytest.mark.parametrize("offset", [-0.5, 0, 0.5])
def test_six_car_pattern_preserves_mass_cg_and_asymmetric_bogie_reactions(offset):
    result = integration.planning_axles(384000, offset, multiplier=1.25)
    axles = result["axles"]
    weight = 384000 * 9.80665 * 1.25
    assert len(axles) == 24
    assert len({a["id"] for a in axles}) == 24
    assert math.fsum(a["force_n"] for a in axles) == pytest.approx(weight)
    assert math.fsum(a["force_n"] * a["x_m"] for a in axles) / weight == pytest.approx(
        55.5 + offset
    )
    if offset:
        assert axles[0]["force_n"] != axles[2]["force_n"]
    assert result["supplier_pattern"] is None
    assert result["accepted_supplier_pattern"] is False


@pytest.mark.parametrize(
    "mass,offset,multiplier", [(0, 0, 1), (258000, 50, 1), (258000, 0, float("nan"))]
)
def test_impossible_or_nonfinite_planning_load_rejected(mass, offset, multiplier):
    with pytest.raises(ValueError):
        integration.planning_axles(mass, offset, multiplier=multiplier)


def test_platform_lengths_preserve_existing_sources_and_fail_short_six_car_cases():
    result = integration.platform_variations()
    assert len(result) == 7
    for variant in result:
        assert variant["source_platform_length_m"] < 60
        assert variant["selected_preliminary_length_m"] == 116
        for case in variant["candidates"]:
            assert case["six_car_length_screen"] == (case["platform_length_m"] >= 115)
            assert not case["site_fit_accepted"] and not case["egress_accepted"]


def test_closed_assembly_graph_does_not_close_interface_acceptance():
    result = integration.graph_and_interfaces()
    assert result["graph_closed"]
    assert result["product_count"] == 120 and result["assembly_count"] == 26
    assert len(result["interfaces"]) == 12
    assert all(
        not r["accepted_reactions"] and not r["accepted_tolerance_stack"]
        for r in result["interfaces"]
    )
    assert not result["manufacturing_release"]
