"""Configuration compatibility, source freshness and complete dependency propagation."""
from copy import deepcopy
import pytest
from engineering.assembly_design import contracts as c, baseline, models
from engineering.twin_workflow import core


def test_prototype_freezes_six_car_repository_profile_without_lm3_floor_adoption():
    p=c.prototype_configuration()
    assert p['architecture']=='baghdad-six-car'
    assert p['values']['length']['value']==111
    assert p['values']['gauge']['value']==1435
    assert p['values']['nominal_passengers']['value']==720
    assert p['bogie_arrangement']['powered_per_car']==1
    assert p['low_floor_layout']['value'] is None
    assert p['door_layout']['state']=='hold'
    assert p['battery_chemistry']=='lfp' and p['conflicts']
    assert p['sensitivities']['gross_mass_cases']['value']==[384000.,460800.]
    assert all(p[k] is False for k in core.FLAGS)
    assert all(core.sha(core.ROOT/path)==digest for path,digest in p['source_sha256'].items())


def test_crosswalk_preserves_all_source_ids_and_groups_repeated_function():
    inventory=baseline.inventory(core.read(baseline.DATA)); result=c.crosswalk(inventory)
    assert result['source_record_count']==414
    assert {r['source_id'] for r in result['items']}=={r['id'] for r in inventory['items']}
    assert 1<len(result['families'])<414
    assert len([r for r in result['items'] if r['architecture']=='baghdad-six-car'])==69
    assert result['duplicate_records']
    assert all(len(r['source_ids'])>1 for r in result['duplicate_records'])
    groups={r['family_id'] for r in result['items']}
    assert 'legacy-lm3/structural-bay' in groups
    assert 'baghdad-six-car/structural-bay' in groups
    assert result['physical_part_count'] is None


def card(**changes):
    values=dict(identity='source',publisher='Manufacturer',exact_part='P-1',revision='drawing-A',
                url='https://example.org/part',locator='table 2',unit='m',retrieved='2026-10-19',
                operating_envelope={'continuous_temperature':c.quantity(50,'degC')},uncertainty='supplier reference; combined ratings unknown',
                document=b'exact supplier bytes')
    values.update(changes);return c.source_card(**values)


def test_supplier_source_changed_hash_and_expiry_are_rejected():
    value=card()
    assert c.validate_source(value, observed_sha256=value['document_sha256'])==value
    with pytest.raises(ValueError,match='stale supplier'):c.validate_source(value,observed_sha256='a'*64)
    with pytest.raises(ValueError,match='stale supplier'):card(valid_until='2026-10-18')
    with pytest.raises(ValueError,match='architecture'):card(applicability='legacy-lm3')
    assert card(document=None)['evidence_state']=='hold-document-not-retained'


@pytest.mark.parametrize('value',(float('inf'),float('-inf'),float('nan')))
def test_nonfinite_values_cannot_enter_quantity_source_or_dependencies(value):
    with pytest.raises(ValueError,match='nonfinite'):c.quantity(value,'m')
    with pytest.raises(ValueError,match='nonfinite'):card(operating_envelope={'temperature':[value]})
    with pytest.raises(ValueError,match='nonfinite'):c.dependency_manifest({'material':{'E':value}})


def test_edition_and_chemistry_never_auto_adopt_licensed_criteria():
    entry=c.standards_register()['entries'][0]
    assert entry['edition']=='2026 edition 3.0'
    assert entry['publication_date']=='2026-07-17'
    old=c.standard_applicability('IEC61373',prior_edition='2010',equipment_category='body-mounted')
    assert any('impact review' in r for r in old['reasons'])
    assert not old['applicable_approved']
    sodium=c.standard_applicability('IEC62928',chemistry='sodium-ion')
    assert any('alternative test strategy' in r for r in sodium['reasons'])
    lfp=c.standard_applicability('IEC62928',chemistry='lfp',equipment_category='traction')
    assert lfp['state']=='hold' and not any('alternative test strategy' in r for r in lfp['reasons'])


def test_interface_missing_endpoint_stale_revision_and_architecture_rejected():
    value=c.interface('cassette-mount','structural-mount',['tray','vehicle-seat'],
                      freedoms=['tx'], quantities={'force':c.quantity(500,'N')})
    c.validate_interface(value, component_ids={'tray','vehicle-seat'})
    with pytest.raises(ValueError,match='missing interface endpoint'):c.validate_interface(value,component_ids={'tray'})
    with pytest.raises(ValueError,match='architecture'):c.validate_interface(value,architecture='legacy-lm3')
    changed=deepcopy(value);changed['degrees_of_freedom'].append('ty')
    with pytest.raises(ValueError,match='stale'):c.validate_interface(changed)
    with pytest.raises(ValueError,match='degree'):c.interface('bad','bearing',['a','b'],freedoms=['unknown'])


