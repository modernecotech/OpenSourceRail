"""Possession-aware route/resource scheduling and energy-constrained fleet diagrams.

This is management planning, not interlocking or movement authority. Search is
bounded and reports its actual scope; fixed relocation/charging policies are
explicit rather than represented as globally optimal fleet optimisation.
"""
import copy
import math
from .contracts import digest, integer, overlaps, records, validate
from .roster import optimise


def movement(package, path, start, kind, identity, dwells=None):
    edges = records(package['edges'], 'edges')
    time = start; energy = 0; claims = []; stops = []; dwells = dwells or {}
    for i, eid in enumerate(path['edges']):
        e = edges[eid]
        if i == 0: stops.append(dict(node=e['from'], arrival_s=time, departure_s=time))
        end = time + e['duration_s']
        claims.extend(dict(resource=r, start_s=time, end_s=end) for r in e['resources'])
        energy += e['energy_kwh']; time = end
        dwell = dwells.get(e['to'], 0)
        stops.append(dict(node=e['to'], arrival_s=time, departure_s=time + dwell))
        if dwell:
            # Platform occupation must be named, not guessed from station proximity.
            platforms = [r['id'] for r in package['resources'] if r['kind'] == 'platform' and r.get('node') == e['to']]
            if not platforms: raise ValueError('Dwell requires explicit station platform resource')
            claims.extend(dict(resource=r, start_s=time, end_s=time + dwell) for r in platforms)
        time += dwell
    return dict(id=identity, kind=kind, path_id=path['id'], start_s=start, end_s=time,
                origin=stops[0]['node'], destination=stops[-1]['node'], energy_kwh=energy,
                stops=stops, claims=claims)


def conflict(package, existing, added):
    resources = records(package['resources'], 'resources')
    for claim in added:
        if claim['end_s'] > package['horizon_s']: return 'outside-planning-horizon'
        for p in package.get('possessions', []):
            if claim['resource'] in p['resources'] and overlaps((claim['start_s'], claim['end_s']), (p['start_s'], p['end_s'])):
                return 'possession:' + p['id']
    # Sweep all reservation boundaries: pairwise overlap counting incorrectly
    # rejects disjoint reservations on resources with capacity greater than one.
    grouped = {}
    for c in existing + added:
        grouped.setdefault((c['resource'], c.get('train_id', 'anonymous:' + str(id(c)))), []).append(c)
    all_claims = []
    for (rid, owner), rows in grouped.items():
        merged = []
        for c in sorted(rows, key=lambda row: row['start_s']):
            if merged and c['start_s'] <= merged[-1]['end_s'] + resources[rid]['headway_s']:
                merged[-1]['end_s'] = max(merged[-1]['end_s'], c['end_s'])
            else: merged.append(dict(c))
        all_claims.extend(merged)
    for rid in {r['resource'] for r in added}:
        r = resources[rid]; events = []
        for c in all_claims:
            if c['resource'] == rid:
                events += [(c['start_s'], 1), (c['end_s'] + r['headway_s'], -1)]
        occupancy = 0
        for _, delta in sorted(events):
            occupancy += delta
            if occupancy > r['capacity']: return 'resource-capacity:' + rid
    return None


