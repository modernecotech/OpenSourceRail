"""Selected-reference Class C system estimate stays distinct from acceptance."""
import pytest

from engineering.development_baseline import FLAGS, evaluate, system_cost, vehicle_cost
from engineering.design_search import model_cost
from engineering.station_rail import ROOT
from engineering.station_rail.common import identity


@pytest.fixture(scope="module")
def estimate():
    selected = evaluate.build(ROOT)
    vehicle = vehicle_cost.evaluate(selected, ROOT)
    return selected, system_cost.evaluate(selected, ROOT, vehicle)


def test_selected_reference_has_candidate_bound_low_base_high_system_estimate(estimate):
    selected, system = estimate
    assert system["candidate_id"] == selected["candidate_id"]
    assert system["vehicle_evaluation_id"] == selected["evaluation_id"]
    assert system["scenario_definition"]["selected_vehicle_candidate_id"] == selected["candidate_id"]
    assert system["evaluation_candidate_id"] != system["candidate_id"]
    assert system["scenario_definition"]["route_scenario"] == {
        "kind": "synthetic-periodic-reference-corridor",
        "directional_ring_length_m": 6000.0,
        "stations": 3,
        "spacing_m": 2000.0,
        "trackways": 2,
        "guideway_family": "box-beam",
        "span_m": 20.0,
        "selected_candidate_geometry_changed": False,
    }
    assert system["model_cost_complete_for_declared_case"] is True
    assert system["missing_cost_scopes"] == []
    assert set(system["scope_totals_iqd"]) == set(model_cost.SCOPES)
    for scope in model_cost.SCOPES:
        values = system["scope_totals_iqd"][scope]
        assert values["low"] > 0
        assert values["low"] <= values["base"] <= values["high"]
    for key, value in FLAGS.items():
        assert system[key] is value
    assert system["cost_estimate_id"] == identity(
        {key: value for key, value in system.items() if key != "cost_estimate_id"}
    )


def test_chargers_shifted_service_energy_and_pack_renewal_are_explicit(estimate):
    _, system = estimate
    charger = next(row for row in system["cost_line_items"]
                   if row["line_key"] == "service-battery-charger-packages")
    assert charger["quantity"]["platforms"] == 6
    assert charger["quantity"]["installed_capacity_kw"] == [5400.0, 7200.0, 9000.0]
    assert system["service_battery_duty"]["assumption_cost_scenarios"] == [35, 35, 50]
    margins = system["service_battery_duty"]["per_cycle_energy_margin_kWh"]
    assert margins["reference"] > 0
    assert margins["adverse"] < 0
    assert system["service_battery_duty"]["repeated_duty_qualified"] is False
    renewal = next(row for row in system["cost_line_items"]
                   if row["line_key"] == "selected-service-battery-and-services-renewal")
    assert renewal["scope"] == "renewals"
    assert len(renewal["quantity"]["event_schedule"]) == 3
    assert all(len(case["events"]) > 0 for case in renewal["quantity"]["event_schedule"])
    assert system["scenario_definition"]["service"]["operations_shifts_per_day"] == [2, 2, 3]
    assert system["scenario_definition"]["service"]["operating_hours_per_day"] == [16, 18, 24]


def test_civil_cost_uses_the_candidate_sized_crowd_control_beam(estimate):
    selected, system = estimate
    selected_beam = selected["civil"]["selected_reference"]
    fixed_stock_control = next(
        beam for beam in selected["civil"]["control_alternatives"]["crowd_control"]
        if beam["family"] == "box-beam" and beam["span_m"] == 20.0
    )
    basis = system["civil_design_basis"]

    assert selected_beam["load_case"] == "crowd_control"
    assert selected_beam["prestress_design_policy"] == "resize-for-this-load"
    assert selected_beam["necessary_longitudinal_screen"] == "pass"
    assert selected_beam["prestress_strands"] == 26
    assert fixed_stock_control["prestress_strands"] == 23
    assert fixed_stock_control["necessary_longitudinal_screen"] == "fail"
    assert basis == system["scenario_definition"]["civil_design_basis"]
    assert basis["alternative_id"] == selected_beam["alternative_id"]
    assert basis["physical_civil_component_id"] == selected_beam["physical_civil_component_id"]
    assert basis["physical_or_engineering_acceptance"] is False

    prestress = next(line for line in system["cost_line_items"]
                     if line["line_key"] == "precast-prestress")
    corridor_spans = (
        system["corridor_basis"]["directional_route_m"]
        * system["corridor_basis"]["trackways"] / basis["span_m"]
    )
    assert prestress["quantity"]["mass_kg"] == pytest.approx(
        selected_beam["prestress_kg"] * corridor_spans
    )


def test_separate_vehicle_estimate_is_not_added_and_acceptance_stays_open(estimate):
    _, system = estimate
    reconciliation = system["vehicle_cost_reconciliation"]
    assert reconciliation["aggregation_rule"].startswith(
        "The system estimate prices selected-candidate geometry/account rows as fleet units"
    )
    assert reconciliation["separate_selected_vehicle_cost_estimate_id"]
    assert reconciliation["account_overlap_possible"] is True
    assert not any(row["line_key"] == "separate-selected-vehicle-estimate"
                   for row in system["cost_line_items"])
    reserve = system["scenario_definition"]["mass_reserve_sensitivity_boundary"]
    assert reserve["case_factors"] == {"low": 0.8, "base": 1.0, "high": 1.2}
    assert reserve["propagated_through_system_cost"] is False
    assert reserve["synthetic_corridor_motion_fleet_energy_and_civil"] == (
        "base accounted vehicle mass only"
    )
    assert system["physical_mass_complete"] is False
    assert system["physical_journey_completed"] is False
    assert system["service_qualified"] is False
    assert system["procurement_ready"] is False
