"""Matched quantities, temporary costs and held construction-stage cases."""

from hashlib import sha256
from math import isclose
from zipfile import ZipFile

import pytest

from cities.Baghdad.engineering.mechanical.civil import rail_fed_erection as study


@pytest.fixture(scope="module")
def baseline():
    return study.evaluate()


def test_comparison_holds_geometry_and_splits_the_two_fronts(baseline):
    geom = baseline["geometry"]
    assert geom["standard_bays"] == 600
    assert geom["standard_girders"] == 1200
    assert geom["standard_shared_support_positions"] == 601
    methods = baseline["methods"]
    for result in methods.values():
        covered = sum(front["road_bays"] + front["rail_bays"] for front in result["fronts"])
        assert covered + result["meeting_bays"] == geom["standard_bays"]
        assert result["setup_and_initial_release_days"] + result["erection_elapsed_days"] == result["calendar_days"]
        assert result["cases"]["base"]["common_scope_usd"] == methods["road_day"]["cases"]["base"]["common_scope_usd"]
    rail = methods["rail_24h"]
    assert sorted(front["standard_bays"] for front in rail["fronts"]) == [299, 300]
    assert rail["starter_bays"] == 4 and rail["meeting_bays"] == 1
    assert rail["overhead_fallback_bays"] == 30
    assert rail["public_road_beam_trips"] + 2*rail["launched_bays"] == geom["standard_girders"]


def test_shuttle_length_release_and_matched_road_windows(baseline):
    methods = baseline["methods"]
    rail = methods["rail_24h"]
    assert rail["calendar_days"] < methods["road_day"]["calendar_days"]
    assert rail["calendar_days"] > methods["road_extended"]["calendar_days"]
    assert rail["road_lane_hours"] < methods["road_day"]["road_lane_hours"]
    assert rail["labour_hours"] > methods["road_day"]["labour_hours"]
    d = baseline["assumptions"]["delivery"]
    assert study.feed_hours(8, d) > study.feed_hours(4, d)
    for front in rail["fronts"]:
        assert front["track_release_hours"] == front["standard_bays"] * d["after_landing_deck_release_h"]
        assert 0 < front["flatbed_hours"] < front["rail_productive_hours"]
    assert not baseline["scope"]["physical_acceptance"]
    assert baseline["geometry"]["flatbed_mean_exceeds_high_operating_max_axle"]


def test_crew_prices_and_cost_headroom(baseline):
    methods = baseline["methods"]
    rail = methods["rail_24h"]
    for case, breakdown in rail["cases"].items():
        assert isclose(sum(r["cost_usd"][case] or 0 for r in rail["crew_shifts"]),
                       breakdown["temporary_and_other_costs_usd"]["launcher_payroll"])
        headroom = baseline["break_even"]["road_day"]["rail_24h"][case]
        assert isclose(headroom["saving_usd"],
                       methods["road_day"]["cases"][case]["method_scope_usd"] - breakdown["method_scope_usd"])
        assert sum(breakdown["road_allowance_usd"].values()) + sum(breakdown["temporary_and_other_costs_usd"].values()) == breakdown["method_scope_usd"]
    assert {c["start_minute"] for c in rail["crew_shifts"] if c["phase"] == "rail-fed erection"} == {360, 840, 1320}


def test_nonstandard_closing_bay_and_all_crossings_hold():
    result = study.evaluate(12.021, 0)
    assert result["geometry"]["standard_bays"] == 601
    assert result["geometry"]["residual_m"] == 1
    assert result["methods"]["rail_24h"]["public_road_beam_trips"] == 12
    assert result["methods"]["road_day"]["public_road_beam_trips"] == 1204
    with pytest.raises(ValueError, match="No standard bays left"):
        study.evaluate(12, 100)


def test_reference_paths_are_source_bound(baseline):
    for path, expected in baseline["source_sha256"].items():
        assert sha256((study.family.ROOT / path).read_bytes()).hexdigest() == expected
    with ZipFile(study.family.vehicle.PROTOTYPE / "airport-prototype.zip") as source:
        for name, expected in baseline["source_prototype_member_sha256"].items():
            assert sha256(source.read(name)).hexdigest() == expected


def test_yard_geometry_and_embedded_casting_payroll(baseline):
    yard = baseline["shared_quantities"]["yard"]
    assert yard["length_m"] == 216
    assert yard["width_m"] == 164
    assert yard["area_m2"] == sum(zone["area_m2"] for zone in yard["layout_bands"])
    assert yard["releases_per_yard_day"]*yard["mould_cycle_hours"]/24 == yard["mould_count"]
    assert yard["released_storage_slots"] == yard["initial_released_stock"] + yard["free_contingency_slots"]
    rail = baseline["methods"]["rail_24h"]
    assert len(rail["yard_shifts"]) == 6
    assert rail["labour_hours_including_casting"] == rail["labour_hours"] + sum(
        shift["paid_hours"] for shift in rail["yard_shifts"])
    assert all(shift["price_basis"] == "Embedded in girder fabrication" for shift in rail["yard_shifts"])
    assert rail["cases"]["base"]["common_scope_breakdown_usd"]["terminal_yard_temporary_hardstand"] == 1_275_264


def test_two_parallel_feeds_require_independent_paths_and_budget(baseline):
    with pytest.raises(ValueError, match="independently cleared"):
        study.evaluate(flatbeds_per_front=2)
    dual = study.evaluate(flatbeds_per_front=2, independent_feed_paths=2)
    old = baseline["methods"]["rail_24h"]
    new = dual["methods"]["rail_24h"]
    assert new["calendar_days"] < old["calendar_days"]
    assert new["plant"]["flatbeds"] == 2*old["plant"]["flatbeds"]
    assert new["temporary_track_km"] == 2*old["temporary_track_km"]
    assert dual["shared_quantities"]["yard"]["area_ha"] > baseline["shared_quantities"]["yard"]["area_ha"]
    assert new["cases"]["base"]["method_scope_usd"] > old["cases"]["base"]["method_scope_usd"]
    assert new["public_road_beam_trips"] == old["public_road_beam_trips"]
    assert not dual["engineering_screen"]["physically_eligible_methods"]


def test_one_launcher_outage_keeps_staffed_time_in_paid_scope(baseline):
    outage = study.evaluate(launcher_outage_days=10)
    expected = baseline["methods"]["rail_24h"]
    revised = outage["methods"]["rail_24h"]
    assert isclose(revised["calendar_days"] - expected["calendar_days"], 10)
    assert revised["fronts"][0]["prescribed_outage_days"] == 0
    assert revised["labour_hours"] > expected["labour_hours"]
    assert revised["cases"]["base"]["method_scope_usd"] > expected["cases"]["base"]["method_scope_usd"]


def test_short_branch_uses_one_offsite_yard_and_road_front():
    result = study.evaluate(.111, include_rail=False, shared_offsite_yard=True)
    assert result["geometry"]["standard_bays"] == 5
    assert result["geometry"]["residual_m"] == 11
    assert result["shared_quantities"]["yards"] == 0
    assert set(result["methods"]) == {"road_day", "road_extended"}
    for method in result["methods"].values():
        assert method["plant"]["concurrent_erection_fronts"] == 1
        assert method["plant"]["terminal_yards"] == 0
        assert method["plant"]["total_moulds"] == 0
        assert method["public_road_beam_trips"] == 12
        assert method["yard_shifts"]
        case = method["cases"]["base"]
        assert "two_yard_forms" not in case["common_scope_breakdown_usd"]
        assert "terminal_yard_temporary_land_lease" not in case["temporary_and_other_costs_usd"]
