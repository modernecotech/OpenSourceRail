"""Bounded exact staff assignment with rest, competence, travel and change cost."""
from .contracts import integer, interval, overlaps, records

ROLES = {'occ', 'station', 'maintenance', 'depot', 'cleaning', 'emergency', 'driver'}


def optimise(package, duties=None, required_ids=None):
    horizon = package['horizon_s']
    duties = sorted(records(package.get('duties', []) if duties is None else duties, 'duties', 100).values(),
                    key=lambda d: (-d.get('weight', 1), d['start_s'], d['id']))
    required_ids = set(required_ids or [])
    if not required_ids <= {d['id'] for d in duties}: raise ValueError('Required roster duty is unknown')
    workers = records(package.get('workers', []), 'workers', 200)
    for d in duties:
        interval(d, horizon); integer(d.get('weight', 1), 1, 1_000_000)
        if d.get('role') not in ROLES or not isinstance(d.get('competencies'), list) or not d.get('location'):
            raise ValueError('Duty requires explicit role, competencies and location')
    for w in workers.values():
        if type(w.get('available')) is not bool or not isinstance(w.get('roles'), list) or not set(w['roles']) <= ROLES:
            raise ValueError('Worker availability and recognised roles required')
        integer(w.get('min_rest_s'), 0, horizon); integer(w.get('max_work_s'), 1, horizon)
        integer(w.get('previous_shift_end_s'), -1_209_600, horizon)
        integer(w.get('max_shift_span_s', w['max_work_s']), 1, horizon)
        integer(w.get('max_continuous_work_s', w['max_work_s']), 1, horizon)
        integer(w.get('min_break_s', 0), 0, horizon)
        for window in w.get('windows', []): interval(window, horizon)
        for c in w.get('competencies', []):
            if not c.get('id') or type(c.get('revoked')) is not bool: raise ValueError('Competence identity/revocation required')
            integer(c.get('valid_from_s'), -1_209_600, horizon); integer(c.get('expires_s'), 0, horizon)
    travel = {}
    for row in package.get('staff_travel', []):
        key = (row['from'], row['to'])
        if key in travel: raise ValueError('Duplicate staff travel relation')
        travel[key] = integer(row['duration_s'], 0, horizon)
    assigned = {key: [] for key in workers}; best = None; visits = 0; exhausted = False

    def eligible(w, d):
        if not w['available'] or d['role'] not in w['roles']: return False
        if not any(a['start_s'] <= d['start_s'] and d['end_s'] <= a['end_s'] for a in w.get('windows', [])): return False
        if d['start_s'] - w['previous_shift_end_s'] < w['min_rest_s']: return False
        held = {c['id'] for c in w.get('competencies', []) if not c['revoked'] and c['valid_from_s'] <= d['start_s'] and d['end_s'] < c['expires_s']}
        if not set(d['competencies']) <= held: return False
        seq = sorted(assigned[w['id']] + [d], key=lambda r: r['start_s'])
        if sum(r['end_s'] - r['start_s'] for r in seq) > w['max_work_s']: return False
        transit_total = 0
        for shift in {r.get('shift_id', 'day') for r in seq}:
            span = [r for r in seq if r.get('shift_id', 'day') == shift]
            if span[-1]['end_s'] - span[0]['start_s'] > w.get('max_shift_span_s', w['max_work_s']): return False
        continuous_start = seq[0]['start_s']
        for a, b in zip(seq, seq[1:]):
            if overlaps(interval(a, horizon), interval(b, horizon)): return False
            transit = 0 if a['location'] == b['location'] else travel.get((a['location'], b['location']))
            if transit is None or a['end_s'] + transit > b['start_s']: return False
            transit_total += transit
            gap = b['start_s'] - a['end_s'] - transit
            if gap > 0 and gap >= w.get('min_break_s', 0): continuous_start = b['start_s']
            if b['end_s'] - continuous_start > w.get('max_continuous_work_s', w['max_work_s']): return False
            # Separate shifts require minimum rest; contiguous split duties belong to one shift.
            if a.get('shift_id', 'day') != b.get('shift_id', 'day') and b['start_s'] - a['end_s'] < w['min_rest_s']: return False
        if sum(r['end_s'] - r['start_s'] for r in seq) + transit_total > w['max_work_s']: return False
        if any(r['end_s'] - r['start_s'] > w.get('max_continuous_work_s', w['max_work_s']) for r in seq): return False
        return True

    def search(i, rows, score, changes):
        nonlocal visits, exhausted, best
        if visits >= package['search_budget']:
            exhausted = True; return
        visits += 1
        if i == len(duties):
            balance = sum(sum(d['end_s']-d['start_s'] for d in work)**2 for work in assigned.values())
            missing_required = len(required_ids - {r['duty_id'] for r in rows})
            key = (missing_required, -score, changes, balance, tuple((r['duty_id'], r['worker_id']) for r in rows))
            if best is None or key < best[0]: best = (key, list(rows))
            return
        d = duties[i]
        for wid in sorted(workers, key=lambda k: (k != d.get('previous_worker'), k)):
            w = workers[wid]
            if eligible(w, d):
                assigned[wid].append(d)
                search(i + 1, rows + [dict(duty_id=d['id'], worker_id=wid, role=d['role'], start_s=d['start_s'], end_s=d['end_s'])],
                       score + d.get('weight', 1), changes + int(bool(d.get('previous_worker')) and wid != d['previous_worker']))
                assigned[wid].pop()
        search(i + 1, rows, score, changes)
    search(0, [], 0, 0)
    rows = best[1] if best else []
    covered = {r['duty_id'] for r in rows}
    return dict(assignments=rows, uncovered=[d['id'] for d in duties if d['id'] not in covered],
                search_exhausted=exhausted, optimal_within_declared_choices=not exhausted, visits=visits,
                objective='maximise weighted coverage, minimise changed assignments, then balance duty hours', creates_native_assignment=False)
