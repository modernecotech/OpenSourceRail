"""Constraint, recovery, offline and interoperability acceptance for review items 1–6."""
import base64
import copy
import hashlib
import http.client
import io
import json
import sys
import threading
import time
import zipfile
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'services/integration'))
sys.path.insert(0, str(ROOT / 'deployment/erpnext/apps/osr_erpnext'))
from osr_integration.config import digest
from osr_integration.store import Store
from osr_integration.server import GatewayHTTPServer, Handler, deliver_field_events
from osr_integration.operations.contracts import validate
from osr_integration.operations.planning import conflict, fleet_diagram, plan
from osr_integration.operations.roster import optimise
from osr_integration.operations.store import OperationsStore
from osr_integration.operations.field import Conflict, validate_completion
from osr_integration.operations.reliability import analyse, calibrate, estimate, forecast
from osr_integration.operations.exchange import (gtfs_import, gtfs_realtime, gtfs_schedule,
    operational_export, operational_import, operator_exchange, passenger_updates)
from osr_erpnext.field_contract import verify


def package():
    return json.loads((ROOT / 'engineering/operations/fixtures/pilot.json').read_text())


def disruption():
    return json.loads((ROOT / 'engineering/operations/fixtures/disruptions.json').read_text())


def test_combined_closure_train_charger_and_staff_recovery():
    p = package(); normal = plan(p); recovered = plan(p, disruption())
    assert len(normal['services']) == len(recovered['services']) == 3
    assert not recovered['search_exhausted']
    assert not recovered['movement_authority']
    assert recovered['input_sha256'] == digest(p)
    assert all(row['train_id'] != 'T2' for row in recovered['services'])
    assert all(row['worker_id'] != 'W1' for row in recovered['roster']['assignments'])
    assert recovered['services'][0]['path_id'] == 'ACB'
    assert all(row.get('charger_id') != 'CH-B1' for row in recovered['fleet_diagram'])
    assert any(row.get('charger_id') == 'CH-B2' for row in recovered['fleet_diagram'])
    assert any(row['kind'] == 'inspection' for row in recovered['fleet_diagram'])
    claims = []
    scenario = copy.deepcopy(p); scenario['possessions'] = disruption()['possessions']
    for row in recovered['fleet_diagram']:
        additions = [dict(c, train_id=row['train_id']) for c in row['claims']]
        assert conflict(scenario, claims, additions) is None
        claims += additions
    assert plan(p, disruption()) == recovered


@pytest.mark.parametrize('mutate', [
    lambda p: p['paths'][0].update(edges=['AB-e', 'AC-e']),
    lambda p: p['edges'][0].update(resources=[]),
    lambda p: p['resources'][0].update(capacity=True),
    lambda p: p['trains'][0].update(energy_kwh=float('nan')),
    lambda p: p['services'][0].update(path_ids=['unknown']),
    lambda p: p.update(possessions=[{'id':'P','resources':['unknown'],'start_s':0,'end_s':10}]),
])
def test_invalid_physical_network_fails_closed(mutate):
    p = package(); mutate(p)
    with pytest.raises(ValueError): validate(p)


def test_capacity_sweep_and_tail_headway():
    p = package(); p['resources'][0]['capacity'] = 2; p['resources'][0]['headway_s'] = 0
    assert conflict(p, [dict(resource='AB',start_s=0,end_s=10),dict(resource='AB',start_s=20,end_s=30)], [dict(resource='AB',start_s=0,end_s=30)]) is None
    assert conflict(p, [dict(resource='AB',start_s=0,end_s=30),dict(resource='AB',start_s=0,end_s=30)], [dict(resource='AB',start_s=20,end_s=25)])
    p['resources'][0].update(capacity=1,headway_s=30)
    assert conflict(p, [dict(resource='AB',start_s=0,end_s=10)], [dict(resource='AB',start_s=39,end_s=50)])
    assert conflict(p, [dict(resource='AB',start_s=0,end_s=10)], [dict(resource='AB',start_s=40,end_s=50)]) is None


