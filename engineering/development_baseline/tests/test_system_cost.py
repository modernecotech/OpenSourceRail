"""Selected-reference Class C system estimate stays distinct from acceptance."""
import pytest

from engineering.development_baseline import FLAGS, evaluate, selection, system_cost, vehicle_cost
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
    for mass_case in system["mass_reserve_sensitivity"]["cases"]:
        plan = mass_case["provisional_manufacturing_plan"]
        assert plan["candidate_id"] == plan["bundle_id"]
        assert plan["body_candidate_id"] == system["scenario_definition"]["selected_body_candidate_id"]
        assert plan["route_count"] == plan["coverage"]["located_stock_occurrences"]
        assert plan["coverage"]["routed_stock_occurrences"] == plan["route_count"]
        assert plan["coverage"]["unrouted_stock_ids"] == []
        assert all(route["candidate_id"] == plan["candidate_id"]
                   and route["estimate_class"] == "C" and route["measured_labor"] is False
                   for route in plan["routes"])
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


def test_service_energy_supply_sensitivity_keeps_physical_and_cost_variants_separate(estimate):
    selected, system = estimate
    duty = system["service_battery_duty"]
    sensitivity = duty["supply_sensitivity"]
    assert sensitivity["parent_candidate_id"] == selected["candidate_id"]
    assert sensitivity["selected_candidate_hardware_changed"] is False
    assert sensitivity["current_candidate_changed"] is False
    assert sensitivity["study_only"] is True
    assert len(sensitivity["battery_charger_cases"]) == 36

    base_reference = next(row for row in sensitivity["battery_charger_cases"]
        if row["battery_parallel_strings"] == 3
        and row["charger_cost_case"] == "base"
        and row["hotel_load_case"] == "reference"
        and row["charge_acceptance_fraction_hypothesis"] == 1.0)
    base_adverse = next(row for row in sensitivity["battery_charger_cases"]
        if row["battery_parallel_strings"] == 3
        and row["charger_cost_case"] == "base"
        and row["hotel_load_case"] == "adverse"
        and row["charge_acceptance_fraction_hypothesis"] == 1.0)
    assert base_reference["battery_component_id"] == sensitivity["selected_service_battery_component_id"]
    assert base_reference["energy_margin_kWh_per_car_per_cycle"] == pytest.approx(
        duty["per_cycle_energy_margin_kWh"]["reference"])
    assert base_adverse["energy_margin_kWh_per_car_per_cycle"] == pytest.approx(
        duty["per_cycle_energy_margin_kWh"]["adverse"])
    assert base_adverse["energy_only_cycles_from_max_SOC_to_minimum_SOC"] is not None

    reduced_pack = next(row for row in sensitivity["battery_charger_cases"]
        if row["battery_parallel_strings"] == 2
        and row["charger_cost_case"] == "base"
        and row["hotel_load_case"] == "reference"
        and row["charge_acceptance_fraction_hypothesis"] == 1.0)
    assert reduced_pack["battery_component_id"] != sensitivity["selected_service_battery_component_id"]
    assert reduced_pack["new_candidate_bundle_required_before_design_use"] is True

    solar = sensitivity["solar_potential"]
    assert len(solar["cases"]) == 12
    maximum_sun = next(row for row in solar["cases"]
        if row["cost_scenario"] == "base" and row["equivalent_peak_sun_hours_per_day"] == 6.0)
    assert maximum_sun["gross_solar_energy_kWh_per_car_day"] > 0
    assert maximum_sun["solar_hardware_mass_kg_per_car"] is None
    assert maximum_sun["solar_hardware_capital_cost_iqd"] is None
    assert maximum_sun["interval_energy_credit_applied"] is False

    independent = sensitivity["independent_continuous_supply_requirement"]
    assert [row["electrical_energy_kWh_per_car_day"] for row in independent["cases"]] == [560, 630, 1200]
    assert independent["physical_candidate_id"] is None
    assert independent["new_physical_candidate_required"] is True

    direct = sensitivity["station_direct_auxiliary_feed_alternative"]
    assert direct["incremental_installed_capacity_kW"] == 1800
    assert direct["partial_class_c_incremental_power_package_and_install_cost_iqd"] == {
        "low": 945000000.0, "base": 3780000000.0, "high": 15120000000.0,
    }
    adverse_direct = next(row for row in direct["cases"] if row["hotel_load_case"] == "adverse")
    assert adverse_direct["dwell_hotel_energy_from_independent_supply_kWh_per_car"] == pytest.approx(50*35/3600)
    assert adverse_direct["energy_margin_kWh_per_car_per_cycle"] < 0
    assert direct["physical_candidate_id"] is None
    assert direct["new_system_candidate_required"] is True
    assert sensitivity["system_cost_base_case_unchanged"] is True


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

    calculated = basis["minimum_gravity_bearing_area_m2_by_pressure_kpa"]
    source_areas = {
        str(int(row["allowable_bearing_kPa_hypothesis"])): row["minimum_gravity_bearing_area_m2"]
        for row in selected_beam["foundation_scenarios"]
    }
    assert calculated == source_areas


