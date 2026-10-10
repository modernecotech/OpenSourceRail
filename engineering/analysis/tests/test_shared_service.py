"""Independent passage kinematics, motion traces, ride integrals and input guards."""
from copy import deepcopy
import json
from pathlib import Path
import runpy
import sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.analysis.shared_service import passage_configuration,case_matrix,coverage,ride_diagnostics
from engineering.civil_exploration.shared_demo import demonstration
from engineering.civil_exploration.spatial_demo import configuration
from engineering.civil_exploration.spatial_vehicle import run_spatial,loaded_model
from engineering.civil_exploration.joint_laws import response
from engineering.civil_exploration.correlation import calibrate
from engineering.civil_exploration.wheel_contact import ProfilePair,profile_normal_gap,TangentialContact
from test_shared_spatial_engineering import dataset


def test_plan_starts_all_axles_before_approach_and_clears_every_axle():
    m=demonstration();cfg=configuration(m);changed,plan=passage_configuration(m,cfg,speed_m_s=15.)
    p=plan['trains'][0]
    assert p['starting_advance_m']+15*plan['duration_s']==pytest.approx(p['required_clearance_advance_m'])
    assert p['expected_complete_passage'] and plan['represented_car_count']==2 and plan['family_car_count']==6
    assert not plan['full_family_represented'] and cfg==configuration(m)


def test_braking_stop_and_acceleration_speed_limits_are_physical_kinematic_checks():
    m=demonstration();c=configuration(m)
    _,p=passage_configuration(m,c,speed_m_s=5.,acceleration_m_s2=-1.)
    assert p['trains'][0]['stopping_test'] and p['duration_s']==pytest.approx(6.)
    with pytest.raises(ValueError,match='exceeds'):passage_configuration(m,c,speed_m_s=20.,acceleration_m_s2=5.)


def test_both_tracks_keep_individual_speeds_and_arrival_offsets():
    m=demonstration();c=configuration(m);other=deepcopy(c['traffic'][0]);other.update(id='B',track=1,speed_m_s=12.,arrival_time_s=.5);c['traffic'].append(other)
    _,p=passage_configuration(m,c,speed_m_s=15.)
    assert p['duration_s']==pytest.approx(.5+(p['trains'][1]['required_clearance_advance_m']-p['trains'][1]['starting_advance_m'])/12.)


def test_case_matrix_includes_named_service_and_distress_conditions_and_fine_speed_band():
    m=demonstration();matrix=case_matrix(m,configuration(m),(10.,15.,20.),(14.,16.,.25))
    kinds={c['kind'] for c in matrix['cases']}
    assert {'normal-service','rescue','maintenance','braking','traction','alignment','distress','degraded','traffic','wear','resonance'}<=kinds
    assert len([c for c in matrix['cases'] if c['kind']=='resonance'])==9
    assert len(matrix['unexecuted_case_ids'])==len(matrix['cases']) and not matrix['engineering_released']


def fake_passage(plan):
    contacts=lambda s:[dict(train=p['train'],wheelset=w,side=side,station_m=s) for p in plan['trains'] for w in p['wheelsets'] for side in (-1,1)]
    return dict(hardware_definition_sha256=plan['hardware_definition_sha256'],configuration_sha256=plan['configuration_sha256'],within_adapter_domain=True,
        history=[dict(time_s=t,contacts=contacts(s)) for t,s in [(0.,-6.),(1.,30.),(2.,81.)]])


def test_coverage_requires_every_wheel_in_the_actual_history():
    m=demonstration();_,p=passage_configuration(m,configuration(m),speed_m_s=15.)
    r=fake_passage(p);assert coverage(r,p)['complete_passage']
    r['history'][-1]['contacts'][0]['station_m']=74.
    assert not coverage(r,p)['complete_passage']
    r=fake_passage(p);r['history'][1]['contacts'].pop()
    assert not coverage(r,p)['all_expected_contacts_recorded']


def test_short_startup_cannot_become_complete_passage_by_changing_duration_metadata():
    m=demonstration();_,p=passage_configuration(m,configuration(m),speed_m_s=15.)
    r=fake_passage(p);r['duration_s']=1000.;r['history']=r['history'][:2]
    assert not coverage(r,p)['complete_passage']


