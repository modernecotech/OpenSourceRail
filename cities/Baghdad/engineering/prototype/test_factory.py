from copy import deepcopy
from fractions import Fraction

import pytest

from cities.Baghdad.engineering.prototype import factory


def test_buyer_capacity_matches_the_issued_parts_and_fixture_ownership():
    record = factory.build()
    by_id = {row["id"]: row for row in record["resources"]}
    known = {"vehicle-saw": 1, "vehicle-body-bed": 2, "vehicle-bogie-bed": 1,
             "vehicle-arc-set": 3, "civil-beam-position": 8, "civil-cage": 5,
             "civil-haul": 4, "civil-erection": 1, "wayside-test": 1}
    assert {k: by_id[k]["required_units"] for k in known} == known
    assert by_id["civil-panel-table"]["required_units"] is None
    assert by_id["civil-panel-table"]["minimum_units"] == 4
    assert by_id["wayside-power-test"]["minimum_units"] is None
    assert by_id["civil-foundation"]["required_units"] is None
    assert record["peak_beam_inventory"] == 163 <= by_id["civil-stock-position"]["minimum_units"]
    assert [r["quantity"] for r in record["fixture_items"] if r["name"] == "Removable end bulkhead assembly"] == [16]
    assert record["prices_confirmed"] is False and record["fabrication_released"] is False
    assert all((factory.HERE / name).read_bytes() == raw for name, raw in factory.artifacts().items())


def test_longer_cure_requires_more_moulds_and_shared_unknown_remains_open():
    shop = {"workdays": 425, "hours_per_day": 24, "utilisation": 1, "daily_targets": {"beam": 8}}
    base = {"id": "bed", "minimum": 1, "load": [{"items": ["beam"], "hours": 24}]}
    demand = {"beam": Fraction(2400), "panels": None}
    assert factory.daily_capacity(base, shop, demand)["required_units"] == 8
    slow = deepcopy(base)
    slow["load"][0]["hours"] = 48
    assert factory.daily_capacity(slow, shop, demand)["required_units"] == 16
    slow["load"].append({"items": ["panels"], "hours": 24})
    row = factory.daily_capacity(slow, shop, demand)
    assert row["required_units"] is None and row["minimum_units"] == 16
    with pytest.raises(ValueError):
        factory.daily_capacity(base, {**shop, "utilisation": 1.2}, demand)
