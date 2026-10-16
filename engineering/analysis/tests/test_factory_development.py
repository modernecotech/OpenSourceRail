"""Analytical controls for the second factory development iteration."""

from copy import deepcopy
import json
import math

import pytest

from engineering.factory_examples import build, models, development as dev


@pytest.fixture(scope="module")
def context():
    folder = build.PACKAGE / "data"
    a = json.loads((folder / "basis.json").read_text())["assumptions"]
    inputs = json.loads((folder / "development.json").read_text())
    equipment = {
        e["id"]: e
        for e in json.loads((folder / "equipment.json").read_text())["equipment"]
    }
    return a, inputs, equipment


@pytest.fixture(scope="module")
def report(context):
    a, i, e = context
    return dev.build(a, i, models.fixture(a), models.civil(a), e)


def test_buckling_converges_to_independent_euler_solution():
    L, E, I = 25, 210e9, 0.000374295552
    analytical = math.pi**2 * E * I / L**2
    error = []
    for n in (4, 8, 16):
        error.append(abs(dev.column_buckling(L, E, I, n, []) / analytical - 1))
    assert error[2] < error[1] < error[0]
    assert error[2] < 3e-6


def test_second_order_sinusoidal_bow_matches_closed_form():
    L, E, I, bow = 25, 210e9, 0.000374295552, 0.01
    Pcr = math.pi**2 * E * I / L**2
    result = dev.imperfect_column(L, E, I, 50, [], Pcr / 4, bow)
    assert result["stable_elastic_tangent"]
    assert result["additional_sway_m"] == pytest.approx(bow / 3, rel=2e-6)
    assert result["free_force_residual_n"] < 1e-5
    assert result["free_moment_residual_nm"] < 1e-5
    assert result["maximum_abs_brace_force_n"] == 0
    assert not dev.imperfect_column(L, E, I, 50, [], Pcr * 1.1, bow)[
        "stable_elastic_tangent"
    ]


def test_ground_restraint_sweep_preserves_failed_cases_and_unknowns(report):
    bed = report["bed"]
    cases = bed["cases"]
    assert all(
        cases[j]["elastic_load_factor"] < cases[j + 1]["elastic_load_factor"]
        for j in range(3)
    )
    assert cases[0]["elastic_load_factor"] < 1
    assert cases[1]["elastic_load_factor"] < 1
    assert cases[2]["elastic_load_factor"] > 1
    assert cases[0]["imperfect_response"]["brace_reactions"] is None
    assert cases[2]["imperfect_response"]["maximum_abs_brace_force_n"] > 0
    assert bed["foundation_stiffness_measured_n_m"] is None
    assert bed["strongback_resistance"] is None
    assert bed["physical_release"] is False
    assert bed["active_length_m"] == 26
    assert bed["assumed_pinned_end_planes_x_m"] == [-0.5, 25.5]
    assert [
        r["global_x_m"] for r in cases[2]["imperfect_response"]["brace_reactions"]
    ] == [3, 6, 9, 12, 15, 18, 21, 24]


@pytest.mark.parametrize("springs", [[(3, -1)], [(25, 1e6)], [(3.1, 1e6)]])
def test_invalid_or_unmodelled_spring_locations_rejected(springs):
    with pytest.raises(ValueError):
        dev.column_buckling(25, 210e9, 0.000374, 50, springs)


def test_full_span_keeps_baseline_and_failed_balanced_alternative(report):
    p = report["prestress"]
    by_id = {r["id"]: r for r in p["alternatives"]}
    assert (
        by_id["low-40"]["scenarios"][0]["minimum_compression_pa_by_stage"]["transfer"]
        < -3e6
    )
    assert by_id["balanced-40"]["scenarios"][0]["no_tension_research_screen"]
    assert not by_id["balanced-40"]["scenarios"][1]["no_tension_research_screen"]
    assert all(
        s["no_tension_research_screen"] for s in by_id["balanced-48"]["scenarios"]
    )
    assert by_id["balanced-48"]["initial_force_n"] == pytest.approx(7.392e6)
    assert p["transfer_length_qualified"] is False
    assert p["material_stress_limits_qualified"] is False
    assert p["railway_live_load_qualified"] is False
    assert p["physical_release"] is False


