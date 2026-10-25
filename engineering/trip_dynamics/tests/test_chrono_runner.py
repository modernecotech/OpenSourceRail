"""Executed native Chrono gravity, coupled transient and station geometry checks."""
import math
import json
from pathlib import Path

import pytest

from engineering.trip_dynamics import chrono_runner as r,formation


def scenario(distance=2000):
    return dict(schema='osr-trip-scenario/1',case_id='six-car-native-benchmark',mode='benchmark',distance_m=distance,cars=6,car_length_m=17.,powered_zone_m=350.,max_speed_m_s=20.,acceleration_m_s2=.8,load_case='AW3',temperature_C=20.)


@pytest.fixture(scope='module')
def native():
    info=r.solver_info()
    if not info['available']:pytest.skip('Genuine Project Chrono unavailable; no numerical fallback')
    return info


def gravity(dt):
    c,s=r.new_system();b=c.ChBody();b.SetMass(2.);b.SetPos(c.ChVector3d(0,0,3));s.AddBody(b)
    for _ in range(round(1/dt)):s.DoStepDynamics(dt)
    return dict(z_m=b.GetPos().z,vz_m_s=b.GetPosDt().z,t_s=s.GetChTime())


def coupled(dt):
    c,s=r.new_system();train=formation.build(s,c,[1000.,2000.],coupler_stiffness_N_per_m=10000.,coupler_damping_Ns_per_m=1000.)
    bodies=train['bodies'];idx=train['accumulators'][0]
    for _ in range(round(2/dt)):
        bodies[0].EmptyAccumulator(idx);bodies[0].AccumulateForce(idx,c.ChVector3d(1000,0,0),bodies[0].GetPos(),False);s.DoStepDynamics(dt)
    displacement=[b.GetPos().x-x0 for b,x0 in zip(bodies,train['initial_positions_m'])]
    return dict(t_s=s.GetChTime(),displacement_m=displacement,COM_displacement_m=(1000*displacement[0]+2000*displacement[1])/3000,
        extension_m=train['couplers'][0].GetLength()-.5,coupler_force_N=train['couplers'][0].GetForce())


def test_unavailable_backend_is_explicit_no_fallback(monkeypatch):
    def unavailable():raise r.BackendUnavailable('fixture absent native library')
    monkeypatch.setattr(r,'_chrono',unavailable);r.solver_info.cache_clear()
    try:
        assert r.solver_info()==dict(available=False,backend='Project Chrono',reason='fixture absent native library',fallback=False)
        with pytest.raises(r.BackendUnavailable):r.run_benchmark(scenario(),[30000.]*6)
    finally:r.solver_info.cache_clear()


def test_real_native_package_identity(native):
    assert native['version']=='10.0.0' and native['fallback'] is False
    assert native['package_url'].startswith('https://conda.anaconda.org/projectchrono/')
    assert '_core.so' in native['native_binary_sha256'] and len(native['native_binary_sha256']['_core.so'])==64


def test_gravity_native_converges_to_independent_ballistic_solution(native):
    a,b=gravity(.002),gravity(.001);exact=3-.5*9.80665
    assert b['vz_m_s']==pytest.approx(-9.80665,abs=1e-9)
    assert abs(b['z_m']-exact)<.006 and abs(b['z_m']-exact)<.51*abs(a['z_m']-exact)


def test_unequal_mass_native_coupler_matches_independent_two_body_solution(native):
    a,b=coupled(.002),coupled(.001);t=2.;q_eq=1000*2000/(10000*3000);rate=.5*1000*(1/1000+1/2000);omega=math.sqrt(10000*(1/1000+1/2000)-rate**2)
    exact=q_eq*(1-math.exp(-rate*t)*(math.cos(omega*t)+rate/omega*math.sin(omega*t)))
    assert b['COM_displacement_m']==pytest.approx(.5*(1000/3000)*t*t,abs=.001)
    assert b['extension_m']==pytest.approx(exact,abs=.0002)
    assert abs(b['extension_m']-exact)<abs(a['extension_m']-exact)
    assert abs(b['coupler_force_N'])>100  # a real load-transfer transient, not equal-force cancellation


@pytest.mark.parametrize('change',[{'mode':'evidence'},{'mode':'exploration'},{'cars':5},{'candidate_id':'physical-candidate'},{'fault':{'id':'failure'}},{'unknown':1},{'scenario_id':'f'*64}])
def test_benchmark_refuses_unmodelled_scope_and_mixed_identity(change):
    s=scenario();s.update(change)
    with pytest.raises(ValueError):r.run_benchmark(s,[30000.]*6,dt_s=.01)


def test_mechanical_timestep_cannot_be_silently_overridden():
    s=scenario();s['mechanical_step_s']=.001
    with pytest.raises(ValueError,match='timesteps differ'):r.run_benchmark(s,[30000.]*6,dt_s=.01)


def test_missing_callback_provenance_refused(native):
    with pytest.raises(ValueError,match='source-bound'):r.run_benchmark(scenario(),[30000.]*6,dt_s=.01,vector_force=lambda *a:[])


@pytest.fixture(scope='module')
def trip(native):return r.run_benchmark(scenario(),[37619.,38000.,37000.,37619.,36000.,39000.],dt_s=.01)


def test_actual_six_body_trip_preserves_common_zones_work_and_terminal_state(trip):
    assert trip['state']=='completed' and trip['summary']['terminal_screen_pass']
    assert trip['summary']['actual_steps']>=12500 and len(trip['trace'])<1300
    assert trip['zones']['launch_m']==[-96.,254.] and trip['zones']['receiving_m']==[1658.5,2008.5]
    assert len(trip['final_state'])==6 and len(trip['summary']['peak_coupler_force_N'])==5
    assert max(trip['summary']['peak_coupler_force_N'])>100
    assert trip['summary']['minimum_nonzero_active_body_overlap_m']>0
    assert abs(trip['summary']['longitudinal_impulse_residual_Ns'])<1e-3
    assert trip['trace'][-1]['time_s']==pytest.approx(125.,abs=1e-8)
    assert trip['physical_accepted'] is False and trip['engineering_qualified'] is False
    assert not trip['timestep_convergence']['executed']
    assert any('magnetic' in x for x in trip['unresolved'])


def test_trace_never_allocates_force_to_car_outside_common_station_zone(trip):
    for frame in trip['trace']:
        if frame['phase'] not in ('launch','receiving'):continue
        zone=trip['zones']['launch_m' if frame['phase']=='launch' else 'receiving_m']
        for car in frame['cars']:
            if car['station_force_N']:assert r._overlap(car['position_m'][0],17.,zone)>0


def test_refinement_comparison_rejects_different_vehicle(trip):
    changed=dict(trip,inputs=dict(trip['inputs'],vehicle_id='different'),dt_s=.005)
    with pytest.raises(ValueError):r.compare_timesteps(trip,changed)
