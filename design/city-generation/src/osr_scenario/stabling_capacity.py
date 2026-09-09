"""Two-train overnight station provision, separate from reference platform geometry."""
from collections import Counter


def two_train_station_capacity(doc, allocations, *, depot_positions=None):
    """Check station limits plus explicitly declared depot-stabling positions.

    Depot positions describe a planned storage allocation, not workshop bays
    or verified physical track capacity. Legacy station-only traces get none.
    """
    depot_positions = depot_positions or {}
    selected = {p['station'] for fleet in doc['fleets'] for p in fleet['dispatch_points']}
    known = {s['id'] for s in doc['stations']}
    if not selected or not selected <= known:
        raise ValueError('capacity check requires valid selected stations')
    if any(s not in known or type(n) is not int or n < 0 for s, n in depot_positions.items()):
        raise ValueError('invalid declared depot stabling positions')
    counts = Counter()
    depot_counts = Counter()
    for row in allocations:
        count = row['trainset_count']
        if row['station'] not in known or type(count) is not int or count < 0:
            raise ValueError('invalid station allocation')
        location = row.get('location_type', 'station')
        if location == 'depot':
            if row['station'] not in depot_positions:
                raise ValueError('depot allocation needs explicit stabling positions')
            depot_counts[row['station']] += count
        elif location == 'station':
            counts[row['station']] += count
        else:
            raise ValueError('unknown stabling location type')
    fleet = sum(f['trainset_count'] for f in doc['fleets'])
    rows = []
    for station in sorted(selected | set(counts)):
        limit = 2 if station in selected else 0
        rows.append({'station': station, 'allocated_trainsets': counts[station],
                     'allowed_trainsets': limit, 'excess_trainsets': max(0, counts[station] - limit),
                     'passed': counts[station] <= limit})
    depots = [{'station': s, 'allocated_trainsets': depot_counts[s], 'allowed_trainsets': n,
               'excess_trainsets': max(0, depot_counts[s] - n), 'passed': depot_counts[s] <= n}
              for s, n in sorted(depot_positions.items())]
    allocated = sum(counts.values()) + sum(depot_counts.values())
    complete = allocated == fleet
    return {'station_limit_trainsets': 2, 'selected_station_count': len(selected),
            'available_station_positions': 2 * len(selected), 'fleet_trainsets': fleet,
            'available_depot_positions': sum(depot_positions.values()),
            'station_allocated_trainsets': sum(counts.values()), 'depot_allocated_trainsets': sum(depot_counts.values()),
            'inventory_excess_trainsets': max(0, fleet - 2 * len(selected) - sum(depot_positions.values())),
            'allocated_trainsets': allocated, 'inventory_complete': complete,
            'over_capacity_station_count': sum(not r['passed'] for r in rows),
            'excess_allocated_trainsets': sum(r['excess_trainsets'] for r in rows + depots),
            'stations': rows, 'depots': depots, 'passed': complete and all(r['passed'] for r in rows + depots),
            'scope': 'Two trainsets per selected station plus explicitly allocated depot stabling; workshop bays are separate'}
