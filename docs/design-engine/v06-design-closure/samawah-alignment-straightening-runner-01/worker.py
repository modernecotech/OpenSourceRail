"""Authenticated screening of bounded route simplifications; no active map edits."""
from __future__ import annotations

from bisect import bisect_right
from copy import deepcopy
import gzip
import hashlib
import importlib.machinery
import json
import math
from pathlib import Path
import subprocess
import sys
import traceback

RUN = Path(__file__).resolve().parent
REQUEST = json.loads((RUN / 'request.json').read_bytes())
ROOT = Path(REQUEST['repository']).resolve()
COMMIT = REQUEST['source_commit']
READS = {}
IMPORTS = {}
CONSUMED = {}
ENCODE = lambda value: (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
SHA = lambda raw: hashlib.sha256(raw).hexdigest()
IDENTITY = lambda value: SHA(ENCODE(value))
EARTH_RADIUS_M = 6_371_008.8


def save(path: str, value: object) -> None:
    target = RUN / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(ENCODE(value))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


reader = subprocess.Popen(
    ['/usr/bin/git', '-c', 'core.packedGitWindowSize=16m',
     '-c', 'core.packedGitLimit=32m', '-C', str(ROOT), 'cat-file', '--batch'],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
)


def blob(name: str):
    if name in READS:
        return READS[name]
    reader.stdin.write((COMMIT + ':' + name + '\n').encode())
    reader.stdin.flush()
    header = reader.stdout.readline().decode().split()
    require(len(header) == 3 and header[1] == 'blob', 'Missing committed source blob: ' + name)
    raw = reader.stdout.read(int(header[2]))
    require(reader.stdout.read(1) == b'\n', 'Truncated committed source blob: ' + name)
    record = dict(path=name, commit=COMMIT, git_blob_id=header[0], sha256=SHA(raw), bytes=len(raw))
    READS[name] = (raw, record)
    return raw, record


def checked(name: str) -> bytes:
    expected, _ = blob(name)
    path = ROOT / name
    require(path.resolve().is_relative_to(ROOT) and not path.is_symlink(), 'Ordinary source path required: ' + name)
    actual = path.read_bytes()
    require(actual == expected, 'Current bytes differ from the requested commit: ' + name)
    CONSUMED[name] = SHA(actual)
    return actual


original_source_code = importlib.machinery.SourceFileLoader.get_code
original_sourceless_code = importlib.machinery.SourcelessFileLoader.get_code


def is_project(fullname: str) -> bool:
    return (fullname == 'engineering' or fullname.startswith('engineering.') or
            fullname == 'services' or fullname.startswith('services.'))


def source_code(loader, fullname):
    if not is_project(fullname):
        return original_source_code(loader, fullname)
    path = Path(loader.path).resolve()
    require(path.is_relative_to(ROOT), 'Foreign project source: ' + fullname)
    name = path.relative_to(ROOT).as_posix()
    raw = checked(name)
    IMPORTS[fullname] = dict(path=name, sha256=SHA(raw), method='compile-authenticated-source-bytes; no project pyc lookup')
    return compile(raw, str(path), 'exec', dont_inherit=True)


def no_project_pyc(loader, fullname):
    if is_project(fullname):
        raise ImportError('Sourceless project bytecode is forbidden: ' + fullname)
    return original_sourceless_code(loader, fullname)


importlib.machinery.SourceFileLoader.get_code = source_code
importlib.machinery.SourcelessFileLoader.get_code = no_project_pyc
require(sys.dont_write_bytecode, 'Python bytecode writes must be disabled at startup')
sys.path.insert(0, str(ROOT))


def project_point(lonlat, origin):
    lon0, lat0 = origin
    x = EARTH_RADIUS_M * math.radians(lonlat[0] - lon0) * math.cos(math.radians(lat0))
    y = EARTH_RADIUS_M * math.radians(lonlat[1] - lat0)
    return x, y


def point_segment_distance_sq(p, a, b):
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    den = dx * dx + dy * dy
    if den == 0:
        return (p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / den))
    qx = a[0] + t * dx
    qy = a[1] + t * dy
    return (p[0] - qx) ** 2 + (p[1] - qy) ** 2


