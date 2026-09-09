"""Direction- and role-specific checks for a native overnight trace."""
from collections import Counter


def inspect_morning_service(doc, events, night_rows, *, morning_elapsed=14400, tolerance_s=60):
    stations = {i + 1: station['id'] for i, station in enumerate(doc['stations'])}
    trains, expected = {}, []
    next_id = 1
    for fleet in doc['fleets']:
        points = fleet['dispatch_points']
        total = fleet['trainset_count']
        spare, cold = fleet.get('spare_count', 0), fleet.get('cold_reserve_count', 0)
        for point in points:
            expected.append((fleet['line'], point['station'], point['heading']))
        for index in range(total):
            point = points[index % len(points)]
            role = 'revenue' if index < total - spare - cold else ('spare' if index < total - cold else 'cold_reserve')
            trains[next_id] = {'line': fleet['line'], 'heading': point['heading'], 'role': role}
            next_id += 1
    ready = Counter()
    roles = Counter()
    seen = set()
    for row in night_rows:
        train_id = int(row['train_id'].removeprefix('T'))
        if train_id in seen:
            raise ValueError('duplicate train in the night snapshot')
        seen.add(train_id)
        train = trains[train_id]
        if row['service_role'] != train['role']:
            raise ValueError('snapshot role disagrees with the fleet inventory')
        roles[train['role']] += 1
        if row['phase'] in ('awaiting', 'dwelling') and row['service_role'] == 'revenue':
            heading = row['departure_heading']
            if heading not in ('forward', 'reverse'):
                raise ValueError('invalid departure heading in the night snapshot')
            ready[(train['line'], stations[int(row['station_id'])], heading)] += 1
    first = {}
    reserve_departures = []
    for event in events:
        train = trains[event['train']]
        if event['kind'] == 'Turnaround':
            train['heading'] = 'reverse' if train['heading'] == 'forward' else 'forward'
        elif event['kind'] in ('DepartStation', 'Dispatched'):
            if train['role'] != 'revenue':
                reserve_departures.append({'train': event['train'], 'role': train['role'], 'sim_time_s': event['sim_time_s']})
                continue
            if event['sim_time_s'] >= morning_elapsed:
                key = (train['line'], stations[event['station']], train['heading'])
                first.setdefault(key, event['sim_time_s'] - morning_elapsed)
    directions = []
    for line, station, heading in sorted(set(expected)):
        key = (line, station, heading)
        delay = first.get(key)
        directions.append({'line': line, 'station': station, 'heading': heading,
                           'ready_revenue_trainsets_at_0529': ready[key],
                           'first_morning_departure_delay_s': delay,
                           'passed': delay is not None and delay <= tolerance_s})
    complete = seen == set(trains)
    return {'snapshot_roles': dict(roles), 'snapshot_covers_fleet': complete,
            'planned_direction_count': len(directions),
            'directions_restarting_within_tolerance': sum(row['passed'] for row in directions),
            'directional_departures': directions,
            'every_planned_direction_restarts_within_60s': bool(directions) and all(row['passed'] for row in directions),
            'reserve_departures': reserve_departures,
            'passed': complete and bool(directions) and all(row['passed'] for row in directions) and not reserve_departures}
