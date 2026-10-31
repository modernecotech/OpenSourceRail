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