def rdp_indices(points, tolerance_m):
    if len(points) <= 2:
        return list(range(len(points)))
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1)]
    limit_sq = tolerance_m * tolerance_m
    while stack:
        first, last = stack.pop()
        greatest = limit_sq
        selected = None
        for index in range(first + 1, last):
            distance_sq = point_segment_distance_sq(points[index], points[first], points[last])
            if distance_sq > greatest:
                greatest = distance_sq
                selected = index
        if selected is not None:
            keep.add(selected)
            stack.extend(((first, selected), (selected, last)))
    return sorted(keep)


def unique_adjacent(points):
    result = []
    for point in points:
        value = [float(point[0]), float(point[1])]
        if not result or value != result[-1]:
            result.append(value)
    return result


def source_interval(coordinates, chain, start_m, end_m, geometry):
    start = geometry.point(coordinates, chain, start_m)
    end = geometry.point(coordinates, chain, end_m)
    rows = [start]
    for i, at in enumerate(chain):
        if start_m + 1e-8 < at < end_m - 1e-8:
            rows.append(coordinates[i])
    rows.append(end)
    rows = unique_adjacent(rows)
    require(len(rows) >= 2, 'Station-to-station source segment collapsed')
    return rows


def sampled_points(coordinates, chain, start_m, end_m, geometry, step_m=5.0):
    result = []
    cursor = start_m
    while cursor < end_m:
        result.append(geometry.point(coordinates, chain, cursor))
        cursor = min(end_m, cursor + step_m)
    result.append(geometry.point(coordinates, chain, end_m))
    return result


def max_deviation_m(source_samples, simplified, origin):
    target = [project_point(point, origin) for point in simplified]
    greatest = 0.0
    for point in source_samples:
        p = project_point(point, origin)
        distance_sq = min(point_segment_distance_sq(p, target[i], target[i + 1])
                          for i in range(len(target) - 1))
        greatest = max(greatest, math.sqrt(distance_sq))
    return greatest


def simplify_line(line, tolerance_m, geometry, baseline_chain):
    coordinates = line['coordinates']
    stops = line['stops']
    for stop in stops:
        mapped = geometry.point(coordinates, baseline_chain, stop['chainage_m'])
        require(stop['lon'] == mapped[0] and stop['lat'] == mapped[1],
                'Source stop does not exactly match its mapped polyline: ' + stop['id'])

    origin = (sum(p[0] for p in coordinates) / len(coordinates),
              sum(p[1] for p in coordinates) / len(coordinates))
    simplified = []
    worst_deviation = 0.0
    source_count = 0
    anchors = [0.0] + [stop['chainage_m'] for stop in stops] + [baseline_chain[-1]]
    for index, (start_m, end_m) in enumerate(zip(anchors, anchors[1:])):
        if end_m - start_m <= 1e-9:
            continue
        original_segment = source_interval(coordinates, baseline_chain, start_m, end_m, geometry)
        metric_segment = [project_point(point, origin) for point in original_segment]
        kept = rdp_indices(metric_segment, tolerance_m)
        selected = [original_segment[i] for i in kept]
        source_count += len(original_segment)
        segment_chain = geometry.route(selected, 'radial')
        if not simplified:
            simplified.extend(selected)
        else:
            require(simplified[-1] == selected[0], 'Simplification changed a stop anchor')
            simplified.extend(selected[1:])
        deviation = max_deviation_m(sampled_points(coordinates, baseline_chain, start_m,
            end_m, geometry), selected, origin)
        worst_deviation = max(worst_deviation, deviation)
    new_chain = geometry.route(simplified, 'radial')
    require(worst_deviation <= tolerance_m + 0.05,
            f'Sampled route deviation {worst_deviation:.4f} m exceeds tolerance {tolerance_m:.2f} m')
    new_stops = deepcopy(stops)
    new_stop_chainages = []
    next_vertex = 0
    for stop in stops:
        target = [stop['lon'], stop['lat']]
        vertex = next((i for i in range(next_vertex, len(simplified)) if simplified[i] == target), None)
        require(vertex is not None, 'Fixed station coordinate is missing from simplified route: ' + stop['id'])
        new_stop_chainages.append(new_chain[vertex])
        next_vertex = vertex + 1
    for stop, chainage in zip(new_stops, new_stop_chainages):
        stop['chainage_m'] = chainage
        mapped = geometry.point(simplified, new_chain, chainage)
        require(abs(stop['lon'] - mapped[0]) <= 1e-10 and abs(stop['lat'] - mapped[1]) <= 1e-10,
                'Simplification moved a fixed station coordinate: ' + stop['id'])
    return simplified, new_chain, new_stops, dict(
        source_point_count=len(coordinates),
        interval_source_point_count=source_count,
        simplified_point_count=len(simplified),
        maximum_sampled_deviation_m=worst_deviation,
        source_route_m=baseline_chain[-1],
        simplified_route_m=new_chain[-1],
        route_length_change_m=new_chain[-1] - baseline_chain[-1],
        stop_coordinates_fixed=True,
        maximum_deviation_test_step_m=5.0,
    )


