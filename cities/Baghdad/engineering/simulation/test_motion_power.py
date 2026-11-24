"""Regression checks for moving ports, protective holds and common demand."""

import json
from types import SimpleNamespace
from zipfile import ZipFile

import pytest

from cities.Baghdad.engineering.simulation import airport_alignment, airport_demand, motion_adapters
from cities.Baghdad.engineering.simulation.motion_dc import Feeder, loadflow
from cities.Baghdad.engineering.simulation.motion_power import (HourlyPassengerLedger, evaluate, moving_grade,
                                                                 normalize, service, validate_od)


def test_shared_droop_and_directional_line_resistance():
    circuit = Feeder("test", (0., 2000.), .01, .008, .004, 2).circuit("normal")
    a, b = circuit.port(300., 0), circuit.port(700., 0)
    opposite = circuit.port(700., 1)
    left_v, left_p, source_i, loss, residual, _ = loadflow(circuit, [a, b], [2e6, 1e6], 4000.)
    divided_v, *_ = loadflow(circuit, [a, opposite], [2e6, 1e6], 4000.)
    assert all(x < y for x, y in zip(left_v, divided_v))
    assert residual < .01
    assert 1500 * source_i == pytest.approx(sum(left_p) + loss, abs=50)


def test_regen_receptivity_and_undervoltage_derating():
    circuit = Feeder("test", (0., 2000.), .01, .008, .004, 1).circuit("normal")
    a, b = circuit.port(800., 0), circuit.port(900., 0)
    volts, loads, supply, loss, _, _ = loadflow(circuit, [a, b], [1e6, -2e6], 4000.)
    assert 0 <= supply < 1e-9 and volts[1] < 1650
    assert sum(loads) <= 0 and loss > 0
    volts, loads, _, _, _, _ = loadflow(circuit, [a, b], [12e6, 12e6], 12000.)
    assert min(volts) < 1350 and max(loads) < 12e6


def test_formation_phase_and_hourly_demand():
    cfg = normalize({"cars": 3, "headway_min": 20})
    assert cfg["length_m"] == 52
    assert service(cfg)[0]["terminal_B_phase_s"] == 600
    assert not service(cfg)[-1]["conflicts"]
    with pytest.raises(ValueError, match="matrix"):
        normalize({"hourly_od": [[[0.] * 6 for _ in range(6)]]})
    with pytest.raises(ValueError, match="nonnegative"):
        validate_od([[-1.] * 6 for _ in range(6)])


