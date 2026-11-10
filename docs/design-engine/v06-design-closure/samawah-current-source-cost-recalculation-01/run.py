#!/usr/bin/env python3
"""Reprice Samawah baseline and route proposal through the authenticated city workflow."""
import argparse
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import sys
import time


HERE = Path(__file__).resolve().parent
REQUEST_PATH = HERE / 'request.json'
PRICING_DESCRIPTIONS = {
    'project-make-buy': ('Class-C modeled make/buy at the city project quantity, including modeled '
        'factory setup/tooling allocation; not a local supplier quotation.'),
    'china-bulk-buy': ('Internal adapter scenario label. This is a Class-C benchmark/forced-purchase '
        'sensitivity using China-origin benchmarks for selected manufactured stock plus assumed '
        'landing costs; some civil purchases use local-contractor proxies. Main item groups do not '
        'use project-volume price-break tiers, and no negotiated or blanket volume discount is applied.')}


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _write(path, data, encoded):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(data))


def _haversine_m(a, b):
    from math import asin, cos, radians, sin, sqrt
    lon1, lat1 = map(radians, a)
    lon2, lat2 = map(radians, b)
    dlat, dlon = lat2-lat1, lon2-lon1
    h = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 6_371_000.0 * 2 * asin(sqrt(h))


def _project(point, origin):
    from math import acos, cos, radians, sin
    earth_radius_m = 6_371_008.8
    lon, lat = map(radians, point)
    lon0, lat0 = map(radians, origin)
    delta_lon = lon-lon0
    cosine = max(-1.0, min(1.0, sin(lat0)*sin(lat)+cos(lat0)*cos(lat)*cos(delta_lon)))
    angle = acos(cosine)
    if angle < 1e-12:
        return (0.0, 0.0)
    scale = angle / sin(angle)
    return (earth_radius_m*scale*cos(lat)*sin(delta_lon),
            earth_radius_m*scale*(cos(lat0)*sin(lat)-sin(lat0)*cos(lat)*cos(delta_lon)))


def _point_segment_distance_sq(point, start, end):
    dx, dy = end[0]-start[0], end[1]-start[1]
    denominator = dx*dx + dy*dy
    if denominator == 0:
        return (point[0]-start[0])**2 + (point[1]-start[1])**2
    fraction = max(0.0, min(1.0, ((point[0]-start[0])*dx + (point[1]-start[1])*dy) / denominator))
    return (point[0]-start[0]-fraction*dx)**2 + (point[1]-start[1]-fraction*dy)**2


def _rdp(points, tolerance_m):
    if len(points) <= 2:
        return list(range(len(points)))
    keep = {0, len(points)-1}
    stack = [(0, len(points)-1)]
    limit = tolerance_m*tolerance_m
    while stack:
        first, last = stack.pop()
        selected, greatest = None, limit
        for index in range(first+1, last):
            distance = _point_segment_distance_sq(points[index], points[first], points[last])
            if distance > greatest:
                greatest, selected = distance, index
        if selected is not None:
            keep.add(selected)
            stack.extend(((first, selected), (selected, last)))
    return sorted(keep)


def _source_interval(coordinates, chain, start_m, end_m, planning_geometry,
                     start_anchor=None, end_anchor=None):
    start = start_anchor or planning_geometry.point(coordinates, chain, start_m)
    end = end_anchor or planning_geometry.point(coordinates, chain, end_m)
    points = [start]
    points.extend(coordinates[i] for i, at in enumerate(chain) if start_m+1e-8 < at < end_m-1e-8)
    points.append(end)
    return [point for i, point in enumerate(points) if i == 0 or point != points[i-1]]


def _sample_interval(coordinates, chain, start_m, end_m, planning_geometry, step_m=5.0):
    samples = []
    cursor = start_m
    while cursor < end_m:
        samples.append(planning_geometry.point(coordinates, chain, cursor))
        cursor = min(end_m, cursor+step_m)
    samples.append(planning_geometry.point(coordinates, chain, end_m))
    return samples


