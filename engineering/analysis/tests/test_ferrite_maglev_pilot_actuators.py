"""Actuator inversion, physical phase and actual fault-hold controls."""
from copy import deepcopy
import math
import numpy as np
import pytest
from engineering.ferrite_maglev import pilot_actuators as a, pilot_product as p, launch_optimisation as l

def test_support_force_inversion_depends_on_physical_gap():
    gaps=np.array([.004,.008,.012]);demand=np.array([10000.,10000.,10000.]);i=a.lift_current(demand,gaps);f,b=a.lift_force(i,gaps)
    assert f==pytest.approx(demand) and i[0]<i[1]<i[2]
    f2,_=a.lift_force(i,np.array([.005,.009,.013]));assert all(f2<demand)

def test_local_group_phase_is_not_whole_train_phase_spread():
    profile=l.reference_profile();cfg=p.configuration_profile();centres=-8.5-np.arange(6)*17.5+np.array([0,.002,.004,.006,.008,.010]);velocity=np.full(6,10.);gaps=np.full((6,24),.008)
    groups=l.group_geometry(profile,7);f,d=a.powered_group_state(groups,centres,velocity,gaps,np.zeros(6),100000.,'departure',a.load())
    assert any(x['phase_error_mdeg']>0 for x in f)
    assert len(d)==14 and all(len(x)==8 for x in d)
    assert max(x['phase_error_mdeg'] for x in f)>5000
    short=l.group_geometry(profile,a.load()['groups_per_direction']);f2,d2=a.powered_group_state(short,centres,velocity,gaps,np.zeros(6),100000.,'departure',a.load())
    assert len(d2)==140 and 4440<max(x['phase_error_mdeg'] for x in f2)<5000

@pytest.fixture(scope='module')
def binary():return a.build_bridge()[0]

@pytest.fixture(scope='module')
def short_run(binary):return a.simulate(binary,duration_s=.04)

def test_actual_rust_current_kernel_is_in_physical_force_path(short_run):
    r=short_run
    assert r['actual_rust_current_kernel'] and r['completed_moving_steps']>0
    assert r['copper_heat_j']>0 and r['extrema']['peak_lift_current_a']>60
    assert r['configuration']['controlled_aw3_kg']>28000
    assert r['extrema']['rl_energy_residual_max_j']<1e-5
    assert not r['screens']['continuous_lift_current']
    assert a.validate_run(r)

@pytest.mark.parametrize('field',['copper_heat_j','peak_flux_t','trace','witness','end-gap'])
def test_executed_window_and_trace_cannot_be_replaced_by_passing_summary(short_run,field):
    r=deepcopy(short_run)
    if field=='copper_heat_j':r[field]=1.;r['rl_energy_residual_j']=r['dc_signed_input_j']-1.-r['emf_transfer_j']-r['current_field_energy_change_j']
    elif field=='peak_flux_t':r['extrema'][field]=.1
    elif field=='trace':r['trace']=[]
    elif field=='witness':r['window_witness']['rows'][0][13]=0.
    else:r['end_state']['physical_gap_m'][0][0]+=.001
    with pytest.raises(ValueError):a.validate_run(r)

@pytest.mark.parametrize('fault',list(a.FAULTS))
def test_actual_faults_hold_and_never_authorise_outputs(binary,fault):
    r=a.simulate(binary,duration_s=.04,fault=fault,fault_time_s=.02,assumptions={**a.load(),'settle_s':.02})
    assert r['failure'] is not None and not r['study_pass']
    assert r['completed_moving_steps']<r['planned_moving_steps']
    assert r['fault_injected_at_s'] is not None
    assert '('+a.FAULTS[fault]+')' in r['fault_observed']
    assert not r['physical_output_authorised']

def test_equal_copper_repair_counts_stock_mass_and_changes_RL():
    c,d=a.variant_configuration('steel-wall-004','equal-copper-100t8mm2');base=p.configuration_profile()
    assert c['controlled_aw3_kg']-base['controlled_aw3_kg']==pytest.approx(247.05264059)
    assert c['body']['longitudinal_stiffness_n_m']==pytest.approx(39744180.43564447)
    old=a.drive.support();new=a.drive.support(d)
    assert new['copper_kg_per_car']==pytest.approx(old['copper_kg_per_car'])
    assert new['coil']['resistance_hot_ohm']==pytest.approx(4*old['coil']['resistance_hot_ohm'])
    assert new['lift_inductance_hypothesis_h']==pytest.approx(4*old['lift_inductance_hypothesis_h'])

