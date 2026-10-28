import json,threading,urllib.request,urllib.error
from http.server import ThreadingHTTPServer
import pytest
from engineering.sourced_case import workbench,coordinator,FLAGS,identity


def saved(tmp_path,monkeypatch,**changes):
    monkeypatch.setattr(coordinator,'sources',lambda root:{} )
    value=dict(source_sha256={},cases=[],pending=[],**FLAGS);value.update(changes);value['run_id']=identity(value)
    coordinator.write(tmp_path/'latest.json',value);return value


def test_rehashed_nested_release_is_rejected(tmp_path,monkeypatch):
    saved(tmp_path,monkeypatch,cases=[dict(manufacturing=dict(manufacturing_release=True))])
    with pytest.raises(ValueError,match='nested acceptance'):workbench.index_view(tmp_path)


def test_changed_sources_are_not_displayed_as_current(tmp_path,monkeypatch):
    saved(tmp_path,monkeypatch,source_sha256={'different.py':'0'*64})
    with pytest.raises(ValueError,match='differs'):workbench.index_view(tmp_path)


def test_http_is_read_only_and_has_no_file_route(tmp_path,monkeypatch):
    value=saved(tmp_path,monkeypatch);server=ThreadingHTTPServer(('127.0.0.1',0),workbench.handler(tmp_path))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();url='http://127.0.0.1:'+str(server.server_port)
    try:
        assert json.load(urllib.request.urlopen(url+'/api/index'))==value
        assert 'sourced design explorer' in urllib.request.urlopen(url).read().decode()
        for path,method,code in [('/api/index','POST',501),('/../latest.json','GET',404),('/api/case?index=-1','GET',400)]:
            with pytest.raises(urllib.error.HTTPError) as e:urllib.request.urlopen(urllib.request.Request(url+path,method=method))
            assert e.value.code==code
        assert coordinator.read(tmp_path/'latest.json')==value
    finally:server.shutdown();server.server_close();thread.join()
