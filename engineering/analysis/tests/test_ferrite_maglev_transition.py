"""Current system coverage is source-bound and never substitutes for acceptance."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import zipfile

import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from engineering.ferrite_maglev import transition


@pytest.fixture(scope='module')
def register():
    return transition.build()


def test_current_systems_have_explicit_identity_process_and_reverse_coverage(register):
    inputs=transition.inventory_inputs()
    assert {r['id'] for r in register['items']}=={r['id'] for r in inputs}
    assert len(inputs)==53
    assert register['inventory_counts']==dict(canonical_items=53,system_items=53,total_source_items=53,
        requirements=72,work_packages=11,primary_work_packages=11,planned_ebom_objects=53)
    for collection in ('items','planned_ebom','industrialisation'):
        assert len(register[collection])==len(inputs)
    for package in register['work_packages']:
        assert package['item_ids'] and package['requirement_ids']
        assert set(package['item_ids'])=={r['id'] for r in inputs if package['id'] in r['work_package_ids']}
        assert package['new_deliverables'] and package['evidence_needed']
    assert all(r['source'].startswith('engineering/ferrite_maglev/') and r['process_route'] for r in inputs)
    assert {r['id'] for r in inputs}>={'FM-FERRITE','FM-CAPTURE','FM-FOUNDATION','FM-STATION',
        'FM-CHARGING','FM-CONTROL-SOFTWARE','FM-EGRESS-SOFTWARE','FM-FACTORY','FM-ASSURANCE',
        'FM-STATION-STATOR','FM-STATION-CONVERTER','FM-STATION-BRAKE-SINK','FM-STATION-LAUNCH',
        'FM-CIVIL-PRODUCTION','FM-GFRP-HARDPOINT','FM-FINITE-MAGNET'}


def test_only_current_sources_bind_inventory(register):
    for path,digest in register['source_sha256'].items():
        assert digest==sha256((ROOT/path).read_bytes()).hexdigest()
        assert path.startswith(('engineering/ferrite_maglev/','engineering/factory_examples/',
            'engineering/analysis/tests/test_ferrite_maglev_','crates/osr-maglev-control/'))
    assert transition.DATA.as_posix().endswith('/data/systems-inventory.json')
    assert 'legacy_packages' not in register
    assert all('legacy_item_ids' not in p for p in register['work_packages'])


def test_local_manufacture_planning_does_not_invent_origin_or_release(register):
    assert register['accepted_item_count']==register['accepted_physical_release_count']==0
    for row in register['items']:
        assert row['candidate_id'] is None and row['accepted'] is False
    for row in register['industrialisation']:
        assert row['local_value_added_fraction'] is None
        assert all(v is None for v in row['actual_records'].values())
        assert len(row['evidence_needed'])>=6 and row['process_route']
    for row in register['planned_ebom']:
        assert row['quantity'] is row['material_grade'] is row['mass_kg'] is row['unit_cost_usd'] is None
        assert row['country_of_origin'] is None
    def holds(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if k in {*transition.FLAGS,'accepted'}:assert v is False
                holds(v)
        elif isinstance(value,list):
            for item in value:holds(item)
    holds(register)


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


@pytest.mark.parametrize('collection',['items','requirements','work_packages','industrialisation','planned_ebom'])
def test_missing_output_identity_fails_closed(register,collection):
    bad=deepcopy(register);bad[collection].pop()
    with pytest.raises(ValueError,match='inventory|coverage'):transition.validate(bad)


@pytest.mark.parametrize('mutation',['duplicate','rename','unknown-requirement','false-release',
    'fake-origin','binding','reverse-missing','receipt','fake-quantity','process-route'])
def test_untraced_claims_and_changed_mappings_are_rejected(register,mutation):
    bad=deepcopy(register)
    if mutation=='duplicate':bad['items'].append(deepcopy(bad['items'][0]))
    elif mutation=='rename':bad['items'][0]['title']='New unsupported part definition'
    elif mutation=='unknown-requirement':bad['items'][0]['requirement_ids'].append('MAG-999')
    elif mutation=='false-release':bad['items'][0]['physical_release']=True
    elif mutation=='fake-origin':bad['industrialisation'][0]['actual_records']['country_of_origin']='IQ'
    elif mutation=='binding':bad['interfaces']['supervision']['tags'][0]['source_binding']='fake-live-device'
    elif mutation=='reverse-missing':bad['work_packages'][0]['item_ids'].pop()
    elif mutation=='receipt':bad['source_sha256'].pop(next(iter(bad['source_sha256'])))
    elif mutation=='fake-quantity':bad['planned_ebom'][0]['quantity']=1
    elif mutation=='process-route':bad['items'][0]['process_route']='Unqualified replacement routing'
    with pytest.raises(ValueError):transition.validate(bad)


def test_new_requirement_requires_explicit_input_allocation():
    with pytest.raises(ValueError,match='requirement allocation'):
        transition.build(requirements=transition.requirement_inputs()+[dict(id='MAG-999',accepted=False,state='open')])


def test_missing_work_package_rejected():
    with pytest.raises(ValueError,match='primary work packages'):
        transition.build(work_packages=[dict(id=i) for i in transition.WORK_PACKAGES[:-1]])


@pytest.mark.parametrize('mutation',['duplicate','unknown-requirement','unknown-package','source-escape','source-traversal','missing-route'])
def test_current_input_changes_require_valid_explicit_allocation(monkeypatch,mutation):
    original=transition._read
    def changed(path):
        value=original(path)
        if path==transition.DATA:
            if mutation=='duplicate':value['items'].append(deepcopy(value['items'][0]))
            elif mutation=='unknown-requirement':value['items'][0]['requirement_ids']=['MAG-999']
            elif mutation=='unknown-package':value['items'][0]['work_package_ids']=['undeclared']
            elif mutation=='source-escape':value['items'][0]['source']='Cargo.toml'
            elif mutation=='source-traversal':value['items'][0]['source']='engineering/ferrite_maglev/../ferrite_maglev/geometry.py'
            else:value['items'][0]['process_route']=''
        return value
    monkeypatch.setattr(transition,'_read',changed)
    with pytest.raises(ValueError):transition.build()


def test_json_roundtrip_is_auditable(register):
    assert transition.validate(json.loads(json.dumps(register)))['schema']==transition.SCHEMA


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


def test_supplier_questions_distinguish_manufacture_from_supply(register):
    location=next(q for q in register['supplier_questions'] if q['id']=='RFQ-manufacturing-location')
    assert 'UK distributor' in location['question']
    assert 'does not prove UK manufacture' in location['evidence_requested']
    for row in register['supplier_questions']:
        assert row['response'] is row['quote'] is row['manufacture_country'] is row['supply_country'] is None
        assert not row['uk_manufacture_verified'] and not row['accepted']


@pytest.mark.parametrize('mutation',['threshold','performed','origin','missing-output'])
def test_protocol_cannot_invent_limits_tests_or_supplier_evidence(register,mutation):
    bad=deepcopy(register)
    if mutation=='threshold':bad['validation_programme']['gates'][1]['limits'][0]['value']=0.05
    elif mutation=='performed':bad['validation_programme']['gates'][2]['actual_evidence']='mock-test'
    elif mutation=='origin':bad['supplier_questions'][0]['manufacture_country']='GB'
    else:bad['requirements'][0]['new_deliverables']=[]
    with pytest.raises(ValueError):transition.validate(bad)


def test_native_field_rust_and_coupled_availability_need_execution_and_physical_evidence(register):
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
    from engineering.ferrite_maglev import geometry
    # Four independent outboard supports replace two beam-crossing members.
    # Both variants retain 26 guideway regions and 28 frame regions; recessing
    # splits each of the 24 ferrite regions into three instead of one.
    support_ids={f'frame/lower-side-cantilever-{x}-{side}' for x in (-6,6) for side in (-1,1)}
    for variant,per_cartridge,total in (('flat-retainer',22,582),('recessed-retainer',24,630)):
        definition=geometry.interface(variant);parts={p['id']:p for p in definition['parts']}
        assert variants[variant]['planned_solid_count']==len(parts)==total==26+28+24*per_cartridge
        assert {name for name in parts if name.startswith('frame/lower-side-cantilever-')}==support_ids
        assert not any(name.startswith('frame/lower-crosshead-') for name in parts)
        for x in (-6,6):
            for side in (-1,1):
                support=parts[f'frame/lower-side-cantilever-{x}-{side}']
                assert support['kind']=='tube' and support['size_m']==[.1,.64,.08]
                assert support['at_m']==[x-.05,.84 if side>0 else -1.48,-.524]
    assert variants['flat-retainer']['nominal_fastener_head_gap_m']==pytest.approx(.002)
    assert variants['recessed-retainer']['nominal_fastener_head_gap_m']==pytest.approx(.008)
    assert all(not r['full_error_budget_accepted'] for r in variants.values())
    assert all('crates/osr-maglev-control' in p for p in capabilities['rust-multimodule-study']['source_sha256'])


@pytest.mark.parametrize('mutation',['qualified-force','stale-source','missing-mapping','export-receipt'])
def test_available_capability_cannot_be_promoted_to_acceptance(register,mutation):
    bad=deepcopy(register)
    if mutation=='qualified-force':bad['capability_availability'][1]['physical_validation']=True
    elif mutation=='stale-source':bad['capability_availability'][1]['source_sha256']['engineering/ferrite_maglev/field.py']='0'*64
    elif mutation=='missing-mapping':
        next(r for r in bad['work_packages'] if r['id']=='coupled-dynamics')['capability_ids']=[]
    else:bad['capability_availability'][0]['execution_receipt']='invented-export'
    with pytest.raises(ValueError):transition.validate(bad)


def test_selected_requirements_use_current_data_and_keep_egress_hold():
    from engineering.ferrite_maglev import requirements
    register=requirements.register()
    assert len(register['requirements'])==72+7+100
    core=next(r for r in register['requirements'] if r['id']=='CIV-004')
    assert not core['alternative_selected'] and core['alternative_requirement_ids']
    assert not register['walkway_removal_approved'] and not register['accepted_requirements']
    assert next(r for r in register['requirements'] if r['id']=='SYS-001')['requirement'].find('six cars')>=0


def test_native_geometry_helpers_are_standalone_and_fcstd_metadata_is_reproducible(tmp_path):
    from engineering.factory_examples.models import part,volume,global_size
    from engineering.factory_examples.native import _canonicalise_fcstd
    import math
    tube=part('tube',[2.,3.,4.],[0.,0.,0.],kind='tube',axis=2,wall_m=.1)
    assert volume(tube)==pytest.approx(24.-1.8*2.8*4.)
    cylinder=part('cylinder',[2.,2.,4.],[0.,0.,0.],kind='cylinder',cylinder_axis='x')
    assert global_size(cylinder)==[4.,2.,2.] and volume(cylinder)==pytest.approx(4*math.pi)
    output=tmp_path/'model.FCStd'
    xml=b'<Property name="CreationDate"><String value="2026-10-20"/></Property><Property name="Uid"><Uuid value="random"/></Property><Object type="Part::Feature" name="Part" id="91"/>'
    with zipfile.ZipFile(output,'w') as z:z.writestr('Document.xml',xml)
    _canonicalise_fcstd(output);first=output.read_bytes()
    _canonicalise_fcstd(output)
    assert output.read_bytes()==first
    with zipfile.ZipFile(output) as z:
        result=z.read('Document.xml')
        assert b'2000-01-01T00:00:00Z' in result and b'id="1"' in result
        assert b'random' not in result and z.getinfo('Document.xml').date_time==(2000,1,1,0,0,0)
