from copy import deepcopy

import pytest

from engineering.development_baseline import FLAGS, factory_draft, vehicle_cost
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
    reserve = cost["mass_reserve_sensitivity"]
    assert reserve["case_factors"] == {"low": 0.8, "base": 1.0, "high": 1.2}
    assert mass["scenario_tare_mass_kg_per_car"] == pytest.approx({
        "low": 17203.958216173272,
        "base": mass["accounted_tare_kg_per_car"],
        "high": 21240.038052510696,
    })
    reserve_lines = [line for line in cost["lines"]
                     if line["line_key"].startswith("unlocated-account/")]
    assert len(reserve_lines) == 10
    for line in reserve_lines:
        quantity = line["quantity"]
        assert quantity["scenario_reserve_mass_kg_per_car"][1] == pytest.approx(
            quantity["residual_account_mass_kg_per_car"])
        assert quantity["scenario_reserve_mass_kg_per_car"][0] == pytest.approx(
            quantity["residual_account_mass_kg_per_car"] * 0.8)
        assert quantity["scenario_reserve_mass_kg_per_car"][2] == pytest.approx(
            quantity["residual_account_mass_kg_per_car"] * 1.2)
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


def test_each_cost_line_recomputes_from_published_quantities(estimate):
    _, cost = estimate
    assumptions = cost["assumption_values"]
    cases = ("low", "base", "high")
    cars = cost["vehicle_account"]["cars_per_train"]
    wages = assumptions["loaded_two_shift_skilled_wage_iqd_per_h"]

    for line in cost["lines"]:
        quantity = line["quantity"]
        expected = []
        if line["line_key"].startswith("located-stock/"):
            family = line["line_key"].rsplit("/", 1)[1]
            for index, case in enumerate(cases):
                material = (
                    quantity["gross_purchase_mass_kg_per_car"][index]
                    * assumptions["material_rate_iqd_per_kg"][family][case]
                    * cars
                )
                labour = quantity["process_hours_per_car"][index] * wages[index] * cars
                equipment = (
                    quantity["machine_hours_per_car"][index]
                    * assumptions["machine_rate_iqd_per_h"][index]
                    * cars
                )
                quality = material * assumptions["body_qa_fraction"][index]
                direct = material + labour + equipment + quality
                expected.append(round(
                    direct * (1 + assumptions["factory_overhead_fraction"][index]), 2
                ))
        elif line["line_key"].startswith("unlocated-account/"):
            expected = [round(
                quantity["scenario_reserve_mass_kg_per_car"][index]
                * assumptions["finished_equipment_iqd_per_kg"][index]
                * cars,
                2,
            ) for index, _case in enumerate(cases)]
        elif line["line_key"] == "six-car-final-vehicle-assembly":
            expected = [round(
                (quantity["labour_hours_per_car"][index] * wages[index]
                 + quantity["equipment_iqd_per_car"][index]) * cars,
                2,
            ) for index, _case in enumerate(cases)]
        elif line["line_key"] == "reference-factory-to-assembly-delivery":
            expected = [round(
                quantity["tonne_km"]
                * assumptions["transport_iqd_per_tonne_km"][index],
                2,
            ) for index, _case in enumerate(cases)]
        else:
            pytest.fail(f"No independent calculation for {line['line_key']}")

        for case, calculated in zip(cases, expected):
            assert abs(line["cost_iqd"][case] - calculated) <= 0.01, (
                line["line_key"], case, line["cost_iqd"][case], calculated
            )

    # Precision-only publication changes must preserve the existing totals.
    assert cost["factory_gate_cost_iqd_per_train"] == {
        "low": 1253378328.35, "base": 6501854060.49, "high": 33053331692.45,
    }
    assert cost["final_vehicle_assembly_cost_iqd_per_train"] == {
        "low": 3450000.0, "base": 13701000.0, "high": 67920000.0,
    }
    assert cost["reference_delivery_cost_iqd_per_train"] == {
        "low": 576659.94, "base": 2306639.78, "high": 8649899.16,
    }
    assert cost["total_vehicle_factory_delivery_assembly_iqd_per_train"] == {
        "low": 1257404988.29, "base": 6517861700.27, "high": 33129901591.61,
    }
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


