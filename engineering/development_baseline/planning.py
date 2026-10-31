"""Candidate-bound planning proposals from current city geography inputs."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import gzip
import json
import math
from pathlib import Path
import re
import tempfile
import zlib

from . import FLAGS, OUTPUT

PLANNING_ROOT = Path(OUTPUT) / 'planning'
CURRENT_CITY_INDEX = Path(OUTPUT) / 'cities.json'
CURRENT_CITY_RECEIPT = Path(OUTPUT) / 'city-catalogue-manifest.json'
SELECTION_SOURCE = Path('engineering/development-baseline.toml')
BRIEF_SOURCE = Path('engineering/station_rail/brief.toml')
SCHEMA = 'osr-v06-planning-handoff/1'
EDIT_SCHEMA = 'osr-planning-edit-bundle/1'
INPUT_SCHEMA = 'osr-current-planning-inputs/1'
BASE_SCHEMA = 'osr-owner-builder-plan/1'
DISPOSITIONS = {**FLAGS, 'movement_authority': False, 'procurement_released': False}
PLAN_DISPOSITIONS = ('design_complete', 'physical_validation', 'manufacturing_release',
    'physical_release', 'engineering_accepted', 'movement_authority', 'procurement_released')
EARTH_M = 6_371_008.8
MAX_BUNDLE_BYTES = 4 * 1024 * 1024
MAX_PLAN_BYTES = 64 * 1024 * 1024


class PlanningError(ValueError):
    """Invalid, stale, or incompatible planning input."""


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def digest_bytes(raw):
    return sha256(raw).hexdigest()


def digest_json(value):
    return digest_bytes(encoded(value))


def _safe_file(root, relative):
    root = Path(root).resolve()
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or any(part in ('', '.', '..') for part in rel.parts):
        raise PlanningError('Expected a repository-relative planning source')
    path = root / rel
    for parent in (path, *path.parents):
        if parent == root:
            break
        if parent.is_symlink():
            raise PlanningError('Symlinks are not planning evidence: ' + str(relative))
    if not path.resolve().is_relative_to(root) or not path.is_file():
        raise PlanningError('Planning evidence is missing or outside the repository: ' + str(relative))
    return path


def _relative_path(root, path):
    root = Path(root).resolve()
    path = Path(path)
    if path.is_absolute():
        try:
            path = path.relative_to(root)
        except ValueError as exc:
            raise PlanningError('Planning path must remain inside the repository') from exc
    if not path.parts or any(part in ('', '.', '..') for part in path.parts):
        raise PlanningError('Expected an ordinary repository-relative planning path')
    return path


def _safe_output_dir(root, path):
    root = Path(root).resolve()
    relative = _relative_path(root, path)
    target = root / relative
    for parent in (target, *target.parents):
        if parent == root:
            break
        if parent.is_symlink():
            raise PlanningError('Symlinks are not planning output paths: ' + str(path))
    if not target.resolve().is_relative_to(root):
        raise PlanningError('Planning output path escapes the repository')
    return target.resolve()


def _read_json(path, *, maximum=MAX_PLAN_BYTES):
    path = Path(path)
    if path.stat().st_size > maximum:
        raise PlanningError('Planning JSON exceeds its byte budget')
    try:
        return json.loads(path.read_bytes())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PlanningError('Invalid planning JSON: ' + str(path)) from exc


def _read_gzip_json(path):
    if Path(path).stat().st_size > MAX_PLAN_BYTES:
        raise PlanningError('Compressed planning base exceeds its byte budget')
    try:
        with gzip.open(path, 'rb') as source:
            raw = source.read(MAX_PLAN_BYTES + 1)
        if len(raw) > MAX_PLAN_BYTES:
            raise PlanningError('Inflated planning base exceeds its byte budget')
        return json.loads(raw)
    except (OSError, EOFError, UnicodeDecodeError, json.JSONDecodeError, zlib.error) as exc:
        raise PlanningError('Invalid compressed planning base') from exc


def _nearest_route_vertex(coordinates, chain, exact, point, source_chainage=None):
    key = tuple(point[:2])
    if key in exact:
        candidates = exact[key]
        index = min(candidates, key=lambda value: (
            abs(chain[value] - source_chainage) if source_chainage is not None else chain[value],
            value))
    else:
        index = min(range(len(coordinates)), key=lambda i: _distance(coordinates[i], point))
    snapped = coordinates[index][:2]
    offset = _distance(snapped, point)
    if offset > 100.:
        raise PlanningError('City stop is more than 100 m from its mapped route')
    return chain[index], snapped, offset


def _current_city_plan(root, city_row, baseline):
    root = Path(root).resolve()
    city = city_row['slug']
    city_rel = Path(city_row['geography_path'])
    city_path = _safe_file(root, city_rel)
    route_rel = Path(city_row['route_geography_path'])
    route_path = _safe_file(root, route_rel)
    geography = _read_json(city_path)
    route_geojson = _read_json(route_path, maximum=MAX_PLAN_BYTES)
    route_features = {}
    for feature in route_geojson.get('features', []):
        properties = feature.get('properties') or {}
        geometry = feature.get('geometry') or {}
        if properties.get('kind') == 'line' and geometry.get('type') == 'LineString':
            route_features[properties.get('name')] = geometry.get('coordinates', [])
    city_lines = {row.get('name'): row for row in geography.get('lines', [])}
    if not city_lines or set(city_lines) != set(route_features):
        raise PlanningError('Current city line definitions and route geometry differ')

    source_paths = {
        city_rel.as_posix(), route_rel.as_posix(), CURRENT_CITY_INDEX.as_posix(),
        CURRENT_CITY_RECEIPT.as_posix(), SELECTION_SOURCE.as_posix(), BRIEF_SOURCE.as_posix(),
        'engineering/development_baseline/planning.py',
    }
    source_hashes = {name: digest_bytes(_safe_file(root, name).read_bytes())
                     for name in sorted(source_paths)}
    service = baseline['selection']['service']
    stations_by_line = {}
    for station in geography.get('stations', []):
        stations_by_line.setdefault(station.get('line'), []).append(station)

    lines = []
    for line_id in sorted(city_lines):
        coordinates = [point[:2] for point in route_features[line_id]]
        if not 2 <= len(coordinates) <= 100_000:
            raise PlanningError('Current route geometry has an invalid point count')
        chain = _chainages(coordinates)
        exact = {}
        for index, value in enumerate(coordinates):
            exact.setdefault(tuple(value[:2]), []).append(index)
        length = chain[-1]
        if not math.isfinite(length) or length < 1.:
            raise PlanningError('Current route geometry has no measurable length')
        stops = []
        for source in stations_by_line.get(line_id, []):
            chainage, location, offset = _nearest_route_vertex(
                coordinates, chain, exact, [source['lon'], source['lat']], source.get('s_m'))
            stops.append(dict(id=source['id'], chainage_m=chainage,
                lon=location[0], lat=location[1], dwell_s=service['dwell_s'],
                source_location_offset_m=offset,
                access_and_transfer_reassessment_required=True))
        stops.sort(key=lambda row: (row['chainage_m'], row['id']))
        if len(stops) < 2:
            raise PlanningError('Each current route needs at least two mapped stops')
        lines.append(dict(id=line_id, coordinates=coordinates, length_m=length,
            headway_s=service['headway_s'], planning_minimum_headway_s=service['headway_s'],
            stops=stops))

    interchanges = []
    for row in geography.get('interchanges', []):
        interchanges.append(dict(id=str(row['id']), lon=float(row['lon']), lat=float(row['lat']),
            lines=sorted(str(value) for value in row.get('lines', [])),
            reassessment_required=True))
    plan = dict(schema=BASE_SCHEMA, environment='planning', city=city, revision=0,
        selection_id=baseline['selection_id'], source_sha256=source_hashes,
        geography_basis='Current city routes, station coordinates and transfer locations; no candidate performance or cost results.',
        lines=lines, interchanges=interchanges, od=[],
        **{key: False for key in PLAN_DISPOSITIONS})
    plan['revision_sha256'] = digest_json(plan)
    return _validate_plan(plan, city)


def _planning_package(root):
    """Build the deterministic current planning inputs and their source receipt."""
    from . import selection
    from engineering.station_rail import cities

    root = Path(root).resolve()
    baseline = selection.load(root)
    catalogue = cities.read_catalogue(root)
    if catalogue.get('selection_id') != baseline['selection_id']:
        raise PlanningError('City geography register and selected candidate differ')
    city_receipt = _read_json(_safe_file(root, CURRENT_CITY_RECEIPT))
    if city_receipt.get('files_sha256', {}).get(CURRENT_CITY_INDEX.as_posix()) != digest_bytes(
            _safe_file(root, CURRENT_CITY_INDEX).read_bytes()):
        raise PlanningError('Current city geography register differs from its receipt')
    city_rows = []
    files = {}
    sources = {CURRENT_CITY_INDEX.as_posix(): digest_bytes(_safe_file(root, CURRENT_CITY_INDEX).read_bytes()),
        CURRENT_CITY_RECEIPT.as_posix(): digest_bytes(_safe_file(root, CURRENT_CITY_RECEIPT).read_bytes()),
        SELECTION_SOURCE.as_posix(): digest_bytes(_safe_file(root, SELECTION_SOURCE).read_bytes()),
        BRIEF_SOURCE.as_posix(): digest_bytes(_safe_file(root, BRIEF_SOURCE).read_bytes()),
        'engineering/development_baseline/planning.py': digest_bytes(Path(__file__).read_bytes())}
    for row in catalogue.get('cities', []):
        plan = _current_city_plan(root, row, baseline)
        relative = f"cities/{row['slug']}.json.gz"
        raw = gzip.compress(encoded(plan), mtime=0)
        files[relative] = raw
        sources.update(plan['source_sha256'])
        city_rows.append(dict(city=row['slug'], label=row['name'], country=row['country'], plan=relative,
            revision_sha256=plan['revision_sha256'],
            route_geography_path=str(Path(row['path']) / (row['slug'] + '.corridor.geojson'))))
    city_rows.sort(key=lambda row: row['city'])
    candidate_ids = ('candidate_id', 'body_candidate_id', 'support_component_id', 'propulsion_component_id')
    index = dict(schema=INPUT_SCHEMA, selection_id=baseline['selection_id'],
        selected_candidate={key: baseline['vehicle'][key] for key in candidate_ids},
        service_proposal=dict(headway_s=baseline['selection']['service']['headway_s'],
            dwell_s=baseline['selection']['service']['dwell_s'], source='selected v0.6 development baseline'),
        city_count=len(city_rows), cities=city_rows, source_sha256=dict(sorted(sources.items())),
        **{key: False for key in FLAGS})
    files['index.json'] = encoded(index)
    package_manifest = dict(schema=INPUT_SCHEMA, selection_id=baseline['selection_id'],
        selected_candidate=index['selected_candidate'], source_sha256=dict(sorted(sources.items())),
        files_sha256={name: digest_bytes(raw) for name, raw in sorted(files.items())},
        **{key: False for key in FLAGS})
    files['manifest.json'] = encoded(package_manifest)
    return files, package_manifest


def publish_inputs(root):
    """Publish geography-only planning bases under the selected current packet."""
    root = Path(root).resolve()
    files, manifest = _planning_package(root)
    output = root / PLANNING_ROOT
    output.mkdir(parents=True, exist_ok=True)
    expected = set(files)
    for old in output.rglob('*'):
        if old.is_file() and old.relative_to(output).as_posix() not in expected:
            old.unlink()
    for name, raw in files.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return dict(published=True, city_count=len(json.loads(files['index.json'])['cities']),
        manifest_id=digest_bytes(files['manifest.json']), **{key: False for key in FLAGS})


def verify_inputs(root):
    """Recreate and compare every current planning input byte and source digest."""
    root = Path(root).resolve()
    files, _ = _planning_package(root)
    output = root / PLANNING_ROOT
    actual = {path.relative_to(output).as_posix() for path in output.rglob('*') if path.is_file()}
    if actual != set(files):
        raise PlanningError('Current planning input inventory differs')
    for name, expected in files.items():
        if (output / name).read_bytes() != expected:
            raise PlanningError('Current planning input differs: ' + name)
    return dict(verified=True, city_count=len(json.loads(files['index.json'])['cities']),
        source_and_payload_integrity=True, **{key: False for key in FLAGS})


def _distance(first, last):
    lon1, lat1 = first[:2]
    lon2, lat2 = last[:2]
    x1, x2 = math.radians(lat1), math.radians(lat2)
    h = math.sin((x2 - x1) / 2) ** 2 + math.cos(x1) * math.cos(x2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * EARTH_M * math.atan2(math.sqrt(max(0., h)), math.sqrt(max(0., 1 - h)))


def _finite(value, name, low, high):
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
        raise PlanningError('Bounded finite ' + name + ' required')
    return float(value)


def _chainages(points):
    result = [0.]
    for first, last in zip(points, points[1:]):
        result.append(result[-1] + _distance(first, last))
    return result


def _point_at(points, chainage):
    chain = _chainages(points)
    value = _finite(chainage, 'station chainage', 0., chain[-1])
    for index, (start, end) in enumerate(zip(chain, chain[1:])):
        if value <= end or index == len(chain) - 2:
            fraction = (value - start) / (end - start) if end > start else 0.
            return [points[index][i] + fraction * (points[index + 1][i] - points[index][i]) for i in range(2)]
    raise PlanningError('Station chainage is outside its route')


def _validate_plan(plan, expected_city=None):
    if not isinstance(plan, dict) or plan.get('schema') != 'osr-owner-builder-plan/1' or plan.get('environment') != 'planning':
        raise PlanningError('A current planning-only city revision is required')
    if expected_city is not None and plan.get('city') != expected_city:
        raise PlanningError('Planning city identity differs')
    if plan.get('revision_sha256') != digest_json({k: v for k, v in plan.items() if k != 'revision_sha256'}):
        raise PlanningError('Planning base revision digest differs')
    if any(plan.get(key) is not False for key in PLAN_DISPOSITIONS):
        raise PlanningError('Current planning input has an unexpected release disposition')
    if not isinstance(plan.get('source_sha256'), dict) or not plan['source_sha256']:
        raise PlanningError('Source-bound planning geography is required')
    if not isinstance(plan.get('lines'), list) or not plan['lines']:
        raise PlanningError('At least one mapped route is required')
    seen_lines, seen_stops = set(), set()
    for line in plan['lines']:
        if not isinstance(line, dict) or not isinstance(line.get('id'), str) or line['id'] in seen_lines:
            raise PlanningError('Unique planning line identities required')
        seen_lines.add(line['id'])
        points = line.get('coordinates')
        if not isinstance(points, list) or not 2 <= len(points) <= 100_000:
            raise PlanningError('Bounded mapped route coordinates required')
        for point in points:
            if not isinstance(point, list) or len(point) < 2:
                raise PlanningError('Longitude/latitude route points required')
            _finite(point[0], 'longitude', -180., 180.)
            _finite(point[1], 'latitude', -90., 90.)
        length = math.fsum(_distance(a, b) for a, b in zip(points, points[1:]))
        declared = _finite(line.get('length_m'), 'route length', 1., 1_000_000.)
        if not math.isclose(length, declared, abs_tol=.01):
            raise PlanningError('Mapped route length differs from its planning record')
        _finite(line.get('headway_s'), 'proposed headway', 10., 86_400.)
        stops = line.get('stops')
        if not isinstance(stops, list) or len(stops) > 10_000:
            raise PlanningError('Bounded proposed station list required')
        previous = -1.
        for stop in stops:
            if not isinstance(stop, dict) or not isinstance(stop.get('id'), str) or not stop['id'] or stop['id'] in seen_stops:
                raise PlanningError('Unique planning stop identities required')
            seen_stops.add(stop['id'])
            chainage = _finite(stop.get('chainage_m'), 'station chainage', 0., declared)
            if chainage <= previous:
                raise PlanningError('Stations must remain in route order')
            previous = chainage
            _finite(stop.get('dwell_s'), 'proposed dwell', 10., 3_600.)
            lon = _finite(stop.get('lon'), 'station longitude', -180., 180.)
            lat = _finite(stop.get('lat'), 'station latitude', -90., 90.)
            if _distance(_point_at(points, chainage), [lon, lat]) > .02:
                raise PlanningError('Proposed station is off its mapped alignment')
    if not isinstance(plan.get('od'), list) or len(plan['od']) > 100_000:
        raise PlanningError('Bounded origin/destination proposal required')
    seen_pairs = set()
    for row in plan['od']:
        if not isinstance(row, dict):
            raise PlanningError('Origin/destination proposal rows must be objects')
        pair = (row.get('origin'), row.get('destination'))
        if (not isinstance(pair[0], str) or not isinstance(pair[1], str)
                or pair[0] not in seen_stops or pair[1] not in seen_stops
                or pair[0] == pair[1] or pair in seen_pairs):
            raise PlanningError('Unique origin/destination references to proposed stops required')
        seen_pairs.add(pair)
        _finite(row.get('trips_per_day'), 'daily trips', 0., 100_000_000.)
        if row.get('basis') not in {'synthetic', 'observed-unaccepted'}:
            raise PlanningError('Explicit unaccepted demand provenance required')
    return plan


def _load_base(root, city):
    root = Path(root).resolve()
    package_manifest_rel = PLANNING_ROOT / 'manifest.json'
    package_index_rel = PLANNING_ROOT / 'index.json'
    current_manifest_rel = Path(OUTPUT) / 'manifest.json'
    package_manifest_path = _safe_file(root, package_manifest_rel)
    package_index_path = _safe_file(root, package_index_rel)
    current_manifest = _read_json(_safe_file(root, current_manifest_rel))
    manifest = _read_json(package_manifest_path)
    if (manifest.get('schema') != INPUT_SCHEMA
            or any(manifest.get(key) is not False for key in FLAGS)):
        raise PlanningError('Current planning input publication has an unexpected identity or release state')
    current_files = current_manifest.get('files_sha256', {})
    package_relative = package_manifest_rel.relative_to(OUTPUT).as_posix()
    if current_files.get(package_relative) != digest_bytes(package_manifest_path.read_bytes()):
        raise PlanningError('Current engineering publication does not bind the planning inputs')
    index_hash = manifest.get('files_sha256', {}).get('index.json')
    if not isinstance(index_hash, str) or digest_bytes(package_index_path.read_bytes()) != index_hash:
        raise PlanningError('Current planning index differs from its publication receipt')
    index = _read_json(package_index_path)
    from . import selection
    baseline = selection.load(root)
    if index.get('selection_id') != baseline['selection_id']:
        raise PlanningError('Current planning index belongs to a different candidate selection')
    rows = [row for row in index.get('cities', []) if row.get('city') == city]
    if len(rows) != 1:
        raise PlanningError('Unique current city geography packet required')
    plan_rel = PLANNING_ROOT / rows[0]['plan']
    if not plan_rel.is_relative_to(PLANNING_ROOT):
        raise PlanningError('Planning base path escapes its publication')
    plan_path = _safe_file(root, plan_rel)
    expected = manifest.get('files_sha256', {}).get(rows[0]['plan'])
    if not isinstance(expected, str) or digest_bytes(plan_path.read_bytes()) != expected:
        raise PlanningError('Current city geography packet differs from its receipt')
    plan = _read_gzip_json(plan_path)
    _validate_plan(plan, city)
    sources = dict(plan['source_sha256'])
    sources[package_manifest_rel.as_posix()] = digest_bytes(package_manifest_path.read_bytes())
    sources[package_index_rel.as_posix()] = digest_bytes(package_index_path.read_bytes())
    sources[plan_rel.as_posix()] = digest_bytes(plan_path.read_bytes())
    sources[current_manifest_rel.as_posix()] = digest_bytes(_safe_file(root, current_manifest_rel).read_bytes())
    for relative, expected_source in plan['source_sha256'].items():
        if not re.fullmatch(r'[0-9a-f]{64}', str(expected_source)):
            raise PlanningError('Invalid current geography source digest')
        path = _safe_file(root, relative)
        if digest_bytes(path.read_bytes()) != expected_source:
            raise PlanningError('Current planning source changed: ' + relative)
    return plan, sources


def _apply_edits(plan, edits, actor):
    if not isinstance(actor, str) or not actor.strip() or len(actor) > 150:
        raise PlanningError('Named planning author required')
    if not isinstance(edits, list) or not 1 <= len(edits) <= 1_000:
        raise PlanningError('Bounded nonempty edit list required')
    revised = deepcopy(plan)
    lines = {line['id']: line for line in revised['lines']}
    proposed_stop_ids = set()
    for edit in edits:
        if not isinstance(edit, dict):
            raise PlanningError('Typed planning edit required')
        kind = edit.get('kind')
        expected_keys = {'set-od': {'kind', 'rows'}, 'add-stop': {'kind', 'line', 'stop', 'chainage_m', 'dwell_s'},
            'move-stop': {'kind', 'line', 'stop', 'chainage_m'}, 'retire-stop': {'kind', 'line', 'stop'},
            'set-service': {'kind', 'line', 'headway_s', 'dwell_s'}, 'straighten-line': {'kind', 'line'}}.get(kind)
        if expected_keys is None or set(edit) != expected_keys:
            raise PlanningError('Planning edit fields differ from the supported proposal schema')
        if kind == 'set-od':
            revised['od'] = deepcopy(edit.get('rows'))
            continue
        line = lines.get(edit.get('line'))
        if line is None:
            raise PlanningError('Unknown planning line')
        if kind == 'add-stop':
            stop_id = edit.get('stop')
            if not isinstance(stop_id, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,80}', stop_id):
                raise PlanningError('Bounded lowercase proposed stop identity required')
            if (stop_id in proposed_stop_ids or
                    any(stop_id == stop['id'] for item in revised['lines'] for stop in item['stops'])):
                raise PlanningError('Proposed stop identity already exists')
            proposed_stop_ids.add(stop_id)
            chainage = _finite(edit.get('chainage_m'), 'station chainage', 0., line['length_m'])
            if not 0. < chainage < line['length_m']:
                raise PlanningError('New station must lie inside the route endpoints')
            dwell = _finite(edit.get('dwell_s'), 'proposed dwell', 10., 3_600.)
            lon, lat = _point_at(line['coordinates'], chainage)
            line['stops'].append(dict(id=stop_id, chainage_m=chainage, lon=lon, lat=lat,
                dwell_s=dwell, access_and_transfer_reassessment_required=True))
            line['stops'].sort(key=lambda stop: stop['chainage_m'])
        elif kind == 'move-stop':
            stop = next((row for row in line['stops'] if row['id'] == edit.get('stop')), None)
            if stop is None:
                raise PlanningError('Unknown planning stop')
            stop['chainage_m'] = _finite(edit.get('chainage_m'), 'station chainage', 0., line['length_m'])
            stop['lon'], stop['lat'] = _point_at(line['coordinates'], stop['chainage_m'])
            stop['access_and_transfer_reassessment_required'] = True
        elif kind == 'retire-stop':
            stop_id = edit.get('stop')
            if not any(row['id'] == stop_id for row in line['stops']):
                raise PlanningError('Unknown planning stop')
            if len(line['stops']) <= 2:
                raise PlanningError('At least two proposed stations must remain on a line')
            if any(row.get('origin') == stop_id or row.get('destination') == stop_id for row in revised.get('od', [])):
                raise PlanningError('Remove or revise OD rows before retiring a station')
            line['stops'] = [row for row in line['stops'] if row['id'] != stop_id]
        elif kind == 'set-service':
            line['headway_s'] = _finite(edit.get('headway_s'), 'proposed headway', 10., 86_400.)
            dwell = _finite(edit.get('dwell_s'), 'proposed dwell', 10., 3_600.)
            for stop in line['stops']:
                stop['dwell_s'] = dwell
        elif kind == 'straighten-line':
            old_length = line['length_m']
            line['coordinates'] = [line['coordinates'][0], line['coordinates'][-1]]
            line['length_m'] = _distance(*line['coordinates'])
            if line['length_m'] < 1.:
                raise PlanningError('Straightened alignment is too short')
            for stop in line['stops']:
                stop['chainage_m'] *= line['length_m'] / old_length
                stop['lon'], stop['lat'] = _point_at(line['coordinates'], stop['chainage_m'])
                stop['access_and_transfer_reassessment_required'] = True
        else:
            raise PlanningError('Unknown planning edit kind')
    revised.update(revision=plan['revision'] + 1,
                   parent_revision_sha256=plan['revision_sha256'], actor=actor.strip(),
                   changes=deepcopy(edits),
                   requires_reassessment=['geography/access/demand', 'station spacing and transfer access',
                       'v0.6 vehicle, propulsion and braking', 'civil geometry and site conditions',
                       'candidate-specific BOM, procurement and manufacturing', 'cost and construction schedule'])
    revised.pop('revision_sha256', None)
    revised['revision_sha256'] = digest_json(revised)
    return _validate_plan(revised, plan['city'])


def _handoff_network(plan):
    """Keep the handoff to route, stop, service, transfer and OD proposals."""
    return dict(city=plan['city'], lines=[dict(id=line['id'], coordinates=deepcopy(line['coordinates']),
        route_length_m=line['length_m'], proposed_headway_s=line['headway_s'],
        stations=[dict(id=stop['id'], chainage_m=stop['chainage_m'], lon=stop['lon'], lat=stop['lat'],
            proposed_dwell_s=stop['dwell_s'], access_and_transfer_reassessment_required=bool(
                stop.get('access_and_transfer_reassessment_required', False))) for stop in line['stops']])
        for line in plan['lines']],
        source_interchange_references=[dict(record=deepcopy(row), state='reassessment-required')
            for row in plan.get('interchanges', [])],
        access_and_transfer_evaluation='pending', service_evaluation='pending',
        origin_destination=deepcopy(plan.get('od', [])))


def compile_bundle(*, root, baseline, current_summary, current_manifest, bundle_path, output_path):
    """Compile a planning-only handoff bound to the exact current selection."""
    root = Path(root).resolve()
    bundle_path = _safe_file(root, _relative_path(root, bundle_path))
    output_path = _safe_output_dir(root, output_path)
    if bundle_path.stat().st_size > MAX_BUNDLE_BYTES:
        raise PlanningError('Edit bundle exceeds its byte budget')
    bundle_raw = bundle_path.read_bytes()
    try:
        value = json.loads(bundle_raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PlanningError('Invalid planning edit bundle') from exc
    if not isinstance(value, dict) or set(value) != {'schema', 'city', 'base_revision_sha256', 'actor', 'edits'} or value.get('schema') != EDIT_SCHEMA:
        raise PlanningError('Typed planning edit bundle required')
    city = value.get('city')
    if not isinstance(city, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,80}', city):
        raise PlanningError('Bounded city identity required')
    original, source_hashes = _load_base(root, city)
    if value.get('base_revision_sha256') != original['revision_sha256']:
        raise PlanningError('Stale planning base revision; reload and review before compiling')
    revised = _apply_edits(original, value['edits'], value['actor'])

    candidate_ids = ('candidate_id', 'body_candidate_id', 'support_component_id', 'propulsion_component_id')
    selected_vehicle = baseline['vehicle']
    if current_summary.get('selection_id') != baseline['selection_id']:
        raise PlanningError('Current published engineering packet and selector differ')
    if not re.fullmatch(r'[0-9a-f]{64}', str(current_summary.get('evaluation_id', ''))):
        raise PlanningError('Source-bound current engineering evaluation required')
    publication_path = _safe_file(root, 'docs/design-engine/current/manifest.json')
    publication_raw = publication_path.read_bytes()
    if _read_json(publication_path) != current_manifest:
        raise PlanningError('Current publication receipt changed during planning compilation')
    identities = {key: selected_vehicle[key] for key in candidate_ids}
    network = _handoff_network(revised)
    network_proposal_id = digest_json(dict(city=city, network=network))
    planning_identity = dict(schema=SCHEMA, selection_id=baseline['selection_id'],
        selected_candidate=identities, selected_for_development=False,
        city=city, revision_number=revised['revision'], parent_planning_revision_sha256=original['revision_sha256'],
        parent_network_proposal_id=baseline['selection'].get('network_proposal_id'),
        network_proposal_id=network_proposal_id,
        network=network, actor=value['actor'].strip(), edits=deepcopy(value['edits']),
        source_sha256=source_hashes)
    revision_id = digest_json(planning_identity)
    planning_identity['planning_revision_id'] = revision_id
    evaluation_basis = dict(selection_id=baseline['selection_id'], candidate=identities,
        v06_evaluation_id=current_summary.get('evaluation_id'), network_proposal_id=network_proposal_id)
    evaluation_id = digest_json(evaluation_basis)
    payload = dict(schema=SCHEMA, execution='completed-proposal-handoff', evaluation_id=evaluation_id,
        selection_id=baseline['selection_id'], physical_candidate=identities,
        network_proposal_id=network_proposal_id,
        base_candidate_evaluation_id=current_summary.get('evaluation_id'),
        planning_revision=planning_identity, selected=False,
        origin='Current city route and stop geography with selected v0.6 service values treated as proposals',
        engineering_evaluation='held', route_performance_evaluated=False, city_performance_published=False,
        complete_cost_known=False,
        procurement_requirements=dict(state='not-evaluated', known_rows=[], quantities_unknown=True,
            cost_usd=None, complete_cost_known=False),
        required_followups=[
            dict(id='route-and-access', state='pending', scope='Survey, walking access, transfers, utilities, terrain and accessibility'),
            dict(id='service-and-fleet', state='pending', scope='Equal-service timetable, capacity, fleet and headway for v0.6'),
            dict(id='vehicle-and-propulsion', state='pending', scope='Available station-LIM force map, full journey, repeated duty and recovery'),
            dict(id='braking-and-protection', state='pending', scope='Independent brake/WSP maps, stopping, fault response and protected headway'),
            dict(id='civil-and-site', state='pending', scope='Route loads, repeatable span, foundations, erection and site evidence'),
            dict(id='procurement-and-cost', state='pending', scope='Candidate-specific purchasing units, local rates, supplier quotes and installed quantities'),
            dict(id='delivery-and-operations', state='pending', scope='Construction schedule, ERP assets, measured commissioning and maintenance records')],
        service_policy='Headway and dwell are proposal defaults from the selected v0.6 development baseline; no service performance is calculated',
        cost_policy='No candidate procurement quantities, installed costs or cashflow are carried into this handoff',
        **DISPOSITIONS)
    files = {'edit-bundle.json': bundle_raw,
             'planning-revision.json': encoded(planning_identity),
             'planning-handoff.json': encoded(payload),
             'issues.json': encoded(dict(schema=SCHEMA, city=city,
                 state='engineering-reassessment-required', issues=payload['required_followups'], **DISPOSITIONS))}
    if output_path == root or root not in output_path.parents:
        raise PlanningError('Output must be a repository-relative subdirectory')
    if output_path.exists():
        raise PlanningError('Planning output path already exists; choose a new revision directory')
    parent = output_path.parent
    parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.osr-plan-', dir=parent))
    try:
        for name, raw in files.items():
            (stage / name).write_bytes(raw)
        source_bindings = {**source_hashes,
            'engineering/development_baseline/planning.py': digest_bytes(Path(__file__).read_bytes()),
            'engineering/development_baseline/entrypoint.py': digest_bytes((root/'engineering/development_baseline/entrypoint.py').read_bytes()),
            'engineering/development-baseline.toml': digest_bytes((root/'engineering/development-baseline.toml').read_bytes()),
            'docs/workbench/planning/index.html': digest_bytes((root/'docs/workbench/planning/index.html').read_bytes()),
            'docs/workbench/planning/planning.js': digest_bytes((root/'docs/workbench/planning/planning.js').read_bytes()),
            'docs/design-engine/current/manifest.json': digest_bytes(publication_raw)}
        for relative, expected in source_bindings.items():
            if digest_bytes(_safe_file(root, relative).read_bytes()) != expected:
                raise PlanningError('Planning source changed during compilation: ' + relative)
        manifest = dict(schema=SCHEMA, planning_revision_id=revision_id, evaluation_id=evaluation_id,
            selection_id=baseline['selection_id'], physical_candidate=identities,
            network_proposal_id=network_proposal_id,
            edit_bundle_source_path=bundle_path.relative_to(root).as_posix(),
            edit_bundle_sha256=digest_bytes(bundle_raw),
            source_sha256=source_bindings,
            files_sha256={name: digest_bytes(raw) for name, raw in files.items()},
            **DISPOSITIONS)
        (stage / 'manifest.json').write_bytes(encoded(manifest))
        stage.rename(output_path)
    except BaseException:
        import shutil
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return manifest


def verify_handoff(output_path, *, root, baseline, current_summary):
    """Verify the handoff bytes, sources, identities, and held dispositions."""
    root = Path(root).resolve()
    output_path = _safe_output_dir(root, output_path)
    if not output_path.is_dir():
        raise PlanningError('Repository-owned planning handoff directory required')
    manifest_path = _safe_file(root, output_path.relative_to(root) / 'manifest.json')
    manifest = _read_json(manifest_path)
    if manifest.get('schema') != SCHEMA or any(manifest.get(key) is not False for key in DISPOSITIONS):
        raise PlanningError('Planning handoff schema or release disposition differs')
    if manifest.get('selection_id') != baseline['selection_id'] or current_summary.get('selection_id') != baseline['selection_id']:
        raise PlanningError('Planning handoff belongs to a different selection')
    vehicle = baseline['vehicle']
    expected_candidate = {key: vehicle[key] for key in ('candidate_id', 'body_candidate_id', 'support_component_id', 'propulsion_component_id')}
    if manifest.get('physical_candidate') != expected_candidate:
        raise PlanningError('Planning handoff uses a different physical candidate')
    expected_files = {'edit-bundle.json', 'planning-revision.json', 'planning-handoff.json', 'issues.json'}
    actual_files = {path.relative_to(output_path).as_posix() for path in output_path.rglob('*') if path.is_file()}
    if actual_files != expected_files | {'manifest.json'} or any(path.is_symlink() for path in output_path.rglob('*')):
        raise PlanningError('Planning handoff inventory differs')
    if set(manifest.get('files_sha256', {})) != expected_files:
        raise PlanningError('Planning handoff output inventory differs from its receipt')
    files = {}
    for name, expected in manifest['files_sha256'].items():
        path = _safe_file(root, output_path.relative_to(root) / name)
        raw = path.read_bytes()
        if digest_bytes(raw) != expected:
            raise PlanningError('Planning handoff output changed: ' + name)
        files[name] = json.loads(raw)
    source_hashes = manifest.get('source_sha256')
    if not isinstance(source_hashes, dict) or not source_hashes:
        raise PlanningError('Planning handoff has no source bindings')
    for relative, expected in source_hashes.items():
        if not re.fullmatch(r'[0-9a-f]{64}', str(expected)) or digest_bytes(_safe_file(root, relative).read_bytes()) != expected:
            raise PlanningError('Planning handoff source changed: ' + relative)
    revision = files['planning-revision.json']
    handoff = files['planning-handoff.json']
    bundle_raw = output_path.joinpath('edit-bundle.json').read_bytes()
    if digest_bytes(bundle_raw) != manifest.get('edit_bundle_sha256'):
        raise PlanningError('Planning handoff edit bundle differs')
    bundle = _read_json(output_path / 'edit-bundle.json', maximum=MAX_BUNDLE_BYTES)
    base_plan, base_sources = _load_base(root, revision.get('city'))
    if (bundle.get('schema') != EDIT_SCHEMA
            or bundle.get('base_revision_sha256') != base_plan.get('revision_sha256')
            or revision.get('parent_planning_revision_sha256') != base_plan.get('revision_sha256')
            or revision.get('revision_number') != base_plan.get('revision', 0) + 1
            or revision.get('actor') != str(bundle.get('actor', '')).strip()
            or revision.get('edits') != bundle.get('edits')
            or revision.get('source_sha256') != base_sources):
        raise PlanningError('Planning revision no longer matches its base and edit bundle')
    for relative, expected in base_sources.items():
        if source_hashes.get(relative) != expected:
            raise PlanningError('Planning handoff base source differs: ' + relative)
    if _handoff_network(_apply_edits(base_plan, bundle['edits'], bundle['actor'])) != revision.get('network'):
        raise PlanningError('Planning handoff geometry differs from its edit bundle')
    if (handoff.get('schema') != SCHEMA or handoff.get('execution') != 'completed-proposal-handoff'
            or handoff.get('selected') is not False or handoff.get('engineering_evaluation') != 'held'
            or handoff.get('route_performance_evaluated') is not False
            or handoff.get('city_performance_published') is not False
            or handoff.get('procurement_requirements') != dict(state='not-evaluated', known_rows=[],
                quantities_unknown=True, cost_usd=None, complete_cost_known=False)
            or handoff.get('complete_cost_known') is not False
            or any(handoff.get(key) is not False for key in DISPOSITIONS)):
        raise PlanningError('Planning handoff contains an unsupported result or release claim')
    identity = {key: value for key, value in revision.items() if key != 'planning_revision_id'}
    revision_id = digest_json(identity)
    if (revision.get('planning_revision_id') != revision_id or manifest.get('planning_revision_id') != revision_id
            or handoff.get('planning_revision') != revision or handoff.get('selection_id') != baseline['selection_id']
            or handoff.get('physical_candidate') != expected_candidate
            or revision.get('selection_id') != baseline['selection_id']
            or revision.get('selected_candidate') != expected_candidate
            or revision.get('selected_for_development') is not False
            or handoff.get('base_candidate_evaluation_id') != current_summary.get('evaluation_id')):
        raise PlanningError('Planning revision identities differ')
    if revision.get('city') != handoff.get('planning_revision', {}).get('city'):
        raise PlanningError('Planning city identity differs')
    evaluation_basis = dict(selection_id=baseline['selection_id'], candidate=expected_candidate,
        v06_evaluation_id=current_summary.get('evaluation_id'), network_proposal_id=revision.get('network_proposal_id'))
    evaluation_id = digest_json(evaluation_basis)
    network_proposal_id = digest_json(dict(city=revision.get('city'), network=revision.get('network')))
    if (revision.get('network_proposal_id') != network_proposal_id
            or manifest.get('network_proposal_id') != network_proposal_id
            or handoff.get('network_proposal_id') != network_proposal_id
            or manifest.get('evaluation_id') != evaluation_id or handoff.get('evaluation_id') != evaluation_id):
        raise PlanningError('Planning evaluation identity differs')
    return dict(verified=True, planning_revision_id=revision_id, evaluation_id=evaluation_id,
        selection_id=baseline['selection_id'], physical_candidate=expected_candidate,
        network_proposal_id=network_proposal_id,
        route_performance_evaluated=False, complete_cost_known=False, **DISPOSITIONS)

