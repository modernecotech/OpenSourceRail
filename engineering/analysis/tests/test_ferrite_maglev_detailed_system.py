"""No mixed configuration or publication-only completion promotion."""
from copy import deepcopy
from hashlib import sha256
from types import SimpleNamespace
import gzip
import json
import pytest
from engineering.ferrite_maglev import detailed_system as d


def components():
    values={name:dict(configuration_sha256='a'*64) for name in d.MODULES if name!='platform_publication'}
    values['candidate_magnetics']['propulsion_accepted_for_simulation']=False
    values['candidate_structures']['all_implemented_screens_pass']=True
    values['full_dynamics']['study_pass']=True
    values['candidate_lifecycle']['native']=dict(state='executed-current')
    return values


def test_magnetic_failure_blocks_otherwise_passing_chain():
    v=d.reconcile(dict(configuration_sha256='a'*64),components())
    assert v['identity_consistent'] and not v['all_required_pass'] and not v['eligible_for_adoption']
    assert not v['physical_release']


def test_mixed_candidate_and_self_asserted_physical_release_refused():
    for mutate in (lambda v:v['bim_field'].update(configuration_sha256='b'*64),lambda v:v['candidate_lifecycle'].update(manufacturing_release=True)):
        values=components();mutate(values)
        with pytest.raises(ValueError):d.reconcile(dict(configuration_sha256='a'*64),values)


@pytest.fixture
def retained(tmp_path,monkeypatch):
    candidate=dict(configuration_sha256='a'*64,parent_configuration_sha256='b'*64,controlled_tare_kg=25000.,controlled_aw3_kg=37000.,cars=6)
    live=dict(components=components(),receipts={name:'c'*64 for name in d.MODULES},economics=dict(configuration_sha256='a'*64,
        whole_pilot_finance=dict(capex_usd=None,annual_opex_usd=None,dscr=None,financial_close=False),**d.platform.FLAGS))
    monkeypatch.setattr(d,'sources',lambda:{'current.py':'d'*64})
    monkeypatch.setattr(d.magnetics,'definition',lambda:deepcopy(candidate))
    monkeypatch.setattr(d,'verified_components',lambda:(deepcopy(live['components']),deepcopy(live['receipts'])))
    monkeypatch.setattr(d.economics,'study',lambda:deepcopy(live['economics']))
    d.publish(tmp_path);d.verify(tmp_path)
    return tmp_path,live


def rewrite(output,mutate):
    """A coherent forgery updates every owned presentation and checksum."""
    value=json.loads(gzip.decompress((output/'study.json.gz').read_bytes()));mutate(value)
    files={'study.json.gz':gzip.compress(d.platform.encoded(value),mtime=0),'economics.json':d.platform.encoded(value['economics']),'README.md':d.readme(value).encode()}
    manifest=json.loads((output/'manifest.json').read_bytes())
    for name,data in files.items():(output/name).write_bytes(data);manifest['files_sha256'][name]=sha256(data).hexdigest()
    (output/'manifest.json').write_bytes(d.platform.encoded(manifest))


@pytest.mark.parametrize('field',('capex_usd','annual_opex_usd','dscr','financial_close'))
def test_rehashed_closed_or_priced_finance_is_refused(retained,field):
    output,live=retained
    rewrite(output,lambda value:value['economics']['whole_pilot_finance'].update({field:True if field=='financial_close' else 1.}))
    with pytest.raises(ValueError,match='finance must remain null'):d.verify(output)


def test_rehashed_economics_must_equal_actual_current_calculation(retained):
    output,live=retained
    rewrite(output,lambda value:value['economics'].update(priced_stock={'magnetic_module_usd':1.}))
    with pytest.raises(ValueError,match='verified current child evidence/economics'):d.verify(output)


def test_even_current_economics_producer_cannot_assert_unqualified_finance(retained):
    output,live=retained
    live['economics']['whole_pilot_finance']['financial_close']=True
    with pytest.raises(ValueError,match='finance must remain null'):d.study()


