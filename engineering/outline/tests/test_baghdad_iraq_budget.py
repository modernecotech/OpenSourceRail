"""Reconcile opening-year passenger income and operating cost for each service."""
import json
import pytest

from cities.Baghdad import iraq_budget


def test_linked_passengers_and_net_fares_price_distance_and_count_transfers_once():
    central = iraq_budget.funding_cases()["first"]["full"]["central"]
    # Undo the transfer, free travel and leg-length adjustments back to passenger-km.
    assert central["paid_m"] / .92 * 1.15 * 11 == pytest.approx(24.666408 * 700 * .15)
    assert central["net_iqd"] == 637.5
    assert central["farebox_m"] == pytest.approx(central["paid_m"] * 637.5 / 1510)


def test_service_options_use_matching_payroll_credit_energy_volume_and_train_distance():
    cases = iraq_budget.funding_cases()
    staffing = json.loads(iraq_budget.WORKFORCE.read_bytes())
    for key, offers in cases.items():
        for offer, sensitivities in offers.items():
            study = staffing["studies"][key] if offer == "full" else staffing["operating_options"][offer]
            for funding, wages in (("downside", "high"), ("central", "base"), ("upside", "low")):
                tested = sensitivities[funding]
                costs = study["opex"]
                pay = study["iraq_payroll"]["cases"][wages]["goa4"]
                assert (tested["opex_m"] - tested["power_m"] - tested["payroll_m"]
                        + pay["embedded_credit_usd_m_year"]) == pytest.approx(
                            costs["baseline_usd_m_year"] - costs["other_costs_usd_m_year"])
            assert sensitivities["upside"]["opex_m"] < sensitivities["central"]["opex_m"] < sensitivities["downside"]["opex_m"]
    metro = cases["metropolitan"]
    main = metro["metropolitan-mainlines"]["central"]
    full = metro["full"]["central"]
    assert main["paid_m"] < full["paid_m"]
    assert main["paid_m"] / full["paid_m"] == pytest.approx(main["power_m"] / full["power_m"])
    assert main["payroll_m"] == full["payroll_m"]
