"""Construct station-straight, tangent-continuous research alignments.

The mapped city path is geographical ancestry, not a buildable rail centreline.
This constructor replaces raster stair steps with explicit quintic curves while
retaining every station. Land, survey, cant and transition verification stay open.
"""
from copy import deepcopy
from math import ceil, comb, cos, degrees, fsum, hypot, isfinite, radians
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from engineering.outline import planning_geometry
from .route import FLAGS

R = 6371000.0
PRODUCER = 'engineering/railway_project/alignment.py'


def _number(value, name, *, positive=True):
    if type(value) not in (int, float) or not isfinite(value) or (value <= 0 if positive else value < 0):
        raise ValueError('Finite '+('positive ' if positive else 'nonnegative ')+name+' required')
    return value


def _unit(v):
    length = hypot(*v)
    if length < 1e-8:
        raise ValueError('Distinct station coordinates required')
    return [x / length for x in v]


def _sub(a, b): return [x-y for x, y in zip(a, b)]
def _add(a, b): return [x+y for x, y in zip(a, b)]
def _mul(v, s): return [x*s for x in v]


def bezier(points, t):
    """Polynomial and first three derivatives in the declared local metre plane."""
    def at(rows):
        n = len(rows)-1
        return [fsum(comb(n, i)*(1-t)**(n-i)*t**i*p[k] for i, p in enumerate(rows)) for k in (0, 1)]
    rows = points
    result = [at(rows)]
    for order in range(3):
        n = len(rows)-1
        rows = [_mul(_sub(b, a), n) for a, b in zip(rows, rows[1:])]
        result.append(at(rows))
    return result


def curve_metrics(points, subdivisions):
    """Numerical curve diagnostics with an explicit refinement residual.

    Sampled curvature is not an interval proof or a railway comfort qualification.
    Zero endpoint second derivatives give C2 joins to station straights.
    """
    rows = []
    for i in range(subdivisions+1):
        q, d, dd, ddd = bezier(points, i/subdivisions)
        speed = hypot(*d)
        if speed < 1e-8:
            raise ValueError('Degenerate or reversing alignment tangent')
        cross = d[0]*dd[1]-d[1]*dd[0]
        curvature = cross/speed**3
        derivative = (d[0]*ddd[1]-d[1]*ddd[0])/speed**4 - 3*cross*(d[0]*dd[0]+d[1]*dd[1])/speed**6
        rows.append(dict(t=i/subdivisions, point=q, speed=speed, curvature=curvature, dk_ds=derivative))
    # Simpson integration measures this polynomial curve, not its display chords.
    length = fsum(r['speed']*(1 if i in (0, subdivisions) else 4 if i%2 else 2) for i, r in enumerate(rows))/(3*subdivisions)
    return dict(length_m=length, max_curvature_per_m=max(abs(r['curvature']) for r in rows),
                max_curvature_derivative_per_m2=max(abs(r['dk_ds']) for r in rows), rows=rows)


def _distance(point, path):
    best = float('inf')
    for a, b in zip(path, path[1:]):
        d = _sub(b, a); n = d[0]**2+d[1]**2
        t = max(0., min(1., fsum(x*y for x, y in zip(_sub(point, a), d))/n)) if n else 0.
        best = min(best, hypot(*_sub(point, _add(a, _mul(d, t)))))
    return best


