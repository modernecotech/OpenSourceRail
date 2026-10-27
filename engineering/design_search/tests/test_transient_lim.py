"""Small independent algebraic method fixtures; no native engineering runs."""
import math
import numpy as np
import pytest
from engineering.design_search import transient_lim as t
from engineering.design_search import lim_materials
from engineering.station_rail import station_motor


def toy():
    # One free central potential; plate has an independent floating return current.
    p=np.array([[0.,0.],[.01,0.],[.01,.01],[0.,.01],[.005,.005]])
    tri=np.array([[0,1,4],[1,2,4],[2,3,4],[3,0,4]])
    return p,tri,np.array([100,2,3,1]),np.arange(4)


def test_inverse_law_stored_energy_and_tangent_are_independent():
    curve=lim_materials.material()
    B=np.array([.031,.42,1.234,1.71,2.01]);H,tangent,W=t.constitutive(B,curve)
    assert H==pytest.approx([lim_materials.field_for_B(curve,x) for x in B])
    eps=1e-7
    plus=t.constitutive(B+eps,curve);minus=t.constitutive(B-eps,curve)
    assert (plus[2]-minus[2])/(2*eps)==pytest.approx(H,rel=1e-7)
    assert (plus[0]-minus[0])/(2*eps)==pytest.approx(tangent,rel=1e-7)
    # Legendre relation distinguishes energy from coenergy for nonlinear steel.
    assert W==pytest.approx([b*h-lim_materials.coenergy_density(curve,h) for b,h in zip(B,H)],rel=1e-12)
    with pytest.raises(ValueError,match='extrapolation'):
        t.constitutive(np.array([curve['B_T'][-1]+.001]),curve)


def test_triangle_gradient_handles_orientation_and_exact_linear_field():
    p=np.array([[0.,0.],[2.,0.],[0.,3.]])
    for tri in (np.array([[0,1,2]]),np.array([[2,1,0]])):
        area,grad=t.geometry(p,tri)
        A=4*p[:,0]-3*p[:,1]+2
        assert area[0]==pytest.approx(3.)
        assert A[tri[0]]@grad[0]==pytest.approx([4.,-3.])
        assert np.sum(grad,axis=1)==pytest.approx(np.zeros((1,2)))


def test_nonlinear_vector_tangent_matches_residual_derivative():
    p=np.array([[0.,0.],[1.,0.],[0.,1.]])
    tri=np.array([[0,1,2]]);area,grad=t.geometry(p,tri);regions=np.array([3]);curve=lim_materials.material()
    A=np.array([.01,.911,.793]);r,J,*_=t.magnetic(A,tri,area,grad,regions,curve)
    eps=1e-7
    for i in range(3):
        delta=np.eye(3)[i]*eps
        rp=t.magnetic(A+delta,tri,area,grad,regions,curve)[0][0]
        rm=t.magnetic(A-delta,tri,area,grad,regions,curve)[0][0]
        assert (rp-rm)/(2*eps)==pytest.approx(J[0,:,i],rel=1e-7,abs=1e-6)
    assert J[0]==pytest.approx(J[0].T)
    assert np.linalg.eigvalsh(J[0])[0]>=-1e-7


def test_phase_sources_are_balanced_and_reverse_in_time():
    c=t.case();d=station_motor.definition();time=.0023
    js=np.array([t.phase_current_density(k,time,c,d) for k in range(100,106)])
    assert sum(js)==pytest.approx(0.,abs=1e-8)
    reverse=t.case(phase_direction=-1)
    assert [t.phase_current_density(k,time,reverse,d) for k in range(100,106)]==pytest.approx([t.phase_current_density(k,-time,c,d) for k in range(100,106)])
    assert js[:3]==pytest.approx(-js[3:])
    assert t.phase_current_density(2,time,c,d)==0


def test_linear_diffusion_matches_independent_single_mode_backward_euler():
    p,tri,regions,boundary=toy();c=t.case(current_peak_A=25,speed_m_s=0,linear=True,steps_per_period=16,periods=1);d=station_motor.definition()
    result=t.solve(p,tri,regions,boundary,c,d,lim_materials.material())
    # Exact element integrals: each triangle area=25e-6, |grad N_center|=200.
    # Floating closure eliminates u=-A_dot/3, leaving M=sigma*area/18.
    area=.000025;K=(3+1/1000)/t.MU0;M=c['aluminium_conductivity_S_m']*area/18
    A=0.;dt=c['dt_s']
    for row in result['trace']:
        source=t.phase_current_density(100,row['time_s'],c,d)*area/3
        A=(source+M*A/dt)/(K+M/dt)
    assert result['final_A_Wb_m'][4]==pytest.approx(A,rel=1e-12)
    assert max(abs(r['net_secondary_current_A']) for r in result['trace'])<1e-12
    scale=max(abs(r['source_field_W']) for r in result['trace'])
    assert max(abs(r['discrete_power_residual_W']) for r in result['trace'])<scale*1e-12
    assert min(r['backward_Euler_dissipation_W'] for r in result['trace'])>=-1e-14


