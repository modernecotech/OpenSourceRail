"""Counterfactual queue balancing; this does not dispatch or teleport trains."""
from collections import Counter
import math


def route_to_point(line, origin, heading, destination, target_heading):
    """Shortest forward-in-time route to a departure point, with terminal turns."""
    stations = [s['id'] for s in line['stations']]
    if heading not in ('forward', 'reverse') or target_heading not in ('forward', 'reverse'):
        raise ValueError('invalid departure heading')
    index = stations.index(origin)
    distance = 0.0
    path = [origin]
    reversals = 0
    for _ in range(2 * len(stations) + 1):
        if stations[index] == destination and heading == target_heading:
            return {'distance_m': distance, 'stations': path, 'terminal_reversals': reversals}
        step = 1 if heading == 'forward' else -1
        next_index = index + step
        if not 0 <= next_index < len(stations):
            if not line.get('is_ring', False):
                return None  # outward starting headings are not an executable departure
            next_index %= len(stations)
            length = float(line['ring_wrap_length_m'])
        else:
            length = float(line['stations'][max(index, next_index)]['distance_from_prev_m'])
        if not math.isfinite(length) or length <= 0:
            raise ValueError('invalid section length')
        distance += length
        index = next_index
        path.append(stations[index])
        if not line.get('is_ring', False) and index in (0, len(stations) - 1):
            heading = 'reverse' if index == len(stations) - 1 else 'forward'
            reversals += 1
    return None


def balance_snapshot(doc, rows, *, kwh_per_km, battery_kwh, max_speed_kmh):
    """Try increasing queue caps, preserving reserves and each departure direction.

    Greedy shortest feasible moves give a constructive target, not a minimum
    shunting-distance solution. Energy and time are optimistic lower bounds.
    """
    if any(not math.isfinite(v) or v <= 0 for v in (kwh_per_km, battery_kwh, max_speed_kmh)):
        raise ValueError('invalid energy or speed input')
    stations = {i + 1: s['id'] for i, s in enumerate(doc['stations'])}
    lines = {line['id']: line for line in doc['lines']}
    points = {f['line']: {(p['station'], p['heading']) for p in f['dispatch_points']} for f in doc['fleets']}
    inventory = {}
    next_id = 1
    lower = 0
    for fleet in doc['fleets']:
        total = fleet['trainset_count']
        lower = max(lower, math.ceil(total / len({p[0] for p in points[fleet['line']]})))
        spare, cold = fleet.get('spare_count', 0), fleet.get('cold_reserve_count', 0)
        for index in range(total):
            role = 'revenue' if index < total - spare - cold else ('spare' if index < total - cold else 'cold_reserve')
            inventory[next_id] = (fleet['line'], role)
            next_id += 1
    original = []
    seen = set()
    for row in rows:
        train = int(row['train_id'].removeprefix('T'))
        if train in seen or train not in inventory:
            raise ValueError('duplicate or unknown train in snapshot')
        seen.add(train)
        line, role = inventory[train]
        if row['phase'] not in ('awaiting', 'dwelling') or row['service_role'] != role:
            raise ValueError('snapshot requires parked trains with declared roles')
        station, heading, soc = stations[int(row['station_id'])], row['departure_heading'], float(row['soc'])
        if (station, heading) not in points[line] or not math.isfinite(soc) or not 0 <= soc <= 1:
            raise ValueError('train is not at a valid selected departure point')
        original.append({'train': train, 'line': line, 'service_role': role,
                         'station': station, 'heading': heading, 'soc': soc})
    if seen != set(inventory):
        raise ValueError('snapshot does not cover the fleet')
    original.sort(key=lambda r: r['train'])
    direction_counts = Counter((r['line'], r['station'], r['heading']) for r in original if r['service_role'] == 'revenue')
    if any(direction_counts[(line, station, heading)] < 1 for line, pairs in points.items() for station, heading in pairs):
        raise ValueError('snapshot lacks revenue coverage for a planned direction')
    total_stations = {station for pairs in points.values() for station, _ in pairs}
    lower = max(lower, math.ceil(len(original) / len(total_stations)))
    fixed = Counter(r['station'] for r in original if r['service_role'] != 'revenue')
    minimum_coverage = Counter(station for pairs in points.values() for station, _ in pairs)
    lower = max(lower, max(fixed[s] + minimum_coverage[s] for s in total_stations))
    observed_max = max(Counter(r['station'] for r in original).values())
    for cap in range(lower, observed_max + 1):
        target = [dict(r) for r in original]
        counts = Counter(r['station'] for r in target)
        coverage = direction_counts.copy()
        moves = []
        while max(counts.values()) > cap:
            choices = []
            for r in target:
                if r['service_role'] != 'revenue' or counts[r['station']] <= cap or coverage[(r['line'], r['station'], r['heading'])] <= 1:
                    continue
                for station, heading in sorted(points[r['line']]):
                    if counts[station] >= cap:
                        continue
                    route = route_to_point(lines[r['line']], r['station'], r['heading'], station, heading)
                    if route is None:
                        continue
                    required = route['distance_m'] / 1000 * kwh_per_km
                    precharge = max(0.0, required + .2 * battery_kwh - r['soc'] * battery_kwh)
                    if required + .2 * battery_kwh > max(.95, r['soc']) * battery_kwh + 1e-6:
                        continue  # no intermediate charging delivery is assumed
                    choices.append((route['distance_m'], r['train'], station, heading, route, precharge, required))
            if not choices:
                break
            _, train, station, heading, route, precharge, required = min(choices, key=lambda x: x[:4])
            r = next(r for r in target if r['train'] == train)
            moves.append({'train': train, 'line': r['line'], 'from_station': r['station'],
                          'from_heading': r['heading'], 'to_station': station, 'to_heading': heading,
                          **route, 'nominal_energy_kwh': required, 'precharge_required_kwh': precharge,
                          'precharge_lower_bound_s_at_150kw': precharge / 150 * 3600,
                          'travel_lower_bound_s': route['distance_m'] / (max_speed_kmh / 3.6)})
            counts[r['station']] -= 1
            coverage[(r['line'], r['station'], r['heading'])] -= 1
            counts[station] += 1
            coverage[(r['line'], station, heading)] += 1
            r['station'], r['heading'] = station, heading
            r['soc'] += (precharge - required) / battery_kwh
        if max(counts.values()) <= cap:
            assert sum(counts.values()) == len(original)
            assert all(coverage[(line, station, heading)] >= 1 for line, pairs in points.items() for station, heading in pairs)
            allocations = Counter((r['line'], r['station'], r['heading'], r['service_role']) for r in target)
            return {'allocation_found': True, 'queue_lower_bound': lower,
                    'observed_maximum_queue': observed_max, 'target_maximum_queue': max(counts.values()),
                    'queue_lower_bound_attained': max(counts.values()) == lower,
                    'trainsets_to_move': len(moves), 'moves': moves,
                    'total_transfer_train_km': sum(m['distance_m'] for m in moves) / 1000,
                    'precharge_required_kwh': sum(m['precharge_required_kwh'] for m in moves),
                    'target_station_trainsets': dict(sorted(counts.items())),
                    'target_allocations': [{'line': l, 'station': s, 'heading': h, 'service_role': role, 'trainset_count': n}
                                           for (l, s, h, role), n in sorted(allocations.items())],
                    'planned_revenue_directions_preserved': sum(len(p) for p in points.values()),
                    'reserve_trainsets_moved': 0}
    raise ValueError('no balanced allocation found, including the observed allocation')
