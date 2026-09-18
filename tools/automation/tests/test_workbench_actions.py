"""Browser mutation boundary: no ambient integration authority or arbitrary proxy."""
import http.client
import importlib.util
import io
import json
from pathlib import Path
import threading
from urllib.error import HTTPError

import pytest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('workbench_actions', ROOT / 'tools/automation/workbench-server.py')
WB = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WB)


@pytest.fixture
def endpoint():
    class Handler(WB.WorkbenchHandler):
        def log_message(self, *args):
            pass
    server = WB.OPS.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    def request(path, headers=None, body=None):
        client = http.client.HTTPConnection('127.0.0.1', server.server_port)
        client.request('POST', '/api/lifecycle/' + path, json.dumps(body or {}), headers or {})
        response = client.getresponse()
        result = response.status, json.loads(response.read())
        client.close()
        return result
    yield request, f'http://127.0.0.1:{server.server_port}'
    server.shutdown()
    server.server_close()
    thread.join()


def test_actions_require_same_origin_and_explicit_credential(endpoint, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('unauthorized request reached integration')
    monkeypatch.setattr('urllib.request.urlopen', forbidden)
    request, origin = endpoint
    assert request('commands')[0] == 403
    assert request('commands', {'Origin': origin})[0] == 403
    assert request('commands', {'Origin': 'https://foreign.invalid', 'Authorization': 'Bearer test'})[0] == 403
    assert request('packages', {'Origin': origin, 'Authorization': 'Bearer test'})[0] == 404


@pytest.mark.parametrize("action", ["alarms/acknowledge", "evidence"])
def test_action_passes_only_caller_token_and_preserves_gateway_denial(endpoint, monkeypatch, action):
    request, origin = endpoint
    def denied(req, **kwargs):
        assert req.full_url == 'http://127.0.0.1:8092/' + action
        assert req.get_header('Authorization') == 'Bearer caller-token'
        assert json.loads(req.data)['city'] == 'outside-scope'
        raise HTTPError(req.full_url, 403, 'Forbidden', {}, io.BytesIO(b'{"error":"City/environment outside authenticated scope"}'))
    monkeypatch.setattr('urllib.request.urlopen', denied)
    status, payload = request(action, {'Origin': origin, 'Authorization': 'Bearer caller-token'}, {'city': 'outside-scope'})
    assert status == 403
    assert 'outside authenticated scope' in payload['error']


def test_change_impact_uses_prepared_package_and_server_side_viewer_credential(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/automation'))
    package = {'city': 'samawah', 'environment': 'simulation', 'sha256': 'prepared',
               'engineering_revision': 'rev1', 'equipment': [{'erp_project':'P1','company_id':'Company'}]}
    folder = tmp_path / 'build/supervision/samawah/simulation'
    folder.mkdir(parents=True)
    (folder / 'package.json').write_text(json.dumps(package))
    private = tmp_path / 'var/supervision'
    private.mkdir(parents=True)
    (private / 'integration.json').write_text(json.dumps({'principals': [
        {'role': 'viewer', 'token': 'server-viewer'}]}))
    monkeypatch.setattr(WB, 'REPO_ROOT', tmp_path)
    monkeypatch.setattr(WB, 'SUPERVISION_ROOT', tmp_path/'build/supervision')
    monkeypatch.setattr(WB, 'SUPERVISION_CONFIG', private/'integration.json')
    monkeypatch.setattr(WB, 'ERP_SNAPSHOT', private/'missing-snapshot.json')

    class Response(io.BytesIO):
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *args):
            self.close()

    def preview(request, **kwargs):
        assert request.full_url == 'http://127.0.0.1:8092/packages/preview'
        assert request.method == 'POST'
        assert request.get_header('Authorization') == 'Bearer server-viewer'
        assert json.loads(request.data) == {'package': package}
        return Response(b'{"schema":"osr-supervisory-change-review/1","status":"no-change"}')
    monkeypatch.setattr('urllib.request.urlopen', preview)

    class Handler(WB.WorkbenchHandler):
        def log_message(self, *args):
            pass
    server = WB.OPS.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    client = http.client.HTTPConnection('127.0.0.1', server.server_port)
    client.request('GET', '/api/lifecycle/change-impact?city=samawah&environment=simulation')
    response = client.getresponse()
    assert response.status == 200
    result=json.loads(response.read())
    assert result['status'] == 'no-change'
    assert not result['cross_domain']['observations_current']
    assert not result['cross_domain']['engineering_release_ready']
    client.close()
    server.shutdown(); server.server_close(); thread.join()
