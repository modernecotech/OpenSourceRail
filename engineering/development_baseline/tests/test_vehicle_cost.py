from copy import deepcopy

import pytest

from engineering.development_baseline import FLAGS, vehicle_cost
from engineering.station_rail import evaluation
from engineering.station_rail.common import identity


@pytest.fixture(scope="module")
def estimate():
    record = evaluation.build()
    return record, vehicle_cost.evaluate(record, evaluation.ROOT)


def test_selected_vehicle_cost_is_bound_and_explicitly_provisional(estimate):
    record, cost = estimate
    for key in ("selection_id", "candidate_id", "body_candidate_id",
                "support_component_id", "propulsion_component_id", "evaluation_id"):
        assert cost[key] == record[key]
    assert cost["estimate_class"] == "C"
    assert cost["currency"] == "IQD"
    assert cost["development_default"] is True
    assert all(cost[key] is False for key in FLAGS)
    assert cost["cost_estimate_id"] == identity(
        {key: value for key, value in cost.items() if key != "cost_estimate_id"}
    )


def test_cost_rollup_prices_accounted_mass_without_claiming_mass_closure(estimate):
    _, cost = estimate
    mass = cost["vehicle_account"]
    assert mass["cars_per_train"] == 6
    assert mass["accounted_tare_kg_per_car"] == pytest.approx(
        mass["located_geometry_kg_per_car"] + mass["residual_account_kg_per_car"],
        abs=1e-5,
    )
    assert mass["geometry_occurrences"] > 0
    assert mass["complete_installed_mass"] is False
    assert cost["accounting_overlap"]["possible"] is True
    assert cost["accounting_overlap"]["overlap_mass_kg"] is None
    assert cost["accounting_overlap"]["total_assumes_gross_accounts_are_distinct"] is True
    assert len(cost["lines"]) > mass["account_rows"]
    for line in cost["lines"]:
        assert line["candidate_id"] == cost["candidate_id"]
        assert line["estimate_class"] == "C"
        assert line["source_ids"]
        values = [line["cost_iqd"][case] for case in ("low", "base", "high")]
        assert values == sorted(values)
    line_totals = [
        sum(line["cost_iqd"][case] for line in cost["lines"]
            if line["stage"] in ("factory-gate", "factory-gate-equipment-allowance"))
        for case in ("low", "base", "high")
    ]
    for actual, expected in zip(
        line_totals,
        cost["factory_gate_cost_iqd_per_train"].values(),
    ):
        assert actual == pytest.approx(expected, abs=2.0)
    total_lines = [
        sum(line["cost_iqd"][case] for line in cost["lines"])
        for case in ("low", "base", "high")
    ]
    for actual, expected in zip(
        total_lines,
        cost["total_vehicle_factory_delivery_assembly_iqd_per_train"].values(),
    ):
        assert actual == pytest.approx(expected, abs=2.0)


def test_shift_scenarios_and_held_whole_railway_scopes_are_explicit(estimate):
    _, cost = estimate
    assert cost["shifts"]["production_per_day"] == {
        "shifts": 2,
        "hours_per_shift": 8,
        "productive_hours_per_day": 12.0,
    }
    assert cost["shifts"]["civil_per_day"] == {"shifts": 2, "hours_per_shift": 8}
    assert [row["hours_per_day"] for row in cost["shifts"]["operations_cases"]] == [16, 18, 24]
    assert [row["shifts_per_day"] for row in cost["shifts"]["operations_cases"]] == [2, 2, 3]
    assert [row["hours_per_shift"] for row in cost["shifts"]["operations_cases"]] == [8, 9, 8]
    inputs = cost["assumption_values"]
    assert inputs["outbound_route_km"] == 50
    assert inputs["body_purchase_yield"] == [0.96, 0.90, 0.82]
    assert inputs["factory_overhead_fraction"] == [0.10, 0.20, 0.30]
    assert inputs["skilled_wage_benchmark_record_id"]
    assert inputs["loaded_two_shift_skilled_wage_iqd_per_h"] == sorted(
        inputs["loaded_two_shift_skilled_wage_iqd_per_h"]
    )
    assert cost["whole_life_cost_iqd"] is None
    assert cost["city_cost_iqd"] is None
    scopes = {row["scope"]: row["status"] for row in cost["scope_status"]}
    assert scopes["rolling-stock"] == "class-c-accounted-mass-estimate"
    assert scopes["factory-tooling"] == "separate-capital-range"
    assert all(value == "held" for key, value in scopes.items()
               if key not in ("rolling-stock", "factory-tooling"))


def test_mixed_selection_and_forged_acceptance_are_rejected(estimate):
    record, _ = estimate
    mixed = deepcopy(record)
    mixed["selection_id"] = "0" * 64
    with pytest.raises(ValueError, match="selection identity"):
        vehicle_cost.evaluate(mixed, evaluation.ROOT)
    accepted = deepcopy(record)
    accepted["physical_accepted"] = True
    accepted["evaluation_id"] = identity(
        {key: value for key, value in accepted.items() if key != "evaluation_id"}
    )
    with pytest.raises(ValueError, match="open acceptance"):
        vehicle_cost.evaluate(accepted, evaluation.ROOT)
