"""Candidate evidence is reachable through the actual public read-only handler."""
import http.client
import importlib.util
from pathlib import Path
import threading

import pytest


@pytest.fixture
def endpoint(tmp_path,monkeypatch):
    root=Path(__file__).resolve().parents[3]
    spec=importlib.util.spec_from_file_location('candidate_workbench',root/'tools/automation/maglev-workbench.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.setattr(module,'ROOT',tmp_path)
    files={'docs/design-engine/design-search/index.html':'<script src="app.js"></script>',
        'docs/design-engine/design-search/app.js':'window.candidateComparisonLoaded=true;',
        'docs/design-engine/design-search/manifest.json':'{}',
        'docs/design-engine/design-search-twins/'+'a'*64+'/README.md':'# Research twin',
        'docs/design-engine/design-search-interpretation.md':'# Interpretation',
        'engineering/design_search/README.md':'# Candidate contracts',
        'engineering/design_search/contracts.py':'private source', 'build/private.txt':'private run data',
        '.codex/config.toml':'private configuration'}
    for name,value in files.items():
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value)
    class Handler(module.Handler):
        def log_message(self,*args):pass
    server=module.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    def request(name,method='GET'):
        client=http.client.HTTPConnection('127.0.0.1',server.server_port)
        client.request(method,name);response=client.getresponse();answer=response.status,dict(response.getheaders()),response.read();client.close();return answer
    yield request
    server.shutdown();server.server_close();thread.join()


@pytest.mark.parametrize('path',[
    '/docs/design-engine/design-search/index.html','/docs/design-engine/design-search/app.js',
    '/docs/design-engine/design-search/manifest.json',
    '/docs/design-engine/design-search-twins/'+'a'*64+'/README.md',
    '/docs/design-engine/design-search-interpretation.md','/engineering/design_search/README.md'])
def test_public_candidate_assets_are_served_with_existing_content_policy(endpoint,path):
    status,headers,body=endpoint(path)
    assert status==200 and body and headers['X-Content-Type-Options']=='nosniff'
    assert "default-src 'self'" in headers['Content-Security-Policy']
    assert "connect-src 'self' blob:" in headers['Content-Security-Policy']


@pytest.mark.parametrize('path',['/engineering/design_search/contracts.py','/build/private.txt','/.codex/config.toml',
    '/docs/design-engine/design-search/%2e%2e/%2e%2e/%2e%2e/build/private.txt'])
def test_candidate_routes_do_not_expose_source_or_private_runs(endpoint,path):
    assert endpoint(path)[0]==404


def test_candidate_handler_remains_read_only(endpoint):
    assert endpoint('/docs/design-engine/design-search/manifest.json',method='POST')[0]==501
