"""Reproducible operating candidates for distributed powered-station stabling.

This assigns abstract simulator queues. Track capacity, security and physical
charging access must be evidenced separately before deployment release.
"""
from __future__ import annotations

import json
import math
import re
import tomllib
from collections import Counter


def distributed_candidate(text: str, fleet_roles: list[dict] | None = None) -> tuple[str, list[dict]]:
    scenario = tomllib.loads(text)
    stations = {s['id']: s for s in scenario['stations']}
    sites = {s['station']: s for s in scenario.get('sites', [])}
    lines = {line['id']: line for line in scenario['lines']}
    roles_by_line = {f["line"]: f for f in fleet_roles} if fleet_roles is not None else {}
    if fleet_roles is not None and len(roles_by_line) != len(fleet_roles):
        raise ValueError("duplicate fleet role declarations")
    allocations = []
    replacements = []
    for fleet in scenario['fleets']:
        allowed = {'line', 'trainset_count', 'dispatch_points', 'service_start', 'service_end', 'schedule', 'station_stabling', 'spare_count', 'cold_reserve_count'}
        if set(fleet) - allowed:
            raise ValueError(f"unsupported fleet fields: {set(fleet) - allowed}")
        line = lines[fleet['line']]
        ids = [s['id'] for s in line['stations']]
        if len(ids) < 2 or len(set(ids)) != len(ids):
            raise ValueError(f"{fleet['line']}: line needs distinct station occurrences")
        count = fleet['trainset_count']
        if type(count) is not int or count <= 0:
            raise ValueError(f"{fleet['line']}: fleet must contain positive integer trainsets")
        roles = roles_by_line.get(fleet['line'], fleet)
        if fleet_roles is not None and fleet['line'] not in roles_by_line:
            raise ValueError(f"{fleet['line']}: missing fleet role declaration")
        spare = roles.get('spare_count', 0)
        cold = roles.get('cold_reserve_count', 0)
        if any(type(v) is not int or v < 0 for v in (spare, cold)) or spare + cold >= count:
            raise ValueError(f"{fleet['line']}: reserve roles leave no valid revenue fleet")
        if roles.get('trainset_count', count) != count:
            raise ValueError(f"{fleet['line']}: role inventory differs from scenario fleet")
        if 'peak_count' in roles and roles['peak_count'] + roles.get('service_rotation_count', 0) + spare + cold != count:
            raise ValueError(f"{fleet['line']}: role counts do not reconcile")
        points = []
        for i, station in enumerate(ids):
            site = sites.get(station, {})
            values = (stations[station].get('charging_power_kw', 0), site.get('grid_import_kw', 0), site.get('charger_max_kw', 500))
            if not all(math.isfinite(float(value)) for value in values):
                raise ValueError(f'{station}: nonfinite charging input')
            if values[0] < 150 or values[1] <= 0 or values[2] < 150:
                continue
            if line.get('is_ring', False) or i < len(ids) - 1:
                points.append({'station': station, 'heading': 'forward'})
            if line.get('is_ring', False) or i > 0:
                points.append({'station': station, 'heading': 'reverse'})
        if not points:
            raise ValueError(f"{fleet['line']}: no powered, grid-connected station can support stabling")
        # If fleet size is smaller than the number of station/direction choices,
        # cover the route at even intervals instead of filling its first stops.
        if count < len(points):
            points = [points[i * len(points) // count] for i in range(count)]
        assignments = Counter()
        for i in range(count):
            point = points[i % len(points)]
            role = 'revenue' if i < count - spare - cold else ('spare' if i < count - cold else 'cold_reserve')
            assignments[(point['station'], point['heading'], role)] += 1
        for (station, heading, role), assigned in assignments.items():
            allocations.append({'line': fleet['line'], 'station': station, 'heading': heading,
                                'trainset_count': assigned, 'service_role': role, 'verified_track_slots': None})
        q = json.dumps
        output = ['[[fleets]]', f"line = {q(fleet['line'])}", f'trainset_count = {count}', f'spare_count = {spare}', f'cold_reserve_count = {cold}', 'station_stabling = true', 'dispatch_points = [']
        output += [f"    {{ station = {q(p['station'])}, heading = {q(p['heading'])} }}," for p in points]
        output += [']', f"service_start = {q(fleet['service_start'])}", f"service_end = {q(fleet['service_end'])}", 'schedule = [']
        output += [f"    {{ from = {q(w['from'])}, to = {q(w['to'])}, headway_min = {w['headway_min']} }}," for w in fleet['schedule']]
        output += [']', '', '']
        replacements.append('\n'.join(output))
    blocks = list(re.finditer(r'(?ms)^\[\[fleets\]\][ \t]*\n.*?(?=^\[|\Z)', text))
    if len(blocks) != len(replacements):
        raise ValueError('cannot identify every fleet block without altering other scenario inputs')
    candidate = text
    for match, replacement in reversed(list(zip(blocks, replacements))):
        candidate = candidate[:match.start()] + replacement + candidate[match.end():]
    parsed = tomllib.loads(candidate)
    assert {k: v for k, v in parsed.items() if k != 'fleets'} == {k: v for k, v in scenario.items() if k != 'fleets'}
    return candidate, allocations