def test_gravity_patches_and_strand_displacement_reconcile_with_equilibrium(context):
    a, _, _ = context
    L = 25

    def moment(x):
        return dev.developed_selfweight(L, x, 48, a)[0]

    _, mass = dev.developed_selfweight(L, 0, 48, a)
    concrete_mass = models.civil(a)["scenarios"][1]["developed_mass_kg"]
    assert mass == pytest.approx(concrete_mass + 48 * 0.00014 * L * (7850 - 2500))
    assert moment(0) == pytest.approx(0, abs=1e-6)
    assert moment(L) == pytest.approx(0, abs=1e-6)
    assert moment(3) == pytest.approx(moment(L - 3))
    dx = 1e-5
    assert (moment(dx) - moment(0)) / dx == pytest.approx(mass * dev.G / 2, rel=1e-5)
    assert moment(L / 2) > models.civil(a)["scenarios"][1]["bare_dead_moment_nm"]


def test_workholding_equilibrium_and_preload_are_not_holding_force(context, report):
    a, i, e = context
    r = report["workholding"]
    expected = 500 * 9.80665 * 1.5 + 3 * 500 - 750
    for case in r["cases"]:
        assert sum(case["vertical_reactions_n"]) == pytest.approx(expected)
    assert r["minimum_contact_reaction_n"] > 0
    assert r["published_nominal_holding_force_n"] == 3500
    assert not r["preload_demonstrated"]
    assert r["clamp_force_compatibility"] is None
    bad = deepcopy(i["fixture"])
    bad["tool_upward_n"] = 20000
    adverse = dev.workholding(a, bad, models.fixture(a), e["brauer-h350-2blc"])
    assert not adverse["all_cases_vertical_contact_screen"]
    assert adverse["released"] is False


def test_rated_crane_wheel_force_conservation_and_concept_girder(report, context):
    a, i, _ = context
    r = report["runway"]
    cfg = i["runway"]
    expected = (125000 * 1.1 + 15000 + 30000) * dev.G
    assert r["vertical_sum_n"] == pytest.approx(expected)
    assert 2 * (r["near_wheel_n"] + r["far_wheel_n"]) == pytest.approx(expected)
    assert r["near_wheel_n"] > r["far_wheel_n"]
    parts = dev.runway_parts(cfg)
    steel = sum(models.volume(p) for p in parts if p["role"] == "runway-girder-concept")
    assert steel == pytest.approx(2 * cfg["bay_span_m"] * r["gross_girder_area_m2"])
    assert r["supplier_reactions_confirmed"] is False
    assert r["pad_resistance_established"] is False
    assert cfg["allowable_ground_bearing_pa"] is None
    route = r["manufacturing_interfaces"]
    assert not route["baseplate_cv5_diameter_screen"]
    assert not route["baseplate_cv5_mass_screen"]
    assert route["baseplate_nominal_mass_kg"] == pytest.approx(317.925)
    assert not route["fabrication_supplier_selected"]


def test_development_cad_strand_counts_and_heights_agree_with_study(context, report):
    _, i, _ = context
    candidate = next(
        r
        for r in report["prestress"]["alternatives"]
        if r["id"] == report["prestress"]["candidate_id"]
    )
    parts = dev.revised_bed_parts(models.mould_bed(), candidate, i["bed"])
    strands = [p for p in parts if p["role"] == "strand-envelope"]
    assert len(strands) == 48
    heights = [p["at_m"][2] + 0.0075 - 0.8 for p in strands]
    for z, count in candidate["rows"]:
        assert sum(abs(h - z) < 1e-9 for h in heights) == count
    assert sum(p["role"] == "foundation-reservation" for p in parts) == 16
