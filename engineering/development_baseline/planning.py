"""Candidate-bound GIS proposal handoff for the selected v0.6 train.

The editable map still starts from a retained historical city plan. This adapter
uses that packet only for geography, stops, and an explicitly unaccepted service
proposal. It does not import its vehicle, propulsion, civil quantities, costs, or
performance into the v0.6 candidate.
"""
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

from . import FLAGS

PLANNING_ROOT = Path('docs/design-engine/ferrite-maglev/planning-platform')
SCHEMA = 'osr-v06-planning-handoff/1'
EDIT_SCHEMA = 'osr-planning-edit-bundle/1'
DISPOSITIONS = {**FLAGS, 'movement_authority': False, 'procurement_released': False}
RETAINED_PLAN_DISPOSITIONS = ('design_complete', 'physical_validation', 'manufacturing_release',
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
        raise PlanningError('A retained planning-only city revision is required')
    if expected_city is not None and plan.get('city') != expected_city:
        raise PlanningError('Planning city identity differs')
    if plan.get('revision_sha256') != digest_json({k: v for k, v in plan.items() if k != 'revision_sha256'}):
        raise PlanningError('Planning base revision digest differs')
    if any(plan.get(key) is not False for key in RETAINED_PLAN_DISPOSITIONS):
        raise PlanningError('Historical planning packet has an unexpected release disposition')
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
    manifest_rel = PLANNING_ROOT / 'manifest.json'
    index_rel = PLANNING_ROOT / 'index.json'
    manifest_path = _safe_file(root, manifest_rel)
    index_path = _safe_file(root, index_rel)
    manifest = _read_json(manifest_path)
    if manifest.get('schema') != 'osr-owner-builder-publication/1' or any(manifest.get(key) is not False for key in RETAINED_PLAN_DISPOSITIONS):
        raise PlanningError('Retained planning publication has an unexpected identity or release state')
    index_hash = manifest.get('files_sha256', {}).get('index.json')
    if not isinstance(index_hash, str) or digest_bytes(index_path.read_bytes()) != index_hash:
        raise PlanningError('Retained planning index differs from its publication receipt')
    index = _read_json(index_path)
    rows = [row for row in index.get('cities', []) if row.get('city') == city]
    if len(rows) != 1:
        raise PlanningError('Unique retained city planning packet required')
    plan_rel = PLANNING_ROOT / rows[0]['plan']
    if not plan_rel.is_relative_to(PLANNING_ROOT):
        raise PlanningError('Planning base path escapes its publication')
    plan_path = _safe_file(root, plan_rel)
    expected = manifest.get('files_sha256', {}).get(rows[0]['plan'])
    if not isinstance(expected, str) or digest_bytes(plan_path.read_bytes()) != expected:
        raise PlanningError('Retained city planning packet differs from its receipt')
    plan = _read_gzip_json(plan_path)
    _validate_plan(plan, city)
    sources = dict(plan['source_sha256'])
    sources[manifest_rel.as_posix()] = digest_bytes(manifest_path.read_bytes())
    sources[index_rel.as_posix()] = digest_bytes(index_path.read_bytes())
    sources[plan_rel.as_posix()] = digest_bytes(plan_path.read_bytes())
    for relative, expected_source in plan['source_sha256'].items():
        if not re.fullmatch(r'[0-9a-f]{64}', str(expected_source)):
            raise PlanningError('Invalid planning source digest')
        path = _safe_file(root, relative)
        if digest_bytes(path.read_bytes()) != expected_source:
            raise PlanningError('Historical planning source changed: ' + relative)
    return plan, sources


def _apply_edits(plan, edits, actor):
    if not isinstance(actor, str) or not actor.strip() or len(actor) > 150:
        raise PlanningError('Named planning author required')
    if not isinstance(edits, list) or not 1 <= len(edits) <= 1_000:
        raise PlanningError('Bounded nonempty edit list required')
    revised = deepcopy(plan)
    lines = {line['id']: line for line in revised['lines']}
    for edit in edits:
        if not isinstance(edit, dict):
            raise PlanningError('Typed planning edit required')
        kind = edit.get('kind')
        expected_keys = {'set-od': {'kind', 'rows'}, 'move-stop': {'kind', 'line', 'stop', 'chainage_m'},
            'set-service': {'kind', 'line', 'headway_s', 'dwell_s'}, 'straighten-line': {'kind', 'line'}}.get(kind)
        if expected_keys is None or set(edit) != expected_keys:
            raise PlanningError('Planning edit fields differ from the supported proposal schema')
        if kind == 'set-od':
            revised['od'] = deepcopy(edit.get('rows'))
            continue
        line = lines.get(edit.get('line'))
        if line is None:
            raise PlanningError('Unknown planning line')
        if kind == 'move-stop':
            stop = next((row for row in line['stops'] if row['id'] == edit.get('stop')), None)
            if stop is None:
                raise PlanningError('Unknown planning stop')
            stop['chainage_m'] = _finite(edit.get('chainage_m'), 'station chainage', 0., line['length_m'])
            stop['lon'], stop['lat'] = _point_at(line['coordinates'], stop['chainage_m'])
            stop['access_and_transfer_reassessment_required'] = True
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
    """Remove historical formation and propulsion fields from the handoff."""
    return dict(city=plan['city'], lines=[dict(id=line['id'], coordinates=deepcopy(line['coordinates']),
        route_length_m=line['length_m'], proposed_headway_s=line['headway_s'],
        stations=[dict(id=stop['id'], chainage_m=stop['chainage_m'], lon=stop['lon'], lat=stop['lat'],
            proposed_dwell_s=stop['dwell_s'], access_and_transfer_reassessment_required=bool(
                stop.get('access_and_transfer_reassessment_required', False))) for stop in line['stops']])
        for line in plan['lines']],
        retained_interchange_references=[dict(record=deepcopy(row), state='reassessment-required')
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
        origin='v0.5 retained city geography and station/service proposal; no old train or cost quantities imported',
        engineering_evaluation='held', route_performance_evaluated=False, city_performance_published=False,
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
        historical_service_values='Retained as proposals from the named city packet; not v0.6 operating results or selected requirements',
        cost_policy='No legacy maglev prices, guidebeam quantities, fleet figures, or cashflow are carried into this handoff',
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

