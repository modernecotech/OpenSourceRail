"""Independent mathematical controls; no qualified railway or full-body jobs."""
from copy import deepcopy
from math import pi
import numpy as np
import pytest

from engineering.railway_progress import structures as s


def cantilever(divisions=1,axis='x'):
    direction={'x':np.array([1.,0.,0.]),'y':np.array([0.,1.,0.]),'z':np.array([0.,0.,1.])}[axis]
    nodes=[(direction*2*i/divisions).tolist() for i in range(divisions+1)]
    return dict(nodes=nodes,elements=[dict(a=i,b=i+1,A=.01,Iy=1e-5,Iz=2e-5,J=1e-5,E=70e9,G=26e9,cy=.1,cz=.1,source='beam',physical_member_length_m=2.) for i in range(divisions)],
        connections=[],supports={str(i):0. for i in range(6)})


def test_frame_stiffness_has_six_rigid_body_modes_and_nonnegative_strain_energy():
    K=s.frame_stiffness(2.,.01,1e-5,2e-5,1e-5,70e9,26e9)
    assert np.allclose(K,K.T)
    values=np.linalg.eigvalsh(K)
    assert np.count_nonzero(values>max(values)*1e-10)==6
    assert min(values)>-max(values)*1e-12


@pytest.mark.parametrize('divisions',[1,2,4])
def test_actual_frame_solution_matches_independent_cantilever_expression(divisions):
    model=cantilever(divisions);F=np.zeros(6*len(model['nodes']));F[-4]=-1000.
    result=s.solve(model,[('cantilever',F,{})]);case=result['cases'][0]
    expected=1000*2**3/(3*70e9*1e-5)
    assert result['execution']=='completed'
    assert case['maximum_translation_m']==pytest.approx(expected,rel=1e-11)
    assert case['free_relative_residual']<1e-11
    assert case['relative_energy_residual']<1e-11
    assert np.linalg.norm(case['force_balance_residual_N'])<1e-8
    assert np.linalg.norm(case['moment_balance_residual_Nm'])<1e-8
    assert case['approved_strength_margin'] is None
    assert case['approved_deflection_limit_m'] is None
    assert case['elements'][0]['unsupported_length_m_hypothesis']==2.
    # Refining a mesh does not fictitiously shorten the physical unbraced beam.
    assert case['elements'][0]['pinned_member_Euler_load_N']==pytest.approx(pi*pi*70e9*1e-5/4)


@pytest.mark.parametrize('axis',['x','y','z'])
def test_axial_frame_response_is_invariant_under_rigid_orientation(axis):
    model=cantilever(axis=axis);F=np.zeros(12);index='xyz'.index(axis);F[6+index]=1000.
    result=s.solve(model,[('axial',F,{})])['cases'][0]
    assert result['displacements_m_rad'][1][index]==pytest.approx(1000*2/(70e9*.01),rel=1e-11)


def test_torsion_is_not_a_pin_graph_or_an_unweighted_translation_model():
    model=cantilever();F=np.zeros(12);F[9]=100.
    case=s.solve(model,[('torsion',F,{})])['cases'][0]
    assert case['displacements_m_rad'][1][3]==pytest.approx(100*2/(26e9*1e-5),rel=1e-11)
    assert case['strain_energy_J']==pytest.approx(.5*100*100*2/(26e9*1e-5))


def test_offset_finite_joint_preserves_force_moment_and_connection_energy():
    model=cantilever();model['nodes']+=[[1.,.1,0.],[2.,.1,0.]]
    model['nodes'][1]=[1.,0.,0.]
    model['elements'].append(dict(model['elements'][0],a=2,b=3,source='second'))
    model['connections']=[dict(a=1,b=2,point=[1.,.05,0.],stiffness=[1e8]*3+[1e6]*3,source_pair=['first','second'])]
    F=np.zeros(24);F[20]=-1000.
    case=s.solve(model,[('offset',F,{})])['cases'][0]
    assert case['free_relative_residual']<1e-8
    assert np.linalg.norm(case['moment_balance_residual_Nm'])<1e-7
    assert case['connections'][0]['strain_energy_J']>0
    assert case['connections'][0]['approved_joint_margin'] is None
    assert case['connections'][0]['maximum_relative_translation_m']>0


def test_free_frame_reports_a_mechanism_instead_of_inventing_restraints():
    model=cantilever();model['supports']={};F=np.zeros(12);F[8]=-1000.
    result=s.solve(model,[('free',F,{})])
    assert result['execution']=='underconstrained'


def test_navier_plate_control_is_separate_from_material_or_bonded_shell_qualification():
    result=s.benchmarks()
    assert result['cantilever']['calculated_tip_m']==pytest.approx(result['cantilever']['analytic_tip_m'],rel=1e-12)
    assert result['torsion']['calculated_rotation_rad']==pytest.approx(result['torsion']['analytic_rotation_rad'],rel=1e-12)
    first,last=result['plate']['results']
    assert first['divisions']==8 and last['divisions']==16
    assert last['relative_error']<first['relative_error']<.03
    assert 'not actual' in result['plate']['domain']


def test_saved_displacements_and_interface_loads_are_recomputed_without_another_solve(monkeypatch):
    model=cantilever();F=np.zeros(12);F[8]=-1000.
    loads=dict(upper_mass_kg=10.,approved_limits=None)
    cases=[('control',F,{})];response=s.solve(model,cases)
    monkeypatch.setattr(s,'build_model',lambda *a,**kw:(model,[]))
    monkeypatch.setattr(s,'load_cases',lambda *a,**kw:(cases,loads))
    request=dict(vehicle={},mesh_sizes_m=[1.],joint_translation_N_m=1e9,joint_rotation_Nm_rad=1e6,material_scale=1.,contact_gap_hypothesis_m=.04)
    worker=dict(results=[dict(mesh_m=1.,model=deepcopy(model),loads=loads,response=deepcopy(response))])
    s._verify_responses(request,worker)
    worker['results'][0]['response']['cases'][0]['support_reactions'][0]['reaction']=123.
    with pytest.raises(ValueError,match='arithmetic'):s._verify_responses(request,worker)
    worker['results'][0]['model']['elements'][0]['E']/=2
    with pytest.raises(ValueError,match='semantic'):s._verify_responses(request,worker)


def test_no_published_typical_stiffness_becomes_a_strength_or_hot_wet_allowable():
    assert all('hexcel.com' in r['url'] or 'hulamin.com' in r['url'] for r in s.PRIMARY_SOURCES)
    assert 'hypothesis' in s.MATERIALS['GFRP']['basis']
    assert not any('allowable' in k for m in s.MATERIALS.values() for k in m)
