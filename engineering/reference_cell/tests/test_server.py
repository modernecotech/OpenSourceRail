"""Actual local HTTP review server; no activation and no arbitrary filesystem API."""
from contextlib import contextmanager
from pathlib import Path
from threading import Thread
from urllib.request import urlopen,Request
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
import gzip,json,shutil
import pytest
from engineering.reference_cell import server as s,coordinator as c,encoded,identity
from engineering.reference_cell.tests.test_coordinator import actual_cell,read,write


@pytest.fixture(scope='module')
def local_server(actual_cell,tmp_path_factory):
    folder=tmp_path_factory.mktemp('http-review-state')/'state';shutil.copytree(actual_cell[0],folder)
    handler=s.handler(folder);server=ThreadingHTTPServer(('127.0.0.1',0),handler)
    worker=Thread(target=server.serve_forever,daemon=True);worker.start()
    yield 'http://127.0.0.1:'+str(server.server_port),folder,actual_cell[1]
    server.shutdown();server.server_close();worker.join(timeout=5)


def get(base,path):
    with urlopen(base+path,timeout=60) as r:
        raw=r.read();return r.status,dict(r.headers),gzip.decompress(raw) if r.headers.get('Content-Encoding')=='gzip' else raw


def test_actual_summary_and_case_share_exact_candidate_and_explicit_hold_flags(local_server):
    base,folder,index=local_server;status,headers,data=get(base,'/api/summary');v=json.loads(data)
    assert status==200 and headers['Cache-Control']=='no-store' and headers['X-Content-Type-Options']=='nosniff'
    assert len(v['cases'])==1 and len(v['pending'])==9 and v['physical_accepted'] is False
    name=index['cases'][0]['request']['vehicle_id'];distance=str(int(index['cases'][0]['request']['distance_m']))
    status,h,data=get(base,'/api/case/'+name+'/'+distance);case=json.loads(data)
    assert status==200 and case['candidate_id']==v['cases'][0]['candidate_id']
    assert case['completed_production_journeys']==0 and case['available_operating_maps']==0
    assert case['manufacturing']['whole_life_cost_usd'] is None


def test_vehicle_registry_explorer_preserves_body_projection_identity(local_server):
    base,folder,index=local_server;name=index['cases'][0]['request']['vehicle_id']
    status,h,data=get(base,'/api/vehicle/'+name);vehicle=json.loads(data)
    assert status==200 and vehicle['registry']['candidate_id']==index['cases'][0]['summary']['body_candidate_id']
    assert vehicle['summary']['mass_upper_bound_kg']>vehicle['summary']['mass_lower_bound_kg']>0
    assert not vehicle['registry']['physical_accepted']


@pytest.mark.parametrize('method',['POST','PUT','PATCH','DELETE'])
def test_mutating_http_methods_are_explicitly_refused(local_server,method):
    base,folder,index=local_server
    with pytest.raises(HTTPError) as caught:urlopen(Request(base+'/api/activate',data=b'{}',method=method),timeout=10)
    assert caught.value.code==405


@pytest.mark.parametrize('path',['/api/case/V1/9999','/api/case/../../etc/passwd','/api/vehicle/../V1',
 '/api/vehicle/nested/V1','/api/vehicle/%2e%2e%2fetc%2fpasswd','/../AGENTS.md','/%2e%2e/AGENTS.md','/api/activate','/api/vehicle/V99'])
def test_unknown_candidate_routes_and_traversal_aliases_are_not_served(local_server,path):
    with pytest.raises(HTTPError) as caught:urlopen(local_server[0]+path,timeout=10)
    assert caught.value.code==404


@pytest.mark.parametrize('path,kind',[('/','text/html'),('/app.js','javascript'),('/app.css','text/css'),('/geography','text/html')])
def test_owned_static_views_and_current_geography_hold_render_without_historical_control_link(local_server,path,kind):
    status,h,data=get(local_server[0],path)
    assert status==200 and kind in h['Content-Type'] and data
    assert b'file://' not in data
    if path=='/geography':
        assert b'266' in data and b'held' in data and b'historical planning editor' in data
        assert b'/ferrite-maglev/' not in data


def test_z_post_start_case_mutation_cannot_be_served_as_trusted_current_evidence(local_server):
    base,folder,index=local_server;row=index['cases'][0];path=folder/row['path'];original=path.read_bytes()
    v=read(path);v['completed_production_journeys']=999;write(path,v)
    name=row['request']['vehicle_id'];distance=str(int(row['request']['distance_m']))
    try:
        try:
            status,h,data=get(base,'/api/case/'+name+'/'+distance)
        except HTTPError as error:
            assert error.code in (409,503)
        else:
            # An immutable verified in-memory snapshot is also valid. Re-reading
            # forged mutable bytes after a one-time startup check is not.
            assert json.loads(data)['completed_production_journeys']==0
    finally:path.write_bytes(original)


def test_uncounted_pending_candidate_is_held_instead_of_serving_another_case(local_server):
    with pytest.raises(HTTPError) as caught:urlopen(local_server[0]+'/api/case/V5/2000',timeout=10)
    assert caught.value.code==404
