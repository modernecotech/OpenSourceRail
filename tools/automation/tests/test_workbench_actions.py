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


def test_action_passes_only_caller_token_and_preserves_gateway_denial(endpoint, monkeypatch):
    request, origin = endpoint
    def denied(req, **kwargs):
        assert req.full_url == 'http://127.0.0.1:8092/alarms/acknowledge'
        assert req.get_header('Authorization') == 'Bearer caller-token'
        assert json.loads(req.data)['city'] == 'outside-scope'
        raise HTTPError(req.full_url, 403, 'Forbidden', {}, io.BytesIO(b'{"error":"City/environment outside authenticated scope"}'))
    monkeypatch.setattr('urllib.request.urlopen', denied)
    status, payload = request('alarms/acknowledge', {'Origin': origin, 'Authorization': 'Bearer caller-token'}, {'city': 'outside-scope'})
    assert status == 403
    assert 'outside authenticated scope' in payload['error']
