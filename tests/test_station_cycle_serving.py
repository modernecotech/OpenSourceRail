"""Exercise the actual Workbench handler, including warm-cache source refusal."""
import json
import threading
import urllib.request
import urllib.error
import pytest
from engineering.development_baseline import server
from engineering.station_cycle import ROOT, coordinator, web_assets


@pytest.fixture(scope='module')
def live_workbench():
    web_assets._verified.clear()
    http=server.make_server(root=ROOT,port=0)
    thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
    yield 'http://127.0.0.1:'+str(http.server_address[1])
    http.shutdown();thread.join(timeout=5);http.server_close()


def test_real_workbench_serves_current_cycle_json_and_head(live_workbench):
    with urllib.request.urlopen(live_workbench+'/docs/design-engine/station-cycle/summary.json',timeout=30) as response:
        data=json.load(response)
        assert response.status==200
    assert data['schema']=='osr-station-cycle-summary/1'
    assert len(data['rows'])==18 and len(data['faults'])==254
    assert data['physical_accepted'] is False
    request=urllib.request.Request(live_workbench+'/docs/design-engine/station-cycle/',method='HEAD')
    with urllib.request.urlopen(request,timeout=30) as response:
        assert response.status==200 and int(response.headers['Content-Length'])>0
        assert response.read()==b''


def test_warm_workbench_rejects_changed_cycle_source(live_workbench,monkeypatch):
    url=live_workbench+'/docs/design-engine/station-cycle/app.js'
    with urllib.request.urlopen(url,timeout=30) as response:assert response.status==200
    original=coordinator.sources
    monkeypatch.setattr(coordinator,'sources',lambda root=ROOT:{**original(root),'unexpected-source':'f'*64})
    with pytest.raises(urllib.error.HTTPError) as caught:urllib.request.urlopen(url,timeout=30)
    assert caught.value.code==503
    body=json.load(caught.value)
    assert body['execution']=='held'
    assert 'source changed' in body['reason']
    assert body['physical_accepted'] is False