def _directed_deviation(samples, target_line, origin):
    target = [_project(point, origin) for point in target_line]
    if len(target) < 2:
        raise ValueError('Simplified route interval needs at least two vertices')
    return max(min(_point_segment_distance_sq(_project(point, origin), target[i], target[i+1])
                   for i in range(len(target)-1))**0.5 for point in samples)


def _simplify_canonical_line(line, tolerance_m, planning_geometry):
    """Recompute a route from the current plan, holding every stop fixed."""
    coordinates = line['coordinates']
    if line['shape'] != 'radial':
        raise ValueError('Only exact-current-source radial routes are currently supported')
    chain = planning_geometry.route(coordinates, line['shape'])
    stops = sorted(line['stops'], key=lambda stop: stop['chainage_m'])
    for stop in stops:
        mapped = planning_geometry.point(coordinates, chain, stop['chainage_m'])
        if _haversine_m(mapped, [stop['lon'], stop['lat']]) > 0.02:
            raise ValueError(f'{line["id"]}/{stop["id"]}: canonical stop is not on current route')
    origin = (sum(point[0] for point in coordinates)/len(coordinates),
              sum(point[1] for point in coordinates)/len(coordinates))
    anchors = [0.0] + [stop['chainage_m'] for stop in stops] + [chain[-1]]
    stop_at = {stop['chainage_m']: [stop['lon'], stop['lat']] for stop in stops}
    simplified = []
    worst = 0.0
    for start_m, end_m in zip(anchors, anchors[1:]):
        if end_m-start_m <= 1e-9:
            continue
        source = _source_interval(coordinates, chain, start_m, end_m, planning_geometry,
            stop_at.get(start_m), stop_at.get(end_m))
        projected = [_project(point, origin) for point in source]
        selected = [source[i] for i in _rdp(projected, tolerance_m)]
        if simplified and simplified[-1] != selected[0]:
            raise ValueError('Route simplification changed a fixed interval endpoint')
        simplified.extend(selected if not simplified else selected[1:])
        original_samples = _sample_interval(coordinates, chain, start_m, end_m, planning_geometry)
        simplified_chain = planning_geometry.route(selected, 'radial')
        reverse_samples = _sample_interval(selected, simplified_chain, 0.0,
            simplified_chain[-1], planning_geometry)
        forward = _directed_deviation(original_samples, selected, origin)
        reverse = _directed_deviation(reverse_samples, source, origin)
        worst = max(worst, forward, reverse)
    new_chain = planning_geometry.route(simplified, 'radial')
    if worst > tolerance_m + 0.05:
        raise ValueError(f'{line["id"]}: sampled deviation {worst:.3f} m exceeds {tolerance_m:.1f} m')
    new_stops = []
    next_index = 0
    for stop in stops:
        target = [stop['lon'], stop['lat']]
        vertex = next((i for i in range(next_index, len(simplified)) if simplified[i] == target), None)
        if vertex is None:
            raise ValueError(f'{line["id"]}/{stop["id"]}: fixed station coordinate not retained as a vertex')
        chainage = new_chain[vertex]
        mapped = planning_geometry.point(simplified, new_chain, chainage)
        if _haversine_m(mapped, target) > 0.001:
            raise ValueError(f'{line["id"]}/{stop["id"]}: simplification moved a canonical station')
        new_stops.append(dict(id=stop['id'], chainage_m=chainage, dwell_s=stop['dwell_s']))
        next_index = vertex+1
    diagnostics = dict(line_id=line['id'], tolerance_m=tolerance_m,
        source_route_m=chain[-1], proposed_route_m=new_chain[-1],
        route_length_change_m=new_chain[-1]-chain[-1], source_vertex_count=len(coordinates),
        proposed_vertex_count=len(simplified), maximum_sampled_deviation_m=worst,
        maximum_original_to_proposed_sampled_m=max(_directed_deviation(
            _sample_interval(coordinates, chain, a, b, planning_geometry),
            simplified, origin) for a, b in zip(anchors, anchors[1:]) if b-a > 1e-9),
        maximum_proposed_to_original_sampled_m=max(_directed_deviation(
            _sample_interval(simplified, new_chain, a, b, planning_geometry),
            coordinates, origin) for a, b in zip([0.0]+[s['chainage_m'] for s in new_stops],
            [s['chainage_m'] for s in new_stops]+[new_chain[-1]]) if b-a > 1e-9),
        metric_projection='local spherical azimuthal-equidistant; 5 m samples in both directions',
        sample_step_m=5.0, stop_count=len(stops), station_coordinates_moved=False,
        station_ids=[stop['id'] for stop in stops],
        source_coordinates_sha256=hashlib.sha256(json.dumps(coordinates, sort_keys=True,
            separators=(',', ':'), allow_nan=False).encode()).hexdigest())
    return simplified, new_stops, diagnostics


