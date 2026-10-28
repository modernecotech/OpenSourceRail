"""Finite-fin/primary interval geometry, without a propulsion or journey model.

Positions use a forward longitudinal axis.  A car's fin begins ``fin_setback``
behind its nose and extends backwards by ``fin_length``.  Banks have positive
length and do not overlap.  Exact edge-alignment events bound linear-overlap
segments; envelope crossings additionally locate the worst single-fin overlap.
The 512 bank/fin-pair limit is an execution bound, not a railway requirement.
"""
from hashlib import sha256
from itertools import islice
import json
from math import fsum, isfinite

SCHEMA = 'osr-sparse-launch-geometry/1'
MAX_PAIRS = 512
RESOLUTION_M = 1e-12


def _q(value):
    if not isfinite(value):
        raise ValueError('Finite representable geometry required')
    result = round(value, 12)
    return 0.0 if result == 0 else result


def _number(value, name, *, positive=False, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('Finite numeric ' + name + ' required')
    try:
        result = _q(float(value))
    except (OverflowError, ValueError) as error:
        raise ValueError('Finite numeric ' + name + ' required') from error
    if positive and result <= 0 or nonnegative and result < 0:
        raise ValueError(('Positive ' if positive else 'Nonnegative ') + name + ' required')
    return result


def _identity(value):
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    return sha256(raw).hexdigest()


def _union(intervals):
    result = []
    for lo, hi in sorted(intervals):
        if hi <= lo:
            continue
        if result and lo <= result[-1][1]:
            result[-1][1] = max(result[-1][1], hi)
        else:
            result.append([lo, hi])
    return result


def geometry(bank_starts_m, bank_length_m, *, cars=6, car_length_m=17.,
             coupling_gap_m=.5, fin_length_m=9., fin_setback_m=4.,
             initial_nose_m=104.5, launch_distance_m=500.):
    """Return bounded exact interval diagnostics; every qualification stays open.

    Coordinates are normalized to the first bank and rounded to 1e-12 m.  A
    common coordinate translation therefore leaves the result unchanged.
    Physical geometry identity excludes initial position and requested travel;
    evaluation identity includes them.  Positive geometric overlap is never
    interpreted as available force, self-start capability or native admission.
    """
    if type(cars) is not int or cars < 1:
        raise ValueError('Positive integer car count required')
    try:
        if isinstance(bank_starts_m, (str, bytes)):
            raise TypeError
        sites = list(islice(iter(bank_starts_m), MAX_PAIRS + 1))
    except TypeError as error:
        raise ValueError('An ordinary finite bank-position sequence is required') from error
    if not sites or len(sites) * cars > MAX_PAIRS:
        raise ValueError('Request needs 1 to 512 bank/fin pairs; this is an execution bound')
    sites = sorted(_number(value, 'bank position') for value in sites)
    anchor = sites[0]
    sites = [_q(value - anchor) for value in sites]
    bank_length = _number(bank_length_m, 'LIM bank length', positive=True)
    car_length = _number(car_length_m, 'car length', positive=True)
    gap = _number(coupling_gap_m, 'coupling gap', nonnegative=True)
    fin_length = _number(fin_length_m, 'fin length', positive=True)
    setback = _number(fin_setback_m, 'fin setback', nonnegative=True)
    initial = _q(_number(initial_nose_m, 'initial nose') - anchor)
    distance = _number(launch_distance_m, 'launch distance', positive=True)
    if _q(fin_length + setback) > car_length:
        raise ValueError('Fin and nose setback must fit within each car')
    if any(_q(left + bank_length) > right for left, right in zip(sites, sites[1:])):
        raise ValueError('Duplicate or overlapping primary banks are not permitted')
    pitch = _q(car_length + gap)
    train_length = _q(cars * car_length + (cars - 1) * gap)
    # These checks also reject overflow in derived coordinates before event work.
    _q(initial + distance)
    _q(sites[-1] + bank_length)
    physical = dict(schema='osr-sparse-launch-physical-geometry/1', cars=cars,
                    car_length_m=car_length, coupling_gap_m=gap,
                    fin_length_m=fin_length, fin_setback_m=setback,
                    bank_starts_m=sites, bank_length_m=bank_length)
    physical_id = _identity(physical)
    request = dict(schema=SCHEMA, physical_geometry_id=physical_id,
                   initial_nose_m=initial, launch_distance_m=distance,
                   coordinate_resolution_m=RESOLUTION_M)

    def length(s, site, car):
        right = _q(initial + s - pitch * car - setback)
        left = _q(right - fin_length)
        return _q(max(0., min(site + bank_length, right) - max(site, left)))

    def record(s):
        matches = []
        full = set()
        for site_index, site in enumerate(sites):
            for car in range(cars):
                overlap = length(s, site, car)
                if overlap > 0:
                    contained = overlap == fin_length
                    if contained:
                        full.add(car)
                    matches.append(dict(site_index=site_index, car_index=car,
                                        overlap_m=overlap, full_fin_contained=contained))
        return dict(nose_advance_m=s, nose_x_m=_q(initial + s),
                    sum_overlap_m=_q(fsum(row['overlap_m'] for row in matches)),
                    longest_single_fin_overlap_m=max((row['overlap_m'] for row in matches), default=0.),
                    active_fins=len({row['car_index'] for row in matches}),
                    active_sites=len({row['site_index'] for row in matches}),
                    active_pairs=len(matches), fully_contained_fins=len(full),
                    overlap_pairs=matches)

    events = {0., distance}
    future = []
    for site in sites:
        for car in range(cars):
            offset = pitch * car + setback - initial
            lo = _q(site + offset)
            hi = _q(site + bank_length + offset + fin_length)
            if hi > 0:
                future.append([max(0., lo), hi])
            for event in (lo, _q(site + bank_length + offset),
                          _q(site + offset + fin_length), hi):
                if 0 <= event <= distance:
                    events.add(event)
    events = sorted(events)
    mids = [_q((lo + hi) / 2) for lo, hi in zip(events, events[1:])]
    crossings = set()
    # The longest individual intersection is the maximum of linear functions.
    # Its minimum can occur between edge events, when two overlaps are equal.
    for lo, hi, mid in zip(events, events[1:], mids):
        lines = {}
        for site in sites:
            for car in range(cars):
                if length(mid, site, car) <= 0:
                    continue
                left, right = length(lo, site, car), length(hi, site, car)
                slope = 1 if right > left else -1 if right < left else 0
                intercept = _q(left - slope * lo)
                lines[slope] = max(intercept, lines.get(slope, intercept))
        coefficients = list(lines.items())
        for index, (a, c) in enumerate(coefficients):
            for b, d in coefficients[index + 1:]:
                cross = _q((d - c) / (a - b))
                if lo < cross < hi:
                    crossings.add(cross)
    points = sorted(set(events) | set(mids) | crossings)
    rows = {point: record(point) for point in points}
    all_rows = list(rows.values())
    future = _union(future)
    required = _union([[lo, min(distance, hi)] for lo, hi in future if lo < distance])
    covered = _q(fsum(hi - lo for lo, hi in required))
    min_overlap = min(row['sum_overlap_m'] for row in all_rows)
    value = dict(
        **request, physical_geometry=physical,
        geometry_evaluation_id=_identity(request),
        coordinate_frame='Forward longitudinal axis, origin at the first bank start',
        train_length_m=train_length, fin_pitch_m=pitch,
        bank_count=len(sites), site_count=len(sites),
        summed_bank_length_m=_q(len(sites) * bank_length),
        bank_footprint_span_m=_q(sites[-1] + bank_length),
        primary_face_count=2 * len(sites),
        primary_face_length_sum_m=_q(2 * len(sites) * bank_length),
        receiving_extent_m=None, installed_cost=None,
        future_contact_union_m=future,
        required_launch_contact_union_m=required,
        geometric_covered_m=covered,
        geometric_uncovered_m=_q(distance - covered),
        last_contact_advance_m=future[-1][1] if future else None,
        start_overlap=rows[0.],
        initial_geometric_overlap=rows[0.]['sum_overlap_m'] > 0,
        continuous_contact_over_launch=min_overlap > 0,
        min_sum_overlap_m=min_overlap,
        max_sum_overlap_m=max(row['sum_overlap_m'] for row in all_rows),
        min_active_fins=min(row['active_fins'] for row in all_rows),
        max_active_fins=max(row['active_fins'] for row in all_rows),
        min_active_sites=min(row['active_sites'] for row in all_rows),
        max_active_sites=max(row['active_sites'] for row in all_rows),
        longest_single_fin_min_m=min(row['longest_single_fin_overlap_m'] for row in all_rows),
        longest_single_fin_metric='Largest single bank/fin intersection, minimized over requested travel',
        fully_contained_fin_all_positions=all(row['fully_contained_fins'] > 0 for row in all_rows),
        breakpoints_m=events,
        breakpoint_records=[rows[point] for point in events],
        interval_records=[rows[point] for point in mids],
        single_fin_envelope_records=[rows[point] for point in sorted(crossings)],
        available_force_N=None, available_electrical_power_W=None,
        force_scaling_per_overlap_available=False,
        force_map_available=False, self_start_proven=False,
        physical_evidence=False, physical_accepted=False,
        engineering_accepted=False, native_dispatch_allowed=False,
        manufacturing_release=False, operating_release=False,
        interval_semantics='Positive overlap on interval interiors; an envelope endpoint can have zero overlap',
        scope='Longitudinal geometry only. No force, fringe-field, current, thermal, motion, braking, cost or physical qualification.')
    value['geometry_result_id'] = _identity(value)
    return value
