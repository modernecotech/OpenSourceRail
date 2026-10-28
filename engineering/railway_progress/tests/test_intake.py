"""Disposable intake/authority fixtures are never project physical or price evidence."""
from copy import deepcopy
from pathlib import Path
import pytest
from engineering.station_rail.common import identity,encoded,digest
from engineering.railway_progress import intake as i
from engineering.reference_cell import vehicles,bundle as binding,economics
from engineering.railway_completion import evidence
from engineering.railway_completion.tests import test_evidence as signed


@pytest.fixture(scope='module')
def cell():
    vehicle=vehicles.evaluate('V1');bundle=binding.materialize(vehicle,2000.)
    civil=dict(candidate_id=bundle['candidate_id'],known_material_mass_kg=1000.,construction_sequence=[{'asset':'span/0'}])
    return vehicle,bundle,civil


def write(folder,name,value):
    p=folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encoded(value))
    return dict(path=name,sha256=digest(p))


def add(folder,manifest,kind,value,context='normal/nominal'):
    name=kind+'-'+str(len(manifest['inputs']))+'.json'
    manifest['inputs'].append(dict(kind=kind,context=context,file=write(folder,name,value)));return manifest


def service(bundle,**changes):
    r=dict(cars=6,car_length_m=17.,normal_places_per_car=46,headway_s=120.,station_spacing_m=bundle['architecture_case']['physical_definition']['route']['station_spacing_m'],
        fleet_trainsets=3,estimate_date='2026-10-28',risk_basis='UNIT-TEST-ONLY',protected_service_qualified=False,engineering_evidence_qualified=False)
    r.update(changes);return r


def quote(vehicle,bundle,**changes):
    q=dict(candidate_id=bundle['candidate_id'],part_definition_id=vehicle['registry']['parts'][0]['physical_definition_id'],source_class='A',
        supplier='DISPOSABLE-TEST-ONLY',source_date='2026-10-01',valid_until='2027-01-01',currency='USD',location='unit-test-cell',
        quantity_basis='one-part',quote_scope='finished-part',source_document_sha256='a'*64,unit_usd=[100.,110.])
    q.update(changes);q['quote_id']=identity(q);return q


def charge(bundle,context,**changes):
    return economics.make_record(bundle['candidate_id'],'rolling-stock',['train/car/part'],[1.,1.],[100.,110.],0,
        'A','a'*64,'2026-10-01','unit-test-cell','one-part',economics.service_identity(context),
        source_document_sha256='b'*64,supplier='DISPOSABLE-TEST-ONLY',valid_until='2027-01-01',**changes)


def test_empty_intake_keeps_all_physical_and_commercial_evidence_open(cell,tmp_path):
    vehicle,bundle,civil=cell;manifest=i.template(bundle);r=i.load(tmp_path,manifest,bundle)
    assert r['inputs']==[] and r['assessments']==[] and not r['authenticated_ids']
    assert all(r[k] is False for k in i.FLAGS)
    assert i.for_context(r,'force-map','normal/nominal') is None
    result=i.lifecycle(bundle,r)
    assert result['execution']=='held' and result['whole_life_cost_usd'] is None
    assert set(result['required_scopes'])==set(economics.SCOPES)


@pytest.mark.parametrize('field,value',[('candidate_id','f'*64),('bundle_definition_id','f'*64),('body_candidate_id','f'*64)])
def test_manifest_exact_physical_and_evaluation_binding_cannot_be_resealed(cell,tmp_path,field,value):
    _,b,_=cell;m=i.template(b);m['binding'][field]=value
    with pytest.raises(ValueError):i.load(tmp_path,m,b)


def test_old_single_fin_reference_cannot_supply_new_segmented_candidate_inputs(cell,tmp_path):
    from engineering.railway_twin import model
    _,b,_=cell;old=model.materialize()['bundle'];m=i.template(old)
    assert old['candidate_id']!=b['candidate_id']
    with pytest.raises(ValueError):i.load(tmp_path,m,b)