def _build_geometry_edits(base_plan, packet_id, geometry_sha, planning_geometry, tolerance_m=25.0):
    """Create a new proposal from current geometry; old screen geometry is never transferred."""
    if len(base_plan['lines']) != 5:
        raise ValueError('Five exact Samawah line identities required')
    edits, diagnostics = [], []
    for base in sorted(base_plan['lines'], key=lambda line: line['id']):
        coordinates, stops, detail = _simplify_canonical_line(base, tolerance_m, planning_geometry)
        detail['proposed_coordinates_sha256'] = hashlib.sha256(json.dumps(coordinates,
            sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
        diagnostics.append(detail)
        edits.append(dict(kind='replace-line-geometry', line=base['id'], coordinates=coordinates,
            shape='radial', stops=stops, design_speed_cap_m_s=base['design_speed_cap_m_s'],
            reason=(f'New {tolerance_m:.0f} m sampled-deviation simplification from exact current '
                    f'canonical route coordinates; prior route-screen packet {packet_id} '
                    f'(scenario {geometry_sha}) supplied tolerance context only.')))
    return edits, diagnostics


def _study_request(request, pricing_scenario, *, base_study_id=None, edit_bundle=None):
    value = dict(schema='osr-city-workflow-request/1', city_slug=request['city_slug'],
        expected_outline_evaluation_id=request['source_outline_evaluation_id'],
        selection=request['baseline_alignment'],
        project=dict(pricing_scenario=pricing_scenario))
    if base_study_id is not None:
        value['base_study_id'] = base_study_id
        value['edit_bundle'] = edit_bundle
    return value


def _replay_verified(manifest, record, replay_requested):
    """The city verifier returns its sealed manifest; successful replay returns normally."""
    if not replay_requested:
        return False
    if manifest.get('evaluation_id') != record.get('evaluation_id'):
        raise ValueError('Replayed city study identity differs from its returned manifest')
    return True


def _validate_base_plan(plan, seed, baseline_summary):
    if (plan.get('official_seed_id') != seed['seed_id']
            or plan.get('source_outline_evaluation_id') != baseline_summary['outline_evaluation_id']
            or plan.get('outline_context', {}).get('seed', {}).get('reference_candidate_ids')
            != seed['reference_candidate_ids']):
        raise ValueError('Baseline study planning record differs from published vehicle or seed')
    return True


def _service_semantics(city):
    """Ignore only evaluation hashes and price-basis labels between price runs."""
    value = deepcopy(city['service_evaluation'])
    value.pop('evaluation_id', None)
    for row in value['line_services']:
        row.pop('evaluation_id', None)
        service = row.get('service', {})
        service.pop('evaluation_id', None)
        for requirements in (row.get('requirements', {}), service.get('requirements', {})):
            requirements.pop('pricing_basis', None)
            project = requirements.get('project')
            if isinstance(project, dict):
                project.pop('pricing_scenario', None)
    return value


def _canonical_identity(value):
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def _run_study(label, request, root, output, workflow, *, replay=True):
    study_id = workflow.identity(request)[:32]
    artifacts = root / 'build/city-studies' / study_id / 'artifacts'
    reused = artifacts.exists()
    if reused:
        cached_request = workflow.read_json(artifacts, 'request.json')
        if _canonical_bytes(cached_request) != _canonical_bytes(request):
            raise ValueError('Existing city study identity is occupied by different request bytes')
    else:
        artifacts.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    if reused:
        manifest = workflow.verify(artifacts, root=root, replay=replay)
        verified = manifest
    else:
        manifest = workflow.run(request, artifacts, root=root)
        verified = workflow.verify(artifacts, root=root, replay=replay)
    elapsed = time.perf_counter() - started
    destination = output / 'studies' / label
    shutil.copytree(artifacts, destination)
    record = workflow.read_json(destination, 'result.json')
    city = record['city_outline']
    costs = city['cost']
    scopes = costs['scope_totals_usd']
    if len(scopes) != 14 or any(set(v) != {'low', 'base', 'high'} for v in scopes.values()):
        raise ValueError('Fourteen complete low/base/high cost scopes required')
    if any(type(v) not in (int, float) or not math.isfinite(v)
           for scope in scopes.values() for v in scope.values()):
        raise ValueError('A missing price must remain an explicit hold, not a zero')
    line_services = city['service_evaluation']['line_services']
    summary = dict(label=label, study_id=study_id, manifest_id=manifest['manifest_id'],
        replay_verified=_replay_verified(verified, record, replay), elapsed_s=elapsed,
        exact_cached_study_reused=reused,
        city_input_id=city['input_id'], outline_evaluation_id=city['evaluation_id'],
        service_evaluation_id=city['service_evaluation']['evaluation_id'],
        service_semantics_id=_canonical_identity(_service_semantics(city)),
        cost_evaluation_id=costs['evaluation_id'],
        candidate_id=city['reference_candidate_ids']['candidate_id'],
        body_candidate_id=city['reference_candidate_ids']['body_candidate_id'],
        planning_revision_id=city['planning_revision_id'],
        reference_candidate_ids=city['reference_candidate_ids'],
        research_configuration_id=city['research_configuration_id'],
        selected_alignment_id=city.get('selected_alignment_id'),
        selected_alignment_kind=city.get('selected_alignment_kind'),
        pricing_scenario=city['policy']['project']['pricing_scenario'],
        pricing_description=PRICING_DESCRIPTIONS[city['policy']['project']['pricing_scenario']],
        outline_acceptance=record['outline_acceptance'],
        route_km=round(sum(line['route_m'] for line in city['geometry_and_service']['lines'])/1000, 6),
        total_trainsets=sum(row['service']['total_trainsets'] for row in line_services),
        line_services=[dict(line_id=row['line_id'], headway_s=row['requirements']['headway_s'],
            trainsets=row['service']['total_trainsets']) for row in line_services],
        installed_capital_usd=costs['installed_capital_usd'],
        whole_life_npv_usd=costs['whole_life_npv_usd'],
        price_per_route_km_usd=costs['price_per_route_km_usd'],
        scope_totals_usd=scopes, estimate_class=costs.get('estimate_class'),
        physical_accepted=False, engineering_accepted=False,
        manufacturing_release=False, operating_release=False, movement_authority=False)
    return dict(study_id=study_id, artifacts=destination, summary=summary,
        request=request, manifest=manifest)


def run(root, output_dir, request_path=REQUEST_PATH):
    root = Path(root).resolve()
    output = Path(output_dir).resolve()
    if output.exists():
        raise ValueError('Fresh private cost-comparison output required')
    request = _load(request_path)
    if request.get('schema') != 'osr-samawah-current-source-cost-comparison-request/1':
        raise ValueError('Known Samawah cost-comparison request required')
    # Import from the exact supplied source root, which may be a full checkout or
    # a read-only-at-the-procedure-level mirror used to complete a sparse tree.
    sys.path.insert(0, str(root))
    from engineering.outline import city_workflow, planning_adapter, planning_geometry
    from engineering.station_rail.common import digest, encoded, identity

    seed = planning_adapter._published_seed(root, request['city_slug'])
    planning_adapter.validate_seed(seed, root)
    refs = seed['reference_candidate_ids']
    if (seed['seed_id'] != request['planning_seed_id']
            or seed['source_outline_evaluation_id'] != request['source_outline_evaluation_id']
            or refs.get('candidate_id') != request['reference_candidate_id']
            or refs.get('body_candidate_id') != request['reference_body_candidate_id']):
        raise ValueError('Published v0.6 vehicle or Samawah seed changed')
    packet = root / request['geometry_proposal']['packet_path']
    packet_manifest = _load(packet / 'manifest.json')
    scenario_path = packet / request['geometry_proposal']['scenario_path']
    if (packet_manifest.get('packet_id') != request['geometry_proposal']['packet_id']
            or digest(packet / 'manifest.json') != request['geometry_proposal']['packet_manifest_sha256']
            or digest(scenario_path) != request['geometry_proposal']['scenario_sha256']):
        raise ValueError('External route proposal packet or scenario bytes changed')
    # Validate the earlier screen packet for provenance. Its station coordinates
    # differ from the current canonical plan, so its geometry is not transferred.
    _load(scenario_path)
    output.mkdir(parents=True)
    _write(output / 'request.json', request, encoded)
    shutil.copy2(request_path, output / 'source-request.json')
    shutil.copy2(HERE / 'run.py', output / 'run.py')
    shutil.copy2(HERE / 'README.md', output / 'method.md')

    results = {}
    base_request = _study_request(request, 'project-make-buy')
    results['baseline-project-make-buy'] = _run_study('baseline-project-make-buy',
        base_request, root, output, city_workflow)
    base_local = results['baseline-project-make-buy']
    base_plan = _load(base_local['artifacts'] / 'planning.json')
    _validate_base_plan(base_plan, seed, base_local['summary'])
    edits, geometry_diagnostics = _build_geometry_edits(base_plan, packet_manifest['packet_id'],
        request['geometry_proposal']['scenario_sha256'], planning_geometry,
        request['geometry_proposal']['maximum_deviation_m'])
    edit_bundle = dict(schema=planning_adapter.EDIT_SCHEMA, city=request['city_slug'],
        base_revision_sha256=base_plan['revision_sha256'], seed_id=seed['seed_id'],
        source_outline_evaluation_id=base_plan['source_outline_evaluation_id'],
        actor='OpenSourceRail v0.6 current-source planning comparison', edits=edits)
    _write(output / 'route-generation.json', dict(
        schema='osr-samawah-current-source-route-simplification/1',
        source_baseline_study_id=base_local['study_id'],
        source_plan_revision_sha256=base_plan['revision_sha256'],
        geometry_method=('Douglas-Peucker independently recomputed per canonical adjacent-stop interval; '
            'local spherical azimuthal-equidistant projection; symmetric 5 m sampled deviations'),
        tolerance_m=request['geometry_proposal']['maximum_deviation_m'], sample_step_m=5.0,
        prior_packet_geometry_reused=False, fixed_operational_stop_coordinates=True,
        lines=geometry_diagnostics, selected=False), encoded)
    route_generation_id = identity(_load(output / 'route-generation.json'))
    scenario = 'china-bulk-buy'
    label = 'baseline-' + scenario
    results[label] = _run_study(label, _study_request(request, scenario), root, output, city_workflow)
    for scenario in request['pricing_scenarios']:
        label = 'route-20m-' + scenario
        study_request = _study_request(request, scenario,
            base_study_id=base_local['study_id'], edit_bundle=edit_bundle)
        results[label] = _run_study(label, study_request, root, output, city_workflow)

    summaries = {name: value['summary'] for name, value in results.items()}
    expected_scope_names = set(base_local['summary']['scope_totals_usd'])
    if any(set(row['scope_totals_usd']) != expected_scope_names for row in summaries.values()):
        raise ValueError('The four studies must use the same fourteen cost scopes')
    for prefix in ('baseline', 'route-20m'):
        local = summaries[prefix + '-project-make-buy']
        china = summaries[prefix + '-china-bulk-buy']
        for field in ('city_input_id', 'service_semantics_id', 'candidate_id', 'body_candidate_id'):
            if local[field] != china[field]:
                raise ValueError(f'{prefix}: supply-price cases differ physically or in service: {field}')
    if (summaries['baseline-project-make-buy']['city_input_id'] ==
            summaries['route-20m-project-make-buy']['city_input_id']):
        raise ValueError('The route geometry alternative must produce a new city input identity')
    if not all(row['replay_verified'] for row in summaries.values()):
        raise ValueError('Every one of the four immutable studies must replay successfully')
    output_record = dict(schema='osr-samawah-current-source-cost-comparison/1',
        source_commit=request['source_commit'], planning_seed_id=seed['seed_id'],
        source_outline_evaluation_id=seed['source_outline_evaluation_id'],
        physical_reference_candidate_id=refs['candidate_id'],
        physical_reference_body_candidate_id=refs['body_candidate_id'],
        alignment_context_packet_id=packet_manifest['packet_id'],
        alignment_context_scenario_sha256=request['geometry_proposal']['scenario_sha256'],
        route_generation_id=route_generation_id,
        studies=summaries, all_fourteen_scopes_present=True,
        all_studies_replayed=True,
        pricing_scenario_notes=PRICING_DESCRIPTIONS,
        pricing_comparison_purpose='Calculated Class C local make/buy vs China benchmark/forced-purchase sensitivity; no confirmed supplier quote or project-volume discount',
        route_comparison_purpose='The 20 m geometry is freshly simplified from the exact current plan with fixed station anchors; service and cost are recalculated under the published v0.6 vehicle',
        limitations=request['open_assumptions'],
        physical_accepted=False, engineering_accepted=False,
        manufacturing_release=False, operating_release=False, movement_authority=False)
    output_record['comparison_id'] = identity(output_record)
    _write(output / 'summary.json', output_record, encoded)
    execution = dict(schema='osr-bounded-city-cost-execution/1',
        source_root=str(root), source_commit=request['source_commit'],
        study_count=len(results), study_results={k:{'study_id':v['study_id'],
            'manifest_id':v['manifest']['manifest_id'], 'replay_verified':v['summary']['replay_verified'],
            'exact_cached_study_reused':v['summary']['exact_cached_study_reused'],
            'elapsed_s':v['summary']['elapsed_s']} for k,v in results.items()},
        os_sandbox_enforced=False, external_network_or_transactions=False)
    _write(output / 'execution.json', execution, encoded)
    files = {p.relative_to(output).as_posix(): digest(p)
        for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'manifest.json'}
    manifest = dict(schema='osr-samawah-current-source-cost-comparison-manifest/1',
        comparison_id=output_record['comparison_id'], request_id=identity(request),
        source_commit=request['source_commit'], files_sha256=files,
        file_count=len(files), selected=False, physical_accepted=False,
        engineering_accepted=False, manufacturing_release=False,
        operating_release=False, movement_authority=False)
    manifest['manifest_id'] = identity(manifest)
    _write(output / 'manifest.json', manifest, encoded)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='Full source checkout for the pinned seed epoch')
    parser.add_argument('--output-dir', type=Path, required=True, help='Fresh private output directory')
    parser.add_argument('--request', type=Path, default=REQUEST_PATH)
    args = parser.parse_args(argv)
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('10-minute execution budget exceeded')))
        signal.alarm(600)
    try:
        result = run(args.root, args.output_dir, args.request)
    finally:
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
