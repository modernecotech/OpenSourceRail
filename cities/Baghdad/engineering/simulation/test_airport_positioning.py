"""Exercise the corrected line's empty-working allowance against its declared gates."""
from itertools import pairwise
import math

import pytest

from cities.Baghdad.engineering.simulation import assumption_audit as audit, motion_power as motion


def inputs():
    route = audit.airport_alignment.evaluate()
    vehicle = audit.vehicle_audit.evaluate(grade_pct=0)
    demand, climate = audit.service_inputs(route, vehicle, 30, 40, None, "service_sensitive")
    mass = vehicle["mass_cases"]["central"]
    return dict(alignment=route, candidate_id=vehicle["candidate_id"], demand_record=demand,
                chainages_km=route["chainages_km"], auxiliary_kw=climate["auxiliary_kw"],
                dwell_s=demand["dwell_s"], tare_train_kg=mass["tare_train_kg"], loaded_train_kg=mass["loaded_train_kg"],
                headway_min=30, topology="paired6", phase_s=1306)


@pytest.mark.parametrize(("phase_s", "delay_s"), ((1306, 60), (1308, 58)))
def test_corrected_empty_workings_keep_passenger_slots_and_close_the_static_overlaps(phase_s, delay_s):
    request = dict(inputs(), phase_s=phase_s)
    refs = motion.reference()
    baseline = motion.service(motion.normalize(request, refs), refs)
    assert len(baseline[-1]["conflicts"]) == 4
    overlap = max(-row["margin_s"] for row in baseline[-1]["conflicts"])
    slack = 30 * math.ceil(overlap / 30)
    assert slack == 210
    for trial_s, conflicts in ((0, 4), (30, 4), (60, 2), (120, 2), (210, 0), (240, 0), (300, 0)):
        trial = motion.service(motion.normalize(dict(request, positioning_slack_s=trial_s), refs), refs)
        assert len(trial[-1]["conflicts"]) == conflicts
    corrected = motion.service(motion.normalize(dict(request, positioning_slack_s=slack), refs), refs)
    assert corrected[1] == baseline[1]
    assert corrected[2] == baseline[2]
    assert len(corrected[4]) == len(baseline[4]) == 2
    for work in corrected[4]:
        unit, side, dep, arr = work
        shift = -slack if side == 0 else slack
        assert (unit, side, dep - shift, arr - shift) in baseline[4]
    assert corrected[-1]["schedule_screen_passed"]
    for slots in corrected[-1]["resources"].values():
        assert all(first["end_s"] <= second["start_s"] for first, second in pairwise(slots))

    result = motion.evaluate(dict(request, positioning_slack_s=slack))
    metrics = result["metrics"]
    assert metrics["completed_passenger_trips"] == metrics["booked_passenger_trips"] == 72
    assert metrics["completed_positioning_trips"] == metrics["booked_positioning_trips"] == 2
    assert metrics["completed_yard_trips"] == metrics["booked_yard_trips"] == 6
    assert metrics["maximum_arrival_delay_s"] == delay_s
    assert result["demand_basis"]["od_id"] == audit.scenario._id(request["demand_record"]["hourly_od"])
    assert result["scenario"]["demand_evaluation_id"] == request["demand_record"]["evaluation_id"]
    booked = sum(metrics[key] for key in ("booked_passenger_km", "booked_positioning_km", "booked_yard_km"))
    assert metrics["booked_yard_km"] == 1.5
    assert result["booked_annual_train_km"] == pytest.approx(booked * refs[0]["vehicle"]["service_days_per_year"])
    assert result["annual_train_km"] == pytest.approx(result["booked_annual_train_km"], abs=.01, rel=0)
    assert result["gates"]["service_within_arrival_envelope"]
    assert result["gates"]["route_and_block_reservations"]
    assert result["physical_accepted"] is False
    assert result["economic_ranking_eligible"] is False


def test_positioning_slack_requires_corrected_alignment_and_bounded_whole_seconds():
    with pytest.raises(ValueError, match="Positioning slack requires a revised alignment"):
        motion.normalize({"positioning_slack_s": 210})
    request = inputs()
    for invalid in (-1, True, 1810, 210.5):
        with pytest.raises(ValueError, match="whole seconds up to one headway"):
            motion.normalize(dict(request, positioning_slack_s=invalid))
