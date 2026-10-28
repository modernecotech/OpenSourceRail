"""Temporal-method, conservation and immutable-domain tests; no physical evidence."""
from copy import deepcopy
import numpy as np
import pytest
from engineering.railway_progress import propulsion as p
from engineering.reference_cell import motor_refinement as prior
from engineering.railway_completion import motor
from engineering.railway_twin import model

@pytest.fixture(scope='module')
def bundle():return motor.rewound_variant(model.materialize()['bundle'])


def test_second_order_history_is_exact_on_constant_linear_quadratic_functions():
    assert p.coefficients('bdf2',1)==(1.,-1.,0.)
    a=p.coefficients('bdf2',2);dt=.01;t=.13
    assert sum(a)==0
    for power in (0,1,2):
        derivative=sum(c*(t-i*dt)**power for i,c in enumerate(a))/dt
        assert derivative==pytest.approx(0. if power==0 else power*t**(power-1),abs=1e-11)


@pytest.mark.parametrize('method,minimum_order',[('backward-euler',.8),('bdf2',1.7)])
def test_independent_analytic_RL_sinusoid_reproduces_declared_temporal_order(method,minimum_order):
    errors=[p.linear_RL_benchmark(dt,method=method)['RMS_error_A'] for dt in (.001,.0005,.00025)]
    orders=[np.log2(a/b) for a,b in zip(errors,errors[1:])]
    assert min(orders)>minimum_order
    assert all(abs(r['circuit_residual_V'])<1e-12 for r in p.linear_RL_benchmark(.001,method=method)['trace'])


def test_BDF2_resolves_sinusoidal_control_more_accurately_than_same_step_BE():
    assert p.linear_RL_benchmark(.001)['RMS_error_A']<p.linear_RL_benchmark(.001,method='backward-euler')['RMS_error_A']*.3


def test_physical_geometry_current_density_and_winding_are_unchanged(bundle):
    old=prior.request(bundle,steps=2)
    new=p.request(bundle,steps=2)
    for key in ('bundle_id','physical_geometry','wiring','motor_component_id','evaluated_component_definition_id','current_limit_A','current_density_limit_RMS_A_mm2'):
        assert new[key]==old[key]
    assert new['request_id']!=old['request_id'] and new['schema']!=old['schema']
    assert new['time_integrator']=='bdf2'
    assert p.path_resistance(new).tolist()==prior.path_resistance(old).tolist()
    assert p.sources()[p.FROZEN]==p.FROZEN_SHA256


@pytest.mark.parametrize('changes',[
 dict(maximum_seconds=1201.),dict(memory_bytes=4*1024**3),dict(maximum_nodes=180001),dict(current_limit_A=240.),
 dict(voltage_peak_V=376.),dict(time_integrator='explicit-euler'),dict(steps=1025)])
def test_resource_change_does_not_weaken_physical_or_absolute_domains(bundle,changes):
    with pytest.raises(ValueError):p.request(bundle,**changes)


def test_necessary_preflight_matches_same_mesh_before_any_large_solve(bundle):
    new=p.request(bundle,steps=128,dt_s=.001,speed_m_s=20.,frequency_Hz=50.,transport_method='supg-coth')
    old=prior.request(bundle,steps=128,dt_s=.001,speed_m_s=20.,frequency_Hz=50.,transport_method='supg-coth')
    assert p.estimate(new)==prior.estimate(old)
    assert p.estimate(new)['mesh_nodes_within_budget']
    assert not p.estimate(new)['unstabilized_domain_supported']


