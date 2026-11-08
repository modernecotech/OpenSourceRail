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
    with urllib.request.urlopen(workbench+'summary.json',timeout=120) as response:v=json.load(response)
    assert v['schema']=='osr-railway-closure-summary/1'
    assert v['physical_accepted'] is False and v['integrated_selection'] is None
    assert len(v['rows'])>=6
    assert v['civil']['native_reference']['applicable'] is True
    request=urllib.request.Request(workbench,method='HEAD')
    with urllib.request.urlopen(request,timeout=120) as response:
        assert response.status==200 and int(response.headers['Content-Length'])>0
        assert response.read()==b''


def test_warm_workbench_refuses_changed_source(workbench,monkeypatch):
    with urllib.request.urlopen(workbench+'summary.json',timeout=120) as response:assert response.status==200
    original=coordinator.sources
    monkeypatch.setattr(coordinator,'sources',lambda root=ROOT:{**original(root),'unexpected-source':'f'*64})
    with pytest.raises(urllib.error.HTTPError) as caught:urllib.request.urlopen(workbench+'summary.json',timeout=120)
    assert caught.value.code==503
    assert 'source changed' in json.load(caught.value)['reason']


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
    payload=out/'study.json.gz';raw=bytearray(payload.read_bytes());raw[9]=3 if raw[9]!=3 else 255
    payload.write_bytes(raw)
    with pytest.raises(ValueError,match='source/artifact changed'):publication.verify(root=ROOT,output=out)
    def seal_transport():
        m=json.loads((out/'manifest.json').read_bytes())
        m['files_sha256']['study.json.gz']=digest(payload)
        m.pop('manifest_id');m['manifest_id']=identity(m)
        (out/'manifest.json').write_bytes(encoded(m))
        return m
    m=seal_transport()
    result=publication.verify(root=ROOT,output=out)
    assert result['verified'] and result['study_id']==m['study_id']
    changed=json.loads(gzip.decompress(payload.read_bytes()))
    changed['records'][0]['result']['normal_arrivals']+=1
    payload.write_bytes(gzip.compress(encoded(changed),mtime=0));seal_transport()
    with pytest.raises(ValueError,match='Study seal differs'):publication.verify(root=ROOT,output=out)