def test_profile_grade_at_motion_position_and_in_each_direction(tmp_path):
    parent = airport_alignment.evaluate()
    points = [stop["longitude_latitude"] for stop in parent["stops"]]
    points[1] = [44.322, 33.298]
    points[4] = [44.351, 33.281]
    midpoint = [(a + b) / 2 for a, b in zip(points[0], points[1])]
    trace = [points[0], midpoint, *points[1:]]
    geometry = {"type": "LineString", "coordinates": trace}
    stops = [dict(id=stop_id, vertex=index, coordinates=point) for stop_id, index, point in
             zip(airport_alignment.STOP_IDS, [0, 2, 3, 4, 5, 6], points, strict=True)]
    digest = airport_alignment.identity(dict(geometry=geometry, stops=stops))
    vertical = dict(geometry_sha256=digest, datum="Synthetic datum", elevations_m=[30, 38, 31, 28, 28, 30, 29])
    survey = dict(schema=airport_alignment.SURVEY_SCHEMA, parent_candidate_id=parent["parent_candidate_id"],
                  crs="EPSG:4326", document="Synthetic fixture", revision="1", verification_reference="Fixture only",
                  geometry=geometry, stops=stops, geometry_sha256=digest, vertical_profile=vertical)
    path = tmp_path / "survey.json"
    path.write_text(json.dumps(survey))
    alignment = airport_alignment.evaluate(path)
    demand = airport_demand.evaluate(alignment, headway_min=30)
    inputs = dict(headway_min=30, step_s=4, alignment=alignment, chainages_km=alignment["chainages_km"],
                  demand_record=demand, dwell_s=demand["dwell_s"])
    case = normalize(inputs)
    vertex = case["grade_profile"]["chainages_m"][1]
    assert moving_grade(case, vertex - 1, 1, False) > 0
    assert moving_grade(case, vertex + 1, -1, False) > 0
    assert moving_grade(case, vertex, 1, False) < 0
    assert moving_grade(case, vertex, -1, False) < 0
    assert moving_grade(case, vertex, 1, True) == 0
    assert motion_adapters.sumo_check(case, None, None)["status"] == "out of domain"
    with pytest.raises(ValueError, match="explicit constant sensitivity"):
        normalize(dict(inputs, grade_pct=1.25))
    override = dict(inputs, grade_pct=1.25, grade_basis="constant_sensitivity")
    assert moving_grade(normalize(override), vertex, -1, False) == -.0125
    profiled = evaluate(inputs)
    flat = evaluate(dict(inputs, grade_basis="constant_sensitivity"))
    assert profiled["candidate_id"] == flat["candidate_id"]
    assert profiled["evaluation_id"] != flat["evaluation_id"]
    assert profiled["metrics"]["vertical_break_step_absolute_error_kwh"] > 0
    assert profiled["energy_kwh_per_train_km"] != flat["energy_kwh_per_train_km"]

    vertical["elevations_m"][1] = 3000
    path.write_text(json.dumps(survey))
    steep = airport_alignment.evaluate(path)
    steep_inputs = dict(inputs, alignment=steep, demand_record=airport_demand.evaluate(steep, headway_min=30))
    with pytest.raises(ValueError, match="planning domain"):
        normalize(steep_inputs)

    # Posted limits are evidence attached to this trace, not radii inferred
    # from its polyline vertices. Use the lowest limit in either direction
    # for a conservative whole-route service and motion sensitivity.
    vertical["elevations_m"][1] = 38
    survey["speed_profile"] = dict(
        geometry_sha256=digest,
        limits_kmh=dict(outward_kmh=[72] * (len(trace) - 1),
                        inward_kmh=[72] * (len(trace) - 1)))
    path.write_text(json.dumps(survey))
    same_cap = airport_alignment.evaluate(path)
    assert same_cap["alignment_id"] == alignment["alignment_id"]
    assert same_cap["record_id"] != alignment["record_id"]
    same_cap_inputs = dict(inputs, alignment=same_cap,
                           demand_record=airport_demand.evaluate(same_cap, headway_min=30))
    assert normalize(same_cap_inputs)["speed_profile"] == same_cap["speed_profile"]
    same_cap_motion = evaluate(same_cap_inputs)
    assert same_cap_motion["candidate_id"] == profiled["candidate_id"]
    assert same_cap_motion["evaluation_id"] != profiled["evaluation_id"]
    assert same_cap_motion["metrics"]["completed_passenger_trips"] == profiled["metrics"]["completed_passenger_trips"]
    assert same_cap_motion["metrics"]["distance_km"] == profiled["metrics"]["distance_km"]
    survey["speed_profile"]["limits_kmh"]["inward_kmh"][2] = 45
    path.write_text(json.dumps(survey))
    reduced = airport_alignment.evaluate(path)
    slower_demand = airport_demand.evaluate(reduced, headway_min=30)
    assert slower_demand["service_offer"]["observation_context"]["speed_cap_kmh"] == 45
    assert slower_demand["service_offer"]["observation_context"]["commercial_speed_kmh"] == 38 * 45 / 72
    assert slower_demand["generalised_cost"]["reference_minutes"] == demand["generalised_cost"]["reference_minutes"]
    assert slower_demand["service_offer"]["booked_ride_minutes"][0][5] > demand["service_offer"]["booked_ride_minutes"][0][5]
    slower_inputs = dict(inputs, alignment=reduced, demand_record=slower_demand)
    slower_case = normalize(slower_inputs)
    assert slower_case["speed_m_s"] == 45 / 3.6
    with pytest.raises(ValueError, match="Airport demand ID"):
        normalize(dict(inputs, alignment=reduced, demand_record=same_cap_inputs["demand_record"]))
    slower_schedule = service(slower_case)
    assert max(leg["cruise_m_s"] for direction in slower_schedule[3] for leg in direction) <= 45 / 3.6
    slower = evaluate(slower_inputs)
    assert slower["scenario"]["speed_m_s"] == 45 / 3.6
    assert slower["metrics"]["fleet_sets_required"] >= same_cap_motion["metrics"]["fleet_sets_required"]
    feed = tmp_path / "restricted.gtfs.zip"
    exported = motion_adapters.matched_gtfs(reduced, slower_case, slower_schedule, feed)
    assert exported["speed_offer"]["speed_cap_kmh"] == 45
    assert exported["trips"] == len(slower_schedule[1])
    with ZipFile(feed) as archive:
        assert len(archive.read("trips.txt").splitlines()) == exported["trips"] + 1
        assert len(archive.read("stop_times.txt").splitlines()) > exported["trips"]
    repeated = (slower_schedule[0], slower_schedule[1] + [slower_schedule[1][0]], *slower_schedule[2:])
    with pytest.raises(ValueError, match="directional booked service"):
        motion_adapters.matched_gtfs(reduced, slower_case, repeated, tmp_path / "duplicate.zip")
    flat_slower_case = normalize(dict(slower_inputs, grade_basis="constant_sensitivity"))
    flat_slower = evaluate(dict(slower_inputs, grade_basis="constant_sensitivity"))
    native = motion_adapters.sumo_check(flat_slower_case, service(flat_slower_case), flat_slower["events"])
    if motion_adapters._executable("sumo") and motion_adapters._executable("netconvert"):
        assert native["status"] == "verified execution"
        assert native["booked_route_trips"] == len(slower_schedule[1]) + len(slower_schedule[4])
        assert max(curve["speed_limit_m_s"] for curve in native["traction_curves"].values()) == 45 / 3.6
    else:
        assert native["status"] == "held"
    survey["speed_profile"]["geometry_sha256"] = "wrong"
    path.write_text(json.dumps(survey))
    with pytest.raises(ValueError, match="bind the supplied"):
        airport_alignment.evaluate(path)
    survey["speed_profile"]["geometry_sha256"] = digest
    del survey["speed_profile"]["limits_kmh"]["inward_kmh"]
    path.write_text(json.dumps(survey))
    with pytest.raises(ValueError, match="both directions"):
        airport_alignment.evaluate(path)