def test_residual_mass_cases_propagate_through_system_economics(estimate):
    selected, system = estimate
    sensitivity = system["mass_reserve_sensitivity"]
    cases = sensitivity["cases"]
    assert [row["mass_case"]["name"] for row in cases] == ["low", "base", "high"]
    assert sensitivity["dimensions"]["residual_mass_cases"] == ["low", "base", "high"]
    assert sensitivity["dimensions"]["independent_class_c_cost_cases"] == ["low", "base", "high"]
    assert system["scenario_definition"]["mass_reserve_sensitivity_boundary"][
        "propagated_through_system_cost"] is True
    assert system["scenario_definition"]["mass_reserve_sensitivity_boundary"][
        "mass_sensitivity_result_id"] == sensitivity["result_id"]

    expected_tare = selection.load(ROOT)["vehicle"]["mass"]["accounted_tare_kg_per_car"]
    for row in cases:
        mass = row["mass_case"]
        assert mass["candidate_id"] == selected["candidate_id"]
        assert mass["selection_id"] == selected["selection_id"]
        assert mass["physical_candidate_identity_changed"] is False
        assert mass["reserve_factor_is_probability_bound"] is False
        assert mass["installed_mass_resolved"] is False
        assert mass["normal_loaded_mass_kg_per_car"] == pytest.approx(
            mass["accounted_tare_mass_kg_per_car"] + 3450.0
        )
        assert mass["crowd_control_mass_kg_per_car"] == pytest.approx(
            mass["accounted_tare_mass_kg_per_car"] + 12000.0
        )
        assert row["journey_demand"]["normal_loaded_mass_kg_per_car"] == pytest.approx(
            mass["normal_loaded_mass_kg_per_car"]
        )
        assert row["journey_demand"]["evidence"] == "analytical-demand-only"
        assert row["physical_journey_completed"] is False
        assert row["physical_acceptance"] is False
        assert row["foundation_area_costing"]["costed_proxy_mass_coupled"] is False
        assert row["foundation_area_costing"]["calculated_minimum_gravity_area_m2_by_pressure_kpa"] == (
            row["civil_design_basis"]["minimum_gravity_bearing_area_m2_by_pressure_kpa"]
        )
        reconciliation = row["mass_reconciliation"]
        assert reconciliation["located_geometry_mass_kg_per_car"] == pytest.approx(
            mass["located_geometry_mass_kg_per_car"]
        )
        assert reconciliation["replaced_residual_mass_kg_per_car"] == pytest.approx(
            mass["scenario_residual_mass_kg_per_car"]
        )
        assert reconciliation["accounted_tare_mass_kg_per_car"] == pytest.approx(
            mass["accounted_tare_mass_kg_per_car"]
        )
        assert sum(reconciliation["residual_account_mass_kg_per_car"].values()) == pytest.approx(
            reconciliation["replaced_residual_mass_kg_per_car"]
        )
        assert set(row["scope_totals_iqd"]) == set(model_cost.SCOPES)
        assert len(row["model_based_installed_CAPEX_iqd"]) == 3

    low, base, high = cases
    assert base["mass_case"]["accounted_tare_mass_kg_per_car"] == pytest.approx(expected_tare)
    assert base["model_based_installed_CAPEX_iqd"] == system["model_based_installed_CAPEX_iqd"]
    assert base["model_based_whole_life_NPV_iqd"] == system["model_based_whole_life_NPV_iqd"]
    assert low["journey_demand"]["traction_mechanical_energy_J_train"] < base["journey_demand"][
        "traction_mechanical_energy_J_train"] < high["journey_demand"]["traction_mechanical_energy_J_train"]
    assert low["civil_design_basis"]["prestress_strands"] < base["civil_design_basis"][
        "prestress_strands"] < high["civil_design_basis"]["prestress_strands"]
    assert low["civil_design_basis"]["minimum_gravity_bearing_area_m2_by_pressure_kpa"]["200"] < high[
        "civil_design_basis"]["minimum_gravity_bearing_area_m2_by_pressure_kpa"]["200"]
    assert low["foundation_area_costing"]["costed_class_c_area_proxy_m2"] == high[
        "foundation_area_costing"]["costed_class_c_area_proxy_m2"]
    assert "foundation costs continue to use separate fixed Class C footprint proxies" in system[
        "scenario_definition"]["mass_reserve_sensitivity_boundary"]["foundation_area_basis"]
    assert low["model_based_installed_CAPEX_iqd"][1] < high["model_based_installed_CAPEX_iqd"][1]
    assert len({row["mass_case"]["mass_case_id"] for row in cases}) == 3
    assert len({row["bundle_definition_id"] for row in cases}) == 3
    assert len({row["model_cost_evaluation_id"] for row in cases}) == 3


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
    assert reserve["propagated_through_system_cost"] is True
    assert "separate low/base/high residual-mass cases" in reserve[
        "synthetic_corridor_motion_fleet_energy_and_beam_foundations"
    ]
    assert system["physical_mass_complete"] is False
    assert system["physical_journey_completed"] is False
    assert system["service_qualified"] is False
    assert system["procurement_ready"] is False