def bundle():
    policy=core.read(baseline.DATA)
    variables=next(models.candidates(policy,'service-cassette'))
    contract=models.build(policy,'service-cassette',variables)['contract']
    materials=[c.material_bundle(identity,material=identity,process='reference-unqualified',density_kg_m3=m['density_kg_m3'])
               for identity,m in contract['materials'].items()]
    first=contract['parts'][0]['id']
    mount=c.interface('mount','structural-mount',[first,'external:vehicle-seat'])
    return c.component_bundle(contract,ownership={p['id']:'purchased' if p.get('geometric_role')=='supplier-coordination-envelope' else 'owned' for p in contract['parts']},
        interfaces=[mount],material_bundles=materials,required_interfaces=['mount'])


def test_existing_geometry_contract_wrapped_without_second_authority():
    value=bundle()
    assert value['geometry']['parts']
    assert c.validate_component(value)==value
    changed=deepcopy(value);changed['required_interfaces'].append('missing-connector')
    with pytest.raises(ValueError,match='missing mandatory interface'):c.validate_component(changed)
    with pytest.raises(ValueError,match='architecture'):c.validate_component(value,architecture='legacy-lm3')
    changed=deepcopy(value);changed['geometry']['parts'][0]['properties']['mass_kg']+=1
    with pytest.raises(ValueError,match='mass differs'):c.validate_component(changed)


@pytest.mark.parametrize('changed',('mount','connector','material'))
def test_critical_revision_regenerates_every_representation_and_reissues_test_requests(changed):
    before={name:{'revision':'A'} for name in ('mount','connector','material')}
    after=deepcopy(before);after[changed]['revision']='B'
    first=c.dependency_manifest(before);next_revision=c.dependency_manifest(after)
    plan=c.invalidation_plan(first,next_revision)
    assert set(plan['invalidated'])==set(c.OUTPUTS)
    called=[]
    def builder(name):
        def run(context):
            called.append(name)
            return {'name':name,'new_context':context['input_revisions'][changed],'state':'tests-requested' if name in {'tests','qa'} else 'regenerated'}
        return run
    result=c.regenerate(first,next_revision,{name:builder(name) for name in c.OUTPUTS})
    assert set(called)==set(c.OUTPUTS)
    assert all(r['accepted'] is False for r in result['receipts'])
    assert len({r['context_revision'] for r in result['receipts']})==1
    assert all(result[k] is False for k in core.FLAGS)
    unchanged=c.regenerate(next_revision,next_revision,{},retained=result['artifacts'])
    assert unchanged['receipts']==[] and unchanged['artifacts']==result['artifacts']


def test_dependency_dag_orders_adapters_and_rejects_missing_or_cyclic_edges():
    deps={'cad':['mount'],'analysis':['cad'],'harness':['cad'],'tests':['analysis','harness']}
    a=c.dependency_manifest({'mount':'A'},deps);b=c.dependency_manifest({'mount':'B'},deps)
    calls=[]
    def builder(name):
        def run(context):
            assert all(k in context['artifacts'] for k in deps[name] if k!='mount')
            calls.append(name);return name
        return run
    c.regenerate(a,b,{name:builder(name) for name in deps})
    assert calls[0]=='cad' and calls[-1]=='tests'
    with pytest.raises(ValueError,match='missing dependency'):c.dependency_manifest({'mount':'A'},{'cad':['unknown']})
    with pytest.raises(ValueError,match='cyclic'):c.dependency_manifest({'mount':'A'},{'cad':['analysis'],'analysis':['cad']})
    with pytest.raises(ValueError,match='missing representation adapter'):c.regenerate(a,b,{})


def test_baseline_source_upgrade_preserves_facts_and_holds_missing_document_hashes():
    policy=core.read(baseline.DATA);cards=c.baseline_source_cards(policy)
    assert len(cards)==8
    source_facts=[f for card in cards for f in card['operating_envelope']['facts']]
    assert len(source_facts)==len([f for f in policy['facts'] if f['source'] in policy['sources']])
    assert all(card['document_sha256'] is None and card['evidence_state']=='hold-document-not-retained' for card in cards)
    assert next(card for card in cards if card['id']=='harwin-power')['exact_part']=='M80-4000000F1-10-326-00-000'


def test_typed_material_density_and_declared_external_endpoint_must_match_geometry():
    value=bundle()
    bad=deepcopy(value);bad['material_bundles'][0]['density']['value']*=2
    m=bad['material_bundles'][0];m['revision']=core.digest({k:v for k,v in m.items() if k!='revision'})
    with pytest.raises(ValueError,match='density mismatch'):c.validate_component(bad)
    bad=deepcopy(value);bad['interfaces'][0]=c.interface('mount','structural-mount',[value['geometry']['parts'][0]['id'],'unknown-seat'])
    with pytest.raises(ValueError,match='missing interface endpoint'):c.validate_component(bad)
