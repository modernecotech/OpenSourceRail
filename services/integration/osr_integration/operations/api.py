"""Allowlisted gateway operations API; never delegates controller commands."""
import base64
import time
from .store import OperationsStore
from .reliability import analyse, calibrate, forecast
from .exchange import (gtfs_import, gtfs_realtime, gtfs_schedule, operational_export,
                       operational_import, operator_exchange, passenger_updates)

GET_ROUTES = {'baseline', 'plan', 'work', 'field-events', 'export'}
POST_ROUTES = {'baseline', 'plan', 'work', 'revoke', 'complete', 'analytics', 'calibrate', 'forecast', 'import', 'operator-exchange', 'import-gtfs'}


def handle(handler, method, endpoint, data, principal):
    allowed = GET_ROUTES if method == 'GET' else POST_ROUTES
    if endpoint not in allowed: return None
    roles = None
    if method == 'POST':
        roles = (['engineer'] if endpoint in ('baseline', 'work', 'revoke', 'import', 'import-gtfs') else
                 ['maintainer'] if endpoint == 'complete' else ['engineer', 'operator', 'maintainer'])
    handler.authorize(principal, data, roles)
    store = OperationsStore(handler.server.store)
    city, environment, actor = data['city'], data['environment'], principal['subject']
    manager = principal['role'] in ('engineer', 'operator')
    if endpoint == 'baseline':
        if method == 'GET': return store.baseline(city, environment)
        if data['package'].get('city') != city or data['package'].get('environment') != environment:
            raise PermissionError('Nested planning scope mismatch')
        return store.register(data['package'], actor, data['expected'])
    if endpoint == 'plan':
        if method == 'GET': return store.get_plan(city, environment, data['id'])
        return store.create_plan(city, environment, data['expected'], actor, data.get('disruptions'))
    if endpoint == 'work':
        if method == 'GET': return dict(items=store.packs(city, environment, actor, manager))
        if data['work'].get('city') != city or data['work'].get('environment') != environment:
            raise PermissionError('Nested field scope mismatch')
        return store.issue_work(data['work'], actor, data['expected'])
    if endpoint == 'revoke': return store.revoke(city, environment, data['id'], actor)
    if endpoint == 'complete': return store.complete(city, environment, data['event'], actor)
    if endpoint == 'field-events': return dict(items=store.events(city, environment, actor, manager))
    if endpoint in ('analytics', 'calibrate', 'forecast'):
        if not isinstance(data.get('data'), dict): raise ValueError('Analysis evidence must be an object')
        result = {'analytics': analyse, 'calibrate': calibrate, 'forecast': forecast}[endpoint](data['data'])
        with handler.server.store.connect() as db:
            handler.server.store.audit(db, actor, 'operations-' + endpoint, store.scope(city, environment), result)
        return result
    if endpoint == 'import-gtfs':
        return gtfs_import(base64.b64decode(data['base64'], validate=True), data['operating_date'])
    if endpoint == 'import':
        package = operational_import(data['payload'])
        if package['city'] != city or package['environment'] != environment: raise PermissionError('Imported scope mismatch')
        return dict(package=package, creates_baseline=False, requires_review=True)
    if endpoint == 'operator-exchange':
        adapter = handler.server.config.get('operations_adapters', {}).get(data['adapter_id'])
        if not adapter or city not in adapter.get('cities', []) or environment not in adapter.get('environments', []):
            raise PermissionError('Operator adapter is not configured for this scope')
        return operator_exchange(data['records'], adapter, data['direction'])
    if endpoint == 'export':
        result = store.get_plan(city, environment, data['id'])
        if not result['current_baseline']: raise ValueError('Stale plan cannot be exported as current')
        package = store.baseline(city, environment)['package']
        if data.get('format') == 'operations-json':
            return operational_export(package, {k: v for k, v in result.items() if k != 'current_baseline'})
        if data.get('format') == 'gtfs':
            return dict(filename='gtfs.zip', content_type='application/zip', base64=base64.b64encode(gtfs_schedule(package)).decode())
        feed = passenger_updates(package, result, time.time())
        if data.get('format') == 'gtfs-rt-json': return feed
        if data.get('format') == 'gtfs-rt':
            return dict(filename='trip-updates.pb', content_type='application/x-protobuf', base64=base64.b64encode(gtfs_realtime(feed)).decode())
        raise ValueError('Unknown export format')