def test_owned_contexts_are_explicit_unique_and_return_defensive_copies(cell,tmp_path):
    _,b,_=cell;m=i.template(b);x=dict(candidate_id=b['candidate_id'],schema='unit-test-only',samples=[])
    add(tmp_path,m,'force-map',x,'normal/nominal');r=i.load(tmp_path,m,b)
    got=i.for_context(r,'force-map','normal/nominal');got['samples'].append('mutated')
    assert i.for_context(r,'force-map','normal/nominal')['samples']==[]
    assert i.for_context(r,'force-map','crowd/nominal') is None
    m['inputs'].append(deepcopy(m['inputs'][0]))
    with pytest.raises(ValueError,match='one input'):i.load(tmp_path,m,b)


@pytest.mark.parametrize('path',['../outside.json','/absolute.json','a/../raw.json','a\\raw.json','./raw.json','a//raw.json'])
def test_input_files_are_owned_canonical_paths(cell,tmp_path,path):
    _,b,_=cell;m=i.template(b);add(tmp_path,m,'component-record',dict(candidate_id=b['candidate_id']))
    m['inputs'][0]['file']['path']=path
    with pytest.raises(ValueError):i.load(tmp_path,m,b)


def test_changed_bytes_and_leaf_or_parent_links_cannot_supply_inputs(cell,tmp_path):
    _,b,_=cell;m=i.template(b);add(tmp_path,m,'site-input',dict(candidate_id=b['candidate_id']))
    original=deepcopy(m['inputs'][0]['file']);m['inputs'][0]['file']['sha256']='f'*64
    with pytest.raises(ValueError):i.load(tmp_path,m,b)
    (tmp_path/'link.json').symlink_to(tmp_path/original['path']);m['inputs'][0]['file']=dict(original,path='link.json')
    with pytest.raises(ValueError):i.load(tmp_path,m,b)
    (tmp_path/'parent').symlink_to(tmp_path,target_is_directory=True);m['inputs'][0]['file']=dict(original,path='parent/'+original['path'])
    with pytest.raises(ValueError):i.load(tmp_path,m,b)


@pytest.mark.parametrize('kind',['force-map','coupled-models','fault-maps','quote','lifecycle-charge','site-input','component-record'])
def test_every_intake_kind_rejects_other_candidate_even_with_hash_correct_files(cell,tmp_path,kind):
    _,b,_=cell;m=i.template(b);add(tmp_path,m,kind,dict(candidate_id='f'*64))
    with pytest.raises(ValueError,match='another candidate'):i.load(tmp_path,m,b)


def test_unowned_extra_input_fields_and_unknown_types_are_refused(cell,tmp_path):
    _,b,_=cell;m=i.template(b);add(tmp_path,m,'force-map',dict(candidate_id=b['candidate_id']))
    m['inputs'][0]['callback']='untrusted.module:approve'
    with pytest.raises(ValueError):i.load(tmp_path,m,b)
    m['inputs'][0].pop('callback');m['inputs'][0]['kind']='authenticator'
    with pytest.raises(ValueError):i.load(tmp_path,m,b)


def test_json_cannot_install_authentication_code_or_suppress_existing_contract_holds(cell,tmp_path):
    _,b,_=cell;m=i.template(b);envelope=signed.fixture_record(tmp_path,b)
    m['evidence_manifest']['envelopes']=[write(tmp_path,'envelope.json',envelope)]
    m['authenticator']={'module':'do_not_import_this','trusted':True}
    try:r=i.load(tmp_path,m,b)
    except ValueError:return
    assert not r['assessments'][0]['authenticated'] and not r['authenticated_ids']
    assert r['assessments'][0]['physical_protocol_screen_passed'] is False


@pytest.mark.parametrize('context',[None,'short','G'*64])
def test_external_authentication_provider_requires_exact_application_context(cell,tmp_path,context):
    _,b,_=cell
    with pytest.raises(ValueError,match='context'):
        i.load(tmp_path,i.template(b),b,authenticator=signed.test_only_authenticator,authentication_context_id=context)


