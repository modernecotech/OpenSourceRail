"""Checks for the Baghdad two-track civil quantity/cost handoff."""
import pytest

from engineering.outline.baghdad_viaduct import evaluate


FIRST = {
    "Green": 19.0, "Red": 27.7, "Blue": 22.0, "Purple": 14.5,
    "Yellow": 30.0, "White": 23.0, "Airport": 12.0,
}


def case(span=10, common=False, crowd=201.732):
    return evaluate(FIRST, span_m=span, common_pier=common,
                    physical_candidate_id=f"baghdad-{span}-{common}-{crowd}",
                    train_crowd_mass_t=crowd)


def test_released_10m_quantity_and_price_control():
    result = case()
    q = result["quantities"]
    assert q["route_km"] == pytest.approx(148.2)
    assert q["beam_count"] == q["lift_count"] == 29_640
    assert q["pier_foundation_count"] == 29_654
    assert result["prices"]["changed_elevated_scope_usd"] == pytest.approx(148.2 * 9_000_000)
    assert result["zero_tunnels"] and result["zero_underground_stations"]
    assert not result["physical_screen"]["gross_10m_native_result_applies_to_baghdad_700_place_train"]
    assert not result["construction_release"]


def test_long_span_and_common_pier_counts_change_but_no_structure_is_qualified():
    short = case()
    long = case(25, True)
    assert long["quantities"]["beam_count"] == 11_856
    assert long["quantities"]["pier_foundation_count"] == 5_935
    assert long["physical_screen"]["length_and_load_scaled_hook_surrogate_t_per_beam"] > 60
    assert not long["physical_screen"]["surrogate_hook_below_reference_crane_chart"]
    assert long["physical_screen"]["gross_10m_native_midspan_deflection_m"] is None
    assert not long["physical_screen"]["baghdad_moving_load_stress_envelope_verified"]
    assert long["evaluation_id"] != short["evaluation_id"]
    assert long["civil_option_physical_id"] != short["civil_option_physical_id"]
    assert long["delivery"]["factory_yards_needed_at_declared_rate"] < short["delivery"]["factory_yards_needed_at_declared_rate"]


@pytest.mark.parametrize("span,bending,deflection", [
    (10, 1, 1), (20, 4, 16), (25, 6.25, 39.0625), (30, 9, 81),
])
def test_span_comparison_keeps_structural_screen_distinct_from_linear_prices(
    span, bending, deflection,
):
    result = case(span)
    screen = result["physical_screen"]
    assert screen["same_section_uniform_load_bending_demand_ratio_to_10m"] == pytest.approx(bending)
    assert screen["same_section_uniform_load_deflection_demand_ratio_to_10m"] == pytest.approx(deflection)
    assert screen["longer_span_section_and_prestress_redesign_required"] is (span > 10)
    assert screen["uniform_load_ratios_are_preliminary_not_a_train_load_case"]
    assert not result["cost_is_a_structurally_qualified_bid"]
    assert not result["construction_release"]


def test_civil_window_has_explicit_ramp_and_availability_margin():
    first = evaluate(FIRST, span_m=10, common_pier=False,
                     physical_candidate_id="first-civil-window", target_years=3)
    delivery = first["delivery"]
    assert (delivery["civil_start_year"], delivery["civil_finish_year"]) == (2028, 2030)
    assert delivery["nominal_workdays_per_yard_or_front"] == 750
    assert delivery["effective_workdays_per_yard_or_front"] == pytest.approx(650)
    assert [row["productive_workdays_per_yard_or_front"]
            for row in delivery["yearly_capacity"]] == pytest.approx([200, 225, 225])
    assert delivery["factory_yards_without_ramp_or_downtime"] == 5
    assert delivery["erection_fronts_without_ramp_or_downtime"] == 5
    assert delivery["factory_yards_needed_at_declared_rate"] == 6
    assert delivery["erection_fronts_needed_at_declared_rate"] == 6
    assert delivery["additional_yard_and_front_cost_usd"] is None


def test_7_year_window_keeps_same_selected_10m_quantities_and_more_capacity():
    metro = evaluate({"metro": 605.652}, span_m=10, common_pier=False,
                     physical_candidate_id="metro-civil-window", target_years=7)
    delivery = metro["delivery"]
    assert (delivery["civil_start_year"], delivery["civil_finish_year"]) == (2028, 2034)
    assert delivery["effective_workdays_per_yard_or_front"] == pytest.approx(1550)
    assert delivery["factory_yards_needed_at_declared_rate"] > delivery["factory_yards_without_ramp_or_downtime"]
    assert delivery["erection_fronts_needed_at_declared_rate"] > delivery["erection_fronts_without_ramp_or_downtime"]


def test_added_train_storage_mass_propagates_to_load_lift_and_civil_price():
    ordinary = case(20, True)
    with_storage = case(20, True, 221.732)
    assert ordinary["quantities"] == with_storage["quantities"]
    assert with_storage["physical_screen"]["crowd_load_ratio_planning_surrogate"] > 1
    assert with_storage["physical_screen"]["length_and_load_scaled_hook_surrogate_t_per_beam"] > ordinary["physical_screen"]["length_and_load_scaled_hook_surrogate_t_per_beam"]
    assert with_storage["prices"]["changed_elevated_scope_usd"] > ordinary["prices"]["changed_elevated_scope_usd"]
    assert with_storage["evaluation_id"] != ordinary["evaluation_id"]
    assert with_storage["civil_option_physical_id"] != ordinary["civil_option_physical_id"]


def test_rejects_undefined_geometry_and_loading():
    with pytest.raises(ValueError):
        evaluate(FIRST, span_m=15, common_pier=False, physical_candidate_id="x")
    with pytest.raises(ValueError):
        evaluate({"Green": 0}, span_m=10, common_pier=False, physical_candidate_id="x")
    with pytest.raises(ValueError):
        evaluate(FIRST, span_m=10, common_pier=False, physical_candidate_id="x",
                 train_crowd_mass_t=0)
    with pytest.raises(ValueError):
        evaluate(FIRST, span_m=10, common_pier=False, physical_candidate_id="x",
                 target_years=2.5)
    with pytest.raises(ValueError):
        evaluate(FIRST, span_m=10, common_pier=False, physical_candidate_id="x",
                 first_year_productivity_fraction=1.1)
