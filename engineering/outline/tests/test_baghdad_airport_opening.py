import json
from math import pi
import pytest

from cities.Baghdad.airport_opening import calculate, validate_parent
from engineering.outline import baghdad_system


def test_airport_opening_prices_dedicated_assets_and_preserves_unpriced_scope():
    case = calculate()
    parent = baghdad_system.load()
    rates = parent["capital_rates_usd_m"]
    b, train, power = case["bundle"], case["train"], case["power"]
    assert b["active_sets"] == 18 and b["spares"] == 3
    assert power["common_service"]["annual_train_km"] == train["scheduled_trips"] * b["route_km"] * 365
    assert sum(train["sets_starting_at_A_B"]) == b["active_sets"]
    assert b["parent"] != case["candidate_id"]
    assert case["civil"]["beam_count"] == 2400 and case["civil"]["pier_foundation_count"] == 2402
    scope = case["scopes_usd_m"]
    assert len(scope) == 14
    assert scope["Depot and control centre"] == rates["depot"] + rates["control_centre"]
    assert scope["Grid supply sites"] == b["grid_sites"] * rates["traction_supply_site"]
    assert scope["Fleet, including spare sets"] == pytest.approx(21 * 8.48)
    assert case["controls"]["grid_protection_gateways"] == 3
    assert case["controls"]["station_dispatch_controllers"] == len(b["stops"])
    dedicated, shared = (case["facility_options"][k] for k in ("dedicated", "shared_or_temporary"))
    assert shared["matched_return_direct_usd_m"] is None
    assert sum(scope.values()) == pytest.approx(shared["priced_other_scope_with_allowances_usd_m"]
        + shared["direct_price_multiplier"] * dedicated["direct_reference_price_usd_m"])
    assert case["complete_opening_capital_usd_m"] is case["opening_date"] is None


def test_iraqi_airport_works_replace_generic_land_cost_and_retain_scope():
    case = calculate()
    estimate = case["iraq_site_estimate"]
    scopes = case["scopes_usd_m"]
    rates = baghdad_system.load()["capital_rates_usd_m"]
    factor = (1 + rates["design_fraction"] + rates["testing_fraction"]) * (1 + rates["project_allowance_fraction"])
    for key in ("low", "base", "high"):
        scenario = estimate["scenarios"][key]
        priced = sum(row["quantity"] * row["unit_iqd"] / estimate["iqd_per_usd"] / 1e6
                     for row in scenario["items"].values())
        assert scenario["direct_site_usd_m"] == pytest.approx(priced)
        assert scenario["capital_usd_m"] == pytest.approx(sum(scopes.values())
            + factor * (priced - scopes["Land, utilities and disruption"]))
        assert "Land, utilities and disruption" not in scenario["scopes_usd_m"]
        assert scenario["scopes_usd_m"]["Viaduct, piers and foundations"] == scopes["Viaduct, piers and foundations"]
    assert [estimate["scenarios"][key]["capital_usd_m"] for key in ("low", "base", "high")] == sorted(
        s["capital_usd_m"] for s in estimate["scenarios"].values())
    base = estimate["scenarios"]["base"]
    pile = base["items"]["Additional foundation shafts under standard caps"]
    assert base["affected_supports"] == 97
    assert pile["quantity"] == pytest.approx(97 * 2 * 24 * pi / 4)
    assert pile["unit_iqd"] == pytest.approx((154000*.36 + 1050000*.12 + 18000*.45 + 24000*.8) * 3.4)
    assert base["items"]["Extra beam haul above standard delivery"]["quantity"] == 2400 * 12
    assert base["items"]["Incremental yard premises and temporary access"]["quantity"] == 24
    lead = base["items"]["Extra depot lead and refuge track"]
    assert lead["direct_usd_m"] == pytest.approx(.85 * 33/32 * 2.5)


def test_iraqi_airport_operations_count_distinct_riders_and_replace_existing_costs():
    case = calculate()
    annual = case["iraq_operations"]
    scenarios = annual["cases"]
    base = scenarios["central"]
    days, trips = 365, case["train"]["scheduled_trips"]
    assert base["air_journeys"] == pytest.approx(4199253 * .12)
    assert base["all_journeys"] == pytest.approx(4199253 * .12 + 500 * days + 4 * 5 * trips * days)
    assert base["paid_journeys"] == pytest.approx(.92 * base["all_journeys"])
    assert base["net_farebox_usd_m"] == pytest.approx(base["paid_journeys"] * 750 * .85 / 1510 / 1e6)
    assert (annual["local_trip_km"], annual["airport_trip_km"]) == pytest.approx((4.2, 7.2))
    assert base["occupancy"] == pytest.approx(base["all_journeys"] * base["mean_trip_km"] / (trips * 12 * 365 * 700))
    costs = case["annual_opex_usd_m"]
    credit = annual["estimated_credit_by_envelope_usd_m_year"]
    assert base["embedded_credit_usd_m"] == pytest.approx(sum(credit.values()))
    assert base["non_revenue_non_energy_usd_m"] == pytest.approx(.025 * (costs["train_operations"] - credit["Non-energy train operations"]))
    for row in scenarios.values():
        assert row["opex_usd_m"] == pytest.approx(sum(costs.values()) - costs["electricity"] - sum(credit.values())
            + row["payroll_usd_m"] + row["electricity_usd_m"] + row["non_revenue_non_energy_usd_m"])
        assert row["annual_operating_support_usd_m"] == pytest.approx(row["opex_usd_m"] - row["net_farebox_usd_m"])
        assert row["total_fte"] == sum(annual["goa4_posts"].values()) + row["airport_liaison_fte"]
    assert scenarios["upside"]["annual_operating_support_usd_m"] < base["annual_operating_support_usd_m"] < scenarios["downside"]["annual_operating_support_usd_m"]


@pytest.mark.parametrize("change", ["pier_family", "power_parent"])
def test_airport_opening_rejects_mixed_equipment_parent(change):
    cfg = baghdad_system.load()
    folder = baghdad_system.ROOT / "cities/Baghdad"
    diagram = json.loads((folder / "service-diagrams.json").read_bytes())["networks"]["first"]
    selected = json.loads((folder / "system-results.json").read_bytes())["networks"]["first"]
    if change == "pier_family":
        cfg["selected_pier_family"] = "common-pier"
    else:
        selected["power_cases"]["protected_conductor"]["physical_candidate_id"] = "another-candidate"
    with pytest.raises(ValueError, match="matching 10 m"):
        validate_parent(cfg, diagram, selected)
