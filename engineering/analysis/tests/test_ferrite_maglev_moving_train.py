"""Independent conservation controls and actual moving six-car Rust feedback."""
from copy import deepcopy
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from engineering.ferrite_maglev import moving_train as moving,station


@pytest.fixture(scope='module')
def bridge():return moving.build_bridge()[0]


def candidate():
    a=deepcopy(moving.load());s=a['beam_section_m'];s['depth']=2.2
    a.update(runtime_s=a['candidate_runtime_s'],acceleration_m_s2=a['candidate_acceleration_m_s2'],coupler_stiffness_n_m=a['candidate_coupler_stiffness_n_m'])
    a['beam_vertical_inertia_m4']=moving.model.section(s['width'],s['depth'],s['web'],s['flange'])['vertical_i_m4']
    a['guideway_line_mass_kg_m']=moving.geometry.guideway_quantities(25.,**s)['total_line_mass_kg_m']
    return a


def test_trajectory_sampling_closes_distance_velocity_and_coast_force():
    t=station.trajectory(runtime_s=100.)
    final=moving.trajectory_at(t,100.)
    assert final['position_m']==pytest.approx(1000.,abs=1e-5)
    assert final['speed_m_s']==pytest.approx(0.,abs=1e-8)
    start=t['phases']['launch']['duration_s'];coast=moving.trajectory_at(t,start+5.)
    assert coast['phase']=='coast' and coast['motor_force_n']==0.
    h=1e-4
    derivative=(moving.trajectory_at(t,start+5+h)['position_m']-moving.trajectory_at(t,start+5-h)['position_m'])/(2*h)
    assert derivative==pytest.approx(coast['speed_m_s'],rel=1e-7)
    for boundary in (start,start+t['phases']['coast']['duration_s']):
        left=moving.trajectory_at(t,boundary-1e-7);right=moving.trajectory_at(t,boundary+1e-7)
        assert abs(left['position_m']-right['position_m'])<1e-5
        assert abs(left['speed_m_s']-right['speed_m_s'])<1e-6


def test_moving_mode_projection_conserves_virtual_work_and_joint_displacement():
    a=moving.load();beam=moving.MovingGuideway(a)
    random=np.random.default_rng(2);beam.velocity[:]=random.normal(size=beam.velocity.shape)
    x=random.uniform(-100,100,144);forces=random.uniform(1.,10000.,144)
    projected,error=beam.project(x,forces)
    assert error<1e-12
    indices,shape=beam.sample(x)
    independent=sum(float(forces[i]*(shape[i]@beam.velocity[indices[i]])) for i in range(144))
    assert float(np.sum(projected*beam.velocity))==pytest.approx(independent,rel=1e-12)
    beam.q[:]=random.normal(size=beam.q.shape)
    for joint in (-25.,0.,25.,50.):
        assert abs(beam.displacement(np.array([joint]))[0])<1e-12
        assert abs(np.diff(beam.displacement(np.array([joint-1e-9,joint+1e-9])))[0])<1e-8


def test_chain_internal_forces_and_undamped_energy_are_conserved():
    chain=moving.CouplerChain(26200.,100e6,0.,.005)
    chain.u[:2]=[.001,-.001];energy=chain.energy();momentum=chain.velocity.sum()
    for _ in range(300):
        r=chain.step(np.zeros(6))
        assert abs(r['internal_net_force_n'])<1e-7
        assert abs(r['energy_residual_j'])<1e-9
    assert chain.energy()==pytest.approx(energy,rel=1e-11)
    assert chain.velocity.sum()==pytest.approx(momentum,abs=1e-12)


def test_chain_damping_removes_energy_and_accounts_for_it():
    chain=moving.CouplerChain(26200.,100e6,200000.,.005)
    chain.u[:2]=[.001,-.001];initial=chain.energy();loss=0.
    for _ in range(300):
        r=chain.step(np.zeros(6));loss+=r['damping_j']
        assert abs(r['energy_residual_j'])<1e-9
    assert chain.energy()<initial/10
    assert initial-chain.energy()==pytest.approx(loss,rel=1e-10)


def test_independent_closed_form_moving_force_and_refinement():
    controls=moving.numerical_controls()
    for key in ('static_point_load','force_projection_virtual_power','support_boundary_continuity',
                'independent_moving_load_solution','moving_load_refines','coupler_energy_conservation','coupler_internal_momentum'):
        assert controls[key] is True
    coarse,fine=controls['moving_load_refinement']
    assert fine['maximum_error']<coarse['maximum_error']/3
    assert coarse['mesh_elements']==fine['mesh_elements']==60
    assert coarse['retained_modes']==fine['retained_modes']==1


