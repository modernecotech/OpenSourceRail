"""Operational JSON, GTFS timetable/update exports and explicit operator mappings."""
import csv
import io
import json
import zipfile
from datetime import datetime, timedelta
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo
from .contracts import digest, identifier, validate
from .planning import movement


def operational_export(package, result):
    validate(package)
    if result['input_sha256'] != digest(package): raise ValueError('Plan/source revision mismatch')
    payload = dict(schema='osr-operational-exchange/1', package=package, plan=result,
                   movement_authority=False, railml_schema_conformance=False)
    payload['sha256'] = digest(payload)
    return payload


def operational_import(payload):
    if payload.get('schema') != 'osr-operational-exchange/1' or payload.get('movement_authority') is not False:
        raise ValueError('Unsupported operational exchange schema/authority')
    if digest({k: v for k, v in payload.items() if k != 'sha256'}) != payload.get('sha256'):
        raise ValueError('Operational exchange checksum mismatch')
    package = validate(payload['package']); result = payload['plan']
    if result.get('input_sha256') != digest(package) or result.get('movement_authority') is not False:
        raise ValueError('Operational exchange baseline/authority mismatch')
    if result.get('sha256') != digest({k: v for k, v in result.items() if k not in ('sha256', 'current_baseline')}):
        raise ValueError('Operational plan hash mismatch')
    return package


def _csv(headers, rows):
    stream = io.StringIO(newline=''); writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(headers); writer.writerows(rows)
    return stream.getvalue()


def _agency(package):
    agency = package.get('agency', {})
    identifier(agency.get('id'))
    if not isinstance(agency.get('name'), str) or not agency['name']: raise ValueError('Agency name required')
    parsed = urlsplit(agency.get('url', ''))
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Public agency URL required')
    tz = ZoneInfo(agency['timezone'])
    epoch = datetime.fromisoformat(package['epoch'].replace('Z', '+00:00')).astimezone(tz)
    return agency, epoch


def gtfs_schedule(package):
    """Original declared timetable; chosen recovery changes are GTFS-RT updates."""
    package = validate(package); agency, epoch = _agency(package)
    nodes = {n['id']: n for n in package['nodes']}
    paths = {p['id']: p for p in package['paths']}
    trips = []; stops = []; routes = set(); stop_ids = set()
    # GTFS defines time from local noon minus twelve hours, including DST days.
    noon = epoch.replace(hour=12, minute=0, second=0, microsecond=0)
    day_seconds = int(epoch.timestamp() - (noon.timestamp() - 43200))
    def clock(seconds):
        value = day_seconds + seconds
        return f'{value // 3600:02}:{value // 60 % 60:02}:{value % 60:02}'
    for s in sorted(package['services'], key=lambda r: r['id']):
        leg = movement(package, paths[s['path_ids'][0]], min(s['departures_s']), 'revenue', s['id'], s.get('dwells_s'))
        routes.add(s['route_id']); trips.append([s['route_id'], 'operating-day', s['id']])
        for sequence, stop in enumerate([r for r in leg['stops'] if nodes[r['node']]['station']], 1):
            stop_ids.add(stop['node'])
            stops.append([s['id'], clock(stop['arrival_s']), clock(stop['departure_s']), stop['node'], sequence])
        if not any(r[0] == s['id'] for r in stops): raise ValueError('Passenger trip has no declared station stops')
    date = epoch.strftime('%Y%m%d')
    files = {
        'agency.txt': _csv(['agency_id', 'agency_name', 'agency_url', 'agency_timezone'], [[agency['id'], agency['name'], agency['url'], agency['timezone']]]),
        'stops.txt': _csv(['stop_id', 'stop_name', 'stop_lat', 'stop_lon'], [[key, nodes[key]['name'], nodes[key]['lat'], nodes[key]['lon']] for key in sorted(stop_ids)]),
        'routes.txt': _csv(['route_id', 'agency_id', 'route_short_name', 'route_long_name', 'route_type'], [[r, agency['id'], r, r, 1] for r in sorted(routes)]),
        'trips.txt': _csv(['route_id', 'service_id', 'trip_id'], trips),
        'stop_times.txt': _csv(['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence'], stops),
        'calendar_dates.txt': _csv(['service_id', 'date', 'exception_type'], [['operating-day', date, 1]]),
    }
    target = io.BytesIO()
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            info = zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0)); info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content.encode())
    return target.getvalue()