def test_coherently_rehashed_component_summary_cannot_replace_verified_child(retained):
    output,live=retained
    def forge(value):
        value['components']['candidate_magnetics'].update(static_comparison_pass=True,propulsion_accepted_for_simulation=True)
        value['chain']=d.reconcile(dict(configuration_sha256='a'*64),value['components'])
    rewrite(output,forge)
    with pytest.raises(ValueError,match='verified current child evidence/economics'):d.verify(output)


def test_rehashed_component_receipt_must_match_actual_current_child(retained):
    output,live=retained
    rewrite(output,lambda value:value['component_receipt_sha256'].update(full_dynamics='f'*64))
    with pytest.raises(ValueError,match='verified current child evidence/economics'):d.verify(output)


def test_failed_actual_child_verification_prevents_integrated_read(retained,monkeypatch):
    output,live=retained
    def failed():raise ValueError('actual child mesh corrupted')
    monkeypatch.setattr(d,'verified_components',failed)
    with pytest.raises(ValueError,match='actual child mesh corrupted'):d.read_summary(output)


def test_current_candidate_masses_cannot_be_relabelled(retained):
    output,live=retained
    rewrite(output,lambda value:value.update(controlled_aw3_kg_per_car=26400.))
    with pytest.raises(ValueError,match='verified current child evidence/economics'):d.verify(output)


def test_verified_summary_calls_its_actual_verifier_once(tmp_path,monkeypatch):
    (tmp_path/'manifest.json').write_text('{}');payload=tmp_path/'field.json';payload.write_text('actual field')
    calls=[]
    def verify():
        calls.append('verify')
        if payload.read_text()!='actual field':raise ValueError('actual field corrupted')
    def summary():verify();return dict(configuration_sha256='a'*64,static_comparison_pass=False)
    module=SimpleNamespace(OUTPUT=tmp_path,read_summary=summary)
    monkeypatch.setattr(d,'MODULES',('candidate_magnetics',));monkeypatch.setattr(d,'modules',lambda:[module])
    values,receipts=d.verified_components()
    assert calls==['verify'] and values['candidate_magnetics']['static_comparison_pass'] is False
    assert receipts==dict(candidate_magnetics=sha256(b'{}').hexdigest())
    payload.write_text('forged field')
    with pytest.raises(ValueError,match='actual field corrupted'):d.verified_components()


def test_child_receipt_cannot_change_between_verification_and_summary(tmp_path,monkeypatch):
    receipt=tmp_path/'manifest.json';receipt.write_text('{}')
    def summary():receipt.write_text('{"new":true}');return dict(configuration_sha256='a'*64)
    monkeypatch.setattr(d,'MODULES',('candidate_magnetics',));monkeypatch.setattr(d,'modules',lambda:[SimpleNamespace(OUTPUT=tmp_path,read_summary=summary)])
    with pytest.raises(ValueError,match='receipt changed'):d.verified_components()


def test_lifecycle_summary_comes_from_verified_payload_not_new_unchecked_study(tmp_path,monkeypatch):
    (tmp_path/'manifest.json').write_text('{}');expected=dict(configuration_sha256='a'*64,native=dict(state='hold'))
    (tmp_path/'study.json.gz').write_bytes(gzip.compress(d.platform.encoded(expected),mtime=0));calls=[]
    def forbidden():raise AssertionError('Do not bypass verified retained lifecycle with an unchecked new study')
    module=SimpleNamespace(OUTPUT=tmp_path,verify=lambda:calls.append('verify'),study=forbidden)
    monkeypatch.setattr(d,'MODULES',('candidate_lifecycle',));monkeypatch.setattr(d,'modules',lambda:[module])
    values,_=d.verified_components()
    assert calls==['verify'] and values['candidate_lifecycle']==expected


