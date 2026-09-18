"""Atomic batch ingestion must preserve the single-reading safety and retry contract."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'services/integration'))
from osr_integration.config import build_package
from osr_integration.server import Handler, request_json
from osr_integration.store import Store


@pytest.fixture
def store(tmp_path):
    gateway = Store(tmp_path / 'gateway.sqlite')
    generic = json.loads((ROOT / 'deployment/supervision/config/generic.json').read_text())
    for city in ('samawah', 'mosul'):
        gateway.apply(build_package(generic, {'city': city}, [
            {'asset_type': 'station', 'asset_id': city + '-station', 'name': 'Station'}], 'r1'), 'engineer')
    return gateway


def reading(second=1000, value=80, **changes):
    return dict(dict(city='samawah', environment='simulation', asset_id='samawah-station:charger',
        measurement='temperature_c', source_id='simulator', sequence=second,
        source_timestamp=datetime.fromtimestamp(second, timezone.utc).isoformat(),
        unit='degC', quality='valid', value=value), **changes)


def counts(store):
    with store.connect() as db:
        return {table: db.execute('SELECT count(*) FROM ' + table).fetchone()[0]
                for table in ('readings', 'alarms', 'audit', 'outbox')}


def test_ordered_alarm_activation_clear_and_retry(store):
    # The configured 6-second persistence delay is evaluated in source-time order.
    messages = [reading(1000), reading(1006), reading(1007, value=35)]
    result = store.ingest_batch(messages, 'simulator', now=1007)
    assert result['results'] == [{'duplicate': False, 'quality': 'valid'}] * 3
    before = counts(store)
    assert before['readings'] == 3 and before['outbox'] == 2
    with store.connect() as db:
        assert [json.loads(r[0])['condition'] for r in db.execute('SELECT body FROM outbox ORDER BY rowid')] == ['active', 'cleared']
        assert db.execute('SELECT active FROM alarms').fetchone()[0] == 0
    assert store.ingest_batch(messages, 'simulator', now=1007)['results'] == [{'duplicate': True}] * 3
    assert counts(store) == before


@pytest.mark.parametrize('bad', [
    {'source_id': 'other'}, {'unit': 'K'}, {'sequence': True}, {'sequence': -1},
    {'source_timestamp': '2099-01-01T00:00:00Z'}, {'source_timestamp': '2000-01-01T00:00:00'},
    {'quality': 'unknown'}, {'value': None}, {'value': float('nan')},
    {'asset_id': 'missing'}, {'measurement': 'missing'},
])
def test_invalid_member_rolls_back_readings_alarms_and_delivery(store, bad):
    before = counts(store)
    with pytest.raises((ValueError, PermissionError)):
        store.ingest_batch([reading(1000), reading(1006), reading(1007, **bad)], 'simulator', now=1007)
    assert counts(store) == before


def test_late_sequence_or_changed_retry_rolls_back_new_members(store):
    store.ingest(reading(1000), 'simulator', now=1000)
    before = counts(store)
    for invalid in (reading(999), reading(1000, value=81), reading(999, sequence=1007)):
        with pytest.raises(ValueError):
            store.ingest_batch([reading(1006), invalid], 'simulator', now=1006)
        assert counts(store) == before


@pytest.mark.parametrize('messages', [None, {}, [], [None], [reading()] * 129])
def test_batch_bounds_and_shape(store, messages):
    with pytest.raises(ValueError): store.ingest_batch(messages, 'simulator', now=1000)
    assert counts(store)['readings'] == 0


def test_concurrent_identical_retries_commit_once(store):
    messages = [reading(1000), reading(1006)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: store.ingest_batch(messages, 'simulator', now=1006), range(8)))
    assert sum(not r['duplicate'] for result in results for r in result['results']) == 2
    assert counts(store)['readings'] == 2 and counts(store)['outbox'] == 1


def test_batch_preserves_invalid_stale_and_disconnected_quality(store):
    result = store.ingest_batch([reading(900), reading(1000, value=1e6),
        reading(1001, value=None, quality='disconnected')], 'simulator', now=1001)
    assert [r['quality'] for r in result['results']] == ['stale', 'invalid', 'disconnected']
    assert counts(store)['outbox'] == 0


def test_http_authorizes_every_member_before_commit(store):
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.store = store
    server.config = {'principals': [dict(token=role, role=role, subject='simulator',
        cities=['samawah'], environments=['simulation']) for role in ('controller', 'viewer')]}
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    url = f'http://127.0.0.1:{server.server_port}/telemetry/batch'
    try:
        message = reading(int(datetime.now(timezone.utc).timestamp()))
        for bad in (dict(message, city='mosul', asset_id='mosul-station:charger'),
                    dict(message, environment='physical'), dict(message, source_id='other')):
            with pytest.raises(HTTPError) as error:
                request_json(url, {'readings': [message, bad]}, {'Authorization': 'Bearer controller'})
            assert error.value.code == 403
            assert counts(store)['readings'] == 0
        with pytest.raises(HTTPError) as error:
            request_json(url, {'readings': [message]}, {'Authorization': 'Bearer viewer'})
        assert error.value.code == 403
        for body in ({'readings': []}, {'readings': [None]}, [], {'readings': [message] * 129}):
            with pytest.raises(HTTPError) as error:
                request_json(url, body, {'Authorization': 'Bearer controller'})
            assert error.value.code == 400
        result = request_json(url, {'readings': [message]}, {'Authorization': 'Bearer controller'})
        assert result['results'] == [{'duplicate': False, 'quality': 'valid'}]
    finally:
        server.shutdown(); server.server_close(); thread.join()


def test_batch_reloads_configuration_and_rejects_retirement(store):
    store.ingest_batch([reading(1000)], 'simulator', now=1000)
    with store.connect() as db:
        db.execute("UPDATE assets SET configuration_status='retired' WHERE asset_id=?", ('samawah-station:charger',))
    before = counts(store)
    with pytest.raises(ValueError, match='retired'):
        store.ingest_batch([reading(1001)], 'simulator', now=1001)
    assert counts(store) == before


def test_full_batch_bound_is_accepted_with_identical_retry(store):
    messages = [reading(1000, sequence=i, value=35) for i in range(128)]
    assert len(store.ingest_batch(messages, 'simulator', now=1000)['results']) == 128
    assert all(r['duplicate'] for r in store.ingest_batch(messages, 'simulator', now=1000)['results'])
    assert counts(store)['readings'] == 128


def test_queued_views_recompute_freshness_after_waiting(store, monkeypatch):
    from contextlib import contextmanager
    from osr_integration import store as module
    store.ingest(reading(1000, value=35), 'simulator', now=1000)
    clock = [1000]
    monkeypatch.setattr(module.time, 'time', lambda: clock[0])
    @contextmanager
    def delayed_lock():
        clock[0] = 1041
        yield
    for view in ('device', 'snapshot'):
        clock[0] = 1000
        monkeypatch.setattr(store, '_view_lock', delayed_lock())
        if view == 'device':
            asset = store.device('samawah', 'simulation', 'samawah-station:charger')
        else:
            snapshot = store.snapshot('samawah', 'simulation')
            assert snapshot['observed_at'] == 1041
            asset = next(a for a in snapshot['assets'] if a['asset_id'] == 'samawah-station:charger')
        assert asset['readings']['temperature_c']['quality'] == 'disconnected'


def test_queued_ingestion_rechecks_source_age_after_waiting(store, monkeypatch):
    from contextlib import contextmanager
    from osr_integration import store as module
    clock = [1000]
    monkeypatch.setattr(module.time, 'time', lambda: clock[0])
    @contextmanager
    def delayed_lock():
        clock[0] = 1041
        yield
    monkeypatch.setattr(store, '_telemetry_lock', delayed_lock())
    assert store.ingest_batch([reading(1000)], 'simulator')['results'][0]['quality'] == 'stale'
    with store.connect() as db:
        assert db.execute('SELECT received FROM readings').fetchone()[0] == 1041
