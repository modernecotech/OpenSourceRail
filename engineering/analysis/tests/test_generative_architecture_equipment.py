"""Primary published limits versus declared research envelopes, not acceptance."""

import math

import pytest

from engineering.generative_design import architecture_equipment as e


def test_real_ccl_geometry_rejects_the_small_hypothetical_tool_reservation():
    case = e.ccl_case()
    m = case["reference_metrics"]
    p = case["published"]
    checks = {r["id"]: r for r in case["criteria"]}
    # At60mm axes,55mm cylinder radius plus7.6mm strand radius
    # exceeds the centre distance by2.6mm in the DECLARED common plane.
    assert p["main_cylinder_diameter_m"] == 0.110
    assert m["same_plane_cylinder_to_adjacent_straight_strand_gap_m"] == pytest.approx(
        -0.0026
    )
    assert (
        checks["same_plane_body_to_straight_tail_clearance"]["status"]
        == "failed-declared-screen"
    )
    assert p["fully_retracted_short_length_m"] == 0.833
    assert m["short_retracted_axial_reservation_gap_m"] == pytest.approx(-0.583)
    assert m["same_tier_width_reservation_gap_m"] == pytest.approx(-0.04)
    assert m["same_tier_height_reservation_gap_m"] == pytest.approx(-0.114)
    assert not m["actual_tool_shape_collision_established"]
    assert m["actual_nose_and_cylinder_axial_position_m"] is None
    assert not case["existing_four_tier_configuration_qualified"]
    assert not case["hypothetical_90x200_tool_qualified_by_this_model"]


def test_force_scalar_pass_cannot_override_the_published_strand_range():
    case = e.ccl_case()
    p = case["published"]
    checks = {r["id"]: r for r in case["criteria"]}
    assert p["maximum_design_load_n"] == 247000
    assert case["reference_metrics"]["declared_initial_force_each_n"] == 154000
    assert checks["force_scalar"]["status"] == "passed-arithmetic-only"
    assert p["strand_diameter_range_m"][1] == 0.015
    assert case["reference_metrics"]["strand_envelope_diameter_m"] == 0.0152
    assert (
        checks["published_numerical_strand_range"]["status"] == "failed-declared-screen"
    )
    assert case["accepted_design_load_n"] is None
    assert "nominal" in checks["published_numerical_strand_range"]["basis"]


def test_stroke_is_distinguished_from_body_length_and_unknown_free_length():
    case = e.ccl_case()
    p = case["published"]
    extension = case["reference_metrics"]["elastic_strand_extension_reference_m"]
    # Independent elastic strain times25mbeam+1.25mtail.
    assert extension == pytest.approx(1100e6 / 195e9 * 26.25)
    assert extension < p["short_extension_m"] == 0.194
    assert p["long_extension_m"] == 0.494
    assert p["minimum_strand_length_m"] == 0.265
    assert any("full free-strand length" in g for g in case["mandatory_unknown_gates"])
    assert (
        p["fully_retracted_short_length_m"]
        > case["reference_metrics"]["reference_axial_tier_pitch_m"]
    )


def test_macalloy_public_ultimate_strength_gives_no_design_resistance():
    case = e.macalloy_case()
    assert case["published"]["family_minimum_ultimate_strength_pa"] == 1030e6
    assert case["published"]["carbon_bar_diameter_range_m"] == [0.0265, 0.075]
    assert case["route_sensitivity"]["optimistic_minimum_piece_count"] == 3
    assert case["route_sensitivity"]["optimistic_minimum_inline_coupler_count"] == 2
    assert case["accepted_design_tension_n"] is None
    assert case["accepted_thread_or_coupler_resistance_n"] is None
    assert case["selected_bar_count"] is None
    assert any("login-only" in s["locator"] for s in case["sources"])


def test_mechan_sensitivities_retain_force_balance_and_no_offered_capacity():
    case = e.mechan_case(loaded_car_mass_kg=60000)
    rows = case["jack_sensitivities"]
    assert len(rows) == 8
    for r in rows:
        # These are aggregate demand hypotheses, with CG/reaction balance
        # expressly unaccepted; they preserve declared totalfactoredforce.
        assert r["demand_mass_equivalent_kg_each"] * r[
            "effective_jacks"
        ] == pytest.approx(60000 * r["dynamic_hypothesis"] * r["imbalance_hypothesis"])
        assert r["accepted_capacity_kg_each"] is None
        assert not r["reaction_distribution_accepted"]
    assert max(r["demand_mass_equivalent_kg_each"] for r in rows) == 30000
    assert case["accepted_capacity_per_jack_kg"] is None
    assert case["offered_configuration"] is None
    assert (
        case["existing_vehicle_crane_comparison"]["status"]
        == "failed-whole-loaded-car-scalar"
    )
    assert case["existing_vehicle_crane_comparison"]["actual_empty_car_mass_kg"] is None
    assert case["published"]["family_capacity_range_kg"] == [5000, 40000]
    assert "historical" in case["model"]


def test_higher_mass_reopens_a_historical_thirty_tonne_enquiry():
    case = e.mechan_case(loaded_car_mass_kg=90000)
    assert any(
        r["historical_capacity_arithmetic"] == "failed-declared-screen"
        for r in case["jack_sensitivities"]
    )
    assert not case["existing_vehicle_crane_comparison"]["accepted_whole_car_lift"]


@pytest.mark.parametrize("mass", [0, -1, True, math.inf, math.nan])
def test_unphysical_or_boolean_car_mass_rejected(mass):
    with pytest.raises(ValueError, match="positive finite"):
        e.mechan_case(loaded_car_mass_kg=mass)


def test_all_primary_leads_and_source_hashes_retain_no_release_or_contact():
    report = e.run()
    assert len(report["supplier_cases"]) == 3
    assert report["retrieved_on"] == "2026-10-17"
    assert report["source_sha256"]
    assert report["accepted_equipment_configurations"] == 0
    for field in [
        "procurement_authorized",
        "supplier_contacted",
        "engineering_design_complete",
        "manufacturing_release",
        "physical_release",
    ]:
        assert report[field] is False
    for case in report["supplier_cases"]:
        assert case["mandatory_unknown_gates"]
        assert case["offered_configuration"] is None
        assert not case["supplier_contacted"] and not case["physical_release"]
        assert not case["exact_offered_origin_accepted"]
        assert all(
            s["url"].startswith("https://") and s["retrieved_on"] == "2026-10-17"
            for s in case["sources"]
        )
