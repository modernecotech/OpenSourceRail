"""Verify the open-circuit, timed-duty and installation accounts on the same Airport train."""
from copy import deepcopy
import json

import pytest

from cities.Baghdad.airport_opening import calculate, opening_inputs
from cities.Baghdad.airport_service import build_service
from cities.Baghdad.airport_supply import bind_supply, build_supply


@pytest.fixture(scope="module")
def layout():
    inputs = opening_inputs()
    service = build_service(inputs[0], inputs[1]["networks"]["first"]["groups"]["Airport"])
    offer = calculate(inputs=inputs, service=service)
    replay = build_supply(service, offer["power"], 12)
    return inputs, service, offer["power"], replay


def test_first_network_bay_is_replaced_by_airport_chainage(layout):
    _, _, _, r = layout
    ref = r["reference"]
    assert ref["site_chainage_km"] == [0, 6, 12]
    assert [row["collector_kv"] for row in ref["midpoint_cases"]] == pytest.approx(
        [1.413708, 1.314372, 1.314372, 1.023005], abs=1e-6)
    assert ref["replay"][1]["worst"]["status"] == "no stable constant-power operating point"
    assert r["minimum_without_impedance_reserve"]["grid_sites"] == 23
    assert r["minimum_without_impedance_reserve"]["sensitivity_two_train_outage"]["collector_kv"] < r["floor_kv"]


def test_all_site_outages_and_kirchhoff_bound(layout):
    _, service, power, r = layout
    assert r["physical_accepted"] is False
    assert r["grid_sites"] == 30
    selected = r["selected"]
    outages = selected["outages"]
    assert [v["failed_site"] for v in outages] == [None, *range(30)]
    assert all(v["worst"]["collector_kv"] >= r["floor_kv"] and v["site_rms_ka_upper"] > 0
               and v["conductor_heat_kw_upper_per_site"] > 0 for v in outages)
    peak_dc = power["traction"]["dc_input_rating_request_mw"]
    running = service["group"]["diagrammed_sets"]
    cruise = peak_dc * (.02 * 9.81 + .02) / (.6 + .02 * 9.81 + .02)
    load = 2 * peak_dc + .3 * running + (running - 2) * cruise
    loop = 1.1 * (.010 + (.008 + .004) * 12 / 29)
    # Independently bisect P = V(E-V)/R on its high voltage branch.
    low, high = .75, 1.5
    for _ in range(60):
        mid = (low + high) / 2
        if mid * (1.5 - mid) / loop >= load:
            low = mid
        else:
            high = mid
    assert selected["minimum_collector_kv"] == pytest.approx(low)
    assert r["procurement"]["minimum_site_peak_dc_mw"] == pytest.approx(1.5 * load / low)
    assert r["procurement"]["feed_half_bays"] == r["procurement"]["dc_outgoing_breaker_circuits"] == 116
    assert r["procurement"]["normally_open_track_ties"] == 58
    assert r["replay"]["pulses"] == 5 * (144 + 2) + 6
    assert r["replay"]["peak_simultaneous_pulses_linewide"] == 2
    assert r["braking_reception"]["cases"][0]["unreceived_kwh"] > 6
    assert r["station_sited_quote_variant"]["installed_price_usd"] is None
    assert r["station_sited_quote_variant"]["minimum_collector_kv"] > 1.35
    json.dumps(r, allow_nan=False)


def test_identity_binding_requires_matching_vehicle_workings_and_final_switchgear(layout):
    inputs, service, _, r = layout
    final_power = calculate(inputs=inputs, service=service, size_feeder=True)["power"]
    bound = bind_supply(r, service, final_power, 12)
    assert bound == build_supply(service, final_power, 12)
    assert bound["power_candidate_id"] == final_power["physical_candidate_id"] != r["power_candidate_id"]
    assert bound["design_id"] == r["design_id"]
    assert bound["evaluation_id"] != r["evaluation_id"]
    corrupt = deepcopy(r)
    corrupt["procurement"]["minimum_site_peak_dc_mw"] /= 2
    altered_power = deepcopy(final_power)
    altered_power["traction"]["dc_input_rating_request_mw"] *= 1.02
    for receipt, workings, power in ((corrupt, service, final_power),
                                      (r, {**service, "positioning_trips": []}, final_power),
                                      (r, service, altered_power)):
        with pytest.raises(ValueError, match="must match"):
            bind_supply(receipt, workings, power, 12)


def test_unsupported_mass_keeps_failed_fixed_point(layout):
    _, service, power, _ = layout
    heavier = deepcopy(power)
    heavier["traction"]["dc_input_rating_request_mw"] *= 3
    unsupported = build_supply(service, heavier, 12)
    assert unsupported["grid_sites"] is unsupported["selected"] is None
    assert "droop" in unsupported["status"]
    assert unsupported["evaluation_id"]
    with pytest.raises(ValueError, match="same 12 km service"):
        build_supply({**service, "peak_headway_s": 150}, power, 12)