def passenger_updates(package, result, now):
    _, epoch_local = _agency(package)
    epoch = datetime.fromisoformat(package['epoch'].replace('Z', '+00:00')).timestamp()
    nodes = {n['id']: n for n in package['nodes']}; paths = {p['id']: p for p in package['paths']}
    declared = {s['id']: movement(package, paths[s['path_ids'][0]], min(s['departures_s']), 'revenue', s['id'], s.get('dwells_s')) for s in package['services']}
    date = epoch_local.strftime('%Y%m%d'); entities = []
    for r in result['services']:
        baseline_nodes = [s['node'] for s in declared[r['id']]['stops'] if nodes[s['node']]['station']]
        current_nodes = [s['node'] for s in r['stops'] if nodes[s['node']]['station']]
        if current_nodes != baseline_nodes:
            # New stop patterns need a reviewed replacement static feed. Do not
            # publish invalid SCHEDULED updates with unknown stop sequences.
            raise ValueError('Changed stop pattern requires a new GTFS schedule before publishing updates')
        update = dict(trip=dict(trip_id=r['id'], route_id=r['route_id'], start_date=date),
                      timestamp=int(now), stop_time_update=[])
        for seq, stop in enumerate([s for s in r['stops'] if nodes[s['node']]['station']], 1):
            update['stop_time_update'].append(dict(stop_sequence=seq, stop_id=stop['node'],
                arrival=dict(time=int(epoch + stop['arrival_s'])), departure=dict(time=int(epoch + stop['departure_s']))))
        entities.append(dict(id=r['id'], trip_update=update))
    for r in result['cancelled']:
        entities.append(dict(id=r['id'], trip_update=dict(trip=dict(trip_id=r['id'], route_id=r['route_id'],
            start_date=date, schedule_relationship='CANCELED'), timestamp=int(now))))
    return dict(header=dict(gtfs_realtime_version='2.0', incrementality='FULL_DATASET', timestamp=int(now)), entity=entities)


# These are the wire field numbers in the official GTFS realtime.proto. Only
# FeedMessage/TripUpdate/StopTimeUpdate are emitted; test with official bindings.
def _varint(value):
    value &= (1 << 64) - 1; out = bytearray()
    while value > 127: out.append((value & 127) | 128); value >>= 7
    out.append(value); return bytes(out)


def _wire(number, value):
    if isinstance(value, str): value = value.encode()
    if isinstance(value, bytes): return _varint(number << 3 | 2) + _varint(len(value)) + value
    return _varint(number << 3) + _varint(value)


def gtfs_realtime(feed):
    header = _wire(1, '2.0') + _wire(2, 0) + _wire(3, feed['header']['timestamp'])
    output = _wire(1, header)
    for entity in feed['entity']:
        u = entity['trip_update']; trip = u['trip']
        descriptor = _wire(1, trip['trip_id']) + _wire(3, trip['start_date']) + _wire(5, trip['route_id'])
        if trip.get('schedule_relationship') == 'CANCELED': descriptor += _wire(4, 3)
        update = _wire(1, descriptor) + _wire(4, u['timestamp'])
        for stop in u.get('stop_time_update', []):
            encoded = _wire(1, stop['stop_sequence']) + _wire(4, stop['stop_id'])
            encoded += _wire(2, _wire(2, stop['arrival']['time'])) + _wire(3, _wire(2, stop['departure']['time']))
            update += _wire(2, encoded)
        output += _wire(2, _wire(1, entity['id']) + _wire(3, update))
    return output


def operator_exchange(payload, adapter, direction):
    """Configured, versioned identity mapping; no invented national API endpoints."""
    if adapter.get('schema') != 'osr-operator-adapter/1' or direction not in ('import', 'export'):
        raise ValueError('Unknown operator exchange profile/direction')
    for key in ('id', 'country', 'operator', 'revision'): identifier(adapter.get(key))
    if adapter.get('accepted') is not True or not adapter.get('acceptance_record'):
        raise ValueError('Operator mapping requires reviewed acceptance record')
    mapping = adapter.get('identities')
    if not isinstance(mapping, dict) or len(set(mapping.values())) != len(mapping): raise ValueError('Ambiguous operator identity mapping')
    lookup = mapping if direction == 'export' else {v: k for k, v in mapping.items()}
    for key, value in lookup.items(): identifier(key); identifier(value)
    rows = []
    for row in payload:
        if row.get('id') not in lookup: raise ValueError('Unmapped operator record identity')
        rows.append(dict(row, id=lookup[row['id']]))
    return dict(schema='osr-operator-exchange/1', adapter=adapter['id'], adapter_revision=adapter['revision'],
        adapter_sha256=digest(adapter), country=adapter['country'], operator=adapter['operator'], records=rows,
        movement_authority=False)