def test_search_budget_and_infeasible_service_do_not_claim_optimality():
    p = package(); p['search_budget'] = 1
    result = plan(p)
    assert result['search_exhausted'] and not result['optimal_within_declared_dispatch_policy']
    result = plan(package(), {'unavailable_trains':['T1','T2','T3']})
    assert len(result['cancelled']) == 3 and not result['services']


def test_unconnected_train_does_not_teleport_and_inspection_deadline_is_enforced():
    p = package(); p['trains'] = [p['trains'][0]]; p['fleet_jobs'] = []
    p['trains'][0]['node'] = 'C'; p['paths'] = [p['paths'][0],p['paths'][1]]
    p['services'] = [dict(p['services'][0],path_ids=['AB'])]
    assert not plan(p)['services']
    p = package(); p['trains'] = [p['trains'][0]]; p['fleet_jobs'] = []
    p['trains'][0]['maintenance_by_s'] = 100
    assert not plan(p)['services']


def test_repositioning_leg_and_energy_are_retained():
    p = validate(package()); p['fleet_jobs'] = []; p['trains'] = [p['trains'][0]]
    service = plan(package())['services'][1]
    diagram, reason = fleet_diagram(p, [dict(service, train_id='T1')])
    assert reason is None
    assert any(row['kind'] == 'deadhead' for row in diagram)
    assert all(row.get('remaining_energy_kwh', 2) >= 2 for row in diagram)


def test_staff_competence_expiry_rest_travel_and_fair_change_preference():
    p = package(); p['workers'][0]['competencies'][0]['expires_s'] = 1800
    result = optimise(p)
    assert next(r for r in result['assignments'] if r['duty_id']=='OCC-day')['worker_id'] != 'W1'
    for w in p['workers']: w['previous_shift_end_s']=0
    assert len(optimise(p)['uncovered']) == 2
    p = package(); p['workers'] = [p['workers'][0]]
    p['duties'][1].update(start_s=1800,end_s=2000)
    assert len(optimise(p)['uncovered']) == 1
    p['staff_travel']=[dict(id='travel', **{'from':'HQ','to':'A'},duration_s=0)]
    assert not optimise(p)['uncovered']
    assert not any(r['role']=='driver' for r in optimise(p)['assignments'])


@pytest.fixture
def operations(tmp_path):
    store=Store(tmp_path/'operations.sqlite'); ops=OperationsStore(store)
    baseline=ops.register(package(),'engineer',None)
    asset=dict(asset_id='A:charger',city='samawah',environment='simulation',engineering_revision='operations-pilot-v1',
               erp_asset_id='ASSET-1',company_id='OSR-Pilot',erp_project='PROJ-1')
    with store.connect() as db:
        db.execute('INSERT INTO assets(scope,city,environment,asset_id,package,body) VALUES(?,?,?,?,?,?)',
            ('samawah|simulation|A:charger','samawah','simulation','A:charger',baseline['sha256'],json.dumps(asset)))
    return store,ops,baseline


def work():
    return dict(id='WORK-1',city='samawah',environment='simulation',asset_id='A:charger',assigned_to='tech',
        method_revision='METHOD-1',erp_task='TASK-1',erp_asset='ASSET-1',native_modified='2026-10-12 06:00:00',
        expires_at='2099-01-01T00:00:00Z',requires_photo=True,
        readings=[dict(id='voltage',kind='number',unit='V',min=0,max=1000,required=True),
                  dict(id='isolated',kind='boolean',required=True)])


def event():
    content=b'\x89PNG\r\n\x1a\n'+b'fixture-image-data'
    return dict(id='EVENT-1',device_id='DEVICE-1',work_id='WORK-1',status='performed-awaiting-inspection',
        readings={'voltage':{'value':48,'unit':'V'},'isolated':True},notes='Recorded for inspection',
        photos=[dict(id='PHOTO-1',mime='image/png',sha256=hashlib.sha256(content).hexdigest(),base64=base64.b64encode(content).decode())])