def test_ride_rms_and_vdv_match_sinusoidal_integrals_and_have_no_iso_claim():
    time=np.linspace(0.,10.,10001);amplitude=2.;frequency=2.
    history=[dict(time_s=float(t),bodies=[dict(train='A',body='car-1',acceleration_body_m_s2=[float(amplitude*np.sin(2*np.pi*frequency*t)),0.,0.],reference_point='synthetic CG')]) for t in time]
    r=ride_diagnostics(dict(history=history));row=r['body_results'][0]
    assert row['rms_xyz_m_s2'][0]==pytest.approx(amplitude/np.sqrt(2),rel=1e-8)
    assert row['vdv_xyz_m_s175'][0]==pytest.approx((10*amplitude**4*3/8)**.25,rel=1e-8)
    assert row['crest_factor_xyz'][0]==pytest.approx(np.sqrt(2)) and row['crest_factor_xyz'][1] is None
    assert not r['iso_comfort_evaluated'] and not r['physical_validation']
    history[50]['bodies']=[]
    with pytest.raises(ValueError,match='histories'):ride_diagnostics(dict(history=history))


def test_solver_retains_individual_vectors_and_callback_cannot_modify_recorded_results():
    m=demonstration();c=configuration(m);received=[]
    def observer(sample):
        received.append(sample);sample['bodies'][0]['acceleration_body_m_s2'][0]=1e12
    r=run_spatial(m,c,dt=.002,duration_s=.006,deck_mesh=2,rail_step=2.,sample_callback=observer)
    assert len(received)==3 and len(r['history'][0]['bodies'])==2
    assert r['history'][0]['bodies'][0]['acceleration_body_m_s2'][0]!=1e12
    assert np.asarray(r['history'][0]['bodies'][0]['frame_to_global']).shape==(3,3)
    assert len(ride_diagnostics(r)['body_results'])==2


def test_independent_nonlinear_curves_cannot_destroy_coupled_matrix_passivity():
    K=np.eye(6);K[0,1]=K[1,0]=.1
    law=dict(stiffness_si=K.tolist(),damping_si=np.eye(6).tolist(),force_displacement_curves=[[[-1.,-1.],[1.,1.]]]+[None]*5)
    with pytest.raises(ValueError,match='coupled'):response(law,np.zeros(6),np.zeros(6))
    law=dict(stiffness_si=np.eye(6).tolist(),damping_si=np.eye(6).tolist(),damping_curves=[[[-1.,0.],[1.,2.]]]+[None]*5)
    with pytest.raises(ValueError,match='dissipate'):response(law,np.zeros(6),np.zeros(6))


def test_calibration_rejects_relabelled_serials_as_independent_specimens(tmp_path):
    m=demonstration();data=dataset(tmp_path,m);data['tests'][1]['serial']=data['tests'][0]['serial']
    parameters=[dict(name='slope',initial=1.,minimum=0.,maximum=5.)]
    with pytest.raises(ValueError,match='relabelled'):calibrate(m,data,parameters,lambda p,t:np.asarray(t['time_s']),root=tmp_path,holdout_specimens=['B'])


def test_spatial_forward_calibration_rejects_wrong_units_and_invalid_domain(monkeypatch):
    api=runpy.run_path(str(ROOT/'tools/automation/shared-engineering-campaign.py'));fn=api['forward']
    m=demonstration();c=configuration(m)
    t=dict(time_s=[.004,.006,.008],quantity='acceleration',unit='m/s2',channel=dict(train='train-A',wheelset='car-1/bogie-1/axle-1',side=1,metric='normal_n'))
    with pytest.raises(ValueError,match='force in N'):fn(m,c,{},t,.002,2,2.)
    t.update(quantity='force',unit='N')
    monkeypatch.setitem(fn.__globals__,'run_spatial',lambda *a,**k:dict(within_adapter_domain=False,domain_exceedances=['profile overlap lost']))
    with pytest.raises(ValueError,match='outside'):fn(m,c,{},t,.002,2,2.)