def fleet_diagram(package, scheduled):
    """Replay every fixed inspection/maintenance and service, including deadheads."""
    paths = records(package['paths'], 'paths')
    trains = records(package['trains'], 'trains')
    charger_rows = sorted(package.get('chargers', []), key=lambda c: c['id'])
    diagram = []; reservations = []
    for tid in sorted(trains):
        t = trains[tid]; location = t['node']; ready = t['ready_s']; energy = t['energy_kwh']; maintenance_by = t['maintenance_by_s']
        jobs = [dict(j, origin=j['node'], destination=j['node'], energy_kwh=0, claims=[], stops=[]) for j in package.get('fleet_jobs', []) if j['train_id'] == tid]
        jobs += [r for r in scheduled if r['train_id'] == tid]
        for job in sorted(jobs, key=lambda j: (j['start_s'], j['id'])):
            if job['start_s'] < ready: return None, 'train-overlap:' + tid
            transits = [None] if location == job['origin'] else [p for p in paths.values()
                if movement(package, p, 0, 'deadhead', 'preview')['origin'] == location
                and movement(package, p, 0, 'deadhead', 'preview')['destination'] == job['origin']]
            choices = []
            for path in transits:
                leg = movement(package, path, ready, 'deadhead', f"{tid}:{job['id']}:position") if path else None
                choices.append((leg['end_s'] if leg else ready, leg['energy_kwh'] if leg else 0, path['id'] if path else '', leg))
            accepted = None
            for _, _, _, relocation in sorted(choices, key=lambda row: row[:3]):
                extra = []; available = ready; trial_energy = energy
                consumption = job['energy_kwh'] + (relocation['energy_kwh'] if relocation else 0)
                need = consumption + t['min_energy_kwh'] - trial_energy
                if need > 0:
                    # Charging occurs before positioning; both charger and track
                    # reservations are retained. A failed charger is a possession.
                    for c in charger_rows:
                        if c['node'] != location: continue
                        duration = math.ceil(need / (c['power_kw'] * c['efficiency']) * 3600)
                        if energy + need > t['capacity_kwh']: continue
                        charge = dict(id=f"{tid}:{job['id']}:charge", train_id=tid, kind='charging',
                            charger_id=c['id'], start_s=ready, end_s=ready + duration,
                            origin=location, destination=location, energy_kwh=-need,
                            stops=[], claims=[dict(resource=c['resource_id'], start_s=ready, end_s=ready + duration)])
                        if not conflict(package, reservations, charge['claims']):
                            extra.append(charge); available = charge['end_s']; trial_energy += need; break
                    else: continue
                if relocation:
                    relocation = movement(package, paths[relocation['path_id']], available, 'deadhead', relocation['id'])
                    relocation['train_id'] = tid
                    extra.append(relocation); available = relocation['end_s']; trial_energy -= relocation['energy_kwh']
                if available > job['start_s']: continue
                if job['kind'] == 'revenue' and job['end_s'] > maintenance_by: continue
                trial_energy -= job['energy_kwh']
                if trial_energy < t['min_energy_kwh'] - 1e-9: continue
                extra.append(dict(job, train_id=tid, remaining_energy_kwh=trial_energy))
                claims = [dict(c, train_id=tid) for leg in extra for c in leg['claims']]
                if conflict(package, reservations, claims): continue
                accepted = extra, trial_energy; break
            if accepted is None: return None, 'fleet-location-energy-or-availability:' + tid
            extra, energy = accepted
            diagram.extend(extra); reservations.extend(dict(c, train_id=tid) for leg in extra for c in leg['claims'])
            if job['kind'] in ('inspection', 'maintenance') and job.get('extends_maintenance_to_s') is not None:
                maintenance_by = job['extends_maintenance_to_s']
            location = job['destination']; ready = job['end_s']
    return diagram, None


def recover(package, disruptions):
    p = copy.deepcopy(package)
    known_trains = records(p['trains'], 'trains'); known_workers = records(p.get('workers', []), 'workers')
    absent = disruptions.get('unavailable_workers', [])
    removed = disruptions.get('unavailable_trains', [])
    if not set(absent) <= known_workers.keys() or not set(removed) <= known_trains.keys():
        raise ValueError('Recovery references unknown train/worker')
    for worker in p.get('workers', []):
        if worker['id'] in absent: worker['available'] = False
    p['unavailable_trains'] = sorted(set(removed))
    p['possessions'] = p.get('possessions', []) + disruptions.get('possessions', [])
    return validate(p)


