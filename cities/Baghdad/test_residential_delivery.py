from copy import deepcopy
from math import isclose

import pytest

from cities.Baghdad import holistic_network, residential_delivery


def _candidate():
    a, b, c, d = [[44.25, 33.30], [44.255, 33.30], [44.26, 33.30], [44.26, 33.305]]
    routes = {
        "A": ("A", [a, b, c], ["West", "Transfer", "East"]),
        "B": ("B", [d, c, b], ["North", "Transfer"]),
    }
    lines = {}
    stations = {}
    for code, path, ids in routes.values():
        track = holistic_network.Track(path)
        chainages = [0, float(track.chainage[1] / 1000), track.km] if code == "A" else [0, track.km]
        lines[code] = dict(geometry=path, station_ids=ids, loop=False, one_way_km=track.km,
                           station_chainage_km=dict(zip(ids, chainages, strict=True)))
        for site, km in zip(ids, chainages, strict=True):
            stations.setdefault(site, dict(coordinates=track.at(km), lines=[]))["lines"].append(code)
    transfers = [dict(id="Transfer", station_ids=["Transfer"], lines=["A", "B"])]
    result = dict(lines=lines, stations=stations, transfers=transfers)
    result["topology"] = holistic_network.validate(result)
    return holistic_network._identity(result)


def test_commons_use_physical_quantities_and_reconcile_prices_and_crews():
    network = _candidate()
    result = residential_delivery.evaluate(network, launcher_pairs=1, road_teams=1)
    assert result["candidate_id"] == network["candidate_id"]
    assert result["network_evaluation_id"] == network["evaluation_id"]
    q = result["quantities"]
    assert q["station_sites"] == 4
    assert q["transfer_sites"] == 1
    assert q["station_line_platform_packages"] == 5
    assert q["service_overlap_km"] > .4
    assert isclose(q["service_route_km"], q["unique_guideway_km"] + q["service_overlap_km"])
    assert q["double_track_km"] == q["unique_guideway_km"] * 2
    assert q["standard_girders"] == 2 * q["standard_bays"]
    assert q["standard_bearings"] == 8 * q["standard_bays"]
    assert isclose(q["standard_bays"] * .020 + q["residual_length_m"] / 1000, q["unique_guideway_km"])
    assert [row["selected_planning_method"] for row in result["orders"]] == ["rail_24h", "road_day"]
    assert result["programme"]["concurrent_yard_sites"] == 3
    assert result["programme"]["opening_date"] is None
    paid = result["workforce"]
    assert paid["paid_deck_and_casting_hours"] == paid["paid_erection_hours"] + paid["paid_casting_hours"]
    assert sum(row["paid_hours"] for row in paid["crew_shifts"]) == paid["paid_deck_and_casting_hours"]
    costs = list(result["cost_cases"].values())
    for row in costs:
        assert isclose(row["direct_usd_m"], sum(row["scope_usd_m"].values()))
        assert isclose(row["scope_usd_m"]["stations_access"], sum(row["station_scope_usd_m"].values()))
    assert costs[0]["direct_usd_m"] < costs[1]["direct_usd_m"] < costs[2]["direct_usd_m"]


def test_edited_map_identity_is_rejected_before_work_orders():
    network = deepcopy(_candidate())
    network["lines"]["A"]["one_way_km"] += 1
    with pytest.raises(ValueError, match="changed since the network map was evaluated"):
        residential_delivery.evaluate(network)