def test_body_acceleration_calibration_selects_the_correct_vector_component(monkeypatch):
    api=runpy.run_path(str(ROOT/'tools/automation/shared-engineering-campaign.py'));fn=api['forward']
    fake=dict(within_adapter_domain=True,history=[dict(time_s=t,bodies=[dict(train='A',body='car-1',acceleration_body_m_s2=[1.,float(t),3.])]) for t in (.002,.004,.006)])
    monkeypatch.setitem(fn.__globals__,'run_spatial',lambda *a,**k:fake)
    t=dict(time_s=[.002,.003,.006],quantity='acceleration',unit='m/s2',channel=dict(kind='body',train='A',body='car-1',metric='acceleration_body_m_s2',axis=1))
    assert fn(demonstration(),configuration(demonstration()),{},t,.002,2,2.)==pytest.approx([.002,.003,.006])


@pytest.mark.parametrize('field,value',[('passenger_mass_kg',-1.),('mass_uncertainty_fraction',2.),('longitudinal_offset_m',100.),('passenger_mass_kg',True)])
def test_invalid_passenger_loads_are_not_coerced_into_physical_records(field,value):
    m=demonstration();case=configuration(m)['traffic'][0]['load_case'];case[field]=value
    with pytest.raises(ValueError):loaded_model(m,case)


def test_profile_gap_translation_derivative_matches_the_contact_normal_once():
    c=configuration(demonstration())['contact'];p=ProfilePair(c['wheel_profiles']['1'],c['rail_profile'],.38,115e9)
    reference=p.locate(0.);h=1e-7
    dy=(profile_normal_gap(0.,p.locate(h),reference)-profile_normal_gap(0.,p.locate(-h),reference))/(2*h)
    dz=profile_normal_gap(h,reference,reference)/h
    assert [dy,dz]==pytest.approx(reference['normal_local'][1:],rel=1e-5,abs=1e-8)


def test_sliding_return_tangents_match_independent_force_perturbations():
    state=TangentialContact();v=np.array([.1,.2]);dt=.01;N=1000.;k=1e6;mu=.3
    r=state.trial(v,dt,N,k,mu);h=1e-6
    numerical=np.column_stack([(state.trial(v+np.eye(2)[i]*h,dt,N,k,mu)['force_n']-state.trial(v-np.eye(2)[i]*h,dt,N,k,mu)['force_n'])/(2*h) for i in range(2)])
    assert numerical==pytest.approx(-r['restoring_tangent_n_m']*dt,rel=1e-6,abs=1e-6)
    dn=(state.trial(v,dt,N+h,k,mu)['force_n']-state.trial(v,dt,N-h,k,mu)['force_n'])/(2*h)
    assert dn==pytest.approx(-r['restoring_normal_derivative'],rel=1e-6,abs=1e-6)


def test_finalist_confirmation_preserves_uncertainty_loading_and_separates_refinements(monkeypatch):
    import engineering.civil_exploration.shared_search as search
    m=demonstration();c=configuration(m);calls=[]
    def forward(h,cfg,**kwargs):
        calls.append((deepcopy(h),deepcopy(cfg),kwargs))
        return dict(maximum_wheel_contact_n=100.,peak_structure_displacement_m=.01,peak_ride_acceleration_m_s2=.1,maximum_wheel_unloading=.2,within_adapter_domain=True)
    monkeypatch.setattr(search,'run_spatial',forward)
    row=dict(candidate_id='candidate',hardware=m,analysis=c,scenarios=[dict(id=name,inputs=dict(modulus_factor=E,passenger_mass_factor=mass,friction=mu))
        for name,E,mass,mu in [('nominal',1.,1.,.3),('adverse',.9,1.05,.1)]])
    r=search.confirm(row)
    assert len(calls)==6 and r['numerical_confirmation_passed']
    for start in (0,3):
        assert calls[start][2]['deck_mesh']==calls[start+1][2]['deck_mesh']
        assert calls[start+1][2]['dt']==calls[start+2][2]['dt']
        assert calls[start][1]['traffic'][0]['load_case']['id']=='uneven'
    assert calls[3][1]['traffic'][0]['load_case']['passenger_mass_kg']==pytest.approx(78.75)
    assert calls[3][1]['infrastructure_condition']['foundation_stiffness_factor']==.5
    assert calls[3][0]['bridge']['candidate']['material']['youngs_modulus_pa']==pytest.approx(m['bridge']['candidate']['material']['youngs_modulus_pa']*.9)