def test_actual_rust_six_car_gravity_replay_and_gap_guards(bridge):
    controls=moving.rust_negative_controls(bridge,moving.load())
    assert controls['gravity_equilibrium'] and controls['replayed_frame_rejected'] and controls['out_of_envelope_gap_rejected']
    assert controls['physical_output_authorised'] is False


def test_actual_moving_feedback_crosses_spans_and_integrates_car_couplers(bridge):
    result=moving.simulate(bridge,assumptions=candidate(),start_time_s=12.,duration_s=2.)
    assert result['study_pass'],result['failure']
    assert result['module_span_boundary_crossings']>100
    assert .003<=result['minimum_gap_m']<result['maximum_gap_m']<=.013
    assert result['peak_coupler_force_n']>1000.
    assert result['peak_coupler_extension_m']>0.
    assert result['coupler_internal_net_force_max_n']<1e-7
    assert result['coupler_step_energy_residual_max_j']<1e-7
    assert result['load_projection_virtual_power_relative_error']<1e-10
    assert result['longitudinal_energy']['relative_residual']<1e-5
    assert all(len(row['car_centres_m'])==6 and len(row['body_down_roll_pitch'])==6 for row in result['trace'])
    assert result['physical_output_authorised'] is False


def test_disconnecting_actual_guideway_feedback_does_not_pass(bridge):
    result=moving.simulate(bridge,duration_s=.1,feedback=False)
    assert not result['study_pass'] and result['failure']


def test_moving_refinement_on_the_same_initialized_window(bridge):
    a=candidate();coarse=moving.simulate(bridge,assumptions=a,start_time_s=20.,duration_s=.5)
    fine=moving.simulate(bridge,assumptions=a,start_time_s=20.,duration_s=.5,step_s=.0025)
    assert coarse['study_pass'] and fine['study_pass']
    assert max(abs(coarse[k]-fine[k]) for k in ('minimum_gap_m','maximum_gap_m'))<a['refinement_gap_tolerance_m']


@pytest.mark.parametrize('bias',[-.0005,.0005])
def test_actual_rust_sensing_bias_retains_independent_physical_gap(bridge,bias):
    a=candidate();a.update(sensor_bias_m=bias,beam_modulus_pa=a['beam_modulus_pa']*.85)
    result=moving.simulate(bridge,assumptions=a,start_time_s=12.,duration_s=.5)
    assert result['study_pass'],result['failure']
    assert all(row['minimum_sensed_gap_m']-row['minimum_gap_m']==pytest.approx(bias,abs=1e-12)
        and row['maximum_sensed_gap_m']-row['maximum_gap_m']==pytest.approx(bias,abs=1e-12) for row in result['trace'])


def test_physical_gap_guard_rejects_bias_that_actual_rust_sensing_cannot_see(bridge):
    a=moving.physical_guard_probe_assumptions()
    result=moving.simulate(bridge,assumptions=a,duration_s=20.)
    assert not result['study_pass']
    assert result['failure']=='independent physical gap outside envelope'
    assert result['minimum_gap_m']<a['gap_minimum_m']
    assert result['minimum_gap_m']+a['sensor_bias_m']>a['gap_minimum_m']
    assert result['completed_moving_steps']>0
    assert moving.physical_guard_counterexample_passed(result)


def test_initial_rust_fallback_cannot_satisfy_independent_moving_physical_guard(bridge):
    a=moving.physical_guard_probe_assumptions();s=a['beam_section_m'];s['depth']=1.8
    a['beam_vertical_inertia_m4']=moving.model.section(s['width'],s['depth'],s['web'],s['flange'])['vertical_i_m4']
    a['guideway_line_mass_kg_m']=moving.geometry.guideway_quantities(25.,**s)['total_line_mass_kg_m']
    result=moving.simulate(bridge,assumptions=a,duration_s=.1)
    assert not result['study_pass'] and result['completed_moving_steps']==0
    assert 'rejected frame' in result['failure']
    assert not moving.physical_guard_counterexample_passed(result)


@pytest.mark.parametrize('kwargs',[{'duration_s':0.},{'step_s':0.},{'start_time_s':-1.},{'feedback':'yes'}])
def test_invalid_moving_controls_fail_before_opening_a_bridge(bridge,kwargs):
    with pytest.raises(ValueError):moving.simulate(bridge,**kwargs)