def test_offline_idempotency_restart_and_independent_erp_contract(operations):
    store,ops,b=operations; pack=ops.issue_work(work(),'engineer',b['sha256']); first=ops.complete('samawah','simulation',event(),'tech')
    assert first['state']=='pending'
    restarted=OperationsStore(Store(store.path))
    assert restarted.complete('samawah','simulation',event(),'tech')['duplicate']
    with store.connect() as db: packet=json.loads(db.execute('SELECT body FROM field_events').fetchone()['body'])
    assert verify(packet)==packet
    bad=event(); bad['notes']='Changed'
    with pytest.raises(Conflict): restarted.complete('samawah','simulation',bad,'tech')
    packet['event']['readings']['voltage']['unit']='A'
    packet['idempotency_sha256']=digest(dict(event=packet['event'],actor='tech',scope='samawah|simulation'))
    with pytest.raises(ValueError): verify(packet)
    assert pack['operational_release'] is False


@pytest.mark.parametrize('change', ['baseline','engineering','serial','revoked','assignment'])
def test_offline_revalidation_rejects_changed_state(operations,change):
    store,ops,b=operations; ops.issue_work(work(),'engineer',b['sha256'])
    if change=='baseline':
        p=package();p['revision']='v2';ops.register(p,'engineer',b['sha256'])
    elif change=='engineering':
        with store.connect() as db:
            a=json.loads(db.execute('SELECT body FROM assets').fetchone()['body']);a['engineering_revision']='v2'
            db.execute('UPDATE assets SET body=?',(json.dumps(a),))
    elif change=='serial':
        with store.connect() as db: db.execute('INSERT INTO installations VALUES(?,?,?,?,?,?,?,NULL)',('I1','samawah|simulation|A:charger','new-serial','batch','v1','evidence',time.time()))
    elif change=='revoked': ops.revoke('samawah','simulation','WORK-1','engineer')
    with pytest.raises((Conflict,PermissionError)):
        ops.complete('samawah','simulation',event(),'other-tech' if change=='assignment' else 'tech')


def test_photo_and_unit_validation(operations):
    _,ops,b=operations;pack=ops.issue_work(work(),'engineer',b['sha256'])
    for mutation in [lambda e:e['readings']['voltage'].update(unit='A'), lambda e:e['photos'][0].update(sha256='0'*64),lambda e:e.update(photos=[]),lambda e:e['readings'].update(unknown=4)]:
        e=event();mutation(e)
        with pytest.raises(ValueError):validate_completion(pack,e)


def test_durable_native_delivery_retries_then_retains_native_receipt(operations):
    store,ops,b=operations;ops.issue_work(work(),'engineer',b['sha256']);ops.complete('samawah','simulation',event(),'tech')
    cfg=dict(url='http://erp.invalid',key='test',secret='test')
    with patch('osr_integration.server.request_json',side_effect=URLError('offline')):deliver_field_events(store,cfg,0)
    assert ops.events('samawah','simulation','tech')[0]['state']=='pending'
    with patch('osr_integration.server.request_json',return_value={'message':{'execution':'EXEC-1','operational_release':False}}):deliver_field_events(store,cfg,1000)
    assert ops.events('samawah','simulation','tech')[0]['response']['execution']=='EXEC-1'


def test_native_conflict_is_terminal_without_disclosing_response(operations):
    store,ops,b=operations;ops.issue_work(work(),'engineer',b['sha256']);ops.complete('samawah','simulation',event(),'tech')
    error=HTTPError('http://erp.invalid',409,'conflict',{},io.BytesIO(b'secret'))
    with patch('osr_integration.server.request_json',side_effect=error):deliver_field_events(store,dict(url='http://erp.invalid',key='x',secret='secret'),0)
    row=ops.events('samawah','simulation','tech')[0]
    assert row['state']=='rejected' and 'secret' not in row['error']