def plan(package, disruptions=None):
    original = validate(package)
    p = recover(original, disruptions or {})
    paths = records(p['paths'], 'paths'); trains = records(p['trains'], 'trains')
    services = sorted(p['services'], key=lambda s: (-s.get('weight', 1), min(s['departures_s']), s['id']))
    best = None; visits = 0; exhausted = False; rejected = {}

    def finish(rows, score, delay):
        nonlocal visits, exhausted
        duties = []
        by_service = {row['id']: row for row in rows}
        for d in p.get('duties', []):
            if d.get('service_id'):
                if d['service_id'] not in by_service: continue
                service = by_service[d['service_id']]
                d = dict(d, start_s=service['start_s'] + d.get('start_offset_s', 0),
                         end_s=service['end_s'] + d.get('end_offset_s', 0))
            duties.append(d)
        roster_package = dict(p, search_budget=max(1, p['search_budget'] - visits))
        required = {d['id'] for d in duties if d.get('service_id')}
        roster = optimise(roster_package, duties, required_ids=required)
        visits += roster['visits']
        exhausted = exhausted or roster['search_exhausted'] or visits >= p['search_budget']
        if required.intersection(roster['uncovered']): return None
        diagram, reason = fleet_diagram(p, rows)
        if reason: return None
        key = (-score, len(roster['uncovered']), delay, tuple((r['id'], r['train_id'], r['start_s'], r['path_id']) for r in rows))
        return key, rows[:], diagram, roster

    def search(i, rows, score, delay):
        nonlocal visits, exhausted, best
        if visits >= p['search_budget']: exhausted = True; return
        visits += 1
        if i == len(services):
            result = finish(rows, score, delay)
            if result and (best is None or result[0] < best[0]): best = result
            return
        s = services[i]; reasons = set()
        for dep in sorted(s['departures_s']):
            for pid in sorted(s['path_ids']):
                leg = movement(p, paths[pid], dep, 'revenue', s['id'], s.get('dwells_s'))
                if leg['end_s'] > p['horizon_s']: reasons.add('outside-planning-horizon'); continue
                for tid, t in sorted(trains.items()):
                    if tid in p.get('unavailable_trains', []) or s['route_id'] not in t['compatible_routes']: continue
                    candidate = dict(leg, train_id=tid, route_id=s['route_id'])
                    _, reason = fleet_diagram(p, rows + [candidate])
                    if reason: reasons.add(reason); continue
                    search(i + 1, rows + [candidate], score + s.get('weight', 1), delay + dep - min(s['departures_s']))
        rejected[s['id']] = sorted(reasons)
        search(i + 1, rows, score, delay)
    best = finish([], 0, 0)
    search(0, [], 0, 0)
    if best:
        _, scheduled, diagram, roster = best
    else:
        scheduled, diagram, roster = [], [], optimise(p, [])
    selected = {r['id'] for r in scheduled}
    result = dict(schema='osr-operations-plan/1', city=p['city'], environment=p['environment'], revision=p['revision'],
        epoch=p['epoch'], input_sha256=digest(original), scenario_sha256=digest(p), disruptions=disruptions or {},
        services=scheduled, cancelled=[dict(id=s['id'], route_id=s['route_id'], reasons=rejected.get(s['id'], []) or ['no-feasible-fleet-or-staff-assignment']) for s in services if s['id'] not in selected],
        fleet_diagram=diagram, roster=roster, possessions=p.get('possessions', []), visits=visits,
        search_exhausted=exhausted or roster['search_exhausted'], feasible=best is not None,
        optimal_within_declared_dispatch_policy=best is not None and not exhausted and not roster['search_exhausted'],
        dispatch_policy='earliest feasible declared positioning path; pre-position charging in charger identity order',
        objective='maximise weighted services, minimise uncovered staff duties, then departure delay',
        movement_authority=False, native_work_or_staff_assignment=False)
    result['sha256'] = digest(result)
    return result
