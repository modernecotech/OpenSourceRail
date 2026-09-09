"""Station launch stock plus depot stabling for the rest of the declared fleet."""
from collections import Counter

from .stabling_capacity import two_train_station_capacity


def station_and_depot_allocation(doc, design, profiles):
    fleets = {f['line']: f for f in doc['fleets']}
    lines = {l['id']: l for l in doc['lines']}
    families = {l.get('id') or l['name']: l['rolling_stock'] for l in design['lines']}
    depots = {d.get('station') or d.get('station_id'): d for d in design.get('depots', [])}
    if not depots:
        raise ValueError('station/depot allocation needs a declared depot')
    known = {s['id'] for s in doc['stations']}
    if not set(depots) <= known:
        raise ValueError('declared depot is absent from the operating network')
    remaining = {line: f['trainset_count'] - f.get('spare_count', 0) - f.get('cold_reserve_count', 0)
                 for line, f in fleets.items()}
    counts = Counter()
    station_rows = Counter()
    missing = []
    # First protect one revenue set for every planned departure direction.
    for line, f in fleets.items():
        for p in f['dispatch_points']:
            station, heading = p['station'], p['heading']
            if counts[station] < 2 and remaining[line] > 0:
                station_rows[(line, station, heading)] += 1
                counts[station] += 1
                remaining[line] -= 1
            else:
                missing.append({'line': line, 'station': station, 'heading': heading})
    # Endpoints have a single inward direction but still receive two sets.
    for line, f in fleets.items():
        for p in f['dispatch_points']:
            station, heading = p['station'], p['heading']
            while counts[station] < 2 and remaining[line] > 0:
                station_rows[(line, station, heading)] += 1
                counts[station] += 1
                remaining[line] -= 1
    allocations = [{'line': line, 'station': station, 'heading': heading, 'location_type': 'station',
                    'service_role': 'revenue', 'trainset_count': n}
                   for (line, station, heading), n in sorted(station_rows.items())]
    demand = Counter()
    access = []
    for line, fleet in fleets.items():
        on_line = {r['id'] for r in lines[line]['stations']}
        local = [s for s in depots if s in on_line]
        eligible = local or list(depots)
        destination = min(eligible, key=lambda s: (depots[s]['archetype'] != 'main-heavy', demand[s], s))
        role_counts = {'revenue': remaining[line], 'spare': fleet.get('spare_count', 0),
                       'cold_reserve': fleet.get('cold_reserve_count', 0)}
        for role, count in role_counts.items():
            if count:
                allocations.append({'line': line, 'station': destination, 'location_type': 'depot',
                                    'service_role': role, 'trainset_count': count})
                demand[destination] += count
        if sum(role_counts.values()) and not local:
            access.append({'line': line, 'depot_station': destination,
                           'trainsets': sum(role_counts.values()), 'status': 'interline-depot-access-to-be-detailed'})
    requirements = []
    for station, count in sorted(demand.items()):
        rows = [r for r in allocations if r['location_type'] == 'depot' and r['station'] == station]
        roles = Counter()
        length = 0.0
        for r in rows:
            roles[r['service_role']] += r['trainset_count']
            length += r['trainset_count'] * (profiles[families[r['line']]]['length_m'] + 10)
        requirements.append({'station': station, 'archetype': depots[station]['archetype'],
                             'stabling_positions_required': count, 'service_roles': dict(roles),
                             'usable_stabling_length_required_m': length,
                             'workshop_bays': depots[station].get('fleet_stalls', 0),
                             'verified_stabling_positions': None})
    capacity = two_train_station_capacity(doc, allocations, depot_positions=dict(demand))
    return {'allocation_passed': capacity['passed'] and not missing,
            'station_trainsets': sum(counts.values()), 'depot_trainsets': sum(demand.values()),
            'fleet_trainsets': sum(f['trainset_count'] for f in fleets.values()),
            'station_trainsets_by_location': dict(sorted(counts.items())),
            'allocations': allocations, 'depot_requirements': requirements,
            'capacity': capacity, 'missing_morning_directions': missing, 'depot_access_requirements': access,
            'physical_release_ready': False,
            'scope': 'Two revenue trainsets per station where fleet permits; all remaining revenue stock and reserves allocated to declared depots'}
