from copy import deepcopy
import json

import pytest

from cities.Baghdad import iraq_capital as capital


@pytest.fixture(scope="module")
def record():
    return capital.build()


def test_market_price_replaces_every_direct_scope_then_applies_each_allowance_once(record):
    baseline = json.loads((capital.CITY / "system-results.json").read_bytes())["networks"]
    cfg = capital.iraq_power.read_toml("system.toml")
    for key, network in record["networks"].items():
        assert network["candidate_id"] == baseline[key]["selected_candidate_id"]
        assert network["reference_installed_usd_m"] == baseline[key]["power_cases"]["protected_conductor"]["installed_capital_usd_m"]
        for case, result in network["cases"].items():
            scope = result["scope_usd_m"]
            assert scope.keys() == baseline[key]["selected_capital_scope_usd_m"].keys()
            direct = sum(v for k, v in scope.items() if k not in {"design_assurance", "testing_commissioning", "project_allowance"})
            assert direct == pytest.approx(result["direct_capital_usd_m"])
            assert result["installed_capital_usd_m"] == pytest.approx(direct * 1.105 * 1.2)
            assert result["installed_capital_iqd_trillion"] == pytest.approx(sum(scope.values()) * record["iqd_per_usd"] / 1e6)
            for draw, weight in zip(result["construction_years"], cfg["networks"][key]["construction_cash_weights"], strict=True):
                assert draw["installed_usd_m"] == pytest.approx(result["installed_capital_usd_m"] * weight)
            assert scope["vehicles"] == pytest.approx(cfg["networks"][key]["fleet_trainsets"] * record["unit_rates"][case]["trainset_usd_m_each"])
        assert network["central_retained_usd_m"] < network["central_iraqi_award_usd_m"] < network["cases"]["base"]["installed_capital_usd_m"]
        values = [network["cases"][case]["installed_capital_usd_m"] for case in capital.CASES]
        assert values[0] < values[1] < values[2]
    guide = (capital.CITY / "IRAQ-CAPITAL.md").read_text()
    assert capital.guide(record, guide) == guide


def test_changes_to_airport_special_works_do_not_change_network_unit_rates(record):
    cfg = capital.iraq_power.read_toml("system.toml")
    study = json.loads((capital.CITY / capital.CIVIL_STUDY).read_bytes())
    works = capital.iraq_power.read_toml("airport-works.toml")
    unrelated = deepcopy(works)
    for key in ("ground", "operations", "site", "logistics"):
        unrelated.pop(key)
    rates = capital.iraq_power.read_toml("iraq-capital.toml")
    sites = capital.iraq_power.build()["supply_site_estimates"]
    assert capital.unit_rates(cfg, study, unrelated, rates, sites, record["iqd_per_usd"], 1) == record["unit_rates"]["base"]


def test_rejects_changed_civil_configuration_or_mixed_selection(record):
    baseline = json.loads((capital.CITY / "system-results.json").read_bytes())["networks"]["first"]
    cfg = capital.iraq_power.read_toml("system.toml")
    baseline["civil_cases"]["10m-separate"]["beam_count"] += 1
    with pytest.raises(ValueError, match="Civil quantities"):
        capital.estimate(cfg, "first", baseline, record["unit_rates"]["base"], record["iqd_per_usd"])
    baseline["selected_candidate_id"] = "other"
    with pytest.raises(ValueError, match="selected"):
        capital.estimate(cfg, "first", baseline, record["unit_rates"]["base"], record["iqd_per_usd"])
