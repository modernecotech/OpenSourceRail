"""Audit actual line-local home returns, depot storage and morning launch stock."""
from collections import Counter
import math

from .stabling_capacity import two_train_station_capacity

DAY_S = 86400
# Match validate-city-simulation.py: 0.001 percentage point permits f32
# integration roundoff (0.00001 as a fraction), not usable reserve depletion.
SOC_TOLERANCE = 1e-5


def inspect_hybrid_cycles(doc, result, snapshots, days):
    if type(days) is not int or not 1 <= days <= 7:
        raise ValueError('days must be an integer from 1 to 7')
    if doc['scenario']['start_time'] != '05:30' or any(
        f['service_start'] != '05:30' or f['service_end'] != '02:00' for f in doc['fleets']
    ):
        raise ValueError('hybrid city screen requires 05:30 opening and 02:00 closure')
    if result['sim_duration_s'] < days * DAY_S + 1801:
        raise ValueError('trace must include 30 minutes after the final opening')
    stations = {i + 1: s['id'] for i, s in enumerate(doc['stations'])}
    depot_positions = {s['id']: s['depot_stabling_positions'] for s in doc['stations'] if s.get('depot_stabling_positions')}
    homes = {}
    expected = set()
    for fleet in doc['fleets']:
        allocations = fleet.get('overnight_allocations', [])
        if sum(a['trainset_count'] for a in allocations) != fleet['trainset_count']:
            raise ValueError('hybrid screen requires complete explicit homes')
        expected.update((fleet['line'], p['station'], p['heading']) for p in fleet['dispatch_points'])
        for a in allocations:
            for _ in range(a['trainset_count']):
                homes[len(homes) + 1] = {**a, 'line': fleet['line']}
    events = result['events']
    if any(e['train'] not in homes for e in events):
        raise ValueError('event references unknown train')
    if any(a['sim_time_s'] > b['sim_time_s'] for a, b in zip(events, events[1:])):
        raise ValueError('events are not in simulation time order')
    departures = [e for e in events if e['kind'] in ('Dispatched', 'DepartStation', 'ReturnToStabling')]
    reserve_departures = [e for e in departures if homes[e['train']]['service_role'] != 'revenue']
    minima = {int(r[0].removeprefix('T')): r[3] for r in result['per_train_final_soc']}
    reserve_ok = set(minima) == set(homes) and all(math.isfinite(v) and 0.2 - SOC_TOLERANCE <= v <= 1 for v in minima.values())
    cycles = []
    for day in range(1, days + 1):
        opening = day * DAY_S
        sample = opening - 60
        rows = snapshots.get(sample, [])
        seen, misplaced, observed = set(), [], Counter()
        headings = {}
        for row in rows:
            train = int(row['train_id'].removeprefix('T'))
            if train not in homes or train in seen or int(row['sim_time_s']) != sample:
                raise ValueError('invalid, duplicate or mistimed train snapshot')
            seen.add(train)
            home = homes[train]
            if row['service_role'] != home['service_role']:
                raise ValueError('snapshot role disagrees with explicit home inventory')
            soc = float(row['soc'])
            if not math.isfinite(soc):
                raise ValueError('nonfinite snapshot SoC')
            location = row['stabling_location']
            parked = row['phase'] in ('awaiting', 'dwelling')
            if location not in ('station', 'depot', 'in_transit') or parked != (location != 'in_transit'):
                raise ValueError('snapshot phase disagrees with storage location')
            station = stations[int(row['station_id'])] if parked else None
            if parked:
                observed[(home['line'], station, location, home['service_role'])] += 1
            headings[train] = row['heading']
            correct = (parked and row['phase'] == 'awaiting' and station == home['station']
                       and location == home['location_type'] and row['departure_heading'] == home['heading']
                       and 0.2 <= soc <= 1)
            if not correct:
                misplaced.append({'train': row['train_id'], 'line': home['line'], 'station': station,
                    'location_type': location, 'soc': soc, 'expected_station': home['station'],
                    'expected_location_type': home['location_type']})
        allocations = [{'line': line, 'station': station, 'location_type': location,
                        'service_role': role, 'trainset_count': n}
                       for (line, station, location, role), n in sorted(observed.items())]
        capacity = two_train_station_capacity(doc, allocations, depot_positions=depot_positions)
        first = {}
        depot_departed = set()
        for e in events:
            if e['sim_time_s'] < sample:
                continue
            if e['sim_time_s'] >= opening + 1800:
                break
            train = e['train']
            home = homes[train]
            if e['kind'] == 'Turnaround' and train in headings:
                headings[train] = 'reverse' if headings[train] == 'forward' else 'forward'
            if e['kind'] == 'Dispatched':
                # Native AwaitingDispatch homes have a declared launch heading.
                headings[train] = home['heading']
            if e['kind'] in ('Dispatched', 'DepartStation') and e['sim_time_s'] >= opening and home['service_role'] == 'revenue':
                key = (home['line'], stations[e['station']], headings.get(train))
                # Count launch stock, not a depot train masking a missing
                # station home or passing service arriving from elsewhere.
                if home['location_type'] == 'station' and stations[e['station']] == home['station']:
                    first.setdefault(key, e['sim_time_s'] - opening)
                if e['kind'] == 'Dispatched' and home['location_type'] == 'depot':
                    depot_departed.add(train)
        directions = [{'line': line, 'station': station, 'heading': heading,
            'first_departure_delay_s': first.get((line, station, heading)),
            'passed': first.get((line, station, heading), 61) <= 60}
            for line, station, heading in sorted(expected)]
        late = [e for e in departures if opening - 10800 <= e['sim_time_s'] < opening]
        passenger_late = [e for e in departures if e['kind'] != 'ReturnToStabling'
                          and opening - 12600 <= e['sim_time_s'] < opening]
        depot_moves = [e for e in departures if e['kind'] == 'ReturnToStabling' and opening - 12600 <= e['sim_time_s'] < opening
                       and homes[e['train']]['location_type'] == 'depot']
        home_ok = seen == set(homes) and not misplaced
        directions_ok = bool(directions) and all(d['passed'] for d in directions)
        cycles.append({'after_service_day': day, 'night_snapshot_elapsed_s': sample,
            'inventory_complete': seen == set(homes), 'home_placement_passed': home_ok,
            'misplaced_trainsets': misplaced, 'observed_allocations': allocations,
            'station_trainsets': sum(a['trainset_count'] for a in allocations if a['location_type'] == 'station'),
            'depot_trainsets': sum(a['trainset_count'] for a in allocations if a['location_type'] == 'depot'),
            'capacity': capacity, 'directional_service': directions,
            'morning_launch_passed': directions_ok,
            'depot_revenue_departures_first_30_minutes': len(depot_departed),
            'depot_return_departures_after_closing': len(depot_moves),
            'departures_between_0230_and_0530': len(late),
            'empty_returns_between_0230_and_0530': sum(e['kind'] == 'ReturnToStabling' for e in late),
            'quiet_period_passed': not late,
            'passenger_departures_after_closing': len(passenger_late),
            'passed': home_ok and capacity['passed'] and directions_ok and not passenger_late})
    return {'cycles': cycles, 'fleet_trainsets': len(homes),
            'minimum_train_soc_during_run': min(minima.values(), default=None),
            'battery_reserve_preserved': reserve_ok, 'battery_reserve_tolerance_fraction': SOC_TOLERANCE, 'reserve_departures': reserve_departures,
            'passed': reserve_ok and not reserve_departures and not result['invariant_violations']
                      and all(c['passed'] for c in cycles)}
