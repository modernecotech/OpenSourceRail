"""Small explicit physical revision controls; no FE or candidate campaign."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import subprocess

import numpy as np
import pytest

from engineering.design_search import topology_geometry as geometry
from engineering.station_rail.common import identity

_spec=importlib.util.spec_from_file_location('engineering.design_search.topology_revisions',
    Path(__file__).resolve().parents[1]/'topology_revisions.py')
r=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(r)


def inputs(mask=None,passive=None,rho=None):
    if mask is None:
        mask=np.zeros((6,6),dtype=bool);mask[[0,-1],:]=True;mask[:,[0,-1]]=True;mask[2,2]=True
    if passive is None:
        passive=np.zeros_like(mask);passive[[0,-1],:]=True;passive[:,[0,-1]]=True
    rho=np.full(mask.shape,.5) if rho is None else rho
    parent=geometry.realize(mask)
    binding=r.make_parent_input(parent,mask,rho,passive,parent_evaluation_id='a'*64,
        parent_request_id='b'*64,arrays_package_sha256='c'*64,
        required_passive_cell_ids=np.flatnonzero(passive).tolist())
    return binding,parent,mask,rho,passive


def test_remove_only_islands_retains_parent_and_creates_separate_physical_revision_identity():
    values=inputs();before=deepcopy(values)
    out=r.propose(*values,strategy='retain-mandatory-component')
    assert out['execution']=='proposal-generated' and out['removed_cell_ids']==[14]
    assert out['added_cell_ids']==[]
    assert out['parent_candidate_id']==values[1]['candidate_id']
    assert out['parent_evaluation_id']=='a'*64 and out['parent_request_id']=='b'*64
    assert out['proposed_candidate_id']!=out['parent_candidate_id']
    assert len({out['proposed_candidate_id'],out['revision_id'],out['evaluation_id']})==3
    assert out['proposed_geometry']['web_geometry']['finite_edge_components']==1
    assert np.all(np.asarray(out['occupancy'])[values[4]])
    assert out['numerical_evaluation_execution']=='not-run' and out['installed_mass_complete'] is False
    assert all(out[k] is False for k in r.FLAGS)
    assert values[0]==before[0] and values[1]==before[1]
    for a,b in zip(values[2:],before[2:]):np.testing.assert_array_equal(a,b)


def test_connection_prefers_high_original_density_and_deterministic_equal_cost_ties():
    values=inputs();values[3][1,2]=.9;values[3][2,1]=.1
    # The changed observed density needs a fresh parent-input binding.
    values=inputs(values[2],values[4],values[3])
    a=r.propose(*values,strategy='connect-all-stock')
    b=r.propose(*values,strategy='connect-all-stock')
    assert a==b
    assert a['execution']=='proposal-generated' and a['removed_cell_ids']==[]
    assert a['added_cell_ids']==[8]
    assert a['decisions'][0]['path_cell_ids']==[2,8,14]
    assert np.all(np.asarray(a['occupancy'])[values[2]])
    ties=inputs();out=r.propose(*ties,strategy='connect-all-stock')
    assert out['added_cell_ids']==[8]


@pytest.mark.parametrize('strategy',r.STRATEGIES)
def test_every_corner_contact_closes_with_explicit_added_stock(strategy):
    mask=np.array([[1,1,1],[1,0,1],[0,1,1]],dtype=bool)
    passive=mask.copy();rho=np.full(mask.shape,.4);rho[1,1]=.9;rho[2,0]=.1
    out=r.propose(*inputs(mask,passive,rho),strategy=strategy)
    assert out['added_cell_ids']==[4]
    assert out['removed_cell_ids']==[]
    assert out['proposed_geometry']['web_geometry']['corner_only_contacts']==0
    assert any(row['kind']=='close-corner-contact' for row in out['decisions'])


def test_split_mandatory_stock_cannot_be_removed_but_can_be_explicitly_connected():
    mask=np.array([[1,0,1]],dtype=bool);passive=mask.copy()
    values=inputs(mask,passive)
    rejected=r.propose(*values,strategy='retain-mandatory-component')
    assert rejected['failure_reason']=='mandatory-stock-spans-multiple-components'
    assert rejected['proposed_geometry'] is None and rejected['removed_cell_ids']==[]
    added=r.propose(*values,strategy='connect-all-stock')
    assert added['added_cell_ids']==[1] and added['removed_cell_ids']==[]
    assert added['proposed_geometry']['web_geometry']['finite_edge_components']==1


@pytest.mark.parametrize('strategy',r.STRATEGIES)
def test_physically_unchanged_proposal_is_rejected(strategy):
    values=inputs(np.ones((3,3),dtype=bool))
    result=r.propose(*values,strategy=strategy)
    assert result['failure_reason']=='physically-identical-no-change'
    assert result['proposed_candidate_id'] is None


@pytest.mark.parametrize('damage',('source','mask','density','passive','binding'))
def test_mixed_or_tampered_parent_inputs_are_rejected(damage):
    binding,parent,mask,rho,passive=inputs()
    if damage=='source':
        parent['source_sha256'][geometry.PRODUCER]='0'*64
        parent['geometry_id']=identity({k:v for k,v in parent.items() if k!='geometry_id'})
    elif damage=='mask':mask[2,2]=False
    elif damage=='density':rho[1,1]=.7
    elif damage=='passive':passive[0,0]=False
    else:binding['parent_evaluation_id']='d'*64
    with pytest.raises(ValueError):r.propose(binding,parent,mask,rho,passive,strategy=r.STRATEGIES[0])


def test_required_cells_missing_or_undeclared_are_rejected():
    binding,parent,mask,rho,passive=inputs()
    with pytest.raises(ValueError,match='mandatory cells'):
        r.make_parent_input(parent,mask,rho,passive,parent_evaluation_id='a'*64,parent_request_id='b'*64,
            arrays_package_sha256='c'*64,required_passive_cell_ids=[0])
    passive[1,1]=True
    with pytest.raises(ValueError,match='must exist'):
        r.make_parent_input(parent,mask,rho,passive,parent_evaluation_id='a'*64,parent_request_id='b'*64,
            arrays_package_sha256='c'*64,required_passive_cell_ids=np.flatnonzero(passive).tolist())


def test_huge_invalid_and_budget_limited_inputs_fail_without_dispatch(monkeypatch):
    values=inputs()
    def forbidden(*args,**kwargs):pytest.fail('No numerical/native dispatch permitted')
    monkeypatch.setattr(subprocess,'run',forbidden);monkeypatch.setattr(subprocess,'Popen',forbidden)
    for kwargs,reason in [(dict(maximum_operations=1),'operation-budget'),(dict(time_budget_s=1e-12),'time-budget')]:
        result=r.propose(*values,strategy=r.STRATEGIES[1],**kwargs)
        assert result['failure_reason']==reason and result['proposed_geometry'] is None
    huge=np.zeros((100,100),dtype=bool)
    with pytest.raises(ValueError,match='element budget'):
        r.propose(values[0],values[1],huge,np.zeros_like(huge,dtype=float),huge,strategy=r.STRATEGIES[0],maximum_elements=7680)
    rho=values[3].copy();rho[0,0]=np.nan
    with pytest.raises(ValueError,match='Finite original density'):
        r.propose(values[0],values[1],values[2],rho,values[4],strategy=r.STRATEGIES[0])
