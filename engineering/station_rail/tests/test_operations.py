from math import isclose
import pytest
from engineering.station_rail import operations as op


def test_energy_and_geometry_close_for_wheel_train():
    p=op.profile(2000,23000)
    assert p['reachable']
    assert abs(p['phase_distance_residual_m'])<1e-8
    assert abs(p['longitudinal_energy_residual_J_per_car'])<1e-7
    assert p['peak_speed_m_s']==20
    assert 0<p['arrival_speed_before_braking_m_s']<20
    assert p['rolling_bearing_aerodynamic_dissipation_J_per_car']>0
    assert p['actual_traction_force_available_N'] is None


def test_short_leg_does_not_invent_cruise_or_overrun():
    p=op.profile(200,23000)
    assert p['reachable'] and p['peak_speed_m_s']<20
    assert p['coast_distance_m']==0
    assert isclose(p['launch_distance_m']+p['braking_distance_m'],200)


def test_drag_is_recomputed_from_actual_mass():
    a=op.profile(2000,18000);b=op.profile(2000,30000)
    assert b['constant_wheel_drag_N_per_car']>a['constant_wheel_drag_N_per_car']
    assert b['launch_mechanical_energy_J_per_car']>a['launch_mechanical_energy_J_per_car']


def test_long_coast_and_downhill_are_retained_failures():
    long=op.profile(100000,23000)
    assert not long['reachable'] and long['runtime_s'] is None
    down=op.profile(2000,23000,grade_fraction=-.02)
    assert not down['reachable'] and 'distributed_braking' in down['reason']


def test_insufficient_station_zone_cannot_pass_even_with_fast_headway():
    p=op.profile(2000,23000)
    bad=op.station_zone(p,350)
    assert not bad['geometry_full_engagement']
    assert bad['nominal_resource_screen']=='fail'
    good=op.station_zone(p,1200)
    assert good['geometry_full_engagement']
    assert good['sections_per_direction']==96
    assert good['nominal_resource_screen']=='pass'
    exclusive=op.station_zone(p,1200,independent_train_phase_branches=1)
    assert exclusive['nominal_resource_screen']=='fail'


def test_wet_downhill_brake_no_regen_credit():
    wet=op.brake_bound()
    assert wet['stopping_distance_m']>690
    impossible=op.brake_bound(adhesion_coefficient=.03,downhill_grade_fraction=.04)
    assert impossible['necessary_stop_screen']=='fail'
    assert impossible['stopping_distance_m'] is None


def test_inputs_fail_closed():
    with pytest.raises(ValueError):op.profile(2000,-1)
    with pytest.raises(ValueError):op.profile(2000,20000,rolling_coefficient=-1)


def test_headwind_increases_energy_and_can_destroy_coast_reach():
    calm=op.profile(2000,23000)
    wind=op.profile(2000,23000,headwind_m_s=10)
    assert wind['reachable']
    assert wind['runtime_s']>calm['runtime_s']
    assert wind['launch_mechanical_energy_J_per_car']>calm['launch_mechanical_energy_J_per_car']
    assert abs(wind['phase_distance_residual_m'])<1e-8
    no_drag=op.profile(2000,23000,rolling_coefficient=0,bearing_drag_N_per_car=0,quadratic_drag_N_per_car_per_m_s_squared=0)
    assert no_drag['reachable']
    assert no_drag['runtime_s']==pytest.approx(125+100/6)