def test_observed_demand_cannot_move_under_a_different_formation(tmp_path):
    alignment = airport_alignment.evaluate()
    forecast = airport_demand.evaluate(alignment)
    survey = dict(schema=airport_demand.OBSERVED_SCHEMA, alignment_id=alignment["alignment_id"],
                  stop_ids=forecast["stop_ids"], timezone="Asia/Baghdad", document="Synthetic fixture",
                  service_offer=forecast["service_offer"]["observation_context"], sample_date_from="2026-11-24",
                  sample_date_to="2026-11-24", observed_days=1, resolution="hourly",
                  od=[{"from": forecast["stop_ids"][0], "to": forecast["stop_ids"][-1],
                       "hour": 10, "all": 50, "paying": 30}])
    path = tmp_path / "observed.json"
    path.write_text(json.dumps(survey))
    observed = airport_demand.evaluate(alignment, observed=path)
    inputs = dict(alignment=alignment, chainages_km=alignment["chainages_km"], demand_record=observed)
    assert normalize(inputs)["cars"] == 6
    with pytest.raises(ValueError, match="formation must match"):
        normalize(dict(inputs, cars=3))
    assert normalize(dict(inputs, cars=3, demand_record=forecast))["cars"] == 3


def test_all_workings_and_radial_isolation():
    od = [[[0.] * 6 for _ in range(6)] for _ in range(24)]
    od[10][0][5] = 100.
    base = dict(headway_min=30, cars=3, loaded_train_kg=95000, tare_train_kg=70000,
                hourly_od=od, auxiliary_kw=80, step_s=4)
    nominal = evaluate(base)
    assert nominal["scenario"]["aux_w"] == 80000
    assert "hourly_od" not in nominal["scenario"]
    assert nominal["metrics"]["boarded_passengers"] == pytest.approx(100)
    assert nominal["metrics"]["unserved_passengers"] == 0
    assert nominal["metrics"]["completed_passenger_trips"] == 72
    assert nominal["gates"]["dc_numerical_screen"]
    assert nominal["metrics"]["fleet_sets_required"] == nominal["metrics"]["diagrammed_sets"] + 3
    assert nominal["gates"]["all_workings_complete"]
    assert not nominal["economic_ranking_eligible"]
    loss = evaluate(dict(base, condition="path_out"))
    assert loss["metrics"]["unserved_passengers"] == 100
    assert loss["metrics"]["protected_hold_train_s"] > 0
    assert not loss["gates"]["all_workings_complete"]
    assert not loss["gates"]["electrical_isolation_screen"]


