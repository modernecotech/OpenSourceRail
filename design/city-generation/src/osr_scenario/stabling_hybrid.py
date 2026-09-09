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
    stations = {s['id']: s for s in doc['stations']}
    known = set(stations)
    site_basis = {s: 'declared-depot' for s in depots}
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
    for line, fleet in fleets.items():
        on_line = {r['id'] for r in lines[line]['stations']}
        powered = {p['station'] for p in fleet['dispatch_points']}
        local = [s for s in depots if s in on_line and s in powered]
        if local:
            destination = min(local, key=lambda s: (depots[s]['archetype'] != 'main-heavy', demand[s], s))
        else:
            # Independent lines use their own existing powered service point.
            # Prefer the designated servicing terminal; no connecting railway
            # or separate heavy workshop is inferred from overnight storage.
            eligible = [r['id'] for r in lines[line]['stations'] if r['id'] in powered]
            if not eligible:
                raise ValueError(f'{line}: no powered location for line-local storage')
            destination = min(eligible, key=lambda s: (
                not stations[s].get('depot_service', False),
                not stations[s].get('is_terminal', False), s))
            depots[destination] = {'archetype': 'layup-minimal', 'fleet_stalls': 0}
            site_basis[destination] = 'storage-at-existing-powered-service-point'
        role_counts = {'revenue': remaining[line], 'spare': fleet.get('spare_count', 0),
                       'cold_reserve': fleet.get('cold_reserve_count', 0)}
        for role, count in role_counts.items():
            if count:
                allocations.append({'line': line, 'station': destination, 'location_type': 'depot',
                                    'service_role': role, 'trainset_count': count})
                demand[destination] += count
    requirements = []
    for station, count in sorted(demand.items()):
        rows = [r for r in allocations if r['location_type'] == 'depot' and r['station'] == station]
        roles = Counter()
        length = 0.0
        for r in rows:
            roles[r['service_role']] += r['trainset_count']
            length += r['trainset_count'] * (profiles[families[r['line']]]['length_m'] + 10)
        requirements.append({'station': station, 'archetype': depots[station]['archetype'],
                             'site_basis': site_basis[station], 'lines': sorted({r['line'] for r in rows}),
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
            'capacity': capacity, 'missing_morning_directions': missing, 'depot_access_requirements': [],
            'physical_release_ready': False,
            'scope': 'Two revenue trainsets per station where fleet permits; all remaining revenue stock and reserves allocated to storage on their own line'}


def native_hybrid_candidate(text, allocation):
    """Serialize the plan only when every depot is accessible on its own line.

    This declares storage slots at existing depot nodes, not new rail links.
    """
    import json
    import re
    import tomllib

    if not allocation['allocation_passed']:
        raise ValueError('morning station allocation is incomplete')
    if allocation['depot_access_requirements']:
        raise ValueError('cross-line depot assignments are not allowed')
    doc = tomllib.loads(text)
    requirements = {r['station']: r['stabling_positions_required'] for r in allocation['depot_requirements']}
    q = json.dumps
    candidate = text
    for match in reversed(list(re.finditer(r'(?ms)^\[\[fleets\]\][ \t]*\n.*?(?=^\[|\Z)', text))):
        fleet = tomllib.loads(match.group())['fleets'][0]
        points = {(p['station'], p['heading']) for p in fleet['dispatch_points']}
        homes = []
        for row in allocation['allocations']:
            if row['line'] != fleet['line']:
                continue
            headings = [p['heading'] for p in fleet['dispatch_points'] if p['station'] == row['station']]
            if not headings:
                raise ValueError(f"{fleet['line']}: depot needs a powered on-line dispatch point")
            heading = row.get('heading', headings[0])
            if (row['station'], heading) not in points:
                raise ValueError('home heading is absent from dispatch points')
            homes.append('{ ' + ', '.join(f'{key} = {q(value)}' for key, value in {
                'station': row['station'], 'heading': heading, 'location_type': row['location_type'],
                'service_role': row['service_role'], 'trainset_count': row['trainset_count'],
            }.items()) + ' }')
        if 'overnight_allocations' in fleet:
            raise ValueError('expected a station-only source candidate')
        replacement = match.group().rstrip() + '\novernight_allocations = [\n  ' + ',\n  '.join(homes) + '\n]\n\n'
        candidate = candidate[:match.start()] + replacement + candidate[match.end():]
    for match in reversed(list(re.finditer(r'(?ms)^\[\[stations\]\][ \t]*\n.*?(?=^\[|\Z)', candidate))):
        station = tomllib.loads(match.group())['stations'][0]
        if station['id'] not in requirements:
            continue
        if 'depot_stabling_positions' in station:
            raise ValueError('conflicting depot storage declaration')
        block = match.group().rstrip()
        if 'is_depot' in station:
            block = re.sub(r'(?m)^is_depot\s*=\s*false\b', 'is_depot = true', block)
            depot_flag = ''
        else:
            depot_flag = '\nis_depot = true'
        # This is a storage declaration at an existing node; workshop, charging
        # quantities and all interstation geometry are preserved.
        replacement = block + depot_flag + f"\ndepot_stabling_positions = {requirements[station['id']]}\n\n"
        candidate = candidate[:match.start()] + replacement + candidate[match.end():]
    parsed = tomllib.loads(candidate)
    assert {k: v for k, v in parsed.items() if k not in ('fleets', 'stations')} == {
        k: v for k, v in doc.items() if k not in ('fleets', 'stations')}
    return candidate
