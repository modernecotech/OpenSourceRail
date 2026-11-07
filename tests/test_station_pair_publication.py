"""Publication/caching integrity, using real frozen results but no native jobs."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import gzip
import json
import os
import shutil

import pytest

from engineering.station_pair import FLAGS, coordinator, native_bridge, publication
from engineering.station_rail.common import digest, encoded, identity

ROOT = Path(__file__).resolve().parents[1]


def test_generated_cargo_outputs_never_change_source_epoch(tmp_path,monkeypatch):
    base=tmp_path/'engineering/station_pair';native=base/'native'
    (native/'src').mkdir(parents=True);(native/'tests').mkdir();(base/'web').mkdir()
    for name in ('Cargo.toml','Cargo.lock'):(native/name).write_text('fixture source')
    (native/'src/lib.rs').write_text('// fixture source')
    before=native_bridge.sources(tmp_path)
    policy=tmp_path/'engineering/design_search/requirement_policy.py'
    policy.parent.mkdir(parents=True);policy.write_text('# fixture policy')
    monkeypatch.setattr(coordinator,'source_hashes',lambda root=ROOT:native_bridge.sources(root))
    published_before=publication.sources(tmp_path)
    (native/'target/debug/build/serde/out').mkdir(parents=True)
    (native/'target/debug/build/serde/out/private.rs').write_text('// generated')
    (native/'target/.rustc_info.json').write_text('{}')
    assert native_bridge.sources(tmp_path)==before
    assert publication.sources(tmp_path)==published_before
    (native/'src/lib.rs').write_text('// revised real source')
    assert native_bridge.sources(tmp_path)!=before


def seal(value, key):
    value.pop(key, None)
    value[key] = identity(value)
    return value


@pytest.fixture(scope='module')
def published(tmp_path_factory):
    """Republish the real study with current mass, cost and browser assets.

    CI requires the checked-in public study. An explicit environment override
    permits a source-bound development run before first publication.
    """
    public = ROOT/publication.OUTPUT
    override = os.environ.get('OSR_STATION_PAIR_TEST_RUN')
    if override:
        run = Path(override)
        study_raw = (run/'result.json.gz').read_bytes()
        mass_raw = (run/'mass-reconciliation.json.gz').read_bytes()
    else:
        assert (public/'study.json.gz').is_file(), 'Publish the mandatory station-pair fixture before running CI'
        study_raw = (public/'study.json.gz').read_bytes()
        mass_raw = (public/'mass-reconciliation.json.gz').read_bytes()
    study = json.loads(gzip.decompress(study_raw))
    assert study['source_sha256'] == coordinator.source_hashes(ROOT)
    base = tmp_path_factory.mktemp('station-pair-publication')
    run = base/'run';run.mkdir()
    (run/'result.json.gz').write_bytes(study_raw)
    (run/'mass-reconciliation.json.gz').write_bytes(mass_raw)
    receipt = dict(schema='osr-station-pair-run/1', study_id=study['study_id'],
        source_sha256=study['source_sha256'], files_sha256={
            n:digest(run/n) for n in ('result.json.gz','mass-reconciliation.json.gz')}, **FLAGS)
    (run/'manifest.json').write_bytes(encoded(seal(receipt,'manifest_id')))
    output = base/'publication'
    publication.publish(run,root=ROOT,output=output)
    return dict(output=output,run=run,sources=publication.sources(ROOT),study=study)


@pytest.fixture
def packet(published,tmp_path):
    output = tmp_path/'packet'
    shutil.copytree(published['output'],output)
    return output


def reseal_artifacts(output, study=None, regenerate=False):
    """Re-seal an intentional malicious edit; independent bindings must catch it."""
    if study is not None:
        seal(study,'study_id')
        if regenerate:
            _,bundle,reconciliation,_=coordinator.variants(ROOT)
            for name,raw in publication.artifacts(study,reconciliation,bundle,ROOT).items():
                (output/name).write_bytes(raw)
        else:
            (output/'study.json.gz').write_bytes(gzip.compress(encoded(study),mtime=0))
    m = json.loads((output/'manifest.json').read_bytes())
    if study is not None:m['study_id']=study['study_id']
    m['files_sha256']={p.relative_to(output).as_posix():digest(p)
                       for p in output.rglob('*') if p.is_file() and p.name!='manifest.json'}
    (output/'manifest.json').write_bytes(encoded(seal(m,'manifest_id')))


def test_real_publication_preserves_candidate_scopes_and_disabled_delivery(published):
    output=published['output'];value=publication.verify(root=ROOT,output=output)
    assert value['verified'] and value['normal_cases']==48 and value['native_replayed'] is False
    assert all(value[k] is v for k,v in FLAGS.items())
    s=json.loads((output/'summary.json').read_bytes())
    draft=json.loads(gzip.decompress((output/'delivery-draft.json.gz').read_bytes()))
    assert s['study_id']==published['study']['study_id']==draft['study_id']
    assert draft['disabled']==1 and not draft['transactions_performed']
    assert all(c['body_candidate_id']==s['body_candidate_id'] for c in draft['candidates'])
    assert all(c['disabled']==1 and c['executable_work_order'] is False for c in draft['candidates'])
    assert all(r['full_grid_kwh'] is None for r in s['rows'] if r['family'] in ('compact-LIM','hybrid'))


def test_publication_rejects_changed_source_epoch(packet,published,monkeypatch):
    changed=dict(published['sources']);changed['engineering/station_pair/coordinator.py']='0'*64
    monkeypatch.setattr(publication,'sources',lambda root=ROOT:changed)
    with pytest.raises(ValueError,match='source/artifact'):
        publication.verify(root=ROOT,output=packet)


@pytest.mark.parametrize('change',['changed','missing','symlink'])
def test_publication_rejects_changed_missing_and_nonordinary_artifacts(packet,tmp_path,change):
    target=packet/'app.js'
    if change=='changed':target.write_bytes(b'changed script')
    elif change=='missing':target.unlink()
    else:
        target.unlink();outside=tmp_path/'outside.js';outside.write_bytes(b'/* inert fixture */');target.symlink_to(outside)
    with pytest.raises((ValueError,OSError)):
        publication.verify(root=ROOT,output=packet)


@pytest.mark.parametrize('change',['candidate','cost','release'])
def test_resealed_study_cannot_mix_candidate_cost_or_release(packet,change):
    s=json.loads(gzip.decompress((packet/'study.json.gz').read_bytes()))
    if change=='candidate':s['cases'][0]['request']['candidate_id']='f'*64
    elif change=='cost':s['cases'][0]['cost']['methods'][0]['installed_capital_usd']['base']-=1000
    else:s['physical_accepted']=True
    reseal_artifacts(packet,s)
    with pytest.raises(ValueError):publication.verify(root=ROOT,output=packet)


def test_resealed_native_request_is_checked_against_the_declared_nominal_case(packet):
    s=json.loads(gzip.decompress((packet/'study.json.gz').read_bytes()))
    c=s['cases'][0];q=c['request'];q['mass_kg']+=1000
    q['id']=identity({k:v for k,v in q.items() if k!='id'})
    c['journey']['id']=q['id'];c['journey']['native_input_id']=identity(q)
    seal(c['journey'],'evaluation_id')
    brief,bundle,reconciliation,_=coordinator.variants(ROOT)
    c['cost']=publication.economics.evaluate(c['variant'],c['journey'],bundle,reconciliation,brief,root=ROOT)
    c['summary'].update(coordinator._brief_result(c['variant'],q,c['journey'],c['cost'],brief))
    s['rows']=[row['summary'] for row in s['cases']]
    reseal_artifacts(packet,s,regenerate=True)
    with pytest.raises(ValueError,match='Nominal request differs'):
        publication.verify(root=ROOT,output=packet)


def fake_kernel(tmp_path,monkeypatch):
    """Synthetic bridge transport fixture, never used as engineering evidence."""
    binary=tmp_path/'fake-kernel';binary.write_bytes(b'not executed')
    pin={'synthetic-fixture.rs':'e'*64}
    build=dict(source_sha256=pin,binary_sha256=digest(binary),fixture_only=True)
    build['receipt_id']=identity(build)
    monkeypatch.setattr(native_bridge,'sources',lambda root=ROOT:pin)
    monkeypatch.setattr(native_bridge.shutil,'which',lambda name:'/usr/bin/prlimit')
    monkeypatch.setattr(native_bridge.subprocess,'check_output',lambda *a,**k:'prlimit synthetic fixture\n')
    calls=[]
    def run(args,**kw):
        calls.append(args);request=json.loads(kw['input'])
        rows=[dict(id=c['id'],candidate_id=c['candidate_id'],conditional=True,
                   physical_accepted=False,engineering_accepted=False,
                   operating_release=False,admitted_operating_map=False) for c in request['cases']]
        return SimpleNamespace(returncode=0,stdout=encoded(dict(schema='osr-journey-result/1',cases=rows)))
    monkeypatch.setattr(native_bridge.subprocess,'run',run)
    state=tmp_path/'state';state.mkdir()
    case=dict(id='fixture-case',candidate_id='a'*64,fixture_only=True)
    return state,case,(binary,build),calls


def test_native_cache_reuses_only_the_exact_request_without_executing(tmp_path,monkeypatch):
    state,case,kernel,calls=fake_kernel(tmp_path,monkeypatch)
    first=native_bridge.execute([case],state,root=ROOT,kernel=kernel)
    assert native_bridge.execute([case],state,root=ROOT,kernel=kernel)==first
    assert len(calls)==1
    assert first[0]['native_input_id']==identity(case)


@pytest.mark.parametrize('change',['input-bytes','resealed-input','mixed-output','released-output'])
def test_native_cache_rejects_tampered_input_and_resealed_mixed_outputs(tmp_path,monkeypatch,change):
    state,case,kernel,calls=fake_kernel(tmp_path,monkeypatch)
    native_bridge.execute([case],state,root=ROOT,kernel=kernel)
    folder=next((state/'native-runs').iterdir());r=json.loads((folder/'receipt.json').read_bytes())
    if change in ('input-bytes','resealed-input'):
        altered=dict(schema='osr-journey-request/1',cases=[dict(case,candidate_id='b'*64)])
        (folder/'input.json.gz').write_bytes(gzip.compress(encoded(altered),mtime=0))
        if change=='resealed-input':r['input_gzip_sha256']=digest(folder/'input.json.gz')
    else:
        value=json.loads(gzip.decompress((folder/'output.json.gz').read_bytes()))
        if change=='mixed-output':value['cases'][0]['candidate_id']='b'*64
        else:value['cases'][0]['physical_accepted']=True
        (folder/'output.json.gz').write_bytes(gzip.compress(encoded(value),mtime=0))
        r['output_sha256']=digest(folder/'output.json.gz')
    (folder/'receipt.json').write_bytes(encoded(seal(r,'receipt_id')))
    with pytest.raises(ValueError):native_bridge.execute([case],state,root=ROOT,kernel=kernel)
    assert len(calls)==1


def test_native_cache_separates_runtime_context_without_executing_real_processes(tmp_path,monkeypatch):
    state,case,kernel,calls=fake_kernel(tmp_path,monkeypatch)
    native_bridge.execute([case],state,root=ROOT,kernel=kernel)
    monkeypatch.setattr(native_bridge.platform,'machine',lambda:'synthetic-different-machine')
    native_bridge.execute([case],state,root=ROOT,kernel=kernel)
    assert len(calls)==2 and len(list((state/'native-runs').iterdir()))==2
