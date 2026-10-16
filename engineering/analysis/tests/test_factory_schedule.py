"""Independent interval calendars, continuous holds and shared-resource failures."""

from copy import deepcopy
import json

import pytest

from engineering.design_engine import factory_schedule as s
from engineering.design_engine.factory import ROOT


@pytest.fixture
def basis():
    return json.loads(
        (ROOT / "engineering/design_engine/data/factory-schedule.json").read_text()
    )


def test_one_beam_matches_hand_scheduled_elapsed_and_operating_hours(basis):
    basis.update(beam_count=1, horizon_days=4, maintenance=[])
    basis["hours"].update(
        reinforcement=1,
        cage_lift=1,
        bed_setup_stress=1,
        casting_setup_finish=1,
        mix_per_batch=0.5,
        pour_per_batch=0.5,
        curing_elapsed=24,
        release_demould=1,
        storage_elapsed=24,
        dispatch=1,
    )
    r = s.schedule(basis, 1, 1, 0.95)
    tasks = {t["task"]: t for t in r["tasks"]}
    assert [
        (tasks[k]["start_h"], tasks[k]["end_h"])
        for k in (
            "reinforcement",
            "cage_lift",
            "bed_setup_stress",
            "casting",
            "release_demould",
            "dispatch",
        )
    ] == [(0, 1), (1, 2), (2, 3), (3, 5), (29, 30), (54, 55)]
    assert r["crane_booked_hours"] == pytest.approx(5)
    assert r["planning_accepted_equivalent"] == pytest.approx(0.95)
    assert r["site_or_supplier_validated"] is False


def test_shift_boundary_and_maintenance_are_independent_calendar_constraints():
    c = s.Calendar({"a": 1}, 8, [dict(resource="a", unit=0, start_h=0, end_h=3)])
    task = c.task("one", "test", ["a"], 0, 2)
    assert task["start_h"] == 3
    assert c.slot(["a"], 5, 4)[0] == 24
    with pytest.raises(ValueError):
        c.slot(["a"], 0, 9)
    with pytest.raises(ValueError, match="overlapping"):
        c.reserve([("a", 0)], 4, 6, "bad")


def test_shared_crane_and_storage_hold_are_not_free_parallel_capacity(basis):
    r = s.schedule(basis, 32.34055, 4, 0.95)
    assert r["batches_per_beam"] == 33
    assert r["casting_block_h"] == pytest.approx(5.2)
    assert r["backlog_at_horizon"] > 0
    assert s.validate(r)
    intervals = sorted(
        (x["start_h"], x["end_h"])
        for x in r["reservations"]
        if x["resource"] == "crane"
    )
    assert all(a[1] <= b[0] + 1e-8 for a, b in zip(intervals, intervals[1:]))
    compressed = deepcopy(basis)
    compressed["resources"]["storage_slot"] = 1
    compressed["hours"]["storage_elapsed"] = 72
    congested = s.schedule(compressed, 32.34055, 4, 0.95)
    assert congested["dispatched_within_horizon"] < r["dispatched_within_horizon"]


@pytest.mark.parametrize(
    "fault", ["crane", "hold", "maintenance", "duration", "unknown-unit", "cure"]
)
def test_retained_schedule_cannot_omit_capacity_or_shorten_holds(basis, fault):
    r = s.schedule(basis, 32.34055, 4, 0.95)
    if fault == "crane":
        r["tasks"][1]["resources"] = [
            x for x in r["tasks"][1]["resources"] if x["resource"] != "crane"
        ]
    elif fault == "hold":
        r["reservations"] = [
            x
            for x in r["reservations"]
            if not (x["resource"] == "bed" and x["task"] == "beam-001/hold")
        ]
    elif fault == "maintenance":
        r["reservations"] = [x for x in r["reservations"] if x["task"] != "maintenance"]
    elif fault == "duration":
        r["tasks"][0]["end_h"] -= 1
    elif fault == "unknown-unit":
        r["reservations"][0]["unit"] = 999
    else:
        r["curing_elapsed_h"] = 0
    with pytest.raises(ValueError):
        s.validate(r)


def test_invalid_capacity_or_long_casting_blocks_reject(basis):
    basis["resources"]["crane"] = 0
    with pytest.raises(ValueError):
        s.schedule(basis, 32.34055, 4, 0.95)
    basis["resources"]["crane"] = 1
    with pytest.raises(ValueError):
        s.schedule(basis, 500, 4, 0.95)