def test_manufacturing_summary_uses_semantically_verified_study(tmp_path,monkeypatch):
    (tmp_path/'manifest.json').write_text('{}');package=dict(configuration_sha256='a'*64,products=[dict(product_id='module',product_revision_sha256='b'*64,bom=[{},{}],estimated_material_process_cost_usd=123.)])
    (tmp_path/'study.json.gz').write_bytes(gzip.compress(d.platform.encoded(dict(lifecycle_package=package)),mtime=0))
    # A separately rehashed mirror must not replace the source-recomputed study.
    forged=deepcopy(package);forged['products'][0]['estimated_material_process_cost_usd']=1.
    (tmp_path/'lifecycle-package.json').write_bytes(d.platform.encoded(forged));calls=[]
    module=SimpleNamespace(OUTPUT=tmp_path,verify=lambda:calls.append('verify'))
    monkeypatch.setattr(d,'MODULES',('candidate_manufacturing',));monkeypatch.setattr(d,'modules',lambda:[module])
    values,_=d.verified_components()
    assert calls==['verify'] and values['candidate_manufacturing']['products'][0]['cost_usd']==123.
    assert values['candidate_manufacturing']['products'][0]['rows']==2


def test_planning_read_uses_verified_canonical_plans_without_full_regeneration(tmp_path,monkeypatch):
    folder=tmp_path/'city';folder.mkdir();(folder/'engineering/maglev').mkdir(parents=True)
    for name,data in [('city.json',{'city':{'slug':'test-city'}}),('line.corridor.geojson',{'features':[]} ),('engineering/maglev/summary.json',{})]:(folder/name).write_bytes(d.platform.encoded(data))
    length=d.platform.operating_plan.distance([0.,0.],[.01,0.]);sources={p.relative_to(tmp_path).as_posix():sha256(p.read_bytes()).hexdigest() for p in (folder/'city.json',folder/'line.corridor.geojson',folder/'engineering/maglev/summary.json')}
    plan=d.platform.seal(dict(schema=d.platform.SCHEMA,city='test-city',revision=1,parent_revision_sha256=None,actor='catalogue-import',source_sha256=sources,environment='planning',changes=[],od=[],
        lines=[dict(id='line',coordinates=[[0.,0.],[.01,0.]],length_m=length,headway_s=240.,planning_minimum_headway_s=240.,stops=[dict(id='a',chainage_m=0.,lon=0.,lat=0.,dwell_s=60.)])],**d.platform.FLAGS))
    output=tmp_path/'output';(output/'cities').mkdir(parents=True)
    (output/'cities/test-city.json.gz').write_bytes(gzip.compress(d.platform.encoded(plan),mtime=0))
    index=dict(cities=[dict(city='test-city',plan='cities/test-city.json.gz',layers='layers/test-city.json.gz',revision_sha256=plan['revision_sha256'],lines=1,stops=1)],layer_count=len(d.platform.LAYERS),**d.platform.FLAGS)
    (output/'index.json').write_bytes(d.platform.encoded(index));calls=[]
    def forbidden():raise AssertionError('Full planning payload must not regenerate in a reader')
    module=SimpleNamespace(OUTPUT=output,folders=lambda:[folder],verify=lambda **kw:calls.append(kw),payload=forbidden)
    monkeypatch.setattr(d,'ROOT',tmp_path)
    assert d._planning_summary(module)['cities']==1 and calls==[dict(recompute=False)]
    # Even coherently resealed geometry is checked against the actual alignment.
    plan['lines'][0]['stops'][0]['lat']=.01;plan=d.platform.seal(plan)
    (output/'cities/test-city.json.gz').write_bytes(gzip.compress(d.platform.encoded(plan),mtime=0))
    with pytest.raises(ValueError,match='off its alignment'):d._planning_summary(module)


def test_child_gzip_expansion_is_bounded(tmp_path,monkeypatch):
    path=tmp_path/'child.json.gz';path.write_bytes(gzip.compress(b' '*101,mtime=0));monkeypatch.setattr(d,'MAX_RAW',100)
    with pytest.raises(ValueError,match='bounded child expansion'):d._json(path)
