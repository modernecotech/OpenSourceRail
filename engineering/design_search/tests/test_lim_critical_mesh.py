"""Independent local-mesh resolution, material and same-candidate controls."""
from copy import deepcopy
from pathlib import Path
import json
import numpy as np
import pytest
from engineering.design_search import moving_lim as m,lim_critical_mesh as c,design_grammar,railway_bundle,transient_lim


@pytest.fixture(scope='module')
def bundle():return railway_bundle.materialize(design_grammar.initial_candidates()[0])


def case(bundle,dx=.02,dy=.00375,**extra):
    return m.request(bundle,speed_m_s=20.,frequency_Hz=50.,dt_s=.001,steps=16,
        transport_method='supg-coth',mesh_family=c.NAME,critical_dx_m=dx,secondary_dy_m=dy,**extra)


def test_streamwise_and_secondary_refinement_are_independent_and_real(bundle):
    coarse=case(bundle);xonly=case(bundle,.01);yonly=case(bundle,dy=.001875);both=case(bundle,.01,.001875);fine=case(bundle,.005,.0009375)
    estimates=[m.estimate(r) for r in (coarse,xonly,yonly,both,fine)]
    grids=[e['active_grid'] for e in estimates]
    assert grids[1]['maximum_dx_in_engaged_primary_m']<grids[0]['maximum_dx_in_engaged_primary_m']
    assert grids[1]['maximum_dy_in_secondary_m']==grids[0]['maximum_dy_in_secondary_m']
    assert grids[2]['maximum_dx_in_engaged_primary_m']==grids[0]['maximum_dx_in_engaged_primary_m']
    assert grids[2]['maximum_dy_in_secondary_m']<grids[0]['maximum_dy_in_secondary_m']
    assert grids[4]['maximum_dx_in_engaged_primary_m']<grids[3]['maximum_dx_in_engaged_primary_m']
    assert grids[4]['maximum_dy_in_secondary_m']<grids[3]['maximum_dy_in_secondary_m']
    assert all(e['nodes']<75000 for e in estimates)
    assert len({r['request_id'] for r in (coarse,xonly,yonly,both,fine)})==5
    assert len({r['evaluated_component_definition_id'] for r in (coarse,xonly,yonly,both,fine)})==1
    assert coarse['schema']=='osr-moving-LIM-request/3'
    assert coarse['operating_hypothesis']['nominal_slip_frequency_Hz']==10.
    assert coarse['operating_hypothesis']['nominal_synchronous_speed_m_s']==25.
    assert coarse['operating_hypothesis']['transient_force_sign_guaranteed'] is False


def test_fixed_remote_grid_material_boundaries_and_exact_stock_are_preserved(bundle):
    r=case(bundle,.005,.0009375);points,tri,regions,boundary,branch,sign=m.mesh(r)
    area,grad=transient_lim.geometry(points,tri);p=r['physical_geometry']
    assert np.sum(area[branch>=0])==pytest.approx(300*.04*.055,rel=1e-10)
    expected_steel=2*(12.5*(.055+.025)-150*.04*.055)
    assert np.sum(area[regions==3])==pytest.approx(expected_steel,rel=1e-10)
    for k in range(30):
        assert np.sum(area[branch==k])==pytest.approx(10*.04*.055,rel=1e-10)
        assert np.sum(area[branch==k]*sign[branch==k])==pytest.approx(0.,abs=1e-12)
    x,y=m._mesh_axes(r)
    assert any(np.isclose(y,.0075,rtol=0,atol=1e-13)) and any(np.isclose(y,.0225,rtol=0,atol=1e-13))
    for start in (-8.95,-8.63):
        m0,m1,m2=m.conductor_moments(points,tri,area,start,9.,.015)
        assert sum(m0)==pytest.approx(.135,abs=1e-11)
        assert np.einsum('ti,ti->',m1,points[tri][:,:,0])/.135==pytest.approx(start+4.5,abs=1e-10)
    a,b=m._mesh_axes(case(bundle)),m._mesh_axes(case(bundle,.005,.0009375))
    assert a[0][a[0]>1.0].tolist()==b[0][b[0]>1.0].tolist()
    fingerprint=m.mesh_fingerprint(points,tri,regions,boundary,branch,sign)
    assert fingerprint['points']['shape']==list(points.shape)
    changed=points.copy();changed[0,0]+=.0001
    assert m.mesh_fingerprint(changed,tri,regions,boundary,branch,sign)['mesh_discretization_id']!=fingerprint['mesh_discretization_id']


@pytest.mark.parametrize('mutation',['window','remote','identity','outside'])
def test_resealed_mesh_or_uncovered_entry_cannot_borrow_critical_definition(bundle,mutation):
    r=case(bundle)
    if mutation=='window':r['mesh_definition']['critical_window_m']=[0.,.1]
    elif mutation=='remote':r['mesh_definition']['far_primary_dx_m']=.5
    elif mutation=='identity':r['mesh_definition']['mesh_definition_id']='a'*64
    else:r['start_m']=1.
    r.pop('request_id');r['request_id']=m.identity(r)
    with pytest.raises(ValueError):m.validate(r)


def test_legacy_request_shape_and_case_semantics_are_unchanged(bundle):
    old=m.request(bundle,speed_m_s=20.,dt_s=.001,steps=16,transport_method='supg-coth')
    assert old['schema']=='osr-moving-LIM-request/2' and 'mesh_definition' not in old and 'operating_hypothesis' not in old
    assert old['request_id']=='ee21f69417358c993cd6b7a247cc83e37bea35021950387a91caeeb476582c21'
    m.validate(old)
    with pytest.raises(ValueError,match='matching numerical variables'):m.request(bundle,critical_dx_m=.01)


def test_remote_grid_transport_range_has_an_independent_steady_scalar_control():
    # The remote fin uses ~0.15m cells, so its high-Pe scalar limit must be
    # checked too. This control says nothing about full 2D field convergence.
    n=8;h=.15;L=n*h;v=20.;diff=1/(transient_lim.MU0*20e6)
    g=np.tile([-1/h,1/h],(n,1));area=np.full(n,h);first=np.full((n,2),h/2)
    o=m.lim_transport.operators(area,first,g,sigma=1.,speed=v,diffusivity=diff,name='supg-coth')
    K=np.zeros((n+1,n+1));rhs=np.zeros(n+1)
    for i in range(n):K[i:i+2,i:i+2]+=diff*h*np.outer(g[i],g[i])+v*np.outer(first[i],g[i])+o['transport'][i]
    K[0,:]=0;K[-1,:]=0;K[0,0]=K[-1,-1]=1;rhs[-1]=1
    x=np.linspace(0,L,n+1);exact=(np.exp((v/diff)*(x-L))-np.exp(-(v/diff)*L))/(1-np.exp(-(v/diff)*L))
    assert np.max(o['streamline_Peclet'])>37
    assert np.linalg.solve(K,rhs)==pytest.approx(exact,abs=1e-12)
