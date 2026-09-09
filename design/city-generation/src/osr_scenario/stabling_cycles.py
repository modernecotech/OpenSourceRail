"""Check repeated morning starts without resetting a native train simulation."""
from collections import Counter
import math

from .stabling_evidence import inspect_morning_service


DAY_S = 86400


def inspect_cycles(doc, result, snapshots, days):
    """Require complete elapsed-time snapshots before each subsequent opening.

    The caller runs from 05:30 through at least 06:00 after the last service
    day. This tests return placement and restart, not daytime timetable delivery.
    """
    if type(days) is not int or not 1 <= days <= 7:
        raise ValueError('service days must be an integer from 1 to 7')
    if doc['scenario']['start_time'] != '05:30' or any(
        f['service_start'] != '05:30' or f['service_end'] != '02:00'
        for f in doc['fleets']
    ):
        raise ValueError('service-cycle screen requires 05:30 start/opening and 02:00 closure')
    if result['sim_duration_s'] < days * DAY_S + 1801:
        raise ValueError('trace must include 30 minutes after the final opening')
    fleet = sum(f['trainset_count'] for f in doc['fleets'])
    stations = {i + 1: s['id'] for i, s in enumerate(doc['stations'])}
    train_lines = {}
    allowed = {}
    next_id = 1
    for f in doc['fleets']:
        allowed[f['line']] = {p['station'] for p in f['dispatch_points']}
        for _ in range(f['trainset_count']):
            train_lines[next_id] = f['line']
            next_id += 1
    cycles = []
    for day in range(1, days + 1):
        opening = day * DAY_S
        sample_time = opening - 60
        rows = snapshots.get(sample_time, [])
        if any(int(r['sim_time_s']) != sample_time for r in rows):
            raise ValueError('night snapshot contains a different elapsed time')
        directional = inspect_morning_service(doc, result['events'], rows, morning_elapsed=opening)
        parked = Counter(stations[int(r['station_id'])] for r in rows if r['phase'] in ('awaiting', 'dwelling'))
        misplaced = []
        allocations = Counter()
        for r in rows:
            if r['phase'] not in ('awaiting', 'dwelling'):
                continue
            line = train_lines[int(r['train_id'].removeprefix('T'))]
            station = stations[int(r['station_id'])]
            allocations[(line, station, r['service_role'])] += 1
            if station not in allowed[line]:
                misplaced.append({'train': r['train_id'], 'line': line, 'station': station,
                                  'service_role': r['service_role'], 'soc': float(r['soc'])})
        socs = [float(r['soc']) for r in rows]
        if any(not math.isfinite(soc) for soc in socs):
            raise ValueError('night snapshot has nonfinite state of charge')
        valid_soc = bool(socs) and all(math.isfinite(soc) and 0.2 <= soc <= 1 for soc in socs)
        # Permit run-in during 02:00–02:30; no routine departure during the
        # remaining three hours of closure. Half-open bounds exclude opening.
        late = [e for e in result['events'] if e['kind'] in ('Dispatched', 'DepartStation')
                and opening - 10800 <= e['sim_time_s'] < opening]
        all_parked = directional['snapshot_covers_fleet'] and sum(parked.values()) == fleet
        cycles.append({
            'after_service_day': day, 'opening_elapsed_s': opening,
            'night_snapshot_elapsed_s': sample_time,
            'parked_trainsets': sum(parked.values()), 'parked_station_count': len(parked),
            'parked_station_trainsets': dict(sorted(parked.items())),
            'largest_station_queue': max(parked.values(), default=0),
            'all_trainsets_parked': all_parked,
            'trainsets_outside_selected_stabling_stations': misplaced,
            'observed_allocations': [{'line': line, 'station': station, 'service_role': role,
                                      'trainset_count': count}
                                     for (line, station, role), count in sorted(allocations.items())],
            'minimum_train_soc': min(socs) if socs else None,
            'mean_train_soc': sum(socs) / len(socs) if socs else None,
            'night_soc_within_20_percent_reserve_and_capacity': valid_soc,
            'departures_between_0230_and_0530': len(late),
            'directional_service': directional,
            'passed': all_parked and not misplaced and valid_soc and not late and directional['passed'],
        })
    minimum = min((row[3] for row in result['per_train_final_soc']), default=None)
    reserve_preserved = minimum is not None and math.isfinite(minimum) and minimum >= 0.2 - 1e-6
    return {'cycles': cycles, 'minimum_train_soc_during_run': minimum,
            'battery_reserve_preserved': reserve_preserved,
            'passed': reserve_preserved and not result['invariant_violations'] and all(c['passed'] for c in cycles)}
