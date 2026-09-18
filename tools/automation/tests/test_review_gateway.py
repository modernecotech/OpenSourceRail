"""Regression and query-budget checks for city-scale supervision reads."""
import copy
import json
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'services/integration'))
from osr_integration.config import build_package
from osr_integration.store import Store


@pytest.fixture
def gateway(tmp_path):
    store = Store(tmp_path / 'gateway.sqlite')
    generic = json.loads((ROOT / 'deployment/supervision/config/generic.json').read_text())
    for city in ['samawah', 'mosul']:
        package = build_package(generic, {'city': city}, [
            {'asset_type': 'station', 'asset_id': f'{city}-station', 'name': 'Station'}], 'rev1')
        store.apply(package, 'engineer')
    return store


def enqueue(store, city, count):
    with store.connect() as db:
        asset = store.asset(db, store.scope(city, 'simulation', city + '-station:charger'))
        for i in range(count):
            store._enqueue(db, asset, asset['alarms'][0], city + '-incident-' + str(i), 1, 'active', 1000)


def test_other_city_cannot_hide_pending_delivery(gateway):
    enqueue(gateway, 'samawah', 1)
    enqueue(gateway, 'mosul', 110)
    snapshot = gateway.snapshot('samawah', 'simulation')
    assert len(snapshot['outbox']) == 1
    assert snapshot['outbox'][0]['incident'] == 'samawah-incident-0'


def test_full_city_snapshot_select_count_is_bounded(gateway, monkeypatch):
    with gateway.connect() as db:
        template = dict(db.execute('SELECT * FROM assets LIMIT 1').fetchone())
        for i in range(573):
            asset = json.loads(template['body'])
            asset['asset_id'] = 'equipment-' + str(i)
            scope = gateway.scope('samawah', 'simulation', asset['asset_id'])
            db.execute('INSERT INTO assets(scope,city,environment,asset_id,package,body) VALUES(?,?,?,?,?,?)',
                       (scope, 'samawah', 'simulation', asset['asset_id'], template['package'], json.dumps(asset)))
    statements = []
    connect = gateway.connect
    @contextmanager
    def counted():
        with connect() as db:
            db.set_trace_callback(lambda sql: statements.append(sql) if sql.lstrip().upper().startswith(('SELECT', 'WITH')) else None)
            yield db
    monkeypatch.setattr(gateway, 'connect', counted)
    assert len(gateway.snapshot('samawah', 'simulation')['assets']) >= 573
    assert len(statements) <= 12, len(statements)


def test_device_read_is_three_selects_and_preserves_quality(gateway, monkeypatch):
    from datetime import datetime, timezone
    scope = gateway.scope('samawah', 'simulation', 'samawah-station:charger')
    with gateway.connect() as db:
        asset = gateway.asset(db, scope)
    name, measurement = next(iter(asset['measurements'].items()))
    value = (measurement['min'] + measurement['max']) / 2
    gateway.ingest(dict(city='samawah', environment='simulation', asset_id=asset['asset_id'],
        source_id=asset['source_id'], measurement=name, unit=measurement['unit'], quality='valid',
        value=value, sequence=1, source_timestamp=datetime.fromtimestamp(1000, timezone.utc).isoformat()), asset['source_id'], now=1000)
    expected = next(a for a in gateway.snapshot('samawah', 'simulation', now=1001)['assets'] if a['asset_id']==asset['asset_id'])
    statements=[]; connect=gateway.connect
    @contextmanager
    def counted():
        with connect() as db:
            db.set_trace_callback(lambda sql: statements.append(sql) if sql.lstrip().upper().startswith('SELECT') else None)
            yield db
    monkeypatch.setattr(gateway, 'connect', counted)
    actual = gateway.device('samawah', 'simulation', asset['asset_id'], now=1001)
    assert actual['readings'] == expected['readings']
    assert actual['alarms'] == expected['alarms']
    assert len(statements) == 3
    assert not {'evidence', 'installations', 'commands_audit'} & actual.keys()
    assert gateway.device('samawah', 'simulation', asset['asset_id'], now=1000+measurement['stale_seconds']*4)['readings'][name]['quality']=='disconnected'
    for city, env in [('mosul','simulation'),('samawah','physical')]:
        with pytest.raises(ValueError): gateway.device(city,env,asset['asset_id'])
    with connect() as db: db.execute("UPDATE assets SET configuration_status='retired' WHERE scope=?",(scope,))
    with pytest.raises(ValueError): gateway.device('samawah','simulation',asset['asset_id'])


