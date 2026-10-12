"""Strict, revisioned management-planning inputs; times are epoch-relative seconds."""
import copy
from datetime import datetime
from ..config import digest, finite, identifier


def integer(value, low=0, high=1_209_600):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'Expected integer in [{low}, {high}]')
    return value


def records(rows, name, limit=1000):
    if not isinstance(rows, list) or len(rows) > limit:
        raise ValueError(f'{name} must be a bounded list')
    result = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f'Invalid {name} record')
        key = identifier(row.get('id'))
        if key in result:
            raise ValueError(f'Duplicate {name} identity: {key}')
        result[key] = row
    return result


def interval(row, horizon):
    start = integer(row.get('start_s'), 0, horizon)
    end = integer(row.get('end_s'), 1, horizon)
    if end <= start:
        raise ValueError('Interval must have positive duration')
    return start, end


def overlaps(a, b):
    return a[0] < b[1] and b[0] < a[1]


def validate(package):
    p = copy.deepcopy(package)
    if not isinstance(p, dict) or p.get('schema') != 'osr-operations/1':
        raise ValueError('Expected osr-operations/1')
    identifier(p.get('city')); identifier(p.get('revision'))
    if p.get('environment') not in ('simulation', 'physical'):
        raise ValueError('Invalid environment')
    epoch = datetime.fromisoformat(p['epoch'].replace('Z', '+00:00'))
    if epoch.tzinfo is None:
        raise ValueError('Planning epoch must include timezone')
    h = integer(p.get('horizon_s'), 1)
    nodes = records(p.get('nodes'), 'nodes')
    resources = records(p.get('resources'), 'resources')
    edges = records(p.get('edges'), 'edges')
    paths = records(p.get('paths'), 'paths')
    for n in nodes.values():
        if type(n.get('station')) is not bool or not isinstance(n.get('name'), str) or not n['name']:
            raise ValueError('Node name and station flag required')
        finite(n.get('lat'), -90, 90); finite(n.get('lon'), -180, 180)
    for r in resources.values():
        integer(r.get('capacity'), 1, 100)
        integer(r.get('headway_s'), 0, h)
        if r.get('kind') not in ('track', 'platform', 'junction', 'charger', 'depot'):
            raise ValueError('Unknown physical resource kind')
    for e in edges.values():
        if e.get('from') not in nodes or e.get('to') not in nodes:
            raise ValueError('Edge references unknown physical node')
        integer(e.get('duration_s'), 1, h)
        finite(e.get('energy_kwh'), 0, 1e6); finite(e.get('distance_km'), 0, 1e6)
        refs = e.get('resources')
        if not isinstance(refs, list) or not refs or len(set(refs)) != len(refs) or not set(refs) <= resources.keys():
            raise ValueError('Edge requires unique known physical resources')
    for path in paths.values():
        refs = path.get('edges')
        if not isinstance(refs, list) or not refs or len(refs) > 200 or not set(refs) <= edges.keys():
            raise ValueError('Path requires known edges')
        if any(edges[a]['to'] != edges[b]['from'] for a, b in zip(refs, refs[1:])):
            raise ValueError('Path is not physically connected; map interchanges do not imply crossovers')
    services = records(p.get('services'), 'services', 80)
    for s in services.values():
        identifier(s.get('route_id'))
        if not isinstance(s.get('path_ids'), list) or not s['path_ids'] or len(set(s['path_ids'])) != len(s['path_ids']) or not set(s['path_ids']) <= paths.keys():
            raise ValueError('Service requires unique known paths')
        deps = s.get('departures_s')
        endpoints = {(edges[paths[pid]['edges'][0]]['from'], edges[paths[pid]['edges'][-1]]['to']) for pid in s['path_ids']}
        if len(endpoints) != 1: raise ValueError('Service alternatives must have identical physical endpoints')
        if not isinstance(deps, list) or not deps or len(deps) > 100 or len(set(deps)) != len(deps):
            raise ValueError('Departure choices must be unique and bounded')
        for d in deps: integer(d, 0, h)
        integer(s.get('weight', 1), 1, 1_000_000)
        for node, dwell in s.get('dwells_s', {}).items():
            if node not in nodes: raise ValueError('Unknown dwell node')
            integer(dwell, 0, h)
    for row in records(p.get('possessions', []), 'possessions').values():
        identifier(row.get('id')); interval(row, h)
        if not isinstance(row.get('resources'), list) or not row['resources'] or not set(row['resources']) <= resources.keys():
            raise ValueError('Possession requires known physical resources')
    trains = records(p.get('trains'), 'trains', 100)
    for t in trains.values():
        if t.get('node') not in nodes: raise ValueError('Unknown train location')
        integer(t.get('ready_s'), 0, h); integer(t.get('maintenance_by_s'), 0, h)
        cap = finite(t.get('capacity_kwh'), 0.01, 1e6)
        minimum = finite(t.get('min_energy_kwh'), 0, cap)
        finite(t.get('energy_kwh'), minimum, cap)
        if not isinstance(t.get('compatible_routes'), list): raise ValueError('Train route compatibility required')
    for c in records(p.get('chargers', []), 'chargers').values():
        if c.get('node') not in nodes or c.get('resource_id') not in resources or resources[c['resource_id']]['kind'] != 'charger':
            raise ValueError('Charger requires known node and charger resource')
        finite(c.get('power_kw'), 0.01, 1e6); finite(c.get('efficiency'), 0.01, 1)
    for j in records(p.get('fleet_jobs', []), 'fleet jobs').values():
        interval(j, h)
        if j.get('extends_maintenance_to_s') is not None: integer(j['extends_maintenance_to_s'], j['end_s'], h)
        if j.get('train_id') not in trains or j.get('node') not in nodes or j.get('kind') not in ('inspection', 'maintenance'):
            raise ValueError('Invalid fixed fleet job')
    if not isinstance(p.get('unavailable_trains', []), list) or not set(p.get('unavailable_trains', [])) <= trains.keys(): raise ValueError('Unknown unavailable train')
    records(p.get('duties', []), 'duties', 100)
    records(p.get('workers', []), 'workers', 200)
    budget = integer(p.get('search_budget', 10000), 1, 100000)
    p['search_budget'] = budget
    # Hashing also rejects non-finite values in optional metadata.
    digest(p)
    return p
