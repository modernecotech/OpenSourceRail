"""Bounded research actions and public reports retain byte/source identity."""
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest

from engineering.design_search.contracts import encoded
from engineering.trip_dynamics import interactive as api
from engineering.trip_dynamics.tests.test_interactive import Handler


def packet(root):
    source=root/'source.py'; source.write_text('source-bound research\n')
    folder=root/api.PUBLICATIONS['electropermanent'];folder.mkdir(parents=True)
    report=folder/'README.md';report.write_text('# Electrical necessary screens\n')
    manifest=dict(schema='osr-electropermanent-publication/1',physical_accepted=False,
                  source_sha256={'source.py':sha256(source.read_bytes()).hexdigest()},
                  files_sha256={'README.md':sha256(report.read_bytes()).hexdigest()})
    (folder/'manifest.json').write_bytes(encoded(manifest))
    return source,folder,manifest


def test_public_research_file_served_by_actual_api_with_source_and_payload_checks(tmp_path):
    _,folder,_=packet(tmp_path)
    request=Handler(SimpleNamespace(root=tmp_path),'/api/trip/publications/electropermanent/README.md')
    assert api.handle_api(request) and request.code==200
    assert request.wfile.getvalue()==(folder/'README.md').read_bytes()
    assert 'sandbox' in request.response_headers['Content-Security-Policy']
    assert api.publication_path(tmp_path,'electropermanent','manifest.json')==folder/'manifest.json'


@pytest.mark.parametrize('kind',['source','payload','release','symlink','unknown-file','traversal','absolute','malformed'])
def test_public_research_tamper_and_unlisted_paths_are_refused(tmp_path,kind):
    source,folder,manifest=packet(tmp_path);name='README.md'
    if kind=='source':source.write_text('changed')
    elif kind=='payload':(folder/name).write_text('changed')
    elif kind=='release':manifest['physical_accepted']=True
    elif kind=='symlink':
        (folder/name).unlink();(folder/name).symlink_to(source)
    elif kind=='unknown-file':name='private.json';(folder/name).write_text('{}')
    elif kind=='traversal':name='../README.md'
    elif kind=='absolute':name='/etc/passwd'
    elif kind=='malformed':manifest['source_sha256']=[]
    (folder/'manifest.json').write_bytes(encoded(manifest))
    with pytest.raises((ValueError,KeyError,OSError)):
        api.publication_path(tmp_path,'electropermanent',name)


def test_research_actions_never_accept_paths_or_settings():
    for action in ('epm-screen','magnetic-confirmation'):
        assert api.validate_command(dict(action=action,parameters={}))['action']==action
        for params in ({'output':'/tmp/escape'},{'getdp':'/bin/sh'},{'cases':['unbounded']},{'voltage':10000}):
            with pytest.raises(ValueError):api.validate_command(dict(action=action,parameters=params))


def test_new_research_code_participates_in_source_epoch(tmp_path,monkeypatch):
    monkeypatch.setattr(api,'CODE_ROOT',tmp_path)
    for family in ('electropermanent','magnetic_confirmation'):
        path=tmp_path/'engineering'/family/'module.py';path.parent.mkdir(parents=True);path.write_text('original')
    before=api._code_snapshot()
    assert len(before)==2
    path.write_text('changed')
    assert api._code_snapshot()!=before
