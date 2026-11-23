from copy import deepcopy
import json

import pytest

from cities.Baghdad.engineering.prototype import factory, shop_costs, sourcing_estimates
from engineering.outline.baghdad_system import _id


def test_quantities_and_credits_follow_factory_operations():
    files = shop_costs.artifacts()
    assert all((shop_costs.HERE / name).read_bytes() == raw for name, raw in files.items())
    record = json.loads(files[shop_costs.REGISTER])
    issued = json.loads((factory.HERE / factory.ROUTES).read_bytes())
    rows = {row["id"]: row for row in record["resources"]}
    assert set(rows) == {row["id"] for row in issued["resources"]}
    assert len(rows) == len(record["resources"]) == 41
    assert all(0 < r["unit_rate_usd"]["low"] <= r["unit_rate_usd"]["base"] <= r["unit_rate_usd"]["high"]
               for r in rows.values())
    # The four vehicles cover the production schedule jointly. Charging for
    # every trip against each truck, or capitalising a truck, overstates cost.
    haul = rows["civil-haul"]
    assert (haul["factory_units"], haul["priced_quantity"], haul["extended_usd"]["base"]) == (4, 2400, 1560000)
    assert rows["civil-erection"]["priced_quantity"] == 300
    assert rows["civil-yard-hook"]["priced_quantity"] == 258
    assert rows["vehicle-plate-contract"]["priced_quantity"] == pytest.approx(20 + 0.06 * 2016)
    assert rows["vehicle-metrology"]["priced_quantity"] == 86
    assert rows["civil-panel-table"]["priced_quantity"] == 4
    assert rows["civil-panel-table"]["quantity_status"] == "known-subset"
    assert rows["civil-placement"]["priced_quantity"] == pytest.approx(2400 * 0.6702)
    assert rows["civil-placement"]["quantity_status"] == "known-subset"
    assert rows["civil-panel-hook"]["extended_usd"] is None
    assert rows["wayside-power-test"]["extended_usd"] is None
    assert record["approved_lot_credit_usd"] is None
    for lot_id, allocation in record["lot_allocations"].items():
        assert allocation["buyer_confirmed_overlap_credit_usd"] is None
        if lot_id == "traction-sites":
            assert allocation["priced_work_within_lot_usd"] is None
            continue
        for case in shop_costs.CASES:
            expected = sum(r["extended_usd"][case] for r in rows.values()
                           if r["lot_id"] == lot_id and r["extended_usd"] is not None)
            assert allocation["priced_work_within_lot_usd"][case] == pytest.approx(expected)
    assert record["period_subtotals_usd"][shop_costs.UPKEEP]["base"] == pytest.approx(
        record["period_subtotals_usd"][shop_costs.EQUIPMENT]["base"] * 0.04
    )
    assert record["factory_evaluation_id"] == issued["evaluation_id"]
    assert record["complete_workshop_installed_price_usd"] is None


def test_reject_mixed_or_incomplete_editions():
    estimate = sourcing_estimates.estimate_lots()
    issued = factory.build(estimate)
    for key in ("candidate_id", "frame_revision", "estimate_evaluation_id", "opening_evaluation_id"):
        changed = {**issued, key: "other"}
        changed["evaluation_id"] = _id({k: v for k, v in changed.items() if k != "evaluation_id"})
        with pytest.raises(ValueError):
            shop_costs.build(changed, estimate)
    altered = deepcopy(issued)
    altered["resources"].pop()
    with pytest.raises(ValueError, match="digest"):
        shop_costs.build(altered, estimate)
    altered["evaluation_id"] = _id({k: v for k, v in altered.items() if k != "evaluation_id"})
    with pytest.raises(ValueError, match="one matching line"):
        shop_costs.build(altered, estimate)


def test_new_panel_count_flows_to_hours_and_hire_as_a_quantity():
    issued = json.loads((factory.HERE / factory.ROUTES).read_bytes())
    panel = next(r for r in issued["resources"] if r["id"] == "civil-panel-hook")
    drivers = {**issued["opening_drivers"], "station bay panels after plant and access openings": 140}
    assert shop_costs.commercial_quantity(panel, {"basis": "shift"}, drivers) == (10, "booked shift", "planned")


def test_cam_training_and_owner_time_have_distinct_periods_and_credits():
    record = json.loads((shop_costs.HERE / shop_costs.REGISTER).read_bytes())
    scenario = record["cam_and_training_scenario"]
    rows = {r["id"]: r for r in scenario["lines"]}
    assert scenario["complete_local_price_usd"] is None
    assert len(record["resources"]) == 41
    assert rows["attendees"]["priced_quantity"] == 7 * 2 * 4
    assert rows["witness"]["priced_quantity"] == 2 * 8
    assert rows["metrology"]["extended_usd"]["base"] == 2 * 1700
    assert all(r["scope_credit"] for r in rows.values())
    assert rows["freecad"]["unit_rate_usd"]["base"] == record["references"]["freecad"]["listed_usd"] == 0
    assert rows["fusion"]["period"] == "optional annual substitution"
    assert "fusion" not in {r["id"] for r in rows.values() if r["period"] == "annual support"}
    assert set(scenario["period_subtotals_usd"]) == {r["period"] for r in rows.values()}
    for period, amounts in scenario["period_subtotals_usd"].items():
        for case in shop_costs.CASES:
            assert amounts[case] == sum(r["extended_usd"][case] for r in rows.values() if r["period"] == period)


def test_unissued_quantities_have_alternatives_outside_the_estimate():
    import tomllib

    record = json.loads((shop_costs.HERE / shop_costs.REGISTER).read_bytes())
    panels, one, two = record["open_quantity_sensitivities"]
    assert panels["assumed_panels"] == panels["assumed_templates"] * panels["panels_per_template"] == 600
    placement, hook = panels["lines"]
    assert placement["quantity"] == pytest.approx(600 * 0.1380456)
    assert hook["quantity"] == 43  # 1,200 moves of 15 min divided by seven usable hours.
    assert panels["additional_scope_usd"]["base"] == 66508.92
    assert one["additional_scope_usd"]["base"] == 180000
    assert two["additional_scope_usd"]["base"] == 360000
    assert record["period_subtotals_usd"][shop_costs.SERVICE]["base"] == 6972900
    assert {r["resource_id"] for case in (panels, one, two) for r in case["lines"]} == {
        "civil-placement", "civil-panel-hook", "wayside-power-test"}
    # When a true count arrives, its ordinary production row can be extended.
    # Suppress the corresponding hypothetical increment to avoid double booking.
    issued = json.loads((factory.HERE / factory.ROUTES).read_bytes())
    card = tomllib.loads((shop_costs.HERE / shop_costs.RATES).read_text())
    issued["opening_drivers"][one["driver"]] = 37
    assert shop_costs.open_quantity_scenarios(issued, card) == [panels]
    issued["opening_drivers"][panels["driver"]] = 475
    assert shop_costs.open_quantity_scenarios(issued, card) == []
