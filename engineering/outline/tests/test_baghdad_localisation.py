"""Guard the boundary between Iraqi awards, domestic production and project costs."""
from copy import deepcopy
import json

import pytest

from cities.Baghdad import localisation


def test_network_targets_and_price_reconcile_to_unchanged_engineering_budget():
    ledger = json.loads((localisation.CITY / "system-results.json").read_bytes())["networks"]
    result = localisation.build()
    targets = localisation.iraq_power.read_toml("system.toml")["networks"]["metropolitan"]["local_contract_fraction"]
    for key, network in result["networks"].items():
        installed = ledger[key]["power_cases"]["protected_conductor"]["installed_capital_usd_m"]
        assert network["installed_capital_usd_m"] == pytest.approx(installed)
        assert network["comparable_price_usd_m"] + network["unassigned_allowance_usd_m"] == pytest.approx(installed)
        for name, p in network["packages"].items():
            assert p["iraqi_award_usd_m"] == pytest.approx(ledger[key]["selected_capital_scope_usd_m"][name] * targets[name])
        assert network["iraqi_award_usd_m"] < network["comparable_price_usd_m"]
        actual = list(network["retained_usd_m"].values())
        assert 0 < actual[0] < actual[1] < actual[2] < network["iraqi_award_usd_m"]
    metro = ledger["metropolitan"]["selected_local_delivery"]
    assert result["networks"]["metropolitan"]["iraqi_award_usd_m"] == pytest.approx(metro["planning_local_contract_usd_m"])
    assert result["networks"]["first"]["award_basis"] == "transferred metropolitan scope targets"
    document = (localisation.CITY / "BUYER-COMPARISON.md").read_text()
    assert localisation.guide(result, document) == document


def test_grid_applies_value_ratio_only_to_awarded_scope_and_land_excludes_transfers():
    result = localisation.build()["networks"]
    grid_cases = localisation.iraq_power.build()["supply_site_estimates"]
    for n in result.values():
        p = n["packages"]["grid_charging_buffers"]
        for case, site in grid_cases.items():
            ratio = site["estimated_domestic_usd_m"] / site["direct_usd_m"]
            assert p["retained_usd_m"][case] == pytest.approx(p["iraqi_award_usd_m"] * ratio)
        land = n["packages"]["land_utilities_disruption"]
        assert land["retained_usd_m"]["base"] == pytest.approx(land["iraqi_award_usd_m"] * .45 * .75)


def test_rejects_unpriced_scope_and_mixed_candidate():
    ledger = json.loads((localisation.CITY / "system-results.json").read_bytes())["networks"]["first"]
    awards = localisation.iraq_power.read_toml("system.toml")["networks"]["metropolitan"]["local_contract_fraction"]
    work = localisation.work_types(localisation.iraq_power.build()["supply_site_estimates"])
    broken = deepcopy(work)
    broken.pop("vehicles")
    with pytest.raises(ValueError, match="cover all priced scopes"):
        localisation.estimate(ledger, awards, broken)
    ledger["selected_candidate_id"] = "other"
    with pytest.raises(ValueError, match="candidate"):
        localisation.estimate(ledger, awards, work)