def test_boarded_but_interrupted_od_is_not_a_completed_journey():
    od = [[[0.] * 6 for _ in range(6)] for _ in range(24)]
    od[9][0][5] = 100.
    ledger = HourlyPassengerLedger(dict(hourly_od=od, demand_factor=1., capacity=700))
    job = SimpleNamespace(kind="passenger", side=0, boarded=0., denied=0., riders=[0.] * 5)
    train = SimpleNamespace(job=job, leg=0, onboard={})
    ledger.board(train, 36000)
    interrupted = ledger.totals()
    assert interrupted["gross_boardings"] == pytest.approx(100.)
    assert interrupted["boarded_passengers"] == 0.
    assert interrupted["unserved_incomplete_trip"] == pytest.approx(100.)
    train.leg = 4
    ledger.alight(train)
    completed = ledger.totals()
    assert completed["boarded_passengers"] == pytest.approx(100.)
    assert completed["unserved_incomplete_trip"] == 0.


def test_sumo_force_curve_uses_formation_and_selected_mass():
    from cities.Baghdad.engineering.simulation.motion_adapters import train_curve

    six = normalize({"cars": 6, "loaded_train_kg": 200000, "tare_train_kg": 150000})
    three = normalize({"cars": 3, "loaded_train_kg": 100000, "tare_train_kg": 75000})
    full, half = train_curve(six, 0), train_curve(three, 0)
    assert full["mass_kg"] == 2 * half["mass_kg"]
    assert full["rolling_resistance_kn"][0] == 2 * half["rolling_resistance_kn"][0]
    assert full["tractive_effort_limit_kn"] == 2 * half["tractive_effort_limit_kn"]
    assert full["wheel_power_limit_kw"] == 2 * half["wheel_power_limit_kw"]
    assert full["net_launch_accel_m_s2"] == pytest.approx(.6)
    assert train_curve(six, 0, positioning=True)["mass_kg"] == 150000
    assert full["tractive_effort_kn"][-1] * full["speeds_m_s"][-1] == pytest.approx(full["wheel_power_limit_kw"])
    uphill, downhill = [train_curve({**six, "grade_pct": 2}, side) for side in (0, 1)]
    assert uphill["grade_force_kn"] > 0 > downhill["grade_force_kn"]
    assert uphill["tractive_effort_limit_kn"] > full["tractive_effort_limit_kn"] > downhill["tractive_effort_limit_kn"]


def test_hourly_od_conserves_demand_after_final_real_boarding_call():
    od = [[[0.] * 6 for _ in range(6)] for _ in range(24)]
    od[10][0][5] = 100.
    od[23][0][5] = 200.
    result = evaluate(dict(headway_min=30, hourly_od=od, step_s=4.))
    metrics = result["metrics"]
    end = max(ev["actual_departure_s"] for ev in result["events"]
              if ev["kind"] == "passenger" and ev["direction"] == 0)
    outside = (86400 - end) * 200 / 3600
    assert metrics["offered_passengers"] == 300.
    assert metrics["unserved_service_boundary"] == pytest.approx(outside, abs=1e-6)
    assert metrics["unserved_service_boundary"] > 0.
    assert metrics["unserved_capacity_at_close"] == 0.
    assert metrics["unserved_incomplete_trip"] == 0.
    assert metrics["boarded_passengers"] + metrics["unserved_passengers"] == pytest.approx(300.)
    assert result["gates"]["capacity_screen"]
