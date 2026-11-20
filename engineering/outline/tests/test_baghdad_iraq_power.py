"""Check local electricity and equipment estimates against the physical network ledger."""
import json
import pytest

from cities.Baghdad import iraq_power as power


def test_grid_classes_and_replacement_energy_are_volume_weighted():
    fx = power.read_toml("iraq-market.toml")["currency"]["iqd_per_usd"]
    scenarios = power.rates()
    assert scenarios["low"]["delivered_usd_per_kwh"] == pytest.approx(60 / fx)
    assert scenarios["base"]["delivered_usd_per_kwh"] == pytest.approx(0.95 * 120 / fx + 0.05 * 0.4)
    assert scenarios["high"]["delivered_usd_per_kwh"] == pytest.approx(0.8 * 120 / fx + 0.2 * 0.4)


def test_matches_selected_meter_and_does_not_add_electricity_or_site_cost_twice():
    result = power.build()
    ledger = json.loads((power.CITY / "system-results.json").read_bytes())
    for key, network in result["networks"].items():
        source = ledger["networks"][key]
        assert source["selected_candidate_id"] == network["candidate_id"]
        capex = source["selected_capital_scope_usd_m"]["grid_charging_buffers"]
        assert capex == network["existing_grid_scope_usd_m"]
        original = source["selected_annual_opex_usd_m"]["energy"]
        for case, row in network["cases"].items():
            price = result["energy_rates"][case]["delivered_usd_per_kwh"]
            meter = source["power_cases"]["protected_conductor"]["annual_grid_gwh"]
            assert row["annual_energy_change_usd_m"] == pytest.approx(meter * price - original)
            sites = result["supply_site_estimates"][case]
            assert row["direct_supply_sites_usd_m"] == pytest.approx(sum(sites["parts_usd_m"].values())
                                                                     * network["supply_sites"])
            assert 0 < row["estimated_domestic_sites_usd_m"] < row["direct_supply_sites_usd_m"]
    guide = (power.CITY / "IRAQ-POWER.md").read_text()
    assert power.guide(result, guide) == guide


def test_alternative_bill_uses_its_own_purchased_energy_and_common_discount():
    result = power.build()
    ledger = json.loads((power.CITY / "system-results.json").read_bytes())
    cfg = power.read_toml("system.toml")
    rate = cfg["discount_rate_real"]
    pv = (1 - (1 + rate) ** -cfg["comparison_years"]) / rate
    for key, n in result["networks"].items():
        alternatives = ledger["networks"][key]["power_cases"]
        for case, row in n["cases"].items():
            delta = result["energy_rates"][case]["delivered_usd_per_kwh"] - cfg["operation_rates"]["delivered_energy_usd_per_kwh"]
            life = {k: alt["whole_life_30y_present_usd_m"] + pv * alt["annual_grid_gwh"] * delta
                    for k, alt in alternatives.items()}
            assert row["overhead_minus_conductor_30y_usd_m"] == pytest.approx(life["overhead"] - life["protected_conductor"])