def test_existing_signed_numerical_fixture_authentication_keeps_its_nonphysical_provenance(cell,tmp_path):
    _,b,_=cell;m=i.template(b);envelope=signed.fixture_record(tmp_path,b)
    m['evidence_manifest']['envelopes']=[write(tmp_path,'envelope.json',envelope)]
    r=i.load(tmp_path,m,b,authenticator=signed.test_only_authenticator,authentication_context_id='a'*64)
    assert r['authentication_context_id']=='a'*64 and r['authenticated_ids']
    assert r['assessments'][0]['authenticated'] is True
    assert r['assessments'][0]['physical_protocol_screen_passed'] is False


def test_quotes_cannot_self_authenticate_or_close_unpriced_installed_scope(cell,tmp_path):
    v,b,c=cell;m=i.template(b);add(tmp_path,m,'quote',quote(v,b),'quote/first-part');r=i.load(tmp_path,m,b)
    with pytest.raises(ValueError,match='authentication'):i.commercial(v,c,b,r)
    r=i.load(tmp_path,m,b,authenticator=lambda *a:True,authentication_context_id='c'*64)
    result=i.commercial(v,c,b,r,authenticator=lambda *a:True)
    assert 0<result['actual_quote_occurrence_coverage']<1
    assert result['complete_installed_vehicle_cost_usd'] is None and result['complete_CAPEX_usd'] is None
    assert result['whole_life_cost_usd'] is None and result['economic_winner'] is None
    assert result['missing_whole_life_scopes'] and not result['ERPNext']['external_transactions_performed']


def test_later_commercial_callback_cannot_bypass_missing_loaded_auth_context(cell,tmp_path):
    v,b,c=cell;m=i.template(b);add(tmp_path,m,'quote',quote(v,b),'quote/first-part');r=i.load(tmp_path,m,b)
    with pytest.raises(ValueError,match='context'):i.commercial(v,c,b,r,authenticator=lambda *a:True)


def test_actual_lifecycle_quote_requires_external_auth_and_missing_scopes_remain_unknown(cell,tmp_path):
    _,b,_=cell;m=i.template(b);m['service_context']=service(b)
    q=charge(b,m['service_context']);add(tmp_path,m,'lifecycle-charge',q,'cost/one-part')
    r=i.load(tmp_path,m,b);result=i.lifecycle(b,r)
    assert result['held_actual_source_record_ids']==[q['record_id']]
    assert result['complete_installed_whole_life_cost_usd'] is None and result['integrated_winner'] is None
    r=i.load(tmp_path,m,b,authenticator=lambda *a:True,authentication_context_id='c'*64)
    result=i.lifecycle(b,r,authenticator=lambda *a:True)
    assert result['actual_authenticated_charge_count']==1
    assert result['conditional_declared_calendar_npv_usd'] is None and result['missing_whole_life_scopes']


@pytest.mark.parametrize('change',[dict(cars=5),dict(car_length_m=18.),dict(station_spacing_m=1500.),dict(normal_places_per_car=120)])
def test_lifecycle_service_cannot_redefine_a_bound_physical_cell(cell,tmp_path,change):
    _,b,_=cell;m=i.template(b);m['service_context']=service(b,**change)
    try:r=i.load(tmp_path,m,b)
    except ValueError:return
    with pytest.raises(ValueError,match='service|formation|candidate|route'):i.lifecycle(b,r)


def test_input_service_strings_cannot_qualify_protection_or_engineering_evidence(cell,tmp_path):
    _,b,_=cell;m=i.template(b);m['service_context']=service(b,protected_service_qualified=True,engineering_evidence_qualified=True)
    try:r=i.load(tmp_path,m,b);result=i.lifecycle(b,r)
    except ValueError:return
    assert result['open_protection_or_evidence'] is True
    assert result['integrated_winner'] is None and result['complete_installed_whole_life_cost_usd'] is None