def test_queue_pagination_counts_and_legacy_scope_migration(gateway):
    enqueue(gateway, 'samawah', 125)
    enqueue(gateway, 'mosul', 110)
    # Simulate the previous schema on disk, preserving all event payloads.
    with gateway.connect() as db:
        db.execute('UPDATE outbox SET city=NULL,environment=NULL,asset_id=NULL')
    migrated = Store(gateway.path)
    first=migrated.outbox_page('samawah','simulation',limit=20)
    assert first['total']==first['pending']==125
    ids={r['id'] for r in first['items']}; cursor=first['next_before']
    enqueue(migrated, 'mosul', 150)
    while cursor:
        page=migrated.outbox_page('samawah','simulation',limit=20,before=cursor)
        assert not ids & {r['id'] for r in page['items']}
        ids.update(r['id'] for r in page['items']);cursor=page['next_before']
    assert len(ids)==125
    with migrated.connect() as db:
        db.execute("UPDATE outbox SET state='delivered' WHERE city='samawah' AND id=?", (first['items'][0]['id'],))
    assert migrated.outbox_page('samawah','simulation',state='pending')['total']==124
    assert migrated.outbox_page('samawah','physical')['total']==0


def test_evidence_is_bounded_paginated_and_city_scoped(gateway):
    scope=gateway.scope('samawah','simulation','samawah-station:charger')
    with gateway.connect() as db:
        for i in range(45):
            db.execute('INSERT INTO evidence VALUES(?,?,?,?,?,?)',(f'E{i}',scope,'test','inspector','{}',1000+i))
    asset=next(a for a in gateway.snapshot('samawah','simulation')['assets'] if a['asset_id']=='samawah-station:charger')
    assert len(asset['evidence'])==20
    assert asset['evidence_page']['total']==45
    ids={r['id'] for r in asset['evidence']};cursor=asset['evidence_page']['next_before']
    while cursor:
        page=gateway.evidence_page('samawah','simulation',asset['asset_id'],before=cursor)
        assert not ids & {r['id'] for r in page['items']}
        ids.update(r['id'] for r in page['items']);cursor=page['next_before']
    assert len(ids)==45
    with pytest.raises(ValueError): gateway.evidence_page('mosul','simulation',asset['asset_id'])
    for options in [dict(limit=0),dict(limit=101),dict(before=-1),dict(before=2**64),dict(limit=True)]:
        with pytest.raises(ValueError): gateway.outbox_page('samawah','simulation',**options)


def test_paged_http_reads_enforce_authenticated_scope(gateway):
    import threading
    from http.server import ThreadingHTTPServer
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
    from osr_integration.server import Handler, FuxaReadHandler
    enqueue(gateway, 'samawah', 1)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.store=gateway
    server.config={'principals':[dict(token='test',role='viewer',subject='viewer',cities=['samawah'],environments=['simulation'])]}
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        def read(endpoint, **query):
            request=Request(f'http://127.0.0.1:{server.server_port}/{endpoint}?'+urlencode(query),headers={'Authorization':'Bearer test'})
            with urlopen(request,timeout=5) as response:return json.load(response)
        assert read('outbox',city='samawah',environment='simulation')['pending']==1
        for endpoint in ('outbox','evidence'):
            for city,env in [('mosul','simulation'),('samawah','physical')]:
                with pytest.raises(HTTPError) as error:read(endpoint,city=city,environment=env,asset_id='samawah-station:charger')
                assert error.value.code==403
            with pytest.raises(HTTPError) as error:read(endpoint,city='samawah',environment='simulation',asset_id='samawah-station:charger',limit='invalid')
            assert error.value.code==400
    finally:server.shutdown();server.server_close();thread.join()
