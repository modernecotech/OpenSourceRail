"""Bounded source projections and read-only HTTP; no physics recomputation."""
import importlib.util
from pathlib import Path
import json
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen,Request
from urllib.error import HTTPError
import pytest

P=Path(__file__).resolve().parents[1]/'sourced-workbench.py';spec=importlib.util.spec_from_file_location('sourced_display',P);s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

class NoIter(list):
    def __iter__(self):raise AssertionError('Full ERP payload must neverbe iterated fordisplay')


def fixture_raw():
    routes=[dict(candidate_id='a'*64,part_definition_id=str(i),quantity=i+1,operations=[dict(sequence=1,name='inspect')]) for i in range(120)]
    manufacturing=dict(candidate_id='a'*64,evaluation_id='c'*64,routings=routes,ERPNext_drafts=dict(candidate_id='a'*64,export_id='d'*64,
       item_drafts=NoIter([{'NEVER-RENDER':'x'*1000}]*20000),BOM_drafts=NoIter([{}]*10000),submission_allowed=False,docstatus=0,items_disabled=True,active_BOMs=False,external_transactions_performed=False),whole_life_cost_usd=None)
    return dict(candidate_id='a'*64,body_candidate_id='b'*64,vehicle_id='V1',variant='x',distance_m=2000,distributed=False,ambient_C=55,
      drive_configuration={},vehicle_summary={'installed_mass':None},partial_public_price={'known_subtotal':17,'whole_life_cost':None},
      auxiliary_power={},charging=dict(trace=[dict(t=i,SOC=.6) for i in range(10000)]),conditional_arrivals=1,
      journeys=[dict(name='nominal',result=dict(evaluation_id='f'*64,trajectory=[dict(front_m=i,speed_m_s=i%20) for i in range(4000)],electrical_duty=dict(samples=list(range(5000))),qualified_numerical_arrival=False))],
      manufacturing=manufacturing,closure=dict(next_tasks=list(range(100)),qualified_journeys=0))

@pytest.fixture
def contracts(monkeypatch):
    r=fixture_raw();run=dict(run_id='e'*64,cases=[dict(evaluation_id='f'*64,candidate_id='a'*64)])
    monkeypatch.setattr(s.frozen,'index_view',lambda *args:run)
    monkeypatch.setattr(s.frozen,'case_view',lambda *args:r)
    monkeypatch.setattr(s.frozen,'part_view',lambda *args:dict(parts=[dict(part_id=str(i)) for i in range(100)]))
    return r,run


def test_manufacturing_drops_ERP_before_serialization(contracts):
    r=s.case_view('unused',0)
    m=r['manufacturing'];raw=json.dumps(r)
    assert len(m['routing_groups'])==20 and m['routing_groups_total']==120
    assert m['ERPNext_draft_status']['item_drafts_count']==20000
    assert m['ERPNext_draft_status']['BOM_drafts_count']==10000
    assert 'NEVER-RENDER' not in raw and '"item_drafts":' not in raw
    assert len(raw)<250000
    assert m['evaluation_id']=='c'*64 and r['evaluation_id']=='f'*64
    assert not m['ERPNext_draft_status']['submission_allowed']


def test_source_trajectories_and_SOC_are_sampled_not_invented(contracts):
    original=contracts[0];r=s.case_view('unused',0)
    points=r['journeys'][0]['result']['trajectory']
    assert len(points)==1000
    assert points[0]==original['journeys'][0]['result']['trajectory'][0]
    assert points[-1]==original['journeys'][0]['result']['trajectory'][-1]
    assert r['journeys'][0]['result']['trajectory_original_count']==4000
    assert r['charging']['trace_original_count']==10000
    assert len(r['charging']['trace'])==30
    assert r['closure']['next_tasks_original_count']==100
    assert len(r['closure']['next_tasks'])==30
    assert r['vehicle_summary']['installed_mass'] is None
    assert r['partial_public_price']['whole_life_cost'] is None


def test_part_drill_reuses_contract_with_bound(contracts):
    r=s.part_view('unused',0,'battery')
    assert r['parts_original_count']==100 and len(r['parts'])==30


def test_saved_closure_matches_run_without_build(tmp_path,contracts):
    report=dict(schema='osr-sourced-engineering-closure-dashboard/1',run_id='e'*64,counts={'cases':30},phases=[dict(phase_id='P0',completion=None)],**s.FLAGS)
    report['evaluation_id']=s.identity(report);p=tmp_path/'closure.json';p.write_text(json.dumps(report))
    r=s.case_view('unused',0,closure_report=p)
    assert r['closure']['saved_report_projection']['counts']['cases']==30
    report['run_id']='0'*64;report.pop('evaluation_id');report['evaluation_id']=s.identity(report);p.write_text(json.dumps(report))
    with pytest.raises(ValueError):s.case_view('unused',0,closure_report=p)


def test_HTTP_five_views_parts_and_mutations_refused(contracts):
    server=ThreadingHTTPServer(('127.0.0.1',0),s.handler('unused'));thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    base='http://127.0.0.1:'+str(server.server_port)
    try:
        html=urlopen(base+'/').read().decode()
        for view in ('Design','Mass and cost','Simulation','Closure','Manufacturing'):assert view in html
        with urlopen(base+'/api/case?index=0') as response:
            value=json.load(response);assert response.headers['Cache-Control']=='no-store'
        assert value['manufacturing']['routing_groups_total']==120
        assert json.load(urlopen(base+'/api/parts?index=0&search=battery'))['parts_original_count']==100
        for method in ('POST','PUT','DELETE'):
            with pytest.raises(HTTPError) as error:urlopen(Request(base+'/api/case?index=0',method=method))
            assert error.value.code==405
        for path in ('/api/case?index=0&extra=bad','/../../etc/passwd'):
            with pytest.raises(HTTPError):urlopen(base+path)
    finally:server.shutdown();server.server_close();thread.join(2)


def test_mixed_projection_identity_refused(contracts):
    contracts[1]['cases'][0]['candidate_id']='0'*64
    with pytest.raises(ValueError):s.case_view('unused',0)


def test_saved_gzip_closure_supported(tmp_path,contracts):
    import gzip
    report=dict(schema='osr-sourced-engineering-closure-dashboard/1',run_id='e'*64,counts={'cases':30},phases=[],**s.FLAGS)
    report['evaluation_id']=s.identity(report)
    p=tmp_path/'closure.json.gz';p.write_bytes(gzip.compress(json.dumps(report).encode()))
    value=s.case_view('unused',0,closure_report=p)
    assert value['closure']['saved_report_projection']['evaluation_id']==report['evaluation_id']
    assert value['closure']['saved_report_projection']['counts']['cases']==30


def test_gzip_closure_decompression_budget_and_truncation(tmp_path,contracts,monkeypatch):
    import gzip
    monkeypatch.setattr(s,'MAX_CLOSURE_BYTES',1024)
    p=tmp_path/'bomb.json.gz';p.write_bytes(gzip.compress(b' '*1025))
    with pytest.raises(ValueError,match='decompression budget'):s.case_view('unused',0,closure_report=p)
    p=tmp_path/'truncated.json.gz';p.write_bytes(gzip.compress(b'{}')[:-5])
    with pytest.raises(ValueError,match='Malformed'):s.case_view('unused',0,closure_report=p)
