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


def distributed_candidate(text: str) -> tuple[str, list[dict]]:
    scenario = tomllib.loads(text)
    stations = {s['id']: s for s in scenario['stations']}
    sites = {s['station']: s for s in scenario.get('sites', [])}
    lines = {line['id']: line for line in scenario['lines']}
    allocations = []
    replacements = []
    for fleet in scenario['fleets']:
        allowed = {'line', 'trainset_count', 'dispatch_points', 'service_start', 'service_end', 'schedule', 'station_stabling'}
        if set(fleet) - allowed:
            raise ValueError(f"unsupported fleet fields: {set(fleet) - allowed}")
        line = lines[fleet['line']]
        ids = [s['id'] for s in line['stations']]
        if len(ids) < 2 or len(set(ids)) != len(ids):
            raise ValueError(f"{fleet['line']}: line needs distinct station occurrences")
        count = fleet['trainset_count']
        if type(count) is not int or count <= 0:
            raise ValueError(f"{fleet['line']}: fleet must contain positive integer trainsets")
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
            assignments[(point['station'], point['heading'])] += 1
        for (station, heading), assigned in assignments.items():
            allocations.append({'line': fleet['line'], 'station': station, 'heading': heading,
                                'trainset_count': assigned, 'verified_track_slots': None})
        q = json.dumps
        output = ['[[fleets]]', f"line = {q(fleet['line'])}", f'trainset_count = {count}', 'station_stabling = true', 'dispatch_points = [']
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