def gtfs_import(content, operating_date):
    """Import a bounded GTFS timetable for review; does not infer track topology."""
    if len(content) > 8_000_000: raise ValueError('GTFS archive too large')
    date = datetime.strptime(operating_date, '%Y%m%d').strftime('%Y%m%d')
    try: archive_file = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile as exc: raise ValueError('Invalid GTFS ZIP archive') from exc
    with archive_file as archive:
        if any(info.flag_bits & 1 for info in archive.infolist()): raise ValueError('Encrypted GTFS ZIP is unsupported')
        names = archive.namelist()
        if len(names) != len(set(names)) or len(names) > 100: raise ValueError('Invalid GTFS archive inventory')
        if sum(info.file_size for info in archive.infolist()) > 20_000_000: raise ValueError('GTFS archive expands beyond size limit')
        def read(name, optional=False):
            if optional and name not in names: return []
            if name not in names: raise ValueError('Missing GTFS file: ' + name)
            return list(csv.DictReader(io.StringIO(archive.read(name).decode('utf-8-sig'))))
        agencies = read('agency.txt')
        if not agencies or len({r['agency_timezone'] for r in agencies}) != 1: raise ValueError('GTFS agencies require one consistent timezone')
        ZoneInfo(agencies[0]['agency_timezone'])
        stop_rows = read('stops.txt'); route_rows = read('routes.txt'); trip_rows = read('trips.txt'); times = read('stop_times.txt')
        calendar = read('calendar.txt', True); exceptions = read('calendar_dates.txt', True)
    stops = {r['stop_id']: r for r in stop_rows}; routes = {r['route_id']: r for r in route_rows}
    if len(stops) != len(stop_rows) or len(routes) != len(route_rows): raise ValueError('Duplicate GTFS stop/route identity')
    active = set(); weekday = datetime.strptime(date, '%Y%m%d').strftime('%A').lower()
    for r in calendar:
        if r['start_date'] <= date <= r['end_date'] and r[weekday] == '1': active.add(r['service_id'])
    for r in exceptions:
        if r['date'] == date:
            if r['exception_type'] == '1': active.add(r['service_id'])
            elif r['exception_type'] == '2': active.discard(r['service_id'])
            else: raise ValueError('Invalid GTFS calendar exception')
    trips = {}; grouped = {}
    for r in trip_rows:
        if r['trip_id'] in trips: raise ValueError('Duplicate GTFS trip identity')
        if r['route_id'] not in routes: raise ValueError('Unknown GTFS route')
        trips[r['trip_id']] = r
    def seconds(value):
        parts = value.split(':')
        if len(parts) != 3 or not all(p.isdigit() for p in parts): raise ValueError('Invalid GTFS stop time')
        hour, minute, second = map(int, parts)
        if hour > 335 or minute > 59 or second > 59: raise ValueError('GTFS time outside supported horizon')
        return hour*3600 + minute*60 + second
    for r in times:
        if r['trip_id'] not in trips or r['stop_id'] not in stops: raise ValueError('Unknown GTFS trip/stop')
        if trips[r['trip_id']]['service_id'] not in active: continue
        sequence = int(r['stop_sequence']); arrival = seconds(r['arrival_time']); departure = seconds(r['departure_time'])
        if sequence < 0 or arrival > departure: raise ValueError('Invalid GTFS stop ordering/time')
        grouped.setdefault(r['trip_id'], []).append(dict(stop_id=r['stop_id'], sequence=sequence, arrival_s=arrival, departure_s=departure))
    output = []
    for tid, rows in sorted(grouped.items()):
        rows.sort(key=lambda r: r['sequence'])
        if len({r['sequence'] for r in rows}) != len(rows) or any(a['departure_s'] > b['arrival_s'] for a, b in zip(rows, rows[1:])):
            raise ValueError('Non-monotonic GTFS trip')
        output.append(dict(id=tid, route_id=trips[tid]['route_id'], stops=rows))
    return dict(schema='osr-imported-timetable/1', operating_date=date, timezone=agencies[0]['agency_timezone'], agencies=agencies, trips=output,
        stops=list(stops.values()), routes=list(routes.values()), requires_physical_path_mapping=True,
        creates_baseline=False, movement_authority=False)
