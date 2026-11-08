"""A completed numerical run need not pass its declared journey envelope."""
from copy import deepcopy
import pytest
from engineering.railway_project import motion,assessment
from test_railway_project_motion import project,scenario
from test_railway_project_civil import seal


def control():
    q,m=motion.compile_case(*project(),0,scenario())
    r=dict(id=q['id'],candidate_id=q['candidate_id'],native_input_id=m['native_input_id'],native_receipt_id='a'*64,
        control=dict(policy_id=q['control']['policy_id'],bounds_valid=True,end_of_authority_violated=False,minimum_stopping_margin_m=.01),
        normal_numerical_arrival=True,rollback_detected=False,energy_residual_j=1e-6,grid_energy_j=1e7,
        brake_heat_j=1e7,grade_work_j=1e6,final_kinetic_energy_j=0.,maximum_speed_m_s=q['speed_cap_m_s'],
        maximum_absolute_jerk_m_s3=.4,maximum_mechanical_power_w=1e6,maximum_grid_power_w=1.5e6,
        physical_accepted=False,engineering_accepted=False,operating_release=False,admitted_operating_map=False)
    return q,m,seal(r)


def assess(q,m,r):
    return assessment.journey(q,m,r,speed_numerical_allowance_m_s=.01,energy_relative_tolerance=1e-6,
        stopping_margin_numerical_allowance_m=1e-6)


def test_unqualified_control_keeps_execution_screen_and_acceptance_separate():
    r=assess(*control())
    assert r['execution']=='completed' and r['model_journey_screen_passed']
    assert r['physical_accepted'] is False and r['protected_service_qualified'] is False
    assert r['thermal_evidence']=='not modelled'


def test_arrival_and_valid_input_flags_cannot_hide_overspeed_or_negative_stopping_margin():
    q,m,r=control();r['maximum_speed_m_s']+=4.;r['control']['minimum_stopping_margin_m']=-.4;seal(r)
    out=assess(q,m,r)
    assert out['execution']=='completed' and not out['model_journey_screen_passed']
    assert 'declared_speed_envelope' in out['failed_checks'] and 'stopping_bound_margin' in out['failed_checks']
    changed=deepcopy(r);changed['native_input_id']='b'*64;seal(changed)
    with pytest.raises(ValueError,match='Mixed'):
        assess(q,m,changed)