def test_rewinding_cannot_relax_current_density_or_copper_heat():
    c,old=a.variant_configuration('steel-wall-004','retained-50t16mm2');_,new=a.variant_configuration('steel-wall-004','equal-copper-100t8mm2')
    current=a.lift_current(np.array([12000.]),np.array([.010]),old['support'])[0]
    rewound=a.lift_current(np.array([12000.]),np.array([.010]),new['support'])[0]
    assert rewound/current==pytest.approx(.5)
    assert current/16==pytest.approx(rewound/8)
    assert current**2*a.drive.support(old)['coil']['resistance_hot_ohm']==pytest.approx(rewound**2*a.drive.support(new)['coil']['resistance_hot_ohm'])
    assert rewound/8>a.load()['baseline_wire_current_density_a_mm2']

def test_final_candidate_counts_larger_mean_turn_pack_cooling_and_load():
    cfg=a.selected_configuration();_,d=a.variant_configuration(a.load()['preferred_body_variant'],a.load()['preferred_winding_variant']);s=a.drive.support(d);bay=a.candidate_packaging(a.load()['preferred_winding_variant'])
    assert d['support']['mean_turn_length_m']==pytest.approx(.70)
    assert s['copper_kg_per_car']==pytest.approx(1264.4352)
    assert s['packing_fraction']<.55 and cfg['controlled_aw3_kg']==pytest.approx(30382.35065664347)
    assert cfg['magnetic']['additional_cooling_allowance_kg']==120
    assert cfg['bay_service_variant']['changed_hardware']['additional_stock_mass_kg_per_car']==pytest.approx(106.01367954281218)
    assert 'steel tubes' in cfg['body']['stiffness_role']
    assert cfg['load_reassessment']['controlled_mass_ratio']>1.15
    power=cfg['support_power_stage']
    assert power['rated_bus_v']==192 and power['continuous_current_a']==60
    assert sum(x['count_per_car']*x['mass_kg_each'] for x in power['components'])==power['additional_mass_kg_per_car']==54
    assert sum(x['count_per_car']*x['unquoted_cost_usd_each'] for x in power['components'])==power['additional_unquoted_cost_usd_per_car']==26400
    assert power['additional_auxiliary_kw_per_car']==1
    assert not bay['internal_bound_intersections'] and bay['path']['clear_under_declared_box_bounds']

def test_actual_pilot_profile_rounded_up_and_140groups_have_local_references():
    cfg=a.selected_configuration();profile=a.motion_profile(cfg);groups=l.group_geometry(profile,a.load()['groups_per_direction'])
    assert profile['inputs']['distance_m']==pytest.approx(2013.884567)
    assert profile['inputs']['runtime_s']==140.417
    assert len(groups)==140 and max(g['length_m'] for g in groups)==5.
    assert max(g['length_m'] for g in groups)<17.5-12.


def test_last_updated_gap_violation_is_checked_before_completion(binary,monkeypatch):
    original=a.moving.MovingGuideway
    class FinalPoseFault(original):
        def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.advances=0
        def advance(self,*args,**kwargs):
            result=super().advance(*args,**kwargs);self.advances+=1;return result
        def displacement(self,*args,**kwargs):
            result=super().displacement(*args,**kwargs)
            return result+.02 if self.advances==40 else result
    monkeypatch.setattr(a.moving,'MovingGuideway',FinalPoseFault)
    r=a.simulate(binary,duration_s=.02,assumptions={**a.load(),'settle_s':.02},body_variant='steel-wall-004',winding_variant='higher-copper-120t20mm2')
    assert r['completed_moving_steps']==r['planned_moving_steps']==20
    assert r['failure']=='independent post-step physical gap outside envelope'
    assert not r['screens']['gap'] and not r['screens']['completed'] and not r['study_pass']
    assert r['end_state']['last_outer_tick']==40
    assert np.min(r['end_state']['physical_gap_m'])<0

