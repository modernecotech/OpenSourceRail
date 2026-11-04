from copy import deepcopy
from math import ceil, isclose

import pytest

from engineering.development_baseline import selection
from engineering.design_search import line_benchmark_service as service
from engineering.station_rail.common import identity


@pytest.fixture(scope="module")
def vehicle():
    return selection.load()["vehicle"]


@pytest.fixture
def inputs():
    requirements=dict(route_km=30,stations=12,trackways=2,cars_per_train=6,
        fixed_seats_per_car=44,wheelchair_places_per_car=2,headway_s=120,dwell_s=35,
        operating_hours_per_day=18)
    design=dict(speed_m_s=20,acceleration_m_s2=1,service_deceleration_m_s2=.6,
        jerk_m_s3=.5,terminal_turnback_s=180,reserve_fraction=.15,
        added_vehicle_mass_kg_per_car=250,aux_kw_per_car=35,charger_kw_per_car=200,
        charge_efficiency=.95)
    return requirements,design


def test_terminal_cycle_and_fleet_are_bidirectional_without_duplicate_clearance(inputs,vehicle):
    r,d=inputs;v=service.evaluate(r,d,vehicle)
    assert 184<v["profile"]["runtime_s"]<188
    expected_one_way=11*v["jerk_timing_profile"]["runtime_s"]+350
    expected_cycle=2*(expected_one_way+180)
    expected_active=ceil(expected_cycle/120)
    assert v["one_way_s"]==expected_one_way
    assert v["round_trip_s"]==expected_cycle
    assert v["active_trainsets"]==expected_active==43
    assert v["spare_trainsets"]==ceil(expected_active*.15)==7
    assert v["total_trainsets"]==50 and v["totalcars"]==300
    assert v["normal_places_per_train"]==276 and v["capacity_pphpd"]==8280
    assert v["fixed_seats_pphpd"]+v["wheelchair_places_pphpd"]==v["capacity_pphpd"]
    assert (v["departure_sites"],v["boarding_edges"],v["minimum_turnback_positions_per_end"],v["terminal_additional_positions"])==(22,24,2,2)
    assert all(v[k] is False for k in service.FLAGS)


def test_jerk_and_contact_envelope_do_not_become_integrated_journey(inputs,vehicle):
    v=service.evaluate(*inputs,vehicle)
    assert v["jerk_launch_distance_m"]==220
    assert v["full_train_fin_launch_envelope_m"]==296.5
    assert v["jerk_full_train_fin_launch_envelope_m"]==316.5
    assert v["jerk_timing_profile"]["launch_time_s"]==22
    assert v["jerk_timing_profile"]["launch_distance_m"]==220
    assert v["jerk_timing_model_valid"] is True
    # Independently integrate ramp, plateau and ramp-down to check tail passage.
    t=v["tail_clearance_s_jerk_bound"]
    u=t-2
    assert isclose(.5*2**3/6+(.5*2**2/2)*u+.5*u*u,104.5,abs_tol=1e-9)
    assert v["tail_clearance_s_constant_acceleration"]<t<16
    assert v["supported_journey_state"]=="not-run"


def test_added_reserve_propagates_to_force_energy_and_identity(inputs,vehicle):
    r,d=inputs;before=deepcopy((r,d,vehicle));a=service.evaluate(r,d,vehicle)
    d2={**d,"added_vehicle_mass_kg_per_car":750};b=service.evaluate(r,d2,vehicle)
    assert b["provisional_normal_mass_kg_per_car"]-a["provisional_normal_mass_kg_per_car"]==500
    assert b["peak_train_force_N"]>a["peak_train_force_N"]
    assert b["mechanical_work_kwh_per_departure"]>a["mechanical_work_kwh_per_departure"]
    assert b["evaluation_id"]!=a["evaluation_id"]
    assert (r,d,vehicle)==before
    assert a["evaluation_id"]==identity({k:x for k,x in a.items() if k!="evaluation_id"})


def test_auxiliary_balance_and_current_cap_are_not_assumed_passes(inputs,vehicle):
    r,d=inputs;v=service.evaluate(r,d,vehicle);q=v["auxiliary"]
    assert q["energy_margin_kwh_per_car_per_half_cycle"]>0
    adverse=service.evaluate(r,{**d,"aux_kw_per_car":50,"charger_kw_per_car":1000},vehicle)["auxiliary"]
    assert adverse["catalogue_capped_charger_kw_per_car"]==216
    assert adverse["energy_margin_kwh_per_car_per_half_cycle"]<0
    moving=11*v["jerk_timing_profile"]["runtime_s"];charge_s=350+180
    assert isclose(q["hotel_energy_kwh_per_car_per_half_cycle"],35*(moving+charge_s)/3600)
    assert isclose(q["charge_input_kwh_per_car_per_half_cycle"],200*charge_s/3600)
    assert q["actual_charge_map_available"] is False
    assert all(not p["reachable"] for p in v["grade_sensitivities"])