def make_scenario(city, tolerance_m, geometry, adapter):
    derived = deepcopy(city)
    line_by_id = {line['line_id']: line for line in derived['lines']}
    original_routes = {line['line_id']: line['route_m'] for line in city['lines']}
    detail = []
    for line in derived['lines']:
        original = next(row for row in city['lines'] if row['line_id'] == line['line_id'])
        old_chain = geometry.route(original['coordinates'], original['shape'])
        new_coords, new_chain, new_stops, metrics = simplify_line(original, tolerance_m, geometry, old_chain)
        legs = [dict(from_stop=a['id'], to_stop=b['id'], distance_m=b['chainage_m'] - a['chainage_m'], closing_leg=False)
                for a, b in zip(new_stops, new_stops[1:])]
        line.update(coordinates=new_coords, coordinate_chainages_m=new_chain, route_m=new_chain[-1],
                    stops=new_stops, legs=legs, operational_route_m=math.fsum(row['distance_m'] for row in legs),
                    unserved_radial_tail_m=new_chain[-1] - math.fsum(row['distance_m'] for row in legs),
                    parent_route_geometry_sha256=SHA(ENCODE(original['coordinates'])),
                    straightening_tolerance_m=tolerance_m,
                    route_geometry_screen_only=True)
        detail.append(dict(line_id=line['line_id'], **metrics,
                           source_station_ids=[stop['id'] for stop in original['stops']],
                           alternative_station_ids=[stop['id'] for stop in new_stops]))

    # The legacy civil classifications are proportionally mapped to the new
    # length by the source loader. Retain that assumption, but do not call it a
    # site reclassification or a civil verification.
    civil = []
    for row in city['civil_segments']:
        line_id = row['line_id']
        ratio = line_by_id[line_id]['route_m'] / original_routes[line_id]
        item = deepcopy(row)
        item['parent_from_m'] = row['from_m']
        item['parent_to_m'] = row['to_m']
        item['from_m'] = row['from_m'] * ratio
        item['to_m'] = row['to_m'] * ratio
        item['route_length_proportional_transfer'] = True
        civil.append(item)
    derived['civil_segments'] = civil
    derived['parent_city_input_id'] = city['input_id']
    derived['parent_planning_revision_sha256'] = city['planning_revision_sha256']
    derived['straightening_hypothesis'] = dict(
        schema='osr-samawah-stop-preserving-simplification/1',
        method='Douglas-Peucker per adjacent-stop interval; station coordinates retained as exact endpoints',
        tolerance_m=tolerance_m,
        metric_projection='local mean-latitude equirectangular; spherical Earth radius 6371008.8 m',
        sampled_deviation_step_m=5.0,
        station_coordinates_fixed=True,
        civil_classification='proportionally transferred from parent route length; requires site reassessment',
        selected=False,
        buildability_verified=False,
    )
    derived['input_id'] = IDENTITY({k: v for k, v in derived.items() if k != 'input_id'})
    result = adapter.evaluate(derived, BODY, POLICY, trusted_city_input_id=derived['input_id'], root=ROOT)
    adapter.verify(result)
    require(result['candidate_id'] != BASELINE['candidate_id'], 'Straightened physical candidate did not receive new identity')
    require(result['body_candidate_id'] == BASELINE['body_candidate_id'] and
            result['body_evaluation_id'] == BASELINE['body_evaluation_id'], 'Body identity changed')
    require(result['policy_id'] == BASELINE['policy_id'], 'Service policy changed')
    require(all(value is None for scope in result['scope_totals_usd'].values() for value in scope.values()),
            'Unpriced city cost scopes must remain null')
    for line in derived['lines']:
        chain = geometry.route(line['coordinates'], line['shape'])
        for stop in line['stops']:
            point = geometry.point(line['coordinates'], chain, stop['chainage_m'])
            require(abs(point[0] - stop['lon']) <= 1e-10 and abs(point[1] - stop['lat']) <= 1e-10,
                    'Output station coordinate no longer lies on candidate route')
    return derived, result, detail