def test_gap_flux_does_not_close_core_window_geometry_hold():
    cfg,d=a.variant_configuration('steel-wall-004','higher-copper-120t20mm2');hold=a.magnetic_geometry_hold(d)
    assert hold['state']=='hold' and hold['assumed_gap_pole_area_m2']==.025
    assert hold['winding_inner_aperture_m2']==pytest.approx(.0096)
    assert hold['pole_to_window_area_ratio']>2.6 and hold['core_neck_area_m2'] is None


def test_normal_wrench_correction_cancels_force_roll_and_pitch():
    wrench=np.array([[1234.,567.,-8910.]]*6)
    correction=a.normal_force_correction(wrench)
    assert correction.shape==(6,24)
    assert correction@a.NORMAL_MAP.T==pytest.approx(-wrench,abs=1e-9)
    assert np.all(a.normal_wrench_observer(None,12.,.001)==0)

@pytest.mark.parametrize('bad',['missing-case','failed-case','force-overload','partial-case','missing-fault','failed-fault'])
def test_all_applicable_full_cases_and_exact_controls_are_required(bad):
    cfg=a.selected_configuration()['configuration_sha256'];runtime=a.motion_profile(a.selected_configuration())['inputs']['runtime_s']
    cases=[dict(configuration_sha256=cfg,start_time_s=0.,requested_duration_s=runtime,profile={'inputs':{'runtime_s':runtime}},completed_moving_steps=140417,planned_moving_steps=140417,study_pass=True,estimator_scale=scale,extrema={'peak_module_force_n':10000.}) for scale in a.load()['normal_feedforward_scales']]
    controls=[dict(fault=fault,expected_hold=True,run={'configuration_sha256':cfg}) for fault in a.FAULTS]
    result=dict(full_estimator_cases=cases,controls=controls)
    assert a.full_eligible(result)
    if bad=='missing-case':cases.pop()
    elif bad=='failed-case':cases[0]['study_pass']=False
    elif bad=='force-overload':cases[-1]['extrema']['peak_module_force_n']=20000.1
    elif bad=='partial-case':cases[1]['completed_moving_steps']-=1
    elif bad=='missing-fault':controls.pop()
    else:controls[-1]['expected_hold']=False
    assert not a.full_eligible(result)

def test_candidate_changed_collector_metadata_matches_actual_dimensions():
    value=a.candidate_packaging(a.load()['preferred_winding_variant'])['definition']
    wall=next(p for p in value['retained_parts'] if '/detachable-bay' in p['id'])
    assert wall['volume_m3']==pytest.approx(a.product.models.volume(wall))
    assert wall['volume_rederived_from_changed_shape']

@pytest.fixture(scope='module')
def rust_coupled_run(binary):
    return a.simulate(binary,duration_s=.02,body_variant=a.load()['preferred_body_variant'],winding_variant=a.load()['preferred_winding_variant'])

def test_real_rust_observer_is_in_the_coupled_current_path(rust_coupled_run):
    r=rust_coupled_run;o=r['observer_execution']
    assert o['backend']=='rust-cdylib' and o['successful_calls']==2020
    assert r['screens']['rust_normal_observer'] and not o['physical_output_authorised']
    assert o['maximum_force_difference_n']<1e-7 and o['maximum_correction_difference_n']<1e-7
    assert a.validate_run(r)

@pytest.mark.parametrize('mutation',['calls','artifact','agreement'])
def test_observer_execution_receipt_cannot_be_replaced(rust_coupled_run,mutation):
    r=deepcopy(rust_coupled_run)
    if mutation=='calls':r['observer_execution']['successful_calls']=0
    elif mutation=='artifact':r['observer_execution']['library_sha256']='unknown'
    else:r['observer_execution']['maximum_force_difference_n']=1.
    with pytest.raises(ValueError):a.validate_run(r)

def test_vectorized_rust_observer_refuses_replayed_clock_without_state_advance():
    library,_=a.build_observer();cfg,d=a.variant_configuration(a.load()['preferred_body_variant'],a.load()['preferred_winding_variant']);profile=a.motion_profile(cfg)
    observer=a.RustNormalObserver(library,cfg,l.group_geometry(profile,a.load()['groups_per_direction']),math.pi/.25,1.)
    desired=np.full((6,24),12400.)
    observer.step(1,desired,None,math.pi/.25,.001)
    saved=bytes(observer.input.state)
    with pytest.raises(RuntimeError):observer.step(1,desired,None,math.pi/.25,.001)
    assert bytes(observer.input.state)==saved and observer.calls==1
