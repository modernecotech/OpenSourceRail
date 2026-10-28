"""Synthetic method controls, never supplier or available propulsion evidence."""
from copy import deepcopy
from math import sqrt
import pytest

from engineering.design_search import system_motion as retained
from engineering.design_search.tests.test_system_motion import bundle, case, force_map, seal
from engineering.railway_completion import motion
from engineering.railway_completion import FLAGS
from engineering.station_rail.common import identity, digest


def method_gate(b,s,m):
    value=dict(schema='osr-wheel-operating-admission/1',admitted=True,evidence_ready=True,
        test_only=True,candidate_id=b['candidate_id'],bundle_definition_id=b.get('definition_id'),
        motor_component_id=b['propulsion_component_id'],scenario_id=s['scenario_id'],
        map_evaluation_id=m['evaluation_id'],reasons=[],scope='Synthetic numerical method fixture only',**FLAGS)
    value['admission_id']=identity(value)
    return value


def updated_case(b,**changes):
    value=case(b);value.update(changes)
    value['scenario_id']=identity({k:v for k,v in value.items() if k!='scenario_id'})
    return value


def test_constant_force_exact_solution_and_energy_match_independent_arithmetic():
    b=bundle();s=case(b);m=force_map(b,s)
    result=motion.forward(b,m,s,admission=method_gate(b,s,m))
    assert result['state']=='destination-boundary'
    assert result['final_position_m']==pytest.approx(100.,abs=1e-8)
    assert result['final_speed_m_s']==pytest.approx(sqrt(20.),abs=1e-8)
    assert result['elapsed_s']==pytest.approx(sqrt(2000.),abs=1e-8)
    assert abs(result['energy_residual_J'])<1e-6 and abs(result['electrical_work_residual_J'])<1e-6
    assert result['test_only'] and result['available_motor_map_id'] is None
    assert all(result[key] is False for key in FLAGS)


@pytest.mark.parametrize('windows,loss', [([[0.,100.]],0.),([[0.,10.]],0.),([[0.,100.]],10.)])
def test_other_valid_cases_reproduce_retained_dynamics_exactly(windows,loss):
    b=bundle();s=updated_case(b,powered_windows=windows);m=force_map(b,s,loss=loss)
    actual=motion.forward(b,m,s,admission=method_gate(b,s,m))
    expected=retained.forward(b,m,s,allow_synthetic=True)
    for key in ('state','final_position_m','final_speed_m_s','elapsed_s','temperature_C','trace',
                'electrical_energy_J','magnetic_loss_energy_J','mechanical_propulsion_work_J',
                'friction_brake_heat_J','energy_residual_J','electrical_work_residual_J'):
        assert actual[key]==expected[key]


def test_partial_window_launch_then_coast_has_no_hidden_force_or_energy():
    b=bundle();s=updated_case(b,powered_windows=[[0.,10.]]);m=force_map(b,s)
    result=motion.forward(b,m,s,admission=method_gate(b,s,m))
    assert result['final_speed_m_s']==pytest.approx(sqrt(2.),abs=1e-7)
    assert result['mechanical_propulsion_work_J']==pytest.approx(1000.,abs=1e-5)
    assert result['elapsed_s']==pytest.approx(sqrt(200.)+90/sqrt(2.),abs=1e-7)
    assert all(r['thrust_N_train']==0 for r in result['trace'] if r['position_m']>10+1e-6)


def test_zero_current_with_positive_drag_stalls_at_origin_without_negative_lookup(monkeypatch):
    b=bundle();s=updated_case(b,current_command_A=0.,initial_current_A=0.,rolling_coefficient=.0025,
                            bearing_N_per_car=50.,aero_N_s2_m2_per_car=1.8)
    m=force_map(b,s);positions=[];sample=motion.sample_map
    def capture(force_map,**state):
        positions.append(state['position_m'])
        return sample(force_map,**state)
    monkeypatch.setattr(motion,'sample_map',capture)
    result=motion.forward(b,m,s,admission=method_gate(b,s,m))
    assert result['state']=='stalled'
    assert result['final_position_m']==result['final_speed_m_s']==result['elapsed_s']==0
    assert result['trace']==[] and result['energy_residual_J']==0
    assert positions and all(x==0. for x in positions) and len(positions)<10


def test_insufficient_nonzero_force_does_not_invent_a_hold_or_current_ramp():
    b=bundle();s=updated_case(b,rolling_coefficient=.0025,bearing_N_per_car=50.)
    m=force_map(b,s,force=5.)
    result=motion.forward(b,m,s,admission=method_gate(b,s,m))
    assert result['state']=='stalled' and result['final_position_m']==0
    assert result['elapsed_s']==0 and result['trace']==[]


@pytest.mark.parametrize('voltage',[-1e6,751.])
def test_kernel_rejects_voltage_magnitude_even_with_a_trusted_method_gate(voltage):
    b=bundle();s=case(b);m=force_map(b,s)
    for row in m['samples']:row['voltage_V']=voltage
    m=seal(m)
    result=motion.forward(b,m,s,admission=method_gate(b,s,m))
    assert result['state']=='electrical-limit' and result['elapsed_s']==0


def test_unadmitted_map_never_reaches_solver():
    b=bundle();s=case(b)
    result=motion.forward(b,None,s,admission=dict(admitted=False,reasons=['Missing authenticated evidence']))
    assert result['execution']=='not-run'
    with pytest.raises(ValueError,match='Trusted operating admission'):
        motion.forward(b,force_map(b,s),s,admission=dict(admitted=True))


@pytest.mark.parametrize('field,value', [('candidate_id','a'*64),('scenario_id','b'*64),('map_evaluation_id','c'*64)])
def test_resealed_gate_cannot_be_reused_for_another_map_or_context(field,value):
    b=bundle();s=case(b);m=force_map(b,s);gate=method_gate(b,s,m)
    gate[field]=value;gate['admission_id']=identity({k:v for k,v in gate.items() if k!='admission_id'})
    with pytest.raises(ValueError,match='Admission belongs'):
        motion.forward(b,m,s,admission=gate)


def test_changed_map_bytes_cannot_inherit_an_already_admitted_map_identity():
    b=bundle();s=case(b);m=force_map(b,s);gate=method_gate(b,s,m)
    changed=force_map(b,s,force=110.)
    with pytest.raises(ValueError,match='Admission belongs'):
        motion.forward(b,changed,s,admission=gate)
    m['samples'][0]['thrust_N_train']=5.
    with pytest.raises(ValueError,match='content identity'):
        motion.forward(b,m,s,admission=gate)


def test_retained_ancestor_remains_byte_identical():
    assert digest(retained.__file__)==motion.ANCESTOR_SHA256
