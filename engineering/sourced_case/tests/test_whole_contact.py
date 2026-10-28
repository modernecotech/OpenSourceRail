from pathlib import Path
import json,numpy as np,pytest
from engineering.sourced_case import whole_contact as w
from engineering.sourced_case import whole_refinement as previous
ROOT=Path(__file__).resolve().parents[3]
from engineering.sourced_case.tests.portable_fixtures import published


def test_independent_continuous_three_piece_I_section():
    b=w.continuous_I_section_benchmark()
    assert b['benchmark_pass']
    assert b['runs'][1]['quadrature_points']==2*b['runs'][0]['quadrature_points']
    assert all(x['relative_energy_error']<1e-9 and x['maximum_contact_slip_m']<1e-12 for x in b['runs'])


def test_beam_interpolation_rigid_modes_and_Timoshenko_endpoint():
    e=dict(a=0,b=1,EA=1e8,EIy=6000.,EIz=8000.,GJ=1000.,Sy=1e6,local_y=[0.,1.,0.]);nodes=[[0.,0.,0.],[2.,0.,0.]]
    for x in (0.,.4,1.,2.):
        N,c=w.beam_section_shape(e,nodes,[x,0.,0.]);u=np.array([0.,0.,0.,0.,-1.,0.,0.,0.,2.,0.,-1.,0.]);assert (N@u)[2]==pytest.approx(x)
        assert np.allclose((N@u)[3:],[0.,-1.,0.])
    N,_=w.beam_section_shape(e,nodes,nodes[0]);assert np.allclose(N[:,:6],np.eye(6));assert np.allclose(N[:,6:],0.)


def test_contact_partition_area_and_mesh_refinement():
    for divisions in (4,8):
        nodes=np.array([[2*i/divisions,0.,0.] for i in range(divisions+1)])
        group=dict(nodes=list(range(len(nodes))))
        q=list(w.contact_quadrature(group,group,np.array([0.,-.004,0.]),np.array([2.,.004,0.]),2,nodes))
        assert len(q)==8*divisions
        assert sum(a for _,a in q)==pytest.approx(.016)
        for i in range(divisions):assert sum(i*2/divisions<x[0]<(i+1)*2/divisions for x,_ in q)==8


def test_same_physical_candidate_new_evaluation_and_real_dimensions():
    vehicle=published('equipped-v1')
    req=w.request(vehicle,mesh_m=1.2,root=ROOT);old=previous.request(vehicle,mesh_m=1.2,root=ROOT)
    assert req['candidate_id']==old['candidate_id'] and req['request_id']!=old['request_id']
    model,rows,panels=w.build(vehicle,1.5)
    assert len(model['components'])==1
    assert all(j['rank']==6 for j in model['joint_mechanical_rank'])
    sourcepair={'car-1/underframe-web/48','car-1/underframe-flange/49'}
    contact=[link for link in model['links'] if set(link['source_pair'])==sourcepair]
    assert len(contact)>40
    assert sum(link['footprint_area_m2'] for link in contact)==pytest.approx(16.8*.008)
    assert all(len(link['dofs'])>=12 and np.asarray(link['interpolation_B']).shape==(3,len(link['dofs'])) for link in contact)
    for group in model['groups']:
        if group['kind']=='sandwich':assert np.ptp(np.asarray(model['nodes'])[group['nodes']],axis=0)[:2]==pytest.approx([4.18,2.65])


def test_sandwich_interpolation_is_mid_surface_field_plus_normal_offset():
    nodes=[[0.,0.,1.],[0.,1.,1.],[1.,0.,1.],[1.,1.,1.]]
    group=dict(kind='sandwich',nodes=[0,1,2,3],grid=dict(nx=1,ny=1,indices={'0,0':0,'0,1':1,'1,0':2,'1,1':3}))
    ids,N=w.contact_mapping(group,[.5,.5,1.],nodes,[])
    assert np.allclose(N[:,[3,4,5,9,10,11,15,16,17,21,22,23]],0.)
    u=np.zeros(24)
    for i,p in enumerate(nodes):u[6*i+2]=p[0]**2/2;u[6*i+4]=p[0]
    assert (N@u)[2]==pytest.approx(.25)
    ids,N=w.contact_mapping(group,[.5,.5,1.1],nodes,[])
    assert (N@u)[0]==pytest.approx(.05)


def test_sparse_array_assembly_preserves_exact_element_stiffness():
    e=dict(a=0,b=1,EA=1e8,EIy=6000.,EIz=8000.,GJ=1000.,Sy=1e6,local_y=[0.,1.,0.])
    nodes=[[0.,0.,0.],[2.,0.,0.]]
    model=dict(nodes=nodes,elements=[e],links=[])
    assert np.array_equal(w.assemble(model).toarray(),w._element_k(e,nodes)[0])
