"""The HTTP boundary uses authenticated accounts and exact revisions, not navigation roles."""
from types import SimpleNamespace
import json
from copy import deepcopy
from engineering.design_engine import http
from engineering.design_engine.runtime import request
from engineering.design_engine.store import Store
from engineering.design_engine.contracts import SCHEMA


def identity():
    return dict(schema=SCHEMA,city='samawah',project='samawah',environment='simulation',configuration_revision='research-1',baseline_sha256=None,run_id=None,asset_id=None,part_id=None)


def handler(tmp_path, data, *, actor=None, csrf=True):
    body=json.dumps(data)
    value=SimpleNamespace(path='/api/design/jobs',headers={'Content-Length':str(len(body)),'Origin':'http://localhost:1234','Host':'localhost:1234'},project_twins=SimpleNamespace(_cities={'samawah':{}}),bootstrap={'city':'samawah'},user_store=None,evidence_root=tmp_path/'evidence')
    value._actor=lambda: actor
    value._valid_csrf=lambda supplied: csrf
    value._read_json=lambda:data
    value._send_json=lambda status,payload:setattr(value,'response',(status,payload))
    return value


def test_navigation_actor_does_not_authenticate_or_bypass_csrf(tmp_path,monkeypatch):
    def forbidden(*args):raise AssertionError('unauthorized request must not initialize jobs')
    monkeypatch.setattr(http,'manager',forbidden)
    data=dict(identity=identity(),problem='clipped-side-bay',actor=dict(username='forged',roles=['admin']))
    unauthenticated=handler(tmp_path,data)
    http.post(unauthenticated);assert unauthenticated.response[0]==403
    actor=dict(username='actual',roles=['admin'],city_scopes=['samawah'])
    no_csrf=handler(tmp_path,data,actor=actor,csrf=False)
    http.post(no_csrf);assert no_csrf.response[0]==403
    wrong_city=handler(tmp_path,data,actor={**actor,'city_scopes':['mosul']})
    http.post(wrong_city);assert wrong_city.response[0]==403


def test_mutation_requires_original_configuration_revision_and_account_review(tmp_path,monkeypatch):
    store=Store(tmp_path/'store');job=store.create(request('clipped-side-bay',identity()))
    monkeypatch.setattr(http,'manager',lambda handler:SimpleNamespace(store=store))
    actor=dict(username='actual',roles=['admin'],city_scopes=['samawah'])
    changed=identity();changed['configuration_revision']='another-revision'
    call=handler(tmp_path,dict(identity=changed),actor=actor);call.path='/api/design/jobs/'+job['id']+'/cancel'
    http.post(call);assert call.response[0]==403
    assert not store.cancelled(job['id'])
    call=handler(tmp_path,dict(identity=identity(),record='record-unavailable',revision='unavailable'),actor=actor);call.path='/api/design/records/verify'
    http.post(call);assert call.response[0]==403
    assert 'named authenticated accounts' in call.response[1]['error']


def test_desktop_json_preserves_float_hashes_and_rejects_ambiguous_values():
    import pytest
    from engineering.design_engine.contracts import fingerprint
    original=dict(coordinates=[0.0,1.0,1.25])
    assert fingerprint(http.decode_definition(json.dumps(original)))==fingerprint(original)
    for invalid in ['{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}']:
        with pytest.raises(ValueError):http.decode_definition(invalid)