def test_factory_draft_uses_only_selected_cost_ledger_and_two_shift_basis(estimate):
    record, cost = estimate
    candidate = {key: record[key] for key in (
        "selection_id", "candidate_id", "body_candidate_id", "support_component_id",
        "propulsion_component_id", "evaluation_id")}
    planning_revision = dict(city="fixture-city", planning_revision_id="a" * 64,
        network_proposal_id="b" * 64)

    plan = factory_draft._build_work_packages(cost, candidate, planning_revision)

    assert len(plan["work_packages"]) == 19
    assert plan["production_shifts"]["shifts_per_day"] == 2
    assert plan["production_shifts"]["hours_per_shift"] == 8
    assert plan["production_shifts"]["productive_hours_per_day"] == 12
    assert plan["cost_estimate_id"] == cost["cost_estimate_id"]
    for previous, current in zip(plan["work_packages"], plan["work_packages"][1:]):
        assert current["predecessor_ids"] == [previous["operation_id"]]
        for case in ("low", "base", "high"):
            assert current["planned_start_workday"][case] == previous["planned_finish_workday"][case]
    assert plan["factory_and_final_assembly_cost_iqd_per_train"] == {
        case: round(cost["factory_gate_cost_iqd_per_train"][case]
                    + cost["final_vehicle_assembly_cost_iqd_per_train"][case], 2)
        for case in ("low", "base", "high")
    }
    assert plan["excluded_cost_lines"][0]["reason"].startswith("Factory plan excludes transport")
    assert plan["inventory_disposition"]["complete_installed_mass"] is False
    resources = plan["provisional_resource_envelope"]
    assert resources["source_package_count"] == 19
    assert resources["scenario_count"] == 27
    assert resources["process_hours_per_train"] == plan["total_process_hours_per_train"]
    assert set(resources["source_cost_line_ids"]) == {row["line_id"] for row in plan["work_packages"]}
    assert resources["assumptions"]["person_hours_per_process_hour_hypothesis"] == 1.0
    assert resources["candidate_id"] == candidate["candidate_id"]
    assert resources["selection_id"] == candidate["selection_id"]
    assert resources["evaluation_id"] == candidate["evaluation_id"]
    keys = [(row["batch_trainsets"], row["horizon_workdays"], row["process_hour_case"])
            for row in resources["scenarios"]]
    assert len(keys) == len(set(keys)) == 27
    assert set(keys) == {(trains, days, case) for trains in (1, 6, 12)
                         for days in (60, 125, 250) for case in ("low", "base", "high")}
    assert resources["actual_factory_capacity_verified"] is False
    assert resources["accounting_overlap_resolved"] is False
    assert resources["manufacturing_release"] is False
    annual = next(row for row in resources["scenarios"] if row["batch_trainsets"] == 1
                  and row["horizon_workdays"] == 250 and row["process_hour_case"] == "base")
    # Each person covers one shift; a second shift requires a second crew.
    assert annual["productive_hours_per_worker_shift_day"] == 6.0
    assert annual["productive_hours_per_equal_two_shift_lane_day"] == 12.0
    assert annual["pooled_positions_per_shift_rounded_up"] == 8
    assert annual["total_positions_across_two_shifts_excluding_relief"] == 16
    assert annual["pooled_productive_capacity_person_hours"] == 16 * 6 * 250
    assert all(row["pooled_productive_capacity_person_hours"] >= row["required_person_hours_hypothesis"]
               for row in resources["scenarios"])
    assert all(row["actual_headcount_including_relief"] is None
               and row["physical_workstations_required"] is None for row in resources["scenarios"])
    for case in resources["process_hours_per_train"]:
        assert sum(row["process_hours_per_train"][case] for row in resources["process_families"]) == pytest.approx(
            resources["process_hours_per_train"][case])
    with pytest.raises(factory_draft.FactoryDraftError, match="Unique source cost lines"):
        factory_draft.resource_envelope(plan["work_packages"] + [plan["work_packages"][0]],
            candidate, cost["cost_estimate_id"], 0.75)


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