try:
    from engineering.railway_project import city_recalculation as adapter
    from engineering.outline import city_inputs, planning_geometry

    bodyraw = checked('docs/design-engine/v06-design-closure/compact-drive-source-replay-01/compact-737-h100/body.json.gz')
    body = json.loads(gzip.decompress(bodyraw))
    BODY = body
    policyraw = checked(adapter.POLICY)
    POLICY = json.loads(policyraw)
    require(POLICY['acceleration_m_s2'] == 0.4, 'The named 0.4 m/s² study control changed')
    require(body['candidate_id'] == REQUEST['body_candidate_id'] and body['evaluation_id'] == REQUEST['body_evaluation_id'],
            'Exact current vehicle body identity required')
    context = city_inputs.prepare(root=ROOT)
    city = city_inputs.load('samawah', root=ROOT, context=context)
    for name, expected in city['source_sha256'].items():
        require(SHA(checked(name)) == expected, 'City input source hash mismatch: ' + name)
    require(city['input_id'] == REQUEST['city_input_id'], 'Exact current Samawah city source required')
    baseline = adapter.evaluate(city, body, POLICY, trusted_city_input_id=city['input_id'], root=ROOT)
    adapter.verify(baseline)
    require(baseline['evaluation_id'] == REQUEST['baseline_evaluation_id'], 'Current source city control did not reproduce')
    BASELINE = baseline
    (RUN / 'inputs').mkdir(exist_ok=True)
    (RUN / 'inputs' / 'body.json.gz').write_bytes(bodyraw)
    (RUN / 'inputs' / 'policy.json').write_bytes(policyraw)
    save('inputs/city.json', city)
    save('baseline.json', baseline)

    summaries = []
    for tolerance in REQUEST['maximum_deviation_tolerances_m']:
        derived, result, details = make_scenario(city, tolerance, planning_geometry, adapter)
        name = f"tolerance-{int(tolerance):03d}m"
        save(f'scenarios/{name}/derived-city.json', derived)
        save(f'scenarios/{name}/evaluation.json', result)
        save(f'scenarios/{name}/line-details.json', details)
        features = []
        for line in derived['lines']:
            features.append(dict(type='Feature', properties=dict(line_id=line['line_id'],
                tolerance_m=tolerance, route_m=line['route_m'], station_count=len(line['stops']),
                candidate_id=result['candidate_id'], evaluation_id=result['evaluation_id']),
                geometry=dict(type='LineString', coordinates=line['coordinates'])))
        save(f'scenarios/{name}/alignment.geojson', dict(type='FeatureCollection', features=features,
            properties=dict(crs='OGC:CRS84', tolerance_m=tolerance, selected=False)))
        original_points = sum(len(line['coordinates']) for line in city['lines'])
        new_points = sum(len(line['coordinates']) for line in derived['lines'])
        routes_by_id = {line['line_id']: line for line in result['lines']}
        summaries.append(dict(
            tolerance_m=tolerance,
            city_input_id=derived['input_id'],
            candidate_id=result['candidate_id'],
            evaluation_id=result['evaluation_id'],
            route_km=result['quantities']['route_m'] / 1000.0,
            geometry_points=new_points,
            source_geometry_points=original_points,
            point_reduction_percent=100.0 * (original_points - new_points) / original_points,
            station_markers=result['quantities']['station_markers'],
            fleet_low_base_high=[result['fleet_request_cases'][case]['total_trainsets'] for case in ('low', 'base', 'high')],
            line1_runtime_s=next(row['assumed_one_way_runtime_s'] for row in result['lines'] if row['line_id'] == 'line-1'),
            definition_failures=result['definition_failures'],
            line_runtime_by_id={line_id: row['assumed_one_way_runtime_s'] for line_id, row in routes_by_id.items()},
            max_deviation_m_by_line={row['line_id']: row['maximum_sampled_deviation_m'] for row in details},
            all_station_coordinates_fixed=all(row['stop_coordinates_fixed'] for row in details),
            all_cost_scopes_unknown=all(value is None for scope in result['scope_totals_usd'].values() for value in scope.values()),
            selected=False,
        ))

    base_lines = {row['line_id']: row for row in city['lines']}
    summary = dict(
        schema='osr-samawah-stop-preserving-straightening-summary/1',
        source_commit=COMMIT,
        city_input_id=city['input_id'],
        baseline_candidate_id=baseline['candidate_id'],
        baseline_evaluation_id=baseline['evaluation_id'],
        baseline=dict(
            candidate_id=baseline['candidate_id'], evaluation_id=baseline['evaluation_id'],
            city_input_id=city['input_id'], route_km=baseline['quantities']['route_m'] / 1000.0,
            geometry_points=sum(len(row['coordinates']) for row in city['lines']),
            station_markers=baseline['quantities']['station_markers'],
            fleet_low_base_high=[baseline['fleet_request_cases'][case]['total_trainsets'] for case in ('low', 'base', 'high')],
            line1_runtime_s=next(row['assumed_one_way_runtime_s'] for row in baseline['lines'] if row['line_id'] == 'line-1'),
        ),
        scenarios=summaries,
        source_station_counts={line_id: len(row['stops']) for line_id, row in base_lines.items()},
        physical_accepted=False, engineering_accepted=False, selected=False, gate_closed=False,
        limitations=[
            'No station coordinates are changed; all original markers are required to lie exactly on the source polyline and remain exact vertices of each simplified route.',
            'Tolerance uses a local mean-latitude equirectangular projection; every source path is sampled at 5 m intervals and checked against each simplified segment.',
            'OSM corridor, right-of-way, land, crossings, buildings, utilities, ground, accessible walks and construction feasibility are not verified.',
            'Civil classifications are proportionally remapped by route-length ratio only; actual site classes and civil loads are not re-evaluated.',
            'The current point-train runtime and fleet values are conditional study calculations; no available force, braking, curve, grade or protected timetable is demonstrated.',
            'All fourteen complete city cost scopes, installed CAPEX and whole-life NPV remain unknown.',
            'No native GIS, CAD, FEM, ERPNext or network client was invoked; source tree remained writable without an OS read-only sandbox.',
        ],
    )
    save('summary.json', summary)
    after = {name: SHA((ROOT / name).read_bytes()) for name in CONSUMED}
    require(after == CONSUMED, 'A consumed source/input changed during the calculation')
    save('source-integrity.json', dict(
        source_commit=COMMIT,
        consumed_source_sha256=CONSUMED,
        git_blob_records=[record for raw, record in READS.values()],
        project_imports=IMPORTS,
        consumed_source_count=len(CONSUMED),
        project_pyc_executed=False,
        bytecode_writes_disabled=sys.dont_write_bytecode,
        before_after_source_bytes_unchanged=True,
        isolation='Commit-authenticated source compilation with before/after observations; source filesystem writable; no OS read-only sandbox.',
    ))
    print(json.dumps(dict(baseline_evaluation_id=baseline['evaluation_id'],
        scenarios=[dict(tolerance_m=row['tolerance_m'],candidate_id=row['candidate_id'],
                        evaluation_id=row['evaluation_id'],route_km=row['route_km'],
                        point_reduction_percent=row['point_reduction_percent'],
                        fleet=row['fleet_low_base_high'],line1_runtime_s=row['line1_runtime_s']) for row in summaries],
        consumed_source_count=len(CONSUMED)), sort_keys=True))
except Exception as exc:
    save('failure.json', dict(stage='samawah-stop-preserving-straightening-worker',
        error=type(exc).__name__, message=str(exc), traceback=traceback.format_exc(),
        consumed_source_sha256=CONSUMED, physical_accepted=False, gate_closed=False))
    traceback.print_exc()
    sys.exit(1)
finally:
    reader.stdin.close()
    reader.wait()
