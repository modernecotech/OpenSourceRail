from pathlib import Path
import gzip,json
import pytest
import numpy as np
from engineering.sourced_case import structure as p
from engineering.sourced_case import whole_structure as w
from engineering.component_registry import validate_registry
ROOT=Path(__file__).resolve().parents[3]
CACHE=Path('/home/hayder/.local/state/opensourcerail/reference-cell-native-20261028/vehicles')

@pytest.fixture(scope='module')
def base():
    value=json.loads(gzip.decompress((CACHE/'V1.json.gz').read_bytes()))
    return p.revision(value,root=ROOT)

@pytest.fixture(scope='module')
def revised(base):return w.revision(base,root=ROOT)


def test_3d_timoshenko_cantilever():
    L=2.;EI=6000.;S=1e6;F=1000.
    e=dict(a=0,b=1,EA=1e8,EIy=EI,EIz=EI,GJ=1000.,Sy=S,local_y=[0.,1.,0.])
    K,_,_=w._element_k(e,[[0.,0.,0.],[L,0.,0.]])
    load=np.zeros(12);load[8]=-F
    u=np.linalg.solve(K[6:,6:],load[6:])
    assert abs(u[2])==pytest.approx(F*L**3/(3*EI)+F*L/S)
    assert np.allclose(K,K.T)


def test_physical_revision_counts_3d_splices_and_retention(base,revised):
    validate_registry(revised['registry'])
    assert revised['candidate_id']!=base['candidate_id']
    a=revised['whole_body_revision_ancestry']
    assert a['parent_candidate_id']==base['candidate_id'] and a['initial_components']>1
    assert a['added_occurrences_per_car']>0 and a['mass_upper_delta_per_car_kg']>0
    assert all(x['bolts_per_end']==2 and not x['qualified_joint'] for x in a['counted_splice_plans'])
    assert revised['requirements']==base['requirements']
    assert all(revised[k] is False for k in w.FLAGS)


def test_layered_strip_stiffness_and_actual_contact_graph(revised):
    model,rows,panels=w.build(revised,1.5)
    assert any(e.get('Sy') for e in model['elements'])
    assert all(l['footprint_area_m2']>0 and not l['qualified_joint'] for l in model['links'])
    assert len(model['support_nodes'])==4
    assert np.allclose(np.array(model['nodes'])[model['support_nodes']],revised['interfaces']['body_secondary_hardpoint_positions_m'])
    assert len(model['components'])==1,[(len(c),c[:2]) for c in model['components']]
    assert all(len(row['transform'])==4 for row in revised['registry']['occurrences'])


def test_equipment_and_pax_routing_conserves_forces_moments(revised):
    model,rows,panels=w.build(revised,1.5);cases,mass=w.loads(revised,model,rows,panels)
    F=dict(cases)['normal-upper'].reshape(-1,6)
    assert F[:,:3].sum(axis=0)[2]==pytest.approx(-(mass['supported_upper_mass_kg']+3450)*w.G)
    xyz=np.array(model['nodes']);moment=(F[:,3:]+np.cross(xyz,F[:,:3])).sum(axis=0)
    assert np.isfinite(moment).all()
    assert all(r['mass_upper_kg']>0 for r in mass['upper_mass_bindings'])


def test_bounded_request_identity_no_baseline_promotion(revised):
    a=w.request(revised,root=ROOT,mesh_m=1.2);b=w.request(revised,root=ROOT,mesh_m=1.5)
    assert a['candidate_id']==b['candidate_id'] and a['request_id']!=b['request_id']
    with pytest.raises(ValueError):w.request(revised,root=ROOT,mesh_m=.1)
