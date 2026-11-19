from collections import Counter, defaultdict
from itertools import pairwise

import pytest

from engineering.outline.baghdad_diagrams import build, pattern


@pytest.fixture(scope="module")
def schedule():
    return build()


def test_each_train_reaches_its_next_origin_and_hourly_offer_is_met(schedule):
    report, details = schedule
    for (network, group), (trips, patterns) in details.items():
        row = report["networks"][network]["groups"][group]
        sets = defaultdict(list)
        departures = Counter()
        for train, side, dep, arr in trips:
            sets[train].append((side, dep, arr))
            departures[(side, dep // 3600)] += 1
        expected = [6, 6, 12, 12, 24, 24, 12, 12, 12, 12, 24, 24, 12, 12, 6, 6, 6, 6]
        for side in (0, 1):
            assert [departures[side, hour] for hour in range(6, 24)] == expected
        for path in sets.values():
            for (a, _, arr), (b, dep, _) in pairwise(path):
                assert patterns[a][-1]["id"] == patterns[b][0]["id"]
                assert dep >= arr + 180
        for calls in patterns:
            assert calls[0]["departure_s"] == 0
            assert calls[-1]["arrival_s"] == row["one_way_s_including_dwell"]
            assert all(b["arrival_s"] > a["departure_s"] for a, b in pairwise(calls))
            assert all(s["departure_s"] - s["arrival_s"] == 35 for s in calls[1:-1])
        assert row["sets_starting_at_A_B"] == row["sets_finishing_at_A_B"]
        assert sum(row["sets_starting_at_A_B"]) == len(sets) == row["diagrammed_sets"]


def test_held_service_and_named_unlocated_stops_remain_visible(schedule):
    report, _ = schedule
    first, metro = (report["networks"][key] for key in ("first", "metropolitan"))
    assert first["annual_diagrammed_train_km"] == 24666408
    assert first["diagrammed_sets"] == 208
    stops = [s for g in first["groups"].values() for s in g["outward_stops"]]
    assert sum(s["register_id"] is None for s in stops) == 15
    assert sum(s["location_scope"] == "unlocated_name" for s in stops) == 13
    assert set(metro["groups"]).isdisjoint(metro["held_service_group_ids"])
    assert metro["held_service_group_ids"] == ["M01", "M02", "M04", "M09"]
    assert (metro["diagrammed_sets"], metro["held_peak_trainsets_cost_screen"]) == (423, 319)
    assert metro["annual_cost_ledger_train_km"] == pytest.approx(
        metro["annual_diagrammed_train_km"] + metro["annual_held_cost_ledger_train_km"])
    assert metro["groups"]["M05"]["outward_stops"][0]["id"] == "airport-terminal"


def test_transfer_times_and_exclusive_station_blocks_remain_conditional(schedule):
    report, _ = schedule
    for network in report["networks"].values():
        assert any(t["overlap_seconds_if_shared_junction"] > 0 for t in network["intermediate_interchanges"])
        for transfer in network["intermediate_interchanges"]:
            ex = transfer["example_connection"]
            assert ex["departure_s"] == ex["arrival_s"] + ex["walk_allowance_s"] + ex["wait_after_walk_s"]
            assert ex["wait_after_walk_s"] >= 0
            assert transfer["overlap_seconds_if_shared_junction"] >= 0
    yellow = report["networks"]["first"]["groups"]["Yellow"]
    assert yellow["whole_interstop_block_conflicts_at_peak"] > 0
    assert yellow["worst_block_clearance_margin_s"] == -268
    with pytest.raises(ValueError, match="speed cap"):
        pattern([{"fraction": 0}, {"fraction": 1}], 100, 35, 3, 72)
