"""Independent spatial/contact/material equations and evidence boundary checks."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from osr_mech.engineering_definition import fingerprint
from osr_mech.joint_design import bolt_group,definitions
from engineering.civil_exploration.shared_demo import demonstration
from engineering.civil_exploration.spatial_demo import configuration,scenarios
from engineering.civil_exploration.spatial_structure import Route,SpatialStructure,element_matrices,native_beam_benchmark
from engineering.civil_exploration.spatial_vehicle import SpatialVehicle,loaded_model,run_spatial
from engineering.civil_exploration.wheel_contact import benchmarks,hertz_coefficients,normal_force,patch,TangentialContact,ProfilePair
from engineering.civil_exploration.constitutive import concrete_state,concrete_stress,steel_return,laminate,laminate_response,cohesive,section_response,rainflow
from engineering.civil_exploration.assembled_materials import synthetic_laws,assess
from engineering.civil_exploration.joint_laws import response
from engineering.civil_exploration.joint_submodel import parse_dat,load_case
from engineering.civil_exploration.correlation import calibrate,protocols


def test_hertz_sphere_pressure_force_and_compression_match_independent_equations():
    r=benchmarks();assert r['passed'] and not r['physical_validation']
    E=115e9;R=.38;F=80000.;c=hertz_coefficients(1/R,1/R,E);p=patch(F,c)
    assert p['penetration_m']==pytest.approx((3*F/(4*E*np.sqrt(R)))**(2/3),rel=1e-9)
    assert p['maximum_pressure_pa']*2*np.pi*p['semi_axis_x_m']*p['semi_axis_y_m']/3==pytest.approx(F)
    assert normal_force(-.1,c)==0.
    assert normal_force(p['penetration_m'],c)==pytest.approx(F)


def test_stick_slip_unload_recontact_are_passive_and_trial_is_not_committed():
    state=TangentialContact();a=state.trial([.1,.2],.01,1000.,1e6,.3)
    assert np.linalg.norm(a['force_n'])==pytest.approx(300.)
    assert a['dissipation_j']>=0 and state.displacement is None
    state.commit(a);stored=a['stored_energy_j'];b=state.trial([0.,0.],.01,0.,1e6,.3)
    assert b['dissipation_j']==pytest.approx(stored) and np.linalg.norm(b['force_n'])==0
    state.commit(b);c=state.trial([0.,0.],.01,1000.,1e6,.3)
    assert c['stored_energy_j']==0 and state.dissipated_j>=stored


def test_supplied_profile_location_and_curvature_use_the_actual_arrays():
    c=configuration(demonstration())['contact'];p=ProfilePair(c['wheel_profiles']['1'],c['rail_profile'],.38,115e9)
    row=p.locate(0.)
    assert row['contact_y_m']==pytest.approx(-.01/(.5+1/.3),abs=1e-8)
    assert row['coefficients']['curvature_y_m_inv']==pytest.approx(.5+1/.3,rel=1e-8)
    with pytest.raises(ValueError,match='overlap'):p.locate(1.)


def test_spatial_beam_matches_native_shear_bending_axial_and_torsion():
    pytest.importorskip('openseespy.opensees')
    r=native_beam_benchmark();assert r['numerical_benchmark_passed']
    assert r['analytic_relative_error']<1e-10 and r['native_relative_error']<1e-10


def test_alignment_tangent_is_arc_length_derivative_with_vertical_curve_and_cant():
    c=configuration(demonstration())['route'];c.update(radius_m=800.,vertical_radius_m=5000.,cant_rad=.04)
    route=Route(c);s=40.;h=1e-3
    tangent=(route.position(s+h)-route.position(s-h))/(2*h)
    assert tangent==pytest.approx(route.frame(s)[:,0],rel=1e-7,abs=1e-8)
    assert np.linalg.det(route.frame(s))==pytest.approx(1.)


def test_full_spatial_structure_static_equilibrium_and_offset_virtual_work():
    m=demonstration();c=configuration(m);s=SpatialStructure(m['bridge'],Route(c['route']),deck_mesh=2,rail_step=2.,modes=8)
    residual=s.K@s.dead_displacement-s.dead_load
    assert np.max(np.abs(residual[s.free]))<.01
    assert s.modal_mass_error<1e-8
    p=s.rail_port(12.,0,1);F=np.arange(1.,7.);velocity=np.linspace(-.01,.02,8)
    assert s.virtual_work_check(p,F,velocity)<1e-12
    r=s.full_member_demands(s.dead_displacement)
    assert {row['kind'] for row in r}=={'deck','cap','pier'}


@pytest.mark.parametrize('scheme',['continuous','link-slab'])
def test_span_connections_preserve_positive_structure_and_the_declared_motion(scheme):
    m=demonstration();m['bridge']['study']['connection_scheme']=scheme
    if scheme=='link-slab':m['bridge']['span_connection']=dict(stiffness_si=np.diag([1e8]*3+[1e6]*3).tolist(),basis='synthetic verification')
    s=SpatialStructure(m['bridge'],Route(configuration(m)['route']),deck_mesh=2,rail_step=2.,modes=8)
    assert np.min(s.omega)>0 and s.modal_mass_error<1e-8
    if scheme=='continuous':assert s.deck_ends[0][0][1]==s.deck_ends[0][1][0]
    else:assert len([j for j in s.springs if j['kind']=='span-connection'])==4


def test_gross_loading_uses_family_capacity_and_preserves_original_hardware():
    m=demonstration();original=deepcopy(m);c=configuration(m);c['traffic'][0]['load_case']['id']='crush'
    loaded=loaded_model(m,c['traffic'][0]['load_case'])
    v=SpatialVehicle(loaded,c['joint_laws']);base=SpatialVehicle(m,c['joint_laws'])
    expected=m['family_definition']['profile']['crush_capacity']/6*75*2
    assert v.total_mass-base.total_mass==pytest.approx(expected)
    assert sum(w['static_n'] for w in v.contacts)==pytest.approx(v.total_mass*9.81,rel=1e-8)
    assert m==original


@pytest.mark.parametrize('name',['straight-empty','curve-cant-braking-uneven','two-track-crush-defect','degraded-joints-adhesion'])
def test_spatial_coupling_runs_with_identity_contact_histories_and_small_residuals(name):
    m=demonstration();r=run_spatial(m,scenarios(m)[name],duration_s=.02,dt=.002,deck_mesh=2,rail_step=2.)
    assert r['full_sparse_fem'] and not r['modal_truncation_used']
    assert r['hardware_definition_sha256']==fingerprint(m)
    assert r['minimum_wheel_contact_n']>=0 and r['maximum_wheel_contact_n']>0
    assert r['contact_power_balance_residual_w']<1e-6
    assert all(h['newton_residual_n']<.1 for h in r['history'])
    assert len(r['trains'])==(2 if name=='two-track-crush-defect' else 1)
    assert not r['physical_validation'] and not r['engineering_released']


def test_joint_nonlinear_curves_stops_and_damping_have_correct_tangents():
    law=dict(stiffness_si=np.eye(6).tolist(),damping_si=np.eye(6).tolist(),
        force_displacement_curves=[[[-1.,-10.],[0.,0.],[1.,20.]]]+[None]*5,
        bump_stops=[dict(lower_si=-.5,upper_si=.5,stiffness_si=100.,damping_si=5.)]+[None]*5)
    q=np.array([.6,0.,0.,0.,0.,0.]);v=q*.1;f,k,c=response(law,q,v)
    assert f[0]==pytest.approx(12.+10.+.06+.3)
    h=1e-7;fp=response(law,q+np.array([h,0,0,0,0,0]),v)[0]
    assert (fp[0]-f[0])/h==pytest.approx(k[0,0],rel=1e-6)
    with pytest.raises(ValueError,match='outside'):response(law,q*2,v)


def test_concrete_small_strain_modulus_and_long_term_creep_are_consistent():
    law=synthetic_laws(demonstration())['concrete'];a=concrete_state(law,28.,20.)
    sigma,_=concrete_stress(-1e-10,a,.5)
    assert sigma/-1e-10==pytest.approx(a['E_pa'],rel=1e-6)
    b=concrete_state(law,365.,20.)
    sigma,_=concrete_stress(b['eigenstrain']-1e-10,b,.5)
    assert sigma/-1e-10==pytest.approx(b['E_pa'],rel=1e-6)
    assert b['eps_c0']/a['eps_c0']==pytest.approx(2.5)
    with pytest.raises(ValueError,match='outside'):concrete_state(law,1000.,20.)


def test_crack_band_softening_integrates_to_declared_fracture_energy():
    from scipy.integrate import quad
    law=synthetic_laws(demonstration())['concrete'];s=concrete_state(law,28.,20.)
    for length in (.1,.5):
        initial=s['ft_pa']/s['E_pa']
        energy=quad(lambda w:concrete_stress(initial+w/length,s,length)[0],0,30*s['fracture_energy_n_m']/s['ft_pa'])[0]
        assert energy==pytest.approx(s['fracture_energy_n_m'],rel=1e-7)


def test_steel_yield_return_and_reversal_have_nonnegative_plastic_work():
    law=dict(E_pa=200e9,yield_pa=400e6,hardening_pa=1e9)
    r=steel_return(.004,law);expected=(200e9*.004-400e6)/(201e9)
    assert r['plastic_strain']==pytest.approx(expected)
    assert r['stress_pa']==pytest.approx(400e6+1e9*expected)
    back=steel_return(-.004,law,r);assert back['plastic_dissipation_j_m3']>=0


def test_laminate_recovers_unidirectional_modulus_coupling_and_ply_stress():
    p=dict(thickness_m=.001,E1_pa=100e9,E2_pa=10e9,G12_pa=5e9,nu12=.25,angle_deg=0.,
        Xt_pa=1e9,Xc_pa=.8e9,Yt_pa=50e6,Yc_pa=100e6,S_pa=60e6)
    r=laminate([p,p]);assert r['longitudinal_modulus_pa']==pytest.approx(100e9)
    assert np.max(np.abs(r['B_n']))<1e-10
    response=laminate_response([p,p],.001)
    assert response['stress_pa']==pytest.approx(100e6)
    assert response['ply_faces'][0]['stress_local_pa'][0]==pytest.approx(100e6)
    rotated=deepcopy(p);rotated['angle_deg']=90.
    assert laminate([rotated])['longitudinal_modulus_pa']==pytest.approx(10e9)


def test_cohesive_mode_I_energy_irreversibility_and_compressive_contact():
    from scipy.integrate import quad
    law=dict(normal_stiffness_n_m3=1e12,shear_stiffness_n_m3=5e11,normal_strength_pa=1e6,
        shear_strength_pa=2e6,mode_I_energy_n_m=100.,mode_II_energy_n_m=200.,bk_exponent=1.5)
    d0=1e-6;df=2*100/1e6
    energy=quad(lambda d:cohesive([d,0.,0.],law)['traction_pa'][0],0.,df,points=[d0])[0]
    assert energy==pytest.approx(100.,rel=1e-6)
    r=cohesive([df,0.,0.],law);assert r['damage']==1.
    r=cohesive([-.0001,0.,0.],law,1.);assert r['traction_pa'][0]<0 and r['damage']==1.


def test_assembled_fiber_section_recovers_independent_elastic_rectangle():
    section=dict(regions=[dict(y_m=0.,z_m=0.,width_m=.2,height_m=.4)],material_roles=['steel'])
    law=dict(type='steel',E_pa=200e9,yield_pa=400e6,hardening_pa=1e9,ultimate_strain=.05)
    demand=dict(axial_n=-10000.,moment_y_nm=1000.,moment_z_nm=500.)
    r=section_response(section,dict(steel=law),demand,fibers_per_region=8)
    assert r['equilibrium_solved'] and not r['ultimate_exceeded']
    assert r['resultant_n_nm']==pytest.approx(list(demand.values()),rel=1e-6)
    assert r['generalised_strains'][0]==pytest.approx(-10000/(200e9*.08),rel=1e-6)
    assert not r['engineering_released']


def test_fatigue_repeated_excursions_preserve_total_cycle_count():
    cycles=rainflow([0.,10.,0.,10.,0.]);assert sum(c['count'] for c in cycles)==pytest.approx(2.)
    assert all(c['range_pa']==10. for c in cycles)
    assert rainflow([1.,1.,1.])==[]


def test_joint_register_and_bolt_equilibrium_leave_unsupplied_preload_open():
    register=definitions(demonstration());assert all(r['open_fields'] for r in register['joints'])
    points=[[-.18,-.09,0.],[-.18,.09,0.],[.18,-.09,0.],[.18,.09,0.]]
    r=bolt_group(points,[1000.,2000.,10000.,100.,200.,300.])
    assert r['equilibrium_residual']<1e-8
    assert all(b['minimum_clamp_n'] is None for b in r['bolts']) and not r['strength_accepted']
    with pytest.raises(ValueError,match='resolve'):bolt_group([[0,0,0],[1,0,0],[2,0,0]],[0]*6)


def test_native_dat_parser_never_treats_reaction_force_as_displacement(tmp_path):
    path=tmp_path/'joint.dat';path.write_text('displacements (vx,vy,vz) for set TOP and time 1.0\n1 .0001 0 0\nforces (fx,fy,fz) for set TOP and time 1.0\n1 30000 0 0\n')
    blocks=parse_dat(path);assert blocks[0]['rows'][0][1]==.0001 and blocks[1]['quantity']=='forces'


def dataset(tmp_path,model):
    source=tmp_path/'measurements.json';source.write_text('synthetic verification only')
    calibration=tmp_path/'calibration.json';calibration.write_text('synthetic verification only')
    ref=lambda p:dict(path=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    times=np.linspace(.1,1.,10)
    tests=[dict(id='T-'+specimen,specimen_id=specimen,serial=specimen,design_revision=model['revision'],
        quantity='force',unit='N',time_s=times.tolist(),values=(3*times+2).tolist(),standard_uncertainty=[.1]*10,
        source=ref(source),calibration_record=ref(calibration)) for specimen in ('A','B')]
    return dict(schema='osr-instrumented-correlation/1',hardware_definition_sha256=fingerprint(model),classification='synthetic-verification',tests=tests)


def test_calibration_recovers_parameters_and_holdout_without_claiming_physical_validation(tmp_path):
    m=demonstration();data=dataset(tmp_path,m);parameters=[dict(name=k,initial=1.,minimum=0.,maximum=5.) for k in ('slope','offset')]
    r=calibrate(m,data,parameters,lambda p,t:p['slope']*np.asarray(t['time_s'])+p['offset'],root=tmp_path,holdout_specimens=['B'])
    assert r['fitted_parameters']==pytest.approx(dict(slope=3.,offset=2.),abs=1e-8)
    assert r['identifiable'] and r['holdout_tests'][0]['rmse']<1e-8
    assert r['training_tests']==['T-A'] and not r['physical_measurements_used'] and not r['physical_validation']
    assert all(row['project_limits'] is None for row in protocols(m)['levels'])


def test_correlation_rejects_revision_unit_evidence_and_holdout_leakage(tmp_path):
    m=demonstration();original=dataset(tmp_path,m);parameters=[dict(name='slope',initial=1.,minimum=0.,maximum=5.)]
    def run(data):return calibrate(m,data,parameters,lambda p,t:p['slope']*np.asarray(t['time_s']),root=tmp_path,holdout_specimens=['B'])
    for key,value,match in [('unit','kN','units'),('design_revision','STALE','revision'),('specimen_id','A','holdout')]:
        data=deepcopy(original);data['tests'][1][key]=value
        with pytest.raises(ValueError,match=match):run(data)
    (tmp_path/'calibration.json').write_text('changed calibration')
    with pytest.raises(ValueError,match='changed'):run(original)