def test_BDF2_circuit_tangent_matches_independent_finite_difference():
    from scipy.sparse import csr_matrix
    rng=np.random.default_rng(37);nf,nc=4,3;dt=.02;a0=1.5;height=.16;leak=.004
    W=rng.normal(size=(nf,nc));b=rng.normal(size=nf);bs=rng.normal(size=nf);closure=rng.normal(size=nf)
    field=rng.normal(size=(nf,nf));R=np.array([.2,.3,.4]);S=2.;old=rng.normal(size=nf+nc);older=rng.normal(size=nf+nc)
    matrix=p.circuit_jacobian(csr_matrix(field),b,closure,S,csr_matrix(W),R+leak*a0/dt,dt/a0,height,field_b=b+bs).toarray()
    def residual(x):
        A=x[:nf];u=x[nf];I=x[nf+1:nf+nc+1];neutral=x[-1]
        Adot=(a0*A-2*old[:nf]+.5*older[:nf])/dt
        Idot=(a0*I-2*old[nf:]+.5*older[nf:])/dt
        return np.r_[field@A+(b+bs)*u-W@I,b@Adot+closure@A+S*u,R*I+leak*Idot+height*W.T@Adot+neutral,I.sum()]
    x=rng.normal(size=nf+nc+2);h=1e-6;fd=np.column_stack([(residual(x+np.eye(len(x))[i]*h)-residual(x-np.eye(len(x))[i]*h))/(2*h) for i in range(len(x))])
    assert np.allclose(matrix,fd,rtol=2e-8,atol=2e-8)


def test_actual_retained_BE_energy_diagnosis_is_numerical_not_physical_heat():
    import json,tarfile
    root=p.ROOT/'docs/design-engine/reference-cell'
    manifest=json.loads((root/'native-motor-refinement-manifest.json').read_bytes())
    with tarfile.open(root/manifest['archive'],'r:gz') as archive:
        request=json.load(archive.extractfile('coarse/input.json'))['request']
        result=json.load(archive.extractfile('coarse/result.json'))
    value=p._time_statistics(request,result)
    retained=manifest['comparison']['full_horizon_statistics'][0]
    assert value['integrated_terminal_energy_J']==pytest.approx(retained['terminal_energy_J'],rel=1e-12)
    assert value['signed_algorithmic_field_energy_defect_J']==pytest.approx(retained['backward_Euler_numerical_energy_J'],rel=1e-12)
    assert value['algorithmic_field_defect_to_terminal_ratio']>.70
    assert value['numerical_work_is_physical_heat'] is False


def test_BDF2_trace_verifier_refuses_relabelled_history_coefficients(bundle):
    r=p.request(bundle,voltage_peak_V=0.,steps=3);rows=[]
    for n in range(1,4):
        t=n*r['dt_s'];start=r['start_m']+r['speed_m_s']*t;g=r['physical_geometry']
        row=dict(time_s=t,time_integrator='bdf2',derivative_coefficients=list(p.coefficients('bdf2',n)),
            secondary_start_m=start,secondary_end_m=start+g['secondary_length_m'],
            conductor_area_m2=g['secondary_length_m']*g['secondary_thickness_m'],
            conductor_first_moment_x_m3=g['secondary_length_m']*g['secondary_thickness_m']*(start+g['secondary_length_m']/2),
            path_currents_A=[0.]*30,phase_currents_A=[0.]*3,phase_voltage_commands_V=[0.]*3,
            primary_copper_W=0.,net_terminal_current_A=0.,external_leakage_energy_J=0.,external_leakage_work_W=0.,
            leakage_algorithmic_energy_defect_W=0.,mechanical_W=0.,thrust_N=0.,magnetic_energy_J=0.,
            algorithmic_energy_defect_W=0.,numerical_field_work_W=0.,terminal_W=0.,secondary_Joule_W=0.,
            stabilization_work_W=0.,discrete_power_residual_W=0.)
        rows.append(row)
    result=dict(execution='completed',state='completed',trace=rows,available_operating_map=None,installed_force_available_N=None,
        repeated_thermal_duty_verified=False,converter_current_control_verified=False)
    p._trace_check(r,result)
    result['trace'][1]['derivative_coefficients']=[1.,-1.,0.]
    with pytest.raises(ValueError,match='history'):p._trace_check(r,result)
