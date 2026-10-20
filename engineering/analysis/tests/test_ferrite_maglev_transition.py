"""Coverage cannot stand in for physical design, material or release evidence."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import transition


@pytest.fixture(scope='module')
def register():
    return transition.build()


def test_exhaustive_source_identities_packages_and_requirements(register):
    assert register['inventory_counts']==dict(canonical_items=345,additional_baghdad_items=69,
        total_source_items=414,legacy_work_packages=63,requirements=72,
        primary_work_packages=11,planned_ebom_objects=23)
    graph=transition._read(transition.GRAPH)
    reference=transition._read(transition.REFERENCE)
    assert {i['id'] for i in register['items']}=={i['id'] for i in graph['items']}|{
        'baghdad:'+p['id'] for p in reference['parts']}
    assert {p['id'] for p in register['legacy_packages']}=={p['id'] for p in graph['packages']}
    assert all(p['legacy_item_ids'] and p['requirement_ids'] for p in register['work_packages'])
    assert len(register['industrialisation'])==414+23
    assert sum(register['disposition_counts'].values())==414
    # Multiple canonical records with a common catalogue label keep their IDs.
    common=[i for i in register['items'] if i['catalogue_id']=='LM3-BDY-P020']
    assert len(common)==2 and len({i['id'] for i in common})==2
    assert all(i['source_records'] and i['source_sha256'] for i in register['items'])


def test_retired_wheel_functions_have_replacements_and_depot_exception(register):
    rows=register['items']
    for row in rows:
        if row['catalogue_id'].startswith('LM3-BOG-'):
            assert row['disposition']=='retire-wheel-specific'
            assert 'MAG-054' in row['requirement_ids']
            assert 'rig-and-demonstrator' in row['work_package_ids']
    rotary=next(i for i in rows if i['catalogue_id']=='LM3-TRC-P010')
    assert rotary['disposition']=='replace' and 'MAG-042' in rotary['requirement_ids']
    depot=next(i for i in rows if i['catalogue_id']=='STN-DEP-P030')
    assert depot['profile_id']=='depot-routing'
    assert any('depot-only' in d for d in depot['new_deliverables'])
    assert next(i for i in rows if i['id']=='baghdad:ME-16')['profile_id']=='capture-redesign'
    assert next(i for i in rows if i['id']=='baghdad:CI-08')['profile_id']=='depot-maintenance'


def test_local_make_does_not_invent_origin_material_geometry_or_acceptance(register):
    assert register['accepted_item_count']==register['accepted_physical_release_count']==0
    for row in register['items']:
        assert row['candidate_id'] is None
        assert row['new_geometry_created'] is False
        assert row['legacy_evidence_transferred'] is False
        assert row['accepted'] is False and row['physical_release'] is False
    for row in register['industrialisation']:
        assert row['local_value_added_fraction'] is None
        assert all(v is None for v in row['actual_records'].values())
        assert len(row['evidence_needed'])>=6
    for row in register['planned_ebom']:
        assert row['quantity'] is row['material_grade'] is row['mass_kg'] is row['unit_cost_usd'] is None
    capture=next(i for i in register['industrialisation'] if i['transition_id']=='FM-CAPTURE')
    assert capture['routing_state']=='new-or-revalidated-routing-required'


def test_erp_and_supervision_preserve_physical_commissioning_holds(register):
    erp=register['interfaces']['erp'];sup=register['interfaces']['supervision']
    assert not erp['production_import_authorized']
    assert not sup['physical_bindings_commissioned']
    assert not sup['grants_movement_authority'] and not sup['closes_support_loop']
    assert len(sup['tags'])==14
    assert {t['unit'] for t in sup['tags']} >= {'m','A','N','V','degC','J'}
    for tag in sup['tags']:
        assert tag['lower_bound'] is tag['upper_bound'] is tag['source_binding'] is tag['validity_limit_ms'] is None
        assert {'timestamp','quality','uncertainty','provenance'}<=set(tag['common_fields'])


@pytest.mark.parametrize('collection', ['items','legacy_packages','requirements','work_packages','industrialisation','planned_ebom'])
def test_missing_output_identity_fails_closed(register,collection):
    bad=deepcopy(register);bad[collection].pop()
    with pytest.raises(ValueError,match='inventory|coverage|objects'):
        transition.validate(bad)


def test_new_source_item_has_no_automatic_profile(monkeypatch):
    original=transition._read
    def changed(path):
        value=original(path)
        if path==transition.GRAPH:
            extra=deepcopy(value['items'][0]);extra['id']='item:new-unassigned'
            value['items'].append(extra)
        return value
    monkeypatch.setattr(transition,'_read',changed)
    with pytest.raises(ValueError,match='disposition coverage'):
        transition.build()


def test_new_spec_requirement_requires_allocation():
    from engineering.ferrite_maglev.model import requirement_register
    reqs=requirement_register()+[dict(id='MAG-999',accepted=False,state='open')]
    with pytest.raises(ValueError,match='requirement allocation'):
        transition.build(requirements=reqs)


def test_missing_primary_work_package_is_rejected():
    with pytest.raises(ValueError,match='primary work packages'):
        transition.build(work_packages=[dict(id=i) for i in transition.WORK_PACKAGES[:-1]])


@pytest.mark.parametrize('mutation', ['duplicate','rename-source','unknown-requirement','false-release',
    'fake-origin','binding','reverse-missing','profile-change','receipt'])
def test_adverse_false_or_untraced_claims_rejected(register,mutation):
    bad=deepcopy(register)
    if mutation=='duplicate':bad['items'].append(deepcopy(bad['items'][0]))
    elif mutation=='rename-source':bad['items'][0]['title']='Renamed to imply magnetic geometry'
    elif mutation=='unknown-requirement':bad['items'][0]['requirement_ids'].append('MAG-999')
    elif mutation=='false-release':bad['items'][0]['physical_release']=True
    elif mutation=='fake-origin':bad['industrialisation'][0]['actual_records']['country_of_origin']='IQ'
    elif mutation=='binding':bad['interfaces']['supervision']['tags'][0]['source_binding']='fake-live-device'
    elif mutation=='reverse-missing':bad['work_packages'][0]['legacy_item_ids'].pop()
    elif mutation=='profile-change':bad['items'][0]['disposition']='replace'
    elif mutation=='receipt':bad['source_sha256'].pop(next(iter(bad['source_sha256'])))
    with pytest.raises(ValueError):transition.validate(bad)


def test_live_authoritative_collection_removed_item_fails(monkeypatch):
    original=transition._read
    target=ROOT/'design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json'
    def changed(path):
        value=original(path)
        if path==target:value['product_items'].pop()
        return value
    monkeypatch.setattr(transition,'_read',changed)
    with pytest.raises(ValueError,match='authoritative collection'):
        transition.build()


def test_json_roundtrip_is_auditable(register):
    assert transition.validate(json.loads(json.dumps(register)))['schema']=='osr-ferrite-maglev-transition/1'


def test_each_requirement_and_package_has_concrete_outputs_and_actions(register):
    for row in register['requirements']+register['work_packages']:
        assert row['new_deliverables'] and row['evidence_needed']
        assert all(isinstance(v,str) and len(v)>20 for v in row['new_deliverables']+row['evidence_needed'])


def test_g0_g5_protocol_limits_and_traveller_prerequisites_remain_holds(register):
    programme=register['validation_programme'];gates=programme['gates']
    assert [g['id'] for g in gates]==['G0','G1','G2','G3','G4','G5']
    assert programme['planning_targets_are_acceptance_limits'] is False
    assert programme['unknown_threshold_is_pass'] is False
    assert {r['id'] for r in register['requirements']}<={r for g in gates for r in g['requirement_ids']}
    for index,gate in enumerate(gates):
        assert gate['requires_gate_ids']==([] if index==0 else ['G'+str(index-1)])
        assert gate['procedure'] and gate['prerequisites'] and gate['evidence_records']
        assert gate['actual_evidence'] is None and gate['accepted'] is False
        assert gate['decision'].startswith('hold')
        for limit in gate['limits']:
            assert limit['value'] is None and limit['approved_by'] is None
            assert limit['derivation_needed'] and limit['unit']
    assert len(programme['traveller']['hold_points'])>=7
    assert programme['traveller']['actual_traveller'] is None


def test_supplier_questions_separate_uk_manufacture_from_supply_and_quotes(register):
    questions=register['supplier_questions']
    location=next(q for q in questions if q['id']=='RFQ-manufacturing-location')
    assert 'UK distributor' in location['question']
    assert 'does not prove UK manufacture' in location['evidence_requested']
    for question in questions:
        assert question['response'] is question['quote'] is question['manufacture_country'] is question['supply_country'] is None
        assert not question['uk_manufacture_verified'] and not question['accepted']


@pytest.mark.parametrize('mutation',['threshold','performed','origin','missing-output'])
def test_protocol_cannot_invent_limits_tests_or_supplier_evidence(register,mutation):
    bad=deepcopy(register)
    if mutation=='threshold':bad['validation_programme']['gates'][1]['limits'][0]['value']=0.05
    elif mutation=='performed':bad['validation_programme']['gates'][2]['actual_evidence']='mock-test'
    elif mutation=='origin':bad['supplier_questions'][0]['manufacture_country']='GB'
    else:bad['requirements'][0]['new_deliverables']=[]
    with pytest.raises(ValueError):transition.validate(bad)


def test_native_field_rust_and_coupled_availability_is_source_bound_without_acceptance(register):
    from hashlib import sha256
    capabilities={r['id']:r for r in register['capability_availability']}
    assert set(capabilities)=={'native-development-solids','two-dimensional-field-hypothesis',
        'rust-multimodule-study','two-way-beam-control-demonstrator','beam-only-evacuation-research'}
    for cap in capabilities.values():
        assert cap['available'] and cap['available_scope'] and cap['evidence_needed']
        assert cap['execution_receipt'] is None and not cap['closes_acceptance_gate']
        assert not cap['physical_tests_performed_by_this_register']
        assert not cap['accepted'] and not cap['physical_release'] and not cap['physical_validation']
        for path,digest in cap['source_sha256'].items():
            assert digest==sha256((ROOT/path).read_bytes()).hexdigest()
            assert register['source_sha256'][path]==digest
    variants={r['variant']:r for r in capabilities['native-development-solids']['geometry_variants']}
    assert variants['flat-retainer']['planned_solid_count']==576
    assert variants['recessed-retainer']['planned_solid_count']==624
    assert variants['flat-retainer']['nominal_fastener_head_gap_m']==pytest.approx(.002)
    assert variants['recessed-retainer']['nominal_fastener_head_gap_m']==pytest.approx(.008)
    assert all(not r['full_error_budget_accepted'] for r in variants.values())
    assert any('no adopted supplier/material grade' in s for s in capabilities['two-dimensional-field-hypothesis']['evidence_needed'])
    assert any('No torsion' in s for s in capabilities['two-way-beam-control-demonstrator']['evidence_needed'])
    assert all('crates/osr-maglev-control' in p for p in capabilities['rust-multimodule-study']['source_sha256'])


@pytest.mark.parametrize('mutation',['qualified-force','stale-source','missing-mapping','export-receipt'])
def test_capability_availability_cannot_be_promoted_to_acceptance(register,mutation):
    bad=deepcopy(register)
    if mutation=='qualified-force':bad['capability_availability'][1]['physical_validation']=True
    elif mutation=='stale-source':bad['capability_availability'][1]['source_sha256']['engineering/ferrite_maglev/field.py']='0'*64
    elif mutation=='missing-mapping':
        row=next(r for r in bad['work_packages'] if r['id']=='coupled-dynamics');row['capability_ids']=[]
    else:bad['capability_availability'][0]['execution_receipt']='invented-export'
    with pytest.raises(ValueError):transition.validate(bad)
