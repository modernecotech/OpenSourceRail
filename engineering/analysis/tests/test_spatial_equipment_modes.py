from copy import deepcopy
from pathlib import Path
import sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.civil_exploration.variant_compiler import compile_variant
from engineering.civil_exploration.spatial_vehicle import SpatialVehicle,run_spatial
from engineering.integration_programme.joints import battery_mount
from engineering.integration_programme.flexible_vehicle import FlexibleVehicle


@pytest.fixture(scope='module')
def package():return compile_variant()

def mounts(package):
    group=battery_mount(package['battery'],dict(diameter_m=.012,grip_m=.018,youngs_pa=210e9))
    return {c['id']+'/battery':dict(stiffness_si=group['stiffness_si'],damping_si=np.zeros((6,6)).tolist(),motion_bounds_si=[[-.01,.01]]*6,basis='geometry-specific engaged elastic shank research; preload/member/thread/fatigue limits open') for c in package['model']['family_definition']['cars']}


def test_equipment_mass_is_removed_from_body_and_reactions_still_balance(package):
    m=package['model'];cfg=package['spatial_configuration'];rigid=SpatialVehicle(m,cfg['joint_laws']);separate=SpatialVehicle(m,cfg['joint_laws'],equipment_mounts=mounts(package))
    assert separate.total_mass==pytest.approx(rigid.total_mass,rel=1e-13)
    assert separate.groups['car-1/battery']['mass']==pytest.approx(package['battery']['properties']['mass_kg'])
    assert separate.groups['car-1']['mass']+separate.groups['car-1/battery']['mass']==pytest.approx(rigid.groups['car-1']['mass'])
    assert sum(c['static_n'] for c in separate.contacts)==pytest.approx(separate.total_mass*9.81,rel=1e-12)
    assert len(separate.joints)==len(rigid.joints)+6
    assert all(c['static_n']>0 for c in separate.contacts)


def test_flexible_modes_mount_loads_and_actuation_are_in_the_actual_monolithic_solve(package):
    cfg=deepcopy(package['spatial_configuration']);cfg['equipment_mounts']=mounts(package)
    cfg['flexible_vehicle']=dict(ei_nm2=3e8,mode_count=2,damping_ratio=.02)
    cfg['actuator_contract']=dict(basis='simulation test callback; no target or calibration',physical_validation=False)
    calls=[]
    def callback(state):
        calls.append(deepcopy(state))
        return dict(wheel_torque_nm={r['id']:10. if r['powered'] else 0. for r in state['wheelsets']},evidence=dict(kind='synthetic verified test callback'))
    r=run_spatial(package['model'],cfg,dt=.005,duration_s=.01,deck_mesh=2,rail_step=2.,actuator_callback=callback)
    assert len(calls)==2 and r['actuator_callback_executed'] and r['modal_truncation_used']
    assert not r['structure_modal_truncation_used'] and not r['physical_validation']
    assert all(len(h['flexible_body_observations'])==18 for h in r['history'])
    assert any(np.linalg.norm(x['force_moment_si'])>0 for h in r['history'] for x in h['joints'] if x['joint']=='car-1/battery-retention')
    assert all(h['actuator_execution'][0]['response']['evidence']['kind']=='synthetic verified test callback' for h in r['history'])
    assert all(x['reference']=='flexible transfer relative to rigid body' for x in r['history'][0]['flexible_body_observations'])


def test_invalid_equipment_scope_is_rejected_without_changing_definition(package):
    m=package['model'];cfg=package['spatial_configuration']
    with pytest.raises(ValueError,match='equipment instance'):SpatialVehicle(m,cfg['joint_laws'],equipment_mounts={'car-1/body':next(iter(mounts(package).values()))})


def test_intrinsic_modal_preload_cancels_joint_static_modal_force(package):
    cfg=package['spatial_configuration'];vehicle=FlexibleVehicle(package['model'],cfg['joint_laws'],equipment_mounts=mounts(package),mode_count=2)
    from engineering.civil_exploration.spatial_structure import Route
    _,_,_,(_,plans)=vehicle.matrices(Route(cfg['route']),0.,0.)
    forces=vehicle.intrinsic_preload.copy()
    for p in plans:forces+=p['J'].T@p['joint']['K']@p['joint']['preload_extension']
    assert np.max(np.abs(forces[vehicle.rigid_size:]))<1e-7


def test_cross_product_and_constant_alignment_match_independent_kinematics():
    from engineering.civil_exploration.spatial_structure import cross3,Route
    rng=np.random.default_rng(14)
    for _ in range(30):
        a=rng.normal(size=3);b=rng.normal(size=3)
        assert cross3(a,b)==pytest.approx(np.cross(a,b),rel=1e-14,abs=1e-14)
    for grade in (0.,.05,-.05):
        route=Route(dict(radius_m=0.,cant_rad=0.,cant_start_m=0.,cant_end_m=1.,grade_rad=grade,basis='analytical constant-alignment verification'))
        direction=np.array([np.cos(grade),0.,np.sin(grade)]);normal=np.array([-np.sin(grade),0.,np.cos(grade)])
        assert route.position(12.,3.,2.)==pytest.approx(12*direction+np.array([0.,3.,0.])+2*normal,abs=1e-13)
        assert route.frame(12.)[:,0]==pytest.approx(direction,abs=1e-14)
        copy=route.frame(2.);copy[:]=0
        assert np.linalg.det(route.frame(2.))==pytest.approx(1.)
