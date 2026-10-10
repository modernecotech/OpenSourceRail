"""Independent equations and full car/bogie/multi-span propagation benchmarks."""
from copy import deepcopy
from pathlib import Path
import sys
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.civil_exploration.shared_demo import demonstration, variants
from engineering.civil_exploration.train_bridge import beam_matrices, hermite, Bridge, Vehicle, run, native_deck_benchmark


def test_consistent_beam_matches_independent_static_and_modal_equations():
    length=25.;EI=30e9*.2;mass=2000.
    for mesh in [4,8]:
        M=np.zeros((2*(mesh+1),)*2);K=np.zeros_like(M)
        for i in range(mesh):
            m,k=beam_matrices(length/mesh,EI,mass);ix=np.ix_(range(2*i,2*i+4),range(2*i,2*i+4));M[ix]+=m;K[ix]+=k
        keep=[i for i in range(len(M)) if i not in [0,2*mesh]];free=K[np.ix_(keep,keep)]
        F=np.zeros(len(M));F[mesh]=10000.
        q=np.linalg.solve(free,F[keep]);mid=q[keep.index(mesh)]
        assert mid==pytest.approx(10000*length**3/(48*EI),rel=1e-10)
        from scipy.linalg import eigh
        frequency=np.sqrt(eigh(free,M[np.ix_(keep,keep)],subset_by_index=[0,0],eigvals_only=True)[0])
        assert frequency==pytest.approx(np.pi**2/length**2*np.sqrt(EI/mass),rel=.001)


def test_hermite_distribution_conserves_force_moment_and_point_power():
    for x in [0.,.1,2.,4.]:
        n,dn=hermite(x,0.,4.)
        assert n[0]+n[2]==pytest.approx(1.)
        assert n[1]+4*n[2]+n[3]==pytest.approx(x)
        assert dn[0]+dn[2]==pytest.approx(0.)


def test_shared_bridge_is_flexible_multispan_and_has_positive_symmetric_matrices():
    model=demonstration();b=Bridge(model['bridge'],4)
    assert b.length==75. and len(b.supports)==4
    assert np.allclose(b.M,b.M.T) and np.allclose(b.K,b.K.T)
    assert np.linalg.eigvalsh(b.M).min()>0 and np.linalg.eigvalsh(b.K).min()>0
    # Independent global equilibrium includes the elastic approach track ground.
    F=np.zeros(len(b.M));F[b.rail_nodes[len(b.rail_nodes)//2][1]]=100000.
    q=np.linalg.solve(b.K,F)
    support=sum(b.ground_stiffness*q[base] for top,base in b.supports)
    approach=sum(k*q[d] for d,k in b.approach_ground_pads)
    assert support+approach==pytest.approx(100000.,rel=1e-7)


def test_vehicle_contains_shared_bodies_bogie_pitch_and_individual_unsprung_axles():
    model=demonstration();v=Vehicle(model)
    assert len(v.wheels)==8 and len(v.M)==20
    assert sum(g['mass'] for g in v.group.values())==pytest.approx(v.static['total_mass_kg'])
    assert sum(w['static_n'] for w in v.wheels)==pytest.approx(v.static['total_mass_kg']*9.81)
    assert np.allclose(v.K,v.K.T) and np.allclose(v.C,v.C.T)
    model['joints']=model['joints'][1:]
    assert len(Vehicle(model).wheels)==8  # Fixed battery geometry does not supply a suspension spring.
    model['joints']=[j for j in model['joints'] if j['connection']!='primary']
    with pytest.raises(ValueError,match='each wheelset'):Vehicle(model)


def test_bidirectional_contact_is_balanced_and_battery_changes_bridge_demand():
    model=demonstration();base=run(model,speed=30.,dt=.01,mesh=2)
    changed=run(variants(model)['battery-plus-10-percent'],speed=30.,dt=.01,mesh=2)
    assert base['within_adapter_domain']
    assert base['contact_force_balance_residual_n']<1e-8
    assert base['contact_moment_balance_residual_nm']<1e-6
    assert base['contact_power_balance_residual_w']<1e-8
    assert changed['total_mass_kg']-base['total_mass_kg']==pytest.approx(250.)
    assert changed['peak_bearing_force_n']!=pytest.approx(base['peak_bearing_force_n'],rel=1e-5)
    assert changed['peak_vehicle_acceleration_m_s2']!=pytest.approx(base['peak_vehicle_acceleration_m_s2'],rel=1e-5)
    assert base['physical_validation'] is False and base['engineering_released'] is False


def test_contact_loss_and_joint_stop_exceedance_fail_adapter_domain():
    model=demonstration()
    for j in model['joints']:
        if j['properties']['design'] is not None:
            j['properties']['design']['lower_stop_m']=-1e-10;j['properties']['design']['upper_stop_m']=1e-10
    result=run(model,speed=30.,dt=.01,mesh=2,irregularity_amplitude=.2)
    assert not result['within_adapter_domain'] and result['joints_outside_linear_stops']
    assert result['minimum_contact_n']<0


def test_timestep_refinement_limits_response_error():
    model=demonstration();a=run(model,speed=30.,dt=.005,mesh=2);b=run(model,speed=30.,dt=.0025,mesh=2)
    for key in ['peak_rail_displacement_m','peak_bearing_force_n','maximum_contact_n']:
        assert a[key]==pytest.approx(b[key],rel=.05)


def test_native_opensees_independently_reproduces_finite_support_deck():
    pytest.importorskip('openseespy.opensees')
    result=native_deck_benchmark(demonstration()['bridge'],4)
    assert result['numerical_benchmark_passed'] and result['relative_displacement_error']<1e-6
    assert result['physical_validation'] is False
