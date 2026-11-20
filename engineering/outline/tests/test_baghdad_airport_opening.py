import json
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
