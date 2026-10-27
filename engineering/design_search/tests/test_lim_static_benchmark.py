"""Pure export/operator contracts; native comparisons are separately budgeted."""
from copy import deepcopy
from pathlib import Path
import json
import numpy as np
import pytest
from engineering.design_search import moving_lim as moving,lim_static_benchmark as static


@pytest.fixture(scope='module')
def parent():
    # Same deterministic canonical parent geometry, without a host evidence path.
    from engineering.design_search import railway_bundle,design_grammar
    return moving.request(railway_bundle.materialize(design_grammar.initial_candidates()[0]),speed_m_s=20.,frequency_Hz=50.,dt_s=.00025,steps=64,transport_method='supg-coth',mesh_family='entry-local-tensor',critical_dx_m=.005,secondary_dy_m=.0009375)


@pytest.fixture(scope='module')
def data(parent):return static.mesh_data(parent)


def test_signed_sources_have_independent_normalization_and_exact_mesh(parent,data):
    points,tri,reg,boundary,branch,sign,area,grad,tags,outer=data
    assert len(points)==44643 and len(tri)==87856 and len(outer)==len(boundary)==1428
    assert len(set(tags))==62
    assert sum(area[tags==1000])==pytest.approx(5*.04*.055)
    assert sum(area[tags==1001])==pytest.approx(5*.04*.055)
    I=np.r_[1.,np.zeros(29)];value=static.reference(parent,I,data,solve=False,A=np.zeros(len(points)))
    assert sum(area[tags==1000]*value['J'][tags==1000])==pytest.approx(200.)
    assert sum(area[tags==1001]*value['J'][tags==1001])==pytest.approx(-200.)
    assert area@value['J']==pytest.approx(0.,abs=1e-10)
    assert max(abs(value['J']))==pytest.approx(40/(.04*.055))
    assert value['energy_per_m_J_m']==0.
    assert static.case_requests(parent,np.zeros(30))[3]['context']['circuit'] is False


def test_msh_export_retains_coordinates_connectivity_and_typed_groups(parent,data):
    points,tri,reg,bnd,branch,sign,area,grad,tags,outer=data
    text=static.msh_text(points,tri,tags,outer);lines=text.splitlines();ni=lines.index('$Nodes');ei=lines.index('$Elements')
    nodes=np.asarray([list(map(float,row.split()[1:3])) for row in lines[ni+2:ni+2+len(points)]])
    assert np.array_equal(nodes,points)
    cells=[list(map(int,row.split())) for row in lines[ei+2:ei+2+len(tri)]]
    assert np.array_equal(np.asarray([row[5:] for row in cells])-1,tri)
    assert np.array_equal([row[3] for row in cells],tags)
    assert int(lines[ei+1])==len(tri)+len(outer)


def test_case_identity_and_linear_static_hypotheses_are_separate(parent):
    cases=static.case_requests(parent,np.arange(30)/30)
    assert len({r['request_id'] for r in cases})==4
    assert all(r['context']['motor_component_id']==parent['motor_component_id'] for r in cases)
    assert cases[2]['path_currents_A']==(-np.asarray(cases[1]['path_currents_A'])).tolist()
    assert cases[3]['path_currents_A']==[1.]+[0.]*29
    assert all(r['physical_accepted'] is r['operating_map_admitted'] is False for r in cases)
    assert all(r['context']['linear_steel_relative_mu']==1000. and r['context']['secondary_eddy_current'] is False for r in cases)
    with pytest.raises(ValueError):static.case_requests(parent,[1.]*29)
    with pytest.raises(ValueError):static.case_requests(parent,[float('nan')]*30)


def test_generated_getdp_uses_independent_static_operator_and_no_motion(parent):
    text=static.formulation(parent,[1.]+[0.]*29)
    assert 'BF_PerpendicularEdge' in text and 'nu[Steel]=1/(1000*mu0)' in text
    assert 'js[Region[1000]]=Vector[0,0,18181.81818181818' in text
    assert 'js[Region[1001]]=Vector[0,0,-18181.81818181818' in text
    assert 'DtDof' not in text and 'sigma' not in text and 'SUPG' not in text
    assert 'Format NodeTable' in text and 'Format ElementTable' in text


def test_output_tables_are_complete_and_reject_duplicate_or_nonconstant_cells(tmp_path):
    a=tmp_path/'a';a.write_text('3\n1 0\n2 .2\n3 -.1\n');assert static.node_table(a,3).tolist()==[0,.2,-.1]
    a.write_text('3\n1 0\n2 .2\n2 -.1\n')
    with pytest.raises(ValueError,match='Duplicate'):static.node_table(a,3)
    b=tmp_path/'b';b.write_text('2\n1 1 2 0\n2 3 4 0 3 4 0 3 4 0\n');assert static.element_table(b,2).tolist()==[[1,2,0],[3,4,0]]
    b.write_text('1\n1 1 2 0 2 2 0 1 2 0\n')
    with pytest.raises(ValueError,match='not constant'):static.element_table(b,1)


def test_reference_linear_energy_and_source_work_are_independent_algebra(parent,data):
    # No field solve: manufactured A exercises nu/height/source conventions.
    points,tri,reg,bnd,branch,sign,area,grad,tags,outer=data
    A=2*points[:,0]-3*points[:,1];r=static.reference(parent,np.zeros(30),data,solve=False,A=A)
    assert r['B'][:,0]==pytest.approx(-3.) and r['B'][:,1]==pytest.approx(-2.)
    expected=sum(area*np.where(reg==3,1/(static.transient.MU0*1000),1/static.transient.MU0))*13/2
    assert r['energy_per_m_J_m']==pytest.approx(expected)
    assert r['source_work_per_m_J_m']==0.
