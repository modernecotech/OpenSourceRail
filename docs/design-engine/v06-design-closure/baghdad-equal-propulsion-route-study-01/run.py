#!/usr/bin/env python3
"""Run a source-bound Baghdad same-propulsion route and cost comparison."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import numpy as np
import shapely
from shapely import distance as shapely_distance, points as shapely_points
from shapely.geometry import LineString

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / 'samawah-current-source-cost-recalculation-01' / 'run.py'


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_bytes())


def write(path, value, encoded):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))


def accelerated_directed_deviation(helper, samples, target_line, origin):
    """Compute the same projected point-to-polyline distance with GEOS indexing."""
    target = np.asarray([helper._project(point, origin) for point in target_line], dtype=np.float64)
    if len(target) < 2:
        raise ValueError('Simplified route interval needs at least two vertices')
    line = LineString(target)
    maximum = 0.0
    for start in range(0, len(samples), 4096):
        chunk = samples[start:start+4096]
        coordinates = np.asarray([helper._project(point, origin) for point in chunk], dtype=np.float64)
        distances = shapely_distance(shapely_points(coordinates[:, 0], coordinates[:, 1]), line)
        maximum = max(maximum, float(np.max(distances)))
    return maximum


def verify_distance_kernel(helper):
    """Differentially compare the vectorized GEOS kernel with the prior all-pairs method."""
    origin = (44.4, 33.3)
    target = [[44.4000, 33.3000], [44.4010, 33.3002], [44.4020, 33.3000],
              [44.4030, 33.3004], [44.4040, 33.3001]]
    samples = [[44.4000+i*0.00002, 33.2995+((i % 7)-3)*0.00008] for i in range(251)]
    reference = helper._directed_deviation(samples, target, origin)
    accelerated = accelerated_directed_deviation(helper, samples, target, origin)
    error = abs(reference-accelerated)
    if error > 1e-7:
        raise ValueError(f'GEOS distance kernel differs from independent all-pairs result by {error} m')
    return dict(state='passed', reference_max_deviation_m=reference,
        accelerated_max_deviation_m=accelerated, absolute_error_m=error,
        tolerance_m=1e-7, engine=f'Shapely {shapely.__version__} / GEOS point-to-LineString')


def normalize_numerical_endpoint_chainages(line, planning_geometry):
    """Snap sub-micrometre stop chainages to an identical route endpoint."""
    normalized = deepcopy(line)
    chain = planning_geometry.route(normalized['coordinates'], 'radial')
    endpoints = ((0.0, normalized['coordinates'][0]), (chain[-1], normalized['coordinates'][-1]))
    changes = []
    for stop in normalized['stops']:
        for endpoint_m, endpoint in endpoints:
            if (abs(float(stop['chainage_m'])-endpoint_m) <= 1e-6
                    and [stop['lon'], stop['lat']] == endpoint
                    and float(stop['chainage_m']) != endpoint_m):
                changes.append(dict(line_id=normalized['id'], stop_id=stop['id'],
                    prior_chainage_m=stop['chainage_m'], canonical_endpoint_m=endpoint_m,
                    stop_coordinates_unchanged=True, tolerance_m=1e-6))
                stop['chainage_m'] = endpoint_m
                break
    return normalized, changes


def run(root, output, request_path):
    root, output = Path(root).resolve(), Path(output).resolve()
    request_path = Path(request_path).resolve()
    if output.exists():
        raise ValueError('Use a fresh private output directory; preserve earlier attempts')
    request = load(request_path)
    expected_commit = request['source_commit']
    actual_commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    if not actual_commit.startswith(expected_commit):
        raise ValueError(f'Expected source epoch {expected_commit}, got {actual_commit}')
    sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location('city_route_helpers', PRIOR)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    from engineering.outline import city_inputs, city_workflow, planning_adapter, planning_geometry, completion_publication
    from engineering.station_rail.common import encoded, identity

    if request['schema'] != 'osr-city-equal-propulsion-route-study-request/1':
        raise ValueError('Unknown request schema')
    publication_manifest, _ = completion_publication.verify(root=root)
    if publication_manifest['manifest_id'] != request['outline_publication_manifest_id']:
        raise ValueError('Current outline publication differs from request')
    seed = planning_adapter._published_seed(root, request['city_slug'])
    planning_adapter.validate_seed(seed, root)
    refs = seed['reference_candidate_ids']
    if (seed['seed_id'] != request['planning_seed_id']
            or seed['source_outline_evaluation_id'] != request['source_outline_evaluation_id']
            or refs.get('candidate_id') != request['reference_candidate_id']
            or refs.get('body_candidate_id') != request['reference_body_candidate_id']):
        raise ValueError('Published planning seed or physical reference candidate changed')
    city = city_inputs.load(request['city_slug'], root=root)
    expected_lines = {line['line_id'] for line in city['lines']}
    policy = request['propulsion_policy_by_line']
    if set(policy) != expected_lines or set(policy.values()) != {'powered-axle-continuous-research'}:
        raise ValueError('One explicit powered-axle research policy per exact city line required')
    distance_kernel_check = verify_distance_kernel(helper)
    helper._directed_deviation = lambda samples, target, origin: accelerated_directed_deviation(
        helper, samples, target, origin)

    output.mkdir(parents=True)
    write(output/'request.json', request, encoded)
    shutil.copy2(request_path, output/'source-request.json')
    shutil.copy2(HERE/'run.py', output/'run.py')
    shutil.copy2(PRIOR, output/'geometry-helper-source.py')

    def make_request(*, base_study_id=None, edit_bundle=None):
        value = helper._study_request(request, request['pricing_scenario'],
            base_study_id=base_study_id, edit_bundle=edit_bundle)
        value['service'] = {'propulsion_policy_by_line': policy}
        return value

    baseline_request = make_request()
    baseline_label = f"baseline-published-{request['baseline_alignment']}-powered-axle"
    route_label = 'simplified-radials-from-published-baseline'
    base = helper._run_study(baseline_label, baseline_request,
        root, output, city_workflow, replay=True)
    base_plan = helper._load(base['artifacts']/'planning.json')
    helper._validate_base_plan(base_plan, seed, base['summary'])

    tolerance = request['geometry_proposal']['maximum_sampled_deviation_m']
    sample_step = request['geometry_proposal']['sample_step_m']
    if sample_step != 5.0:
        raise ValueError('This reproduced simplifier currently uses exact 5 m bidirectional sampling')
    edits, diagnostics = [], []
    endpoint_normalizations = []
    for line in sorted(base_plan['lines'], key=lambda item: item['id']):
        if line['shape'] != 'radial':
            diagnostics.append(dict(line_id=line['id'], source_shape=line['shape'],
                geometry_status='retained-unchanged', stop_count=len(line['stops']),
                reason='Closed ring geometry is unchanged in this radial-route sensitivity; square-ring design needs a separate explicit candidate.'))
            continue
        normalized_line, normalized = normalize_numerical_endpoint_chainages(line, planning_geometry)
        endpoint_normalizations.extend(normalized)
        coordinates, stops, detail = helper._simplify_canonical_line(normalized_line, tolerance, planning_geometry)
        detail['proposed_coordinates_sha256'] = hashlib.sha256(canonical(coordinates)).hexdigest()
        detail['geometry_status'] = 'simplified-between-fixed-stops'
        diagnostics.append(detail)
        edits.append(dict(kind='replace-line-geometry', line=line['id'], coordinates=coordinates,
            shape='radial', stops=stops, design_speed_cap_m_s=line['design_speed_cap_m_s'],
            reason=(f'New {tolerance:.0f} m sampled-deviation simplification from exact current canonical route coordinates; '
                    'all operational station coordinates retained.')))
    if not edits:
        raise ValueError('No supported radial route to simplify')
    edit_bundle = dict(schema=planning_adapter.EDIT_SCHEMA, city=request['city_slug'],
        base_revision_sha256=base_plan['revision_sha256'], seed_id=seed['seed_id'],
        source_outline_evaluation_id=base_plan['source_outline_evaluation_id'],
        actor='OpenSourceRail Baghdad route sensitivity', edits=edits)
    generation = dict(schema='osr-baghdad-equal-propulsion-route-generation/1',
        source_baseline_study_id=base['study_id'],
        source_plan_revision_sha256=base_plan['revision_sha256'],
        geometry_method=('Douglas-Peucker recomputed within each canonical adjacent-stop interval; '
            'local spherical azimuthal-equidistant projection; symmetric 5 m samples in both directions'),
        tolerance_m=tolerance, sample_step_m=sample_step,
        distance_kernel_check=distance_kernel_check,
        endpoint_chainage_normalizations=endpoint_normalizations,
        prior_geometry_reused=False, station_coordinates_fixed=True,
        simplified_radial_line_count=len(edits), retained_nonradial_line_ids=[x['line_id'] for x in diagnostics
            if x['geometry_status']=='retained-unchanged'],
        line_diagnostics=diagnostics, selected=False)
    generation['generation_id'] = identity(generation)
    write(output/'route-generation.json', generation, encoded)
    route_request = make_request(base_study_id=base['study_id'], edit_bundle=edit_bundle)
    route = helper._run_study(route_label, route_request,
        root, output, city_workflow, replay=True)

    summaries_out = {}
    expected_scopes = set(base['summary']['scope_totals_usd'])
    for record in (base, route):
        result = city_workflow.read_json(record['artifacts'], 'result.json')
        city_record = result['city_outline']
        costs = city_record['cost']
        if set(costs['scope_totals_usd']) != expected_scopes or len(expected_scopes) != 14:
            raise ValueError('Both studies must contain the same fourteen cost scopes')
        hypotheses = [line['propulsion_hypothesis'] for line in city_record['service_evaluation']['line_services']]
        if len(hypotheses) != len(policy) or any(h['kind'] != 'powered-axle-continuous-research'
                or h['policy_basis'] != 'explicit-per-line-policy'
                or h['automatic_fallback_selected'] is not False
                or h['actual_available_force_map'] is not None for h in hypotheses):
            raise ValueError('A line changed family, fell back automatically, or gained an unsupported force map')
        service_assumptions = city_record['service_evaluation']['assumptions']
        if service_assumptions.get('propulsion_policy_by_line') != policy:
            raise ValueError('The fixed policy did not propagate into the city record')
        summaries_out[record['summary']['label']] = dict(
            **record['summary'], propulsion_hypotheses=hypotheses,
            source_sha256=city_record['source_sha256'], assumptions=service_assumptions,
            line_service_results=[dict(line_id=x['line_id'], headway_s=x['requirements']['headway_s'],
                dwell_s=x['requirements'].get('dwell_s'), trainsets=x['service']['total_trainsets'])
                for x in city_record['service_evaluation']['line_services']],
            model_acceptance_flags={k: city_record[k] for k in (
                'outline_complete','physical_accepted','engineering_accepted',
                'manufacturing_release','operating_release','movement_authority') if k in city_record})
    if base['summary']['city_input_id'] == route['summary']['city_input_id']:
        raise ValueError('The geometry revision must produce a distinct city-input identity')
    if any(not row['summary']['replay_verified'] for row in (base, route)):
        raise ValueError('Both fresh city studies must replay')
    if any(summaries_out[name]['candidate_id'] != summaries_out[next(iter(summaries_out))]['candidate_id']
            or summaries_out[name]['body_candidate_id'] != summaries_out[next(iter(summaries_out))]['body_candidate_id']
            for name in summaries_out):
        raise ValueError('Physical vehicle/body candidate identities changed across route cases')

    result = dict(schema='osr-baghdad-equal-propulsion-route-study/1',
        source_commit=actual_commit, planning_seed_id=seed['seed_id'],
        outline_publication_manifest_id=publication_manifest['manifest_id'],
        physical_vehicle_candidate_id=refs['candidate_id'], physical_body_candidate_id=refs['body_candidate_id'],
        propulsion_policy_by_line=policy, pricing_scenario=request['pricing_scenario'],
        route_generation_id=generation['generation_id'], studies=summaries_out,
        same_propulsion_for_all_lines=True, fixed_physical_candidate=True,
        fourteen_scopes_present=True, all_studies_replayed=True,
        force_map_available=False, selected=False,
        limitations=request['open_assumptions'], physical_accepted=False,
        engineering_accepted=False, manufacturing_release=False,
        operating_release=False, movement_authority=False)
    result['comparison_id'] = identity(result)
    write(output/'summary.json', result, encoded)
    execution = dict(schema='osr-bounded-equal-propulsion-city-execution/1',
        source_root=str(root), source_commit=actual_commit,
        cpu_limit_s=600, address_space_limit_bytes=3*1024**3,
        file_size_limit_bytes=32*1024**2, open_file_limit=256,
        os_sandbox_enforced=False,
        studies={key:{'study_id':value['study_id'],'manifest_id':value['manifest_id'],
            'replay_verified':value['replay_verified'],
            'exact_cached_study_reused':value['exact_cached_study_reused'],
            'elapsed_s':value['elapsed_s']} for key,value in
            ((base['summary']['label'],base['summary']),(route['summary']['label'],route['summary']))})
    write(output/'execution.json', execution, encoded)
    files={p.relative_to(output).as_posix():digest(p)
        for p in sorted(output.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    manifest=dict(schema='osr-baghdad-equal-propulsion-route-study-manifest/1',
        comparison_id=result['comparison_id'], request_id=identity(request),
        source_commit=actual_commit, files_sha256=files, file_count=len(files),
        selected=False, physical_accepted=False, engineering_accepted=False,
        manufacturing_release=False, operating_release=False, movement_authority=False)
    manifest['manifest_id'] = identity(manifest)
    write(output/'manifest.json', manifest, encoded)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--request', type=Path, default=HERE/'request.json')
    args = parser.parse_args()
    for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
        os.environ[name] = '1'
    resource.setrlimit(resource.RLIMIT_CPU, (600,610))
    resource.setrlimit(resource.RLIMIT_AS, (3*1024**3,3*1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (32*1024**2,32*1024**2))
    resource.setrlimit(resource.RLIMIT_NOFILE, (256,256))
    print(json.dumps(run(args.root,args.output,args.request),sort_keys=True))


if __name__ == '__main__':
    raise SystemExit(main())
