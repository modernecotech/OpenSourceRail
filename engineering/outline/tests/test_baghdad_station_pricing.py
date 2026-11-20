"""Prevent point occurrences, duplicated station IDs or partial quotes becoming a station price."""
from copy import deepcopy

import pytest

from cities.Baghdad.maps.station_pricing import DIR, build, guide, price, station_row, template


@pytest.fixture(scope="module")
def record():
    return build()


def offer(n):
    row = station_row()
    points = max(n["same_source_groups"], key=len)
    row.update(budget_slot=n["budget_slots"][0], surveyed_station_id="Fixture site 001",
               station_class="interchange", mapped_point_ids=points, complete_station_scope_usd_m=19)
    row["evidence"] = {k: "fixture/"+k for k in row["evidence"]}
    return row


def test_budgets_keep_unassigned_slots_and_repeated_map_features(record):
    first, metropolitan = record["networks"].values()
    assert len(first["source_occurrences"]) == 37
    assert len(first["same_source_groups"]) == 27
    assert len(record["first_review_located"]) == 39
    assert sum(map(len,record["first_review_unlocated"].values())) == 13
    assert len(metropolitan["same_source_groups"]) == 220
    assert metropolitan["coordinate_count"] == 177
    for network, count, cost in ((first,64,832), (metropolitan,280,3640)):
        base = price(network,template(network))
        assert len(base["unassigned_slots"]) == count
        assert base["comparative_station_scope_usd_m"] == cost
    assert guide(record) == (DIR/"STATION-PRICING.md").read_text()


def test_shared_entrances_match_only_one_full_station(record):
    n = record["networks"]["first"]
    form=template(n)
    form["stations"].append(offer(n))
    result=price(n,form)
    assert result["class_subtotals"]["interchange"] == {"stations":1,"direct_usd_m":19}
    assert result["comparative_station_scope_usd_m"] == 838
    assert len(result["unassigned_slots"]) == 63
    with pytest.raises(ValueError):
        price(record["networks"]["metropolitan"],form)
    row=deepcopy(form["stations"][0])
    row.update(budget_slot=n["budget_slots"][1],surveyed_station_id="Fixture site 002")
    form["stations"].append(row)
    with pytest.raises(ValueError, match="linked points"):
        price(n,form)
    row["mapped_point_ids"]=[]
    row["surveyed_station_id"]=" fixture SITE 001 "
    with pytest.raises(ValueError, match="unique station"):
        price(n,form)


@pytest.mark.parametrize("bad",["missing scope", "unmapped foreign point", "non-finite price"])
def test_refuse_ineligible_substitution(record,bad):
    n=record["networks"]["first"]
    form=template(n)
    row=offer(n)
    form["stations"].append(row)
    if bad=="missing scope":
        row["evidence"]["step_free_access_and_egress"] = None
    elif bad=="unmapped foreign point":
        row["mapped_point_ids"]=["M-001"]
    else:
        row["complete_station_scope_usd_m"]=float("nan")
    with pytest.raises(ValueError):
        price(n,form)
