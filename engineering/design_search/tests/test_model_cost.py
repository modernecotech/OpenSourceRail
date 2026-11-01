"""Model-based Class C costs complete declared scopes without closing gates."""
from copy import deepcopy
from math import ceil

import pytest

from engineering.design_search import (
    design_grammar, model_cost, railway_bundle, railway_campaign,
    system_inventory, system_motion,
)
from engineering.station_rail import ROOT


def _evaluate(family):
    body = design_grammar.initial_candidates()[0]
    bundle = railway_bundle.materialize(body, family=family, root=ROOT)
    spec = railway_campaign.specification(ROOT)
    inventory = system_inventory.evaluate(
        body, bundle_id=bundle["candidate_id"], source_root=ROOT,
        comparison_context=spec["experiment"],
        component_substitutions=bundle["component_substitutions"],
        extra_equipment_tasks=bundle["unweighed_architecture_equipment"],
    )
    architecture = railway_bundle.assess_architecture(bundle)
    propulsion = railway_campaign.propulsion(bundle, architecture)
    motion = system_motion.evaluate(bundle, available_map=None)
    civil = railway_bundle.assess_civil(bundle)
    estimate = model_cost.evaluate(bundle, inventory, architecture, propulsion, motion, civil, root=ROOT)
    return bundle, inventory, estimate


def test_candidate_costs_quantify_all_scopes_and_keep_release_gates_open():
    bundle, inventory, estimate = _evaluate("P1")

    assert estimate["candidate_id"] == bundle["candidate_id"]
    assert estimate["model_cost_complete_for_declared_case"] is True
    assert estimate["model_cost_missing_scopes"] == []
    assert set(estimate["scope_totals_iqd"]) == set(model_cost.SCOPES)
    assert all(values[0] > 0 and values == sorted(values)
               for values in estimate["scope_totals_iqd"].values())
    assert estimate["currency"] == "IQD"
    assert estimate["estimate_class"] == "C"
    assert estimate["rate_evidence_summary"]["actual_supplier_quotes"] == 0
    assert estimate["model_based_installed_CAPEX_iqd"] == sorted(estimate["model_based_installed_CAPEX_iqd"])
    assert estimate["model_based_whole_life_NPV_iqd"] == sorted(estimate["model_based_whole_life_NPV_iqd"])
    assert estimate["annual_operations_iqd"][1] > 0
    plan=estimate["production_plan"]
    assert plan["production_shifts_per_day"] == 2
    assert plan["civil_shifts_per_day"] == 2
    assert plan["operations_shifts_per_day_cases"] == [2, 2, 3]
    assert plan["operating_hours_per_day_cases"] == [16, 18, 24]
    assert plan["required_parallel_workcells"][1] > 0
    routes = estimate["provisional_manufacturing_plan"]
    located_stock = {
        row["id"]: row for row in inventory["engineering_BOM"]
        if row.get("scope") == "located-nominal-gross-body-stock"
    }
    assert routes["candidate_id"] == bundle["candidate_id"]
    assert routes["plan_id"] == model_cost.identity(
        {key: value for key, value in routes.items() if key != "plan_id"}
    )
    assert routes["route_count"] == len(located_stock)
    assert routes["coverage"]["routed_stock_occurrences"] == len(located_stock)
    assert routes["coverage"]["unrouted_stock_ids"] == []
    assert {row["stock_id"] for row in routes["routes"]} == set(located_stock)
    cost_lines = {
        line["line_key"].removeprefix("vehicle-stock/"): line
        for line in estimate["cost_line_items"]
        if line["line_key"].startswith("vehicle-stock/")
    }
    assert set(cost_lines) == set(located_stock)
    for route in routes["routes"]:
        stock = located_stock[route["stock_id"]]
        line = cost_lines[route["stock_id"]]
        assert route["candidate_id"] == line["candidate_id"] == bundle["candidate_id"]
        assert route["component_definition_id"] == stock["component_definition_id"]
        assert route["cost_line_id"] == line["line_id"]
        assert route["provisional_process"] == stock["geometry"]["definition"]["process"]
        assert route["estimate_class"] == "C"
        assert route["process_qualified"] is False
        assert route["measured_labor"] is False
        assert route["manufacturing_release"] is False
        assert line["quantity"]["process_hours_per_car"] == pytest.approx(
            [route["labor_hours_per_car"][case] for case in ("low", "base", "high")], abs=0.011
        )
        assert line["quantity"]["fleet_process_hours"] == pytest.approx(
            [route["fleet_labor_hours"][case] for case in ("low", "base", "high")], abs=0.011
        )
    assert all(row["labor_h"] is None for row in inventory["manufacturing_BOM"])
    for case in ("low", "base", "high"):
        assert routes["total_fleet_labor_hours"][case] == pytest.approx(
            sum(row["fleet_labor_hours"][case] for row in routes["routes"]), abs=0.01
        )
    assert plan["located_body_stock_route_count"] == routes["route_count"]
    assert plan["located_body_stock_process_hours_for_fleet"] == routes["total_fleet_labor_hours"]
    schedule=plan["construction_schedule_days"]
    assert schedule["civil_shifts_per_day"] == 2
    for shifts_key, days_key in (("foundation_work_shifts", "foundations"),
                                 ("span_erection_work_shifts", "span_erection"),
                                 ("rail_installation_work_shifts", "rail_installation"),
                                 ("station_installation_work_shifts", "stations")):
        assert schedule[days_key] == [ceil(shifts/2) for shifts in schedule[shifts_key]]
    assert estimate["annual_operations_iqd"][2] > estimate["annual_operations_iqd"][1]
    assert estimate["annual_electricity_kwh"][2] > estimate["annual_electricity_kwh"][1]
    assert estimate["annual_maintenance_iqd"][2] > estimate["annual_maintenance_iqd"][1]
    assert estimate["physical_mass_complete"] is False
    assert estimate["physical_journey_completed"] is False
    assert estimate["procurement_ready"] is False
    assert estimate["physical_or_safety_accepted"] is False
    assert all(line["candidate_id"] == bundle["candidate_id"] and line["source_ids"]
               for line in estimate["cost_line_items"])
    assert inventory["complete_installed_mass_kg"] is None