def generate(corridor, *, platform_straight_m, train_length_m, platform_end_margin_m,
             requested_speed_m_s, lateral_acceleration_target_m_s2,
             lateral_jerk_target_m_s3, longitudinal_acceleration_bound_m_s2,
             maximum_deviation_m, root=ROOT):
    if (corridor.get('schema') != 'osr-mapped-corridor-input/1' or
        corridor.get('evaluation_id') != identity({k:v for k, v in corridor.items() if k != 'evaluation_id'}) or
        corridor.get('corridor_geometry_id') != identity(corridor['definition'])):
        raise ValueError('Exact sealed mapped corridor required')
    values = dict(platform_straight_m=platform_straight_m, train_length_m=train_length_m,
        platform_end_margin_m=platform_end_margin_m, requested_speed_m_s=requested_speed_m_s,
        lateral_acceleration_target_m_s2=lateral_acceleration_target_m_s2,
        lateral_jerk_target_m_s3=lateral_jerk_target_m_s3,
        longitudinal_acceleration_bound_m_s2=longitudinal_acceleration_bound_m_s2,
        maximum_deviation_m=maximum_deviation_m)
    for name, value in values.items(): _number(value, name)
    if platform_straight_m < train_length_m + 2*platform_end_margin_m:
        raise ValueError('Straight platform must contain train and declared margins')
    stations = corridor['definition']['stations']
    source = corridor['definition']['coordinates']
    if not 2 <= len(stations) <= 100 or not 2 <= len(source) <= 20000:
        raise ValueError('Bounded explicit corridor geometry required')
    origin = [stations[0]['longitude'], stations[0]['latitude']]
    lon0, lat0 = map(radians, origin)
    def project(p): return [R*cos(lat0)*(radians(p[0])-lon0), R*(radians(p[1])-lat0)]
    def unproject(p): return [degrees(lon0+p[0]/(R*cos(lat0))), degrees(lat0+p[1]/R)]
    source_xy = [project(p) for p in source]
    if any(hypot(*p) > 50000 for p in source_xy) or abs(origin[1]) > 75:
        raise ValueError('Local alignment construction domain is 50km, below75degrees latitude')
    positions = [project([s['longitude'], s['latitude']]) for s in stations]
    directions = [_unit(_sub(b, a)) for a, b in zip(positions, positions[1:])]
    tangents = [directions[0]] + [_unit(_add(a, b)) for a, b in zip(directions, directions[1:])] + [directions[-1]]
    if any(fsum(x*y for x, y in zip(a, b)) <= 0 for a, b in zip(directions, directions[1:])):
        raise ValueError('A turn of90degrees or more needs a separate alignment family')
    pieces = []; station_chain = [0.]; chain = 0.; half = platform_straight_m/2
    display = [positions[0]]; dense_checks = [positions[0]]; max_k = 0.; max_dk = 0.; length_residual = 0.
    curvature_residual = 0.; derivative_residual = 0.; maximum_sample_gap = 0.; curve_chord_bound = 0.
    for i, (a, b) in enumerate(zip(positions, positions[1:])):
        if hypot(*_sub(b, a)) <= 2*platform_straight_m:
            raise ValueError('Stations too close for this straight-platform curve family')
        start = _add(a, _mul(tangents[i], half)); end = _sub(b, _mul(tangents[i+1], half))
        chord = _sub(end, start); d = hypot(*chord)/5
        if any(fsum(x*y for x, y in zip(chord, v)) <= 0 for v in (tangents[i], tangents[i+1])):
            raise ValueError('Station straight reverses the interstation alignment')
        controls = [start, _add(start, _mul(tangents[i], d)), _add(start, _mul(tangents[i], 2*d)),
                    _sub(end, _mul(tangents[i+1], 2*d)), _sub(end, _mul(tangents[i+1], d)), end]
        coarse = curve_metrics(controls, 128); fine = curve_metrics(controls, 256)
        length_residual = max(length_residual, abs(fine['length_m']-coarse['length_m']))
        curvature_residual = max(curvature_residual, abs(fine['max_curvature_per_m']-coarse['max_curvature_per_m']))
        derivative_residual = max(derivative_residual, abs(fine['max_curvature_derivative_per_m2']-coarse['max_curvature_derivative_per_m2']))
        max_k = max(max_k, fine['max_curvature_per_m']); max_dk = max(max_dk, fine['max_curvature_derivative_per_m2'])
        derivative_controls=[_mul(_sub(q,p),5) for p,q in zip(controls,controls[1:])]
        second_controls=[_mul(_sub(q,p),4) for p,q in zip(derivative_controls,derivative_controls[1:])]
        curve_chord_bound=max(curve_chord_bound,max(hypot(*p) for p in second_controls)/(8*256**2))
        # Positive forward projection of all derivative control points is a
        # convex-hull check against a hidden loop between sampled locations.
        unit = _unit(chord)
        if any(fsum(x*y for x,y in zip(_sub(q,p), unit)) <= 0 for p,q in zip(controls, controls[1:])):
            raise ValueError('Curve is not forward monotone')
        pieces.append(dict(from_stop=stations[i]['id'], to_stop=stations[i+1]['id'],
            departure_straight_m=half, arrival_straight_m=half,
            control_points_xy_m=controls, degree=5, curve_length_m=fine['length_m'],
            distance_m=platform_straight_m+fine['length_m'],start_chainage_m=chain))
        points = [a] + [row['point'] for row in fine['rows']] + [b]
        for left,right in zip(points,points[1:]):
            steps=max(1,ceil(hypot(*_sub(right,left))/10.))
            dense_checks += [_add(left,_mul(_sub(right,left),j/steps)) for j in range(1,steps+1)]
            maximum_sample_gap=max(maximum_sample_gap,hypot(*_sub(right,left))/steps)
        display += points[1:]
        chain += pieces[-1]['distance_m']; station_chain.append(chain)
    if len(dense_checks)*(len(source_xy)-1)>2000000:
        raise ValueError('Alignment distance-check computation budget exceeded; use a spatial-index evaluator')
    deviation = max(_distance(p, source_xy) for p in dense_checks)
    # Distance to a set is1-Lipschitz. Bernstein derivative control hulls bound
    # the curve-to-chord error by max||Bsecond|| * delta_t²/8. Together these
    # give a local-plane deviation bound to the declared source polyline.
    deviation_upper=deviation+maximum_sample_gap/2+curve_chord_bound
    geographic = [unproject(p) for p in display]
    display_length = planning_geometry.route(geographic, 'radial')[-1]
    projection_residual = abs(display_length-chain)
    if projection_residual > max(.05, chain*.001):
        raise ValueError('Local-plane and geodetic metric disagree outside stated construction domain')
    definition = dict(schema='osr-station-straight-alignment-geometry/1',
        projection=dict(method='local equirectangular',
            origin_longitude_latitude=origin, earth_radius_m=R, unit='m'),
        stations=[dict(id=s['id'], longitude=s['longitude'], latitude=s['latitude'],
                       chainage_m=at, tangent_xy=t) for s, at, t in zip(stations, station_chain, tangents)],
        platform_straight_m=platform_straight_m, pieces=pieces)
    candidate_id = identity(definition)
    acceleration = requested_speed_m_s**2*max_k
    jerk = requested_speed_m_s**3*max_dk + 2*requested_speed_m_s*longitudinal_acceleration_bound_m_s2*max_k
    checks = dict(straight_platform=platform_straight_m>=train_length_m+2*platform_end_margin_m,
        sampled_lateral_acceleration=acceleration<=lateral_acceleration_target_m_s2,
        sampled_lateral_jerk=jerk<=lateral_jerk_target_m_s3,
        local_plane_corridor_deviation_bound=deviation_upper<=maximum_deviation_m,
        curve_length_refinement=length_residual<.001,
        local_projection_metric=projection_residual<=max(.05,chain*.001))
    sources = deepcopy(corridor['source_sha256']); sources[PRODUCER] = digest(Path(root)/PRODUCER)
    result = dict(schema='osr-station-straight-alignment/1', candidate_id=candidate_id,
        physical_definition=definition, corridor_evaluation_id=corridor['evaluation_id'],
        source_corridor_geometry_id=corridor['corridor_geometry_id'],
        route_m=chain, source_route_m=corridor['route_m'], display_coordinates=geographic,
        legs=[dict(from_stop=r['from_stop'], to_stop=r['to_stop'], distance_m=r['distance_m']) for r in pieces],
        numerical=dict(maximum_sampled_curvature_per_m=max_k, minimum_sampled_radius_m=None if max_k<1e-14 else 1/max_k,
            maximum_sampled_curvature_derivative_per_m2=max_dk, lateral_acceleration_m_s2=acceleration,
            lateral_jerk_upper_estimate_m_s3=jerk, maximum_sampled_source_deviation_m=deviation,
            source_deviation_local_plane_upper_m=deviation_upper,curve_to_display_chord_bound_m=curve_chord_bound,
            deviation_polyline_sampling_addition_m=maximum_sample_gap/2, curve_length_refinement_residual_m=length_residual,
            curvature_refinement_residual_per_m=curvature_residual,
            curvature_derivative_refinement_residual_per_m2=derivative_residual,
            local_vs_geodetic_metric_residual_m=projection_residual, interval_enclosure_verified=False),
        requirements=values, checks=checks, calculated_alignment_screen_passed=all(checks.values()),
        holds=['Land/access, utilities, obstacles and station footprints are not surveyed.',
               'Quintic sampled curvature and jerk are research diagnostics; interval bounds, cant, vehicle dynamics and survey are not verified.',
               'Vertical profile is unknown; no implicit flat route, foundation or operating clearance approval.'],
        source_sha256=sources, **FLAGS)
    result['evaluation_id'] = identity(result)
    return result
