"""Installed-record integrity and rigid-body arithmetic, no physical evidence."""
from copy import deepcopy
import numpy as np
import pytest
from engineering.design_search import equipped_candidates as e, design_grammar as g, railway_bundle


@pytest.fixture(scope='module')
def parent():
    body=g.build(g.parameters())
    return body,railway_bundle.materialize(body,family='P1')


def sealed(record):
    value=deepcopy(record);value.pop('record_id',None);value['record_id']=e.identity(value);return value


def record(tmp_path,parent):
    body,bundle=parent;account=body['retained_equipment_accounts'][0]
    geometry=tmp_path/'method.step';geometry.write_text('Synthetic source-byte fixture, not CAD evidence.\n')
    ref=dict(path=geometry.name,sha256=e.digest(geometry))
    pose=dict(frame_id='vehicle',translation_m=[2.,3.,4.],rotation=[[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
    return sealed(dict(schema=e.SCHEMA,parent_bundle_id=bundle['bundle_id'],body_candidate_id=body['candidate_id'],
        component_occurrence_id=account['id'],parent_component_definition_id=account['component_definition_id'],
        evidence_kind='synthetic-method-test',assembly_mass_includes_hardware_and_services=True,source_locator='Synthetic method fixture only',source_files=[ref],
        physical_definition=dict(local_frame=dict(id='assembly',unit='m',axes='right-handed orthonormal',origin_m=[0.,0.,0.]),native_geometry=ref,occupied_bounds_m=dict(min_m=[-1.,-2.,-3.],max_m=[1.,2.,3.]),
            hardware=[dict(occurrence_id='fixture/mounting-bolt',kind='fastener',quantity=4,included_mass_kg=1.,positions_local_m=[[-.5,-.5,0.],[.5,-.5,0.],[-.5,.5,0.],[.5,.5,0.]])],services=[]),
        installed_transform=pose,nominal_mass_kg=12.,mass_interval_kg=[11.,13.],local_CG_m=[0.,0.,0.],
        local_CG_inertia_kg_m2=[[52.,0.,0.],[0.,40.,0.],[0.,0.,20.]],
        access=dict(installation_path=[pose],removal_path=[pose],tool_envelopes=[dict(frame_id='vehicle',bounds_m=dict(min_m=[-1.,-1.,-1.],max_m=[1.,1.,1.]))],
            lifting=dict(rated_capacity_kg=20.,source=ref,lifting_points_local_m=[[-.5,0.,0.],[.5,0.,0.]]),sequence=['isolate services','support assembly','remove mounting bolts','remove assembly']),
        qualification_record_reference=None))


def test_three_physical_families_remain_incomplete_and_same_bundle():
    result=e.comparison()
    assert len({r['body']['candidate_id'] for r in result['candidates']})==3
    assert {r['body']['parameters']['family'] for r in result['candidates']}=={'aluminium_frame','aluminium_stressed_skin','gfrp_semimonocoque'}
    for row in result['candidates']:
        p=row['projection'];b=row['bundle']
        assert p['parent_bundle_id']==b['bundle_id'] and p['body_candidate_id']==b['body_candidate_id']
        assert p['complete_installed_mass_kg'] is None and p['complete_installed_CG_m'] is None and p['complete_installed_inertia_kg_m2'] is None
        assert p['unresolved_component_occurrence_ids'] and p['remaining_unlocated_account_mass_kg']>0
        assert all(v is None for v in p['total_installed_hardware_counts'].values())
        assert not p['physical_journey_mass_admitted'] and not p['structural_status']['qualified']
        assert p['engineering_BOM'] and p['manufacturing_BOM'] and p['assembly_dependencies']
        assert p['declared_body_joint_count']==len(row['body']['joins'])>0
        assert p['located_body_stock_occurrence_count']==len(row['body']['parts'])>0
    assert result['complete_equipped_candidates']==0 and result['integrated_winner'] is None


def test_transform_inertia_and_parallel_axis_are_independent_of_account(parent,tmp_path):
    body,bundle=parent;r=record(tmp_path,parent)
    result=e.evaluate(bundle,body,assembly_records=[r],source_root=tmp_path,allow_synthetic=True)
    row=result['imported_assembly_records'][0]
    assert row['vehicle_CG_m']==[2.,3.,4.]
    assert np.allclose(row['vehicle_CG_inertia_kg_m2'],np.diag([40.,52.,20.]))
    stock=result['parent_engineering_BOM'];old=next(x for x in stock if x['id']==r['component_occurrence_id'])
    assert old['accounted_mass_kg']!=12.
    proposal=next(x for x in result['engineering_BOM'] if x['id']==r['component_occurrence_id'])
    assert proposal['nominal_mass_kg']==12. and proposal['scope']=='installed-assembly-proposal'
    assert sum(x['id']==r['component_occurrence_id'] for x in result['engineering_BOM'])==1
    own=e._aggregate([dict(mass_kg=2.,CG_m=[-1.,0.,0.],CG_inertia_kg_m2=np.diag([1.,2.,2.])),dict(mass_kg=2.,CG_m=[1.,0.,0.],CG_inertia_kg_m2=np.diag([1.,2.,2.]))])
    assert own['CG_m']==[0.,0.,0.] and np.allclose(own['CG_inertia_kg_m2'],np.diag([2.,8.,8.]))
    assert result['canonical_bundle_propagation_required'] and result['physical_revision_required']
    assert result['complete_installed_mass_kg'] is None and not result['source_authentication_verified']
    assert result['complete_installed_manufacturing_BOM'] is None
    assert result['manufacturing_BOM_scope'].startswith('Parent body gross-stock')


def test_wrong_bundle_definition_duplicate_scope_and_synthetic_default_rejected(parent,tmp_path):
    body,bundle=parent;r=record(tmp_path,parent)
    with pytest.raises(ValueError,match='Synthetic'):e.evaluate(bundle,body,assembly_records=[r])
    for field,value in [('parent_bundle_id','0'*64),('body_candidate_id','0'*64),('parent_component_definition_id','0'*64)]:
        bad=sealed({**r,field:value})
        with pytest.raises(ValueError):e.evaluate(bundle,body,assembly_records=[bad],source_root=tmp_path,allow_synthetic=True)
    with pytest.raises(ValueError,match='counted more than once'):
        e.evaluate(bundle,body,assembly_records=[r,r],source_root=tmp_path,allow_synthetic=True)
    bad=deepcopy(r);bad['component_occurrence_id']=body['parts'][0]['id'];bad['parent_component_definition_id']=next(x['component_definition_id'] for x in body['components'] if x['occurrence_id']==bad['component_occurrence_id'])
    with pytest.raises(ValueError,match='body stock'):e.evaluate(bundle,body,assembly_records=[sealed(bad)],source_root=tmp_path,allow_synthetic=True)


def test_nonrigid_transform_unphysical_inertia_and_insufficient_lift_rejected(parent,tmp_path):
    body,bundle=parent;r=record(tmp_path,parent)
    wrongs=[]
    a=deepcopy(r);a['installed_transform']['rotation'][0][0]=1.;wrongs.append(a)
    a=deepcopy(r);a['local_CG_inertia_kg_m2']=[[1.,0.,0.],[0.,1.,0.],[0.,0.,4.]];wrongs.append(a)
    a=deepcopy(r);a['local_CG_inertia_kg_m2']=np.diag([1e12,1e12,1e12]).tolist();wrongs.append(a)
    a=deepcopy(r);a['local_CG_m']=[1.,0.,0.];wrongs.append(a)
    a=deepcopy(r);a['access']['lifting']['rated_capacity_kg']=12.;wrongs.append(a)
    a=deepcopy(r);a['mass_interval_kg']=[13.,14.];wrongs.append(a)
    a=deepcopy(r);a['physical_definition']['hardware'][0]['included_mass_kg']=0.;wrongs.append(a)
    for bad in wrongs:
        with pytest.raises(ValueError):e.evaluate(bundle,body,assembly_records=[sealed(bad)],source_root=tmp_path,allow_synthetic=True)


def test_continuous_sweep_bounds_intermediate_rotations():
    box=dict(min_m=[-2.,-.1,-.1],max_m=[2.,.1,.1])
    a=dict(frame_id='vehicle',translation_m=[0.,0.,0.],rotation=np.eye(3).tolist())
    b=dict(frame_id='vehicle',translation_m=[0.,0.,0.],rotation=[[-1.,0.,0.],[0.,-1.,0.],[0.,0.,1.]])
    result=e.swept_envelope(box,[a,b])
    # The endpoint union has y extent0.1; a90degree intermediate pose reaches2m.
    assert result['min_m'][1]<-2. and result['max_m'][1]>2.
    assert not result['collision_checked'] and not result['access_qualified']


def test_source_payload_mutation_and_empty_access_are_refused(parent,tmp_path):
    body,bundle=parent;r=record(tmp_path,parent)
    (tmp_path/'method.step').write_text('Mutated geometry source')
    with pytest.raises(ValueError,match='source bytes'):e.evaluate(bundle,body,assembly_records=[r],source_root=tmp_path,allow_synthetic=True)
    r=record(tmp_path,parent);r['access']['removal_path']=[]
    with pytest.raises(ValueError,match='Access path'):e.evaluate(bundle,body,assembly_records=[sealed(r)],source_root=tmp_path,allow_synthetic=True)


def test_measured_claim_requires_traceability_and_inclusive_scope(parent,tmp_path):
    body,bundle=parent;r=record(tmp_path,parent)
    r['evidence_kind']='measured-installed-assembly'
    with pytest.raises(ValueError,match='serial/date'):
        e.evaluate(bundle,body,assembly_records=[sealed(r)],source_root=tmp_path,allow_synthetic=True)
    r=record(tmp_path,parent);r['assembly_mass_includes_hardware_and_services']=False
    with pytest.raises(ValueError,match='inclusive assembly mass'):
        e.evaluate(bundle,body,assembly_records=[sealed(r)],source_root=tmp_path,allow_synthetic=True)
    r=record(tmp_path,parent);r['physical_accepted']=True
    with pytest.raises(ValueError,match='assert qualification'):
        e.evaluate(bundle,body,assembly_records=[sealed(r)],source_root=tmp_path,allow_synthetic=True)