def test_planning_margin_changes_scheduled_fleet_without_inventing_motion(inputs,vehicle):
    r,d=inputs
    raw=service.evaluate(r,d,vehicle)
    planned=service.evaluate(r,{**d,"schedule_running_time_margin_fraction":.05},vehicle)
    assert planned["minimum_unpadded_active_trainsets"]==raw["active_trainsets"]==43
    assert planned["active_trainsets"]==45
    assert planned["total_trainsets"]==52
    assert planned["totalcars"]==312
    assert planned["profile"]==raw["profile"]
    assert planned["jerk_timing_profile"]==raw["jerk_timing_profile"]
    assert planned["mechanical_work_kwh_per_departure"]==raw["mechanical_work_kwh_per_departure"]
    assert planned["scheduled_segment_runtime_s"]==pytest.approx(raw["unpadded_segment_runtime_s"]*1.05)
    assert planned["one_way_s"]==pytest.approx(11*raw["unpadded_segment_runtime_s"]*1.05+350)
    assert planned["auxiliary"]["hotel_energy_kwh_per_car_per_half_cycle"]>raw["auxiliary"]["hotel_energy_kwh_per_car_per_half_cycle"]


def test_true_s_curve_launch_work_matches_independent_simpson_integration(inputs,vehicle):
    v=service.evaluate(*inputs,vehicle)
    def velocity(t):
        if t<=2:return .25*t*t
        if t<=20:return t-1
        u=t-20
        return 19+u-.25*u*u
    count=2200;step=22/count
    values=[velocity(i*step)**3 for i in range(count+1)]
    integral=step/3*(values[0]+values[-1]+4*sum(values[1:-1:2])+2*sum(values[2:-1:2]))
    mass=v["provisional_normal_mass_kg_per_car"]+v["rotating_equivalent_mass_kg_per_car"]
    c=v["profile"]["constant_wheel_drag_N_per_car"]
    expected=(mass*20**2/2+c*220+1.8*integral)*6/3.6e6
    assert v["mechanical_work_kwh_per_departure"]==pytest.approx(expected,rel=1e-10)
    assert v["jerk_launch_work"]["velocity_cubed_integral_m3_s2"]==pytest.approx(integral,rel=1e-10)
    assert v["mechanical_work_kwh_per_departure"]>v["constant_acceleration_mechanical_work_kwh_per_departure"]


def test_short_segment_cannot_inherit_a_full_speed_jerk_timetable(inputs,vehicle):
    r,d=inputs;v=service.evaluate({**r,"route_km":1},d,vehicle)
    assert v["jerk_timing_model_valid"] is False
    assert v["one_way_s"] is None and v["active_trainsets"] is None
    assert v["auxiliary"] is None


@pytest.mark.parametrize("which,key,value",[("r","route_km",float("nan")),("r","headway_s",0),
    ("r","stations",12.5),("r","fixed_seats_per_car",48),("r","trackways",1),
    ("d","added_vehicle_mass_kg_per_car",-1),("d","reserve_fraction",1.1),
    ("d","charge_efficiency",float("inf")),("d","jerk_m_s3",0),
    ("d","schedule_running_time_margin_fraction",-0.1)])
def test_invalid_or_incompatible_inputs_do_not_inherit_selected_vehicle(inputs,vehicle,which,key,value):
    r,d=inputs;(r if which=="r" else d)[key]=value
    with pytest.raises(ValueError):service.evaluate(r,d,vehicle)


def test_vehicle_mass_tampering_is_rejected(inputs,vehicle):
    altered=deepcopy(vehicle);altered["mass"]["accounted_cap_loaded_kg_per_car"]=0
    with pytest.raises(ValueError,match="identity"):
        service.evaluate(*inputs,altered)


def test_result_keeps_a_separate_input_snapshot(inputs,vehicle):
    r,d=inputs;d["annotation"]={"items":["provisional"]}
    value=service.evaluate(r,d,vehicle)
    d["annotation"]["items"].append("later")
    assert value["design"]["annotation"]["items"]==["provisional"]
    assert value["evaluation_id"]==identity({k:x for k,x in value.items() if k!="evaluation_id"})