def test_native_export_import_and_gtfs_timetable_round_trip():
    p=package(); r=plan(p,disruption());payload=operational_export(p,r)
    assert operational_import(payload)==p
    imported=gtfs_import(gtfs_schedule(p),'20261012')
    assert len(imported['trips'])==3 and imported['requires_physical_path_mapping']
    assert [stop['stop_id'] for stop in imported['trips'][0]['stops']]==['A','B']
    feed=passenger_updates(p,r,1800000000)
    assert len(feed['entity'])==3 and feed['header']['timestamp']==1800000000
    assert gtfs_realtime(feed).startswith(b'\x0a')
    payload['package']['revision']='tampered'
    with pytest.raises(ValueError): operational_import(payload)


def test_gtfs_realtime_is_decodable_by_official_bindings():
    from google.transit import gtfs_realtime_pb2
    p=package();r=plan(p,{'unavailable_trains':['T1','T2','T3']})
    message=gtfs_realtime_pb2.FeedMessage();message.ParseFromString(gtfs_realtime(passenger_updates(p,r,1800000000)))
    assert message.IsInitialized() and len(message.entity)==3
    assert all(entity.trip_update.trip.schedule_relationship==gtfs_realtime_pb2.TripDescriptor.CANCELED for entity in message.entity)
    r=plan(p,disruption());message.ParseFromString(gtfs_realtime(passenger_updates(p,r,1800000000)))
    assert len(message.entity[0].trip_update.stop_time_update)==2
    from datetime import datetime
    epoch=int(datetime.fromisoformat(p['epoch']).timestamp())
    assert message.entity[0].trip_update.stop_time_update[1].arrival.time==epoch+r['services'][0]['stops'][-1]['arrival_s']


def test_operator_mapping_is_explicit_reversible_and_rejects_ambiguity():
    adapter=dict(schema='osr-operator-adapter/1',id='pilot',country='IQ',operator='pilot-op',revision='v1',accepted=True,acceptance_record='review-1',identities={'S1':'external-001'})
    result=operator_exchange([{'id':'S1','delay_s':30}],adapter,'export')
    assert operator_exchange(result['records'],adapter,'import')['records'][0]['id']=='S1'
    adapter['identities']['S2']='external-001'
    with pytest.raises(ValueError):operator_exchange([],adapter,'export')


def calibration_data():
    def row(identity,failed=True):
        return dict(id=identity,unit='mm',asset_family='bearing',samples=[dict(at_s=t,value=t/1000)for t in [1000,2000,3000]],
                    **({'failed_at_s':10000} if failed else {'observed_until_s':20000}))
    return dict(asset_family='bearing',unit='mm',direction='rising',threshold=10,warning_horizon_s=10000,
        minimum_lead_s=5000,minimum_assets=2,maximum_mae_s=1000,maximum_false_alert_rate=1,
        training=[row('train-'+str(i))for i in range(2)],held_out=[row('test-'+str(i))for i in range(2)]+[row('censored-'+str(i),False)for i in range(2)])


def test_reliability_exposure_resets_open_incidents_and_no_failure_semantics():
    data=dict(assets=[dict(id='T1',km=[dict(at_s=0,value=100),dict(at_s=3600,value=200),dict(at_s=4100,value=10)],
        km_resets=[dict(at_s=4100,before=200,after=10,increment=10,approved=True,record='reset-1')],
        failures=[dict(id='F1',fault_code='BEARING',failed_at_s=10,restored_at_s=3610),dict(id='F2',fault_code='BEARING',failed_at_s=4000)])])
    original=copy.deepcopy(data);r=analyse(data)
    assert data==original and r['mdbf_km']==55 and r['mttr_hours']==1 and r['open_failures']==1
    data['assets'][0]['km_resets'][0]['approved']=False
    with pytest.raises(ValueError):analyse(data)
    assert analyse({'assets':[dict(id='T1',km=[dict(at_s=0,value=0),dict(at_s=1,value=100)])]})['mdbf_km'] is None


