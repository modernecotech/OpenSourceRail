"""Declared mass-reserve cases replace existing accounting residuals once."""
from engineering import mass_reserve_sensitivity as sensitivity


def test_reserve_sensitivity_reconciles_existing_mass_without_claiming_installation():
    result = sensitivity.plan()
    assert result["residual_account_count"] == 10
    assert abs(result["existing_unlocated_residual_kg_per_car"] - 10090.199590843558) < 1e-6
    cases = result["sensitivity_cases"]
    assert [case["name"] for case in cases] == ["low", "base", "high"]
    assert [round(case["scenario_tare_mass_kg_per_car"], 3) for case in cases] == [
        17203.958, 19221.998, 21240.038]
    assert abs(cases[1]["scenario_tare_mass_kg_per_car"]
               - result["accounted_tare_mass_kg_per_car"]) < 1e-6
    assert all(account["added_instead_of_replaced"] is False
               and account["physically_installed_mass_kg"] is None
               and account["installed_position_m"] is None
               for account in result["reserve_accounts"])
    assert result["mass_scenario_complete_for_declared_scope"] is True
    assert result["installed_mass_complete"] is False
    assert result["complete_installed_mass_kg_per_car"] is None
    assert result["installed_centre_of_gravity_m"] is None
    assert result["installed_inertia_kg_m2"] is None
    assert result["axle_reactions"] is None


def test_component_completion_replaces_each_account_once_and_keeps_overlap_open():
    result = sensitivity.plan()
    completion = result["component_completion"]
    assert completion["account_count"] == 10
    assert completion["all_account_residuals_partitioned"] is True
    assert completion["cross_account_overlap_closed"] is False
    assert completion["all_account_cost_total_iqd"] is None
    assert completion["integrated_into_city_cost_model"] is False
    assert completion["production_shift_basis"]["shifts_per_day"] == 2
    assert completion["production_shift_basis"]["civil_shifts_per_day"] == 2
    assert completion["production_shift_basis"]["operations_shifts_per_day_cases"] == [2, 2, 3]
    for account in completion["account_packages"]:
        rows = [row for row in completion["components"] if row["account_id"] == account["account_id"]]
        assert len(rows) == account["component_count"]
        assert abs(sum(row["base_mass_kg"] for row in rows)
                   - account["source_residual_kg_per_car"]) < 1e-6
        assert all(row["replaces_account_id"] == account["account_id"]
                   and row["added_on_top_of_account"] is False
                   and row["installed_position_m"] is None
                   and row["physical_acceptance"] is False
                   for row in rows)
        costs = [account["low_base_high"][name]["cost_iqd"] for name in ("low", "base", "high")]
        assert costs == sorted(costs)
        assert account["six_car_cost_iqd_by_case"]["base"] == 6 * account["low_base_high"]["base"]["cost_iqd"]
    frame_bolt = next(row for row in completion["components"]
                      if row["component_id"] == "joints/M8-shank")
    assert frame_bolt["quantity"] == 520
    assert abs(frame_bolt["base_mass_kg"] - 12.311022) < 1e-6
    service_components = [row for row in completion["components"] if row["account_id"] == "services"]
    assert len(service_components) == 7
    assert abs(sum(row["base_mass_kg"] for row in service_components) - 1345.0) < 1e-6
    assert all(row["mass_equivalent_volume_is_not_geometry"] is True for row in completion["components"])
    assert completion["physical_acceptance"] is False
    assert completion["installed_mass_complete"] is False