def test_wheel_traction_and_laminate_alternatives_are_costed_in_their_own_scopes():
    wheel_bundle, _, wheel = _evaluate("P6")
    lim_bundle, _, lim = _evaluate("P7")
    wheel_keys = {line["line_key"] for line in wheel["cost_line_items"]}
    lim_keys = {line["line_key"] for line in lim["cost_line_items"]}

    assert wheel_bundle["candidate_id"] != lim_bundle["candidate_id"]
    assert "unweighed-architecture-equipment-package" in wheel_keys
    assert "unlocated-wayside-propulsion-package" not in wheel_keys
    assert "traction-converter-capacity" not in wheel_keys
    assert "unlocated-wayside-propulsion-package" in lim_keys
    assert "unweighed-architecture-equipment-package" in lim_keys
    assert wheel["scope_totals_iqd"]["stations-power"][1] > 0
    assert lim["scope_totals_iqd"]["rolling-stock"][1] > 0


def test_cost_comparison_is_same_service_and_rejects_mixed_candidate_inputs():
    bundle, inventory, first = _evaluate("P1")
    _, _, second = _evaluate("P6")
    comparison = model_cost.compare([first, second])
    assert comparison["integrated_winner"] is None
    assert comparison["selected_reference_changed"] is False
    assert set(comparison["nondominated_candidate_ids"]) <= {
        first["candidate_id"], second["candidate_id"]
    }

    wrong_inventory = deepcopy(inventory)
    wrong_inventory["candidate_id"] = "f" * 64
    architecture = railway_bundle.assess_architecture(bundle)
    propulsion = railway_campaign.propulsion(bundle, architecture)
    motion = system_motion.evaluate(bundle, available_map=None)
    civil = railway_bundle.assess_civil(bundle)
    with pytest.raises(ValueError, match="Mixed candidate"):
        model_cost.evaluate(bundle, wrong_inventory, architecture, propulsion, motion, civil, root=ROOT)

    different_service = deepcopy(second)
    different_service["corridor_basis"]["offered_capacity_pphpd"] += 1
    different_service["evaluation_id"] = model_cost.identity(
        {key: value for key, value in different_service.items() if key != "evaluation_id"})
    with pytest.raises(ValueError, match="Equal currency, cost assumptions, route and nominal service"):
        model_cost.compare([first, different_service])


def test_two_directional_service_and_hotel_load_charging_are_counted_once():
    bundle, _, estimate = _evaluate("P1")
    assumptions = model_cost.assumptions(ROOT)
    reliability = next(row for row in estimate["cost_line_items"]
                       if row["line_key"] == "service-disruption-and-corrective-reserve")
    direction_count = assumptions["service_directions"]
    route_km = estimate["corridor_basis"]["directional_route_m"] / 1000.0
    headway = bundle["requirements"]["target_headway_s"]
    expected_train_km = [
        direction_count * 3600.0 / headway * hours * route_km
        for hours in assumptions["operating_hours_per_day_cases"]
    ]
    assert reliability["quantity"]["train_km_per_day"] == pytest.approx(expected_train_km)
    # The physical two trackways are already reflected in infrastructure quantities;
    # they do not double the two directional service loops a second time.
    assert estimate["corridor_basis"]["trackways"] == 2

    energy = next(row for row in estimate["cost_line_items"]
                  if row["line_key"] == "conditional-annual-electricity")
    quantity = energy["quantity"]
    cars = bundle["cars"]
    trains = estimate["corridor_basis"]["normal_trainsets"]
    days = assumptions["operating_days_per_year"]
    auxiliary = [trains * cars * kw * hours * days
                 for kw, hours in zip(assumptions["assumptions"]["auxiliary_kw_per_car"],
                                      assumptions["operating_hours_per_day_cases"])]
    grid_input = [auxiliary[i] / assumptions["assumptions"]["service_battery_charging_efficiency"][i]
                  for i in range(3)]
    assert quantity["auxiliary_kwh_per_year"] == pytest.approx(auxiliary)
    assert quantity["service_battery_grid_input_kwh_per_year"] == pytest.approx(grid_input)
    assert quantity["service_battery_charging_loss_kwh_per_year"] == pytest.approx(
        [grid_input[i] - auxiliary[i] for i in range(3)])
