"""Closed-form and failure controls for analytical architecture demand."""
from math import sqrt
import pytest
from engineering.design_search.architecture_demand import demand,G
from engineering.station_rail.operations import profile


def test_zero_drag_ideal_solution_and_exact_stop():
    m=23000.;rot=1770.;r=demand(2000,m,rot,powered_windows=[[0,500]],
        rolling_coefficient=0,constant_resistance_N_per_car=0,aero_coefficient_N_s2_m2=0)
    assert r['reachable'] and r['runtime_s']==pytest.approx(2000/20+20/(2*.4)+20/(2*.6),abs=1e-10)
    assert r['final_position_m']==2000 and r['final_speed_m_s']==0
    ke=.5*(m+rot)*20**2
    assert r['traction_mechanical_energy_J_per_car']==pytest.approx(ke,rel=1e-12)
    assert r['friction_brake_energy_J_per_car']==pytest.approx(ke,rel=1e-12)
    assert r['rolling_aero_dissipation_J_train']==0
    assert r['peak_required_force_N_per_car']==pytest.approx((m+rot)*.4)
    assert r['peak_friction_brake_force_N_per_car']==pytest.approx((m+rot)*.6)
    assert r['relative_energy_residual']<1e-12


def test_matches_existing_closed_form_coast_with_finite_launch_receiving_windows():
    p=profile(2000,23000,rotating_equivalent_mass_kg_per_car=1770)
    brake_start=2000-p['braking_distance_m']
    r=demand(2000,23000,1770,powered_windows=[[0,500],[brake_start,2000]])
    assert r['reachable']
    assert r['runtime_s']==pytest.approx(p['runtime_s'],abs=1e-8)
    assert r['phase_distance_m']['unpowered-coast']==pytest.approx(p['coast_distance_m'],abs=1e-8)
    assert r['traction_mechanical_energy_J_per_car']==pytest.approx(p['launch_mechanical_energy_J_per_car'],rel=1e-12)
    assert r['friction_brake_energy_J_per_car']==pytest.approx(p['receiving_mechanical_energy_J_per_car'],rel=1e-12)
    assert r['peak_required_power_W_per_car']==pytest.approx(p['peak_launch_power_W_per_car'],rel=1e-12)
    assert r['available_force'] is None and not r['physical_journey_completed']
    assert r['evidence']=='analytical-demand-only' and not r['complete_installed_mass']


def test_grade_wind_energy_and_step_refinement_close_independently():
    rows=[demand(2000,23000,1770,powered_windows=[[0,500]],grade=.004,headwind=9,dt=h) for h in (1.,.2,.05)]
    for r in rows:
        assert r['reachable'] and r['final_position_m']==2000 and r['final_speed_m_s']==0
        assert r['grade_work_J_train']==pytest.approx(-23000*G*.004*2000*6,rel=1e-11)
        balance=r['traction_mechanical_energy_J_train']-r['friction_brake_energy_J_train']-r['rolling_aero_dissipation_J_train']+r['grade_work_J_train']
        assert abs(balance)<1e-3 and r['relative_energy_residual']<1e-10
    assert abs(rows[0]['runtime_s']-rows[-1]['runtime_s'])<1e-7
    calm=demand(2000,23000,1770,powered_windows=[[0,500]])
    assert rows[-1]['runtime_s']>calm['runtime_s']
    assert rows[-1]['traction_mechanical_energy_J_train']>calm['traction_mechanical_energy_J_train']


def test_explicit_booster_prevents_known_off_zone_stall_without_hidden_power():
    stalled=demand(2000,23000,1770,powered_windows=[[0,100]])
    booster=demand(2000,23000,1770,powered_windows=[[0,100],[500,800]])
    assert not stalled['reachable'] and stalled['reason']=='stalled_off_powered_window'
    assert 100<stalled['final_position_m']<2000 and stalled['final_speed_m_s']==0
    assert booster['reachable'] and booster['final_position_m']==2000
    assert booster['phase_distance_m']['powered-acceleration']==pytest.approx(400.,abs=1e-9)
    assert all(p['required_traction_force_N_per_car']==0 for p in booster['trace'] if p['phase']=='unpowered-coast')
    rest=demand(1500,23000,1770,powered_windows=[])
    assert not rest['reachable'] and rest['runtime_s']==0 and rest['final_position_m']==0
    later=demand(1500,23000,1770,powered_windows=[[10,500]])
    assert not later['reachable'] and later['final_position_m']==0


def test_downhill_cap_protection_is_counted_as_friction_not_hidden_traction():
    r=demand(1500,23000,1770,powered_windows=[[0,500]],grade=-.02)
    assert r['reachable'] and r['peak_speed_m_s']<=20+1e-9
    assert r['phase_distance_m']['downhill-cap-braking']>600
    samples=[p for p in r['trace'] if p['phase']=='downhill-cap-braking']
    assert samples and all(p['required_friction_brake_force_N_per_car']>0 and p['required_traction_force_N_per_car']==0 for p in samples)
    assert r['grade_work_J_train']>0 and r['friction_brake_energy_J_train']>0


def test_short_route_brake_event_is_inside_timestep_and_rotation_is_not_weight():
    r=demand(200,23000,1770,powered_windows=[[0,200]],dt=.7)
    peak=sqrt(2*200/(1/.4+1/.6))
    assert r['reachable'] and r['peak_speed_m_s']==pytest.approx(peak,abs=1e-10)
    trigger=next(p for p in r['events'] if p['kind']=='final-brake-trigger')
    assert trigger['position_m']==pytest.approx(120,abs=1e-10)
    assert trigger['time_s']/.7!=pytest.approx(round(trigger['time_s']/.7))
    a=demand(200,23000,0,powered_windows=[[0,200]])
    assert r['trace'][0]['resistance_N_per_car']==a['trace'][0]['resistance_N_per_car']
    assert r['peak_required_force_N_per_car']-a['peak_required_force_N_per_car']==pytest.approx(1770*.4)


def test_invalid_inputs_and_budget_do_not_create_a_journey():
    for changed in [dict(distance_m=-1),dict(mass_kg_per_car=float('nan')),dict(rotating_mass_kg_per_car=-1),dict(cars=6.5),dict(headwind=-1),dict(dt=0),dict(maximum_runtime_s=601)]:
        kwargs=dict(distance_m=2000,mass_kg_per_car=23000,rotating_mass_kg_per_car=1770,powered_windows=[[0,500]])
        kwargs.update(changed)
        with pytest.raises(ValueError):demand(**kwargs)
    for windows in ([[100,0]],[[0,2001]],[[0,500],[400,600]],[[600,700],[0,500]],None):
        with pytest.raises(ValueError):demand(2000,23000,1770,powered_windows=windows)
    r=demand(2000,23000,1770,powered_windows=[[0,500]],maximum_steps=1)
    assert not r['reachable'] and r['execution']=='interrupted'
    assert r['reason']=='bounded_runtime_or_step_budget_exhausted'
    assert not r['physical_journey_completed'] and r['available_force'] is None