def test_zero_excitation_has_no_force_current_or_magnetic_work():
    p,tri,regions,boundary=toy();c=t.case(current_peak_A=0,speed_m_s=0,periods=1,steps_per_period=16)
    r=t.solve(p,tri,regions,boundary,c,station_motor.definition(),lim_materials.material())
    for row in r['trace']:
        for key in ('source_field_W','secondary_Joule_W','thrust_N','normal_force_N','magnetic_energy_J','discrete_power_residual_W'):
            assert row[key]==0.


def test_moving_discrete_work_closure_and_material_domain_hold():
    p,tri,regions,boundary=toy();regions=np.array([2,2,3,100]);c=t.case(speed_m_s=1,periods=1,steps_per_period=16)
    r=t.solve(p,tri,regions,boundary,c,station_motor.definition(),lim_materials.material())
    scale=max(abs(x['source_field_W']) for x in r['trace'])
    assert max(abs(x['thrust_N']) for x in r['trace'])>1e-8
    assert max(abs(x['discrete_power_residual_W']) for x in r['trace'])<scale*1e-7
    for row in r['trace']:
        assert row['mechanical_W']==pytest.approx(row['thrust_N']*c['speed_m_s'])
        assert row['backward_Euler_dissipation_W']>=-1e-13
    # No invented stabilization: coarse/fast conductor is refused before solving.
    c['speed_m_s']=10
    with pytest.raises(ValueError,match='Peclet'):
        t.solve(p,tri,regions,boundary,c,station_motor.definition(),lim_materials.material())


def test_case_identity_cannot_reseal_changed_geometry_or_resource_domain():
    c=t.case();t.validate_case(c)
    c['secondary_length_m']=.4;c['case_id']=t.identity({k:v for k,v in c.items() if k!='case_id'})
    with pytest.raises(ValueError,match='constructor'):t.validate_case(c)
    for kwargs in ({'current_peak_A':141},{'frequency_Hz':0},{'steps_per_period':128},{'linear':'yes'}):
        with pytest.raises(ValueError):t.case(**kwargs)


def test_benchmark_plan_is_bounded_unexecuted_and_does_not_supply_a_map():
    plan=t.benchmark_plan()
    assert len(plan['jobs'])==plan['maximum_jobs']==6
    assert plan['timeout_s']==90 and plan['memory_mb']==3072
    assert plan['installed_available_force_N'] is None
    assert plan['nonlinear_operating_map_available'] is False
    assert plan['physical_accepted'] is False
    assert all(job['case']['position_changes_during_solve'] is False for job in plan['jobs'])
    assert 'fixed' in t.__doc__.lower()


def test_linear_period_response_converges_to_closed_form_diffusion():
    p,tri,regions,boundary=toy();d=station_motor.definition();curve=lim_materials.material();errors=[]
    for resolution in (16,32,64):
        c=t.case(speed_m_s=0,linear=True,steps_per_period=resolution,periods=1)
        r=t.solve(p,tri,regions,boundary,c,d,curve)
        area=.000025;K=(3+1/1000)/t.MU0;M=c['aluminium_conductivity_S_m']*area/18
        omega=2*math.pi*c['frequency_Hz'];T=1/c['frequency_Hz']
        source=d['turns_per_coil']*c['current_peak_A']/(d['slot_width_m']*d['slot_depth_m'])*area/3
        exact=source/(K*K+(M*omega)**2)*(K*math.cos(omega*T)+M*omega*math.sin(omega*T)-K*math.exp(-K*T/M))
        errors.append(abs(r['final_A_Wb_m'][4]-exact))
    assert errors[2]<errors[1]<errors[0]
    assert errors[0]/errors[1]>1.8


def test_physical_fixture_identity_does_not_change_with_numerical_hypothesis():
    a=t.case(linear=True,steps_per_period=16)
    b=t.case(linear=False,steps_per_period=64)
    assert a['case_id']!=b['case_id']
    assert t.definition(a)['motor_component_id']==t.definition(b)['motor_component_id']
    assert t.definition(a)['motor_component_id']!=station_motor.definition()['motor_component_id']
    assert t.definition(a)['fixture_geometry']['primary_length_m']==.5
    assert t.definition(a)['secondary_length_m']==.3
