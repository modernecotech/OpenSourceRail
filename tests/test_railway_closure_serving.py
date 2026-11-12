"""Real Workbench routes and native-proof rejection for the public dossier."""
from copy import deepcopy
from pathlib import Path
import gzip,json,threading,urllib.request,urllib.error,shutil
import pytest
from engineering.development_baseline import server
from engineering.railway_closure import ROOT,publication,coordinator,web_assets,fleet
from engineering.station_rail.common import identity,encoded,digest


@pytest.fixture(scope='module')
def study():
    return json.loads(gzip.decompress((ROOT/publication.OUTPUT/'study.json.gz').read_bytes()))


@pytest.fixture(scope='module')
def workbench():
    web_assets._verified.clear();http=server.make_server(root=ROOT,port=0)
    thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
    yield 'http://127.0.0.1:'+str(http.server_address[1])+'/'+publication.OUTPUT+'/'
    http.shutdown();thread.join(timeout=5);http.server_close()


def test_real_workbench_serves_bound_summary_and_head(workbench):
    manifest=json.loads((ROOT/publication.OUTPUT/'manifest.json').read_bytes())
    if coordinator.sources(ROOT)==manifest['source_sha256']:
        with urllib.request.urlopen(workbench+'summary.json',timeout=120) as response:v=json.load(response)
        assert v['schema']=='osr-railway-closure-summary/1'
        assert v['physical_accepted'] is False and v['integrated_selection'] is None
        assert len(v['rows'])>=6
        assert v['civil']['native_reference']['applicable'] is True
    else:
        with pytest.raises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(workbench+'summary.json',timeout=120)
        assert caught.value.code==503
        held=json.load(caught.value)
        assert 'source' in held['reason'].lower() and 'changed' in held['reason'].lower()
        assert held['physical_accepted'] is False
    # The byte-checked viewer shell remains available while numeric evidence is held.
    request=urllib.request.Request(workbench,method='HEAD')
    with urllib.request.urlopen(request,timeout=120) as response:
        assert response.status==200 and int(response.headers['Content-Length'])>0
        assert response.read()==b''


def test_warm_workbench_refuses_changed_source(workbench,monkeypatch):
    folder=(ROOT/publication.OUTPUT).resolve();manifest=folder/'manifest.json'
    recorded=json.loads(manifest.read_bytes())
    original=coordinator.sources
    if original(ROOT)==recorded['source_sha256']:
        with urllib.request.urlopen(workbench+'summary.json',timeout=120) as response:assert response.status==200
        monkeypatch.setattr(coordinator,'sources',lambda root=ROOT:{**original(root),'unexpected-source':'f'*64})
    else:
        # A token left from a previously verified epoch must not bypass source checks.
        # This does not grant the stale packet a current-source verification result.
        with web_assets._lock:web_assets._verified[str(folder)]=digest(manifest)
    try:
        with pytest.raises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(workbench+'summary.json',timeout=120)
        assert caught.value.code==503
        assert 'source changed' in json.load(caught.value)['reason'].lower()
    finally:
        with web_assets._lock:web_assets._verified.pop(str(folder),None)


def test_resealed_fabricated_native_outcome_is_rejected(study):
    changed=dict(study);changed['records']=list(study['records'])
    record=deepcopy(study['records'][0]);result=record['result']
    result['normal_arrivals']+=1;result.pop('evaluation_id');result['evaluation_id']=identity(result)
    changed['records'][0]=record
    with pytest.raises(ValueError,match='preserved execution output'):
        publication.verify_native(changed,ROOT/publication.OUTPUT,ROOT)


def test_abrupt_component_force_cannot_pass_nominal_screen(study):
    record=next(r for r in study['records'] if r['experiment']=='nominal')
    assert record['assessment']['nominal_model_screen']
    result=deepcopy(record['result'])
    next(d for d in result['departures'] if d['journey'])['energy']['release_control']['forced_cutoffs']=1
    assert fleet.screen(result,record['service'])['tests']['component_force_slew'] is False
    assert fleet.screen(result,record['service'])['nominal_model_screen'] is False


def test_legal_gzip_repacking_keeps_inner_provenance_and_outer_tamper_guard(tmp_path):
    out=tmp_path/'repacked';shutil.copytree(ROOT/publication.OUTPUT,out)
    payload=out/'study.json.gz'
    original=publication.study_value(payload.read_bytes());original_transport=digest(payload)
    original_manifest=json.loads((out/'manifest.json').read_bytes())
    source_current=coordinator.sources(ROOT)==original_manifest['source_sha256']
    raw=bytearray(payload.read_bytes());raw[9]=3 if raw[9]!=3 else 255
    payload.write_bytes(raw)
    assert digest(payload)!=original_transport
    decoded=publication.study_value(payload.read_bytes())
    assert decoded==original
    assert identity({k:v for k,v in decoded.items() if k!='study_id'})==decoded['study_id']
    with pytest.raises(ValueError,match='source/artifact changed'):publication.verify(root=ROOT,output=out)
    def seal_transport():
        m=json.loads((out/'manifest.json').read_bytes())
        m['files_sha256']['study.json.gz']=digest(payload)
        m.pop('manifest_id');m['manifest_id']=identity(m)
        (out/'manifest.json').write_bytes(encoded(m))
        return m
    m=seal_transport()
    if source_current:
        result=publication.verify(root=ROOT,output=out)
        assert result['verified'] and result['study_id']==m['study_id']
    else:
        # Repacking authenticated inner bytes never repairs stale producer bindings.
        with pytest.raises(ValueError,match='source/artifact changed'):
            publication.verify(root=ROOT,output=out)
    changed=deepcopy(decoded);native=changed['records'][0]['result']
    native['normal_arrivals']+=1
    native.pop('evaluation_id');native['evaluation_id']=identity(native)
    payload.write_bytes(gzip.compress(encoded(changed),mtime=0));seal_transport()
    tampered=publication.study_value(payload.read_bytes())
    assert identity({k:v for k,v in tampered.items() if k!='study_id'})!=tampered['study_id']
    # Even a resealed fabricated native result must resolve to preserved execution bytes.
    with pytest.raises(ValueError,match='preserved execution output'):
        publication.verify_native(tampered,out,ROOT)
    with pytest.raises(ValueError,match='Study seal differs' if source_current else 'source/artifact changed'):
        publication.verify(root=ROOT,output=out)
