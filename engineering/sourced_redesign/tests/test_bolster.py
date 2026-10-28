from pathlib import Path
import json
import numpy as np
import pytest
from engineering.component_registry import validate_registry
from engineering.sourced_redesign import bolster as b
from engineering.sourced_case import layered_structure as layer
from engineering.sourced_case import whole_contact as whole
ROOT=Path(__file__).resolve().parents[3]

@pytest.fixture(scope='module')
def parent():
    path=Path('/home/hayder/.local/state/opensourcerail/sourced-whole-contact-20261028/V4/input.json')
    if not path.exists():pytest.skip('Exact immutable V4 numerical input unavailable')
    return json.loads(path.read_text())['vehicle']

@pytest.fixture(scope='module')
def revised(parent):return b.revision(parent,root=ROOT)


def test_revision_identity_mass_equipment_and_requirements(parent,revised):
    validate_registry(revised['registry'])
    assert revised['candidate_id']!=parent['candidate_id']
    assert revised['registry']['parent_candidate_id']==parent['candidate_id']
    assert revised['requirements']==parent['requirements']
    assert revised['per_car_mass_properties']['mass_upper_bound_kg']>parent['per_car_mass_properties']['mass_upper_bound_kg']
    assert all(revised[k] is False for k in b.FLAGS)
    assert revised['bolster_revision']['closed_torsion_box'] is False
    assert revised['bolster_revision']['physical_joint_allowables'] is None
    layer._vehicle(revised)


def test_all_four_pads_and_both_rail_webs_are_located(revised):
    interfaces=revised['bolster_revision']['interfaces']
    assert len(interfaces)==4
    assert {tuple(i['pad_center_m']) for i in interfaces}=={(x,y,.78) for x in (2.9,14.1) for y in (-.95,.95)}
    assert all(i['pad_top_z_m']==pytest.approx(i['bolster_bottom_z_m']) and i['bolts']==4 for i in interfaces)
    records=revised['bolster_revision']['rail_clearance_definitions']
    assert {(r['bogie_x_m'],r['web_y_m']) for r in records}=={(x,y) for x in (2.9,14.1) for y in (-1.15,1.15)}


def test_primitive_copes_avoid_parent_rail_and_rib_solids(parent,revised):
    original=layer._rows(parent);now=layer._rows(revised)
    obstacles=[r for r in original if layer._is(r,'underframe-web') or layer._is(r,'underframe-flange') or layer._is(r,'transverse-floor-member') or r['occurrence']['occurrence_id'].split('/')[1].startswith('floor-rib-cap-')]
    new=[r for r in now if '/bolster-' in r['occurrence']['occurrence_id'] and r['part']['geometry']['kind']=='box']
    for a in new:
        for o in obstacles:
            overlap=np.minimum(a['upper'],o['upper'])-np.maximum(a['lower'],o['lower'])
            assert not np.all(overlap>1e-9),(a['occurrence']['occurrence_id'],o['occurrence']['occurrence_id'],overlap)
    assert all(r['part']['mass']['calculated_kg']>0 for r in new)


def test_superseded_local_doublers_and_splices_are_removed(parent,revised):
    names=[o['occurrence_id'] for o in revised['registry']['occurrences']]
    assert not any('/hardpoint-local-doubler/' in x for x in names)
    removed=revised['bolster_revision']['removed_local_names']
    assert len(removed)>4
    assert all(not any(x.endswith('/'+old) for x in names) for old in removed)
    assert len(revised['manufacturing_plan'])==len(revised['registry']['parts'])


def test_finite_loadpath_contact_graph_and_access(revised):
    model,rows,panels=whole.build(revised,1.5)
    assert len(model['components'])==1
    assert all(j['rank']==6 for j in model['joint_mechanical_rank'])
    for pad in revised['bolster_revision']['interfaces']:
        assert any(pad['pad_occurrence_id'] in link['source_pair'] and any('bottom-plate' in x for x in link['source_pair']) for link in model['links'])
    assert len([a for a in revised['assembly_access'] if a.get('id','').startswith('bolster-service-')])==2
    assert all(not a['clearance_and_lifting_verified'] for a in revised['assembly_access'] if a.get('id','').startswith('bolster-service-'))


def test_reject_wrong_physical_parent(parent):
    fake=dict(parent,candidate_id='0'*64)
    with pytest.raises(ValueError):b.revision(fake,root=ROOT)