def test_rul_requires_held_out_assets_units_and_observed_false_alerts():
    data=calibration_data(); r=calibrate(data)
    assert r['validation_passed'] and not r['commissioned_predictive_maintenance']
    assert r['held_out_mae_s']==0 and r['false_alert_rate']==1
    data['maximum_false_alert_rate']=.1
    assert not calibrate(data)['validation_passed']
    data['held_out'][0]['id']=data['training'][0]['id']
    with pytest.raises(ValueError):calibrate(data)
    data=calibration_data();data['held_out'][0]['unit']='m'
    with pytest.raises(ValueError):calibrate(data)
    assert estimate([],10)['status']=='insufficient-data'


@pytest.fixture
def api_server(operations):
    store,_,_=operations
    server=GatewayHTTPServer(('127.0.0.1',0),Handler);server.store=store
    server.config={'principals':[dict(token=role,role=role,subject='tech' if role=='maintainer' else role,cities=['samawah'],environments=['simulation'])for role in ['viewer','engineer','operator','maintainer','controller']]}
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    def call(method,endpoint,data=None,role='operator'):
        connection=http.client.HTTPConnection('127.0.0.1',server.server_port)
        path='/operations/'+endpoint
        if method=='GET':path+='?city=samawah&environment=simulation'
        connection.request(method,path,json.dumps({'city':'samawah','environment':'simulation',**(data or {})})if method=='POST' else None,{'Authorization':'Bearer '+role,'Content-Type':'application/json'})
        response=connection.getresponse();value=json.loads(response.read());connection.close();return response.status,value
    yield call
    server.shutdown();server.server_close();thread.join()


def test_http_roles_nested_scope_and_compare_and_swap(api_server):
    call=api_server
    assert call('GET','baseline',role='viewer')[0]==200
    assert call('POST','plan',{'expected':'stale'},role='viewer')[0]==403
    assert call('POST','plan',{'expected':'stale'})[0]==409
    p=package();p['city']='other'
    assert call('POST','baseline',{'package':p,'expected':None},role='engineer')[0]==403
    baseline=call('GET','baseline')[1]
    status,result=call('POST','plan',{'expected':baseline['sha256'],'disruptions':disruption()})
    assert status==200 and len(result['services'])==3
    assert call('POST','commands')[0]==404


def test_staff_breaks_shift_span_and_no_implicit_drivers():
    p=package();p['workers']=[p['workers'][0]]
    p['duties'][1].update(start_s=1900,end_s=2100,location='HQ')
    p['workers'][0].update(min_break_s=200,max_continuous_work_s=1800,max_shift_span_s=3000)
    assert len(optimise(p)['uncovered'])==1
    p['duties'][1].update(start_s=2000,end_s=2200)
    assert not optimise(p)['uncovered']
    p['workers'][0]['max_shift_span_s']=2100
    assert len(optimise(p)['uncovered'])==1


def test_reliability_trends_require_matching_meter_window():
    data=dict(assets=[dict(id='T1',km=[dict(at_s=0,value=0),dict(at_s=100,value=100),dict(at_s=200,value=220)],
        failures=[dict(id='F1',fault_code='motor',failed_at_s=50,restored_at_s=60),dict(id='F2',fault_code='motor',failed_at_s=150,restored_at_s=180)])],
        periods=[dict(id='first',start_s=0,end_s=100),dict(id='second',start_s=100,end_s=200)])
    r=analyse(data)
    assert [row['mdbf_km'] for row in r['trends']]==[100,120]
    data['periods'][0]['start_s']=1
    assert analyse(data)['trends'][0]['mdbf_km'] is None


def test_invalid_gtfs_archive_is_a_validation_error():
    with pytest.raises(ValueError):gtfs_import(b'not-a-zip','20261012')


def test_required_service_staff_is_prioritised_before_optional_duties():
    p=package();p['workers']=[p['workers'][0]]
    p['duties'][0]['weight']=1;p['duties'][1]['weight']=100
    result=optimise(p,required_ids={'OCC-day'})
    assert result['assignments'][0]['duty_id']=='OCC-day'
    assert result['uncovered']==['station-day']
